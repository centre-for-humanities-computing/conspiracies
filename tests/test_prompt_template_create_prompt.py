import pytest
from conspiracies import (
    MarkdownPromptTemplate1,
    MarkdownPromptTemplate2,
    PromptTemplate1,
    PromptTemplate2,
    XMLStylePromptTemplate,
)

from .test_data.prompt_data import (
    test_tweet,
    load_examples,
    PromptTemplate2_expected_prompt,
    PromptTemplate1_expected_prompt,
    MarkdownPromptTemplate1_expected_prompt,
    MarkdownPromptTemplate2_expected_prompt,
    XMLStylePromptTemplate_expected_prompt,
)


def get_examples_task_introduction():
    task_description = "This is a test task description"
    examples, triplets = load_examples()
    return (examples, triplets), task_description, test_tweet


examples, task_description, test_tweet = get_examples_task_introduction()  # noqa


@pytest.mark.parametrize(
    "template, target, examples, task_description, expected_prompt",
    [
        (
            PromptTemplate1,
            test_tweet,
            examples,
            task_description,
            PromptTemplate1_expected_prompt,
        ),
        (
            PromptTemplate2,
            test_tweet,
            examples,
            task_description,
            PromptTemplate2_expected_prompt,
        ),
        (
            MarkdownPromptTemplate1,
            test_tweet,
            examples,
            task_description,
            MarkdownPromptTemplate1_expected_prompt,
        ),
        (
            MarkdownPromptTemplate2,
            test_tweet,
            examples,
            task_description,
            MarkdownPromptTemplate2_expected_prompt,
        ),
        (
            XMLStylePromptTemplate,
            test_tweet,
            examples,
            task_description,
            XMLStylePromptTemplate_expected_prompt,
        ),
    ],
)
def test_PromptTemplate_create_prompt(
    template,
    target,
    examples,
    task_description,
    expected_prompt,
):
    template = template(examples, task_description)
    prompt = template.create_prompt(target)
    assert prompt == expected_prompt
