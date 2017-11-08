import os
import json
import sys
import re
from collections import defaultdict

def main():
	total_doi = 0
	total_pdf = 0
	incor_pdf = 0
	total_meta = 0
	for filename in os.listdir('.'):
		if filename[0] == ".":
			continue
		fp = open(filename, "r")
		curr_list = json.load(fp)
		fp.close()
		for curr_dict in curr_list:
			total_doi += 1
			if curr_dict["meta_succ"]:
				total_meta += 1
			if curr_dict["pdf_succ"]:
				total_pdf += 1
	print(total_doi)
	print(total_meta)
	print(total_pdf)

def count_doi():
	total_doi = 0
	for filename in os.listdir('.'):
		if filename[0] == ".":
			continue
		fp = open(filename, "r")
		curr_list = json.load(fp)
		fp.close()
		for curr_dict in curr_list:
			total_doi += 1
	print(total_doi)

def unique_doi():
	track = defaultdict(int)
	for filename in os.listdir('.'):
		if filename[0] == ".":
			continue
		fp = open(filename, "r")
		curr_list = json.load(fp)
		fp.close()
		for curr_dict in curr_list:
			track[curr_dict] = 0
	keys = track.keys()
	dump_list = []
	for key in keys:
		dump_list.append(str(key))
	return dump_list

def meta_doi():
	track = defaultdict(int)
	for filename in os.listdir('.'):
		if filename[0] == ".":
			continue
		fp = open(filename, "r")
		curr_list = json.load(fp)
		fp.close()
		for curr_dict in curr_list:
			doi = curr_dict["doi"]
			track[doi] = 0
	keys = track.keys()
	dump_list = []
	for key in keys:
		dump_list.append(str(key))
	return dump_list

def cross_ref():
	fp = open("unique_doi.json", "r")
	all_doi = json.load(fp)
	fp.close()
	fp = open("meta_doi.json", "r")
	meta_doi = json.load(fp)
	fp.close()
	missing_list = []
	print(len(all_doi))
	print(len(meta_doi))
	for doi in all_doi:
		if doi not in meta_doi:
			missing_list.append(doi)
	dp = open("missing_doi.json", "w")
	json.dump(missing_list, dp)
	dp.close()
	return







if __name__ == "__main__":
	cross_ref()
	sys.exit()
	keys = meta_doi()
	dp = open("meta_doi.json", "w")
	json.dump(keys, dp)
	dp.close()