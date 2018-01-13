'''
AutosarkasmusBot (class), AutosarkasmusBotStreamer (class)
'''

import tweepy, json, re
from random import randint

from autosarkasmus.preprocessor.pipeline import Pipeline
from autosarkasmus.extractor.feature_extractor import FeatureExtractor
from autosarkasmus.classifier.mlp_classifier import MultiLayerPerceptronClassifier


class AutosarkasmusBot:
    '''
    A bot for the @autosarkasmus twitter account

    Processes sarcasm classification requests and corresponding feedback.
    '''

    def __init__(self, config_path, verbose=False):
        '''
        Constructor of AutosarkasmusBot

        Keyword arguments:
            config_path (str): path to the json configuration file
            verbose (str): stdout verbosity
        '''
        self.verbose = verbose
        self._load_config(config_path) # load config from file
        # Twitter API parameters
        self.oauth = tweepy.OAuthHandler(self.CONSUMER_KEY, self.CONSUMER_SECRET)
        self.oauth.set_access_token(self.ACCESS_KEY, self.ACCESS_SECRET)
        self.twitter_api = tweepy.API(self.oauth)
        # tweet processing
        self.pipeline = Pipeline(self.training_corpus_positive_path, self.pipeline_tagger_mapping_path)
        self.feature_extractor = FeatureExtractor(self.features, self.feature_order)
        self.classifier = MultiLayerPerceptronClassifier(self.feature_order, verbose=self.verbose)

    def _load_config(self, config_path):
        '''
        Loads configuration from JSON file

        Keyword arguments:
            config_path (str): path to the json configuration file
        '''
        config_json = {}
        try:
            with open(config_path, 'r', encoding='utf8') as fop:
                config_json = json.load(fop)
        except Exception as ex:
            print('Error: Could not read config file at "' + config_path + '".')
            print(ex)
        self.screen_name = config_json.get('SCREEN_NAME', None) # screen name used by the bot
        self.enquiry_pattern = config_json.get('ENQUIRY_PATTERN', None) # pattern that matches an enquiry
        self.enquiry_responses = config_json.get('ENQUIRY_RESPONSES', {'positive':[], 'negative':[]}) # responses to an enquiry
        self.feedback_responses = config_json.get('FEEDBACK_RESPONSES', {'positive':[], 'negative':[]}) # responses to feedback
        self.CONSUMER_KEY = config_json.get('CONSUMER_KEY', None) # Twitter API consumer key
        self.CONSUMER_SECRET = config_json.get('CONSUMER_SECRET', None) # Twitter API consumer token
        self.ACCESS_KEY = config_json.get('ACCESS_KEY', None) # Twitter API application access key
        self.ACCESS_SECRET = config_json.get('ACCESS_SECRET', None) # Twitter API application secret key
        self.pipeline_tagger_mapping_path = config_json.get('PIPELINE_TAGGER_MAPPING_PATH', None) # path to tagger mapping file
        self.training_corpus_positive_path = config_json.get('TRAINING_CORPUS_POSITIVE_PATH', None) # path to corpus with positive training data
        self.training_corpus_negative_path = config_json.get('TRAINING_CORPUS_NEGATIVE_PATH', None) # path to corpus with negative training data
        self.history_path = config_json.get('HISTORY_PATH', None) # path to the bot's history
        # load history to memory
        self.history = {}
        try:
            with open(self.history_path, 'r', encoding='utf8') as fop:
                self.history = json.load(fop)
        except Exception as ex:
            print('Error: Could not read history file at "' + config_path + '".')
            print(ex)
        # load features to memory
        self.features = {}
        self.feature_order = []
        features_json = config_json.get('FEATURES', [])
        for feature_json in features_json:
            self.feature_order.append(feature_json['key'])
            self.features[feature_json['key']] = feature_json['values']

    def train(self):
        '''
        Train the bot on given data
        '''
        tweets_ext = self.feature_extractor.extract_features(self.training_corpus_positive_path, self.training_corpus_negative_path, verbose=self.verbose) # extract features from training corpora
        if self.verbose: print('training classifier...')
        self.classifier.train(tweets_ext)

    def classify_tweet(self, tweet_raw):
        '''
        Classifies a single tweet

        Keyword arguments:
            tweet_raw (str): text of the tweet to classify

        Returns:
            dict: the extracted features of the tweet in addition to class
        '''
        if self.verbose: print('classifying tweet: "' + tweet_raw + '"')
        tweet_tkn, tweet_proc = self.pipeline.process_tweet(tweet_raw) # preprocess the raw tweet
        if self.verbose: print(str(tweet_tkn) + '\n' + str(tweet_proc))
        tweet_ext = self.feature_extractor.extract_features_from_tweet(tweet_tkn, tweet_proc, True) # extract features from tweet (sarcasm is True per default)
        del(tweet_ext['class']) # delete class since it is only a default value
        if self.verbose: print([(feature, tweet_ext[feature]) for feature in self.feature_order if tweet_ext.get(feature, 0) != 0 ]) # print all features != 0
        tweet_class = self.classifier.classify([tweet_ext]) # classify the tweet
        if self.verbose: print('classified with sarcasm:', tweet_class[0]['class'])
        return tweet_class[0]

    def is_sarcastic_tweet(self, tweet_raw):
        '''
        Identifies sarcasm in a single tweet

        Keyword arguments:
            tweet_raw (str): text of the tweet to classify

        Returns:
            bool: whether the tweet was classified as being sarcastic
        '''
        return self.classify_tweet(tweet_raw)['class']

    def is_valid_enquiry(self, tweet_json):
        '''
        Checks whether the given tweet is a valid enquiry

        Keyword arguments:
            tweet_json (dict): JSON representation of the tweet object

        Returns:
            bool: whether the tweet is a valid enquiry
        '''
        res = False
        # check if tweet matches enquiry pattern, no case matching
        if re.match(self.enquiry_pattern, tweet_json['text'], re.IGNORECASE):
            # check if tweet wasn't authored by the bot itself
            if tweet_json['user']['screen_name'] != self.screen_name:
                # check for retweeted enquiry
                if not tweet_json['retweeted']:
                    # check if tweet is a reply to anything
                    if tweet_json['in_reply_to_status_id']:
                        res = True
        return res

    def is_valid_feedback(self, tweet_json):
        '''
        Checks whether the given tweet is valid feedback

        Keyword arguments:
            tweet_json (dict): JSON representation of the tweet object

        Returns:
            bool: whether the tweet is valid feedback
        '''
        res = False
        # check if tweet wasn't authored by the bot itself
        if tweet_json['user']['screen_name'] != self.screen_name:
            # check for retweet
            if not tweet_json['retweeted']:
                # check if tweet is reply to a tweet sent by the bot
                if tweet_json['in_reply_to_status_id']:
                    reply_tweet_status = self.twitter_api.get_status(tweet_json['in_reply_to_status_id'])
                    if reply_tweet_status.user.screen_name == self.screen_name:
                        # check if bot tweeted a classification
                        for enquiry_response in self.enquiry_responses['positive'] + self.enquiry_responses['negative']:
                            if enquiry_response in reply_tweet_status.text:
                                res = True
                                break
        return res

    def gen_enquiry_response(self, recipient, tweet_is_sarcastic):
        '''
        Generate response to an enquiry

        Keyword arguments:
            recipient (str): user handle of the addressee
            tweet_is_sarcastic (bool): whether the tweet was classified as sarcastic

        Returns:
            str: twitter-ready response
        '''
        response = '😓' # default response
        # pick fitting response at random
        if tweet_is_sarcastic:
            response = self.enquiry_responses['positive'][randint(0,len(self.enquiry_responses['positive'])-1)]
        else:
            response = self.enquiry_responses['negative'][randint(0,len(self.enquiry_responses['negative'])-1)]
        # prepend the recipient
        response = '@' + recipient + ' ' + response + ' Korrekt? (j/n)'
        # trim tweet if necessary
        if len(response) > 140:
            response = response[:137] + '...'
        return response

    def gen_feedback_response(self, recipient, correctly_classified):
        '''
        Generate response to feedback

        Keyword arguments:
            recipient (str): user handle of the addressee
            correctly_classified (bool): whether the tweet was correctly classified

        Returns:
            str: twitter-ready response
        '''
        response = 'Danke! ^^' # default response
        # pick fitting response at random
        if correctly_classified:
            response = self.feedback_responses['positive'][randint(0,len(self.feedback_responses['positive'])-1)]
        else:
            response = self.feedback_responses['negative'][randint(0,len(self.feedback_responses['negative'])-1)]
        # prepend the recipient
        response = '@' + recipient + ' ' + response
        # trim tweet if necessary
        if len(response) > 140:
            response = response[:137] + '...'
        return response

    def respond(self, tweet_json):
        '''
        Respond to a tweet

        Responses are generated for classification enquiries and feedback to said enquiries

        Keyword arguments:
            tweet_json (dict): JSON representation of the tweet to respond to
        '''
        if self.verbose: print('mentioned by @' + tweet_json['user']['screen_name'] + '\n"' + tweet_json['text'] + '"')
        bot_response = None

        if self.is_valid_enquiry(tweet_json): # if tweet is a classification enquiry
            if tweet_json['in_reply_to_status_id'] not in self.history: # check if tweet has already been classifed
                eval_tweet_status = self.twitter_api.get_status(tweet_json['in_reply_to_status_id']) # get tweet to be classified (as Tweepy.Status object)
                eval_tweet_sarcastic = self.is_sarcastic_tweet(eval_tweet_status.text) # classify the tweet
                bot_response = self.gen_enquiry_response(tweet_json['user']['screen_name'], eval_tweet_sarcastic) # generate response accordingly
                # save tweet and its classification in history
                self.history[eval_tweet_status.id] = eval_tweet_status._json
                self.history[eval_tweet_status.id]['sarcasm_predicted'] = eval_tweet_sarcastic
                self.save_history()

        elif self.is_valid_feedback(tweet_json): # if tweet is feedback
            correctly_classified = None
            # analyze feedback
            if re.match(r'.*?\b(j(a|o|ep)?|y(es|o)?)\b.*?', tweet_json['text'], re.IGNORECASE):
                correctly_classified = True
            elif re.match(r'.*?\b(n(e(in)?|o(pe)?)?)\b.*?', tweet_json['text'], re.IGNORECASE):
                correctly_classified = False
            if correctly_classified is not None: # if feedback could be parsed
                # follow the tweet trail back to the source (feedback -> classification -> enquiry -> classified_tweet)
                class_tweet_status = self.twitter_api.get_status(tweet_json['in_reply_to_status_id'])
                enq_tweet_status = self.twitter_api.get_status(class_tweet_status.in_reply_to_status_id)
                eval_tweet_status = self.twitter_api.get_status(enq_tweet_status.in_reply_to_status_id)
                # save the evaluation
                if 'sarcasm_actual' not in self.history[eval_tweet_status.id]:
                    bot_response = self.gen_feedback_response(tweet_json['user']['screen_name'], correctly_classified)
                    self.history[eval_tweet_status.id]['sarcasm_actual'] = self.history[eval_tweet_status.id]['sarcasm_predicted'] and correctly_classified
                    self.save_history()

        if bot_response: self.twitter_api.update_status(bot_response, tweet_json['id']) # post response to twitter
        if self.verbose and bot_response: print('responded with: "' + str(bot_response) + '"')

    def save_history(self):
        '''
        Saves the bot's history to file
        '''
        try:
            with open(self.history_path, 'w', encoding='utf8') as fop:
                json.dump(self.history, fop)
        except Exception as ex:
            print('Error: Could not save history to "' + self.history_path + '"')
            print(ex)


class AutosarkasmusBotStreamer(tweepy.streaming.StreamListener):
    '''
    StreamListener for the AutosarkasmusBot
    '''

    def __init__(self, bot, api=None):
        '''
        Constructor of AutosarkasmusBotStreamer

        Keyword arguments:
            bot (AutosarkasmusBot): bot that listens to the stream
            api (Tweepy.API): the initilized API for accessing twitter
        '''
        super().__init__(api)
        self.bot = bot

    def on_data(self, data):
        '''
        Processes tweets sent to the bot

        Keyword arguments:
            data (str): tweet as JSON string
        '''
        tweet_json = json.loads(data.strip()) # load JSON string to object
        self.bot.respond(tweet_json) # have the bot respond to it (or not)
