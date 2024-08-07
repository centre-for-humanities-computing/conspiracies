import os
from pathlib import Path
from typing import Iterable

import spacy
import torch
from jsonlines import jsonlines
from tqdm import tqdm

from conspiracies import docs_to_jsonl
from conspiracies.common.modelchoice import ModelChoice
from conspiracies.document import Document, text_with_context, remove_context


class DocProcessor:
    def _build_coref_pipeline(self):
        nlp_coref = spacy.blank(self.language)
        nlp_coref.add_pipe("sentencizer")
        nlp_coref.add_pipe(
            "allennlp_coref",
            config={
                "device": (
                    0 if self.prefer_gpu_for_coref and torch.cuda.is_available() else -1
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
    ):
        self.language = language
        self.batch_size = batch_size
        self.prefer_gpu_for_coref = prefer_gpu_for_coref
        self.coref_pipeline = self._build_coref_pipeline()
        self.triplet_extraction_component = triplet_extraction_method
        self.triplet_extraction_pipeline = self._build_triplet_extraction_pipeline()

    def process_docs(
        self,
        docs: Iterable[Document],
        output_path: Path,
        continue_from_last=False,
    ):
        if continue_from_last and os.path.exists(output_path):
            with jsonlines.open(output_path) as annotated_docs:
                already_processed = {
                    annotated_doc["id"] for annotated_doc in annotated_docs
                }
            print(f"Skipping {len(already_processed)} processed docs.")
            docs = (doc for doc in docs if doc.id not in already_processed)

        # The coreference pipeline tends to choke on too large batches because of an
        # extreme memory pressure, hence the small batch size
        coref_resolved_docs = self.coref_pipeline.pipe(
            ((text_with_context(src_doc), src_doc) for src_doc in docs),
            batch_size=self.batch_size,
            as_tuples=True,
        )

        with_triplets = self.triplet_extraction_pipeline.pipe(
            (
                (remove_context(doc._.resolve_coref), src_doc)
                for doc, src_doc in coref_resolved_docs
            ),
            batch_size=self.batch_size,
            as_tuples=True,
        )

        docs_to_jsonl(
            tqdm(d for d in with_triplets),
            output_path,
            append=continue_from_last,
        )
