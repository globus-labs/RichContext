import sys
import os
import json

def main():
	total_list = []
	for file_name in os.listdir("DOIS/"):
		fp = open("DOIS/" + file_name, "r")
		temp_list = json.load(fp)
		fp.close()
		print(len(temp_list))
		total_list.extend(temp_list)
	print(len(total_list))
	return

if __name__ == "__main__":
	main()
