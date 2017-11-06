import json
import os
import re
import csv
from operator import itemgetter
from parser import DatasetNamesParser
from counter import Counter
from pprint import pprint

# pprint(data)

# print(data[0]["coredata"]["dc:title"])
# print(data[0]["coredata"]["prism:doi"])
# print(data[0]["coredata"]["dc:description"])
# print(data[0]["originalText"])

# total = 0
# exception1 = 0
# exception2 = 0
# exception3 = 0
# no_abstract = 0
# got_dataset = 0
# success = 0
all_dataset = Counter()
# flag = False
resultFile = open("JpamResultFile.csv", 'w')
wr = csv.writer(resultFile, dialect='excel')
all_dataset_file = open("jpam_all_dataset.csv", 'w')
wr2 = csv.writer(all_dataset_file, dialect='excel')
parser = DatasetNamesParser()
for root, dirs, files in os.walk("/home/hong/Downloads/jpam_texts"):
    for file in files:
        full_path = os.path.join(root, file)
        with open(full_path) as data_file:
            full_text = data_file.readlines()
            # you may also want to remove whitespace characters like `\n`
            # at the end of each line
            full_text = [x.strip() for x in full_text]
            dataset = parser.findCapitalizedWords(full_text)
            for item in dataset:
                all_dataset[item] += 1
            ans = [file]
            ans.extend(dataset)
            wr.writerow(ans)

for ds_tuple in sorted(all_dataset.items(), key=itemgetter(1), reverse=True):
    wr2.writerow(ds_tuple)
resultFile.close()
all_dataset_file.close()
