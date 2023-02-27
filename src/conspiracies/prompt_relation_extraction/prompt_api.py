from typing import Any, Dict, List

from catalogue import registry


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

        # TODO: Add auto dropping of example tweets if prompt is too long.
        response = openai.Completion.create(
            model=model_name,
            prompt=prompt_template.generate_prompt(target),
            **api_kwargs,
        )
        return response

    return openai_prompt
