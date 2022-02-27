#########################################################################################
# This python project is based on Garfield++(CERN) & ROOT(CERN).                        #
# This certain code is to simulate Fe55 X-Ray test.                                     #
# First contributed by PKU-CMS GEM group 2022-02-18 Licheng ZHANG & Aera JUNG & Yue WANG#
# Author: contact L.C.ZHANG (licheng.zhang@cern.ch)                                     #
#########################################################################################

import ROOT as R
import os, sys
import math
import ctypes
import argparse
from array import array

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--multithread", dest="multi",    default=0,     type=int,   help="enable multi-thread with n threads (default = 0)" )
parser.add_argument("-v", "--verbose",     dest="verb",     default=1,     type=int,   help="different verbose level (default = 1)" )
parser.add_argument("-b", "--batchMode",   dest="batch",    default=True,  type=bool,  help="if enable batch mode (default = true)" )
parser.add_argument("-c", "--configFile",  dest="config",   default='Full_SIM_config.txt',  type=str,  help="configuration file (default = Full_SIM_config.txt)" )
args = parser.parse_args()

if args.batch == True:
    R.gROOT.SetBatch(R.kTRUE)
else:
    R.gROOT.SetBatch(R.kFALSE)
    
if args.multi != 0:
    R.EnableImplicitMT(args.multi)
    print('using ' + str(args.multi) + ' threads in MT Mode!')
else:
    print('Disable MT Mode!')

path = os.getenv('GARFIELD_INSTALL')

if sys.platform == 'darwin':
    R.gSystem.Load(path + '/lib64/libmagboltz.dylib')
    R.gSystem.Load(path + '/lib64/libGarfield.dylib')
else:
    R.gSystem.Load(path + '/lib64/libmagboltz.so')
    R.gSystem.Load(path + '/lib64/libGarfield.so')
    R.gSystem.Load(path + '/lib64/libGarfield.so')
    
## Functions
#################################################################################
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
            if args.verb > 2:
                print("Following line is commented and will be removed:")
                print(line)
    return cleanedLines

def MakeConfigMap(lines):
    if args.verb > 0: print('\033[1;32m Making Config Map... \033[0m')
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
    if args.verb > 2:
        print(filelines)
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
        if "WeightingField" in settings.keys():
            weightFile = []
            for fileName in os.listdir(settings["WeightingField"]):
                weightFile.append(fileName+'/ELIST.lis')
            #end
            for i in range(1,len(weightFile)+1):
                fm.SetWeightingField(settings["WeightingField"]+weightFile[i-1],'readout'+str(i))
                print('Link '+weightFile[i-1]+' to '+'readout'+str(i))
            #end
        else:
            print('\033[1;31m WARNING:: \033[0m Weighting fields do not been set, signals cannot be calculated, please double check!')
        fm.EnablePeriodicityX()
        fm.EnablePeriodicityY()
        if args.verb>0:
            fm.PrintRange()
        nMaterials = fm.GetNumberOfMaterials()
        for i in range(0,nMaterials):
            eps = fm.GetPermittivity(i)
            if (abs(eps - 1.) < 1.e-3):
                fm.SetMedium(i, gas)
        #end
        if args.verb>0:
            fm.PrintMaterials()
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
    else:
        incidentpart = 'photon'
        print("\033[1;31m ERROR:: \033[0m Incident particle does not been set. default is X-Ray photon")
    
    return gas,fm,len(weightFile),lowerbound,upperbound,incidentpart

def TransferFunction(t):
    tau=100.
    return (t/tau)**3*math.exp(-3*t/tau)

#################################################################################

config_file = args.config
pitch = 0.014 # cm
nstrip = 1 # number of readout strips
lowerbound = -0.0030
upperbound = 1.3040
SOURCE = 'photon'

###########################
GAS = R.Garfield.MediumMagboltz()
FM = R.Garfield.ComponentAnsys123()
SENSOR = R.Garfield.Sensor()
DRIFT = R.Garfield.AvalancheMC()
AVAL = R.Garfield.AvalancheMicroscopic()
TRACK = R.Garfield.TrackHeed()
###########################licheng

GAS,FM,nstrip,lowerbound,upperbound,SOURCE = ReadTextFile(config_file)

GAS.LoadIonMobility(path + '/share/Garfield/Data/IonMobility_Ar+_Ar.txt')

times = R.std.vector('double')()
values = R.std.vector('double')()
for i in range(0,1000):
    times.push_back(1.e3 * float(i))
    values.push_back(float(TransferFunction(1.e3 * float(i))))
SENSOR.SetTransferFunction(times, values)
SENSOR.AddComponent(FM)
for i in range(1,nstrip+1):
    SENSOR.AddElectrode(FM,"readout"+str(i))
