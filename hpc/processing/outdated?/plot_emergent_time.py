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
    hosts=pd.read_csv(folder+'/hosts.csv', low_memory=False, sep=";", dtype=str)
    hosts = hosts.drop(['evolvables', 'subcells'], axis=1)
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


usual_colors = ['tab:blue', 'tab:orange', 'tab:green','tab:purple','tab:red',
'tab:pink','tab:brown'] 


hosts['growth_rate']=hosts['growth_rate'].replace({'15':'1.5', '05':'0.5'})
hosts['time'] = hosts['time'].astype(float)
hosts = hosts.fillna(0)

interest_params = ['total_vol', 'time of birth', 'V', 'vol', 'n mito','total_oxphos']

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
        for ev in interest_params:
            hosts[ev]=hosts[ev].astype(float)
            print(ev)
            d = {}
            i=0
            for value in tmp['seed'].unique():
                d[value] = usual_colors[i]
                i+=1
            colors = [d[i] for i in tmp['seed']]
            
            fig, ax = plt.subplots(1, 1, figsize=(15,10))
            tmp[ev]=tmp[ev].astype(float)
            tmp.plot.scatter(x='time', y=ev, c=colors, label=k,
                alpha=0.1, s=2, ax=ax
                )
            
            ax.set_ylim(min(hosts[ev]), max(hosts[ev]))
            ax.set_ylabel(ev)
            ax.set_xlabel('time')
            ax.legend(handles = [mpatches.Patch(color=d[k], label=k) for k in d.keys()], title = k)
            ax.set_title(ev+" over time "+str(c))

            fig.tight_layout()
            fig.savefig(folder+'/processing/hosts/'+ev+'_time_'+str(c)+'.png',dpi=600)
            plt.close(fig)

    print("finished unique plots. On to merged seeds")
          

for k in params: # different values given at the beginning of the simulation
    d = {}
    i=0
    print(k)
    
    for ev in interest_params: # Which thing over time we want to plot
        hosts[ev] = hosts[ev].astype(float)
        d = {}
        i=0
        for value in hosts[k].unique():
            d[value] = usual_colors[i]
            i+=1
        colors = [d[i] for i in hosts[k]]

        fig, ax = plt.subplots(1, 1, figsize=(15,10))
        hosts.plot.scatter(x='time', y=ev, c=colors, label=k,
            alpha=0.1, s=2, ax=ax
            )
        try:
            ax.set_ylim(min(hosts[ev]), max(hosts[ev]))
        except:
            pass
        ax.set_ylabel(ev)
        ax.set_xlabel('time')
        ax.legend(handles = [mpatches.Patch(color=d[k], label=k) for k in d.keys()], title = k)
        ax.set_title(ev+" over time for different "+k)

        fig.tight_layout()
        fig.savefig(folder+'/processing/hosts/'+ev+'_time_'+k+'.png',dpi=600)
        plt.close(fig)

        fig, ax = plt.subplots(2, 1)
        for unique_value in hosts[k].unique():
            tmp = hosts[hosts[k]==unique_value]
            X = [np.median(tmp[tmp['time']==t][ev]) for t in tmp['time'].unique()]
            Z = [np.mean(tmp[tmp['time']==t][ev]) for t in tmp['time'].unique()]
            lab = str(k)+' '+str(unique_value)
            ax[0].scatter(tmp['time'].unique(), X, label=lab, alpha=.6)
            ax[1].scatter(tmp['time'].unique(), Z, label=lab, alpha=.6)
        ax[0].set_ylabel(ev)
        ax[0].legend()
        ax[0].set_xlabel('time')
        ax[0].set_title("Median "+ev+" over time for different "+k)
        ax[1].set_ylabel(ev)
        ax[1].set_xlabel('time')
        ax[1].set_title("Mean "+ev+" over time for different "+k)
        fig.tight_layout()
        fig.savefig(folder+'/processing/hosts/'+ev+'_time_'+k+'_summarize.png',dpi=600)
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

                    tmp.plot.scatter(x='time', y=ev, c=colors,
                        alpha=0.1, s=2, ax=ax
                        )
                    try:
                        ax.set_ylim(min(hosts[ev]), max(hosts[ev]))
                    except:
                        pass
                    ax.set_ylabel(ev)
                    ax.set_xlabel('time')
                    ax.legend(handles = [mpatches.Patch(color=d[k], label=k) for k in d.keys()], title = other_param)
                    ax.set_title(ev+" over time for "+k+" "+str(unique_value))

                    fig.tight_layout()
                    fig.savefig(folder+'/processing/hosts/'+ev+'_time_'+other_param+"_"+str(unique_value)+'.png',dpi=600)
                    plt.close(fig)
                
                    fig, ax = plt.subplots(2, 1)
                    for value in hosts[other_param].unique():
                        tmp2 = tmp[tmp[other_param]==value]
                        X = [np.median(tmp2[tmp2['time']==t][ev]) for t in tmp2['time'].unique()]
                        Z = [np.mean(tmp2[tmp2['time']==t][ev]) for t in tmp2['time'].unique()]
                        lab = str(other_param)+' '+str(value)
                        ax[0].scatter(tmp2['time'].unique(), X, label=lab, alpha=.6)
                        ax[1].scatter(tmp2['time'].unique(), Z, label=lab, alpha=.6)
                    ax[0].set_ylabel(ev)
                    ax[0].legend()
                    ax[0].set_xlabel('time')
                    ax[0].set_title("Median "+ev+" over time for different "+other_param+"\n"+k+" is "+unique_value)
                    ax[1].set_ylabel(ev)
                    ax[1].set_xlabel('time')
                    ax[1].set_title("Mean "+ev+" over time for different "+other_param+"\n"+k+" is "+unique_value)
                    fig.tight_layout()
                    fig.savefig(folder+'/processing/hosts/'+ev+'_time_'+k+'-'+str(unique_value)+'_'+other_param+'_summarize.png',dpi=600)
                    plt.close(fig)
