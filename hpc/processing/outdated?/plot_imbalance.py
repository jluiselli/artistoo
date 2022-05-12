import auxiliary.processthread as process
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt 
import seaborn as sns
import numpy as np
import json
import keywords
import argparse

options = keywords.getarguments()
sns.set(style="whitegrid", rc={'figure.figsize':(10,3)})

def select(timestep, time):
    i=0
    timestep = json.loads(timestep)
    out = []
    min_unmut = 1
    for hostId, host in timestep.items():
        host_sigma = 0
        host_var = 0

        for mitoId, mito in host['subcells'].items():
            rep_prod = mito['products'][10:]
            host_sigma += np.std(rep_prod)
            host_var += np.var(rep_prod)

        if host['n mito'] != 0:
            host_sigma /= host['n mito']
            host_var /= host['n mito']

        dctout = {"time":time, "var":host_var, "sigma":host_sigma}
        out.append(dctout)        
    return out

dfs = process.get(force=options.f, picklefname=keywords.nfile("imbalance.pickle"),runs=keywords.getruns(),folder=keywords.getfoldername(), 
 selector=select,  sortbykeywordix=keywords.getkeywordix(), sortbylineix=keywords.getlineix(),verbose=options.v)



end_df = pd.DataFrame([], columns=["var","sigma","fusion_rate"])
for path in dfs:
    expdir, expname = path.split('/')
    df = pd.DataFrame(dfs[path]['data'])
    if df['time'].iloc[-1] < 15000:
        if options.v:
            print(path, "not making plot due to early end")
        continue
    if options.v:
        print(path, " making plot")
        print(df.columns)

    fig, ax = plt.subplots(2,1, figsize=(10,8))
    
    g = sns.lineplot(data=df, x='time', y='var', palette="colorblind", ax=ax[0], label='mean variance') 
    g = sns.lineplot(data=df, x='time', y='sigma', palette="colorblind", ax=ax[1], label='mean std') 
    
    plt.legend(loc="upper left")
    title = "replication protein imbalance across time\n"
    title += (expname)
    g.set_title(title, y=0.9)
    fig.tight_layout()
    fig.subplots_adjust(top=0.8)

    plt.savefig(keywords.nfile("imbalance/"+ expname +".png"), dpi=600)
    plt.close()
    k = expname.split('-')
    i = iter(k)
    params = dict(zip(i,i))

    tmp = pd.DataFrame([], columns=["var","sigma","fusion_rate"])
    tmp['var'] = df['var'][-1000:]
    tmp['sigma'] = df['sigma'][-1000:]
    tmp['fusion_rate'] = params['fusion_rate_param']

    end_df = pd.concat([end_df, tmp])


print(end_df.columns)
print(len(end_df.columns))
#ax[0].boxplot(end_df['var'])
fig, ax = plt.subplots(2,1, figsize=(10,8))
end_df.boxplot(column = 'var', by='fusion_rate', ax = ax[0])
end_df.boxplot(column = 'sigma', by='fusion_rate', ax = ax[1])
#end_df.boxplot("sigma",  by="fusion_rate")

plt.savefig(keywords.nfile("imbalance/mean_final.png"), dpi=600)
plt.close()
   
