import csv
from ICPSR_dataset_crawler import IcpsrDatasetCrawler


with open("dataset_names.csv", "w") as dataset_file:
    wr = csv.writer(dataset_file, quoting=csv.QUOTE_ALL, delimiter="\n")
    dataset = IcpsrDatasetCrawler.get_dataset(20)
    print(str(len(dataset)) + " dataset names acquired.")
    wr.writerow(dataset)
