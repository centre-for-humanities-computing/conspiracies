import pytest  # noqa F401

from conspiracies.prompt_relation_extraction import (  # noqa F401
    PromptOutput,
    SpanTriplet,
)


def test_prompt_output():
    prompt = PromptOutput(text="test", triplets=[["a", "b", "c"], ["d", "e", "f"]])
    assert prompt.text == "test"
    assert prompt.triplets == [["a", "b", "c"], ["d", "e", "f"]]


class TestSpanTriplet:
    def test_visualize(self):
        pass

    def test_to_json(self):
        pass

    def test_from_json(self):
        pass

    def test_span_triplet_from_doc(self):
        pass

    def test_span_triplet_from_span_triplet(self):
        pass

    def test_span_triplet_from_text_triplet(self):
        pass
