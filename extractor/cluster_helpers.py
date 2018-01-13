# -*- coding: utf-8 -*-
'''
Cluster Helpers (functions)

Functions that help with clusters.
'''

#  This file can be found in our projectfolder in /softpro/ss16/swp-ss16-srk/autosarkasmus/autosarkasmus/baseline/rsrc
CLUSTER_FILE = '../rsrc/lda-topics-10-50.v2'

# Get the number of clusters
def load_number_of_clusters():
    '''Load the number of clusters from the file and return it'''
    res = []
    maximum = 0
    with open(CLUSTER_FILE, 'r', encoding='latin-1') as fop:
        for line in fop:
            res.append(int(line.strip().split("\t")[2]))

    return max(res)

def load_clusters():
    '''Construct the cluster keys'''
    res = []
    for no in range(0,load_number_of_clusters()+1):
        res.append('cluster-' + str(no))

    return res


def cluster_map():
    '''create cluster lists'''
    cluster_map = {}
    with open(CLUSTER_FILE, 'r', encoding='latin-1') as fop:
        for line in fop:
            no = int(line.strip().split("\t")[2])
            token = line.strip().split("\t")[1]
            cluster_map[token] = no


    return cluster_map
