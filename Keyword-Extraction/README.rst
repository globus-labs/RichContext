Keyword Extraction
==================

This program serves two main purposes:

1. Create a Convolutional Neural Network (CNN) model to predict key term labels based on  supervised labels for a set of documents.
2. Use this supervised CNN model to predict tags for a set of unlabeled documents, and then use this newly labeled data to create a better, semi-supervised CNN model.

Files
-----
* main.py
* KeyTermCNN.py
* textEmbedder.py

Execution
---------
Execute using the following command:

.. code-block:: none

	python3 main.py (or python main.py if Python3 is the default driver)


This program is intended to be run using Python 3, and has not been tested using Python 2.

Inputs
------

The dependencies for the program are as follows:

1. Keras (Using Theano backend).

The other dependencies should all come preinstalled with Python 3. If not, they can be found in the top lines of main.py.

Within the directory should be included the following input files:

1. A folder containing GloVe embeddings. The particular embedding dimensionality can be changed within main.py at the top of the file.
2. A JSON file containing a list of dictionaries with supervised tags. Each dictionary should represent an individual journal document, and should containing a text field mapping to the document's text, and a desired tag field containing the supervised labels. The name of this file can be specified at the top of main.py.
3. A JSON file containing a list of dictionaries without labels. This should also have a text field, but does not need to have tags. This will be used to train for the semisupervised model.
	
The name of the text field and tag field can be specified within main.py. 

Intermediate Files
------------------

In the course of running, the program will save the supervised model CNN and the semisupervised model CNN. The files that these are saved to can be specified at the top of main.py as well. The program also saves a .json file that contains the mappings from keywords to numbers and vice versa. This can be used to map the CNN outputs to specific tags.

Outputs
-------

The program outputs predictions for a set of documents, as well as a score that is determined by comparing true labels to predicted labels to actual labels for a withheld set of supervised documents. The file paths in which to save these files can be specified in main.py as well.

The main method can be modified as desired to adjust output format, and the KeyTermCNN and textEmbedder classes can be used in conjunction with other main methods to get the desired  output.
