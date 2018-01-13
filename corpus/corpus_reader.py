'''
CorpusReader(class) to read the corpus, created by the sarcasm_twython.py script

'''

from csv import reader
import sys
import json

class CorpusReader:
    '''	This class takes a tweet file with json objects or a txt file with per line tweets and returns a list of the text attribute of all tweets.'''

    def __init__(self, filename):
        '''
		Constructor of CorpusReader

		Keyword arguments:
		filename (str): path to the corpus file
        '''
        self.this_file = open(filename,"r")

    def iterload(self):
        '''
		Make the json file with multiple json objects an iterable. 
		See http://stackoverflow.com/a/10195371/4643936
		'''
        buffer = ""
        dec = json.JSONDecoder()
        for line in self.this_file:
            buffer = buffer.strip(" \n\r\t") + line.strip(" \n\r\t")
            while(True):
                try:
                    r = dec.raw_decode(buffer)
                except:
                    break
                yield r[0]
                buffer = buffer[r[1]:].strip(" \n\r\t")

    def text_json(self):
        '''	Takes a json file and returns a list containing the value of the text attribute in a tweet'''
        tweets = []
        for o in self.iterload():
            tweets.append(o['text'])

        return tweets

    def text_txt(self):
        '''Takes a txt file and returns a list containing the value of the text attribute in a tweet'''
        tweets = []
        for line in reader(self.this_file):
            tweets.append(line[2].strip())
        
        return tweets
        

    def date_id_text(self):
        '''Takes a txt file and returns a list containing the tweetid, date and text of a tweet comma seperated'''
        tweets = []
        for line in reader(self.this_file):
            tweets.append(line)
        
        return tweets



