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
    #sys.stdout = open('{}.stdout'.format(os.getpid()), 'w')
    #sys.stderr = open('{}.stderr'.format(os.getpid()), 'w')
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

def toSteps(inst, var, step):
    # round to nearest 'step' step and concatenates the name of the sensor and the result
    return inst.apply(lambda x : (var + " " + str((np.round(float(x) / step)) * step)))

if __name__ == '__main__':
    start = time.time()
    #path = raw_input("Please, write the path to the CSV file \n")
    path = r"C:\Users\migue\Documents\TFG\despacho_liencres.csv"

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
    instances = instances[instances['VAR'] != "Analog Value"]

    print("Step 3: {}".format(len(instances)))
    
    instances['RAW'] = instances['RAW'].replace('^ERROR.*$', np.nan, regex=True)
    instances = instances.dropna()

    print("Step 4: {}".format(len(instances)))

    
    # DISCRETISATION & BINNING 
    # discretise data by steps, and finish binning by adding the name of the sensor
    # discretise temperature data by rounding in steps of 0.5 degrees
    instances['RAW'][instances['VAR'] == "Temperature"] = instances['RAW'][instances['VAR'] == "Temperature"].apply(float)
    instances['RAW'][instances['VAR'] == "Temperature"] /= 100.0
    instances['RAW'][instances['VAR'] == "Temperature"] = toSteps(instances['RAW'][instances['VAR'] == "Temperature"], "Temperature", 0.5)
    # discretise illuminance data by rounding in steps of 1 lux
    instances['RAW'][instances['VAR'] == "Illuminance"] = toSteps(instances['RAW'][instances['VAR'] == "Illuminance"], "Illuminance", 100)
    # discretise sound intensity data by rounding in steps of 5 units (upper envelop value)
    instances['RAW'][instances['VAR'] == "Intensity"] = toSteps(instances['RAW'][instances['VAR'] == "Intensity"], "Intensity", 5)
    # discretise humidity data by rounding in steps of 5 units (% of relative humidity)
    instances['RAW'][instances['VAR'] == "Humidity"] = instances['RAW'][instances['VAR'] == "Humidity"].apply(float)
    instances['RAW'][instances['VAR'] == "Humidity"] *= 10.0
    instances['RAW'][instances['VAR'] == "Humidity"] = toSteps(instances['RAW'][instances['VAR'] == "Humidity"], "Humidity", 5)
    # discretise CO2 data by rounding in steps of 50 ppm
    instances['RAW'][instances['VAR'] == "CO2 Concentration"] = toSteps(instances['RAW'][instances['VAR'] == "CO2 Concentration"], "CO2 Concentration", 50)
    # discretise air pressure data by rounding in steps of 0.5 mbar (500 mbar/1000)
    instances['RAW'][instances['VAR'] == "Air Pressure"] = toSteps(instances['RAW'][instances['VAR'] == "Air Pressure"], "Air Pressure", 500)
    # discretise acceleration data by rounding in steps of 5 grams
    instances['RAW'][instances['VAR'] == "Acceleration-X"] = toSteps(instances['RAW'][instances['VAR'] == "Acceleration-X"], "Acceleration-X", 5)
    instances['RAW'][instances['VAR'] == "Acceleration-Y"] = toSteps(instances['RAW'][instances['VAR'] == "Acceleration-Y"], "Acceleration-Y", 5)
    instances['RAW'][instances['VAR'] == "Acceleration-Z"] = toSteps(instances['RAW'][instances['VAR'] == "Acceleration-Z"], "Acceleration-Z", 5)
    # generate valid binary steps for the motion detector data
    instances['RAW'][instances['VAR'] == "Motion Detected"] = toSteps(instances['RAW'][instances['VAR'] == "Motion Detected"], "Motion Detected", 1)
    # discretise altitude data by rounding in steps of 10m
    instances['RAW'][instances['VAR'] == "Altitude"] = toSteps(instances['RAW'][instances['VAR'] == "Altitude"], "Altitude", 1000)

    # we need complete instants (with all sensors)
    instances = instances.groupby(['TIME']).filter(lambda time_instant : len(time_instant) == 11)
    #timestamp = instances.TIME.unique()

    #split = np.array_split(timestamp, multiprocessing.cpu_count())
    #print(len(split))
    #pool = multiprocessing.Pool()
    #the_partial = partial(removeIncomplete, instances=instances)

    #to_remove = pool.map(the_partial, split)
    #print(to_remove)

    #dict = {}

    #for i in instances:
        #dict.setdefault(i['TIME'], []).append(i.index())
    #print dict
    #for key in dict:
    instances.drop(instances.index[0], axis = 1)
    print("Step 5: {}".format(len(instances)))
    

    instances.to_csv(r"C:\Users\migue\Documents\TFG\prep_nuevo.csv", sep=';')

    print("Rows after preprocessing: {}".format(len(instances)))
    end = time.time()
    print("Time elapsed: %f" %(end - start))