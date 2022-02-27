import ROOT as R
import os, sys
import math
import ctypes
import argparse
from array import array

R.gROOT.SetBatch(R.kTRUE)

path = os.getenv('GARFIELD_INSTALL')

if sys.platform == 'darwin':
    R.gSystem.Load(path + '/lib64/libmagboltz.dylib')
    R.gSystem.Load(path + '/lib64/libGarfield.dylib')
else:
    R.gSystem.Load(path + '/lib64/libmagboltz.so')
    R.gSystem.Load(path + '/lib64/libGarfield.so')
    R.gSystem.Load(path + '/lib64/libGarfield.so')
    
full_sim_result = R.TFile("full_sim_result.root","RECREATE")
event = array('i',[0])
full_sim_result_tree = R.TTree("full_sim_result_tree","full_sim_result_tree")
full_sim_result_tree.Branch('event',event,'event/I')

nevents = 10
for EVE in range(0,nevents):
    event[0] = EVE
    full_sim_result_tree.Fill()
    
full_sim_result_tree.Write()
full_sim_result.Close()

exit(0)