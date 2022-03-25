# Usage : python3 plot_death_over_time.py Folder_with_all_runs/ -v [verbose] -c [if runs shorter than 50000 timesteps]
# Gives plots of mean death rate across time, at different bin sizes. Top = mito, bottom = hosts
# « Corrected » :death per host summed and divided by 7000 ? Why ?
import auxiliary.processthread as process
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt 
import seaborn as sns
import numpy as np
import json
import keywords

options = keywords.getarguments()
plt.rcParams['svg.fonttype'] = 'none'
sns.set(style="whitegrid", rc={'figure.figsize':(10,5)})

def selectDeath(timestep, time):
    dctin = json.loads(timestep)
    dctout = {}
    dctout['time'] = dctin['time']
    dctout['type'] = dctin['type']
    dctout['V'] = dctin['V']
    if 'time of birth' in dctin:
        dctout['time of birth'] = dctin['time of birth']
    else:
        dctout['time of birth'] = 0
    
    return  [dctout]

def selectPopSize(timestep, time):
    dctin = json.loads(timestep)
    dctout = {}
    dctout['hosts'] = len(dctin)
    dctout['mitos'] = 0
    for host in dctin:
        dctout['time'] = dctin[host]['time'] # will set too many times but okay
        dctout['mitos'] += len(dctin[host]['subcells'])
    return [dctout]

popsizedfs = process.get(picklefname=keywords.nfile('popsizes.pickle'),fname='Mitochondrialog.txt',runs=keywords.getruns(),force=options.f, folder=keywords.getfoldername(), selector=selectPopSize,  verbose=options.v,   sortbykeywordix=keywords.getkeywordix(), load=options.l)
dfs = process.get(picklefname=keywords.nfile('mitodeath.pickle'),fname='deaths.txt',runs=keywords.getruns(),force=options.f, folder=keywords.getfoldername(), selector=selectDeath,  verbose=options.v,   sortbykeywordix=keywords.getkeywordix(),load=options.l)


alldf = []
categorical = []
for path in dfs: #All individual run one by one
    df = pd.DataFrame.from_dict(dfs[path]['data'])
    dfpopsize = pd.DataFrame.from_dict(popsizedfs[path]['data'])

    if df['time'].iloc[-1] < 50000:
        if options.v:
            print("short run, only going on if flag -c")
        if not options.c:
            continue

    df['time'] = df['time'].round(decimals=-1)
    df['time'] += 1

    dfpopsize = dfpopsize.set_index('time')
    dfpopsize = dfpopsize.reindex(df['time'], method="ffill")
    dfpopsize = dfpopsize.reset_index()
  
    df['perhost'] = 1/dfpopsize['hosts']
    df['permito'] = 1/dfpopsize['mitos']

    title = "Host death through time\n"
    for key, val in dfs[path].items():
        if key != 'data':
            df[key] = val
            title += (key + " = " + str(val) + '\n')
    if options.v:
        print(df)
    fig, ax = plt.subplots(nrows=2)
    alldf.append(df)
    
    g1 = sns.histplot(data=df[(df['type'] == 'mito')], x='time',stat='frequency', ax=ax[0], weights='permito', bins=20)
    g2 = sns.histplot(data=df[(df['type'] == 'host')], x='time', stat='frequency' ,ax=ax[1], weights='perhost', bins=10)
    df = df[(df['time'] >=3000)]
    print(dfs[path])

    print("hosts ???\n",df[(df['type']== 'host')])
    categorical.append({"type": "host", "death":df[(df['type']== 'host')].perhost, "seed":dfs[path]['seed']}) #Could add here the parameters of the run
    categorical.append({"type": "mito", "death":df[(df['type']== 'mito')].permito, "seed":dfs[path]['seed']})

    fig.suptitle(title)
    fig.tight_layout()
    fig.subplots_adjust(top=0.8)
    plt.savefig(keywords.nfile("deaths/corrected2" + path[-4:] +".png"))
    plt.savefig(keywords.nfile("deaths//svgs/corrected2"+ path[-4:] +".svg"))
    plt.close()



fig, ax = plt.subplots(nrows=2)


lstdf = alldf
alldf = pd.concat(alldf, ignore_index=True)


# ASSUMES ALL RUNS HAVE RUN AS LONG AS EACH OTHER!!!
# best practice would be to div by time point how many unique runs have been there

g1 = sns.histplot(data=alldf[(alldf['type'] == 'mito')], x='time',stat='frequency', ax=ax[0], weights='permito', bins=30)
g2 = sns.histplot(data=alldf[(alldf['type'] == 'host')], x='time', stat='frequency' ,ax=ax[1], weights='perhost', bins=30)
ax[0].set_title("Mit death rate")
ax[1].set_title("Host death rate")
ax[0].set_xticks([])
ax[0].set_xlabel('')
fig.suptitle("Deaths through time")
plt.savefig(keywords.nfile("allcorrectedmorebins2.png"))
plt.savefig(keywords.nfile("allcorrectedmorebins2.svg"))

plt.close()
fig, ax = plt.subplots(nrows=2)

g1 = sns.histplot(data=alldf[(alldf['type'] == 'mito')], x='time',stat='frequency', ax=ax[0], weights='permito', bins=1)
g2 = sns.histplot(data=alldf[(alldf['type'] == 'host')], x='time', stat='frequency' ,ax=ax[1], weights='perhost', bins=1)
fig.suptitle("Mean death rate")
ax[0].set_title("Mit death rate")
ax[0].set_xticks([])
ax[0].set_xlabel('')
ax[1].set_title("Host death rate")
plt.savefig(keywords.nfile("allcorrected2.png"))
plt.savefig(keywords.nfile("allcorrected2.svg"))
plt.close()

fig, ax = plt.subplots(nrows=2)
