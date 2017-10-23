# coding: utf-8
# purpose: Define Different Types of Abnormal Scenario
# Author: weiyiliu@us.ibm.com

import networkx as nx
import glob
import random
import copy
import numpy as np
import sys
from sklearn.metrics import roc_auc_score
import time
from interruptingcow import timeout

from Algorithms.pylouvain import LouvainCommunities


def _synthetic_network(syntheticFlag, network, devices_number):
    """
    add synthetic nodes to network

    @param syntheticFlag
    @param network
    @param devices_number

    return modified network
    """
    abnormal_network = copy.deepcopy(network)
    if syntheticFlag == "add_edges":
        # randomly add edges with abnormal device
        node = "abnormal_device"
        if len(network.nodes()) >= devices_number:
            devices = random.sample(network.nodes(), devices_number)
        else:
            devices = random.sample(network.nodes(), 1)
        for device in devices:
            weight = random.uniform(0,1)
            abnormal_network.add_weighted_edges_from([(node, device, weight)])
    elif syntheticFlag == "add_isolated_nodes":
        node = "abnormal_device"
        abnormal_network.add_node(node)

    return abnormal_network



def Detection_Outliers(network):
    """
    detect outliers in a network

    @param network: weighted/merged network from multilayer network

    @return weight_list, weight_com
    """
    modify_weight_network = nx.Graph()
    for e in network.edges(data=True):
        u,v,W = e
        w=W['weight']
        if w == 0:
            modify_weight_network.add_edge(u,v,weight=1)
        elif w == 1:
           modify_weight_network.add_edge(u,v,weight=1)
        else:
            modify_weight_network.add_edge(u,v,weight=w/100)

    # 1. get community result
    """
    Fix Bug: Check Louvain... If stuck, restart to calculate... up to 10 times
    """
    start = time.time()
    restart_time = 10
    while restart_time > 0:
        try:
            with timeout(10, exception=RuntimeError):
                NodeCommunity, Modularity = LouvainCommunities(modify_weight_network)
                restart_time = 0
        except RuntimeError:
            sys.stdout.write('\r [!!!] Louvain needs reboot...remain %i / 10 times '%restart_time)
            sys.stdout.flush()
            restart_time -= 1
            NodeCommunity = [modify_weight_network.nodes()]
            Modularity = 0

    """FIX BUGS: Louvain Community Algorithm will omit isolated node"""
    ISO_Nodes = nx.isolates(network)
    if len(ISO_Nodes) != 0:
        for node in ISO_Nodes:
            NodeCommunity.append([node])
    # 2. get community score
    score_set  = set()
    score_com   = {}
    for com in NodeCommunity:
        current_score = 0
        for n1_idx in range(len(com)-1):
            for n2_idx in range(n1_idx+1, len(com)):
                n1 = com[n1_idx]
                n2 = com[n2_idx]
                if n2 in nx.neighbors(network, n1):
                    weight = network.get_edge_data(n1,n2)['weight']
                    current_score += weight
        score_set.add(current_score)
        if current_score not in score_com.keys():
            score_com[current_score] = []
        score_com[current_score].append(com)

    return score_set, score_com

def synthetic_nodes(normal_path, synthetic_type):
    """
    add new nodes, try to identify if the algorithm can detect it.

    @param normal_files: files that is normal
    @return precision, Recall, F1_score
    """
    Precision  = []
    Recall     = []
    F1         = []
    AUC        = []

    # all files
    networks = []
    normal_files = glob.glob(normal_path+'/*.gml')
    networks = [nx.read_gml(file) for file in normal_files]

    # Define How Many Times
    synthetic_times = 1000
    # Define How Many Devices
    devices_number = 1

    if synthetic_type == "Mix":
        syntheticFlags = [
            "add_edges",
            "add_isolated_nodes"
        ]
    elif synthetic_type == "Nodes":
        syntheticFlags = [
            "add_isolated_nodes"
        ]
    elif synthetic_type == "Edges":
        syntheticFlags = [
            "add_edges"
        ]

    for time in range(synthetic_times):
        syntheticFlag = random.sample(syntheticFlags,1)[0]
        # randomly choose one network
        network = random.sample(networks,1)[0]
        new_network = _synthetic_network(syntheticFlag, network, devices_number)

        # extract com
        score_set, score_coms = Detection_Outliers(new_network)
        min_score = sorted(score_set)[0]
        min_coms = score_coms[min_score]

        # calculate matric
        # 1. calculate all Recall
        recallFlag = False
        for com in min_coms:
            for node in com:
                if 'abnormal_device' in node:
                    recallFlag = True
                    break
        if recallFlag is True:
            Recall.append(1.0)
        else:
            Recall.append(0.0)

        # 2. calculate all Precision
        total_coms = len(min_coms)
        Precision.append(Recall[-1]/total_coms)

        # 3. calculate F1
        if Precision[-1] == 0 and Recall[-1] == 0:
            F1.append(0)
        else:
            F1.append(2*Precision[-1]*Recall[-1]/(Precision[-1]+Recall[-1]))

    return Precision, Recall, F1

