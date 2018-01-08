import numpy as np
import pandas as pd
import os
import sys
import random as rd
import ast
import json
import codecs
import re

from nltk.corpus import stopwords as STOPWORDS
from textEmbedder import textEmbedder
from KeyTermCNN import CNN_1D


stopwords = set(STOPWORDS.words("english"))

args = sys.argv

#Where to read the text and tag data from
DATA_LABELED_PATH = "tagged_docs.json"
#Where unlabeled data comes from
DATA_UNLABELED_PATH = "untagged_docs.json"
#Which field we want to use to train the neural network
CHOSEN_FIELD = "populations"
#Which field the text is located in the JSON object
TEXT_FIELD = "text"
#Where to write the supervised score to
SCORE_FILE_SUP = "sample_score_sup.txt"
#Where to write the semisupervised score to
SCORE_FILE_SEMI = "sample_score_semi.txt"
#Where to store mapping from label to number/index and vice versa
MAPPING_FILE = "tags_bij_index.json"
#File in which to store supervised tags
SUP_TAG_FILE = "sample_tags_sup.json"
#File in which to store semisupervised tags
SEMI_TAG_FILE = "sample_tags_semi.json"
#Dimensionality of embedding to use 
DIMENSION = 50
#Name of file to store trained supervised model in
SUPERVISED_MODEL = "supervised_model.h5"
#Name of the file to store trained semisupervised model in
SEMI_MODEL = "semi_model.h5"
#Total number of words per document to use as the input to the neural network
NUM_WORDS = 500
#The proportion of the documents to use for intial training
PROP_SUPERVISED = 0.5
#The proportion of the documents to use for the second round of traning
PROP_SEMI = 0.8
#What mode to run the program in 
MODE = "Semisupervised"

'''
Given a list of lists of tags, where each list of tags corresponds to the tags on a given document,
picks out all distinct tags, and enumerates them. More specifically, returns a dictionary mapping from
tags to number, and number to tags. That is, the mapping is a bijection.

Input: List of lists of tags
Output: dictionary mapping from tags to numbers, and mapping from numbers to tags 

'''
def enumerate_tags(tags_list):
    total_tags = []
    for tags in tags_list:
        for tag in tags:
            total_tags.append(tag)
    total_tags = set(total_tags)
    word_to_num = {}
    num_to_word = {}
    for place, word in enumerate(total_tags):
        word_to_num[word] = place
        num_to_word[place] = word
    return word_to_num, num_to_word

'''
Input:
Y_data: a list of lists of keywords. The position i, j corresponds to the jth keyword of the ith document
tags_to_num: a dictionary mapping from keywords to a number/index

Output:
Y_vecs: A list of vectors. The position i, j correpsonds to the jth coordinate of the vector for the ith
document. If this value is 1, then the ith document is tagged with the jth keyword. Otherwise, the ith document
is not tagged with the jth keyword.
'''
def tags_to_vector(Y_data, tags_to_num):
    Y_vecs = []
    num_tags = len(tags_to_num.keys())
    for tag_set in Y_data:
        to_append = np.zeros(num_tags)
        for tag in tag_set:
            to_append[tags_to_num[tag]] = 1
        Y_vecs.append(to_append)
    return Y_vecs
'''
Input:
Y_vecs: A list of vectors. The position i, j correpsonds to the jth coordinate of the vector for the ith
document. 

num_to_tags: A dictionary mapping from number/index to a distinct keyword. The mapping is bijective.

threshold: If the i, j coordinate has a value >= threshold, then will tag the ith document with the jth
keyword

Output:

Y_tags a list of lists of keywords. The position i, j corresponds to the jth keyword of the ith document
tags_to_num: a dictionary mapping from keywords to a number/index

'''
def recover_tags(Y_vecs, num_to_tags, threshold = 1):
    Y_tags = []
    for vec in Y_vecs:
        to_append = []
        for i in range(len(num_to_tags.keys())):
            if vec[i] >= threshold:
                to_append.append(num_to_tags[i])
        Y_tags.append(to_append)
    return Y_tags


'''
Input:
text: a given string of arbitrary length to be parsed and tokenized.

Output:
parsed_text: A list of parsed and tokenized non-stopwords that represents the given input document
'''
def _parse_and_tokenize_text(text):
    words = text.split()
    parsed_text = []
    for word in words:
        word = word.lower()
        if word in stopwords:
            continue
        word_new = word.replace("'s", "")
        word_new = re.sub(r"[^a-zA-Z]", "", word_new)
        parsed_text.append(word_new)
    return parsed_text


'''
Input:
X_data: A list of strings representing documents.

Output: A list of lists of strings, where each element of the latter list of strings represents a
tokenized document.
'''
def parse_and_tokenize_texts(X_data):
    X_data_parsed = []
    for text in X_data:
        X_data_parsed.append(_parse_and_tokenize_text(text))
    return X_data_parsed

'''
Input:
l: a list

prop: a decimal number greater than or equal to zero and less than or equal to one.

Output:
two lists, the former representing all elements in the frist prop amount of the list, the latter
representing all elements after the proportioned split.
'''
def quick_split(l, prop):
    return l[:int(prop*len(l))], l[int(prop * len(l)):]


