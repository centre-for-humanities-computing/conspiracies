from collections import defaultdict, Counter
from itertools import groupby
from typing import (
    List,
    Callable,
    Any,
    Hashable,
    Dict,
    Union,
    Iterable,
    Iterator,
    Tuple,
    TypeVar,
    Optional,
)

import networkx
import numpy as np
from hdbscan import HDBSCAN
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

from conspiracies.common.modelchoice import ModelChoice
from conspiracies.corpusprocessing.triplet import TripletField, Triplet


class Mappings(BaseModel):
    entities: Dict[str, str]
    super_entities: Dict[str, str]
    predicates: Dict[str, str]

    def map_entity(self, entity: str):
        return self.entities[entity] if entity in self.entities else entity

    def entity_alt_labels(self):
        alt_labels = defaultdict(list)
        for entity, label in self.entities.items():
            alt_labels[label].append(entity)
        return alt_labels

    def get_super_entity(self, entity: str):
        return self.super_entities[entity] if entity in self.super_entities else None

    def map_predicate(self, predicate: str):
        return self.predicates[predicate] if predicate in self.predicates else predicate

    def predicate_alt_labels(self):
        alt_labels = defaultdict(list)
        for predicate, label in self.predicates.items():
            alt_labels[label].append(predicate)
        return alt_labels


_V = TypeVar("_V")
_K = TypeVar("_K", bound=Hashable)


def _group_by_key(
    elements: Iterable[_V],
    key: Callable[[_V], _K] = lambda x: x,
) -> Iterator[Tuple[_K, List[_V]]]:
    grouped = defaultdict(list)
    for item in elements:
        grouped[key(item)].append(item)
    yield from grouped.items()


class Clustering:

    _cached_sent_transformer = None

    def __init__(
        self,
        language: str,
        n_dimensions: int = None,
        n_neighbors: int = 15,
        min_cluster_size: int = 5,
        min_samples: int = 3,
        embedding_model: str = None,
    ):
        self.language = language
        self.n_dimensions = n_dimensions
        self.n_neighbors = n_neighbors
        self.min_cluster_size = min_cluster_size
        self.min_samples = min_samples
        self._embedding_model = embedding_model

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
        if self._cached_sent_transformer is None:
            self._cached_sent_transformer = SentenceTransformer(embedding_model)
        return self._cached_sent_transformer

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
        show_progress: bool = True,
        get_combine_key: Callable[[str], Hashable] = lambda x: x,
    ):
        model = self._get_embedding_model()

        embeddings = model.encode(
            labels,
            normalize_embeddings=True,
            show_progress_bar=show_progress,
        )

        hdbscan_model = HDBSCAN(
            min_cluster_size=self.min_cluster_size,
            min_samples=self.min_samples,
        )
        hdbscan_model.fit(embeddings)

        clusters = defaultdict(list)
        for label, embedding, cluster_label, probability in zip(
            labels,
            embeddings,
            hdbscan_model.labels_,
            hdbscan_model.probabilities_,
        ):
            # skip noise and low confidence
            if cluster_label == -1 or probability < 0.3:
                lowest_key = min(clusters.keys(), default=0)
                clusters[lowest_key - 1].append((label, embedding))
            else:
                clusters[cluster_label].append((label, embedding))

        merged = self._combine_clusters(
            list(clusters.values()),
            get_combine_key=lambda t: get_combine_key(t[0]),
        )

        # sort by how "prototypical" a member is in the cluster
        for cluster in merged:
            mean = np.mean(np.stack([t[1] for t in cluster]), axis=0)
            cluster.sort(key=lambda t: np.inner(t[1], mean), reverse=True)

        # get rid of embeddings in returned list
        return [[t[0] for t in cluster] for cluster in merged]

    @staticmethod
    def _cluster_via_labels(
        labels: List[str],
        is_main_label: Optional[Callable[[str], bool]] = None,
        get_norm_label: Callable[[str], str] = lambda x: x,
    ) -> Tuple[List[List[str]], List[str]]:
        counter = Counter(labels)

        norm_map = {
            label: " "
            + get_norm_label(label)
            + " "  # surrounding spaces avoids matches like evil <-> devil
            for label in counter.keys()
        }
        cluster_map = {
            label: []
            for label in counter.keys()
            if is_main_label is None or is_main_label(label)
        }

        unclustered = []

        for label in counter.keys():
            norm_label = norm_map[label]
            matches = [
                candidate
                for candidate in cluster_map.keys()
                if norm_map[candidate] in norm_label
            ]
            if not matches:
                unclustered.append(label)
                continue

            # best match is the shortest norm match; then the most frequent label
            best_match = min(
                matches,
                key=lambda match: (
                    len(match.strip().split()),
                    -counter[match],
                ),
            )
            if best_match != label:
                cluster_map[best_match].append(label)

        clusters = [
            [main_label]
            + sorted(
                alt_labels,
                key=lambda label: (
                    len(label.strip().split()),
                    -counter[label],
                ),
            )
            for main_label, alt_labels in cluster_map.items()
            if alt_labels
        ]

        return clusters, unclustered

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

        print("Creating mappings for entities")
        # In case identical text pieces get different lemmas, e.g. due to POS-tagging
        # differences, the most popular ones is selected as THE lemma.
        # Ideal? No. Good enough? Yes.
        entity_norm = {
            text: Counter(pair[1] for pair in text_lemma_pairs).most_common(1)[0][0]
            for text, text_lemma_pairs in _group_by_key(
                ((e.text, e.trimmed_and_normalized("entity")) for e in entities),
                lambda x: x[0],
            )
        }
        super_entity_labels = {e.text for e in entities if e.max_entity}
        super_entity_clusters, unclustered = self._cluster_via_labels(
            [e.text for e in entities],
            is_main_label=lambda text: text in super_entity_labels,
            get_norm_label=lambda text: entity_norm[text],
        )
        entity_clusters = [
            sorted(sub_cluster, key=len)
            for cluster in super_entity_clusters + [unclustered]
            for _, sub_cluster in _group_by_key(cluster, lambda text: entity_norm[text])
        ]

        print("Creating mappings for predicates")
        predicate_norm = {
            text: Counter(pair[1] for pair in text_lemma_pairs).most_common(1)[0][0]
            for text, text_lemma_pairs in groupby(
                [(p.text, p.trimmed_and_normalized("relation")) for p in predicates],
                lambda x: x[0],
            )
        }
        predicate_clusters, _ = self._cluster_via_labels(
            [p.text for p in predicates],
            get_norm_label=lambda text: predicate_norm[text],
        )

        mappings = Mappings(
            entities=self._mapping_to_first_member(entity_clusters),
            super_entities=self._mapping_to_first_member(super_entity_clusters),
            predicates=self._mapping_to_first_member(predicate_clusters),
        )

        return mappings
