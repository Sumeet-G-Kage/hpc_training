# Benchmark Framework

A modular, extensible HPC benchmarking framework that automates environment setup, component installation, benchmark builds, job submission via SLURM, and result collection.

**Author:** Sumeet G Kage  
**Repository:** [https://github.com/Sumeet-G-Kage/hpc_training](https://github.com/Sumeet-G-Kage/hpc_training)

---

## Table of Contents

- [Overview](#overview)
- [Directory Structure](#directory-structure)
- [Prerequisites](#prerequisites)
- [Usage](#usage)
  - [Preprocess](#preprocess)
  - [Build](#build)
  - [Cleanup](#cleanup)
  - [Postprocess](#postprocess)
- [Framework Flags](#framework-flags)

---

## Overview

The framework provides a single entry point `run.py` that handles the full lifecycle of HPC benchmarking:

- **Preprocess** — Detects and installs system components (e.g. Slurm), builds tools from source (OpenMPI, GCC), and auto-generates environment modulefiles
- **Build** — Checks if the benchmark binary already exists, submits a SLURM build job if not, waits for completion, then submits the run job and collects results
- **Cleanup** — Safely removes builds and logs for a given app or component
- **Postprocess** — Re-displays results from any previous run using just the log directory name

All benchmark runs are logged in sequentially numbered case directories (`case_<app>_<timestamp>_<NNN>`) so every run is traceable and reproducible.

---

## Directory Structure

```
benchmark-framework/
├── apps/                        # Benchmark app modules
│   ├── stream/
│   │   └── stream.py            # STREAM benchmark logic
│   └── hpl/
│       └── hpl.py               # HPL benchmark logic
├── builds/                      # Compiled binaries (generated at runtime)
├── components/                  # System-level dependencies
├── configs/                     # YAML configuration files
│   ├── stream.yaml
│   └── hpl.yaml
├── logs/                        # Per-run log directories (generated at runtime)
├── scripts/                     # Orchestration scripts
│   ├── build.py
│   ├── cleanup.py
│   ├── preprocess.py
│   ├── sbatch_generator.py
│   └── templates/
│       └── sbatch_base.sh
├── state/                       # Component install state flags
└── run.py                       # Entry point
```

---

## Prerequisites

- Python 3.6+
- SLURM workload manager (`sbatch`, `squeue`)
- `wget`, `git`, `cmake` available on the system
- At least one supported compiler stack loaded via modules


---

## Usage

All commands are run from inside the `benchmark-framework/` directory.

### Preprocess

Install system components and build tools from source:

```bash
# Detect and install all system components (e.g. Slurm)
python3 run.py preprocess

# Build OpenMPI from source + generate modulefile
python3 run.py preprocess --component openmpi --version 5.0.7

# Build GCC from source + generate modulefile
python3 run.py preprocess --component gcc --version 15.2
```

---

### Build

Build and run a benchmark. If the binary already exists the build step is skipped automatically.

#### STREAM

```bash
# Default (gcc compiler, 1 thread)
python3 run.py build --app stream --compiler gcc --threads 1

# AMD AOCC stack, 4 threads
python3 run.py build --app stream --compiler aocc --threads 4

# Intel stack
python3 run.py build --app stream --compiler intel --threads 1
```

#### HPL

```bash
# Defaults from configs/hpl.yaml
python3 run.py build --app hpl --compiler aocc

# Custom problem size, 1 MPI rank
python3 run.py build --app hpl --compiler aocc --np 1 --N 10000 --NB 256 --P 1 --Q 1

# 4 MPI ranks, 2x2 process grid, 2 OpenMP threads per rank
python3 run.py build --app hpl --compiler aocc --np 4 --N 20000 --NB 256 --P 2 --Q 2 --threads 2

# Intel MKL stack
python3 run.py build --app hpl --compiler intel --np 1 --N 10000 --NB 256 --P 1 --Q 1
```

> **Note:** For HPL, `--np` must equal `--P * --Q`. The framework validates this before submitting any job.

Each run creates a sequentially numbered directory under `logs/<app>/`:
```
logs/hpl/
    case_hpl_20260507_091200_001/    # first run — build + run
        build.sbatch
        build.log
        run.sbatch
        run.log
    case_hpl_20260507_092100_002/    # second run — binary existed, run only
        run.sbatch
        run.log
```

---

### Cleanup

Remove builds and logs for an app or component:

```bash
# Remove all builds and logs for STREAM
python3 run.py cleanup --app stream

# Remove all builds and logs for HPL
python3 run.py cleanup --app hpl

# Remove a specific OpenMPI version build
python3 run.py cleanup --component openmpi --version 5.0.7

# Remove all OpenMPI builds
python3 run.py cleanup --component openmpi
```

---

### Postprocess

Re-display results from any previous run using just the case directory name. The framework auto-detects the app (stream or hpl) by searching under `logs/`.

```bash
python3 run.py -p case_stream_20260507_042019_001
python3 run.py -p case_hpl_20260507_040917_001
```

---

## Framework Flags

| Flag | Applies To | Description |
|------|-----------|-------------|
| `--app` | build, cleanup | App name: `stream` or `hpl` |
| `--compiler` | build | Compiler stack: `gcc`, `aocc`, `intel` |
| `--threads` | build | `OMP_NUM_THREADS` for STREAM and HPL |
| `--np` | build (HPL) | Number of MPI ranks — must equal `P × Q` |
| `--N` | build (HPL) | Problem size |
| `--NB` | build (HPL) | Block size |
| `--P` | build (HPL) | Process grid rows |
| `--Q` | build (HPL) | Process grid cols |
| `--component` | preprocess, cleanup | Component name: `slurm`, `openmpi`, `gcc` |
| `--version` | preprocess, cleanup | Version for component builds |
| `-p <casedir>` | postprocess | Display results for a previous run |
| `--help` / `-h` | all | Show help and usage examples |
