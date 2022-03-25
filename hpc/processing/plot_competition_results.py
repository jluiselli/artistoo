import pandas as pd
import sys, os
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

folder = sys.argv[1]

if not os.path.isdir(folder+'/processing/'):
    print('The directory is not present. Creating a new one..')
    os.mkdir(folder+'/processing/')

victories = []
for f in os.listdir(folder):
    try:
        ifs = open('./'+folder+'/'+f+'/competition.txt')
        line = ifs.readline()
        print(line)
        line = ifs.readline()
        print(line)
        victories += [int(line)]
        ifs.close()

    except:
        print("reading error for "+f)



fig, ax = plt.subplots(1, 1, figsize=(15,10))

ax.hist(victories)

ax.set_ylabel(col)
ax.set_xlabel('Winner')
ax.set_title("Nb of wins for each strain")

fig.tight_layout()
fig.savefig(folder+'/processing/competition_results.png')
plt.close(fig)


if os.path.exists(folder+'/competition_time.csv'):
    df = pd.read_csv(folder+'/competition_time.csv')
else:
    print("creating df")
    df = pd.DataFrame()
    for f in os.listdir(folder):
        print(f)
        k = f.replace('/',' ').split('-')
        i = iter(k)
        params = dict(zip(i,i))

        print(params)
        try:
            tmp = []

            ifs = open('./'+folder+'/'+f+'/competition_log.txt')
            line = ifs.readline()
            

            while line:
                print(line)
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
        
        df = pd.concat([df, tmp_df], sort=False)
    
    df.to_csv(folder+'/competition_time.csv')


print(df.shape)
# df = df.sample(frac=0.002) # Otherwise too long to plot
df["seed"] = df["seed"].astype(str) # To get categorical in hue color

fig, ax = plt.subplots(1, 1, figsize=(15,10))
sns.lineplot(data=df, x='time',y='prop_1', hue='seed', ax=ax, linewidth=3)
ax.set_ylim(0,1)
ax.axhline(y=0.5, color='grey')
fig.tight_layout()
fig.savefig(folder+'/processing/competition_time.png')
plt.close(fig)

