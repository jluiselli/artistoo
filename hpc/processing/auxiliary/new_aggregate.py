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

hosts, mit = pd.DataFrame(), pd.DataFrame()
deaths_mit, deaths_host, divisions =  pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

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
            if k[i][-2:]=='1e' or k[i][-2:]=='5e' or k[i][-2:]=='2e': #For degenerated cases of rates
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
        hosts_tmp = pd.read_csv('./'+folder+'/'+f+'/Hosts_Mitochondrialog.txt', sep=';', low_memory=False)
        mit_tmp = pd.read_csv('./'+folder+'/'+f+'/Mit_Mitochondrialog.txt', sep=';', low_memory=False)
        try:
            deaths_mit_tmp = pd.read_csv('./'+folder+'/'+f+'/Mit_deaths.txt', sep=';', low_memory=False)
            deaths_host_tmp = pd.read_csv('./'+folder+'/'+f+'/Host_deaths.txt', sep=';', low_memory=False)
            divisions_tmp = pd.read_csv('./'+folder+'/'+f+'/divisions.txt', sep=';', low_memory=False)
        except:
            print("no recent version of deaths and division recording")
            deaths_mit_tmp = pd.DataFrame()
            deaths_host_tmp = pd.DataFrame()
            divisions_tmp = pd.DataFrame()
       
        
        for k in params:
            hosts_tmp[k] = params[k]
            mit_tmp[k] = params[k]
            deaths_mit_tmp[k] = params[k]
            deaths_host_tmp[k] = params[k]
            divisions_tmp[k] = params[k]

        hosts = pd.concat([hosts, hosts_tmp], sort=False)
        mit = pd.concat([mit, mit_tmp], sort=False)
        deaths_mit = pd.concat([deaths_mit, deaths_mit_tmp], sort=False)
        deaths_host = pd.concat([deaths_host, deaths_host_tmp], sort=False)
        divisions = pd.concat([divisions, divisions_tmp], sort=False)
        if args.verbose:
            print(hosts, mit, deaths_mit, deaths_host, divisions)
    
    except:
        pass

print(hosts)
hosts.to_csv(folder+'/hosts.csv', sep=";")
mit.to_csv(folder+'/mit.csv', sep=";")
deaths_mit.to_csv(folder+'/deaths_mit.csv', sep=';')
deaths_host.to_csv(folder+'/deaths_host.csv', sep=';')
divisions.to_csv(folder+'/divisions.csv', sep=';')