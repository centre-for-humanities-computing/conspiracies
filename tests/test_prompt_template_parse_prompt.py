import pytest

from conspiracies import (
    MarkdownPromptTemplate1,
    MarkdownPromptTemplate2,
    PromptTemplate1,
    PromptTemplate2,
    XMLStylePromptTemplate,
)

from .test_data.prompt_data import (
    MarkdownPromptTemplate1_expected_response,
    MarkdownPromptTemplate1_expected_triplets,
    MarkdownPromptTemplate2_expected_response,
    MarkdownPromptTemplate2_expected_triplets,
    PromptTemplate1_expected_response,
    PromptTemplate1_expected_triplets,
    PromptTemplate2_expected_response,
    PromptTemplate2_expected_triplets,
    XMLStylePromptTemplate_expected_response,
    XMLStylePromptTemplate_expected_triplets,
    test_tweet,
)


@pytest.mark.parametrize(
    "template, target, response, expected_triplets",
    [
        (
            PromptTemplate1,
            test_tweet,
            PromptTemplate1_expected_response,
            PromptTemplate1_expected_triplets,
        ),
        (
            PromptTemplate2,
            test_tweet,
            PromptTemplate2_expected_response,
            PromptTemplate2_expected_triplets,
        ),
        (
            MarkdownPromptTemplate1,
            test_tweet,
            MarkdownPromptTemplate1_expected_response,
            MarkdownPromptTemplate1_expected_triplets,
        ),
        (
            MarkdownPromptTemplate2,
            test_tweet,
            MarkdownPromptTemplate2_expected_response,
            MarkdownPromptTemplate2_expected_triplets,
        ),
        (
            XMLStylePromptTemplate,
            test_tweet,
            XMLStylePromptTemplate_expected_response,
            XMLStylePromptTemplate_expected_triplets,
        ),
    ],
)
def test_PromptTemplate_parse_prompt(template, target, response, expected_triplets):
    template_instance = template()
    parsed_triplets = template_instance.parse_prompt(response, target)
    assert parsed_triplets == expected_triplets
    parsed_triplets = template_instance.parse_prompt(response, target)
    assert parsed_triplets == expected_triplets
