from fastcoref.spacy_component import FastCorefResolver
from spacy.language import Language
from spacy.pipeline import Pipe
from typing import Iterable

import logging

logging.getLogger("fastcoref").setLevel(logging.WARNING)


class SafeFastCoref(Pipe):
    def __init__(self, component):
        """Initialize the wrapper with the original component."""
        self.component = component

    def pipe(self, stream: Iterable, batch_size: int = 128):
        """Wrap the pipe method of the component."""
        try:
            yield from self.component.pipe(stream, batch_size=batch_size)
        except Exception as e:
            # Log the error and return the unprocessed documents
            logging.error(f"Error in SafeFastCoref pipe: {e}")
            for doc in stream:
                yield doc  # Return the original document

    def __call__(self, doc):
        """Wrap the __call__ method of the component."""
        try:
            return self.component(doc)
        except Exception as e:
            # Log the error and return the original document
            logging.error(f"Error in SafeFastCoref __call__: {e}")
            return doc


@Language.factory(
    "safe_fastcoref",
    assigns=["doc._.resolved_text", "doc._.coref_clusters"],
    default_config={
        "model_architecture": "FCoref",  # FCoref or LingMessCoref
        "model_path": "biu-nlp/f-coref",  # You can specify your own trained model path
        "device": None,  # "cuda" or "cpu" None defaults to cuda
        "max_tokens_in_batch": 10000,
        "enable_progress_bar": True,
    },
)
def create_safe_fastcoref(
    nlp,
    name,
    model_architecture: str,
    model_path: str,
    device,
    max_tokens_in_batch: int,
    enable_progress_bar: bool,
):
    """Factory method to create the SafeFastCoref component."""
    # Create the original FastCorefResolver with the given configuration
    fastcoref_component = FastCorefResolver(
        nlp=nlp,
        name=name,
        model_architecture=model_architecture,
        model_path=model_path,
        device=device,
        max_tokens_in_batch=max_tokens_in_batch,
        enable_progress_bar=enable_progress_bar,
    )
    # Wrap it with SafeFastCoref
    return SafeFastCoref(fastcoref_component)
