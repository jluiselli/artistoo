import pandas as pd
import matplotlib.pyplot as plt 
import sys, os
import matplotlib.patches as mpatches
import matplotlib.colors as clrs
import numpy as np
import ast
import random
import colorsys
import matplotlib.animation as manimation


folder = sys.argv[1]
filters = sys.argv[2:]

#Usage : plot_fisfus_time.py folder/ damage_rate 5e-6
# To get all seeds with damage_rate 5e-6
#Usage : plot_fisfus_time.py folder/ damage_rate 5e-6 growth_rate 2
# To get all seeds with damage_rate 5e-6 and growth_rate 2

# try:
try:
    hosts=pd.read_csv(folder+'/hosts.csv', low_memory=False, sep=";", dtype=str)
    try:
        hosts = hosts.drop(['time of birth','good','bads','dna','type'], axis=1)
        hosts = hosts.drop(['evolvables', 'subcells'], axis=1)
    except:
        pass
    hosts = hosts.replace({'undefined':np.NaN})
    hosts = hosts.drop([i for i in hosts.columns if i[:7]=='Unnamed'], axis=1)
    try:
        hosts['degradation'] = hosts['degradation'].replace({'001':'0.01', '01':'0.1', '005':'0.05'})
    except:
        pass
    try:
        df['growth_rate']=df['growth_rate'].replace({'15':'1.5', '05':'0.5'})
    except:
        pass
    hosts = hosts.astype(float)
    # hosts = hosts.sample(frac=.5)
except:
    print("Data must have been aggregated with aggregate.py before")


if not os.path.isdir(folder+'/processing/'):
    print('The directory is not present. Creating a new one..')
    os.mkdir(folder+'/processing/')

if not os.path.isdir(folder+'/processing/hosts/'):
    print('The directory is not present. Creating a new one..')
    os.mkdir(folder+'/processing/hosts/')

for ev in [i for i in hosts.columns if i[:10]=='evolvables']:
    hosts = hosts.rename(columns = {ev : ev[11:]})

i = iter(filters)
params = dict(zip(i,i))
for k in params:
    hosts = hosts[hosts[k]==float(params[k])]

print(params)

hosts = hosts[["time", "seed", "fusion_rate", "fission_rate"]]


usual_colors = ['tab:blue', 'tab:orange', 'tab:green','tab:purple','tab:red',
'tab:pink','tab:brown'] 
seeds = hosts['seed'].unique()
d = {seeds[i]:usual_colors[i] for i in range(len(seeds))}

print(hosts,d)
n = 1000
x = np.linspace(0, 6*np.pi, n)
y = np.sin(x)

# # Define the meta data for the movie
# comments = 'evolution for ' + params
# FFMpegWriter = manimation.writers['ffmpeg']
# metadata = dict(title='Fusion/Fission across time', artist='Jluiselli',
#                 comment=comments)
# writer = FFMpegWriter(fps=15, metadata=metadata)

# fig = plt.figure()
# sine_line, = plt.plot(x, y, 'b')
# fig.legend(handles = [mpatches.Patch(color=d[k], label=k) for k in d.keys()])
# # data, = plt.scatter([],[])
# red_circle, = plt.plot([], [], 'ro', markersize = 10)
# plt.xlabel("fission_rate")
# plt.set_ylabel("fusion_rate")

# with writer.saving(fig, "test.mp4", 100):
#     for t in hosts['time']:
#         x = hosts[hosts['time']==t]["fission_rate"]
#         y = hosts[hosts['time']==t]["fusion_rate"]
#         c = [d[s] for s in hosts[hosts['time']==t]["seed"]
#         # data.set_data(x,y)
#         red_circle.set_data(x0, y0)
#         writer.grab_frame

FFMpegWriter = manimation.writers['ffmpeg']
metadata = dict(title='Movie Test', artist='Matplotlib',
                comment='a red circle following a blue sine wave')
writer = FFMpegWriter(fps=15, metadata=metadata)
fig = plt.figure()
fig.legend(handles = [mpatches.Patch(color=d[k], label=k) for k in d.keys()])


red_circle, = plt.plot([], [], 'ro', markersize = 10, c=[])
plt.xlabel("fission_rate")
plt.ylabel("fusion_rate")


with writer.saving(fig, "writer_test.mp4", 100):
    i=0
    for t in hosts['time']:
        print(t)
        x0 = hosts[hosts['time']==t]["fission_rate"]
        y0 = hosts[hosts['time']==t]["fusion_rate"]
        c = [d[s] for s in hosts[hosts['time']==t]["seed"]]
        red_circle.set_data(x0, y0, c=c)
        writer.grab_frame()
        i+=1