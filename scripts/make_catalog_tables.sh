#!/bin/bash
#
# Shell script to create and fill some different size catalog tables for testing.
# This script is run inside the ImdTk Docker container, and uses the tools it contains.
#

# echo "ARGS=$*"

Usage () {
   echo "Usage: $0 [ -s | -m | -l ]"
   echo "where: '-s', '-m', '-l' flags mean use 'small', 'medium', or 'large' test tables"
}

SIZE=${1:-'-s'}

case "$SIZE" in
    -s)
        CAT_NAME='small_table.fits';
        TBL_NAME='test_tbl_s' ;;
    -m)
        CAT_NAME='DC_191217/EAZY_results_summary_F356W.fits';
        TBL_NAME='test_tbl_m' ;;
    -l)
        CAT_NAME='DC_191217/Photometric_Catalog.F200W_kron_f80.fits';
        TBL_NAME='test_tbl_l' ;;
    *)  Usage;
        exit 1 ;;
esac

fits_cat_mktbl_pipe -ff /catalogs/${CAT_NAME} -a /imdtk/config/jwst-cat-aliases.ini -ct ${TBL_NAME} -v
if [ $? -eq 0 ]; then
    fits_cat_table_pipe -ff /catalogs/${CAT_NAME} -ct ${TBL_NAME} -v
fi
