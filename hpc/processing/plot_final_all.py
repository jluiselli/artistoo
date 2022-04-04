import pandas as pd
import matplotlib.pyplot as plt 
import sys, os
import matplotlib.patches as mpatches
import matplotlib.colors as clrs
import numpy as np
import ast
import random
import colorsys
import seaborn as sns


folder = sys.argv[1]
params = sys.argv[2:]

if os.path.exists(folder+'/total_df.csv'):
    print("retrieving existing df")
    df = pd.read_csv(folder+'/total_df.csv', sep=';')
else:
    print("merging dfs")
    hosts=pd.read_csv(folder+'/hosts.csv', low_memory=False, sep=";", dtype=str)
    try:
        hosts = hosts.drop(['time of birth','good','bads','dna','type'], axis=1)
        hosts = hosts.drop([i for i in hosts.columns if i[:7]=='Unnamed'], axis=1)
    except:
        pass
    hosts['time']=hosts['time'].astype(float)
    hosts = hosts[hosts['time']<300000]
    print(hosts.columns)

    
    print("to mit")
    mit=pd.read_csv(folder+'/mit.csv', low_memory=False, sep=";", dtype=str)
    mit = mit.drop(['products', 'bad products', 'sum dna', 'new DNA ids', 'type'], axis=1)
    mit = mit.drop([i for i in mit.columns if i[:7]=='Unnamed'], axis=1)
    print(mit.columns)

    mit = mit.rename(columns = {'id':'mit_id','host':'host_id','V':'V_mit','vol':'vol_mit'})
    hosts = hosts.rename(columns = {'id':'host_id','V':'V_host','vol':'vol_host'})

    
    mit['time']=mit['time'].astype(float)
    mit = mit[mit['time']<300000]

    df = hosts.merge(mit, on=None, how='right')
    print(df)
    df.to_csv(folder+'/total_df.csv',sep=";")



try:
    df['degradation']=df['degradation'].replace({'01':'0.1', '005':'0.05', '001':'0.01', '0025':'0.025', '0075':'0.075'})
except:
    pass
try:
    df['growth_rate']=df['growth_rate'].replace({'15':'1.5', '05':'0.5'})
except:
    pass


df = df.drop([i for i in df.columns if i[:7]=='Unnamed'], axis=1)

for col in ['time', 'host_id', 'mit_id', 'V_mit', 'V_host', 'idx1', 'idx2', 'seed',
    'fission events', 'fusion events', 'repliosomes', 'parent']:
    try:
        df = df.drop([col])
    except:
        pass

df = df.replace({'undefined':np.NaN})
df = df.astype(float)

if not os.path.isdir(folder+'/processing/'):
    print('The directory is not present. Creating a new one..')
    os.mkdir(folder+'/processing/')

if not os.path.isdir(folder+'/processing/end_values/'):
    print('The directory is not present. Creating a new one..')
    os.mkdir(folder+'/processing/end_values/')


usual_colors = ['tab:blue', 'tab:orange', 'tab:green','tab:purple','tab:red',
'tab:pink','tab:brown'] 


evolvables = [i for i in df.columns if i[:10]=='evolvables']

for ev in evolvables:
    df = df.rename(columns = {ev : ev[11:]})


df = df[df['time']==max(df['time'])]

df = df[df['time']==299701]
print(df.shape)
print(df)
 #Plotting the last generation
non_plottable = [i for i in params]
non_plottable += ['time', 'host_id', 'mit_id', 'V_mit', 'V_host', 'idx1', 'idx2', 'seed',
    'fission events', 'fusion events', 'repliosomes', 'parent']

if len(params)==1:
    for k in params:
        print(k)
        d = {}
        i=0
        for value in df[k].unique():
            d[value] = usual_colors[i]
            i+=1
        colors = [d[i] for i in df[k]]
        for val in df.columns:
            if val not in non_plottable:
                if not val =='vol_mit':
                    tmp =df[df['type']=='host']
                else:
                    tmp =df[df['type']=='mito']
                print(val)
                
                fig, ax = plt.subplots(1, 1, figsize=(15,10))
                try:
                    sns.violinplot(x=k, y=val, inner=None, data=tmp, ax=ax,
                        color='.9')
                    sns.stripplot(x=k, y=val, hue="seed", data=tmp, ax=ax,
                        linewidth=1)
                    ax.set_title(str(folder)+'\n'+val+" at time "+str(max(df['time'])))
                    ax.set_xlabel(k)
                    if val=='fusion_rate':
                        ax.set_ylim(-1e-3, 1e-3)
                    elif val=='host_division_volume':
                        ax.set_ylim(0,5000)
                    elif val=='fission_rate':
                        ax.set_ylim(-1e-5,5.5e-5)
                    elif val=='rep':
                        ax.set_ylim(5,35)
                    elif val=='HOST_V_PER_OXPHOS':
                        ax.set_ylim(-1e-5,1)
                    else:
                        ax.set_ylim(min(df[val]), max(df[val]))

                    fig.tight_layout()
                    fig.savefig(folder+'/processing/end_values/'+val+'_'+k+'.png')
                except:
                    pass
                plt.close(fig)


else:
    for k in params: # different values given at the beginning of the simulation
        print(k)
        for unique_value in df[k].unique():
            tmp = df[df[k]==unique_value]
            max_time = max(tmp['time'].unique())

            for other_param in params:
                if k!=other_param:
                    for val in df.columns:
                        if not val =='vol_mit':
                            tmp2 =tmp[tmp['type']=='host']
                        else:
                            tmp2 =tmp[tmp['type']=='mito']
                        fig, ax = plt.subplots(1, 1, figsize=(15,10))
                        try:
                            sns.violinplot(x=other_param, y=val, inner=None, data=tmp2, ax=ax,
                                color='.2')
                            sns.stripplot(x=other_param, y=val, hue="seed", data=tmp2, ax=ax,
                                linewidth=1)
                            
                            ax.set_title(str(folder)+'\n'+val+" at time "+str(max_time)+" "+str(k)+" "+str(unique_value))
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
                                ax.set_ylim(min(df[val]), max(df[val]))

                            fig.tight_layout()
                            fig.savefig(folder+'/processing/final_fusion/'+val+'_'+k+"_"+str(unique_value)+'.png')
                        except:
                            pass
                        plt.close(fig)


                