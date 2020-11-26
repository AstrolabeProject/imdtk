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
cat_aliases -d --version
csv_sink -d --version
fields_info -d --version
fits_cat_data -d --version
fits_cat_fill -d --version
fits_cat_md -d --version
fits_cat_mktbl -d --version
fits_cat_mktbl_pipe -d --version
fits_cat_table_pipe -d --version
fits_img_md -d --version
img_aliases -d --version
irods_fits_cat_md -d --version
irods_fits_img_md -d --version
irods_jwst_oc_calc -d --version
irods_md_pghyb_pipe -d --version
irods_md_pgsql_pipe -d --version
irods_mmd_pghyb_pipe -d --version
irods_mmd_pgsql_pipe -d --version
jwst_oc_calc -d --version
jwst_pghyb_sink -d --version
jwst_pgsql_sink -d --version
md_pghyb_pipe -d --version
md_pgsql_pipe -d --version
miss_report -d --version
mmd_pghyb_pipe -d --version
mmd_pgsql_pipe -d --version
no_op -d --version
pickle_sink -d --version

echo "============================================"
echo "All tools: show HELP"
echo "--------------------------------------------"
cat_aliases --help
echo "--------------------------------------------"
csv_sink --help
echo "--------------------------------------------"
fields_info --help
echo "--------------------------------------------"
fits_cat_data --help
echo "--------------------------------------------"
fits_cat_fill --help
echo "--------------------------------------------"
fits_cat_md --help
echo "--------------------------------------------"
fits_cat_mktbl --help
echo "--------------------------------------------"
fits_cat_mktbl_pipe --help
echo "--------------------------------------------"
fits_cat_table_pipe --help
echo "--------------------------------------------"
fits_img_md --help
echo "--------------------------------------------"
img_aliases --help
echo "--------------------------------------------"
irods_fits_cat_md --help
echo "--------------------------------------------"
irods_fits_img_md --help
echo "--------------------------------------------"
irods_jwst_oc_calc --help
echo "--------------------------------------------"
irods_md_pghyb_pipe --help
echo "--------------------------------------------"
irods_md_pgsql_pipe --help
echo "--------------------------------------------"
irods_mmd_pghyb_pipe --help
echo "--------------------------------------------"
irods_mmd_pgsql_pipe --help
echo "--------------------------------------------"
jwst_oc_calc --help
echo "--------------------------------------------"
jwst_pghyb_sink --help
echo "--------------------------------------------"
jwst_pgsql_sink --help
echo "--------------------------------------------"
md_pghyb_pipe --help
echo "--------------------------------------------"
md_pgsql_pipe --help
echo "--------------------------------------------"
miss_report --help
echo "--------------------------------------------"
mmd_pghyb_pipe --help
echo "--------------------------------------------"
mmd_pgsql_pipe --help
echo "--------------------------------------------"
no_op --help
echo "--------------------------------------------"
pickle_sink --help


# echo "============================================"
# echo "Headers only, verbose, to STANDARD OUTPUT:"
# echo "--------------------------------------------"
# fits_img_md -v -ff /vos/images/JADES/goods_s_F356W_2018_08_30.fits

echo "============================================"
echo "Headers only, named filename:"
echo "--------------------------------------------"
fits_img_md -v -ff /vos/images/JADES/goods_s_F356W_2018_08_30.fits -of /work/GOODS_F356W_headers.json

echo "============================================"
echo "Headers only, generated filename:"
echo "--------------------------------------------"
fits_img_md -v -ff /vos/images/JADES/goods_s_F356W_2018_08_30.fits -g

echo "============================================"
echo "Headers to img_aliases:"
echo "--------------------------------------------"
fits_img_md -v -ff /vos/images/DC_191217/F356W.fits | img_aliases -v -g

echo "============================================"
echo "Headers to img_aliases to fields_info:"
echo "--------------------------------------------"
fits_img_md -v -ff /vos/images/DC_191217/F356W.fits | img_aliases -v | fields_info -v -g

echo "============================================"
echo "Headers to img_aliases to fields_info to jwst_oc_calc:"
echo "--------------------------------------------"
fits_img_md -v -ff /vos/images/DC_191217/F356W.fits | img_aliases -v | fields_info -v | jwst_oc_calc -v -ff /vos/images/DC_191217/F356W.fits -g

