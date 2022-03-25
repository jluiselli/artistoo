import pandas as pd
import sys, os
import numpy as np

folder = sys.argv[1]

comp_df = pd.DataFrame()


for f in os.listdir(folder):

    k = f.replace('/',' ').split('-')
    
    i = iter(k)
    params = dict(zip(i,i))


    print(params)
    try:
        comp_tmp = pd.read_csv('./'+folder+'/'+f+'/competition_log.txt', sep=';', header = None, names=["time","distribution"], low_memory=False)    
        
        for k in params:
            comp_tmp[k] = params[k]

        comp_tmp["ones"]=0
        comp_tmp["prop_ones"]=0.0

        for j in range(len(comp_tmp)):
            comp_tmp.loc[j, "ones" ]= 0
            save = [int(comp_tmp.loc[j,"distribution"].split(',')[i]) for i in range(len(comp_tmp.loc[j,"distribution"].split(','))-1)]
            comp_tmp.loc[j, "ones"] += sum([i for i in save if i==1])
            comp_tmp.loc[j, "prop_ones"] = comp_tmp["ones"][j]/len(save)
        
        print(comp_tmp)
       
        comp_df = pd.concat([comp_tmp, comp_df], sort=False)

    except:
        pass

print(comp_df)

comp_df.to_csv('./'+folder+'/competition.csv', sep=";")
