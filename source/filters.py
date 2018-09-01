#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Filters
filters for working with manufacturer : model hashes
"""

import arrow
import statistics
from currency_converter import CurrencyConverter

def cost_filter(products_hash, n_stdevs=2, base_currency='USD'):
    """filter to remove outlier cost listings from products_hash dict()
    this requires re-visiting each listing 3 times
    - base_currency is what all costs will be converted & compared with
    - n_stdevs is how many standard deviations away from median to filter

    removes cost outliers from products_hash
    returns a list of removed outlier listings
    """

    # try to get the best currency conversion, but fallback if data missing
    # @TODO need a solution which has older data, or exclude fallback calcs
    # ...from removal?
    conv = CurrencyConverter(fallback_on_missing_rate=True,
                             fallback_on_wrong_date=True)

    removed_listings = []

    for manu in products_hash:

        # don't run for un-matched listings
        if manu == 'unknown':
            continue

        for model in products_hash[manu]:
            # make a median cost from the listings

            # don't run for un-matched listings
            if model == 'unknown':
                continue

            # don't run for empty listings
            if len(products_hash[manu][model]['listings']) < 2:
                continue

            # get the date of the product for currency conversion
            date = arrow.get(products_hash[manu][model]['product']\
                             ['announced-date']).datetime

            # convert costs to same time and currency
            costs = []
            for l in products_hash[manu][model]['listings']:
                costs.append(conv.convert(l['price'],
                             l['currency'], base_currency, date))

            # calculate the limits
            median = statistics.median(costs)
            stdev = statistics.stdev(costs)
            max_cost = median + stdev * n_stdevs
            min_cost = median - stdev * n_stdevs

            # identify outlier listings
            pop_list = []
            for i, (cost, l) in enumerate(zip(costs,
                products_hash[manu][model]['listings'])):
                if l['price'] > max_cost or l['price'] < min_cost:
                    pop_list.append(i)

            # pop outlier listings from hashed list
            if pop_list:
                pop_list.sort(reverse=True)
                for i in pop_list:
                    removed_listings.append(
                        products_hash[manu][model]['listings'].pop(i))

    return removed_listings
