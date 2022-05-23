import pandas as pd
import sys, os
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

folder = sys.argv[1]

if not os.path.isdir(folder+'/processing/'):
    print('The directory is not present. Creating a new one..')
    os.mkdir(folder+'/processing/')

# victories = []
# for f in os.listdir(folder):
#     try:
#         ifs = open('./'+folder+'/'+f+'/competition.txt')
#         line = ifs.readline()
#         print(line)
#         line = ifs.readline()
#         print(line)
#         victories += [int(line)]
#         ifs.close()
#         print(f+" completed")

#     except:
#         print("reading error for "+f)



# fig, ax = plt.subplots(1, 1, figsize=(15,10))

# ax.hist(victories)

# ax.set_xlabel('Winner')
# ax.set_title("Nb of wins for each strain")

# fig.tight_layout()
# fig.savefig(folder+'/processing/competition_results.png')
# plt.close(fig)


if os.path.exists(folder+'/competition_time.csv'):
    df = pd.read_csv(folder+'/competition_time.csv')
else:
    print("creating df")
    df = pd.DataFrame()
    for f in os.listdir(folder):
        print(f)
        k = f.replace('/',' ').split('-')
        if k[0]!='seed':
            continue
        k = k[:8]+k[9:]
        i = 0
        while i < len(k):
            try:
                if k[i][-2:]=='1e' or k[i][-2:]=='5e' or k[i][-2:]=='2e'  or k[i][-2:]=='3e' or k[i][-2:]=='4e'  or k[i][-2:]=='6e'  or k[i][-2:]=='7e'  or k[i][-2:]=='8e' or k[i][-2:]=='9e': #For degenerated cases of rates
                    k[i] = k[i]+ '-' + k[i+1]
                    if i < len(k)-2:
                        k = k[:i+1]+k[i+2:]
                    i=0
                    continue
            except:
                pass
            i+=1
        i = iter(k)
        params = dict(zip(i,i))

        print(params)
        try:
            tmp = []

            ifs = open('./'+folder+'/'+f+'/competition_log.txt')
            line = ifs.readline()
            

            while line:
                time, distr = line.split(";")
                ones = np.char.count([str(distr)], "1")[0]
                twos = np.char.count([str(distr)], "2")[0]
                prop_1 = ones/(ones+twos)

                tmp += [[time,ones,prop_1]]
            
                line = ifs.readline()
            
            ifs.close()

            tmp_df = pd.DataFrame(tmp, columns=["time","ones","prop_1"])

            for p in params:
                tmp_df[p] = params[p]

        except:
            print("reading error for "+f)
            tmp_df = pd.DataFrame()
        
        print(tmp_df.shape)
        df = pd.concat([df, tmp_df], sort=False)
    
    df.to_csv(folder+'/competition_time.csv')


print(df.shape)
df = df.sample(frac=0.5) # Otherwise too long to plot
df["seed"] = df["seed"].astype(str) # To get categorical in hue color
# df["ncells"] = df["ones"]*100/df["prop_1"]

print(df)

fig, ax = plt.subplots(1, 1, figsize=(15,10))
sns.lineplot(data=df, x='time',y='prop_1', hue='seed', ax=ax, linewidth=3)
# ax2 = ax.twinx()
# sns.lineplot(data=df, x='time',y='ncells', hue='seed', ax=ax2, linewidth=3)
ax.set_ylim(0,1)
ax.axhline(y=0.5, color='grey')
fig.tight_layout()
fig.savefig(folder+'/processing/competition_time.png')
plt.close(fig)

