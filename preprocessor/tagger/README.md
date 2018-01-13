tagger
==========
runs the tree tagger by Helmut Schmid / LMU (1995) and uses the stts-universal tagset mapping by Petrov et al. (2011)


* **accuracy_baseline.py**
First finds out most frequent pos tag for baseline and then writes a new file ('most-freq_baseline.tagged') with the most frequent pos tag which is NOUN in order to enable an evaluation between those two files.

* **accuracy_pipe.py**
Activates our pipeline to prepare an output file for tagger evaluation.
Input: gold_corpus.raw
Output: our_tagger_output.tagged

* **tagger_accuracy.py**
Computes the accuracy for either baseline or our treetagger implementation.
First argument: output to be compared to baseline (in our case "our_tagger_output.tagged")
Second argument: gold standard annotations (usually "gold_corpus.tags")

* **tagger_m.py**
Wrapper class for TreeTagger with mapping.
Version which the pipeline also uses.
Usage: tagger_m.py <mapping_file> (e.g. "de-tiger.map")

* **tagger_n.py**
Old version of TreeTagger implementation.

==========

Further files:

* **accuracy_neg.tags**
Gold standard data comparison - between TreeTagger annotation (2nd column) and Gold annotation (3rd column) with lemma in 1st column - with respect to differing tags.

* **comparison.txt**
Gold standard data comparison with one lemma per line.

* **comparison_baseline.txt**
Tagger accuracy with most frequent pos tag (NOUN) baseline

* **comparison_univ.txt**
Final tagger accuracy

* **gold_corpus.raw**
Gold standard data with one tweet per line

* **gold_corpus.tags**
Gold standard data annotated in original STTS (Ines Rehbein) with one lemma per line and one blank line between tweets

* **gold_corpus_universal.tags**
Gold standard data annotated in Universal tagset (Slav Petrov with modifications) with one lemma per line and one blank line between tweets.

* **most-freq_baseline.tagged**
Gold standard data with only most frequent pos tag (NOUN) annotations with one lemma per line and one blank line between tweets.

* **our_tagger_output.tagged**
Gold standard data after being put through our pipeline, with modified Universal tagset with one lemma per line and one blank line between tweets.