'''
Activates our pipeline to prepare an output file for tagger evaluation.

Input: gold_corpus.raw
Output: our_tagger_output.tagged
'''

import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from autosarkasmus.preprocessor.pipeline import Pipeline

pipe = Pipeline('foo', '../rsrc/de-tiger.map') # creates pipeline with mapping from STTS to universal

'''
Reads gold corpus
'''
corpus = []
with open('gold_corpus.raw', 'r') as fop:
    for line in fop:
        corpus.append([token.strip() for token in line.split(' ')])

tweets = [] # tweets are being read separately with this list
tweets_tagged = [] # this is the tagger output
# example: [('und', 'CONJ'), ('wieder', 'ADV'), ... , ('hashtag', 'NN'), ('user', 'NN)]

for tweet in corpus: # iterate through tweets in gold corpus
    tweet_tagged = pipe.tag(tweet)
    newLemma = []
    # example: [(tuple(('hashtag','HASH')) if lemma[0] == 'hashtag' else lemma) for lemma in tweet_tagged]
    for lemma in tweet_tagged:
		'''
		checking for different cases of twitter-specific tags in extended/modified universal pos tag set...
		If the script finds special tags, there will be a new annotation with the correct tag appended.
		'''
        if lemma[0] == 'hashtag':
            newLemma.append(('hashtag', 'HASH'))
        elif lemma[0] == 'emoticon':
            newLemma.append(('emoticon','EMO'))
        elif lemma[0] == 'url':
            newLemma.append(('url','URL'))
        elif lemma[0] == '@':
            newLemma.append(('@','ADDRESS'))
        elif lemma[0] == 'user':
            newLemma.append(('user','ADDRESS'))
        elif lemma[0] == '@card@':
            newLemma.append(('@card@','CARD'))
        else:
            newLemma.append((lemma[0],lemma[1]))
    tweets_tagged.append(newLemma) # adds the special cases annotations to the tagger output
    
pipe.write_file(tweets_tagged, "our_tagger_output.tagged")