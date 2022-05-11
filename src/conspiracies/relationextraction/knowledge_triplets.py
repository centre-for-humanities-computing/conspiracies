from .dataset import EvalDataset
from .other import utils
import torch
import time
from .extract import extract_to_list, extract_to_dict
from torch.utils.data import DataLoader
from typing import Optional, List, Tuple
import urllib.request
import os
from pathlib import Path


DEFAULT_MODEL_DIR = Path(Path.home(), ".relation_model")


class KnowledgeTriplets:

    """A class for extracting triplets from a given text document.

    Typical usage example:

       re = KnowledgeTriplets(model_path = None)
       extracted_triplets = re.extract_relations(list_of_sent)


    Args:
        model_path: Path to a model (str, optional).

    Attributes:

        batch_size: An integer indicating the number of samples that will be propogated through the network.
        max_len: An integer defining the maximum sentence (vector?) length.
        num_workers: An integer which controls the number of worker threads which performe simultaneous training of a model.
        pin_memory: A boolean indicating if the fetched data Tensors should be put in pinned memory.
        bert_config: A string defining the configuration type.
        device: A boolean indicating whether to train a model on GPU or CPU.



    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        batch_size: int = 64,
        max_len: int = 64,
        num_workers: int = 1,  # it should be one if device is CPU otherwise torch is competing for cpus
        pin_memory: bool = True,
        device: Optional[str] = None,
    ):

        self._bert_config = "bert-base-multilingual-cased"
        if not device:
            self._device = torch.device(
                "cuda:0" if torch.cuda.is_available() else "cpu"
            )
        else:
            self._device = device
        self._batch_size = batch_size
        self._max_len = max_len
        self._num_workers = num_workers
        self._args = {"bert_config": self._bert_config, "device": self._device}
        self._bert_model = self._prepare_model(model_path)
        self._pin_memory = pin_memory

    def _load_model(self, path):
        model = utils.get_models(
            bert_config=self._bert_config,
            pred_n_labels=3,
            arg_n_labels=9,
            n_arg_heads=8,
            n_arg_layers=4,
            pos_emb_dim=64,
            use_lstm=False,
            device=self._device,
        )

        model.load_state_dict(
            torch.load(path, map_location=torch.device(self._device)), strict=False
        )
        model.zero_grad()
        model.eval()

        return model

    def _prepare_model(self, model_path: str = None):
        if model_path is None:
            if not DEFAULT_MODEL_DIR.exists():
                DEFAULT_MODEL_DIR.mkdir()

            model_path = DEFAULT_MODEL_DIR / "relation_model_v01.bin"

            if model_path.exists():
                return self._load_model(path=model_path)
            print(f"Downloading model to {model_path}...")
            urllib.request.urlretrieve(
                url="https://sciencedata.dk//shared/81ee2688645634814152e3965e74b7f7?download",
                filename=model_path,
            )

        return self._load_model(path=model_path)

    def _prepare_data(self, sents: List[str]):
        dataset = EvalDataset(sents, self._max_len, self._bert_config)
        test_loader = DataLoader(
            dataset,
            batch_size=self._batch_size,
            num_workers=self._num_workers,
            pin_memory=self._pin_memory,
            shuffle=False,
        )
        return test_loader

    def extract_relations(self, text: List[str], verbose: bool = False) -> List[Tuple]:
        if verbose:
            start = time.time()
        prepared_sent = self._prepare_data(sents=text)
        extractions = extract_to_dict(self._args, self._bert_model, prepared_sent)
        if verbose:
            print("TIME: ", time.time() - start)
        return extractions
