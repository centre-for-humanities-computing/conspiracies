import pytest
import spacy
from spacy import Vocab

from conspiracies.docprocessing.relationextraction.gptprompting import (
    DocTriplets,
    SpanTriplet,
    StringTriplet,
)
from conspiracies.docprocessing.relationextraction import data_classes
from spacy.tokens import Doc


def test_relationextraction_doc_extension():
    """Verifies the behavior of the relation triplet extension and the lambdas
    that back it."""
    data_classes.install_extensions(force=True)

    words = "this is a test . the test seems cool".split()
    vocab = Vocab(strings=words)
    test_doc = Doc(vocab, words=words)

    this = test_doc[0:1]
    is_ = test_doc[1:2]
    a_test = test_doc[2:4]
    the_test = test_doc[5:7]
    seems = test_doc[7:8]
    cool = test_doc[8:9]

    triplets = DocTriplets(
        span_triplets=[
            SpanTriplet.from_tuple((this, is_, a_test)),
            SpanTriplet.from_tuple((the_test, seems, cool)),
        ],
        doc=test_doc,
    )

    test_doc._.relation_triplets = triplets

    # check setter/getter mirroring
    assert test_doc._.relation_triplets == triplets

    # check index extension
    assert test_doc._.relation_triplet_idxs == [
        ((0, 1), (1, 2), (2, 4)),
        ((5, 7), (7, 8), (8, 9)),
    ]

    # check heads, relations and tails
    assert test_doc._.relation_head == [this, the_test]
    assert test_doc._.relation_relation == [is_, seems]
    assert test_doc._.relation_tail == [a_test, cool]


@pytest.fixture
def nlp():
    nlp = spacy.blank("en")
    nlp.add_pipe("sentencizer")
    return nlp


@pytest.fixture
def doc(nlp):
    return nlp("I am happy today")


@pytest.fixture
def span_triplets(doc):
    triplet = SpanTriplet(
        subject=doc[0:1],
        predicate=doc[1:2],
        object=doc[2:3],
    )

    triplet_w_overlap = SpanTriplet(
        subject=doc[0:2],
        predicate=doc[1:2],
        object=doc[2:3],
    )

    return [triplet, triplet_w_overlap]


@pytest.fixture
def string_triplets(doc):
    text = doc.text

    triplet = StringTriplet(
        subject="I",
        predicate="am",
        object="happy",
        text=text,
    )

    triplet_w_overlap = StringTriplet(
        subject="I am",
        predicate="am",
        object="happy",
        text=text,
    )

    return [triplet, triplet_w_overlap]


class TestSpanTriplet:
    def test_visualize(self, span_triplets):
        for triplet in span_triplets:
            triplet.visualize()

    def test_equal(self, span_triplets):
        triplet1, triplet2 = span_triplets
        assert triplet1 != triplet2
        assert triplet1 == triplet1

    def test_to_from_dict(self, span_triplets, nlp):
        for triplet in span_triplets:
            d = triplet.to_dict()
            _triplet = SpanTriplet.from_dict(d, nlp)
            assert triplet.is_string_match(_triplet)

    @pytest.mark.parametrize(
        "text,str_triplet",
        [
            ("jeg er glad i dag", ["jeg", "er", "glad"]),
            ("jeg er glad i dag", ["jeg", "er", "glad i dag"]),
            ("Kenneth er glad i   dag", ["Kenneth", "er", "glad i   dag"]),
            ("Kenneth er glad i dag", ["Kenneth", "er", "glad i dag"]),
        ],
    )
    def test_from_doc(self, nlp, text, str_triplet):
        doc = nlp(text)
        triplet = SpanTriplet.from_doc(str_triplet, doc=doc, nlp=nlp)

        assert triplet.subject.text == str_triplet[0]
        assert triplet.predicate.text == str_triplet[1]
        assert triplet.object.text == str_triplet[2]


class TestDocTriplet:
    def test_init(self, span_triplets):
        doc = span_triplets[0].doc
        # test empty triplets
        doc_triplets_empty = DocTriplets(span_triplets=[], doc=doc)
        assert len(doc_triplets_empty) == 0
        doc_triplets = DocTriplets(span_triplets=span_triplets, doc=doc)
        assert len(doc_triplets) == 2

        # test add
        new_doc_triplets = doc_triplets_empty + doc_triplets
        assert new_doc_triplets == doc_triplets

        doc_triplets_ = [doc_triplets_empty, doc_triplets, new_doc_triplets]
        for dt in doc_triplets_:
            assert isinstance(dt.doc, Doc)

    def test_doc_triplet_from_str_triplets(self, string_triplets, doc: Doc):
        doc_triplets = DocTriplets.from_str_triplets(triplets=string_triplets, doc=doc)
        assert len(doc_triplets) == 2

    def test_score_relations(self, nlp: spacy.Language):
        doc = nlp("I am happy today I am happy today")

        triplet = SpanTriplet(
            subject=doc[0:1],
            predicate=doc[1:2],
            object=doc[2:3],
        )

        # exact match
        doc_triplets_gold = DocTriplets(span_triplets=[triplet], doc=doc)
        doc_triplets_pred = DocTriplets(span_triplets=[triplet], doc=doc)

        scores = doc_triplets_pred.score_relations(doc_triplets_gold)
        scores["exact_span_match"] = 1
        scores["exact_text_match"] = 1
        scores["normalized_span_overlap"] = 1
        scores["normalized_char_overlap"] = 1

        # exact string match
        triplet_string_match = SpanTriplet(
            subject=doc[4:5],
            predicate=doc[5:6],
            object=doc[6:7],
        )

        doc_triplets_pred = DocTriplets(span_triplets=[triplet_string_match], doc=doc)
        scores = doc_triplets_pred.score_relations(doc_triplets_gold)
        scores["exact_span_match"] = 0
        scores["exact_text_match"] = 1
        scores["normalized_span_overlap"] = 0
        scores["normalized_char_overlap"] = 1

        # partial span match
        triplet_part_span = SpanTriplet(
            subject=doc[0:1],
            predicate=doc[1:2],
            object=doc[2:4],
        )

        doc_triplets_pred = DocTriplets(span_triplets=[triplet_part_span], doc=doc)
        scores = doc_triplets_pred.score_relations(doc_triplets_gold)
        scores["exact_span_match"] = 0
        scores["exact_text_match"] = 0
        scores["normalized_span_overlap"] = 0
        scores["normalized_char_overlap"] = 0.8

        # partial string match
        triplet_part_char = SpanTriplet(
            subject=doc[4:5],
            predicate=doc[5:6],
            object=doc[6:8],
        )

        doc_triplets_pred = DocTriplets(span_triplets=[triplet_part_char], doc=doc)
        scores = doc_triplets_pred.score_relations(doc_triplets_gold)
        scores["exact_span_match"] = 0
        scores["exact_text_match"] = 0
        scores["normalized_span_overlap"] = 0
        scores["normalized_char_overlap"] = 0.8
