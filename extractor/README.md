extractor
=========
a module for extracting features from tweets

Components
----------
* **arff_document**  
    Helper class for the creation of ARFF documents that can be used in the [WEKA](http://www.cs.waikato.ac.nz/ml/weka/) toolkit.
* **cluster_helpers**  
    Helper class for loading and working with word clusters.
* **feature_extractor**  
    Extracts give features from tweets and returns them as feature vectors.
* **hashtag_helpers**  
    Helper class for loading and working with hashtags (extracted from corpus or given as list).
* **intensifier_helpers**  
    Helper class for loading and working with intensifiers given a list.
* **sentiws_helpers**  
    Helper class for loading and working with the SentiWS sentiment dictionary.
* **unigram_helpers**  
    Helper class for loading and working with unigrams (extracted from corpus or given as list).

Usage
-----
The FeatureExtractor can be used in the following manner (after sourcing the virtual environment):

    from autosarkasmus.extractor.feature_extractor import FeatureExtractor

    features = [{'feature-0':'numeric'}, {'feature-1':['val1', 'val2']}, {'class':['sarcastic', 'non-sarcastic']}]
    feature_order = ['feature-0', 'feature-1', 'class']

    feature_extractor = FeatureExtractor(features, feature_order)

    # extract from positive and negative corpora
    tweets_ext = feature_extractor.extract_features(corpus_pos_path, corpus_neg_path)

    # extract from single tweet given its tokenization and pos-tagged normalization
    tweet_ext = feature_extractor.extract_features_from_tweet(tweet_tkn, tweet_proc, is_sarcastic=True)

The complete list of compatible features can be found in the docstring for *feature_extractor.extract_features_from_tweet()*. Please make sure that if you provide your own resources (e.g. intensifier list) the paths in the corresponding helper classes are set correctly.
