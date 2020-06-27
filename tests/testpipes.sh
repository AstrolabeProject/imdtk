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
# headers -ff /images/DC_191217/F356W.fits | aliases -v | pickle_sink -v


#############
# Good pipes:
#############

echo "All tools: show versions"
headers -d --version
aliases -d --version
fields_info -d --version
jwst_oc_calc -d --version
miss_report -d --version
no_op -d --version
pickle_sink -d --version
jwst_pgsql_sink -d --version
csv_sink -d --version

echo "--------------------------------------------"
echo "All tools: show HELP"
headers --help
aliases --help
fields_info --help
jwst_oc_calc --help
miss_report --help
no_op --help
pickle_sink --help
jwst_pgsql_sink --help
# csv_sink --help

echo "--------------------------------------------"
echo "Headers only, verbose, to STANDARD OUTPUT:"
# headers -v -ff /images/JADES/goods_s_F356W_2018_08_30.fits

echo "--------------------------------------------"
echo "Headers only, named filename:"
headers -v -ff /images/JADES/goods_s_F356W_2018_08_30.fits -of /work/JADES_F356W_headers.json

echo "--------------------------------------------"
echo "Headers only, generated filename:"
headers -v -ff /images/JADES/goods_s_F356W_2018_08_30.fits -g

echo "--------------------------------------------"
echo "Headers to aliases:"
headers -v -ff /images/DC_191217/F356W.fits | aliases -v -g

echo "--------------------------------------------"
echo "Headers to aliases to fields_info:"
headers -v -ff /images/DC_191217/F356W.fits | aliases -v | fields_info -v -g

echo "--------------------------------------------"
echo "Headers to aliases to fields_info to jwst_oc_calc:"
headers -v -ff /images/DC_191217/F356W.fits | aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits -g

echo "--------------------------------------------"
echo "Headers to aliases to fields_info to jwst_oc_calc to miss_report:"
headers -v -ff /images/DC_191217/F356W.fits | aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits | miss_report -v -g

echo "--------------------------------------------"
echo "Headers to aliases to fields_info to jwst_oc_calc to miss_report, specify COLLECTION:"
headers -v -ff /images/DC_191217/F356W.fits | aliases -v | fields_info -v | jwst_oc_calc -v -c TEST_COLL -ff /images/DC_191217/F356W.fits | miss_report -v -g

echo "--------------------------------------------"
echo "Headers to aliases to fields_info to jwst_oc_calc to miss_report to no_op:"
headers -v -ff /images/DC_191217/F356W.fits | aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits | miss_report -v | no_op -v -g

echo "--------------------------------------------"
echo "Headers to aliases to fields_info to jwst_oc_calc to miss_report to no_op to pickle_sink:"
headers -v -ff /images/DC_191217/F356W.fits | aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits | miss_report -v | no_op -v | pickle_sink -v -g

echo "--------------------------------------------"
echo "Headers to aliases to fields_info to jwst_oc_calc to miss_report to no_op to jwst_pgsql_sink:"
headers -v -ff /images/DC_191217/F356W.fits | aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits | miss_report -v | no_op -v | jwst_pgsql_sink -v -sql -g


echo "--------------------------------------------"
echo "Pickle pipeline, generated filename:"
headers -v -ff /images/DC_191217/F356W.fits | aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits | miss_report -v | pickle_sink -v -g

echo "--------------------------------------------"
echo "Pickle pipeline, named filename:"
headers -v -ff /images/DC_191217/F356W.fits | aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits | miss_report -v | pickle_sink -v -of /work/DC_F356W.pickle

echo "--------------------------------------------"
echo "Pickle pipeline, all DEBUG:"
headers -d -ff /images/DC_191217/F356W.fits | aliases -d | fields_info -d | jwst_oc_calc -d -ff /images/DC_191217/F356W.fits | miss_report -d | pickle_sink -d -g

echo "--------------------------------------------"
echo "Pickle pipeline, all SILENT:"
headers -ff /images/DC_191217/F356W.fits | aliases | fields_info | jwst_oc_calc -ff /images/DC_191217/F356W.fits | miss_report | pickle_sink -g


echo "--------------------------------------------"
echo "PG SQL pipeline, generated filename:"
headers -v -ff /images/DC_191217/F356W.fits | aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits | miss_report -v | jwst_pgsql_sink -v -sql -g

