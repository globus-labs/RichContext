import sys
import os
import requests
import uuid
import json

import urllib.request

from bs4 import BeautifulSoup

POTENTIAL_RESOLVE_1 = "http://onlinelibrary.wiley.com/doi/10.1002/pam.v{}:{}/issuetoc"
POTENTIAL_RESOLVE_12 = "http://onlinelibrary.wiley.com/doi/10.1002/pam.v{}.{}/issuetoc"
POTENTIAL_RESOVLE_2 = "http://onlinelibrary.wiley.com/doi/10.1002/pam.{}.{}.issue-{}/issuetoc"
POTENTIAL_RESOLVE_3 = "http://onlinelibrary.wiley.com/doi/10.1002/{}1520-6688({}{}){}:{}%3C%3E1.0.CO;2-{}/issuetoc"
nums = ["21", "22", "23", "24"]
letters = ["P", "X", "T", "L", "H", "D", "0", "8", "4", "3"]
filler_text = ["(SICI)", ""]
'''
POTENTIAL_RESOLVE_4 = "http://onlinelibrary.wiley.com/doi/10.1002/(SICI)1520-6688(199622){}:{}%3C%3E1.0.CO;2-T/issuetoc"
POTENTIAL_RESOLVE_5 = "http://onlinelibrary.wiley.com/doi/10.1002/(SICI)1520-6688(199621){}:{}%3C%3E1.0.CO;2-L/issuetoc"
POTENTIAL_RESOLVE_6 = "http://onlinelibrary.wiley.com/doi/10.1002/(SICI)1520-6688(199621){}:{}%3C%3E1.0.CO;2-X/issuetoc"
further_resolves = {3 : POTENTIAL_RESOLVE_3, 4 : POTENTIAL_RESOLVE_4, 5 : POTENTIAL_RESOLVE_5,
    6 : POTENTIAL_RESOLVE_6}
'''

class jpamVolumeExtractor(object):
    
    def __init__(self, volume, issue, year=None):
        self.volume = volume
        self.issue = issue
        if year == None:
            self.year = self._resolve_year(volume, issue)
        self.req = self._resolve_volume(volume, issue, year)
        self.dois = self._load_dois()

    def __iter__(self):
        for doi in self.dois:
            yield doi

    def get_dois(self):
        if len(self.dois) == 0:
            raise Exception("Make sure to load DOIS!")
        else:
            return self.dois

    def _load_dois(self):
        r = self.req
        soup = BeautifulSoup(r.content, "html.parser")
        dois = []
        for doi_tag in soup.find_all("input", {"name" : "doi"}):
            dois.append(doi_tag["value"])
        return dois


    def _resolve_year(self, volume, issue):
        if volume <= 7:
            return None
        else:
            if issue == 1:
                return volume + 1980
            else:
                return volume + 1981

    def _resolve_volume(self, volume, issue, year=None):
        freedom = False
        if year is None:
            year = self._resolve_year(volume, issue)
        req = None
        try:
            temp_url = POTENTIAL_RESOLVE_1
            temp_url = temp_url.format(str(volume), str(issue))
            r = requests.request("GET", temp_url)
            if r.status_code != 200:
                raise Exception("Did not receive a 200 response! Instead received %s"%str(r.status_code))
            req = r
            freedom = True
        except Exception as e:
            print(e)
        if req == None:
            try:
                temp_url = POTENTIAL_RESOLVE_12
                temp_url = temp_url.format(str(volume), str(issue))
                r = requests.request("GET", temp_url)
                if r.status_code != 200:
                    raise Exception("Did not receive a 200 response! Instead received %s"%str(r.status_code))
                req = r
                freedom = True
            except Exception as e:
                print(e)
        if req == None and year != None:
            try:
                temp_url = POTENTIAL_RESOVLE_2
                temp_url = temp_url.format(str(year), str(volume), str(issue))
                r = requests.request("GET", temp_url)
                if r.status_code != 200:
                    raise Exception("Did not receive a 200 response! Instead received %s"%str(r.status_code))
                req = r
                freedom = True


            except Exception as e:
                print(e)
        double_break = False
        for resolv_num in nums:
            if freedom == True:
                break
            for resolve_let in letters:
                for filler in filler_text:
                    try:
                        temp_url = POTENTIAL_RESOLVE_3
                        temp_url = temp_url.format(str(filler), str(year), str(resolv_num), str(volume), str(issue), str(resolve_let))
                        r = requests.request("GET", temp_url)
                        if r.status_code != 200:
                            raise Exception("Did not receive a 200 response for" + temp_url +"! Instead received %s"%str(r.status_code))
                        req = r
                        double_break = True
                        break
                    except Exception as e:
                        print(e)
            if double_break:
                break
        if req == None:
            raise Exception("Could not resolve the journal page for volume " + str(volume) + " issue " + str(issue))
        else:
            return req


def main():
    for volume in range(int(sys.argv[1]),37):
        for issue in range(1,5):
            print(str(volume) + " " + str(issue))
            curr_vol = jpamVolumeExtractor(volume, issue)
            curr_dois = curr_vol.get_dois()
            fpath = "DOIS/jpam_vol_{}_issue_{}.json".format(str(volume), str(issue))
            fp = open(fpath, "w")
            json.dump(curr_dois, fp)
            fp.close()

if __name__ == "__main__":
    main()

