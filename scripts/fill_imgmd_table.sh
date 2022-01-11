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
#   make runtep EP=scripts/fill_imgmd_table.sh
#
CONVOS=/vos

mmd_pghyb_pipe -tn imgmd -idir $CONVOS/images/JADES -c JADES -v
mmd_pghyb_pipe -tn imgmd -idir $CONVOS/images/DC19 -c DC19 -v
mmd_pghyb_pipe -tn imgmd -idir $CONVOS/images/DC20 -c DC20 -v
mmd_pghyb_pipe -tn imgmd -idir $CONVOS/images/XTRAS -c XTRAS -v
