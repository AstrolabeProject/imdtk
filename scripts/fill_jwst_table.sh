#!/bin/sh
# =============================================================
# Pipelines to restore image metadata table in a Test database.
# Pipeline commands are executed by/within an IMDTK container.
# -------------------------------------------------------------
#
# To reload the TestDB 'jwst' table do the following:
#
# In dksql:
#   delete from jwst;
#   alter SEQUENCE jwst_id_seq RESTART;
#
# Then run this script, from the IMDTK project root:
#   make runtep EP=scripts/fill_jwst_table.sh
#
VOS=/usr/local/data/vos

mmd_pgsql_pipe -tn jwst -idir $VOS/images/JADES -c JADES -v
mmd_pgsql_pipe -tn jwst -idir $VOS/images/DC19 -c DC19 -v
mmd_pgsql_pipe -tn jwst -idir $VOS/images/DC20 -c DC20 -v
mmd_pgsql_pipe -tn jwst -idir $VOS/images/XTRAS -c XTRAS -v
md_pgsql_pipe -tn jwst -ff tests/resources/HorseHead.fits -c TEST -v
md_pgsql_pipe -tn jwst -ff tests/resources/m13.fits -c TEST -v
