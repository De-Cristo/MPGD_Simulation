#########################################################################################
# This python project is based on Garfield++(CERN) & ROOT(CERN).                        #
# This certain code is to simulate GEM detector.                                        #
# First contributed by PKU-CMS GEM group 2022-10-13 Licheng ZHANG                       #
# Author: contact L.C.ZHANG (licheng.zhang@cern.ch)                                     #
#########################################################################################
import os, sys

def CleanLines(lines):
    cleanedLines=[]
    for line in lines:
        # skip if it is 100% whitespace
        if line.isspace():
            continue
        # remove comments
        if line.find("#") == -1:        # no comment
            cleanedLines.append(line.split("\n")[0])
        elif line.find("#") != 0:   # there is an inline comment
            cleanedLines.append(line[:line.find("#")])
        else:                           # whole line is commented
            print("Following line is commented and will be removed:")
            print(line)
    return cleanedLines

def MakeConfigMap(lines):
    settings = {}
    for line in lines:
        for item in line.split():
            if len(item.split("=")) == 2:
                name,value = item.split("=")
                settings[name] = value
            else:
                print("{0} not in setting=value format".format(item))
    return settings

def ReadTextFile(filename):
    textfile =open(filename, 'r')
    filelines = textfile.readlines()
    filelines = CleanLines(filelines)
    settings = MakeConfigMap(filelines)
    
    gpu = ''
    if "gpu" in settings.keys():
        gpu = settings["gpu"]
            
    return gpu
