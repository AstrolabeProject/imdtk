#!/bin/bash
#
# Shell script to run pipelines from inside the imdtk Docker file
# using the tools it contains. This script should be mounted by
# the container and runs within its environment.
# 

# echo "ARGS=$*"

# headers -ofmt pickle -ff /images/DC_191217/F356W.fits | aliases -d -ifmt pickle -os file
# headers -ff /images/DC_191217/F356W.fits
headers -ff /images/DC_191217/F356W.fits | aliases -d -os file
