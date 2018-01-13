# -*- coding: utf-8 -*-
'''
Feature Extractor (class)
'''

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import re

from autosarkasmus.preprocessor.pipeline import Pipeline

from autosarkasmus.extractor.sentiws_helpers import load_sentiws
from autosarkasmus.extractor.cluster_helpers import cluster_map

class FeatureExtractor():
    '''
    Performs feature extraction for tweet data
    '''

    def __init__(self, features, feature_order, texts=False):
        '''
        Constructor for FeatureExtractor

        Keyword arguments:
            features (dict): features as name, value pairs (e.g. {'feature-0':'numeric', 'feature-1':['val1', 'val2']})
            feature_order (list): order of features
            texts (bool): whether the original tweets should be returned along with their features
        '''
        self.features = features
        self.feature_order = feature_order
        self.texts = texts
        self.resources = {}
        if any(feature in ['sentiment-pos', 'sentiment-neg', 'sentiment-all'] for feature in self.feature_order):
            self.resources['sentiment'] = load_sentiws() # SentiWS setup
        if any(feature.startswith('cluster-') for feature in self.feature_order):
            self.resources['clusters'] = cluster_map() # unigram cluster setup

    def extract_features_from_tweet(self, tweet_tkn, tweet_proc, is_sarcastic):
        '''
        Extracts features from a tweet

        The following features are supported:
            * capitalization (numeric)
            * extended-vocals (numeric)
            * hashtag-$HASHTAG (numeric)
            * word-length-avg (numeric)
            * unigram-$UNIGRAM (numeric)
            * cluster-$CLUSTER (numeric)
            * pos-$POSTAG (numeric)
            * intensifier-$INTENSE (numeric)
            * emoticon-pos, emoticon-neg, emoticon-all (numeric)
            * sentiment-pos, sentiment-neg, sentiment-all (numeric)
            * tweet-length (numeric)
            * ratio-noun-verb (numeric)

        Keyword arguments:
            tweet_tkn (list): tokenized raw tweet
            tweet_proc (list): preprocessed tweet
            is_sarcastic (bool): whether the tweet is sarcastic

        Returns:
            dict: the extracted features of the tweet
        '''
        res = {}
        # class
        res['class'] = is_sarcastic

        for token in tweet_tkn:
            token_low = token.lower()
            # capitalization
            if 'capitalization' in self.feature_order and re.match(r"[A-ZÄÖÜß]{2,}", token):
                res['capitalization'] = res.get('capitalization', 0) + 1
            # extended vocals
            if 'extended-vocals' in self.feature_order and re.match(r"a{3,}|e{3,}|i{3,}|o{3,}|u{3,}|ä{3,}|ö{3,}|ü{3,}", token_low):
                res['extended-vocals'] = res.get('extended-vocals', 0) + 1
            # hashtags
            if token_low.startswith('#'):
                hashtag = token_low[1:]
                if 'hashtag-'+hashtag in self.feature_order:
                    res['hashtag-'+hashtag] = res.get('hashtag-'+hashtag, 0) + 1
            # word length
            if 'word-length-avg' in self.feature_order:
                res['word-length-avg'] = res.get('word-length-avg', 0.) + (len(token)/len(tweet_tkn))

        for token, tag in tweet_proc:
            token_low = token.lower()
            tag_low = tag.lower()
            # unigrams
            if 'unigram-'+token_low in self.feature_order:
                res['unigram-'+token_low] = res.get('unigram-'+token_low, 0) + 1
            # clusters
            if any(feature.startswith('cluster-') for feature in self.feature_order):
                if token_low in self.resources['clusters']:
                    if 'cluster-'+str(self.resources['clusters'][token_low]) in self.feature_order:
                        res['cluster-'+str(self.resources['clusters'][token_low])] = res.get('cluster-'+str(self.resources['clusters'][token_low]), 0) + 1
            # pos
            if 'pos-'+tag_low in self.feature_order:
                res['pos-'+tag_low] = res.get('pos-'+tag_low, 0) + 1
            # intensifiers
            if 'intensifier-'+token_low in self.feature_order:
                res['intensifier-'+token_low] = res.get('intensifier-'+token_low, 0) + 1
            # emoticons
            if 'emoticon-pos' in self.feature_order and token_low == '%smiley-pos%':
                res['emoticon-pos'] = res.get('emoticon-pos', 0) + 1
            if 'emoticon-neg' in self.feature_order and token_low == '%smiley-neg%':
                res['emoticon-neg'] = res.get('emoticon-neg', 0) + 1
            if 'emoticon-all' in self.feature_order and re.match(r"%smiley(\-pos|\-neg)?%", token_low):
                res['emoticon-all'] = res.get('emoticon-all', 0) + 1
            # sentiment
            if any(feature in ['sentiment-pos', 'sentiment-neg', 'sentiment-all'] for feature in self.feature_order):
                sentiment_value = self.resources['sentiment'].get(token_low, 0.)
                if sentiment_value > 0:
                    res['sentiment-pos'] = res.get('sentiment-pos', 0.) + (sentiment_value/len(tweet_proc))
                if sentiment_value < 0:
                    res['sentiment-neg'] = res.get('sentiment-neg', 0.) + (sentiment_value/len(tweet_proc))
                res['sentiment-all'] = res.get('sentiment-all', 0.) + (sentiment_value/len(tweet_proc))

        # tweet length
        if 'tweet-length' in self.feature_order:
            res['tweet-length'] = len(" ".join(tweet_tkn))
        # noun to verb ratio
        if 'ratio-noun-verb' in self.feature_order:
            res['ratio-noun-verb'] = res.get('pos-noun', 1.)/res.get('pos-verb', 1.)

        # set remaining features to 0.
        for feature_key in self.feature_order:
            res[feature_key] = res.get(feature_key, 0)
        return res

    def extract_features(self, corpus_file_pos, corpus_file_neg, verbose=False):
        '''
        Extract features from positive and negative corpora

        Keyword arguments:
            corpus_file_pos (str): path to positive corpus
            corpus_file_neg (str): path to negative corpus
            verbose (bool): stdout verbosity

        Returns:
            list, tuple: list of extracted features and, depending on texts flag, the tokenized raw tweets
        '''
        res = []
        tweet_texts = []

        # extract features
        if verbose: print('extracting features...')

        for is_sarcastic in [True, False]:
            if verbose: print('   preprocessing samples with sarcastic='+str(is_sarcastic)+'...')
            # preprocess tweets
            if is_sarcastic:
                pipeline = Pipeline(corpus_file_pos, '../rsrc/de-tiger.map', verbose=verbose)
            else:
                pipeline = Pipeline(corpus_file_neg, '../rsrc/de-tiger.map', verbose=verbose)
            tweets_tkn, tweets_proc = pipeline.process()
            if verbose: print('   extracting features...')
            # extract features from tweets
            for tweet_index in range(len(tweets_tkn)):
                ext_features = self.extract_features_from_tweet(tweets_tkn[tweet_index], tweets_proc[tweet_index], is_sarcastic)
                res.append(ext_features)
            for text in tweets_tkn:
                tweet_texts.append(text)

        if self.texts:
            return res, tweet_texts
        else:
            return res
