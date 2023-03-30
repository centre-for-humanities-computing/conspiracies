import networkx as nx
import random
import json
from collections import Counter
import matplotlib.pyplot as plt


def load_json(file_path: str):
    with open(file_path, mode="r", encoding="utf8") as f:
        data = json.load(f)
    return data


def most_frequent_tuples(lst, n):
    counter = Counter()
    for tup in lst:
        for string in tup:
            counter[string] += 1
    most_common_strings = set(string for string, count in counter.most_common(n))
    result = []
    for tup in lst:
        if any(string in most_common_strings for string in tup):
            result.append(tup)
    return result


def create_network_graph(
    node_list,
    k=0.3,
    node_size_mult=4,
    fontsize=12,
    color="#2a89d6",
):
    G = nx.Graph()
    G.add_edges_from(node_list)
    c = Counter(node_list)
    for u, v, d in G.edges(data=True):
        d["weight"] = c[u, v]
    # pos = nx.random_layout(G)
    pos = nx.fruchterman_reingold_layout(G, k=k)
    # pos=nx.shell_layout(G)

    degrees = nx.degree(G)

    plt.figure(figsize=(8, 8))
    nx.draw(
        G,
        pos,
        node_size=[k[1] ** node_size_mult for k in degrees],
        node_color=color,
        edge_color=color + "80",
        # width=0.2,
        width=[
            0.2 if d["weight"] < 0.2 else d["weight"] for _, _, d in G.edges(data=True)
        ],
    )

    for node, (x, y) in pos.items():
        plt.text(x, y, node, fontsize=fontsize, ha="left", va="bottom")
    return G


week_1_nodes_edges = load_json(
    "extracted_triplets_papers/covid_week_1/nodes_edges.json",
)
week_2_nodes_edges = load_json(
    "extracted_triplets_papers/covid_week_2/nodes_edges.json",
)

non_self_1 = [(e1, e2) for e1, e2 in week_1_nodes_edges["nodes"] if e1 != e2]
only_most_frequent_1 = most_frequent_tuples(non_self_1, 10)
non_self_2 = [(e1, e2) for e1, e2 in week_2_nodes_edges["nodes"] if e1 != e2]
only_most_frequent_2 = most_frequent_tuples(non_self_2, 10)

x_graph_1 = create_network_graph(
    only_most_frequent_1,
    k=0.6,
    node_size_mult=2.5,
    fontsize=11,
)

x_graph_2 = create_network_graph(
    only_most_frequent_2,
    k=0.6,
    node_size_mult=2.5,
    fontsize=11,
)
