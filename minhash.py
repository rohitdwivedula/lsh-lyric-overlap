import argparse
import csv 
from hashlib import sha256 as sha	
import pickle																																																																	
import os
import re
import random
import numpy as np
import csv
import time

SHINGLE_LENGTH = 7 # number of characters in a shingle
REMOVE_SPACES = True # should spaces be removed while processing text?
PRINT_FREQUENCY = 75 # once in how many documents should print statement be triggered
NUM_HASHES = 100 # number of hash functions to use
USE_PARTIAL_DATASET = True # create search function on only a part of the dataset
NUM_DOCS = 6000 # number of songs to consider in the partial dataset

def remove_spaces(string):
	# remove all spaces from string
    pattern = re.compile(r'\s+') 
    return re.sub(pattern, '', string) 

def hash_word(text):
	# 32 bit hash of the given hash_word
	return (int(sha(text.encode('utf-8')).hexdigest(), 16) % 2**32)

def shingle_text(datafile):
	'''
		Create all k-shingles present across all songs
		datafile: path to csv file
		@return shingles_dict dictionary containing all the shingles and their index.
	'''
	shingles = set()
	with open(args.dataset, 'r') as datafile:
		dataReader = csv.DictReader(datafile, delimiter=',')
		j = 0
		for row in dataReader:
			j+=1
			if not j%PRINT_FREQUENCY: 
				print("[Shingle] Song " + str(j) + "  processing... # shingles:" + str(len(shingles)))
			if USE_PARTIAL_DATASET and j == NUM_DOCS: 
				break
			song_text = row['text']
			if REMOVE_SPACES:
				song_text = remove_spaces(song_text)
			for i in range(0, len(song_text) - SHINGLE_LENGTH+1):
				shingle = hash_word(song_text[i:i+SHINGLE_LENGTH])
				shingles.add(shingle)
	shingles = list(shingles)
	shingles_dict = dict()
	k = 0
	for shingle in shingles:
		shingles_dict[shingle] = k
		k+=1
	return shingles_dict

def create_boolean_matrix(datafile, shingles):
	'''
		Create a matrix which stores all occurences of all k-shingles in all songs. 
	'''
	boolean_matrix = []
	with open(args.dataset, 'r') as datafile:
		dataReader = csv.DictReader(datafile, delimiter=',')
		j = 0
		for row in dataReader:
			j+=1
			if not j%PRINT_FREQUENCY: 
				print("[Bool Matrix] Song " + str(j) + "  processing...")
			if USE_PARTIAL_DATASET and j == NUM_DOCS: 
				break
			shingles_present = set()
			song_text = row['text']
			if REMOVE_SPACES:
				song_text = remove_spaces(song_text)
			for i in range(0, len(song_text) - SHINGLE_LENGTH+1):
				shingle = song_text[i:i+SHINGLE_LENGTH]
				shingles_present.add(shingles[hash_word(shingle)])
			boolean_matrix.append(shingles_present)
	return boolean_matrix

def valueAt(mat, shingling, document):
	document_shingles = mat[document]
	if shingling in document_shingles:
		return 1
	else:
		return 0

