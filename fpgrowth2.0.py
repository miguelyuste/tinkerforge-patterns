#C:\Users\migue\Documents\UC3M\TU Graz\Bachelor thesis\Data\ct_meeting_6.2.csv

import csv
import pickle
import numpy
import math
import pandas as pd
import pyfpgrowth as fpg
import matplotlib.pyplot as plt
import time

    
if __name__ == '__main__':
    start = time.time()
    print("Frequent Pattern analysis with FPGrowth")
     #path = raw_input("Please, write the path to the CSV file \n")
    path = r"C:\Users\migue\Documents\UC3M\TU Graz\Bachelor thesis\Data\prep_nuevo.csv"
    # read CSV file and store it
    instances = pd.read_csv(path, sep=';')
    ##mmm = instances['RAW'][instances['VAR']== "CO2 Concentration"].as_matrix()
    ##plt.xlim([min(mmm)-5, max(mmm)+5])

    ##plt.hist(mmm, alpha=0.5)
    ##plt.title('CO2 Concentration')
    ##plt.xlabel('value')
    ##plt.ylabel('count')

    ##plt.show()
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

    #for i in chosenSensors:
    #    plt.figure()
    #    plt.title(i)
    #    plt.hist(instances['RAW'][instances['VAR'] == i], bins=50)
    #    plt.show()

    # input data for FPGrowth: one column per sensor
    # file with bins info
    hdr = ";".join(chosenSensors)

    ############### FREQUENT PATTERN DETECTION ###############
    inst_fp = instances
    num_instances = len(inst_fp)
    #eliminate = []
    for col, i in enumerate(chosenSensors):
        bins = inst_fp['RAW'][inst_fp['VAR'] == i].unique()
        # remove bins that contain less than 5% of the instances
        for x in set(bins):
            if inst_fp['RAW'][(inst_fp.VAR == i) & (inst_fp.RAW == x)].count() < (num_instances*0.05):
                inst_fp['RAW'][inst_fp['VAR'] == i] = inst_fp['RAW'][(inst_fp.VAR == i) & (inst_fp.RAW != x)]
    del inst_fp['VAR']
    ############## REFINARLO, ESTO NO FUNCIONA ################
#    inst_fp = list(inst_fp.groupby(['TIME']))
#    #########FUNSIONA UNA POCA###########
#    #hola = inst_fp.set_index(['TIME'])
#    #subset5 = hola[['RAW']]
#    #tuples5 = [tuple(x) for x in subset5.values]
#    start = time.time()
#    for i in inst_fp.TIME.unique():
#        new3.append(tuple(inst_fp.RAW[inst_fp.TIME == i]))
#    end = time.time()
#    print('ELAPSED TIME:'+end-start)
    
    inst_fp = tuple(inst_fp.groupby('TIME')['RAW'].apply(tuple))
    
    #    # get instances of sensor in numpy array
    #    aux = inst_fp['RAW'][instances['VAR'] == i].as_matrix()
    #    # calculate bins
    #    bins = numpy.linspace(min(aux), max(aux), numBins-1)
    #    row = 0
    #    for j in bins:
    #        allbins[row][col] = j
    #    # write bins to file
    #    ##### TODO: write doesnt work too well. writes E22 power for god knows which reason
    #    #bins.tofile(r"C:\Users\migue\Documents\UC3M\TU Graz\Bachelor thesis\Data\bins_file.csv", sep=";", format="%s")
    #    #numpy.savetxt(r"C:\Users\migue\Documents\UC3M\TU Graz\Bachelor thesis\Data\bins_file.csv", bins, delimiter=';', newline='\n', header=hdr, footer='', comments='# ')
    #    ### ALTITUDE VALUES ARE NEGATIVE, MONOTONY PROBLEMS
    #    bin_means = (numpy.histogram(aux, bins, weights=aux)[0] / numpy.histogram(aux, bins)[0])
    #    print bin_means
    #    print "BINNING"
    #    # arbitrarily chosen 2% treshold
    #    num_instances = len(inst_fp)
    #    rows_to_keep = numpy.array([True]*len(inst_fp))
    #    for x in set(bin_means):
    #        if bin_means.count(x) < (num_instances*0.02):
    #            rows_to_keep = numpy.logical_and( rows_to_keep, bin_means != x )
    #    inst_fp = inst_fp[rows_to_keep]
    #    # write binned data to our input data matrix
    #    for row, j in enumerate(bin_means):
    #        data[row][col] = j
    #        row += 1
    #numpy.savetxt(r"C:\Users\migue\Documents\UC3M\TU Graz\Bachelor thesis\Data\bins.csv", allbins, delimiter=';', newline='\n', header=hdr, footer='', comments='# ')
    #numpy.savetxt(r"C:\Users\migue\Documents\UC3M\TU Graz\Bachelor thesis\Data\binned_values.csv", data, delimiter=';', newline='\n', header=hdr, footer='', comments='# ')


    #instances.to_dict('records')
    #print("dictionary created") 
    #instances =[]
    #with open(path, 'rb') as f:
    #    reader = csv.reader(f)
    #    instances = list(reader)
    #print("List created")
    #frequent_items = pd.DataFrame()
    #minsup=0.15
    ########## PICKLE SAVES WEIRD STUFF
    patterns = fpg.find_frequent_patterns(inst_fp, 5)
    print(patterns)
    rules = fpg.generate_association_rules(patterns, 2)
    print(rules)
    pickle.dump( rules, open(r"C:\Users\migue\Documents\UC3M\TU Graz\Bachelor thesis\Data\frequent_rules.csv", "wb" ) )


    ############### SURPRISING PATTERN DETECTION ###############
    inst_sp = instances
    for col, i in enumerate(chosenSensors):
        bins = inst_sp['RAW'][inst_sp['VAR'] == i].unique()
        # remove bins that contain more than 5% of the instances
        for x in set(bins):
            if inst_sp['RAW'][(inst_sp.VAR == i) & (inst_sp.RAW == x)].count() > (num_instances*0.05):
                inst_sp['RAW'][inst_sp['VAR'] == i] = inst_sp['RAW'][(inst_sp.VAR == i) & (inst_fp.RAW != x)]
    del inst_sp['VAR']
    inst_sp = list(inst_sp.groupby(['TIME']))
    surprising_items = pd.DataFrame()
    patterns = fpg.find_frequent_patterns(inst_sp, 2)
    print(patterns)
    pickle.dump( patterns, open(r"C:\Users\migue\Documents\UC3M\TU Graz\Bachelor thesis\Data\surprising_patterns.csv", "wb" ) )
    rules = fpg.generate_association_rules(patterns, 0.7)
    print(rules)
    pickle.dump( rules, open(r"C:\Users\migue\Documents\UC3M\TU Graz\Bachelor thesis\Data\surprising_rules.csv", "wb" ) )
    end = time.time()
    print("Time elapsed: %f" %(end - start))