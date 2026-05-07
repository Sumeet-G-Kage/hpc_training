#!/bin/bash
#SBATCH --job-name=stream_run_intel_1
#SBATCH --output=/home/sumeet/benchmark-framework/logs/stream/case_stream_20260507_042711_004/run.log
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=01:00:00

echo "[JOB] Starting stream_run_intel_1"

module purge
module load intel/2025


export OMP_NUM_THREADS=1
cd /home/sumeet/benchmark-framework/builds/stream/install/bin
./stream_c.exe


echo "[JOB] Completed"
