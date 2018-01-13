# -*- coding: utf-8 -*-
import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import pickle, numpy

from autosarkasmus.preprocessor.pipeline import Pipeline

data = []
for is_sarcastic in [True, False]:
    break
    print('preprocessing samples with sarcastic='+str(is_sarcastic)+'...')
    # preprocess tweets
    if is_sarcastic:
        pipeline = Pipeline('../corpus/txt/reviewed_corpus_files/tweets_pos_3099random.txt', '../rsrc/de-tiger.map', verbose=True)
    else:
        pipeline = Pipeline('../corpus/txt/reviewed_corpus_files/tweets_not-pos_3099random.txt', '../rsrc/de-tiger.map', verbose=True)
    tweets_tkn, tweets_proc = pipeline.process()
    for tweet_proc in tweets_proc:
        data.append(
            {
                'tweet': tweet_proc,
                'class': is_sarcastic
            }
        )
data = pickle.load(open('../rsrc/tweets_proc_debug.pkl', 'rb'), encoding='bytes')
# pickle.dump(data, open('../rsrc/tweets_proc_debug.pkl', 'wb'))

embeddings = pickle.load(open('../rsrc/polyglot-de-dict.pkl', 'rb'), encoding='bytes')

total = 0
oov = 0
vocab = set()
for d in data:
    for w in d['tweet']:
        if w[0] not in embeddings:
            oov += 1
        vocab.add(w[0])
        total += 1

oov_vocab = 0
for v in vocab:
    if v not in embeddings:
        oov_vocab += 1

print("- vocab")
print("oov:", oov_vocab, "of", len(vocab))
print(oov_vocab/len(vocab), "%")
print("- total")
print("oov:", oov, "of", total)
print(oov/total, "%")
