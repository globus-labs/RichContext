import os
import sys
import codecs
import numpy as np

'''
A class that loads a GloVe embedding and maps from words to coordinates.
'''
class textEmbedder(object):


  
    '''
    Inputs:
    dimension: Dimensionality of the GloVe embedding to use.
    text_length: the maximum length of a document to allow to be embedded.

    Outputs:
    None
    '''
    def __init__(self, dimension=50, text_length=1000):
        self.embeddings = {}
        self.dimension = dimension
        self.text_length = text_length
        file_name = "glove.6B.%sd.txt"%str(dimension)
        EMBED_PATH = "glove_embeddings/"
        emb_file = codecs.open(EMBED_PATH + file_name, "r", encoding='utf-8',
                    errors='ignore')
        for line in emb_file:
            emb_comp = line.split()
            self.embeddings[emb_comp[0]] = np.asarray(emb_comp[1:], dtype = 'float32')
        emb_file.close()
        return

    '''
    Input: A word to be embedded

    Output: If the word is in the embedding, the embedding coordintes, else, a vector of zeros
    '''
    def embed_word(self, word):
        emb_vec = self.embeddings.get(word)
        if emb_vec is None:
            return np.zeros(self.dimension)
        else:
            return emb_vec

    '''
    Inputs:
    text: the text to be embedded
    split: true if the text is tokenized, false if not.

    Outputs:
    An array where each row represents the coordinates of a word in the document        
    '''
    def embed_text(self, text, split=True):
        words = []
        if not split:
            words = text.split()
        else:
            words = text
        if len(words) > self.text_length:
            words = words[:self.text_length]
        i = 0
        emb_text = []
        while i < len(words):
            emb_text.append(self.embed_word(words[i]))
            i += 1
        while i < self.text_length:
            emb_text.append(np.zeros(self.dimension))
            i += 1
        return emb_text

