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
        if len(list_of_text) > 10000:
            print("KMeans fit not recommended for less that 10k data points")

        print("fitting KMeans model...")
        self.vectorizer = TfidfVectorizer(stop_words=self.language)
        self.model = KMeans(n_clusters=self.num_clusters,
                            init='k-means++',
                            max_iter=max_iter,
                            n_init=1,
                            verbose=True)

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


    def get_top_cluster_keywords(self, predictions, n_words=15):
        """from predictions, get the top n_words for each cluster
        key of the cluster dict is the index in the list_of_text predicted with
        """
        #  make a dict for listings keyed by centroid number
        cluster_dict = dict([(i, []) for i in range(self.num_clusters)])
        for c in range(self.num_clusters):
            top_features = self.centroids[c][:n_words]
            cluster_dict[c] = [self.features[i] for i in top_features]
        return cluster_dict
