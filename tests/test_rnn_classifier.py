import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from autosarkasmus.preprocessor.pipeline import Pipeline
from autosarkasmus.classifier.rnn_classifier import RecurrentNeuralNetworkClassifier
import argparse, json, pickle, numpy

if __name__ == '__main__':
    # argument parsing
    arg_parser = argparse.ArgumentParser(description='RNN Classifier Test')
#    arg_parser.add_argument('corpus_file_pos', help='path to the positive corpus file')
#    arg_parser.add_argument('corpus_file_neg', help='path to the negative corpus file')
    arg_parser.add_argument('embeddings_file', help='path to the embeddings file')
    arg_parser.add_argument('iterations', type=int, default=10000, help='number of iterations')
    args = arg_parser.parse_args()

    print('\n - RNN Classifier Test -\n')

    # feature setup
    print('loading embeddings...')
    embeddings = pickle.load(open(args.embeddings_file, 'rb'), encoding='bytes')

    # data setup
    print('setting up data...')
#    train_data = []
#    for is_sarcastic in [True, False]:
#        print('   preprocessing samples with sarcastic='+str(is_sarcastic)+'...')
#        # preprocess tweets
#        if is_sarcastic:
#            pipeline = Pipeline(args.corpus_file_pos, '../rsrc/de-tiger.map')
#        else:
#            pipeline = Pipeline(args.corpus_file_neg, '../rsrc/de-tiger.map')
#        tweets_tkn, tweets_proc = pipeline.process()
#        for tweet_proc in tweets_proc:
#            train_data.append(
#                {
#                    'tweet': tweet_proc,
#                    'class': is_sarcastic
#                }
#            )
    train_data = pickle.load(open('debug/tweets_proc.pkl', 'rb'), encoding='bytes')

    # classification
    rnn_classifier = RecurrentNeuralNetworkClassifier(embeddings, args.iterations, verbose=True)
    rnn_classifier.train(train_data)
    class_results = rnn_classifier.classify(train_data[:10])
    print(class_results)

    rnn_classifier.save("debug/rnn_multi_session_debug_"+str(args.iterations)+".ckpt")
    rnn_classifier.close()
    print('\n - end of program -')
