import pandas as pd
import sys, os
import reading as rd

folder = sys.argv[1]
is_mit = int(sys.argv[2])

hosts, mit = pd.DataFrame(), pd.DataFrame()


for f in os.listdir(folder):
    k = f.replace('/',' ').split('_')
    i = iter(k)
    params = dict(zip(i,i))

    print(f)
    print(params)
    try:
        if is_mit:
            hosts_tmp, mit_tmp = rd.readfile(fname='./'+folder+'/'+f+"/Mitochondrialog.txt",
                        start=10,
                        exclude=['subcells','V','vol','parent','good','bads',
                                'dna','type','n mito', 'total_oxphos'])
        else:
            hosts_tmp, mit_tmp = rd.readfile(fname='./'+folder+'/'+f+"/Mitochondrialog.txt",
                    start=10, 
                    exclude=['V','vol','parent','good','bads',
                            'dna','type','n mito', 'total_oxphos'])
        
        for k in params:
            hosts_tmp[k] = float(params[k])
            mit_tmp[k] = float(params[k])
        
        hosts = pd.concat([hosts, hosts_tmp], sort=False)
        mit = pd.concat([mit, mit_tmp], sort=False)
    
    except:
        pass


for key in hosts.iloc[0]['evolvables'].keys():
    hosts[str(key)] = [hosts.iloc[i]['evolvables'][str(key)] for i in range(len(hosts))]

hosts.to_csv(folder+'/hosts.csv')
mit.to_csv(folder+'/mit.csv')