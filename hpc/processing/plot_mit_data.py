import pandas as pd
import matplotlib.pyplot as plt 
import sys, os, shutil
import matplotlib.patches as mpatches
import matplotlib.colors as clrs
import numpy as np
import ast
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
parser.add_argument("-g", "--max_generation", type=int, help="end generation for the temporal plots. Default is last generation", default=-1)
parser.add_argument("-f", "--fraction", help="fraction of dataframe you want to plot (can be used to make plots quicker)", default=1, type=float)

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
    mit=pd.read_csv(folder+'/mit.csv', low_memory=False, sep=';')
    mit = mit.drop(['products', 'bad products', 'sum dna', 'new DNA ids'], axis=1)
    mit = mit.astype(float)
    mit = mit.sample(frac=args.fraction)
    if args.verbose:
        print(mit.columns)
except:
    print("Data must have been aggregated with aggregate.py before")
    exit


if not os.path.isdir(folder+'/processing/'):
    print('The directory is not present. Creating a new one..')
    os.mkdir(folder+'/processing/')

if args.clean:
    shutil.rmtree(folder+'/processing/mit/', ignore_errors=True)

if not os.path.isdir(folder+'/processing/mit/'):
    print('The directory is not present (or was deleted). Creating a new one..')
    os.mkdir(folder+'/processing/mit')


usual_colors = ['tab:blue', 'tab:orange', 'tab:green','tab:purple','tab:red',
'tab:pink','tab:brown'] 


try:
    mit['growth_rate']=mit['growth_rate'].replace({15:1.5, 5:0.5})
except:
    pass
mit['bad_oxphos']=mit['ros']-mit['oxphos']

# interest_params = ['V','vol','n DNA','oxphos','ros','bad_oxphos', 'translate', 'replicate', 'replisomes', 'unmut']
interest_params = ['vol','n DNA','oxphos','ros','replisomes', 'unmut']

if args.max_generation != -1:
    mit = mit[mit['time'] <= max_generation]
mit = mit [mit['time']>=5000]

# if params[-1]=='seed':
#     unique_plots = True
#     params = params[:-1]
# else:
#     unique_plots = False

# if unique_plots:
if args.verbose:
    print("doing all unique plots")
comb = []
for k in params:
    tmp_list = []
    for val in mit[k].unique():
        tmp_list+=[val]
    comb += [tmp_list]
combinations = list(itertools.product(*comb))
for c in combinations:
    if args.verbose:
        print("unique plot",c)
    tmp = mit
    i=0
    for k in params:
        tmp = tmp[tmp[k]==c[i]]
        if tmp.empty:
            continue
        i+=1
    for ev in interest_params:
        if args.verbose:
            print(ev)
        fig, ax = plt.subplots(1, 1, figsize=(15,10))
        for seed in mit['seed'].unique():
            tmp2 = tmp[tmp['seed']==seed]
            if not tmp2.empty:
                Z = [np.mean(tmp2[tmp2['time']==t][ev]) for t in tmp2['time'].unique()]
                lab = 'seed '+str(seed)
                ax.scatter(tmp2['time'].unique(), Z, label=lab, alpha=.6)
        ax.set_ylabel(ev)
        ax.set_xlabel('time')
        ax.set_title("Mean "+ev+" over time for "+str(c))
        ax.legend()
        fig.tight_layout()
        fig.savefig(folder+'/processing/mit/'+ev+'_time_'+str(c)+'_mean.png')
        plt.close(fig)
        
if args.verbose:
    print("finished unique plots. On to merged seeds")

for k in params: # different values given at the beginning of the simulation    
    for ev in interest_params:
        if args.verbose:
            print(ev, " starting")
        try:
            mit[ev]=mit[ev].astype(float)
        except:
            continue

        fig, ax = plt.subplots(1, 1, figsize=(15,10))
        for unique_value in mit[k].unique():
            tmp = mit[mit[k]==unique_value]
            if tmp.empty:
                continue
            Z = [np.mean(tmp[tmp['time']==t][ev]) for t in tmp['time'].unique()]
            lab = str(k)+' '+str(unique_value)
            ax.scatter(tmp['time'].unique(), Z, label=lab, alpha=.6)
        ax.set_ylabel(ev)
        ax.set_xlabel('time')
        ax.set_title("Mean "+ev+" over time for different "+k)
        fig.tight_layout()
        fig.savefig(folder+'/processing/mit/'+ev+'_time_'+k+'_summarize.png')
        plt.close(fig)

        if args.verbose:
            print(ev,k," done")

        for unique_value in mit[k].unique():
            tmp = mit[mit[k]==unique_value]
            if tmp.empty:
                continue
            for other_param in params:
                if k!=other_param:

                    fig, ax = plt.subplots(1, 1, figsize=(15,10))
                    for value in mit[other_param].unique():
                        tmp2 = tmp[tmp[other_param]==value]
                        if tmp2.empty:
                            continue
                        Z = [np.mean(tmp2[tmp2['time']==t][ev]) for t in tmp2['time'].unique()]
                        lab = str(other_param)+' '+str(value)
                        ax.scatter(tmp2['time'].unique(), Z, label=lab, alpha=.6)
                    ax.set_ylabel(ev)
                    ax.legend()
                    ax.set_xlabel('time')
                    ax.set_title("Mean "+ev+" over time for different "+other_param+"\n"+k+" is "+str(unique_value))
                    fig.tight_layout()
                    fig.savefig(folder+'/processing/mit/'+ev+'_time_'+k+'-'+str(unique_value)+'_'+other_param+'_summarize.png')
                    plt.close(fig)


