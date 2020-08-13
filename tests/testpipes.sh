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
fits_cat_md -d --version
fits_cat_mktbl -d --version
fits_img_md -d --version
img_aliases -d --version
jwst_oc_calc -d --version
jwst_pghyb_sink -d --version
jwst_pgsql_sink -d --version
md_pgsql_pipe -d --version
miss_report -d --version
multi_md_pgsql_pipe -d --version
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
fits_cat_md --help
echo "--------------------------------------------"
fits_cat_mktbl --help
echo "--------------------------------------------"
fits_img_md --help
echo "--------------------------------------------"
img_aliases --help
echo "--------------------------------------------"
jwst_oc_calc --help
echo "--------------------------------------------"
jwst_pghyb_sink --help
echo "--------------------------------------------"
jwst_pgsql_sink --help
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


# echo "============================================"
# echo "Headers only, verbose, to STANDARD OUTPUT:"
# echo "--------------------------------------------"
# fits_img_md -v -ff /images/JADES/goods_s_F356W_2018_08_30.fits

echo "============================================"
echo "Headers only, named filename:"
echo "--------------------------------------------"
fits_img_md -v -ff /images/JADES/goods_s_F356W_2018_08_30.fits -of /work/GOODS_F356W_headers.json

echo "============================================"
echo "Headers only, generated filename:"
echo "--------------------------------------------"
fits_img_md -v -ff /images/JADES/goods_s_F356W_2018_08_30.fits -g

echo "============================================"
echo "Headers to img_aliases:"
echo "--------------------------------------------"
fits_img_md -v -ff /images/DC_191217/F356W.fits | img_aliases -v -g

echo "============================================"
echo "Headers to img_aliases to fields_info:"
echo "--------------------------------------------"
fits_img_md -v -ff /images/DC_191217/F356W.fits | img_aliases -v | fields_info -v -g

echo "============================================"
echo "Headers to img_aliases to fields_info to jwst_oc_calc:"
echo "--------------------------------------------"
fits_img_md -v -ff /images/DC_191217/F356W.fits | img_aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits -g

echo "============================================"
echo "Headers to img_aliases to fields_info to jwst_oc_calc to miss_report:"
echo "--------------------------------------------"
fits_img_md -v -ff /images/DC_191217/F356W.fits | img_aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits | miss_report -v -g

echo "============================================"
echo "Headers to img_aliases to fields_info to jwst_oc_calc to miss_report, specify COLLECTION:"
echo "--------------------------------------------"
fits_img_md -v -ff /images/DC_191217/F356W.fits | img_aliases -v | fields_info -v | jwst_oc_calc -v -c TEST_COLL -ff /images/DC_191217/F356W.fits | miss_report -v -g

echo "============================================"
echo "Headers to img_aliases to fields_info to jwst_oc_calc to miss_report to no_op:"
echo "--------------------------------------------"
fits_img_md -v -ff /images/DC_191217/F356W.fits | img_aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits | miss_report -v | no_op -v -g

echo "============================================"
echo "Headers to img_aliases to fields_info to jwst_oc_calc to miss_report to no_op to pickle_sink:"
echo "--------------------------------------------"
fits_img_md -v -ff /images/DC_191217/F356W.fits | img_aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits | miss_report -v | no_op -v | pickle_sink -v -g

echo "============================================"
echo "Headers to img_aliases to fields_info to jwst_oc_calc to miss_report to no_op to jwst_pgsql_sink:"
echo "--------------------------------------------"
fits_img_md -v -ff /images/DC_191217/F356W.fits | img_aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits | miss_report -v | no_op -v | jwst_pgsql_sink -v -sql -g

echo "============================================"
echo "Headers to img_aliases to fields_info to jwst_oc_calc to miss_report to no_op to jwst_pghyb_sink:"
echo "--------------------------------------------"
fits_img_md -v -ff /images/DC_191217/F356W.fits | img_aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits | miss_report -v | no_op -v | jwst_pghyb_sink -v -sql -g


