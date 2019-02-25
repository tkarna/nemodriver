#!/bin/bash
#
# Execute monthly runs in a sequence
#

# time span to execute, start date of first/last run
start_date="2016-06-01"
end_date="2018-06-01"

# cold/hot start date
init_date="2016-06-01"

hotstart=1
restart_src_dir=/lustre/tmp/karna/runs/bal-mfc/NemoNordic/reference/nemo4_2016-2018/run005/run_2016-11/output/restarts/

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
        if [ $hotstart = 1 ]; then
            CMD="./run_month.sh -r -R $restart_src_dir -s ${year}-${month}"
        else
            # coldstart
            CMD="./run_month.sh -s ${year}-${month}"
        fi
    else
        PARENT_ID=$(cat last_job_id.txt)
        CMD="./run_month.sh -s ${year}-${month} -r -p $PARENT_ID"
    fi
    echo $CMD
    $CMD &> $LOGFILE

    # ------------------------------------------------------------------
    # increment date
    current_date=`date +"%Y-%m-%d" -d "$current_date + 1 month"`;
done
