# coding: utf-8
# purpose: Feed all_time, calculate related incremental time, save to disk as csv file

import numpy as np
import matplotlib.pyplot as plt

import seaborn as sns

""" Read All Time """
all_time = []
with open('all_time','r+') as f:
    for line in f.readlines():
        time = float(line.strip())
        all_time.append(time)

""" Calculate Incremental Time """
incremental_time = [all_time[0]]
for idx in range(1,len(all_time)):
    time_interval = all_time[idx]
    incrementalT = incremental_time[-1]+time_interval
    incremental_time.append(incrementalT)

# transfer (s) -> (ms)
incremental_time = [t*1000 for t in incremental_time]

""" save incremental_time to disk as csv file """
with open('incrementa_time.csv','w+') as f:
    for t in incremental_time:
        f.write(str(t))
        f.write('\n')

""" Draw Incremental Time """
sns.set_style("darkgrid", {'font.family':'serif','font.serif':'Times New Roman'})

x = list(range(1, len(incremental_time)+1))
plot = sns.pointplot(x=x, y=incremental_time)

# plot.set(xticks=[])
plt.xlabel('Cumulative Accounts Number')
plt.ylabel('Cumulative Time (ms)')

plt.savefig('incremental_time.pdf')
plt.show()