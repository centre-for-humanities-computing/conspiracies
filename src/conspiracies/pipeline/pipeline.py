import json
import os
from datetime import datetime
from pathlib import Path

from tqdm import tqdm

from conspiracies.common.fileutils import iter_lines_of_files
from conspiracies.corpusprocessing.aggregation import TripletAggregator
from conspiracies.corpusprocessing.clustering import Clustering, Mappings
from conspiracies.corpusprocessing.triplet import Triplet
from conspiracies.database.engine import get_engine, setup_database, get_session
from conspiracies.database.models import (
    TripletOrm,
    DocumentOrm,
    ModelLookupCache,
)
from conspiracies.docprocessing.docprocessor import DocProcessor
from conspiracies.document import Document
from conspiracies.pipeline.config import PipelineConfig, Thresholds
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
        self.input_path = Path(config.preprocessing.input_path)
        self.output_path = Path(config.base.output_path)
        os.makedirs(self.output_path, exist_ok=True)
        self.config = config
        print("Initialized Pipeline with config:", config)

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

        if self.config.databasepopulation.enabled:
            self.databasepopulation()

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
            n_process=self.config.docprocessing.n_process,
            doc_bin_size=self.config.docprocessing.doc_bin_size,
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
        if self.config.corpusprocessing.thresholds is None:
            thresholds = Thresholds.estimate_from_n_triplets(len(triplets))
        else:
            thresholds = self.config.corpusprocessing.thresholds
        triplets = Triplet.filter_on_entity_label_frequency(
            triplets,
            thresholds.min_label_occurrence,
        )
        Triplet.write_jsonl(self.output_path / "triplets.ndjson", triplets)

        print("Clustering entities and predicates to create mappings.")
        clustering = Clustering(
            language=self.config.base.language,
            n_dimensions=self.config.corpusprocessing.dimensions,
            n_neighbors=self.config.corpusprocessing.n_neighbors,
            min_cluster_size=thresholds.min_cluster_size,
            min_samples=thresholds.min_samples,
            cache_location=self.output_path / "cache",
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

    def databasepopulation(self):
        if self.config.databasepopulation.clear_and_write:
            if os.path.exists(self.output_path / "database.db"):
                print("Removing old database.")
                os.remove(self.output_path / "database.db")

        print("Populating database.")
        engine = get_engine(self.output_path / "database.db")
        setup_database(engine)
        session = get_session(engine)

        with open(self.output_path / "mappings.json") as mappings_file:
            mappings = Mappings(**json.load(mappings_file))

        with open(self.output_path / "triplets.ndjson") as triplets_file:
            cache = ModelLookupCache(session)
            bulk = []
            for line in tqdm(triplets_file, desc="Writing triplets to database"):
                triplet = Triplet(**json.loads(line))
                subject_id = cache.get_or_create_entity(
                    mappings.map_entity(triplet.subject.text),
                    session,
                )
                object_id = cache.get_or_create_entity(
                    mappings.map_entity(triplet.object.text),
                    session,
                )
                relation_id = cache.get_or_create_relation(
                    subject_id,
                    object_id,
                    mappings.map_predicate(triplet.predicate.text),
                    session,
                )

                triplet_orm = TripletOrm(
                    doc_id=int(triplet.doc),
                    subject_id=subject_id,
                    relation_id=relation_id,
                    object_id=object_id,
                    subj_span_start=triplet.subject.start_char,
                    subj_span_end=triplet.subject.end_char,
                    pred_span_start=triplet.predicate.start_char,
                    pred_span_end=triplet.predicate.end_char,
                    obj_span_start=triplet.object.start_char,
                    obj_span_end=triplet.object.end_char,
                )
                bulk.append(triplet_orm)
                if len(bulk) >= 500:
                    session.bulk_save_objects(bulk)
                    bulk.clear()
        session.bulk_save_objects(bulk)
        bulk.clear()
        session.commit()

        for doc in (
            json.loads(line)
            for line in tqdm(
                iter_lines_of_files(self.output_path / "annotations.ndjson"),
                desc="Writing documents to database",
            )
        ):
            doc_orm = DocumentOrm(
                id=doc["id"],
                text=doc["text"],
                timestamp=datetime.fromisoformat(doc["timestamp"]),
            )
            bulk.append(doc_orm)
            if len(bulk) >= 500:
                session.bulk_save_objects(bulk)
                bulk.clear()
        session.bulk_save_objects(bulk)
        session.commit()
