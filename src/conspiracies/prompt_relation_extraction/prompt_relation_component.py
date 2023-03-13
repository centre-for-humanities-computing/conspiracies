"""A relation extraction component for spaCy using prompt-based relation
extraction."""


from typing import Any, Dict, List, Optional

from spacy.language import Language
from spacy.tokens import Doc

from ..registry import registry
from .data_classes import DocTriplets, SpanTriplet


class PromptRelationExtractionComponent:
    """A class for extracting relations from a spaCy Doc using prompt-based
    relation extraction."""

    def __init__(
        self,
        nlp: Language,
        name: str,
        prompt_template: str,
        examples: Optional[List[List[SpanTriplet]]],
        task_description: Optional[str],
        model_name: str,
        backend: str,
        api_key: str,
        api_kwargs: Dict[Any, Any],
        split_doc_fn: Optional[str],
        force: bool,
    ):
        """Initialise components."""
        self.name = name
        self.nlp = nlp
        p_template = registry.get("prompt_templates", prompt_template)

        self.prompt_template = p_template(
            task_description=task_description,
            examples=examples,
        )

        # create prompt function using the desired API
        self.prompt_fn = registry.get("prompt_apis", backend)(
            self.prompt_template,
            api_key,
            model_name,
            api_kwargs,
        )
        self.model_name = model_name
        self.backend = backend
        self.api_key = api_key
        self.api_kwargs = api_kwargs
        if split_doc_fn is not None:
            self.split_doc_fn = registry.get("split_doc_functions", split_doc_fn)()
        else:
            self.split_doc_fn = None

        if not Doc.has_extension("relation_triplets") or force:
            Doc.set_extension("relation_triplets", default=None, force=force)

    def combine_docs(self, docs: List[Doc]) -> Doc:
        """Combine a list of docs into a single doc."""
        raise NotImplementedError("Combine docs not implemented yet.")

    def set_annotation(self, doc, docs: List[Doc], prompt_outputs: List[str]) -> Doc:
        """Set the annotation on the doc."""
        spantriplets = []
        for doc_span, prompt in zip(docs, prompt_outputs):
            triplets = self.prompt_template.parse_prompt(
                prompt,
                target_tweet=doc_span.text,
            )
            spantriplets.extend(triplets)

        doc._.relation_triplets = DocTriplets.doc_triplet_from_str_triplets(
            doc,
            spantriplets,
        )
        return doc

    def __call__(self, doc: Doc):
        """Run the pipeline component."""
        # split into tweets
        if self.split_doc_fn is not None:
            doc_spans = self.split_doc_fn(doc)
        else:
            doc_spans = [doc]

        # prompt
        responses = [self.prompt_fn(span) for span in doc_spans]
        doc = self.set_annotation(doc, doc_spans, responses)
        return doc


@Language.factory(
    "conspiracies/prompt_relation_extraction",
    default_config={
        "prompt_template": "conspiracies/template1",
        "examples": None,
        "task_description": None,
        "model_name": "text-davinci-002",
        "backend": "conspiracies/openai_api",
        "api_key": str,
        "split_doc_fn": None,
        "api_kwargs": {
            "max_tokens": 500,
            "temperature": 0.7,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0,
        },
        "force": True,
    },
)
def create_prompt_relation_extraction_component(
    nlp: Language,
    name: str,
    prompt_template: str,
    examples: Optional[List[List[SpanTriplet]]],
    task_description: Optional[str],
    model_name: str,
    backend: str,
    api_key: str,
    api_kwargs: Dict[Any, Any],
    split_doc_fn: Optional[str],
    force: bool,
) -> PromptRelationExtractionComponent:
    """Allows PromptRelationExtractionComponent to be added to a spaCy pipe
    using nlp.add_pipe("conspiracies/prompt_relation_extraction").

    Args:
        nlp (Language): A spaCy Language object.
        name (str): The instance name of the component in the pipeline.
        prompt_template (str): The name of the prompt template to use. Defaults to
            "conspiracies/template1". Available templates are reqistered in
            registry.prompt_templates.
        examples (List[List[SpanTriplet]]): A list of lists of SpanTriplets to use as
            examples for the prompt. Defaults to None. If None, the examples will be
            taken from the prompt template.
        task_description (str): A description of the task to be performed. Defaults to
            None. If None, the task description will be taken from the prompt template.
        model_name (str): The name of the model to use for the prompt. Defaults to
            "text-davinci-002".
        backend (Literal["openai", "huggingface"]): The backend to use for the prompt.
        force (bool): Whether to force the extension to be added to the Doc.

    Returns:
        PromptRelationExtractionComponent: A spaCy component for prompt-based relation
            extraction.

    Example:
        >>> import spacy
        >>> import conspiracies
        >>> nlp = spacy.load("en_core_web_sm")
        >>> config = {"prompt_template": "conspiracies/template1",
        ...           "examples": None,
        ...           "task_description": None,
        ...           "force": True}
        >>> nlp.add_pipe("conspiracies/prompt_relation_extraction", config=config)
        >>> doc = nlp("This is a test document.")
        >>> doc._.relation_triplet
    """

    return PromptRelationExtractionComponent(
        nlp,
        name=name,
        prompt_template=prompt_template,
        examples=examples,
        task_description=task_description,
        model_name=model_name,
        backend=backend,
        api_key=api_key,
        api_kwargs=api_kwargs,
        split_doc_fn=split_doc_fn,
        force=force,
    )
