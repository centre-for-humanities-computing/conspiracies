"""
a sample script for matching the extracted semantic triplets from the prompt output with
the original text.
"""

import json
from copy import copy
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

import spacy
from pydantic import BaseModel
from spacy import displacy
from spacy.tokens import Doc, Span


def subspan_of_span(
    subspan: Union[Span, Doc], span: Union[Span, Doc], lowercase: bool = False
) -> Optional[Span]:
    """Checks if a token is contained in a span. This function assumes that the token
    is not from the span and therefore

    Args:
        subspan (Union[Span, Doc]): a spacy span or doc to check if it is contained
            wihtin span.
        span (Union[Span, Doc]): a spacy span (or Doc) to check if the subspan is
            contained within.

    Returns:
        Optional[Span]: The subsspan of span if it is contained within span, else None.
    """
    span_len = len(subspan)
    _spans = [span[i : i + span_len] for i in range(len(span) - span_len + 1)]
    subspan_text = subspan.text.lower() if lowercase else subspan.text
    for _span in _spans:
        _span_text = _span.text.lower() if lowercase else _span.text
        if subspan_text == _span_text:
            return _span
    return None


class SpanTriplet(BaseModel):
    """A class for a semantic triplet with spans.

    Args:
        subject (Span): Subject of the triplet.
        predicate (Span): Predicate of the triplet.
        object (Span): Object of the triplet.
    """

    subject: Span
    predicate: Span
    object: Span

    class Config:
        arbitrary_types_allowed = True

    def visualize(self):
        """Visualizes the triplet using displacy."""

        colors = {
            "SUBJECT": "#7aecec",
            "PREDICATE": "#ff9561",
            "OBJECT": "#aa9cfc",
        }

        doc = self.subject.doc
        doc_copy = copy(doc)
        options = {"ents": ["SUBJECT", "PREDICATE", "OBJECT"], "colors": colors}
        doc_copy.ents = [self.subject, self.predicate, self.object]
        displacy.render(doc_copy, style="ent", options=options)


