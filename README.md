# TLE Doppler Curve matching.

## Problem:  
Given a whole bunch of satellites deployed at once (28 in 300 seconds on PSLV-40), which one is mine?

## Measurements:
Doppler Measurmement collected using GNU-Radio and the VTGS systems.  An N210 USRP with a UBX daughtercard was the receiver.  The N210 was connected to a GPS Disciplined Oscillator to provided a trusted frequency measurement.  Without the GPSDO connection, the USRP could have (would have) had a frequency offset, which may have corrupted the measurements.  For this test case, the target satellite is AMSAT's FOX-1D with a 145.88 MHz downlink.  For this particular pass the satellite was in 'high speed mode' and therefore was constantly transmitting (excellent conditions for doppler measurement).  A Frequency Locked Loop (FLL) was used to compensate for the doppler offset from the center frequency of the USRP.  The frequency error signal of the FLL was converted to hertz and then dumped to file at a rate of 10 measurements per second (10 Hz, accomplished via decimation in the flowgraph on the measurement stream).  

## Doppler Offset Conversion and Time Stamps:
This measurement file was then converted into float values.  The original doppler measurement file recorded a timestamp in the filename.  As part of the conversion process, the orginal file is trimmed towards the beginning and end of the file to remove low SNR measurements.  After trimming the file, the converted measurement data (float value) and its location in the stream relative to the startup time stamp (accounting for the trimming) allowed for a time stamp of each doppler offest value to be generated.  This information is then stored in a JSON file.


## Generated Data:
The post launch TLEs were obtained and used for the generation of doppler curves.  Doppler offset data from each TLE set was generated using the pyephem, a python based SGP4 orbital propagator.  A regression is then performed on this data to generated a 3 order polynomial equation representing the doppler curve.  The same regression is performed on the doppler measurement data.  In the same regression process, a derivative of each doppler polynomial curve is taken, and the minimum is found.  This is the Time of Closest Approach (TCA), or the instant in the satellite pass when it is the closest to the ground station and the value of the doppler offset is 0.  This information is again stored off as a JSON file.   

## TLE Matching
The polynomial information (and TCA) for each generated doppler curve is compared to the measured doppler curve in order to find the closest match.  More specifically, a time difference is taken between the measured TCA and the Generated TCA.  The TLE set with the smallest delta in TCA compared to the measured TCA is determined to be the matching TLE.

## Future Work.
This Code is an ABSOLUTE MESS and was hacked together.  It needs to be significantly cleaned up and streamlined.

Only using the TCA for comparison.  Should do something more advanced, like determine the L-1 norm of each curve and compare.  Additionally, in this case it was lucky that FOX-1D had a very accurate center frequency for its downlink.  had their been an offset in the downlink frequency (due to the transmitter, not the receiver offsets, as corrected by the GPSDO) then there would have been a bias in the measured curve.  This could have been accounted for assuming a trusted receiver (i.e. with GPSDO or other high accuracy frequency reference)).   Also, we had a nice strng constant signal to measure, most of the time the signals will be bursty (like beacons), therefore need a better doppler measurement technique for bursty signals in GNU Radio.

## Bottom Line:
Satellite launched on a Thursday night (EST).  We took this measurment the following Saturday morning.  Had this code been written before the launch, we would have been able to determine the correct TLE for FOX-1D (AO-92) within ~36 hours of deployment.

