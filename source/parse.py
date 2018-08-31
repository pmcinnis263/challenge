#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Parses product and listing data
This script parses the product and listing json files into sanitized,
machine interpretable, dictionaries
"""

import json
import os

#FOREGIN_CHARS=['à', 'é']

def parse_json(file_path):
    """Parses listings file, which is one json object per line
    """

    # assert file exists
    assert(os.path.exists(file_path)), \
        "file {0} not found".format(file_path)

    # load the json
    list_of_json=[]
    for line in open(file_path, 'r', encoding='utf-8').readlines():
        list_of_json.append(json.loads(line))

    return list_of_json


def get_unique_list(l):
    # remove duplicates
    ulist = []
    [ulist.append(x) for x in l if x not in ulist]
    return ulist


def sanitize_listings_by_language(listings,
                                  english_currencies=['USD', 'CAD', 'GBP']):
    """Sanitizes the text in listing titles
       input: a list() of dict() Listings, containing 'title' & 'currency' keys
       returns: a dict() of lists() of Listings, keyed by 'english', 'foreign'
    """
    ret_listings = {'english' : [], 'foreign' : []}
    for i,l in enumerate(listings):
        # regex is ~4.5 time slower than a single .replace() call
        words = l['title'].lower().replace('/', ' ').replace('(',
                '').replace(')','').split()
        l['sanitized_text'] = ' '.join(get_unique_list(words))

        if l['currency'] in english_currencies:
            ret_listings['english'].append(l)
        else:
            ret_listings['foreign'].append(l)

    return ret_listings