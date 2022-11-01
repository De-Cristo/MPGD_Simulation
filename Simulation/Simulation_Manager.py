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
from OutputHelper import *
from SimProducer import generate_spectrum_Ru

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
    allowed_particle = ['electron','e-','muon','mu-']
    maxPrimaryEle = 800
    maxPrimaryClusters = 40
    maxTimeBins = 2000

    def __init__(self, input_file, output_file):
        self.inFile_name = input_file
        self.outFile_name = R.TFile(output_file+'.root','RECREATE')
        self.outTree_name =  R.TTree("full_simulation_tree","full_simulation_tree")
        self.out = OutputTree(self.outFile_name,self.outTree_name)
        self.GAS,self.FM,self.Nstrip,self.LB,self.UB,self.SOURCE,self.Energy,self.DriftBoundary,self.InductBoundary = ReadTextFile(input_file)
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
        self.TRACK.SetSensor(self.SENSOR)
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
    
    def quanlity_producer(self,dosig):
        self.out.branch("Events",   "I")
        self.out.branch("ionization",   "I")
        self.out.branch("Incident_xposition",   "F")
        self.out.branch("Incident_yposition",   "F")
        self.out.branch("Incident_zposition",   "F")
        
        self.out.branch("Incident_energy",   "F")
        self.out.branch("Incident_time",   "F")
        
        self.out.branch("PrimaryCluster_number",   "I")
        self.out.branch("PrimaryCluster_xposition",   "F", self.maxPrimaryClusters)
        self.out.branch("PrimaryCluster_yposition",   "F", self.maxPrimaryClusters)
        self.out.branch("PrimaryCluster_zposition",   "F", self.maxPrimaryClusters)
        self.out.branch("PrimaryCluster_time",        "F", self.maxPrimaryClusters)
        self.out.branch("PrimaryCluster_energy",      "F", self.maxPrimaryClusters)
        
        self.out.branch("PrimaryElectron_number",   "I")
        self.out.branch("PrimaryElectron_xposition", "F", self.maxPrimaryEle)
        self.out.branch("PrimaryElectron_yposition", "F", self.maxPrimaryEle)
        self.out.branch("PrimaryElectron_zposition", "F", self.maxPrimaryEle)
        self.out.branch("PrimaryElectron_energy", "F", self.maxPrimaryEle)
        self.out.branch("PrimaryElectron_time", "F", self.maxPrimaryEle)
        self.out.branch("PrimaryElectron_number_inDrift",   "I")
        self.out.branch("PrimaryElectron_number_inDrift_aval",   "I")
        self.out.branch("PrimaryElectron_number_NotinDrift_aval",   "I")
        self.out.branch("FinalElectron_number",   "I")
        self.out.branch("Effective_Gain",   "F")
        
        self.out.branch("time_bin",   "I")
        self.out.branch("V_sig_max",  "F")
        
        self.out.branch("V_sig_tot", "F", self.maxTimeBins)
        if self.Nstrip!=0:
            for i in range(0, self.Nstrip):
                self.out.branch('V_sig_'+str(i+1), "F", self.maxTimeBins)
        
        return 0
    
    def photon_loop(self,nevents):
        for EVE in range(0,nevents):
            print('\033[1;35m Simulation_Manager::\033[0m +++++++++' + 'Event No. ' + str(EVE+1)+' of ' + str(nevents))
            self.out.fillBranch("Events",EVE+1)
            x0 = (R.Garfield.RndmUniform()*2-1) * 3 * self.pitch
            x0 = 0.0070
            self.out.fillBranch("Incident_xposition",x0)
            y0 = math.sqrt(3) * self.pitch * (R.Garfield.RndmUniform()*2-1)
            y0 = 0.0000
            self.out.fillBranch("Incident_yposition",y0)
            z0 = self.UB-0.0001
