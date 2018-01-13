# -*- coding: utf-8 -*-
"""Corpus Filter (script)

Simplifies manual filtering of corpus data.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import argparse

from corpus_reader import CorpusReader

def get_input_option(prompt, options) :
	res = input(prompt + " (" + "/".join(options) + ") ")
	while res not in options :
		res = input("pardon? (" + "/".join(options) + ") ")
	return res

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Corpus Filter')
    arg_parser.add_argument('corpus_file', help='path to the corpus file')
    arg_parser.add_argument('output_prefix', help='path to the output files')
    args = arg_parser.parse_args()

    print('\n - Filtering Corpus -\n')

    corpus = CorpusReader(args.corpus_file)
    file_output_pos = open(args.output_prefix + '.pos', 'w', encoding='utf8')
    file_output_neg = open(args.output_prefix + '.neg', 'w', encoding='utf8')
    file_output_fav = open(args.output_prefix + '.fav', 'w', encoding='utf8')

    for tweet in corpus.text_json():
        tweet = tweet.replace('\n', ' ')
        tweet = tweet.strip()
        print('"' + tweet + '"')
        action = get_input_option('sarcasm detected?', ['y', 'n', 'f', 'q'])
        if action == 'f':
            file_output_fav.write(tweet + '\n')
            action = get_input_option('faved, but is there sarcasm?', ['y', 'n', 'q'])
        if action == 'y':
            file_output_pos.write(tweet + '\n')
        elif action == 'n':
            file_output_neg.write(tweet + '\n')
        elif action == 'q':
            break
        print()

    file_output_pos.close()
    file_output_neg.close()
    file_output_fav.close()

    print('\n - end of program -')
