import json
import os
from pathlib import Path


from conspiracies.common.fileutils import iter_lines_of_files
from conspiracies.corpusprocessing.aggregation import TripletAggregator
from conspiracies.corpusprocessing.clustering import Clustering
from conspiracies.corpusprocessing.triplet import Triplet
from conspiracies.docprocessing.docprocessor import DocProcessor
from conspiracies.document import Document
from conspiracies.pipeline.config import PipelineConfig, ClusteringThresholds
from conspiracies.preprocessing.csv import CsvPreprocessor
from conspiracies.preprocessing.infomedia import InfoMediaPreprocessor
from conspiracies.preprocessing.preprocessor import Preprocessor
from conspiracies.preprocessing.text import TextFilePreprocessor
from conspiracies.preprocessing.tweets import TweetsPreprocessor
from conspiracies.visualization.graph import (
    transform_triplets_to_graph_data,
    create_network_graph,
)


class Pipeline:
    def __init__(self, config: PipelineConfig):
        self.project_name = config.base.project_name
        self.input_path = Path(config.preprocessing.input_path)
        self.config = config
        print("Initialized Pipeline with config:", config)
        self.output_path = Path(self.config.base.output_root, self.project_name)
        os.makedirs(self.output_path, exist_ok=True)

    def run(self):
        if self.config.preprocessing.enabled:
            if self.input_path is None:
                raise ValueError("'input_path' must be provided for preprocessing!")
            self.preprocessing()

        if self.config.docprocessing.enabled:
            self.docprocessing(
                continue_from_last=self.config.docprocessing.continue_from_last,
            )

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
            self.output_path / "preprocessed.ndjson",
            n_docs=self.config.preprocessing.n_docs,
        )

    def _get_docprocessor(self) -> DocProcessor:
        return DocProcessor(
            language=self.config.base.language,
            batch_size=self.config.docprocessing.batch_size,
            triplet_extraction_method=self.config.docprocessing.triplet_extraction_method,
            prefer_gpu_for_coref=self.config.docprocessing.prefer_gpu_for_coref,
        )

    def docprocessing(self, continue_from_last=False):
        docprocessor = self._get_docprocessor()
        docprocessor.process_docs(
            (
                Document(**json.loads(line))
                for line in iter_lines_of_files(
                    self.output_path / "preprocessed.ndjson",
                )
            ),
            self.output_path / "annotations.ndjson",
            continue_from_last=continue_from_last,
        )

    def corpusprocessing(self):
        # TODO: make into logging messages or progress bars instead
        print("Collecting triplets.")
        triplets = Triplet.from_annotated_docs(self.output_path / "annotations.ndjson")
        triplets = Triplet.filter_on_stopwords(triplets, self.config.base.language)
        Triplet.write_jsonl(self.output_path / "triplets.ndjson", triplets)

        if self.config.corpusprocessing.thresholds is None:
            thresholds = ClusteringThresholds.estimate_from_n_triplets(len(triplets))
        else:
            thresholds = self.config.corpusprocessing.thresholds
        print("Clustering entities and predicates to create mappings.")
        clustering = Clustering(
            language=self.config.base.language,
            n_dimensions=self.config.corpusprocessing.dimensions,
            n_neighbors=self.config.corpusprocessing.n_neighbors,
            min_cluster_size=thresholds.min_cluster_size,
            min_samples=thresholds.min_samples,
        )
        mappings = clustering.create_mappings(triplets)
        with open(self.output_path / "mappings.json", "w") as out:
            out.write(mappings.json())

        print("Aggregating triplets, entities and predicates and outputting stats.")
        aggregator = TripletAggregator(mappings=mappings)
        triplet_stats = aggregator.aggregate(triplets)
        with open(self.output_path / "triplet_stats.json", "w") as out:
            json.dump(triplet_stats.entries(), out)

        print("Creating graph data.")
        nodes, edges = transform_triplets_to_graph_data(triplet_stats)
        graph_data = {
            "nodes": [
                {"id": label, "label": label, "stats": stats}
                for label, stats in triplet_stats.entities.items()
            ],
            "edges": [
                {"from": subj, "to": obj, "label": pred, "stats": stats}
                for (subj, pred, obj), stats in triplet_stats.triplets.items()
            ],
        }
        with open(self.output_path / "graph.json", "w+") as out:
            json.dump(graph_data, out)

        create_network_graph(
            nodes,
            edges,
            save=self.output_path / "graph.png",
        )
