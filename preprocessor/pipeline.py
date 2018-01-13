# -*- coding: utf-8 -*-
'''Preprocessing Pipeline (class)

A wrapper class for twitter data preprocessing.
'''

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from autosarkasmus.corpus.corpus_reader import CorpusReader
from autosarkasmus.preprocessor.tokenizer.tokenizer import Tokenizer
from autosarkasmus.preprocessor.normalizer.normalizer import Normalizer
from autosarkasmus.preprocessor.tagger.tagger_m import Tagger


class Pipeline:
    '''
    A wrapper class for twitter data preprocessing

    Performs tokenization, normalization and pos-tagging of tweet corpora or independent tweets.
    '''

    def __init__(self, corpus_path, tagger_mapping_path, json_corpus=False, verbose=False):
        '''
        Constructor of Pipeline

        Keyword arguments:
            corpus_path (str): path to corpus file required for normalizer training and optional processing
            tagger_mapping_path (str): path to mapping file for pos-tagger
            json_corpus (bool): denotes whether corpus is in json format (default=True)
        '''
        self.corpus_path = corpus_path
        self.tokenizer = Tokenizer()
        self.normalizer = None # normalizer is not initialized until needed
        self.tagger = Tagger(tagger_mapping_path)
        self.json_corpus = json_corpus
        self.verbose = verbose

    def _initialize_normalizer(self):
        '''
        Initialization of Normalizer

        Since the normalizer requires training data, it is only initialized shortly before it is needed.
        This is only required once.
        '''
        normalizer = Normalizer()
        corpus = CorpusReader(self.corpus_path)
        corpus_iter = corpus.text_json() if self.json_corpus else corpus.text_txt()
        for tweet in corpus_iter:
            tweet_tkn = self.tokenize(tweet)
            data = normalizer.get_contexts(tweet_tkn)
            for (token, context) in data:
                normalizer.collect_bigrams(token, context) # train on token_bigrams in corpus
        self.normalizer = normalizer

    def tokenize(self, tweet_raw):
        '''
        Tokenizes a raw tweet

        Keyword arguments:
            tweet_raw (str): raw tweet string

        Returns:
            list: tokenized tweet with one element per token
        '''
        return self.tokenizer.tokenize(tweet_raw)

    def normalize(self, tweet_tkn):
        '''
        Normalizes a tokenized tweet

        Keyword arguments:
            tweet_tkn (list): tokenized tweet

        Returns:
            list: of normalized tokens
        '''
        res = []
        if self.normalizer is None:
            self._initialize_normalizer()
        contexts = self.normalizer.get_contexts(tweet_tkn) # get context
        for token, context in contexts:
            normalized = self.normalizer.normalize(token, context) # normalize given token and its context
            if token.startswith('#'):
                res.append('%HASHTAG%') # append %HASHTAG% indicator before hashtag content
            res.append(normalized)
        return res

    def tag(self, tweet_norm):
        '''
        POS-tag a normalized tweet

        Keyword arguments:
            tweet_norm (list): normalized tweet

        Returns:
            list: of tagged and normalized tokens (e.g. [('Deutsche', 'ADJ'), ('Bahn', 'NOUN')])
        '''
        return self.tagger.tag(tweet_norm)

    def process_tweet(self, tweet_raw):
        '''
        Process a single tweet

        Keyword arguments:
            tweet_raw (str): raw tweet string

        Returns:
            tuple: tokenized tweet, normalized/tagged tweet
        '''
        tweet_tkn = self.tokenize(tweet_raw)
        tweet_norm = self.normalize(tweet_tkn)
        tweet_tag = self.tag(tweet_norm)
        return tweet_tkn, tweet_tag

    def process(self):
        '''
        Process the entire given corpus

        Returns:
            tuple: list of tokenized tweets, list of their normalized and tagged counterparts
        '''
        res_tkn = []
        res_proc = []
        corpus = CorpusReader(self.corpus_path)
        corpus_iter = corpus.text_json() if self.json_corpus else corpus.text_txt() # check for corpus type
        for tweet_i, tweet_raw in enumerate(corpus_iter):
            if self.verbose:
                sys.stdout.write('\rtweet: %d of %d' % (tweet_i+1, len(corpus_iter)))
                sys.stdout.flush()
            tweet_tkn, tweet_proc = self.process_tweet(tweet_raw)
            res_tkn.append(tweet_tkn)
            res_proc.append(tweet_proc)
        if self.verbose: sys.stdout.write('\rpreprocessing complete (%d tweets)'%(len(corpus_iter)) + (' ' * len(str(len(corpus_iter))) + '\n'))
        return res_tkn, res_proc

    def write_file(self, tweets_proc, path):
        '''
        Writes tweets to file

        Supports tokenized, normalized and tagged tweets.
        One token (optionally with tag) per line.

        Keyword arguments:
            tweets_proc (list): contains processed tweets
            path (str): path to output file
        '''
        with open(path, 'w', encoding='utf8') as fop:
            for tweet_proc in tweets_proc:
                for token_proc in tweet_proc:
                    # check if tagged
                    if type(token_proc) is tuple:
                        fop.write(token_proc[0] + '\t' + token_proc[1] + '\n') # tab-separate token and tag
                    else:
                        fop.write(token_proc + '\n')
                fop.write('\n')

    def load_file(self, path):
        '''
        Loads processed tweets from file.

        Keyword arguments:
            path (str): to input file

        Returns:
            list: of tokenized, normalized and/or tagged tweets
        '''
        res = []
        with open(path, 'r', encoding='utf8') as fop:
            cur_tweet = []
            for line in fop:
                if line.startswith('#'): # ignore comments
                    continue
                line_parts = [part.trim() for part in line.split('\t')]
                if len(line_parts) == 1: # line contains only token
                    if line_parts[0] == '\n':
                        res.append(cur_tweet)
                        cur_tweet = []
                    else:
                        cur_tweet.append(line_parts[0])
                elif len(line_parts) == 2: # line also contains tags
                    cur_tweet.append((line_parts[0], line_parts[1]))
        return res
