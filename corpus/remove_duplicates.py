''' 
RemoveDuplicateTweets(class)

Remove duplicate tweets and write them to a new file
'''

import re, difflib, itertools, time, sys
from csv import reader, writer
import csv


class RemoveDuplicateTweets():
    '''This class has methods to remove similar and duplicate tweets and write them to a new file'''

    def __init__(self, filename):
        '''
		Constructor of RemoveDuplicateTweets

		Keyword arguments:
		filename (str): path to the corpus file
        '''
        self.filename = filename
        self.res = []
        self.res_filtered = []


    def remove_dups(self):
        '''
		This method creates a list of all tweets in a file and removes urls, almost similar tweets and duplicate tweets. 
		It returns a list of filtered tweets
        '''
        try:
            # First we remove all the urls from the tweets
            with open(self.filename) as f:
                for line in reader(f):
                    line[2] = re.sub(r'https:\/\/t.co\/\w+', '', line[2])
                    self.res.append(line)

            start = time.clock()
            for i, j in zip(self.res,self.res[1:]):
                    sm = difflib.SequenceMatcher(None,i[2],j[2]).ratio()
                    if sm < 0.9 and i not in self.res_filtered and j not in self.res_filtered or sm is 1.0:
                        self.res_filtered.append(i)


            for i,j in itertools.combinations(self.res_filtered, 2):
                    sm = difflib.SequenceMatcher(None,i[2],j[2]).ratio()
                    if sm > 0.9 and i in self.res_filtered:
                        self.res_filtered.remove(i)
                        print("Removed Tweet: ",i[2])

            end = time.clock()
            print("Time passed for cleaning Tweets:  ",end-start)
            self.res_filtered = list(self.res_filtered)

            return self.res_filtered

        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise

    def similarity(self,a,b):
        '''Meassure the similarity between two tweets using difflib'''
        sm = difflib.SequenceMatcher(None,a[2],b[2]).ratio()
        if sm > 0.9:
            return True
        else:
            return False

    def write(self):
        '''This method writes a list of tweets to a file'''
        try:
            # Write the filtered list to a file
            with open(self.filename+"cleaned", "w") as f:
                csvwriter = writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
                for line in self.remove_dups():
                    csvwriter.writerow(line)
            print("Saved new Tweets to: ", self.filename+".cleaned")

            print("Number of Tweets in old file: ",len(self.res))
            print("Number of filtered Tweets ",len(self.res_filtered))
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise

if __name__ == '__main__':
    if len(sys.argv) == 2:
        Rd = RemoveDuplicateTweets(sys.argv[1])
        Rd.write()
    else:
        print("Please enter a valid filename")
