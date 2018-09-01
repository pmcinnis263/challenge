# Matching Challenge

Task details on challenge [blog post](https://www.sortable.com/coding-challenge).

## Run the Solution
`python3 run.py`

* `python3` is required due to use of built-in string translation method
* No additional packages are required

## Approach

I tried a couple approaches, first a `KMeans` clustering algorithm, and then a simpler (but more robust) `hashing` method. 

The `hashing` approach is what has been retained for use with `run.py`, but I left the the generally useful KMeans text clustering class I wrote in `source/cluster.py` (using this this requires you `pip3 install -r source/kmeans_requirements.txt`). 



### KMeans
`sci-kit` learn is packed with tools for analyzing data, so I started looking at what tools were available to solve this kind of 'matching' problem.

* According to the [sklearn algorithm cheatsheet](http://scikit-learn.org/stable/tutorial/machine_learning_map/index.html), this problem fits into the path of: `categorization` --> `un-labelled data` --> `known # categories` (products) --> `>10k samples` - which means that [`KMeans`](http://scikit-learn.org/stable/modules/clustering.html#k-means) clustering is recommended.

	>The KMeans algorithm clusters data by trying to separate samples in n groups of equal variance, minimizing a criterion known as the inertia or within-cluster sum-of-squares.

* Existing text analysis and comparison work pointed me towards clustering `Listings` by text contents using a [TF-IDF feature](https://pythonprogramminglanguage.com/kmeans-text-clustering/) of the `title` field

##### Upsides:
* can reduce the search-size of an even greater number of more varied listings (i.e not just imaging products as provided)
* model converges well on listing `title` data
* can estimate similarity between listings even if the similarity would be complex to express via direct string operations

##### Downsides:
* `~80%` of the top `15` words in each cluster centroid do not contain desired manufacturer or model keywords, making it challenging to associate products to clusters
* the model is sensitive to the language of the text, and with data that is mostly english, it is more challenging to produce accurate predictions for all listings. 
* it is non-trivial to cluster by text data alongside cost, date, etc.
* Products don't have enough text data to make an accurate cluster prediction to match them

##### Performance
* when clustering by the number of products, and using listing `titles` as text features, `Kmeans` is able to match `9%` of `products` to `%20` of `listings`. 
* model fitting takes approximately 10 seconds on an 8-core machine
* there are many `listings` that do not contain the `model` or `manufacturer` strings in the matched `product`.

### Hashing
Because the `product` data contains strings that should be explicitly present in associated `Listings`, I decided to try a hashing approach where I build a `dict()` keyed by `manufacturer` and `model`. 

##### Upsides:
* much faster than KMeans
* is not very language specific, since the model name and manufacturer do not change significantly across languages.
* performing operations on a dict hashed by manufacturer and model minimizes the number of comparison operations required

##### Downsides:
* hashing short `model` or `manufacturer` strings (ex: `hp`) leads to an increase in false-positive `listing`-`product` matches
* requires programmer time to develop the string comparison and sanitization 
* has many edge-cases in the formation of the product hash
* requires more assertions to function 
	
##### Performance
* the hashing approach matches `99%` of products to `87%` listings. 
* with `--strict` matching rules (*only match a product to a listing if the `model` is in the listing `title` or if the `manufacturer` matches*): `98%` of products are matched to `82%` of listings.
* runs in well-under 10 seconds on an 8-core machine

---

### Task
Generate a file full of `Result` objects which associate each known `Product` to its associated `Listing(s)`. Precision is valued over Recall, but both should be maximized. 

The `Result` should match product listings from a 3rd party retailers, e.g. `“Nikon D90 12.3MP Digital SLR Camera (Body Only)”` against a set of known products, e.g. `“Nikon D90”`. 

There are `20196` listings and `743` known products in the provided dataset.

### Objects

`Listing`:

	{'title': 'LED Flash Macro Ring Light (48 X LED) with 6 Adapter Rings for For Canon/Sony/Nikon/Sigma Lenses',
	'manufacturer': 'Neewer Electronics Accessories', 
	'currency': 'CAD', 'price': '35.99'}

`Product`:

	{'announced-date': '2010-01-06T19:00:00.000-05:00',
	 'family': 'Cyber-shot',
	 'manufacturer': 'Sony',
	 'model': 'DSC-W310',
	 'product_name': 'Sony_Cyber-shot_DSC-W310'}

`Result`:

		{"product_name": String,
		 "listings": list(Listings) }

### Caveats
* some listings will contain the titles of other listings ex: tripods/cases/batteries, which also includes a list of compatible cameras
* prices are in multiple currencies, across multiple dates
* `family` keyword is not always in `Product`
* similar products may have numerical ratings that are slightly different ex: `3.2mp` vs `3mp`
* listings are in different languages
	* 67% of `Listings` (`13454`)  appear to be in english language
	* 33% of `Listings` (`6742`) appear to be in foreign languages

* many product names are very similar:

		 'Fujifilm_FinePix_S200EXR',
		 'Fujifilm_FinePix_S2500HD',
		 'Fujifilm_FinePix_S2600HD',
		 'Fujifilm_FinePix_S2800HD',
		 'Fujifilm_FinePix_S2900HD',
