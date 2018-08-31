#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""KMeans cluster
This class implements a Kmeans text clustering in sklean, it should be used for:
categorization --> un-labelled data --> known # categories --> >10k samples
"""

import pickle

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans


class k_means_cluster():
    """interface to fit and predict with a Kmeans model
    reference: https://pythonprogramminglanguage.com/kmeans-text-clustering/
    """

    def __init__(self, num_clusters, language='english'):
        """init
        language: language for text-->features vectorization
                  ... should be kept constant for each model
        num_clusters: should be a known/approximated number of expected clusters
        """
        self.language = language
        self.num_clusters = num_clusters


    def fit(self, list_of_text, max_iter=100):
        """fit KMeans model to a list() containing strings
        max_iter: maximum # of iterations to fit model
        """
        print("fitting KMeans model...")
        self.vectorizer = TfidfVectorizer(stop_words=self.language)
        self.model = KMeans(n_clusters=self.num_clusters,
                            init='k-means++',
                            max_iter=max_iter,
                            n_init=1)

        # fit the model get the centroids of clusters and, text:features map
        self.model.fit(self.vectorizer.fit_transform(list_of_text))
        self.centroids = self.model.cluster_centers_.argsort()[:, ::-1]
        self.features = self.vectorizer.get_feature_names()
        print("model fit complete")


    def predict(self, list_of_text):
        """get centroids of clusters, vectorized terms, and cluster predictions
        returns a list of cluster indices for each elem of list_of_text
        """
        return self.model.predict(self.vectorizer.transform(list_of_text))


    def save(self, path):
        """ pickle and save the model to <path>
        """
        pickle.dump((self.vectorizer, self.model, self.centroids,
                     self.features, self.language, self.num_clusters),
                    open(path, 'wb'))


    def load(self, path):
        """load model from a saved pickle at <path>
        """
        self.vectorizer, self.model, self.centroids, self.features, \
        self.language, self.num_clusters = pickle.load(open(path, 'rb'))


    def predict_and_print_clusters(self, list_of_text, n_to_show=5):
        """predicts and makes a dict() keyed by cluster of top keywords
        dict keyed by fitted cluster # containing 'top_keywords'
        ... and the index in the items in list_of_text that are associated
        """
        predictions = self.predict(list_of_text)
        for c in range(min(n_to_show, self.num_clusters)):
            print("---------\nCluster {0}:\n{1}\n==".format(c,
                [self.features[ind] for ind in self.centroids[c, :15]])),
            for i,l in enumerate(predictions):
                if l == c:
                    print ('{0}'.format(list_of_text[i]))


    def get_top_cluster_keywords(self, predictions, n_words=15):
        """from predictions, get the top n_words for each cluster
        key of the cluster dict is the index in the list_of_text predicted with
        """
        #  make a dict for listings keyed by centroid number
        cluster_dict = dict([(i, []) for i in range(self.num_clusters)])
        for c in range(self.num_clusters):
            top_features = self.centroids[c][:n_words] #[predictions[c]][:n_words]
            cluster_dict[c] = [self.features[i] for i in top_features]
        return cluster_dict
