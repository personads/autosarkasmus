# -*- coding: utf-8 -*-
'''
Feature Extractor (script)

The feature extraction for unigram baseline creation.
'''
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import argparse
import re

from autosarkasmus.preprocessor.pipeline import Pipeline

from arff_document import ARFFDocument
#from unihash_helpers import load_unihash
from unigram_helpers import load_unigrams


def setup_features():
	 '''Setup the features by using the unigram_helpers: unigrams'''
    features = {}
    feature_order = []
    feature_order += load_unigrams()
    feature_order += [
        'class'
    ]

    for feature_key in feature_order:
        if feature_key == 'class':
            features[feature_key] = set(['sarcastic', 'non-sarcastic'])
        else:
            features[feature_key] = 'numeric'

    return features, feature_order

def extract_features(tweet_tkn, tweet_proc, is_sarcastic, features, feature_order, resources={}):
    res = {}
    # class
    res['class'] = 'sarcastic' if is_sarcastic else 'non-sarcastic'
    for token in tweet_tkn:
        token_low = token.lower()
        if 'unigram-'+token_low in feature_order:
            res['unigram-'+token_low] = res.get('unigram-'+token_low, 0) + 1

    for feature_key in feature_order:
        res[feature_key] = res.get(feature_key, 0)
    return res

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

    # resource setup
    print('setting up resources...')
    resources = {}

    # ARFF document setup
    arff_doc = ARFFDocument('Sarkasmuserkennung', features, feature_order)

    # extract features
    print('extracting features...')

    print('   preprocessing positive samples...')
    pipeline = Pipeline(args.corpus_file_pos, '../rsrc/de-tiger.map')
    tweets_tkn, tweets_proc = pipeline.process()
    print('   extracting features for positive samples...')
    for tweet_index in range(len(tweets_tkn)):
        ext_features = extract_features(tweets_tkn[tweet_index], tweets_proc[tweet_index], True, features, feature_order, resources)
        arff_doc.add_data(ext_features)
    print('   writing to files (for safety)...')
    pipeline.write_file(tweets_tkn, args.corpus_file_pos + '.tkn')
    pipeline.write_file(tweets_proc, args.corpus_file_pos + '.proc')
    arff_doc.generate_document(args.output_file + '.pos')

    print('   preprocessing negative samples...')
    pipeline = Pipeline(args.corpus_file_neg, '../rsrc/de-negra.map')
    tweets_tkn, tweets_proc = pipeline.process()
    print('   extracting features for negative samples...')
    for tweet_index in range(len(tweets_tkn)):
        ext_features = extract_features(tweets_tkn[tweet_index], tweets_proc[tweet_index], False, features, feature_order, resources)
        arff_doc.add_data(ext_features)
    pipeline.write_file(tweets_tkn, args.corpus_file_neg + '.tkn')
    pipeline.write_file(tweets_proc, args.corpus_file_neg + '.proc')
    arff_doc.generate_document(args.output_file + '.neg')

    #
    # testing block
    #
    # tweet_tkn = ['Ich', 'liiiiebe', 'es', ',', 'VERSPÄTUNG', 'zu', 'haben', '#selbstverliebt', '#DeutscheBahn', ':(']
    # tweet_proc = [('Ich', 'PRON'), ('liebe', 'VERB'), ('es', 'PRON'), (',', 'PUNCT'), ('Verspätung', 'NOUN'), ('zu', ''), ('haben', 'VERB'), ('selbstverliebt','SYM'),('DeutscheBahn', 'SYM'), ('%SMILEY-NEG%', 'SYM')]
    # arff_doc.add_data(extract_features(tweet_tkn, tweet_proc, True, features, feature_order, resources))
    #
    # end of testing block
    #

    # generate final ARFF document
    print('generating ARFF document...')
    arff_doc.generate_document(args.output_file)

    print('\n - extracted features from ' + str(len(arff_doc.data)) + ' tweets -\n')

