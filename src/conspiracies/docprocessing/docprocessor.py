import json
import os
from glob import glob
from pathlib import Path
from typing import Iterable, Tuple, Iterator

import spacy
import torch
from spacy.tokens import DocBin, Doc
from tqdm import tqdm

from conspiracies import docs_to_jsonl
from conspiracies.common.modelchoice import ModelChoice
from conspiracies.document import Document, text_with_context, remove_context


class DocProcessor:
    def _build_coref_pipeline(self):
        nlp_coref = spacy.blank(self.language)
        nlp_coref.add_pipe("sentencizer")
        if self.language == "en":
            nlp_coref.add_pipe(
                "safe_fastcoref",
                config={
                    "enable_progress_bar": False,
                    "model_architecture": "LingMessCoref",
                },
            )
        elif self.language == "da":
            nlp_coref.add_pipe(
                "allennlp_coref",
                config={
                    "device": (
                        0
                        if self.prefer_gpu_for_coref and torch.cuda.is_available()
                        else -1
                    ),
                },
            )

        def warn_error(proc_name, proc, docs, e):
            print(
                f"An error occurred when applying component {proc_name}. "
                f"{[d[:20] + '...' for d in docs]}. {e}",
            )

        nlp_coref.set_error_handler(warn_error)
        return nlp_coref

    def _build_triplet_extraction_pipeline(self):
        model = ModelChoice(da="da_core_news_sm", en="en_core_web_sm").get_model(
            self.language,
        )
        nlp = spacy.load(model)
        nlp.add_pipe(
            "heads_extraction",
            config={"normalize_to_entity": True, "normalize_to_noun_chunk": True},
        )
        # TODO: Any and only (!) relevant configuration from pipeline config should
        #  trickle down to configuration of individual components here. For now, this
        #  is just copy-pasta from elsewhere.
        if self.triplet_extraction_component.lower() == "multi2oie":
            config = {"confidence_threshold": 2.7, "model_args": {"batch_size": 10}}
            nlp.add_pipe("relation_extractor", config=config)
        elif self.triplet_extraction_component.lower() == "prompting":
            config = {
                "prompt_template": "conspiracies/template_1",
                "examples": None,
                "task_description": None,
                "model_name": "text-davinci-002",
                "backend": "conspiracies/openai_gpt3_api",
                "api_key": "",
                "split_doc_fn": None,
                "api_kwargs": {
                    "max_tokens": 500,
                    "temperature": 0.7,
                    "top_p": 1,
                    "frequency_penalty": 0,
                    "presence_penalty": 0,
                },
                "force": True,
            }

            nlp.add_pipe(
                "conspiracies/prompt_relation_extraction",
                last=True,
                config=config,
            )
        else:
            ValueError(
                f"{self.triplet_extraction_component} is not a valid triplet "
                f"relation extraction component.",
            )
        return nlp

    def __init__(
        self,
        language="da",
        batch_size=25,
        triplet_extraction_method="multi2oie",
        prefer_gpu_for_coref: bool = False,
        n_process: int = 1,
        doc_bin_size: int = 100,
    ):
        self.language = language
        self.batch_size = batch_size
        self.prefer_gpu_for_coref = prefer_gpu_for_coref
        self.n_process = n_process
        if n_process > 1:
            # multiprocessing and torch with multiple threads result in a deadlock, therefore:
            torch.set_num_threads(1)
        self.doc_bin_size = doc_bin_size
        self.coref_pipeline = self._build_coref_pipeline()
        self.triplet_extraction_component = triplet_extraction_method
        self.triplet_extraction_pipeline = self._build_triplet_extraction_pipeline()

    @staticmethod
    def _set_user_data_on_docs(docs: Iterator[Tuple[Doc, Document]]) -> Iterator[Doc]:
        for doc, src_doc in docs:
            # FIXME: this is kind of stupid, but with old pydantic this will have to work for now.
            doc.user_data["doc_metadata"] = json.loads(src_doc.json())
            yield doc

    def _store_doc_bins(self, docs: Iterator[Doc], output_path: Path):
        output_dir = Path(os.path.dirname(output_path)) / "spacy_docs"
        output_dir.mkdir(parents=True, exist_ok=True)

        size = self.doc_bin_size
        doc_bin = DocBin(store_user_data=True)
        for i, doc in enumerate(docs, start=1):
            doc_bin.add(doc)
            if i % size == 0:
                with open(output_dir / f"{i // size}.bin", "wb") as f:
                    f.write(doc_bin.to_bytes())
                doc_bin = DocBin(store_user_data=True)
            yield doc

    def process_docs(
        self,
        docs: Iterable[Document],
        output_path: Path,
        continue_from_last=False,
    ):
        if continue_from_last and os.path.exists(output_path):
            already_processed = set()

            # FIXME: paths should be given elsewhere and not be inferred like this
            for bin_file in glob(
                (Path(os.path.dirname(output_path)) / "spacy_docs").as_posix()
                + "/*.bin",
            ):
                with open(bin_file, "rb") as bytes_data:
                    doc_bin = DocBin().from_bytes(bytes_data.read())
                    for doc in doc_bin.get_docs(self.triplet_extraction_pipeline.vocab):
                        id_ = doc.user_data["doc_metadata"]["id"]
                        already_processed.add(id_)

            print(f"Skipping {len(already_processed)} processed docs.")
            docs = (doc for doc in docs if doc.id not in already_processed)

        # The coreference pipeline tends to choke on too large batches because of an
        # extreme memory pressure, hence the small batch size
        coref_resolved_docs = self.coref_pipeline.pipe(
            ((text_with_context(src_doc), src_doc) for src_doc in docs),
            batch_size=self.batch_size,
            as_tuples=True,
            n_process=self.n_process,
            component_cfg={"fastcoref": {"resolve_text": True}},
        )

        with_triplets = self.triplet_extraction_pipeline.pipe(
            (
                (remove_context(doc._.resolved_text), src_doc)
                for doc, src_doc in coref_resolved_docs
            ),
            batch_size=self.batch_size,
            as_tuples=True,
            n_process=self.n_process,
        )

        with_user_data = self._set_user_data_on_docs(with_triplets)

        stored = self._store_doc_bins(with_user_data, output_path)

        docs_to_jsonl(
            tqdm(stored),
            output_path,
            append=continue_from_last,
        )
