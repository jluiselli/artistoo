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


folder = sys.argv[1]
params = sys.argv[2:]

# try:
hosts = pd.read_csv(folder+'/hosts.csv', low_memory=False, sep=";", dtype=str)
print(hosts.columns)
# hosts = hosts.drop(['evolvables', 'subcells'], axis=1)
hosts = hosts.astype(float)
    # hosts = hosts.sample(frac=.5)
# except:
#     print("Data must have been aggregated with aggregate.py before")


if not os.path.isdir(folder+'/processing/'):
    print('The directory is not present. Creating a new one..')
    os.mkdir(folder+'/processing/')

usual_colors = ['tab:blue', 'tab:orange', 'tab:green','tab:purple','tab:red',
'tab:pink','tab:brown'] 


hosts['growth_rate']=hosts['growth_rate'].replace({15:1.5, 5:0.5})
hosts = hosts.fillna(0)

if params[-1]=='seed':
    unique_plots = True
    params = params[:-1]
else:
    unique_plots = False


if unique_plots:
    print("doing all unique plots")
    comb = []
    for k in params:
        tmp_list = []
        for val in hosts[k].unique():
            tmp_list+=[val]
        comb += [tmp_list]
    combinations = list(itertools.product(*comb))
    for c in combinations:
        print("unique plot",c)
        tmp = hosts
        i=0
        for k in params:
            tmp = tmp[tmp[k]==c[i]]
            i+=1

        fig, ax = plt.subplots(1, 1, figsize=(15,10))
        for seed in tmp['seed'].unique():
            tmp2 = tmp[tmp['seed']==seed]
            ncells = [len(tmp2[tmp2['time']==t]) for t in tmp2['time'].unique()]
            ax.scatter(tmp2['time'].unique(), ncells, label = str(seed), s=20)

        ax.set_ylabel('nb of hosts cells')
        ax.set_xlabel('time')
        ax.legend()
        ax.set_title("ncells over time "+str(c))
        fig.tight_layout()
        fig.savefig(folder+'/processing/ncells_time_'+str(c)+'.png',dpi=600)
        plt.close(fig)

    print("finished unique plots. On to merged seeds")
          

for k in params: # different values given at the beginning of the simulation
    d = {}
    i=0
    print(k)
    for value in hosts[k].unique():
        
        tmp = hosts[hosts[k]==value]
        for other_param in params:
            if k!=other_param:
                d = {}
                i=0
                fig, ax = plt.subplots(1, 1, figsize=(15,10))
                for other_value in hosts[other_param].unique():
                    tmp2=tmp[tmp[other_param]==value]
                    ncells = [len(tmp2[tmp2['time']==t])/len(tmp2['seed'].unique()) for t in tmp2['time'].unique()]
                    ax.scatter(tmp2['time'].unique(), ncells, label = str(other_value), s=20)

                ax.set_ylabel('nb of cells')
                ax.set_xlabel('time')
                ax.legend()
                ax.set_title("ncells over time for "+k+" "+str(value))

                fig.tight_layout()
                fig.savefig(folder+'/processing/ncells_time_'+other_param+'_'+k+"_"+str(value)+'.png',dpi=600)
                plt.close(fig)
            
