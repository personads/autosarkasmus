# -*- coding: utf-8 -*-
import hunspell
import re
from collections import defaultdict

class Normalizer:
    def __init__(self):
        """
        Normalizer: restores original/formal spelling of misspelled/colloquial token, replaces twitter-specific phenomena for tagging

        Normalization requires setup of a dictionary of unigram/bigram occurences (to make the most probable correction)
        - first, run collect_bigrams() on every tweet
        - then, the normalize() function can be used

        For detailed usage, see tests/test_normalizer
        """
        self.dictionary = hunspell.HunSpell("../rsrc/hunspell/de_DE.dic", "../rsrc/hunspell/de_DE.aff")
        self.bigrams = defaultdict(lambda: 1.0) #add-1
        self.unigrams = defaultdict(lambda: 1.0)
        self.emoji_pos = [u"\U0001F601", u"\U0001F602", u"\U0001F603", u"\U0001F604", u"\U0001F605", u"\U0001F606", u"\U0001F607", u"\U0001F608", u"\U0001F609", u"\U0001F60A", u"\U0001F60B", u"\U0001F60C", u"\U0001F60D", u"\U0001F60E", u"\U0001F60F", u"\U0001F638", u"\U0001F639", u"\U0001F63A", u"\U0001F63B"]
        self.emoji_neg = [u"\U0001F612", u"\U0001F61E", u"\U0001F61F", u"\U0001F620", u"\U0001F621", u"\U0001F622", u"\U0001F623", u"\U0001F625", u"\U0001F627", u"\U0001F628", u"\U0001F62D", u"\U0001F63E", u"\U0001F63F"]
        self.special_tags = ["%HASHTAG%", "%MENTION%", "%SMILEYPOS%", "%SMILEYNEG%", "%SMILEY%", "%URL%", ",", ".", "!", "?", ":", ";", "-", "+++", "–", "\"", "|"]
        self.tokens = 0
        self._cache_spelling = {}

    def get_contexts(self, tweet):
        """
        creates all possible bigram combinations for a tweet
        input: list of tokens
        output: list of tuples containing token i and a tuple of token i-1 and i+1 for all tokens

        Example:
        input: ["Hello", "world", "!"]
        output: [("Hello", (None, "world")), ("world", ("Hello", "!")), ("!", ("world", None)]
        """
        contexts = []
        for i in range(len(tweet)):
                    if i == 0 and len(tweet) > 1:
                        context = (None, tweet[i+1])
                    elif i == len(tweet)-1:
                        context = (tweet[i-1], None)
                    else:
                        context = (tweet[i-1], tweet[i+1])
                    contexts.append((tweet[i], context))
        return contexts

    def collect_bigrams(self, token, contexts):
        """
        collects unigram and bigram counts for a token
        """
        self.unigrams[token] += 1
        self.bigrams[(contexts[0], token)] += 1
        self.bigrams[(token, contexts[1])] += 1


    def oov(self, token):
        """
        checks if a token is misspelled (not known to the hunspell dictionary)
        """
        try:
            token = token.encode("latin-1")
        except UnicodeEncodeError:
            return True
        if self.dictionary.spell(token) == False:
            return True
        else:
            return False

    def normalize(self, token, context):
        """
        uses Regex rules to correct a token's spelling:
        - replaces twitter phenomena (hashtags, URLs, @Mentions, Smileys and Emojis) with placeholders for POS-Tagging
        - restores probable original spelling of words not found in the dictionary

        current restoration rules:
        - ne, n, nen -> ein/e/n
        - shorten lengthened vowels
        - correct capitalization
        - correct unknown words using hunspell's spellcheck suggestions
        all corrections only take place if the resulting trigram (i-1, i, i+1) is more likely in respect to the corpus data
        """
        normalized = token
        # if not self.oov(normalized):
        #    return normalized

        # Hashtags: sanitize
        match_hashtag = re.match(r'^#(\S+)', normalized)
        if match_hashtag:
            return match_hashtag.group(1)

        # @-Mentions: delete content
        if re.match(r'^@\S+', normalized):
            return "%MENTION%"

        # Smiley: neg/pos
        if re.match(r"^[:;x]'?-?[\)D]$", normalized):
            return "%SMILEYPOS%"
        if re.match(r"^[:;]'?-?[\(<sSoO]$", normalized):
            return "%SMILEYNEG%"
        if re.match(r"^[:;]'?-?[^\)\(DsSoOcC<]$", normalized):
            return "%SMILEY%"

        # Unicode-Emojis
        if normalized in self.emoji_pos:
            return "%SMILEYPOS%"
        if normalized in self.emoji_neg:
            return "%SMILEYNEG%"
        if re.match(r"\\U0001F[0-9A-F]{3}", normalized):
            return "%SMILEY%"

        # URLs: sub
        if re.match(r"(https?://)?([a-z]+\.)?[a-z0-9-]+\.[a-z]+(\.[a-z]+)?(/\S*)*", normalized):
            return "%URL%"

        # punctuation handling
        match_punct = re.match(r"^[!\?,\.\-\_:;\(\)\[\]\{\}\+\=\~'\"]+$", normalized)
        if match_punct:
            if len(normalized) > 3:
                return normalized[:3]
            else:
                return normalized

        # correct capitalization:
        if len(normalized) > 1 and token == token.upper():
            uppercase = normalized[0].upper()+normalized[1:].lower()
            lowercase = normalized.lower()
            normalized = self.checkprob(lowercase, uppercase, context)

        # successively shorten lenghthened vowels
        match_vocal = re.findall("[aA]{3,}|[eE]{3,}|[iI]{3,}|[oO]{3,}|[uU]{3,}|[äÄ]{3,}|[üÜ]{3,}|[öÖ]{3,}", normalized)
        if len(match_vocal) > 0:
            for match in match_vocal:
                while self.oov(normalized) and len(match) > 0:
                    shortened = match[:-1]
                    normalized = re.sub(match, shortened, normalized)
                    match = shortened

        # correct colloquial articles (nen, ne...)
        # check context: ne Zahl vs toll, ne ?
        match_det = re.match(r"^('?n(en|e)?)$", normalized)
        if match_det:
            normalized = "ei"+match_det.group(0)

        # spellcheck:
        if self.oov(normalized):
            normalized = self.suggest_spelling(normalized, context)

        return normalized


    def suggest_spelling(self, token, context):
        """
        uses hunspell dictionary to get correction suggestions for misspelled words
        input: token, and tuple of previous and following token
        output: corrected token if the correction is more likely to occur in corpus
        """
        res = token
        try:
            if token in self._cache_spelling:
                suggestions = self._cache_spelling[token]
            else: 
                suggestions = self.dictionary.suggest(token)
                self._cache_spelling[token] = suggestions
        except UnicodeEncodeError:
            return res 
        for suggestion in suggestions[:3]:
            try:
                suggestion = suggestion.decode('latin-1')
            except UnicodeDecodeError:
                continue
            # prioritize capitaliation mistakes
            if token.lower() == suggestion.lower():
                res = suggestion
                break
            else:
                res = self.checkprob(res, suggestion, context)
        return res

    def getprob(self, token, context):
        """
        find the probability of sequence token-1 token token+1 given the current corpus of tweets
        input: token, and tuple of previous and following token
        output: probability (float)
        """
        res = 0.
        c_bigram_pre = self.bigrams[(context[0], token)]
        c_bigram_past = self.bigrams[(token, context[1])]
        c_token = self.unigrams[token]
        c_pre = self.unigrams[context[0]]
        c_past = self.unigrams[context[1]]
        res = (c_bigram_pre/(c_token+c_pre))*(c_bigram_past/(c_token+c_past))
        return res

    def checkprob(self, old, new, context):
        """
        compare the probability of a token with the probability for its corrected form in a given context
        input: token and spelling alternative, tuple of token-1 and token+1
        output: more probable of the spelling alternatives
        """
        p_old = self.getprob(old, context)
        p_new = self.getprob(new, context)
        if p_new > p_old:
            return new
        else:
            return old
