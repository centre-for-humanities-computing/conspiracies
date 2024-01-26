import json
from typing import Tuple, List, Dict, Optional, Union
import os
import spacy
from umap import UMAP
from hdbscan import HDBSCAN
from sentence_transformers import SentenceTransformer
from stop_words import get_stop_words
from sklearn.preprocessing import StandardScaler
from numpy import ndarray
from collections import Counter
import random
import argparse


def read_txt(path: str):
    with open(path, mode="r", encoding="utf8") as f:
        lines = f.read().splitlines()
    return lines


def triplet_from_line(line: str) -> Union[Tuple[str, str, str], None]:
    """Converts a line from a txt file to a triplet.

    Lines that are not exactly three elements are ignored.
    All elements in the triplet are stripped of whitespace and lowercased.
    Args:
        line: Line from a txt file
    Returns:
        triplet: Triplet
    """
    as_list = line.split(", ")
    if len(as_list) != 3:
        return None
    if line in ["Subject, Predicate, Object", "---, ---, ---"]:
        return None
    return tuple(map(str.strip, map(str.lower, as_list)))  # type: ignore


def filter_triplets_with_stopwords(
    triplets: List[Tuple[str, str, str]],
    stopwords: List[str],
    soft: bool = True,
) -> List[Tuple[str, str, str]]:
    """Filters triplets that contain a stopword.

    Args:
        triplets: List of triplets. A triplet is a tuple of
            three strings.
        stopwords: List of stopwords
        soft: If True, only the subject and object are checked for stopwords. If
            False, the whole triplet is checked.
    Returns:
        filtered_triplets: List of triplets without
        stopwords
    """
    filtered_triplets = []
    if soft:
        for triplet in triplets:
            subject, predicate, obj = triplet
            if subject not in stopwords and obj not in stopwords:
                filtered_triplets.append(triplet)
    else:
        for triplet in triplets:
            if not any(stopword in triplet for stopword in stopwords):
                filtered_triplets.append(triplet)
    return filtered_triplets


def load_triplets(
    file_path: str,
    soft_filtering: bool = True,
    shuffle: bool = True,
) -> Tuple[list, list, list, list]:
    """Loads triplets from a file and filters them.

    Args:
        file_name: Name of the file to load triplets from
        soft_filtering: Whether to use soft filtering or not
        shuffle: Whether to shuffle the triplets or not
    Returns:
        subjects: List of subjects
        predicates: List of predicates
        objects: List of objects
        filtered_triplets: List of filtered triplets
    """
    triplets_list: List[Tuple[str, str, str]] = []
    data = read_txt(file_path)
    triplets_list = [
        triplet_from_line(line)
        for line in data
        if triplet_from_line(line)  # type: ignore
    ]
    filtered_triplets = filter_triplets_with_stopwords(
        triplets_list,
        get_stop_words("danish"),
        soft=soft_filtering,
    )

    if shuffle:
        random.shuffle(filtered_triplets)

    subjects = [
        triplet[0]
        for triplet in filtered_triplets
        if triplet[0] not in ["Subject", "---"]
    ]
    predicates = [
        triplet[1]
        for triplet in filtered_triplets
        if triplet[0] not in ["Predicate", "---"]
    ]
    objects = [
        triplet[2]
        for triplet in filtered_triplets
        if triplet[0] not in ["Object", "---"]
    ]
    return subjects, predicates, objects, filtered_triplets


def freq_of_most_frequent(list_of_strings: List[str]) -> Tuple[str, float]:
    """Calculates the frequency of the most frequent element in a list of
    strings.

    Frequency is measured as how much of the list the most frequent element takes up,
        percentage-wise.
    Args:
        list_of_strings: List of strings to find the most frequent element
        in
    Returns:
        most_common_string (str), percentage: Frequency of the most frequent
        element, its percentage
    """
    most_common = Counter(list_of_strings).most_common(1)[0]
    most_common_string = most_common[0]
    percentage = most_common[1] / len(list_of_strings)
    return most_common_string, percentage


def most_frequent_token(list_of_strings: List[str], nlp) -> Tuple[str, float]:
    """Finds the most frequent token in a list of strings.

    Args:
        list_of_strings: List of strings to find the most frequent token in
        nlp: Spacy language model
    Returns:
        most_common_token: Most frequent token
    """
    token_list = []
    for string in list_of_strings:
        doc = nlp(string)
        for token in doc:
            token_list.append(token.text)
    most_common_token, percentage = freq_of_most_frequent(token_list)
    return most_common_token, percentage


