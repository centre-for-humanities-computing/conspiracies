from pathlib import Path
from typing import List, Union, Iterable, Tuple

import jsonlines
from spacy.language import Language
from spacy.tokens import Doc

from conspiracies.docprocessing.relationextraction.data_classes import (
    install_extensions,
)
from conspiracies.docprocessing.relationextraction.gptprompting import (
    DocTriplets,
    SpanTriplet,
)
from conspiracies.document import Document


def _doc_to_json(
    doc: Union[Doc, Tuple[Doc, Union[str, Document]]],
    include_span_heads=True,
):
    if isinstance(doc, Tuple):
        if isinstance(doc[1], str):
            doc, id_ = doc
            timestamp = None
        elif isinstance(doc[1], Document):
            doc, src_doc = doc
            id_ = src_doc.id
            timestamp = src_doc.timestamp.isoformat()
        else:
            raise TypeError(f"Unexpected input type {type(doc[1])}")
    elif "doc_metadata" in doc.user_data:
        id_ = doc.user_data["doc_metadata"]["id"]
        timestamp = doc.user_data["doc_metadata"]["timestamp"]
    else:
        id_ = None
        timestamp = None
    if Doc.has_extension("relation_triplets"):
        triplets = doc._.relation_triplets
    else:
        triplets = []
    json = doc.to_json()
    if id_ is not None:
        json["id"] = id_
    if timestamp is not None:
        json["timestamp"] = timestamp
    json["semantic_triplets"] = [
        triplet.to_dict(include_doc=False, include_span_heads=include_span_heads)
        for triplet in triplets
    ]
    return json


def _doc_from_json(json: dict, nlp: Language) -> Doc:
    doc = Doc(nlp.vocab).from_json(json)
    triplets = [
        SpanTriplet.from_dict(triplet_json, nlp=nlp, doc=doc)
        for triplet_json in json["semantic_triplets"]
    ]
    if not Doc.has_extension("relation_triplets"):
        install_extensions()
    doc._.relation_triplets = DocTriplets(span_triplets=triplets, doc=doc)
    return doc


def docs_to_jsonl(
    docs: Iterable[Union[Doc, Tuple[Doc, Union[str, Document]]]],
    path: Union[Path, str],
    append=False,
    include_span_heads=True,
) -> None:
    """Write docs and triplets to a jsonl file.

    Args:
        docs: a list of docs. If the docs have the extension
            "relation_triplets", the triplets will written to the jsonl file.
        path: path to the jsonl file.
        append: whether to append to file instead of overwriting
        include_span_heads: whether to output an "extracted_head" field in the JSON
            output from :class:`HeadWordExtractionComponent`
    """
    with jsonlines.open(path, "a" if append else "w") as writer:
        writer.write_all(
            _doc_to_json(doc, include_span_heads=include_span_heads) for doc in docs
        )


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
        install_extensions(force=True)
    docs = []
    with jsonlines.open(path, "r") as reader:
        for json in reader:
            doc = _doc_from_json(json, nlp)
            docs.append(doc)
    return docs
