import pickle
import numpy as np
import pandas as pd

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

def encode(BPE, dataset):
    print ('encoding dataset is executing.... ... ... .. ..  .  .')

    data = list(dataset)
    for pair in BPE['merges']:
        data = replace_data(data, pair)

    return data

def decode(encoded ):
    return ''.join(encoded)


def train_test_split(data):
    N = len(data)
    train_n = N//100*85

    return data[:train_n], data[train_n:]

def get_counts(Data):

    print ('get_counts is executing.... ... ... .. ..  .  .')
    Counts = {
        "unigram" : {},
        "bigram" : {},
        "trigram" : {}
    }

    for token in Data:
        if token not in Counts['unigram'].keys():
            Counts['unigram'][token] = 1
        else:
            Counts['unigram'][token] += 1
    
    for i in range(len(Data)-1):
        bigram = (Data[i], Data[i+1])

        if bigram not in Counts['bigram'].keys():
            Counts['bigram'][bigram] = 1
        else:
            Counts['bigram'][bigram] += 1
    
    for i in range(len(Data)-2):
        trigram = (Data[i], Data[i+1], Data[i+2])

        if trigram not in Counts['trigram'].keys():
            Counts['trigram'][trigram] = 1
        else:
            Counts['trigram'][trigram] += 1
    
    return Counts

def train_lembdas(Dev_set):
    
    Ngram_Counts = get_counts(Dev_set)

    lembda1 = 0
    lembda2 = 0
    lembda3 = 0

    for w3,w2,w1 in Ngram_Counts['trigram'].keys(): # P(w1 | w3,w2) = P(w3, w2, w1) / P(w3, w2)

        P3 = Ngram_Counts['trigram'][(w3,w2,w1)] / Ngram_Counts['bigram'][(w3,w2)]
        P2 = Ngram_Counts['bigram'][(w2,w1)] / Ngram_Counts['unigram'][(w2)]
        P1 = Ngram_Counts['unigram'][(w1)] / len(Dev_set)

        if P3 >= P2 and P3 >= P1:
                # lembda1 += Ngram_Counts['trigram'][(w3,w2,w1)]
                lembda1 += 1
        elif P2 >= P1:
                # lembda2 += Ngram_Counts['bigram'][(w2,w1)]
                lembda2 += 1
        else:
                # lembda3 += Ngram_Counts['unigram'][(w1)]
                lembda3 += 1
    
    total = lembda1 + lembda2 + lembda3
    return lembda1/total, lembda2/total, lembda3/total

def train_trigram(train):

    with open('BPE.pkl', 'rb') as file:
        BPE = pickle.load(file)
        
    train_data = ""
    for doc in train['Stories']:
        train_data += doc
        
    encoded_train_data = encode(BPE, train_data)

    train_set = encoded_train_data[ :len(encoded_train_data)//100*10 ]
    DEV_set = encoded_train_data[len(encoded_train_data)//100*10 :]


    lembda1, lembda2, lembda3 = train_lembdas(DEV_set)

    Ngram_Counts = get_counts(train_set)

    return {
        
        'trigram': Ngram_Counts['trigram'],
        'bigram': Ngram_Counts['bigram'],
        'unigram': Ngram_Counts['unigram'],
        'lembda1':lembda1,
        'lembda2':lembda2,
        'lembda3':lembda3,
        'corpus_size': len(train_set)

    }
    
def save_model(model, file_name):
    with open(file_name, 'wb') as file:
        pickle.dump(model, file)

    
dataset = pd.read_csv("train_corpus.csv")
model = train_trigram(dataset)
print (model)
save_model(model, "trigram_model.pkl")