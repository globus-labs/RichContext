from parser import DatasetNamesParser
import os
import csv


dataset_parser = DatasetNamesParser()

# files = ["/home/hong/Downloads/page1.html",
#          "/home/hong/Downloads/page2.html",
#          "/home/hong/Downloads/page3.html",
#          "/home/hong/Downloads/page4.html",
#          "/home/hong/Downloads/page5.html"]

# i = 1
# for file in files:
#     print("Dataset Names Found in File " + str(i) + ": ")
#     print(dataset_parser.findDatasetNames(file))
#     print("\n\n")
#     i += 1

csvfile = open('output.csv', 'w')
for root, dirs, files in os.walk("/home/hong/Downloads/icpsr papers"):
    for file in files:
        if file.endswith(".html"):
            full_path = os.path.join(root, file)
            # print(file + ', ', end='', flush=True)
            # print(dataset_parser.findDatasetNames(full_path))

            filewriter = csv.writer(csvfile, delimiter=',',
                                    quoting=csv.QUOTE_ALL)
            filewriter.writerow(dataset_parser.findDatasetNames(full_path))
    break;  # only traverse the top directory without entering subdirectories
csvfile.close()
