 end_param = {
    '1e-5': {
        '2516': {
            'fusion_rate':2.7384668519792937e-05,
            'fission_rate':2.243298692922667e-05,
            'rep':23.539005807287168,
            'HOST_V_PER_OXPHOS':0.22714164694234532,
            'host_division_volume':3054.0748268372727,
        },
        '4279': {
            'fusion_rate':4.833433773191071e-05,
            'fission_rate':2.2887737340325555e-05,
            'rep':16.85745305650218,
            'HOST_V_PER_OXPHOS':0.1061346793472079,
            'host_division_volume':3413.9801732154406,
        },
        '477072': {
            'fusion_rate':-0.00034165826438228565,
            'fission_rate':2.447711089928693e-05,
            'rep':17.004894051890986,
            'HOST_V_PER_OXPHOS':0.24089276580857652,
            'host_division_volume':3238.8149569052516,
        },
        '539267': {
            'fusion_rate':0.00018650682467690288,
            'fission_rate':2.346222410219342e-05,
            'rep':19.13765523451326,
            'HOST_V_PER_OXPHOS':0.187200718802012,
            'host_division_volume':3235.6867643666933,
        },
        '630781' : {
            'fusion_rate':0.0003832943035344817,
            'fission_rate':4.153838410527556e-05,
            'rep':19.015717251259332,
            'HOST_V_PER_OXPHOS':0.15731043572829437,
            'host_division_volume':4242.351701161582,
        },
    },
    '5e-6': {
        '2516': {
            'fusion_rate':0.0007698905127168522,
            'fission_rate':1.26435985644814e-05,
            'rep':23.822415626552676,
            'HOST_V_PER_OXPHOS':0.35318875387694176,
            'host_division_volume':2274.0217399233256,
        },
        '4279': {
            'fusion_rate':0.00020773349142608847,
            'fission_rate':2.9734563934103032e-05,
            'rep':12.849194397799769,
            'HOST_V_PER_OXPHOS':0.14957347785116765,
            'host_division_volume':3421.184652783957,
        },
        '477072': {
            'fusion_rate':0.0004990224342063012,
            'fission_rate':2.4342049549866985e-05,
            'rep':20.738601426141187,
            'HOST_V_PER_OXPHOS':0.20371494445106061,
            'host_division_volume':2717.833873995393,
        },
        '539267': {
            'fusion_rate':0.0006616986268638812,
            'fission_rate':2.1927398295462504e-05,
            'rep':20.813487645728955,
            'HOST_V_PER_OXPHOS':0.22612044609299725,
            'host_division_volume':2683.09556687052,
        },
        '630781' : {
            'fusion_rate':5.5585205140555446e-05,
            'fission_rate':1.9926546910546363e-05,
            'rep':24.447518827444178,
            'HOST_V_PER_OXPHOS':0.1735765033096156,
            'host_division_volume':2527.0305366924385,
        },
    },
    '5e-5': {
        '2516': {
            'fusion_rate':0.00026117206561496116,
            'fission_rate':3.035864070915758e-05,
            'rep':15.485949242579471,
            'HOST_V_PER_OXPHOS':0.34696884595842287,
            'host_division_volume':3111.137406112978,
        },
        '4279': {
            'fusion_rate':0.000251920029669243,
            'fission_rate':3.13508279111806e-05,
            'rep':19.89101884421596,
            'HOST_V_PER_OXPHOS':0.4028820447858228,
            'host_division_volume':3201.9533850652783,
        },
        '477072': {
            'fusion_rate':-0.00018859701758699814,
            'fission_rate':3.190641319320489e-05,
            'rep':18.01202276173148,
            'HOST_V_PER_OXPHOS':0.2751361682412419,
            'host_division_volume':3870.3839447913724,
        },
        '539267': {
            'fusion_rate':-0.0004485832182359092,
            'fission_rate':2.6342677578643742e-05,
            'rep':27.090727258827588,
            'HOST_V_PER_OXPHOS':0.44490581572176463,
            'host_division_volume':3944.7075144052737,
        },
        '630781' : {
            'fusion_rate':0.00010716723052163382,
            'fission_rate':2.669434799492067e-05,
            'rep':17.58656751830081,
            'HOST_V_PER_OXPHOS':0.4056631896328896,
            'host_division_volume':3548.5180918799606,
        },
    }
}

import pandas as pd 
import numpy as np
df = pd.read_csv('./Hosts_Mitochondrialog.txt', sep=";")
df = df[df['time']==max(df['time'])]
print(np.mean(df['evolvables_fusion_rate']))
