import math
import os
from collections import defaultdict, Counter
from pathlib import Path
from typing import List, Callable, Any, Hashable, Dict, Union

import networkx
import numpy as np
from hdbscan import HDBSCAN
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from umap import UMAP

from conspiracies.common.modelchoice import ModelChoice
from conspiracies.corpusprocessing.triplet import TripletField, Triplet


class Mappings(BaseModel):
    entities: Dict[str, str]
    predicates: Dict[str, str]

    def map_entity(self, entity: str):
        return self.entities[entity] if entity in self.entities else entity

    def entity_alt_labels(self):
        alt_labels = defaultdict(list)
        for entity, label in self.entities.items():
            alt_labels[label].append(entity)
        return alt_labels

    def map_predicate(self, predicate: str):
        return self.predicates[predicate] if predicate in self.predicates else predicate

    def predicate_alt_labels(self):
        alt_labels = defaultdict(list)
        for predicate, label in self.predicates.items():
            alt_labels[label].append(predicate)
        return alt_labels


class Clustering:
    def __init__(
        self,
        language: str,
        n_dimensions: int = None,
        n_neighbors: int = 15,
        min_cluster_size: int = 5,
        min_samples: int = 3,
        embedding_model: str = None,
        cache_location: Path = None,
    ):
        self.language = language
        self.n_dimensions = n_dimensions
        self.n_neighbors = n_neighbors
        self.min_cluster_size = min_cluster_size
        self.min_samples = min_samples
        self._embedding_model = embedding_model
        self.cache_location = cache_location
        if self.cache_location is not None:
            os.makedirs(self.cache_location, exist_ok=True)

    def _get_embedding_model(self):
        # figure out embedding model if not given explicitly
        if self._embedding_model is None:
            embedding_model = ModelChoice(
                da="vesteinn/DanskBERT",
                en="all-MiniLM-L6-v2",
                fallback="sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
            ).get_model(self.language)
        else:
            embedding_model = self._embedding_model
        return SentenceTransformer(embedding_model)

    @staticmethod
    def _combine_clusters(
        clusters: List[List[Any]],
        get_combine_key: Callable[[Any], Hashable] = lambda x: x,
    ) -> List[List[Any]]:
        # find matches of on combine key and keep track of their indices
        matches = defaultdict(set)
        for i, cluster in enumerate(clusters):
            for member in cluster:
                key = get_combine_key(member)
                if key:
                    matches[key].add(i)

        # create a graph where nodes are cluster indices and edges are key matches
        graph = networkx.Graph()
        graph.add_nodes_from(range(len(clusters)))
        for match in matches.values():
            for i in match:
                for j in match:
                    if i != j:
                        graph.add_edge(i, j)

        # connected components of the graph tell us which clusters should be merged
        merged_clusters = []
        for component in networkx.connected_components(graph):
            merged = []
            for node in component:
                merged += clusters[node]
            merged_clusters.append(merged)

        return merged_clusters

    def _cluster_via_embeddings(
        self,
        labels: List[str],
        cache_name: str = None,
        show_progress: bool = True,
    ):
        emb_cache = (
            Path(self.cache_location, f"embeddings-{cache_name}.npy")
            if self.cache_location and cache_name
            else None
        )
        if emb_cache and emb_cache.exists():
            print(
                "Reusing cached embeddings! Delete cache if this is not supposed to happen.",
            )
            embeddings = np.load(emb_cache)
        else:
            model = self._get_embedding_model()

            counter = Counter((field for field in labels))
            condensed = [
                field
                for field, count in counter.items()
                for _ in range(math.ceil(count / 1000))
            ]
            embeddings = model.encode(
                condensed,
                normalize_embeddings=True,
                show_progress_bar=show_progress,
            )
            if emb_cache:
                np.save(emb_cache, embeddings)

        if self.n_dimensions is not None:
            reduced_emb_cache = (
                Path(
                    self.cache_location,
                    f"embeddings-{cache_name}-red{self.n_dimensions}.npy",
                )
                if self.cache_location and cache_name
                else None
            )
            if reduced_emb_cache and reduced_emb_cache.exists():
                print(
                    "Reusing cached reduced embeddings! Delete cache if this is not supposed to happen.",
                )
                embeddings = np.load(reduced_emb_cache)
            else:
                print("Reducing embedding space ...")
                reducer = UMAP(
                    n_components=self.n_dimensions,
                    n_neighbors=self.n_neighbors,
                )
                embeddings = reducer.fit_transform(embeddings)
                if self.cache_location:
                    np.save(reduced_emb_cache, embeddings)

        hdbscan_model = HDBSCAN(
            min_cluster_size=self.min_cluster_size,
            max_cluster_size=self.min_cluster_size
            * 10,  # somewhat arbitrary, mostly to avoid mega clusters that suck up everything
            min_samples=self.min_samples,
        )
        hdbscan_model.fit(embeddings)

        clusters = defaultdict(list)
        for field, embedding, label, probability in zip(
            labels,
            embeddings,
            hdbscan_model.labels_,
            hdbscan_model.probabilities_,
        ):
            # skip noise and low confidence
            if label == -1 or probability < 0.5:
                continue
            clusters[label].append((field, embedding))

        merged = self._combine_clusters(
            list(clusters.values()),
            get_combine_key=lambda t: t[0],
        )

        # sort by how "prototypical" a member is in the cluster
        for cluster in merged:
            mean = np.mean(np.stack([t[1] for t in cluster]), axis=0)
            cluster.sort(key=lambda t: np.inner(t[1], mean), reverse=True)

        # get rid of embeddings in returned list
        return [[t[0] for t in cluster] for cluster in merged]

    @staticmethod
    def _cluster_via_normalization(
        labels: List[str],
        top: Union[int, float] = 1.0,
        restrictive_labels=True,
    ) -> List[List[str]]:
        counter = Counter((label for label in labels))
        if isinstance(top, float):
            top = int(top * len(counter))

        norm_map = {
            label: " "
            + label.lower()
            + " "  # surrounding spaces avoids matches like evil <-> devil
            for label in counter.keys()
        }
        cluster_map = {
            label: []
            for label, count in counter.most_common(top)
            # FIXME: hack due to lack of NER and lemmas at the time of writing
            if not restrictive_labels
            or len(label) >= 4
            and label[0].isupper()
            or len(label.split()) > 1
        }

        for label in counter.keys():
            norm_label = norm_map[label]
            matches = [
                substring
                for substring in cluster_map.keys()
                if norm_map[substring] in norm_label
            ]
            if not matches:
                continue

            best_match = min(
                matches,
                key=lambda substring: len(norm_map[substring]),
            )
            if best_match != label:
                cluster_map[best_match].append(label)

        clusters = [
            [main_label] + alt_labels
            for main_label, alt_labels in cluster_map.items()
            if alt_labels
        ]
        return clusters

    @staticmethod
    def _mapping_to_first_member(
        clusters: List[List[Union[TripletField, str]]],
    ) -> Dict[str, str]:
        def get_text(member: Union[TripletField, str]):
            if isinstance(member, TripletField):
                return member.text
            else:
                return member

        return {
            member: get_text(cluster[0])
            for cluster in clusters
            for member in set(get_text(member) for member in cluster)
        }

    def create_mappings(self, triplets: List[Triplet]) -> Mappings:
        subjects = [triplet.subject for triplet in triplets]
        objects = [triplet.object for triplet in triplets]
        entities = subjects + objects
        predicates = [triplet.predicate for triplet in triplets]

        # FIXME: clustering gets way to aggressive for many triplets
        # print("Creating mappings for entities")
        # entity_clusters = self._cluster(entities, "entities")
        # print("Creating mappings for predicates")
        # predicate_clusters = self._cluster(predicates, "predicates")

        print("Creating mappings for entities")
        entity_clusters = self._cluster_via_normalization(
            [e.text for e in entities],
            0.2,
        )
        entity_clusters = [
            sub_cluster
            for cluster in tqdm(entity_clusters, desc="Creating sub-clusters")
            for sub_cluster in (
                self._cluster_via_embeddings(cluster, show_progress=False)
                if len(cluster) > 10
                else [cluster]
            )
        ]

        print("Creating mappings for predicates")
        predicate_clusters = self._cluster_via_normalization(
            [p.text for p in predicates],
            top=0.2,
            restrictive_labels=False,
        )

        mappings = Mappings(
            entities=self._mapping_to_first_member(entity_clusters),
            predicates=self._mapping_to_first_member(predicate_clusters),
        )

        return mappings
