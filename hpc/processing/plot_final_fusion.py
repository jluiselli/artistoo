import pandas as pd
import matplotlib.pyplot as plt 
import sys, os
import matplotlib.patches as mpatches
import matplotlib.colors as clrs
import numpy as np
import ast
import random
import colorsys
import itertools
import seaborn as sns


folder = sys.argv[1]
params = sys.argv[2:]

try:
    hosts=pd.read_csv(folder+'/hosts.csv', low_memory=False, sep=";", dtype=str)
    print(hosts.columns)
    try:
        hosts = hosts.drop(['time of birth','good','bads','dna','type'], axis=1)
        hosts = hosts.drop([i for i in hosts.columns if i[:7]=='Unnamed'], axis=1)
        hosts = hosts.drop(['evolvables', 'subcells'], axis=1)
    except:
        pass
    hosts = hosts.replace({'undefined':np.NaN})
    try:
        hosts['degradation'] = hosts['degradation'].replace({'001':'0.01', '01':'0.1', '005':'0.05', '0025':'0.025', '0075':'0.075'})
    except:
        pass
    try:
        hosts['growth_rate'] = hosts['growth_rate'].replace({'05':'0.5', '15':'1.5'})
    except:
        pass
    hosts = hosts.astype(float)
    # hosts = hosts.sample(frac=.5)
except:
    print("Data must have been aggregated with aggregate.py before")


if not os.path.isdir(folder+'/processing/'):
    print('The directory is not present. Creating a new one..')
    os.mkdir(folder+'/processing/')

if not os.path.isdir(folder+'/processing/final_fusion/'):
    print('The directory is not present. Creating a new one..')
    os.mkdir(folder+'/processing/final_fusion/')



usual_colors = ['tab:blue', 'tab:orange', 'tab:green','tab:purple','tab:red',
'tab:pink','tab:brown'] 

try:
    hosts['growth_rate']=hosts['growth_rate'].replace({15:1.5, 5:0.5})
except:
    pass

hosts = hosts.fillna(0)

evolvables = []
for ev in [i for i in hosts.columns if i[:10]=='evolvables']:
    hosts = hosts.rename(columns = {ev : ev[11:]})
    evolvables += [ev[11:]]


for k in params: # different values given at the beginning of the simulation
    print(k)
    for unique_value in hosts[k].unique():
        tmp = hosts[hosts[k]==unique_value]
        # max_time = max(tmp['time'].unique())
        max_time = 299701
        tmp = tmp[tmp['time']==max_time]

        for other_param in params:
            if k!=other_param:
                for ev in evolvables:
                    fig, ax = plt.subplots(1, 1, figsize=(15,10))
                    try:
                        sns.violinplot(x=other_param, y=ev, inner=None, data=tmp, ax=ax,
                            color='.2')
                        sns.stripplot(x=other_param, y=ev, hue="seed", data=tmp, ax=ax,
                            linewidth=1)
                        
                        ax.set_title(str(folder)+'\n'+ev+" at time "+str(max_time)+" "+str(k)+" "+str(unique_value))
                        ax.set_xlabel(other_param)
                        if ev=='fusion_rate':
                            ax.set_ylim(-1e-3, 1e-3)
                        elif ev=='host_division_volume':
                            ax.set_ylim(0,5000)
                        elif ev=='fission_rate':
                            ax.set_ylim(-1e-5,5.5e-5)
                        elif ev=='rep':
                            ax.set_ylim(5,35)
                        elif ev=='HOST_V_PER_OXPHOS':
                            ax.set_ylim(-1e-5,1)
                        else:
                            ax.set_ylim(min(hosts[ev]), max(hosts[ev]))

                        fig.tight_layout()
                        fig.savefig(folder+'/processing/final_fusion/'+ev+'_'+k+"_"+str(unique_value)+'.png')
                    except:
                        pass
                    plt.close(fig)
