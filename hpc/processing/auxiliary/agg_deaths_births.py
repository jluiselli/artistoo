import pandas as pd
import sys, os
import reading as rd

folder = sys.argv[1]

deaths, divisions = pd.DataFrame(), pd.DataFrame()


for f in os.listdir(folder):
    k = f.replace('/',' ').split('-')
    try:
        k[-2] = k[-2]+'-'+k[-1]
    except:
        pass
    i = iter(k)
    params = dict(zip(i,i))

    print(f)
    print(params)
    try:   
        deaths_tmp = rd.read_deaths_births(fname='./'+folder+'/'+f+"/deaths.txt")
        print(deaths_tmp)
        print(folder+'/'+f+'/deaths.csv')
        for k in params:
            deaths_tmp[k] = float(params[k])
        deaths_tmp.to_csv(folder+'/'+f+'/deaths.csv', sep=';')
        divisions_tmp = rd.read_deaths_births(fname='./'+folder+'/'+f+"/divisions.txt")
        
        for k in params:
            divisions_tmp[k] = float(params[k])
        
        print(divisions_tmp)
        print(folder+'/'+f+'/deaths.csv')
        divisions_tmp.to_csv(folder+'/'+f+'/divisions.csv', sep=';')
        
        deaths = pd.concat([deaths, deaths_tmp], sort=False)
        divisions = pd.concat([divisions, divisions_tmp], sort=False)
    except:
        pass


    deaths.to_csv(folder+'/deaths.csv', sep=';')
    divisions.to_csv(folder+'/divisions.csv', sep=';')