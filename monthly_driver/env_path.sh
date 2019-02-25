#
# Set directory paths for NEMO run
#

# root directory where all individual run dirs will be created
RUNTAG=wam-tauoc-01
RUN_ROOT_DIR=../../$RUNTAG

# choose which namelist template to use
# NMLCONFIG=master
NMLCONFIG=wam-coupling

# config specific flags
FLAG_WAVE=.true.
FLAG_WDRAG=.false.
FLAG_STOKES=.false.
FLAG_NTAUW=.true.
FLAG_TAUW=.false.

# prefix to be used in run directory names, e.g. run_2016-06
RUNDIR_PREFIX='run'

# directory that contains all the necessary input files
# - netcdf files, *.xml files, nemo xios binary files
# NOTE: do not include namelist files here
CFG_TEMPLATE_DIR=$RUN_ROOT_DIR/../run_template

# time span to execute, start date of first/last run
start_date="2016-11-01"
end_date="2017-03-01"

# cold/hot start date
init_date="2016-11-01"

# hotstart option
HOTSTART=1
RESTART_SRC_DIR=/lustre/tmp/karna/runs/bal-mfc/NemoNordic/reference/nemo4_2016-2018/run005/run_2016-11/output/restarts/
