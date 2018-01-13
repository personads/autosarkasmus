# -*- coding: utf-8 -*-
'''
SentiWS Helpers (functions)

Functions that help with processing the SentiWS list.

R. Remus, U. Quasthoff & G. Heyer: SentiWS - a Publicly Available German-language Resource for Sentiment Analysis.
In: Proceedings of the 7th International Language Ressources and Evaluation (LREC'10), pp. 1168--1171, 2010
http://asv.informatik.uni-leipzig.de/download/sentiws.html
'''
SENTIWS_FILE_POS = '../rsrc/SentiWS_v1.8c_Positive.txt'
SENTIWS_FILE_NEG = '../rsrc/SentiWS_v1.8c_Negative.txt'

def load_sentiws_file(filename):
    '''Load the sentiws file'''
    res = {}
    with open(filename, 'r', encoding='utf8') as fop:
        for line in fop:
            line_parts = line.split('\t')
            keys = [line_parts[0].split('|')[0].lower()]
            if len(line_parts) > 2:
                for inflection in line_parts[2].split(','):
                    keys.append(inflection.lower())
            for key in keys:
                res[key] = float(line_parts[1])
    return res

def load_sentiws():
    '''Load the sentiws and return them as a list'''
    res = {}
    res_pos = load_sentiws_file(SENTIWS_FILE_POS)
    res_neg = load_sentiws_file(SENTIWS_FILE_NEG)
    res.update(res_pos)
    res.update(res_neg)
    return res
