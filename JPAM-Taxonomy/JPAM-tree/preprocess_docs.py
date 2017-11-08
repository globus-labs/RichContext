import sys
import os

from gensim.corpora import Dictionary
from collections import defaultdict

args = sys.argv

DUMP_DIRECTORY = ""
DUMP_FILE = ""
DICT_FILE = ""

def extract_texts(directory, dump_dir):

    def extract_text(fp):
        return

    if not os.path.exists(directory):
        raise Exception("%s is not a valid directory!" % directory)
    for filename in os.listdir(directory):
        path = directory + filename
        fp = open(path, "rb")
        text = extract_text(fp)
        fp.close()
        dpath = dump_dir + filename.strip(".pdf") + ".txt"
        dp = open(dpath, "w")
        dp.write(text)
        dp.close()
    return

def generate_dict(directory, dict_name):
    if not os.path.exists(directory):
        raise Exception("%s is not a valid directory!" % directory)
    documents = []
    for filename in os.listdir(directory):
        path = directory + filename
        fp = open(path, "r")
        documents.append(fp.read())
        fp.close()
    dictionary = Dictionary(documents)
    dictionary.save(dict_name)
    return

def generate_sparse(directory):
    if not os.path.exists(directory):
        raise Exception("%s is not a valid directory" % directory)
    corpus = []



if __name__ == "__main__":
    if len(args) <= 1:
        print("You need to select modes")
        sys.exit()
    if "extract" in args[1:]:
        extract_texts(INPUT_DIR)
    if "dictionary" in args[1:] and os.path.exists("./" + DUMP_DIRECTORY):
        generate_dict(INPUT_DIR)
    if "sparse"  in args[1:] and os.path.exists("./" + DUMP_DIRECTORY) and os.path.exits("./" + DUMP_DIRECTORY)
        and os.path.exits("./" + DICT_FILE):
        generate_sparse(INPUT_DIR)
    sys.exit()




