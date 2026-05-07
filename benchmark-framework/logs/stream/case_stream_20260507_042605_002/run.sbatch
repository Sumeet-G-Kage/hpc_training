#!/bin/bash
#SBATCH --job-name=stream_run_aocc_1
#SBATCH --output=/home/sumeet/benchmark-framework/logs/stream/case_stream_20260507_042605_002/run.log
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=01:00:00

echo "[JOB] Starting stream_run_aocc_1"

module purge
module load aocc/5.1
module load aocl/5.2
module load openmpi/5.0.9-aocc


export OMP_NUM_THREADS=1
cd /home/sumeet/benchmark-framework/builds/stream/install/bin
./stream_c.exe


echo "[JOB] Completed"
