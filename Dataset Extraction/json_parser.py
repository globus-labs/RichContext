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

total = 0
exception1 = 0
exception2 = 0
exception3 = 0
no_abstract = 0
got_dataset = 0
success = 0
all_dataset = Counter()
flag = False
resultFile = open("resultFile.csv", 'w')
wr = csv.writer(resultFile, dialect='excel')
all_dataset_file = open("all_dataset.csv", 'w')
wr2 = csv.writer(all_dataset_file, dialect='excel')

for root, dirs, files in os.walk("/home/hong/Dropbox/scidir"):
    for file in files:
        if file.startswith("scidir_text"):
            full_path = os.path.join(root, file)
            with open(full_path) as data_file:
                data = json.load(data_file)
                try:
                    for i in range(0, len(data)):
                        # full_text = data[i]["originalText"]
                        # if isinstance(full_text, str) and \
                        #         full_text.count("1Introduction") == 2:
                        #     success += 1
                        #     flag = True
                        #     title2 = re.search("1Introduction(.+?)[^a-zA-Z].*?3\S",
                        #                        full_text).group(1)
                        #     regex_str = "1Introduction.*1Introduction(.+?)"+title2
                        #     intro = re.search(
                        #         regex_str,
                        #         full_text)
                        #     if not intro:
                        #         print(file)
                        #     intro = intro.group(1)
                        #     title = data[i]["coredata"]["dc:title"]
                        #     doi = data[i]["coredata"]["dc:identifier"]
                        #     abstract = data[i]["coredata"]["dc:description"]
                        #     if not abstract:
                        #         no_abstract += 1
                        #     parser = DatasetNamesParser()
                        #     dataset = parser.\
                        #         findCapitalizedWords([abstract, intro])

                        title = data[i]["coredata"]["dc:title"]
                        doi = data[i]["coredata"]["dc:identifier"]
                        full_text = data[i]["originalText"]
                        parser = DatasetNamesParser()

                        if title and full_text:
                            dataset = parser.findCapitalizedWords([full_text])
                            success += 1
                            if dataset:
                                got_dataset += 1

                                for item in dataset:
                                    all_dataset[item] += 1
                            ans = [full_path, title, doi]
                            ans.extend(dataset)
                            # print(dataset)
                            wr.writerow(ans)
                            # print(intro)
                            break
                    if not flag:
                        a = 1
                        #print(full_path)
                    else:
                        flag = False
                except:
                    # print(full_path)
                    exception3 += 1
                finally:
                    total += 1
    break

for ds_tuple in sorted(all_dataset.items(), key=itemgetter(1), reverse=True):
    wr2.writerow(ds_tuple)

resultFile.close()
all_dataset_file.close()
print(str(got_dataset) + '/' + str(success) + '/' + str(total) + ', ' + str(no_abstract))
