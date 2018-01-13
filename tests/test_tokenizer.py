# -*- coding: utf-8 -*-
import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from autosarkasmus.corpus.corpus_reader import CorpusReader
from autosarkasmus.preprocessor.tokenizer.tokenizer import Tokenizer

if __name__ == "__main__":
	cr = CorpusReader("test.txt")
	tkn = Tokenizer()
	for tweet in cr.text_txt():
		print(tweet)
		print("\t"+str(tkn.tokenize(tweet))+"\n")
