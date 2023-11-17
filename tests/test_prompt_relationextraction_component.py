from typing import List

import pytest
from confection import registry
from conspiracies.docprocessing.relationextraction.gptprompting import (
    SpanTriplet,
    StringTriplet,
)
from spacy.language import Language

from .test_prompt_template_parse_prompt import (
    MarkdownPromptTemplate1_expected_response,
    MarkdownPromptTemplate1_expected_triplets,
)
import spacy
from .utils import docs_with_triplets, nlp_da  # noqa F401

thread1 = """
@user1: This is a test tweet, I am commenting on something someone else said. END
@user1: @user2 this is not good enough END
    """

sample_threads = [thread1]
api_responses = [MarkdownPromptTemplate1_expected_response]
expected_triplets = [MarkdownPromptTemplate1_expected_triplets]


@pytest.mark.parametrize(
    "sample_thread, api_response, expected_triplets",
    list(zip(sample_threads, api_responses, expected_triplets)),
)
def test_prompt_relation_extraction(
    nlp_da: Language,  # noqa F811
    sample_thread: str,
    api_response: str,
    expected_triplets: List[StringTriplet],
):
    nlp = nlp_da
    expected_span_triplets = [
        SpanTriplet.from_doc(triplet, nlp(sample_thread))
        for triplet in expected_triplets
    ]

    @registry.prompt_apis.register("test_api")  # type: ignore
    def create_test_api(prompt_template, api_key, model_name, api_kwargs):
        """A test api for testing purposes.

        assumes prompttemplate is markdown_template_2
        """

        def test_api(target):
            return [api_response]

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
        },
        "force": True,
    }
    nlp.add_pipe("conspiracies/prompt_relation_extraction", config=config)

    doc = nlp(sample_thread)

    doc_relation_triplets = doc._.relation_triplets
    assert doc_relation_triplets is not None and len(doc_relation_triplets) > 0
    for triplet in doc_relation_triplets:
        assert isinstance(triplet, SpanTriplet)
        triplet in expected_span_triplets


def test_create_pipeline():
    nlp = spacy.blank("da")
    config = {"api_key": ""}

    nlp.add_pipe("conspiracies/prompt_relation_extraction", config=config)

    # remove pipeline
    nlp.remove_pipe("conspiracies/prompt_relation_extraction")

    # add pipeline with speicifc config
    config = {
        "prompt_template": "conspiracies/template_1",
        "examples": None,
        "task_description": None,
        "model_name": "text-davinci-002",
        "backend": "conspiracies/openai_gpt3_api",
        "api_key": "",
        "split_doc_fn": None,
        "api_kwargs": {
            "max_tokens": 500,
            "temperature": 0.7,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0,
        },
        "force": True,
    }

    nlp.add_pipe(
        "conspiracies/prompt_relation_extraction",
        last=True,
        config=config,
    )
