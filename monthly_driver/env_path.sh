#
# Set directory paths for NEMO run
#

# root directory where all individual run dirs will be created
RUNTAG=run004
RUN_ROOT_DIR=../../$RUNTAG

# prefix to be used in run directory names, e.g. run_2016-06
RUNDIR_PREFIX='run'

# directory that contains all the necessary input files
# - netcdf files, *.xml files, nemo xios binary files
# NOTE: do not include namelist files here
CFG_TEMPLATE_DIR=$RUN_ROOT_DIR/../run_template
