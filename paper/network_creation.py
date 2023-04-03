import networkx as nx
import json
from collections import Counter
import matplotlib.pyplot as plt
import os
import numpy as np
import typing


def load_json(file_path: str):
    with open(file_path, mode="r", encoding="utf8") as f:
        data = json.load(f)
    return data


def most_frequent_tuples(node_dict: dict, n):
    counter: typing.Counter = Counter()
    for i, tup in node_dict.items():
        for string in tup:
            counter[string] += 1
    most_common_strings = set(string for string, count in counter.most_common(n))
    result = {}
    for i, tup in node_dict.items():
        if any(string in most_common_strings for string in tup):
            result[i] = tup
    return result


def get_nodes_edges(
    event: str,
    file: str,
    remove_self_edges: bool = True,
    n_most_frequent: int = 10,
):
    nodes_edges = load_json(
        os.path.join("extracted_triplets_papers", event, file),
    )
    nodes = {i: tuple(edge) for i, edge in enumerate(nodes_edges["nodes"])}
    edges = {i: edge for i, edge in enumerate(nodes_edges["edges"])}

    # Removing self edges and only keeping the most frequent nodes
    if remove_self_edges:
        nodes = {i: (e1, e2) for i, (e1, e2) in nodes.items() if e1 != e2}
    most_frequent_nodes = most_frequent_tuples(nodes, n_most_frequent)
    associated_edges = {
        i: edge for i, edge in edges.items() if i in most_frequent_nodes.keys()
    }
    return most_frequent_nodes, associated_edges


def quantile_min_value(lst, quantile):
    q = np.quantile(lst, quantile)
    return min(filter(lambda x: x >= q, lst))


def create_network_graph(
    node_list,
    edge_list,
    k=0.3,
    node_size_mult=4,
    fontsize=12,
    color="#2a89d6",
):
    G = nx.Graph()
    G.add_edges_from(list(node_list.values()))
    c = Counter(list(node_list.values()))  # edge weights = frequency of edge
    for u, v, d in G.edges(data=True):
        # Make the graph undirected - for some reason, the tuples are sometimes reversed in the edge list
        d["weight"] = c[(u, v)] + c[(v, u)]

    edge_label_weight_cutoff = quantile_min_value(list(c.values()), 0.90)
    edges_to_draw = {}
    for n, nodes in node_list.items():
        if c[nodes] >= edge_label_weight_cutoff:
            edges_to_draw[nodes] = edge_list[n]

    pos = nx.fruchterman_reingold_layout(G, k=k)
    # pos = nx.kamada_kawai_layout(G)

    degrees = nx.degree(G)

    plt.figure(figsize=(8, 8))
    nx.draw(
        G,
        pos,
        node_size=[k[1] ** node_size_mult for k in degrees],
        node_color=color,
        edge_color=color + "80",
        width=[d["weight"] * 2 for _, _, d in G.edges(data=True)],
    )
    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels=edges_to_draw,
        font_size=fontsize - 2,
        label_pos=0.5,
        bbox=dict(
            facecolor="white",
            edgecolor=color,
            alpha=0.8,
            boxstyle="round,pad=0.2",
        ),
    )

    offset = 0.01
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
        plt.text(
            x,
            y,
            node,
            fontsize=fontsize,
            color="#404040",
            ha=h_align,
            va=v_align,
            bbox=dict(
                facecolor="white",
                edgecolor="#404040",
                alpha=0.8,
                boxstyle="round,pad=0.1",
            ),
        )
    return G


week_1_dansk_nodes, week_1_dansk_edges = get_nodes_edges(
    "covid_week_1",
    "danskBERT_nodes_edges.json",
)
week_1_para_nodes, week_1_para_edges = get_nodes_edges(
    "covid_week_1",
    "paraphrase_nodes_edges.json",
)
week_2_dansk_nodes, week_2_dansk_edges = get_nodes_edges(
    "covid_week_2",
    "danskBERT_nodes_edges.json",
)
week_2_para_nodes, week_2_para_edges = get_nodes_edges(
    "covid_week_2",
    "paraphrase_nodes_edges.json",
)


week_1_dansk_graph = create_network_graph(
    week_1_dansk_nodes,
    week_1_dansk_edges,
    k=0.6,
    node_size_mult=2.5,
    fontsize=11,
)

week_1_para_graph = create_network_graph(
    week_1_para_nodes,
    week_1_para_edges,
    k=1,
    node_size_mult=2.5,
    fontsize=10,
)

week_2_dansk_graph = create_network_graph(
    week_2_dansk_nodes,
    week_2_dansk_edges,
    k=0.6,
    node_size_mult=2.5,
    fontsize=11,
)

week_2_para_graph = create_network_graph(
    week_2_para_nodes,
    week_2_para_edges,
    k=0.6,
    node_size_mult=2.5,
    fontsize=11,
)