echo "============================================"
echo "Headers to img_aliases to fields_info to jwst_oc_calc to miss_report:"
echo "--------------------------------------------"
fits_img_md -v -ff /vos/images/DC_191217/F356W.fits | img_aliases -v | fields_info -v | jwst_oc_calc -v -ff /vos/images/DC_191217/F356W.fits | miss_report -v -g

echo "============================================"
echo "Headers to img_aliases to fields_info to jwst_oc_calc to miss_report, specify COLLECTION:"
echo "--------------------------------------------"
fits_img_md -v -ff /vos/images/DC_191217/F356W.fits | img_aliases -v | fields_info -v | jwst_oc_calc -v -c TEST -ff /vos/images/DC_191217/F356W.fits | miss_report -v -g

echo "============================================"
echo "Headers to img_aliases to fields_info to jwst_oc_calc to miss_report to no_op:"
echo "--------------------------------------------"
fits_img_md -v -ff /vos/images/DC_191217/F356W.fits | img_aliases -v | fields_info -v | jwst_oc_calc -v -ff /vos/images/DC_191217/F356W.fits | miss_report -v | no_op -v -g

echo "============================================"
echo "Headers to img_aliases to fields_info to jwst_oc_calc to miss_report to no_op to pickle_sink:"
echo "--------------------------------------------"
fits_img_md -v -ff /vos/images/DC_191217/F356W.fits | img_aliases -v | fields_info -v | jwst_oc_calc -v -ff /vos/images/DC_191217/F356W.fits | miss_report -v | no_op -v | pickle_sink -v -g


echo "============================================"
echo "Pickle pipeline, generated filename:"
echo "--------------------------------------------"
fits_img_md -v -ff /vos/images/DC_191217/F356W.fits | img_aliases -v | fields_info -v | jwst_oc_calc -v -ff /vos/images/DC_191217/F356W.fits | miss_report -v | pickle_sink -v -g

echo "============================================"
echo "Pickle pipeline, named filename:"
echo "--------------------------------------------"
fits_img_md -v -ff /vos/images/DC_191217/F356W.fits | img_aliases -v | fields_info -v | jwst_oc_calc -v -ff /vos/images/DC_191217/F356W.fits | miss_report -v | pickle_sink -v -of /work/DC_F356W.pickle

echo "============================================"
echo "Pickle pipeline, all DEBUG:"
echo "--------------------------------------------"
fits_img_md -d -ff /vos/images/DC_191217/F356W.fits | img_aliases -d | fields_info -d | jwst_oc_calc -d -ff /vos/images/DC_191217/F356W.fits | miss_report -d | pickle_sink -d -g

echo "============================================"
echo "Pickle pipeline, all SILENT:"
fits_img_md -ff /vos/images/DC_191217/F356W.fits | img_aliases | fields_info | jwst_oc_calc -ff /vos/images/DC_191217/F356W.fits | miss_report | pickle_sink -g


echo "============================================"
echo "PG SQL pipeline, generated filename:"
echo "--------------------------------------------"
fits_img_md -v -ff /vos/images/DC_191217/F356W.fits | img_aliases -v | fields_info -v | jwst_oc_calc -v -ff /vos/images/DC_191217/F356W.fits | miss_report -v | jwst_pgsql_sink -v -sql -g

echo "============================================"
echo "PG SQL pipeline, named filename:"
echo "--------------------------------------------"
fits_img_md -v -ff /vos/images/DC_191217/F356W.fits | img_aliases -v | fields_info -v | jwst_oc_calc -v -ff /vos/images/DC_191217/F356W.fits | miss_report -v | jwst_pgsql_sink -v -sql -of /work/testql.sql

echo "============================================"
echo "PG SQL pipeline, all DEBUG:"
echo "--------------------------------------------"
fits_img_md -d -ff /vos/images/DC_191217/F356W.fits | img_aliases -d | fields_info -d | jwst_oc_calc -d -ff /vos/images/DC_191217/F356W.fits | miss_report -d | jwst_pgsql_sink -d -sql -g

