'''
Xvalidator(class)
legacy version

Split dataset into k-fold sets
'''


class LegacyXvalidator:
    '''
    This class splits your dataset into k-fold training and test sets.

	To see the Xvalidator running, there is an example script (test_classify_tweets.py) in the tests/ folder.
    '''

    def __init__(self, dataset_one, folds, dataset_two=[]):
        '''
	Constructor of the Xvalidator class

	Keyword arguments:
	dataset_one (list):  dataset
	dataset_two (list);  second dataset (optional)
	folds (int): number of folds for crossvalidation
        '''
        self.K = folds
        self.X_one = dataset_one
        self.X_two = dataset_two

    # Thanks to John Reid for this code snippet: http://code.activestate.com/recipes/521906-k-fold-cross-validation-partition/
    def k_fold_cross_validation(self):
        '''
        Generates K (training, validation) pairs from the items in X_one and optionaly X_two.

        Each pair is a partition of X, where validation is an iterable
        of length len(X)/K. So each training iterable is of length (K-1)*len(X)/K.

        If randomise is true, a copy of X is shuffled before partitioning,
        otherwise its order is preserved in training and validation.
        '''

        for k in range(self.K):
            if len(self.X_two) > 0:
                training_one = [x for i, x in enumerate(self.X_one) if i % self.K != k]
                validation_one = [x for i, x in enumerate(self.X_one) if i % self.K == k]
                training_two = [x for i, x in enumerate(self.X_two) if i % self.K != k]
                validation_two = [x for i, x in enumerate(self.X_two) if i % self.K == k]
            else:
                training = [x for i, x in enumerate(self.X_one) if i % self.K != k]
                validation = [x for i, x in enumerate(self.X_one) if i % self.K == k]

            if len(self.X_two) > 0:
                yield training_one, validation_one, training_two, validation_two
            else:
                yield training, validation