#             z0 = 0.0200
            self.out.fillBranch("Incident_zposition",z0)
            if self.Energy == 'Ru':
                e0 = generate_spectrum_Ru(EVE)
            else:
                e0 = self.Energy
            self.out.fillBranch("Incident_energy",e0)
            t0 = 0.
            self.out.fillBranch("Incident_time",t0)
            phi = (R.Garfield.RndmUniform()*2-1) * 3.1415927 / 4
            theta = (R.Garfield.RndmUniform()*2-1) * 3.1415927
            track_dx = math.sin(phi)*math.cos(theta)
            track_dy = math.sin(phi)*math.sin(theta)
            track_dz = -math.cos(phi)
            track_dx = 0
            track_dy = 0
            track_dz = -1

            ion = 0
            nel = ctypes.c_int(0)
            self.TRACK.TransportPhoton(x0, y0, z0, t0, e0, track_dx, track_dy, track_dz, nel)
            self.out.fillBranch("PrimaryElectron_number",nel.value)
            
            ex0_list = []
            ey0_list = []
            ez0_list = []
            ee0_list = []
            et0_list = []
            _PrimaryElectron_number_inDrift = 0
            _PrimaryElectron_number_inDrift_aval = 0
            _PrimaryElectron_number_NotinDrift_aval = 0
            _FinalElectron_number = 0
            if nel.value!=0:
                ion = 1
                ex0 = ctypes.c_double(-9.)
                ey0 = ctypes.c_double(-9.)
                ez0 = ctypes.c_double(-9.)
                ee0 = ctypes.c_double(-9.)
                et0 = ctypes.c_double(-9.)
                edx0 = ctypes.c_double(0.)
                edy0 = ctypes.c_double(0.)
                edz0 = ctypes.c_double(0.)
                for i in range(0,nel.value):
                    print('Tracking No. ' + str(i+1) + ' Primary Electron')
                    i_c = ctypes.c_int(i)
                    self.TRACK.GetElectron(i_c.value, ex0, ey0, ez0, et0, ee0, edx0, edy0, edz0)
                    ex0_list.append(ex0.value)
                    ey0_list.append(ey0.value)
                    ez0_list.append(ez0.value)
                    ee0_list.append(ee0.value)
                    et0_list.append(et0.value)
                    if ez0.value>self.DriftBoundary:
                        _PrimaryElectron_number_inDrift+=1
                    self.AVAL.AvalancheElectron(ex0, ey0, ez0, et0, ee0, edx0, edy0, edz0)
                    np = self.AVAL.GetNumberOfElectronEndpoints()
                    if np>1 and ez0.value>self.DriftBoundary:
                        _PrimaryElectron_number_inDrift_aval+=1
                    if np>1 and ez0.value<self.DriftBoundary:
                        _PrimaryElectron_number_NotinDrift_aval+=1
                    xe1 = ctypes.c_double(0.)
                    ye1 = ctypes.c_double(0.)
                    ze1 = ctypes.c_double(0.)
                    te1 = ctypes.c_double(0.)
                    ee1 = ctypes.c_double(0.)

                    xe2 = ctypes.c_double(0.)
                    ye2 = ctypes.c_double(0.)
                    ze2 = ctypes.c_double(0.)
                    te2 = ctypes.c_double(0.)
                    ee2 = ctypes.c_double(0.)
                    status = ctypes.c_int(0)
                    for j in range(0,np):
                        self.AVAL.GetElectronEndpoint(j, xe1, ye1, ze1, te1, ee1, xe2, ye2, ze2, te2, ee2, status)
                        if (ze2.value < self.InductBoundary):
                            _FinalElectron_number+=1
                    
            ex0_list = make_list(ex0_list,self.maxPrimaryEle)
            ey0_list = make_list(ey0_list,self.maxPrimaryEle)
            ez0_list = make_list(ez0_list,self.maxPrimaryEle)
            ee0_list = make_list(ee0_list,self.maxPrimaryEle)
            et0_list = make_list(et0_list,self.maxPrimaryEle)
            self.out.fillBranch("PrimaryElectron_xposition",ex0_list)
            self.out.fillBranch("PrimaryElectron_yposition",ey0_list)
            self.out.fillBranch("PrimaryElectron_zposition",ez0_list)
            self.out.fillBranch("PrimaryElectron_energy",ee0_list)
            self.out.fillBranch("PrimaryElectron_time",et0_list)
            self.out.fillBranch("ionization",ion)
            self.out.fillBranch("PrimaryElectron_number_inDrift",_PrimaryElectron_number_inDrift)
            self.out.fillBranch("PrimaryElectron_number_inDrift_aval",_PrimaryElectron_number_inDrift_aval)
            self.out.fillBranch("PrimaryElectron_number_NotinDrift_aval",_PrimaryElectron_number_NotinDrift_aval)
            self.out.fillBranch("FinalElectron_number",_FinalElectron_number)
            if _PrimaryElectron_number_inDrift != 0 :
                self.out.fillBranch("Effective_Gain",float(_FinalElectron_number)/float(_PrimaryElectron_number_inDrift))
            else:
                self.out.fillBranch("Effective_Gain",-999.)
            
            # place for signal simulation
            
            
            
            self.out.fill()
        self.out.write()
        return 1
        
        
    def particle_loop(self,nevents):
        for EVE in range(0,nevents):
            print('\033[1;35m Simulation_Manager::\033[0m +++++++++ ' + 'Event No.' + str(EVE+1)+' of ' + str(nevents))
            self.out.fillBranch("Events",EVE+1)
            x0 = (R.Garfield.RndmUniform()*2-1) * 3 * self.pitch
            x0 = 0.0070
            self.out.fillBranch("Incident_xposition",x0)
            y0 = math.sqrt(3) * self.pitch * (R.Garfield.RndmUniform()*2-1)
            y0 = 0.0000
            self.out.fillBranch("Incident_yposition",y0)
            z0 = self.UB-0.0001
