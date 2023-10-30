"""A custom Coreference model for wrapping an AllenNLP's Predictor for
coreference resolution on SpaCy Docs."""

from typing import List, Union
from pathlib import Path

from spacy.tokens import Doc

from allennlp.predictors.predictor import Predictor
from allennlp.data import Instance
from allennlp.models.archival import load_archive
from allennlp.common.util import prepare_environment

# required for reading an archive using the "coref"
from allennlp_models.coref.dataset_readers.conll import ConllCorefReader  # noqa

from conspiracies.docprocessing.modeldownload import download_model


@Predictor.register("coreference_resolution_v1")
class CoreferenceModel(Predictor):
    """A coreference predictor model using the AllenNLP API, but for handling
    SpaCy docs.

    Args:
        model_path(Union[Path, str, None], optional): Path to the model, if None, the
            model will be downloaded to the default cache directory.
        device(int, optional): Cuda device. If >= 0 will use the corresponding GPU,
            below 0 is CPU. Defaults to -1.
        open_unverified_connection (bool, optional): Should you download from an
            unverified connection. Defaults to False.

    Returns:
        CoreferenceModel: The coreference model
    """

    def __init__(
        self,
        model_path: Union[Path, str, None] = None,
        device: int = -1,
        open_unverified_connection: bool = False,
        **kwargs,
    ) -> None:
        if model_path is None:
            model_path = download_model(
                "da_coref_twitter_v1",
                open_unverified_connection=open_unverified_connection,
            )

        archive = load_archive(model_path, cuda_device=device, **kwargs)
        config = archive.config
        prepare_environment(config)
        dataset_reader = archive.validation_dataset_reader
        super().__init__(archive.model, dataset_reader)

    def _doc_to_instance(self, doc: Doc) -> Instance:
        sentences = [[token.text for token in sentence] for sentence in doc.sents]
        instance = self._dataset_reader.text_to_instance(sentences)
        return instance

    def predict_batch_docs(self, docs: List[Doc]) -> List[Instance]:
        """Convert a list of docs to Instance and predict the batch."""
        instances = [self._doc_to_instance(doc) for doc in docs]
        return self.predict_batch_instance(instances)
