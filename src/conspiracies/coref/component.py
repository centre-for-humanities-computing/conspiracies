"""
A SpaCy component for coference using an AllenNLP coference model.
"""

from typing import Dict, Iterable, Iterator, Union
from pathlib import Path

from spacy import Vocab
from spacy.language import Language
from spacy.pipeline import TrainablePipe
from spacy.tokens import Doc, Span
from spacy.util import minibatch

from conspiracies.coref import CoreferenceModel


@Language.factory(
    "allennlp_coref",
    default_config={
        "model_path": None,
        "device": -1,
    },
)
def create_coref_component(
    nlp: Language, name: str, model_path: Union[Path, str, None], device: int
):
    """Creates coference model component

    Args:
        nlp (Language): A spacy language pipeline
        name (str): The name of the component
        model_path (Union[Path, str, None]): Path to the model, if None, the
            model will be downloaded to the default cache directory.
        device (int, optional): Cuda device. If >= 0 will use the corresponding GPU,
            below 0 is CPU. Defaults to -1.

    Returns:
        CorefenceComponent: The coreference model component
    """

    return CoreferenceComponent(
        nlp.vocab, name=name, model_path=model_path, device=device
    )


class CoreferenceComponent(TrainablePipe):
    def __init__(
        self, vocab: Vocab, name: str, model_path: Union[Path, str, None], device: int
    ):

        self.name = name
        self.vocab = vocab
        self.model = CoreferenceModel(model_path=model_path, device=device)

        # Register custom extension on the Doc and Span
        if not Doc.has_extension("resolved_coref"):
            Doc.set_extension("resolved_coref", default=None)
        if not Doc.has_extension("coref_clusters"):
            Doc.set_extension("coref_clusters", default=[])
        if not Span.has_extension("coref_cluster"):
            Span.set_extension("coref_cluster", default=[])
        if not Span.has_extension("antecedent"):
            Span.set_extension("antecedent", default=None)

    def set_annotations(self, docs: Iterable[Doc], model_output) -> None:
        """Set the coref attributes on Doc and Token level
        Args:
            docs (Iterable[Doc]): The documents to modify.
            model_output: (Dict): A batch outåut of self.predict().
        """
        for doc, prediction in zip(docs, model_output):
            clusters = prediction["clusters"]
            coref_clusters = [
                (
                    clusters.index(d),
                    [doc[cluster_ids[0] : cluster_ids[1] + 1] for cluster_ids in d],
                )
                for d in clusters
            ]
            doc._.coref_clusters.append(coref_clusters)
            doc._.coref_clusters = coref_clusters
            coref_clusters_lookup_dict = dict(coref_clusters)
            for sent in doc.sents:
                for cluster, corefs in coref_clusters:
                    for coref in corefs:
                        coref._.antecedent = corefs[0]
                        if sent == coref.sent:
                            sent._.coref_cluster.append((cluster, coref))
                            sent._.antecedent = coref_clusters_lookup_dict[cluster][0]
                            
            # Add the resolved coreference doc
            resolved = list(tok.text_with_ws for tok in doc)
            for i, cluster in doc._.coref_clusters:
                for coref in cluster:
                    if coref != coref._.antecedent:
                        resolved[coref.start] = coref._.antecedent.text + doc[coref.end-1].whitespace_
                        for i in range(coref.start+1, coref.end):
                            resolved[i] = ""
            doc._.resolved_coref = ''.join(resolved)
    
    def __call__(self, doc: Doc) -> Doc:
        """
        Apply the pipe to one document. The document is modified in place,
        and returned. This usually happens under the hood when the nlp object
        is called on a text and all components are applied to the Doc.

        Args:
            docs (Doc): The Doc to process.

        Returns:
            Doc: The processed Doc.
        """
        outputs = self.predict([doc])
        self.set_annotations([doc], outputs)
        return doc

    def pipe(self, stream: Iterable[Doc], *, batch_size: int = 128) -> Iterator[Doc]:
        """
        Apply the pipe to a stream of documents. This usually happens under
        the hood when the nlp object is called on a text and all components are
        applied to the Doc. Batch size is controlled by `batch_size` when
        instatiating the nlp.pipe object.

        Args:
            stream (Iterable[Doc]): A stream of documents.
            batch_size (int): The number of documents to buffer.

        Yields:
            Doc: Processed documents in order.
        """
        for outer_batch in minibatch(stream, batch_size):
            outer_batch = list(outer_batch)
            self.set_annotations(outer_batch, self.predict(outer_batch))

            yield from outer_batch

    def predict(self, docs: Iterable[Doc]) -> Dict:
        """
        Apply the pipeline's model to a batch of docs, without modifying them.
        Returns the extracted features as the FullTransformerBatch dataclass.

        Args:
            docs (Iterable[Doc]): The documents to predict.

        Returns:
            Dict: The extracted features.
        """
        return self.model.predict_batch_docs(docs)
