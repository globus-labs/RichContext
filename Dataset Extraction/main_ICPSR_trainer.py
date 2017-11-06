import csv
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.naive_bayes import MultinomialNB


with open("dataset_names.csv", "r", newline='') as dataset_file:
    reader = csv.reader(dataset_file)
    dataset_list = list()

    # this wouldn't work because each line would be treated as a list object
    # dataset_list = list(reader)

    for row in reader:
        dataset_list.extend(row)

    # print(len(dataset_list))
    training_set = dataset_list[:500]
    test_set = dataset_list[500:]
    # training_set2 = ("The sky is blue.", "The sun is bright.")

    # vectorizer = CountVectorizer(analyzer='word', stop_words='english')
    # train_counts = vectorizer.fit_transform(training_set)
    #
    # freq_term_matrix = vectorizer.transform(test_set)
    # tfidf = TfidfTransformer(norm="l2")
    # tfidf.fit(freq_term_matrix)
    #
    # tf_idf_matrix = tfidf.transform(freq_term_matrix)
    #
    # print(tf_idf_matrix)

    # tfidf_transformer = TfidfTransformer()
    # train_tfidf = tfidf_transformer.fit_transform(train_counts)
    # nb_classifier = MultinomialNB()
    # nb_classifier.fit(train_tfidf, training_set)
    # predicted = nb_classifier.predict(test_set)
    # print(np.mean(predicted))

    # Cosine Similarity
    dataset_list.append("Supplemental Nutritional Assistance Program")
    dataset_list.append("Special Supplemental Nutrition Program for Women")
    dataset_list.append("Using the Fragile Families and Child Wellbeing Study")
    dataset_list.append("Fragile Families and Child Wellbeing Study")
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(dataset_list)
    res = cosine_similarity(tfidf_matrix[1000:], tfidf_matrix[:500])
    avg = np.nanmean(res, axis=1)
    print(avg*100)
    # print(" <  1% : " + str((avg < 0.01).sum()))
    # print(" <  2% : " + str(((0.01 <= avg) & (avg < 0.02)).sum()))
    # print(" <  5% : " + str(((0.02 <= avg) & (avg < 0.05)).sum()))
    # print(" < 10% : " + str(((0.05 <= avg) & (avg < 0.10)).sum()))
    # print(" < 20% : " + str(((0.10 <= avg) & (avg < 0.20)).sum()))
    # print(" < 50% : " + str(((0.20 <= avg) & (avg < 0.50)).sum()))
    # print(" < 80% : " + str(((0.50 <= avg) & (avg < 0.80)).sum()))
    # print(" < 100% : " + str((0.80 <= avg).sum()))
