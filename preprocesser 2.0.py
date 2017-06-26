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
import time


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
    return inst.apply(lambda x : ((np.round(float(x) / step)) * step))

if __name__ == '__main__':
    start = time.time()
    #path = raw_input("Please, write the path to the CSV file \n")
    path = r"C:\Users\migue\Documents\UC3M\TU Graz\Bachelor thesis\Data\despacho_liencres - copia.csv"

    # read CSV file and store it
    instances = pd.read_csv(path, sep=';')

    print("Rows before preprocessing: {}".format(len(instances)))

    # drop useless columns
    del instances['UID']
    # removing accelerometer temperature readings before we delete the NAME column, which we dont need
    instances = instances[np.logical_not(np.logical_and(instances['VAR'] == "Temperature", instances['NAME'] == "Accelerometer Bricklet"))]
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

    # ERROR: dataframe is still string despite conversion
    # DISCRETISATION
    # discretise temperature data by rounding in steps of 0.5 degrees
    instances['RAW'][instances['VAR'] == "Temperature"] = instances['RAW'][instances['VAR'] == "Temperature"].apply(float)
    instances['RAW'][instances['VAR'] == "Temperature"] /= 100.0
    instances['RAW'][instances['VAR'] == "Temperature"] = toSteps(instances['RAW'][instances['VAR'] == "Temperature"], 0.5)
    # discretise illuminance data by rounding in steps of 1 lux
    instances['RAW'][instances['VAR'] == "Illuminance"] = toSteps(instances['RAW'][instances['VAR'] == "Illuminance"], 100)
    # discretise sound intensity data by rounding in steps of 5 units (upper envelope value)
    instances['RAW'][instances['VAR'] == "Intensity"] = toSteps(instances['RAW'][instances['VAR'] == "Intensity"], 5)
    # discretise humidity data by rounding in steps of 5 units (% of relative humidity)
    instances['RAW'][instances['VAR'] == "Humidity"] = instances['RAW'][instances['VAR'] == "Humidity"].apply(float)
    instances['RAW'][instances['VAR'] == "Humidity"] *= 10.0
    instances['RAW'][instances['VAR'] == "Humidity"] = toSteps(instances['RAW'][instances['VAR'] == "Humidity"], 5)
    # discretise CO2 data by rounding in steps of 50 ppm
    instances['RAW'][instances['VAR'] == "CO2 Concentration"] = toSteps(instances['RAW'][instances['VAR'] == "CO2 Concentration"], 50)
    # discretise air pressure data by rounding in steps of 500 mbar/1000
    instances['RAW'][instances['VAR'] == "Air Pressure"] = toSteps(instances['RAW'][instances['VAR'] == "Air Pressure"], 500)
    # discretise air pressure data by rounding in steps of 500 mbar/1000
    instances['RAW'][instances['VAR'] == "Air Pressure"] = toSteps(instances['RAW'][instances['VAR'] == "Air Pressure"], 500)
    # there is no need to standardise accelerometer data, the variations are too small
    # same for movement detection, as it can either be 0 or 1

    # we need complete instants (with all sensors)
    timestamp = instances.TIME.unique()

    split = np.array_split(timestamp, multiprocessing.cpu_count())
    #print(len(split))
    pool = multiprocessing.Pool()
    the_partial = partial(removeIncomplete, instances=instances)
    #the_partial = partial(removeIncomplete, instances.copy())

    indexes_to_remove = []
    for rem_list in pool.map(the_partial, split):
        indexes_to_remove += rem_list
    pool.close()
    instances.drop(indexes_to_remove, inplace=True)
    print("Step 5: {}".format(len(instances)))
    

    instances.to_csv(r"preprocessing_out.csv", sep=';')

    print("Rows after preprocessing: {}".format(len(instances)))
    end = time.time()
    print("Time elapsed: %f" %(end - start))