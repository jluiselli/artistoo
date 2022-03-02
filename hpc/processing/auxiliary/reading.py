import json, os, pickle, re
import pandas as pd
from file_read_backwards import FileReadBackwards
from multiprocessing.dummy import Pool as ThreadPool
from functools import partial
import random as rd



def readfile(fname, verbose=True, start=None, stop=None,
    exclude=['subcells', 'type'], rate=1):
    print("reading ", rate," proportion of file")

    if not os.path.isfile(fname) or os.path.getsize(fname) == 0:
        if verbose:
            print("Cannot see: " + fname + " or it is empty")
        return

    ifs = open(fname)
    line = ifs.readline()
    it = 0
    hosts = pd.DataFrame()
    mit = pd.DataFrame()

    while line:
        if rd.random() > rate:
            line = ifs.readline()
            it += 1
        else:
            if (start != None and it < start):
                line = ifs.readline()
                it += 1
                continue
            if (stop != None and it > stop):
                break

            if line[0] == "{":
                it += 1
                read = json.loads(line)

                tmp_df = pd.DataFrame.from_dict(read, orient='index')

                if 'subcells' in exclude:
                    for key in exclude:
                        if key!='subcells':
                            tmp_df.pop(key)
                    hosts = pd.concat([hosts, tmp_df], sort=False)
                    line = ifs.readline()
                    continue

                else:
                    for idx, row in tmp_df.iterrows():
                        mit = pd.concat([mit,
                            pd.DataFrame.from_dict(row['subcells'], orient='index')], sort=False)
                    
                    for key in exclude:
                        tmp_df.pop(key)
                        try:
                            tmp_df.pop(key)
                        except:
                            pass
                        try:
                            mit.pop(key)
                        except:
                            pass
                
                if tmp_df['time'].iloc[0]%500==1:
                    print(fname, "time:",tmp_df['time'].iloc[0])
                hosts = pd.concat([hosts, tmp_df], sort=False)
                line = ifs.readline()

            elif line[0] != "{":
                it += 1
                line = ifs.readline()

    ifs.close()
    return hosts, mit