import random
from typing import Any, Dict, List, Tuple

from catalogue import registry
from spacy.tokens import Doc

from conspiracies.prompt_relation_extraction import PromptTemplate, SpanTriplet


@registry.prompt_apis.register("conspiracies/openai_api")
def create_openai_prompt_api(
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

                except openai.error.InvalidRequestError:
                    # Randomly select an example to drop
                    current_examples: List[Tuple[Doc, List[SpanTriplet]]] = list(
                        *zip(prompt_template.examples)
                    )
                    current_examples.pop(random.randrange(len(current_examples)))
                    examples = tuple(zip(*current_examples))
                    prompt_template.set_examples(examples)  # type: ignore

            responses.append(response)

        return responses

    return openai_prompt