def get_cluster_label(
    cluster: List[Tuple[str, int]],
    nlp,
    first_cutoff: float = 0.8,
    min_cluster_length: int = 10,
    second_cutoff: float = 0.3,
) -> Union[str, None]:
    """Finds the most frequent token in a cluster.

    Args:
        cluster: Cluster of elements
        nlp: Spacy language model
        certain_cutoff: Minimum percentage of the most frequent token.
            All clusters that have a most frequent token at least as frequent as this
            value gets that token as label.
    Returns:
        label: The cluster label according to the rules
    """
    cluster_strings = [element[0] for element in cluster]
    most_common, percentage = freq_of_most_frequent(cluster_strings)

    # If the most frequent token is frequent enough, use it as label
    if percentage >= first_cutoff:
        return most_common

    else:
        # If the cluster is not clearly defined and it is short,
        # return None to indicate it should be removed
        if len(cluster) < min_cluster_length:
            return None

        # Clusters that are large and relatively clearly defined
        if percentage >= second_cutoff:
            return most_common

        # If the cluster is not clearly defined, find the most frequent token
        most_common_token, percentage = most_frequent_token(cluster_strings, nlp)

        # The most frequent token must be frequent enough to be used as label,
        # otherwise return None to indicate it should be removed
        if percentage >= 0.2:  # TODO: Make this a parameter
            return most_common_token
        else:
            return None


def cluster_dict(topic_labels: ndarray, input_list: List[str]) -> Dict[int, List[str]]:
    """Creates a dictionary containing all elements in a cluster from a
    BERTopic model.

    Only clusters with at least `cutoff` elements.
    Args:
        topic_model: BERTopic model
        input_list: The list of string that were used to create the BERTopic
        model
        cutoff: Minimum number of elements in a cluster
    Returns:
        cluster_dict: Dictionary of clusters
    """
    assert len(topic_labels) == len(
        input_list,
    ), "Length of topic labels and input list must be equal"
    # topic_info = topic_model.get_topic_info()
    # relevant_topics = topic_info.loc[topic_info["Count"] >= cutoff]
    cluster_dict: Dict[int, list] = {i: [] for i in range(max(topic_labels) + 1)}
    topic_tuples = zip(topic_labels, input_list)
    for index, (topic_n, element) in enumerate(topic_tuples):
        if topic_n != -1:
            cluster_dict[topic_n].append((element, index))
    return cluster_dict


def label_clusters(
    cluster_dict,
    nlp,
    first_cutoff: float = 0.8,
    min_cluster_length: int = 10,
    second_cutoff: float = 0.3,
    predicates: bool = False,
):
    """Labels clusters according to the rules in `get_cluster_label`.
    Args:
        cluster_dict: Dictionary of clusters to label
        nlp: Spacy language model to use for tokenization of less defined
            clusters
        first_cutoff: Minimum percentage of the most frequent element.
            All clusters that have a most frequent element at least as frequent as this
            value gets that element as label.
        min_cluster_length: Minimum number of elements in a cluster
        second_cutoff: Minimum percentage of the most frequent element.
            This cutoff is only used if the cluster has a less clearly defined label,
            but is still large enough.

    Returns:
        dict_with_labels: Dictionary of clusters with
        labels
            The keys are the labels, the values are dictionaries with the keys
                "cluster" (final elements in the cluster), and
                "n_elements" (number of elements in the final cluster)
    """
    if predicates:
        min_cluster_length = 1
        second_cutoff = 0.0
    dict_with_labels: Dict[str, dict] = {}
    # Get the label for each cluster
    for cluster in cluster_dict.values():
        cluster_label = get_cluster_label(
            cluster,
            nlp,
            first_cutoff,
            min_cluster_length,
            second_cutoff,
        )
        if cluster_label:  # If the cluster is not None
            if (
                cluster_label in dict_with_labels.keys()
            ):  # If the label already exists, merge
                dict_with_labels[cluster_label]["cluster"].extend(cluster)
                dict_with_labels[cluster_label]["n_elements"] += len(cluster)
            else:  # If the label does not exist, create a new entry
                dict_with_labels[cluster_label] = {}
                dict_with_labels[cluster_label]["cluster"] = cluster
                dict_with_labels[cluster_label]["n_elements"] = len(cluster)

    # Remove clusters that are too small even after merging identical clusters
    clusters_to_keep = {
        label: content
        for label, content in dict_with_labels.items()
        if content["n_elements"] > min_cluster_length
    }
    return clusters_to_keep