echo "============================================"
echo "PG SQL pipeline, all SILENT:"
fits_img_md -ff /vos/images/DC_191217/F356W.fits | img_aliases | fields_info | jwst_oc_calc -ff /vos/images/DC_191217/F356W.fits | miss_report | jwst_pgsql_sink -sql -g


echo "============================================"
echo "CSV pipeline, generated filename:"
echo "--------------------------------------------"
fits_img_md -v -ff /vos/images/DC_191217/F356W.fits | img_aliases -v | fields_info -v | jwst_oc_calc -v -ff /vos/images/DC_191217/F356W.fits | miss_report -v | csv_sink -v -g

echo "============================================"
echo "CSV pipeline, named filename:"
echo "--------------------------------------------"
fits_img_md -v -ff /vos/images/DC_191217/F356W.fits | img_aliases -v | fields_info -v | jwst_oc_calc -v -ff /vos/images/DC_191217/F356W.fits | miss_report -v | csv_sink -v -of /work/test.csv

echo "============================================"
echo "CSV pipeline, all DEBUG:"
echo "--------------------------------------------"
fits_img_md -d -ff /vos/images/DC_191217/F356W.fits | img_aliases -d | fields_info -d | jwst_oc_calc -d -ff /vos/images/DC_191217/F356W.fits | miss_report -d | csv_sink -d -g

echo "============================================"
echo "CSV pipeline, all SILENT:"
fits_img_md -ff /vos/images/DC_191217/F356W.fits | img_aliases | fields_info | jwst_oc_calc -ff /vos/images/DC_191217/F356W.fits | miss_report | csv_sink -g


echo "============================================"
echo "PG Hybrid pipeline, generated filename:"
echo "--------------------------------------------"
fits_img_md -v -ff /vos/images/DC_191217/F356W.fits | img_aliases -v | fields_info -v | jwst_oc_calc -v -ff /vos/images/DC_191217/F356W.fits | miss_report -v | jwst_pghyb_sink -v -sql -g

echo "============================================"
echo "PG Hybrid pipeline, named filename:"
echo "--------------------------------------------"
fits_img_md -v -ff /vos/images/DC_191217/F356W.fits | img_aliases -v | fields_info -v | jwst_oc_calc -v -ff /vos/images/DC_191217/F356W.fits | miss_report -v | jwst_pghyb_sink -v -sql -of /work/hyb1.sql

echo "============================================"
echo "PG Hybrid pipeline, all DEBUG:"
echo "--------------------------------------------"
fits_img_md -d -ff /vos/images/DC_191217/F356W.fits | img_aliases -d | fields_info -d | jwst_oc_calc -d -ff /vos/images/DC_191217/F356W.fits | miss_report -d | jwst_pghyb_sink -d -sql -g

echo "============================================"
echo "PG Hybrid pipeline, all SILENT:"
fits_img_md -ff /vos/images/DC_191217/F356W.fits | img_aliases | fields_info | jwst_oc_calc -ff /vos/images/DC_191217/F356W.fits | miss_report | jwst_pghyb_sink -sql -g


echo "============================================"
echo "NO-OPs in various positions:"
echo "--------------------------------------------"
fits_img_md -v -ff /vos/images/DC_191217/F356W.fits | img_aliases -v | no_op -v -g
fits_img_md -v -ff /vos/images/DC_191217/F356W.fits | no_op -v | img_aliases -v -g
fits_img_md -d -ff /vos/images/DC_191217/F356W.fits | no_op -d | img_aliases -d -g


echo "============================================"
echo "Explicit intermediate file pipeline:"
echo "--------------------------------------------"
fits_img_md -d -ff /vos/images/DC_191217/F356W.fits -of /work/h.json
img_aliases -d -if /work/h.json -of /work/ha.json
fields_info -d -if /work/ha.json -of /work/hafi.json
jwst_oc_calc -d -ff /vos/images/DC_191217/F356W.fits -if /work/hafi.json -of /work/hafijoc.json
miss_report -d -if /work/hafijoc.json -of /work/hafijocmr.json
pickle_sink -d -if /work/hafijocmr.json -of /work/hafijocmrpk.pickle
jwst_pgsql_sink -d -sql -if /work/hafijocmr.json -of /work/hafijocmrsql.sql
jwst_pghyb_sink -d -sql -if /work/hafijocmr.json -of /work/hafijocmrhyb.sql
csv_sink -d -if /work/hafijocmr.json -of /work/hafijocmr.csv

