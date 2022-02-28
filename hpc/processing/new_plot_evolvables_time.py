import pandas as pd
import matplotlib.pyplot as plt 
import sys, os
import matplotlib.patches as mpatches
import matplotlib.colors as clrs
import numpy as np
import ast
import random
import colorsys


folder = sys.argv[1]
params = sys.argv[2:]

try:
    hosts=pd.read_csv(folder+'/hosts.csv', low_memory=False, sep=";", dtype=str)
    hosts = hosts.sample(frac=.5)
except:
    print("Data must have been aggregated with aggregate.py before")


if not os.path.isdir(folder+'/processing/'):
    print('The directory is not present. Creating a new one..')
    os.mkdir(folder+'/processing/')


usual_colors = ['tab:blue', 'tab:orange', 'tab:green','tab:purple','tab:red',
'tab:pink','tab:brown'] 

evolvables = [i[11:] for i in hosts.columns if i[:10]=="evolvables"]
hosts['path']=""

hosts['growth_rate']=hosts['growth_rate'].replace({'15':'1.5', '05':'0.5'})
hosts['deprecation_rate']=hosts['deprecation_rate'].replace({'001':'0.01', '01':'0.1', '005':'0.05'})
hosts['time'] = hosts['time'].astype(float)

for k in params: # different values given at the beginning of the simulation
    d = {}
    i=0
    hosts['path']+=[k+" "+str(val)+" | " for val in hosts[k]]
    print(k)
    
    for ev in evolvables:
        long_ev = "evolvables_"+ev
        hosts[long_ev] = hosts[long_ev].astype(float)
        for value in hosts[k].unique():
            d[value] = usual_colors[i]
            i+=1
        colors = [d[i] for i in hosts[k]]

        fig, ax = plt.subplots(1, 1, figsize=(15,10))
        hosts.plot.scatter(x='time', y=long_ev, c=colors, label=k,
            alpha=0.1, s=2, ax=ax
            )
    
        ax.set_ylim(min(hosts[long_ev]), max(hosts[long_ev]))
        ax.set_ylabel(ev)
        ax.set_xlabel('time')
        ax.legend(handles = [mpatches.Patch(color=d[k], label=k) for k in d.keys()], title = k)
        ax.set_title(ev+" over time for different "+k)

        fig.tight_layout()
        fig.savefig(folder+'/processing/'+ev+'_time_'+k+'.png',dpi=600)
        plt.close(fig)
        print(ev,k," done. Going to cross plots")

        for unique_value in hosts[k].unique():
            tmp = hosts[hosts[k]==unique_value]
            for other_param in params:
                if k!=other_param:
                    d = {}
                    i=0
                    for value in hosts[other_param].unique():
                        d[value] = usual_colors[i]
                        i+=1
                    colors = [d[i] for i in tmp[other_param]]
                    fig, ax = plt.subplots(1, 1, figsize=(15,10))

                    tmp.plot.scatter(x='time', y=long_ev, c=colors,
                        alpha=0.1, s=2, ax=ax
                        )

                    ax.set_ylim(min(hosts[long_ev]), max(hosts[long_ev]))
                    ax.set_ylabel(ev)
                    ax.set_xlabel('time')
                    ax.legend(handles = [mpatches.Patch(color=d[k], label=k) for k in d.keys()], title = other_param)
                    ax.set_title(ev+" over time for "+k+" "+str(unique_value))

                    fig.tight_layout()
                    fig.savefig(folder+'/processing/'+ev+'_time_'+other_param+"_"+str(unique_value)+'.png',dpi=600)
                    plt.close(fig)