def embed_and_cluster(
    list_to_embed: List[str],
    embedding_model: str = "vesteinn/DanskBERT",
    n_dimensions: int = 40,
    n_neighbors: int = 15,
    min_cluster_size: int = 5,
    min_samples: int = 3,
    min_topic_size: int = 10,
    predicates: bool = False,
):
    """Embeds and clusters a list of strings.

    Args:
        list_to_embed: List of strings to embed and cluster
        n_dimensions: Number of dimensions to reduce the embedding space to
        n_neighbors: Number of neighbors to use for UMAP
        min_cluster_size: Minimum cluster size for HDBscan
        min_samples: Minimum number of samples for HDBscan
        min_topic_size: Minimum number of elements in a cluster
    Returns:
        clusters: Dictionary of clusters with labels
            The keys are the labels, the values are dictionaries with the keys
                "cluster" (final elements in the cluster), and
                "n_elements" (number of elements in the final cluster)
    """

    embedding_model = SentenceTransformer(embedding_model)

    # Embed and reduce embdding space
    print("Embedding and reducing embedding space")
    embeddings = embedding_model.encode(list_to_embed)  # type: ignore
    scaled_embeddings = StandardScaler().fit_transform(embeddings)
    reducer = UMAP(n_components=n_dimensions, n_neighbors=n_neighbors)
    reduced_embeddings = reducer.fit_transform(scaled_embeddings)

    # Cluster with HDBscan
    print("Clustering")
    hdbscan_model = HDBSCAN(min_cluster_size=min_cluster_size, min_samples=min_samples)
    hdbscan_model.fit(reduced_embeddings)
    hdbscan_labels = hdbscan_model.labels_
    assert len(hdbscan_labels) == len(
        list_to_embed,
    ), "Length of hdbscan labels and input list must be equal"
    clusters = cluster_dict(hdbscan_labels, list_to_embed)

    # Label and prune clusters
    print("Labeling clusters")
    nlp = spacy.load("da_core_news_sm")
    labeled_clusters = label_clusters(
        clusters,
        nlp,
        min_cluster_length=min_topic_size,
        predicates=predicates,
    )

    return labeled_clusters


def create_nodes_and_edges(
    subj_obj_clusters: Dict[str, Dict[str, List[str]]],
    predicate_clusters: Dict[str, Dict[str, List[str]]],
    n_elements: int,
    no_predicate_filler: str = "",
    save: Optional[Union[bool, str]] = False,
):
    """Creates nodes and edges from clusters of subjects, objects and predicates.
    Args:
        subj_obj_clusters : Dictionary of clusters
            with labels
            The keys are the labels, the values are dictionaries with the keys
                "cluster" (final elements in the cluster), and
                "n_elements" (number of elements in the final cluster)
        predicate_clusters : Dictionary of clusters
            with labels
            The keys are the labels, the values are dictionaries with the keys
                "cluster" (final elements in the cluster), and
                "n_elements" (number of elements in the final cluster)
        no_predicate_filler : String to use as filler for predicates that do not
            have a cluster
        save : If a string, nodes and edges are saved to a
            json file. If False, does not save.

    Returns:
        nodes, edges: nodes and edges for the graph
    """

    labelled_subjects = {i: "" for i in range(0, n_elements)}
    labelled_objects = {i: "" for i in range(0, n_elements)}

    for label, content in subj_obj_clusters.items():
        cluster = content["cluster"]
        for _, index in cluster:  # type: ignore
            if index < n_elements:  # type: ignore
                labelled_subjects[index] = label  # type: ignore
            else:
                labelled_objects[index - n_elements] = label  # type: ignore
    labelled_subjects = {  # type: ignore
        i: label
        for i, label in labelled_subjects.items()
        if label != ""  # type: ignore
    }
    labelled_objects = {
        i: label for i, label in labelled_objects.items() if label != ""
    }

    labelled_predicates = {i: "" for i in range(0, n_elements)}
    for label, content in predicate_clusters.items():
        cluster = content["cluster"]
        for _, index in cluster:  # type: ignore
            labelled_predicates[index] = label  # type: ignore
    labelled_predicates = {
        i: label for i, label in labelled_predicates.items() if label != ""
    }

    nodes = []
    edges = []
    for s_index, subject in labelled_subjects.items():
        if s_index in labelled_objects.keys():
            nodes.append((subject, labelled_objects[s_index]))
            if s_index in labelled_predicates.keys():
                edges.append(labelled_predicates[s_index])
            else:
                edges.append(no_predicate_filler)

    if save:
        with open(save, "w") as f:
            json.dump({"nodes": nodes, "edges": edges}, f)
    return nodes, edges


