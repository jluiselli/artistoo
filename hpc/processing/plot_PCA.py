import pandas as pd
import matplotlib.pyplot as plt 
import sys, os, shutil
import matplotlib.patches as mpatches
import numpy as np
import itertools
import plotly.express as px
from sklearn.decomposition import PCA
import argparse
 
# Initialize parser
parser = argparse.ArgumentParser()

# Adding optional argument
parser.add_argument("folder", help="folder in which to run the code") # positional arg
parser.add_argument("-c", "--competition", help = "Specify that dual values are expected", action="store_true")
parser.add_argument("-p", dest='params', help="parameters in folder names to use", nargs='+')
parser.add_argument("-v", "--verbose", help="print more information", action="store_true")
parser.add_argument("--clean", help="cleans the folder before replotting", action="store_true")
parser.add_argument("-g", "--generation", type=int, help="generation for which we want the PCA. Default is last generation", default=-1)
 
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
    hosts=pd.read_csv(folder+'/hosts.csv', low_memory=False, sep=";", dtype=str)
except:
    print("Data must have been aggregated with aggregate.py before")
    sys.exit()

hosts = hosts.astype({'time':float})

if args.generation != -1:
    target_gen = float(args.generation)
     # retain target generation
else:
    target_gen = float(max(hosts['time'])) # retaining only the final data
hosts = hosts[hosts['time']==target_gen]
hosts = hosts.drop(['time','id', 'parent','total_vol'], axis=1) #No NaN possibe and total_vol not always defined

hosts = hosts.drop([i for i in hosts.columns if i[:7]=='Unnamed'], axis=1)
hosts = hosts.drop(['time of birth','good','bads','dna','type', 'fission events', 'fusion events'], axis=1)
hosts = hosts.replace({"True":1,"False":0})

try:
    hosts = hosts.astype(float)
except:
    hosts = hosts.drop(["total_vol"],axis=1)
    hosts = hosts.astype(float)

if hosts.empty:
    print("empty df ! Are there data at this generation ?")
    sys.exit()

if not os.path.isdir(folder+'/processing/'):
    print('The directory processing is not present. Creating a new one..')
    os.mkdir(folder+'/processing/')

if args.clean:
    shutil.rmtree(folder+'/processing/pca/', ignore_errors=True)

if not os.path.isdir(folder+'/processing/pca/'):
    print('The directory pca is not present (or was deleted). Creating a new one..')
    os.mkdir(folder+'/processing/pca/')

usual_colors = ['tab:blue', 'tab:orange', 'tab:green','tab:purple','tab:red',
'tab:pink','tab:brown'] 


X = hosts.drop([p for p in params], axis=1)
# parameters fixed by user prior the run should not be taken into account for the PCA
Y = X.drop([col for col in X.columns if col[:4]=="evol"], axis=1) #drop explicitely evolving parameters
pca = PCA(n_components=2)
components = pca.fit_transform(X)
components2 = pca.fit_transform(Y)

## actual stuff
for p in params:
    if p != 'seed':
        hosts[p]=hosts[p].astype(str) #no continuous colors wanted
        fig = px.scatter(components, x=0, y=1, color=hosts[p], title='PCA_'+p)                        
        fig.write_image(folder+'/processing/pca/PCA_'+p+'_gen_'+str(target_gen)+'.png')
        plt.close()

        fig = px.scatter(components2, x=0, y=1, color=hosts[p], title='PCA_noeevparam_'+p)                        
        fig.write_image(folder+'/processing/pca/PCA_noeevparam_'+p+'_gen_'+str(target_gen)+'.png')
        plt.close()
        if args.verbose:
            print("general plot for "+p+" done, going to unique values")

        for unique_value in hosts[p].unique():
            tmp = hosts[hosts[p]==unique_value]
            tmp = tmp.astype({'seed': str})
            X1 = tmp.drop([p for p in params], axis=1)
            Y1 = X1.drop([col for col in X.columns if col[:4]=="evol"], axis=1)
            components3 = pca.fit_transform(X1)

            hosts = hosts.astype({p: str})
            fig = px.scatter(components3, x=0, y=1, color=tmp['seed'], title='PCA_'+p+str(unique_value))                        
            fig.write_image(folder+'/processing/pca/PCA_'+p+str(unique_value)+'_gen_'+str(target_gen)+'.png')
            plt.close()

            components4 = pca.fit_transform(Y1)
            fig = px.scatter(components4, x=0, y=1, color=tmp['seed'], title='PCA_noeevparam_'+p+str(unique_value))                        
            fig.write_image(folder+'/processing/pca/PCA_noeevparam_'+p+str(unique_value)+'_gen_'+str(target_gen)+'.png')
            plt.close()

evolvables = [col for col in hosts.columns if col[:4]=="evol"]
for ev in evolvables:
    X = hosts.drop([p for p in params], axis=1)
    # parameters fixed by user prior the run should not be taken into account for the PCA
    Y = X.drop([col for col in X.columns if col[:4]=="evol"], axis=1) #drop explicitely evolving parameters

    components = pca.fit_transform(Y)
    fig = px.scatter(components, x=0, y=1, color=hosts[ev], title='PCA_noeevparam_'+ev)                        
    fig.write_image(folder+'/processing/pca/PCA_noeevparam_'+ev+'_gen_'+str(target_gen)+'.png')
    plt.close()