echo "============================================"
echo "Pickle pipeline, generated filename:"
echo "--------------------------------------------"
fits_img_md -v -ff /images/DC_191217/F356W.fits | img_aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits | miss_report -v | pickle_sink -v -g

echo "============================================"
echo "Pickle pipeline, named filename:"
echo "--------------------------------------------"
fits_img_md -v -ff /images/DC_191217/F356W.fits | img_aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits | miss_report -v | pickle_sink -v -of /work/DC_F356W.pickle

echo "============================================"
echo "Pickle pipeline, all DEBUG:"
echo "--------------------------------------------"
fits_img_md -d -ff /images/DC_191217/F356W.fits | img_aliases -d | fields_info -d | jwst_oc_calc -d -ff /images/DC_191217/F356W.fits | miss_report -d | pickle_sink -d -g

echo "============================================"
echo "Pickle pipeline, all SILENT:"
fits_img_md -ff /images/DC_191217/F356W.fits | img_aliases | fields_info | jwst_oc_calc -ff /images/DC_191217/F356W.fits | miss_report | pickle_sink -g


echo "============================================"
echo "PG SQL pipeline, generated filename:"
echo "--------------------------------------------"
fits_img_md -v -ff /images/DC_191217/F356W.fits | img_aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits | miss_report -v | jwst_pgsql_sink -v -sql -g

echo "============================================"
echo "PG SQL pipeline, named filename:"
echo "--------------------------------------------"
fits_img_md -v -ff /images/DC_191217/F356W.fits | img_aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits | miss_report -v | jwst_pgsql_sink -v -sql -of /work/testql.sql

echo "============================================"
echo "PG SQL pipeline, all DEBUG:"
echo "--------------------------------------------"
fits_img_md -d -ff /images/DC_191217/F356W.fits | img_aliases -d | fields_info -d | jwst_oc_calc -d -ff /images/DC_191217/F356W.fits | miss_report -d | jwst_pgsql_sink -d -sql -g

echo "============================================"
echo "PG SQL pipeline, all SILENT:"
fits_img_md -ff /images/DC_191217/F356W.fits | img_aliases | fields_info | jwst_oc_calc -ff /images/DC_191217/F356W.fits | miss_report | jwst_pgsql_sink -sql -g


echo "============================================"
echo "CSV pipeline, generated filename:"
echo "--------------------------------------------"
fits_img_md -v -ff /images/DC_191217/F356W.fits | img_aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits | miss_report -v | csv_sink -v -g

echo "============================================"
echo "CSV pipeline, named filename:"
echo "--------------------------------------------"
fits_img_md -v -ff /images/DC_191217/F356W.fits | img_aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits | miss_report -v | csv_sink -v -of /work/test.csv

echo "============================================"
echo "CSV pipeline, all DEBUG:"
echo "--------------------------------------------"
fits_img_md -d -ff /images/DC_191217/F356W.fits | img_aliases -d | fields_info -d | jwst_oc_calc -d -ff /images/DC_191217/F356W.fits | miss_report -d | csv_sink -d -g

echo "============================================"
echo "CSV pipeline, all SILENT:"
fits_img_md -ff /images/DC_191217/F356W.fits | img_aliases | fields_info | jwst_oc_calc -ff /images/DC_191217/F356W.fits | miss_report | csv_sink -g


echo "============================================"
echo "PG Hybrid pipeline, generated filename:"
echo "--------------------------------------------"
fits_img_md -v -ff /images/DC_191217/F356W.fits | img_aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits | miss_report -v | jwst_pghyb_sink -v -sql -g

echo "============================================"
echo "PG Hybrid pipeline, named filename:"
echo "--------------------------------------------"
fits_img_md -v -ff /images/DC_191217/F356W.fits | img_aliases -v | fields_info -v | jwst_oc_calc -v -ff /images/DC_191217/F356W.fits | miss_report -v | jwst_pghyb_sink -v -sql -of /work/hyb1.sql