def main(
    path: str,
    embedding_model: str,
    dim=40,
    n_neighbors=15,
    min_cluster_size=5,
    min_samples=3,
    min_topic_size=20,
    save: bool = False,
):
    # Load triplets
    print("Loading triplets")
    subjects, predicates, objects, filtered_triplets = load_triplets(
        path,
        soft_filtering=True,
        shuffle=True,
    )

    if save and not isinstance(save, str):
        save = path.replace(
            "triplets.txt",
            f"{embedding_model}_dim={dim}_neigh={n_neighbors}"
            f"_clust={min_cluster_size}_samp={min_samples}_nodes_edges.json",
        )  # type: ignore

    model = (
        "vesteinn/DanskBERT"
        if embedding_model == "danskBERT"
        else "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    )

    print(
        f"Dimensions: {dim}, neighbors: {n_neighbors}, min cluster size: "
        f"{min_cluster_size}, samples: {min_samples}, min topic size: {min_topic_size}",
    )
    print("\n_________________\n")
    print("Embedding and clustering predicates")
    # For predicate, we wanna keep all clusters -> min_topic_size=1
    predicate_clusters = embed_and_cluster(
        list_to_embed=predicates,
        embedding_model=model,
        n_dimensions=dim,
        n_neighbors=n_neighbors,
        min_cluster_size=min_cluster_size,
        min_samples=min_samples,
        min_topic_size=1,
        predicates=True,
    )

    print("\n_________________\n")
    print("Embedding and clustering subjects and objects together")
    subj_obj = subjects + objects
    subj_obj_clusters = embed_and_cluster(
        list_to_embed=subj_obj,
        embedding_model=model,
        n_dimensions=dim,
        n_neighbors=n_neighbors,
        min_cluster_size=min_cluster_size,
        min_samples=min_samples,
        min_topic_size=min_topic_size,
    )

    # Create nodes and edges
    print("Creating nodes and edges")

    assert (
        len(subjects) == len(objects) == len(predicates)
    ), "Subjects, objects and predicates must have the same length"
    nodes, edges = create_nodes_and_edges(
        subj_obj_clusters,
        predicate_clusters,
        len(subjects),
        save=save,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-e",
        "--event",
        type=str,
        help="Event to cluster. Must include name of source folder (newspapers or "
        "twitter) and event",
    )
    parser.add_argument(
        "-emb",
        "--embedding_model",
        type=str,
        default="paraphrase",
        help="""Which embedding model to use, default is paraphrase. 
        The other option is danskBERT""",
    )
    parser.add_argument(
        "-dim",
        "--n_dimensions",
        type=int,
        default=40,
        help="Number of dimensions to reduce the embedding space to",
    )
    parser.add_argument(
        "-neigh",
        "--n_neighbors",
        type=int,
        default=15,
        help="Number of neighbors to use for UMAP",
    )
    parser.add_argument(
        "-min_clust",
        "--min_cluster_size",
        type=int,
        default=5,
        help="Minimum cluster size for HDBscan",
    )
    parser.add_argument(
        "-min_samp",
        "--min_samples",
        type=int,
        default=3,
        help="Minimum number of samples for HDBscan",
    )
    parser.add_argument(
        "-save",
        "--save",
        type=bool,
        default=False,
        help="whether or not to save nodes and edges to json file",
    )

    args = parser.parse_args()
    path = os.path.join(args.event, "triplets.txt")
    main(
        path,
        embedding_model=args.embedding_model,
        dim=args.n_dimensions,
        n_neighbors=args.n_neighbors,
        min_cluster_size=args.min_cluster_size,
        min_samples=args.min_samples,
        save=args.save,
    )
