import pandas as pd
import sys, os

folder = sys.argv[1]

hosts, mit = pd.DataFrame(), pd.DataFrame()
deaths_mit, deaths_host, divisions =  pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

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
            deaths_mit_tmp = params[k]
            deaths_host_tmp = params[k]
            divisions_tmp = params[k]

        hosts = pd.concat([hosts, hosts_tmp], sort=False)
        mit = pd.concat([mit, mit_tmp], sort=False)
        deaths_mit = pd.concat([deaths_mit, deaths_mit_tmp], sort=False)
        deaths_host = pd.concat([deaths_host, deaths_host_tmp], sort=False)
        divisions = pd.concat([divisions, divisions_tmp], sort=False)
    
    except:
        pass

print(hosts)
hosts.to_csv(folder+'/hosts.csv', sep=";")
mit.to_csv(folder+'/mit.csv', sep=";")
deaths_mit.to_csv(folder+'/deaths_mit.csv', sep=';')
deaths_host.to_csv(folder+'/deaths_host.csv', sep=';')
divisions.to_csv(folder+'/divisions.csv', sep=';')