from pathlib import Path

import pytest
import spacy
from conspiracies import docs_from_jsonl, docs_to_jsonl
from conspiracies.docprocessing.relationextraction.gptprompting import (
    DocTriplets,
    SpanTriplet,
)
from spacy.tokens import Doc

from .utils import docs_with_triplets  # noqa: F401


@pytest.fixture()
def path():
    data_path = Path(__file__).parent / "test_data" / "triplets.jsonl"
    return data_path


@pytest.fixture()
def nlp():
    nlp = spacy.blank("en")
    nlp.add_pipe("sentencizer")
    return nlp


def test_docs_from_jsonl(path, nlp):
    docs = docs_from_jsonl(path, nlp=nlp)

    for doc in docs:
        assert isinstance(doc, Doc)
        triplets = doc._.relation_triplets
        for triplet in triplets:
            assert isinstance(triplet, SpanTriplet)
        for triplet in triplets:
            assert isinstance(triplet, SpanTriplet)


def test_docs_to_jsonl(nlp, docs_with_triplets):  # noqa: F811
    docs = docs_with_triplets
    docs_to_jsonl(docs, "test.jsonl", include_span_heads=False)
    _docs = docs_from_jsonl("test.jsonl", nlp=nlp)

    assert len(docs) == len(_docs)

    for doc, _doc in zip(docs, _docs):
        assert doc.text == _doc.text
        triplets = doc._.relation_triplets
        _triplets = _doc._.relation_triplets

        assert isinstance(triplets, DocTriplets)
        assert isinstance(_triplets, DocTriplets)

        assert len(triplets) == len(_triplets)
        for triplet, _triplet in zip(triplets, _triplets):
            assert triplet.is_string_match(_triplet)

    # clean up by removing the file
    Path("test.jsonl").unlink()
