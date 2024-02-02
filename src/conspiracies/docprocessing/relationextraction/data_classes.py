"""Pydantic data classes for the relation extraction using prompt-based
models."""

from copy import copy
from difflib import SequenceMatcher
from functools import partial
from typing import (
    Any,
    Dict,
    Iterable,
    Iterator,
    List,
    Literal,
    Optional,
    Sequence,
    Tuple,
    Union,
)

import numpy as np
import spacy
from pydantic import BaseModel, Extra
from spacy import displacy
from spacy.tokens import Doc, Span, Token


def get_text(span: Iterable[Token], ignore_spaces: bool, lowercase: bool) -> str:
    """Gets the text of a span or doc.

    Args:
        span (Iterable[Token]): a spacy span or doc.
        ignore_spaces (bool): whether to ignore spaces.
        lowercase (bool): whether to lowercase the text.

    Returns:
        str: the text of the span or doc.
    """
    if ignore_spaces:
        span_str = " ".join([t.text.strip() for t in span])
    else:
        span_str = "".join([t.text_with_ws for t in span])
    if lowercase:
        span_str = span_str.lower()
    return span_str


def subspan_of_span(
    subspan: Union[Span, Doc],
    span: Union[Span, Doc],
    lowercase: bool = False,
    ignore_spaces: bool = False,
) -> List[Span]:
    """Checks if a token is contained in a span. This function assumes that the
    token is not from the span and therefore.

    Args:
        subspan (Union[Span, Doc]): a spacy span or doc to check if it is contained
            wihtin span.
        span (Union[Span, Doc]): a spacy span (or Doc) to check if the subspan is
            contained within.

    Returns:
        List[Span]: a list of spans from span that are (string-)equal to the subspan.
    """
    if not span:
        return []

    _get_text = partial(get_text, ignore_spaces=ignore_spaces, lowercase=lowercase)
    if ignore_spaces:
        subspan = [t for t in subspan if t.text.strip() != ""]  # type: ignore
        span = [t for t in span if t.text.strip() != ""]  # type: ignore
    span_len = len(subspan)
    _spans = [span[i : i + span_len] for i in range(len(span) - span_len + 1)]

    subspan_text = _get_text(subspan)

    potential_spans = []
    for _span in _spans:
        _span_text = _get_text(_span)
        if subspan_text == _span_text:
            potential_spans.append(_span)

    if ignore_spaces:  # reconstruct to spans instead of list[token]
        try:
            doc = span[0].doc
            potential_spans = [
                doc[span[0].i : span[-1].i + 1] for span in potential_spans
            ]
        except IndexError:
            return []

    return potential_spans


class StringTriplet(BaseModel):
    class Config:
        extra = Extra.forbid

    subject: str
    predicate: str
    object: str
    subject_char_span: Optional[Tuple[int, int]] = None
    predicate_char_span: Optional[Tuple[int, int]] = None
    object_char_span: Optional[Tuple[int, int]] = None
    text: Optional[str] = None

    @property
    def triplet(self) -> Tuple[str, str, str]:
        return (self.subject, self.predicate, self.object)

    @property
    def char_spans(
        self,
    ) -> Tuple[
        Optional[Tuple[int, int]],
        Optional[Tuple[int, int]],
        Optional[Tuple[int, int]],
    ]:  # noqa: E501
        return (self.subject_char_span, self.predicate_char_span, self.object_char_span)

    def has_ranges(self) -> bool:
        return all(r is not None for r in self.char_spans)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, StringTriplet):
            if self.has_ranges() and other.has_ranges():
                has_same_char_span = self.char_spans == other.char_spans
            else:
                has_same_char_span = True

            return (
                self.triplet == other.triplet
                and self.text == other.text
                and has_same_char_span
            )
        return False


def _lcs_size(a: Sequence, b: Sequence) -> int:
    """Return the size of the longest common subsequence."""
    s = SequenceMatcher(None, a, b)
    return s.find_longest_match().size


