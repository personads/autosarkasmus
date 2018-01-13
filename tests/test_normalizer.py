# -*- coding: utf-8 -*-
import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from autosarkasmus.corpus.corpus_reader import CorpusReader
from autosarkasmus.preprocessor.tokenizer.tokenizer import Tokenizer
from autosarkasmus.preprocessor.normalizer.normalizer import Normalizer

if __name__=="__main__":
	corpus = CorpusReader("test.txt")
	tweets = corpus.text_txt()
	tokenizer = Tokenizer()
	normalizer = Normalizer()
	for tweet in tweets:
		# first: setup unigram&bigram counts
		tweet = tokenizer.tokenize(tweet)
		c = normalizer.get_contexts(tweet)
		for (token, context) in c:
			normalizer.collect_bigrams(token, context)
			
	for tweet in tweets:
		# second round: normalize
		tweet = tokenizer.tokenize(tweet)
		c = normalizer.get_contexts(tweet)
		for (token, context) in c:
			tn = normalizer.normalize(token, context)
			print("{} -> {}".format(token, tn))