def create_signatures(bool_matrix, shingles, num_hashes):
	'''
		bool_matrix: boolean incidence matrix of all docs, and whether each k-shingle is present in it
		num_hashes: number of hash functions to use
		shingles: list of all shingles and their indices
		num_hashes: number of hash functions to create
		@return signature matrix
	'''
	num_shingles = len(shingles)	
	num_songs = len(bool_matrix)
	base_case = list(range(0, num_shingles))
	print("Creating {} hashes...".format(num_hashes))
	if os.path.exists('hash_functions.csv'):
		with open('hash_functions.csv', "r") as permutations_file:
			permutations = list(csv.reader(permutations_file))
	else:
		permutations = set()
		while len(permutations) < num_hashes:
			print("Generating permutations: " + str(len(permutations)))
			permutations.add(tuple(np.random.permutation(num_shingles)))
		print("Created hashes OK")
		permutations = list(permutations)
		# with open("hash_functions.csv","w+") as permutations_file:
		#     csvWriter = csv.writer(permutations_file,delimiter=',')
		#     csvWriter.writerows(permutations)
		# print("Hash matrices written into memory. Rerun program to calculate signature matrix")

	signature_matrix = np.ones((num_hashes,num_songs)) * np.inf
	print("Initialized empty signature matrix. Shape: " + str(signature_matrix.shape))
	for r in range(0, num_shingles):
		if not r%PRINT_FREQUENCY: 
			print("[MinHash Sign] Current Row:" + str(r))
		for c in range(0, num_songs):
			if valueAt(bool_matrix, r, c) != 0:
				for i in range(0, num_hashes):
					try:
						signature_matrix[i][c] = min(signature_matrix[i][c], permutations[i][r])
					except IndexError as e:
						print(e)
						print(i)
						print(c)
						print(r)
						exit()
	return signature_matrix


if __name__ == "__main__":
	start_time = time.process_time()
	parser = argparse.ArgumentParser(description='Make shingles, and create boolean matrix for given dataset.')
	parser.add_argument('dataset')
	args = parser.parse_args()
	print("Attempt read from file: " + args.dataset)
	#  create dictionary of all shingles in the dataset, with shingle mapping 
	#  to the index in which it occurs in the boolean matrix
	recalculate = False 
	'''
		all_shingles -> boolean_matrix -> minhash_signature. Here, minhash_signature
		is dependent on boolean_matrix, which itself is dependent on all_shingles. 

		So, if all_shingles isn't found in the directory, all successors of all_shingles
		will be recalculated due to break in dependencies.  
	'''
	if os.path.exists('all_shingles'):
		shingles_file = open('all_shingles','rb')			
		shingles = pickle.load(shingles_file)
		shingles_file.close()
	else:
		recalculate = True
		shingles = shingle_text(args.dataset)
		shingles_file = open('all_shingles','wb')
		pickle.dump(shingles, shingles_file)
		shingles_file.close()
	print("TOTAL SHINGLES: " + str(len(shingles)))
	shingling_time = time.process_time()
	if os.path.exists('boolean_matrix') and not recalculate:
		boolean_matrix_file = open('boolean_matrix','rb')			
		boolean_matrix = pickle.load(boolean_matrix_file)
		boolean_matrix_file.close()
	else:
		recalculate = True
		boolean_matrix = create_boolean_matrix(args.dataset, shingles)
		boolean_matrix_file = open('boolean_matrix', 'wb')
		pickle.dump(boolean_matrix, boolean_matrix_file)
		boolean_matrix_file.close()
	print("TOTAL Songs: " + str(len(boolean_matrix)))
	boolean_matrix_calculation_time = time.process_time()
	if os.path.exists('minhash_signature') and not recalculate:
		minhash_signature_file = open('minhash_signature','rb')			
		minhash_signature = pickle.load(minhash_signature_file)
		minhash_signature_file.close()
	else:
		recalculate = True
		minhash_signature = create_signatures(boolean_matrix, shingles, NUM_HASHES)
		minhash_signature_file = open('minhash_signature', 'wb')
		pickle.dump(minhash_signature, minhash_signature_file)
		minhash_signature_file.close()
	minhash_signature_calculation_time = time.process_time()
	print("Minhash matrix generated: " + str(len(boolean_matrix)))
	print("===== STATISTICS =====")
	print("Time taken for:")
	print("\tShingling:\t\t", shingling_time - start_time)
	print("\tCharacteristic Matrix:  ", boolean_matrix_calculation_time - shingling_time)
	print("\tGenerate Signatures:    ", minhash_signature_calculation_time - boolean_matrix_calculation_time)
	print("Total time: ", minhash_signature_calculation_time - start_time)