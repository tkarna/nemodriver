#
# Set directory paths for NEMO run
#

# root directory where all individual run dirs will be created
RUNTAG=run4-03
RUN_ROOT_DIR=../../$RUNTAG

# choose which namelist template to use
NMLCONFIG=cal2014-03

# config specific flags
FLAG_WAVE=.false.
FLAG_WDRAG=.false.
FLAG_STOKES=.false.
FLAG_NTAUW=.false.
FLAG_TAUW=.false.

# prefix to be used in run directory names, e.g. run_2016-06
RUNDIR_PREFIX='run'

# directory that contains all the necessary input files
# - netcdf files, *.xml files, nemo xios binary files
# NOTE: do not include namelist files here
CFG_TEMPLATE_DIR=$RUN_ROOT_DIR/../run_template

# time span to execute, start date of first/last run
start_date="2014-10-01"
end_date="2015-03-01"

# cold/hot start date
init_date="2014-10-01"

# hotstart option
HOTSTART=0
HOTSTART_DIR=''
