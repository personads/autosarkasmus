# -*- coding: utf-8 -*-
"""Tokenizer (class)

RegEx based tokenizer for tweets
"""

import re

class Tokenizer:
    '''
    RegEx bases tokenizer for tweets

    The following are interpreted as tokens (in decending priority):
        * URLs (e.g. http://www.cl.uni-heidelberg.de/courses/)
        * e-mail addresses (e.g. swp-ss16-srk@cl.uni-heidelberg.de)
        * Twitter user handles (e.g. @autosarkasmus)
        * Twitter hashtags (e.g. #Sarkasmus)
        * character emoticons (e.g. :D)
        * emoji (e.g. 😺)
        * punctuation (e.g. ! or +++)
        * words (e.g. Tweet-Tokenizer_class)
        * any non-whitespace sequence
    '''

    def __init__(self):
        self.regex_word = r"[\w\_]+|\S" #default words and every non-whitespace sequence
        self.regex_punctuation = r"[\-+=\*~]{2,}|(?:\.|\||[\?\!]){1,}|[:,;&'\"\(\)\[\]\^/\\+\-\*\=]" #default punctuation and decorators
        self.regex_emoji = r"[\U0001f600-\U0001f650]"
        self.regex_emoticon = "|".join([
            r"[<>]?[:;=]\-?[\)\]\(\[dDpP/\:\}\{@\|\\]", #left to right emoticons
            r"[\)\]\(\[dDpP/\:\}\{@\|\\]\-?[:;=][<>]?", #right to left emoticons
            r"<3" #non-face emoticons
        ])
        self.regex_hashtag = r"\#\w+" #hashtags
        self.regex_user = r"@[\w_]+" #twitter handles
        self.regex_email = r"[\w.+-]+@[\w-]+\.(?:[\w-]\.?)+[\w-]" #email addresses
        self.regex_url = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+" #urls

        #combined regex (one regex to rule them all)
        self.regex_all = "(" + "|".join([
            self.regex_url,
            self.regex_email,
            self.regex_user,
            self.regex_hashtag,
            self.regex_emoticon,
            self.regex_emoji,
            self.regex_punctuation,
            self.regex_word
        ]) + ")"

    def tokenize(self, tweet):
        '''Returns a list of tokens in a tweet.

        Keyword arguments:
            tweet (str): the raw tweet (str) to be tokenized

        Returns:
            list: of tokens (str)
        '''
        res = []
        res = re.findall(self.regex_all, tweet)
        return res
