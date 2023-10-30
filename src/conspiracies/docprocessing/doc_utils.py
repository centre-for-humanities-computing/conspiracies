from pathlib import Path
from typing import List, Union

import jsonlines
from spacy.language import Language
from spacy.tokens import Doc

from conspiracies.docprocessing.relationextraction.gptprompting import (
    DocTriplets,
    SpanTriplet,
)


def _doc_to_json(doc: Doc):
    if Doc.has_extension("relation_triplets"):
        triplets = doc._.relation_triplets
    else:
        triplets = []
    json = doc.to_json()
    json["semantic_triplets"] = [
        triplet.to_dict(include_doc=False) for triplet in triplets
    ]
    return json


def _doc_from_json(json: dict, nlp: Language) -> Doc:
    doc = Doc(nlp.vocab).from_json(json)
    triplets = [
        SpanTriplet.from_dict(triplet_json, nlp=nlp, doc=doc)
        for triplet_json in json["semantic_triplets"]
    ]
    if not Doc.has_extension("relation_triplets"):
        Doc.set_extension("relation_triplets", default=[], force=True)
    doc._.relation_triplets = DocTriplets(span_triplets=triplets, doc=doc)
    return doc


def docs_to_jsonl(
    docs: List[Doc],
    path: Union[Path, str],
) -> None:
    """Write docs and triplets to a jsonl file.

    Args:
        docs: a list of docs. If the docs have the extension
            "relation_triplets", the triplets will written to the jsonl file.
        path: path to the jsonl file.
    """
    jsonl = [_doc_to_json(doc) for doc in docs]
    with jsonlines.open(path, "w") as writer:
        writer.write_all(jsonl)


def docs_from_jsonl(
    path: Union[Path, str],
    nlp: Language,
) -> List[Doc]:
    """Read docs and triplets from a jsonl file.

    Args:
        path: path to the jsonl file.
        nlp: a spacy language model.

    Returns:
        A list of docs with the extension `doc._.relation_triplets` set.
    """
    if not Doc.has_extension("relation_triplets"):
        Doc.set_extension("relation_triplets", default=[], force=True)
    docs = []
    with jsonlines.open(path, "r") as reader:
        for json in reader:
            doc = _doc_from_json(json, nlp)
            docs.append(doc)
    return docs