'''
def main_supervised(x_train, y_train, x_test, y_test):
    cnn = CNN_1D(input_dim=(2000, 50), output_dim=len(word_to_num.keys()))
    cnn.train(x_train, y_train, term_present=False, multi_label=True, nb_epochs=10)
    score = cnn.predict(x_test, y_test, term_present=False, multi_label=True)
    print(score)
    outfile = open(SCORE_FILE, "w")
    outfile.write(str(score))
    outfile.close()
'''

def field_to_list(jsons, field):
    ret_list = []
    for doc in jsons:
        try:
            ret_list.append(doc[field])
        except:
            ret_list.append([])
    return ret_list

'''
Main method for the class. Refer to top of the file for keyword labels. Will parse labeled data
file to make input for testing and training neural network. If set to Supervised learning, will 
use the data to make a solely supervised model. If set to semisupervised, will first make sure that
a supervised model exists, and will then use it to tag unlabelled data to be input for another 
supervised model. 

Will save the models and the scores. The name of the files to be saved to can be found and modified
once again at the top of this file. To convert from vector to keyword labels, the mapping from tag
to index and index to tag are also saved, once again at the beggining of the file.


'''
if __name__ == '__main__':
    fp = codecs.open(DATA_LABELED_PATH, "r", encoding='utf-8',
                    errors='ignore')
    text_w_tags = json.load(fp)
    fp.close()

    X_text = field_to_list(text_w_tags, TEXT_FIELD)
    Y_tags = field_to_list(text_w_tags, CHOSEN_FIELD)
    tags_to_num, num_to_tags = enumerate_tags(Y_tags)
    maps = [tags_to_num, num_to_tags]
    map_file = open(MAPPING_FILE, "w")
    json.dump(maps, map_file)
    map_file.close()

    Y_vecs = tags_to_vector(Y_tags, tags_to_num)
    X_data = parse_and_tokenize_texts(X_text)
    embedder = textEmbedder(dimension=DIMENSION, text_length=NUM_WORDS)
    X_data_temp = []


    for text in X_data:
        X_data_temp.append(embedder.embed_text(text, split=True))
    X_data = X_data_temp
    x_data, y_data = np.array(X_data), np.array(Y_vecs)
    x_train, x_test = quick_split(x_data, 0.8)
    y_train, y_test = quick_split(y_data, 0.8)


    if MODE == "Supervised" or not os.path.exists(SUPERVISED_MODEL):
        cnn = CNN_1D(input_dim=(NUM_WORDS, DIMENSION), output_dim=len(tags_to_num.keys()))
        cnn.train(x_train, y_train)
        score = cnn.score(x_test, y_test)
        labels = cnn.predict(x_test)


        tag_file = open(SUP_TAG_FILE, "w")
        arr_and_tags = [x_test.tolist(), labels.tolist()]
        json.dump(arr_and_tags, tag_file)
        tag_file.close()


        outfile = open(SCORE_FILE_SUP, "w")
        outfile.write(str(score))
        outfile.close()
        cnn.save(SUPERVISED_MODEL)


    if MODE == "Semisupervised":
        cnn = CNN_1D()
        cnn.from_file(SUPERVISED_MODEL, input_dim=(NUM_WORDS, DIMENSION), output_dim=len(tags_to_num.keys()))
        fp = codecs.open(DATA_UNLABELED_PATH, "r", encoding='utf-8',
                    errors='ignore')
        text_w_tags_un = json.load(fp)
        fp.close()


        X_text_un = field_to_list(text_w_tags_un, TEXT_FIELD)
        X_data_un = parse_and_tokenize_texts(X_text_un)
        X_data_temp = []
        for text in X_data_un:
            X_data_temp.append(embedder.embed_text(text, split=True))
        X_data_un = X_data_temp
        Y_labels_un = cnn.predict(X_data_un)


        Total_X = np.concatenate((x_train, X_data_un))
        print(Total_X.shape)
        Total_Y = np.concatenate((y_train, Y_labels_un))
        Total_X_train, Total_X_test = quick_split(Total_X, 0.8)
        Total_Y_train, Total_Y_test = quick_split(Total_Y, 0.8)


        cnn_semi = CNN_1D(input_dim=(NUM_WORDS, DIMENSION), output_dim=len(tags_to_num.keys()))
        cnn_semi.train(Total_X_train, Total_Y_train)
        predictions_semi = cnn_semi.predict(Total_X_test)
        tag_file = open(SEMI_TAG_FILE, "w")
        arr_and_tags = [Total_X_test.tolist(), predictions_semi.tolist()]
        json.dump(arr_and_tags, tag_file)
        tag_file.close()
        
        score_semi = cnn_semi.score(Total_X_test, Total_Y_test)
        cnn_semi.save(SEMI_MODEL)
        outfile = open(SCORE_FILE_SEMI, "w")
        outfile.write(str(score_semi))
        outfile.close()