echo "============================================"
echo "Explicit intermediate file pipeline with non-json names:"
echo "--------------------------------------------"
fits_img_md -d -ff /vos/images/DC_191217/F356W.fits -of /work/h1
img_aliases -d -if /work/h1 -of /work/ha1
fields_info -d -if /work/ha1 -of /work/hafi1
jwst_oc_calc -d -ff /vos/images/DC_191217/F356W.fits -if /work/hafi1 -of /work/hafijoc1
miss_report -d -if /work/hafijoc1 -of /work/hafijocmr1
pickle_sink -d -if /work/hafijocmr1 -of /work/hafijocmrpk1
jwst_pgsql_sink -d -sql -if /work/hafijocmr1 -of /work/hafijocmrsql1
jwst_pghyb_sink -d -sql -if /work/hafijocmr1 -of /work/hafijocmrhyb1
csv_sink -d -if /work/hafijocmr1 -of /work/hafijocmrcsv1


echo "=================================================="
echo "Exception catching on bad files (ERRORS EXPECTED):"
echo "--------------------------------------------------"
fits_img_md -ff /vos/images/BAD.fits -g -v
fits_img_md -ff /vos/images/small_table.fits -g -v
fits_img_md -ff /vos/images/NOSUCH.fits -g -v
fits_img_md -ff /vos/images/m13.fits | pickle_sink -v
echo "--------------------------------------------------"
fits_cat_md -ff /vos/images/BAD.fits -g -v
fits_cat_md -ff /vos/images/m13.fits -g -v
fits_cat_md -ff /vos/images/NOSUCH.fits -g -v


echo "============================================"
echo "Catalog Metadata:"
echo "--------------------------------------------"
# fits_cat_md -ff /vos/catalogs/DC_191217/EAZY_results_summary_F356W.fits -d -g
fits_cat_md -ff /vos/catalogs/DC_191217/EAZY_results_summary_F356W.fits -v -g
fits_cat_md -ff /vos/catalogs/DC_191217/EAZY_results_summary_F356W.fits -v -of /work/ez_cat.json
echo "--------------------------------------------"
# fits_cat_md -ff /vos/catalogs/DC_191217/Photometric_Catalog.F356W_kron_f80.fits -d -g
fits_cat_md -v -ff /vos/catalogs/DC_191217/Photometric_Catalog.F356W_kron_f80.fits -v -g
fits_cat_md -ff /vos/catalogs/DC_191217/Photometric_Catalog.F356W_kron_f80.fits -v -of /work/photo_cat.json


echo "============================================"
echo "Catalog Metadata with Aliases:"
echo "--------------------------------------------"
fits_cat_md -v -ff /vos/catalogs/small_table.fits | cat_aliases -v -g
fits_cat_md -v -ff /vos/catalogs/small_table.fits | cat_aliases -v -of /work/small_table_fits_cat_md_alias.json


echo "============================================"
echo "Catalog Make Table:"
echo "--------------------------------------------"
fits_cat_md -v -ff /vos/catalogs/small_table.fits | fits_cat_mktbl -ct test_tbl -v -sql -g
fits_cat_md -v -ff /vos/catalogs/small_table.fits | fits_cat_mktbl -ct test_tbl -v -sql -of /work/small_table_fits_cat_mktbl.sql
echo "--------------------------------------------"
fits_cat_md -v -ff /vos/catalogs/small_table.fits | cat_aliases -v | fits_cat_mktbl -ct test_tbl -v -sql -g
fits_cat_md -v -ff /vos/catalogs/small_table.fits | cat_aliases -v | fits_cat_mktbl -ct test_tbl -v -sql -of /work/small_table_fits_cat_mktbl_alias.sql
echo "--------------------------------------------"
fits_cat_md -v -ff /vos/catalogs/small_table.fits | fits_cat_mktbl -ct noalias -v -sql -g
fits_cat_md -v -ff /vos/catalogs/small_table.fits | fits_cat_mktbl -ct noalias -v -sql -of /work/small_table_fits_cat_mktbl_noalias.sql


