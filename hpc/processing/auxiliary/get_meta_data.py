import pandas as pd
import sys, os, shutil
import numpy as np
import itertools
import argparse


# Initialize parser
parser = argparse.ArgumentParser()

# Adding optional argument
parser.add_argument("folder", help="folder in which to run the code") # positional arg
parser.add_argument("-v", "--verbose", help="print more information", action="store_true")
parser.add_argument("-g", "--generation", type=int, help="which generation do you want to extract")

duplicated_params = {
    'genes':'rep_genes', 'deprecation_rate':'pdeg','growth_rate':'mit_growth_rate',
    'damage':'damage_rate', 'degradation':'pdeg', 'start':'init_fusion','rep':'production',
    'prot_mut':'pmut'
    }

# Read arguments from command line
args = parser.parse_args()
folder = args.folder
if args.verbose:
    print(args)

try:
    hosts = pd.read_csv(folder+'/hosts_'+str(args.generation)+'.csv', sep=";")
    mit = pd.read_csv(folder+'/mit_'+str(args.generation)+'.csv', sep=";")
    rates = pd.read_csv(folder+'/rates_'+str(args.generation)+'.csv', sep=';')
except:
    print("you should have aggregated data first")
    sys.exit()


mit = mit.rename(columns = {'id':'mit_id','host':'host_id','V':'V_mit','vol':'vol_mit','time of birth':'time of birt mit'})
mit = mit.drop([i for i in mit.columns if "Unname" in i], axis=1)
mit = mit.rename(columns=duplicated_params)

hosts = hosts.rename(columns = {'id':'host_id','V':'V_host','vol':'vol_host','time of birth':'time of birt host'})
hosts = hosts.drop([i for i in hosts.columns if "Unname" in i], axis=1)
hosts = hosts.rename(columns=duplicated_params)

df = pd.merge_ordered(hosts, mit, fill_method='ffill')
if args.verbose:
    print(df)

rates["time"] = [t if t%10==0 else t-1 for t in rates["time"]]
df["time"] = [t if t%10==0 else t-1 for t in df["time"]]

df = pd.merge_ordered(df, rates, fill_method='ffill')
if args.verbose:
    print(df)

df = df.replace({'true':1,'True':1,'False':0,'false':0, "undefined":'NaN'})
df.to_csv('total_df_'+str(args.generation)+'.csv',sep=';')


meta_data = pd.DataFrame()

possibles_params = [
        'rep_genes','tr_genes','growth_rate','selective','seed','evolving_grrate','cplx',
        'rep','genes','pmut','pdeg','partition','damage','mit_growth_rate','host_growth_rate',
        'damage_rate','deprecation_rate','production','degradation','div_vol','host_mutation',
        'mit_t','start','init_fusion','sharing', 'mutant', 'folder',
    ]

id = 0
meta = pd.DataFrame()
for mut in df.mutant.unique():
    print(mut)
    tmp_df = df[df['mutant']==mut]
    for fol in tmp_df.folder.unique():
        print(fol)
        tmp_df2 = tmp_df[tmp_df['folder']==fol]
        for s in tmp_df2.seed.unique():
            print(s)
            tmp_df3 = tmp_df2[tmp_df2['seed']==s]

            comb = []
            for k in [param for param in tmp_df3.columns if param in possibles_params]:
                tmp_list = []
                for val in tmp_df3[k].unique():
                    tmp_list+=[val]
                comb += [[k]]
                comb += [tmp_list]
            combinations = list(itertools.product(*comb))


            for c in combinations:
                d = {}
                for i in range(int(len(c)/2)):
                    d[c[int(2*i)]]=c[int(2*i+1)]
                # if args.verbose:
                #     print(d)
                

                tmp_df4 = tmp_df3.loc[(tmp_df3[list(d)] == pd.Series(d)).all(axis=1)]
                if tmp_df4.empty:
                    continue
                
                tmp_meta = pd.DataFrame()
                for key in d:
                    tmp_meta[key] = [d[key]]

                for col in tmp_df4.columns:
                    if (col not in d) and (col not in ['type','good','bads','dna','bad products', 'products', 'sum dna']):
                        tmp_df4 = tmp_df4.astype({col:float})
                        tmp_meta['mean_'+col] = np.mean(tmp_df4[col].unique())
                        tmp_meta['std_'+col] = np.std(tmp_df4[col].unique())

                tmp_meta['n cells'] = len(tmp_df4['host_id'].unique())

                # for col in ["birth_rate", "death_rate_hosts", "death_rate_mit"]:
                for col in ["birth_rate", "death_rate_hosts"]:
                    tmp_meta[col] = tmp_df4[col].unique()

                tmp_meta['id']=id
                id += 1
                
                meta = pd.concat([meta, tmp_meta])
            if args.verbose:
                print(meta.shape)

meta.to_csv(folder+'/meta_data_'+str(args.generation)+'.csv', sep=';')
if args.verbose:
    print("done.")




    

