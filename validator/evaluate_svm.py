'''

EvaluateSarcasmDetection(class)

This class uses the XValidator class to crossvalidate the dataset and output the tweettexts, including true and predicted labels and the precision,
recall, f1-score and accuracy of each fold. Additionally it outputs the most significant features for each fold

'''

import sys
import os
import csv
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from autosarkasmus.extractor.extract_features import setup_features as full_featured
from autosarkasmus.extractor.extract_features_unigrams import setup_features as unigram_featured
from autosarkasmus.extractor.feature_extractor import FeatureExtractor
from autosarkasmus.classifier.svm_classifier import SVMClassifier
from autosarkasmus.validator.legacy_xvalidator import LegacyXvalidator
from autosarkasmus.corpus.corpus_reader import CorpusReader


class EvaluateSarcasmDetection():
	'''
	This class uses the XValidator class to crossvalidate the dataset and output the tweettexts, including true and predicted labels and the precision,
	recall, f1-score and accuracy of each fold. Additionally it outputs the most significant features for each fold
	'''

	def __init__(self, pos_set, neg_set, k, outputfile, features="full_featured"):
		'''
		Constructor of SVMClassifier
        	Keyword arguments:
            	pos_set (str): the path to the positive corpusfile
            	neg_set (str): the path to the negative corpusfile
            	k (int): defines n-fold crossvalidation
            	outputfile (string): filename to save the results in
            	features (string) default= 'full_featured': Defines the set of features to validate on ('full_featured', 'unigram_featured')
        '''
		self.pos_set = CorpusReader(pos_set).date_id_text()
		self.neg_set = CorpusReader(neg_set).date_id_text()
		self.k = k
		self.outputfile = outputfile
		self.features = features

	def evaluate(self):
		'''start evaluation and output the results in a file'''
		try:
			# Count the folds
			n = 1
			# Create the outputfile
			f = open(self.outputfile, "w")

			# Set the finale score variables
			accuracy_res = 0
			precision_res = 0
			recall_res = 0
			f1_res = 0

			# Start the evaluation using Xvalidator
			for training_pos, validation_pos, training_neg, validation_neg in Xvalidator(self.pos_set, self.k, self.neg_set).k_fold_cross_validation():

				# Create temporary files to store the splitted datasets for classification
				training_pos_file = open ("temp_tweets-training-pos-"+str(n), "w")
				writer_pos_file = csv.writer(training_pos_file,quoting=csv.QUOTE_NONNUMERIC,lineterminator='\n')
				writer_pos_file.writerows(training_pos)

				training_pos_file.flush()

				training_neg_file = open ("temp_tweets-training-neg-"+str(n), "w")
				writer_neg_file = csv.writer(training_neg_file,quoting=csv.QUOTE_NONNUMERIC,lineterminator='\n')
				writer_neg_file.writerows(training_neg)

				training_neg_file.flush()

				validation_pos_file = open ("temp_tweets-validation-pos-"+str(n), "w")
				writer_validation_pos_file = csv.writer(validation_pos_file,quoting=csv.QUOTE_NONNUMERIC,lineterminator='\n')
				writer_validation_pos_file.writerows(validation_pos)

				validation_pos_file.flush()

				validation_neg_file = open ("temp_tweets-validation-neg-"+str(n), "w")
				writer_validation_neg_file = csv.writer(validation_neg_file,quoting=csv.QUOTE_NONNUMERIC,lineterminator='\n')
				writer_validation_neg_file.writerows(validation_neg)

				validation_neg_file.flush()

				# Extract feature list
				if self.features is "full_featured":
				    feature_list, feature_order = full_featured("temp_tweets-training-pos-"+str(n))
				elif self.features is "unigram_featured":
					feature_list, feature_order = unigram_featured("temp_tweets-training-pos-"+str(n))

				feature_extractor = FeatureExtractor(feature_list, feature_order)

				tweets_train_ext = feature_extractor.extract_features("temp_tweets-training-pos-"+str(n), "temp_tweets-training-neg-"+str(n), verbose=True)
				tweets_test_ext = feature_extractor.extract_features("temp_tweets-validation-pos-"+str(n), "temp_tweets-validation-neg-"+str(n), verbose=True)
				# Create lists, to store the labels for predicted and true classes
				y_true = []
				y_pred = []

				# Merge the validation dataset for classification
				validation = validation_pos + validation_neg

				# Set the line variable to write the results to a file
				line = ""


				line += "+++++++++++++++++++++BEGIN OF " + str(n) + " nth fold++++++++++++++++++++++++" + "\n"
				line += "---------------------REAL LABELS--------------------------------" + "\n"
				for tweet, y in zip(validation, tweets_test_ext):
					y_true.append(y['class'])
					line += "Tweet: " + tweet[2]
					line += "\n"
					line += "Label: " + str(y['class'])
					line += "\n"

				Classifier = SVMClassifier(feature_order,'linear',-1,False)
				Classifier.train(tweets_train_ext)
				classification_results = Classifier.classify(tweets_test_ext)

				training = training_pos + training_neg
				print("Validation "+str(len(validation)))
				print("Training "+str(len(training)))


				line += "----------------------PREDICTED LABELS--------------------------------" + "\n"
				for tweet, val in zip(validation, classification_results):
					y_pred.append(val['class'])

					line += "Tweet: " + tweet[2]
					line += "\n"
					line += "Label: " + str(val['class'])
					line += "\n"


				# Remove the temporary files
				os.remove("temp_tweets-training-pos-"+str(n))
				os.remove("temp_tweets-training-neg-"+str(n))
				os.remove("temp_tweets-validation-pos-"+str(n))
				os.remove("temp_tweets-validation-neg-"+str(n))

				# Show most significant features
				def show_most_informative_features(features, clf, n=20):
					feature_names = features
					output = "Most significant features: \n"
					coefs_with_fns = sorted(zip(clf.coef_[0], feature_names))
					top = zip(coefs_with_fns[:n], coefs_with_fns[:-(n + 1):-1])
					for (coef_1, fn_1), (coef_2, fn_2) in top:
						output += "\t%.4f\t%-15s\t\t%.4f\t%-15s" % (coef_1, fn_1, coef_2, fn_2) + "\n"
					return output

				# Calculate the current scores
				accuracy = accuracy_score(y_true, y_pred)
				print("Accuracy: "+str(accuracy))
				precision = precision_score(y_true, y_pred, average='binary', pos_label='sarcastic')
				print("Precision: "+str(precision))
				recall = recall_score(y_true, y_pred, average='binary', pos_label='sarcastic')
				print("Recall: "+str(recall))
				f1 = f1_score(y_true, y_pred, average='binary', pos_label='sarcastic')
				print("F1-Score: "+str(f1))


				# Calculate the final scores
				accuracy_res += accuracy
				precision_res += precision
				recall_res += recall
				f1_res += f1

				line += "Accuracy: " + str(accuracy) + "\n"
				line += "Precision: " + str(precision) + "\n"
				line += "Recall: " + str(recall) + "\n"
				line += "F1-Score: " + str(f1) + "\n"

				line += show_most_informative_features(feature_order, Classifier.svm)
				line += "++++++++++++++++++++++END OF " + str(n) + " nth fold++++++++++++++++++++++++++++++" + "\n"
				f.write(line)

				print(n)
				n += 1

			line = ""
			line += "Accuracy: " + str(accuracy_res/self.k) + "Precision: " + str(precision_res/self.k) + "Recall: " + str(recall_res/self.k) + "F1-Score: " + str(f1_res/self.k)

			f.write(line)
			f.close()

		except IOError as e:
			print("I/O error({0}): {1}".format(e.errno, e.strerror))

if __name__ == "__main__":
	'''
	# Start the evaluation of the unigram classifier
	print("Evaluation of the unigram classifier")
	Eval = EvaluateSarcasmDetection("../corpus/txt/reviewed_corpus_files/tweets_pos_3099random.txt", "../corpus/txt/reviewed_corpus_files/tweets_neg_3099random.txt", 10, "output_eval_unigram_neg.txt", "unigram_featured")
	Eval.evaluate()

	# Start the evaluation of the full featured classifier
	print("Evaluation of full featured classifier")
	Eval = EvaluateSarcasmDetection("../corpus/txt/reviewed_corpus_files/tweets_pos_3099random.txt", "../corpus/txt/reviewed_corpus_files/tweets_neg_3099random.txt", 10, "output_eval_full_neg.txt")
	Eval.evaluate()
    '''
