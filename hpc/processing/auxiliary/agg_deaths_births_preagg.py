import pandas as pd
import matplotlib.pyplot as plt 
import sys, os
import matplotlib.patches as mpatches
import numpy as np
import itertools
import argparse
 
# Initialize parser
parser = argparse.ArgumentParser()

# Adding optional argument
parser.add_argument("folder", help="folder in which to run the code") # Positional argument
parser.add_argument("-v", "--verbose", help="print more information", action="store_true")
parser.add_argument("-f", "--force", help="re-aggregating even if already done", action="store_true")
 
# Read arguments from command line
args = parser.parse_args()

folder = args.folder

deaths, divisions =  pd.DataFrame(), pd.DataFrame()

if not args.force and (os.path.exists(folder+'/hosts.csv') and os.path.exists(folder+'/mit.csv')
    and os.path.exists('/deaths_mit.csv') and os.path.exists('/deaths_host.csv') and os.path.exists(folder+'/divisions.csv')):
    print("Everything is already computed")
    print("Use option --force or -f to recompute")
    sys.exit()

for f in [seed_folder for seed_folder in os.listdir(folder) if seed_folder[:4]=='seed']:
    #Iterating over folder beginning with "seed"
    k = f.replace('/',' ').split('-')
    i = 0
    while i < len(k):
        try:
            if k[i][-2:]=='1e' or k[i][-2:]=='5e': #For degenerated cases of rates
                k[i] = k[i]+ '-' + k[i+1]
                if i < len(k)-2:
                    k = k[:i+1]+k[i+2:]
                i=0
                continue
        except:
            i+=1
        i+=1
    i = iter(k)
    params = dict(zip(i,i))

    print(params)
    try:
        deaths_tmp = pd.read_csv('./'+folder+'/'+f+'/deaths.csv', sep=';', low_memory=False)
        divisions_tmp = pd.read_csv('./'+folder+'/'+f+'/divisions.csv', sep=';', low_memory=False)
       
        
        for k in params:
            deaths_tmp[k] = params[k]
            divisions_tmp[k] = params[k]

        deaths = pd.concat([deaths, deaths_tmp], sort=False)
        divisions = pd.concat([divisions, divisions_tmp], sort=False)
        if args.verbose:
            print(deaths, divisions)
    
    except:
        pass

deaths.to_csv(folder+'/deaths.csv', sep=';')
divisions.to_csv(folder+'/divisions.csv', sep=';')