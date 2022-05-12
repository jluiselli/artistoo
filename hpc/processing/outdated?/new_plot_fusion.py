import pandas as pd
import matplotlib.pyplot as plt 
import sys
import matplotlib.patches as mpatches
import numpy as np

folder = sys.argv[1]
params = sys.argv[2:]

hosts=pd.read_csv(folder+'/hosts.csv')



usual_colors = ['tab:blue', 'tab:orange', 'tab:green','tab:purple','tab:red',
'tab:pink','tab:brown'] 

for k in params:
    d = {}
    i=0
    for value in hosts[k].unique():
        d[value] = usual_colors[i]
        i+=1
    colors = [d[i] for i in hosts[k]]
    
    hosts.plot.scatter(x='time', y='fusion_rate', c=colors, label=k,
        alpha=0.5, s=1
        )

    plt.ylim(min(hosts['fusion_rate'])-0.0001,max(hosts['fusion_rate'])+0.0001)
    plt.legend(handles = [mpatches.Patch(color=d[k], label=k) for k in d.keys()], title = k)
    plt.title("Fusion rate over time for different "+k)

    plt.tight_layout()
    plt.savefig(folder+'/fusion_time_'+k+'.png')
    plt.close()