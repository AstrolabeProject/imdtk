# Environment variables for running an ImdTk Docker container from a shell script.
#   This file is sourced by commands in the 'bin' subdirectory to establish the
#   Docker 'run' command parameters.
#
# TOPLVL=${PWD%/*}
TOPLVL=${PWD}
CATS=${TOPLVL}/catalogs
IMGS=${TOPLVL}/images
SCRIPTS=${TOPLVL}/scripts
WORK=${TOPLVL}/work

APP_ROOT=/imtk
CONSCRIPTS=${APP_ROOT}/scripts
COLLECTION=JWST
IMG=imdtk:devel
NAME=imdtk
NET=vos_net
PROG=imdtk
RUN=${SCRIPTS}/runit
SHELL=/bin/bash
STACK=vos
TARG=/imdtk
TSTIMG=imdtk:test
