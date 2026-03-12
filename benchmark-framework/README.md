# Benchmark Automation Framework

The **Benchmark Automation Framework** is a modular system designed to automate the setup, build, and cleanup of benchmarking environments.  
It simplifies benchmarking workflows by automating component installation, software builds, and environment cleanup.

---

## Overview

Setting up a benchmarking environment manually can be time-consuming and repetitive.  
This framework automates the entire lifecycle of benchmark preparation.

The framework provides:

- Automated installation of required system components
- Automated building of benchmark software versions
- Safe cleanup of installed components
- A modular and extensible structure

The framework is controlled through a single entry point:


python3 run.py


---

## Framework Structure


benchmark-framework

│

├── components/ # system components (e.g., Slurm)

├── build/ # build scripts for benchmark software

├── builds/ # compiled software versions

├── scripts/ # framework logic (preprocess, build, cleanup)

├── config/ # configuration files

├── state/ # tracks installed components

├── logs/ # installation logs

└── run.py # main controller


---

## Framework Workflow

The framework operates in three main stages.

### 1. Preprocess

Checks whether required system components exist and installs them if needed.


python3 run.py preprocess


Example: installs Slurm if it is not already installed.

---

### 2. Build

Builds different versions of benchmark software.


python3 run.py build


Example: builds OpenMPI versions defined in `versions.conf`.

Built software is stored in:


builds/<component>/<version>


---

### 3. Cleanup

Removes software and components installed by the framework.


python3 run.py cleanup


This restores the system to its original state.

---

## Command-Line Flags

The framework supports optional flags for targeted operations.

### Build a specific version


python3 run.py build --component openmpi --version 5.0.7


### Remove a specific component


python3 run.py cleanup --component slurm


### Remove a specific build version


python3 run.py cleanup --component openmpi --version 5.0.7


These flags allow more controlled and flexible framework operations.

---

## Example Usage

Install required components:


python3 run.py preprocess


Build benchmark software:


python3 run.py build


Build a specific version:


python3 run.py build --component openmpi --version 5.0.6


Cleanup framework installations:


python3 run.py cleanup


---

## Key Features

- Modular framework design
- Automated component installation
- Versioned software builds
- Targeted execution using flags
- Safe cleanup mechanism

---

---
