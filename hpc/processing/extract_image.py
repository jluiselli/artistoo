import sys, os, shutil

folder = sys.argv[1]
gener = sys.argv[2]
subfolders = sys.argv[3:]

if subfolders == []:
    subfolders = [i for i in os.listdir(folder) if i[:4]=='seed']

if not os.path.isdir(folder+'/processing/'):
    print('The directory processing is not present. Creating a new one..')
    os.mkdir(folder+'/processing/')

for subfolder in subfolders:
    print(subfolder)
    if not os.path.isdir(folder+'/processing/'+subfolder):
        print('The directory for this run is not present. Creating a new one..')
        os.mkdir(folder+'/processing/'+subfolder)

    
    try:
        shutil.copy(folder+'/'+subfolder+'/Mitochondria-n_DNA-t'+gener+'.png',
            folder+'/processing/'+subfolder+'/Mitochondria-n_DNA-t'+gener+'.png')
        shutil.copy(folder+'/'+subfolder+'/Mitochondria-oxphos_avg-t'+gener+'.png',
            folder+'/processing/'+subfolder+'/Mitochondria-oxphos_avg-t'+gener+'.png')
        shutil.copy(folder+'/'+subfolder+'/Mitochondria-fraction_unmutated-t'+gener+'.png',
            folder+'/processing/'+subfolder+'/Mitochondria-fraction_unmutated-t'+gener+'.png')
    except:
        print("no image at this generation, retrieving the most advanced one")
        try:
            M=0
            for f in os.listdir(folder+'/'+subfolder):
                if f[-3:]=='png':
                    f = f.split('.')[0].split('-')[-1]
                    n = int(f[1:])
                    if n>M:
                        M=n
            shutil.copy(folder+'/'+subfolder+'/Mitochondria-n_DNA-t'+str(M)+'.png',
                folder+'/processing/'+subfolder+'/Mitochondria-n_DNA-t'+str(M)+'.png')
            shutil.copy(folder+'/'+subfolder+'/Mitochondria-oxphos_avg-t'+str(M)+'.png',
                folder+'/processing/'+subfolder+'/Mitochondria-oxphos_avg-t'+str(M)+'.png')
            shutil.copy(folder+'/'+subfolder+'/Mitochondria-fraction_unmutated-t'+str(M)+'.png',
                folder+'/processing/'+subfolder+'/Mitochondria-fraction_unmutated-t'+str(M)+'.png')  
            print("successful")
        
        except:
            print("no images here. Movie already done ?")
            try:
                shutil.copy(folder+'/'+subfolder+'/video_all.mp4',
                folder+'/processing/'+subfolder+'/video_all.mp4')
                print("successful !")
            except:
                print("error, no images nor movies for ", subfolder)