class SpanTriplet(BaseModel):
    """A class for a semantic triplet with spans.

    Args:
        subject (Span): Subject of the triplet.
        predicate (Span): Predicate of the triplet.
        object (Span): Object of the triplet.
    """

    class Config:
        arbitrary_types_allowed = True
        extra = Extra.forbid

    subject: Span
    predicate: Span
    object: Span

    @property
    def triplet(self) -> Tuple[Span, Span, Span]:
        """Returns the triplet as a tuple."""
        return self.subject, self.predicate, self.object

    @property
    def span(self) -> Span:
        """Returns the span of the triplet."""
        min_start = min([s.start for s in self.triplet])
        max_end = max([s.end for s in self.triplet])

        return self.subject.doc[min_start:max_end]

    @property
    def sentence(self) -> Span:
        """Returns the sentence of the triplet."""
        span = self.span
        doc = span.doc

        for sent in doc.sents:
            if sent.start <= span.start and sent.end >= span.end:
                return sent
            else:
                return doc[:]

    @property
    def doc(self) -> Doc:
        """Returns the doc of the triplet."""
        return self.subject.doc

    def __visualize_w_overlap(self):
        """Visualizes the triplet using displacy."""
        colors = {
            "SUBJECT": "#7aecec",
            "PREDICATE": "#ff9561",
            "OBJECT": "#aa9cfc",
        }
        spans = [
            {
                "start_token": s.start,
                "end_token": s.end,
                "label": s.label_,
            }
            for s in self.triplet
        ]
        ex = [
            {
                "text": self.doc.text,
                "spans": spans,
                "tokens": [t.text for t in self.doc],
            },
        ]
        html = displacy.render(
            ex,
            style="span",
            manual=True,
            options={"colors": colors},
        )
        return html

    def __visualize_no_overlap(self):
        """Visualizes the triplet using displacy."""
        self.subject.label_ = "SUBJECT"
        self.predicate.label_ = "PREDICATE"
        self.object.label_ = "OBJECT"
        colors = {
            "SUBJECT": "#7aecec",
            "PREDICATE": "#ff9561",
            "OBJECT": "#aa9cfc",
        }
        sent = self.sentence
        copy_doc = self.doc[:].as_doc()  # to avoid overwriting the original doc
        options = {"ents": ["SUBJECT", "PREDICATE", "OBJECT"], "colors": colors}
        copy_doc.ents = [self.subject, self.predicate, self.object]
        viz_doc = copy_doc[sent.start : sent.end].as_doc()
        html = displacy.render(viz_doc, style="ent", options=options)
        return html

    def is_string_match(self, other) -> bool:
        if not isinstance(other, SpanTriplet):
            return False

        triplet_is_string_match = all(
            s1.text == s2.text for s1, s2 in zip(self.triplet, other.triplet)
        )
        return triplet_is_string_match

    def visualize(self, overlap: Optional[bool] = None):
        """Visualizes the triplet using displacy."""
        if overlap is None:
            try:
                return self.__visualize_no_overlap()
            except ValueError:
                return self.__visualize_w_overlap()
        if overlap:
            return self.__visualize_w_overlap()
        else:
            return self.__visualize_no_overlap()

    @staticmethod
    def span_to_json(span: Union[Span, Doc]) -> Dict[str, Any]:
        if isinstance(span, Doc):
            span = span[:]
        return {
            "text": span.text,
            "start": span.start,
            "end": span.end,
        }

    @staticmethod
    def span_from_json(json: dict, doc: Doc) -> Span:
        span = doc[json["start"] : json["end"]]
        return span

    def to_dict(self, include_doc=True, include_span_heads=False) -> Dict[str, Any]:
        if include_doc:
            data = self.span.doc.to_json()
        else:
            data = {}
        data["semantic_triplets"] = self.dict()
        data["semantic_triplets"]["subject"] = self.span_to_json(self.subject)
        data["semantic_triplets"]["predicate"] = self.span_to_json(self.predicate)
        data["semantic_triplets"]["object"] = self.span_to_json(self.object)
        if include_span_heads and Span.has_extension("most_common_ancestor"):
            subject_head = self.subject._.most_common_ancestor.text
            data["semantic_triplets"]["subject"]["head"] = subject_head
            object_head = self.object._.most_common_ancestor.text
            data["semantic_triplets"]["object"]["head"] = object_head

        return data

    @staticmethod
    def from_tuple(
        triplet: Tuple[Span, Span, Span],
    ):
        subject = triplet[0]
        predicate = triplet[1]
        object = triplet[2]
        subject.label_ = "SUBJECT"
        predicate.label_ = "PREDICATE"
        object.label_ = "OBJECT"

        return SpanTriplet(
            subject=subject,
            predicate=predicate,
            object=object,
        )

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
        nlp: spacy.Language,
        doc: Optional[Doc] = None,
    ):
        if doc is None:
            doc = Doc(nlp.vocab).from_json(data)  # type: ignore
        subject = SpanTriplet.span_from_json(data["semantic_triplets"]["subject"], doc)
        predicate = SpanTriplet.span_from_json(
            data["semantic_triplets"]["predicate"],
            doc,
        )
        object = SpanTriplet.span_from_json(data["semantic_triplets"]["object"], doc)
        subject.label_ = "SUBJECT"
        predicate.label_ = "PREDICATE"
        object.label_ = "OBJECT"

        return SpanTriplet(
            subject=subject,
            predicate=predicate,
            object=object,
        )

    @staticmethod
    def span_triplet_from_text_triplet(
        triplet: Tuple[str, str, str],
        span: Union[Span, Doc],
        lowercase: Optional[bool] = None,
    ) -> Optional["SpanTriplet"]:
        """Checks if the triplet contained within the doc based on text
        overlap.

        Args:
            triplet (Tuple[str, str, str]): A semantic triplet to check if contained
                within the span. A triplet contains subject, predicate, and object (in
                that order).
            span (Union[Span, Doc]): A spacy span or doc.
            lowercase (Optional[bool]): Whether to use lowercase
                comparison. Defaults to None. If None it will first try to match the
                triplet in the original case and then fallback to lowercase.

        Returns:
            Optional[SpanTriplet]: A SpanTriplet object. Returns None if the triplet is
                not contained in the span.
        """
        if any(t.strip() == "" for t in triplet):
            return None

        if lowercase is None:
            spantriplet = SpanTriplet.span_triplet_from_text_triplet(
                triplet,
                span,
                lowercase=False,
            )
            if spantriplet is not None:
                return spantriplet
            return SpanTriplet.span_triplet_from_text_triplet(
                triplet,
                span,
                lowercase=True,
            )

        if lowercase:
            text = span.text.lower()
            subj, pred, obj = [t.lower() for t in triplet]
        else:
            text = span.text
            subj, pred, obj = triplet
        subj_start = text.find(subj)
        if subj_start == -1:
            return None
        subj_end = subj_start + len(subj)

        # first try to find the object after the subject
        obj_start = text[subj_end:].find(obj)
        if obj_start != -1:
            obj_start = text.find(obj)
        if obj_start == -1:
            return None
        obj_end = obj_start + len(obj)

        # first try to find the predicate in between the subject and object
        start_pred = text[subj_end:obj_end].find(pred)
        if start_pred != -1:
            start_pred = text.find(pred)
        if start_pred == -1:
            return None
        end_pred = start_pred + len(pred)

        # create spans from ranges
        return SpanTriplet.from_char_span(
            span,
            (subj_start, subj_end),
            (start_pred, end_pred),
            (obj_start, obj_end),
        )

    @staticmethod
    def from_char_span(
        doc: Union[Span, Doc],
        subj_char_span: Tuple[int, int],
        pred_char_span: Tuple[int, int],
        obj_char_span: Tuple[int, int],
    ) -> Optional["SpanTriplet"]:
        """Creates a SpanTriplet from a StringTriplet.

        Args:
            doc: A spacy span or doc.
            str_triplet: A StringTriplet object.

        Returns:
            A SpanTriplet object. Returns None if the triplet is not contained in the
                span.
        """
        triplet = []
        for label, (start, end) in zip(
            ["SUBJECT", "PREDICATE", "OBJECT"],
            [subj_char_span, pred_char_span, obj_char_span],
        ):
            span = doc.char_span(start, end, label=label)  # type: ignore
            if span is None:
                return None
            triplet.append(span)

        return SpanTriplet.from_tuple(triplet)  # type: ignore

    @staticmethod
    def span_triplet_from_span_triplet(
        triplet: Tuple[Span, Span, Span],
        span: Union[Span, Doc],
        lowercase: Optional[bool] = None,
        ignore_spaces: Optional[bool] = True,
    ) -> Optional["SpanTriplet"]:
        """Checks if the triplet contained within the doc based on overlap of
        span tokens.

        Args:
            triplet: A semantic triplet to check if contained
                within the span. A triplet contains subject, predicate, and object (in
                that order).
            span: A spacy span or doc.
            lowercase: Whether to use lowercase comparison. Defaults to
                None. If None it will first try to match the triplet in the original
                case and then fallback to lowercase.
            ignore_spaces: Whether to ignore spaces when comparing
                spans. Defaults to True. If None it will first try to match the triplet
                with spaces and then fallback to ignoring spaces.

        Returns:
            Optional[SpanTriplet]: A SpanTriplet object. Returns None if the triplet is
                not contained in the span.
        """

        if isinstance(span, Doc):
            span = span[:]
        if ignore_spaces is None:
            spantriplet = SpanTriplet.span_triplet_from_span_triplet(
                triplet,
                span,
                lowercase=lowercase,
                ignore_spaces=False,
            )
            if spantriplet is not None:
                return spantriplet
            return SpanTriplet.span_triplet_from_span_triplet(
                triplet,
                span,
                lowercase=lowercase,
                ignore_spaces=True,
            )
        if lowercase is None:
            spantriplet = SpanTriplet.span_triplet_from_span_triplet(
                triplet,
                span,
                lowercase=False,
            )
            if spantriplet is not None:
                return spantriplet
            return SpanTriplet.span_triplet_from_span_triplet(
                triplet,
                span,
                lowercase=True,
            )

        _subspan_of_span = partial(
            subspan_of_span,
            lowercase=lowercase,
            ignore_spaces=ignore_spaces,
        )

        subj, pred, obj = triplet
        cand_subj_span = _subspan_of_span(subj, span)
        if not cand_subj_span:
            return None
        subj_span = cand_subj_span[0]  # assume first match is correct

        # first assume object is after subject
        cand_obj_span = _subspan_of_span(obj, span.doc[subj_span.end : span.end])
        if not cand_obj_span:
            cand_obj_span = _subspan_of_span(obj, span)
        if not cand_obj_span:
            return None
        obj_span = cand_obj_span[0]  # assume first match is correct

        # first assume predicate is in between subject and object
        min_idx = min(subj_span.end, obj_span.end)
        max_idx = max(subj_span.start, obj_span.start)
        cand_pred_span = _subspan_of_span(pred, span.doc[min_idx:max_idx])
        if not cand_pred_span:  # fallback to entire span
            cand_pred_span = _subspan_of_span(pred, span)
            if not cand_pred_span:
                return None

            # try to find the predicate closest to the subject object span
            cand_pred_span_before = [
                span for span in cand_pred_span if span.end < min_idx
            ]
            if cand_pred_span_before:
                pred_span = sorted(cand_pred_span_before, key=lambda x: x.end)[-1]
            else:
                # otherwise take the first match
                pred_span = cand_pred_span[0]
        else:
            # assume the one closest to the object
            pred_span = sorted(
                cand_pred_span,
                key=lambda x: abs(x.start - obj_span.start),
            )[0]

        # update the subject span to be the closest to the predicate/obj
        min_idx = min(pred_span.end, obj_span.end)
        cand_subj_span = [s for s in cand_subj_span if s.end <= min_idx]
        if cand_subj_span:
            subj_span = sorted(cand_subj_span, key=lambda x: x.start)[-1]

        # label spans
        subj_span.label_ = "SUBJECT"
        pred_span.label_ = "PREDICATE"
        obj_span.label_ = "OBJECT"

        return SpanTriplet(
            subject=subj_span,
            predicate=pred_span,
            object=obj_span,
        )

    @staticmethod
    def from_doc(
        triplet: Union[Tuple[str, str, str], "StringTriplet"],
        doc: Union[Doc, Span],
        nlp: Optional[spacy.Language] = None,
        method: Optional[Literal["span", "text"]] = None,
        lowercase: Optional[bool] = None,
        ignore_spaces: Optional[bool] = True,
    ) -> Optional["SpanTriplet"]:
        """Converts the StringTriplet to a SpanTriplet. First checks if the
        span is contained within a singular sentence, then it checks if the
        span is contained within the entire document.

        Args:
            doc: Document of the text.
            triplet: A semantic triplet to check if contained within the span. A triplet
                contains subject, predicate, and object (in that order).
            nlp: Spacy language model. Defaults to None. In which case it will create a
                blank spacy model based on the language of the doc.
            method: Whether to use the span or text comparison to find valid span
                triplets. Defaults to None. If None it will first try to match the
                triplet based on the span and then fallback to text comparison.
            lowercase: Whether to lowercase the text before comparison. Defaults to
                None. If None it will first try to match the triplet in the original
                case and then fallback to lowercase.
            ignore_spaces: Whether to ignore spaces when comparing spans. Defaults to
                True. If None it will first try to match the triplet with spaces and
                then fallback to ignoring spaces.

        Returns:
            A SpanTriplet object. Returns None if the triplet is not contained in the
                span.
        """
        if isinstance(triplet, StringTriplet):
            if triplet.has_ranges():
                span_triplet = SpanTriplet.from_char_span(
                    doc,
                    triplet.subject_char_span,  # type: ignore
                    triplet.predicate_char_span,  # type: ignore
                    triplet.object_char_span,  # type: ignore
                )
                if span_triplet is not None:
                    return span_triplet
            triplet = triplet.triplet

        subject, predicate, object = triplet
        if any(t.strip() == "" for t in triplet):
            return None
        if method is None:
            span_triplet = SpanTriplet.from_doc(
                triplet,
                doc,
                nlp=nlp,
                method="span",
                lowercase=lowercase,
                ignore_spaces=ignore_spaces,
            )
            if span_triplet is not None:
                return span_triplet
            return SpanTriplet.from_doc(
                triplet,
                doc,
                nlp=nlp,
                method="text",
                lowercase=lowercase,
                ignore_spaces=ignore_spaces,
            )
        if nlp is None:
            if isinstance(doc, Span):
                lang = doc.doc.lang_
            else:
                lang = doc.lang_
            nlp = spacy.blank(lang)
            nlp.add_pipe("sentencizer")

        if method == "span":
            triplet = tuple([doc[:] for doc in nlp.pipe(triplet)])  # type: ignore
        else:
            triplet = triplet

        span_triplet_from_mapping = {
            "span": partial(
                SpanTriplet.span_triplet_from_span_triplet,
                ignore_spaces=ignore_spaces,
            ),
            "text": SpanTriplet.span_triplet_from_text_triplet,
        }

        span_triplet_from = span_triplet_from_mapping[method]

        for sent in doc.sents:  # type: ignore
            span_triplet = span_triplet_from(
                triplet,
                sent,
                lowercase=lowercase,  # type: ignore
            )
            if span_triplet is not None:
                return span_triplet
        return span_triplet_from(triplet, doc, lowercase=lowercase)  # type: ignore

    def normalized_span_overlap(self, other: "SpanTriplet") -> float:
        """Calculates the normalized span overlap between two span triplets.
        Note this assumes the self SpanTriplet is the reference.

        Args:
            other: The other span triplet.

        Returns:
            The normalized span overlap between the two span triplets. The normalized
                is normalized between 0 and 1.
        """
        _normalized_overlap = 0.0
        for s_t, o_t in zip(self.triplet, other.triplet):
            overlap = _lcs_size(s_t, o_t)  # type: ignore
            _normalized_overlap += overlap / len(s_t)
        return _normalized_overlap / 3

    def normalized_string_overlap(self, other: "SpanTriplet") -> float:
        """Calculates the normalized span overlap between two span triplets.
        Note this assumes the self SpanTriplet is the reference.

        Args:
            other: The other span triplet.

        Returns:
            The normalized span overlap between the two span triplets. The normalized
                is normalized between 0 and 1.
        """
        _normalized_overlap = 0.0
        for s_t, o_t in zip(self.triplet, other.triplet):
            overlap = _lcs_size(s_t.text, o_t.text)
            _normalized_overlap += overlap / len(s_t.text)
        return _normalized_overlap / 3

    def __eq__(self, other) -> bool:
        if not isinstance(other, SpanTriplet):
            return False

        # It does not make sense to compare Spans in different texts, but they can
        # be different Doc objects!
        if self.doc.text != other.doc.text:
            return False

        # Equality is checked for start, end and text such that two triplets in
        # different Doc objects can be considered equal
        triplet_is_equal = all(
            s1.start == s2.start and s1.end == s2.end and s1.text == s2.text
            for s1, s2 in zip(self.triplet, other.triplet)
        )
        return triplet_is_equal


