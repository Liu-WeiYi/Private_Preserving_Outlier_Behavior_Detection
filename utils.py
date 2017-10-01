# coding: utf-8
import time
import csv
import json
import os,sys
import random
import networkx as nx
import matplotlib.pyplot as plt

from statistics import median, mean
from datetime import datetime


def to_second(time_str):
    """
    transfer time_str to seconds
    From http://www.xinghaixu.com/archives/685

    @param time_str: e.g. 20170412164640
    @return seconds from UTC time
    """
    format_time_str = "%s-%s-%s %s:%s:%s"%(
                        time_str[0:4],
                        time_str[4:6],
                        time_str[6:8],
                        time_str[8:10],
                        time_str[10:12],
                        time_str[12:]
                    )
    seconds = datetime.strptime(format_time_str, "%Y-%m-%d %H:%M:%S")
    return time.mktime(seconds.timetuple())


def find_median_delta_T(all_time):
    """
    Extract all Delta T among all_time

    @param all_time: ['201705040913','201705040932', ...]
    @return median_deltaT
    """
    all_delta_T = []
    # find all Delta_T
    for t1_idx in range(len(all_time)-1):
        t2_idx = t1_idx + 1
        t1 = to_second(all_time[t1_idx])
        t2 = to_second(all_time[t2_idx])
        all_delta_T.append(abs(t2-t1))

    # for t1_idx in range(len(all_time)-1):
    #     for t2_idx in range(t1_idx+1, len(all_time)):
    #         t1 = to_second(all_time[t1_idx])
    #         t2 = to_second(all_time[t2_idx])
    #         all_delta_T.append(abs(t2-t1))

    """ FIX BUGS: We should exclude value zero !!!!! """
    all_delta_T = [i for i in all_delta_T if i != 0]
    # TODO: DETERMINE WE SHOULD USE MEDIAN OR MEAN!!!
    # return median(sorted(all_delta_T))
    """
    FIX BUGS:
      If current user has only ONE Log Time all_delta_T = []
    """
    if all_delta_T == []:
        all_delta_T = [0]
    return mean(all_delta_T)

def generate_time_group(all_time, deltaT):
    """
    generate time group by using DeltaT

    @param all_time: all time
    @param deltaT: DeltaT with seconds

    @return interval_dict
    """
    interval_count = 1
    interval_dict = {}

    """ Alg: Time Grouping """
    t1_idx = 0
    last_one_hit = False
    while t1_idx <= len(all_time)-1:
        t2_idx = t1_idx + 1
        if t2_idx >= len(all_time): break
        t1 = all_time[t1_idx]
        t2 = all_time[t2_idx]

        continueFlag = True
        group = set()
        while continueFlag is True:
            # in case solo time
            if len(group) == 0:
                group.add(t1)
            # if we need to add t2 into the same group
            if abs(to_second(t1)-to_second(t2)) <= deltaT:
                group.add(t2)
                t1_idx += 1
                if all_time[t1_idx] == all_time[-1]:
                        last_one_hit = True
                t2_idx += 1
                if t2_idx >= len(all_time):
                    interval_dict[interval_count] = list(group)
                    interval_count += 1
                    t1_idx = t2_idx
                    continueFlag = False
                else:
                    t1 = all_time[t1_idx]
                    t2 = all_time[t2_idx]
            elif abs(to_second(t1)-to_second(t2)) > deltaT:
                interval_dict[interval_count] = list(group)
                interval_count += 1
                t1_idx = t2_idx
                continueFlag = False
    """ FIX BUGS: add last one as we ignore t2 """
    if last_one_hit is False:
        interval_dict[interval_count] = [all_time[-1]]

    return interval_dict

