#########################################################################################
# This python project is based on Garfield++(CERN) & ROOT(CERN).                        #
# This certain code is to simulate Fe55 X-Ray test.                                     #
# First contributed by PKU-CMS GEM group 2022-02-18 Licheng ZHANG & Aera JUNG & Yue WANG#
# Author: contact L.C.ZHANG (licheng.zhang@cern.ch)                                     #
#########################################################################################
# It is fully hard coding. Will be more flexiable and the figure will be more elegent, if I remember.

import ROOT as R
import os, sys
import math
import ctypes
import argparse
from multiprocessing import Pool

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--multithread", dest="multi",    default=0,     type=int,   help="enable multi-thread with n threads (default = 0)" )
parser.add_argument("-v", "--verbose",     dest="verb",     default=1,     type=int,   help="different verbose level (default = 1)" )
parser.add_argument("-b", "--batchMode",   dest="batch",    default=True,  type=bool,  help="if enable batch mode (default = true)" )
parser.add_argument("-e", "--EField",      dest="ef",       default="../FieldExample/SingleGEM/",  type=str,  help="path to Electric Field file (default = ../FieldExample/SingleGEM/)" )
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

fm = R.Garfield.ComponentAnsys123()
fmpath = os.path.abspath(args.ef)
fm.Initialise(fmpath+"/ELIST.lis",fmpath+"/NLIST.lis",\
              fmpath+"/MPLIST.lis",fmpath+"/PRNSOL.lis","mm") #the unit adopted by ANSYS15.0 is mm
fm.EnableMirrorPeriodicityX()
fm.EnableMirrorPeriodicityY()
fm.PrintRange()
# exit(0)
# nMaterials = fm.GetNumberOfMaterials()
# for i in range(0,nMaterials):
#     eps = fm.GetPermittivity(i)
#     if (abs(eps - 1.) < 1.e-3):
#         fm.SetMedium(i, gas)
# fm.PrintMaterials()

# sensor = R.Garfield.Sensor()
# sensor.AddComponent(fm)

pitch = 0.0140
# sensor.SetArea(-3 * pitch, -3 * pitch, -0.0030, 3 * pitch,  3 * pitch, 1.3040)

ex=ctypes.c_double(0.)
ey=ctypes.c_double(0.)
ez=ctypes.c_double(0.)
v=ctypes.c_double(0.)
med = R.Garfield.Medium()
stat = ctypes.c_int(0)

lowerbound = -0.1000
upperbound =  0.1000

pixal1 = 400
pixal2 = 400

x = 0.
y = 0.02
z = 0.

hxz = R.TH2D("XZ_field","E field", pixal1, -3 * pitch, 3 * pitch, pixal2, lowerbound, upperbound)
for ix in range(0,pixal1):
    for iz in range(0,pixal2):
        x = (3 * pitch--3 * pitch)*ix/pixal1+-3 * pitch
        z = (upperbound-lowerbound)*iz/pixal2+lowerbound
        fm.ElectricField(x,y,z,ex,ey,ez,v,med,stat)
#         hxz.SetBinContent(ix+1,iz+1,math.sqrt(ex.value**2+ey.value**2+ez.value**2))
        hxz.SetBinContent(ix+1,iz+1,ez.value)
c = R.TCanvas('field','field',900,600)
c.SetRightMargin(0.15)
R.gStyle.SetOptStat(0000)
hxz.Draw('colz4')
c.SaveAs('./XZ_EField.png')

hxz = R.TH2D("XZ_Volt","Potential", pixal1, -3 * pitch, 3 * pitch, pixal2, lowerbound, upperbound)
for ix in range(0,pixal1):
    for iz in range(0,pixal2):
        x = (3 * pitch--3 * pitch)*ix/pixal1+-3 * pitch
        z = (upperbound-lowerbound)*iz/pixal2+lowerbound
        fm.ElectricField(x,y,z,ex,ey,ez,v,med,stat)
        hxz.SetBinContent(ix+1,iz+1,v)
#         hxz.SetBinContent(ix+1,iz+1,math.sqrt(ex.value**2+ey.value**2+ez.value**2))
#         hxz.Fill(x,z,ez)
c = R.TCanvas('potential','potential',900,600)
c.SetRightMargin(0.15)
R.gStyle.SetOptStat(0000)
hxz.Draw('colz4')
c.SaveAs('./XZ_Potential.png')

z = 0.0026

hxy = R.TH2D("XY_field","E field", pixal1, -3 * pitch, 3 * pitch, pixal1, -3 * pitch, 3 * pitch)
for ix in range(0,pixal1):
    for iy in range(0,pixal1):
        x = (3 * pitch--3 * pitch)*ix/pixal1+-3 * pitch
        y = (3 * pitch--3 * pitch)*iy/pixal1+-3 * pitch
        fm.ElectricField(x,y,z,ex,ey,ez,med,stat)
        hxy.SetBinContent(ix+1,iy+1,math.sqrt(ex.value**2+ey.value**2+ez.value**2))
c = R.TCanvas()
c.SetRightMargin(0.15)
R.gStyle.SetOptStat(0000)
hxy.Draw('colz4')
c.SaveAs('./XY_EField.png')
    