class DocTriplets(BaseModel):
    """A class containing the relations of a documents."""

    class Config:
        arbitrary_types_allowed = True
        extra = Extra.forbid

    span_triplets: List[SpanTriplet]
    doc: Doc

    @staticmethod
    def from_str_triplets(
        doc: Union[Doc, Span],
        triplets: List[StringTriplet],
    ) -> "DocTriplets":
        span_triplets = []
        for triplet in triplets:
            span_triplet = SpanTriplet.from_doc(triplet=triplet, doc=doc)
            if span_triplet is not None:
                span_triplets.append(span_triplet)
        return DocTriplets(span_triplets=span_triplets, doc=doc)

    def score_relations(self, reference: "DocTriplets") -> Dict[str, Any]:
        """Score the relations of the doctriplet against the relations of the
        current doctriplet."""
        self_relations = list(self)
        reference_relations = list(reference)
        self_relations.sort(key=lambda x: x.subject.text)
        reference_relations.sort(key=lambda x: x.subject.text)

        score = {
            "exact_span_match": 0,
            "exact_string_match": 0,
            "normalized_span_overlap": 0.0,
            "normalized_string_overlap": 0.0,
            "length_self": len(self_relations),
            "length_reference": len(reference_relations),
        }

        if score["length_reference"] == 0:
            return score

        _self_relations = copy(self_relations)
        missing_matches = {}

        for ref_i, ref_rel in enumerate(reference_relations):
            span_norm_overlap = []
            string_norm_overlap = []
            span_match_found = False
            string_match_found = False

            if not _self_relations:
                break

            for self_i, self_rel in enumerate(_self_relations):
                if self_rel == ref_rel:
                    span_match_found = True
                    break

                if self_rel.is_string_match(ref_rel):
                    string_match_found = True
                    s_norm_overlap = ref_rel.normalized_span_overlap(self_rel)

                if not string_match_found:
                    str_norm_overlap = ref_rel.normalized_string_overlap(self_rel)
                    s_norm_overlap = ref_rel.normalized_span_overlap(self_rel)
                    string_norm_overlap.append(str_norm_overlap)
                    span_norm_overlap.append(s_norm_overlap)

            if span_match_found:
                score["exact_span_match"] += 1
                score["exact_string_match"] += 1
                score["normalized_string_overlap"] += 1
                score["normalized_span_overlap"] += 1
                _self_relations.pop(self_i)
                continue
            if string_match_found:
                score["exact_string_match"] += 1
                score["normalized_string_overlap"] += 1
                score["normalized_span_overlap"] += s_norm_overlap
                _self_relations.pop(self_i)
                continue
            # if not match then just record the best match
            which_max = np.argmax(string_norm_overlap)
            missing_matches[ref_i] = {
                "span_norm_overlap": span_norm_overlap[which_max],
                "string_norm_overlap": string_norm_overlap[which_max],
                "self_i": which_max,
            }

        if missing_matches and _self_relations:
            # if there are missing matches and there are still self relations
            # then we can try to match them

            # sort the missing matches by the string norm overlap
            _missing_matches = [
                (k, v)
                for k, v in sorted(
                    missing_matches.items(),
                    key=lambda item: item[1]["string_norm_overlap"],  # type: ignore
                )
            ]

            while _missing_matches and _self_relations:
                ref_i, match = _missing_matches.pop()
                score["normalized_string_overlap"] += match["string_norm_overlap"]
                score["normalized_span_overlap"] += match["span_norm_overlap"]
                _self_relations.pop()  # just pop any self relation
        return score

    def __getitem__(self, index: int) -> SpanTriplet:
        return self.span_triplets[index]

    def __iter__(self) -> Iterator[SpanTriplet]:  # type: ignore
        return iter(self.span_triplets)

    def __len__(self) -> int:
        return len(self.span_triplets)

    def __add__(self, other: Union["DocTriplets", "SpanTriplet"]) -> "DocTriplets":
        if self.doc != other.doc:
            raise ValueError("Can only add DocTriplets from the same document.")
        if isinstance(other, SpanTriplet):
            self.span_triplets.append(other)
        else:
            self.span_triplets.extend(other.span_triplets)
        return self

    def __eq__(self, other: Any) -> bool:
        """Check if two DocTriplets are equal based on if all their span
        triplets are the same."""
        if not isinstance(other, DocTriplets):
            return False
        for s, o in zip(self, other):
            if s != o:
                return False
        return True


