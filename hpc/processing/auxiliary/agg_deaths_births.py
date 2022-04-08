import pandas as pd
import sys, os
import reading as rd

folder = sys.argv[1]

deaths, divisions = pd.DataFrame(), pd.DataFrame()


for f in os.listdir(folder):
    k = f.replace('/',' ').split('-')
    i = 0
    while i < len(k):
        try:
            if k[i][-2:]=='1e' or k[i][-2:]=='5e':
                k[i] = k[i]+ '-' + k[i+1]
                if i < len(k)-2:
                    k = k[:i+1]+k[i+2:]
                i=0
                continue
        except:
            i+=1
        i+=1

    j = iter(k)
    params = dict(zip(j,j))

    print(f)
    print(params)
    try:   
        print('./'+folder+'/'+f+"/deaths.txt")
        deaths_tmp = rd.read_deaths_births(fname='./'+folder+'/'+f+"/deaths.txt")
        print(deaths_tmp)
        print(folder+'/'+f+'/deaths.csv')
        for k in params:
            deaths_tmp[k] = float(params[k])
        deaths_tmp.to_csv(folder+'/'+f+'/deaths.csv', sep=';')

        divisions_tmp = rd.read_deaths_births(fname='./'+folder+'/'+f+"/divisions.txt", ignore=0)
        
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