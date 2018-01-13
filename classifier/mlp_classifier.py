'''
    Multi-Layer Perceptron Classifier (class)
'''
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from autosarkasmus.classifier.tf_classifier import TensorFlowClassifier

import tensorflow as tf

class MultiLayerPerceptronClassifier(TensorFlowClassifier):
    '''
    Multi-Layer Perceptron based classifier
    '''

    def __init__(self, features, iterations=20000, hidden_size=100, learning_rate=0.1, verbose=False):
        '''
        Constructor of MultiLayerPerceptronClassifier

        Keyword arguments:
            features (list): features in a sample's feature vector
            iterations (int): number of training iterations
            learning_rate (float): learning rate for AdaGrad
            verbose (bool): stdout verbosity
        '''
        # init tensorflow classifier
        TensorFlowClassifier.__init__(self, features, iterations, verbose)
        # init tensorflow variables
        # -- init model
        self.hidden_size = hidden_size
        self.learning_rate = learning_rate
        self.tf_input = tf.placeholder(tf.float32, [None, len(self.features)])
        self.tf_var_w1 = tf.Variable(tf.truncated_normal([len(self.features), self.hidden_size], stddev=0.1))
        self.tf_var_b1 = tf.Variable(tf.constant(0.1, shape=[self.hidden_size]))
        self.tf_layer1 = tf.sigmoid(tf.matmul(self.tf_input, self.tf_var_w1) + self.tf_var_b1)
        self.tf_var_w2 = tf.Variable(tf.truncated_normal([self.hidden_size, 2], stddev=0.1))
        self.tf_var_b2 = tf.Variable(tf.constant(0.1, shape=[2]))
        self.tf_layer2 = tf.matmul(self.tf_layer1, self.tf_var_w2) + self.tf_var_b2
        self.tf_model = tf.nn.softmax(self.tf_layer2)
        # -- init loss and optimizer
        self.tf_truth = tf.placeholder(tf.float32, [None, 2])
        self.tf_cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=self.tf_model, labels=self.tf_truth))
        self.tf_train_step = tf.train.AdagradOptimizer(self.learning_rate).minimize(self.tf_cross_entropy)
        # -- init session
        self.tf_session = tf.Session()
        self.tf_session.run(tf.global_variables_initializer())

    def train(self, train_data, batch_size=100):
        '''
        Train the MLP on given data

        The training data must be a list of dicts with each containing the feature keys and their values for one data point.
        E.g. [{'feature-0': value}]

        Keyword arguments:
            training_data (list): training data points
            batch_size (int): size of training data batches
        '''
        # convert training data
        train_vectors, train_classes = self._convert_to_vectors(train_data)
        if self.verbose: print("training Multi-Layer Perceptron...")
        self.seek = 0
        for train_i in range(self.iterations):
            if self.verbose:
                sys.stdout.write('\riteration: %d of %d' % (train_i+1, self.iterations))
                sys.stdout.flush()
            # create batch
            cur_train_vectors, cur_train_classes = self._create_next_batch(train_vectors, train_classes, batch_size)
            # run training step
            self.tf_session.run(self.tf_train_step, feed_dict={self.tf_input: cur_train_vectors, self.tf_truth: cur_train_classes})
        if self.verbose: sys.stdout.write('\rtraining complete (%d iterations)'%(self.iterations) + (' ' * len(str(self.iterations)) + '\n'))

    def classify(self, class_data):
        '''
        Classify the given data

        The data must be a list of dicts with each containing the feature keys and their values for one data point.
        E.g. [{'feature-0': value}]

        Keyword arguments:
            class_data (list): classification data points
        '''
        res = []
        class_vectors, class_classes = self._convert_to_vectors(class_data)

        if self.verbose: print("predicting classes...")
        predict_classes = []
        predict_classes = self.tf_session.run(self.tf_model, feed_dict={self.tf_input: class_vectors})

        # add class attribute with appropriate value to original classification data
        for instance_index, instance in enumerate(class_data):
            res.append(dict(class_data[instance_index]))
            res[instance_index]['sarcastic-prob'] = predict_classes[instance_index][0]
            res[instance_index]['non-sarcastic-prob'] = predict_classes[instance_index][1]
            res[instance_index]['class'] = True if res[instance_index]['sarcastic-prob'] > res[instance_index]['non-sarcastic-prob'] else False

        return res
