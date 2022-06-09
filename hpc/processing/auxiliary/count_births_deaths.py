import pandas as pd
import sys, os, shutil
import numpy as np
import random
import itertools
import copy as copy
 

def count_births_deaths(folder, verbose=False):
    possibles_params = [
        'rep_genes','tr_genes','growth_rate','selective','seed','evolving_grrate','cplx',
        'rep','genes','pmut','pdeg','partition','damage','mit_growth_rate','host_growth_rate',
        'damage_rate','deprecation_rate','production','degradation','div_vol','host_mutation',
        'mit_t','start','init_fusion', 'mutant', 'folder'
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

    try:
        count_df = pd.read_csv(folder+'/count_df.csv', sep=';')
        count_df = count_df.rename(columns=duplicated_params)
        if verbose:
            print("counts already computed")
    except:
        if verbose:
            print("computing from scratch")
        for tmpfile in ["/deaths_host.csv","/deaths_mit.csv","/divisions.csv", "/hosts.csv"]:
            with open(folder+tmpfile) as f:
                lines = f.readlines()
            for i in range(100):
                lines[0]=lines[0].replace('; '+str(i)+';',';')
            # lines[0]=lines[0].replace('tr_genes;;mit','tr_genes;mit')
            # lines[0]=lines[0].replace(';tr_genes;evolving_grrate',';tr_genes;;evolving_grrate')
            # lines[0]=lines[0].replace('mit_growth_rate;s','mit_growth_rate;;s')
            # lines[0]=lines[0].replace('e;selective','e;;selective')
            # lines[0]=lines[0].replace('g;selective','g;;selective')
            # lines[0]=lines[0].replace('init_fusion;s','init_fusion;;s')
            # lines[0]=lines[0].replace(';evolvables_sharing_rate;;selective',';evolvables_sharing_rate;;;;selective')
            # lines[0]=lines[0].replace(';evolvables_sharing_rate;;;;selective',';evolvables_sharing_rate;;;selective')
            # lines[0]=lines[0].replace('evolving_grrate;sharing;selective;','evolving_grrate;sharing;;selective;')
            lines[0]=lines[0].replace(';evolvables_sharing_rate; 21;',';evolvables_sharing_rate;;;')
            lines[0]=lines[0].replace(";sharing;evolvables_sharing_rate;tr_genes;;evolving_grrate",
                            ";sharing;evolvables_sharing_rate;;;tr_genes;evolving_grrate")
            lines[0]=lines[0].replace(";sharing;tr_genes",";sharing;;;tr_genes")
            lines[0]=lines[0].replace('evolvables_sharing_rate;tr_genes','evolvables_sharing_rate;;;tr_genes')
            lines[0]=lines[0].replace('evolvables_sharing_rate;;;;tr_genes','evolvables_sharing_rate;;;tr_genes')
            with open(folder+tmpfile,'w') as f:
                f.writelines(lines)
            
        # deaths_m = pd.read_csv(folder+'/deaths_mit.csv', low_memory=False, sep=";", index_col=False)
        deaths_h = pd.read_csv(folder+'/deaths_host.csv', low_memory=False, sep=";",index_col=False)
        print(deaths_h)
        divisions = pd.read_csv(folder+'/divisions.csv', low_memory=False, sep=';',index_col=False)
        if verbose:
            print("data read")
        if not "time" in divisions.columns:
            divisions = divisions.rename(columns={"parent_time":"time"})

        deaths_h = deaths_h.astype({"time":float})
        # deaths_m = deaths_m.astype({"time":float})
        divisions = divisions.astype({"time":float})
        for key in default_params:
            if key not in deaths_h.columns:
                deaths_h[key] = default_params[key]
            # if key not in deaths_m.columns:
            #     deaths_h[key] = default_params[key]
            if key not in divisions.columns:
                deaths_h[key] = default_params[key]

        # max_time = max(max(deaths_h['time']),max(deaths_m['time']),max(divisions['time']))
        max_time = max(max(deaths_h['time']),max(divisions['time']))

        deaths_h = deaths_h.drop(['sharing'],axis=1)
        divisions = divisions.drop(['sharing'],axis=1)

        if verbose:
            print("max time :", max_time)

        comb = []
        for k in [param for param in deaths_h.columns if param in possibles_params]:
            tmp_list = []
            for val in deaths_h[k].unique():
                tmp_list+=[val]
            comb += [[k]]
            comb += [tmp_list]
        combinations = list(itertools.product(*comb))

        if verbose:
            print("all combinations :\n",combinations)

        count_df = pd.DataFrame()
        for c in combinations:
            d = {}
            for i in range(int(len(c)/2)):
                d[c[int(2*i)]]=c[int(2*i+1)]
            if verbose:
                print(d)
            
            for key in d:
                print(key, d[key], deaths_h[key].unique())
            tmp_deaths_h = deaths_h.loc[(deaths_h[list(d)] == pd.Series(d)).all(axis=1)]
            # tmp_deaths_m = deaths_m.loc[(deaths_m[list(d)] == pd.Series(d)).all(axis=1)]
            tmp_divisions = divisions.loc[(divisions[list(d)] == pd.Series(d)).all(axis=1)]
            
            if verbose:
                print("filtering done")
            
            if len(tmp_deaths_h)==0:
                continue

            tmp2 = pd.DataFrame()
            tmp2["deaths_hosts"] = [len(tmp_deaths_h[(tmp_deaths_h["time"]>t*1000) & (tmp_deaths_h["time"]<(t+1)*1000)])
                        for t in range(int((max_time+1)/1000))]
            # tmp2["deaths_mit"] = [len(tmp_deaths_m[(tmp_deaths_m["time"]>t*1000) & (tmp_deaths_m["time"]<(t+1)*1000)]) 
            #             for t in range(int((max_time+1)/1000))]
            tmp2["divisions"] = [len(tmp_divisions[(tmp_divisions["time"]>t*1000) & (tmp_divisions["time"]<(t+1)*1000)]) 
                        for t in range(int((max_time+1)/1000))]
            tmp2["time"] = [t*1000 for t in range(int((max_time+1)/1000))]

            for key in d:
                tmp2[key] = d[key]
            
            if verbose:
                print(tmp2.shape)
                
            count_df = pd.concat([count_df,tmp2])
            if verbose:
                print(count_df.shape)
        
        count_df = count_df.rename(columns=duplicated_params)
        count_df.to_csv(folder+'/count_df.csv',sep=';')

    if verbose:
        print("now to rates")

    # for tmpfile in ["/hosts.csv","/mit.csv"]:
    #     print("rewriting ", tmpfile)
    #     with open(folder+tmpfile) as f:
    #         lines = f.readlines()
    #     lines[0]=lines[0].replace('""" 0"""""""','')
    #     lines[0]=lines[0].replace('; 19;',';')
    #     for i in range(100):
    #         lines[0]=lines[0].replace('; '+str(i)+';',';')
    #         lines[0]=lines[0].replace(';""" '+str(i)+'"""""""',';')
    #     lines[0]=lines[0].replace('tr_genes;;mit','tr_genes;mit')
    #     lines[0]=lines[0].replace('tr_genes;tr_genes;','')
    #     lines[0]=lines[0].replace('init_fusion;s','init_fusion;;s')
    #     lines[0]=lines[0].replace('mit_growth_rate;s','mit_growth_rate;;s')
    #     lines[0]=lines[0].replace('tr_genes;evolving_grrate','tr_genes;;evolving_grrate')
    #     lines[0]=lines[0].replace('e;selective','e;;selective')
    #     lines[0]=lines[0].replace('g;selective','g;;selective')
    #     if folder[-4:]=='cplx':
    #         lines[0]=lines[0].replace('e;selective','e;;;selective')
    #         lines[0]=lines[0].replace('e;;selective','e;;;selective')
    #     print(lines[0])
    #     with open(folder+tmpfile,'w') as f:
    #         f.writelines(lines)
    
    df_h = pd.read_csv(folder+'/hosts.csv', sep=';', index_col=False)
    # df_m = pd.read_csv(folder+'/mit.csv',low_memory=False, sep=';', index_col=False)
    df_h = df_h.rename(columns=duplicated_params)
    # df_m = df_m.rename(columns=duplicated_params)
    count_df = count_df.rename(columns=duplicated_params)
    max_time = min(max(df_h['time']),max(count_df['time']))-1000 # Safeguard
    print(max_time)
    print(df_h)
    for col in df_h.columns:
        print(col)
        print(df_h[col])

    if verbose:
        print("data read")

    comb = []
    for k in [param for param in count_df.columns if param in possibles_params]:
        tmp_list = []
        for val in count_df[k].unique():
            tmp_list+=[val]
        comb += [[k]]
        comb += [tmp_list]
    combinations = list(itertools.product(*comb))

    rates = pd.DataFrame()
    for c in combinations:
        d = {}
        for i in range(int(len(c)/2)):
            d[c[int(2*i)]]=c[int(2*i+1)]
        
        if verbose:
            print(d)
        
        #Extract data for this combination
        tmp_df_h = df_h.loc[(df_h[list(d)] == pd.Series(d)).all(axis=1)] #individuals
        # tmp_df_m = df_m.loc[(df_m[list(d)] == pd.Series(d)).all(axis=1)] #mit
        if tmp_df_h.empty:
            if verbose:
                # print(df_h)
                for k in d:
                    print(k, d[k], df_h[k].unique())
                print("empty combination 2")
            continue
        
        tmp_count = count_df.loc[(count_df[list(d)] == pd.Series(d)).all(axis=1)] #deaths/divisions
        if tmp_count.empty:
            if verbose:
                print("empty combination 1")
            continue
        print(max_time)
       
        n_indiv = pd.DataFrame()
        n_indiv["n_h"] = [len(tmp_df_h[(tmp_df_h["time"]>t*1000) & (tmp_df_h["time"]<(t+1)*1000)])
                            for t in range(int(max_time/1000+1))]
        # n_indiv["n_m"] = [len(tmp_df_m[(tmp_df_m["time"]>t*1000) & (tmp_df_m["time"]<(t+1)*1000)])
        #                     for t in range(int((max_time)/1000)+1)]

        tmp_rates = pd.DataFrame(data={
            "time" : [t*1000+1 for t in range(int((max_time)/1000+1))],
            "birth_rate": [a/b if b!=0 else np.nan for a,b in zip(tmp_count.divisions, n_indiv.n_h) ],
            "death_rate_hosts" : [a/b if b!=0 else np.nan for a,b in zip(tmp_count.deaths_hosts, n_indiv.n_h) ],
            # "death_rate_mit" : [a/b if b!=0 else np.nan for a,b in zip(tmp_count.deaths_mit, n_indiv.n_m) ],
            "seed" : [d['seed'] for t in range(int((max_time)/1000+1))]
        })
        for key in d:
            tmp_rates[key] = d[key]
        
        rates = pd.concat([rates,tmp_rates])
    
    rates.to_csv(folder+'/rates.csv', sep=';')
    if verbose:
        print("Rates computed")
        print(rates)

    return


