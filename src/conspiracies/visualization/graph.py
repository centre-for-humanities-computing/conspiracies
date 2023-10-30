import networkx as nx
import json
from collections import Counter
import matplotlib.pyplot as plt
import os
import numpy as np
import ndjson
import typing
from typing import Dict, Tuple, Optional, List
from networkx.drawing.layout import (
    fruchterman_reingold_layout,
    kamada_kawai_layout,
)


def load_json(file_path: str) -> dict:
    """Loads a json file.

    Args:
        file_path (str): path to the json file

    Returns:
        data (dict): the data from the file as a dictionary
    """
    with open(file_path, mode="r", encoding="utf8") as f:
        data = json.load(f)
    return data


def most_frequent_tuples(
    node_dict: Dict[int, tuple],
    n: int,
    hard_filter: bool = False,
) -> Dict[int, tuple]:
    """Find the tuples that contain one of the n most frequent elements.

    Args:
        node_dict (dict): dictionary with node ids as keys and node pairs as values
        n (int): The number of most frequent elements to keep

    Returns:
        result (dict): filtered dictionary with node ids as keys and node pairs as
            values
    """
    element_counter: typing.Counter = Counter()
    # Count the frequency for all elements and identify the n most frequent
    for i, tup in node_dict.items():
        for string in tup:
            element_counter[string] += 1
    most_common_strings = set(string for string, _ in element_counter.most_common(n))
    highest_freq = element_counter.most_common(1)[0][1]

    # Only keep the nodes that contain one of the most frequent elements
    result = {}
    for i, tup in node_dict.items():
        if any(string in most_common_strings for string in tup):
            fr = sum([element_counter[tup[0]], element_counter[tup[1]]])
            # If hard_filter, keep only pairs of nodes at least at frequent
            # as the most frequent node
            if hard_filter:
                if fr >= highest_freq:
                    result[i] = tup
            else:
                result[i] = tup
    return result


def get_nodes_edges(
    event: str,
    file: str,
    remove_self_edges: bool = True,
    remove_custom_nodes: Optional[List[str]] = None,
    n_most_frequent: int = 10,
    hard_filter: bool = False,
    save: Optional[str] = None,
) -> Tuple[Dict[int, tuple], Dict[int, tuple]]:
    """Loads nodes and edges from a json file, removes self edges and only
    keeps the n most frequent nodes.

    Args:
        event (str): the name of the event
        file (str): the specific file to load. Must be placed in a folder with the event
            name
        remove_self_edges (bool, optional): Whether or not to remove self edges.
            Defaults to True.
        remove_custom_nodes (list, optional): A list of nodes to remove from the graph.
            Defaults to None.
        n_most_frequent (int, optional): The number of most frequent elements to
            include. Defaults to 10.
        hard_filter (bool, optional): Passed to most_frequent_tuples. Whether or not to
            filter away pairs of nodes that are less frequent than the single most
            frequent. Defaults to False.
        save (str, optional): If provided, the filtered nodes and edges will be saved
            to this path.

    Returns:
        Tuple[Dict[int, tuple], Dict[int, tuple]]: a dictionary with the most frequent
        nodes and a dictionary with the associated edges
    """
    nodes_edges = load_json(
        os.path.join(event, file),
    )
    nodes = {i: tuple(edge) for i, edge in enumerate(nodes_edges["nodes"])}
    edges = {i: edge for i, edge in enumerate(nodes_edges["edges"])}

    # Removing self edges and only keeping the most frequent nodes
    if remove_self_edges:
        nodes = {i: (e1, e2) for i, (e1, e2) in nodes.items() if e1 != e2}
    if remove_custom_nodes:
        nodes = {
            i: (e1, e2)
            for i, (e1, e2) in nodes.items()
            if e1 not in remove_custom_nodes and e2 not in remove_custom_nodes
        }
    most_frequent_nodes = most_frequent_tuples(nodes, n_most_frequent, hard_filter)
    associated_edges = {
        i: edge for i, edge in edges.items() if i in most_frequent_nodes.keys()
    }
    if save:
        with open(save, "w") as f:
            ndjson.dump(
                {
                    "nodes": list(most_frequent_nodes.values()),
                    "edges": list(associated_edges.values()),
                },
                f,
            )
    return most_frequent_nodes, associated_edges


def quantile_min_value(lst, quantile):
    q = np.quantile(lst, quantile)
    return min(filter(lambda x: x >= q, lst))


