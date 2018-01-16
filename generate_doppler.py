#!/usr/bin/env python
#################################################
#   Title: Generate Doppler
# Project: TLE Match
#    Date: Jan 2018
#  Author: Zach Leffke, KJ4QLP
#    Desc:
#       Generates Doppler Curve data from list of TLE files and saves
#       doppler date for later use
#################################################
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

import utilities.pyephem
import utilities.satellite
import utilities.plotting
#from utilities import *

deg2rad = math.pi / 180
rad2deg = 180 / math.pi

def main():
    """ Main entry point """
    os.system('reset')
    startup_ts = dt.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    cwd = os.getcwd()
    #--------START Command Line argument parser------------------------------------------------------
    parser = argparse.ArgumentParser(description="Generates Doppler Curves from TLE list, \
                                        uses measurement metadata to derive required parameters",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    tle = parser.add_argument_group('TLE related configurations')
    tle_fp_default = '/'.join([cwd, 'tle'])
    tle.add_argument('--tle_file',
                    dest='tle_file',
                    type=str,
                    default='pslv40_st.tle',
                    help="TLE File of candidate satellites",
                    action="store")
    tle.add_argument('--tle_folder',
                    dest='tle_folder',
                    type=str,
                    default=tle_fp_default,
                    help="Folder containing TLE file",
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
    gen.add_argument('--gen_json',
                        dest='gen_json',
                        type=str,
                        default=None,
                        help="Generated Doppler offset measurement file, JSON format",
                        action="store")
    gen.add_argument('--gen_csv',
                        dest='gen_csv',
                        type=str,
                        default=None,
                        help="Generated Doppler offset measurement file, CSV format",
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
    #with open

    #--Read in TLE Files--
    tle = utilities.pyephem.tle_file_input(args.tle_folder, args.tle_file)
    #print tle

    #--create list of satellite objects with pyephem--
    sats = [] #list of satellite objects
    for sat in tle.keys():
        ephem_sat = ephem.readtle(sat, tle[sat]['line1'], tle[sat]['line2'])
        norad_id = tle[sat]['line1'][2:7]
        sats.append(utilities.satellite.satellite(ephem_sat,sat, norad_id))

    #--create ground station object with pyephem--
    gs = ephem.Observer()
    gs.lat, gs.lon, gs.elevation =  md['gs_lat']*deg2rad, \
                                    md['gs_lon']*deg2rad, \
                                    md['gs_alt']

    #Read in Doppler Measurement File
    #This data is needed to get the relevant time stamps
    fp_meas = '/'.join([args.meas_folder,args.meas_json])
    print 'Importing measurement metadata from: {:s}'.format(fp_meas)
    df = pd.read_json(fp_meas, orient='records')
    df.name = md['sat_name']

    dopplers = [] #list containing doppler data, might not be needed
    for sat in sats:
        print "Generating Doppler data for {:s}_{:s}".format(sat.sat_name, sat.norad_id)
        print "Downlink Center Freq [MHz]: {:3.6f}".format(md['rx_center_freq']/1e6)
        dop_df = sat.gen_doppler(   gs, \
                                    df['timestamp'].values.tolist(), \
                                    md['rx_center_freq'])

        dopplers.append(dop_df)

    for dop in dopplers:
        ts = dop['timestamp'][0].strftime("%Y%m%d_%H%M%S.%f_UTC")
        fn = '_'.join(['DOPPLER', dop.name, ts, md['samp_rate_str']])
        fp_json = '/'.join([args.gen_folder,fn]) + '.json'
        fp_csv  = '/'.join([args.gen_folder,fn]) + '.csv'

        #--Export JSON Doppler File
        print "Exporting JSON Doppler Measurement File: {:s}".format(fp_json)
        dop.to_json(fp_json, \
                    orient='records', \
                    date_format='iso', \
                    date_unit = 'us')

        #--Export CSV Doppler File
        print " Exporting CSV Doppler Measurement File: {:s}".format(fp_csv)
        dop.to_csv( fp_csv, \
                    index_label ="index", \
                    float_format="%.10f", \
                    date_format='%Y-%m-%dT%H:%M:%S.%fZ')






if __name__ == '__main__':
    main()