echo "--------------------------------------------"
echo "PG SQL pipeline, named filename:"
headers -v -ff /images/DC_191217/F356W.fits | aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits | miss_report -v | jwst_pgsql_sink -v -sql -of /work/testql.sql

echo "--------------------------------------------"
echo "PG SQL pipeline, all DEBUG:"
headers -d -ff /images/DC_191217/F356W.fits | aliases -d | fields_info -d | jwst_oc_calc -d -ff /images/DC_191217/F356W.fits | miss_report -d | jwst_pgsql_sink -d -sql -g

echo "--------------------------------------------"
echo "PG SQL pipeline, all SILENT:"
headers -ff /images/DC_191217/F356W.fits | aliases | fields_info | jwst_oc_calc -ff /images/DC_191217/F356W.fits | miss_report | jwst_pgsql_sink -sql -g


echo "--------------------------------------------"
echo "CSV pipeline, generated filename:"
headers -v -ff /images/DC_191217/F356W.fits | aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits | miss_report -v | csv_sink -v -g

echo "--------------------------------------------"
echo "CSV pipeline, named filename:"
headers -v -ff /images/DC_191217/F356W.fits | aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits | miss_report -v | csv_sink -v -of /work/test.csv

echo "--------------------------------------------"
echo "CSV pipeline, all DEBUG:"
headers -d -ff /images/DC_191217/F356W.fits | aliases -d | fields_info -d | jwst_oc_calc -d -ff /images/DC_191217/F356W.fits | miss_report -d | csv_sink -d -g

echo "--------------------------------------------"
echo "CSV pipeline, all SILENT:"
headers -ff /images/DC_191217/F356W.fits | aliases | fields_info | jwst_oc_calc -ff /images/DC_191217/F356W.fits | miss_report | csv_sink -g


echo "--------------------------------------------"
echo "NO-OPs in various positions, verbose:"
headers -v -ff /images/DC_191217/F356W.fits | aliases -v | no_op -v -g
headers -v -ff /images/DC_191217/F356W.fits | no_op -v | aliases -v -g

echo "--------------------------------------------"
echo "NO-OPs in various positions, debug:"
headers -v -ff /images/DC_191217/F356W.fits | aliases -v | no_op -v -g
headers -d -ff /images/DC_191217/F356W.fits | no_op -d | aliases -d -g


echo "--------------------------------------------"
echo "Explicit intermediate file pipeline:"
headers -d -ff /images/DC_191217/F356W.fits -of /work/h.json
aliases -d -if /work/h.json -of /work/ha.json
fields_info -d -if /work/ha.json -of /work/hafi.json
jwst_oc_calc -d -ff /images/DC_191217/F356W.fits -if /work/hafi.json -of /work/hafijoc.json
miss_report -d -if /work/hafijoc.json -of /work/hafijocmr.json
pickle_sink -d -if /work/hafijocmr.json -of /work/hafijocmrpk.pickle
jwst_pgsql_sink -d -sql -if /work/hafijocmr.json -of /work/hafijocmr.sql
csv_sink -d -if /work/hafijocmr.json -of /work/hafijocmr.csv

echo "--------------------------------------------"
echo "Explicit intermediate file pipeline with non-json names:"
headers -d -ff /images/DC_191217/F356W.fits -of /work/h1
aliases -d -if /work/h1 -of /work/ha1
fields_info -d -if /work/ha1 -of /work/hafi1
jwst_oc_calc -d -ff /images/DC_191217/F356W.fits -if /work/hafi1 -of /work/hafijoc1
miss_report -d -if /work/hafijoc1 -of /work/hafijocmr1
pickle_sink -d -if /work/hafijocmrnr1 -of /work/hafijocmrpk1
jwst_pgsql_sink -d -sql -if /work/hafijocmr1 -of /work/hafijocmrsql1
csv_sink -d -if /work/hafijocmr1 -of /work/hafijocmrcsv1


echo "--------------------------------------------"
echo "Current development:"
# headers -v -ff /images/DC_191217/F356W.fits | aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits | miss_report -v | csv_sink -v
# headers -d -ff /images/DC_191217/F356W.fits | aliases -d | fields_info -d | jwst_oc_calc -d -ff /images/DC_191217/F356W.fits | miss_report -d | csv_sink -d -g
# headers -v -ff /images/DC_191217/F356W.fits | aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits | miss_report -v | csv_sink -v -of /work/testql.sql
# headers -v -ff /images/DC_191217/F356W.fits | aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits | miss_report -v | csv_sink -v -g
