# -*- coding: utf-8 -*-
'''
Feature Extractor (script)

The feature extraction for simplified baseline creation.
'''
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import argparse
import re

from autosarkasmus.preprocessor.pipeline import Pipeline

from feature_extractor import FeatureExtractor
from arff_document import ARFFDocument
from sentiws_helpers import load_sentiws
from cluster_helpers import load_clusters


def setup_features():
    '''Setup the features: clusters, POS, emoticons, sentiment, tweet-length, word-length, ratio-noun-verb, class'''
    features = {}
    feature_order = []
    # Unigrams from clusters
    feature_order += load_clusters()
    feature_order += [
        # POS-Tags
        'pos-.', 'pos-adj', 'pos-adv', 'pos-conj', 'pos-det', 'pos-noun', 'pos-num', 'pos-pron', 'pos-prt', 'pos-verb', 'pos-x', 'pos-hashtag', 'pos-mention', 'pos-url',
        # emoticons
        'emoticon-pos',
        'emoticon-neg',
        'emoticon-all',
        # sentiment
        'sentiment-pos',
        'sentiment-neg',
        'sentiment-all',
        # surface features
        'tweet-length',
        'word-length-avg',
        'ratio-noun-verb',
        # class
        'class'
    ]

    for feature_key in feature_order:
        if feature_key == 'class':
            features[feature_key] = set(['sarcastic', 'non-sarcastic'])
        else:
            features[feature_key] = 'numeric'

    return features, feature_order

if __name__ == '__main__':
    # argument parsing
    arg_parser = argparse.ArgumentParser(description='Feature Extraction for the Autosarkasmus Baseline')
    arg_parser.add_argument('corpus_file_pos', help='path to the positive corpus file')
    arg_parser.add_argument('corpus_file_neg', help='path to the negative corpus file')
    arg_parser.add_argument('output_file', help='path to the output file')
    args = arg_parser.parse_args()

    print('\n - Autosarkasmus Baseline Feature Extraction (Simplified) -\n')

    # feature setup
    print('setting up features...')
    features, feature_order = setup_features()
    print('setting up feature extractor...')
    feature_extractor = FeatureExtractor(features, feature_order)

    # ARFF document setup
    arff_doc = ARFFDocument('Sarkasmuserkennung', features, feature_order)

    # the magic
    tweets_ext = feature_extractor.extract_features(args.corpus_file_pos, args.corpus_file_neg, verbose=True)

    # generate final ARFF document
    print('generating ARFF document...')
    for tweet_ext in tweets_ext:
        arff_doc.add_data(tweet_ext)
    arff_doc.generate_document(args.output_file)

    print('\n - extracted features from ' + str(len(arff_doc.data)) + ' tweets -\n')
