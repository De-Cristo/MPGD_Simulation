import numpy as np
import awkward as ak
import matplotlib.pyplot as plt
import uproot as u
from plot_vars import *
import os
import sys
import argparse

import boost_histogram as bh
import mplhep as hep

import pandas as pd
from sklearn.metrics import roc_curve, roc_auc_score
from scipy.interpolate import InterpolatedUnivariateSpline

from matplotlib.ticker import AutoMinorLocator

def plot_manager(args):
    print(args[1])
#     data = ak.flatten(args[0].array(), axis=None)
    if args[3] == False:
        plot_histo(args[1], args[0], args[2])
    else:
        plot_2d_scatter(args[1], args[0], args[4], args[2])
    

def save_plot_batch( plot_str ):
    plt.savefig(plot_str)
    plt.show()
    plt.close()

def plot_histo(var, data, outDir):
    plt.style.use(hep.style.ROOT)
    
    n, binning, patch = plt.hist(data,
             color='r', 
             alpha=0.5, 
             bins = plot_configs[var]["bins"],
             log = plot_configs[var]["log"],
             histtype='stepfilled', 
             density=False,
             label='{}'.format(var))
#     scale = len(data) / sum(n)
    scale = 1
#     err   = np.sqrt(n * scale) / scale
    err = []
    for _n in n:
        if _n > 0: err.append(scale / np.sqrt(_n * scale))
        else: err.append(0)
#     err   = scale / np.sqrt(n * scale)
    err = np.array(err)
    width = (binning[1] - binning[0])
    center = (binning[:-1] + binning[1:]) / 2
    plt.errorbar(center, n, yerr=err, fmt=' ', c='b', ecolor='b', elinewidth=2, alpha = 0.8)
    
    overflow_default = "NULL"
    underflow_default = "NULL"
    default = "NULL"
    if plot_configs[var].get("underflow",False) is not False:
        underflow_default = plot_configs[var]["underflow"]
        default = underflow_default
    elif plot_configs[var].get("overflow",False) is not False:
        overflow_default = plot_configs[var]["overflow"]
        default = overflow_default
        
    overflow = 0
    underflow = 0
    over = plot_configs[var]["bins"][-1]
    under = plot_configs[var]["bins"][0]
    for ele in data:
        if ele > over:
            overflow+=1
            if ele == overflow_default:
                overflow-=1
        if ele < under:
            underflow+=1
            if ele == underflow_default:
                underflow-=1
    plt.legend(loc='best',frameon=True,edgecolor='blue',facecolor='blue') 
    plt.legend()
    plt.xlabel('[MAX={1} , MIN={2}, default = {3}] {0}'.format(var,str(np.max(data)),str(np.min(data)),str(default)),fontsize=16)
    plt.ylabel("Events [Events = {0}, Inrange = {1}, overflow = {2} , underflow = {3} range({4},{5})]".format(len(data),str(sum(n)),str(overflow),str(underflow),str(under),str(over)),fontsize=14)
    plt.subplots_adjust(left=0.15)
    save_plot_batch('{0}/{1}.png'.format(outDir,var))
    
def plot_2d_scatter(plot_name, data1, data2, outDir):
    plt.style.use(hep.style.ROOT)
    
    fig=plt.figure()
    axes=fig.add_subplot(111)
    typep1=axes.scatter(data1,data2,c='y',marker='o',s=1.)
    plt.xlim(twod_plots[plot_name][2],twod_plots[plot_name][3])
    plt.ylim(twod_plots[plot_name][4],twod_plots[plot_name][5])
    plt.xlabel(twod_plots[plot_name][0],fontsize=14)
    plt.ylabel(twod_plots[plot_name][1],fontsize=14)
    plt.subplots_adjust(left=0.15)
    # axes.legend((typep1,typen1),('positive','negative'))
    save_plot_batch('{0}/{1}.png'.format(outDir,plot_name))    
    
    
def plot_comparison_manager(args): #arguement = [array1, array2, _var, ourDir, 'local', 'condor']
    var = args [-4]
    outDir = args [-3]
    print(var)
    
    plt.style.use(hep.style.ROOT)
    
    fig, ax = plt.subplots(2, 1, gridspec_kw={'height_ratios': [3, 1]})
    fig.subplots_adjust(hspace=0)
    
    data = args[0]
    label1 = args[-2]
    n1, binning, patch = ax[0].hist(data,
             color='r', 
             alpha=0.5, 
             bins = plot_configs[var]["bins"],
             log = plot_configs[var]["log"],
             histtype='stepfilled', 
             density=True,
             label='{}'.format(label1))
    scale = len(data) / sum(n1)
    err1   = np.sqrt(n1 * scale) / scale
    width = (binning[1] - binning[0])/2
    center = (binning[:-1] + binning[1:]) / 2
    ax[0].errorbar(center, n1, yerr=err1, fmt='', c='r', alpha = 0.8)
    
    data = args[1]
    label2 = args[-1]
    n2, binning, patch = ax[0].hist(data,
             color='b', 
             alpha=0.5, 
             bins = plot_configs[var]["bins"],
             log = plot_configs[var]["log"],
             histtype='stepfilled', 
             density=True,
             label='{}'.format(label2))
    scale = len(data) / sum(n2)
    err2   = np.sqrt(n2 * scale) / scale
    width = (binning[1] - binning[0])/2
    center = (binning[:-1] + binning[1:]) / 2
    ax[0].errorbar(center, n2, yerr=err2, fmt='', c='b', alpha = 0.8)
    
    ax[0].legend(loc='best',frameon=True,edgecolor='blue',facecolor='blue') 
    ax[0].legend()
    ax[0].set_xlabel('{}'.format(var),fontsize=16)
    ax[0].set_ylabel("Arbitrary Units; [{0} = {1}; {2} = {3}] ".format(label1,len(args[0]),label2,len(args[1])),fontsize=16)
    
    ratio = n2/(n1+1e-9)
    ratio_error = np.sqrt(err2**2+err1**2)
    ax[1].errorbar(
        center,
        ratio,
        xerr=width,
        yerr=ratio_error,
        color="black",
        ecolor="r",
        linestyle="None",
        marker=None,
    )
    ax[1].axhline(y=1.0, linestyle="dashed", color="grey", alpha=0.5)
    ax[1].xaxis.set_minor_locator(AutoMinorLocator())
    ax[1].tick_params(which='minor', length=4, color='black')
    ax[1].set_ylabel(
        "$\\frac{{{0}}}{{{1}}}$".format(args[5], args[4])
    )
    ax[1].set_xlabel('{}'.format(var),fontsize=16)
    save_plot_batch('{0}/{1}.png'.format(outDir,var))
    
    
def spit_out_roc(disc,truth_array,selection_array):
    newx = np.logspace(-3.5, 0, 100)
    tprs = pd.DataFrame()
    truth = truth_array[selection_array]*1
    disc = disc[selection_array]
    tmp_fpr, tmp_tpr, _ = roc_curve(truth, disc)
    coords = pd.DataFrame()
    coords['fpr'] = tmp_fpr
    coords['tpr'] = tmp_tpr
    clean = coords.drop_duplicates(subset=['fpr'])
    spline = InterpolatedUnivariateSpline(clean.fpr, clean.tpr,k=1)
    tprs = spline(newx)
    return tprs, newx