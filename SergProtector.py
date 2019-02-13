# -*- coding: utf-8 -*-
"""
Created on Mon Nov  5 20:23:33 2018

@author: Sergey Koryakin

This script reads EPOC EEG data from a .csv file. Can read a file that is also 
simultaneously being written to. Thus, can read live data.

For live data:
    - EEGLogger.exe must be started a few seconds prior to running this python
    data reader file. ***this may change, if subprocesses get figured out***
    - the readfile() function must be fed "isLive = True"
    - to see live data plot, feed "doplots = True" to readfile()
    - to see # lines acquired every 0.5s, feed "explicit = True" to readfile()
    - live plot will first show baseline of false data to distinguish new stuff
"""

"""
###############################################################################
here be the imports and function definition.
could be made into a separate file that is imported as a module...
###############################################################################
"""
# all necessary module imports
import numpy as np
import time
import os
import csv
import matplotlib.pyplot as plt


#function definition
def readfile(filepath,isLive,doplots,explicit=True):
    with open(filepath,'r') as csvfile:
        firstread = csv.reader(csvfile, delimiter=',')
#        headers = list(firstread)[0]
        print("didit")
        dat = np.array(list(firstread)[1:-1])
    csvfile.close()
    length = len(dat)
    if explicit:
        print("File successfully read.\nThere are "+str(length) + " lines of data.")
    if isLive:
        init = 1
        if doplots:
            limit = 2000
            x = np.linspace(1,limit,limit)
            ydat = np.zeros(limit)
            plt.ion()
            fig = plt.figure()
            ax = fig.add_subplot(111)
            line1, = ax.plot(x, ydat, 'r-')
        running = True
        while running:
            with open(filepath,'r') as csvfile:
                reread = csv.reader(csvfile, delimiter=',')
                data = np.array(list(reread))
            if len(data) > length:
                diff = len(data)-length
                print(str(diff)+" new lines")
                length = len(data)
                init = 1
                time.sleep(0.5)
                """
                updating plot
                """
                if doplots:
                    print(data)
                    dats = np.array(list(data[:-1]))
                    dats = dats[-int(diff):,3]
                    ydat = ydat[diff:]
                    ydat = np.append(ydat,dats)
                    line1.set_ydata(ydat)
                    ax.relim()
                    ax.autoscale_view()
                    fig.canvas.draw()
                    fig.canvas.flush_events()
            elif init < 10:
                init += 1
                time.sleep(1)
                print("no new lines... retrying x" + str(init))
            else:
                running=False
                csvfile.close() 
    return(dat) #,headers)



"""
###############################################################################
here be the stuff that runs readfile()
for live data use: relativepath = '\\EEGLogger\\bin\\Debug\\EEGLogger.csv'
###############################################################################
"""
try:
    #initialization
    relativepath = '\\EEGLogger\\bin\\Debug\\EEGLogger.csv'
#    relativepath = '\\dataForTesting\\dataFromAndrewIDK.csv' # this is a test file; not live data destination
    cwd = os.getcwd()                                # ^-- NOT FOR USE WITH DRONE!!!!!
    fpath = cwd + relativepath
    #parameters
#    live = "N"
#    plotting = "N"
    live = input("Live? (Y/N): ")
    plotting = "Y"
    if live =="Y":
        isLive = True
    else:
        isLive = False
    if plotting=="Y":
        doplots = True
    else:
        doplots = False
    #running...
    alldat = np.array(readfile(fpath,isLive,doplots)) # & on next line maybe: headers = alldat[0]
    dat = np.array(alldat[1:]).astype(float)
    print(dat)    
    
    
    """
    ###############################################################################
    here be stuff for non-live data...
    it is a bit trickier bc the shifting plot simulates delay of incoming data...
    ###############################################################################
    """
    #plotting stuff
    if isLive==False:
        length = len(dat)
        headers = dat[0]
        fullXaxis = np.linspace(1,length,length)
        plt.plot(fullXaxis,dat[:,3])
    
        limit = 2000
        x = np.linspace(1,limit,limit)
        ydat = np.zeros(limit)
        plt.ion()
        fig = plt.figure()
        ax = fig.add_subplot(111)
        line1, = ax.plot(x, ydat, 'r-')
    
        numchunks = 1000
        chunksize = int(length/numchunks)
        datcol3 = dat[:,3]
        for chunk in range(numchunks):
            start = chunk*chunksize
            end = (chunk+1)*chunksize-1
            ydat = ydat[chunksize-1:]
            ydat = np.append(ydat,datcol3[start:end])
            #    print((phase,ydat))
            line1.set_ydata(ydat)
            ax.relim()
            ax.autoscale_view()
            fig.canvas.draw()
            fig.canvas.flush_events()
        
        fullXaxis = np.linspace(1,length,length)
        plt.plot(fullXaxis,datcol3)
        plt.title(headers[3])
        plt.show()

except KeyboardInterrupt:
    print("Whoops... Interrupted by user...")
    time.sleep(0.5)
    print("Cancelling process...")
    time.sleep(1)
    raise
    
"""
NOTES
-----
maybe add queries for input?
    #live = str(input("Live? (Y/N) \nENTER: ")).upper()
    #plotting = str(input("Plotting? (Y/N) \nENTER: ")).upper()

"""