class StringTriplet(BaseModel):
    """A class for semantic triplets.

    Args:
        subject (str): Subject of the triplet.
        predicate (str): Predicate of the triplet.
        object (str): Object of the triplet.
    """

    subject: str
    predicate: str
    object: str

    class Config:
        anystr_strip_whitespace = True  # remove trailing whitespace

    @staticmethod
    def from_tuple(triplet: Tuple[str, str, str]) -> "StringTriplet":
        """Creates a StringTriplet object from a tuple.

        Args:
            triplet (tuple): A tuple of strings.

        Returns:
            StringTriplet: A StringTriplet object.
        """
        return StringTriplet(
            subject=triplet[0], predicate=triplet[1], object=triplet[2]
        )

    @staticmethod
    def span_triplet_from_text_triplet(
        triplet: Tuple[str, str, str],
        span: Union[Span, Doc],
        lowercase: Optional[bool] = None,
    ) -> Optional[SpanTriplet]:
        """Checks if the triplet contained within the doc based on text overlap.

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
        if lowercase is None:
            spantriplet = StringTriplet.span_triplet_from_text_triplet(
                triplet, span, lowercase=False
            )
            if spantriplet is not None:
                return spantriplet
            return StringTriplet.span_triplet_from_text_triplet(
                triplet, span, lowercase=True
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
        subj_span = span.char_span(subj_start, subj_end, label="SUBJECT")
        pred_span = span.char_span(start_pred, end_pred, label="PREDICATE")
        obj_span = span.char_span(obj_start, obj_end, label="OBJECT")

        if subj_span is None or pred_span is None or obj_span is None:
            return None
        return SpanTriplet(subject=subj_span, predicate=pred_span, object=obj_span)

    @staticmethod
    def span_triplet_from_span_triplet(
        triplet: Tuple[Span, Span, Span],
        span: Union[Span, Doc],
        lowercase: Optional[bool] = None,
    ) -> Optional[SpanTriplet]:
        """Checks if the triplet contained within the doc based on overlap of span
        tokens.

        Args:
            triplet (Tuple[Span, Span, Span]): A semantic triplet to check if contained
                within the span. A triplet contains subject, predicate, and object (in
                that order).
            span (Union[Span, Doc]): A spacy span or doc.
            lowercase (Optional[bool]): Whether to use lowercase comparison. Defaults to
                None. If None it will first try to match the triplet in the original
                case and then fallback to lowercase.

        Returns:
            Optional[SpanTriplet]: A SpanTriplet object. Returns None if the triplet is
                not contained in the span.
        """
        if lowercase is None:
            spantriplet = StringTriplet.span_triplet_from_span_triplet(
                triplet, span, lowercase=False
            )
            if spantriplet is not None:
                return spantriplet
            return StringTriplet.span_triplet_from_span_triplet(
                triplet, span, lowercase=True
            )

        subj, pred, obj = triplet
        subj_span = subspan_of_span(subj, span, lowercase=lowercase)
        if subj_span is None:
            return None

        pred_span = subspan_of_span(pred, span, lowercase=lowercase)
        if pred_span is None:
            return None

        obj_span = subspan_of_span(obj, span, lowercase=lowercase)
        if obj_span is None:
            return None

        return SpanTriplet(subject=subj_span, predicate=pred_span, object=obj_span)

    def span_triplet_from_doc(
        self,
        doc: Doc,
        nlp: Optional[spacy.Language] = None,
        method: Optional[Literal["span", "text"]] = None,
        lowercase: Optional[bool] = None,
    ) -> Optional[SpanTriplet]:
        """Converts the StringTriplet to a SpanTriplet.
        First checks if the span is contained within a singular sentence, then it checks
        if the span is contained within the entire document.

        Args:
            doc (Doc): Document of the text.
            nlp (Optional[spacy.Language]): Spacy language model. Defaults to None. In
                which case it will create a blank spacy model based on the language of
                the doc.
            method (Optional[Literal["span", "text"]]): Whether to use the span or text
                comparison to find valid span triplets. Defaults to None. If None it
                will first try to match the triplet based on the span and then fallback
                to text comparison.
            lowercase (Optional[bool]): Whether to lowercase the text before comparison.
                Defaults to None. If None it will first try to match the triplet in the
                original case and then fallback to lowercase.

        Returns:
            Optional[SpanTriplet]: A SpanTriplet object. Returns None if the triplet is
                not contained in the span.
        """
        if method is None:
            span_triplet = self.span_triplet_from_doc(
                doc, nlp=nlp, method="span", lowercase=lowercase
            )
            if span_triplet is not None:
                return span_triplet
            return self.span_triplet_from_doc(
                doc, nlp=nlp, method="text", lowercase=lowercase
            )

        span_triplet_from_mapping = {
            "span": self.span_triplet_from_span_triplet,
            "text": self.span_triplet_from_text_triplet,
        }

        span_triplet_from = span_triplet_from_mapping[method]

        if nlp is None:
            nlp = spacy.blank(doc.lang_)

        triplet = [nlp(token) for token in [self.subject, self.predicate, self.object]]
        for sent in doc.sents:
            span_triplet = span_triplet_from(triplet, sent, lowercase=lowercase)
            if span_triplet is not None:
                return span_triplet
        return self.span_triplet_from_span(doc)

    def contained_within_span(
        self,
        span: Span,
        character_fallback: bool = True,
        lowercase_fallback: bool = True,
        nlp: Optional[spacy.Language] = None,
    ):
        """Checks if the triplet is contained in the span.

        Args:
            span (Span): Span to check.
            character_fallback (bool): Whether to fallback to character comparison after
                token comparison. Defaults to True.
            lowercase_fallback (bool): Whether to fallback to lowercase comparison.
                Defaults to True.
            nlp (Optional[spacy.Language]): Spacy language model. Defaults to None.
        """

        subj, pred, obj = [
            nlp(token) for token in [self.subject, self.predicate, self.object]
        ]
        subj_span = subspan_of_span(subj, span)
        pred_span = subspan_of_span(pred, span)
        obj_span = subspan_of_span(obj, span)

        if character_fallback:
            idx_subject, idx_predicate, idx_object = self.contained_within_text(
                span.text, lowercase_fallback
            )
            if idx_subject != -1 and idx_predicate != -1 and idx_object != -1:
                return idx_subject, idx_predicate, idx_object

    def span_triplet_from_span(self, span: Union[Span, Doc]) -> Optional[SpanTriplet]:
        """Converts the StringTriplet to a SpanTriplet.

        Args:
            span (Union[Span, Doc]): Span to check.

        Returns:
            Optional[SpanTriplet]: A SpanTriplet object. Returns None if the triplet is
                not contained in the span.
        """
        idx_subj, idx_pred, idx_obj = self.contained_within_text(span)
        if idx_subj == -1 or idx_pred == -1 or idx_obj == -1:
            return None

        subj_span = span.char_span(
            idx_subj, idx_subj + len(self.subject), label="SUBJECT"
        )
        pred_span = span.char_span(
            idx_pred, idx_pred + len(self.predicate), label="PREDICATE"
        )
        obj_span = span.char_span(idx_obj, idx_obj + len(self.object), label="OBJECT")

        if subj_span is None or pred_span is None or obj_span is None:
            raise ValueError("SpanTriplet cannot be created.")

        return SpanTriplet(subject=subj_span, predicate=pred_span, object=obj_span)

    def span_triplet_from_doc(self, doc: Doc) -> Optional[SpanTriplet]:
        """Converts the StringTriplet to a SpanTriplet.
        First checks if the span is contained within a singular sentence, then it checks
        if the span is contained within the entire document.

        Args:
            doc (Doc): Document of the text.

        Returns:
            Optional[SpanTriplet]: A SpanTriplet object. Returns None if the triplet is
                not contained in the span.
        """
        for sent in doc.sents:
            span_triplet = self.span_triplet_from_span(sent)
            if span_triplet is not None:
                return span_triplet

        return self.span_triplet_from_span(doc)


def read_prompts(path: Path) -> List[Dict[str, Any]]:
    """Reads prompts from a JSON file.

    Args:
        path (Path): Path to the JSON file.

    Returns:
        list: List of prompts.
    """
    with open(path, "r") as f:
        prompts = json.load(f)
    return prompts


if __name__ == "__main__":
    path = Path(__file__).parent.parent.parent / "data" / "gpt_predictions_compare.json"
    prompts = read_prompts(path)

    for prompt in prompts:

        triplets = prompt["gold_tagging"]
        triplet = StringTriplet.from_tuple(triplets[0])
        text = prompt["tweet"]

        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
        span_triplet = triplet.span_triplet_from_doc(doc)

        # visualize the triplet
        span_triplet.visualize()