SENSOR.SetArea(-20 * pitch, -20 * pitch, lowerbound, 20 * pitch,  20 * pitch, upperbound)
tmin = 0.
tmax = 1000.
tstep = 0.5
nTimeBins = int((tmax - tmin) / tstep)
SENSOR.SetTimeWindow(tmin, tstep, nTimeBins)

DRIFT.SetSensor(SENSOR)
DRIFT.SetDistanceSteps(0.0005)
DRIFT.EnableRKFSteps(True)
DRIFT.SetTimeWindow(0, 1000)

AVAL.SetSensor(SENSOR)
AVAL.EnableSignalCalculation()
AVAL.EnableMagneticField()
# AVAL.DisableAvalancheSizeLimit()
AVAL.EnableAvalancheSizeLimit(2)

TRACK.SetSensor(SENSOR)
TRACK.EnableElectricField()

###########################
nevents = 10

###########################
full_sim_result = R.TFile("full_sim_result.root","RECREATE")

### Variables
event = array('i',[0])
ionization = array('i',[0])

Incident_xposition = array('f',[0])
Incident_yposition = array('f',[0])
Incident_zposition = array('f',[0])
Incident_dx = array('f',[0])
Incident_dy = array('f',[0])
Incident_dz = array('f',[0])
Incident_energy = array('f',[0])

PrimaryElectron_number = array('i',[0])
maxPrimaryEle = 800
PrimaryElectron_energy = array('f',maxPrimaryEle*[0])
PrimaryElectron_time = array('f',maxPrimaryEle*[0])
PrimaryElectron_zposition = array('f',maxPrimaryEle*[0])
PrimaryElectron_xposition = array('f',maxPrimaryEle*[0])
PrimaryElectron_yposition = array('f',maxPrimaryEle*[0])

PrimaryElectron_number_inDrift = array('i',[0]) # primary electron generated in the drift region
PrimaryElectron_number_inDrift_aval = array('i',[0]) # primary electron generated in the drift region and avalanched

FinalElectron_number = array('i',[0])

maxTimeBins = 2000
time_bin = array('i',[0])
V_sig = []
for i in range(0,nstrip):
    V_sig.append(array('f',maxTimeBins*[0]))
#end
V_sig_tot = array('f',maxTimeBins*[0])
V_sig_max = array('f',[0])
### Variables


full_sim_result_tree = R.TTree("full_sim_result_tree","full_sim_result_tree")
full_sim_result_tree.Branch('event',event,'event/I')
full_sim_result_tree.Branch('ionization',ionization,'ionization/I')

full_sim_result_tree.Branch('Incident_xposition',Incident_xposition,'Incident_xposition/F')
full_sim_result_tree.Branch('Incident_yposition',Incident_yposition,'Incident_yposition/F')
full_sim_result_tree.Branch('Incident_zposition',Incident_zposition,'Incident_zposition/F')
full_sim_result_tree.Branch('Incident_dx',Incident_dx,'Incident_dx/F')
full_sim_result_tree.Branch('Incident_dy',Incident_dy,'Incident_dy/F')
full_sim_result_tree.Branch('Incident_dz',Incident_dz,'Incident_dz/F')
full_sim_result_tree.Branch('Incident_energy',Incident_energy,'Incident_energy/F')

full_sim_result_tree.Branch('PrimaryElectron_number',PrimaryElectron_number,'PrimaryElectron_number/I')
full_sim_result_tree.Branch('PrimaryElectron_energy',PrimaryElectron_energy,'PrimaryElectron_energy[PrimaryElectron_number]/F')
full_sim_result_tree.Branch('PrimaryElectron_time',PrimaryElectron_time,'PrimaryElectron_time[PrimaryElectron_number]/F')
full_sim_result_tree.Branch('PrimaryElectron_zposition',PrimaryElectron_zposition,'PrimaryElectron_zposition[PrimaryElectron_number]/F')
full_sim_result_tree.Branch('PrimaryElectron_xposition',PrimaryElectron_xposition,'PrimaryElectron_xposition[PrimaryElectron_number]/F')
full_sim_result_tree.Branch('PrimaryElectron_yposition',PrimaryElectron_yposition,'PrimaryElectron_yposition[PrimaryElectron_number]/F')

full_sim_result_tree.Branch('PrimaryElectron_number_inDrift',PrimaryElectron_number_inDrift,'PrimaryElectron_number_inDrift/I')
full_sim_result_tree.Branch('PrimaryElectron_number_inDrift_aval',PrimaryElectron_number_inDrift_aval,'PrimaryElectron_number_inDrift_aval/I')
full_sim_result_tree.Branch('FinalElectron_number',FinalElectron_number,'FinalElectron_number/I')

full_sim_result_tree.Branch('time_bin',time_bin,'time_bin/I')

