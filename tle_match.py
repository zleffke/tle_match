#!/usr/bin/env python
#########################################
#   Title: TLE Match                    #
# Project: Multiple                     #
#    Date: Jan 2018                     #
#  Author: Zach Leffke, KJ4QLP          #
#########################################
import os
import sys
import math
import ephem
import argparse
import json
import datetime as dt

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


import utilities.satellite
import utilities.plotting
import utilities.poly
#from utilities import *

deg2rad = math.pi / 180
rad2deg = 180 / math.pi

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, dt.datetime):
        return obj.__str__()
    raise TypeError ("Type %s not serializable" % type(obj))

def main():
    """ Main entry point """
    os.system('reset')
    startup_ts = dt.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    cwd = os.getcwd()
    #--------START Command Line argument parser------------------------------------------------------
    parser = argparse.ArgumentParser(description="TLE Doppler Match",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)


    parser.add_argument('--pd_file',
                        dest='pd_file',
                        type=str,
                        default='FOX-1D.json',
                        help="Polynomial Data JSON File",
                        action="store")

    plot = parser.add_argument_group('Plotting Related Configurations')
    fig_fp_default = '/'.join([cwd, 'figures'])
    plot.add_argument('--fig_path',
                        dest='fig_path',
                        type=str,
                        default=fig_fp_default,
                        help="Folder location for saved figures",
                        action="store")
    plot.add_argument('--fig_save',
                        dest='fig_save',
                        type=int,
                        default=0,
                        help="Save Figure Flag, 0=N, 1=Y",
                        action="store")

    args = parser.parse_args()
    #--------END Command Line argument parser------------------------------------------------------
    import warnings
    warnings.filterwarnings('ignore')

    #--Read in polynomial data

    if not os.path.isfile(args.pd_file) == True:
        print 'ERROR: invalid Measurement Metadata file: {:s}'.format(args.pd_file)
        sys.exit()

    print 'Importing measurement metadata from: {:s}'.format(args.pd_file)
    with open(args.pd_file, 'r') as f:
        poly_data = json.load(f)


    reg_x = np.arange(0,5000)
    for idx, pd in enumerate(poly_data):
        #print pd['pf']['polynomial']
        ts_format = "%Y-%m-%d %H:%M:%S.%f"
        pd['pf']['tca_utc'] = dt.datetime.strptime(pd['pf']['tca_utc'],ts_format)
        reg_x = np.arange(0,pd['pf']['len_reg_x'])
        pd['pf']['equation'] = np.polyval(pd['pf']['polynomial'], reg_x)
        #print pd['pf']['equation']


    print len(poly_data)
    meas_sat = poly_data.pop(0)
    print len(poly_data)
    print meas_sat['name']
    for idx, pd in enumerate(poly_data):
        tca_delta = (meas_sat['pf']['tca_utc']-pd['pf']['tca_utc']).total_seconds()
        pd['tca_delta'] = tca_delta
        print pd['tca_delta']
        #fig_idx = utilities.plotting.plot_2poly_ts(0, reg_x, \
        #                                        meas_sat, \
        #                                        pd, \
        #                                        args.fig_path,0)

    tle_match = None
    last_delta = 1e6
    for idx, pd in enumerate(poly_data):
        if abs(pd['tca_delta']) < last_delta:
            last_delta = abs(pd['tca_delta'])
            tle_match = pd
    print tle_match['tca_delta']
    print 'Matching Satellite for {:s} is: {:s}'.format(meas_sat['name'], tle_match['name'])
    print 'TCA Delta of matching satellite [s]: {:3.3f}'.format(tle_match['tca_delta'])


if __name__ == '__main__':
    main()
