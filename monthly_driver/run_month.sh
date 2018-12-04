#!/bin/bash
#
# Execute a single month NEMO run
#


#-----------------------------------------------------------------------------
# parse user input

# YEAR=2016
# MONTH=06
# PARENT_JOB=

PARENT_JOB=''
RESTART=".false."

while getopts ":s:p:rh" opt; do
  case $opt in
    h )
      echo "Usage:"
      echo "    pip -h                         Display this help message."
      echo "    pip -s 2018-03                 Run month 2018-03"
      echo "    pip -r                         Restart from previous month"
      echo "    pip ...  -p 123456             Add job dependency. Job starts"
      echo "                                   when parent job has finished."
      exit 0
      ;;
    s)
      YEARMONTH=$OPTARG
      ;;
    p)
      PARENT_JOB=$OPTARG
      ;;
    r)
      RESTART=".true."
      ;;
    \? )
      echo "Invalid Option: -$OPTARG" 1>&2
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      exit 1
      ;;
  esac
done

if [ -z "$YEARMONTH" ]; then
    echo "Invalid Option: YEAR-MONTH must be given" 1>&2
    exit 1
fi

YEAR=${YEARMONTH%-*}
MONTH=${YEARMONTH#*-}

if [ ${#YEAR} -ne "4" ]; then
    echo "Invalid Option: could not parse YEAR: $YEAR" 1>&2
    exit 1
fi

if [ ${#MONTH} -ne "2" ]; then
    echo "Invalid Option: could not parse MONTH: $MONTH" 1>&2
    exit 1
fi

echo $RESTART

source env_path.sh

#-----------------------------------------------------------------------------
# parameters

START_DATE=$(date +"%Y%m%d" -d "$YEAR-$MONTH-01")
END_DATE=$(date +"%Y%m%d" -d "$YEAR-$MONTH-01 + 1 month")

CUR_DIR=$(pwd)

#-----------------------------------------------------------------------------
# generate rundir

RUN_ROOT_DIR=$(realpath $RUN_ROOT_DIR)
CFG_TEMPLATE_DIR=$(realpath $CFG_TEMPLATE_DIR)

if [ ! -d "$CFG_TEMPLATE_DIR" ]; then
  echo "ERROR: CFG_TEMPLATE_DIR not found: $CFG_TEMPLATE_DIR"
  exit -1
fi

RUN_DIR=$RUN_ROOT_DIR/run_${YEAR}-${MONTH}
echo "Copying setup to $RUN_DIR"
mkdir -p $RUN_DIR

mkdir -p $RUN_DIR/output/{data,logs,restarts}

REL_TEMPLATE_DIR=$(realpath --relative-to=$RUN_DIR $CFG_TEMPLATE_DIR)

for fpath in $(ls $CFG_TEMPLATE_DIR/*); do
    f=$(basename $fpath)
    extension="${f##*.}"
    if [ "$extension" = "nc" ]; then
        echo "Link $f"
        ln -s $REL_TEMPLATE_DIR/$f $RUN_DIR/$f
    else
        echo "Copy $f"
        cp $fpath $RUN_DIR
    fi
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
cp nemo_duration.py $RUN_DIR

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

if [ -z "$PARENT_JOB" ]; then
    DEP_STR=''
else
    echo "Jobs starts after parent job: $PARENT_JOB"
    DEP_STR="-W depend=afterok:${PARENT_JOB}"
fi

QCMD="qsub $JOB_SCRIPT $DEP_STR"
echo $QCMD
id=$($QCMD)
JOB_ID=${id%.*}
echo "parsed job id: $JOB_ID"

# submit post-proc as a dependency
# qsub -W depend=afterany:$JOB_ID $POSTPROC_SCRIPT

cd $CUR_DIR
