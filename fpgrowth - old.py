#C:\Users\migue\Documents\UC3M\TU Graz\Bachelor thesis\Data\ct_meeting_6.2.csv

import sys
import csv
import pandas as pd
from fp_growth import find_frequent_itemsets

    
if __name__ == '__main__':
     #path = raw_input("Please, write the path to the CSV file \n")
    path = r"C:\Users\migue\Documents\UC3M\TU Graz\Bachelor thesis\Data\despacho_liencres_out.csv"

    # read CSV file and store it
    #instances = pd.read_csv(path, sep=';')
    #print("csv read")
    #instances.to_dict('records')
    #print("Dictionary created") 
    instances =[]
    with open(path, 'rb') as f:
        reader = csv.reader(f)
        instances = list(reader)
    print("List created")
    frequent_items = pd.DataFrame()
    #minsup=0.15
    for idx, itemset in find_frequent_itemsets(instances, 4):
        frequent_items.append(itemset)
        if (idx%100 == 0):
            print(idx)
    print(frequent_items)

    # ----------------------------------------------------------------------------------------------
    #path = input("Please, write the path to the CSV file \n")
    #csvout = "C:\\Users\\migue\\Documents\\UC3M\\TU Graz\\Bachelor thesis\\Data\\" + input("Please, write the name of the CSV output file \n")

    ## open files & create outfile
    #counter = 0

    #sound = []
    #barometer = []
    #temperature = []
    #co2 = []
    #light = []
    #master = []
    #moisture = []
    #humidity = []
    #motion = []  
    
    ##with open(csvout, "w+") as outfile:
    #with open(path, "r+") as csvfile:
    #    reader = csv.reader(csvfile, delimiter=';', quotechar='|')
    #    for row in reader:
    #        if row[1] == "Sound Intensity Bricklet":
    #            sound.append(row[4])
    #        elif row[1] == 'Barometer Bricklet':
    #            barometer.append(row[4])
    #        elif row[1] == 'Temperature Bricklet':
    #            temperature.append(row[4])
    #        elif row[1] == 'CO2 Bricklet':
    #            co2.append(row[4])
    #        elif row[1] == 'Ambient Light Bricklet':
    #            light.append(row[4])
    #        elif row[1] == 'Master Bricklet':
    #            master.append(row[4])
    #        elif row[1] == 'Moisture Bricklet':
    #            moisture.append(row[4])
    #        elif row[1] == 'Humidity Bricklet':
    #            humidity.append(row[4])
    #        elif row[1] == 'Motion Detector Bricklet':
    #            motion.append(row[4])
    #        counter += 1
    #        print("Processing instance number %d" % counter, end='\r')
    #    for itemset in find_frequent_itemsets(sound, 1):
    #        print(itemset)
    #csvfile.close()
    #outfile.close()