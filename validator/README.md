xvalidator
==========
a module for spliting your dataset into k-fold training and test sets.

Components
----------
* **Xvalidator**  
    A helper class for cross-validating autosarkasmus classifiers.
* **LegacyXvalidator**  
* **EvaluateSarcasmDetection**  
    A wrapper class for sklearn's SVM Classifier that accepts feature vectors in the autosarkasmus format.

Usage
-----

The XValidator can be used in the following manner (after sourcing the virtual environment):
```python
from autosarkasmus.validator.xvalidator import XValidator

folds = 10
data = # load data (splits will be performed automatically)
classifiers = [
    {
        'name': 'classifier0',
        'classifier': Classifier()
    }
]

xvalidator = XValidator(folds, data, classifiers, 'experiment_name')
xvalidator.run()
```

The output will be a directory 'experiment_name' containing the split_data.pkl and results.pkl. The latter contains a dict with the following structure:

```python
results[fold][classifier['name']] = {
    'precision': 0.,
    'recall': 0.,
    'accuracy': 0.,
    'fone': 0.
}

results['final'][classifier['name']] = {
    'precision': 0.,
    'recall': 0.,
    'accuracy': 0.,
    'fone': 0.
}
```

The LegacyXvalidator can be used in the following manner (after sourcing the virtual environment):

```python
  from autosarkasmus.validator.Xvalidator_test import Xvalidator

  data = ['One_pos', 'Two_pos', 'Three_pos', 'Four_pos', 'Five_pos', 'Six_pos']

  k = 5

  for training, validation in Xvalidator(data, k).k_fold_cross_validation():
      print("Training: " + str(training))
      print("Validation: " + str(validation))
```

Output:

```
Training: ['Two_pos', 'Three_pos', 'Four_pos', 'Five_pos', 'Six_pos']
Validation: ['One_pos']
Training: ['One_pos', 'Three_pos', 'Four_pos', 'Five_pos', 'Six_pos']
Validation: ['Two_pos']
Training: ['One_pos', 'Two_pos', 'Four_pos', 'Five_pos', 'Six_pos']
Validation: ['Three_pos']
Training: ['One_pos', 'Two_pos', 'Three_pos', 'Five_pos', 'Six_pos']
Validation: ['Four_pos']
Training: ['One_pos', 'Two_pos', 'Three_pos', 'Four_pos', 'Six_pos']
Validation: ['Five_pos']
Training: ['One_pos', 'Two_pos', 'Three_pos', 'Four_pos', 'Five_pos']
Validation: ['Six_pos']
```

The Xvalidator will return splitted training and testsets in k-fold


The evaluation script can be run as follows:
```python
from autosarkasmus.evaluate.evaluatesarcasmdetection import EvaluateSarcasmDetection

# Start the evaluation of the unigram classifier
print("Evaluation of the unigram classifier")
Eval = EvaluateSarcasmDetection("../corpus/txt/reviewed_corpus_files/tweets_pos_3099random.txt", "../corpus/txt/reviewed_corpus_files/tweets_neg_3099random.txt", 10, "output_eval_unigram_neg.txt", "unigram_featured")
Eval.evaluate()
```


References
----------
1. Scikit Learn, http://scikit-learn.org/stable/
2. Code snippets from John Reid, http://code.activestate.com/recipes/521906-k-fold-cross-validation-partition/
