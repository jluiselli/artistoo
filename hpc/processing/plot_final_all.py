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
parser.add_argument("-g", "--generation", help="generation for to plot. Default is last generation", default=-1)


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
    host = pd.read_csv(folder+'/hosts.csv', low_memory=False, sep=";", dtype=str)
    host = host.drop(['time of birth','good','bads','dna','type'], axis=1)
    host = host.drop([i for i in host.columns if i[:7]=='Unnamed'], axis=1)
    if (not "growth_rate" in params) and ("growth_rate" in host.columns):
        host = host.drop(["growth_rate"], axis=1)

    mit = pd.read_csv(folder+'/mit.csv', low_memory=False, sep=';')
    mit = mit.drop(['products', 'bad products', 'sum dna', 'new DNA ids','type', 'host'], axis=1)
    mit = mit.drop([i for i in mit.columns if i[:7]=='Unnamed'], axis=1)
    if (not "growth_rate" in params) and ("growth_rate" in mit.columns):
        mit = mit.drop(["growth_rate"], axis=1)
except:
    print("***\nData must have been aggregated before use\n***")
    sys.exit()

host = host.astype({'time':float})
mit = mit.astype({'time':float})
if args.generation!=-1:
    target_gen = args.generation
else:
    target_gen = max(host['time'])

host = host[host['time']==target_gen]
mit = mit[mit['time']==target_gen]

try:
    mit['degradation']=mit['degradation'].replace({'01':'0.1', '005':'0.05', '001':'0.01', '0025':'0.025', '0075':'0.075'})
    host['degradation']=host['degradation'].replace({'01':'0.1', '005':'0.05', '001':'0.01', '0025':'0.025', '0075':'0.075'})
except:
    pass
try:
    mit['growth_rate']=mit['growth_rate'].replace({'15':'1.5', '05':'0.5'})
    host['growth_rate']=host['growth_rate'].replace({'15':'1.5', '05':'0.5'})
except:
    pass
try:
    host = host.drop([i for i in host.columns if i[:7]=='Unnamed'], axis=1)
    mit = mit.drop([i for i in mit.columns if i[:7]=='Unnamed'], axis=1)
except:
    pass

host = host.replace({'undefined':"NaN"})
host = host.astype(float)
mit = mit.replace({'undefined':"NaN"})
mit = mit.astype(float)


if args.verbose:
    print(host.columns)
    print(mit.columns)

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


evolvables = [i for i in host.columns if i[:10]=='evolvables']
for ev in evolvables:
    host = host.rename(columns = {ev : ev[11:]})

host = host.rename(columns = {'vol': 'vol_host'})
mit = mit.rename(columns = {'vol': 'vol_mit'})

non_plottable = [i for i in params]
non_plottable += ['time', 'id', 'V', 'seed', 'time of birth',
    'fission events', 'fusion events', 'repliosomes', 'parent']

for df in [host,mit]:
    if len(params)==1:
        for k in params:
            if args.verbose:
                print(k)
            for val in df.columns:
                if val not in non_plottable:
                    tmp=df
                    if args.verbose:
                        print(val)
                    
                    fig, ax = plt.subplots(1, 1, figsize=(15,10))
                    try:
                        sns.violinplot(x=k, y=val, inner=None, data=tmp, ax=ax,
                            color='.9')
                        sns.stripplot(x=k, y=val, hue="seed", data=tmp, ax=ax,
                            linewidth=1)
                        ax.set_title(str(folder)+'\n'+val+" at time "+str(target_gen))
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
                        fig.savefig(folder+'/processing/end_values/'+val+'_'+k+'_time_'+str(target_gen)+'.png')
                    except:
                        pass
                    plt.close(fig)

    else:
        for k in params: # different values given at the beginning of the simulation
            print(k)
            for unique_value in df[k].unique():
                tmp = df[df[k]==unique_value]

                for other_param in params:
                    if k!=other_param:
                        for val in df.columns:
                            fig, ax = plt.subplots(1, 1, figsize=(15,10))
                            try:
                                sns.violinplot(x=other_param, y=val, inner=None, data=tmp, ax=ax,
                                    color='.2')
                                sns.stripplot(x=other_param, y=val, hue="seed", data=tmp, ax=ax,
                                    linewidth=1)
                                
                                ax.set_title(str(folder)+'\n'+val+" at time "+str(target_gen)+" "+str(k)+" "+str(unique_value))
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
                                fig.savefig(folder+'/processing/final_fusion/'+val+'_'+k+"_"+str(unique_value)+'_time_'+str(target_gen)+'.png')
                            except:
                                pass
                            plt.close(fig)


                    