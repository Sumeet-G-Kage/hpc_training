#!/bin/bash
set -e

VERSION=$1
PREFIX="$HOME/benchmark-framework/builds/gcc/$VERSION"
SRC="/tmp/gcc-build"

if [ -d "$PREFIX" ]; then
    echo "[FRAMEWORK] GCC $VERSION already installed. Skipping."
    exit 0
fi

echo "[FRAMEWORK] Building GCC $VERSION"

mkdir -p $SRC
cd $SRC

MAJOR=$(echo $VERSION | cut -d '.' -f1)
URL="https://ftp.gnu.org/gnu/gcc/gcc-$VERSION/gcc-$VERSION.tar.gz"

if [ ! -f gcc-$VERSION.tar.gz ]; then
    echo "[FRAMEWORK] Downloading source from $URL"
    wget -q $URL
fi

if [ ! -d gcc-$VERSION ]; then
    echo "[FRAMEWORK] Extracting source"
    tar -xzf gcc-$VERSION.tar.gz
fi

cd gcc-$VERSION

# Download prerequisites (gmp, mpfr, mpc)
echo "[FRAMEWORK] Downloading prerequisites"
./contrib/download_prerequisites

mkdir -p build
cd build

echo "[FRAMEWORK] Configuring"
../configure \
    --prefix=$PREFIX \
    --enable-languages=c,c++,fortran \
    --disable-multilib \
    --enable-shared \
    --enable-threads=posix \
    --with-system-zlib

echo "[FRAMEWORK] Compiling (this may take a while)"
make -j$(nproc)

echo "[FRAMEWORK] Installing"
make install

echo "[FRAMEWORK] GCC $VERSION installed successfully at $PREFIX"
