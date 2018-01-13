# -*- coding: utf-8 -*-
'''
Unigram Helpers (functions)

Functions that help with unigrams.
'''
from autosarkasmus.extractor.unihash_helpers import load_unigram

UNIGRAM_FILE = '../rsrc/german-unigrams.txt'

def load_unigrams():
    '''Load unigrams from a file and return them as a list'''
    res = []
    with open(UNIGRAM_FILE, 'r', encoding='utf8') as fop:
        for line in fop:
            res.append('unigram-' + line.lower().strip())
    return res
    
def load_unigrams_from_corpus(corpus_file):
    '''Load dynamically unigrams from a given corpus '''
    return load_unigram(corpus_file)
