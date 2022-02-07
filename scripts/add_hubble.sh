#!/bin/sh
# =============================================================
# Pipelines to add Hubble mosaic image metadata table to a database.
# Pipeline commands are executed by/within an IMDTK container.
# -------------------------------------------------------------
#
# To reload the TestDB 'imgmd' table do the following:
#
# In dksql:
#   delete from imgmd;
#   -- alter SEQUENCE jwst_id_seq RESTART;
#
# Then run this script, from the IMDTK project root:
#   make runtep EP=scripts/add_hubble.sh
#
CONVOS=/vos

mmd_pghyb_pipe -tn imgmd -idir $CONVOS/images/HUBMOS -c HUBMOS -v