def extract_user_time(filenames):
    """
    Extract All Users ReachTime and DataTime

    @params filenames
    @return all_user_statistic: a dict to save userID with corresponding time information
    """
    statistic_file_name = 'user_time_info.json'
    all_user_id = set()
    all_user_time_info = {}

    for file in filenames:
        count = 0

        # Limited Memory on MacPro!!!  test_cookie.csv is 10G
        if 'device' in file:
            MAX_RECORDS = 1000000000000000000000000
        elif 'cookie' in file:
            MAX_RECORDS = 1000000000000000000000000

        print('processing file: %s'%file)
        with open(file, 'r+') as f:
            for row in f.readlines():
                if count == 0:
                    # skip csv header
                    count += 1
                elif count <= MAX_RECORDS:
                    row = row.strip().split(',')
                    if count %1000000 == 0:
                        print('--processed %d million entries...'%(count/1000000))

                    # --- 1. extract user ID --- #
                    user = row[0]
                    if 'device' in file:
                        all_user_id.add(user)
                        if user not in all_user_time_info.keys():
                            all_user_time_info[user] = {}
                    elif 'cookie' in file:
                        if user not in all_user_id:
                            continue

                    # --- 2. extract Reach_Time or Data_Time --- #
                    if 'device' in file:
                        # extract Reach_Time from device.csv
                        if 'Reach_Time' not in all_user_time_info[user].keys():
                            all_user_time_info[user]['Reach_Time'] = []
                        try:
                            Reach_Time = row[-2]
                            all_user_time_info[user]['Reach_Time'].append(Reach_Time)
                        except Exception as exc:
                            print(traceback.format_exc())
                            print(exc)
                    if 'cookie' in file:
                        # extract Data_Time from cookie.csv
                        if 'Data_Time' not in all_user_time_info[user].keys():
                            all_user_time_info[user]['Data_Time'] = []
                        try:
                            Data_Time = row[1]
                            all_user_time_info[user]['Data_Time'].append(Data_Time)
                        except Exception as exc:
                            print(traceback.format_exc())
                            print(exc)
                else:
                    break

                count += 1


    print('Save Results to Disk...')
    with open('all_user_id.txt','w+') as f:
        for id in all_user_id:
            f.write(id)
            f.write('\n')
    json.dump(all_user_time_info, open(statistic_file_name,'w+'))

    print('Save sampled users info...')
    sampled_all_user_id = random.sample(list(all_user_id),10)
    with open('10_all_user_id.txt','w+') as f:
            for id in sampled_all_user_id:
                f.write(id)
                f.write('\n')
    sampled_all_user_time_info = {}
    for user in sampled_all_user_id:
        sampled_all_user_time_info[user] = all_user_time_info[user]
    json.dump(sampled_all_user_time_info, open('10_%s'%statistic_file_name,'w+'))

    return all_user_id, all_user_time_info


def extract_user_Devices_info(all_user_id, filenames):
    """
    Extract all users devices infor corresponding to time

    @param all_user_id
    @param filenames

    @return all_user_info : a dict
    """
    all_user_info = {}
    print(len(all_user_id))

    for file in filenames:
        count = 0

        # Limited Memory on MacPro!!!  test_cookie.csv is 10G
        if 'device' in file:
            MAX_RECORDS = 1000000000000000000000000
        elif 'cookie' in file:
            MAX_RECORDS = 1000000000000000000000000

        print('processing file: %s'%file)
        with open(file, 'r+') as f:
            for row in f.readlines():
                if count == 0:
                    # skip csv header
                    count += 1
                elif count <= MAX_RECORDS:
                    row = row.strip().split(',')
                    if count %1000000 == 0:
                        print('--processed %d million entries...'%(count/1000000))

                    # --- 1. Compare user ID --- #
                    user = row[0]
                    if user not in all_user_info.keys():
                        all_user_info[user] = {
                            'Reach_Time':{},
                            'Data_Time':{}
                        }
                    # --- 2. extract time from device_related .csv file --- #
                    if 'device' in file:
                        try:
                            Reach_Time = row[-2]
                            Device_IP = row[-9]
                            Keyword = row[-8]
                            if Reach_Time not in all_user_info[user]['Reach_Time'].keys():
                                all_user_info[user]['Reach_Time'][Reach_Time] = {}
                            Devices = row[1:4]
                            for d in Devices:
                                if d != '':
                                    all_user_info[user]['Reach_Time'][Reach_Time][d] = {
                                        'Device_IP':[],
                                        'Keyword':[]
                                    }
                                    # add related info...
                                    all_user_info[user]['Reach_Time'][Reach_Time][d]['Device_IP'].append(Device_IP)
                                    all_user_info[user]['Reach_Time'][Reach_Time][d]['Keyword'].append(Keyword)
                        except Exception as exc:
                            print(traceback.format_exc())
                            print(exc)
                    # --- 3. extract time from cookie_related .csv file --- #
                    if 'cookie' in file:
                        try:
                            Data_Time = row[1]
                            Cookie = row[2]
                            Cookie_IP = row[-2]
                            title = row[-1]
                            if Data_Time not in all_user_info[user]['Data_Time'].keys():
                                all_user_info[user]['Data_Time'][Data_Time] = {
                                    'Cookie':[],
                                    'Cookie_IP':[],
                                    'title':[]
                                }
                                # add related info...
                                all_user_info[user]['Data_Time'][Data_Time]['Cookie'].append(Cookie)
                                all_user_info[user]['Data_Time'][Data_Time]['Cookie_IP'].append(Cookie_IP)
                                all_user_info[user]['Data_Time'][Data_Time]['title'].append(title)
                        except Exception as exc:
                            print(traceback.format_exc())
                            print(exc)
                else:
                    break
                count += 1

    # save to disk in case some thing fly!!!
    print('Save Results to Disk...')
    json.dump(all_user_info, open('all_user_info.json','w+'))

    # get sampled user_info_dict... FOR MAC USE :)
    sampled_user_id = []
    with open('10_all_user_id.txt','r+') as f:
        for line in f.readlines():
            sampled_user_id.append(line.strip())
    sampled_user_info = {}
    for user in sampled_user_id:
        sampled_user_info[user] = all_user_info[user]
    json.dump(sampled_user_info, open('10_all_user_info.json','w+'))

    return all_user_info



