import pytest
import spacy


@pytest.fixture
def nlp_en():
    return spacy.load("en_core_web_sm")


@pytest.fixture
def nlp_da_w_coref(nlp_da):
    nlp_da.add_pipe("allennlp_coref")
    return nlp_da


@pytest.fixture
def nlp_da():
    return spacy.load("da_core_news_sm")
