"""
a sample script for matching the extracted semantic triplets from the prompt output with
the original text.
"""

import json
from copy import copy
from functools import partial
from pathlib import Path
from typing import Any, Dict, Iterable, List, Literal, Optional, Tuple, Union

import spacy
from pydantic import BaseModel
from spacy import displacy
from spacy.tokens import Doc, Span, Token
from wasabi import msg


def get_text(span: Iterable[Token], ignore_spaces: bool, lowercase: bool) -> str:
    """Gets the text of a span or doc.

    Args:
        span (Union[Span, Doc]): a spacy span or doc.

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
    """Checks if a token is contained in a span. This function assumes that the token
    is not from the span and therefore

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
        doc = span[0].doc
        potential_spans = [doc[span[0].i : span[-1].i + 1] for span in potential_spans]

    return potential_spans


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
    span: Union[Span, Doc]

    class Config:
        arbitrary_types_allowed = True

    def visualize(self):
        """Visualizes the triplet using displacy."""

        colors = {
            "SUBJECT": "#7aecec",
            "PREDICATE": "#ff9561",
            "OBJECT": "#aa9cfc",
        }

        if isinstance(self.span, Doc):
            doc = self.span
            start, end = 0, len(doc)
        else:
            doc = self.span.doc
            start, end = self.span.start, self.span.end

        copy_doc = copy(doc)  # to avoid overwriting the original doc
        options = {"ents": ["SUBJECT", "PREDICATE", "OBJECT"], "colors": colors}
        copy_doc.ents = [self.subject, self.predicate, self.object]
        viz_doc = copy_doc[start:end].as_doc()
        displacy.render(viz_doc, style="ent", options=options)


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
        return SpanTriplet(
            subject=subj_span, predicate=pred_span, object=obj_span, span=span
        )

    @staticmethod
    def span_triplet_from_span_triplet(
        triplet: Tuple[Span, Span, Span],
        span: Union[Span, Doc],
        lowercase: Optional[bool] = None,
        ignore_spaces: Optional[bool] = True,
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
            ignore_spaces (Optional[bool]): Whether to ignore spaces when comparing
                spans. Defaults to True. If None it will first try to match the triplet
                with spaces and then fallback to ignoring spaces.

        Returns:
            Optional[SpanTriplet]: A SpanTriplet object. Returns None if the triplet is
                not contained in the span.
        """
        if isinstance(span, Doc):
            span = span[:]
        if ignore_spaces is None:
            spantriplet = StringTriplet.span_triplet_from_span_triplet(
                triplet, span, lowercase=lowercase, ignore_spaces=False
            )
            if spantriplet is not None:
                return spantriplet
            return StringTriplet.span_triplet_from_span_triplet(
                triplet, span, lowercase=lowercase, ignore_spaces=True
            )
        if lowercase is None:
            spantriplet = StringTriplet.span_triplet_from_span_triplet(
                triplet, span, lowercase=False
            )
            if spantriplet is not None:
                return spantriplet
            return StringTriplet.span_triplet_from_span_triplet(
                triplet, span, lowercase=True
            )

        _subspan_of_span = partial(
            subspan_of_span, lowercase=lowercase, ignore_spaces=ignore_spaces
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
            pred_span = cand_pred_span[0]  # assume first match is correct

        # label spans
        subj_span.label_ = "SUBJECT"
        pred_span.label_ = "PREDICATE"
        obj_span.label_ = "OBJECT"

        return SpanTriplet(
            subject=subj_span, predicate=pred_span, object=obj_span, span=span
        )

    def span_triplet_from_doc(
        self,
        doc: Doc,
        nlp: Optional[spacy.Language] = None,
        method: Optional[Literal["span", "text"]] = None,
        lowercase: Optional[bool] = None,
        ignore_spaces: Optional[bool] = True,
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
            ignore_spaces (Optional[bool]): Whether to ignore spaces when comparing
                spans. Defaults to True. If None it will first try to match the triplet
                with spaces and then fallback to ignoring spaces.

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

        if nlp is None and method == "span":
            nlp = spacy.blank(doc.lang_)
            triplet = tuple(
                [
                    doc[:]
                    for doc in nlp.pipe([self.subject, self.predicate, self.object])
                ]
            )
        else:
            triplet = (self.subject, self.predicate, self.object)  # type: ignore

        span_triplet_from_mapping = {
            "span": self.span_triplet_from_span_triplet,
            "text": self.span_triplet_from_text_triplet,
        }

        span_triplet_from = span_triplet_from_mapping[method]

        for sent in doc.sents:
            span_triplet = span_triplet_from(
                triplet, sent, lowercase=lowercase  # type: ignore
            )
            if span_triplet is not None:
                return span_triplet
        return span_triplet_from(triplet, doc, lowercase=lowercase)  # type: ignore


class PromptOutput(BaseModel):
    """
    A prompt output.

    Args:
        input_text (str): The target of the prompt.
        triplets (List[Tuple[str, str, str]]): A list of triplets.
    """

    input_text: str
    triplets: List[Tuple[str, str, str]]


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


def test_prompt(prompt: PromptOutput, nlp: spacy.Language) -> None:
    doc = nlp(prompt.input_text)
    for triplet in prompt.triplets:
        triplet = StringTriplet.from_tuple(triplet)  # type: ignore

        span_triplet = triplet.span_triplet_from_doc(doc)  # type: ignore

        if span_triplet is None:
            msg.warn(f"Could not find triplet {triplet} in {prompt.input_text}")
            continue
        # visualize the triplet
        span_triplet.visualize()  # type: ignore


if __name__ == "__main__":
    path = Path(__file__).parent.parent.parent / "data" / "gpt_predictions_compare.json"
    prompts = read_prompts(path)
    nlp = spacy.load("en_core_web_sm")

    # try with a single prompt at a time
    # prompt1 = PromptOutput(
    #     input_text="@Berry1952K: @BibsenSkyt @JakobEllemann Synes det er total mangel på respekt for alle andre partiledere.",  # noqa: E501
    #     triplets=[["@Berry1952K", "Synes", "det er total mangel på respekt"]],
    # )

    # test_prompt(prompt1, nlp)

    # prompt2 = PromptOutput(
    #     input_text=prompts[1]["tweet"],
    #     triplets=prompts[1]["gold_tagging"],
    # )

    # test_prompt(prompt2, nlp) # gold is wrong in the third triplet

    # prompt_test = PromptOutput(
    #     input_text=prompts[16]["tweet"],
    #     triplets=prompts[16]["gold_tagging"],
    # )

    # test_prompt(prompt_test, nlp)

    for i, prompt in enumerate(prompts):
        msg.info(f"Prompt {i}")
        _prompt = PromptOutput(
            input_text=prompt["tweet"], triplets=prompt["gold_tagging"]
        )
        test_prompt(_prompt, nlp)

    # prompt 1: gold is wrong in the third triplet
    # prompt 2: error in last triplet (umhu vs omhu)
    # prompt 7: error in predicate (er ikke vs er jo ikke)
    # [SOLVED] prompt 9: triplet 4: alignment error: potential try to use the closest match instead of the
    # first match
    # prompt 10: Error in gold (inreb vs indgreb)
    # prompt 11: error caused by error tweet (missing verb)
    # [SOLVED] prompt 12: check third triplet (er is not in between the two others)
    # might be worth to make the "in-between to a dyanamic min/max"
    # prompt 14: Error in gold (mundbing vs mundbind)
    # [Will not fix] prompt 15: triplet 3, wrong extraction, can't see a way to fix
    # this one though. Naturally could do prefer predicate closest to the subject, but
    # not sure if that generalize
    # [SOLVED] prompt 16: check triplet 2 - error with matchup when there is double
    # spaces
    # prompt 18: error in hold "har ikke" vs "ikke har"
    # prompt 21: potential error in gold (subject contained in predicate)
    # prompt 23: error in gold
    # [SOLVED] prompt 24: triplet 2: extraction error. Prefer subject closest to (but before)
    # the object (try to post hoc fix this)
    # prompt 24: triplet 3: error in gold (ikke gjort vs ikke rigtig gjort)
    # prompt 25: error in gold (det her møde vs det møde)
    # prompt 26: error in gold (ender vi med vs ender med)
    # prompt 28: error in gold (missing alligevel)
