import sys
import os
import csv
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from autosarkasmus.validator.Xvalidator import Xvalidator

data = ['One_pos', 'Two_pos', 'Three_pos', 'Four_pos', 'Five_pos', 'Six_pos']

k = 6
  
for training, validation in Xvalidator(data, k).k_fold_cross_validation():
    print("Training: " + str(training))
    print("Validation: " + str(validation))