# echo "============================================"
# echo "Catalog Data extraction:"
# echo "--------------------------------------------"
# Smallest (~60k) data file (with meta):
# fits_cat_data -v -ff /vos/catalogs/small_table.fits -v -g
# Medium sized (~1M) data file:
# fits_cat_data -v -ff /vos/catalogs/DC_191217/EAZY_results_summary_F356W.fits -v -g
# Medium sized (~2.9M) data file:
# fits_cat_data -v -ff /vos/catalogs/DC_191217/Photometric_Catalog.F200W_kron_f80.fits -v -g
# Largest (~4M) and most complex (nested fields) data file:
# fits_cat_data -v -ff /vos/catalogs/DC_191217/photometry_table_psf_matched_v5.0.fits -v -g


echo "======================================================="
echo "Single FITS metadata to PostgreSQL JWST table pipeline:"
echo "-------------------------------------------------------"
echo "BAD inputs or invalid arguments (ERRORS EXPECTED):"
echo "--------------------------------------------------"
md_pgsql_pipe -ff /vos/images/BAD.fits -g -v
md_pgsql_pipe -ff /vos/images/small_table.fits -g -v
md_pgsql_pipe -ff /vos/images/NOSUCH.fits -g -v
echo "--------------------------------------------------"
md_pgsql_pipe -ff /vos/images/DC_191217/F356W.fits -v -sql -g
md_pgsql_pipe -ff /vos/images/DC_191217/F444W.fits -v -sql -g


echo "==================================================================="
echo "Single FITS metadata to PostgreSQL/JSON hybrid JWST table pipeline:"
echo "-------------------------------------------------------------------"
echo "BAD inputs or invalid arguments (ERRORS EXPECTED):"
echo "--------------------------------------------------"
md_pghyb_pipe -ff /vos/images/BAD.fits -g -v
md_pghyb_pipe -ff /vos/images/small_table.fits -g -v
md_pghyb_pipe -ff /vos/images/NOSUCH.fits -g -v
echo "--------------------------------------------------"
md_pghyb_pipe -ff /vos/images/DC_191217/F356W.fits -v -sql -g
md_pghyb_pipe -ff /vos/images/DC_191217/F444W.fits -v -sql -g


# echo "========================================================="
# echo "Multiple FITS metadata to PostgreSQL JWST table pipeline:"
# echo "---------------------------------------------------------"
# mmd_pgsql_pipe -idir /tmp -c JADES -sql -g -v
# echo "--------------------------------------------"
# mmd_pgsql_pipe -idir /vos/images/JADES -v
# mmd_pgsql_pipe -idir /vos/images/JADES -c JADES -v
# mmd_pgsql_pipe -idir /vos/images/JADES -sql -g -v
# echo "--------------------------------------------"
# mmd_pgsql_pipe -idir /vos/images/DC_191217 -v
# mmd_pgsql_pipe -idir /vos/images/DC_191217 -c DC_191217 -v
# mmd_pgsql_pipe -idir /vos/images/DC_191217 -sql -g -v
# echo "--------------------------------------------"
# mmd_pgsql_pipe -idir /vos/images -c TEST_ALL  -v
# mmd_pgsql_pipe -idir /vos/images -c TEST_ALL -sql -g -v


# echo "============================================"
# echo "Multiple FITS metadata to hybrid PostgreSQL/JSON JWST table pipeline:"
# echo "--------------------------------------------"
# mmd_pghyb_pipe -idir /tmp -c JADES -sql -g -v
# echo "--------------------------------------------"
# mmd_pghyb_pipe -idir /vos/images/JADES -v
# mmd_pghyb_pipe -idir /vos/images/JADES -c JADES -v
# mmd_pghyb_pipe -idir /vos/images/JADES -sql -g -v
# echo "--------------------------------------------"
# mmd_pghyb_pipe -idir /vos/images/DC_191217 -v
# mmd_pghyb_pipe -idir /vos/images/DC_191217 -c DC_191217 -v
# mmd_pghyb_pipe -idir /vos/images/DC_191217 -sql -g -v
# echo "--------------------------------------------"
# mmd_pghyb_pipe -idir /vos/images -c TEST_ALL -v
# mmd_pghyb_pipe -idir /vos/images -c TEST_ALL -sql -g -v


