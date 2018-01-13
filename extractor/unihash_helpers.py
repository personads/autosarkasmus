# -*- coding: utf-8 -*-
'''
Unigram and Hashtag Extraction Helper (functions)

Functions that help with extracting frequent hashtags and unigrams

'''
import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from autosarkasmus.corpus.corpus_reader import CorpusReader
from autosarkasmus.preprocessor.tokenizer.tokenizer import Tokenizer

UNIHASH_CORPUS_FILE = '../corpus/txt/devset/dev_positives_samples.txt'
UNIHASH_STOPWORDS_FILE = '../rsrc/german-stopwords.txt'

def get_unihash(corpusfile=UNIHASH_CORPUS_FILE):
    '''load stopwords'''
    stopwords = []
    if corpusfile:
        with open(UNIHASH_STOPWORDS_FILE, "r") as f:
            for line in f:
                line = line.strip()
                stopwords.append(line)

    # count
    unigram_counts = {}
    hashtag_counts = {}
    cr = CorpusReader(corpusfile)
    tkn = Tokenizer()
    for tweet in cr.text_txt():
        for token in tkn.tokenize(tweet):
            if token.startswith('#') and len(token) > 1:
                hashtag_counts.setdefault(token.lower(), 0)
                hashtag_counts[token.lower()] += 1
            else:
                # Filter stopwords
                if token.lower() not in stopwords and 'http' not in token and '@' not in token and len(token) > 1:
                    unigram_counts.setdefault(token.lower(), 0)
                    unigram_counts[token.lower()] += 1

    # sort and remove special words. Only select unigranms, which occur at least 3 times.
    frequent_unigrams = [item for item in sorted(list(unigram_counts.items()), key=lambda item : item[1], reverse=True) if item[1] > 2 and "esc" not in item[0] and "eurovision" not in item[0] and "bpw" not in item[0] and "euro2016" not in item[0]]
    # sort and remove special words. Only select hashtags, which occur at least 4 times.
    frequent_hashtags = [item for item in sorted(list(hashtag_counts.items()), key=lambda item : item[1], reverse=True) if item[1] > 3 and "esc" not in item[0] and "eurovision" not in item[0] and "bpw" not in item[0] and "euro2016" not in item[0] and "pokemongo" not in item[0] and "gerita"  not in item[0] and "brexit" not in item[0] and "gerfra" not in item[0] and "em2016" not in item[0]]
    return frequent_unigrams, frequent_hashtags

def load_unigram(corpus_file):
    '''load the unigrams from a given corpus file'''
    unigrams = get_unihash(corpus_file)[0]
    res = []
    for unigram in unigrams:
        res.append('unigram-' + unigram[0])
    res = sorted(res)
    return res
    
def load_hashtag(corpus_file):
    '''load the hashtags from a given corpus'''
    hashtags = get_unihash(corpus_file)[1]
    res = []
    for hashtag in hashtags:
        res.append('hashtag-' + hashtag[0].strip().lower().replace('#',''))
    res = sorted(res)
    return res
