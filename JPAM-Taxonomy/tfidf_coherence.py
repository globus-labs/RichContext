import sys
import os
import json
import numpy as np
import itertools
import json

from gensim import corpora
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict
from tree import read_state


E = 1
STATE_PATH = "skewed_run/mode"
DUMP_PATH = "JPAM-coherence/test.json"

def get_tfidf(corpus, word_list):
    vectorizer = TfidfVectorizer(vocabulary=word_list)
    matrix = vectorizer.fit_transform(corpus)
    return matrix, vectorizer

def file_to_corpus(file_path, dictionary):
    fp = open(file_path, "r")
    corpus = []
    for line in fp:
        freqs = line.split()[1:]
        doc = ""
        for pair in freqs:
            word_num, freq = pair.split(":")
            word = dictionary[int(word_num)]
            for i in range(int(freq)):
                doc += word
                doc += " "
        corpus.append(doc)
    return corpus

def construct_freqs(file_path):
    fp = open(file_path, "r")
    frequencies = defaultdict(lambda: defaultdict(float))
    for line in fp:
        parts = line.split()
        num, fr = parts[0], parts[1:]
        for part in fr:
            wn, f = part.split(":")
            frequencies[int(num)][int(wn)] = float(f)
    return frequencies

def get_normalize_coef(tfidf, word, freq, doc_num):
    run_sum = 0
    for doc in range(doc_num):
        if freq[doc][word] > 0:
            run_sum += tfidf[doc][word]
    return run_sum

def get_top_coef(tfidf, w1, w2, freq, doc_num):
    run_sum = 0
    for doc in range(doc_num):
        if freq[doc][w1] > 0 and freq[doc][w2] > 0:
            run_sum += tfidf[doc][w1] * tfidf[doc][w2]
    return run_sum

def tfidf_coherence(tfidf, freq, t, Wt, doc_num):
    coh = 0
    for w1, w2 in itertools.product(Wt, Wt):
        numer = get_top_coef(tfidf, w1, w2, freq, doc_num)
        denom = get_normalize_coef(tfidf, w2, freq, doc_num)
        coh += np.log(numer/denom)
    return coh

    
def read_topics(state_filename,
               vocab,
               sig_size):
    """
    read the state from an iteration file (e.g., mode)

    """

    def top_n_words(topic,
                vocab,
                nwords):
        """
        the top n words from a topic
        vocab is a map from integers to words

        """
        indices = list(range(len(vocab)))
        indices.sort(key=lambda i: topic[i], reverse=True)
        return [(i, topic[i]) for i in indices[0:nwords]]

    state = open(state_filename, 'r')
    topics = {}
    num_words = {}
    count = 0
    for line in state:
        if count < 9:
            count += 1
            continue
        (top_num, parent, ndocs, nwords, scale, word_cnt) = line.split(None, 5)
        (top_num, parent, ndocs, nwords) = [int(x) for
                                       x in [top_num, parent, ndocs, nwords]]
        scale = float(scale)
        num_words[top_num] = nwords
        topic = [int(x) for x in word_cnt.split()]
        topics[top_num] = top_n_words(topic, vocab, sig_size)
    return topics, num_words

def main_vectorize():
    corpus_path = sys.argv[1]
    dictionary = corpora.Dictionary.load(sys.argv[2])
    corpus = file_to_corpus(corpus_path, dictionary)
    num_docs = len(corpus)
    freq = construct_freqs(corpus_path)
    words = dictionary.values()
    tfidf, vect = get_tfidf(corpus, words)
    print(tfidf[0][0][0])
    sys.exit()
    topics, num_words = read_topics(STATE_PATH, dictionary, 20)
    coherence_score = {}
    for t in topics.keys():
        Wt = [wn for wn, word in topics[t]]
        coh = tfidf_coherence(tfidf, freq, t, Wt, num_docs)
        coherence_score[t] = coh
    return coherence_score
    #vect = get_tfidf()


if __name__ == "__main__":
    coherences = main_vectorize()
    dp = open(DUMP_PATH, "w")
    json.dump(coherences, dp)
    dp.close()


    