def extract_devices_behavior_on_time_group(time_group, current_user_info):
    """
    Extract devices behaviors

    @param time_group: current time group
    @param current_user_info : per_user_info_dict, contain 'Reach_Time' and 'Data_Time'

    @return grouped_devices_dict
    """
    grouped_devices_dict = {}
    # --- 1. Group Cookie Related Records --- #
    for data_time in current_user_info['Data_Time'].keys():
        if data_time in time_group:
            # TODO: How can we leverage Cookies related Information, like Data_Time, Title, etc
            pass

    # --- 2. Group Devices Related Records --- #
    for Reach_Time in current_user_info['Reach_Time'].keys():
        if Reach_Time in time_group:
            devices = current_user_info['Reach_Time'][Reach_Time]
            for d in devices:
                if d not in grouped_devices_dict.keys():
                    grouped_devices_dict[d] = {
                        'Keyword':[],
                        'Device_IP':[]
                    }
                grouped_devices_dict[d]['Keyword'].append(
                    current_user_info['Reach_Time'][Reach_Time][d]['Keyword']
                )
                grouped_devices_dict[d]['Device_IP'].append(
                    current_user_info['Reach_Time'][Reach_Time][d]['Device_IP']
                )
    return grouped_devices_dict

def calculate_devices_weight(d1, d2, devices_info):
    """
    Calculate similarity among d1 and d2

    @param d1: first device
    @param d2: second device
    @param devices_info: a dict to store related 'Keyword' and 'ReachTime' for each devices

    @return weight
    """
    def _Jaccard(l1, l2):
        """ Calculate Jaccard Similarity among list l1 and list l2 """
        l11 = []
        for l in l1:
            for i in l:
                l11.append(i)
        l22 = []
        for l in l2:
            for j in l:
                l22.append(j)

        _common = set(l11)&set(l22)
        _all = set(l11)|set(l22)
        if len(_all) != 0:
            sim = len(_common)/len(_all)
        else:
            sim = 0.0
        return sim

    weight = 0.0

    # 1. Keyword Similarity
    keyword_weight  = _Jaccard(devices_info[d1]['Keyword'], devices_info[d2]['Keyword'])
    # 2. IP Similarity
    IP_weight       = _Jaccard(devices_info[d1]['Device_IP'], devices_info[d2]['Device_IP'])

    weight = 0.5*keyword_weight + 0.5*IP_weight
    return weight

