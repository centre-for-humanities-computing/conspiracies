from functools import partial
from typing import Iterable, List, Union, Tuple

from spacy.tokens import Doc, Span, Token
import jsonlines
from pathlib import Path
from conspiracies import SpanTriplet
from spacy.language import Language


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


def _doc_to_json(doc: Doc, triplets: List[SpanTriplet]):
    json = doc.to_json()
    json["semantic_triplets"] = [
        triplet.to_json(include_doc=False) for triplet in triplets
    ]
    return json


def _doc_from_json(json: dict, nlp: Language) -> Tuple[Doc, List[SpanTriplet]]:
    doc = Doc(nlp.vocab).from_json(json)
    triplets = [
        SpanTriplet.from_json(triplet_json, nlp=nlp, doc=doc)
        for triplet_json in json["semantic_triplets"]
    ]
    return doc, triplets


def docs_to_jsonl(
    docs: List[Doc], triplets: List[List[SpanTriplet]], path: Union[Path, str]
) -> None:
    """
    Write docs and triplets to a jsonl file.

    Args:
        docs (List[Doc]): a list of docs.
        triplets (List[List[SpanTriplet]]): a list of lists of triplets.
        path (Union[Path, str]): path to the jsonl file.
    """
    jsonl = [_doc_to_json(doc, triplets_) for doc, triplets_ in zip(docs, triplets)]
    with jsonlines.open(path, "w") as writer:
        writer.write_all(jsonl)


def docs_from_jsonl(
    path: Union[Path, str], nlp: Language
) -> Tuple[List[Doc], List[List[SpanTriplet]]]:
    """
    Read docs and triplets from a jsonl file.

    Args:
        path (Union[Path, str]): path to the jsonl file.
        nlp (Language): a spacy language model.

    Returns:
        Tuple[List[Doc], List[List[SpanTriplet]]]: a tuple of a list of docs and a list
            of lists of triplets.
    """
    docs = []
    triplets = []
    with jsonlines.open(path, "r") as reader:
        for json in reader:
            doc, _triplets = _doc_from_json(json, nlp)
            docs.append(doc)
            triplets.append(_triplets)
    return docs, triplets