echo "============================================"
echo "PG Hybrid pipeline, all DEBUG:"
echo "--------------------------------------------"
fits_img_md -d -ff /images/DC_191217/F356W.fits | img_aliases -d | fields_info -d | jwst_oc_calc -d -ff /images/DC_191217/F356W.fits | miss_report -d | jwst_pghyb_sink -d -sql -g

echo "============================================"
echo "PG Hybrid pipeline, all SILENT:"
fits_img_md -ff /images/DC_191217/F356W.fits | img_aliases | fields_info | jwst_oc_calc -ff /images/DC_191217/F356W.fits | miss_report | jwst_pghyb_sink -sql -g


echo "============================================"
echo "NO-OPs in various positions, verbose:"
echo "--------------------------------------------"
fits_img_md -v -ff /images/DC_191217/F356W.fits | img_aliases -v | no_op -v -g
fits_img_md -v -ff /images/DC_191217/F356W.fits | no_op -v | img_aliases -v -g

echo "============================================"
echo "NO-OPs in various positions, debug:"
echo "--------------------------------------------"
fits_img_md -v -ff /images/DC_191217/F356W.fits | img_aliases -v | no_op -v -g
fits_img_md -d -ff /images/DC_191217/F356W.fits | no_op -d | img_aliases -d -g


echo "============================================"
echo "Explicit intermediate file pipeline:"
echo "--------------------------------------------"
fits_img_md -d -ff /images/DC_191217/F356W.fits -of /work/h.json
img_aliases -d -if /work/h.json -of /work/ha.json
fields_info -d -if /work/ha.json -of /work/hafi.json
jwst_oc_calc -d -ff /images/DC_191217/F356W.fits -if /work/hafi.json -of /work/hafijoc.json
miss_report -d -if /work/hafijoc.json -of /work/hafijocmr.json
pickle_sink -d -if /work/hafijocmr.json -of /work/hafijocmrpk.pickle
jwst_pgsql_sink -d -sql -if /work/hafijocmr.json -of /work/hafijocmrsql.sql
jwst_pghyb_sink -d -sql -if /work/hafijocmr.json -of /work/hafijocmrhyb.sql
csv_sink -d -if /work/hafijocmr.json -of /work/hafijocmr.csv

echo "============================================"
echo "Explicit intermediate file pipeline with non-json names:"
echo "--------------------------------------------"
fits_img_md -d -ff /images/DC_191217/F356W.fits -of /work/h1
img_aliases -d -if /work/h1 -of /work/ha1
fields_info -d -if /work/ha1 -of /work/hafi1
jwst_oc_calc -d -ff /images/DC_191217/F356W.fits -if /work/hafi1 -of /work/hafijoc1
miss_report -d -if /work/hafijoc1 -of /work/hafijocmr1
pickle_sink -d -if /work/hafijocmr1 -of /work/hafijocmrpk1
jwst_pgsql_sink -d -sql -if /work/hafijocmr1 -of /work/hafijocmrsql1
jwst_pghyb_sink -d -sql -if /work/hafijocmr1 -of /work/hafijocmrhyb1
csv_sink -d -if /work/hafijocmr1 -of /work/hafijocmrcsv1


echo "============================================"
echo "Exception catching on bad files:"
echo "--------------------------------------------"
fits_img_md -ff /images/BAD.fits -g -v
fits_img_md -ff /images/small_table.fits -g -v
fits_img_md -ff /images/NOSUCH.fits -g -v

md_pgsql_pipe -ff /images/BAD.fits -g -v
md_pgsql_pipe -ff /images/small_table.fits -g -v
md_pgsql_pipe -ff /images/NOSUCH.fits -g -v

multi_md_pgsql_pipe -idir /tmp/NOSUCH -g -v

