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
    df_deaths = pd.read_csv(folder+'/deaths.csv', low_memory=False, sep=";")
    df_divisions = pd.read_csv(folder+'/divisions.csv', low_memory=False, sep=';')
    print(deaths.columns)
    print(divisions.columns)
    
except:
    print("Data must have been aggregated with aggregate.py before")


if not os.path.isdir(folder+'/processing/'):
    print('The directory is not present. Creating a new one..')
    os.mkdir(folder+'/processing/')

if not os.path.isdir(folder+'/processing/deaths_births/'):
    print('The directory is not present. Creating a new one..')
    os.mkdir(folder+'/processing/deaths_births/')


usual_colors = ['tab:blue', 'tab:orange', 'tab:green','tab:purple','tab:red',
'tab:pink','tab:brown'] 


if params[-1]=='seed':
    unique_plots = True

for celltype in ['host','mito']:
    print(celltype)
    deaths = df_deaths[df_deaths['type']==celltype]
    divisions = df_divisions[df_divisions['type']==celltype]
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
            tmp_deaths = deaths
            tmp_divisions = divisions
            i=0
            for k in params:
                tmp_deaths = tmp_deaths[tmp_deaths[k]==c[i]]
                tmp_divisions = tmp_divisions[tmp_divisions[k]==c[i]]
                i+=1
            
            fig, ax = plt.subplots(1, 1, figsize=(15,10))
            tmp_deaths.plot.hist(column='time', 
                alpha=0.9, ax=ax  )
            ax.set_ylabel('# deaths')
            ax.set_xlabel('time')
            ax.set_title("# deaths over time "+str(c))
            fig.tight_layout()
            fig.savefig(folder+'/processing/deaths_births/death_time_'+str(c)+'.png')
            plt.close(fig)

            fig, ax = plt.subplots(1, 1, figsize=(15,10))
            tmp_divisions.plot.hist(column='time', 
                alpha=0.9, ax=ax  )
            ax.set_ylabel('# divisions')
            ax.set_xlabel('time')
            ax.set_title("# divisions over time "+str(c))
            fig.tight_layout()
            fig.savefig(folder+'/processing/deaths_births/birth_time_'+str(c)+'.png')
            plt.close(fig)

        params = params[:-1]
        print("finished unique plots. On to merged seeds")
        

    for k in params: # different values given at the beginning of the simulation
        print(k)

        fig, ax = plt.subplots(1, 1, figsize=(15,10))
        deaths.plot.hist(column='time', alpha=.4, by=k, ax=ax)
        ax.set_ylabel('# deaths')
        ax.set_xlabel('time')
        ax.set_title("deaths over time for different "+k)
        fig.tight_layout()
        fig.savefig(folder+'/processing/deaths_births/death_time_'+k+'.png')
        plt.close(fig)

        fig, ax = plt.subplots(1, 1, figsize=(15,10))
        divisions.plot.hist(column='time', alpha=.4, by=k, ax=ax)
        ax.set_ylabel('# divisions')
        ax.set_xlabel('time')
        ax.set_title("divisions over time for different "+k)
        fig.tight_layout()
        fig.savefig(folder+'/processing/births_births/birth_time_'+k+'.png')
        plt.close(fig)


        for unique_value in deaths[k].unique():
            tmp_deaths = deaths[deaths[k]==unique_value]
            tmp_divisions = divisions[divisions[k]==unique_value]
            for other_param in params:
                if k!=other_param:
                    fig, ax = plt.subplots(1, 1, figsize=(15,10))
                    tmp_deaths.plot.hist(column='time', by=other_param,
                        alpha=0.4, ax=ax
                        )
                    ax.set_ylabel('#deaths')
                    ax.set_xlabel('time')
                    ax.set_title("deaths over time for "+k+" "+str(unique_value))
                    fig.tight_layout()
                    fig.savefig(folder+'/processing/deaths_births/death_time_'+other_param+"_"+str(unique_value)+'.png')
                    plt.close(fig)

                    fig, ax = plt.subplots(1, 1, figsize=(15,10))
                    tmp_divisions.plot.hist(column='time', by=other_param,
                        alpha=0.4, ax=ax
                        )
                    ax.set_ylabel('#deaths')
                    ax.set_xlabel('time')
                    ax.set_title("deaths over time for "+k+" "+str(unique_value))
                    fig.tight_layout()
                    fig.savefig(folder+'/processing/deaths_births/birth_time_'+other_param+"_"+str(unique_value)+'.png')
                    plt.close(fig)