#!/bin/bash
#
# Execute a single month NEMO run
#


#-----------------------------------------------------------------------------
# user input

RUN_ROOT_DIR=../test/
YEAR=2016
MONTH=06

TEMPLATE_DIR=../forcing_files

RESTART=".false."

#-----------------------------------------------------------------------------
# parameters

START_DATE=$(date +"%Y%m%d" -d "$YEAR-$MONTH-01")
END_DATE=$(date +"%Y%m%d" -d "$YEAR-$MONTH-01 + 1 month")

CUR_DIR=$(pwd)

#-----------------------------------------------------------------------------
# generate rundir

if [ ! -d "$TEMPLATE_DIR" ]; then
  echo "ERROR: TEMPLATE_DIR not found: $TEMPLATE_DIR"
  exit -1
fi

RUN_ROOT_DIR=$(realpath $RUN_ROOT_DIR)

RUN_DIR=$RUN_ROOT_DIR/run_${YEAR}-${MONTH}
echo "Copying setup to $RUN_DIR"
mkdir -p $RUN_DIR


for f in $(ls $TEMPLATE_DIR/*); do
    echo "Copy $f"
    cp $f $RUN_DIR
done

JOB_SCRIPT="job_nemo.pbs"
echo "Copy $JOB_SCRIPT"
cp $JOB_SCRIPT $RUN_DIR

cd $RUN_DIR
ln -s nemo*.exe nemo.exe
ln -s xios*.exe xios.exe
cd $CUR_DIR

#-----------------------------------------------------------------------------
# generate namelists

NAMELIST_DIR="../template/namelist/"

for f in $(ls $NAMELIST_DIR/*); do
    echo "Copy $f"
    cp $f $RUN_DIR
done

# compute number of time steps
cp compute_ntimestep.py $RUN_DIR
cd $RUN_DIR
NTIMESTEP=$(python compute_ntimestep.py $START_DATE $END_DATE)
echo "Start date: $START_DATE"
echo "end   date: $END_DATE"
echo "Total time steps: $NTIMESTEP"
NML_FILE=namelist_cfg
echo "Generating namelist $NML_FILE"
sed -i "s|__INITDATE__|${START_DATE}|g" $NML_FILE
sed -i "s|__NTIMESTEP__|${NTIMESTEP}|g" $NML_FILE
sed -i "s|__RESTART__|${RESTART}|g" $NML_FILE
cd $CUR_DIR

#-----------------------------------------------------------------------------
# submit job

cd $RUN_DIR

sed -i "s|nemo4run|nemo${YEAR}${MONTH}|g" $JOB_SCRIPT

id=$(qsub $JOB_SCRIPT)
JOB_ID=${id%.*}
echo "parsed job id: $JOB_ID"

# submit post-proc as a dependency
# qsub -W depend=afterany:$JOB_ID $POSTPROC_SCRIPT

cd $CUR_DIR
