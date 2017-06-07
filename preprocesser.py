# -*- coding: utf-8 -*-
"""
Created on Tue Dec 20 19:14:51 2016

@author: MiguelYuste
"""

#C:\Users\migue\Documents\UC3M\TU Graz\Bachelor thesis\Data\ct_meeting_6.2.csv
#import glob
import sys
#import tempfile
import csv

    
if __name__ == '__main__':
    path = input("Please, write the path to the CSV file \n")
    csvout = "C:\\Users\\migue\\Documents\\UC3M\\TU Graz\\Bachelor thesis\\Data\\" + input("Please, write the name of the CSV output file \n")
    sensor = input("Please choose a sensor: sound, barometer, temperature, co2, light, master, moisture, humidity, motion \n")

    # open files & create outfile
    counter = 0
    with open(csvout, "w+") as outfile:
        with open(path, "r+") as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='|')
            for row in reader:
                if sensor is 'sound':
                    if row[1].lower() is 'Sound Intensity Bricklet'.lower():
                        csvout.write(row)
                elif sensor is 'barometer':
                    if row[1] is 'Barometer Bricklet':
                        csvout.write(row)
                elif sensor is 'temperature':
                    if row[1] is 'Temperature Bricklet':
                        csvout.write(row)
                elif sensor is 'co2':
                    if row[1] is 'CO2 Bricklet':
                        csvout.write(row)
                elif sensor is 'light':
                    if row[1] is 'Ambient Light Bricklet':
                        csvout.write(row)
                elif sensor is 'master':
                    if row[1] is 'Master Bricklet':
                        csvout.write(row)
                elif sensor is 'moisture':
                    if row[1] is 'Moisture Bricklet':
                        csvout.write(row)
                elif sensor is 'humidity':
                    if row[1] is 'Humidity Bricklet':
                        csvout.write(row)
                elif sensor is 'motion':
                    if row[1] is 'Motion Detector Bricklet':
                        csvout.write(row)
                counter += 1
                print("Processing instance number %d" % counter, end='\r')
        csvfile.close()
    outfile.close()