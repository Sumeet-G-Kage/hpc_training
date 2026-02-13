#!/bin/bash

#SBATCH --job-name=python_build
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=1G
#SBATCH --time=00:30:00
#SBATCH --output=python_build_out.txt
#SBATCH --error=python_build_err.txt

echo "PYTHON VERSION 3.13.12  INSTALLATION STARTED"
echo "Installation started on $(date)"
wget https://www.python.org/ftp/python/3.13.12/Python-3.13.12.tar.xz
mkdir python31
cp Python-3.13.12.tar.xz python31
cd pyhton31


tar -xvf Python-3.13.12.tar.xz

cd Python-3.13.12
./configure --prefix=/root/python31
make
make install



echo "Python installation done"
echo "Installed on $(date)"
