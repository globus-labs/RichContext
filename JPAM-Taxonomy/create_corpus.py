from __future__ import print_function

import glob
import json
import os
import subprocess
import sys
from pipes import quote
from time import time

import gensim


sys.path.append("/usr/local/lib/python2.7/site-packages/")


CNAME = "corpusLem"

LEMMATIZED = {}


class DirectoryCorpus(gensim.corpora.TextCorpus):

    def get_texts(self):
        for i, filename in enumerate(self.input):
            print(filename)
            with open(filename) as reader:
                text = reader.read()
                toks = gensim.utils.tokenize(text)
                yield toks


def pdf_to_text(filepath):
    """Extract the text from the pdf given by filepath"""
    call_time = int(time())
    output_path = os.path.join(
        "tmp", "%d.txt" % call_time
    )
    qinput = quote(filepath)
    qoutput = quote(output_path)
    subprocess.call(
        'pdftotext %s %s' % (qinput, qoutput),
        shell=True
    )
    path, filename = os.path.split(filepath)
    basename, extension = os.path.splitext(filename)
    text = open(output_path).read()
    os.remove(output_path)
    return text  # .decode("utf-8").encode("ascii", "ignore")


def pdf_dir_to_txt_dir(directory="./JPAM-pull/PDFS/"):
    pdfglob = os.path.join(directory, "*.pdf")
    pdffiles = glob.glob(pdfglob)
    txtfiles = [os.path.splitext(os.path.split(f)[1])[
        0] + ".txt" for f in pdffiles]
    txtfiles = [os.path.join("texts", f) for f in txtfiles]

    for pdf, txt in zip(pdffiles, txtfiles):
        try:
            text = pdf_to_text(pdf)
            with open(txt, "w") as w:
                w.write(text)
        except:
            pass


def main(n=10, directory="./texts/"):
    # pdf_dir_to_txt_dir()

    # exit(0)

    directory = os.path.join(directory, "*.txt")
    filenames = glob.glob(directory)[:n]

    corpus = {}
    for i, fname in enumerate(filenames):
        print(i, fname)
        try:
            with open(fname) as r:
                corpus[fname] = list(gensim.utils.tokenize(r.read()))
        except Exception as e:
            print("Failed:", repr(e))
    json.dump(corpus, open("corpus.json", "w"))
    id2word = corpus.dictionary
    id2word.filter_extremes()

    with open(CNAME + "%d.vocab" % n, "w") as w:
        for ix, word in id2word.items():
            w.write(word + "\n")

    print("Iterating...")
    docmap_writer = open(CNAME + "%d.map" % n, "w")
    corpus_writer = open(CNAME + "%d.txt" % n, "w")
    for i, text in enumerate(corpus.get_texts()):
        try:
            bow = id2word.doc2bow(text)
            bow = ["%d:%d" % (tid, tcount) for tid, tcount in bow]
            M = len(bow)
            docmap_writer.write("Document %d\n" % i)
            corpus_writer.write("%d " % M)
            corpus_writer.write(" ".join(bow))
            corpus_writer.write("\n")
            docmap_writer.flush()
            corpus_writer.flush()
        except Exception as e:
            print(e)

    print("Closing files")
    corpus_writer.close()
    docmap_writer.close()
    id2word.save(CNAME + "%d.dict" % n)


if __name__ == "__main__":
    n = int(sys.argv[1])
    directory = sys.argv[2]
    main(n, directory)
