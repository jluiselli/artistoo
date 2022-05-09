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

    hosts = pd.read_csv('./'+folder+'/'+subfolder+'/Hosts_Mitochondrialog.txt', sep=';')
    mit = pd.read_csv('./'+folder+'/'+subfolder+'/Mit_Mitochondrialog.txt', sep=';')

    unnamed = [i for i in hosts.columns if i[:7]=='Unnamed']
    hosts = hosts.drop(['parent', 'type', 'fusion events',
        'fission events', 'good', 'bads', 'time of birth'], axis=1)
    hosts = hosts.drop(unnamed, axis = 1)
    hosts = hosts.rename(columns={'V':'target V'})  
    
    unnamed = [i for i in mit.columns if i[:7]=='Unnamed']
    mit = mit.drop(['host', 'type', 'sum dna', 'time of birth',
        'new DNA ids'], axis=1)
    mit = mit.drop(unnamed, axis = 1)
    mit = mit.rename(columns={'V':'target V'})
    mit_prod = mit[['time','products']]
    mit_badprod = mit[['time','bad products']]
    mit = mit.drop(['products', 'bad products'], axis=1)
    mit_prod = [list(map(int, s.split(','))) for s in mit_prod['products']]
    mit_badprod = [list(map(int, s.split(','))) for s in mit_badprod['bad products']]

    host_dna = hosts[['dna','time']]
    hosts = hosts.drop('dna',axis=1)
    host_dna['dna']= [list(map(int, s.split(','))) for s in host_dna['dna']]
    
    try:
        hosts = hosts.replace({'undefined':np.NaN})
    except:
        pass

    if (len(hosts.columns)>12) or (len(mit.columns)>12):
        print(hosts.columns)
        print(len(hosts.columns))
        print(len(mit.columns))
        raise "Not correct format"

    fig, ax = plt.subplots(3, 4, figsize=(25,15))
    j=0
    for col in hosts.columns:
        if col != 'time':
            print(col)
            tmp = hosts.drop(hosts.index[hosts[col] == 'undefined'])
            # if col=='total_vol':
            #     continue # Il faudrait virer les lignes qui ont des « undefined »
            try:
                Mean = [np.mean(tmp[tmp['time']==t][col]) for t in tmp['time'].unique()]
                Median = [np.median(tmp[tmp['time']==t][col]) for t in tmp['time'].unique()]
            except:
                ax[j//4][j%4].set_ylabel(col)
                j+=1
                continue
            ax[j//4][j%4].scatter(tmp['time'],tmp[col],s=0.5)
            ax[j//4][j%4].plot(tmp['time'].unique(),Mean,color='tab:red')
            ax[j//4][j%4].plot(tmp['time'].unique(),Median,color='tab:blue')
            ax[j//4][j%4].set_ylabel(col)
            ax[j//4][j%4].set_ylim(min(tmp[col]),max(tmp[col]))
            j+=1
    fig.suptitle(subfolder)
    fig.tight_layout()
    fig.savefig(folder+'/processing/'+subfolder+'/hosts.png',dpi=600)
    plt.close(fig)


    fig, ax = plt.subplots(3, 4, figsize=(25,15))
    j=0
    for col in mit.columns:
        if col != 'time':
            print(col)
            tmp = mit.drop(mit.index[mit[col] == 'undefined'])
            try:
                Mean = [np.mean(tmp[tmp['time']==t][col]) for t in tmp['time'].unique()]
                Median = [np.median(tmp[tmp['time']==t][col]) for t in tmp['time'].unique()]
            except:
                ax[j//4][j%4].set_ylabel(col)
                j+=1
                continue
            ax[j//4][j%4].scatter(tmp['time'],tmp[col],s=0.5)
            ax[j//4][j%4].plot(tmp['time'].unique(),Mean,color='tab:red')
            ax[j//4][j%4].plot(tmp['time'].unique(),Median,color='tab:blue')
            ax[j//4][j%4].set_ylabel(col)
            ax[j//4][j%4].set_ylim(min(tmp[col]),max(tmp[col]))
            j+=1
    fig.suptitle(subfolder)
    fig.tight_layout()
    fig.savefig(folder+'/processing/'+subfolder+'/mit.png',dpi=600)
    plt.close(fig)
    
    
