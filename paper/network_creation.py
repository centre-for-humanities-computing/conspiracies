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
    spring_layout,
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
        result (dict): filtered dictionary with node ids as keys and node pairs as values
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
        file (str): the specific file to load. Must be placed in a folder with the event name
        remove_self_edges (bool, optional): Whether or not to remove self edges. Defaults to True.
        n_most_frequent (int, optional): The number of most frequent elements to include. Defaults to 10.

    Returns:
        Tuple[Dict[int, tuple], Dict[int, tuple]]: a dictionary with the most frequent nodes and
        a dictionary with the associated edges
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


def create_network_graph(
    node_list,
    edge_list,
    title: str = "Narrative network graph",
    layout=fruchterman_reingold_layout,
    k: float = 0.3,
    node_size_mult: float = 4,
    fontsize: int = 12,
    color: str = "#2a89d6",
    plot_coordinates: bool = False,
    seed: Optional[int] = None,
    save=False,
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

    if layout == kamada_kawai_layout:
        # element_counter: typing.Counter = Counter()
        # for tup in node_list.values():
        #     for string in tup:
        #         element_counter[string] += 1
        # most_common = element_counter.most_common(5)

        # value_dict = {k:100 for k,_ in most_common[1:]}
        # dist = {most_common[0][1]:value_dict}
        # pos = layout(G, dist=dist)
        pos = layout(G, scale=2)
    else:
        pos = layout(G, k=k, seed=seed)

    degrees = nx.degree(G)

    plt.figure(figsize=(10, 10))
    plt.title(title, color="#115691")
    nx.draw(
        G,
        pos,
        node_size=[
            k[1] ** node_size_mult  # if k[1] ** node_size_mult < 1000 else 1000
            for k in degrees
        ],
        node_color=color,
        edge_color=color + "80",
        width=[d["weight"] ** 2 for _, _, d in G.edges(data=True)],
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
        plt.text(
            x,
            y,
            label,
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
    if save:
        plt.savefig(f"{save}.png", format="PNG")
    return G


# Twitter

twitter_week_1_nodes, twitter_week_1_edges = get_nodes_edges(
    "extracted_triplets_tweets/covid_week_1",
    "paraphrase_dim=40_neigh=15_clust=5_samp=3_nodes_edges.json",
    hard_filter=True,
    save="twitter_week_1_nodes_edges.ndjson",
)

twitter_week_1_graph = create_network_graph(
    twitter_week_1_nodes,
    twitter_week_1_edges,
    title="Covid-19 lockdown week 1 - Twitter",
    # layout=spring_layout,
    # layout=kamada_kawai_layout,
    k=2.5,
    node_size_mult=2,
    fontsize=11,
    save="fig/twitter_week_1_graph",
)

# No få
twitter_week_1_nodes_rm_få, twitter_week_1_edges_rm_få = get_nodes_edges(
    "extracted_triplets_tweets/covid_week_1",
    "paraphrase_dim=40_neigh=15_clust=5_samp=3_nodes_edges.json",
    remove_custom_nodes=["få"],
    hard_filter=True,
    save="twitter_week_1_nodes_edges.ndjson",
)

twitter_week_1_graph = create_network_graph(
    twitter_week_1_nodes_rm_få,
    twitter_week_1_edges_rm_få,
    title="Covid-19 lockdown week 1 - Twitter",
    # layout=spring_layout,
    # layout=kamada_kawai_layout,
    k=2.5,
    node_size_mult=2,
    fontsize=11,
    save="fig/twitter_week_1_graph_rm_få.png",
)

# News papers

news_week_1_nodes, news_week_1_edges = get_nodes_edges(
    "extracted_triplets_papers/covid_week_1",
    "paraphrase_dim=40_neigh=15_clust=5_samp=3_nodes_edges.json",
    save="news_week_1_nodes_edges.ndjson",
)

news_week_2_nodes, news_week_2_edges = get_nodes_edges(
    "extracted_triplets_papers/covid_week_2",
    # "paraphrase_nodes_edges.json",
    "paraphrase_dim=40_neigh=15_clust=5_samp=3_nodes_edges.json",
)


news_week_1_graph = create_network_graph(
    news_week_1_nodes,
    news_week_1_edges,
    title="Covid-19 lockdown week 1 - Newspapers",
    k=1.5,
    node_size_mult=2,
    fontsize=10,
    save="fig/news_week_1_graph",
)

news_week_2_graph = create_network_graph(
    news_week_2_nodes,
    news_week_2_edges,
    title="Week 2 of the COVID-19 lockdown",
    # layout=spring_layout,
    # layout=kamada_kawai_layout,
    k=2.5,
    node_size_mult=2,
    fontsize=10,
    save="fig/news_week_2_graph",
)


### Using danskbert instead
# week_1_dansk_nodes, week_1_dansk_edges = get_nodes_edges(
#     "covid_week_1",
#     "danskBERT_nodes_edges.json",
# )

# week_2_dansk_nodes, week_2_dansk_edges = get_nodes_edges(
#     "covid_week_2",
#     "danskBERT_nodes_edges.json",
# )

### Testing different hyperparameters

week_1_nodes_15, week_1_edges_15 = get_nodes_edges(
    "covid_week_1",
    "paraphrase_dim=40_neigh=15_clust=15_samp=5_nodes_edges.json",
)
week_1_nodes_10, week_1_edges_10 = get_nodes_edges(
    "covid_week_1",
    "paraphrase_dim=40_neigh=15_clust=10_samp=5_nodes_edges.json",
)
week_1_nodes_8, week_1_edges_8 = get_nodes_edges(
    "covid_week_1",
    "paraphrase_dim=40_neigh=15_clust=8_samp=5_nodes_edges.json",
)
week_1_nodes_5, week_1_edges_5 = get_nodes_edges(
    "covid_week_1",
    "paraphrase_dim=40_neigh=15_clust=5_samp=5_nodes_edges.json",
)
week_1_para_graph_15 = create_network_graph(
    week_1_nodes_15,
    week_1_edges_15,
    k=1,
    node_size_mult=2.5,
    fontsize=10,
)
week_1_para_graph_10 = create_network_graph(
    week_1_nodes_10,
    week_1_edges_10,
    k=1,
    node_size_mult=2.5,
    fontsize=10,
)
week_1_para_graph_8 = create_network_graph(
    week_1_nodes_8,
    week_1_edges_8,
    k=1,
    node_size_mult=2.5,
    fontsize=10,
)
week_1_para_graph_5 = create_network_graph(
    week_1_nodes_5,
    week_1_edges_5,
    k=1,
    node_size_mult=2.5,
    fontsize=10,
)


# week_1_dansk_graph = create_network_graph(
#     week_1_dansk_nodes,
#     week_1_dansk_edges,
#     k=0.6,
#     node_size_mult=2.5,
#     fontsize=11,
# )
# week_2_dansk_graph = create_network_graph(
#     week_2_dansk_nodes,
#     week_2_dansk_edges,
#     k=0.6,
#     node_size_mult=2.5,
#     fontsize=11,
# )