full_sim_result_tree.Branch('V_sig_max',V_sig_max,'V_sig_max/F')
for i in range(0,nstrip):
    full_sim_result_tree.Branch('V_sig_'+str(i+1),V_sig[i],'V_sig_'+str(i+1)+'[time_bin]/F')
#end

# looping!
for EVE in range(0,nevents):
    print('+++++++++' + 'Event No. ' + str(EVE+1)+' of ' + str(nevents))
    event[0] = EVE+1
    
    x0 = 0.0390 -2 * pitch + 4 * R.Garfield.RndmUniform() * pitch
    y0 = 0.0066  + 1 * math.sqrt(3) * pitch * R.Garfield.RndmUniform()
    z0 = upperbound-0.0001
    e0 = 5900 #eV
    t0 = 0.
# double phi = r->Uniform(-0.5,0.5) * 3.1415927 / 2;
# double theta = r->Uniform(-1,1) * 3.1415927;
# double dx0 = sin(phi)*cos(theta);
# double dy0 = sin(phi)*sin(theta);
# double dz0 = -cos(phi);

    track_dx = 0.
    track_dy = 0.
    track_dz = -1.
    
    Incident_xposition[0] = x0
    Incident_yposition[0] = y0
    Incident_zposition[0] = z0
    Incident_energy[0] = e0
    Incident_dx[0] = track_dx
    Incident_dy[0] = track_dy
    Incident_dz[0] = track_dz
    
    nel = ctypes.c_int(0)
    
    TRACK.TransportPhoton(x0, y0, z0, t0, e0, track_dx, track_dy, track_dz, nel)
    PrimaryElectron_number[0] = nel.value
    print('Event No. ' + str(EVE+1)+' generates ' + str(nel.value) + ' Primary Electron')
    _PrimaryElectron_number_inDrift = 0
    _PrimaryElectron_number_inDrift_aval = 0
    _FinalElectron_number = 0
    
    if(nel.value==0):
        ion = 0
        ionization[0] = ion
    else:
        ion = 1
        ionization[0] = ion
        ex0 = ctypes.c_double(0.)
        ey0 = ctypes.c_double(0.)
        ez0 = ctypes.c_double(0.)
        ee0 = ctypes.c_double(0.)
        et0 = ctypes.c_double(0.)
        edx0 = ctypes.c_double(0.)
        edy0 = ctypes.c_double(0.)
        edz0 = ctypes.c_double(0.)

        for i in range(0,nel.value):
            print('Tracking No. ' + str(i+1) + ' Primary Electron')
            i_c = ctypes.c_int(i)
            TRACK.GetElectron(i_c.value, ex0, ey0, ez0, et0, ee0, edx0, edy0, edz0)
            PrimaryElectron_zposition[i] = ez0.value
            PrimaryElectron_yposition[i] = ey0.value
            PrimaryElectron_xposition[i] = ex0.value
            PrimaryElectron_time[i] = et0.value
            PrimaryElectron_energy[i] = ee0.value
            
            if(ez0.value>0.4240):
                _PrimaryElectron_number_inDrift+=1
            AVAL.AvalancheElectron(ex0, ey0, ez0, et0, ee0, edx0, edy0, edz0)
            np = AVAL.GetNumberOfElectronEndpoints()
            if np>1 and ez0.value>0.4240:
                _PrimaryElectron_number_inDrift_aval+=1
            
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
                AVAL.GetElectronEndpoint(j, xe1, ye1, ze1, te1, ee1, xe2, ye2, ze2, te2, ee2, status)
                if (ze2.value < 0.1000):
                    _FinalElectron_number+=1
                #endif
            #end loop
        #end loop
    #endif
    PrimaryElectron_number_inDrift[0] = _PrimaryElectron_number_inDrift
    PrimaryElectron_number_inDrift_aval[0] = _PrimaryElectron_number_inDrift_aval
    FinalElectron_number[0] = _FinalElectron_number
    
    SENSOR.ConvoluteSignals()
    for i in range(0,nstrip):
        V_sig[i] = array('f',maxTimeBins*[0])
    #end
    
    time_bin[0] = maxTimeBins
    
    _temp_sig_max = 0.
    for _t in range(0,maxTimeBins):
        _temp_sig_total = 0.
        for _s in range(1,nstrip+1):
            V_sig[_s-1][_t] = -SENSOR.GetSignal("readout"+str(_s), _t + 1)
            _temp_sig_total += V_sig[_s-1][_t]
        #end
        V_sig_tot[_t] = _temp_sig_total
        if _temp_sig_total>_temp_sig_max:
            _temp_sig_max = _temp_sig_total
    #end
    V_sig_max[0] = _temp_sig_max
    SENSOR.ClearSignal()
    full_sim_result_tree.Fill()
#endloop
full_sim_result_tree.Write()
# full_sim_result.Close()

exit(0)