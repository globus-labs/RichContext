import sys
import os
import json
import itertools
import wikipedia as wiki
import pickle as pk
import re


class WikiNode(object):

    def __init__(self, terms):
        self.data = {}
        self.pages = set()
        self.terms = terms
        self.children = []
        self.labels = []

    def add_child(self, child_node):
        self.children.append(child_node)

    def set_data(self, data_field, data):
        self.data[data_field] = data

    def set_pages(self, page_list):
        self.pages = page_list

    def total_pages(self):
        pages = self.pages
        for child in self.children:
            pages.union(child.total_pages)
        return pages

    def _wiki_search(self, terms):
        pages = set()
        for search_phrase in itertools.combinations(terms, 4):
            try:
                search_results = wiki.search(search_phrase)
                print(search_results)
                for page_name in search_results:
                    try:
                        pages.union({self._get_page(page_name)})
                    except Exception as e:
                        print("_wiki_search1")
                        print(e)
                        raise(e)
                        continue
            except Exception as e:
                print("_wiki_search2")
                print(e)
        return pages

    def _get_page(self, page_name):
        page = -1
        try:
            page = wiki.page(page_name)
        except wiki.exceptions.DisambiguationError as e:
            try:
                main_option = e.options[0]
                page = wiki.page(main_option)
            except Exception as e:
                pass
            except Exception as e:
                print("_get_page1")
                print(e)
                pass
        except Exception as e:
            print("_get_page2")
            print(e)
            pass
        return page

    def _label_links(self, pages):
        occurrences = defaultdict(int)
        for page in pages:
            links = pages.links
            for link in links:
                occurrences[link.lower()] += 1
        key_occ = [(k, v) for (k, v) in occurrences.items()]
        key_occ = sorted(key_occ, key=lambda x: x[1], reverse=True)
        return key_occ
       
    def _label_categories(self, pages):
        occurrences = defaultdict(int)
        for page in pages:
            categories = pages.categories
            for link in links:
                occurrences[link.lower()] += 1
        key_occ = [(k, v) for (k, v) in occurrences.items()]
        key_occ = sorted(key_occ, key=lambda x: x[1], reverse=True)
        return key_occ

    def label(self):
        self.pages = self._wiki_search(self.terms)
        if len(self.children) == 0:
            self.labels = self._label_links(self.pages)
            return
        for child in self.children:
            child.label()
        all_pages = self.total_pages()
        self.labels = self._label_categories(all_pages)
        return all_pages

    def phrase_to_labels(self):
        curr_dict = {}
        for child in self.children:
            curr_dict.update(child.phrase_to_labels)
        return curr_dict

    def prettify_tree(self, fields=["terms"]):
        return self._prettify(0, fields=fields)

    def _prettify(self, depth, fields=["terms"]):
        curr_text = ""
        print(self.children)
        for i in range(depth + 1):
            curr_text += "\t"
        if "terms" in fields:
            curr_text += (" ").join(self.terms)
        if "labels" in fields:
            curr_text += (" ").join(self.labels)
        for child in self.children:
            curr_text += "\n"
            curr_text += child._prettify(depth + 1, fields=fields)
        return curr_text

        

def _lead_space(line):
    return len(line) - len(line.lstrip())

def _make_tree(tree_text, start_index, depth):
    line = tree_text[start_index]
    #print(line)
    terms = line.split()
    currNode = WikiNode(terms=terms)
    if depth == 2: 
        print(currNode.children)
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
            print(depth)
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
    tp = open(sys.argv[1], "r")
    tree_text = tp.read()
    tp.close()
    #print(tree_text)
    working_wiki_tree = make_tree(tree_text)
    #print(working_wiki_tree.prettify_tree())
    pp = open(sys.argv[2], "wb")
    pk.dump(working_wiki_tree, pp)
    pp.close()
    #print(working_wiki_tree.children)
    
    child_node = working_wiki_tree
    '''
    for node in working_wiki_tree.children:
        print(node.terms)
    print("\n\n")
    for node in child_node.children:
        print(node.terms)
    depth_count = 0
    print("\n\n")
    while len(child_node.children) != 0:
        if depth_count > 30:
            sys.exit()
        depth_count += 1
        print(child_node.terms)
        child_node = child_node.children[0]
    
    '''
    print(child_node.prettify_tree(fields=["terms"]))
    child_node.label()
    print(child_node.prettify_tree(fields=["terms", "labels"]))
















