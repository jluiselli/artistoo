import pandas as pd
import matplotlib.pyplot as plt 
import sys, os, shutil
import matplotlib.patches as mpatches
import numpy as np
import random
import colorsys
import itertools
import argparse
 
# Initialize parser
parser = argparse.ArgumentParser()

# Adding optional argument
parser.add_argument("folder", help="folder in which to run the code") # positional arg
parser.add_argument("-c", "--competition", help = "Specify that dual values are expected", action="store_true")
parser.add_argument("-p", dest='params', help="parameters in folder names to use", nargs='+')
parser.add_argument("-v", "--verbose", help="print more information", action="store_true")
parser.add_argument("--clean", help="cleans the folder before replotting", action="store_true")
parser.add_argument("-g", "--max_generation", type=int, help="end generation for the temporal plots. Default is last generation", default=-1)

# Read arguments from command line
args = parser.parse_args()
if args.verbose:
    print(args)

folder = args.folder
params = args.params

if args.competition:
    print("handling of competition runs for this plot not implemented yet")
    sys.exit()

if not os.path.isdir(folder+'/processing/'):
    print('The directory is not present. Creating a new one..')
    os.mkdir(folder+'/processing/')

if args.clean:
    shutil.rmtree(folder+'/processing/deaths_births/', ignore_errors=True)

if not os.path.isdir(folder+'/processing/deaths_births/'):
    print('The directory is not present or has been removed. Creating a new one..')
    os.mkdir(folder+'/processing/deaths_births/')

try:
    count_df = pd.read_csv(folder+'/count_df.csv', sep=';')
except:
    try:
        df_deaths = pd.read_csv(folder+'/deaths.csv', low_memory=False, sep=";")
        df_divisions = pd.read_csv(folder+'/divisions.csv', low_memory=False, sep=';')
        if args.verbose:
            print(df_deaths.columns)
            print(df_divisions.columns)
    except:
        try: # New type of data
            df_deaths_mit = pd.read_csv(folder+'/deaths_mit.csv', low_memory=False, sep=";")
            df_deaths_mit["type"] = "mito"
            df_deaths_host = pd.read_csv(folder+'/deaths_host.csv', low_memory=False, sep=";")
            df_deaths_host["type"] = "host"
            df_deaths = pd.concat([df_deaths_host, df_deaths_mit], sort=False)
            if args.verbose:
                print(df_deaths)
                print(df_deaths_host, df_deaths_mit)
                print(df_deaths.columns)
            df_divisions = pd.read_csv(folder+'/divisions.csv', low_memory=False, sep=';')
            if args.verbose:
                print(df_divisions.columns)
        except:
            print("***\nDeaths and births must have been aggregated !\nWarning: this can be very long for ancient simulations\n***")
            sys.exit()

    try:
        df_divisions = df_divisions.rename(columns={"parent_time":"time"})
    except:
        pass

    if args.max_generation != -1:
        df_deaths = df_deaths[df_deaths['time']<args.max_generation]
        df_divisions = df_divisions[df_divisions['time']<args.max_generation]



    usual_colors = ['tab:blue', 'tab:orange', 'tab:green','tab:purple','tab:red',
    'tab:pink','tab:brown'] 


    if params[-1]=='seed':
        unique_plots = True
    else:
        unique_plots = False

    comb = []
    for k in params:
        if k == 'seed':
            continue
        tmp_list = []
        for val in df_deaths[k].unique():
            tmp_list+=[val]
        comb += [tmp_list]
    combinations = list(itertools.product(*comb))

    df_deaths = df_deaths.astype({"time":float})
    df_divisions = df_divisions.astype({"time":float})

    timesteps = max(df_deaths['time'])//25000 #Nb of blocs of 25000 generations
    print(timesteps)
    count_df = pd.DataFrame()


    for t in range(int(timesteps)):
        deaths_h = df_deaths[df_deaths['type']=="host"]
        deaths_m = df_deaths[df_deaths['type']=="mito"]
        divisions = df_divisions
        print(t)
        print(t*25000)
        timestep = int(t*25000)
        deaths_h = deaths_h[deaths_h["time"]<=25000*(t+1)]
        deaths_m = deaths_m[deaths_m["time"]<=25000*(t+1)]
        divisions = divisions[divisions["time"]<=25000*(t+1)]
        deaths_h = deaths_h[deaths_h["time"]>25000*(t)]
        deaths_m = deaths_m[deaths_m["time"]>25000*(t)]
        divisions = divisions[divisions["time"]>25000*(t)]
        for s in df_deaths["seed"].unique():
            tmp_deaths_h = deaths_h[deaths_h["seed"]==s]
            tmp_deaths_m = deaths_m[deaths_m["seed"]==s]
            tmp_divisions = divisions[divisions["seed"]==s]
            for c in combinations:
                tmp = pd.DataFrame()
                tmp["timestep"]=timestep
                tmp["comb"]=c
                tmp["seed"]=s
                tmp["timestep"]=timestep
                i=0
                for k in params:
                    tmp[k] = c[i]
                    tmp_deaths_h2 = tmp_deaths_h[tmp_deaths_h[k]==c[i]]
                    tmp_deaths_m2 = tmp_deaths_m[tmp_deaths_m[k]==c[i]]
                    tmp_divisions2 = tmp_divisions[tmp_divisions[k]==c[i]]
                    i+=1
                if len(tmp_deaths_h2)==0 or len(tmp_deaths_m2)==0 or len(tmp_divisions2)==0:
                    continue
                tmp["deaths_hosts"] = len(tmp_deaths_h2)
                tmp["deaths_mit"] = len(tmp_deaths_m2)
                tmp["divisions"] = len(tmp_divisions2)
                count_df = pd.concat([count_df,tmp])
    count_df.to_csv(folder+'/count_df.csv',sep=';')

