# Matching Challenge

[link](https://www.sortable.com/coding-challenge)

#### Task
Generate a file full of `Result` objects which associate each known `Product` to its associated `Listing(s)`. Precision is valued over Recall, but both should be maximized. 

The `Result` should match product listings from a 3rd party retailers, e.g. `“Nikon D90 12.3MP Digital SLR Camera (Body Only)”` against a set of known products, e.g. `“Nikon D90”`. 

There are `20196` listings and `743` known products in the provided dataset.


#### Objects

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

#### Caveats
* some listings will contain the titles of other listings ex: tripods/cases listing camera compatibility
* prices are in multiple currencies, across multiple dates
		
#### Research / Thoughts
* According to the [sklearn algorithm cheatsheet](http://scikit-learn.org/stable/tutorial/machine_learning_map/index.html), this problem fits into the path of categorization --> un-labelled data --> known # categories --> >10k samples which means I should probably try using [`KMeans`](http://scikit-learn.org/stable/modules/clustering.html#k-means) clustering.

	>The KMeans algorithm clusters data by trying to separate samples in n groups of equal variance, minimizing a criterion known as the inertia or within-cluster sum-of-squares.

* cluster `Listings` by:
	* text content [TF-IDF feature](https://pythonprogramminglanguage.com/kmeans-text-clustering/)
		* should cluster the title of the listing and the manufacturer
	* price
* need to find a way to cluster by different metrics 
* match clusters of `Listings` to a `Product` by:
	* percentage match of top N clustered keywords
	* ...

#### Prerequisites
1. Download the product and listings data:

	`wget https://s3.amazonaws.com/sortable-public/challenge/challenge_data_20110429.tar.gz data/`
1. You must have `python 3`
1. Install requirements `pip3 install -r requirements.txt`

#### Running
1. execute `python3 -m run.py`