def merged_graph(name, graph_list):
    """
    Merged graphs into a Multilayer Graph from graph_list

    @param name: current user's name
    @param graph_list
    @return merged_graph
    """
    merged_graph = nx.Graph(name='merged_%s'%name)

    idx = 0

    for g in graph_list:
        # add current nodes and edges
        nodes = [node+'_'+str(idx) for node in g.nodes()]
        merged_graph.add_nodes_from(nodes)
        for edge in g.edges(data=True):
            u,v,w = edge
            merged_graph.add_edge(
                u+'_'+str(idx),
                v+'_'+str(idx),
                weight=w['weight']
            )

        # add link between idx and idx-1
        if idx > 0:
            back_idx = idx-1
            nodes = merged_graph.nodes()
            for node in nodes:
                if "_"+str(idx) in node: # only care about node in current graph!
                    # add edges among same name node
                    same_name_node = node.split('_')[0]
                    back_node = same_name_node+'_'+str(back_idx)
                    if back_node in nodes:
                        if node != back_node:
                            merged_graph.add_edge(node, back_node, weight=0)

        idx += 1


    return merged_graph

def draw_graph(median_T, current_time, user_idx, user, graph, self_define_pos = True,save_to_disk=True):
    """
    Save graph to disk

    @param median_T: current median_T for current user
    @param current_time: current Time, used for creating folder
    @param user_idx: user's idx, use for indicating current user/instead of using nonsense user name
    @param user: user name
    @param graph: multilayer graph
    @param self_define_pos: the pos for each node in the graph is defined by ourselves [True]
    @param save_to_disk: if we need to save files to disk [True]
    """
    cleaned_graph = nx.Graph(name=graph.name)

    node_map = {}
    idx = 0
    for node in graph.nodes():
        same_name_node = node.split('_')[0]
        if same_name_node not in node_map.keys():
            node_map[same_name_node] = 'd%d'%idx
            idx += 1

    # update nodes in graph
    for node in graph.nodes():
        same_name_node, idx = node.split('_')
        updated_node = node_map[same_name_node]+'_'+idx
        cleaned_graph.add_node(updated_node)

    # update edges in graph
    for edge in graph.edges(data=True):
        u,v,w = edge
        if u != v: # break self-link
            same_name_node, idx = u.split('_')
            updated_u = node_map[same_name_node]+'_'+idx
            same_name_node, idx = v.split('_')
            updated_v = node_map[same_name_node]+'_'+idx
            cleaned_graph.add_edge(
                u=updated_u,
                v=updated_v,
                weight=w['weight']
            )
    # TODO: DEFINE IF WE NEED DRAW GRAPH BY OURSELVES
    if self_define_pos is True:
        # define pos for each node
        pos = {}
        # find out how many node we have and how many layers we have
        same_name_node = set([node.split('_')[0] for node in cleaned_graph.nodes()])
        layers = set([node.split('_')[1] for node in cleaned_graph.nodes()])

        # each layer has same init Y
        Y = 0.0
        for layer in layers:
            # each node's init X is the same
            X = 0.0
            for node in sorted(cleaned_graph.nodes()):
                if layer == node.split('_')[1]:
                    pos[node] = (X,Y)
                    X += 0.2
            Y += 1
    else:
        pos = nx.spring_layout(cleaned_graph)


    # plt.figure()
    nx.draw_networkx_nodes(cleaned_graph,pos,node_color='w',node_size=100)

    for edge in cleaned_graph.edges(data=True):
        if edge[2]['weight'] == 0:
            nx.draw_networkx_edges(cleaned_graph,pos,edgelist=[edge],edge_color='r',style='dashed',width=0.5)
        elif edge[2]['weight'] == 1:
            nx.draw_networkx_edges(cleaned_graph,pos,edgelist=[edge],edge_color='k')
        else:
            nx.draw_networkx_edges(cleaned_graph,pos,edgelist=[edge],edge_color='b')
            """ For WorkStation """
            """ We only Save Abnormal Nodes! """
            save_to_disk = True

    nx.draw_networkx_labels(cleaned_graph,pos,font_size=3)

    if save_to_disk is True:
        nx.draw_networkx_edge_labels(cleaned_graph,pos,label_pos=0.5,font_size=1)

    if save_to_disk is True:
        if not os.path.exists('%s---sampled_results'%current_time):
            os.mkdir('%s---sampled_results'%current_time)

        nx.write_gml(graph, "%s---sampled_results/%s--%s.gml"%(current_time, user_idx, median_T))
        plt.savefig("%s---sampled_results/%s--%s.pdf"%(current_time, user_idx, median_T))

        # save user name to disk
        if not os.path.exists('%s---sampled_results/abnormal_user.txt'%(current_time)):
            with open('abnormal_user.txt','a+') as f:
                f.write(user)
                f.write('\n')


    plt.clf()

    # plt.show()
