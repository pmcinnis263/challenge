#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Matching Challenge
This python program attempts to match products to listings
"""

import argparse
import json
import os
import sys

from source.cluster import k_means_cluster
from source.parse import parse_json, sanitize_listings_by_language
#from source.

ENGLISH_CURRENCIES=['USD', 'CAD', 'GBP']

if __name__ == "__main__":

    # parse cli
    parser = argparse.ArgumentParser(description='Matching Challenge entry')
    parser.add_argument('-p', dest='products', type=str, required=False,
        help='input products.txt', default=os.path.join('data','products.txt'))
    parser.add_argument('-l', dest='listings', type=str, required=False,
        help='input listings.txt', default=os.path.join('data','listings.txt'))
    parser.add_argument('-o', dest='results', type=str, required=False,
        help='output results.txt', default=os.path.join('output','results.txt'))
    parser.add_argument("--cached", dest='cache', required=False,
        help='use cached model', action='store_true')
    parser.add_argument("--debug", dest='debug', required=False,
        help='show debug messages', action='store_true')
    args = vars(parser.parse_args(sys.argv[1:]))

    # parse the files to lists of dictionaries
    products = parse_json(args['products'])
    listings = parse_json(args['listings'])

    # the number of products is the known number of clusters
    num_products = len(products)

    # get clean, non-duplicated listing titles
    # @todo parse makes products['model'].lower() & ['manufacturer'].lower()
    # @todo make lists of sanitized text in the below method
    sanitized_listings = sanitize_listings_by_language(
                                    listings=listings,
                                    english_currencies=ENGLISH_CURRENCIES)

    # sort the listings by language so that KMeans is more accurate
    english_titles = [l['sanitized_text'] for l in sanitized_listings['english']]
    foreign_titles = [l['sanitized_text'] for l in sanitized_listings['foreign']]
    all_titles = []
    all_titles.extend(english_titles)
    all_titles.extend(foreign_titles)

    assert(len(english_titles) > 10000), \
        "KMeans fit solution is not recommended for less that 10k data points"

    # perform Kmeans clustering of the listing titles
    kmc = k_means_cluster(num_clusters=num_products, language='english')
    if args['cache']:
        kmc.load('model.pkl')
    else:
        kmc.fit(list_of_text=english_titles, max_iter=1000)
        kmc.save('model.pkl')

    # print the first 5 clusters and all associated listings (debug)
    if args['debug']:
        kmc.predict_and_print_clusters(list_of_text=all_titles)

    # get predictions for all the titles, with associated top keywords
    predictions = kmc.predict(list_of_text=all_titles)
    clusters = kmc.get_top_cluster_keywords(predictions=predictions)

    # @todo filter cost outliers from clusters

    # match the word clusters to products
    results = {}
    product_matches = 0
    for i, p in enumerate(products):
        for c in clusters:
            if p['model'].lower() in clusters[c] and \
               p['manufacturer'].lower() in clusters[c]:
                assert(c not in results)
                results[c] = {'product' : p,
                              'cluster' : clusters.pop(c),
                              'listings' : []}
                product_matches += 1
                break

    # inject listings into the result dict by cluster #
    listing_matches = 0
    for i, (l, p) in enumerate(zip(listings, predictions)):
        if p in results and \
           results[p]['product']['model'].lower() in l['sanitized_text']:
            l.pop('sanitized_text') # we don't want this in the results.txt
            results[p]['listings'].append(l)
            listing_matches += 1

    print ("matched {0:.1f}% of clusters to products\n"\
           "matched {1:.1f}% of listings to products".format(
            product_matches/len(products) * 100,
            listing_matches/len(listings) * 100))

    # finally, match the listings to the word clusters by using their predictions
    with open(os.path.join('output','results.txt'), 'wt') as outf:
        for r in results:
            outf.write(json.dumps({
                "product_name": results[r]['product']['product_name'],
                "listings": results[r]['listings']}) + "\n")
