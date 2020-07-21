#!/bin/bash
#
# Shell script to run pipelines from inside the imdtk Docker file
# using the tools it contains. This script should be mounted by
# the container and runs within its environment.
#

# echo "ARGS=$*"


echo "============================================"
echo "All tools: show versions"
echo "--------------------------------------------"
fits_headers -d --version
aliases -d --version
fields_info -d --version
jwst_oc_calc -d --version
md_pgsql_pipe -d --version
miss_report -d --version
multi_md_pgsql_pipe -d --version
no_op -d --version
pickle_sink -d --version
jwst_pgsql_sink -d --version
csv_sink -d --version
jwst_pghybrid_sink -d --version
fits_table -d --version

echo "============================================"
echo "All tools: show HELP"
echo "--------------------------------------------"
fits_headers --help
echo "--------------------------------------------"
aliases --help
echo "--------------------------------------------"
fields_info --help
echo "--------------------------------------------"
jwst_oc_calc --help
echo "--------------------------------------------"
md_pgsql_pipe --help
echo "--------------------------------------------"
miss_report --help
echo "--------------------------------------------"
multi_md_pgsql_pipe --help
echo "--------------------------------------------"
no_op --help
echo "--------------------------------------------"
pickle_sink --help
echo "--------------------------------------------"
jwst_pgsql_sink --help
echo "--------------------------------------------"
csv_sink --help
echo "--------------------------------------------"
jwst_pghybrid_sink --help
echo "--------------------------------------------"
fits_table --help

# echo "============================================"
# echo "Headers only, verbose, to STANDARD OUTPUT:"
# echo "--------------------------------------------"
# fits_headers -v -ff /images/JADES/goods_s_F356W_2018_08_30.fits

echo "============================================"
echo "Headers only, named filename:"
echo "--------------------------------------------"
fits_headers -v -ff /images/JADES/goods_s_F356W_2018_08_30.fits -of /work/GOODS_F356W_headers.json

echo "============================================"
echo "Headers only, generated filename:"
echo "--------------------------------------------"
fits_headers -v -ff /images/JADES/goods_s_F356W_2018_08_30.fits -g

echo "============================================"
echo "Headers to aliases:"
echo "--------------------------------------------"
fits_headers -v -ff /images/DC_191217/F356W.fits | aliases -v -g

echo "============================================"
echo "Headers to aliases to fields_info:"
echo "--------------------------------------------"
fits_headers -v -ff /images/DC_191217/F356W.fits | aliases -v | fields_info -v -g

echo "============================================"
echo "Headers to aliases to fields_info to jwst_oc_calc:"
echo "--------------------------------------------"
fits_headers -v -ff /images/DC_191217/F356W.fits | aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits -g

echo "============================================"
echo "Headers to aliases to fields_info to jwst_oc_calc to miss_report:"
echo "--------------------------------------------"
fits_headers -v -ff /images/DC_191217/F356W.fits | aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits | miss_report -v -g

echo "============================================"
echo "Headers to aliases to fields_info to jwst_oc_calc to miss_report, specify COLLECTION:"
echo "--------------------------------------------"
fits_headers -v -ff /images/DC_191217/F356W.fits | aliases -v | fields_info -v | jwst_oc_calc -v -c TEST_COLL -ff /images/DC_191217/F356W.fits | miss_report -v -g

echo "============================================"
echo "Headers to aliases to fields_info to jwst_oc_calc to miss_report to no_op:"
echo "--------------------------------------------"
fits_headers -v -ff /images/DC_191217/F356W.fits | aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits | miss_report -v | no_op -v -g

echo "============================================"
echo "Headers to aliases to fields_info to jwst_oc_calc to miss_report to no_op to pickle_sink:"
echo "--------------------------------------------"
fits_headers -v -ff /images/DC_191217/F356W.fits | aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits | miss_report -v | no_op -v | pickle_sink -v -g

echo "============================================"
echo "Headers to aliases to fields_info to jwst_oc_calc to miss_report to no_op to jwst_pgsql_sink:"
echo "--------------------------------------------"
fits_headers -v -ff /images/DC_191217/F356W.fits | aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits | miss_report -v | no_op -v | jwst_pgsql_sink -v -sql -g

echo "============================================"
echo "Headers to aliases to fields_info to jwst_oc_calc to miss_report to no_op to jwst_pghybrid_sink:"
echo "--------------------------------------------"
fits_headers -v -ff /images/DC_191217/F356W.fits | aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits | miss_report -v | no_op -v | jwst_pghybrid_sink -v -sql -g


