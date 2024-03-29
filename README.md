This code generates shingles, the boolean characterisitic matrix between all documents and shingles, and generates minhash signatures using these. 

# Installation Instructions

First, begin by running the file `minhash.py`. This file will create the `minhash_signature` and place it in a Python Pickle file of the same name. Intermediate steps will generate pickle files `all_shingles` and `boolean_matrix`. The command line arguments to be passed can be seen in the help message. This file expects the stemmed songs dataset to be passed to it as a comman line argument containing the location of the CSV file. The CSV file must have column names in the first line, and the column called `'text'` will be assumed to be the lyric of the song. 

```
>>> python3 minhash.py -h

	usage: minhash.py [-h] dataset

	Make shingles, and create boolean matrix for given dataset.

	positional arguments:
	  dataset

	optional arguments:
	  -h, --help  show this help message and exit
```

The working of this code can be tweaked by altering these variables, which are also present in the code file:
```
SHINGLE_LENGTH: number of characters in a shingle
REMOVE_SPACES: should spaces be removed while processing text?
PRINT_FREQUENCY: once in how many documents should print statement be triggered
NUM_HASHES: number of hash functions to use
USE_PARTIAL_DATASET: create search function on only a part of the dataset
NUM_DOCS: number of songs to consider, if you're working on the partial dataset

To find similar songs, run the `lsh.py`.
