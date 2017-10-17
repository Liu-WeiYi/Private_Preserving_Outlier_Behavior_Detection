# coding: utf-8
# author: weiyiliu@us.ibm.com

from __future__ import print_function
from __future__ import division

import sys
import pickle
import os
import json
import networkx as nx
import traceback
from datetime import datetime

import time

from utils import *
from Abnormal_Scenario_Generation import *

def extract_time(filenames, TEST_FLAG=True):
    """
    Extract all users ReachTime and DataTime Information

    @return all_user_id, all_user_statistic_file
    """
    all_user_id         = []
    all_user_time_info  = {}

    all_user_id_file    = 'all_user_id.txt'
    user_time_info_file = 'user_time_info.json'

    # for TEST USE ONLY
    if TEST_FLAG is True:
        all_user_id_file = '10_all_user_id.txt'
        user_time_info_file = '10_user_time_info.json'
    # END TEST USE

    if os.path.exists(user_time_info_file) and os.path.exists(all_user_id_file):
        with open(all_user_id_file,'r+') as f:
            for line in f.readlines():
                all_user_id.append(line.strip())

        all_user_time_info = json.load(open(user_time_info_file))
        print('--Done loading files:\t%s, %s'%(all_user_id_file, user_time_info_file))
    else:
        all_user_id, all_user_time_info = extract_user_time(filenames)

    return all_user_id, all_user_time_info


def extract_user_info(all_user_id, filenames, TEST_FLAG=True):
    """
    Extract All users info based on Time and corresponding devices

    @param all_user_id: a list to store all users id
    @return all_user_info : a dict
    """
    all_user_info_file = "all_user_info.json"

    # for TEST USE ONLY
    if TEST_FLAG is True:
        all_user_info_file = '10_all_user_info.json'
    # END TEST USE

    if os.path.exists(all_user_info_file):
        all_user_info = json.load(open(all_user_info_file))
        print('--Done Loading Files:\t%s'%all_user_info_file)
    else:
        all_user_info = extract_user_Devices_info(all_user_id, filenames)

    return all_user_info


def analysis_Time(user, per_user_info):
    """

    @return median_deltaT, Dates_Interval_Dict
    """
    try:
        Reach_time = per_user_info["Reach_Time"]
        # Data_time = per_user_info["Data_Time"]
        # all_time=sorted(Reach_time+Data_time)
        all_time = sorted(list(set(sorted(Reach_time))))
        median_deltaT = find_median_delta_T(all_time)
    except Exception as exc:
        print('Abnormal User ID: %s'%user)
        # print(sys.exc_info()[0])
        print(traceback.format_exc())
        print(exc)

    # use median Delta_T to determine Time Interval among dates
    # print('--Current Median_Delta_T = %.2f'%median_deltaT)
    Dates_Interval_Dict = generate_time_group(all_time, median_deltaT)

    return median_deltaT, Dates_Interval_Dict

def group_user_behavior_by_Dates_interval(Dates_Interval_Dict, current_user_info):
    """
    group users behavior by dates

    @param Dates_interval_Dict
    @param current_user_info: per_user_info_dict, contain 'Reach_Time' and 'Data_Time'
    @return grouped_user_info_dict
    """
    grouped_user_info_dict = {}

    for key in Dates_Interval_Dict.keys():
        # 1. extract time group
        time_group = Dates_Interval_Dict[key]
        # 2. for each time group, find devices attributes
        grouped_devices_dict = extract_devices_behavior_on_time_group(
            time_group,
            current_user_info
        )
        # 3. assign current grouped devices with current time_group
        grouped_user_info_dict[key] = grouped_devices_dict

    return grouped_user_info_dict

