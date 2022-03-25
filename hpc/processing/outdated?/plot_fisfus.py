
import auxiliary.process as process
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt 
import seaborn as sns
import numpy as np
import json
import keywords

# sns.set(style="whitegrid", rc={'figure.figsize':(20,10)})
perrun = False
# colorby = 'path'
colorby = 'rep'

def select(timestep, time):
    timestep = json.loads(timestep)
    out = []
    min_unmut = 1
    for hostId, host in timestep.items():
        host_ndna = 0
        host_unmut = 0
        for mitoId, mito in host['subcells'].items():
            host_ndna += mito['n DNA']
            if mito['n DNA'] > 0:
                host_unmut += mito['unmut'] *mito['n DNA']
            # heteroplasmy.append([time, int(mitoId), mito["n DNA"], mito["unmut"], mito['translate']])
            # host_ndna += mito["n DNA"]
            # if mito["unmut"]  is not None:
                # min_unmut = min(min_unmut, float(mito["unmut"]))
        # if len(host['subcells']) > 0:
        #     host_unmut /= len(host['subcells']
        # print(host.keys())s
        out.append({"host":hostId, "time":time, "n DNA":host_ndna, "unmut":host_unmut, "fission rate":host['fission_rate'],"fusion rate":host['fusion_rate'], "rep":host['rep']})
    return out

def draw_heatmap(*args, **kwargs):
    data = kwargs.pop('data')
    d = data.pivot(index=args[1], columns=args[0], values=args[2])
    sns.heatmap(d, **kwargs)

# picklefname='./ndna_at_death.pickle'
# dfs = process.get(force=False, folder='../current', reverse=False, selector=select, start=0,  verbose=True,   sortbykeywordix=[("fission_rate", -1), ("fusion rate", -1), ("deprecation_rate", -1), ("division_volume", -1)])
dfs = process.get(force=False, picklefname="fisfus.pickle",folder=keywords.getfoldername(),  selector=select,  verbose=True,   sortbykeywordix=keywords.getkeywordix())
# dfs = process.get(force=False, folder='./fisfus1', reverse=True,stop=1, selector=selectOnlyTime,  verbose=True,   sortbykeywordix=[("fission_rate", -1), ("fusion rate", -1), ("deprecation_rate", -1)])
# print (dfs.keys())
processed = {}
for path in dfs: 
    pre_df = []
    # params = {}
    # entry = {}
    
    for dct in dfs[path]['data']:
        # print(dct)
        # dct.update(params)
        pre_df.append(dct)
        # print(dct)s
    processed[path] = pd.DataFrame(pre_df)
    processed[path] = processed[path].groupby(["host"]).mean().reset_index()
    for key, val in dfs[path].items():
        if key != 'data':
            processed[path][key]=float(val)
            # print(str(val), key)
            # print(processed[path][key])

if perrun:
    for path in processed:
        print(path, " making plot")
        df = processed[path]
        df = df.groupby(["host"]).mean().reset_index()
        # print(df)
        # keywords.rename(df)
        fig, ax = plt.subplots()
        df['fission rate'] = df["fission rate"] *10000
        df['fusion rate'] = df["fusion rate"] *10000
        g = sns.scatterplot(data=df, x='fission rate', y='fusion rate',hue="time", legend=None, ax=ax, palette='viridis')
        # g = sns.lineplot(data=df, x='fission rate', y='fusi', units="host", estimator=None, hue="host", lw=1, palette="colorblind", legend=None, ax=ax) 
        title = "fission fusion x10k, avg time  on color \n"
        # for kw, ix in keywords.getkeywordix():
        #     # print(title, kw, df[kw][0])
        #     title += (kw + " = " + str(df[kw][0]) + '\n')
        g.set_title(title)
        fig.tight_layout()
        # ax.title.set_y(0.5)
        fig.subplots_adjust(top=0.9)
        norm = plt.Normalize(df['time'].min(), df['time'].max())
        sm = plt.cm.ScalarMappable(cmap="viridis", norm=norm)
        sm.set_array([])

        # Remove the legend and add a colorbar
        # ax.get_legend().remove()
        ax.figure.colorbar(sm)

        plt.savefig("current_processing/perrun/fisfus/fisfus of "+ path[-4:] +".png", dpi=300)
        plt.close()

alldf = []
for path in processed:
    df = processed[path]
    df['fission rate'] = df["fission rate"] *10000
    df['fusion rate'] = df["fusion rate"] *10000
    # print(df)
    df['path'] = path[-4:]
    alldf.append(df)
alldf= pd.concat(alldf)


keywords.rename(alldf)
print(alldf)
print(pd.unique(alldf['p']))
fig, ax = plt.subplots()
if colorby == 'path':
    # sns.scatterplot(data=alldf, x='fission rate', y='fusion rate',hue="path", palette="colorblind", edgecolor=None, ax=ax, s=4)
    sns.relplot(data=alldf, x='fission rate', y='fusion rate',row='p',hue="path", palette="colorblind", edgecolor=None, s=4)
    plt.savefig("current_processing/fissionfusion.png")
elif colorby == 'time':
    g = sns.relplot(data=alldf, x='fission rate', y='fusion rate',row='p',hue="time", palette="viridis", edgecolor=None, s=4)
    # norm = plt.Normalize(df['time'].min(), df['time'].max())
    # sm = plt.cm.ScalarMappable(cmap="viridis", norm=norm)
    # sm.set_array([])
    # ax.figure.colorbar(sm)
    plt.savefig("current_processing/fissionfusiontime.png")
elif colorby == 'rep':
    g = sns.scatterplot(data=alldf, x='fission rate', y='fusion rate',row='p',hue="rep", palette="viridis", edgecolor=None, s=4)
    norm = plt.Normalize(df['rep'].min(), df['rep'].max())
    sm = plt.cm.ScalarMappable(cmap="viridis", norm=norm)
    sm.set_array([])
    ax.figure.colorbar(sm)
    plt.savefig("current_processing/fissionfusiontime.png")

# fg = keywords.getfacetgrid(df)
# fg.map_dataframe(draw_heatmap, 'fission_rate', 'fusion rate', 'unmut', cbar=False, annot=True, square = True, label='small', fmt='.1f')
# for ax in fg.axes.flat:
#     ax.set_aspect('equal','box')
# fg.fig.tight_layout()

# fg.fig.suptitle("mean percentage unmutated DNA per vesicle at last 400 MCS")
# plt.savefig("current_processing/unmut vesicle at end.png")