echo "=================================================="
echo "iRods Image Metadata extraction:"
echo "--------------------------------------------------"
echo "BAD inputs or invalid arguments (ERRORS EXPECTED):"
echo "--------------------------------------------------"
irods_fits_img_md -iff /iplant/home/hickst/vos/images/m14.fits -v
irods_fits_img_md -iff /iplant/home/hickst/vos/images/BAD.fits -v
irods_fits_img_md -iff /iplant/home/hickst/vos/images/m13.fits -v -hdu 1
irods_fits_img_md -iff /iplant/home/hickst/vos/images/HorseHead.fits -v -hdu 1
irods_fits_img_md -iff /iplant/home/hickst/vos/images/small_table.fits -v
irods_fits_img_md -iff /iplant/home/hickst/vos/images/small_table.fits -v -hdu 1
irods_fits_img_md -iff /iplant/home/hickst/astrolabe/data/w5/w5.fits -v -hdu 1
irods_fits_img_md -iff /iplant/home/hickst/vos/images/DC_191217/F444W.fits -v -hdu 1
irods_fits_img_md -iff /iplant/home/hickst/vos/catalogs/DC_191217/EAZY_results_summary_F356W.fits -v
irods_fits_img_md -iff /iplant/home/hickst/vos/catalogs/DC_191217/EAZY_results_summary_F356W.fits -v -hdu 0
irods_fits_img_md -iff /iplant/home/hickst/vos/catalogs/DC_191217/EAZY_results_summary_F356W.fits -v -hdu 1
echo "--------------------------------------------------"
irods_fits_img_md -iff /iplant/home/hickst/vos/images/m13.fits -g -v
irods_fits_img_md -iff /iplant/home/hickst/vos/images/HorseHead.fits -g -v
irods_fits_img_md -iff /iplant/home/hickst/astrolabe/data/w5/w5.fits -g -v
irods_fits_img_md -iff /iplant/home/hickst/vos/images/DC_191217/F444W.fits -g -v


echo "=================================================="
echo "iRods Catalog Metadata extraction:"
echo "--------------------------------------------------"
echo "BAD inputs or invalid arguments (ERRORS EXPECTED):"
echo "--------------------------------------------------"
irods_fits_cat_md -iff /iplant/home/hickst/vos/images/m14.fits -v
irods_fits_cat_md -iff /iplant/home/hickst/vos/images/BAD.fits -v
irods_fits_cat_md -iff /iplant/home/hickst/vos/images/m13.fits -v
irods_fits_cat_md -iff /iplant/home/hickst/vos/images/m13.fits -v -chdu 1
irods_fits_cat_md -iff /iplant/home/hickst/vos/images/m13.fits -v -chdu 0
irods_fits_cat_md -iff /iplant/home/hickst/vos/images/HorseHead.fits -v -chdu 0
irods_fits_cat_md -iff /iplant/home/hickst/vos/images/small_table.fits -v -chdu 0
irods_fits_cat_md -iff /iplant/home/hickst/astrolabe/data/w5/w5.fits -v
irods_fits_cat_md -iff /iplant/home/hickst/astrolabe/data/w5/w5.fits -v -chdu 1
irods_fits_cat_md -iff /iplant/home/hickst/astrolabe/data/w5/w5.fits -v -chdu 0
irods_fits_cat_md -iff /iplant/home/hickst/vos/images/DC_191217/F444W.fits -v
irods_fits_cat_md -iff /iplant/home/hickst/vos/images/DC_191217/F444W.fits -v -chdu 0
irods_fits_cat_md -iff /iplant/home/hickst/vos/images/DC_191217/F444W.fits -v -chdu 1
irods_fits_cat_md -iff /iplant/home/hickst/vos/catalogs/DC_191217/EAZY_results_summary_F356W.fits -v -chdu 0
echo "--------------------------------------------------"
irods_fits_cat_md -iff /iplant/home/hickst/vos/images/HorseHead.fits -g -v
irods_fits_cat_md -iff /iplant/home/hickst/vos/images/HorseHead.fits -g -v -chdu 1
irods_fits_cat_md -iff /iplant/home/hickst/vos/images/small_table.fits -g -v
irods_fits_cat_md -iff /iplant/home/hickst/vos/images/small_table.fits -g -v -chdu 1
irods_fits_cat_md -iff /iplant/home/hickst/vos/catalogs/DC_191217/EAZY_results_summary_F356W.fits -g -v
irods_fits_cat_md -iff /iplant/home/hickst/vos/catalogs/DC_191217/EAZY_results_summary_F356W.fits -g -v -chdu 1


