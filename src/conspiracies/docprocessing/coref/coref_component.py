"""A SpaCy component for coference using an AllenNLP coference model."""

from pathlib import Path
from typing import Dict, Iterable, Iterator, Union

from spacy import Vocab
from spacy.language import Language
from spacy.pipeline import TrainablePipe
from spacy.tokens import Doc, Span
from spacy.util import minibatch

from conspiracies.docprocessing.coref import CoreferenceModel


class CoreferenceComponent(TrainablePipe):
    def __init__(
        self,
        vocab: Vocab,
        name: str,
        model_path: Union[Path, str, None],
        device: int,
        open_unverified_connection: bool,
    ):
        self.name = name
        self.vocab = vocab
        self.model = CoreferenceModel(  # type: ignore
            model_path=model_path,
            device=device,
            open_unverified_connection=open_unverified_connection,
        )

        # Register custom extension on the Doc and Span
        if not Doc.has_extension("resolve_coref"):
            Doc.set_extension("resolve_coref", getter=self.resolve_coref_doc)
        if not Span.has_extension("resolve_coref"):
            Span.set_extension("resolve_coref", getter=self.resolve_coref_span)
        if not Doc.has_extension("coref_clusters"):
            Doc.set_extension("coref_clusters", default=list())
        if not Span.has_extension("coref_clusters"):
            Span.set_extension("coref_clusters", default=list())
        if not Span.has_extension("antecedent"):
            Span.set_extension("antecedent", default=None)

    def resolve_coref_doc(self, doc: Doc) -> str:
        """Resolve the coreference clusters by replacing each entity with the
        antecedent. The antecedent is the first entity that appears in the
        cluster. This is for the whole doc.

        Args:
            doc (Doc): The document.

        Returns:
            Str: The text of the document with resolved coreference clusters.
        """
        resolved = list(tok.text_with_ws for tok in doc)
        for i, cluster in doc._.coref_clusters:
            for coref in cluster:
                if coref != coref._.antecedent:
                    resolved[coref.start] = (
                        coref._.antecedent.text + doc[coref.end - 1].whitespace_
                    )
                    for i in range(coref.start + 1, coref.end):
                        resolved[i] = ""
        return "".join(resolved)

    def resolve_coref_span(self, sent: Span) -> str:
        """Resolve the coreference clusters by replacing each entity with the
        antecedent. The antecedent is the first entity that appears in the
        cluster. This is for the the sent.

        Args:
            sent (Span): The document.

        Returns:
            Str: The text of the sentence with resolved coreference clusters.
        """
        resolved_span = list(tok.text_with_ws for tok in sent)

        # Calibrate coref index since it is based on the Doc level
        sentence_lengths = [len(sent) for sent in sent.doc.sents]
        index_calibrate = 0
        for i, doc_sent in enumerate(sent.doc.sents):
            if doc_sent == sent:
                break
            else:
                index_calibrate += sentence_lengths[i]

        for i, coref in sent._.coref_clusters:
            coref_start = coref.start - index_calibrate
            coref_end = coref.end - index_calibrate
            if coref != coref._.antecedent:
                resolved_span[coref_start] = (
                    coref._.antecedent.text + sent.doc[coref_end].whitespace_
                )
                for i in range(coref_start + 1, coref_end):
                    resolved_span[i] = ""
        return "".join(resolved_span).strip()

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
                            sent._.coref_clusters.append((cluster, coref))
                            sent._.antecedent = coref_clusters_lookup_dict[cluster][0]

    def pipe(self, stream: Iterable[Doc], *, batch_size: int = 128) -> Iterator[Doc]:
        """Apply the pipe to a stream of documents. This usually happens under
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
        """Apply the pipeline's model to a batch of docs, without modifying
        them. Returns the extracted features as the FullTransformerBatch
        dataclass.

        Args:
            docs (Iterable[Doc]): The documents to predict.

        Returns:
            Dict: The extracted features.
        """
        return self.model.predict_batch_docs(docs)

    def __call__(self, doc: Doc) -> Doc:
        """Apply the pipe to one document. The document is modified in place,
        and returned. This usually happens under the hood when the nlp object
        is called on a text and all components are applied to the Doc.

        Args:
            doc (Doc): The Doc to process.

        Returns:
            Doc: The processed Doc.
        """
        outputs = self.predict([doc])
        self.set_annotations([doc], outputs)
        return doc


@Language.factory(
    "allennlp_coref",
    default_config={
        "model_path": None,
        "device": -1,
        "open_unverified_connection": True,
    },
)
def create_coref_component(
    nlp: Language,
    name: str,
    model_path: Union[Path, str, None],
    device: int,
    open_unverified_connection: bool,
):
    """Creates coference model component.

    Args:
        nlp (Language): A spacy language pipeline
        name (str): The name of the component
        model_path (Union[Path, str, None]): Path to the model, if None, the
            model will be downloaded to the default cache directory.
        device (int, optional): Cuda device. If >= 0 will use the corresponding GPU,
            below 0 is CPU. Defaults to -1.
        open_unverified_connection (bool, optional): Should you download the model from
            an unverified connection. Defaults to True.

    Returns:
        CorefenceComponent: The coreference model component
    """

    return CoreferenceComponent(
        nlp.vocab,
        name=name,
        model_path=model_path,
        device=device,
        open_unverified_connection=open_unverified_connection,
    )
