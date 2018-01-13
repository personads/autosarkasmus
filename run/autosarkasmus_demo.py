# -*- coding: utf-8 -*-
'''
Autosarkasmus Demo (script)

A demo script for sarcasm classification of German tweets
'''
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import argparse

from autosarkasmus.preprocessor.pipeline import Pipeline
from autosarkasmus.extractor.feature_extractor import FeatureExtractor
from autosarkasmus.extractor.extract_features import setup_features
from autosarkasmus.classifier.mlp_classifier import MultiLayerPerceptronClassifier

if __name__ == '__main__':
    # argument parsing
    arg_parser = argparse.ArgumentParser(description='Feature Extraction for the Autosarkasmus Baseline')
    arg_parser.add_argument('training_pos_path', help='path to the positive training corpus')
    arg_parser.add_argument('training_neg_path', help='path to the negative training corpus')
    arg_parser.add_argument('tagger_mapping_path', help='path to the tagger mapping')
    arg_parser.add_argument('-f', '--input_file', help='path to input file')
    args = arg_parser.parse_args()

    print('\n - Autosarkasmus Demo -\n')

    # preprocessing pipeline setup
    pipeline = Pipeline(args.training_pos_path, args.tagger_mapping_path)

    # feature setup
    print('setting up features...')
    features, feature_order = setup_features()

    # feature extraction
    print('setting up feature extractor...')
    feature_extractor = FeatureExtractor(features, feature_order)
    tweets_ext = feature_extractor.extract_features(args.training_pos_path, args.training_neg_path, verbose=True)
    print('extracted features from ' + str(len(tweets_ext)) + ' tweets.')

    # svm training
    print('training classifier...')
    classifier = MultiLayerPerceptronClassifier(feature_order, verbose=True)
    classifier.train(tweets_ext)
    print('\nready to classify.')

    # classification
    if args.input_file:
        print('preprocessing tweets...')
        pipeline = Pipeline(args.input_file, args.tagger_mapping_path)
        tweets_tkn, tweets_proc = pipeline.process()
        print('extracting features from tweets...')
        tweets_ext = []
        for tweet_index in range(len(tweets_tkn)):
            tweets_ext.append(feature_extractor.extract_features_from_tweet(tweets_tkn[tweet_index], tweets_proc[tweet_index], True))
        print('classifying tweets...')
        tweets_class = classifier.classify(tweets_ext)
        print('writing output to "' + args.input_file + '.out"')
        with open(args.input_file + '.out', 'w', encoding='utf8') as fop:
            for tweet_index in range(len(tweets_tkn)):
                fop.write('"' + ' '.join(tweets_tkn[tweet_index]) + '","' + tweets_class[tweet_index]['class'] + '"\n')
    else:
        tweet_input = "tweet_input"
        while tweet_input:
            tweet_input = input("Enter tweet to classify:\n")
            if len(tweet_input) < 1:
                break
            tweet_tkn, tweet_proc = pipeline.process_tweet(tweet_input) # preprocess the raw tweet
            print(str(tweet_tkn) + '\n' + str(tweet_proc))
            tweet_ext = feature_extractor.extract_features_from_tweet(tweet_tkn, tweet_proc, True) # extract features from tweet (sarcasm is True per default)
            del(tweet_ext['class']) # delete class since it is only a default value
            print([(feature, tweet_ext[feature]) for feature in feature_order if tweet_ext.get(feature, 0) != 0 ]) # print all features != 0
            tweet_class = classifier.classify([tweet_ext]) # classify the tweet according to the svm
            print("classified with sarcasm:", tweet_class[0]['class'])
            if 'sarcastic-prob' in tweet_class[0]:
                print("probablity for sarcasm:", tweet_class[0]['sarcastic-prob'])
            print()

    print('\n - end of program -\n')
