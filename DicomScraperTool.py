import os
import sys
import getopt
import glob
import subprocess
import csv
import pydicom
import pandas as pd 
import cmd


# function for scraping a folder and looking for DICOM files
def scrapePath(thisPath):
    dirs = os.listdir(thisPath)
    
    dicomFile = []
    
    for dir1 in dirs:           
    
        newDir =  thisPath + '/' + dir1  
        if(os.path.isfile(newDir)):
            if(len(dicomFile)<1):
                try: 
                    ds = pydicom.dcmread(newDir)   # try read the file as a dicom
                    dicomFile.append(newDir) 
                except: 
                    a = 1  # junk command
                    
    # return identified dicomFile (empty list for none)
    return dicomFile


# function to scrape the dicomfile for the meta data outlined in the keyList
def scrapeDicomFile(thisFile,keyList):
    
    ds = pydicom.dcmread(thisFile)   # read the file
    
    # initiate the storage dataframe row
    thisDF = pd.DataFrame(columns = keyList)
    
    # loop through the keys
    for key in keyList: 
        if '00' in key:    # tag info provided
            fd = ds[eval(key)]
            field = fd.value 
        else:   # tag string key given
            fd = ds[key]
            field = fd.value
    
        out = '%s' % field  # push everything to string -- deals with tag types
        thisDF.at[0,key] = out   # fill the dataframe
        
    return thisDF
       
# function to read the user-provided tag key list
def readKeyList(keyFile): 
    with open(keyFile) as f:
        keyList = f.readlines()
    
    for ind in range(0,len(keyList)): 
        thisKey = keyList[ind]
        keyList[ind] = thisKey.replace("\n", "")
    
    return keyList



def main(argv):
    try:
      opts, args = getopt.getopt(argv,"p:k:o:",["searchPath=","keyFile=","outFile="])
      fail = (len(opts) < 3)
      if fail:
        print("Input error: DicomScraperTool -p (search path) -k (key filename) -o (out filename)")
        sys.exit(2)
    except: 
        print("Input error: DicomScraperTool -p (search path) -k (key filename) -o (out filename)")
        sys(exit(2))

    try: 
        for opt, arg in opts:
            if opt in ("-p", "--searchPath"):
                searchPath = arg
            elif opt in ("-k", "--keyFile"):
                keyFile = arg
            elif opt in ("-o", "--outFile"):
                outFile = arg
    except: 
        print("Input error: DicomScraperTool -p (search path) -k (key filename) -o (out filename)")
        sys(exit(2))


    # read keylist file -- this list determines the columns in the output CSV file
    keyList = readKeyList(keyFile)
    pstr = 'Requested keys to be scraped from key list file: %s' % keyFile
    print(pstr)
    cli = cmd.Cmd()
    cli.columnize(keyList, displaywidth=20)
    print(' ')

    # the search directory
    directoryList= searchPath
    
    # build the dataframe template -- using the keylist info as the columns
    dataFrame = pd.DataFrame(columns = keyList)

    # develop a list of all subdirectories in the search path
    dirList = []
    for root, subdirs, files in  os.walk(directoryList):
        for name in subdirs: 
            dirList.append(os.path.join(root, name))

    # independent DICOM series (i.e folder) counter: 
    seriesCounter = 0

    # DICOM series directory list: 
    dicomSeriesDirectories = []

    dcmFile = scrapePath(directoryList)   # scrape the top level

    if(len(dcmFile) > 0):
        scrapeDicomFile(dcmFile[0])
        comb = [dataFrame,df]
        dataFrame = pd.concat(comb)  # this is the composite dataframe of requested metaData
        seriesCounter = seriesCounter+1
        dicomSeriesDirectories.append(directoryList)

    # now loop through all of the subdirectories to look for DICOM series: 
    for newDir in dirList:    
        dcmFile = scrapePath(newDir) 
        if(len(dcmFile) > 0):
            df = scrapeDicomFile(dcmFile[0],keyList)
            comb = [dataFrame,df]  # this adds the new row to the composite dataframe
            dataFrame = pd.concat(comb)
            
            seriesCounter = seriesCounter+1
            dicomSeriesDirectories.append(newDir)


    pstr = 'We found %d dicom series in the following directories: ' % seriesCounter
    print(pstr)
    cli = cmd.Cmd()
    cli.columnize(dicomSeriesDirectories, displaywidth=80)
    print(' ')


    pstr = '...which were scraped to form the following data table, determined by your keyList input file:  '
    print(pstr)
    # display and save the composite metadata dataframe
    print(dataFrame)
    print(' ')


    dataFrame.to_csv(outFile,index=False)
    pstr = '...which has been output to the following csv file: %s  ' % outFile
    print(pstr)



if __name__ == "__main__":
   main(sys.argv[1:])