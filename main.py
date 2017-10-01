# coding: utf-8
# author: weiyiliu@us.ibm.com

import sys
import os
import glob
import json
import pickle
import time
import networkx as nx
import matplotlib.pyplot as plt
import Abnormal_Scenario_Generation as ASG

def main(normal_path, abnormal_path):
    """
    main entry

    @param normal_path
    @param abnormal_path
    """
    normal_files = glob.glob(normal_path+'/*.gml')
    abnormal_files = glob.glob(abnormal_path+'/*.gml')

    # --------------------- #
    # Process normal People
    # --------------------- #
    for file in abnormal_files[0:2]:
        print('current file:\t', file)
        network = nx.read_gml(file)
        score_set, score_com = ASG.Detection_Outliers(network)

        # For DEBUG
        for s in set(score_set):
            print('score: ', s)
            for com in score_com[s]:
                print('\t',com)
        print('\n')
        # END DEBUG

if __name__ == "__main__":

    normal_path = 'Normal_Example'
    abnormal_path = 'Abnormal_Example'

    main(normal_path, abnormal_path)