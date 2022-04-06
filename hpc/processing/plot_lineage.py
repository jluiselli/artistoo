import pandas as pd
import matplotlib.pyplot as plt 
import sys, os
import matplotlib.patches as mpatches
import numpy as np

folder = sys.argv[1]
subfolders = sys.argv[2:]

if subfolders == []:
    subfolders = [i for i in os.listdir(folder) if i[:4]=='seed']

if not os.path.isdir(folder+'/processing/'):
    print('The directory is not present. Creating a new one..')
    os.mkdir(folder+'/processing/')

for subfolder in subfolders:
    print(subfolder)

    if not os.path.isdir(folder+'/processing/'+subfolder):
        print('The directory is not present. Creating a new one..')
        os.mkdir(folder+'/processing/'+subfolder)

# Get data
    if os.path.exists(folder+'/'+subfolder+'/lineage.csv'):
        print("lineage exists")
        lineage = pd.read_csv(folder+'/'+subfolder+'/lineage.csv',sep=';')
    else:
        if os.path.exists(folder+'/'+subfolder+'/total_df.csv'):
            print("df exists")
            df = pd.read_csv(folder+'/'+subfolder+'/total_df.csv', sep=';')
        else:
            print("merging dfs")
            try:
                hosts = pd.read_csv('./'+folder+'/'+subfolder+'/Hosts_Mitochondrialog.txt', sep=';', low_memory=False)
                mit = pd.read_csv('./'+folder+'/'+subfolder+'/Mit_Mitochondrialog.txt', sep=';', low_memory=False)
            except:
                continue
            hosts = hosts.drop(['time of birth','good','bads','dna','type', 'fusion events', 'fission events'], axis=1)
            hosts = hosts.drop([i for i in hosts.columns if i[:7]=='Unnamed'], axis=1)
            hosts = hosts.astype(float)
            
            mit = mit.drop(['products', 'bad products', 'sum dna', 'new DNA ids', 'type', 'time of birth'], axis=1)
            mit = mit.drop([i for i in mit.columns if i[:7]=='Unnamed'], axis=1)
            mit = mit.astype(float)

            mit = mit.rename(columns = {'id':'mit_id','host':'host_id','V':'target_V_mit','vol':'vol_mit'})
            hosts = hosts.rename(columns = {'id':'host_id','V':'target_V_host','vol':'vol_host'})

            df = hosts.merge(mit, on=None, how='right')
            df.to_csv(folder+'/'+subfolder+'/total_df.csv',sep=";")
    

        lineage = df[df['time']==max(df['time'])]
        lastgener = df[df['time']==max(df['time'])]
        host_ids = list(lastgener['host_id'].unique())
        parents_ids = list(lastgener['parent'].unique())
        if df.empty:
            continue

        for t in reversed(df['time'].unique()):
            tmp = df[df['time']==t]
            for p_id in parents_ids:
                parent_df = tmp[tmp['host_id']==p_id]
                if not parent_df.empty:
                    lineage = pd.concat([lineage, parent_df])
                    parents_ids.remove(p_id)
                    host_ids += [p_id]
                    parents_ids += list(parent_df['parent'].unique())
                    # AJOUTER LE PARENT A SUIVRE
            for h_id in host_ids:
                host_df = tmp[tmp['host_id']==h_id]
                if host_df.empty:
                    host_ids.remove(h_id)
                else:
                    lineage = pd.concat([lineage, host_df])
            if len(host_ids)==0 or len(parents_ids) == 0:
                print("NO MORE CELLS TO TRACK ! ERROR !")
                raise ERROR
        
        print("sucessfully tracked ancestor !")
        lineage.to_csv(folder+'/'+subfolder+'/lineage.csv', sep=';')
    
    #Now plot
    lineage = lineage.drop([i for i in lineage.columns if i[:7]=='Unnamed'], axis=1)
    lineage = lineage.drop(['parent','host_id','mit_id'], axis=1)
    for col in lineage.columns:
        if col != 'time':
            fig, ax = plt.subplots(1, 1, figsize=(15,10))

            lineage.plot.scatter(x='time', y=col, alpha=0.9, s=10, ax=ax)

            Mean = [np.mean(lineage[lineage['time']==t][col]) for t in lineage['time'].unique()]

            plt.plot(lineage['time'].unique(), Mean, color='tab:red')  
            plt.plot(pd.DataFrame(lineage['time'].unique()).rolling(50).mean(),
                pd.DataFrame(Mean).rolling(50).mean(),
                color='tab:orange', linewidth=3)

            try:
                ax.set_ylim(0.99*min(lineage[col]), 1.01*max(lineage[col]))
            except:
                pass
            ax.set_ylabel(col)
            ax.set_xlabel('time')
            ax.set_title(col+" over time for the lineage")

            fig.tight_layout()
            fig.savefig(folder+'/processing/'+subfolder+'/'+col+'_lineage.png')
            plt.close(fig)
    
    
    col = 'total_mit_volume'
    fig, ax = plt.subplots(1, 1, figsize=(15,10))

    mit_vol = [np.sum(lineage[lineage['time']==t]['vol_mit']) for t in lineage['time'].unique()]
    plt.scatter(lineage['time'].unique(), mit_vol)
  
    try:
        ax.set_ylim(0.99*min(mit_vol), 1.01*max(mit_vol))
    except:
        pass
    ax.set_ylabel(col)
    ax.set_xlabel('time')
    ax.set_title(col+" over time for the lineage")

    fig.tight_layout()
    fig.savefig(folder+'/processing/'+subfolder+'/'+col+'_lineage.png')
    plt.close(fig)
