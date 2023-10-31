import pytest
from conspiracies.docprocessing.relationextraction.gptprompting import (
    MarkdownPromptTemplate1,
    MarkdownPromptTemplate2,
    PromptTemplate1,
    PromptTemplate2,
    XMLStylePromptTemplate,
    chatGPTPromptTemplate,
)

from .test_data.prompt_data import (
    MarkdownPromptTemplate1_expected_prompt,
    MarkdownPromptTemplate2_expected_prompt,
    PromptTemplate1_expected_prompt,
    PromptTemplate2_expected_prompt,
    XMLStylePromptTemplate_expected_prompt,
    chatGPTPromptTemplate_expected_prompt,
    load_examples,
    test_tweet,
)


def get_examples_task_introduction():
    task_description = "This is a test task description"
    examples = load_examples()
    return examples, task_description, test_tweet


examples, task_description, test_tweet = get_examples_task_introduction()  # noqa


@pytest.mark.parametrize(
    "Template, target, examples, task_description, expected_prompt",
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
        (
            chatGPTPromptTemplate,
            test_tweet,
            examples,
            task_description,
            chatGPTPromptTemplate_expected_prompt,
        ),
    ],
)
def test_PromptTemplate_create_prompt(
    Template,
    target,
    examples,
    task_description,
    expected_prompt,
):
    template = Template(task_description=task_description, examples=examples)
    prompt = template.create_prompt(target)
    assert prompt == expected_prompt
