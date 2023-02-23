from spacy.tokens import Doc

from conspiracies import SpanTriplet
from conspiracies.data import load_gold_triplets


def test_load_gold_triplets():
    docs, triplets = load_gold_triplets()
    for doc, triplet in zip(docs, triplets):
        assert isinstance(doc, Doc)
        for span_triplet in triplet:
            assert isinstance(span_triplet, SpanTriplet)
