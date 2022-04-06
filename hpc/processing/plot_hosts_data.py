import pandas as pd
import matplotlib.pyplot as plt 
import sys, os, shutil
import matplotlib.patches as mpatches
import numpy as np
import itertools
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
parser.add_argument("-f", "--fraction", help="fraction of dataframe you want to plot (can be used to make plots quicker)", default=1)


# Read arguments from command line
args = parser.parse_args()
if args.verbose:
    print(args)

folder = args.folder
params = args.params

try:
    hosts=pd.read_csv(folder+'/hosts.csv', low_memory=False, sep=";", dtype=str)
    if args.verbose:
        print(hosts.columns)
    try:
        hosts = hosts.drop(['time of birth','good','bads','dna','type'], axis=1)
        hosts = hosts.drop([i for i in hosts.columns if i[:7]=='Unnamed'], axis=1)
    except:
        pass
    if args.competition:
        for ev in [i for i in hosts.columns if i[:10]=='evolvables']:
            hosts[ev]= [i.split(',') for i in hosts[ev]]
            new_name1 = ev+'_1'
            new_name2 = ev+'_2'
            hosts[new_name1] = [i[0] for i in hosts[ev]]
            hosts[new_name2] = [i[1] for i in hosts[ev]]
            hosts = hosts.drop([ev], axis=1)

    hosts = hosts.replace({'undefined':'NaN'})
    hosts = hosts.astype(float)
    hosts = hosts.sample(frac=args.fraction)
except:
    print("Data must have been aggregated with aggregate.py before plotting")


if not os.path.isdir(folder+'/processing/'):
    print('The directory is not present. Creating a new one..')
    os.mkdir(folder+'/processing/')

if args.clean:
    shutil.rmtree(folder+'/processing/hosts/')

if not os.path.isdir(folder+'/processing/hosts/'):
    print('The directory is not present or was deleted. Creating a new one..')
    os.mkdir(folder+'/processing/hosts/')


usual_colors = ['tab:blue', 'tab:orange', 'tab:green','tab:purple','tab:red',
'tab:pink','tab:brown']
if args.fraction < 0.5:
    alpha=0.5
else:
    alpha=0.1


try:
    hosts['growth_rate']=hosts['growth_rate'].replace({15:1.5, 5:0.5})
except:
    pass

if args.max_generation != -1:
    hosts = hosts[hosts['time']<args.max_generation]

interest_params = ['total_vol', 'vol', 'n mito','total_oxphos']
if args.competition:
    interest_params += [i for i in hosts.columns if (i[:10]=='evolvables' and i[-2:]=='_1')]
    interest_params += [i for i in hosts.columns if (i[:10]=='evolvables' and i[-2:]=='_2')]
else:
    interest_params += [i for i in hosts.columns if i[:10]=='evolvables']


if params[-1]=='seed':
    unique_plots = True
    params = params[:-1]
else:
    unique_plots = False

if unique_plots:
    if args.verbose:
        print("doing all unique plots")
    comb = []
    for k in params:
        tmp_list = []
        for val in hosts[k].unique():
            tmp_list+=[val]
        comb += [tmp_list]
    combinations = list(itertools.product(*comb))
    for c in combinations:
        if args.verbose:
            print("unique plot",c)
        tmp = hosts
        i=0
        for k in params:
            tmp = tmp[tmp[k]==c[i]]
            i+=1
        if tmp.empty:
            continue
        for ev in interest_params:
            if args.verbose:
                print(ev)

            tmp = tmp.astype({'seed':str})
            fig, ax = plt.subplots(1, 1, figsize=(15,10))
            sns.scatterplot(x='time', y=ev, data=tmp, ax=ax, hue="seed", s=2, alpha=alpha)            
            ax.set_ylim(min(hosts[ev]), max(hosts[ev]))
            ax.set_ylabel(ev)
            ax.set_xlabel('time')
            ax.legend()
            ax.set_title(ev+" over time "+str(c))
            fig.tight_layout()
            fig.savefig(folder+'/processing/hosts/'+ev+'_time_'+str(c)+'.png',dpi=600)
            plt.close(fig)

    if args.verbose:
        print("finished unique plots. On to merged seeds")
          

for k in params: # different values given at the beginning of the simulation
    if args.verbose:
        print(k)
    
    for ev in interest_params: # Which thing over time we want to plot
        fig, ax = plt.subplots(1, 1, figsize=(15,10))
        sns.scatterplot(x='time', y=ev, hue=k, alpha=alpha,s=2, ax=ax, data=hosts)

        try:
            ax.set_ylim(min(hosts[ev]), max(hosts[ev]))
        except:
            pass
        ax.set_ylabel(ev)
        ax.set_xlabel('time')
        ax.legend()
        ax.set_title(ev+" over time for different "+k)
        fig.tight_layout()
        fig.savefig(folder+'/processing/hosts/'+ev+'_time_'+k+'.png',dpi=600)
        plt.close(fig)

        fig, ax = plt.subplots(1, 1, figsize=(15,10))
        for unique_value in hosts[k].unique():
            tmp = hosts[hosts[k]==unique_value]
            Z = [np.mean(tmp[tmp['time']==t][ev]) for t in tmp['time'].unique()]
            lab = str(k)+' '+str(unique_value)
            ax.scatter(tmp['time'].unique(), Z, label=lab, alpha=.6)
        ax.set_ylabel(ev)
        ax.set_xlabel('time')
        ax.set_title("Mean "+ev+" over time for different "+k)
        ax.legend()
        fig.tight_layout()
        fig.savefig(folder+'/processing/hosts/'+ev+'_time_'+k+'_summarize.png',dpi=600)
        plt.close(fig)
        
        if args.verbose:
            print(ev,k," done. Going to cross plots")

        for unique_value in hosts[k].unique():
            tmp = hosts[hosts[k]==unique_value]
            if tmp.empty:
                continue
            for other_param in params:
                if k!=other_param:
                    fig, ax = plt.subplots(1, 1, figsize=(15,10))
                    sns.scatterplot(x='time', y=ev, hue=other_param, alpha=alpha,s=2, ax=ax, data=tmp)

                    ax.set_ylim(min(hosts[ev]), max(hosts[ev]))
                    ax.set_ylabel(ev)
                    ax.set_xlabel('time')
                    ax.legend()
                    ax.set_title(ev+" over time for "+k+" "+str(unique_value))
                    fig.tight_layout()
                    fig.savefig(folder+'/processing/hosts/'+ev+'_time_'+other_param+"_"+str(unique_value)+'.png',dpi=600)
                    plt.close(fig)
                
                    fig, ax = plt.subplots(1, 1, figsize=(15,10))
                    for value in hosts[other_param].unique():
                        tmp2 = tmp[tmp[other_param]==value]
                        if tmp2.empty:
                            continue
                        Z = [np.mean(tmp2[tmp2['time']==t][ev]) for t in tmp2['time'].unique()]
                        lab = str(other_param)+' '+str(value)
                        ax.scatter(tmp2['time'].unique(), Z, label=lab, alpha=.6)
                    ax.legend()
                    ax.set_ylim(0.9*min(Z),1.1*max(Z))
                    ax.set_ylabel(ev)
                    ax.set_xlabel('time')
                    ax.set_title("Mean "+ev+" over time for different "+other_param+"\n"+k+" is "+str(unique_value))
                    fig.tight_layout()
                    fig.savefig(folder+'/processing/hosts/'+ev+'_time_'+k+'-'+str(unique_value)+'_'+other_param+'_summarize.png',dpi=600)
                    plt.close(fig)
