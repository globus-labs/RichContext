import sys
import os
import json
import re
import nltk

TREE_FILE = "791docs_8330iter_skewed.txt"
LABEL_FILE = "categorical_labels_skewed.json"
DUMP_FILE = sys.argv[1]
NUM_TO_KEEP = 4

def remove_high_level(level_words, curr_json, div_lev):
    if div_lev == 0:
        return curr_json
    bad_words = []
    new_json = []
    for i in range(div_lev):
        for word in curr_json:
            if word in level_words[i] and word not in bad_words:
                bad_words.append(word)
    for word in curr_json:
        if word not in bad_words:
            new_json.append(word) 
    print("bad words" + str(bad_words))
    print("words making it throught" +str(new_json))
    return new_json



def tree_mapping(tree_data, labels):
    text = re.sub('\[.*?\]', '', tree_data)
    lines = text.split("\n")
    new_tree = []
    prev_spaces = -1
    level_words = []
    for i in range(3):
        level_words.append([])
    for line in lines:
        line_new = line.strip()
        if line_new == "":
            continue
        curr_label = labels[line_new]
        if curr_label == []:
            continue
        num_spaces = len(line) - len(line.lstrip(" "))
        div_lev = int(num_spaces/5)
        if num_spaces <= prev_spaces:
            for i in range(len(level_words)):
                if i >= div_lev:
                    level_words[i] = []
        #print(num_spaces)
        new_string = ""
        for i in range(num_spaces):
            new_string += " "
        level_words[div_lev] = curr_label
        new_string += str(line_new)
        new_string += "\t"
        curr_label = remove_high_level(level_words, curr_label, div_lev)
        if len(curr_label) <= NUM_TO_KEEP:
            new_string += str(curr_label)
        else:
            new_string += str(curr_label[:NUM_TO_KEEP])
        new_tree.append(new_string)
        #print(new_string)
    print(level_words)
    return ("\n").join(new_tree)



def main():
    fp = open(LABEL_FILE, "r")
    labels = json.load(fp)
    fp.close()
    tp = open(TREE_FILE, "r")
    tree_data = ("\n").join(tp.read().split("\n")[9:])
    mapping = tree_mapping(tree_data, labels)
    dp = open(DUMP_FILE, "w")
    dp.write(mapping)
    dp.close()
    return




if __name__ == "__main__":
    main()