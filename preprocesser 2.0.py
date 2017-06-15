# -*- coding: utf-8 -*-
"""
Created on Tue Dec 20 19:14:51 2016

@author: MiguelYuste
"""

#C:\Users\migue\Documents\UC3M\TU Graz\Bachelor thesis\Data\despacho_liencres.csv
#import glob
import sys
import os
#import tempfile
#import csv
import pandas as pd
import numpy as np
import multiprocessing
#import threading
from functools import partial


def removeIncomplete (timestamp, instances):
    with open('{}.out'.format(os.getpid()), 'w') as fp:
        sys.stdout = fp
        sys.stderr = fp
        toremove = []
    
    
        _len = len(timestamp)
        for idx, i in enumerate(timestamp):
            inst = instances[instances['TIME'] == i]
            if len(inst) != 13:
                toremove += inst.index.tolist()
            if idx%10 == 0:
                print("{}/{}".format(idx, _len))
                sys.stdout.flush()
    return toremove

def toSteps(inst, step):
    data = np.round(np.array(inst, dtype=float)/ step) * step
    return  pd.DataFrame(data)

if __name__ == '__main__':
    #path = raw_input("Please, write the path to the CSV file \n")
    path = r"C:\Users\migue\Documents\UC3M\TU Graz\Bachelor thesis\Data\despacho_liencres - copia.csv"

    # read CSV file and store it
    instances = pd.read_csv(path, sep=';')

    print("Rows before preprocessing: {}".format(len(instances)))

    # drop useless columns
    del instances['UID']
    del instances['NAME']
    del instances['UNIT']
    
    print("Step 2: {}".format(len(instances)))

    # remove sensor data we dont need
    instances = instances[instances['VAR'] != "Chip Temperature"]
    instances = instances[instances['VAR'] != "Stack Current"]
    instances = instances[instances['VAR'] != "Stack Voltage"]

    print("Step 3: {}".format(len(instances)))
    
    instances['RAW'] = instances['RAW'].replace('^ERROR.*$', np.nan, regex=True)
    instances = instances.dropna()

    print("Step 4: {}".format(len(instances)))
    
    transf = pd.DataFrame()
    instances['RAW'][instances['VAR'] == "Temperature" & instances['VAR'].len() == 4] /= 100
    for i in instances['RAW'][instances['VAR'] == "Temperature"]:
         if len(i) == 4:
             i = float(i)/100
         transf.add(i)
    instances['RAW'][instances['VAR'] == "Temperature"] = transf
    # round values to nearest step
    haha = toSteps(instances['RAW'][instances['VAR'] == "Temperature"], 0.5)
    haha.to_csv(r"C:\Users\migue\Documents\UC3M\TU Graz\Bachelor thesis\Data\haha.csv", sep=';')

    # we need complete instants (with all sensors)
    timestamp = instances.TIME.unique()

    split = np.array_split(timestamp, multiprocessing.cpu_count())
    print(len(split))
    pool = multiprocessing.Pool()
    the_partial = partial(removeIncomplete, instances=instances)
    #the_partial = partial(removeIncomplete, instances.copy())

    indexes_to_remove = []
    for rem_list in pool.map(the_partial, split):
        indexes_to_remove += rem_list
    pool.close()
    instances.drop(indexes_to_remove, inplace=True)
    print("Step 5: {}".format(len(instances)))
    

    instances.to_csv(r"despacho_liencres_out_PRUEBA.csv", sep=';')

    print("Rows after preprocessing: {}".format(len(instances)))