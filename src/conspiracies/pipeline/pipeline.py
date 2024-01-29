import glob
import json

from conspiracies.corpusprocessing import umap_hdb
from conspiracies.docprocessing.docprocessor import DocProcessor
from conspiracies.document import Document
from conspiracies.pipeline.config import (
    ProjectConfig,
    PreprocessingConfig,
    DocprocessingConfig,
)
from conspiracies.preprocessing.infomedia import InfoMediaPreprocessor
from conspiracies.preprocessing.preprocessor import Preprocessor
from conspiracies.preprocessing.tweets import TweetsPreprocessor
from conspiracies.visualization.graph import create_network_graph, get_nodes_edges


def iter_lines_of_files(glob_pattern: str):
    files = glob.glob(glob_pattern, recursive=True)
    for file in files:
        with open(file) as f:
            for line in f:
                yield line


class Pipeline:
    project_config: ProjectConfig
    preprocessing_config: PreprocessingConfig
    docprocessing_config: DocprocessingConfig

    def _get_preprocessor(self) -> Preprocessor:
        doc_type = self.preprocessing_config.doc_type.lower()
        if doc_type == "tweets":
            return TweetsPreprocessor(self.project_config.project_name)
        elif doc_type == "infomedia":
            return InfoMediaPreprocessor(self.project_config.project_name)
        else:
            raise ValueError(
                f"Unknown document type: {doc_type}. "
                f"Available types are: tweets, infomedia",
            )

    def preprocessing(self) -> None:
        preprocessor = self._get_preprocessor()
        preprocessor.preprocess_docs(self.preprocessing_config.input_path)

    def _get_docprocessor(self) -> DocProcessor:
        return DocProcessor(
            triplet_extraction=self.docprocessing_config.triplet_extraction_method,
        )

    def docprocessing(self, continue_from_last=False):
        docprocessor = self._get_docprocessor()
        docprocessor.process_docs(
            (
                json.loads(line, object_hook=Document)
                for line in iter_lines_of_files(
                    f"output/{self.project_config.project_name}/preprocessed.ndjson",
                )
            ),
            f"output/{self.project_config.project_name}/annotations.ndjson",
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
                f"output/{self.project_config.project_name}/annotations.ndjson",
            )
        )
        with open(
            f"output/{self.project_config.project_name}/triplets.csv",
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
            f"output/{self.project_config.project_name}/triplets.csv",
            "danskBERT",
            dim=40,
            save=f"output/{self.project_config.project_name}/nodes_edges.json",
        )
        nodes, edges = get_nodes_edges(
            f"output/{self.project_config.project_name}/",
            "nodes_edges.json",
        )
        graph = create_network_graph(
            nodes,
            edges,
            save=f"output/{self.project_config.project_name}/graph",
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
        with open(f"output/{self.project_config.project_name}/graph.json", "w+") as out:
            json.dump(graph_data, out)
