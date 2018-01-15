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
import datetime as dt

import utilities.pyephem
import utilities.gr_doppler
import utilities.satellite
#from utilities import *

deg2rad = math.pi / 180
rad2deg = 180 / math.pi

def main():
    """ Main entry point """
    os.system('reset')
    startup_ts = dt.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    cwd = os.getcwd()
    #--------START Command Line argument parser------------------------------------------------------
    parser = argparse.ArgumentParser(description="TLE Doppler Match",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    tle = parser.add_argument_group('TLE related configurations')
    tle_fp_default = '/'.join([cwd, 'tle'])
    tle.add_argument('--tle_file',
                    dest='tle_file',
                    type=str,
                    default='pslv40.tle',
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
    meas.add_argument('--dop_file',
                        dest='dop_file',
                        type=str,
                        default='FOX-1D_USRP_20180113_161106.862011_UTC_50k.dop',
                        help="Doppler offset measurement file from GNU Radio",
                        action="store")
    meas.add_argument('--dop_folder',
                        dest='dop_folder',
                        type=str,
                        default=meas_fp_default,
                        help="Doppler offset measurement file from GNU Radio",
                        action="store")
    meas.add_argument('--rx_center_freq',
                        dest='rx_center_freq',
                        type=float,
                        default=145.88e6,
                        help="Receiver Center Frequency [Hz]",
                        action="store")
    meas.add_argument('--gs_lat',
                        dest='gs_lat',
                        type=float,
                        default=37.229976,
                        help="Ground Station Latitude [deg], N=+, S=-",
                        action="store")
    meas.add_argument('--gs_lon',
                        dest='gs_lon',
                        type=float,
                        default=-80.439627,
                        help="Ground Station Longitude [deg], E=+, W=-",
                        action="store")
    meas.add_argument('--gs_alt',
                        dest='gs_alt',
                        type=float,
                        default=610,
                        help="Ground Station Altitude [m]",
                        action="store")
    meas.add_argument('--offset',
                        dest='offset',
                        type=float,
                        default=0,
                        help="Offset from dop_file start for begining of valid data [seconds]",
                        action="store")



    args = parser.parse_args()
    #--------END Command Line argument parser------------------------------------------------------


    #--Read in TLE Files--
    tle = utilities.pyephem.tle_file_input(args.tle_folder, args.tle_file)
    print tle

    #--create list of satellite objects with pyephem--
    sats = [] #list of pyephem satellite objects
    for sat in tle.keys(): sats.append(ephem.readtle(sat, tle[sat]['line1'], tle[sat]['line2']))

    #--create ground station object with pyephem--
    gs = ephem.Observer()
    gs.lat, gs.lon, gs.elevation =  args.gs_lat*deg2rad, \
                                    args.gs_lon*deg2rad, \
                                    args.gs_alt

    #Read in Doppler Measurement File
    dop_df = utilities.gr_doppler.Import_Doppler_Data(args.dop_folder, args.dop_file)
    print dop_df.name
    print dop_df['timestamp']
    #Convert to floats (struct pack....)



if __name__ == '__main__':
    main()
