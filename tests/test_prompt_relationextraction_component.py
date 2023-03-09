from typing import List

import pytest
from catalogue import registry
from spacy.language import Language

from conspiracies import SpanTriplet

from .test_prompt_template_parse_prompt import (
    MarkdownPromptTemplate1_expected_response,
    MarkdownPromptTemplate1_expected_triplets,
)
from .utils import nlp_da  # noqa F401

thread1 = """
@user1: This is a test tweet, I am commenting on something someone else said. END
@user1: @user2 this is not good enough END
    """

sample_threads = [thread1]
api_responses = [MarkdownPromptTemplate1_expected_response]
expected_triplets = [MarkdownPromptTemplate1_expected_triplets]


@pytest.mark.parametrize(
    "sample_thread, api_response, expected_triplets",
    list(*zip(sample_threads, api_responses, expected_triplets)),
)
def test_prompt_relation_extraction(
    nlp_da: Language,  # noqa F811
    sample_thread: str,
    api_response: str,
    expected_triplets: List[SpanTriplet],
):
    nlp = nlp_da

    @registry.prompt_apis.register("conspiracies", "test_api")
    def create_test_api(prompt_template, api_key, model_name, api_kwargs):
        """a test api for testing purposes.

        assumes prompttemplate is markdown_template_2
        """

        def test_api(target):
            return api_response

        return test_api

    # test that component can be added.
    config = {
        "prompt_template": "conspiracies/markdown_template_2",
        "examples": None,
        "task_description": None,
        "model_name": "text-davinci-002",
        "backend": "test_api",
        "api_key": "empty-key",
        "api_kwargs": {
            "max_tokens": 500,
            "temperature": 0.7,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "stop": ["\n", "Tweet:"],
        },
        "force": True,
    }
    nlp.add_pipe("prompt_relation_extraction", config=config)

    doc = nlp(sample_thread)

    assert doc._.prompt_relation_extraction is not None
    for triplet in doc._.relations_triplets:
        assert isinstance(triplet, SpanTriplet)
        triplet in expected_triplets
