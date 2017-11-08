import json
import logging
import random
from collections import deque
from functools import lru_cache
from typing import List, Tuple

import networkx as nx
import wikipedia
from bs4 import BeautifulSoup
from gensim import matutils, utils
from gensim.models import LdaModel
from nltk.stem import WordNetLemmatizer
from requests import get

from heap import PriorityQueue


mw_base = "https://en.wikipedia.org/w/api.php"
headers = {'user-agent': 'CIWikiLabeler/0.0.1'}
params = {
    'action': 'query',
    'format': 'json',
    'list': 'categorymembers',
    'cmtitles': 'Category:Childhood|Category:Child Labour',
    'cmtype': 'subcat'
}

BAD_PAGES = [
    "International Standard Book Number",
    "Digital object identifier",
    "Category:Main topic classifications"
]

BAD_FILTERS = [
    lambda page: " by " in page,
    lambda page: "Subfields" in page,
    lambda page: page in BAD_PAGES
]


def lemmatize(word: str) -> str:
    """
    Apply WordNetLemmatizer to `word` and attempt both noun and verb
    lemmatization.
    :param word:
    :return: lemmatized word
    """
    lem = lemmatize.lemmer.lemmatize(word)
    if lem == word:
        lem = lemmatize.lemmer.lemmatize(word, 'v')
    return lem


lemmatize.lemmer = WordNetLemmatizer()


def BAD(page: str) -> bool:
    """
    Return true if the page is bad as defined by the BAD_FILTERS and BAD_PAGES
    """
    return any(f(page) for f in BAD_FILTERS)


def is_category(page: str) -> bool:
    return page.startswith("Category:")


@lru_cache(4096)
def page_text(page: str, full_text=False) -> str:
    """
    Get the full text of a wikipedia page.  If `full_text` is set to `True`
    then the full text of the page is retrieved.  Otherwise only the summary.
    :param page: title of the desired page
    :param full_text: functionality described above
    :return: text or summary of page
    """
    try:
        p = wikipedia.page(page)
    except:
        return ""
    if full_text or len(p.summary) == 0:
        html = wikipedia.page(page).html()
        soup = BeautifulSoup(html, "lxml")
        return soup.text
    else:
        return p.summary


@lru_cache(2048)
def model_page(page: str, model: LdaModel, sample_size=20) -> List[Tuple[int, float]]:
    """
    Compute the sparse vector (list of items) for the page in the LdaModel.
    If the page is a category, models all the member pages of the category.
    :param page: title of wikipedia page
    :return: sparse vector of topics and their proportions
    """
    text = ""
    if is_category(page):
        members = member_pages(page)
        sample_size = min(len(members), sample_size)
        sample = random.sample(members, sample_size)
        text = "".join(page_text(p) for p in sample)
    else:
        text = page_text(page)

    tokens = utils.tokenize(text)
    lems = [lemmatize(t) for t in tokens]
    bow = model.id2word.doc2bow(lems)
    inferred = model.get_document_topics(bow, minimum_probability=0.0)
    return inferred


def _heuristic(page1: str, page2: str, model: LdaModel) -> float:
    """
    Heuristic between two pages of wikipedia is the cosine similarity
    between their topic vectors.
    """
    vec1 = model_page(page1, model)
    vec2 = model_page(page2, model)
    distance = -1 * matutils.cossim(vec1, vec2)
    logging.info("Distance between '%s' and '%s' : %f", page1, page2, distance)
    return distance


