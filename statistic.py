# coding: utf-8
# author: weiyiliu@us.ibm.com
# purpose: statistic features related information

import json

from Process_TianChi_Main import analysis_Time
from utils import *

""" 0. all users"""
users = []
with open('all_user_id.txt','r+') as f:
    users = [line.strip() for line in f.readlines()]
print('# users:\t', len(users))

choose = sys.argv[1]

if choose == '1':
    print('time group...')
    """ 1. timegroup information"""
    with open('user_time_info.json') as f:
        user_time = json.load(f)
        all_time = 0
        count = 0
        for user in user_time.keys():

            count += 1
            percentage = 100*count/len(user_time.keys())
            sys.stdout.write('\r>> Processing Users............ %.2f %%'%percentage)
            sys.stdout.flush()

            per_user_info = user_time[user]
            _, Dates_Interval_Dict = analysis_Time(user, per_user_info)
            all_time += len(Dates_Interval_Dict.keys())
    print('\n# avg time group:\t', all_time/len(user_time.keys()))


if choose == '2':
    print('features...')
    """ 2. All/AVG Keyword/IP """
    with open('all_user_info.json') as f:
        all_user_info = json.load(f)

        all_keyword = 0
        avg_keyword = 0
        all_IP = 0
        avg_IP = 0

        count = 0
        for user in all_user_info.keys():

            count += 1
            percentage = 100*count/len(all_user_info.keys())
            sys.stdout.write('\r>> Processing Users............ %.2f %%'%percentage)
            sys.stdout.flush()

            info = all_user_info[user]["Reach_Time"]
            for time in info.keys():
                for user in info[time].keys():
                    all_keyword += len(info[time][user]["Keyword"])
                    all_IP += len(info[time][user]["Device_IP"])

        avg_keyword = all_keyword/len(all_user_info.keys())
        avg_IP = all_IP/len(all_user_info.keys())

    print('\n# all keyword:\t', all_keyword)
    print('# avg keyword:\t', avg_IP)
    print('# all IP:\t', all_IP)
    print('# avg IP:\t', avg_IP)