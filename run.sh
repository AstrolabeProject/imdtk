#!/bin/bash
#
# Shell script to run pipelines from inside the imdtk Docker file
# using the tools it contains. This script should be mounted by
# the container and runs within its environment.
# 

# echo "ARGS=$*"

# Bad calls:
#
# headers -ff /images/DC_191217/F356W.fits -ofmt csv
# headers -ff /images/DC_191217/F356W.fits | aliases -v -g -ofmt csv

# Good calls:
#
# headers -ff /images/DC_191217/F356W.fits
# headers -ff /images/DC_191217/F356W.fits -g
# headers -ff /images/DC_191217/F356W.fits | aliases -v
headers -ff /images/DC_191217/F356W.fits | aliases -d -g
# headers -ff /images/DC_191217/F356W.fits | aliases -v -g