echo "============================================"
echo "Pickle pipeline, generated filename:"
echo "--------------------------------------------"
fits_headers -v -ff /images/DC_191217/F356W.fits | aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits | miss_report -v | pickle_sink -v -g

echo "============================================"
echo "Pickle pipeline, named filename:"
echo "--------------------------------------------"
fits_headers -v -ff /images/DC_191217/F356W.fits | aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits | miss_report -v | pickle_sink -v -of /work/DC_F356W.pickle

echo "============================================"
echo "Pickle pipeline, all DEBUG:"
echo "--------------------------------------------"
fits_headers -d -ff /images/DC_191217/F356W.fits | aliases -d | fields_info -d | jwst_oc_calc -d -ff /images/DC_191217/F356W.fits | miss_report -d | pickle_sink -d -g

echo "============================================"
echo "Pickle pipeline, all SILENT:"
fits_headers -ff /images/DC_191217/F356W.fits | aliases | fields_info | jwst_oc_calc -ff /images/DC_191217/F356W.fits | miss_report | pickle_sink -g


echo "============================================"
echo "PG SQL pipeline, generated filename:"
echo "--------------------------------------------"
fits_headers -v -ff /images/DC_191217/F356W.fits | aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits | miss_report -v | jwst_pgsql_sink -v -sql -g

echo "============================================"
echo "PG SQL pipeline, named filename:"
echo "--------------------------------------------"
fits_headers -v -ff /images/DC_191217/F356W.fits | aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits | miss_report -v | jwst_pgsql_sink -v -sql -of /work/testql.sql

echo "============================================"
echo "PG SQL pipeline, all DEBUG:"
echo "--------------------------------------------"
fits_headers -d -ff /images/DC_191217/F356W.fits | aliases -d | fields_info -d | jwst_oc_calc -d -ff /images/DC_191217/F356W.fits | miss_report -d | jwst_pgsql_sink -d -sql -g

echo "============================================"
echo "PG SQL pipeline, all SILENT:"
fits_headers -ff /images/DC_191217/F356W.fits | aliases | fields_info | jwst_oc_calc -ff /images/DC_191217/F356W.fits | miss_report | jwst_pgsql_sink -sql -g


echo "============================================"
echo "CSV pipeline, generated filename:"
echo "--------------------------------------------"
fits_headers -v -ff /images/DC_191217/F356W.fits | aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits | miss_report -v | csv_sink -v -g

echo "============================================"
echo "CSV pipeline, named filename:"
echo "--------------------------------------------"
fits_headers -v -ff /images/DC_191217/F356W.fits | aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits | miss_report -v | csv_sink -v -of /work/test.csv

echo "============================================"
echo "CSV pipeline, all DEBUG:"
echo "--------------------------------------------"
fits_headers -d -ff /images/DC_191217/F356W.fits | aliases -d | fields_info -d | jwst_oc_calc -d -ff /images/DC_191217/F356W.fits | miss_report -d | csv_sink -d -g

echo "============================================"
echo "CSV pipeline, all SILENT:"
fits_headers -ff /images/DC_191217/F356W.fits | aliases | fields_info | jwst_oc_calc -ff /images/DC_191217/F356W.fits | miss_report | csv_sink -g


echo "============================================"
echo "PG Hybrid pipeline, generated filename:"
echo "--------------------------------------------"
fits_headers -v -ff /images/DC_191217/F356W.fits | aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits | miss_report -v | jwst_pghybrid_sink -v -sql -g

echo "============================================"
echo "PG Hybrid pipeline, named filename:"
echo "--------------------------------------------"
fits_headers -v -ff /images/DC_191217/F356W.fits | aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits | miss_report -v | jwst_pghybrid_sink -v -sql -of /work/hybrid1.sql

echo "============================================"
echo "PG Hybrid pipeline, all DEBUG:"
echo "--------------------------------------------"
fits_headers -d -ff /images/DC_191217/F356W.fits | aliases -d | fields_info -d | jwst_oc_calc -d -ff /images/DC_191217/F356W.fits | miss_report -d | jwst_pghybrid_sink -d -sql -g

echo "============================================"
echo "PG Hybrid pipeline, all SILENT:"
fits_headers -ff /images/DC_191217/F356W.fits | aliases | fields_info | jwst_oc_calc -ff /images/DC_191217/F356W.fits | miss_report | jwst_pghybrid_sink -sql -g


echo "============================================"
echo "NO-OPs in various positions, verbose:"
echo "--------------------------------------------"
fits_headers -v -ff /images/DC_191217/F356W.fits | aliases -v | no_op -v -g
fits_headers -v -ff /images/DC_191217/F356W.fits | no_op -v | aliases -v -g

