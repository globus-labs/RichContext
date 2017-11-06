Dataset Extraction
===================


This is the Named Entity Recognition (NER) model of automatic dataset extraction from scientific publications.

----------
**ICPSR_dataset_crawler.py:** a utility class to get metadata of the studies indexed by ICPSR

**main_ICPSR_crawler.py:** the main entry program for the ICPSR metadata crawler

**main_ICPSR_OAI_craler.py:** the main entry program for getting ICPSR metadata (including citation)


**parser.py:** use the NER model to extract dataset names from texts. 

**json_parser.py:** parse texts from json papers

**HTMLParser.py:** parse texts from HTML papers

**jpam_parser.py** parse texts from JPAM pdf papers

