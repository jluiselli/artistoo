#!/usr/bin/env python
# encoding=utf8

import os, time
import shutil
from execo import logger as ex_log
from execo_engine import Engine, logger, ParamSweeper, sweep, slugify
import random

class mito_matrix(Engine):
    def run(self):
        """ """
        self.define_parameters()
	
        self.working_dir = '/home/jluiselli/Documents/Cours/utrecht/artistoo/hpc/testing_execo/'
        self.template_param_file = self.working_dir+'../config.js.tpl'

        comb = self.sweeper.get_next()
        while comb != None:
            self.workflow(comb)
            comb = self.sweeper.get_next()


    def define_parameters(self):
        """ """
        n = 1
        seeds = []
        for i in range(n):
            seeds += [random.randint(0,10000)]
        parameters = {
            'seed' : seeds,
        #   'seed' : [1579374282,  475373665, 9990631808, 5893536182, 8895015748,
       	# 		7748158497, 7208666090, 8603824805, 8613560671, 1024314629,
        #         1593625377,  343447143, 1198463043, 4953505017,  526184103,
       	# 		6818153527, 1782071352, 8199255165, 9379524478, 4115706337],
          'NDNA_MUT_LIFETIME' : [0, 0.000001, 0.000005, 0.00001],
        }
        sweeps = sweep(parameters)
        self.sweeper = ParamSweeper(os.path.join(self.result_dir, "sweeps"), sweeps)
        logger.info('Number of parameters combinations %s', len(self.sweeper.get_remaining()))


    def write_param_file(self, comb, bucketname):
        param_file = bucketname+'/config.js'
        
        f_template = open(self.template_param_file)
        f = open(param_file, 'w')
        
        for line in f_template:
            line = line.replace('SEED_NUMBER',str(comb['seed']))
            line = line.replace('NDNA_MUT_LIFETIME_PARAM',str(comb['NDNA_MUT_LIFETIME']))
            f.write(line)
 
        f_template.close()
        f.close()      

    def workflow(self, comb):
        """ """
        bucketname = self.working_dir+'/'+slugify(comb)+'/'
        print(bucketname)
        
        # If directory is empty
        if not os.path.isdir(bucketname):
            os.mkdir(bucketname)
  
        # Generate param file
        self.write_param_file(comb,bucketname)
        
        time.sleep(3)

        os.chdir(bucketname)
        os.system('../../run_and_make_video.sh &')
        os.chdir('..')
         

if __name__ == "__main__":
    engine = mito_matrix()
    engine.start()
