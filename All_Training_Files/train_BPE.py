import numpy as np
import pandas as pd
import pickle

def get_most_frequent_pair(data):
    dict = {}

    for i in range(len(data)-1):
        pair = (data[i], data[i+1])

        if pair not in dict.keys():

            dict[pair] = 1
        else:
            dict[pair] += 1
    
    max_ind = np.argmax(np.array(dict.values()))
    return list(dict.keys())[max_ind]

def replace_data(data, pair):
    updated_data = []
    i = 0
    
    while i < len(data):  

        if i < len(data) - 1 and (data[i], data[i+1]) == pair:
            updated_data.append(data[i] + data[i+1])
            i += 2  
        else:
            updated_data.append(data[i])
            i += 1  
    
    return updated_data

def train_BPE(dataset, VOCAB_SIZE):

    data = list(dataset)
    characters = set()
    for c in data:
        characters.update(c)

    vocab = {}

    i = 0
    for ch in characters:
        vocab[ch] = i
        i+=1

    vocab_size = len(characters)
    merges = []

    while vocab_size < VOCAB_SIZE:

        print (f'vocab_size: {vocab_size}')
        mf_pair = get_most_frequent_pair(data)
        merges.append(mf_pair)
        vocab[mf_pair[0] + mf_pair[1]] = vocab_size
        vocab_size+=1
        data = replace_data(data, mf_pair)

    return vocab, merges

def save_BPE(vocab, merges, vocab_size, file_name):
    with open(file_name, 'wb') as file:
        pickle.dump({'vocab': vocab, 'merges': merges, 'vocab_size': vocab_size}, file)

def train_test_split(data):
    N = len(data)
    train_n = N//100*85

    return data[:train_n], data[train_n:]


dataset = pd.read_csv("corpus.csv")
train , test = train_test_split(dataset)

train_data = ""
for doc in train['Stories']:
    train_data = train_data + doc

vocab_size = 250
vocab, merges = train_BPE(train_data, vocab_size)
save_BPE(vocab, merges, vocab_size, "BPE.pkl")