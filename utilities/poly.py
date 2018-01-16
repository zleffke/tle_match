#!/usr/bin/env python
#############################################
#   Title: Satellite utilities              #
# Project: TLE Match                        #
#    Date: Jan 2018                         #
#  Author: Zach Leffke, KJ4QLP              #
#############################################
import sys
import os
import math
import string
import struct
import numpy
import scipy
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import *

deg2rad = math.pi / 180
rad2deg = 180 / math.pi
c       = float(299792458)    #[m/s], speed of light

def Find_File_Names(path):
    #--return list of all filenames in 'folder'------------
    file_names = []
    #path =  os.getcwd() + '/' + folder + '/'
    for (dirpath, dirnames, filenames) in os.walk(path):
        file_names.extend(filenames)
        break
    file_names.sort()
    return file_names

def Find_Dir_Names(folder):
    #--return list of all subdirectories in 'folder'------------
    dir_names = []
    path =  os.getcwd() + '/' + folder + '/'
    for (dirpath, dirnames, filenames) in os.walk(path):
        dir_names.extend(dirnames)
        break
    dir_names.sort()
    return dir_names


# Polynomial Regression
def polyfit(x, y, reg_x, degree):
    results = {}
    coeffs = np.polyfit(x, y, degree)
    equation = np.polyval(coeffs, reg_x)
    results['equation'] = equation
    results['degree'] = degree
    # Polynomial Coefficients
    results['polynomial'] = coeffs.tolist()
    # r-squared
    p = np.poly1d(coeffs)
    # fit values, and mean
    yhat = p(x)                         # or [p(z) for z in x]
    ybar = np.sum(y)/len(y)          # or sum(y)/len(y)
    ssreg = np.sum((yhat-ybar)**2)   # or sum([ (yihat - ybar)**2 for yihat in yhat])
    sstot = np.sum((y - ybar)**2)    # or sum([ (yi - ybar)**2 for yi in y])
    results['determination'] = ssreg / sstot
    return results

def polydiff(x, coeffs):
    results = {}
    coeffs_prime = []
    for i in range(len(coeffs)-1):
        coeffs_prime.append(coeffs[i]*(len(coeffs) - 1 - i))
    #print len(coeffs), len(coeffs_prime)
    #print coeffs, coeffs_prime
    reg_idx = 0
    results['equation'] = np.polyval(coeffs_prime, x)
    for i in range(len(results['equation'])):
        if results['equation'][i] == min(results['equation']):
            results['min_idx'] = i
            break
    return results

def findBestFit(time_stamps, offsets, reg_x):
    #-Initialize variables---
    results = {}
    idx = 1
    r2 = 0
    reg_eq = None
    coeffs = None
    #-cycle through polyfits trying to maximize r-squared
    while 1:
        pf = polyfit(time_stamps, offsets, reg_x, idx)  #do the polyfit
        r2_last = r2    #save the previous r2 value
        r2 = pf['determination'] #get the new r2 value from most recent polyfit
        #print pf['degree'], len(pf['polynomial']), pf['determination']
        if r2 > r2_last: #compare R2 values, if current is better than previous
            #print pf['degree'], len(pf['polynomial']), pf['determination']
            results['polynomial']       = pf['polynomial'] #store coefficients
            results['equation']         = pf['equation'] #store regresseion equation
            results['degree']           = pf['degree']
            results['determination']    = pf['determination']
            idx = idx + 1 #increment polynomial degree
        else:break #if most recent R2 value is less than previous, break and keep old values.
    #os.system('clear')
    return results


def Doppler_Regression(df):
    # Input Files:
    #time_stamps = [dt.datetime.utcfromtimestamp(element*1e-9) for element in df['timestamp'].values.tolist()]

    #offsets = df['doppler_offset'].values.tolist()
    #print time_stamps
    # Read input Measurement Data Files
    #file_input(time_stamps, offsets, options.filename)
    #reg_x = np.arange(time_stamps[0], time_stamps[len(time_stamps)-1], 0.05)
    #print df['timestamp'].iloc[0], df['timestamp'].iloc[-1]
    reg_x = np.arange(df['timestamp'].iloc[0], df['timestamp'].iloc[-1], 0.05)

    #Find Best Polyfit
    #pf = findBestFit(time_stamps, offsets, reg_x)
    pf = findBestFit(df['timestamp'], df['doppler_offset'], reg_x)
    #Take Derivatives of polyfit data to find inflection point
    pd_reg = polydiff(reg_x, pf['polynomial'])
    reg_idx = pd_reg['min_idx']

    print "               Order of Polynomial with best fit: ", pf['degree']
    print "         Coefficient of Determination, R-Squared: ", pf['determination']
    print "      Time Stamp of Inflection Point, Regression: ", reg_x[reg_idx]
    print "Frequency Offset at Inflection Point, Regression: ", pf['equation'][reg_idx]

    plt.plot(time_stamps, offsets, '.') #plot original data
    plt.plot(reg_x, pf['equation'], 'r-') #plot regression curve
    plt.plot(reg_x, pd_reg['equation'], 'g-') #plot derivative curve
    plt.plot(reg_x[reg_idx], pf['equation'][reg_idx], 'r+', markersize=20) #plot PCA marker
    label = 'Time: ' + str(reg_x[reg_idx]) + ' [s],\nOffset: ' + str(pf['equation'][reg_idx]) +' [Hz]'
    plt.text(reg_x[reg_idx]+20, pf['equation'][reg_idx]+100, label)
    plt.xlabel('Time (s)')
    plt.ylabel('Doppler Offset [Hz]')
    data = options.filename.split('_')
    f_actual = 145.98e6 + pf['equation'][reg_idx]
    f_str = (str(f_actual / 1e6))[0:10]
    plt.title('AO-85 Doppler Shift, ' + str(data[1]) + '_' + str(data[2]) + '_' + str(data[3]) + '\n$f_{nom}$= 145.980 [MHz], $f_{actual}$= '+f_str+' [MHz]')
    plt.grid()
    plt.show()
