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

from Simulation_Manager import Simulation_Manager, env
from Functions import TransferFunction

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--multithread", dest="multi",    default=0,     type=int,   help="enable multi-thread with n threads (default = 0)" )
parser.add_argument("-v", "--verbose",     dest="verb",     default=2,     type=int,   help="different verbose level (default = 1)" )
parser.add_argument("-b", "--batchMode",   dest="batch",    default=True,  type=bool,  help="if enable batch mode (default = true)" )
parser.add_argument("-c", "--configFile",  dest="config",   default='Full_SIM_config.txt',  type=str,  help="configuration file (default = Full_SIM_config.txt)" )
parser.add_argument("-n", "--outFileName", dest="name",     default='xray',  type=str,  help="The name of the output root file (default = xray)" )
parser.add_argument("-e", "--nEvent",      dest="neve",     default=10,  type=int,  help="Event number in the loop (default = 10)" )
args = parser.parse_args()

def main():
    env(args.batch,args.multi)
    
    SM = Simulation_Manager(args.config,args.name)
    SM.GAS.LoadIonMobility('../gas/IonMobility_Ar+_Ar.txt')
    if args.verb>1:
        SM.print_fm_info()
    SM.import_transferfunction(TransferFunction)
    if SM.Nstrip!=0: # only if we have readout boards simulated. (by weighting fields)
        SM.link_readouts()
    SM.set_sensitive_space_time(-50 * SM.pitch, -50 * SM.pitch, -0.1000, 50 * SM.pitch,  50 * SM.pitch, 0.1000, 0, 1000, 0.5)
    ###########################
    nevents = 10
    nevents = args.neve
    ###########################
    
    SM.quanlity_producer(SM.Nstrip)
    
    success = 0
    if SM.SOURCE == 'photon':
        success = SM.photon_loop(nevents)
    elif SM.SOURCE in SM.allowed_particle:
        success = SM.particle_loop(nevents)
    else:
        print("\033[1;31m ERROR::\033[0m The simulation of the input source {0} have not been optimized, EXITING!".format(SM.SOURCE))
        return 0
    
    if success == 1:
        print("\033[1;32m SUCCESS::\033[0m The simulation is succeeded, so long ^_^")
    else:
        print("\033[1;31m ERROR::\033[0m Something was wrong in the simulation please check carefully, EXITING!")
    return 0
    
if __name__ == '__main__':
    main()
    