import pandas as pd
import matplotlib.pyplot as plt 
import sys, os
import matplotlib.patches as mpatches
import matplotlib.colors as clrs
import numpy as np
import ast
import random
import colorsys


folder = sys.argv[1]
params = sys.argv[2:]

try:
    hosts=pd.read_csv(folder+'/hosts.csv')
    hosts = hosts.sample(frac=.15)
except:
    print("Data must have been aggregated with aggregate.py before")


if not os.path.isdir(folder+'/processing/'):
    print('The directory is not present. Creating a new one..')
    os.mkdir(folder+'/processing/')


usual_colors = ['tab:blue', 'tab:orange', 'tab:green','tab:purple','tab:red',
'tab:pink','tab:brown'] 
try:
    evolvables = ast.literal_eval(hosts.iloc[1]['evolvables']).keys()
    hosts['path']=""

    hosts['growth_rate']=hosts['growth_rate'].replace({15:1.5, 5:0.5})

    for k in params: # different values given at the beginning of the simulation
        d = {}
        i=0
        for value in hosts[k].unique():
            d[value] = usual_colors[i]
            i+=1
        colors = [d[i] for i in hosts[k]]
        hosts['path']+=[k+" "+str(val)+" | " for val in hosts[k]]
        print(d)
        
        for ev in evolvables:
            # fig, ax = plt.subplots(1, 1, figsize=(15,10))
            # hosts.plot.scatter(x='time', y=ev, c=colors, label=k,
            #     alpha=0.1, s=2, ax=ax
            #     )
        
            # ax.set_ylim(min(hosts[ev]), max(hosts[ev]))
            # ax.set_ylabel(ev)
            # ax.set_xlabel('time')
            # ax.legend(handles = [mpatches.Patch(color=d[k], label=k) for k in d.keys()], title = k)
            # ax.set_title(ev+" over time for different "+k)

            # fig.tight_layout()
            # fig.savefig(folder+'/processing/'+ev+'_time_'+k+'.png',dpi=600)
            # plt.close(fig)
            # print(ev,k," done")

            for unique_value in hosts[k].unique():
                tmp = hosts[hosts[k]==unique_value]
                for other_param in params:
                    if k!=other_param:
                        d = {}
                        i=0
                        for value in hosts[other_param].unique():
                            d[value] = usual_colors[i]
                            i+=1
                        colors = [d[i] for i in tmp[other_param]]
                        fig, ax = plt.subplots(1, 1, figsize=(15,10))
                        print(d)
                        tmp.plot.scatter(x='time', y=ev, c=colors,
                            alpha=0.1, s=2, ax=ax
                            )

                        ax.set_ylim(min(hosts[ev]), max(hosts[ev]))
                        ax.set_ylabel(ev)
                        ax.set_xlabel('time')
                        ax.legend(handles = [mpatches.Patch(color=d[k], label=k) for k in d.keys()], title = other_param)
                        ax.set_title(ev+" over time for "+k+" "+str(unique_value))

                        fig.tight_layout()
                        fig.savefig(folder+'/processing/'+ev+'_time_'+other_param+"_"+str(unique_value)+'.png',dpi=600)
                        plt.close(fig)


    # for ev in evolvables:
    #     d = {}
    #     i=0
    #     N = len(hosts["path"].unique())
    #     HSV_tuples = [(x*1.0/N, 0.9, 0.9) for x in range(N)]
    #     RGB_tuples = list(map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples))

    #     for value in hosts["path"].unique():
    #         d[value] = RGB_tuples[i]
    #         i+=1
    #     colors = [d[i] for i in hosts["path"]]

    #     fig, ax = plt.subplots(1, 1, figsize=(15,10))
    #     hosts.plot.scatter(x='time', y=ev, c=colors,
    #         alpha=0.1, s=2, ax=ax
    #         )
        
    #     ax.set_ylim(min(hosts[ev]), max(hosts[ev]))
    #     ax.set_ylabel(ev)
    #     ax.set_xlabel('time')
    #     ax.legend(handles = [mpatches.Patch(color=d[k], label=k) for k in d.keys()], fontsize = 8, loc='lower left')
    #     ax.set_title(ev+" over time")

    #     fig.tight_layout()
    #     fig.savefig(folder+'/processing/'+ev+'_time.png',dpi=600)
    #     plt.close(fig)
    #     print(ev,"total done")

    # USAGE:
    # ! data must have been aggregate before
    # python3 plot_evolvables_time.py path/to/folder/ first_var_elt second_var_elt third_var_elt ...
except:
    pass