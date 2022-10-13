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

def TransferFunction(t):
    tau=100.
    return (t/tau)**3*math.exp(-3*t/tau)

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
