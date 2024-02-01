"""A relation extraction component for spaCy using prompt-based relation
extraction."""

from typing import Any, Dict, Iterable, List, Optional

import numpy as np
from spacy.language import Language
from spacy.tokens import Doc
from spacy.training.example import Example

from conspiracies.registry import registry
from conspiracies.docprocessing.relationextraction.data_classes import (
    DocTriplets,
    SpanTriplet,
    install_extensions,
)
from .prompt_apis import create_openai_chatgpt_prompt_api  # noqa: F401


def score_open_relations(examples: Iterable[Example]) -> Dict[str, Any]:
    """Score the predicted relations against the gold relations."""
    keys = [
        "exact_span_match",
        "exact_string_match",
        "normalized_span_overlap",
        "normalized_string_overlap",
    ]
    hits = {key: 0 for key in keys}
    n_pred = 0
    n_ref = 0
    sample_scores = []

    for example in examples:
        gold_doc_triplets = example.reference._.relation_triplets
        pred_doc_triplets = example.predicted._.relation_triplets

        _score = pred_doc_triplets.score_relations(gold_doc_triplets)
        sample_scores.append(_score)

        hits["exact_span_match"] += _score["exact_span_match"]
        hits["exact_string_match"] += _score["exact_string_match"]
        hits["normalized_span_overlap"] += _score["normalized_span_overlap"]
        hits["normalized_string_overlap"] += _score["normalized_string_overlap"]
        n_pred += _score["length_self"]
        n_ref += _score["length_reference"]

    scores: Dict[str, Any] = {}

    # calculate precision, recall, f1_macro
    for key in hits:
        if n_pred:
            scores[f"{key}_precision"] = hits[key] / n_pred
        else:
            scores[f"{key}_precision"] = np.nan
        if n_ref:
            scores[f"{key}_recall"] = hits[key] / n_ref
        else:
            scores[f"{key}_recall"] = np.nan

        if scores[f"{key}_precision"] == 0 and scores[f"{key}_recall"] == 0:
            scores[f"{key}_f1"] = np.nan
        else:
            scores[f"{key}_f1"] = (
                2
                * (scores[f"{key}_precision"] * scores[f"{key}_recall"])
                / (scores[f"{key}_precision"] + scores[f"{key}_recall"])
            )

    scores["sample_scores"] = sample_scores
    scores["n_predictions"] = n_pred
    scores["n_references"] = n_ref

    return scores


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
            install_extensions(force=force)

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

        doc._.relation_triplets = DocTriplets.from_str_triplets(
            doc,
            spantriplets,
        )
        return doc

    def score(self, examples: Iterable[Example]) -> Dict[str, Any]:
        """Score the predicted relations against the gold relations. Scores
        using the following attributes:

        - `exact_span_match`: Whether there is an exact span match of the all three of
            the triplets (1 or 0).
        - `exact_string_match`: Whether there is an exact string match of the all three
            of the triplets (1 or 0).
        - `normalized_span_overlap`: The normalized span overlap between the predicted
            and gold relations. A value of 1 indicates an exact match (0-1, exact span
            match is 1).
        - `normalized_string_token_overlap`: The normalized string token overlap between
            the predicted and gold relations. A value of 1 indicates an exact match
            (0-1, exact string match is 1).

        For each of these and `{score}.f1_macro`, `{score}.f1_micro`, `{score}.recall`,
        `{score}.precision` are calculated.

        Args:
            examples (Iterable[Example]): A list of spaCy Examples.

        Returns:
            Dict[str, Any]: A dictionary of scores.
        """
        return score_open_relations(examples)

    def __call__(self, doc: Doc):
        """Run the pipeline component."""
        # split into tweets
        if self.split_doc_fn is not None:
            doc_spans = self.split_doc_fn(doc)
        else:
            doc_spans = [doc]

        # prompt
        responses = self.prompt_fn([span.text for span in doc_spans])
        doc = self.set_annotation(doc, doc_spans, responses)
        return doc


@Language.factory(
    "conspiracies/prompt_relation_extraction",
    default_config={
        "prompt_template": "conspiracies/template_1",
        "examples": None,
        "task_description": None,
        "model_name": "text-davinci-002",
        "backend": "conspiracies/openai_gpt3_api",
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
