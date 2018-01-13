import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from autosarkasmus.extractor.extract_features import setup_features
from autosarkasmus.classifier.mlp_classifier import MultiLayerPerceptronClassifier
import argparse, json

if __name__ == '__main__':
    # argument parsing
    arg_parser = argparse.ArgumentParser(description='MLP Classifier Test')
    arg_parser.add_argument('corpus_file', help='path to the positive corpus file')
    args = arg_parser.parse_args()

    print('\n - MLP Classifier Test -\n')


    # feature setup
    print('setting up features...')
    features, feature_order = setup_features()

    # data setup
    print('setting up data...')
    tweet_vectors = json.load(open(args.corpus_file, 'r',encoding='utf8'))

    # classification
    mlp_classifier = MultiLayerPerceptronClassifier(feature_order, 20000, verbose=True)
    mlp_classifier.train(tweet_vectors)
    class_results = mlp_classifier.classify(tweet_vectors[:10])
    print(class_results)

    mlp_classifier.save("mlp_session_debug.ckpt")
    mlp_classifier.close()
    print('\n - end of program -')
