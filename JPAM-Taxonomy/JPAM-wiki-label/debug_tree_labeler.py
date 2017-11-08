import sys
import os
import json
import itertools
import wikipedia as wiki
import pickle as pk
import re
import enchant as en





from collections import defaultdict

TEST_DUMP = "d3_intermediate_skewed.pk"
TREE_FILE = "d3_intermediate_skewed_tree.txt"
UNLABELED_FILE = "d3_intermediate_skewed_unlabeled.pk"
FORMAT = "piped"

'''

A class for creating a tree where each node has, associated with it, several
terms, wikipedia titles and pages associated with the terms, and labels based
on the pages that occur at and in children of the node.

'''
fp = open('countries.txt')
COUNTRIES = [country.lower() for country in fp.read().split("\n")]
fp.close()

ap = open("acro_to_phrase.json", "r")
ACRO_LIST = json.load(ap)
ap.close()

print(ACRO_LIST)

SPELL_CHECK = en.Dict("en_US")


class WikiNode(object):

    '''
    Construct a node from a given array of terms.
    '''
    def __init__(self, terms):
        self.pages = {}
        self.terms = list(terms.copy())
        self.children = []
        self.labels_links = []
        self.labels_categories = []


    def _get_phrase(self, terms):
        search_phrase = ""
        for term in terms:
            if term.upper() in ACRO_LIST.keys():
                search_phrase += ACRO_LIST[term.upper()]
                search_phrase += " "
            elif SPELL_CHECK.check(term):
                search_phrase += term
                search_phrase += " "
            else:
                continue
        return search_phrase


    def add_child(self, child_node):
        self.children.append(child_node)

    def set_pages(self, page_list):
        self.pages = page_list.copy()

    '''
    Returns all wikipedia pages that occur at this node or at a child
    of this node.
    '''
    def total_pages(self):
        pages = self.pages.copy()
        for child in self.children:
            child_pages = child.total_pages()
            pages.update(child_pages)
        return pages


    '''
    Returns a dictionary of wikipedia titles mapping to wikipedia pages based
    on all possible combinations of a given set of terms.
    '''
    def _wiki_search(self, terms):
        pages = {}
        for search_phrase in itertools.combinations(terms, len(terms)):
            try:
                phrase = self._get_phrase(search_phrase)
                search_results = []
                timeout = len(search_phrase) - 1
                while search_results == [] and timeout > 0:
                    print("PHRASE: " +  phrase)
                    search_results = wiki.search(phrase)
                    print(search_results)
                    if search_results == []:
                        search_phrase = search_phrase[:len(search_phrase) - 1]
                        phrase = self._get_phrase(search_phrase)
                        timeout -= 1
            except Exception as e:
                print(e)
                continue
            for page_name in search_results[:5]:
                print(page_name)
                try:
                    curr_page = self._get_page(page_name)
                except Exception as e:
                    print(e)
                    continue
                pages[page_name] = curr_page
        return pages

    '''
    Given the name of a wikipedia page, will return the wikipedia page associated with the title. Will
    raise an exception if it cannot find a wikipedia page with a close enough title.
    '''
    def _get_page(self, page_name):
        page = -1
        try:
            page = wiki.page(page_name)
        except wiki.exceptions.DisambiguationError as e:
            try:
                main_option = e.options[0]
                page = wiki.page(main_option)
            except Exception as e:
                print(e)
                pass
        except Exception as e:
            print("_get_page2")
            print(e)
            pass
        if page == -1:
            raise Exception("Did not properly load %s" % page_name)
        return page


    '''
    Given
    '''
    def _label_links(self, pages):
        occurrences = defaultdict(int)
        for page in pages.keys():
            try:
                links = pages[page].links
                for link in links:
                    occurrences[link.lower()] += 1
            except Exception as e:
                print(e)
                print("LINKS: failed on page: " + page)
        key_occ = [(k, v) for (k, v) in occurrences.items()]
        key_occ = sorted(key_occ, key=lambda x: x[1], reverse=True)
        return key_occ
       
    def _label_categories(self, pages):
        occurrences = defaultdict(int)
        for page in pages.keys():
            try:
                categories = pages[page].categories
                for category in categories:
                    occurrences[category.lower()] += 1
            except Exception as e:
                print(e)
                print("CATEGORIES: failed on page: " + page)
        key_occ = [(k, v) for (k, v) in occurrences.items()]
        key_occ = sorted(key_occ, key=lambda x: x[1], reverse=True)
        return key_occ

    def label(self):
        self.pages = self._wiki_search(self.terms)
        if len(self.children) == 0:
            self.labels_links = self._label_links(self.pages)
            self.labels_categories = self._label_categories(self.pages)
            return
        for child in self.children:
            child.label()
        all_pages = self.total_pages()
        self.labels_links = self._label_links(all_pages)
        self.labels_categories = self._label_categories(all_pages)
        return all_pages

    def phrase_to_labels(self):
        curr_dict = {}
        for child in self.children:
            curr_dict.update(child.phrase_to_labels())
        return curr_dict

    def prettify_tree(self, fields, num_to_keep):
        return self._prettify(0, fields, num_to_keep)

    def _prettify(self, depth, fields, num_to_keep):
        curr_text = ""
        #print(self.children)
        curr_tab = ""
        for i in range(depth + 1):
            curr_tab += "\t"
        if "terms" in fields:
            curr_text += curr_tab
            curr_text += "TERMS: "
            curr_text += str(self.terms)
            curr_text += "\n"
        if "labels_links" in fields:
            curr_text += curr_tab
            curr_text += "LINK LABELS: "
            temp_labels = self._prune(self.labels_links, num_to_keep)
            curr_text += str(temp_labels)
            curr_text += "\n"
        if "labels_categories" in fields:
            curr_text += curr_tab
            curr_text += "CATEGORY LABELS: "
            temp_labels = self._prune(self.labels_categories, num_to_keep)
            curr_text += str(temp_labels)
            curr_text += "\n"
        if "labels_pages" in fields:
            curr_text += curr_tab
            curr_text += "WIKI PAGES: "
            curr_text += str(list(self.pages.keys()))
            curr_text += "\n"
        for child in self.children:
            curr_text += "\n"
            curr_text += child._prettify(depth + 1, fields, num_to_keep)
            
        return curr_text

    def _prune(self, pairs, number):
        ret = []
        bad_words = set(["article", "articles", "wikipedia", "book", "number", "identifier", "pages", "webarchive", "wayback", "cs1",
            "multiple names", "list", "deprecated", "citations", "url", "link", "wikidata", "authority", "featured", "lists", "dmy", "jstor",
            "pubmed"])
        bad_words = bad_words.union(COUNTRIES)
        for k, v in pairs:
            if set(k.split()).intersection(bad_words) == set():
                ret.append(k)
            if len(ret) > number:
                return ret
        return ret


        

