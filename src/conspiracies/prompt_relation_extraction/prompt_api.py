from typing import Any, Dict, List

from catalogue import registry

import random

@registry.prompt_apis.register("conspiracies/openai_api")
def create_openai_prompt_api(
    prompt_template,  # TODO: add type hint PromptTemplate
    api_key: str,
    model_name: str,
    api_kwargs: Dict[Any, Any],
):
    def openai_prompt(target: List[str]) -> List[str]:
        """"""
        import openai

        openai.api_key = api_key

        # Run loop until reaching return and response is returned
        while True:
            try:
                response = openai.Completion.create(
                    model=model_name,
                    prompt=prompt_template.generate_prompt(target),
                    **api_kwargs,
                )
                return response
            
            except openai.error.InvalidRequestError:
                # Randomly select an example to drop
                current_examples = prompt_template.examples
                current_examples.pop(random.randrange(len(current_examples)))
                prompt_template.set_examples(current_examples)
                continue

    return openai_prompt
