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
parser.add_argument("-p", dest='params', help="data to extract", nargs='+')
parser.add_argument("--cplx", help="some runs with complexes involved ?", action="store_true")

# Read arguments from command line
args = parser.parse_args()

folder = args.folder

hosts, mit = pd.DataFrame(), pd.DataFrame()
deaths_mit, deaths_host, divisions =  pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

if args.cplx:
    hosts_cplx = ['hosts1.csv','hosts2.csv','hosts3.csv','hosts4.csv','hosts5.csv','hosts6.csv','hosts7.csv','hosts9.csv','hosts10.csv','hosts11.csv','hosts12.csv',
        'hosts14.csv','hosts15.csv','hosts16.csv','hosts17.csv','hosts18.csv','hosts26.csv','hosts27.csv','hosts35.csv','hosts37.csv']
    mit_cplx = ['mit1.csv','mit2.csv','mit3.csv','mit4.csv','mit5.csv','mit6.csv','mit7.csv','mit9.csv','mit10.csv','mit11.csv','mit12.csv',
        'mit14.csv','mit15.csv','mit16.csv','mit17.csv','mit18.csv','mit26.csv','mit27.csv','mit35.csv','mit37.csv']

if not args.force and (os.path.exists(folder+'/total_hosts.csv') and os.path.exists(folder+'/total_mit.csv')):
    # and os.path.exists('/deaths_mit.csv') and os.path.exists('/deaths_host.csv') and os.path.exists(folder+'/divisions.csv')):
    print("Everything is already computed")
    print("Use option --force or -f to recompute")
    sys.exit()

for f in [seed_folder for seed_folder in os.listdir(folder)]:
    #Iterating over folder beginning with "seed"
    if args.verbose:
        print(f)

    try:
        hosts_tmp, mit_tmp = pd.DataFrame(), pd.DataFrame()
        deaths_mit_tmp, deaths_host_tmp, divisions_tmp =  pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        for string in args.params:
            if f[:4]=='host' and string=='host' and f!="hosts.csv":
                hosts_tmp = pd.read_csv('./'+folder+'/'+f, sep=';', low_memory=False)
                if args.cplx:
                    if f in hosts_cplx:
                        if args.verbose:
                            print("cplx")
                        hosts_tmp['cplx']=1
                    else:
                        if args.verbose:
                            print("no cplx")
                        hosts_tmp['cplx']=0
                if "genes" in hosts_tmp.columns:
                    hosts_tmp=hosts_tmp[hosts_tmp["genes"] != 100]
            elif f[:3]=='mit' and string=="mit" and f!='mit.csv':
                mit_tmp = pd.read_csv('./'+folder+'/'+f, sep=';', low_memory=False)
                if args.cplx:
                    if f in mit_cplx:
                        if args.verbose:
                            print("cplx")
                        mit_tmp['cplx']=1
                    else:
                        if args.verbose:
                            print("no cplx")
                        mit_tmp['cplx']=0
                if "genes" in mit_tmp.columns:
                    mit_tmp=mit_tmp[mit_tmp["genes"] != 100]
            
            elif f[:11]=='deaths_host' and string=='deaths_host' and f!="deaths_host.csv":
                deaths_host_tmp = pd.read_csv('./'+folder+'/'+f, sep=';', low_memory=False)
                if args.cplx:
                    if f in mit_cplx:
                        if args.verbose:
                            print("cplx")
                        deaths_host_tmp['cplx']=1
                    else:
                        if args.verbose:
                            print("no cplx")
                        deaths_host_tmp['cplx']=0
                if "genes" in deaths_host_tmp.columns:
                    deaths_host_tmp=deaths_host_tmp[deaths_host_tmp["genes"] != 100]
                
            elif f[:10]=='deaths_mit' and string=='deaths_mit' and f!="deaths_mit.csv":
                deaths_mit_tmp = pd.read_csv('./'+folder+'/'+f, sep=';', low_memory=False)
                if args.cplx:
                    if f in mit_cplx:
                        if args.verbose:
                            print("cplx")
                        deaths_mit_tmp['cplx']=1
                    else:
                        if args.verbose:
                            print("no cplx")
                        deaths_mit_tmp['cplx']=0
                if "genes" in deaths_mit_tmp.columns:
                    deaths_mit_tmp=deaths_mit_tmp[deaths_mit_tmp["genes"] != 100]
            
            elif f[:9]=='divisions' and string=='divisions' and f!="divisions.csv":
                divisions_tmp = pd.read_csv('./'+folder+'/'+f, sep=';', low_memory=False)
                if args.cplx:
                    if f in mit_cplx:
                        if args.verbose:
                            print("cplx")
                        divisions_tmp['cplx']=1
                    else:
                        if args.verbose:
                            print("no cplx")
                        divisions_tmp['cplx']=0
                if "genes" in divisions_tmp.columns:
                    divisions_tmp=divisions_tmp[divisions_tmp["genes"] != 100]


        hosts = pd.concat([hosts, hosts_tmp], sort=False)
        mit = pd.concat([mit, mit_tmp], sort=False)
        deaths_mit = pd.concat([deaths_mit, deaths_mit_tmp], sort=False)
        deaths_host = pd.concat([deaths_host, deaths_host_tmp], sort=False)
        divisions = pd.concat([divisions, divisions_tmp], sort=False)

        if args.verbose:
            print(hosts.shape, mit.shape)
            print(deaths_mit.shape, deaths_host.shape, divisions.shape)
    
    except:
        print("error for ",f)
        pass
    
if "host" in args.params:
    hosts.to_csv(folder+'/hosts.csv', sep=";")
if "mit" in args.params:
    mit.to_csv(folder+'/mit.csv', sep=";")
if "deaths_mit" in args.params:
    deaths_mit.to_csv(folder+'/deaths_mit.csv', sep=';')
if "deaths_host" in args.params:
    deaths_host.to_csv(folder+'/deaths_host.csv', sep=';')
if "divisions" in args.params:
    divisions.to_csv(folder+'/divisions.csv', sep=';')