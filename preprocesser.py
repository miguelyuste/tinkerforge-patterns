# -*- coding: utf-8 -*-
#!/usr/bin/python

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


def prep(i, path, output_path):
    start = time.time()
    print("Preprocessing module initialising...")

    # read CSV file and store it
    instances = pd.read_csv(path, sep=';')

    # create output file
    #i = 0
    #while os.path.exists(output_path + ("\\preprocessing_results_%i.csv" % i)):
    #    i += 1
    path_out = output_path + ("\\preprocessing_results_%i.csv" % i)
    out = open(path_out, "wb")
   
    rows_before = len(instances)
    results = "Rows before preprocessing: %i\n" % rows_before
    print(results)
    
    ### UNNECESSARY AND ERRONEOUS DATA REMOVAL ##
    print("Removing unnecessary and erroneous data...")
    # drop useless columns
    del instances['UID']
    # removing accelerometer temperature readings before we delete the NAME column, which we dont need
    instances = instances[np.logical_not(np.logical_and(instances['VAR'] == "Temperature", instances['NAME'] == "Accelerometer Bricklet"))]
    del instances['NAME']
    del instances['UNIT']

    # remove sensor data we dont need
    instances = instances[instances['VAR'] != "Chip Temperature"]
    instances = instances[instances['VAR'] != "Stack Current"]
    instances = instances[instances['VAR'] != "Stack Voltage"]
    instances = instances[instances['VAR'] != "Analog Value"]
    
    # remove erroneous readings
    instances['RAW'] = instances['RAW'].replace('^ERROR.*$', np.nan, regex=True)
    instances = instances.dropna()
    
    ### DISCRETISATION & BINNING ### 
    print("Binning process running...")
    
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
    
    print("Binning process done")

    # we need complete instants (with all sensors)
    print("Eliminating incomplete instants...")
    instances = instances.groupby(['TIME']).filter(lambda time_instant : len(time_instant) == 11)
    print("Elimination complete. Writing results to output file...")
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
    #instances.drop(instances.index[0], axis = 1)
    
    ### FINAL STEPS ###
    # write results to output file
    instances.to_csv(out, sep=';')
    out.close()
    end = time.time()

    # INFO FOR LOG 
    # remaining rows
    rows_after = len(instances)
    print("Preprocessing done. \nRows after preprocessing: %i" % rows_after)
    results += "Rows after preprocessing: %i \n" % rows_after
    
    # discarded rows
    discarded_rows = rows_before - rows_after
    discarded = "Rows discarded: %i \n" % discarded_rows
    print discarded 
    results += discarded
    
    # elapsed time
    elapsed = "Time elapsed in preprocessing: %f seconds \n" %(end - start)
    print elapsed
    results += elapsed
    
    return {'results':results, 'path_out':path_out}