#
# Set directory paths for NEMO run
#

# root directory where all individual run dirs will be created
RUN_ROOT_DIR=../..

# directory that contains all the necessary input files
# - netcdf files, *.xml files, nemo xios binary files
# NOTE: do not include namelist files here
CFG_TEMPLATE_DIR=$RUN_ROOT_DIR/run_template
