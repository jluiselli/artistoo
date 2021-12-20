
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

def selectVol(timestep, time):
    if (time %1000 != 0):
        return []
    timestep = json.loads(timestep)
    out = []
    for hostId, host in timestep.items():
        hostout = {"type":'host', "time":host['time'],"id": hostId}
        hostdna = 0
        hostunmut = 0
        for mitoId, mito in host['subcells'].items():
            mitoout = {"type":'mito', "time":host['time'], 'n DNA':mito['n DNA'], "id":mitoId}
            hostdna += mito['n DNA']
            if mito['unmut'] != None:
                hostunmut += mito['unmut'] * mito['n DNA']
                mitoout['unmut'] = mito['unmut'] * mito['n DNA']
            out.append(mitoout)
        hostout['n DNA'] = hostdna
        hostout['unmut'] = hostunmut
        out.append(hostout)
    return  out

dfs = process.get(picklefname=keywords.nfile('ndnaCond4.pickle'),runs=keywords.getruns(),force=options.f, folder=keywords.getfoldername(), selector=selectVol,  verbose=options.v, sortbykeywordix=keywords.getkeywordix(),load=options.l)


alldf = []
for path in dfs:
    
    df = pd.DataFrame.from_dict(dfs[path]['data'])
    # print(df)
    if df['time'].iloc[-1] < 9000:
        if options.v:
            print("short run, only making with flag -c", df['time'].iloc[-1] , dfs[path]['setting'])
        if not options.c:
            continue
    for key, val in dfs[path].items():
        if key != 'data':
            #title += (key + " = " + str(val) + '\n')
            df[key] = val
    alldf.append(df)

fig, ax = plt.subplots(nrows=1)
alldf = pd.concat(alldf, ignore_index=True)
if options.v:   
    print(alldf)


alldf['frac'] = alldf['unmut']/alldf['n DNA']
alldf['mutated'] = alldf['n DNA'] - alldf['unmut']

# -- FINAL PLOTS N mtDNA --
g= sns.histplot(data=alldf[(alldf['type'] == 'host')], x='n DNA', hue='setting',stat='percent', ax=ax,element='step', common_norm=False, bins=int(np.max(alldf[(alldf['type'] == 'host')]['n DNA'])))
ax.set_xlim(0,150)
# g= sns.histplot(data=alldf[(alldf['type'] == 'mito')], x='n DNA', hue='setting',stat='percent', ax=ax,element='step', common_norm=False, bins=int(np.max(alldf[(alldf['type'] == 'mito')]['n DNA'])))
# ax.set_xlim(0,10)


# -- FINAL PLOTS FRACTION UNMUTATED -- 
# g= sns.histplot(data=alldf[(alldf['type'] == 'host')], x='frac', hue='setting',stat='percent',multiple='layer', ax=ax, common_norm=False, kde=True)
# g= sns.histplot(data=alldf[(alldf['type'] == 'mito')], x='frac', hue='setting',stat='percent',multiple='layer', ax=ax, common_norm=False, bins=5, element="step", kde=True, kde_kws={"bw_adjust":2})

plt.savefig(keywords.nfile("final_ndnahosts.png"))
plt.savefig(keywords.nfile("final_ndnahosts.svg"))
plt.close()





# --  Messy try out stuff -- 


# g= sns.kdeplot(data=alldf[(alldf['type'] == 'mito')], x='n DNA',clip=(0,1200), hue='setting', ax=ax, common_norm=False, lw=2, bw_adjust=4)
# alldf['cat DNA'] = alldf['n DNA']
# condmid = (alldf['n DNA'] >= 3) & (alldf['n DNA'] <= 5)
# condhigh = alldf['n DNA'] > 5
# alldf['cat DNA'] = alldf['cat DNA'].where(condmid, "3 to 5")
# alldf['cat DNA'] = alldf['cat DNA'].where(condhigh, "> 6")
# alldf = alldf[(alldf['n DNA']) >0]
# alldf = alldf[(alldf['n DNA']) <20]
# print(np.max(alldf[(alldf['type'] == 'mito')]['n DNA']))
# g = sns.histplot(data=alldf[(alldf['type'] == 'mito')], x='n DNA',hue='setting',element='step', stat='frequency', palette='flare',bins=[i for i in range(1, np.max(alldf[(alldf['type'] == 'mito')]['n DNA']), 1)])
# g = sns.countplot(data=alldf[(alldf['type'] == 'mito')], x='n DNA',hue='setting', palette='flare')
# ax.set_xlim(-0.5,14.5)

# g = sns.histplot(data=alldf[(alldf['type'] == 'host')], x='n DNA',hue='setting',element='step', stat='density', palette='flare',bins=[i for i in range(1, np.max(alldf[(alldf['type'] == 'host')]['n DNA']), 1)])
# ax.set_xlim(-0.5,14.5)

# ax.set_xscale('log')


# ax.set_xlim(0,10)
# # # g= sns.kdeplot(data=alldf[(alldf['type'] == 'mito')], x='n DNA',clip=(0,1200), hue='setting', ax=ax, common_norm=False, lw=2, bw_adjust=4)
# g= sns.kdeplot(data=alldf[(alldf['type'] == 'host')], x='frac', hue='setting', ax=ax, clip=(0,1), common_norm=False, lw=2, bw_adjust=4)
# ax.set_yscale('log')
# g = sns.displot

# g= sns.displot(data=alldf[(alldf['type'] == 'mito')], x='frac', stat='density',col='setting', kind='hist', ax=ax, kde=True, kde_kws={"bw_adjust":4})
# print(len(alldf[(alldf['type'] == 'mito') & (alldf['n DNA']==0)]))
# change_width(ax, .34)
# g1 = sns.countplot(data=alldf[(alldf['type'] == 'mito')], x='setting',  hue='cat DNA', ax=ax[0])
# g2 = sns.violinplot(data=alldf[(alldf['type'] == 'host')], x='setting' , y = 'n DNA', hue='type',max=ax[1])