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

try:
    mit=pd.read_csv(folder+'/mit.csv', low_memory=False, sep=';')
    mit = mit.drop(['products', 'bad products', 'sum dna', 'new DNA ids'], axis=1)
    mit = mit.drop([i for i in hosts.columns if i[:7]=='Unnamed'], axis=1)
    mit = mit.astype(float)
    # mit = mit.sample(frac=.5)
    print(mit.columns)
except:
    print("Data must have been aggregated with aggregate.py before")
    exit


if not os.path.isdir(folder+'/processing/'):
    print('The directory is not present. Creating a new one..')
    os.mkdir(folder+'/processing/')

if not os.path.isdir(folder+'/processing/mit/'):
    print('The directory is not present. Creating a new one..')
    os.mkdir(folder+'/processing/mit')


usual_colors = ['tab:blue', 'tab:orange', 'tab:green','tab:purple','tab:red',
'tab:pink','tab:brown'] 

mit['path']=""

mit['growth_rate']=mit['growth_rate'].replace({15:1.5, 5:0.5})
mit['bad_oxphos']=mit['ros']-mit['oxphos']

interest_params = ['V','vol','n DNA','oxphos','ros','bad_oxphos', 'translate', 'replicate', 'replisomes', 'unmut']

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
        for val in mit[k].unique():
            tmp_list+=[val]
        comb += [tmp_list]
    combinations = list(itertools.product(*comb))
    for c in combinations:
        print("unique plot",c)
        tmp = mit
        i=0
        for k in params:
            tmp = tmp[tmp[k]==c[i]]
            i+=1
        for ev in interest_params:
            mit[ev]=mit[ev].astype(float)
            print(ev)
            d = {}
            i=0
            for value in tmp['seed'].unique():
                d[value] = usual_colors[i]
                i+=1
            colors = [d[i] for i in tmp['seed']]

            fig, ax = plt.subplots(1, 1, figsize=(15,10))
            for seed in mit['seed'].unique():
                tmp2 = tmp[tmp['seed']==seed]
                Z = [np.mean(tmp2[tmp2['time']==t][ev]) for t in tmp2['time'].unique()]
                lab = 'seed '+str(seed)
                ax.scatter(tmp2['time'].unique(), Z, label=lab, alpha=.6)
            ax.set_ylabel(ev)
            ax.set_xlabel('time')
            ax.set_title("Mean "+ev+" over time for "+str(c))
            fig.tight_layout()
            fig.savefig(folder+'/processing/mit/'+ev+'_time_'+str(c)+'.png',dpi=600)
            plt.close(fig)
            
    print("finished unique plots. On to merged seeds")

for k in params: # different values given at the beginning of the simulation
    mit['path']+=[k+" "+str(val)+" | " for val in mit[k]]
    
    for ev in interest_params:
        print(ev, " starting")
        d = {}
        i=0
        try:
            mit[ev]=mit[ev].astype(float)
        except:
            continue
        # for value in mit[k].unique():
        #     d[value] = usual_colors[i]
        #     i+=1
        # colors = [d[i] for i in mit[k]]
        # fig, ax = plt.subplots(1, 1, figsize=(15,10))
        # mit.plot.scatter(x='time', y=ev, c=colors, label=k,
        #     alpha=0.1, s=2, ax=ax
        #     )
    
        # ax.set_ylim(min(mit[ev]), max(mit[ev]))
        # ax.set_ylabel(ev)
        # ax.set_xlabel('time')
        # ax.legend(handles = [mpatches.Patch(color=d[k], label=k) for k in d.keys()], title = k)
        # ax.set_title(ev+" over time for different "+k)

        # fig.tight_layout()
        # fig.savefig(folder+'/processing/mit/'+ev+'_time_'+k+'.png',dpi=600)
        # plt.close(fig)

        fig, ax = plt.subplots(1, 1, figsize=(15,10))
        for unique_value in mit[k].unique():
            tmp = mit[mit[k]==unique_value]
            Z = [np.mean(tmp[tmp['time']==t][ev]) for t in tmp['time'].unique()]
            lab = str(k)+' '+str(unique_value)
            ax.scatter(tmp['time'].unique(), Z, label=lab, alpha=.6)
        ax.set_ylabel(ev)
        ax.set_xlabel('time')
        ax.set_title("Mean "+ev+" over time for different "+k)
        fig.tight_layout()
        fig.savefig(folder+'/processing/mit/'+ev+'_time_'+k+'_summarize.png',dpi=600)
        plt.close(fig)

        print(ev,k," done")

        for unique_value in mit[k].unique():
            tmp = mit[mit[k]==unique_value]
            for other_param in params:
                if k!=other_param:
                    # d = {}
                    # i=0
                    # for value in mit[other_param].unique():
                    #     d[value] = usual_colors[i]
                    #     i+=1
                    # colors = [d[i] for i in tmp[other_param]]
                    # fig, ax = plt.subplots(1, 1, figsize=(15,10))
                    # print(d)
                    # tmp.plot.scatter(x='time', y=ev, c=colors,
                    #     alpha=0.1, s=2, ax=ax
                    #     )

                    # ax.set_ylim(min(mit[ev]), max(mit[ev]))
                    # ax.set_ylabel(ev)
                    # ax.set_xlabel('time')
                    # ax.legend(handles = [mpatches.Patch(color=d[k], label=k) for k in d.keys()], title = other_param)
                    # ax.set_title(ev+" over time for "+k+" "+str(unique_value))

                    # fig.tight_layout()
                    # fig.savefig(folder+'/processing/mit/'+ev+'_time_'+other_param+"_"+str(unique_value)+'.png',dpi=600)
                    # plt.close(fig)

                    fig, ax = plt.subplots(2, 1, figsize=(15,15))
                    for value in mit[other_param].unique():
                        tmp2 = tmp[tmp[other_param]==value]
                        X = [np.median(tmp2[tmp2['time']==t][ev]) for t in tmp2['time'].unique()]
                        Z = [np.mean(tmp2[tmp2['time']==t][ev]) for t in tmp2['time'].unique()]
                        lab = str(other_param)+' '+str(value)
                        ax[0].scatter(tmp2['time'].unique(), X, label=lab, alpha=.6)
                        ax[1].scatter(tmp2['time'].unique(), Z, label=lab, alpha=.6)
                    ax[0].set_ylabel(ev)
                    ax[0].legend()
                    ax[0].set_xlabel('time')
                    ax[0].set_title("Median "+ev+" over time for different "+other_param+"\n"+k+" is "+str(unique_value))
                    ax[1].set_ylabel(ev)
                    ax[1].set_xlabel('time')
                    ax[1].set_title("Mean "+ev+" over time for different "+other_param+"\n"+k+" is "+str(unique_value))
                    fig.tight_layout()
                    fig.savefig(folder+'/processing/mit/'+ev+'_time_'+k+'-'+str(unique_value)+'_'+other_param+'_summarize.png',dpi=600)
                    plt.close(fig)


