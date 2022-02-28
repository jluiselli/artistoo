import pandas as pd
import sys, os

folder = sys.argv[1]

hosts, mit = pd.DataFrame(), pd.DataFrame()


for f in os.listdir(folder):
    # k = f.replace('/',' ').split('_')
    # i = iter(k)
    # params = dict(zip(i,i))

    k = f.replace('/',' ').split('-')
    try:
        k[5] = k[5]+'-'+k[6]
        k = k[:6]+k[7:]
    except:
        pass
    i = iter(k)
    params = dict(zip(i,i))


    print(params)
    try:
        hosts_tmp = pd.read_csv('./'+folder+'/'+f+'/Hosts_Mitochondrialog.txt', sep=';', low_memory=False)
        mit_tmp = pd.read_csv('./'+folder+'/'+f+'/Mit_Mitochondrialog.txt', sep=';', low_memory=False)
       
        
        for k in params:
            hosts_tmp[k] = params[k]
            mit_tmp[k] = params[k]

        hosts = pd.concat([hosts, hosts_tmp], sort=False)
        mit = pd.concat([mit, mit_tmp], sort=False)
    
    except:
        pass

print(hosts)
hosts.to_csv(folder+'/hosts.csv', sep=";")
mit.to_csv(folder+'/mit.csv', sep=";")