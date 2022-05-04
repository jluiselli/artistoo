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
import itertools
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


# Read arguments from command line
args = parser.parse_args()
if args.verbose:
    print(args)

folder = args.folder
params = args.params
if 'seed' in params:
    params.remove('seed')
    if args.verbose:
        "Seeds are not taken into account as parameters here."

if args.competition:
    print("handling of competition runs for this plot not implemented yet")
    sys.exit()

try:
    df = pd.read_csv("end_with_comb.csv",sep=';')
    try:
        df = df.drop([i for i in df.columns if i[:7]=='Unnamed'], axis=1)
    except:
        pass
except:

    try:
        host = pd.read_csv(folder+'/hosts.csv', low_memory=False, sep=";")
        host = host.astype({'time':float})
        if args.generation!=-1:
            target_gen = args.generation
        else:
            target_gen = max(host['time'])
        if args.verbose:
            print("target generation is", target_gen)

        host = host[host['time']==target_gen]

        host = host.drop(['time of birth','good','bads','dna','type'], axis=1)
        host = host.drop([i for i in host.columns if i[:7]=='Unnamed'], axis=1)
        if (not "growth_rate" in params) and ("growth_rate" in host.columns):
            host = host.drop(["growth_rate"], axis=1)

        # mit = pd.read_csv(folder+'/mit.csv', low_memory=False, sep=';')
        # mit = mit.drop(['products', 'bad products', 'sum dna', 'new DNA ids','type', 'host'], axis=1)
        # mit = mit.drop([i for i in mit.columns if i[:7]=='Unnamed'], axis=1)
        # if (not "growth_rate" in params) and ("growth_rate" in mit.columns):
        #     mit = mit.drop(["growth_rate"], axis=1)
    except:
        print("***\nData must have been aggregated before use\n***")
        sys.exit()

# mit = mit[mit['time']==target_gen]

    if args.verbose:
        print(host)
        # print(host, mit)

    host = host.replace({'undefined':"NaN", "True":1,"False":0})
    host = host.astype(float)
    # mit = mit.replace({'undefined':"NaN", "True":1,"False":0})
    # mit = mit.astype(float)

    host = host.rename(columns = {'vol': 'vol_host'})
    # mit = mit.rename(columns = {'vol': 'vol_mit'})

    comb = []
    for k in params:
        tmp_list = []
        for val in host[k].unique():
            tmp_list+=[val]
        comb += [tmp_list]
    combinations = list(itertools.product(*comb))

    df = pd.DataFrame()
    for c in combinations:
        if args.verbose:
            print("unique comb",c)
        tmp = host
        i=0
        for k in params:
            tmp = tmp[tmp[k]==c[i]]
            i+=1
        if tmp.empty:
            if args.verbose:
                print("this combination is empty")
            continue
        tmp['comb']=str(c)
        df = pd.concat([df,tmp])

    df.to_csv('end_with_comb.csv',sep=";")

if not os.path.isdir(folder+'/processing/'):
    print('The directory is not present. Creating a new one..')
    os.mkdir(folder+'/processing/')

if args.clean:
    shutil.rmtree(folder+'/processing/end_allcomb/', ignore_errors=True)

if not os.path.isdir(folder+'/processing/end_allcomb/'):
    print('The directory is not present or has been removed. Creating a new one..')
    os.mkdir(folder+'/processing/end_allcomb/')

evolvables = [i for i in df.columns if i[:10]=='evolvables']

non_plottable = [i for i in params]
non_plottable += ['time', 'id', 'V', 'seed', 'time of birth',
    'fission events', 'fusion events', 'repliosomes', 'parent', 'genes', 'comb']

comb = []
for k in params:
    tmp_list = []
    for val in df[k].unique():
        tmp_list+=[val]
    comb += [tmp_list]
combinations = list(itertools.product(*comb))

# for ev in evolvables:
#     host = host.rename(columns = {ev : ev[11:]})
if len(combinations)>40:
    if args.verbose:
        print("big length, splitting data")
    tmp_df1, tmp_df2 = pd.DataFrame(), pd.DataFrame()
    # try:
    i=0
    mid = len(combinations)/2
    for c in combinations:
        if args.verbose:
            print("comb ",c)
        if len(df[df["comb"]==str(c)]["seed"].unique())==1:
            continue
        if i<mid:
            tmp_df1 = pd.concat([tmp_df1, df[df["comb"]==str(c)]])
        else:
            tmp_df2 = pd.concat([tmp_df2, df[df["comb"]==str(c)]])
        i += 1
    if args.verbose:
        print(tmp_df1, tmp_df2)

target_gen = max(df['time'])

maximums, minimums = {}, {}
for col in df.columns:
    if col not in non_plottable:
        maximums[col] = max(df[col])
        minimums[col] = min(df[col])

for val in df.columns:
# for val in ["evolvables_fusion_rate"]:
    if args.verbose:
        print(val)
    if val not in non_plottable:
        if args.verbose:
            print(val)

        if len(combinations)>40:
            fig, ax = plt.subplots(2, 1, figsize=(70,30))
            sns.violinplot(x="comb", y=val, inner=None, data=tmp_df1, ax=ax[0],
                color='.9')
            sns.stripplot(x="comb", y=val, hue="seed", data=tmp_df1, ax=ax[0])
            sns.violinplot(x="comb", y=val, inner=None, data=tmp_df2, ax=ax[1],
                color='.9')
            sns.stripplot(x="comb", y=val, hue="seed", data=tmp_df2, ax=ax[1])
            fig.suptitle(str(folder)+'\n'+val+" at time "+str(target_gen))
            # ax.set_xlabel("combination")
            ax[0].set_ylim(minimums[val], maximums[val])
            ax[1].set_ylim(minimums[val], maximums[val])

            ax[0].get_legend().remove()
            ax[1].get_legend().remove()
            for tick in ax[0].get_xticklabels():
                tick.set_rotation(45)
            for tick in ax[1].get_xticklabels():
                tick.set_rotation(45)
            fig.tight_layout()
            fig.savefig(folder+'/processing/end_allcomb/'+val+'_time_'+str(target_gen)+'.png')
            # except:
            #     pass

        else:
            fig, ax = plt.subplots(1, 1, figsize=(70,10))
            try:
                sns.violinplot(x="comb", y=val, inner=None, data=df, ax=ax,
                    color='.9')
                sns.stripplot(x="comb", y=val, hue="seed", data=df, ax=ax,
                    )
                ax.set_title(str(folder)+'\n'+val+" at time "+str(target_gen))
                ax.set_xlabel("combination")
                ax.set_ylim(minimums[val], maximums[val])

                fig.tight_layout()
                fig.savefig(folder+'/processing/end_allcomb/'+val+'_time_'+str(target_gen)+'.png')
            except:
                pass
        plt.close(fig)
