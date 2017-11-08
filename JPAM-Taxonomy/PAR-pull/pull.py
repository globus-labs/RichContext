from bs4 import BeautifulSoup, Tag
import json
import logging
import os.path
from requests import get
from urllib.parse import urljoin, urlparse
from urllib.request import urlopen
from typing import List

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s',
    level=logging.INFO
)


DOMAIN = "http://onlinelibrary.wiley.com"
ISSUE_LIST_URL = urljoin(DOMAIN, "/journal/10.1111/(ISSN)1540-6210/issues")
ACTIVE_YEARS = list(range(2000, 2018))
OUTDIR = "pdfs"


def get_issues_by_year(year: str) -> List[Tag]:
    """
    Get a list of <a> tags to issues of the PAR journal by year.
    """
    response = get(ISSUE_LIST_URL, {"activeYear": year})
    soup = BeautifulSoup(response.text, "html.parser")

    issue_spans = soup.find_all("span", {"class": "licensedContent"})
    issue_links = [s.next_sibling.a for s in issue_spans
                   if s.next_sibling.a is not None]
    return issue_links


def get_article_links(issue_url: str) -> List[Tag]:
    """
    Get a list of <a> tags to articles of the PAR journal from the url of an
    issue.
    """
    response = get(issue_url)
    soup = BeautifulSoup(response.text, "html.parser")
    article_entries = soup.find_all("div", {"class": "tocArticle"})
    links = [entry.a for entry in article_entries]
    links = filter(lambda l: "Booknotes" not in l.text, links)
    links = filter(lambda l: "Index for Volume" not in l.text, links)
    return list(links)


def article_url_to_doi(article_url: str) -> str:
    """
    Extract the DOI from a Wiley Online article's url. Online Wiley article
    urls are always of the form:
        http://onlinelibrary.wiley.com/doi/10.1000/033-52.00113/full
    """
    parsed = urlparse(article_url)
    path = parsed.path
    toks = path.split("/")
    toks = toks[2:-1]  # path of form `/doi/10.1000/033-52.00113/full`
    return "/".join(toks)


def download_pdf(article_url, out_fname):
    assert article_url.endswith("full")
    intermediate_url = article_url[:-4] + "pdf"

    r = get(intermediate_url)
    soup = BeautifulSoup(r.text, "html.parser")
    pdf_url = soup.find("iframe")["src"]

    r = urlopen(pdf_url)
    with open(out_fname, "wb") as w:
        w.write(r.read())


def main():
    all_issue_links = list()
    for year in ACTIVE_YEARS:
        all_issue_links += get_issues_by_year(year)
    logging.info("Found %d issues", len(all_issue_links))

    all_article_links = list()
    for link in all_issue_links:
        url = link["href"]
        issue_url = urljoin(DOMAIN, url)
        article_links = get_article_links(issue_url)
        print("Found %d articles" % len(article_links))
        all_article_links += article_links

    logging.info(
        "Found %d articles across %d issues",
        len(all_article_links),
        len(all_issue_links)
    )

    article_urls = [l["href"] for l in all_article_links]
    article_urls = [urljoin(DOMAIN, url) for url in article_urls]

    json.dump(article_urls, open("article_urls.json", "w"))

    for url in article_urls:
        doi = article_url_to_doi(url)
        fname = doi.replace("/", "|") + ".pdf"
        fname = os.path.join(OUTDIR, fname)
        if os.path.exists(fname):
            continue
        try:
            download_pdf(url, fname)
        except:
            pass


if __name__ == "__main__":
    main()
