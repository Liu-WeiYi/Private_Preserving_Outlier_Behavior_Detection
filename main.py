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
from statistics import mean
import Abnormal_Scenario_Generation as ASG

def main(normal_path, abnormal_path, synthetic_type):
    """
    main entry

    @param normal_path
    @param abnormal_path
    """
    normal_files = glob.glob(normal_path+'/*.gml')
    abnormal_files = glob.glob(abnormal_path+'/*.gml')

    # UPDATE: 2017-10-17 add time statistics #
    analysis_time = []
    # UPDATE END #


    # --------------------- #
    # Get Community Score
    # --------------------- #
    for file in normal_files:
        startTime = time.time()
        print('current file:\t', file)
        # read network
        network = nx.read_gml(file) # all layer in one. Easy to parse coms
        # get score
        score_set, score_com = ASG.Detection_Outliers(network)

        time_inverval = time.time()-startTime
        analysis_time.append(time_inverval)

        # For DEBUG
        # for s in set(score_set):
        #     print('score: ', s)
        #     for com in score_com[s]:
        #         print('\t',com)
        # print('\n')
        # END DEBUG

    # --------------------- #
    # Get Evaluation
    # --------------------- #
    # Precision, Recall, F1 = ASG.synthetic_nodes(normal_path,synthetic_type)
    # print('avg Precision:\t', mean(Precision))
    # print('avg Recall:\t', mean(Recall))
    # print('avg F1:\t', mean(F1))

    # Time Output #
    min_time = min(analysis_time)
    max_time = max(analysis_time)
    avg_time = mean(analysis_time)
    sum_time = sum(analysis_time)

    print('min_time:   ',min_time)
    print('avg_time:   ',avg_time)
    print('max_time:   ',max_time)
    print('sum_time:   ',sum_time)
if __name__ == "__main__":

    normal_path = 'Normal_Example'
    abnormal_path = 'Abnormal_Example'

    synthetic_type = "Nodes"
    # synthetic_type = "Edges"
    # synthetic_type = "Mix"

    main(normal_path, abnormal_path, synthetic_type)