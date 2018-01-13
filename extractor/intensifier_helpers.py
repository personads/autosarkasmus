# -*- coding: utf-8 -*-
'''
Intense Helpers (functions)

Functions that help with intensifiers.
'''
INTENSIFIERS_FILE = '../rsrc/german_intensifiers.txt'

def load_intensifiers():
    '''Load intensifiers from the file and return them as a list'''
    res = []
    with open(INTENSIFIERS_FILE, 'r', encoding='utf8') as fop:
        for line in fop:
            if not line.startswith('#'):
                res.append('intensifier-' + line.strip().lower())
    return res
