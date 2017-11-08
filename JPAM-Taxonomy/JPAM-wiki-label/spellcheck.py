import sys
import enchant as en
import re
import json

args = sys.argv
d = en.Dict("en_US")

def main_spellcheck(in_path, out_path):
    fp = open(in_path, "r")
    text = fp.read()
    fp.close()
    mispelled_words = spell_check(text)
    dp = open(out_path, "w")
    json.dump(mispelled_words, dp)
    dp.close()
    return



def spell_check(input_text):
    text = re.sub('\[.*?\]', '', input_text)
    lines = text.split("\n")
    mispelled_words = []
    for line in lines[9:]:
        line = line.strip()
        if line == "":
            continue
        else:
            curr_phrase = line.split(" ")
            x_tend = [word for word in curr_phrase if not d.check(word)]
            mispelled_words.extend(x_tend)
    return mispelled_words

if __name__ == "__main__":
    in_path = args[1]
    out_path = args[2]
    main_spellcheck(in_path, out_path)
    sys.exit()
