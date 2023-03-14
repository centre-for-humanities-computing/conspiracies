import pytest
import spacy

from .test_data.prompt_data import load_gold_triplets


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


@pytest.fixture
def docs_with_triplets():
    return load_gold_triplets()