#             z0 = 0.0200
            self.out.fillBranch("Incident_zposition",z0)
            if self.Energy == 'Ru':
                e0 = generate_spectrum_Ru(EVE)
            else:
                e0 = self.Energy
            self.out.fillBranch("Incident_energy",e0)
            t0 = 0.
            self.out.fillBranch("Incident_time",t0)
            phi = (R.Garfield.RndmUniform()*2-1) * 3.1415927 / 4
            theta = (R.Garfield.RndmUniform()*2-1) * 3.1415927
            track_dx = math.sin(phi)*math.cos(theta)
            track_dy = math.sin(phi)*math.sin(theta)
            track_dz = -math.cos(phi)
            track_dx = 0
            track_dy = 0
            track_dz = -1
            
            self.TRACK.SetKineticEnergy(e0)
            self.TRACK.NewTrack(x0, y0, z0, t0, track_dx, track_dy, track_dz)
            nel = ctypes.c_int(0)
            ncluster = ctypes.c_int(0)
            ion = 0
            xcls_list = []
            ycls_list = []
            zcls_list = []
            ecls_list = []
            tcls_list = []
            ncls = ctypes.c_int(0)
            xcls = ctypes.c_double(-9.)
            ycls = ctypes.c_double(-9.)
            zcls = ctypes.c_double(-9.)
            ecls = ctypes.c_double(-9.)
            tcls = ctypes.c_double(-9.)
            extra = ctypes.c_double(0.)
            
            ex0_list = []
            ey0_list = []
            ez0_list = []
            ee0_list = []
            et0_list = []
            _PrimaryElectron_number_inDrift = 0
            _PrimaryElectron_number_inDrift_aval = 0
            _PrimaryElectron_number_NotinDrift_aval = 0
            _FinalElectron_number = 0
            
            ex0 = ctypes.c_double(-9.)
            ey0 = ctypes.c_double(-9.)
            ez0 = ctypes.c_double(-9.)
            ee0 = ctypes.c_double(-9.)
            et0 = ctypes.c_double(-9.)
            edx0 = ctypes.c_double(0.)
            edy0 = ctypes.c_double(0.)
            edz0 = ctypes.c_double(0.)
            