def _lead_space(line):
    return len(line) - len(line.lstrip())

def _make_tree(tree_text, start_index, depth):
    line = tree_text[start_index]
    #print(line)
    if FORMAT == "piped":
        terms = []
        line_parts = line.split()
        for part in line_parts:
            terms.append(part.split("|")[0])
    else: 
        terms = line.split()
    currNode = WikiNode(terms=terms)
    #if depth == 2: 
        #print(currNode.children)
    if len(tree_text[start_index:]) == 1 or _lead_space(tree_text[start_index + 1]) <= _lead_space(line):
        '''
        print("in here")
        print(depth)
        print(currNode.terms)
        print(currNode.children)
        '''
        return start_index + 1, currNode

    else:
        i = start_index + 1
        while i < len(tree_text) and _lead_space(line) < _lead_space(tree_text[i]):
            #print(depth)
            i, child = _make_tree(tree_text, i, depth + 1)
            currNode.children.append(child)

        return i, currNode


def make_tree(tree_text):
    tree_text = re.sub('\[.*?\]', '', tree_text)
    lines = tree_text.split("\n")
    header = lines[:9]
    lines = lines[9:]
    new_lines = []
    for line in lines:
        if line.strip() == "":
            pass
        else:
            #print(_lead_space(line))
            new_lines.append(line)
    #sys.exit()        
    i, root = _make_tree(new_lines, 0, 0)
    return root
    



if __name__ == "__main__":
    if os.path.exists(TEST_DUMP):
        print("it exists!")
        pp = open(TEST_DUMP, "rb")
        node = pk.load(pp)
        very_neat = node.prettify_tree(["terms", "labels_links", "labels_categories", "labels_pages"], 5)
        dp = open(TREE_FILE, "w")
        dp.write(very_neat)
        dp.close()
        sys.exit()
    tp = open(sys.argv[1], "r")
    tree_text = tp.read()
    tp.close()
    #print(tree_text)
    working_wiki_tree = make_tree(tree_text)
    #print(working_wiki_tree.prettify_tree())
    pp = open(UNLABELED_FILE, "wb")
    pk.dump(working_wiki_tree, pp)
    pp.close()
    #print(working_wiki_tree.children)
    
    child_node = working_wiki_tree
    print("got child!")
    child_node.label()
    pp = open(TEST_DUMP, "wb")
    pk.dump(child_node, pp)
    pp.close()
    very_neat = child_node.prettify_tree(["terms", "labels_links", "labels_categories", "labels_pages"], 5)
    dp = open(TREE_FILE, "w")
    dp.write(very_neat)
    dp.close()
    sys.exit()

















