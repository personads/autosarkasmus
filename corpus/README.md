Corpus Tools
==========
a module for reading and collecting tweets.

Components
----------
* **CorpusReader**  
    A wrapper class for sklearn's SVM Classifier that accepts feature vectors in the autosarkasmus format.

* **CustomStreamListener (script)**
    A Crawler for listening to the Twitter Streaming API, collect german sarcastic tweets and save them into .json and .txt files
* **RemoveDuplicateTweets**  
    A class for removing tweets out of a given corpusfile of tweets.


Usage of CorpusReader
-----
The CorpusReader can be used in the following manner (after sourcing the virtual environment):
```python
 from corpus.corpus_reader import CorpusReader
 
 Read = CorpusReader("tweets.txt")
 for tweet in Read.text_txt()::
    print(tweet)
```

Output

The method returns a list of tweettexts.

['This is a sarcastic tweet', 'This is another sarcastic tweet']

Usage of RemoveDuplicateTweets
-----
The RemoveDuplicateTweets can be used in the following manner (after sourcing the virtual environment):
```python

    from corpus.remove_duplicates import RemoveDuplicateTweets
    
    Rd = RemoveDuplicateTweets('tweets.txt')
    Rd.write()
```

Output

The class will save the given tweets into a file with the suffix .cleaned.

References
----------
1. Linguistics of German Twitter, http://www.ling.uni-potsdam.de/∼scheffler/twitter/
2. Stand-alone language identification system, https://github.com/saffsd/langid.py
3. Tweepy - Twitter for Python, https://github.com/tweepy/tweepy


