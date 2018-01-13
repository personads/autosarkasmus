# -*- coding: utf-8 -*-
'''
Tagger (class)

Wrapper class for TreeTagger with mapping
'''

import treetaggerwrapper
import re

TREETAGGER_PATH = '/resources/processors/tagger/tree-tagger-3.2'

class Tagger:
    '''
    Wrapper class for TreeTagger that performs mapping
    '''

    def __init__(self, mapping_file):
        '''
        Constructor of Tagger

        The mapping file should be tab-separated tag -> map.
        One mapping per line.

        Keyword arguments:
            mapping_file (str): path to mapping file
        '''
        self.mapping = {}
        for line in open(mapping_file):
            args = line.split() # split tags and mapping at whitespace
            self.mapping[args[0]] = args[1] # save mapping internally
        self.tree_tagger = treetaggerwrapper.TreeTagger(TAGDIR=TREETAGGER_PATH, TAGLANG='de', TAGINENC='utf8') # initialize a TreeTagger wrapper

    def tag(self, tweet_tkn):
        '''
        Performs tagging for tokenized tweet

        Keyword arguments:
            tweet_tkn (list): tokenized (optionally normalized) tweet

        Returns:
            list: of token, tag tuples
        '''
        res = []
        tagged_sentence = self.tree_tagger.tag_text('\n'.join(tweet_tkn), tagonly=True) # join tokens to string with one token per line; set tagger to perform no additional normalization
        for tagged_token in tagged_sentence:
            tagged_token_parts = tagged_token.split('\t')
            special_match = re.match(r'%(.+?)%', tagged_token_parts[0]) # check for special tokens (e.g. %HASHTAG%)
            if special_match:
                res.append((tagged_token_parts[0], special_match.group(1))) # set special tags accordingly
            else:
                res.append((tagged_token_parts[0], self.apply_map(tagged_token_parts[1]))) # set mapped tags
        return res

    def apply_map(self, tag):
        '''
        Applies mapping given a tag

        Keyword arguments:
            tag (str): pos-tag to be mapped
        '''
        return self.mapping.get(tag, 'X') # return mapping or X for unknown