def construct_graph(name, devices_info):
    """
    Calculate devices behavior based on time_group

    @param name: current graph's name
    @param devices_info: a dict to store related 'Keyword' and 'ReachTime' for each devices

    @return graph: nx.Graph object
    """
    graph = nx.Graph(name=name)

    devices_list = list(devices_info.keys())
    graph.add_nodes_from(devices_list)

    if len(devices_list) > 1:
        for d1_idx in range(len(devices_list)-1):
            for d2_idx in range(d1_idx+1, len(devices_list)):
                d1 = devices_list[d1_idx]
                d2 = devices_list[d2_idx]
                edge_weight = calculate_devices_weight(d1,d2,devices_info)
                graph.add_edge(d1, d2, weight=edge_weight)

    return graph

global IO_Time
IT_Time = 0

if __name__ == "__main__":

    TEST_FLAG = True # Indicate we use WorkStation in Watson


    try:
        if sys.argv[1] == '-w':
            TEST_FLAG = False
    except:
        pass

    # On Mac
    filenames = ['ijcai_device_encode_test_sample.csv','ijcai_cookie_encode_test_sample.csv']

    # On Work Station
    if TEST_FLAG is False:
        filenames = [
            'ijcai_device_encode_training.csv',
            'ijcai_device_encode_test.csv',
            'ijcai_cookie_encode_training.csv',
            'ijcai_cookie_encode_test.csv'
        ]

    """ 1. Extract All Users ReachTime and Data_Time """
    # --- 1.1 Extract All User and corresponding ReachTime and DataTime --- #
    all_user_id, all_user_time_info = extract_time(filenames, TEST_FLAG)

    # --- 1.2 Extract All users info based on Time and corresponding devices --- #
    all_user_info = extract_user_info(all_user_id, filenames, TEST_FLAG)

    current_time = str(datetime.now()).split()[0] + '-' + str(datetime.now()).split()[1]

    # --- Let's FLY!!!! --- #
    # --- UPDATE: 2017-10-16 Log Time --- #
    construction_times = []
    # UPDATE END #

    for user_idx in range(len(all_user_id)):
        startTime = time.time()

        # --- add Progress Statue --- #
        percentage = 100*(user_idx+1)/len(all_user_id)
        # print('\r>> Processing Users............ %.2f %%'%percentage,flush=True)
        sys.stdout.write('\r>> Processing Users............ %.2f %%'%percentage)
        sys.stdout.flush()
        # --- End Progree Statue --- #
        user = all_user_id[user_idx]

        per_user_info = all_user_time_info[user]

        # --- 2.1 Analysis Reach_time and Data_Time --- #
        median_T, Dates_Interval_Dict = analysis_Time(user, per_user_info)
        if Dates_Interval_Dict == {} and median_T == []:
            print('Cannot Parse Current User: %s'%user)
            continue

        # --- 2.2 Extract User Devices Behaviors based on Dates Interval --- #
        current_user_info = all_user_info[user]
        current_user_time_based_device = group_user_behavior_by_Dates_interval(Dates_Interval_Dict, current_user_info)

        # --- 2.3 Calculate Devices Related Similarity per time_group --- #
        graph_list = []
        for key in current_user_time_based_device.keys():
            graph = construct_graph(
                name=user+'_'+str(key),
                devices_info=current_user_time_based_device[key]
            )
            graph_list.append(graph)

        # --- 2.4 Create Multi-Layer Graph based on graph_list --- #
        multi_layer_graph = merged_graph(user, graph_list)

        TimeInterval = time.time()-startTime
        construction_times.append(TimeInterval)

        # --- 2.5 Draw graph --- #
        # nx.draw_networkx(multi_layer_graph)
        draw_graph(str(median_T),current_time, str(user_idx), user, multi_layer_graph, self_define_pos=True,save_to_disk=True)

        """
        # ================================ #
        # -- Create Date: 2017.09.27
        # -- UPDATED: Introduce Abnormality ...
        # ================================ #
        """
        # Abnormal Type 1:
        # --- Add Different Devices --- #

    print('\n')
    min_time = min(construction_times)
    max_time = max(construction_times)
    avg_time = mean(construction_times)
    sum_time = sum(construction_times)
    print('min_time:  ',min_time)
    print('avg_time:  ',avg_time)
    print('max_time:  ',max_time)
    print('all_tim:   ',sum_time)

    print('\nall down!!!')
