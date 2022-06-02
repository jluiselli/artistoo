import pandas as pd
import matplotlib.pyplot as plt 
import sys, os
import numpy as np
import itertools
import argparse
from count_births_deaths import count_births_deaths

 
# Initialize parser
parser = argparse.ArgumentParser()

# Adding optional argument
parser.add_argument("folder", help="folder in which to run the code") # Positional argument
parser.add_argument("-v", "--verbose", help="print more information", action="store_true")
parser.add_argument("-f", "--force", help="re-aggregating even if already done", action="store_true")
parser.add_argument("-g", "--generation", type=int, help="which generation do you want to extract", required = True)

# Read arguments from command line
args = parser.parse_args()

folder = args.folder

hosts, mit, rates = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

default_params = {
    'rep_genes':50,'tr_genes':5,'selective':'false','evolving_grrate':'false','cplx':'false',
    'pmut':0,'pdeg':0.1,'partition':0.5,'mit_growth_rate':2,'host_growth_rate':0.3,
    'damage_rate':5e-6,'production':19,'div_vol':-1,'host_mutation':5e-6, 'sharing':0,
    'mit_t':0,'init_fusion':0.0001, 'host_division_volume': 2000, 'mutant':None, 'folder':None
}
duplicated_params = {
    'genes':'rep_genes', 'deprecation_rate':'pdeg','growth_rate':'mit_growth_rate',
    'damage':'damage_rate', 'degradation':'pdeg', 'start':'init_fusion','rep':'production',
    'prot_mut':'pmut'
    }

if not args.force and (os.path.exists(folder+'/total_df.csv')):
    # and os.path.exists('/deaths_mit.csv') and os.path.exists('/deaths_host.csv') and os.path.exists(folder+'/divisions.csv')):
    print("Everything is already computed")
    print("Use option --force or -f to recompute")
    sys.exit()


folders = []
for subFolderRoot, foldersWithinSubFolder, f in os.walk(folder, topdown=False):
    if foldersWithinSubFolder == []: #Last level of folder
        folders += [subFolderRoot]
if args.verbose:
    print(folders)
 
 
for f in folders:
    if args.verbose:
        print(f)
    if os.path.exists(f+'/rates_'+str(args.generation)+'.csv'):
        print("exists")
        tmp_df = pd.read_csv(f+'/hosts_'+str(args.generation)+'.csv', sep=';')
        hosts = pd.concat([hosts, tmp_df], sort=False)
        tmp_df = pd.read_csv(f+'/mit_'+str(args.generation)+'.csv', sep=';')
        mit = pd.concat([mit, tmp_df], sort=False)
        tmp_df = pd.read_csv(f+'/rates_'+str(args.generation)+'.csv', sep=';')
        rates = pd.concat([rates, tmp_df], sort=False)
        continue

    if not os.path.exists(os.path.join(f,'rates.csv')):
        if args.verbose:
            print("first computing rates")
        count_births_deaths(f,verbose=args.verbose) #Big function to count births and deaths

    for dffile in ['hosts.csv','mit.csv','rates.csv']:
    # for dffile in ['hosts.csv','rates.csv']:
        if args.verbose:
            print(dffile)
        tmp_df = pd.read_csv(os.path.join(f,dffile), sep=';')
        if dffile == 'hosts.csv':
            tmp_df = pd.read_csv(os.path.join(f,dffile), sep='[:;]',engine='python')
        tmp_df = tmp_df.drop([i for i in tmp_df.columns if i[:7]=='Unnamed'], axis=1)
        tmp_df = tmp_df.astype({"time":float})
        tmp_df = tmp_df[(tmp_df["time"]==args.generation) | (tmp_df["time"]==args.generation+1) | (tmp_df["time"]==args.generation-1)]
        tmp_df = tmp_df.rename(columns=duplicated_params)
        if dffile == 'hosts.csv':
            hosts = pd.concat([hosts, tmp_df], sort=False)
            for key in default_params:
                if key not in tmp_df.columns:
                    tmp_df[key] = default_params[key]
            tmp_df.to_csv(f+'/hosts_'+str(args.generation)+'.csv', sep=";")
        elif dffile == 'mit.csv':
            for key in default_params:
                if key not in tmp_df.columns:
                    tmp_df[key] = default_params[key]
            mit = pd.concat([mit, tmp_df], sort=False)
            tmp_df.to_csv(f+'/mit_'+str(args.generation)+'.csv', sep=";")
        elif dffile == 'rates.csv':
            for key in default_params:
                if key not in tmp_df.columns:
                    tmp_df[key] = default_params[key]
            rates = pd.concat([rates,tmp_df], sort=False)
            tmp_df.to_csv(f+'/rates_'+str(args.generation)+'.csv', sep=";")
        print(tmp_df)
    
    if args.verbose:
        print(hosts.shape,mit.shape,rates.shape)

    
hosts.to_csv(folder+'/hosts_'+str(args.generation)+'.csv', sep=";")
mit.to_csv(folder+'/mit_'+str(args.generation)+'.csv', sep=";")
rates.to_csv(folder+'/rates_'+str(args.generation)+'.csv', sep=';')