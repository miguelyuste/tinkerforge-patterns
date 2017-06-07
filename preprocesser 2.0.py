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
    sys.stdout = open('{}.stdout'.format(os.getpid()), 'w')
    sys.stderr = open('{}.stderr'.format(os.getpid()), 'w')
    toremove = []
#    for i in multiprocessing.cpu_count():
#        i[]:
    _len = len(timestamp)
    for idx, i in enumerate(timestamp):
        instant = instances[instances['TIME'] == i]
        if len(instant) != 13:
            toremove.append(instant)
        if idx%100 == 0:
            print("{}/{}".format(idx, _len))
            sys.stdout.flush()
    return toremove

if __name__ == '__main__':
    #path = raw_input("Please, write the path to the CSV file \n")
    path = r"C:\Users\migue\Documents\UC3M\TU Graz\Bachelor thesis\Data\despacho_liencres.csv"

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

    # we need complete instants (with all sensors)
    timestamp = instances.TIME.unique()

    #split = np.array_split(timestamp, multiprocessing.cpu_count())
    #print(len(split))
    #pool = multiprocessing.Pool()
    #the_partial = partial(removeIncomplete, instances=instances)

    #to_remove = pool.map(the_partial, split)
    #print(to_remove)

    dict = {}

    for i in instances:
        dict.setdefault(i['TIME'], []).append(i.index())
    print dict
    #for key in dict:
            

    instances.to_csv(path=r"C:\Users\migue\Documents\UC3M\TU Graz\Bachelor thesis\Data\despacho_liencres_out.csv", mode='w+')

    print("Rows after preprocessing: {}".format(len(instances)))