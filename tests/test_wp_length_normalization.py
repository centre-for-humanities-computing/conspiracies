import pytest

from .utils import nlp_da  # noqa

from conspiracies.preprocessing.wordpiece_length_normalization import (
    wordpiece_length_normalization,
)
from transformers import AutoTokenizer


@pytest.fixture()
def tokenizer():
    return AutoTokenizer.from_pretrained("alexandrainst/da-sentiment-base")


def test_wp_length_normalization_short(nlp_da, tokenizer):  # noqa
    short_texts = ["hello there"]
    norm_text = wordpiece_length_normalization(short_texts, nlp_da, tokenizer)
    norm_text = list(norm_text)

    assert len(norm_text) == 1, "a short text should only result of one normalized text"
    assert norm_text[0] == short_texts[0], "a short text should result the same text"


def test_wp_length_normalization_long(nlp_da, tokenizer):  # noqa
    long_text = ["Hej mit navn er Kenneth. " * 200]
    norm_text = wordpiece_length_normalization(long_text, nlp_da, tokenizer)
    norm_text = list(norm_text)

    assert len(norm_text) > 1, "a long text should be split into multiple texts"
    assert norm_text[0] == norm_text[1], "splits are not consistent"


def test_wp_length_normalization_no_sent(nlp_da, tokenizer):  # noqa
    # irregular example without sentences
    irregular_text = ["hello " * 600]
    norm_text = wordpiece_length_normalization(irregular_text, nlp_da, tokenizer)
    norm_text = list(norm_text)

    assert (
        len(norm_text) == 2
    ), "irregular text (['hello ' * 600]) should result in 2 texts"
