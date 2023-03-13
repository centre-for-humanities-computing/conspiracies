from pathlib import Path

import pytest
import spacy
from conspiracies import SpanTriplet, docs_from_jsonl, docs_to_jsonl
from spacy.tokens import Doc

from .utils import docs_and_triplets  # noqa: F401


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
    docs, triplets = docs_from_jsonl(path, nlp=nlp)

    assert len(docs) == len(triplets)

    for doc, _triplets in zip(docs, triplets):
        assert isinstance(doc, Doc)
        for triplet in _triplets:
            assert isinstance(triplet, SpanTriplet)
        for triplet in _triplets:
            assert isinstance(triplet, SpanTriplet)


def test_docs_to_jsonl(nlp, docs_and_triplets):  # noqa: F811
    docs, triplets = docs_and_triplets
    docs_to_jsonl(docs, triplets, "test.jsonl")
    _docs, _triplets = docs_from_jsonl("test.jsonl", nlp=nlp)

    assert len(docs) == len(_docs)
    assert len(triplets) == len(_triplets)

    for doc, _doc in zip(docs, _docs):
        assert doc.text == _doc.text

    for triplets_, _triplets_ in zip(triplets, _triplets):
        for triplet, _triplet in zip(triplets_, _triplets_):
            assert triplet.is_string_match(_triplet)

    # remove the file
    Path("test.jsonl").unlink()
