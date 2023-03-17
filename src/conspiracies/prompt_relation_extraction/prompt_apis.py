import random
from typing import Any, Dict, List, Tuple

from ..registry import registry
from spacy.tokens import Doc

from conspiracies.prompt_relation_extraction import PromptTemplate, SpanTriplet


@registry.prompt_apis.register("conspiracies/openai_gpt3_api")
def create_openai_gpt3_prompt_api(
    prompt_template: PromptTemplate,
    api_key: str,
    model_name: str,
    api_kwargs: Dict[Any, Any],
):
    def openai_prompt(targets: List[str]) -> List[str]:
        """"""
        try:
            import openai
        except ImportError:
            raise ImportError(
                "The OpenAI API requires the openai package to be installed. "
                "You can install the requirements for this module using "
                "`pip install conspiracies[openai]`.",
            )

        openai.api_key = api_key

        responses: List[str] = []
        for target in targets:
            # Run loop until reaching return and response is returned
            while True:
                try:
                    response = openai.Completion.create(
                        model=model_name,
                        prompt=prompt_template.create_prompt(target),
                        **api_kwargs,
                    )
                    responses.append(response["choices"][0]["text"])
                    break

                except openai.error.InvalidRequestError as e:
                    print("Invalid request got error: ", e)
                    print("Retrying with fewer examples...")
                    # Randomly select an example to drop
                    current_examples: List[Tuple[Doc, List[SpanTriplet]]] = list(
                        *zip(prompt_template.examples)
                    )
                    current_examples.pop(random.randrange(len(current_examples)))
                    examples = tuple(zip(*current_examples))
                    prompt_template.set_examples(examples)  # type: ignore

        return responses

    return openai_prompt


@registry.prompt_apis.register("conspiracies/openai_chatgpt_api")
def create_openai_chatgpt_prompt_api(
    prompt_template: PromptTemplate,
    api_key: str,
    api_kwargs: Dict[Any, Any],
):
    def openai_prompt(targets: List[str]) -> List[str]:
        """"""
        try:
            import openai
        except ImportError:
            raise ImportError(
                "The OpenAI API requires the openai package to be installed. "
                "You can install the requirements for this module using "
                "`pip install conspiracies[openai]`.",
            )

        openai.api_key = api_key
        message_example = prompt_template.create_prompt("test")
        assert (
            type(message_example) == list and type(message_example[0]) == dict
        ), "ChatGPT requires a list of message dicts. Consider using chatGPTPromptTemplate as template."  # noqa: E501

        responses: List[str] = []
        for target in targets:
            # Run loop until reaching return and response is returned
            while True:
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=prompt_template.create_prompt(target),
                        **api_kwargs,
                    )
                    responses.append(response["choices"][0]["message"]["content"])
                    break

                except openai.error.InvalidRequestError:
                    # Randomly select an example to drop
                    current_examples = prompt_template.examples
                    current_examples.pop(random.randrange(len(current_examples)))
                    examples = current_examples
                    prompt_template.set_examples(examples)  # type: ignore

        return responses

    return openai_prompt
