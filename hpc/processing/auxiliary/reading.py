import json, os, pickle, re
import pandas as pd
from file_read_backwards import FileReadBackwards
from multiprocessing.dummy import Pool as ThreadPool
from functools import partial
import numpy as np



def readfile(fname, verbose=True, start=None, stop=None,
    exclude=['subcells', 'type']):
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
            
            if tmp_df['time'].iloc[0]%1000==1:
                print("time:",tmp_df['time'].iloc[0])
            hosts = pd.concat([hosts, tmp_df], sort=False)
            line = ifs.readline()

        elif line[0] != "{":
            it += 1
            line = ifs.readline()

    ifs.close()
    return hosts, mit



def read_deaths_births(fname, verbose=True, start=None, stop=None, ignore=0.9):
    if not os.path.isfile(fname) or os.path.getsize(fname) == 0:
        if verbose:
            print("Cannot see: " + fname + " or it is empty")
        return

    ifs = open(fname)
    line = ifs.readline()
    it = 0
    data = pd.DataFrame()

    while line:
        if (start != None and it < start):
            line = ifs.readline()
            it += 1
            continue
        if (stop != None and it > stop):
            break

        if np.random.random()<ignore:
            continue

        if line[0] == "{":
            it += 1
            read = json.loads(line)
            tmp_df = pd.DataFrame.from_dict(read, orient='index')
            tmp_df = tmp_df.T
            try:
                tmp_df = tmp_df[["time","type"]] #deaths
            except:
                tmp_df = tmp_df.T # divisions
                tmp_df = pd.DataFrame(
                    {"time": [tmp_df.iloc[0]["time"]],
                     "type": [tmp_df.iloc[0]["type"]]}
                )
            
            if tmp_df['time'].iloc[0]%10000==0:
                print("time:",tmp_df['time'].iloc[0])
                # print(data)

            # tmp_df = tmp_df[['time','type']]
            data = pd.concat([data, tmp_df], sort=False)
            line = ifs.readline()
        elif line[0] != "{":
            it += 1
            line = ifs.readline()

    ifs.close()
    return data