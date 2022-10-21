#########################################################################################
# This python project is based on Garfield++(CERN) & ROOT(CERN).                        #
# This certain code is to simulate GEM detector.                                        #
# First contributed by PKU-CMS GEM group 2022-10-13 Licheng ZHANG                       #
# Author: contact L.C.ZHANG (licheng.zhang@cern.ch)                                     #
#########################################################################################
import ROOT as R
import os, sys
import math
import ctypes
import argparse
from array import array

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
    
    if "GasFile" in settings.keys():
        gas = R.Garfield.MediumMagboltz()
        gas.LoadGasFile(settings["GasFile"])
        if "MaxElectronEnergy" in settings.keys():
            gas.SetMaxElectronEnergy(float(settings["MaxElectronEnergy"]))
        gas.Initialise(True)
        rPenning = 0.57
        lambdaPenning = 0.
        gas.EnablePenningTransfer(rPenning, lambdaPenning, "ar")
    else:
        print("\033[1;31m ERROR:: \033[0m Gas file dose not been found. Exitting")
        exit(0)
        
    if "AnsysFile" in settings.keys():
        fm = R.Garfield.ComponentAnsys123()
        fm.Initialise(settings["AnsysFile"]+"/ELIST.lis",settings["AnsysFile"]+"/NLIST.lis",\
                      settings["AnsysFile"]+"/MPLIST.lis",settings["AnsysFile"]+"PRNSOL.lis","mm") #the unit adopted by ANSYS15.0 is mm
        weightFile = []
        if "WeightingField" in settings.keys():
            for fileName in os.listdir(settings["WeightingField"]):
                weightFile.append(fileName+'/PRNSOL.lis')
            #end
            for i in range(1,len(weightFile)+1):
                fm.SetWeightingField(settings["WeightingField"]+weightFile[i-1],'readout'+str(i))
                print('Link '+weightFile[i-1]+' to '+'readout'+str(i))
            #end
        else:
            print('\033[1;31m WARNING:: \033[0m Weighting fields have not been set, signals cannot be calculated, please double check!')
        if "MirrorPeriodic" in settings.keys():
            if settings["MirrorPeriodic"]=="True":
                print("\033[1;34m Periodic::Enable Mirror Periodic\033[0m")
                fm.EnableMirrorPeriodicityX()
                fm.EnableMirrorPeriodicityY()
            else:
                fm.EnablePeriodicityX()
                fm.EnablePeriodicityY()

        nMaterials = fm.GetNumberOfMaterials()
        for i in range(0,nMaterials):
            eps = fm.GetPermittivity(i)
            if (abs(eps - 1.) < 1.e-3):
                fm.SetMedium(i, gas)
        #end
    else:
        print("\033[1;31m ERROR:: \033[0m Field file does not been found. Exitting")
        exit(0) 
    
    if "LowerBound" in settings.keys() and "UpperBound" in settings.keys():
        lowerbound=float(settings["LowerBound"])
        upperbound=float(settings["UpperBound"])
    else:
        print("\033[1;31m ERROR:: \033[0m Sensor range does not been settled. Exitting")
        exit(0) 
        
    if "IncidentParticle" in settings.keys():
        incidentpart = settings["IncidentParticle"]
        print("\033[1;34m Incident_Particle::{0}\033[0m".format(incidentpart))
    else:
        incidentpart = 'photon'
        print("\033[1;31m ERROR:: \033[0m Incident particle does not been set. default is X-Ray photon")
    
    kineticenergy = 100 # ev
    if "Energy" in settings.keys():
        kineticenergy = settings["Energy"]
        if kineticenergy=='Ru':
            print("\033[1;34m Incident_Particle::Kinetic energy will be set to self-generated {0}, which can be found in SimProducer.py\033[0m".format(kineticenergy))
        else:
            kineticenergy=float(kineticenergy)
            print("\033[1;34m Incident_Particle::Kinetic energy will be set to {0}\033[0m".format(str(kineticenergy)))
    else:
        print('\033[1;31m WARNING:: \033[0m Kinetic energy of the incident particle has not been set, will be set to default value (100 ev), please double check!')
    
    driftboundary = 0.0030
    if "DriftBoundary" in settings.keys():
        driftboundary = float(settings["DriftBoundary"])
        print("\033[1;34m Detector_Geometry::The lower boundary of the drift region will be set to {}\033[0m".format(str(driftboundary)))
    else:
        print("\033[1;31m ERROR:: \033[0m Detector_Geometry::The lower boundary of the drift region will be set to {} (default)".format(str(driftboundary)))
        
    inductboundary = -0.0030
    if "InductBoundary" in settings.keys():
        inductboundary = float(settings["InductBoundary"])
        print("\033[1;34m Detector_Geometry::The upper boundary of the induct region will be set to {}\033[0m".format(str(inductboundary)))
    else:
        print("\033[1;31m ERROR:: \033[0m Detector_Geometry::The upper boundary of the induct region will be set to {} (default)".format(str(inductboundary)))
    
    return gas,fm,len(weightFile),lowerbound,upperbound,incidentpart,kineticenergy,driftboundary,inductboundary