echo "============================================"
echo "NO-OPs in various positions, debug:"
echo "--------------------------------------------"
fits_headers -v -ff /images/DC_191217/F356W.fits | aliases -v | no_op -v -g
fits_headers -d -ff /images/DC_191217/F356W.fits | no_op -d | aliases -d -g


echo "============================================"
echo "Explicit intermediate file pipeline:"
echo "--------------------------------------------"
fits_headers -d -ff /images/DC_191217/F356W.fits -of /work/h.json
aliases -d -if /work/h.json -of /work/ha.json
fields_info -d -if /work/ha.json -of /work/hafi.json
jwst_oc_calc -d -ff /images/DC_191217/F356W.fits -if /work/hafi.json -of /work/hafijoc.json
miss_report -d -if /work/hafijoc.json -of /work/hafijocmr.json
pickle_sink -d -if /work/hafijocmr.json -of /work/hafijocmrpk.pickle
jwst_pgsql_sink -d -sql -if /work/hafijocmr.json -of /work/hafijocmrsql.sql
jwst_pghybrid_sink -d -sql -if /work/hafijocmr.json -of /work/hafijocmrhyb.sql
csv_sink -d -if /work/hafijocmr.json -of /work/hafijocmr.csv

echo "============================================"
echo "Explicit intermediate file pipeline with non-json names:"
echo "--------------------------------------------"
fits_headers -d -ff /images/DC_191217/F356W.fits -of /work/h1
aliases -d -if /work/h1 -of /work/ha1
fields_info -d -if /work/ha1 -of /work/hafi1
jwst_oc_calc -d -ff /images/DC_191217/F356W.fits -if /work/hafi1 -of /work/hafijoc1
miss_report -d -if /work/hafijoc1 -of /work/hafijocmr1
pickle_sink -d -if /work/hafijocmr1 -of /work/hafijocmrpk1
jwst_pgsql_sink -d -sql -if /work/hafijocmr1 -of /work/hafijocmrsql1
jwst_pghybrid_sink -d -sql -if /work/hafijocmr1 -of /work/hafijocmrhyb1
csv_sink -d -if /work/hafijocmr1 -of /work/hafijocmrcsv1


echo "============================================"
echo "Exception catching on bad files:"
echo "--------------------------------------------"
fits_headers -ff /images/BAD.fits -g -v
fits_headers -ff /images/small_table.fits -g -v
fits_headers -ff /images/NOSUCH.fits -g -v

md_pgsql_pipe -ff /images/BAD.fits -g -v
md_pgsql_pipe -ff /images/small_table.fits -g -v
md_pgsql_pipe -ff /images/NOSUCH.fits -g -v

multi_md_pgsql_pipe -idir /tmp/NOSUCH -g -v

fits_table -ff /images/BAD.fits -g -v
fits_table -ff /images/m13.fits -g -v
fits_table -ff /images/NOSUCH.fits -g -v


echo "============================================"
echo "Exception catching on bad task arguments:"
echo "--------------------------------------------"
fits_headers -ff /images/m13.fits | pickle_sink -v


echo "============================================"
echo "Single FITS metadata to PostgreSQL JWST table pipeline:"
echo "--------------------------------------------"
md_pgsql_pipe -ff /images/DC_191217/F356W.fits -v -sql -g


echo "============================================"
echo "Multiple FITS metadata to PostgreSQL JWST table pipeline:"
echo "--------------------------------------------"
multi_md_pgsql_pipe -idir /tmp -c JADES -sql -g -v
echo "--------------------------------------------"
# multi_md_pgsql_pipe -idir /images/JADES -sql -g -v
echo "--------------------------------------------"
# multi_md_pgsql_pipe -idir /images/DC_191217 -sql -g -v
echo "--------------------------------------------"
# multi_md_pgsql_pipe -idir /images -sql -g -v


echo "============================================"
echo "Current development:"
echo "--------------------------------------------"
fits_table -ff /catalogs/DC_191217/EAZY_results_summary_F356W.fits -d -g
fits_table -ff /catalogs/DC_191217/EAZY_results_summary_F356W.fits -v -of /work/ez_cat.json
fits_table -ff /catalogs/DC_191217/EAZY_results_summary_F356W.fits -v -g
fits_table -ff /catalogs/DC_191217/Photometric_Catalog.F356W_kron_f80.fits -d -g
fits_table -ff /catalogs/DC_191217/Photometric_Catalog.F356W_kron_f80.fits -v -of /work/photo_cat.json
fits_table -ff /catalogs/DC_191217/Photometric_Catalog.F356W_kron_f80.fits -v -g

echo "============================================"
