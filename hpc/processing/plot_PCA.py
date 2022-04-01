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
import plotly.express as px
from sklearn.decomposition import PCA


folder = sys.argv[1]
params = sys.argv[2:]

try:
    hosts=pd.read_csv(folder+'/hosts.csv', low_memory=False, sep=";", dtype=str)
    print(hosts.columns)
except:
    print("Data must have been aggregated with aggregate.py before")

hosts = hosts.drop([i for i in hosts.columns if i[:7]=='Unnamed'], axis=1)
hosts = hosts.drop(['time of birth','good','bads','dna','type', 'fission events', 'fusion events'], axis=1)
hosts = hosts[hosts['time']==max(hosts['time'])]
hosts = hosts.astype(float)


if not os.path.isdir(folder+'/processing/'):
    print('The directory is not present. Creating a new one..')
    os.mkdir(folder+'/processing/')

if not os.path.isdir(folder+'/processing/pca/'):
    print('The directory is not present. Creating a new one..')
    os.mkdir(folder+'/processing/pca/')

usual_colors = ['tab:blue', 'tab:orange', 'tab:green','tab:purple','tab:red',
'tab:pink','tab:brown'] 

try:
    hosts['growth_rate']=hosts['growth_rate'].replace({'15':'1.5', '05':'0.5'})
except:
    pass

X = hosts.drop([p for p in params], axis=1)
Y = X.drop([col for col in X.columns if col[:4]=="evol"], axis=1)

for p in params:
    # fig, ax = plt.subplots(1, 1, figsize=(15,10))
    X = hosts.drop([p for p in params], axis=1)
    X = X.drop(['time', 'id'], axis=1)
    Y = X.drop([col for col in X.columns if col[:4]=="evol"], axis=1)
    pca = PCA(n_components=2)
    components = pca.fit_transform(X)

    hosts[p]=hosts[p].astype(str)
    fig = px.scatter(components, x=0, y=1, color=hosts[p], title='PCA_'+p)                        
    fig.write_image(folder+'/processing/pca/PCA_'+p+'.png')
    plt.close()

    components = pca.fit_transform(Y)
    fig = px.scatter(components, x=0, y=1, color=hosts[p], title='PCA_noeevparam_'+p)                        
    fig.write_image(folder+'/processing/pca/PCA_noeevparam_'+p+'.png')
    plt.close()

    for unique_value in hosts[p].unique():
        if p != 'seed':
            tmp = hosts[hosts[p]==unique_value]
            tmp['seed']=tmp['seed'].astype(str)
            X = tmp.drop([p for p in params], axis=1)
            X = X.drop(['time', 'id'], axis=1)
            Y = X.drop([col for col in X.columns if col[:4]=="evol"], axis=1)
            pca = PCA(n_components=2)
            components = pca.fit_transform(X)

            hosts[p]=hosts[p].astype(str)
            fig = px.scatter(components, x=0, y=1, color=tmp['seed'], title='PCA_'+p+str(unique_value))                        
            fig.write_image(folder+'/processing/pca/PCA_'+p+str(unique_value)+'.png')
            plt.close()

            components = pca.fit_transform(Y)
            hosts[p]=hosts[p].astype(str)
            fig = px.scatter(components, x=0, y=1, color=tmp['seed'], title='PCA_noeevparam_'+p+str(unique_value))                        
            fig.write_image(folder+'/processing/pca/PCA_noeevparam_'+p+str(unique_value)+'.png')
            plt.close()

