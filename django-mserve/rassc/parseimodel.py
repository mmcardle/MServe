# -*- coding: cp1252 -*-
"""
 ########################################################################
 #
 # © University of Southampton IT Innovation Centre, 2011 
 # Copyright in this library belongs to the University of Southampton 
 # University Road, Highfield, Southampton, UK, SO17 1BJ 
 # This software may not be used, sold, licensed, transferred, copied 
 # or reproduced in whole or in part in any manner or form or in or 
 # on any media by any person other than in accordance with the terms 
 # of the Licence Agreement supplied with the software, or otherwise 
 # without the prior written consent of the copyright owners.
 #
 # This software is distributed WITHOUT ANY WARRANTY, without even the 
 # implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE, 
 # except where stated in the Licence Agreement supplied with the software.
 #
 #	Created By :		Alexandru Puia
 #	Created Date :		2011-07-07
 #	Created for Project :	PrestoPRIME
 #
 ########################################################################
"""

#import sys
import csv

#function that clears that hashmap so it can be reused in the iteration
def clearDataTable(dict):
    for (k,v) in dict.items():
        dict[k] = ''

#function that takes a string "Storage System x" and returns the number x
def getNumber(string):
    words = string.split(' ')
    return words[2]

#function that will merge two given lists
def mergeLists(l1,l2):
    index = 0
    for v1,v2 in zip(l1,l2):
        if v1 == '' and v2 !='':
            l1[index] = v2
        index += 1

#open the file given as an argument in the command line
#f = open(sys.argv[1], 'r')

def parse(filename, outfilename="data.csv"):
    f = open(filename, 'r')
    #create a hash map with the headers found in the file received as argument
    default = 'Storage System'
    string = ''
    data = {}
    for line in f:
        #print(line)
        [stamp, vars] = line.split(' - [')
        vars = vars.replace(']', '').split(' [')
        for var in vars:
            [name, value] = var.split(': ')
            data[string+name] = ''
            if name == 'category':
                string = ''
            if name == 'category' and default in value:
                string = 'Storage System '+getNumber(value)+' '
        string = ''

    #return to the first line of the file
    f.seek(0)

    #create a new hashmap that ensures unicity of the timestamp over category 
    #timeStamp = {}
    duplicate = {}
    for line in f:
        [stamp, vars] = line.split(' - [')
        vars = vars.replace(']', '').split(' [')
        for var in vars:
            [name, value] = var.split(': ')
            name = name.rstrip()
            data[string+name] = value.rstrip()
            if name == 'category':
                string = ''
            if name == 'category' and default in value:
                string = 'Storage System '+getNumber(value)+' '
            list = []
        string = ''
        for k,v in sorted(data.items()):
            if k != 'category':
                list.append(v)
        simTime = data['Current simulation time']
        
        if duplicate.has_key(simTime) == True:
            mergeLists(duplicate[simTime],list)
        else:
            duplicate[simTime] = list

        #timeStamp[simTime+data['category']] = list

        clearDataTable(data)

    #finally write the data in CSV file
    #open the file in which the data will be written
    g = open(outfilename, 'wb') 
    fileWriter = csv.writer(g,
                            delimiter=',',quotechar='|',
                            quoting=csv.QUOTE_MINIMAL)
    del data['category']
    fileWriter.writerow(sorted(data.keys()))
    for k,v in sorted(duplicate.items()):
        fileWriter.writerow(v)
    #print "Created the file "+outputFile

    #Close the files   
    f.close()
    g.close()

