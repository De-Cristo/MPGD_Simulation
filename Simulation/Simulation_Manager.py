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

from ReadInput import ReadTextFile

def env(batch, multi):
    ## Environment test and setups
    if batch == True: R.gROOT.SetBatch(R.kTRUE)
    else: R.gROOT.SetBatch(R.kFALSE)
        
    if multi != 0:
        R.EnableImplicitMT(multi)
        print('using ' + str(multi) + ' threads in MT Mode!')
    else:
        print('Disable MT Mode!')

    path = os.getenv('GARFIELD_INSTALL')

    if sys.platform == 'darwin':
        R.gSystem.Load(path + '/lib64/libmagboltz.dylib')
        R.gSystem.Load(path + '/lib64/libGarfield.dylib')
    else:
        R.gSystem.Load(path + '/lib64/libmagboltz.so')
        R.gSystem.Load(path + '/lib64/libGarfield.so')
        

'''
pitch                 : The distance between the centre of the nabouring holes
self.inFile_name      : The name of the configure file
self.GAS              : Magboltz gas container from Garfield.MediumMagboltz()
self.FM               : Field Map container from Garfield.ComponentAnsys123()
self.Nstrip           : Number of the readout strip (based on the number of weighting fields, need to be further developed)
self.LB               : The Lower Boundary of the sensitive region
self.UB               : The Upper Boundary of the sensitive region
self.SOURCE           : The type of the incident particle
'''
class Simulation_Manager:
    
    pitch=0.0140

    def __init__(self, input_file):
        self.inFile_name = input_file
        self.GAS,self.FM,self.Nstrip,self.LB,self.UB,self.SOURCE = ReadTextFile(input_file)
        self.SENSOR = R.Garfield.Sensor()
        self.SENSOR.AddComponent(self.FM)
        self.DRIFT = R.Garfield.AvalancheMC()
        self.DRIFT.SetSensor(self.SENSOR)
        self.DRIFT.SetDistanceSteps(0.0005)
        self.DRIFT.EnableRKFSteps(True)
        self.AVAL = R.Garfield.AvalancheMicroscopic()
        self.AVAL.SetSensor(self.SENSOR)
        self.AVAL.EnableSignalCalculation()
        self.AVAL.EnableMagneticField()
        self.AVAL.DisableAvalancheSizeLimit()
        self.TRACK = R.Garfield.TrackHeed()
        self.TRACK.SetSensor(SENSOR)
        self.TRACK.EnableElectricField()
        if self.SOURCE!='photon':
            self.TRACK.SetParticle(self.SOURCE)
            
    def print_fm_info(self):
        self.FM.PrintRange()
        self.FM.PrintMaterials()
        return 0
    
    def import_transferfunction(self,TransferFunction):
        times = R.std.vector('double')()
        values = R.std.vector('double')()
        
        for i in range(0,4000):
            times.push_back(float(i)/4.0)
            values.push_back(float(TransferFunction(float(i)/4.0)))
        self.SENSOR.SetTransferFunction(times, values)
        print("\033[1;35m Tranfer_Function::Enable Tranfer Function.\033[0m")
        return 0
    
    def link_readouts(self):
        for i in range(1,self.Nstrip+1):
            self.SENSOR.AddElectrode(self.FM,"readout"+str(i))
        return 0 
    
    def set_sensitive_space_time(self,x0,y0,z0,x1,y1,z1,t0,t1,dt):
        if z0 != self.LB or z1 != self.UB:
            print("\033[1;31m WARNING::\033[0m The lower or the upper boundaries are being re-writed by user defined numbers, be careful!")
        self.SENSOR.SetArea(x0,y0,z0,x1,y1,z1)
        nTimeBins = int((t1 - t0) / dt)
        self.SENSOR.SetTimeWindow(t0, t1, nTimeBins)
        self.DRIFT.SetTimeWindow(t0, t1)
        print("\033[1;35m Space_Time::Sensitive space and time have been fixed:\033[0m")
        print("\033[1;35m X(cm) from {0} to {1};\033[0m".format(x0,x1))
        print("\033[1;35m Y(cm) from {0} to {1};\033[0m".format(y0,y1))
        print("\033[1;35m Z(cm) from {0} to {1};\033[0m".format(z0,z1))
        print("\033[1;35m T(ns) from {0} to {1}, time step {2};\033[0m".format(t0,t1,dt))
        return 0