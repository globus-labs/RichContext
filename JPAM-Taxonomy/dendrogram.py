from gensim.models import LdaModel
import logging
from matplotlib import pyplot as plt
import networkx as nx
from scipy.cluster.hierarchy import dendrogram
from scipy.cluster.hierarchy import linkage
from scipy.spatial.distance import pdist

import wiki

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s',
    level=logging.DEBUG
)


def topic_linkage(model):
    topic_term = model.state.get_lambda()
    distances = pdist(topic_term, metric='cosine')
    Z = linkage(distances, "ward")
    return Z


def draw_dendrogram(model):
    Z = topic_linkage(model)

    fig = plt.figure(figsize=(20, 40))
    plt.title("Topic Dendrogram")
    plt.xlabel("Distance")

    dendrogram(
        Z,
        orientation="left"
    )

    ax = fig.get_axes()[0]
    ylabels = [int(item.get_text()) for item in ax.get_yticklabels()]
    ylabels = [model.print_topic(i, topn=5) for i in ylabels]
    ax.set_yticklabels(ylabels)
    ax.tick_params(labelsize=20)


def label_hierarchy(model: LdaModel, linkage_matrix):
    G = nx.DiGraph()

    topic_labels = list()
    for topic_num in range(model.num_topics):
        topn = model.show_topic(topic_num, topn=5)
        terms = [term for term, weight in topn]
        labels = wiki.page_labels(terms, n=5)

        logging.debug(topic_num, labels)

        topic_labels.append(labels)
        G.add_node(topic_num, labels=labels)

    for id1, id2, dist, sample_cnt in linkage_matrix:
        new_id = G.number_of_nodes()
        labels1 = list(G.node[id1]["labels"])
        labels2 = list(G.node[id2]["labels"])
        new_labels = wiki.list_sca(labels1, labels2, depth=10, pl=1000)
        topic_labels.append(new_labels)
        G.add_node(new_id, labels=new_labels)
        G.add_edge(id1, new_id)
        G.add_edge(id2, new_id)

    return G
