JPAM Taxonomy
=============


This project aims to automate the creation of a herirachical ontology from a corpus of text. The purpose for this is to develop an ontology that can then be used for classifying various objects. In this repository we explore methods for categorizing objects through the automatically generated topic tree for our target journals. 

Hierarchical LDA
----------------
The Hierarchical LDA model is a form of unsupervised learning that aims to discover latent topics present in a corpus of papers, as well the relationships between the latent topics. Preprocessing of data consisted of mapping each document into a bag of words format, which essentially ignores order of words in the learning process, and pruning stop words, or words which have little importance to the meaning of an article, such as the words "the" and "of". Overall, this approach was not well suited for our purposes. First, it is computationally intensive and therefore slow.  Secondly,  our corpus size was too small to develop sufficiently coherent topics.  

Clustering Topic models
----------------------
The second approach uses a standard LDA model and hierarchical clustering to build the ontology. Here we preprocess the data in an identical manner to the above approach. Following the construction of the base vanilla LDA model, we build a tree on the topics using hierarchical clustering. Before clustering, we filtered out topics we viewed as noise by hand, such as "doi journal public policy", that could be considered "catch all" topics. We would expect almost every article in all of the journals to fall into these topics, so we gain no benefit by keeping them in the model. For the clustering, we used a measure of closeness that considered the pairwise distance between two given topics in the LDA model, where each topic is a probability distribution over all of the words found in our corpus, minus the words we exclude through stopword pruning.  This approach generates a tree of height log(n), where n is the number of topics generated.

Labelling 
---------

One of the biggest problems with such latent models is that topics are opaque: they are a collection of words that are often meaningless to others. To address this problem and in an effort to derive metadata to be associated with documents we wanted to provide a single word or phrase labels to each topic. We developed and tested a myriad of labeling approaches. Specifically, we applied wiki-labeling approaches that leverage wikipedia's vast corpus of curated documents to obtain labels. 

We used a direct wiki-labeling technique to label the leaves of our developed tree which consisted of finding the wikipedia article returned with search of several of the most probable words in a given topic. After we used this technique to label the leaves, we tested a number of metrics that given a set of wikipedia pages and topics could find good labels to apply to intermediate nodes of the tree (e.g. where two or more topics meet, a most recent ancestor). Some of the techniques we used are as follows:

* Shortest Common Ancestor in the wikipedia category tree
* Shortest Common Ancestor guided by A*
* Most central node in graph of wikipedia links
* Highest pagerank among wikipedia category pages above the topic pages
* Highest pagerank among pages linked to by topic pages

Visualization
------------
This project includes several models for visualization opaque topics as well as compare corpera. 

Our first visualization shows the derived hierarchical topic models in dendrogram form. Here, each of the topics are clustered by their relationship with one and other. Colors depict groupings of related topics. We also include the terms and their weightings for each of the topics to enable readers to understand these groupings. 

Our second visualization explores differences between corpera based on topic distance measures. These methods show which area each corpus is focused and areas in which it is not. 

Finally, our third visualization uses a graph to show connected (related) entities.  Here we placed each document as a node in a graph where the edge represents a relationship based on shared metadata (e.g., similar topic weights). 


Code
----

This project contains several modules for downloading publications, deriving the ontology, associating labels with topics, and visualizing results. 

The first collection of scripts downloads articles from various journals. 

* JPAM-pull: Scripts for downloading articles from JPAM. volume_iterator.py retrieves a collection of DOIs from specified JPAM volumes. percentage_pull.py then downloads full text articles and metadata for those publications. 
* JPART-pull: Scripts for downloading articles from JPART. pull.py downloads papers from the JPART website. 
* PAR-pull: Scripts for downloading articles from PAR. pull.py downlaods papers from the PAR website. 

The second collection of scripts create the ontology using herirachical LDA and heirarchical clustering of LDA topics

* tree.py: a script to create a hierarchical LDA topic model for a given corpus. 

The third collection of scripts associates lables with topics identified by the topic model

* wiki.py: a script to associate labels with topics. It uses various methods for identifying labels and different distance measures to associate labels with a given topic. 

The fourth collection of scripts visualizes and compares the various datasets. 

* compare_corpera.ipynb: a notebook that compares articles from the three journals. Specifically it calculates k-nearest neighbors from journal vectors and unique fingerprints for each journal.
* Dendrogram.ipynb: a notebook that creates dendogram visualizations of the derived ontologies as well as graphs that show the connections between topics.  


