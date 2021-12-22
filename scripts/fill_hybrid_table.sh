#!/bin/sh
# =============================================================
# Pipelines to restore image metadata table in a Test database.
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
#   make runtep EP=scripts/fill_hybrid_table.sh
#
VOS=/usr/local/data/vos

mmd_pghyb_pipe -tn imgmd -idir $VOS/images/JADES -c JADES -v
mmd_pghyb_pipe -tn imgmd -idir $VOS/images/DC19 -c DC19 -v
mmd_pghyb_pipe -tn imgmd -idir $VOS/images/DC20 -c DC20 -v
mmd_pghyb_pipe -tn imgmd -idir $VOS/images/XTRAS -c XTRAS -v
