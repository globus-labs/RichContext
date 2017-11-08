import sys
import os
import requests
import urllib.request as urllib
import json

from bs4 import BeautifulSoup

BASE_FPATH = "DOIS/"
BASE_PDFPATH = "PDFS/"
BASE_METAPATH = "META/"
BASE_URL = "http://onlinelibrary.wiley.com/doi/"

class doiResolver(object):

    
    #META_FIELDS = ["date", "doi", "authors", "volume", "issue"]

    def __init__(self, mode="crash"):
        self.meta_succ = False
        self.pdf_succ = False
        self.issue = None
        self.volume = None
        self.curr_doi = None
        self.successful_pulls = []
        self.failed_pulls_meta = []
        self.failed_pulls_pdf = []
        self.exceptions_meta = []
        self.exceptions_pdf = []
        self.meta_req = None
        self.pdf_req = None
        if mode not in ["crash", "continue"]:
            raise Exception("Please choose a proper mode for using this class")
        self.mode = mode

    def _get_abstract(self, soup):
        abstract = ""
        try:
            abstract = soup.find("section", {"id" : "abstract"}).find("p").contents[0].strip()
        except Exception as e:
            print(e)
            raise Exception("Failed getting abstract on following DOI: " + str(self.curr_doi))
        return abstract

    def _get_abstract_dep(self, soup):
        abstract = None
        try:
            abstract = soup.find("div", {"class" : "article-section__content mainAbstract"}).find(
                "p").contents[0].strip()
        except Exception as e:
            print(e)
            raise Exception("Failed getting abstract on following DOI: " + str(self.curr_doi))
        return abstract

    def _get_date(self, soup):
        try:
            curr_node = soup.find("time", {"id" : "first-published-date"})
            datetime = curr_node["datetime"]
            date = curr_node.contents[0].strip()
        except Exception as e:
            print(e)
            raise Exception("Failed getting date on following DOI: " + str(self.curr_doi))
        return datetime, date

    def _get_authors(self, soup):
        authors_list = []
        try:
            for author_div in soup.find_all("h3", 
                {"class" : "article-header__authors-name"}):
                author_name = author_div.contents[0].strip().strip(",")
                authors_list.append(author_name)
        except Exception as e:
            print(e)
            raise Exception("Failed getting author on following DOI: " + str(self.curr_doi))
        return authors_list

    def _construct_link(self, mode="full"):
        if mode == "full":
            return BASE_URL + self.curr_doi +"/full"
        elif mode == "pdf":
            return BASE_URL + self.curr_doi +"/pdf"
        else:
            raise Exception("The following is not a valid mode: " + mode)

    def _load_meta(self):
        url = BASE_URL + self.curr_doi + "/full"
        r = requests.request("GET", url)
        if r.status_code != 200:
            raise Exception("Expected status code 200, received status code " + str(r.status_code))
        return r

    def _load_pdf(self):
        url = BASE_URL + self.curr_doi + "/pdf"
        temp_r = requests.request("GET", url)
        if temp_r.status_code != 200:
            raise Exception("Couldn't find pdf frame, received code: " + str(temp_r.status_code))
        temp_soup = BeautifulSoup(temp_r.text, "html.parser")
        try:
            curr_node = temp_soup.find("iframe")
            new_url = str(curr_node.get("src"))
            response = urllib.urlopen(new_url)
            curr_bytes = response.read()
            return curr_bytes
        except Exception as e:
            print(e)
            raise(e)
        return

    def _load_pdf_v2(self):
        url = BASE_URL + self.curr_doi + "/pdf"
        temp_r = requests.request("GET", url)
        if temp_r.status_code != 200:
            raise Exception("Couldn't find pdf frame, received code: " + str(temp_r.status_code))
        temp_soup = BeautifulSoup(temp_r.text, "html.parser")
        try:
            curr_node = temp_soup.find("src")
        except:
            pass
        return

    def set_issue(self, issue):
        if issue in range(1,5):
            self.issue = issue
        else:
            raise Exception(str(issue) + " is not a valid issue number")
        return

    def set_volume(self, volume):
        if volume in range(1, 37):
            self.volume = volume
        else:
            raise Exception(str(volume) + " is not a valid volume number")
        return

    def load_doi(self, doi):
        self.curr_doi = doi
        self.meta_succ = False
        self.pdf_succ = False
        failed = False
        try:
            self.meta_req = self._load_meta()
        except Exception as e:
            self.exceptions_meta.append(str(e))
            self.failed_pulls_meta.append(self.curr_doi)
            failed = True
        try:
            self.pdf_req = self._load_pdf()
        except Exception as e:
            self.exceptions_pdf.append(str(e))
            self.failed_pulls_pdf.append(self.curr_doi)
            failed = True
        if failed is False:
            self.pdf_succ = True
        elif self.mode == "crash":
            failed_field = ""
            failed_doi = ""
            if len(self.exceptions_pdf) > 0:
                failed_field = "pdf"
            elif len(self.exceptions_meta) > 0:
                failed_field = "meta"
            raise Exception("Failed getting " + failed_field +" for " + self.curr_doi)
        else:
            return self.curr_doi
        return True

    def get_pdf(self):
        if self.pdf_req is None:
            raise Exception("You need to load a doi before getting a pdf")
        curr_req = self.pdf_req
        return curr_req

        

    def get_metadata_dump(self, doi=None):
        if doi != None:
            self.load_doi(doi)
        elif self.curr_doi == None:
            raise Exception("There is currently no loaded DOI")
        meta_ball = {}
        req = self.meta_req
        meta_soup = BeautifulSoup(req.content, "html.parser")
        #print(meta_soup)
        fail_count = 0
        try:
            meta_ball["abstract"] = self._get_abstract(meta_soup)
        except Exception as e:
            self.exceptions_meta.append(e)
            fail_count += 1
        try:
            meta_ball["datetime"], meta_ball["date"] = self._get_date(meta_soup)
        except Exception as e:
            self.exceptions_meta.append(e)
            fail_count += 1
        try:
            meta_ball["authors"] = self._get_authors(meta_soup)
        except Exception as e:
            self.exceptions_meta.append(e)
            fail_count += 1
        try:
            meta_ball["doi"] = self.curr_doi
        except Exception as e:
            self.exceptions_meta.append(e)
            fail_count += 1
        try:
            meta_ball["link-to-full"] = self._construct_link()
        except Exception as e:
            self.exceptions_meta.append(e)
            fail_count += 1
        try:
            meta_ball["volume"] = self.volume
            meta_ball["issue"] = self.issue
        except Exception as e:
            self.exceptions_meta.append(e)
            fail_count += 1
        if fail_count > 0:
            self.failed_pulls_meta.append(self.curr_doi)
        elif not self.meta_succ:
            self.meta_succ = True
        if self.meta_succ and self.pdf_succ:
            self.successful_pulls.append(self.curr_doi)
        meta_ball["meta_succ"] = self.meta_succ
        meta_ball["pdf_succ"] = self.pdf_succ
        return meta_ball