def A_star_sca(page1: str, page2: str, model: LdaModel, max_iter=100):
    """
    Search for shortest (lowest) common ancestor between two pages in wikipedia
    using the A* algorithm. THe heuristic for A* is defined by the `_heuristic`
    function.
    :param page1: title of wikipedia page
    :param page2: title of wikipedia page
    :param model: LdaModel from gensim.  Topics in this model guide the A* algo
    :param max_iter: maximum number of iterations to perform before terminating
    :return: title of SCA.
    """
    pq1 = PriorityQueue()
    pq1.enq(page1, _heuristic(page1, page2, model))
    pq2 = PriorityQueue()
    pq2.enq(page2, _heuristic(page2, page1, model))

    visited1 = set()
    visited2 = set()

    iter_no = 0
    while not pq1.empty() or not pq2.empty() and iter_no < max_iter:
        iter_no += 1

        s1, p1 = pq1.deq() if not pq1.empty() else (1, "")
        s2, p2 = pq2.deq() if not pq2.empty() else (1, "")

        logging.info("Advancing 1 to  %s with distance %f", p1, s1)
        logging.info("Advancing 2 to  %s with distance %f", p2, s2)

        if p1 == p2:
            return p1

        if p1 in visited2:
            return p1

        if p2 in visited1:
            return p2

        visited1.add(p1)

        visited2.add(p2)

        for cat in categories(p1):
            pq1.enq(cat, _heuristic(cat, page2, model))

        for cat in categories(p2):
            pq2.enq(cat, _heuristic(cat, page1, model))


def central(pages: List[str], max_depth: int=2) -> List[str]:
    """
    Compute the central node(s) in the graph defined by the links between
    wikipedia pages. The `max_depth` parameter limits the number of steps out
    from the `pages` to explore.  This should be a *small* number due to the
    exponential blow up of the graph.
    :param pages: list of titles of wikipedia pages for which to find center
    :param max_depth:
    :return: List[str] central pages of the graph
    """
    if len(pages) == 0:
        return []

    G = nx.Graph()
    G.add_nodes_from(pages)
    front = pages
    for i in range(max_depth):
        new_front = []
        for page in front:
            for link in links(page):
                G.add_edge(page, link)
                new_front.append(link)
        front = new_front

    if not nx.is_connected(G):
        return []

    return nx.center(G)


def highcatrank(pages, max_depth=1, n=2):
    if len(pages) == 0:
        return []

    G = nx.Graph()
    G.add_nodes_from(pages)
    front = pages
    for i in range(max_depth):
        new_front = []
        for page in front:
            for cat in categories(page):
                G.add_edge(page, cat)
                new_front.append(cat)
        front = new_front

    print("Calculating rank on %d nodes" % G.number_of_nodes())
    ranks = nx.pagerank(G)
    ranks = sorted(ranks.keys(), key=lambda k: ranks[k], reverse=True)
    return ranks[:n]


def highpagerank(pages, max_depth=1, n=2):
    if len(pages) == 0:
        return []

    G = nx.Graph()
    G.add_nodes_from(pages)
    front = pages
    for i in range(max_depth):
        new_front = []
        print(len(front))
        for page in front:
            for link in links(page):
                G.add_edge(page, link)
                new_front.append(link)
        front = new_front

    print("Calculating rank on %d nodes" % G.number_of_nodes())
    ranks = nx.pagerank(G)
    ranks = sorted(ranks.keys(), key=lambda k: ranks[k], reverse=True)
    return ranks[:n]


@lru_cache(2048)
def links(page):
    try:
        page = wikipedia.page(page)
        return page.links
    except:
        return []


def list_sca(titles1, titles2, depth=3, pl=1000):
    s_ancestors = set()
    s_dist = 2 ** 32

    # Pages accesible from each set
    closed1 = set()
    closed2 = set()

    dist_from1 = {t: 0 for t in titles1}
    dist_from2 = {t: 0 for t in titles2}

    # Front of reachable area of each set
    front1 = deque(titles1)
    front2 = deque(titles2)

    limiter = depth

    while 0 < len(front1) + len(front2) < pl and limiter > 0:
        print(
            "Limiter %d; Front1: %d; Front2: %d" %
            (limiter, len(front1), len(front2))
        )
        limiter -= 1
        next_front1 = deque()
        next_front2 = deque()

        for title in front1:
            add_supers(title, dist_from1, next_front1)
            if title in closed2:
                length = dist_from1[title] + dist_from2[title]
                if length == s_dist and title not in s_ancestors:
                    s_ancestors.add(title)
                    print(s_ancestors, s_dist)
                elif length < s_dist:
                    s_ancestors = {title}
                    s_dist = length
                    limiter = length // 2
                    print(s_ancestors, s_dist)
            closed1.add(title)

        for title in front2:
            add_supers(title, dist_from2, next_front2)
            if title in closed1:
                length = dist_from1[title] + dist_from2[title]
                if length == s_dist:
                    s_ancestors.add(title)
                    print(s_ancestors, s_dist)
                elif length < s_dist:
                    s_ancestors = {title}
                    s_dist = length
                    limiter = length // 2
                    print(s_ancestors, s_dist)
            closed2.add(title)

        front1 = next_front1
        front2 = next_front2

    return s_ancestors


