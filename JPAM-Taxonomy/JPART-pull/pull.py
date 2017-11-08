import json
import logging
import os.path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup, Tag
from requests import get

from typing import List


logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s',
    level=logging.INFO
)


HEADERS = requests.utils.default_headers()
HEADERS["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6)" + \
                        "AppleWebKit/603.3.8 (KHTML, like Gecko)" + \
                        "Version/10.1.2 Safari/603.3.8"
DOMAIN = "https://academic.oup.com"
ISSUE_LIST_URL = DOMAIN + "/jpart/issue"
VOLUMES = list(range(1, 28))
OUTDIR = "pdfs"


def get_issues_by_volume(volume: str) -> List[Tag]:
    url = ISSUE_LIST_URL + "/%s/1" % volume
    logging.info("Examining %s", url)
    response = get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    options = soup.find_all("option", {"class": "issue-entry"})
    urls = [urljoin(DOMAIN, o["value"]) for o in options]
    return urls


def get_article_urls(issue_url: str) -> List[Tag]:
    response = get(issue_url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    titles = soup.find_all("h5", {"class": "item-title"})
    links = [title.a for title in titles]
    urls = [urljoin(DOMAIN, link["href"]) for link in links]
    return urls


def article_soup_to_doi(article_soup: BeautifulSoup):
    citation_div = article_soup.find("div", {"class": "ww-citation-primary"})
    doi_link = citation_div.a
    doi_url = doi_link["href"]
    path = urlparse(doi_url).path
    doi = path[1:]  # /10.1093/oxfordjournals.jpart.a037072
    return doi


def download_pdf(article_soup: BeautifulSoup, out_fname: str):
    """
    :param article_soup:
    :param foo:
    """
    link = article_soup.find("a", {"class": "article-pdfLink"})
    url = urljoin(DOMAIN, link["href"])
    r = get(url, headers=HEADERS)
    with open(out_fname, "wb") as w:
        w.write(r.content)


def main():
    # logging.info("Scanning for issues")

    # all_issue_urls = [
    #     url
    #     for vol in VOLUMES
    #     for url in get_issues_by_volume(str(vol))
    # ]

    # logging.info("Found %d issues", len(all_issue_urls))
    # logging.info("Scanning for articles")

    # all_article_urls = [
    #     url
    #     for issue_url in all_issue_urls
    #     for url in get_article_urls(issue_url)
    # ]

    # json.dump(all_article_urls, open("jpart_urls.json", "w"))

    all_article_urls = json.load(open("./jpart_urls.json"))

    logging.info("Found %d articles", len(all_article_urls))

    for i, url in enumerate(all_article_urls):
        print(i, url)
        if i < 1103:
            continue

        r = get(url, headers=HEADERS)
        soup = BeautifulSoup(r.text, "html.parser")
        doi = article_soup_to_doi(soup)
        fname = doi.replace("/", "|") + ".pdf"
        fname = os.path.join(OUTDIR, fname)

        if os.path.exists(fname):
            continue

        try:
            download_pdf(soup, fname)
        except TypeError as e:
            logging.error("Failed to download pdf")


if __name__ == "__main__":
    main()
