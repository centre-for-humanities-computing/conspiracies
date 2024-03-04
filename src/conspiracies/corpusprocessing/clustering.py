from collections import defaultdict
from typing import List, Callable, Any, Hashable, Dict

import networkx
import numpy as np
from hdbscan import HDBSCAN
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import StandardScaler
from umap import UMAP

from conspiracies.common.modelchoice import ModelChoice
from conspiracies.corpusprocessing.triplet import TripletField, Triplet


class Mappings(BaseModel):
    entities: Dict[str, str]
    predicates: Dict[str, str]

    def map_entity(self, entity: str):
        return self.entities[entity] if entity in self.entities else entity

    def map_predicate(self, predicate: str):
        return self.predicates[predicate] if predicate in self.predicates else predicate


class Clustering:
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

    def _cluster(
        self,
        fields: List[TripletField],
    ):
        model = self._get_embedding_model()
        embeddings = model.encode([field.text for field in fields])
        embeddings = StandardScaler().fit_transform(embeddings)

        if self.n_dimensions is not None:
            print("Reducing embedding space")
            reducer = UMAP(n_components=self.n_dimensions, n_neighbors=self.n_neighbors)
            embeddings = reducer.fit_transform(embeddings)

        hdbscan_model = HDBSCAN(
            min_cluster_size=self.min_cluster_size,
            min_samples=self.min_samples,
        )
        hdbscan_model.fit(embeddings)

        clusters = defaultdict(list)
        for field, embedding, label, probability in zip(
            fields,
            embeddings,
            hdbscan_model.labels_,
            hdbscan_model.probabilities_,
        ):
            # skip noise and low confidence
            if label == -1 or probability < 0.1:
                continue
            clusters[label].append((field, embedding))

        merged = self._combine_clusters(
            list(clusters.values()),
            get_combine_key=lambda t: t[0].text,
        )
        merged = self._combine_clusters(
            merged,
            get_combine_key=lambda t: t[0].head,
        )

        # sort by how "prototypical" a member is in the cluster
        for cluster in merged:
            mean = np.mean(np.stack([t[1] for t in cluster]), axis=0)
            cluster.sort(key=lambda t: np.inner(t[1], mean), reverse=True)

        # get rid of embeddings in returned list
        return [[t[0] for t in cluster] for cluster in merged]

    @staticmethod
    def _mapping_to_first_member(clusters: List[List[TripletField]]) -> Dict[str, str]:
        return {
            member: cluster[0].text
            for cluster in clusters
            for member in set(member.text for member in cluster)
        }

    def create_mappings(self, triplets: List[Triplet]) -> Mappings:
        subjects = [triplet.subject for triplet in triplets]
        objects = [triplet.object for triplet in triplets]
        entities = subjects + objects
        predicates = [triplet.predicate for triplet in triplets]

        entity_clusters = self._cluster(entities)
        predicate_clusters = self._cluster(predicates)

        mappings = Mappings(
            entities=self._mapping_to_first_member(entity_clusters),
            predicates=self._mapping_to_first_member(predicate_clusters),
        )

        return mappings
