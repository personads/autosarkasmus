#!/usr/bin/python
import operator

'''
First finds out most frequent pos tag for baseline
and then writes a new file ('most-freq_baseline.tagged') with the most frequent pos tag which is NOUN in order to enable an evaluation between those two files.
NOTE: For future implementations, the arg max function in l.23 may be saved in a variable and passed on to l.30.
'''

tagdict = {}
with open('our_tagger_output.tagged') as fop:
    for line in fop:
        anno = line.split('\t')
        if len(anno) > 1: # skips all lines which don't have sufficient annotations
            postag = anno[1].strip()
            if postag not in tagdict:
                tagdict.update({str(postag): 1}) # adds previously not existent tag
            else:
                tagdict[postag] = tagdict.get(postag, 0) + 1 # updates/increments existent tag
                
print(tagdict)
print("Most frequent POS tag is: " + max(tagdict.iteritems(), key=operator.itemgetter(1))[0])

with open('our_tagger_output.tagged') as fop:
    with open('most-freq_baseline.tagged', 'w') as fw:
        for line in fop:
            anno = line.split('\t')
            if len(anno) > 1:
                anno[1] = "NOUN" # change all tags to NOUN which is the most frequent pos tag
                fw.write(str(anno[0]) + '\t' + str(anno[1]) + '\n')
            else:
                fw.write('\n')
