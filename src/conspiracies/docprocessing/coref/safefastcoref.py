from fastcoref.spacy_component import FastCorefResolver
from spacy.language import Language
from spacy.pipeline import Pipe
from typing import Iterable

import logging

from spacy.util import minibatch
from datasets.utils.logging import disable_progress_bar


disable_progress_bar()  # annoying progress bar per batch
logging.getLogger("fastcoref").setLevel(logging.WARNING)


class SafeFastCoref(Pipe):
    def __init__(self, component: FastCorefResolver):
        """Initialize the wrapper with the original component."""
        self.component = component

    def pipe(self, stream: Iterable, batch_size: int = 128):
        """Wrap the pipe method of the component."""
        for mb in minibatch(stream, size=batch_size):
            try:
                # The pipe method can fail on one document in a loop and thereby fail on all docs in that
                # minibatch. However, it is made as a generator and may not show before long after the first
                # documents have passed through the whole pipeline. Therefore, the minibatch is processed fully
                # and then yielded. If it fails, they will be processed individually.
                annotated = list(
                    self.component.pipe(
                        mb,
                        batch_size=batch_size,
                        resolve_text=True,
                    ),
                )
            except Exception as e:
                # Log the error and return the unprocessed documents
                logging.error(
                    f"Error in SafeFastCoref pipe: {e}. Trying documents individually",
                )
                annotated = [self(d) for d in mb]
            yield from annotated

    def __call__(self, doc):
        """Wrap the __call__ method of the component."""
        try:
            return self.component(doc, resolve_text=True)
        except Exception as e:
            # Log the error and return the original document
            logging.error(f"Error in SafeFastCoref __call__: {e}")
            doc._.coref_clusters = []
            doc._.resolved_text = doc.text
            return doc


@Language.factory(
    "safe_fastcoref",
    assigns=["doc._.resolved_text", "doc._.coref_clusters"],
    default_config={
        "model_architecture": "FCoref",  # FCoref or LingMessCoref
        "model_path": "biu-nlp/f-coref",  # You can specify your own trained model path
        "device": None,  # "cuda" or "cpu" None defaults to cuda
        "max_tokens_in_batch": 10000,
        "enable_progress_bar": False,
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
