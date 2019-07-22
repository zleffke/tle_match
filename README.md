# TLE Doppler Curve matching.

## NOTE:
re-writing to use [skyfield](https://rhodesmill.org/skyfield/) instead of [pyephem](https://rhodesmill.org/pyephem/).  retaining the original version of this code based on pyephem in the 'pyephem' directory.

## Major changes (intent):
* skyfield instead of pyephem.
* measurements from burst decoder.  original measurements were of a continuous signal using FLL error outputs.  Burst decoder used in VCC mission generates a carrier frequency offset measurement for each packet decoded.
* generally cleaner implementation from original hacked together version.
