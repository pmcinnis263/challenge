#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Matching Challenge
This python program attempts to match products to listings
"""

import argparse
import os
import sys

from source.parse import parse_json
from source.cluster import k_means_cluster_listing_titles

if __name__ == "__main__":

    # parse cli
    parser = argparse.ArgumentParser(description='Matching Challenge entry')
    parser.add_argument('-p', dest='products', type=str, required=False,
        help='input products.txt', default=os.path.join('data','products.txt'))
    parser.add_argument('-l', dest='listings', type=str, required=False,
        help='input listings.txt', default=os.path.join('data','listings.txt'))
    parser.add_argument('-o', dest='results', type=str, required=False,
        help='output results.txt', default=os.path.join('output','results.txt'))
    args = vars(parser.parse_args(sys.argv[1:]))

    # parse the files to lists of dictionaries
    products = parse_json(args['products'])
    listings = parse_json(args['listings'])

    # the number of products is the known number of clusters
    num_products = len(products)

    # perform Kmeans clustering of the listing titles
    centroids, terms = clustered_listings = k_means_cluster_listing_titles(
                                                    listings=listings,
                                                    num_products=num_products)

    # print top 5 words in each product listing cluster
    for i in range(num_products):
        print("Cluster %d:" % i),
        for ind in centroids[i, :5]:
            print(' %s' % terms[ind]),
        print

    import pdb; pdb.set_trace()