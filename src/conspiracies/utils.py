from pathlib import Path
from typing import List, Tuple, Union

import jsonlines
from spacy.language import Language
from spacy.tokens import Doc

from .prompt_relation_extraction import SpanTriplet


def _doc_to_json(doc: Doc, triplets: List[SpanTriplet]):
    json = doc.to_json()
    json["semantic_triplets"] = [
        triplet.to_dict(include_doc=False) for triplet in triplets
    ]
    return json


def _doc_from_json(json: dict, nlp: Language) -> Tuple[Doc, List[SpanTriplet]]:
    doc = Doc(nlp.vocab).from_json(json)
    triplets = [
        SpanTriplet.from_dict(triplet_json, nlp=nlp, doc=doc)
        for triplet_json in json["semantic_triplets"]
    ]
    return doc, triplets


def docs_to_jsonl(
    docs: List[Doc],
    triplets: List[List[SpanTriplet]],
    path: Union[Path, str],
) -> None:
    """Write docs and triplets to a jsonl file.

    Args:
        docs (List[Doc]): a list of docs.
        triplets (List[List[SpanTriplet]]): a list of lists of triplets.
        path (Union[Path, str]): path to the jsonl file.
    """
    jsonl = [_doc_to_json(doc, triplets_) for doc, triplets_ in zip(docs, triplets)]
    with jsonlines.open(path, "w") as writer:
        writer.write_all(jsonl)


def docs_from_jsonl(
    path: Union[Path, str],
    nlp: Language,
) -> Tuple[List[Doc], List[List[SpanTriplet]]]:
    """Read docs and triplets from a jsonl file.

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
