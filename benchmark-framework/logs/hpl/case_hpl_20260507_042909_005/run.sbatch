#!/bin/bash
#SBATCH --job-name=hpl_run_intel_np1_t1
#SBATCH --output=/home/sumeet/benchmark-framework/logs/hpl/case_hpl_20260507_042909_005/run.log
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=01:00:00

echo "[JOB] Starting hpl_run_intel_np1_t1"

module purge
module load intel/2025


export OMP_NUM_THREADS=1
cd /home/sumeet/benchmark-framework/builds/hpl/src/hpl-2.3/bin/INTEL

echo "[RUN] HPL.dat:"
cat HPL.dat

mpirun -np 1 ./xhpl


echo "[JOB] Completed"
