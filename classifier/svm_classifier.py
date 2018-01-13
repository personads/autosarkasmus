'''
    SVM Classifier (class)
'''
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from sklearn import svm
import numpy as np
import pickle

class SVMClassifier:
    '''
    Support Vector Machine based classifier
    '''

    def __init__(self, features, kernel_type='rbf', max_iter=-1, verbose=False):
        '''
        Constructor of SVMClassifier

        Keyword arguments:
            features (list): features in a sample's feature vector
            kernel_type (str): type of kernel to be used (default=‘rbf’, ‘linear’, ‘poly’, ‘sigmoid’, ‘precomputed’)
            max_iter (int): iteration limit for solver (default=-1, unlimited)
            verbose (bool): stdout verbosity
        '''
        self.features = [feature for feature in features if feature != 'class'] # add all features except for class
        self.svm = svm.SVC(kernel=kernel_type, max_iter=max_iter, verbose=verbose) # initialize SVM
        self.verbose = verbose

    def save(self, path):
        pickle.dump(self.svm, open(path, 'wb'))
        if self.verbose: print("saved model to '" + path + "'")

    def restore(self, path):
        self.svm = pickle.load(open(path, 'rb'), encoding='bytes')
        if self.verbose: print("restored model from '" + path + "'")

    def close(self):
        pass

    def train(self, training_data):
        '''
        Train the SVM on given data

        The training data must be a list of dicts with each containing the feature keys and their values for one data point.
        E.g. [{'feature-0': value}]

        Keyword arguments:
            training_data (list): training data points
        '''
        if self.verbose: print('converting training data to vectors...')
        training_vectors = []
        training_classes = []
        for instance in training_data:
            # create vector for current instance
            cur_training_vector = []
            for feature in self.features:
                cur_training_vector.append(instance[feature])
            training_vectors.append(cur_training_vector)
            # append current class to classes vector
            training_classes.append(instance['class'])
        if self.verbose: print('training SVM...')
        self.svm.fit(training_vectors, training_classes) # train the svm

    def classify(self, classification_data):
        '''
        Classify the given data

        The data must be a list of dicts with each containing the feature keys and their values for one data point.
        E.g. [{'feature-0': value}]

        Keyword arguments:
            classification_data (list): classification data points
        '''
        res = []
        if self.verbose: print('converting classification data to vectors...')
        classification_vectors = []
        classification_classes = []
        # convert dicts to vectors
        for instance in classification_data:
            cur_classification_vector = []
            for feature in self.features:
                cur_classification_vector.append(instance[feature])
            classification_vectors.append(cur_classification_vector)

        if self.verbose: print('predicting classes...')
        classification_classes = self.svm.predict(classification_vectors) # perform the classification

        # add class attribute with appropriate value to original classification data
        for instance_index, instance in enumerate(classification_data):
            res.append(dict(instance))
            res[instance_index]['class'] = classification_classes[instance_index]

        return res
