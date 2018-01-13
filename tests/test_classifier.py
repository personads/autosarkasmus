import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from autosarkasmus.classifier.svm_classifier import SVMClassifier

Classifier = SVMClassifier(['Cluster-1','Intensifiers','class'],'rbf',-1,True)

Classifier.train([{"Intensifiers": 1, "Cluster-1": 1, "class": "sarcastic"},{'Cluster-1': 2, 'Intensifiers': 3, "class": "sarcastic"},{'Cluster-1': 4, 'Intensifiers': 1, "class": "sarcastic"},{'Cluster-1': 0, 'Intensifiers': 3, "class": "sarcastic"},{'Cluster-1': 2.5, 'Intensifiers': 5.5, "class": "non-sarcastic"},{'Cluster-1': 5, 'Intensifiers': 4, "class": "non-sarcastic"},{'Cluster-1': 4, 'Intensifiers': 6.5, "class": "non-sarcastic"},{'Cluster-1': 6, 'Intensifiers': 7, "class": "non-sarcastic"}])

print(Classifier.classify([{"Cluster-1": 1, "Intensifiers": 8}, {"Cluster-1": 0, "Intensifiers": 1}, {"Cluster-1": 5, "Intensifiers": 1}, {"Cluster-1": 0, "Intensifiers": 6.5}]))
