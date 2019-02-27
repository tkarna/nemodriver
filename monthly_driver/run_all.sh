#!/bin/bash
#
# Execute monthly runs in a sequence
#

source env_path.sh

# global run_month flags
FGLAS=""

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
        # lauch first run
        if [ $HOTSTART = 1 ]; then
            CMD="./run_month.sh $FGLAS -r -R $HOTSTART_DIR -s ${year}-${month}"
        else
            # coldstart
            CMD="./run_month.sh $FGLAS -s ${year}-${month}"
        fi
    else
        PARENT_ID=$(cat last_job_id.txt)
        CMD="./run_month.sh $FGLAS -s ${year}-${month} -r -p $PARENT_ID"
    fi
    echo $CMD
    $CMD &> $LOGFILE

    # ------------------------------------------------------------------
    # increment date
    current_date=`date +"%Y-%m-%d" -d "$current_date + 1 month"`;
done
