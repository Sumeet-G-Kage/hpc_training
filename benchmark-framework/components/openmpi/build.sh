#!/bin/bash
set -e

VERSION=$1

PREFIX="$HOME/benchmark-framework/builds/openmpi/$VERSION"
SRC="/tmp/openmpi-build"

if [ -d "$PREFIX" ]; then
    echo "[FRAMEWORK] OpenMPI $VERSION already installed. Skipping."
    exit 0
fi

echo "[FRAMEWORK] Building OpenMPI $VERSION"

mkdir -p $SRC
cd $SRC

MAJOR=$(echo $VERSION | cut -d '.' -f1,2)

URL="https://download.open-mpi.org/release/open-mpi/v$MAJOR/openmpi-$VERSION.tar.gz"

if [ ! -f openmpi-$VERSION.tar.gz ]; then
    echo "[FRAMEWORK] Downloading source"
    wget -q $URL
fi

if [ ! -d openmpi-$VERSION ]; then
    tar -xzf openmpi-$VERSION.tar.gz
fi

cd openmpi-$VERSION

echo "[FRAMEWORK] Configuring"
./configure --prefix=$PREFIX

echo "[FRAMEWORK] Compiling"
make -j$(nproc)

echo "[FRAMEWORK] Installing"
make install

echo "[FRAMEWORK] OpenMPI $VERSION installed successfully"
