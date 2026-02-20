import random
import math
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
    data = list(dataset)
    for pair in BPE['merges']:
        data = replace_data(data, pair)

    return data

def decode(encoded ):
    return ''.join(encoded)


def predict_next_token(vocab, w3, w2, trigram_model, temperature=0.8, recent_tokens=None):

    probabilities = {}
    
    for w1 in vocab.keys():
        P = 0
        
        if w3 != "":
            trigram_count = trigram_model['trigram'].get((w3, w2, w1), 0)
            bigram_count = trigram_model['bigram'].get((w3, w2), 0)
            if bigram_count > 0:
                P += trigram_model['lembda1'] * (trigram_count / bigram_count)
        
        bigram_count = trigram_model['bigram'].get((w2, w1), 0)
        unigram_w2 = trigram_model['unigram'].get(w2, 0)
        if unigram_w2 > 0:
            P += trigram_model['lembda2'] * (bigram_count / unigram_w2)
        
        unigram_w1 = trigram_model['unigram'].get(w1, 0)
        P += trigram_model['lembda3'] * (unigram_w1 / trigram_model['corpus_size'])
        
        if P > 0:
            probabilities[w1] = P
    
    if not probabilities:
        return ""
    
    # repetition penalty
    if recent_tokens:
        for token in probabilities.keys():

            count = recent_tokens.count(token)
            if count > 0:
                penalty = 0.5 ** count
                probabilities[token] *= penalty
    
    tokens = list(probabilities.keys())
    probs = list(probabilities.values())
    
    # Weighted Random Sampling
    
    if temperature != 1.0:
        max_prob = max(probs)
        probs = [math.exp((math.log(p) - math.log(max_prob)) / temperature) for p in probs]
    
    total = sum(probs)
    if total == 0:
        return random.choice(tokens)
    
    probs = [p / total for p in probs]
    
    return random.choices(tokens, weights=probs, k=1)[0]


def storygeneration(test_string, trigram_model, BPE, story_length=1000, temperature=0.8):

    EOT = '\uE003'
    
    encoded_test = encode(BPE, test_string)
    
    if len(encoded_test) == 0:
        return "Error: Empty input"
    elif len(encoded_test) == 1:
        w3 = ""
        w2 = encoded_test[0]
    else:
        w3, w2 = encoded_test[-2:]
    
    recent_tokens = []
    
    count = 0
    w1 = ""
    
    while EOT not in w1 and count < story_length:
        w1 = predict_next_token(
            BPE['vocab'], 
            w3, 
            w2, 
            trigram_model,
            temperature=temperature,
            recent_tokens=recent_tokens[-5:]  
        )
        
        if w1 == "":
            break
        
        encoded_test.append(w1)
        recent_tokens.append(w1)
        
        w3 = w2
        w2 = w1
        count += 1
    
    return decode(encoded_test)


with open('BPE.pkl', 'rb') as f:
    BPE = pickle.load(f)
    
with open('trigram_model.pkl', 'rb') as f:
    trigram = pickle.load(f)
    
prompt = "اپنے بادشاہ کی وفادار تھی"
story = storygeneration(prompt, trigram, BPE)
print(story)