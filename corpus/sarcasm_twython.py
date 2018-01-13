# -*- coding: utf-8 -*-
''' 
Twython(script), CustomStreamListener(class)
by Tatjana Scheffler
A simple example script for corpus collection from Twitter using Tweepy https://github.com/tweepy

Modified by PRP to filter positive and negative samples of ironic related tweets. Additionally the scripts produces two outputs:
1. A textfile with the text of every tweet, new line seperated
2. A json file with all the tweets as json objects
'''

import json
import sys
import tweepy
import langid
import csv
import codecs
import re
import time
from datetime import date

consumer_key = 'VzDPMM4UPSxFRInnoPBrtZhMG'
consumer_secret = 'umbtMHt6rmHbOlMQ0YToj5s9qT2ysl3ZRFDawqVOmsMohVojqc'
access_key = "1359041948-ZVZzpVVVHJ1iRUNW0KFxKdUgiCFcgTPzUicLQK7"
access_secret = "WUyHHgEvJwgdpWvpuTU3QR25bkH2sCUrWp1tttT8ccQV0"


auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)


# open log file
logfile = open('twython.log', 'a')


class CustomStreamListener(tweepy.StreamListener):
    '''This class creates a connection to the Twitter Streaming API.'''
    print("Starting the Stream")
    def on_status(self, status):
        '''Start checking and collecting, if a tweet comes in'''
        global old_date

        # Set global vars for the filewriters
        global writer_pos
        global writer_neg
        global outfile_pos
        global outfile_neg
        global outfile_json_pos
        global outfile_json_neg
        global outfile_json_not_pos
        global writer_not_pos
        global outfile_not_pos

        new_date = date.today()
        if not new_date == old_date:
            # create a new file with current date, if new day
            outfile_pos.close
            outfile_json_pos.close()
            outfile_neg.close
            outfile_json_neg.close()
            outfile_not_pos.close()
            outfile_json_not_pos.close()

            outfile_pos = codecs.open ("txt/tweets-pos-" + str(new_date) + ".txt", "ab", "utf-8")
            outfile_json_pos = codecs.open ("json/tweets-pos-" + str(new_date) + ".json", "ab", "utf-8")
            outfile_neg = codecs.open ("txt/tweets-neg-" + str(new_date) + ".txt", "ab", "utf-8")
            outfile_json_neg = codecs.open ("json/tweets-neg-" + str(new_date) + ".json", "ab", "utf-8")
            outfile_not_pos = codecs.open("txt/tweets-not-pos-"+str(new_date)+".txt", "ab", "utf-8")
            outfile_json_not_pos = codecs.open ("json/tweets-not-pos-" + str(new_date) + ".json", "ab", "utf-8")

            writer_pos = csv.writer(outfile_pos,quoting=csv.QUOTE_NONNUMERIC,lineterminator='\n')
            writer_neg = csv.writer(outfile_neg,quoting=csv.QUOTE_NONNUMERIC,lineterminator='\n')
            writer_not_pos = csv.writer(outfile_not_pos,quoting=csv.QUOTE_NONNUMERIC,lineterminator='\n')

            old_date = new_date

        try:
            # Use the langid package to guess the tweets language
            lang = langid.classify(status.text)[0];
            # Check, if this is a 'just url' tweet
            url_tweet = re.compile(r"^http:\/\/[a-zA-Z0-9.\/]*\s+(#[a-zA-Z0-9]+\s*)*$")
            
            if lang == "de" and 'RT @' not in status.text and status.retweeted is False and not re.search(url_tweet, status.text):
                # If tweet is german and not a retweet
                if re.search(r'#nicht\b', status.text.lower()) or re.search(r'#not\b', status.text.lower()) or '#ironie' in status.text.lower() \
                            or '#ironisch' in status.text.lower()\
                            or '#sarkasmus' in status.text.lower() or '#sarkastisch' in status.text.lower() \
                            or '#irony' in status.text.lower() or '#ironic' in status.text.lower() \
                            or '#sarcasm' in status.text.lower() or '#sarcastic' in status.text.lower():

                    # collect the positive samples and write them to a file
                    print ("POSITIVE SAMPLE "+ status.text.replace('\n',' '))
                    writer_pos.writerow( (status.created_at, status.id_str, status.text.replace('\n',' ')) )
                    outfile_json_pos.write(json.dumps(status._json, indent=4))
                    outfile_pos.flush()
                    outfile_json_pos.flush()

                if '#witz' in status.text.lower() or '#joke' in status.text.lower() or '#humor' in status.text.lower() \
                            or '#education' in status.text.lower() or '#bildung' in status.text.lower()\
                            or '#science' in status.text.lower() or '#wissenschaft' in status.text.lower() \
                            or '#sport' in status.text.lower():

                    # Collect the negative samples and write them to a file
                    print ("NEGATIVE SAMPLE "+ status.text.replace('\n',' '))
                    writer_neg.writerow( (status.created_at, status.id_str, status.text.replace('\n',' ')) )
                    outfile_json_neg.write(json.dumps(status._json, indent=4))
                    outfile_neg.flush()
                    outfile_json_neg.flush()


                if not re.search(r'#nicht\b', status.text.lower()) or not re.search(r'#not\b', status.text.lower()) or not '#ironie' in status.text.lower() \
                            or not '#ironisch' in status.text.lower()\
                            or not '#sarkasmus' in status.text.lower() or not '#sarkastisch' in status.text.lower() \
                            or not '#irony' in status.text.lower() or not '#ironic' in status.text.lower() \
                            or not '#sarcasm' in status.text.lower() or not '#sarcastic' in status.text.lower():

                    # Collect not positive samples and write them to a file
                    #print ("NOT POSITIVE SAMPLE "+ status.text.replace('\n',' '))
                    writer_not_pos.writerow( (status.created_at, status.id_str, status.text.replace('\n',' ')) )
                    outfile_not_pos.flush()
                    outfile_json_not_pos.write(json.dumps(status._json, indent=4))
                    outfile_json_not_pos.flush()



        except Exception as e:
            # Catch any unicode errors while printing to console
            # and just ignore them to avoid breaking application.
            #sys.exc_clear()
            print(e)
            pass


    def on_error(self, status_code):
        '''If an error occurs, write the error message to the log file, but do not kill the stream'''
        print (status_code)
        logfile.write(str(time.asctime( time.localtime(time.time()) )) + ' Encountered error with status code:' + str(status_code) + "\n")
        return True # Don't kill the stream

    def on_timeout(self):
        '''If a timeout occurs, write it to the log file, but do not kill the stream'''
        logfile.write(str(time.asctime( time.localtime(time.time()) )) + ' Timeout...' + "\n")
        return True # Don't kill the stream