fits_cat_md -ff /images/BAD.fits -g -v
fits_cat_md -ff /images/m13.fits -g -v
fits_cat_md -ff /images/NOSUCH.fits -g -v


echo "============================================"
echo "Exception catching on bad task arguments:"
echo "--------------------------------------------"
fits_img_md -ff /images/m13.fits | pickle_sink -v


echo "============================================"
echo "Single FITS metadata to PostgreSQL JWST table pipeline:"
echo "--------------------------------------------"
md_pgsql_pipe -ff /images/DC_191217/F356W.fits -v -sql -g


echo "============================================"
echo "Multiple FITS metadata to PostgreSQL JWST table pipeline:"
echo "--------------------------------------------"
multi_md_pgsql_pipe -idir /tmp -c JADES -sql -g -v
echo "--------------------------------------------"
# multi_md_pgsql_pipe -idir /images/JADES -v
# multi_md_pgsql_pipe -idir /images/JADES -sql -g -v
echo "--------------------------------------------"
# multi_md_pgsql_pipe -idir /images/DC_191217 -v
# multi_md_pgsql_pipe -idir /images/DC_191217 -sql -g -v
echo "--------------------------------------------"
# multi_md_pgsql_pipe -idir /images -v
# multi_md_pgsql_pipe -idir /images -sql -g -v


echo "============================================"
echo "Multiple FITS metadata to hybrid PostgreSQL/JSON JWST table pipeline:"
echo "--------------------------------------------"
# multi_md_pghyb_pipe -idir /tmp -c JADES -sql -g -v
echo "--------------------------------------------"
# multi_md_pghyb_pipe -idir /images/JADES -v
# multi_md_pghyb_pipe -idir /images/JADES -sql -g -v
echo "--------------------------------------------"
# multi_md_pghyb_pipe -idir /images/DC_191217 -v
# multi_md_pghyb_pipe -idir /images/DC_191217 -sql -g -v
echo "--------------------------------------------"
# multi_md_pghyb_pipe -idir /images -c ALLIMGS -v
# multi_md_pghyb_pipe -idir /images -c ALLIMGS -sql -g -v


# echo "============================================"
# echo " SQL refactoring:"
# echo "--------------------------------------------"
# multi_md_pgsql_pipe -idir /images/JADES -c JADES2 -v
# multi_md_pghyb_pipe -idir /images -c HYB_ALLIMGS -v
# multi_md_pgsql_pipe -idir /images -c SQL_ALLIMGS -v


echo "============================================"
echo "Catalog Metadata:"
echo "--------------------------------------------"
fits_cat_md -ff /catalogs/DC_191217/EAZY_results_summary_F356W.fits -d -g
fits_cat_md -ff /catalogs/DC_191217/EAZY_results_summary_F356W.fits -v -of /work/ez_cat.json
fits_cat_md -ff /catalogs/DC_191217/EAZY_results_summary_F356W.fits -v -g
echo "--------------------------------------------"
fits_cat_md -ff /catalogs/DC_191217/Photometric_Catalog.F356W_kron_f80.fits -d -g
fits_cat_md -ff /catalogs/DC_191217/Photometric_Catalog.F356W_kron_f80.fits -v -of /work/photo_cat.json
fits_cat_md -v -ff /catalogs/DC_191217/Photometric_Catalog.F356W_kron_f80.fits -v -g


echo "============================================"
echo "Current development:"
echo "--------------------------------------------"
fits_cat_md -v -ff /catalogs/small_table.fits | cat_aliases -v -g
fits_cat_md -v -ff /catalogs/small_table.fits | fits_cat_mktbl -ct noalias -sql -v -of /work/small_table_fits_cat_maketbl_noalias.sql
fits_cat_md -v -ff /catalogs/small_table.fits | cat_aliases -v | fits_cat_mktbl -ct test_tbl -sql -g -v

echo "============================================"