print(count_df)
tosort = ["timestep"] + params
count_df = count_df.sort_values(by=tosort)
comb = []
for k in params:
    if k == 'seed':
        continue
    tmp_list = []
    for val in count_df[k].unique():
        tmp_list+=[val]
    comb += [tmp_list]
combinations = list(itertools.product(*comb))
for c in combinations:
    tmp_count = count_df[count_df["comb"]==c]
    deaths_h, deaths_m, div = [],[],[]
    std_h, std_m, std_div = [],[],[]
    for t in tmp_count["timestep"].unique():
        tmp2 = tmp_count[tmp_count["timestep"]==t]
        deaths_h += [np.mean(tmp2["deaths_hosts"])]
        deaths_m += [np.mean(tmp2["deaths_mit"])]
        div += [np.mean(tmp2["divisions"])]
        std_h += [np.std(tmp2["deaths_hosts"])]
        std_m += [np.std(tmp2["deaths_mit"])]
        std_div += [np.std(tmp2["divisions"])]


    fig, ax = plt.subplots(1, 1, figsize=(15,10))
    ax.errorbar(x=tmp_count["timestep"].unique(),
            y = deaths_h, yerr = std_h, capsize=4, linewidth=3,
            )
    ax.set_ylabel('# deaths')
    ax.set_xlabel('time')
    ax.set_title("hosts deaths over time for "+str(c))
    fig.tight_layout()
    fig.savefig(folder+'/processing/deaths_births/death_time_host_'+str(c)+'.png')
    plt.close(fig)

    fig, ax = plt.subplots(1, 1, figsize=(15,10))
    ax.errorbar(x=tmp_count["timestep"].unique(),
            y = deaths_m, yerr = std_m, capsize=4, linewidth=3,
            )
    ax.set_ylabel('# deaths')
    ax.set_xlabel('time')
    ax.set_title("mit deaths over time for "+str(c))
    fig.tight_layout()
    fig.savefig(folder+'/processing/deaths_births/death_time_mit_'+str(c)+'.png')
    plt.close(fig)

    fig, ax = plt.subplots(1, 1, figsize=(15,10))
    ax.errorbar(x=tmp_count["timestep"].unique(),
            y = div, yerr = std_div, capsize=4, linewidth=3,
            )
    ax.set_ylabel('# divisions')
    ax.set_xlabel('time')
    ax.set_title("hosts divisons over time for "+str(c))
    fig.tight_layout()
    fig.savefig(folder+'/processing/deaths_births/divisions_'+str(c)+'.png')
    plt.close(fig)

