import pandas as pd
import sys, os
import matplotlib.pyplot as plt

folder = sys.argv[1]

if not os.path.isdir(folder+'/processing/'):
    print('The directory is not present. Creating a new one..')
    os.mkdir(folder+'/processing/')

victories = []
for f in os.listdir(folder):
    try:
        ifs = open('./'+folder+'/'+f+'/competition.txt')
        line = ifs.readline()
        line = ifs.readline()
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
