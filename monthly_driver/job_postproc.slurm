#!/bin/bash
#SBATCH --job-name=postproc
#SBATCH --account=Project_2001635
#SBATCH --partition=fmi
#SBATCH --time=05:00:00
#SBATCH --ntasks=4
#SBATCH --mem-per-cpu=4G
#SBATCH -o stdout.log
#SBATCH -e stderr.log

# activate python
module load python-env

# compress output
COMP_OPT='d1:cx/12,y/12,deptht/56,time_counter/1'

grids=(grid_T grid_U grid_V grid_W)
for g in "${grids[@]}"; do
    cmd="python compress_ncfiles.py -vv -D -s $COMP_OPT output NORDIC_*${g}*.nc"
    echo $cmd
    $cmd &> log_postproc_${g}.txt &
done

wait

# extract transect
RUNTAG=$(basename "$(pwd)")  # run_2016-10
python extract_transect.py output/NORDIC_?h_grid_T_*.nc domain_cfg.nc \
    salinity transect_baltic-inflow_lonlat.txt \
    output/transect_baltic-inflow_salinity_${RUNTAG/run_/}.nc
