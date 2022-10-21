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

