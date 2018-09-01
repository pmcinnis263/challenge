#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""methods to perform record linkage 'matching'
"""


def match_listings(product_hash, listings, strict=False):
    """hash listings into supplied product hash dict() by manufacturer:product
    - passing strict will enforce explicit matches for manufacturers|models
    - populates product_hash dict with listings
    - listings not matched to manufacturer are returned as as 'unknown'
    - listings not matched to a manufacturer & model are keyed by 'unknown'

    populates the product hash dict() in-place
    """

    for manu in product_hash:
        pop_list = []

        for i, l in enumerate(listings):
            # perform matches to minimize string comp:

            # do the manufacturers match directly in either direction?
            match = manu in l['sanitized']['manufacturer']
            if not match and l['sanitized']['manufacturer']:
                if l['sanitized']['manufacturer'] in manu:
                    match = True

            # is the manufacturer in the title?
            if not match and manu in l['sanitized']['title'] and not strict:
                match = True
                #this is a weaker match...

            if match:
                # match the listing to a model if we can
                match_model_key = 'unknown'

                # try to find the model that the listing matches
                num_model_matches = 0
                for model in product_hash[manu]:
                    if model in l['sanitized']['title']:
                        match_model_key = model
                        num_model_matches += 1
                        break

                # we can't be sure, might be a listing containing model #'s
                if num_model_matches > 1:
                    match_model_key = 'unknown'

                # put this model into the predicted location without added data
                l.pop('sanitized')
                product_hash[manu][match_model_key]['listings'].append(l)
                pop_list.append(i)

        # pop listings from list for which the manufacturer|model was matched
        if pop_list:
            pop_list.sort(reverse=True)
            for i in pop_list:
                listings.pop(i)

    # the remaining listings are of unknown manufacturer
    product_hash['unknown'] = {'listings': listings}

    # remove modified listings object since we store it inside product hash
    del listings
