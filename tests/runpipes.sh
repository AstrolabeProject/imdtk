#!/bin/bash
#
# Shell script to run pipelines from inside the imdtk Docker file
# using the tools it contains. This script should be mounted by
# the container and runs within its environment.
# 

# echo "ARGS=$*"

#############
# Bad pipes:
#############

# headers -ff /images/DC_191217/F356W.fits -ofmt xxx
# headers -ff /images/DC_191217/F356W.fits | aliases -v -g -ofmt xxx


#############
# Good pipes:
#############

# All tools: show versions
headers -d --version
aliases -d --version
fields_info -d --version
jwst_oc_calc -d --version
miss_report -d --version

# Headers only, to standard output:
# headers -v -ff /images/JADES/goods_s_F356W_2018_08_30.fits

# Headers only, named filename:
headers -v -ff /images/JADES/goods_s_F356W_2018_08_30.fits -of /work/JADES_F356W_headers.json

# Headers only, generated filename:
headers -v -ff /images/JADES/goods_s_F356W_2018_08_30.fits -g

# Headers to aliases:
headers -v -ff /images/DC_191217/F356W.fits | aliases -v -g

# Headers to aliases to fields_info:
headers -v -ff /images/DC_191217/F356W.fits | aliases -v | fields_info -v -g

# Headers to aliases to fields_info to jwst_oc_calc:
headers -v -ff /images/DC_191217/F356W.fits | aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits -g

# Last tool debug and generate filename:
headers -ff /images/DC_191217/F356W.fits | aliases -d -g

# Explicit intermediate file pipeline:
# headers -d -ff /images/DC_191217/F356W.fits -of /work/h.json
# aliases -d -if /work/h.json -of /work/ha.json
# fields_info -d -if /work/ha.json -of /work/hafi.json
# jwst_oc_calc -d -ff /images/DC_191217/F356W.fits -if /work/hafi1.json -of /work/hafijoc1.json
# miss_report -d -if /work/hafijoc1.json -of /work/hafijocmr1.json

# Explicit intermediate file pipeline with non-json names:
headers -d -ff /images/DC_191217/F356W.fits -of /work/h1
aliases -d -if /work/h1 -of /work/ha1
fields_info -d -if /work/ha1 -of /work/hafi1
jwst_oc_calc -d -ff /images/DC_191217/F356W.fits -if /work/hafi1 -of /work/hafijoc1
miss_report -d -if /work/hafijoc1 -of /work/hafijocmr1

# Last tool verbose, to standard output:
# headers -ff /images/DC_191217/F356W.fits | aliases | fields_info -v

# All tools verbose, specify collection:
headers -v -ff /images/DC_191217/F356W.fits | aliases -v | fields_info -v | jwst_oc_calc -v -c TEST_COLL -ff /images/DC_191217/F356W.fits -g

# All tools silent:
headers -ff /images/DC_191217/F356W.fits | aliases | fields_info | jwst_oc_calc -ff /images/DC_191217/F356W.fits | miss_report -g

# All tools debug:
headers -d -ff /images/DC_191217/F356W.fits | aliases -d | fields_info -d | jwst_oc_calc -d -ff /images/DC_191217/F356W.fits | miss_report -d -g

# All tools verbose:
headers -v -ff /images/DC_191217/F356W.fits | aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits | miss_report -v -g
