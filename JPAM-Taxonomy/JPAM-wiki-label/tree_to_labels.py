import sys
import os
import json
import re
import nltk
import wikipedia as wiki
import enchant

from collections import defaultdict

REPLACE_FILE = "acro_to_phrase.json"

class words2Label(object):

    def __init__(self, word_list=[], num_labels=1, lazy_labels=1, mode="lazy", threshold=3,
                replace_acro=True, acro_map=None):
        self.num = num_labels
        self.lazy_num = lazy_labels
        self.words = word_list
        self.thresh = threshold
        self.mode = mode
        self.acro = replace_acro
        self.acro_map = acro_map


    def set_labels(self, num_labels):
        self.num = num_labels

    def set_words(self, word_list):
        self.words = word_list

    def _get_labels_lazy(self):
        if len(self.words) == 0:
            raise Exception("The word list is empty!")
        search_phrase = ""
        if self.acro:
            words = []
            for word in self.words:
                if word.upper() in self.acro_map:
                    words.append(self.acro_map[word])
                else:
                    words.append(word)
            search_phrase = (" ").join(words)
        else:
            search_phrase = (" ").join(self.words)
        print("phrase: " + search_phrase)
        search_results = wiki.search(search_phrase)
        if len(search_results) <= self.lazy_num:
            return search_results
        else:
            return search_results[:self.lazy_num]

    def _preprocess(self, text):
        sents = [nltk.word_tokenize(sent) for sent in nltk.sent_tokenize(text)]
        sents = [nltk.pos_tag(sent) for sent in sents]
        return sents

    def _get_labels_advanced(self):
        labels = self._get_labels_lazy()
        print(labels)
        occurrences = defaultdict(int)
        for label in labels:
            print(label)
            try:
                page = wiki.page(label)
            except DisambiguationError as e:
                main_option = e.options[0]
                page = wiki.page(main_option)
            summary = page.summary
            sentences = self._preprocess(summary)
            sentences = [nltk.ne_chunk(sent, binary=True) for sent in sentences]
            num_ent = 0
            for sent in sentences:
                for pair in sent:
                    if isinstance(pair, nltk.tree.Tree):
                        for item in pair:
                            num_ent += 1
                            print(item[0])
                            occurrences[item[0]] += 1
                    else:
                        pass
            print(num_ent)
        key_occ = [(k, v) for (k, v) in sorted(occurrences.items())]
        print(key_occ)
        ret = []
        for item in key_occ:
            k = item[0]
            v = item[1]
            print(v)
            if v >= self.thresh:
                ret.append(k)
            else:
                break
        if len(ret) <= self.num:
            return ret
        else:
            return ret[:self.num]

    def _get_labels_categorical(self):
        try:
            labels = self._get_labels_lazy()
        except Exception as e:
            print(e)
            return []
        print(labels)
        occurrences = defaultdict(int)
        for label in labels:
            try:
                print(label)
                try:
                    page = wiki.page(label)
                except wiki.exceptions.DisambiguationError as e:
                    try:
                        main_option = e.options[0]
                        page = wiki.page(main_option)
                    except Exception as e:
                        continue
                except Exception as e:
                    print(e)
                    continue
                categories = page.categories
                for category in categories:
                    occurrences[category.lower()] += 1
            except Exception as e:
                print(e)
        key_occ = [(k, v) for (k, v) in occurrences.items()]
        key_occ = sorted(key_occ, key=lambda x: x[1], reverse=True)

        print(key_occ)
        print(len(key_occ))
        ret = []
        for item in key_occ:
            print(item)
            k = item[0]
            v = item[1]
            if v >= self.thresh and "page" not in k and "article" not in k:
                print("here")
                ret.append(k)
            else:
                continue
        if len(ret) <= self.num:
            print(ret)
            return ret
        else:
            print(ret)
            return ret[:self.num]

    def _get_labels_links(self):
        labels = self._get_labels_lazy()
        print(labels)
        occurrences = defaultdict(int)
        for label in labels:
            try:
                print(label)
                try:
                    page = wiki.page(label)
                except wiki.exceptions.DisambiguationError as e:
                    try:
                        main_option = e.options[0]
                        page = wiki.page(main_option)
                    except Exception as e:
                        continue
                except Exception as e:
                    print(e)
                    continue
                links = page.links
                for link in links:
                    occurrences[link.lower()] += 1
            except Exception as e:
                print(e)
        key_occ = [(k, v) for (k, v) in occurrences.items()]
        key_occ = sorted(key_occ, key=lambda x: x[1], reverse=True)
        print(key_occ)
        print(len(key_occ))
        ret = []
        for item in key_occ:
            print(item)
            k = item[0]
            v = item[1]
            if v >= self.thresh:
                print("here")
                ret.append(k)
            else:
                continue
        if len(ret) <= self.num:
            return ret
        else:
            return ret[:self.num]



    def get_labels(self):
        if self.mode == "lazy":
            return self._get_labels_lazy()
        elif self.mode == "advanced":
            return self._get_labels_advanced()
        elif self.mode == "categorical":
            return self._get_labels_categorical()
        elif self.mode == "links":
            return self._get_labels_links()
        return -1












def label_tree(input_text, mode):
    text = re.sub('\[.*?\]', '', input_text)
    lines = text.split("\n")
    words_to_labels = {}
    jp = open(REPLACE_FILE, "r")
    spellcheck = json.load(jp)
    jp.close()
    wiki_labeler = words2Label(num_labels=5, lazy_labels=10, threshold=2, mode=mode, acro_map=spellcheck)
    for line in lines[9:]:
        line = line.strip()
        if line == "":
            continue
        else:
            curr_phrase = line.split(" ")
            wiki_labeler.set_words(curr_phrase)
            result = wiki_labeler.get_labels()
            words_to_labels[line] = result
    return words_to_labels

def main():
    tree_file = sys.argv[1]
    fp = open(tree_file, "r")
    text = fp.read()
    mode = sys.argv[3]
    fp.close()
    mappings = label_tree(text, mode)
    dp = open(sys.argv[2], "w")
    json.dump(mappings, dp)
    dp.close()
    return



def test_advanced():
    test_parts = "Education logistical statistical inference".split()
    wiki_labeler = words2Label(num_labels=5, mode="links", threshold=2)
    wiki_labeler.set_words(test_parts)
    res = wiki_labeler.get_labels()
    print(res)
    return


if __name__ == "__main__":
    print("starting")
    main()
    print("done")