for k in params:
    fig, ax = plt.subplots(1, 1, figsize=(15,10))
    for x in count_df[k].unique():
        tmp_count = count_df[count_df[k]==x]
        deaths_h = []
        std_h = []
        for t in tmp_count["timestep"].unique():
            deaths_h += [np.mean(tmp_count[tmp_count["timestep"]==t]["deaths_hosts"])]
            std_h += [np.std(tmp_count[tmp_count["timestep"]==t]["deaths_hosts"])]
        ax.errorbar(x=tmp_count["timestep"].unique(),
                y = deaths_h, yerr = std_h, label=str(x), capsize=4, linewidth=3,
                )

    ax.set_ylabel('# deaths')
    ax.set_xlabel('time')
    ax.legend()
    ax.set_title("hosts deaths over time "+k)
    fig.tight_layout()
    fig.savefig(folder+'/processing/deaths_births/death_time_host_'+str(k)+'.png')
    plt.close(fig)

    fig, ax = plt.subplots(1, 1, figsize=(15,10))
    for x in count_df[k].unique():
        tmp_count = count_df[count_df[k]==x]
        deaths_m = []
        std_m = []
        for t in tmp_count["timestep"].unique():
            deaths_m += [np.mean(tmp_count[tmp_count["timestep"]==t]["deaths_mit"])]
            std_m += [np.std(tmp_count[tmp_count["timestep"]==t]["deaths_mit"])]
        ax.errorbar(x=tmp_count["timestep"].unique(),
                y = deaths_m, yerr = std_m, label=str(x), capsize=4, linewidth=3,
                )

    ax.set_ylabel('# deaths')
    ax.set_xlabel('time')
    ax.legend()
    ax.set_title("mit deaths over time "+k)
    fig.tight_layout()
    fig.savefig(folder+'/processing/deaths_births/death_time_mit_'+str(k)+'.png')
    plt.close(fig)

    fig, ax = plt.subplots(1, 1, figsize=(15,10))
    for x in count_df[k].unique():
        tmp_count = count_df[count_df[k]==x]
        div = []
        std_div = []
        for t in tmp_count["timestep"].unique():
            div += [np.mean(tmp_count[tmp_count["timestep"]==t]["divisions"])]
            std_div += [np.std(tmp_count[tmp_count["timestep"]==t]["divisions"])]
        ax.errorbar(x=tmp_count["timestep"].unique(),
                y = div, yerr = std_div, label=str(x), capsize=4, linewidth=3,
                )

    ax.set_ylabel('# divisions')
    ax.set_xlabel('time')
    ax.legend()
    ax.set_title("hosts divisons over time "+k)
    fig.tight_layout()
    fig.savefig(folder+'/processing/deaths_births/divisions_'+str(k)+'.png')
    plt.close(fig)

# for celltype in ['host','mito']:
#     if args.verbose:
#         print(celltype)
#         # print(df_deaths)
#         # print(df_divisions)
#     deaths = df_deaths[df_deaths['type']==celltype]
#     divisions = df_divisions
#     if unique_plots:
#         if args.verbose:
#             print("doing all unique plots")
#         comb=[]
#         for k in params:
#             tmp_list = []
#             for val in deaths[k].unique():
#                 tmp_list+=[val]
#             comb += [tmp_list]
#         combinations = list(itertools.product(*comb))
#         for c in combinations:
#             if args.verbose:
#                 print("unique plot",c)
#             tmp_deaths = deaths
#             tmp_divisions = divisions
#             i=0
#             for k in params:
#                 tmp_deaths = tmp_deaths[tmp_deaths[k]==c[i]]
#                 tmp_divisions = tmp_divisions[tmp_divisions[k]==c[i]]
#                 i+=1
#             if tmp_deaths.empty or tmp_divisions.empty:
#                 continue
            
