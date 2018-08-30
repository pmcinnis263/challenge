#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Clusters listings
This python program attempts to cluster similar listings using KMeans
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score

def k_means_cluster_listing_titles(listings, num_products, max_iter=100):
    ## cluster the products according to the text contents
    # https://pythonprogramminglanguage.com/kmeans-text-clustering/

    # vectorize the listing titles
    titles = [l['title'] for l in listings] #@TODO grab this in parse.py
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(titles)

    # perform KMeans clustering to obtain cluster centroids
    model = KMeans(n_clusters=num_products,
                   init='k-means++',
                   max_iter=max_iter,
                   n_init=1)
    model.fit(X)

    # convert each centroid into a sorted list of the most "relevant" words
    # ... access as: terms[centroids[i]] for i in range(num_products)
    centroids = model.cluster_centers_.argsort()[:, ::-1]
    terms = vectorizer.get_feature_names()

    return centroids, terms
