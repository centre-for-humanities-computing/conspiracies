import catalogue
from confection import registry

registry.prompt_templates = catalogue.create(  # type: ignore
    "conspiracies",
    "prompt_templates",
)
# a prompt template class object

registry.split_doc_functions = catalogue.create(  # type: ignore
    "conspiracies",
    "split_functions",
)
# split functions:
# Callable[[Doc], List[Span]]

registry.prompt_apis = catalogue.create("conspiracies", "prompt_apis")  # type: ignore
# prompt APIs:
# Callable[[PromptTemplate, str, str, Dict[Any, Any]], Callable[[str], str]]
# corresponding to the prompt_template, api_key, model_name, api_kwargs and return
# a function which takes in a target string and returns a output response (str).
