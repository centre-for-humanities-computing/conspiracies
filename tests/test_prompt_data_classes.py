import pytest
import spacy

from conspiracies.prompt_relation_extraction import PromptOutput, SpanTriplet


def test_prompt_output():
    prompt = PromptOutput(text="test", triplets=[["a", "b", "c"], ["d", "e", "f"]])
    assert prompt.text == "test"
    assert prompt.triplets == [("a", "b", "c"), ("d", "e", "f")]


class TestSpanTriplet:
    @pytest.fixture(scope="class")
    def nlp(self):
        nlp = spacy.blank("en")
        nlp.add_pipe("sentencizer")
        return nlp

    @pytest.fixture(scope="class")
    def span_triplets(self, nlp):
        doc = nlp("I am happy today")

        triplet = SpanTriplet(
            subject=doc[0:1],
            predicate=doc[1:2],
            object=doc[2:3],
            span=doc[:],
        )

        triplet_w_overlap = SpanTriplet(
            subject=doc[0:2],
            predicate=doc[1:2],
            object=doc[2:3],
            span=doc[:],
        )

        return [triplet, triplet_w_overlap]

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
