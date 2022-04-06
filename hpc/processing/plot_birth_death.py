import pandas as pd
import matplotlib.pyplot as plt 
import sys, os, shutil
import matplotlib.patches as mpatches
import numpy as np
import random
import colorsys
import itertools
import argparse
 
# Initialize parser
parser = argparse.ArgumentParser()

# Adding optional argument
parser.add_argument("folder", help="folder in which to run the code") # positional arg
parser.add_argument("-c", "--competition", help = "Specify that dual values are expected", action="store_true")
parser.add_argument("-p", dest='params', help="parameters in folder names to use", nargs='+')
parser.add_argument("-v", "--verbose", help="print more information", action="store_true")
parser.add_argument("--clean", help="cleans the folder before replotting", action="store_true")
parser.add_argument("-g", "--max_generation", help="end generation for the temporal plots. Default is last generation", default=-1)

# Read arguments from command line
args = parser.parse_args()
if args.verbose:
    print(args)

folder = args.folder
params = args.params

if args.competition:
    print("handling of competition runs for this plot not implemented yet")
    sys.exit()

try:
    df_deaths = pd.read_csv(folder+'/deaths.csv', low_memory=False, sep=";")
    df_divisions = pd.read_csv(folder+'/divisions.csv', low_memory=False, sep=';')
    if args.verbose:
        print(df_deaths.columns)
        print(df_divisions.columns)
except:
    print("***\nDeaths and births must have been aggregated !\nWarning: this can be very long for ancient simulations\n***")
    sys.exit()

if args.max_generation != -1:
    df_deaths = df_deaths[df_deaths['time']<args.max_generation]
    df_divisions = df_divisions[df_divisions['time']<args.max_generation]


if not os.path.isdir(folder+'/processing/'):
    print('The directory is not present. Creating a new one..')
    os.mkdir(folder+'/processing/')

if args.clean:
    shutil.rmtree(folder+'/processing/deaths_births/')

if not os.path.isdir(folder+'/processing/deaths_births/'):
    print('The directory is not present or has been removed. Creating a new one..')
    os.mkdir(folder+'/processing/deaths_births/')


usual_colors = ['tab:blue', 'tab:orange', 'tab:green','tab:purple','tab:red',
'tab:pink','tab:brown'] 


if params[-1]=='seed':
    unique_plots = True

for celltype in ['host','mito']:
    if args.verbose:
        print(celltype)
    deaths = df_deaths[df_deaths['type']==celltype]
    divisions = df_divisions[df_divisions['type']==celltype]
    if unique_plots:
        if args.verbose:
            print("doing all unique plots")
        comb = []
        for k in params:
            tmp_list = []
            for val in hosts[k].unique():
                tmp_list+=[val]
            comb += [tmp_list]
        combinations = list(itertools.product(*comb))
        for c in combinations:
            if args.verbose:
                print("unique plot",c)
            tmp_deaths = deaths
            tmp_divisions = divisions
            i=0
            for k in params:
                tmp_deaths = tmp_deaths[tmp_deaths[k]==c[i]]
                tmp_divisions = tmp_divisions[tmp_divisions[k]==c[i]]
                i+=1
            if tmp_deaths.empty or tmp_divisions.empty:
                continue
            
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
        if args.verbose:
            print("finished unique plots. On to merged seeds")
        

    for k in params: # different values given at the beginning of the simulation
        if args.verbose:
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
            if tmp_deaths.empty or tmp_divisions.empty:
                continue
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