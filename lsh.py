import numpy as np
import pandas as pd
import pickle
import time

import numpy as np
import copy
from math import sqrt
import pickle
import time

import numpy as np
from math import sqrt
import pickle
import time

def euclidian_dist(vec1,vec2, bool_matrix):
    values1 = copy.deepcopy(bool_matrix[vec1])
    values2 = copy.deepcopy(bool_matrix[vec2])
    dist = 0
    for v1 in values1:
        if v1 in values2:
            values2.remove(v1)
        else:
            dist += 1
    for element in values2:
        dist+=1
    dist = dist ** 0.5
    return dist

def hamming_dist(vec1,vec2, bool_matrix):
    values1 = copy.deepcopy(bool_matrix[vec1])
    values2 = copy.deepcopy(bool_matrix[vec2])
    dist = 0
    for v1 in values1:
        if v1 in values2:
            values2.remove(v1)
        else:
            dist+=1
    for v2 in values2:
        dist+=1
    return dist

def cosine_distance(vec1, vec2, bool_matrix):
    values1 = copy.deepcopy(bool_matrix[vec1])
    values2 = copy.deepcopy(bool_matrix[vec2])
    denominator = (len(values1) * len(values2))**0.5  
    numerator = 0
    for v1 in values1:
        if v1 in values2:
            numerator+=1.0
    return numerator/denominator

def jaccard(vec1, vec2, bool_matrix):
    values1 = copy.deepcopy(bool_matrix[vec1])
    values2 = copy.deepcopy(bool_matrix[vec2])    
    num = 0.0 # will contain intersection of sets
    for v1 in values1:
        if v1 in values2:
            num += 1.0
    den = len(values1) + len(values2) - num
    return (num/den)

def jaccard_minhash(vec1, vec2, minhash):
    sim = 0.0
    for row in minhash:
        if row[vec1] == row[vec2]:
            sim += 1.0
    return sim/len(minhash)

def getAllDistances(vec1, vec2):
    start = time.process_time()
    with open('boolean_matrix', 'rb') as datafile:
        bool_matrix = pickle.load(datafile)
    print("\t\t\t\t==== STATS ====")
    print("\t\tEuclidean Distance: ", euclidian_dist(vec1, vec2, bool_matrix))
    print("\t\tHamming Distance: ", hamming_dist(vec1, vec2, bool_matrix))
    print("\t\tCosine Distance: ", cosine_distance(vec1, vec2, bool_matrix))
    print("\t\tJaccard Similarity (actual): ", jaccard(vec1, vec2, bool_matrix))
    with open('minhash_signature', 'rb') as datafile:
        minhash_signatures = pickle.load(datafile)
    print("\t\tJaccard Similarity (MinHash): ", jaccard_minhash(vec1, vec2, minhash_signatures))
    end = time.process_time()
    return end-start

def lsh(minhash,input_doc):
    """
    inputs: the minhash matrix, and the index of the document for which similar docs need to be found
    output: a list of similar document indexes
    """
    
    b = 25
    r = 4
    
    thres = np.power(1/b, 1/r)  #threshold value
    
    
    split = np.split(minhash, b, axis = 0)  #splitting the minhash array into b bands
    #print(split[0])
    buckets = [None] * b #a list having a dictionary element for each band
    for j,band in enumerate(split):
        buckets[j] = {}  # for band j, dictionary keys are hash outputs, key value:list of document indexes giving hvalue
        for i in range(band.shape[1]):
                k = hash(tuple(band[:,i])) #key
                if k in buckets[j].keys():
                    cur_val = buckets[j].get(k)
                    cur_val.append(i)
                    buckets[j][k] = cur_val # updating values list with new found index
                else:
                    buckets[j][k] = [i] # creating new key
    
    #print(buckets[0])
    index = input_doc
    
    sim_docs = []
    
    for band_buckets_dict in buckets:
        for value_list in band_buckets_dict.values():
            if index in value_list:
                sim_docs.extend(value_list)
    
    sim_docs = set(sim_docs)
    sim_docs.remove(index)
    sim_docs = list(sim_docs)
    return sim_docs
    #print(minhash[:,sim_docs])


if __name__ == '__main__':

    minhash_file = open("minhash_signature","rb")
    minhash = pickle.load(minhash_file)
    minhash_file.close()
    df = pd.read_csv("6000_data.csv", header = 0, index_col = False)
    
    song_name = input("Enter the name of a song\n")
    if(song_name == ""): song_name="Let It Snow"
    artist_name = input("Enter the name of the artist\n")
    if(artist_name==""): artist_name="America"    
    tick = time.time()
    index_list = df.index[df['song'] == song_name]
    flag = 0
    for x in index_list:
        if df.iat[x,0] == artist_name:
                ind = x
                flag = 1
        if flag == 0:
            print("\nERROR. No such song found!\n")
            exit(0)

    list1 = lsh(minhash, ind)

    print(f"\nNumber of similar songs found: {len(list1)}")
    for i,x in enumerate(list1):
        print(f"{i+1}. Song Name: {df.iat[x,1]}")
        print(f"   Artist: {df.iat[x,0]}")      
        print(f"   Link: https://www.lyricsfreak.com{df.iat[x,2]}")
        # print(f"Lyrics: {df.iat[x,3]}")
        assert(list1[i] == x)
        print("Song Index: ", x)
        getAllDistances(ind, list1[i])
        print()
    tock = time.time()
    print("Total time taken: ", tock - tick)