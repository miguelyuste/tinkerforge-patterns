#C:\Users\migue\Documents\UC3M\TU Graz\Bachelor thesis\Data\ct_meeting_6.2.csv

import pandas as pd
import pyfpgrowth as fpg
import time
import csv
import os

def writeOutput(dict, path):
    f_aux = open(path, "wb")
    w = csv.writer(f_aux)
    for key, val in patterns.items():
        w.writerow([key, val])
    f_aux.close()
        
#def printOutput(dict):
#    for x in dict:
#        print (x)
#        for y in dict[x]:
#            print (y,':',dict[x][y])
    
if __name__ == '__main__':
    start = time.time()
    print("Frequent and Surprising Pattern analysis with FP-Growth")
     #path = raw_input("Please, write the path to the CSV file \n")
    path = r"C:\Users\migue\Documents\TFG\prep_nuevo.csv"
    # create output data folder
    output_path = os.path.dirname(os.path.abspath(__file__)) + "\Output data"
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    # read CSV file and store it
    instances = pd.read_csv(path, sep=';')
    
    
    while True:
        print("Please, select the sensors you want to analyse, separated by commas.")
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
            chosenSensors.append("Acceleration-X","Acceleration-Y","Acceleration-Z")
        elif sensor == 'altitude':
            chosenSensors.append("Altitude")

    #remove sensors we dont need
    notChosen = [item for item in sensors if item not in chosenSensors]
    for i in notChosen:
        instances = instances[instances['VAR'] != i]
    hdr = ";".join(chosenSensors)

    ############### FREQUENT PATTERN DETECTION ###############
    inst_fp = instances.copy()
    for i in chosenSensors:
        # number of rows of the current sensor
        num_instances = len(inst_fp[inst_fp.VAR==i])
        # we dont wanna filter out the rare motion detections
        if i!='Motion Detected':
            bins = inst_fp['RAW'][inst_fp['VAR'] == i].unique()
            # remove bins that contain less than 5% of the instances of the sensor
            for x in set(bins):
                if inst_fp['RAW'][(inst_fp.VAR == i) & (inst_fp.RAW == x)].count() < (num_instances*0.05):
                    inst_fp[inst_fp.VAR == i] = inst_fp[(inst_fp.VAR == i) & (inst_fp.RAW != x)]
    #eliminate instants left incomplete
    inst_fp = inst_fp.groupby(['TIME']).filter(lambda time_instant : len(time_instant) == len(chosenSensors))
    #we dont need the VAR column anymore
    del inst_fp['VAR']
    # input data for FP-Growth must be immutable
    inst_fp = tuple(inst_fp.groupby('TIME')['RAW'].apply(tuple))
    # find patterns, rules and write them to output files
    patterns = fpg.find_frequent_patterns(inst_fp, 5)
    no_fp = len(patterns)
    print("%i frequent patterns were found" % no_fp)
    i = 0
    while os.path.exists(output_path + ("\\frequent_patterns_%i.csv" % i)):
        i += 1
    f_freq_pat = output_path + ("\\frequent_patterns_%i.csv" % i)
    writeOutput(patterns, f_freq_pat)
    rules = fpg.generate_association_rules(patterns, 2)
    no_fr = len(rules)
    print("%i frequent pattern association rules were found" % no_fr)
    i = 0
    while os.path.exists(output_path + ("\\frequent_rules_%i.csv" % i)):
        i += 1
    f_freq_rules = output_path + ("\\frequent_rules_%i.csv" % i)
    writeOutput(rules, f_freq_rules)


    ############### SURPRISING PATTERN DETECTION ###############
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
    patterns = fpg.find_frequent_patterns(inst_fp, 5)
    no_sp = len(patterns)
    print("%i surprising patterns were found" % no_sp)
    i = 0
    while os.path.exists(output_path + ("\\surprising_patterns_%i.csv" % i)):
        i += 1
    f_freq_pat = output_path + ("\\surprising_patterns_%i.csv" % i)
    writeOutput(patterns, f_freq_pat)
    rules = fpg.generate_association_rules(patterns, 2)
    no_sr = len(rules)
    print("%i surprising pattern association rules were found" % no_sr)
    i = 0
    while os.path.exists(output_path + ("\\surprising_rules_%i.csv" % i)):
        i += 1
    f_freq_rules = output_path + ("\\surprising_rules_%i.csv" % i)
    writeOutput(rules, f_freq_rules)

    ############### FINAL STEPS ###############
    end = time.time()
    # log writing
    print("Writing log file")
    i = 0
    while os.path.exists(output_path + ("\\log_%i.txt" % i)):
        i += 1
    f_log = open((output_path + ("\\log_%i.txt" % i)), "wb")
    f_log.write("Time elapsed: %f seconds \n" %(end - start))
    sensors = ', '.join(chosenSensors)
    f_log.write("%i sensors used: %s \n" % (len(chosenSensors), sensors))
    f_log.write("Number of frequent patterns found: %f \n" % no_fp)
    f_log.write("Number of frequent pattern association rules found: %f \n" % no_fr)
    f_log.write("Number of surprising patterns found: %f \n" % no_sp)
    f_log.write("Number of surprising pattern association rules found: %f" % no_sr)
    f_log.close()