#!/bin/bash
#
# Execute monthly runs in sequence
#

init_date=`date +"%Y-%m-%d" -d "2016-06-01"`
start_date=`date +"%Y-%m-%d" -d "2016-06-01"`
end_date=`date +"%Y-%m-%d" -d "2018-06-01"`

check_date=`date +"%Y-%m-%d" -d "$end_date + 1 month"`;

current_date=$start_date
while [ "$current_date" != "$check_date" ]; do
    year=`date +"%Y" -d "$current_date"`
    month=`date +"%m" -d "$current_date"`
    day=`date +"%d" -d "$current_date"`
    # ------------------------------------------------------------------
    LOGFILE=log_setup_${year}-${month}.txt
    if [ "$current_date" == "$init_date" ]; then
        CMD="./run_month.sh -s ${year}-${month} >& $LOGFILE"
    else
        PARENT_ID=$(cat last_job_id.txt)
        CMD="./run_month.sh -s ${year}-${month} -r -p $PARENT_ID >& $LOGFILE"
    fi
    echo $CMD
    $CMD

    # ------------------------------------------------------------------
    # increment date
    current_date=`date +"%Y-%m-%d" -d "$current_date + 1 month"`;
done
