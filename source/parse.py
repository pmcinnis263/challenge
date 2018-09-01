#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Parse json and text
methods for parsing/hashing json data and sanitizing text
"""

import json
import os
import string

REMOVE_PUNCTUATION = str.maketrans('', '', string.punctuation)


def sanitize(i):
    """sanitize an input string object i
    this method removes punctuation and converts string to lowercase
    """
    # this is faster than equivilant regex
    assert(isinstance(i, str)), "cannot sanitize non-string object"
    return i.lower().translate(REMOVE_PUNCTUATION)


def parse_json(file_path, sanitize_keys=[], convert_keys=[]):
    """Parses listings file, which is one json object per line
    keys in loaded json are sanitized if passed to 'sanitize_keys'
    convert_keys maps keys : types i.e 'str' for type conversion
        ... format is [ (key1, type1), (key2, type2), .. ]
    """

    # assert file exists
    assert(os.path.exists(file_path)), \
        "file {0} not found".format(file_path)

    # load the json
    list_of_json = []
    for line in open(file_path, 'r', encoding='utf-8').readlines():
        json_line = json.loads(line)

        # add sanitized text to 'sanitized' sub-key if keys are supplied
        if sanitize_keys:
            json_line['sanitized'] = {}

            for k in sanitize_keys:
                assert(k in json_line), "{0} not found in {1}, "\
                    "cannot sanitize".format(k, file_path)
                json_line['sanitized'][k] = sanitize(json_line[k])

        # convert types key1 : str(), key2 : int(), etc...
        if convert_keys:
            for k, ty in convert_keys:
                assert(k in json_line), "{0} not found in {1}, "\
                    "cannot sanitize".format(k, file_path)
                json_line[k] = ty(json_line[k])

        list_of_json.append(json_line)

    return list_of_json


def hash_products(products, strict=False, min_model_len=2, min_manu_len=2):
    """hash products into a dict() keyed by manufacturer -> model
    - from a list of json objects read from parse_json, try to parse products
    into clean manufacturer and model names for hashing
    - passing strict will disallow using 'family' names to make a valid model
    - rejects model names less than min_model_len
    - rejects manufacturer names less thatn min_manu_len
    - rejected products are returned as a list of unhashed_products

    returns a product hash dict and unhashed products
    """

    results = {}
    unhashed_products = []

    for p in products:
        manu = p['sanitized']['manufacturer']
        model = p['sanitized']['model']

        # try to expand any models that are too short:
        if model and len(model) <= min_model_len and 'family' in p and \
           not strict:
            # lets try and make this into a valid model name by using family
            model = sanitize(p['family']) + model

        # only allow models that parsed to a string of more than a single char:
        if len(manu) > min_manu_len and len(model) > min_model_len:
            if manu not in results:
                # add the manufacturer to our results, support unknown listings
                results[manu] = {'unknown': {'listings': []}}

            # substring search for duplication eg. 'cl30' vs 'cl30 clik'
            model_exists = False
            for existing_model in results[manu]:
                if model in existing_model:
                    model_exists = True
                    break

            # it's a new model for this manufacturer
            if not model_exists:
                # make sure the model is a contiguous keyword
                split_model = model.split()

                if len(split_model) > 1:
                    # try to take the portion of the model name that has #'s:
                    for word in split_model:
                        if len(word) > min_model_len:
                            if any(char.isdigit() for char in word):
                                model = word
                                break

                # unknown is protected keyword
                assert(manu != 'unknown'), "cannot hash 'unknown' manufacturer"
                assert(model != 'unknown'), "cannot hash 'unknown' model"

                results[manu].update({model: {'product': p, 'listings': []}})
        else:
            # we can't use this listing
            unhashed_products.append(p)

    return results, unhashed_products


def writeout_results(results, results_output_path,
                     unhashed_products, unhashed_products_json_path,
                     outlier_listings, outlier_listings_json_path,
                     unmatched_listing_json_path):
    """save a hashed result dict() into results format file
    - dumps unhashed products list() to unhashed_products_json_path
    - dumps un-matched listings in results to unmatched_listing_json_path
    - dumps cost outlier listings to outlier_listings_json_path
    """

    # write out un-hashed products to a json
    if unhashed_products:
        print("\033[91munable to hash {0} products\033[0m".format(
              len(unhashed_products)))
        json.dump(unhashed_products, open(unhashed_products_json_path, 'w'),
                  indent=4, ensure_ascii=False)

    # dump listings for which the listing could not be matched to a product
    unmatched_models = 0

    if 'unknown' in results:
        unmatched = results.pop('unknown')['listings']

    for manu in results:
        if 'unknown' in results[manu]:
            unmatched_models += len(results[manu]['unknown'])
            unmatched.append(results[manu].pop('unknown'))

    if unmatched:
        json.dump(unmatched, open(unmatched_listing_json_path, 'w'),
                  indent=4, ensure_ascii=False)

    # dump listings which are cost outliers
    if outlier_listings:
        json.dump(outlier_listings, open(outlier_listings_json_path, 'w'),
                  indent=4, ensure_ascii=False)

    print("\033[91munable to match {0} listings to a product manufacturer\n"
          "unable to match {1} listings to a product manufacturer & model"
          " model\nremoved {2} matched, cost-outlier listings\033[0m".format(
            len(unmatched), unmatched_models, len(outlier_listings)))

    # finally, write out the results dict in the format specified
    with open(results_output_path, 'wt') as outf:
        for manu in results:
            for model in results[manu]:
                if model == 'unknown':
                    continue
                outf.write(json.dumps({"product_name":
                           results[manu][model]['product']['product_name'],
                           "listings": results[manu][model]['listings']},
                           ensure_ascii=False) + "\n")

        # write out the products we didn't hash with empty lists in output
        for p in unhashed_products:
            outf.write(json.dumps({
                "product_name": p['product_name'],
                "listings": []}, ensure_ascii=False) + "\n")
