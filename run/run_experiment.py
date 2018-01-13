'''
Run experiments with MLP Classifier and RNN Classifier
'''
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import argparse, json, pickle, numpy

from autosarkasmus.preprocessor.pipeline import Pipeline
from autosarkasmus.extractor.feature_extractor import FeatureExtractor
from autosarkasmus.extractor.extract_features import setup_features
from autosarkasmus.validator.xvalidator import XValidator
from autosarkasmus.classifier.svm_classifier import SVMClassifier
from autosarkasmus.classifier.mlp_classifier import MultiLayerPerceptronClassifier
from autosarkasmus.classifier.rnn_classifier import RecurrentNeuralNetworkClassifier

if __name__ == '__main__':
    # argument parsing
    arg_parser = argparse.ArgumentParser(description='Autosarkasmus Experiment')
    arg_parser.add_argument('experiment_name', help='name of the experiment (for save-files)')
    arg_parser.add_argument('corpus_file_pos', help='path to the positive corpus file')
    arg_parser.add_argument('corpus_file_neg', help='path to the negative corpus file')
    arg_parser.add_argument('embeddings_file', help='path to the embeddings file')
    arg_parser.add_argument('folds', type=int, default=10, help='number of folds for cross-validation')
    arg_parser.add_argument('model', default='rnn', help='model to evaluate (mlp, rnn, svm)')
    args = arg_parser.parse_args()

    print('\n - Autosarkasmus Experiment -\n')

    # feature setup
    print('loading embeddings...')
    embeddings = pickle.load(open(args.embeddings_file, 'rb'), encoding='bytes')
    print('setting up features...')
    features, feature_order = setup_features()

    # data setup
    print('setting up data...')
    data = []
    if args.model == 'rnn':
        for is_sarcastic in [True, False]:
            print('  preprocessing samples with sarcastic='+str(is_sarcastic)+'...')
            # preprocess tweets
            if is_sarcastic:
                pipeline = Pipeline(args.corpus_file_pos, '../rsrc/de-tiger.map', verbose=True)
            else:
                pipeline = Pipeline(args.corpus_file_neg, '../rsrc/de-tiger.map', verbose=True)
            tweets_tkn, tweets_proc = pipeline.process()
            for tweet_proc in tweets_proc:
                data.append(
                    {
                        'tweet': tweet_proc,
                        'class': is_sarcastic
                    }
                )

    if args.model in ['svm', 'mlp']:
        feature_extractor = FeatureExtractor(features, feature_order)
        data = feature_extractor.extract_features(args.corpus_file_pos, args.corpus_file_neg, verbose=True) # extract features from training corpora

    # classifier setup
    classifiers = []
    if args.model == 'svm':
        classifiers.append(
            {
                'name': 'svm_classifier',
                'classifier': SVMClassifier(feature_order, verbose=True)
            }
        )
    elif args.model == 'mlp':
        classifiers.append(
            {
              'name': 'mlp_classifier',
               'classifier': MultiLayerPerceptronClassifier(feature_order, verbose=True)
            }
        )
    elif args.model == 'rnn':
        classifiers.append(
            {
                'name': 'rnn_classifier',
                'classifier': RecurrentNeuralNetworkClassifier(embeddings, verbose=True)
            }
        )
    else:
        print("Error: The specified model does not seem to be supported. Please choose from ['mlp', 'rnn', 'svm']")

    # xvalidator setup
    xvalidator = XValidator(args.folds, data, classifiers, args.experiment_name, verbose=True)

    # geronimo!
    xvalidator.run()

    # clean up
    for classifier in classifiers:
        classifier['classifier'].close()

    print('\n - end of program -')
