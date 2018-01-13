preprocessor
============
a module for preprocessing German tweets

Components
----------
* **pipeline**  
    A pipeline for preprocessing raw German tweets. Includes tokenization, normalization and pos-tagging.
* **normalizer**  
    Given tokenized tweets, this module performs normalization of twitter-specific phenomena such as mentions, hashtags, emoticons etc. and corrects spelling errors including extended vocalizations.
* **tagger**  
    Given normalized tweets, this module performs pos-tagging using the TreeTagger. (Please set the path to your TreeTagger installtion accordingly in *tagger_m.py*)
* **tokenizer**  
    Given raw tweets, this module performs a rule-based tokenization.

Usage
-----
The complete preprocessing pipeline can be used in the following manner (after sourcing the virtual environment):

    from autosarkasmus.preprocessor.pipeline import Pipeline

    pipeline = Pipeline(corpus_path, tagger_mapping_path)
    tweets_tkn, tweets_proc = pipeline.process()

    pipeline.write_file(tweets_tkn, corpus_path + '.tkn')
    pipeline.write_file(tweets_proc, corpus_path + '.proc')

The output *tweets_tkn* contains all tokenized tweets as a list of tokens while *tweets_proc* contains all tokenized and normalized tweets with their corresponding pos-tags. Additionally, results can be stored in files with one token (optionally tab separated with tag) per line.  

Individual actions may also be performed on single tweets, but a full corpus must still be provided because the normalizer uses bigram frequencies to assist in the spelling correction. Corpora may either be in the csv-format or consist of the raw JSON-dumps from Twitter. This can be specified with the *json_corpus* flag which is *False* by default.

    from autosarkasmus.preprocessor.pipeline import Pipeline

    pipeline = Pipeline(training_corpus_path, tagger_mapping_path, json_corpus=True)

    tweet_raw = 'Mal wieder 50 Minuten Verspätung. TOLL! #nicht'

    tweet_tkn = pipeline.tokenize(tweet_raw)
    tweet_nrm = pipeline.normalize(tweet_tkn)
    tweet_tag = pipeline.tag(tweet_norm)

    tweet_tkn, tweet_proc = pipeline.process_tweet(tweet_raw) # or in one step
    
References
----------
1. Sidarenka, Uladzimir, Tatjana Scheffler, and Manfred Stede. "Rule-based normalization of german twitter messages." Proc. of the GSCL Workshop Verarbeitung und Annotation von Sprachdaten aus Genres internetbasierter Kommunikation. 2013.

