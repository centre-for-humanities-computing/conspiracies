import json
import os

from conspiracies.common.fileutils import iter_lines_of_files
from conspiracies.corpusprocessing import umap_hdb
from conspiracies.docprocessing.docprocessor import DocProcessor
from conspiracies.document import Document
from conspiracies.pipeline.config import PipelineConfig
from conspiracies.preprocessing.csv import CsvPreprocessor
from conspiracies.preprocessing.infomedia import InfoMediaPreprocessor
from conspiracies.preprocessing.preprocessor import Preprocessor
from conspiracies.preprocessing.text import TextFilePreprocessor
from conspiracies.preprocessing.tweets import TweetsPreprocessor
from conspiracies.visualization.graph import create_network_graph, get_nodes_edges


class Pipeline:
    def __init__(self, config: PipelineConfig):
        self.project_name = config.base.project_name
        self.input_path = config.preprocessing.input_path
        self.config = config
        print("Initialized Pipeline with config:", config)
        self.output_path = os.path.join(self.config.base.output_root, self.project_name)
        os.makedirs(self.output_path, exist_ok=True)

    def run(self):
        if self.config.preprocessing.enabled:
            if self.input_path is None:
                raise ValueError("'input_path' must be provided for preprocessing!")
            self.preprocessing()

        if self.config.docprocessing.enabled:
            self.docprocessing(continue_from_last=True)

        if self.config.corpusprocessing.enabled:
            self.corpusprocessing()

    def _get_preprocessor(self) -> Preprocessor:
        config = self.config.preprocessing
        doc_type = config.doc_type.lower()
        if doc_type == "text":
            return TextFilePreprocessor(**config.extra)
        if doc_type == "csv":
            return CsvPreprocessor(
                metadata_fields=config.metadata_fields,
                **config.extra,
            )
        elif doc_type == "tweets":
            return TweetsPreprocessor(
                metadata_fields=config.metadata_fields,
                **config.extra,
            )
        elif doc_type == "infomedia":
            return InfoMediaPreprocessor(metadata_fields=config.metadata_fields)
        else:
            raise ValueError(
                f"Unknown document type: {doc_type}. "
                f"Available types are: tweets, infomedia",
            )

    def preprocessing(self) -> None:
        preprocessor = self._get_preprocessor()
        preprocessor.preprocess_docs(
            self.input_path,
            f"{self.output_path}/preprocessed.ndjson",
        )

    def _get_docprocessor(self) -> DocProcessor:
        return DocProcessor(
            triplet_extraction=self.config.docprocessing.triplet_extraction_method,
        )

    def docprocessing(self, continue_from_last=False):
        docprocessor = self._get_docprocessor()
        docprocessor.process_docs(
            (
                json.loads(line, object_hook=Document)
                for line in iter_lines_of_files(
                    f"{self.output_path}/preprocessed.ndjson",
                )
            ),
            f"{self.output_path}/annotations.ndjson",
            continue_from_last=continue_from_last,
        )

    def corpusprocessing(self):
        # TODO: this process is kind of dumb with all the writing and reading of
        #  files etc., but for now just make it work. It comes from individual scripts
        #  and a lot of the logic of data structures happen in those read/writes. Also,
        #  a lot of data that we might want to save is thrown away, e.g. clsutered
        #  entities, or calculated/fetched on the go, e.g. node weights for graphs.
        docs = (
            json.loads(line)
            for line in iter_lines_of_files(
                f"{self.output_path}/annotations.ndjson",
            )
        )
        with open(
            f"{self.output_path}/triplets.csv",
            "w+",
        ) as out:
            for doc in docs:
                for triplet in doc["semantic_triplets"]:
                    triplet_fields = [
                        triplet["semantic_triplets"][field]["text"]
                        for field in ("subject", "predicate", "object")
                    ]
                    print(", ".join(triplet_fields), file=out)
        umap_hdb.main(
            f"{self.output_path}/triplets.csv",
            "danskBERT",
            dim=40,
            save=f"{self.output_path}/nodes_edges.json",
        )
        nodes, edges = get_nodes_edges(
            f"{self.output_path}/",
            "nodes_edges.json",
        )
        graph = create_network_graph(
            nodes,
            edges,
            save=f"{self.output_path}/graph",
        )
        graph_data = {
            "nodes": [
                {"label": node[0], "data": node[1]} for node in graph.nodes.data()
            ],
            "edges": [
                {"from ": edge[0], "to": edge[1], "data": edge[2]}
                for edge in graph.edges.data()
            ],
        }
        with open(f"{self.output_path}/graph.json", "w+") as out:
            json.dump(graph_data, out)
