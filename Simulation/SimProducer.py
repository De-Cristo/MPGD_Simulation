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

def SimProducer(dosig):
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
    maxPrimaryEle = 1000
    PrimaryElectron_energy = array('f',maxPrimaryEle*[0])
    PrimaryElectron_time = array('f',maxPrimaryEle*[0])
    PrimaryElectron_zposition = array('f',maxPrimaryEle*[0])
    PrimaryElectron_xposition = array('f',maxPrimaryEle*[0])
    PrimaryElectron_yposition = array('f',maxPrimaryEle*[0])

    PrimaryElectron_number_inDrift = array('i',[0]) # primary electron generated in the drift region
    PrimaryElectron_number_inDrift_aval = array('i',[0]) # primary electron generated in the drift region and avalanched

    FinalElectron_number = array('i',[0])


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

    if dosig == 0:
        print("\033[1;35m Quality_Producer::There will be no time or readout signals because readout board not set.:\033[0m")
    else:
        maxTimeBins = 2000
        time_bin = array('i',[0])
        V_sig = []
        for i in range(0,dosig):
            V_sig.append(array('f',maxTimeBins*[0]))
        #end
        V_sig_tot = array('f',maxTimeBins*[0])
        V_sig_max = array('f',[0])
        full_sim_result_tree.Branch('time_bin',time_bin,'time_bin/I')
        full_sim_result_tree.Branch('V_sig_max',V_sig_max,'V_sig_max/F')
        full_sim_result_tree.Branch('V_sig_tot',V_sig_tot,'V_sig_tot[time_bin]/F')
        for i in range(0,dosig):
            full_sim_result_tree.Branch('V_sig_'+str(i+1),V_sig[i],'V_sig_'+str(i+1)+'[time_bin]/F')
        #end
    return full_sim_result_tree,0

def generate_spectrum_Ru(SEED):
    # generate specific energy spectrum. This time: Ru106
    _max = 0.001891
    _r = R.TRandom3(SEED*2)
    while(1):
        _energy = _r.Uniform(0,4) # (0,4)MeV electron energy
        _prob   = _r.Uniform(0,1) * _max
        _limit  = 0.000499266 + 0.00139833 * _energy + 0.00092349 * pow(_energy,2) - 0.00148737 * pow(_energy,3) + 0.000551184 * pow(_energy,4) - 8.79583e-05 * pow(_energy,5) + 5.73446e-06 * pow(_energy,6)
        if (_prob<_limit and _energy<=3.5):
            return _energy * 1000000
        else:
            continue
            