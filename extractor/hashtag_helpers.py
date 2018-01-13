# -*- coding: utf-8 -*-
'''
Hashtag Helpers (functions)

Functions that help with hashtags.
'''

from autosarkasmus.extractor.unihash_helpers import load_hashtag

HASHTAG_FILE = '../rsrc/hashtags.txt'

def load_hashtags():
    '''Load the hashtags from the file and return them as a list'''
    res = []
    with open(HASHTAG_FILE, 'r', encoding='utf8') as fop:
        for line in fop:
                res.append('hashtag-' + line.strip().lower().replace('#',''))
    res = sorted(res)
    return res

def load_hashtags_from_corpus(corpus_file):
    '''Load dynamically hashtags from a given corpus'''
    return load_hashtag(corpus_file)