# Get the local time for the filename
localtime = time.asctime( time.localtime(time.time()) )
logfile.write( localtime + " Tracking terms from ../twython-keywords.txt\nStarting stream \n")

# longer timeout to keep SSL connection open even when few tweets are coming in
stream = tweepy.streaming.Stream(auth, CustomStreamListener(), timeout=1000.0)

# Extract the terms to filter from the stopwordlist
terms = [line.strip() for line in open('../rsrc/twython-stopwords.txt')]

# open output files for positive not positive and negative samples
old_date = date.today()
outfile_pos = codecs.open ("txt/tweets-pos-" + str(old_date) + ".txt", "ab", "utf-8")
outfile_json_pos = codecs.open ("json/tweets-pos-" + str(old_date) + ".json", "ab", "utf-8")

outfile_neg = codecs.open ("txt/tweets-neg-" + str(old_date) + ".txt", "ab", "utf-8")
outfile_json_neg = codecs.open ("json/tweets-neg-" + str(old_date) + ".json", "ab", "utf-8")

outfile_not_pos = codecs.open ("txt/tweets-not-pos-" + str(old_date) + ".txt", "ab", "utf-8")
outfile_json_not_pos = codecs.open ("json/tweets-not-pos-" + str(old_date) + ".json", "ab", "utf-8")


writer_pos = csv.writer(outfile_pos,quoting=csv.QUOTE_NONNUMERIC,lineterminator='\n')
writer_neg = csv.writer(outfile_neg,quoting=csv.QUOTE_NONNUMERIC,lineterminator='\n')
writer_not_pos = csv.writer(outfile_not_pos,quoting=csv.QUOTE_NONNUMERIC,lineterminator='\n')
 

# Start the stream
stream.filter(track=terms, stall_warnings=True)
