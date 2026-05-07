#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --output={log_file}
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=01:00:00

echo "[JOB] Starting {job_name}"

{module_loads}

{commands}

echo "[JOB] Completed"
