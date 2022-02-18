import ROOT as R
import os, sys
import math
import ctypes

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--multithread",       dest="multi",    default=0,     type=int,   help="enable multi-thread with n threads (default = 0)" )
parser.add_argument("-v", "--verbose",           dest="verb",     default=0,     type=int,   help="different verbose level (default = 0)" )
parser.add_argument("-b", "--batchMode",         dest="batch",    default=true,  type=bool,  help="if enable batch mode (default = true)" )
parser.add_argument("-c", "--configFile",        dest="config",   default='/afs/cern.ch/work/l/lichengz/public/simulation_2022/PyGarfield/Full_SIM_config.txt',  type=str,  help="configuration file (default = /afs/cern.ch/work/l/lichengz/public/simulation_2022/PyGarfield/Full_SIM_config.txt)" )

args = parser.parse_args()

if args.batch=true:
    R.gROOT.SetBatch(R.kTRUE)
else:
    R.gROOT.SetBatch(R.kFALSE)
    
if args.multi != 0:
    R.EnableImplicitMT(args.multi)
    print('using ' + str(args.multi) + ' threads in MT Mode!')
else:
    print('Disable MT Mode!')

path = os.getenv('GARFIELD_INSTALL')
config = 
if sys.platform == 'darwin':
    R.gSystem.Load(path + '/lib64/libmagboltz.dylib')
    R.gSystem.Load(path + '/lib64/libGarfield.dylib')
else:
    R.gSystem.Load(path + '/lib64/libmagboltz.so')
    R.gSystem.Load(path + '/lib64/libGarfield.so')

def transfer(t):
    tau=100.
    return (t/tau)**3*exp(-3*t/tau)

full_sim_result = R.TFile("full_sim_result.root","RECREATE")

gas = R.Garfield.MediumMagboltz()
gas.LoadGasFile('/afs/cern.ch/work/l/lichengz/public/simulation_2022/gas/ar_93_co2_7_3bar.gas')
gas.LoadIonMobility(path + '/share/Garfield/Data/IonMobility_Ar+_Ar.txt')

###########################
nevents = 10

###########################