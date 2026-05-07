#!/bin/bash
#SBATCH --job-name=hpl_run_aocc_np1_t1
#SBATCH --output=/home/sumeet/benchmark-framework/logs/hpl/case_hpl_20260507_042817_004/run.log
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=01:00:00

echo "[JOB] Starting hpl_run_aocc_np1_t1"

module purge
module load aocc/5.1
module load aocl/5.2
module load openmpi/5.0.9-aocc


export OMP_NUM_THREADS=1
cd /home/sumeet/benchmark-framework/builds/hpl/src/hpl-2.3/bin/AMD

echo "[RUN] HPL.dat:"
cat HPL.dat

mpirun -np 1 ./xhpl


echo "[JOB] Completed"
