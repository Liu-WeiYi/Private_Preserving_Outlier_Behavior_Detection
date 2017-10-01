# coding: utf-8
# purpose: Define Different Types of Abnormal Scenario
# Author: weiyiliu@us.ibm.com

from Algorithms.pylouvain import LouvainCommunities

def add_different_Devices(current_user_time_based_device):
    """
    randomly add different devices :)

    @param current_user_time_based_device
    @return abnormal_embeded current_user_time_based_device
    """


def Detection_Outliers(network):
    """
    detect outliers in a network

    @param network: weighted/merged network from multilayer network
    """

   # --------------------- #
   # Community Detection
   # --------------------- #

   NodeCommunity, Modularity = LouvainCommunities(network)
   print('Current Modularity:\t', Modularity)
   print('Node Communities Info:\n', NodeCommunity)
