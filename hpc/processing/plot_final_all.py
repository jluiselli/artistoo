import pandas as pd
import matplotlib.pyplot as plt 
import sys, os, shutil
import matplotlib.patches as mpatches
import matplotlib.colors as clrs
import numpy as np
import ast
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
parser.add_argument("-g", "--generation", type=int, help="generation for to plot. Default is last generation", default=-1)
parser.add_argument("-t", "--type", type=str, help="which type of cells to plot", default="host")


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
    if args.type == "host":
        df = pd.read_csv(folder+'/hosts.csv', low_memory=False, sep=";", dtype=str)
        df = df.drop(['time of birth','good','bads','dna','type'], axis=1)
    else:
        df = pd.read_csv(folder+'/mit.csv', low_memory=False, sep=';')
        df = df.drop(['products', 'bad products', 'sum dna', 'new DNA ids','type', 'host'], axis=1)

    df = df.drop([i for i in df.columns if i[:7]=='Unnamed'], axis=1)

except:
    print("***\nData must have been aggregated before use\n***")
    sys.exit()

df = df.astype({'time':float})
if args.generation!=-1:
    target_gen = args.generation
else:
    target_gen = max(df['time'])

if args.verbose:
    print("target generation is", target_gen)

df = df[df['time']==target_gen]

if args.verbose:
    print(df)

try:
    df['degradation']=df['degradation'].replace({'01':'0.1', '005':'0.05', '001':'0.01', '0025':'0.025', '0075':'0.075'})
except:
    pass
try:
    df['growth_rate']=df['growth_rate'].replace({'15':'1.5', '05':'0.5'})
except:
    pass

df = df.replace({'undefined':"NaN", "True":1,"False":0, "true":1, "false":0})
df = df.astype(float)

if args.verbose:
    print(df.columns)

if not os.path.isdir(folder+'/processing/'):
    print('The directory is not present. Creating a new one..')
    os.mkdir(folder+'/processing/')

if args.clean:
    shutil.rmtree(folder+'/processing/end_values/', ignore_errors=True)

if not os.path.isdir(folder+'/processing/end_values/'):
    print('The directory is not present or has been removed. Creating a new one..')
    os.mkdir(folder+'/processing/end_values/')


usual_colors = ['tab:blue', 'tab:orange', 'tab:green','tab:purple','tab:red',
'tab:pink','tab:brown'] 


evolvables = [i for i in df.columns if i[:10]=='evolvables']
# for ev in evolvables:
#     host = host.rename(columns = {ev : ev[11:]})

df = df.rename(columns = {'vol': 'vol_'+args.type})

non_plottable = [i for i in params]
non_plottable += ['time', 'id', 'V', 'seed', 'time of birth',
    'fission events', 'fusion events', 'repliosomes', 'parent', 'genes']


if len(params)==1:
    for k in params:
        if args.verbose:
            print(k)
        for val in df.columns:
            if args.verbose:
                print(val)
            if val not in non_plottable:
                if args.verbose:
                    print(val)
                
                fig, ax = plt.subplots(1, 1, figsize=(15,10))
                try:
                    sns.violinplot(x=k, y=val, inner=None, data=df, ax=ax,
                        color='.9')
                    sns.stripplot(x=k, y=val, hue="seed", data=df, ax=ax,
                        )
                    ax.set_title(str(folder)+'\n'+val+" at time "+str(target_gen))
                    ax.set_xlabel(k)
                    if val=='evolvables_fusion_rate':
                        ax.set_ylim(-1.2e-3, 1.2e-3)
                    elif val=='evolvables_host_division_volume':
                        ax.set_ylim(0,5000)
                    elif val=='evolvables_fission_rate':
                        ax.set_ylim(-1e-5,5.5e-5)
                    elif val=='evolvables_rep':
                        ax.set_ylim(5,35)
                    elif val=='evolvables_HOST_V_PER_OXPHOS':
                        ax.set_ylim(-1e-5,1)
                    else:
                        ax.set_ylim(min(df[val]), max(df[val]))

                    fig.tight_layout()
                    fig.savefig(folder+'/processing/end_values/'+val+'_'+k+'_time_'+str(target_gen)+'.png')
                except:
                    pass
                plt.close(fig)

else:
    print(df)
    for k in params: # different values given at the beginning of the simulation
        print(k)
        for unique_value in df[k].unique():
            tmp = df[df[k]==unique_value]
            for other_param in params:
                if args.verbose:
                    print(k, other_param)
                if k!=other_param and k!='seed':
                    for val in df.columns:
                        if val not in non_plottable:
                            if args.verbose:
                                print(k, other_param, val)
                            fig, ax = plt.subplots(1, 1, figsize=(15,10))
                            try:
                                sns.violinplot(x=other_param, y=val, inner=None, data=tmp, ax=ax,
                                    color='.9')
                                sns.stripplot(x=other_param, y=val, hue="seed", data=tmp, ax=ax,
                                    )
                                ax.set_title(str(folder)+'\n'+val+" at time "+str(target_gen)+" "+str(k)+" "+str(unique_value))
                                ax.set_xlabel(other_param)
                                if val=='evolvables_fusion_rate':
                                    ax.set_ylim(-1e-3, 1e-3)
                                elif val=='evolvables_host_division_volume':
                                    ax.set_ylim(0,5000)
                                elif val=='evolvables_fission_rate':
                                    ax.set_ylim(-1e-5,5.5e-5)
                                elif val=='evolvables_rep':
                                    ax.set_ylim(5,35)
                                elif val=='evolvables_HOST_V_PER_OXPHOS':
                                    ax.set_ylim(-1e-5,1)
                                else:
                                    ax.set_ylim(min(df[val]), max(df[val]))
                                fig.tight_layout()
                                fig.savefig(folder+'/processing/end_values/'+val+'_'+k+"_"+str(unique_value)+'_'+other_param+'_'+'_time_'+str(target_gen)+'.png')
                            except:
                                print("Failed for ",k, unique_value, other_param, val)
                                pass
                            plt.close(fig)


                