def save_pdf(pdf_contents, doi):
    doi = doi.replace("/", ".")
    title = doi + ".pdf"
    fp = open(BASE_PDFPATH + title, "wb")
    fp.write(pdf_contents)
    fp.close()
    return title

def main():
    resolver = doiResolver(mode="continue")
    successful_dois = []
    failed_pdfs = []
    failed_metas = []
    for filepath in os.listdir(BASE_FPATH):
        if filepath[0] == ".":
            continue
        parts = filepath.replace(".json", "").split("_")
        print(parts)
        volume = int(parts[2])
        issue = int(parts[4])
        resolver.set_volume(volume)
        resolver.set_issue(issue)
        meta_list = []
        fp = open(BASE_FPATH + filepath, "r")
        dois = json.load(fp)
        fp.close()
        for doi in dois:
            resolver.load_doi(doi)
            try:
                curr_pdf_content = resolver.get_pdf()
            except Exception as e:
                print(e)
            curr_meta = resolver.get_metadata_dump()
            if resolver.pdf_succ is True:
                save_path = save_pdf(curr_pdf_content, doi)
                curr_meta["pdf-name"] = save_path
            meta_list.append(curr_meta)
        curr_fp = open(BASE_METAPATH + "metadata_jpam_vol_{}_issue_{}.json".format(str(volume), str(issue)), "w")
        json.dump(meta_list, curr_fp)
        curr_fp.close()
    successful_dois = resolver.successful_pulls
    failed_metas = resolver.failed_pulls_meta
    failed_pdfs = resolver.failed_pulls_pdf
    succ = open("successfully_pulled_dois.json", "w")
    json.dump(successful_dois, succ)
    succ.close()
    fail_1 = open("failed_meta.json", "w")
    json.dump(failed_metas, fail_1)
    fail_1.close()
    fail_2 = open("failed_pdf.json", "w")
    json.dump(failed_pdfs, fail_2)
    fail_2.close()
    return

if __name__ == "__main__":
    main()




















