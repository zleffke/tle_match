#!/usr/bin/env python
#################################################
#   Title: Convert GR Doppler
# Project: TLE Match
#    Date: Jan 2018
#  Author: Zach Leffke, KJ4QLP
#    Desc:
#       Converts GNU Radio based Doppler offset measurements into a json
#       object for use with other scripts
#################################################
import os
import sys
import math
import json
import argparse
import datetime as dt

import utilities.gr_doppler #GNU Radio specific doppler utilities
import utilities.satellite  #General Satellite utilities, including doppler func
#from utilities import *

deg2rad = math.pi / 180
rad2deg = 180 / math.pi

def main():
    """ Main entry point """
    os.system('reset')
    startup_ts = dt.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    cwd = os.getcwd()
    #--------START Command Line argument parser------------------------------------------------------
    parser = argparse.ArgumentParser(description="Converts GNU Radio Doppler Measurements to JSON",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    meas = parser.add_argument_group('Measurement Related Configurations')
    meas_fp_default = '/'.join([cwd, 'measurements'])
    meas.add_argument('--meas_file',
                        dest='meas_file',
                        type=str,
                        default='FOX-1D_USRP_20180113_161106.862011_UTC_10sps.f32',
                        help="Doppler offset measurement file from GNU Radio",
                        action="store")
    meas.add_argument('--meas_folder',
                        dest='meas_folder',
                        type=str,
                        default=meas_fp_default,
                        help="Doppler offset measurement file from GNU Radio",
                        action="store")
    meas.add_argument('--rx_center_freq',
                        dest='rx_center_freq',
                        type=float,
                        default=145.880e6,
                        help="Receiver Center Frequency [Hz]",
                        action="store")
    meas.add_argument('--start',
                        dest='start',
                        type=int,
                        default=0,
                        help="Start Sample Offset from meas_file start for start of valid data",
                        action="store")
    meas.add_argument('--stop',
                        dest='stop',
                        type=int,
                        default=0,
                        help="Stop Sample Offset from meas_file end for valid data",
                        action="store")

    gs = parser.add_argument_group('Ground Station Related Configurations')
    gs.add_argument('--gs_lat',
                        dest='gs_lat',
                        type=float,
                        default=37.229976,
                        help="Ground Station Latitude [deg], N=+, S=-",
                        action="store")
    gs.add_argument('--gs_lon',
                        dest='gs_lon',
                        type=float,
                        default=-80.439627,
                        help="Ground Station Longitude [deg], E=+, W=-",
                        action="store")
    gs.add_argument('--gs_alt',
                        dest='gs_alt',
                        type=float,
                        default=610,
                        help="Ground Station Altitude [m]",
                        action="store")
    gs.add_argument('--gs_name',
                        dest='gs_name',
                        type=str,
                        default=None,
                        help="Ground Station Name",
                        action="store",
                        required=False)
    gs.add_argument('--gs_callsign',
                        dest='gs_callsign',
                        type=str,
                        default=None,
                        help="Ground Station Callsign",
                        action="store",
                        required=False)
    gs.add_argument('--gs_location',
                        dest='gs_location',
                        type=str,
                        default=None,
                        help="Ground Station Location (city, state)",
                        action="store",
                        required=False)

    args = parser.parse_args()
    #--------END Command Line argument parser------------------------------------------------------


    import warnings
    warnings.filterwarnings('ignore')
    #--Read in Doppler Measurement File
    dop_df = utilities.gr_doppler.Import_Doppler_Data(args.meas_folder, args.meas_file)
    dop_df['measured_freq'] = dop_df['doppler_offset'] + args.rx_center_freq

    #--Extract valid start, stop samples
    start = args.start
    stop = len(dop_df)-args.stop
    print 'Extracting Data Points: [{:d}:{:d}]'.format(start, stop)
    dop_df = dop_df[start:stop]
    dop_df = dop_df.reset_index()
    del dop_df['index']

    #--Generate Output File Names and Paths--
    file_md = utilities.gr_doppler.Get_Meas_File_Metadata(args.meas_file)
    ts = dt.datetime.strftime(dop_df['timestamp'][0], "%Y%m%d_%H%M%S.%f_UTC")
    fn_json = '_'.join(['DOPPLER',file_md['sat_name'], ts,file_md['samp_rate_str']]) + '.json'
    fn_csv  = fn_json.replace('json', 'csv')
    fn_md  = fn_json.replace('json', 'md')
    fp_json = '/'.join([args.meas_folder,fn_json])
    fp_csv  = '/'.join([args.meas_folder,fn_csv])
    fp_md   = '/'.join([args.meas_folder,fn_md])

    #--Generate Metadata information
    md = {}
    md['sat_name'] = file_md['sat_name']
    md['receiver'] = file_md['receiver']
    md['rx_center_freq'] = args.rx_center_freq
    #print vars(args)
    for key in vars(args).keys(): #cycle through argparser keys
        if 'gs' in key: #for gs items
            if vars(args)[key]: #if the value isn't None
                #print key, vars(args)[key]
                md[key] = vars(args)[key]

    #--Export Metadata File
    print "                  Exporting Metadata to: {:s}".format(fp_md)
    with open(fp_md, 'w') as of:
        json.dump(md, of)
        of.close()

    #--Export JSON Doppler File
    print "Exporting JSON Doppler Measurement File: {:s}".format(fp_json)
    dop_df.to_json( fp_json, \
                    orient='records', \
                    date_format='iso', \
                    date_unit = 'us')

    #--Export CSV Doppler File
    print " Exporting CSV Doppler Measurement File: {:s}".format(fp_csv)
    dop_df.to_csv(  fp_csv, \
                    index_label ="index", \
                    float_format="%.10f", \
                    date_format='%Y-%m-%dT%H:%M:%S.%fZ')




if __name__ == '__main__':
    main()
