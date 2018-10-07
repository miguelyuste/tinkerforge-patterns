#!/usr/bin/python

import pandas as pd
import pyfpgrowth as fpg
import time
import csv
from collections import OrderedDict

def writeOutput(patterns, path):
    f_aux = open(path, "wb")
    w = csv.writer(f_aux)
    for key, val in patterns.items():
        w.writerow([key, val])
    f_aux.close()
  
def find_patterns(i, path, output_path):
    start = time.time()
    print("Miner initialising...")
    # read CSV file and store it
    instances = pd.read_csv(path, sep=';')
    
    
    while True:
        print("Please select the sensors you want to analyse, separated by commas.")
        # excluding accelerometer temperature readings
        print("Possibilities: all, motion, light, sound, temperature, humidity, co2, pressure, acceleration, altitude")
        aux = raw_input().split(",")
        if (len(aux) < 2) & (aux[0].lower() != "all"):
            print("Please choose at least two sensors.")
        else: 
            break
    idx = 0
    for i in aux:
        aux[idx] = i.lower().replace(" ", "")
        idx += 1
    
    #remove index column imported from preprocessed CSV
    instances[instances.columns[1:]]   

    sensors = ["Motion Detected","Illuminance","Intensity","Temperature","Humidity","CO2 Concentration","Air Pressure","Acceleration-X","Acceleration-Y","Acceleration-Z","Altitude"]
    chosenSensors = []
    for sensor in aux:
        if sensor == "all":
            chosenSensors.extend(("Motion Detected","Illuminance","Intensity","Temperature","Humidity","CO2 Concentration","Air Pressure","Acceleration-X","Acceleration-Y","Acceleration-Z","Altitude"))
        elif sensor == 'motion':
            chosenSensors.append("Motion Detected")
        elif sensor == 'light':
            chosenSensors.append("Illuminance")
        elif sensor == 'sound':
            chosenSensors.append("Intensity")
        elif sensor == 'temperature':
            chosenSensors.append("Temperature")
        elif sensor == 'humidity':
            chosenSensors.append("Humidity")
        elif sensor == 'co2':
            chosenSensors.append("CO2 Concentration")
        elif sensor == 'pressure':
            chosenSensors.append("Air Pressure")
        elif sensor == 'acceleration':
            chosenSensors.extend(("Acceleration-X","Acceleration-Y","Acceleration-Z"))
        elif sensor == 'altitude':
            chosenSensors.append("Altitude")
    
    #get support levels from user. currently using same support level for pattern and rule detection,
    #additional code needed to get separate values from both from the user
    while True:
        minsup_fp = raw_input("Please, specify the support level to use in the frequent pattern detection \n") 
        if not (minsup_fp.isdigit()):
            print("Please specify a number.")
        else:
            minsup_fr = minsup_fp = int(float(minsup_fp))
            break
        
    while True:
        minsup_sp = raw_input("Please, specify the support level to use in the surprising pattern detection \n")
        if not (minsup_sp.isdigit()):
            print("Please specify a number.")
        else: 
            minsup_sr = minsup_sp = int(float(minsup_sp))
            break
    
    #remove sensors we dont need
    notChosen = [item for item in sensors if item not in chosenSensors]
    for j in notChosen:
        instances = instances[instances['VAR'] != j]
    sensors = ', '.join(chosenSensors)
    print("\nRunning miner with the following sensors: %s \n" % sensors)
    
    ############### FREQUENT PATTERN DETECTION ###############
    print("Frequent pattern mining running...")
    inst_fp = instances.copy()
    for k in chosenSensors:
        # number of rows of the current sensor
        num_instances = len(inst_fp[inst_fp.VAR==k])
        # we dont wanna filter out the rare motion detections
        if k!='Motion Detected':
            bins = inst_fp['RAW'][inst_fp['VAR'] == k].unique()
            # remove bins that contain less than 5% of the instances of the sensor
            for x in set(bins):
                if inst_fp['RAW'][(inst_fp.VAR == k) & (inst_fp.RAW == x)].count() < (num_instances*0.05):
                    inst_fp[inst_fp.VAR == k] = inst_fp[(inst_fp.VAR == k) & (inst_fp.RAW != x)]
    #eliminate instants left incomplete
    inst_fp = inst_fp.groupby(['TIME']).filter(lambda time_instant : len(time_instant) == len(chosenSensors))
    #we dont need the VAR column anymore
    del inst_fp['VAR']
    # input data for FP-Growth must be immutable
    inst_fp = tuple(inst_fp.groupby('TIME')['RAW'].apply(tuple))
    # find patterns, rules and write them to output files
    patterns = fpg.find_frequent_patterns(inst_fp, minsup_fp)
    
    # sort patterns in descending frequency order
    patterns = sorted(patterns.items(), key=lambda x: x[1], reverse=True)
    _tmp = OrderedDict()
    for k,v in patterns:
        _tmp[k] = v
        
    patterns = _tmp
    no_fp = len(patterns)
    print("%i frequent patterns were found" % no_fp)
    f_freq_pat = output_path + ("\\frequent_patterns_%i.csv" % idx)
    writeOutput(patterns, f_freq_pat)
    rules = fpg.generate_association_rules(patterns, minsup_fr)
    
    # sort rules in descending frequency order
    rules = sorted(rules.items(), key=lambda x: x[1], reverse=True)
    _tmp = OrderedDict()
    for k,v in rules:
        _tmp[k] = v
        
    rules = _tmp
    no_fr = len(rules)
    print("%i frequent pattern association rules were found" % no_fr)
    f_freq_rules = output_path + ("\\frequent_rules_%i.csv" % idx)
    writeOutput(rules, f_freq_rules)
    print("Frequent pattern mining done")


    ############### SURPRISING PATTERN DETECTION ###############
    print("Surprising pattern mining running...")
    inst_sp = instances.copy()
    for i in chosenSensors:
        # number of rows of the current sensor
        num_instances = len(inst_sp[inst_sp.VAR==i])
        # we dont wanna filter out the rare motion detections
        if i!='Motion Detected':
            bins = inst_sp['RAW'][inst_sp['VAR'] == i].unique()
            # remove bins that contain more than 5% of the instances of the sensor
            for x in set(bins):
                if inst_sp['RAW'][(inst_sp.VAR == i) & (inst_sp.RAW == x)].count() > (num_instances*0.05):
                    inst_sp[inst_sp.VAR == i] = inst_sp[(inst_sp.VAR == i) & (inst_sp.RAW != x)]
    #eliminate instants left incomplete
    inst_sp = inst_sp.groupby(['TIME']).filter(lambda time_instant : len(time_instant) == len(chosenSensors))
    #we dont need the VAR column anymore
    del inst_sp['VAR']
    # input data for FP-Growth must be immutable
    inst_sp = tuple(inst_sp.groupby('TIME')['RAW'].apply(tuple))
    # find patterns, rules and write them to output files
    patterns = fpg.find_frequent_patterns(inst_sp, minsup_sp)
    
    # sort patterns in descending frequency order
    patterns = sorted(patterns.items(), key=lambda x: x[1], reverse=True)
    _tmp = OrderedDict()
    for k,v in patterns:
        _tmp[k] = v
        
    patterns = _tmp
    no_sp = len(patterns)
    print("%i surprising patterns were found" % no_sp)
    f_freq_pat = output_path + ("\\surprising_patterns_%i.csv" % idx)
    writeOutput(patterns, f_freq_pat)
    rules = fpg.generate_association_rules(patterns, minsup_sr)
    
    # sort rules in descending frequency order
    rules = sorted(rules.items(), key=lambda x: x[1], reverse=True)
    _tmp = OrderedDict()
    for k,v in rules:
        _tmp[k] = v
        
    rules = _tmp
    no_sr = len(rules)
    print("%i surprising pattern association rules were found" % no_sr)
    f_freq_rules = output_path + ("\\surprising_rules_%i.csv" % idx)
    writeOutput(rules, f_freq_rules)
    print("Surprising pattern mining done")

    ############### FINAL STEPS ###############
    end = time.time()
    print("**PATTERN MINING DONE**\n")
    results = "Time elapsed in mining: %f seconds \n" %(end - start)
    print (results)
    results += "%i sensors used: %s \n" % (len(chosenSensors), sensors)
    results += "Number of frequent patterns found: %i \n" % no_fp
    results += "Number of frequent pattern association rules found: %i \n" % no_fr
    results += "Number of surprising patterns found: %i \n" % no_sp
    results += "Number of surprising pattern association rules found: %i \n" % no_sr
    results += "Minimum support for frequent pattern mining: %i \n" %minsup_fp
    results += "Minimum support for frequent pattern association rules mining: %i \n" %minsup_fr
    results += "Minimum support for surprising pattern mining: %i \n" %minsup_sp
    results += "Minimum support for surprising pattern association rules mining: %i \n" %minsup_sr
    return results