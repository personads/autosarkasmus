'''
Computes the accuracy for either baseline or our treetagger implementation.

It is recommended to use the methods buildCorpus and compare separately!

First argument: output to be compared to baseline (in our case "our_tagger_output.tagged")
Second argument: gold standard annotations (usually "gold_corpus.tags")
'''
#!/usr/bin/python
import os
import sys
import subprocess
import re
import xml.etree.ElementTree as ET

class TaggerAccuracy:

    def __init__(self):
        self.goldInput = "twitter.gold.test.xml" # you need to add <root> </root> in XML file first, it's missing in our gold standard data
        self.goldRaw = "gold_corpus.raw" # XML file of gold standard data is being read and raw text is being written with one tweet per line.
        self.negTags = "accuracy_neg.tags" # differing tags are being saved here
        self.treeTags = sys.argv[1] # in our case "our_tagger_output.tagged" (see README)
        self.goldTags = sys.argv[2] # in our case "gold_corpus.tags" : The correct annotations according to gold standard data formatted as LEMMA <TAB> POSTAG.

    def buildCorpus(self): # reads XML input file
        tree = ET.parse(self.goldInput)
        root = tree.getroot()
        r = open(self.goldRaw, 'w', encoding='utf-8')
        t = open(self.goldTags, 'w', encoding='utf-8')
        for child in root:
            #r.write(",,\"")
            for subchild in child.findall('w'):
                r.write(subchild.get('lemma') + ' ')
                t.write(subchild.get('lemma') + '\t' + subchild.get('type') + '\n')
            r.write('\n')
            t.write('\n')

    def compare(self):
        """
        t : Einlesen der Golddaten, die von der Pipeline verarbeitet wurden (Tagging des TreeTaggers)
        g : Einlesen der Gold-Tags (Tagging, wie es im Goldstandard angegeben ist)
        """
        t = open(self.treeTags).readlines()
        t = [line for line in t if line != "\n"] # removes empty lines
        g = open(self.goldTags).readlines()
        g = [line for line in g if line != "\n"]
        n = open(self.negTags, 'w')
        n.write("Lemma" + '\t' + "TreeTagger" + '\t' + "Gold" + '\n\n')
        wc = 0 # wordcount
        pos = 0 # identical tags
        offset = 0 # ensures alignment
        
        for i in range(len(g)):
            wc += 1
            lemmaT = (t[i+offset].split('\t'))[0].strip()
            lemmaG = (g[i].split('\t'))[0].strip()
            treeTag = (t[i+offset].split('\t'))[1]
            goldTag = (g[i].split('\t'))[1]
            goldTag = goldTag.replace('\xc2\xa0', ' ') # removes non-breaking spaces
            if lemmaT == lemmaG:
                if treeTag == goldTag: # if tags between gold and treetagger are identical
                    pos += 1
                else: # if not, they're being written to "accuracy_neg.tags"
                    n.write(lemmaT + '\t' + treeTag.strip() + '\t' + '\t' + goldTag.strip() + '\n')
            else: # if the lemmata don't align, the offset tries to solve this problem in lines 55 and 57
                offset += 1
        
        accuracy = (pos/wc)*100 # compute accuracy
        print("Accuracy: " + str(accuracy) + " (" + str(pos) + " korrekt aus " + str(wc) + " Tokens)")
        n.close()

if __name__ == "__main__":
    acc = TaggerAccuracy()
    acc.buildCorpus()
    acc.compare()