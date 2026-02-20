from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import pickle
import random
import math
import os
import asyncio

# Run Command
# C:\Python314\python.exe -m uvicorn main:app --reload --port 8000

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

def decode(encoded):
    EOS = '\uE001'
    EOP = '\uE002'
    EOT = '\uE003'
    string = ''.join(encoded)
    string = string.replace(EOS, '۔')
    string = string.replace(EOP, '\n\n')
    string = string.replace(EOT, '')
    return string

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

    if recent_tokens:
        for token in probabilities.keys():
            count = recent_tokens.count(token)
            if count > 0:
                penalty = 0.5 ** count
                probabilities[token] *= penalty

    tokens = list(probabilities.keys())
    probs = list(probabilities.values())

    if temperature != 1.0:
        max_prob = max(probs)
        probs = [math.exp((math.log(p) - math.log(max_prob)) / temperature) for p in probs]

    total = sum(probs)
    if total == 0:
        return random.choice(tokens)

    probs = [p / total for p in probs]
    return random.choices(tokens, weights=probs, k=1)[0]


# Load models
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, 'BPE.pkl'), 'rb') as f:
    BPE = pickle.load(f)
with open(os.path.join(BASE_DIR, 'trigram_model.pkl'), 'rb') as f:
    trigram = pickle.load(f)

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class GenerateRequest(BaseModel):
    prefix: str
    max_length: int = 500


@app.post("/generate")
def generate(req: GenerateRequest):
    story = storygeneration(req.prefix, trigram, BPE, story_length=req.max_length)
    return {"story": story}


@app.post("/generate-stream")
async def generate_stream(req: GenerateRequest):
    # ✅ KEY FIX: async generator so FastAPI flushes each token immediately
    async def stream_story():
        EOT = '\uE003'
        encoded_test = encode(BPE, req.prefix)

        if len(encoded_test) == 0:
            yield "Error: Empty input"
            return
        elif len(encoded_test) == 1:
            w3 = ""
            w2 = encoded_test[0]
        else:
            w3, w2 = encoded_test[-2:]

        # Yield the prefix first
        yield req.prefix

        recent_tokens = []
        count = 0
        w1 = ""

        while EOT not in w1 and count < req.max_length:
            # Run the CPU-bound prediction in a thread so event loop stays free
            w1 = await asyncio.get_event_loop().run_in_executor(
                None,
                predict_next_token,
                BPE['vocab'],
                w3,
                w2,
                trigram,
                0.8,
                recent_tokens[-5:]
            )

            if w1 == "":
                break

            if EOT not in w1:
                # ✅ Replace special tokens before sending to client
                token_out = w1.replace('\uE001', '۔').replace('\uE002', '\n\n')
                yield token_out
                await asyncio.sleep(0)  # ✅ yield control so response is flushed

            recent_tokens.append(w1)
            w3 = w2
            w2 = w1
            count += 1

    return StreamingResponse(
        stream_story(),
        media_type="text/plain; charset=utf-8",
        headers={
            "X-Accel-Buffering": "no",   # ✅ disables Nginx buffering
            "Cache-Control": "no-cache", # ✅ prevents proxy caching
        }
    )


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