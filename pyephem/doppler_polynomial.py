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

    parser.add_argument('--interp',
                        dest='interp',
                        type=float,
                        default=1.0,
                        help="Regression interpolation factor",
                        action="store")
    meas = parser.add_argument_group('Measurement Related Configurations')
    meas_fp_default = '/'.join([cwd, 'measurements'])
    meas.add_argument('--meas_json',
                        dest='meas_json',
                        type=str,
                        default='DOPPLER_FOX-1D_20180113_161201.862011_UTC_10sps.json',
                        help="Converted Doppler offset measurement file, JSON format",
                        action="store")
    meas.add_argument('--meas_csv',
                        dest='meas_csv',
                        type=str,
                        default='DOPPLER_FOX-1D_20180113_161201.862011_UTC_10sps.csv',
                        help="Converted Doppler offset measurement file, CSV format",
                        action="store")
    meas.add_argument('--meas_md',
                        dest='meas_md',
                        type=str,
                        default='DOPPLER_FOX-1D_20180113_161201.862011_UTC_10sps.md',
                        help="Measurement metadata file, JSON format",
                        action="store")
    meas.add_argument('--meas_folder',
                        dest='meas_folder',
                        type=str,
                        default=meas_fp_default,
                        help="Converted Doppler offset measurement file location",
                        action="store")

    gen = parser.add_argument_group('Generated Doppler Related Configurations')
    gen_fp_default = '/'.join([cwd, 'generated'])
    gen.add_argument('--gen_folder',
                        dest='gen_folder',
                        type=str,
                        default=gen_fp_default,
                        help="Generated Doppler measurement file location",
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

    #--Read in Measurement metadata
    fp_md = '/'.join([args.meas_folder,args.meas_md])
    if not os.path.isfile(fp_md) == True:
        print 'ERROR: invalid Measurement Metadata file: {:s}'.format(fp_md)
        sys.exit()

    print 'Importing measurement metadata from: {:s}'.format(fp_md)
    with open(fp_md, 'r') as f:
        md = json.load(f)

    for k in md.keys():
        print k, md[k]

    #Read in Doppler Measurement File
    fp_meas = '/'.join([args.meas_folder,args.meas_json])
    print 'Importing measurement metadata from: {:s}'.format(fp_meas)
    df = pd.read_json(fp_meas, orient='records')
    df.name = md['sat_name']
    df['dop_norm'] = df['doppler_offset'] / md['rx_center_freq']

    #Read in Generated Doppler Files
    gen_files = utilities.poly.Find_File_Names(args.gen_folder)
    gen_files = [ x for x in gen_files if ".csv" not in x ]

    dop_df = [] #list containing doppler data, might not be needed
    dop_df.append(df)
    for gen_f in gen_files:
        #print gen_f
        fp_gen = '/'.join([args.gen_folder,gen_f])
        if os.path.isfile(fp_gen) == True:
            print 'Importing generated doppler data from: {:s}'.format(fp_gen)
            dop_df.append(pd.read_json(fp_gen, orient='records'))
            dop_df[-1].name = gen_f.split('_')[1]
            dop_df[-1]['dop_norm'] = dop_df[-1]['doppler_offset'] / md['rx_center_freq']
            #print dop_df
        else:
            'ERROR: invalid generated doppler file: {:s}'.format(fp_gen)

    print md['rx_center_freq']


    #utilities.plotting.plot_multi_doppler_ts(0,dop_df, args.fig_path, args.fig_save)
    #utilities.poly.Doppler_Regression(df)
    poly_data = []
    for dop in dop_df:
        dop_poly = {}
        dop_poly['name'] = dop.name
        dop_poly['pf'] = utilities.poly.Doppler_Poly_Regression_idx(dop,args.interp)
        poly_data.append(dop_poly)

    print poly_data
    #fig_cnt = utilities.plotting.plot_offset(0, df, args.fig_path, args.fig_save)


    out_fp = md['sat_name'] + '.' + 'json'

    print json.dumps(poly_data, indent=4, default=json_serial)
    with open(out_fp, 'w') as outfile:
        json.dump(poly_data, outfile, indent=4, default=json_serial)

if __name__ == '__main__':
    main()
