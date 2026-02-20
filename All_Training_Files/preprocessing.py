
import re
import unicodedata
import pandas as pd


def normalize_string(txt):

    ind = txt.find('\n') #remove author name
    if ind != -1 and (len(txt[:ind]) <= 100):
        txt = txt[ind+1:]

    txt = unicodedata.normalize('NFKC', txt)
    urdu_characters = r'[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF\s\d۔؟!،]'
    txt = ''.join(re.findall(urdu_characters, txt))
    txt = re.sub(r' +', ' ', txt) #remove extra spaces
    txt = re.sub(r'\n\n+', '\n\n', txt) #remove extra line breaks
    
    return txt.strip()


def add_special_characters(txt): # add EOS, EOP, EOT

    EOS = '\uE001' 
    EOP = '\uE002'  
    EOT = '\uE003'

    paragraphs = txt.split('\n\n')
    
    final_txt = []
    for p in paragraphs:
        if not p.strip():
            continue
        
        sentences = re.split(r'[۔؟!]', p)
        
        paragraph_txt = ''
        for s in sentences:
            s = s.strip()
            if s:
                paragraph_txt += s + EOS
        
        if paragraph_txt:
            final_txt.append(paragraph_txt + EOP)
    
    return ''.join(final_txt) + EOT


def preprocess(txt):

    preprocessed_txt = normalize_string(txt)
    preprocessed_txt = add_special_characters(preprocessed_txt)

    return preprocessed_txt




def built_corpus(documents, file_name):

    corpus_file = file_name + ".txt"
    with open(corpus_file, 'w', encoding='utf-8') as file:
        for doc in documents:
            file.write(doc )
    
    df = pd.DataFrame(documents, columns=['Stories'])
    df.to_csv(file_name+".csv", index=False)


dataset = pd.read_csv("stories.csv") 
documents = []
for story in dataset['content']:
    documents.append(preprocess(story))

built_corpus(documents, "corpus")
