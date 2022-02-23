#!/usr/bin/env python3

import shutil
import os
import sys
import subprocess

expdir = sys.argv[1]
prefix1 = "Mitochondria-fraction_unmutated-t"
prefix2 = "Mitochondria-n_DNA-t"
prefix3 = "Mitochondria-oxphos_avg-t"
extension = "png"

for sourcedir in os.listdir(expdir):
    sourcedir =  expdir + '/' + sourcedir + '/'
    try:
        os.mkdir(sourcedir+"/"+prefix1)
        os.mkdir(sourcedir+"/"+prefix2)
        os.mkdir(sourcedir+"/"+prefix3)
    
        for f in os.listdir(sourcedir):
            if f.startswith(prefix1) and f.endswith(extension):
                shutil.move(sourcedir+f,sourcedir+prefix1+"/"+f)
            if f.startswith(prefix2) and f.endswith(extension):
                shutil.move(sourcedir+f,sourcedir+prefix2+"/"+f)
            if f.startswith(prefix3) and f.endswith(extension):
                shutil.move(sourcedir+f,sourcedir+prefix3+"/"+f)

        files1 = [(f, f[f.rfind("."):], f[:f.rfind(".")].replace(prefix1, "")) for f in os.listdir(sourcedir+"/"+prefix1) if f.endswith(extension)]
        maxlen1 = len(max([f[2] for f in files1], key = len))
        files2 = [(f, f[f.rfind("."):], f[:f.rfind(".")].replace(prefix2, "")) for f in os.listdir(sourcedir+"/"+prefix2) if f.endswith(extension)]
        maxlen2 = len(max([f[2] for f in files2], key = len))
        files3 = [(f, f[f.rfind("."):], f[:f.rfind(".")].replace(prefix3, "")) for f in os.listdir(sourcedir+"/"+prefix3) if f.endswith(extension)]
        maxlen3 = len(max([f[2] for f in files3], key = len))
    except:
        files1, files2, files3 = [], [], []
        pass


    for item in files1:
        zeros = maxlen1 - len(item[2])
        shutil.move(sourcedir+"/"+prefix1+"/"+item[0], sourcedir+"/"+prefix1+"/"+prefix1+str(zeros*"0"+item[2])+item[1])
    for item in files2:
        zeros = maxlen2 - len(item[2])
        shutil.move(sourcedir+"/"+prefix2+"/"+item[0], sourcedir+"/"+prefix2+"/"+prefix2+str(zeros*"0"+item[2])+item[1])
    for item in files3:
        zeros = maxlen3 - len(item[2])
        shutil.move(sourcedir+"/"+prefix3+"/"+item[0], sourcedir+"/"+prefix3+"/"+prefix3+str(zeros*"0"+item[2])+item[1])
    try:
        os.chdir(sourcedir)
        print(os.getcwd())
        subprocess.run('../../make_videos.sh')
        os.chdir('../../')
    except:
        pass
