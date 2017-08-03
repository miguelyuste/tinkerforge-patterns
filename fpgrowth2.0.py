#C:\Users\migue\Documents\UC3M\TU Graz\Bachelor thesis\Data\ct_meeting_6.2.csv

import pickle
import pandas as pd
import pyfpgrowth as fpg
import time

    
if __name__ == '__main__':
    start = time.time()
    print("Frequent and Surprising Pattern analysis with FPGrowth")
     #path = raw_input("Please, write the path to the CSV file \n")
    path = r"C:\Users\migue\Documents\UC3M\TU Graz\Bachelor thesis\Data\prep_nuevo.csv"
    # read CSV file and store it
    instances = pd.read_csv(path, sep=';')
    print("Please, select the sensors you want to analyse, separated by commas if there is more than one.")
    # excluding accelerometer temperature readings
    print("Possibilities: all, motion, light, sound, temperature, humidity, co2, pressure, acceleration, altitude")
    aux = raw_input().split(",")
    idx = 0
    for i in aux:
        aux[idx] = i.lower().replace(" ", "")
        idx += 1
    del instances['IDX']
   
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
    patterns = fpg.find_frequent_patterns(inst_fp, 5)
    print("Frequent patterns:\n"+patterns)
    pickle.dump(patterns, open(r"C:\Users\migue\Documents\UC3M\TU Graz\Bachelor thesis\Data\frequent_patterns.csv", "wb" ) )
    rules = fpg.generate_association_rules(patterns, 2)
    print("Frequent rules:\n"+rules)
    pickle.dump( rules, open(r"C:\Users\migue\Documents\UC3M\TU Graz\Bachelor thesis\Data\frequent_rules.csv", "wb" ) )


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
    patterns = fpg.find_frequent_patterns(inst_sp, 5)
    print("Surprising patterns:\n"+patterns)
    pickle.dump(patterns, open(r"C:\Users\migue\Documents\UC3M\TU Graz\Bachelor thesis\Data\surprising_patterns.csv", "wb" ) )
    rules = fpg.generate_association_rules(patterns, 2)
    print("Surprising rules:\n"+rules)
    pickle.dump( rules, open(r"C:\Users\migue\Documents\UC3M\TU Graz\Bachelor thesis\Data\surprising_rules.csv", "wb" ) )
    
    
    
    end = time.time()
    print("Time elapsed: %f seconds" %(end - start))