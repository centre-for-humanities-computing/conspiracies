from pathlib import Path

import networkx as nx
from collections import defaultdict
import matplotlib.pyplot as plt
from typing import Tuple, Optional, List, Union

from networkx.classes.reportviews import NodeView, EdgeView

from conspiracies.corpusprocessing.aggregation import TripletStats


def transform_triplets_to_graph_data(
    triplet_stats: TripletStats,
    top_n: int = 100,
) -> Tuple[
    List[Tuple[str, float]],
    List[Tuple[str, str, float]],
]:
    """Transforms TripletStats into graph data, considering only the top_n most
    frequent entities.

    Parameters:
    - triplet_stats: The TripletStats data structure containing entities, predicates, and their frequencies.
    - top_n: The number of top frequent entities to consider for the graph.

    Returns:
    - A tuple containing the node list and edge list for graph creation, with norm frequencies
    """

    # Sort entities based on frequency and select the top_n
    top_entities = sorted(
        triplet_stats.entities.items(),
        key=lambda x: x[1]["frequency"],
        reverse=True,
    )[:top_n]
    top_entities_set = set([te[0] for te in top_entities])

    # Filter triplets to include only those involving the top entities
    filtered_triplets = {
        key: value
        for key, value in triplet_stats.triplets.items()
        if key[0] in top_entities_set and key[2] in top_entities_set
    }

    node_connections = defaultdict(int)
    for subj, _, obj in filtered_triplets:
        node_connections[subj] += 1
        node_connections[obj] += 1

    # Prepare node and edge lists
    nodes = [(entity, node_connections[entity]) for entity, stats in top_entities]
    edges = [
        (triplet[0], triplet[2], stats["frequency"])
        for triplet, stats in filtered_triplets.items()
    ]

    return nodes, edges


def _calculate_weights(
    view_with_data: Union[NodeView, EdgeView],
    scale: Tuple[int, int],
):
    min_weight, max_weight = scale
    weights = [x[-1]["weight"] for x in view_with_data]
    max_observed = max(weights)
    return [
        (weight / max_observed) * (max_weight - min_weight) + min_weight
        for weight in weights
    ]


def create_network_graph(
    node_list: List[Tuple[str, float]],
    edge_list: List[Tuple[str, str, float]],
    node_weight_scale: Tuple[int, int] = (200, 5000),
    edge_weight_scale: Tuple[int, int] = (1, 15),
    node_color: str = "#146D25",
    edge_color: str = "#54A463",
    fig_size: (int, int) = (10, 10),
    save: Optional[str | Path] = None,
):
    """Creates and displays a network graph based on provided nodes and edges,
    with customizable visual attributes.

    Parameters:
    - node_list: List of nodes, where each node can be a string or a tuple of (node identifier, float) representing the
    node and its size factor.
    - edge_list: List of edges, where each edge is a tuple of (source node, target node, optional weight factor).
    - node_size_scale: Tuple specifying the minimum and maximum size of nodes.
    - edge_weight_scale: Tuple specifying the scale for edge widths.
    - node_color: Color of the nodes.
    - edge_color: Color of the edges.
    - fig_size: Size of the figure to display the graph.
    - save: Optional filename to save the figure. If None, the figure is not saved.
    """
    graph = nx.Graph()

    # edges
    for src, dst, weight in edge_list:
        graph.add_edge(src, dst, weight=weight)
    edge_weights = _calculate_weights(graph.edges(data=True), edge_weight_scale)

    # nodes
    for node, weight in node_list:
        graph.add_node(node, weight=weight)
    node_weights = _calculate_weights(graph.nodes(data=True), node_weight_scale)

    pos = nx.fruchterman_reingold_layout(graph, k=0.3)

    plt.figure(figsize=fig_size)
    nx.draw(
        graph,
        pos=pos,
        with_labels=True,
        node_color=node_color,
        edge_color=edge_color,
        node_size=node_weights,
        width=edge_weights,
    )

    if save:
        plt.savefig(save, format="PNG", dpi=300)

    return graph
