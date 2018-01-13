classifier
==========
a module for classifying tweets based in their extracted feature vectors

Components
----------
* **mlp_classifier**  
    A Multi-Layer Perceptron based classifier implemented in TensorFlow that accepts feature vectors in the autosarkasmus format.
* **rnn_classifier**  
    A Multi-Layer Recurrent Neural Network based classifier implemented in TensorFlow that accepts normalized tweets in the autosarkasmus format.
* **svm_classifier**  
    A wrapper class for sklearn's SVM Classifier that accepts feature vectors in the autosarkasmus format.

Usage
-----
The SVMClassifier and MultiLayerPerceptronClassifier can be used in the following manner (after sourcing the virtual environment):

    from autosarkasmus.classifier.mlp_classifier import MultiLayerPerceptronClassifier
    from autosarkasmus.classifier.svm_classifier import SVMClassifier

    features = ['feature-0', 'feature-1']
    tweets_train = [
        {
            'feature-0': 0,
            'feature-1': 1,
            'class': True
        },
        {
            'feature-0': 1,
            'feature-1': 0,
            'class': False
        }
    ]
    tweets_test = [
        {
            'feature-0': 2,
            'feature-1': 3
        },
        {
            'feature-0': -1,
            'feature-1': -2
        }
    ]

    mlp_classifier = MultiLayerPerceptronClassifier(features)
    mlp_classifier.train(tweets_ext)
    tweets_class = mlp_classifier.classify(tweets_ext)

    svm_classifier = SVMClassifier(features)
    svm_classifier.train(tweets_ext)
    tweets_class = svm_classifier.classify(tweets_ext)

The *tweets_class* variable will contain a list of feature vectors equal to *tweets_ext*, but with the addition of the *class* attribute with its value being the class assigned by the classifier.  

The RecurrentNeuralNetworkClassifier can be used in a similar manner, the difference being that it only requires the normalized tweets and pre-trained word-embeddings.

    from autosarkasmus.classifier.rnn_classifier import RecurrentNeuralNetworkClassifier

    embeddings = {
        'word': [1, 0, 1, 0]
    }

    tweets_proc = [
        {
            'tweet': [
                ('foo', 'POS'),
                ('bar', 'POS')
            ],
            'class': True
        }
    ]

    rnn_classifier = RecurrentNeuralNetworkClassifier(embeddings)
    rnn_classifier.train(tweets_proc)
    tweets_class = rnn_classifier.classify(tweets_proc)

    The *tweets_class* variable will contain a list equal to *tweets_proc*, but with the determined *class* attribute and the fields 'sarcastic-prob' and 'non-sarcastic-prob'.
