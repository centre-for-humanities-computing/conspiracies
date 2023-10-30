from conspiracies.visualization.graph import (
    get_nodes_edges,
    create_network_graph,
    spring_layout,
)

# Twitter
twitter_week_1_nodes, twitter_week_1_edges = get_nodes_edges(
    "extracted_triplets_tweets/covid_week_1",
    "paraphrase_dim=40_neigh=15_clust=5_samp=3_nodes_edges.json",
    n_most_frequent=3,
)

# GReens
twitter_week_1_graph = create_network_graph(
    twitter_week_1_nodes,
    twitter_week_1_edges,
    title="Twitter (GPT-3): First week of the lockdown",
    k=2.5,
    edge_quantile_value=0.9,
    save="fig/twitter_week_1",
)


# # No få
# twitter_week_1_nodes_rm_få, twitter_week_1_edges_rm_få = get_nodes_edges(
#     "extracted_triplets_tweets/covid_week_1",
#     "paraphrase_dim=40_neigh=15_clust=5_samp=3_nodes_edges.json",
#     remove_custom_nodes=["få"],
#     hard_filter=True,
# )
# twitter_week_1_rm_få = create_network_graph(
#     twitter_week_1_nodes_rm_få,
#     twitter_week_1_edges_rm_få,
#     title="Covid-19 lockdown week 1 - Twitter",
#     k=2.5,
#     node_color="#A82800",
#     fontsize=11,
#     save="fig/twitter_week_1_graph_rm_få",
# )


# With old triplet extraction instead of GPT
twitter_week_1_nodes_multi, twitter_week_1_edges_multi = get_nodes_edges(
    "extracted_triplets_tweets/covid_week_1_multi",
    "paraphrase_dim=40_neigh=15_clust=5_samp=3_nodes_edges.json",
)

twitter_week_1_graph_multi = create_network_graph(
    twitter_week_1_nodes_multi,
    twitter_week_1_edges_multi,
    title="Twitter (Multi2OIE): First week of the lockdown",
    k=3.5,
    edge_quantile_value=0.8,
    save="fig/twitter_week_1_multi_no_labels",
    draw_labels=False,
)

# Mink start
twitter_mink_start_nodes, twitter_mink_start_edges = get_nodes_edges(
    "extracted_triplets_tweets/mink_start",
    "paraphrase_dim=40_neigh=15_clust=5_samp=3_nodes_edges.json",
    hard_filter=True,
)

twitter_mink_start_graph = create_network_graph(
    twitter_mink_start_nodes,
    twitter_mink_start_edges,
    title="Twitter (GPT-3): First week of the mink case",
    layout=spring_layout,
    k=4,
    edge_quantile_value=0.83,
    save="fig/twitter_mink_start",
)

twitter_mink_start_nodes_multi, twitter_mink_start_edges_multi = get_nodes_edges(
    "extracted_triplets_tweets/mink_start_multi",
    "paraphrase_dim=40_neigh=15_clust=5_samp=3_nodes_edges.json",
)

twitter_mink_start_graph_multi = create_network_graph(
    twitter_mink_start_nodes_multi,
    twitter_mink_start_edges_multi,
    title="Twitter (Multi2OIE): First week of the mink case",
    k=3,
    save="fig/twitter_mink_start_multi",
)

### News papers

# Mink start

news_mink_start_nodes, news_mink_start_edges = get_nodes_edges(
    "extracted_triplets_papers/mink_start",
    "paraphrase_dim=40_neigh=15_clust=5_samp=3_nodes_edges.json",
    hard_filter=True,
)

news_mink_start_graph = create_network_graph(
    news_mink_start_nodes,
    news_mink_start_edges,
    title="Newspapers: First week of the mink case",
    layout=spring_layout,
    k=3,
    edge_quantile_value=0.83,
    save="fig/news_mink_start",
)

# mink - Mogens Jensen resigning

news_mink_mj_nodes, news_mink_mj_edges = get_nodes_edges(
    "extracted_triplets_papers/mink_mogens_jensen",
    "paraphrase_dim=40_neigh=15_clust=5_samp=3_nodes_edges.json",
    hard_filter=True,
)

news_mink_mj_graph = create_network_graph(
    news_mink_mj_nodes,
    news_mink_mj_edges,
    title="Newspapers: Mogens Jensen's resignation",
    layout=spring_layout,
    k=2,
    save="fig/news_mink_mj",
)

# Covid week 1

news_week_1_nodes, news_week_1_edges = get_nodes_edges(
    "extracted_triplets_papers/covid_week_1",
    "paraphrase_dim=40_neigh=15_clust=5_samp=3_nodes_edges.json",
)

news_week_2_nodes, news_week_2_edges = get_nodes_edges(
    "extracted_triplets_papers/covid_week_2",
    "paraphrase_dim=40_neigh=15_clust=5_samp=3_nodes_edges.json",
)


news_week_1_graph = create_network_graph(
    news_week_1_nodes,
    news_week_1_edges,
    title="Newspapers: First week of the lockdown",
    save="fig/news_week_1",
    k=2.5,
)

news_week_2_graph = create_network_graph(
    news_week_2_nodes,
    news_week_2_edges,
    title="Newspapers: Second week of the lockdown",
    k=2.5,
    save="fig/news_week_2",
)