def span_to_idx(span: Span) -> Tuple[int, int]:
    return span.start, span.end


def idx_to_span(idx: Tuple[int, int], doc: Doc) -> Span:
    start, end = idx
    return doc[start:end]


def install_extensions(force=False) -> None:
    """Sets extensions on the SpaCy Doc class.

    Relation triplets are stored internally as index tuples, but they
    are created with getters and setters that map the index tuples to
    and from SpaCy Span objects. Heads, relations and tails are
    retrieved from the triplets. Confidence numbers are stored as is.
    """
    extensions = [
        "relation_triplet_idxs",
        "relation_triplets",
        "relation_head",
        "relation_relation",
        "relation_tail",
        "relation_confidence",
    ]
    if not force and all(Doc.has_extension(ext) for ext in extensions):
        return  # job's done!

    Doc.set_extension("relation_triplet_idxs", default=[], force=force)
    Doc.set_extension(
        "relation_triplets",
        setter=lambda doc, triplets: setattr(
            doc._,
            "relation_triplet_idxs",
            [
                tuple(span_to_idx(span) for span in span_triplet.triplet)
                for span_triplet in triplets
            ],
        ),
        getter=lambda doc: DocTriplets(
            span_triplets=[
                SpanTriplet.from_tuple(
                    (
                        idx_to_span(idx[0], doc),
                        idx_to_span(idx[1], doc),
                        idx_to_span(idx[2], doc),
                    ),
                )
                for idx in doc._.relation_triplet_idxs
            ],
            doc=doc,
        ),
        force=force,
    )
    Doc.set_extension(
        "relation_head",
        getter=lambda doc: [t.subject for t in doc._.relation_triplets],
        force=force,
    )
    Doc.set_extension(
        "relation_relation",
        getter=lambda doc: [t.predicate for t in doc._.relation_triplets],
        force=force,
    )
    Doc.set_extension(
        "relation_tail",
        getter=lambda doc: [t.object for t in doc._.relation_triplets],
        force=force,
    )
    Doc.set_extension("relation_confidence", default=None, force=force)