def add_supers(title, distances, next_front):
    for c in categories(title):
        if c not in distances:
            distances[c] = distances[title] + 1
        next_front.append(c)


def merge(set1, set2):
    set1 = set(set1)
    set2 = set(set2)

    if len(set1) == 0 and len(set2) != 0:
        set1 = set2
    if len(set2) == 0 and len(set1) != 0:
        set2 = set1
    if len(set1) == 0 and len(set2) == 0:
        return {}

    intersection = {}
    iter_no = 0
    while len(intersection) == 0 and iter_no < 2:
        set1 |= {c for t in set1 for c in categories(t)}
        set2 |= {c for t in set2 for c in categories(t)}
        intersection = set1.intersection(set2)
        iter_no += 1

    return intersection


def member_pages(category):
    assert is_category(category)
    params = {
        'action': 'query',
        'format': 'json',
        'list': 'categorymembers',
        'cmtitle': category
    }
    members = []
    cont = True
    while cont:
        cont = False
        r = get(mw_base, params=params, headers=headers)
        response = json.loads(r.text)
        members += [p["title"] for p in response["query"]["categorymembers"]]
        if "continue" in response:
            cont = True
            params["cmcontinue"] = response["continue"]["cmcontinue"]

    return [p for p in members if not is_category(p)]


def subcategories(title):
    """
    Get a list of titles of subcategories for the given page title. Title must
    be a category title.
    :param title: title of the category, e.g.: "Category:Humanities"
    :return: list(str)
    """
    assert is_category(title)
    params = {
        'action': 'query',
        'format': 'json',
        'list': 'categorymembers',
        'cmtitle': title,
        'cmtype': 'subcat'
    }
    r = get(mw_base, params=params, headers=headers)
    response = json.loads(r.text)
    categorymembers = response["query"]["categorymembers"]
    return [cm["title"] for cm in categorymembers]


@lru_cache(2048)
def categories(title):
    params = {
        'action': 'query',
        'format': 'json',
        'prop': 'categories',
        'clshow': '!hidden',
        'titles': title
    }
    r = get(mw_base, params=params, headers=headers)
    response = json.loads(r.text)
    try:
        response = response["query"]["pages"]
        pages = {d["title"]: d for pid, d in response.items()}
        page = pages[title]
        categories = page["categories"]
        return [c["title"] for c in categories]
    except Exception as e:
        print(e)
        print(response)
        return []


def page_labels(terms, n=3):
    params = {
        'action': 'query',
        'format': 'json',
        'prop': 'categories',
        'clcategories': 'Category:Social Sciences',
        'list': 'search',
        'srsearch': 'schools educational parents voucher children'
    }
    q = " ".join(terms)
    params['srsearch'] = q
    r = get(mw_base, params=params, headers=headers)
    response = json.loads(r.text)
    results = response["query"]["search"]
    # results = sorted(results, key=lambda d: d["size"], reverse=True)
    top_results = results[0:n]
    return [top['title'] for top in top_results]


if __name__ == "__main__":
    r = get(mw_base, params=params, headers=headers)
    response = json.loads(r.text)
    print(json.dumps(response, indent=4))
    response = response["query"]["pages"]
    # pages = {d["title"]: d for pid, d in response.items()}
    # print(json.dumps(pages, indent=4))
    # results = response["query"]["search"]
    # results = sorted(results, key=lambda d: d["size"], reverse=True)
    # print(json.dumps(results[0:3], indent=4))
