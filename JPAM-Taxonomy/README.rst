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
