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
    df=pd.read_csv(folder+'/total_df.csv', low_memory=False, sep=";")
except:
    print("Data must have been aggregated with aggregate.py and collapse to total_df.csv before")
    sys.exit()

df = df.astype({'time':float})

# n mito;total_oxphos;seed;vol_mit;n DNA;oxphos;ros;translate;replicate;replisomes;unmut

if args.generation != -1:
    target_gen = float(args.generation)
     # retain target generation
else:
    target_gen = float(max(df['time'])) # retaining only the final data
df = df[df['time']==target_gen]

df = df.drop(['time'], axis=1)
df = df.drop([i for i in df.columns if i[:7]=='Unnamed'], axis=1)
df = df.drop(['host_id','V_host','vol_host','parent','total_vol','fission events', 'fusion events','mit_id',
    'V_mit','oxphos_avg'], axis=1)

df = df.astype({'unmut':str})
df = df.replace({'nan':0,'NaN':0,'undefined':0,"True":1,"False":0}) #undefined is in unmut
# Makes sense to be 0 as there is no DNA = bad sign (!= 1 would be perfect DNA)


df = df.astype(float)
df = df.sort_values(by=params)

if df.empty:
    print("empty df ! Are there data at this generation ?")
    sys.exit()

if not os.path.isdir(folder+'/processing/'):
    print('The directory processing is not present. Creating a new one..')
    os.mkdir(folder+'/processing/')

if args.clean:
    shutil.rmtree(folder+'/processing/pca_mit/', ignore_errors=True)

if not os.path.isdir(folder+'/processing/pca_mit/'):
    print('The directory pca is not present (or was deleted). Creating a new one..')
    os.mkdir(folder+'/processing/pca_mit/')


X = df.drop([p for p in params], axis=1)
try:
    X = X.drop('seed',axis=1)
except:
    pass
# parameters fixed by user prior the run should not be taken into account for the PCA
Y = X.drop([col for col in X.columns if col[:4]=="evol"], axis=1) #drop explicitely evolving parameters
pca = PCA(n_components=2)
components = pca.fit_transform(X)
components2 = pca.fit_transform(Y)

## actual stuff
for p in params:
    if p != 'seed':
        df[p]=df[p].astype(str) #no continuous colors wanted
        df[p]=df[p].astype(float)
        fig = px.scatter(components, x=0, y=1, color=df[p], title='PCA_'+p, opacity=0.4)                        
        fig.write_image(folder+'/processing/pca_mit/PCA_'+p+'_gen_'+str(target_gen)+'.png')
        plt.close()

        fig = px.scatter(components2, x=0, y=1, color=df[p], title='PCA_noeevparam_'+p, opacity=0.4)                        
        fig.write_image(folder+'/processing/pca_mit/PCA_noeevparam_'+p+'_gen_'+str(target_gen)+'.png')
        plt.close()
        if args.verbose:
            print("general plot for "+p+" done, going to unique values")

        for unique_value in df[p].unique():
            tmp = df[df[p]==unique_value]
            tmp = tmp.astype({'seed': str})
            X1 = tmp.drop([p for p in params], axis=1)
            try:
                X1 = X1.drop("seed", axis=1)
            except:
                pass
            Y1 = X1.drop([col for col in X.columns if col[:4]=="evol"], axis=1)
            # components3 = pca.fit_transform(X1)

            # df = df.astype({p: str})
            # fig = px.scatter(components3, x=0, y=1, color=tmp['seed'], title='PCA_'+p+str(unique_value))                        
            # fig.write_image(folder+'/processing/pca_mit/PCA_'+p+str(unique_value)+'_gen_'+str(target_gen)+'.png')
            # plt.close()

            components4 = pca.fit_transform(Y1)
            fig = px.scatter(components4, x=0, y=1, color=tmp['seed'], title='PCA_noeevparam_'+p+str(unique_value), opacity=0.4)                        
            fig.write_image(folder+'/processing/pca_mit/PCA_noeevparam_'+p+str(unique_value)+'_gen_'+str(target_gen)+'.png')
            plt.close()

evolvables = [col for col in df.columns if col[:4]=="evol"]
for ev in evolvables:
    X = df.drop([p for p in params], axis=1)
    try:
        X = X.drop("seed", axis=1)
    except:
        pass
    # parameters fixed by user prior the run should not be taken into account for the PCA
    Y = X.drop([col for col in X.columns if col[:4]=="evol"], axis=1) #drop explicitely evolving parameters

    components = pca.fit_transform(Y)
    fig = px.scatter(components, x=0, y=1, color=df[ev], title='PCA_noeevparam_'+ev, opacity=0.4)                        
    fig.write_image(folder+'/processing/pca_mit/PCA_noeevparam_'+ev+'_gen_'+str(target_gen)+'.png')
    plt.close()