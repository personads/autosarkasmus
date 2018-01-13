# -*- coding: utf-8 -*-
'''
Feature Extractor (script)

The feature extraction for baseline creation.
'''
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import argparse
import re

from autosarkasmus.preprocessor.pipeline import Pipeline

from autosarkasmus.extractor.feature_extractor import FeatureExtractor
from autosarkasmus.extractor.arff_document import ARFFDocument
from autosarkasmus.extractor.hashtag_helpers import load_hashtags, load_hashtags_from_corpus
from autosarkasmus.extractor.intensifier_helpers import load_intensifiers
from autosarkasmus.extractor.sentiws_helpers import load_sentiws
from autosarkasmus.extractor.cluster_helpers import load_clusters


def setup_features(corpus_file=""):
    '''Extract features: hashtags, clusters, POS, extended-vocals, capitalization, intensifiers, emoticons, sentiment, class'''
    features = {}
    feature_order = []
    # Hastags
    if corpus_file is not "":
        feature_order += load_hashtags_from_corpus(corpus_file)
    else:
        feature_order += load_hashtags()
    # Unigrams from clusters
    feature_order += load_clusters()
    feature_order += [
        # POS-Tags
        'pos-.', 'pos-adj', 'pos-adv', 'pos-conj', 'pos-det', 'pos-noun', 'pos-num', 'pos-pron', 'pos-prt', 'pos-verb', 'pos-x', 'pos-hashtag', 'pos-mention', 'pos-url',
        # extended vocals
        'extended-vocals',
        # capitalization
        'capitalization'
    ]
    # intensifiers
    feature_order += load_intensifiers()
    feature_order += [
        # emoticons
        'emoticon-pos',
        'emoticon-neg',
        'emoticon-all',
        # sentiment
        'sentiment-pos',
        'sentiment-neg',
        'sentiment-all',
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

    print('\n - Autosarkasmus Baseline Feature Extraction -\n')

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
