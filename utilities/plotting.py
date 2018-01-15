#!/usr/bin/env python
#########################################
#   Title: pyephem helper utilities     #
# Project: TLE Match                    #
#    Date: Jan 2018                     #
#  Author: Zach Leffke, KJ4QLP          #
#########################################
import sys
import os
import math
import string
import struct
import numpy as np
import scipy
import datetime as dt
import pytz
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
from matplotlib.dates import DateFormatter
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import matplotlib.dates as mdates
import matplotlib.colors as colors


deg2rad = math.pi / 180
rad2deg = 180 / math.pi
c       = float(299792458)    #[m/s], speed of light


def plot_offset(idx, df, o_path, save = 0):
    a = df.name
    x = [dt.datetime.utcfromtimestamp(element*1e-9) for element in df['timestamp'].values.tolist()] #independent variable, input
    y = df['doppler_offset'].values.tolist()
    #---- START Figure 1 ----
    xinch = 14
    yinch = 7
    fig1=plt.figure(idx, figsize=(xinch,yinch/.8))
    ax1 = fig1.add_subplot(1,1,1)
    #ax2 = ax1.twinx()

    #Configure Grids
    ax1.xaxis.grid(True,'major', linewidth=1)
    ax1.yaxis.grid(True,'minor')
    ax1.yaxis.grid(True,'major', linewidth=1)
    ax1.yaxis.grid(True,'minor')

    #Configure Labels and Title
    ax1.set_xlabel('Time [UTC]')
    ax1.set_ylabel('Doppler Offset [Hz]')
    title = '{:s} Doppler Offset [Hz]'.format(a)
    ax1.set_title(title)

    #Plot Data
    ax1.plot(x, df['doppler_offset'], linestyle = '-', label="{:s}".format(a), markersize=1, markeredgewidth=0)

    #Formate X Axis Timestamps
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d\n %H:%M:%S"))
    #ax1.set_xlim(x2[0] - dt.timedelta(minutes = 30), x2[-1] +  dt.timedelta(minutes=30))

    for label in ax1.xaxis.get_ticklabels():
        label.set_rotation(45)

    fig1.subplots_adjust(bottom=0.2)

    #Configure Legend
    box = ax1.get_position()
    h1, l1 = ax1.get_legend_handles_labels()
    ax1.legend(h1, l1, loc='center left', numpoints = 1, bbox_to_anchor=(0.8, 0.85))

    #Save Figure
    if save:

        fig_f = '{:s} Doppler Offset.png'.format(a)
        fig_fp = '/'.join([o_path,fig_f])
        print "Output Path:", fig_fp
        print "Saving Figure {:2d}: {:s}".format(idx, fig_fp)
        fig1.savefig(fig_fp)

    plt.show()
    #plt.close(fig1)
    idx += 1
    return idx
