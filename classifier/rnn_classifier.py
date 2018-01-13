'''
    Recurrent Neural Network Classifier (class)
'''
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from autosarkasmus.classifier.tf_classifier import TensorFlowClassifier

import tensorflow as tf

class RecurrentNeuralNetworkClassifier(TensorFlowClassifier):
    '''
    Recurrent Neural Network based classifier
    '''

    def __init__(self, embeddings, iterations=10000, hidden_size=100, layer_count=3, dropout_prob=0.5, learning_rate=0.5, verbose=False):
        '''
        Constructor of RecurrentNeuralNetworkClassifier

        Keyword arguments:
            embeddings (dict): {"word": numpy_array} embeddings
            iterations (int): number of training iterations
            hidden_size (int): size of the RNN cell
            layer_count (int): number of RNN cell layers
            dropout_prob (float): probablity of retaining output
            learning_rate (float): learning rate for AdaGrad
            verbose (bool): stdout verbosity
        '''
        # init tensorflow classifier
        TensorFlowClassifier.__init__(self, [], iterations, verbose)
        # init embeddings
        self.embeddings = embeddings
        self.embedding_size = len(self.embeddings['<UNK>'])
        # init tensorflow variables
        # -- init model
        self.hidden_size = hidden_size
        self.layer_count = layer_count
        self.dropout_prob = dropout_prob
        self.learning_rate = learning_rate
        self.max_length = 64
        self.tf_input = tf.placeholder(tf.float32, [None, self.max_length, self.embedding_size])
        # --- define multi-layer rnn with gru and dropout
        self.tf_rnn_cell = tf.contrib.rnn.GRUCell(num_units=self.hidden_size)
        self.tf_rnn_dropout = tf.contrib.rnn.DropoutWrapper(self.tf_rnn_cell, output_keep_prob=self.dropout_prob)
        self.tf_rnn = tf.contrib.rnn.MultiRNNCell([self.tf_rnn_cell] * self.layer_count)
        self.tf_rnn_out, self.tf_rnn_state = tf.nn.dynamic_rnn(
            self.tf_rnn,
            self.tf_input,
            dtype=tf.float32,
            sequence_length=self._get_seq_len(self.tf_input)
        )
        self.tf_rnn_out = self._get_seq_last(self.tf_rnn_out, self._get_seq_len(self.tf_input))
        # --- output layer
        self.tf_var_w1 = tf.Variable(tf.truncated_normal([self.hidden_size, self.hidden_size], stddev=0.1))
        self.tf_var_b1 = tf.Variable(tf.constant(0.1, shape=[self.hidden_size]))
        self.tf_layer1 = tf.sigmoid(tf.matmul(self.tf_rnn_out, self.tf_var_w1) + self.tf_var_b1)
        self.tf_var_w = tf.Variable(tf.truncated_normal([self.hidden_size, 2], stddev=0.1))
        self.tf_var_b = tf.Variable(tf.constant(0.1, shape=[2]))
        self.tf_layer_out = tf.matmul(self.tf_layer1, self.tf_var_w) + self.tf_var_b
        self.tf_model = tf.nn.softmax(self.tf_layer_out)
        # -- init loss and optimizer
        self.tf_truth = tf.placeholder(tf.float32, [None, 2])
        self.tf_cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=self.tf_model, labels=self.tf_truth))
        self.tf_train_step = tf.train.AdagradOptimizer(self.learning_rate).minimize(self.tf_cross_entropy)
        # -- init session
        self.tf_session = tf.Session()
        self.tf_session.run(tf.global_variables_initializer())

    def _get_seq_len(self, sequence):
        res = 0
        seq_binary = tf.sign(tf.reduce_max(tf.abs(sequence), axis=2)) # 1 if content, 0 if padding
        res = tf.reduce_sum(seq_binary, axis=1) # sum length of content
        return tf.cast(res, tf.int32)

    def _get_seq_last(self, output, lengths):
        res = None
        batch_size = tf.shape(output)[0]
        indices = tf.range(0, batch_size) * self.max_length + (lengths - 1) # determine cutoff indices
        states = tf.reshape(output, [-1, self.hidden_size]) # flatten to sequence
        res = tf.gather(states, indices)
        return res

    def _get_permutations(self, token):
        res = [token]
        res.append(token.lower())
        res.append(token[0].upper() + token[1:].lower())
        res.append(token.upper())
        return res

    def _convert_to_embeddings(self, data):
        if self.verbose: print("converting data to embeddings...")
        res_embeddings = []
        res_classes = []
        for instance in data:
            cur_embedding = []
            cur_class = [1,0] if instance['class'] else [0,1]
            for token, tag in instance['tweet']:
#                cur_token_embedding = self.embeddings['<UNK>']
                cur_token_embedding = self.embeddings.get(token, self.embeddings['<UNK>'])
                # check for possible permutations
#                for mut in self._get_permutations(token):
#                    if mut in self.embeddings:
#                        cur_token_embedding = self.embeddings[mut]
#                        break
                cur_embedding.append(cur_token_embedding)
            if len(cur_embedding) < self.max_length:
                cur_embedding += [[0. for j in range(self.embedding_size)] for i in range(self.max_length - len(cur_embedding))]
            res_embeddings.append(cur_embedding)
            res_classes.append(cur_class)
        return res_embeddings, res_classes

    def train(self, train_data, batch_size=100):
        '''
        Train the RNN on given data

        The training data must be a list of preprocessed tweets and classes.
        E.g. [{'tweet': [('text', 'NOUN')], 'class': True}]

        Keyword arguments:
            training_data (list): training data points
        '''
        # convert training data
        train_embeddings, train_classes = self._convert_to_embeddings(train_data)
        if self.verbose: print("training Recurrent Neural Network...")
        self.seek = 0
        for train_i in range(self.iterations):
            if self.verbose:
                sys.stdout.write('\riteration: %d of %d' % (train_i+1, self.iterations))
                sys.stdout.flush()
            # create batch
            cur_train_embeddings, cur_train_classes = self._create_next_batch(train_embeddings, train_classes, batch_size)
            # run training step
            self.tf_session.run(self.tf_train_step, feed_dict={self.tf_input: cur_train_embeddings, self.tf_truth: cur_train_classes})
        if self.verbose: sys.stdout.write('\rtraining complete (%d iterations)'%(self.iterations) + (' ' * len(str(self.iterations)) + '\n'))

    def classify(self, class_data):
        '''
        Classify the given data

        The data must be a list of preprocessed tweets and classes.
        E.g. [{'tweet': [('text', 'NOUN')], 'class': None}]

        Keyword arguments:
            classification_data (list): classification data points
        '''
        res = []
        class_embeddings, class_classes = self._convert_to_embeddings(class_data)

        if self.verbose: print("predicting classes...")
        predict_classes = []
        predict_classes = self.tf_session.run(self.tf_model, feed_dict={self.tf_input: class_embeddings})

        # add class attribute with appropriate value to original classification data
        for instance_index, instance in enumerate(class_data):
            res.append(dict(class_data[instance_index]))
            res[instance_index]['sarcastic-prob'] = predict_classes[instance_index][0]
            res[instance_index]['non-sarcastic-prob'] = predict_classes[instance_index][1]
            res[instance_index]['class'] = True if res[instance_index]['sarcastic-prob'] > res[instance_index]['non-sarcastic-prob'] else False

        return res
