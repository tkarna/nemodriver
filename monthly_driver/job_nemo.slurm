#!/bin/bash
#SBATCH --job-name=nemo4run
#SBATCH --account=Project_2001635
#SBATCH --partition=fmi
#SBATCH --time=14:00:00
#SBATCH --ntasks=319
#SBATCH --nodes=8
#SBATCH --exclusive
#SBATCH -o stdout.log
#SBATCH -e stderr.log
#SBATCH --mem-per-cpu=4G
 
module load intel/19.0.4
module del hpcx-mpi
module load intel-mpi/18.0.5
module load hdf5/1.10.4-mpi
module load netcdf/4.7.0
module load netcdf-fortran/4.4.4

echo "Run begins at" $(date "+%Y-%m-%d %H:%M:%S")

#__LINK_RESTART_CMD__
 
cat > task_config.txt <<EOL
0-310 ./nemo.exe
311-318 ./xios.exe
EOL

srun --multi-prog task_config.txt
