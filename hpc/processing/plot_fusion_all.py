import pandas as pd
import matplotlib.pyplot as plt 
import sys, os, shutil
import numpy as np
import random
import colorsys
import argparse
import seaborn as sns
 
# Initialize parser
parser = argparse.ArgumentParser()

# Adding optional argument
parser.add_argument("folder", help="folder in which to run the code")
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
    hosts['time']=hosts['time'].astype(float)
    if args.max_generation != -1:
        target_gen = max(hosts['time'])
    else:
        target_gen = args.max_generation
    hosts = hosts[hosts['time']<target_gen]
    if args.verbose:
        print(hosts.columns)

        
        print("to mit")
    mit=pd.read_csv(folder+'/mit.csv', low_memory=False, sep=";", dtype=str)
    mit = mit.drop(['products', 'bad products', 'sum dna', 'new DNA ids', 'type', 'time of birth'], axis=1)
    mit = mit.drop([i for i in mit.columns if i[:7]=='Unnamed'], axis=1)
    if args.verbose:
        print(mit.columns)

    mit = mit.rename(columns = {'id':'mit_id','host':'host_id','V':'V_mit','vol':'vol_mit'})
    hosts = hosts.rename(columns = {'id':'host_id','V':'V_host','vol':'vol_host'})

    
    mit['time']=mit['time'].astype(float)
    mit = mit[mit['time']<target_gen]

    df = hosts.merge(mit, on=None, how='right')
    df = df.replace({'undefined':"NaN"})
    if args.verbose:
        print(df)
    df.to_csv(folder+'/total_df.csv',sep=";")
# except:
#     print("Data must have been aggregated with aggregate.py before")
#     exit



try:
    df['degradation']=df['degradation'].replace({'01':'0.1', '005':'0.05', '001':'0.01', '0025':'0.025', '0075':'0.075'})
except:
    pass

try:
    df = df.drop([i for i in df.columns if i[:7]=='Unnamed'], axis=1)
except:
    pass

df = df.replace({'undefined':"NaN"})
df = df.astype(float)

if not os.path.isdir(folder+'/processing/'):
    print('The directory is not present. Creating a new one..')
    os.mkdir(folder+'/processing/')

if args.clean:
    shutil.rmtree(folder+'/processing/fusion/', ignore_errors=True)

if not os.path.isdir(folder+'/processing/fusion/'):
    print('The directory is not present or has been deleted. Creating a new one..')
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

for k in params:
    non_plottable = [i for i in params]
    non_plottable += ['time', 'fusion_rate', 'host_id', 'mit_id', 'V_mit', 'V_host', 'idx1', 'idx2', 'seed',
    'fission events', 'fusion events', 'repliosomes', 'parent', 'growth_rate', 'damage_rate']
    if args.verbose:
        print(k)
    for val in df.columns:
        if args.verbose:
            print(val)
        if val not in non_plottable:
            df = df.astype({val:float})
            df = df.astype({k:str})
            fig, ax = plt.subplots(1, 1, figsize=(15,10))
            sns.scatterplot(x=val, y='fusion_rate', hue=k,
                data=df, alpha = 0.1, s=20, ax=ax)

            ax.set_ylim(min(df['fusion_rate']), max(df['fusion_rate']))
            ax.set_xlim(min(df[val]), max(df[val]))
        
            ax.set_ylabel('fusion_rate')
            ax.set_xlabel(val)
            if val=="vol_mit":
                ax.set_xscale('log')
            if val=="n DNA":
                # Function x**(1/2)
                def forward(x):
                    return x**(1/2)
                def inverse(x):
                    return x**2
                ax.set_xscale('function', functions=(forward, inverse))
            ax.legend()
            ax.set_title("fusion rate against "+val+" for different "+k)
            fig.tight_layout()
            fig.savefig(folder+'/processing/fusion/'+val+'_'+k+'.png',dpi=600)
            plt.close(fig)
            if args.verbose:
                print(k,val,'done')
            
            for other_param in params:
                if other_param!=k and other_param!='seed':
                    for unique_value in df[k].unique():
                        tmp = df[df[k]==unique_value]
                        if tmp.empty:
                            continue
                        
                        df = df.astype({other_param:str})
                        fig, ax = plt.subplots(1, 1, figsize=(15,10))
                        sns.scatterplot(x=val, y='fusion_rate', hue=other_param,
                            alpha=0.1, s=20, ax=ax, data=tmp
                            )
                        ax.set_xlim(min(df[val]), max(df[val]))
                        ax.set_ylim(min(df['fusion_rate']), max(df['fusion_rate']))
                        ax.set_ylabel('fusion_rate')
                        ax.set_xlabel(val)
                        if val=="vol_mit":
                            ax.set_xscale('log')
                        if val=="n DNA":
                            # Function x**(1/2)
                            def forward(x):
                                return x**(1/2)
                            def inverse(x):
                                return x**2
                            ax.set_xscale('function', functions=(forward, inverse))
                        ax.legend()
                        ax.set_title("fusion rate against "+val+" with "+k+"="+str(unique_value))

                        fig.tight_layout()
                        fig.savefig(folder+'/processing/fusion/'+val+'_'+k+'_'+str(unique_value)+'.png',dpi=600)
                        plt.close(fig)
            
            if args.verbose:
                print(k,val,'unique \ done')