echo "============================================================="
echo "Single FITS iRods metadata to PostgreSQL JWST table pipeline:"
echo "-------------------------------------------------------------"
echo "BAD inputs or invalid arguments (ERRORS EXPECTED):"
echo "--------------------------------------------------"
irods_md_pgsql_pipe -iff /iplant/home/hickst/vos/images -v
irods_md_pgsql_pipe -iff /iplant/home/hickst/vos/images/BAD.fits -v
irods_md_pgsql_pipe -iff /iplant/home/hickst/vos/images/small_table.fits -v
echo "-------------------------------------------------------------"
irods_md_pgsql_pipe -iff /iplant/home/hickst/vos/images/m13.fits -sql -g -v
irods_md_pgsql_pipe -iff /iplant/home/hickst/vos/images/HorseHead.fits -sql -g -v
irods_md_pgsql_pipe -iff /iplant/home/hickst/vos/images/DC_191217/F444W.fits -sql -g -v
irods_md_pgsql_pipe -iff /iplant/home/hickst/vos/images/DC_191217/F356W.fits -sql -g -v


echo "========================================================================="
echo "Single FITS iRods metadata to PostgreSQL/JSON hybrid JWST table pipeline:"
echo "-------------------------------------------------------------------------"
echo "BAD inputs or invalid arguments (ERRORS EXPECTED):"
echo "--------------------------------------------------"
irods_md_pghyb_pipe -iff /iplant/home/hickst/vos/images -v
irods_md_pghyb_pipe -iff /iplant/home/hickst/vos/images/BAD.fits -v
irods_md_pghyb_pipe -iff /iplant/home/hickst/vos/images/small_table.fits -v
echo "-------------------------------------------------------------"
irods_md_pghyb_pipe -iff /iplant/home/hickst/vos/images/m13.fits -sql -g -v
irods_md_pghyb_pipe -iff /iplant/home/hickst/vos/images/HorseHead.fits -sql -g -v
irods_md_pghyb_pipe -iff /iplant/home/hickst/vos/images/DC_191217/F444W.fits -sql -g -v
irods_md_pghyb_pipe -iff /iplant/home/hickst/vos/images/DC_191217/F356W.fits -sql -g -v


echo "==============================================================="
echo "Multiple FITS iRods metadata to PostgreSQL JWST table pipeline:"
echo "---------------------------------------------------------------"
echo "BAD inputs or invalid arguments (ERRORS EXPECTED):"
echo "--------------------------------------------------"
irods_mmd_pgsql_pipe -idir /iplant/home/hickst/vos/nosuchdir -v
echo "---------------------------------------------------------------"
irods_mmd_pgsql_pipe -idir /iplant/home/hickst/resources -c EMPTY -v
irods_mmd_pgsql_pipe -idir /iplant/home/hickst/vos/images/JADES -sql -g -v
irods_mmd_pgsql_pipe -idir /iplant/home/hickst/vos/images/DC_191217 -sql -g -v


echo "==========================================================================="
echo "Multiple FITS iRods metadata to hybrid PostgreSQL/JSON JWST table pipeline:"
echo "---------------------------------------------------------------------------"
echo "BAD inputs or invalid arguments (ERRORS EXPECTED):"
echo "--------------------------------------------------"
irods_mmd_pghyb_pipe -idir /iplant/home/hickst/vos/nosuchdir -v
echo "---------------------------------------------------------------------------"
irods_mmd_pghyb_pipe -idir /iplant/home/hickst/resources -c EMPTY -v
irods_mmd_pghyb_pipe -idir /iplant/home/hickst/vos/images/JADES -sql -g -v
irods_mmd_pghyb_pipe -idir /iplant/home/hickst/vos/images/DC_191217 -sql -g -v


echo "============================================"