#             fig, ax = plt.subplots(1, 1, figsize=(15,10))
#             tmp_deaths["time"].plot.hist( alpha=0.9, ax=ax  )
#             ax.set_ylabel('# deaths')
#             ax.set_xlabel('time')
#             ax.set_title("# deaths over time "+str(c)+" "+celltype)
#             fig.tight_layout()
#             fig.savefig(folder+'/processing/deaths_births/death_time_'+str(c)+'_'+celltype+'.png')
#             plt.close(fig)

#             fig, ax = plt.subplots(1, 1, figsize=(15,10))
#             tmp_divisions["time"].plot.hist(alpha=0.9, ax=ax)
#             ax.set_ylabel('# divisions')
#             ax.set_xlabel('time')
#             ax.set_title("# divisions over time "+str(c))
#             fig.tight_layout()
#             fig.savefig(folder+'/processing/deaths_births/birth_time_'+str(c)+'_host.png')
#             plt.close(fig)

#         if args.verbose:
#             print("finished unique plots. On to merged seeds")
        

#     for k in params: # different values given at the beginning of the simulation
#         if k!='seed':
#             if args.verbose:
#                 print(k)
#             deaths = deaths.sort_values(by=[k])
#             fig, ax = plt.subplots(1, 1, figsize=(15,10))
#             ax.hist([deaths[deaths[k]==x]["time"] for x in deaths[k].unique()],
#                 label=deaths[k].unique())
#             ax.set_ylabel('# deaths')
#             ax.set_xlabel('time')
#             ax.legend(title=k)
#             ax.set_title("deaths over time for different "+k+" "+celltype)
#             fig.tight_layout()
#             fig.savefig(folder+'/processing/deaths_births/death_time_'+k+'_'+celltype+'.png')
#             plt.close(fig)

#             divisions = divisions.sort_values(by=[k])
#             fig, ax = plt.subplots(1, 1, figsize=(15,10))
#             ax.hist([divisions[divisions[k]==x]["time"] for x in divisions[k].unique()],
#                 label=divisions[k].unique())
#             ax.set_ylabel('# divisions')
#             ax.set_xlabel('time')
#             ax.legend(title=k)
#             ax.set_title("divisions over time for different "+k)
#             fig.tight_layout()
#             fig.savefig(folder+'/processing/deaths_births/birth_time_'+k+'.png')
#             plt.close(fig)


#             for unique_value in deaths[k].unique():
#                 tmp_deaths = deaths[deaths[k]==unique_value]
#                 tmp_divisions = divisions[divisions[k]==unique_value]
#                 if tmp_deaths.empty or tmp_divisions.empty:
#                     continue
#                 for other_param in params:
#                     if k!=other_param:
#                         tmp_deaths = tmp_deaths.sort_values(by=[other_param])
#                         tmp_divisions = tmp_divisions.sort_values(by=[other_param])
#                         fig, ax = plt.subplots(1, 1, figsize=(15,10))
#                         ax.hist([tmp_deaths[tmp_deaths[other_param]==x]["time"] for x in tmp_deaths[other_param].unique()],
#                             label=tmp_deaths[other_param].unique())
#                         ax.set_ylabel('#deaths')
#                         ax.set_xlabel('time')
#                         ax.legend(title=other_param)
#                         ax.set_title("deaths over time for "+k+" "+str(unique_value)+" "+celltype)
#                         fig.tight_layout()
#                         fig.savefig(folder+'/processing/deaths_births/death_time_'+k+"_"+str(unique_value)+'_'+celltype+'.png')
#                         plt.close(fig)

#                         fig, ax = plt.subplots(1, 1, figsize=(15,10))
#                         ax.hist([tmp_divisions[tmp_divisions[other_param]==x]["time"] for x in tmp_divisions[other_param].unique()],
#                             label=tmp_divisions[other_param].unique())
#                         ax.set_ylabel('#births')
#                         ax.set_xlabel('time')
#                         ax.legend(title=other_param)
#                         ax.set_title("divisions over time for "+k+" "+str(unique_value))
#                         fig.tight_layout()
#                         fig.savefig(folder+'/processing/deaths_births/birth_time_'+k+"_"+str(unique_value)+'.png')
#                         plt.close(fig)