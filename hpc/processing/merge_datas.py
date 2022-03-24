import pandas as pd
import sys, os
import numpy as np


folder = sys.argv[1]

# try:
if os.path.exists(folder+'/total_df.csv'):
    print("df exists")
else:
    print("merging dfs")
    hosts=pd.read_csv(folder+'/hosts.csv', low_memory=False, sep=";", dtype=str)
    try:
        hosts = hosts.drop(['time of birth','good','bads','dna','type'], axis=1)
        hosts = hosts.drop([i for i in hosts.columns if i[:7]=='Unnamed'], axis=1)
    
    except:
        pass
    print(hosts.columns)

    for col in hosts.columns:
        hosts[col] = hosts[col].replace({'undefined':np.NaN})
        hosts[col] = hosts[col].astype(float)
    hosts = hosts.astype(float)
    
    mit=pd.read_csv(folder+'/mit.csv', low_memory=False, sep=";", dtype=str)
    print(mit.columns)
    mit = mit.drop(['products', 'bad products', 'sum dna', 'new DNA ids', 'type'], axis=1)
    mit = mit.drop([i for i in hosts.columns if i[:7]=='Unnamed'], axis=1)
    
    for col in mit.columns:
        mit[col] = mit[col].replace({'undefined':np.NaN})
        mit[col] = mit[col].astype(float)
    mit = mit.astype(float)

    mit = mit.rename(columns = {'id':'mit_id','host':'host_id','V':'target_V_mit','vol':'vol_mit'})
    hosts = hosts.rename(columns = {'id':'host_id','V':'target_V_host','vol':'vol_host'})

    df = hosts.merge(mit, on=None, how='right')
    print(df)
    df.to_csv(folder+'/total_df.csv',sep=";")
