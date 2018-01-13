# -*- coding: utf-8 -*-
import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from autosarkasmus.preprocessor.pipeline import Pipeline


pp = Pipeline("test.txt", "../rsrc/de-tiger.map")
tweets, tagged = pp.process()
for i in range(len(tweets)):
	print(" ".join(tweets[i]))
	output = ""
	for token, tag in tagged[i]:
		output += "{}|{} ".format(token, tag)
	print(output.strip())
	print()
