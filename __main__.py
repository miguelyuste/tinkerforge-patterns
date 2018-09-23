import preprocesser as prep
import miner as fpg
import time
import os


if __name__ == '__main__':
     ### SCRIPT THAT RUNS BOTH OF THE MODULES
    start = time.time()
    print("***** Frequent and Surprising Pattern mining with FP-Growth ***** \nInitialisation running...")
    
    # create output data folders
    output_path = os.path.dirname(os.path.abspath(__file__))
    output_path += "\\Output data"
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    i = 0
    while os.path.exists(output_path + ("\\Execution #%i" % i)):
        i += 1
    output_path += "\\Execution #%i" % i
    os.makedirs(output_path)

    #create log file
    i = 0
    while os.path.exists(output_path + ("\\log_%i.txt" % i)):
        i += 1
    f_log = open((output_path + ("\\log_%i.txt" % i)), "wb")

    #C:\Users\migue\Documents\TFG\despacho_liencres.csv
    path = raw_input("Please, write the path to the CSV file \n")

    # run preprocesser 
    # parametres: path to input CSV, path to output folder where results will be placed
    prep_res = prep.prep(i, path, output_path)
    f_log.write(prep_res['results'])
    
    #print (memory_usage((prep, [], {})))
    
    # run miner
    # parametres: path to preprocesed CSV, path to output folder where results will be placed 
    mining_res = fpg.find_patterns(i, prep_res['path_out'], output_path)
    f_log.write(mining_res) 
    
    # final log writing
    end = time.time()
    elapsed = "Execution finished. Total time elapsed: %f seconds" %(end - start)
    f_log.write(elapsed)
    f_log.close()   
    print("All output files and the log have been placed in an '\Output data' folder under the main directory of the scripts.\n")
    