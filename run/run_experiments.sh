#!/bin/bash

RSRC_DIR=/softpro/ss16/swp-ss16-srk/autosarkasmus/autosarkasmus/rsrc/
CORPUS_POS=/softpro/ss16/swp-ss16-srk/autosarkasmus/autosarkasmus/corpus/txt/reviewed_corpus_files/tweets_pos_3099random.txt
CORPUS_NEG=/softpro/ss16/swp-ss16-srk/autosarkasmus/autosarkasmus/corpus/txt/reviewed_corpus_files/tweets_not-pos_3099random.txt
EMBEDDINGS=../rsrc/polyglot-de-dict.pkl

if [ ! -d "$RSRC_DIR" ]; then
    echo "error: please verify that the resource directory (e.g. /softpro) is mounted"
    exit
fi

ln -s $RSRC_DIR ../rsrc

# python run_experiment.py expsvm $CORPUS_POS $CORPUS_NEG $EMBEDDINGS 10 svm | tee autosarkasmus_experiments.log

# python run_experiment.py expmlp $CORPUS_POS $CORPUS_NEG $EMBEDDINGS 10 mlp | tee autosarkasmus_experiments.log

python run_experiment.py exprnn $CORPUS_POS $CORPUS_NEG $EMBEDDINGS 10 rnn | tee autosarkasmus_experiments.log

echo "please check autosarkasmus_experiments.log for results"
