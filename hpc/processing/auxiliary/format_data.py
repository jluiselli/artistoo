import pandas as pd
import matplotlib.pyplot as plt 
import sys, os
import matplotlib.patches as mpatches
import numpy as np
import itertools
import argparse

 
# Initialize parser
parser = argparse.ArgumentParser(description="""default_params = {
    'rep_genes':50,'tr_genes':5,'selective':'false','evolving_grrate':'false','cplx':'false',
    'pmut':0,'pdeg':0.1,'partition':0.5,'mit_growth_rate':2,'host_growth_rate':0.3,
    'damage_rate':5e-6,'production':19,'div_vol':-1,'host_mutation':5e-6, 'sharing':0,
    'mit_t':0,'init_fusion':0.0001, 'host_division_volume': 2000, 'mutant':None, 'folder':None
}""")

# Adding optional argument
parser.add_argument("folder", help="folder in which to run the code") # Positional argument
parser.add_argument("-v", "--verbose", help="print more information", action="store_true")
parser.add_argument("-p", "--params", help="enable to specify value differing from default", nargs='+')
 
# Read arguments from command line
args = parser.parse_args()

folder = args.folder
params = args.params

dict_params = {}
for i in range(int(len(params)/2)):
    dict_params[params[int(2*i)]] = params[int(2*i+1)]

if not ("folder" in dict_params):
    print("Please specify the folder name")
    sys.exit()

if not ("mutant" in dict_params):
    print("Please specify the mutant number")
    sys.exit()

possibles_params = [
    'rep_genes','tr_genes','selective','evolving_grrate','cplx',
    'pmut','pdeg','partition','mit_growth_rate','host_growth_rate',
    'damage_rate','production','div_vol','host_mutation', 'sharing',
    'mit_t','init_fusion','host_division_volume', 'mutant', 'folder'
]

duplicated_params = {
    'genes':'rep_genes', 'deprecation_rate':'pdeg','growth_rate':'mit_growth_rate',
    'damage':'damage_rate', 'degradation':'pdeg', 'start':'init_fusion','rep':'production',
    'prot_mut':'pmut'
}

default_params = {
    'rep_genes':50,'tr_genes':5,'selective':'false','evolving_grrate':'false','cplx':'false',
    'pmut':0,'pdeg':0.1,'partition':0.5,'mit_growth_rate':2,'host_growth_rate':0.3,
    'damage_rate':5e-6,'production':19,'div_vol':-1,'host_mutation':5e-6, 'sharing':0,
    'mit_t':0,'init_fusion':0.0001, 'host_division_volume': 2000, 'mutant':None, 'folder':None
}

first = True

for f in ['/hosts.csv', '/mit.csv', '/deaths_mit.csv', '/deaths_host.csv', '/divisions.csv']:
    used_default = []
    used_param = []
    if args.verbose:
        print(f)
    df = pd.read_csv(folder+f, sep="[:;]", engine='python')
    df = df.rename(columns=duplicated_params)
    df = df.drop([i for i in df.columns if i[:7]=='Unnamed'], axis=1)
    df = df.drop([i for i in df.columns if i[:7]=='"Unname'], axis=1)
    for p in possibles_params:
        if p in df.columns:
            continue
        if args.verbose:
            print(p)
        if p in dict_params:
            df[p] = dict_params[p]
            used_param += [p]
        else:
            df[p] = default_params[p]
            used_default += [p]


    print("Default value used for ",f)
    print(str([(p,default_params[p]) for p in used_default]))
    print(str([(p,dict_params[p]) for p in used_param]))

    df.to_csv(folder+f, sep=';',index=False)
    print(f, " done")