#             self.TRACK.DisableDeltaElectronTransport() # cannot disable
            while(self.TRACK.GetCluster(xcls, ycls, zcls, tcls, ncls, ecls, extra)):
                ncluster.value+=1
                xcls_list.append(xcls.value)
                ycls_list.append(ycls.value)
                zcls_list.append(zcls.value)
                ecls_list.append(ecls.value)
                tcls_list.append(tcls.value)
                print('\033[1;35m Simulation_Manager::\033[0m'+'Event No.' + str(EVE+1)+' - Cluster No.' + str(ncluster.value) + ' contains '+str(ncls.value) + ' electrons.')
                for i in range(nel.value, nel.value+ncls.value):
                    i_c = ctypes.c_int(i-nel.value)
                    print('\033[1;35m Simulation_Manager::\033[0m'+'Tracking electron No.'+str(i_c.value))
                    self.TRACK.GetElectron(i_c.value, ex0, ey0, ez0, et0, ee0, edx0, edy0, edz0)
                    ex0_list.append(ex0.value)
                    ey0_list.append(ey0.value)
                    ez0_list.append(ez0.value)
                    ee0_list.append(ee0.value)
                    et0_list.append(et0.value)
                    
                    if ez0.value>self.DriftBoundary:
                        _PrimaryElectron_number_inDrift+=1
                    self.AVAL.AvalancheElectron(ex0, ey0, ez0, et0, ee0, edx0, edy0, edz0)
                    np = self.AVAL.GetNumberOfElectronEndpoints()
                    if np>1 and ez0.value>self.DriftBoundary:
                        _PrimaryElectron_number_inDrift_aval+=1
                    if np>1 and ez0.value<self.DriftBoundary:
                        _PrimaryElectron_number_NotinDrift_aval+=1
                    xe1 = ctypes.c_double(0.)
                    ye1 = ctypes.c_double(0.)
                    ze1 = ctypes.c_double(0.)
                    te1 = ctypes.c_double(0.)
                    ee1 = ctypes.c_double(0.)

                    xe2 = ctypes.c_double(0.)
                    ye2 = ctypes.c_double(0.)
                    ze2 = ctypes.c_double(0.)
                    te2 = ctypes.c_double(0.)
                    ee2 = ctypes.c_double(0.)
                    status = ctypes.c_int(0)
                    
                    for j in range(0,np):
                        self.AVAL.GetElectronEndpoint(j, xe1, ye1, ze1, te1, ee1, xe2, ye2, ze2, te2, ee2, status)
                        if (ze2.value < self.InductBoundary):
                            _FinalElectron_number+=1
                                       
                    
                nel.value+=ncls.value
            
            if nel.value!=0:
                ion = 1
            self.out.fillBranch("ionization",ion)
            self.out.fillBranch("PrimaryCluster_number",ncluster.value)
            xcls_list = make_list(xcls_list,self.maxPrimaryClusters)
            ycls_list = make_list(ycls_list,self.maxPrimaryClusters)
            zcls_list = make_list(zcls_list,self.maxPrimaryClusters)
            tcls_list = make_list(tcls_list,self.maxPrimaryClusters)
            ecls_list = make_list(ecls_list,self.maxPrimaryClusters)
            self.out.fillBranch("PrimaryCluster_xposition",xcls_list)
            self.out.fillBranch("PrimaryCluster_yposition",ycls_list)
            self.out.fillBranch("PrimaryCluster_zposition",zcls_list)
            self.out.fillBranch("PrimaryCluster_energy",ecls_list)
            self.out.fillBranch("PrimaryCluster_time",ecls_list)
            self.out.fillBranch("PrimaryElectron_number",nel.value)
            ex0_list = make_list(ex0_list,self.maxPrimaryEle)
            ey0_list = make_list(ey0_list,self.maxPrimaryEle)
            ez0_list = make_list(ez0_list,self.maxPrimaryEle)
            ee0_list = make_list(ee0_list,self.maxPrimaryEle)
            et0_list = make_list(et0_list,self.maxPrimaryEle)
            self.out.fillBranch("PrimaryElectron_xposition",ex0_list)
            self.out.fillBranch("PrimaryElectron_yposition",ey0_list)
            self.out.fillBranch("PrimaryElectron_zposition",ez0_list)
            self.out.fillBranch("PrimaryElectron_energy",ee0_list)
            self.out.fillBranch("PrimaryElectron_time",et0_list)
            self.out.fillBranch("PrimaryElectron_number_inDrift",_PrimaryElectron_number_inDrift)
            self.out.fillBranch("PrimaryElectron_number_inDrift_aval",_PrimaryElectron_number_inDrift_aval)
            self.out.fillBranch("PrimaryElectron_number_NotinDrift_aval",_PrimaryElectron_number_NotinDrift_aval)
            self.out.fillBranch("FinalElectron_number",_FinalElectron_number)
            if _PrimaryElectron_number_inDrift != 0 :
                self.out.fillBranch("Effective_Gain",float(_FinalElectron_number)/float(_PrimaryElectron_number_inDrift))
            else:
                self.out.fillBranch("Effective_Gain",-9.)
                
            
            
            # place for signal simulation
            
            
            self.out.fill()
        self.out.write()
        return 1
