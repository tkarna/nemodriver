#!/bin/bash
#
# Execute monthly runs in a sequence
#

source env_path.sh

echo "Run tag: " $RUNTAG
echo "Run dir: " $(readlink -f $RUN_ROOT_DIR)

# global run_month flags
FLAGS=""

PARENT_FLAG=""
if [ -n "$MASTER_PARENT_JOB" ]; then
    echo "First run pending on job $MASTER_PARENT_JOB"
    PARENT_FLAG="-p $MASTER_PARENT_JOB"
fi

# ------------------------------------------------------------------

check_date=`date +"%Y-%m-%d" -d "$end_date + 1 month"`;

current_date=$start_date
while [ "$current_date" != "$check_date" ]; do
    year=`date +"%Y" -d "$current_date"`
    month=`date +"%m" -d "$current_date"`
    day=`date +"%d" -d "$current_date"`
    # ------------------------------------------------------------------
    LOGFILE=log_setup_${year}-${month}.txt
    if [ "$current_date" == "$init_date" ]; then
        # lauch first run from init
        if [ $HOTSTART = 1 ]; then
            CMD="./run_month.sh $FLAGS $PARENT_FLAG -r -R $HOTSTART_DIR -s ${year}-${month}"
        else
            # coldstart
            CMD="./run_month.sh $FLAGS $PARENT_FLAG -s ${year}-${month}"
        fi
    elif [ "$current_date" == "$start_date" ]; then
        # launch first run from a later date
        # restart from previous month that is already finished
        CMD="./run_month.sh $FLAGS -s ${year}-${month} -r $PARENT_FLAG"
    else
        # push other jobs to the queue
        PARENT_ID=$(cat last_job_id.txt)
        CMD="./run_month.sh $FLAGS -s ${year}-${month} -r -p $PARENT_ID"
    fi
    echo $CMD
    $CMD &> $LOGFILE
    if [ "$?" -ne 0 ]; then
        echo "  FAILED: see $LOGFILE"
        tail -n 10 $LOGFILE
        exit 1
    fi 

    # ------------------------------------------------------------------
    # increment date
    current_date=`date +"%Y-%m-%d" -d "$current_date + 1 month"`;
done
