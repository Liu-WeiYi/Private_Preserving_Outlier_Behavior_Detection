# coding: utf-8
# purpose: Define Different Types of Abnormal Scenario
# Author: weiyiliu@us.ibm.com

import networkx as nx

from Algorithms.pylouvain import LouvainCommunities


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

        modify_weight_network.add_edge(u,v)

    # 1. get community result
    NodeCommunity, Modularity = LouvainCommunities(modify_weight_network)
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