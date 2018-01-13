autosarkasmus
=============
a framework for detecting sarcasm in German Twitter data

Modules
-------
* **bot**  
    A Twitter bot that listens to sarcasm classification requests.
* **classifier**  
    A wrapper class for sklearn's SVM Classifier that accepts feature vectors in the autosarkasmus format.
* **corpus**  
    Our tweet aggregation scripts as well as their results. These are stored in three formats: sarcastic tweets, non-sarcastic tweets (based on hashtags) and random non-sarcastic tweets.
* **extractor**  
    Includes methods for extracting features from tweets.
* **preprocessor**  
    A pipeline for preprocessing raw German tweets. Includes tokenization, normalization and pos-tagging.
* **validator**  
    A custom cross-validator which splits corpora into specified or random subsets.

Requirements
------------
* Python 3.4 or greater
    * tweepy (and its dependencies)
    * hunspell (and a German dictionary, requires libhunspell-dev)
    * [treetaggerwrapper 2.2.3](https://pypi.python.org/pypi/treetaggerwrapper/2.2.3)
    * [langid 1.1.6](https://pypi.python.org/pypi/langid)
    * sklearn (with numpy and scipy, requires python3-dev)
    * tensorflow
* [TreeTagger](http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/) installation
    * Negra / Tiger [STTS to Universal tagset mapping](https://github.com/slavpetrov/universal-pos-tags)
* optional resources
    * list of German intensifiers
    * [SentiWS](http://asv.informatik.uni-leipzig.de/download/sentiws.html) dictionary ([CC 3.0 BY-NC-SA](http://creativecommons.org/licenses/by-nc-sa/3.0/))
    * Brown Clusters for German words

Installation Instructions
-------------------------
We recommend using a virtual environment for Python 3.

    $ virtualenv -p python3 venv
    $ source venv/bin/activate  
    $ pip install -r requirements.txt  

Congratulations! You are now ready to classify sarcasm.

Pipeline
--------
The autosarkasmus pipeline consists of several steps that are outlined here.  

**corpus acquisition** (corpus module)  
Sarcastic and non-sarcastic tweets can be collected using the *sarcasm_twython.py* script. The collected data or previously collected data can then be easily loaded into an iterable CorpusReader object found in *corpus_reader.py*.  
**preprocessing** (preprocessor module)  
Using the Pipeline class in *pipeline.py* tweets in a acquired corpus can be tokenized, normalized and pos-tagged.  
**feature extraction** (extractor module)  
Given a set of features the FeatureExtractor class in *feature_extractor.py* can extract them from a preprocessed corpus or raw positive and negative training corpora.  
**training** (classifier module)  
The classifiers MultiLayerPerceptronClassifier and SVMClassifier can be trained using the feature vectors extracted with the feature extractor. The RecurrentNeuralNetworkClassifier can skip this step and only requires pre-trained word-embeddings.  
**classification** (classifier module)  
Once training is complete, the same pipeline can be applied to new tweets which can then be fed into the classifier.  

More detailed documentation is provided in the READMEs of the individual modules as well as their docstrings.

Performing Classification
-------------------------
Classification of individual tweets as well as entire corpora can be performed using the modules provided or as demonstrated in *autosarkasmus/run/autosarkasmus_demo.py*.  
All corpora for the demo must be provided in the following csv-format:

    "yyyy-mm-dd hh:mm:ss","tweet_id","tweet_text"
    ...

The classification of single tweets requires one training corpus with sarcastic tweets and one without in addition to a tagger mapping file (e.g. *rsrc/de-tiger.map*).  
After initialization and training, an input prompt is displayed into which a tweet can be manually entered and confirmed with a new-line. To end the program, enter only a new-line at the input prompt.

    $ source venv/bin/activate
    $ cd run/
    $ python autosarkasmus_demo.py [training corpus (pos)] [training corpus (neg)] [tag mapping]
    $ python autosarkasmus_demo.py ../corpus/txt/reviewed_corpus_files/tweets_pos_3099random.txt ../corpus/txt/reviewed_corpus_files/tweets_not-pos_3099random.txt ../rsrc/de-tiger.map

Batch classification of a corpus can be performed by providing its path in the -f or --input-file option. The output will be stored as the original path plus the *.out* extension.

    $ python autosarkasmus_demo.py -f=[corpus] [training corpus (pos)] [training corpus (neg)] [tag mapping]

Performing Evaluation
---------------------
Evaluation of the models provided in the classifier package can be performed using the XValidator. A prepared script can be found in *autosarkasmus/run/run_experiment.py*. It can be run as follows:

    $ source venv/bin/activate
    $ cd run/
    $ python run_experiment.py [experiment name] [training corpus (pos)] [training corpus (neg)] [embeddings_file]
    $ python run_experiment.py exp tweets_pos_3099random.txt tweets_not-pos_3099random.txt ../rsrc/embeddings.pkl

A ready-to-run script for evaluating the classifiers can be found in *autosarkasmus/run/run_experiments.sh*.  The default classifier is the RecurrentNeuralNetworkClassifier and others can be uncommented. (Please note that only one instance of MultiLayerPerceptronClassifier or RecurrentNeuralNetworkClassifier can be classified at once due to the variable scope in TensorFlow).

    $ source venv/bin/activate
    $ cd run/
    $ ./run_experiments.sh

Twitter Bot
-----------
Once the API keys are placed into the `bot/config.json`, the bot performs an initial training run on the data and will start listening for sarcasm requests.

    $ source venv/bin/activate
    $ cd bot/
    $ python run_bot.py

References
----------
1. E. Riloff, et al. "Sarcasm as Contrast between a Positive Sentiment and Negative Situation." EMNLP. 2013.
2. David Bamman, A. Smith, ”Contextualized Sarcasm Detection on Twitter”, Proceedings of the Ninth International AAAI Conference on Web and Social Media, 2015.
3. R. González-Ibánez, S. Muresan, and N. Wacholder. "Identifying sarcasm in Twitter: a closer look." Proceedings of the 49th Annual Meeting of the Association for Computational Linguistics: Human Language Technologies: short papers-Volume 2. Association for Computational Linguistics, 2011.
4. I. Rehbein. "Fine-grained pos tagging of german tweets." Language Processing and Knowledge in the Web. Springer Berlin Heidelberg, 2013. 162-175.
5. R. Remus, U. Quasthoff & G. Heyer. "SentiWS - a Publicly Available German-language Resource for Sentiment Analysis." Proceedings of the 7th International Language Ressources and Evaluation (LREC'10), pp. 1168--1171, 2010
6. N. Feldhus, D. Hoff, M. Müller-Eberstein & P. Richter-Pechanski. "Softwareprojekt SS 16 - Sarkasmuserkennung auf Twitter." Universität Heidelberg, 2016.
