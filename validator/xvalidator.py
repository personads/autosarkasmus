'''
XValidator (class)

Helper class for cross-validation
'''
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import random, pickle

class XValidator:
    '''
    Cross-Validator

    Given a number of folds, a list of data points and a list of classifiers this class autmatically performs a k-fold cross-validation and saves the results in a directory specified by the experiment's name.
    '''

    def __init__(self, folds, data, classifiers, name="xvalidator", randomize=True, verbose=False):
        '''
        XValidator (Constructor)

        Keyword arguments:
            folds (int): number of folds
            data (list): list of data points
            classifiers (list): {'name': 'classy', 'classifier': Classifier()} list of classifiers
            name (str): name of XValidator instance (also result directory prefix)
            randomize (bool): flag for data randomization
            verbose (bool):stdout verbosity
        '''
        self.folds = folds
        self.data = data # [{'*', 'class'}]
        self.classifiers = classifiers # [{'name', 'classifier'}]
        self.results = {}
        for fold in list(range(self.folds)) + ['final']:
            self.results[fold] = {}
            for classifier in self.classifiers:
                self.results[fold][classifier['name']] = {
                    'precision': 0.,
                    'recall': 0.,
                    'accuracy': 0.,
                    'fone': 0.
                }
        self.name = name
        self.randomize = randomize
        self.verbose = verbose
        try:
            os.mkdir(self.name)
        except:
            print("error: could not create experiment directory")
        for classifier in self.classifiers:
            os.mkdir(self.name + '/' + classifier['name'])
            classifier['classifier'].save(self.name + '/' + classifier['name'] + '/default.ckpt')

    def _save_data(self, data, path):
        pickle.dump(data, open(path, 'wb'))

    def _prepare_data(self):
        if self.verbose: print("splitting data into", self.folds, "folds...")
        res = []
        if self.randomize:
            random.shuffle(self.data)
        split_size = 1./self.folds*len(self.data)
        for fold in range(self.folds):
            res.append(self.data[int(round(fold*split_size)):int(round((fold+1)*split_size))])
        return res

    def evaluate(self, truth_data, class_results):
        precision, recall, accuracy, fone = 0., 0., 0., 0.
        tp, fp, tn, fn = 0., 0., 0., 0.
        for data_i in range(len(truth_data)):
            if truth_data[data_i]['class'] and class_results[data_i]['class']:
                tp += 1
            if (not truth_data[data_i]['class']) and (not class_results[data_i]['class']):
                tn += 1
            if (not truth_data[data_i]['class']) and class_results[data_i]['class']:
                fp += 1
            if truth_data[data_i]['class'] and (not class_results[data_i]['class']):
                fn += 1
        precision = tp / (tp + fp)
        recall = tp / (tp + fn)
        accuracy = (tp + tn) / len(truth_data)
        fone = (2 * tp) / (2 * tp + fp + fn)
        return precision, recall, accuracy, fone

    def run(self):
        if self.verbose: print("running cross-validation...")
        split_data = self._prepare_data()
        for fold in range(self.folds):
            train_data = []
            for split_i, split in enumerate(split_data):
                if split_i == fold:
                    continue
                train_data += split
            test_data = split_data[fold]
            if self.verbose: print("- fold", str(fold+1) + "/" + str(self.folds), "with", str(len(train_data)) + "/" + str(len(test_data)), "split")
            for classifier in self.classifiers:
                if self.verbose: print("training classifier:", classifier['name'])
                classifier['classifier'].restore(self.name + '/' + classifier['name'] + '/default.ckpt')
                classifier['classifier'].train(train_data)
                if self.verbose: print("evaluating classifier:", classifier['name'])
                class_results = classifier['classifier'].classify(test_data)
                eval_precision, eval_recall, eval_accuracy, eval_fone = self.evaluate(test_data, class_results)
                # save results
                self.results[fold][classifier['name']]['precision'] = eval_precision
                self.results[fold][classifier['name']]['recall'] = eval_recall
                self.results[fold][classifier['name']]['accuracy'] = eval_accuracy
                self.results[fold][classifier['name']]['fone'] = eval_fone
                # update final results
                self.results['final'][classifier['name']]['precision'] += (eval_precision/self.folds)
                self.results['final'][classifier['name']]['recall'] += (eval_recall/self.folds)
                self.results['final'][classifier['name']]['accuracy'] += (eval_accuracy/self.folds)
                self.results['final'][classifier['name']]['fone'] += (eval_fone/self.folds)
                if self.verbose: print("precision:", eval_precision, "| recall:", eval_recall, "| accuracy:", eval_accuracy, "| f1-score:", eval_fone)
        if self.verbose:
            print("- final results")
            for classifier in self.classifiers:
                print(classifier['name'])
                print("  precision:", self.results['final'][classifier['name']]['precision'])
                print("  recall:", self.results['final'][classifier['name']]['recall'])
                print("  accuracy:", self.results['final'][classifier['name']]['accuracy'])
                print("  f1-score:", self.results['final'][classifier['name']]['fone'])
        if self.verbose: print("saving results...")
        self._save_data(self.results, self.name + '/results.pkl')
        if self.verbose: print("saving split-data...")
        self._save_data(split_data, self.name + '/split_data.pkl')