def min_max_normalize(list_to_normalize: list, min_constant=0.5) -> list:
    """Normalizes a list between 0 and 1 using min-max normalization.

    Args:
        list_to_normalize (list): The list to normalize

    Returns:
        list: The normalized list
    """
    min_value = min(list_to_normalize)
    max_value = max(list_to_normalize)
    if min_value == max_value:
        return list_to_normalize
    scaled_list = [(x - min_value) / (max_value - min_value) for x in list_to_normalize]
    return [x + min_constant for x in scaled_list]


def create_network_graph(
    node_list,
    edge_list,
    title: Optional[str] = None,
    layout=fruchterman_reingold_layout,
    k: float = 0.3,
    node_size_mult: float = 3000,
    node_size_min: float = 0.001,
    edge_weight_mult: float = 5,
    fontsize: int = 12,
    edge_quantile_value: float = 0.90,
    node_quantile_value: Optional[float] = None,
    node_color: str = "#146D25",
    edge_color: str = "#54A463",
    fig_size: int = 10,
    plot_coordinates: bool = False,
    seed: Optional[int] = None,
    draw_labels: bool = True,
    save=False,
):
    G = nx.Graph()
    G.add_edges_from(list(node_list.values()))
    c = Counter(list(node_list.values()))  # edge weights = frequency of edge
    for u, v, d in G.edges(data=True):
        # Make the graph undirected - for some reason, the tuples are sometimes reversed
        # in the edge list
        d["weight"] = c[(u, v)] + c[(v, u)]

    edge_label_weight_cutoff = quantile_min_value(list(c.values()), edge_quantile_value)
    edges_to_draw = {}
    for n, nodes in node_list.items():
        if c[nodes] >= edge_label_weight_cutoff:
            edges_to_draw[nodes] = edge_list[n]

    if layout == kamada_kawai_layout:
        pos = layout(G, scale=2)
    else:
        pos = layout(G, k=k, seed=seed)

    degrees = nx.degree(G)
    normalized_degrees = min_max_normalize(
        [d[1] for d in degrees],
        min_constant=node_size_min,
    )

    plt.figure(figsize=(fig_size, fig_size))
    if title:
        plt.title(
            title,
            color="k",
            fontsize=fontsize + 8,
        )

    edge_weights = min_max_normalize([d["weight"] for _, _, d in G.edges(data=True)])

    nx.draw(
        G,
        pos,
        # node_size=non_norm_degrees,
        node_size=[d * node_size_mult for d in normalized_degrees],
        node_color=node_color,
        edge_color=edge_color + "80",
        # width=[d["weight"] ** edge_weight_mult for _, _, d in G.edges(data=True)],
        width=[e * edge_weight_mult for e in edge_weights],
    )
    if draw_labels:
        nx.draw_networkx_edge_labels(
            G,
            pos,
            edge_labels=edges_to_draw,
            font_size=fontsize - 1,
            label_pos=0.5,
            bbox=dict(
                facecolor="white",
                edgecolor=edge_color,
                alpha=0.8,
                boxstyle="round,pad=0.2",
            ),
        )

        offset = 0.015
        for node, (x, y) in pos.items():
            h_align = "center"
            v_align = "center"
            if x < 0:
                x -= offset
                h_align = "right"
            if x > 0:
                x += offset
                h_align = "left"
            if y < 0:
                y -= offset
                v_align = "top"
            if y > 0:
                y += offset
                v_align = "bottom"
            if plot_coordinates:
                label = f"{node} ({x:.2f}, {y:.2f})"
            else:
                label = node
            if node_quantile_value:
                node_label_draw_cutoff = quantile_min_value(
                    [value for key, value in degrees],
                    node_quantile_value,
                )
                if degrees[node] >= node_label_draw_cutoff:
                    plt.text(
                        x,
                        y,
                        label,
                        fontsize=fontsize,
                        color="k",
                        ha=h_align,
                        va=v_align,
                        bbox=dict(
                            facecolor="white",
                            edgecolor=node_color,
                            alpha=0.8,
                            boxstyle="round,pad=0.1",
                        ),
                    )
            else:
                plt.text(
                    x,
                    y,
                    label,
                    fontsize=fontsize,
                    # fontname="Helvetica",
                    color="k",
                    ha=h_align,
                    va=v_align,
                    bbox=dict(
                        facecolor="white",
                        edgecolor=node_color,
                        alpha=0.8,
                        boxstyle="round,pad=0.1",
                    ),
                )
    if save:
        plt.savefig(
            f"{save}.png",
            format="PNG",
            bbox_inches="tight",
        )
    return G
