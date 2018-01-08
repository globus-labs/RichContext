Dataset Extraction
===================

Locating external references to datasets (and other entities) in publications is challenging as no relevant ontology is available and standard named entity recognition approaches do not apply. 

This project includes a dataset-specific Named Entity Recognition (NER) model  for exracting datasets from publications. We first split the paper into sections and apply the same natural language processing (NLP) models on each section to derive references. Specifically the sections extracted are abstracts, data sections, and figure and table captions.  

In each case we applied a model that aims to identify words that we view as "dataset indicative" (e.g. “survey”, “study”, “dataset”): that is, words that we find are often used within several words of the name of a dataset. We use several differnet methods to generate this list of words: manually defined, TF-IDF, and TextRank. 

We apply a named entity recognition approach and filter the named entities by the set of dataset indicative words. 

We evaluate our model on manually established linkages from the ICPSR repository. Our current model is able to extract dataset citations with precision of 89.13% and recall of 90.11%. Of our 50 papers, we correctly obtained the dataset in 82% of cases. We completely missed the dataset in 8% and incorrectly extracted a dataset in 10% of cases.  

Code
----------

The first scripts are designed to download linkages between papers and datasets from ICPSR. We first crawl the web interface to obtain linkages between papers and dataset. 

**ICPSR_dataset_crawler.py:** a utility class to get metadata of the studies indexed by ICPSR

**main_ICPSR_crawler.py:** the main entry program for the ICPSR metadata crawler

**main_ICPSR_OAI_craler.py:** the main entry program for getting ICPSR metadata (including citation)

The second set of scripts extract content from papers in different formats (e.g., JSON, HTML, and PDF). 

**json_parser.py:** parse texts from json papers

**HTMLParser.py:** parse texts from HTML papers

**jpam_parser.py** parse texts from JPAM pdf papers

Finally our third scripts apply the NER model to text documents to identify datasets.

**parser.py:** use the NER model to extract dataset names from texts. 



