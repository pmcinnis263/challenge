#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Matching Challenge
This python program attempts to match products to listings using hashing
"""

import argparse
import json
import os
import sys

from source.parse import parse_json, hash_products, writeout_results
from source.match import match_listings

MIN_MODEL_LEN = 2       # less than 2 will allow excessive model matches
MIN_MANU_LEN = 1        # less than 1 will exclude all 'hp' listings
UMMATCHED_LISTINGS_JSON = os.path.join('output', 'unmatched_listings.json')
UNHASHED_PRODUCTS_JSON = os.path.join('output', 'unhashed_products.json')


if __name__ == "__main__":

    # parse cli args
    parser = argparse.ArgumentParser(description='Matching Challenge entry')
    parser.add_argument('-p', dest='products', type=str, required=False,
                        help='input products.txt',
                        default=os.path.join('data', 'products.txt'))
    parser.add_argument('-l', dest='listings', type=str, required=False,
                        help='input listings.txt',
                        default=os.path.join('data', 'listings.txt'))
    parser.add_argument('-o', dest='output', type=str, required=False,
                        help='output results.txt',
                        default=os.path.join('output', 'results.txt'))
    parser.add_argument("--strict", action='store_true',
                        help='use strict matching rules, matches will only be '
                        'constructed if:\n - listing title explicitly contains'
                        ' the product manufacturer\n - product manufacturer na'
                        'mes are longer than {0} characters'.format(
                            MIN_MANU_LEN))

    args = vars(parser.parse_args(sys.argv[1:]))

    # parse the files to lists of dictionaries
    products = parse_json(file_path=args['products'],
                          sanitize_keys=['manufacturer', 'model'])
    listings = parse_json(file_path=args['listings'],
                          sanitize_keys=['title', 'manufacturer'])
    num_listings = len(listings)

    # parse the JSON products from the products.txt into hashed results
    product_hash, unhashed_products = hash_products(
                                                products=products,
                                                min_manu_len=MIN_MANU_LEN,
                                                min_model_len=MIN_MODEL_LEN,
                                                strict=args['strict'])

    # match the listings to the product hash * modifies listings *
    results = match_listings(product_hash=product_hash,
                             strict=args['strict'],
                             listings=listings)

    # @TODO filter listings for which tdif cosine similarity is low..languages?
    # @TODO dump listings for which cost difference is an outlier

    # print out some metrics
    print("using {0:.1f}% of products\n"
          "matched {1:.1f}% of listings to products".format(
            (len(products) - len(unhashed_products))/len(products) * 100,
            (num_listings-len(results['unknown']['listings'])) / num_listings
            * 100))

    # dump the results
    writeout_results(results=results,
                     results_output_path=args['output'],
                     unhashed_products=unhashed_products,
                     unhashed_products_json_path=UNHASHED_PRODUCTS_JSON,
                     unmatched_listing_json_path=UMMATCHED_LISTINGS_JSON)
