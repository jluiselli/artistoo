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

# try:
if os.path.exists(folder+'/total_df.csv'):
    print("retrieving existing df")
    df = pd.read_csv(folder+'/total_df.csv', sep=';')
else:
    print("merging dfs")
    hosts=pd.read_csv(folder+'/hosts.csv', low_memory=False, sep=";", dtype=str)
    try:
        hosts = hosts.drop(['time of birth','good','bads','dna','type', 'Unnamed: 20'], axis=1)
        hosts = hosts.drop(['evolvables', 'subcells'], axis=1)
    except:
        pass
    print(hosts.columns)
    for col in hosts.columns:
        hosts[col] = hosts[col].replace({'undefined':np.NaN})
        hosts[col] = hosts[col].astype(float)
    hosts = hosts.astype(float)
    mit=pd.read_csv(folder+'/mit.csv', low_memory=False, sep=";", dtype=str)
    print(mit.columns)
    mit = mit.drop(['products', 'bad products', 'sum dna', 'new DNA ids', 'type', 'Unnamed: 19'], axis=1)
    for col in mit.columns:
        print(col)
        mit[col] = mit[col].replace({'undefined':np.NaN})
        mit[col] = mit[col].astype(float)
    mit = mit.astype(float)
    # hosts.drop('subcells')
    mit = mit.rename(columns = {'id':'mit_id','host':'host_id','V':'V_mit','vol':'vol_mit','Unnamed: 0':'idx1'})
    hosts = hosts.rename(columns = {'id':'host_id','V':'V_host','vol':'vol_host','Unnamed: 0':'idx2'})
    joint_on = ['time','host_id','seed']+params

    df = hosts.merge(mit, on=None, how='right')
    print(df)
    df.to_csv(folder+'/total_df.csv',sep=";")
# except:
#     print("Data must have been aggregated with aggregate.py before")
#     exit


if not os.path.isdir(folder+'/processing/'):
    print('The directory is not present. Creating a new one..')
    os.mkdir(folder+'/processing/')

if not os.path.isdir(folder+'/processing/fusion/'):
    print('The directory is not present. Creating a new one..')
    os.mkdir(folder+'/processing/fusion/')


usual_colors = ['tab:blue', 'tab:orange', 'tab:green','tab:purple','tab:red',
'tab:pink','tab:brown'] 


print(df.columns)
evolvables = [i for i in df.columns if i[:10]=='evolvables']
print(evolvables)
for ev in evolvables:
    df = df.rename(columns = {ev : ev[11:]})
print(df.columns)
df['growth_rate']=df['growth_rate'].replace({15:1.5, 5:0.5})
df['time'] = df['time'].astype(float)
df['fusion_rate'] = df['fusion_rate'].astype(float)
df = df.astype(float)
df = df[df['time']>=max(df['time'])-10000] #Plotting the 10000 last generations

for k in params:
    non_plottable = [i for i in params]
    non_plottable += ['time', 'fusion_rate', 'host_id', 'mit_id', 'V_mit', 'V_host', 'idx1', 'idx2', 'seed',
    'fission events', 'fusion events', 'repliosomes', 'parent']
    print(k)
    for val in df.columns[2:]:
        df[val]=df[val].astype(float)
        print(val)
        if val not in non_plottable:
            df[val] = df[val].astype(float)

            d = {}
            i=0
            for value in df[k].unique():
                d[value] = usual_colors[i]
                i+=1
            colors = [d[i] for i in df[k]]
            
            
            fig, ax = plt.subplots(1, 1, figsize=(15,10))
            df.plot.scatter(x=val, y='fusion_rate', c=colors,
                alpha=0.1, s=20, ax=ax
                )
            ax.set_ylim(min(df['fusion_rate']), max(df['fusion_rate']))
            try:
                ax.set_xlim(min(df[val]), max(df[val]))
            except:
                pass
        
            ax.set_ylabel('fusion_rate')
            ax.set_xlabel(val)
            ax.legend(handles = [mpatches.Patch(color=d[k], label=k) for k in d.keys()], title = k)
            ax.set_title("fusion rate against "+val+" for different "+k)

            fig.tight_layout()
            fig.savefig(folder+'/processing/fusion/'+val+'_'+k+'.png')
            plt.close(fig)
            print(k,val,'done')
            

            for other_param in params:
                if other_param!=k:
                    for unique_value in df[k].unique():
                        tmp = df[df[k]==unique_value]

                        d = {}
                        i=0
                        for value in df[other_param].unique():
                            d[value] = usual_colors[i]
                            i+=1
                        colors = [d[i] for i in tmp[other_param]]

                        fig, ax = plt.subplots(1, 1, figsize=(15,10))
                        tmp.plot.scatter(x=val, y='fusion_rate', c=colors,
                            alpha=0.1, s=20, ax=ax
                            )
                        ax.set_xlim(min(df[val]), max(df[val]))
                        ax.set_ylim(min(df['fusion_rate']), max(df['fusion_rate']))
                        ax.set_ylabel('fusion_rate')
                        ax.set_xlabel(val)
                        ax.legend(handles = [mpatches.Patch(color=d[k], label=k) for k in d.keys()], title = other_param)
                        ax.set_title("fusion rate against "+val+" with "+k+"="+str(unique_value))

                        fig.tight_layout()
                        fig.savefig(folder+'/processing/fusion/'+val+'_'+k+'_'+str(unique_value)+'.png')
                        plt.close(fig)

            print(k,val,'unique \ done')
