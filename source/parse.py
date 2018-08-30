#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Parses product and listing data
This script parses the product and listing json files into sanitized,
machine interpretable, dictionaries
"""

import json
import os


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
