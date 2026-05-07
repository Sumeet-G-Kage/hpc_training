#!/bin/bash
set -e

VERSION=$1
PREFIX="$HOME/benchmark-framework/builds/gcc/$VERSION"
MODULEFILE="$HOME/modulefiles/gcc/$VERSION"

if [ -z "$VERSION" ]; then
    echo "[FRAMEWORK] Usage: uninstall.sh <version>"
    exit 1
fi

if [ -d "$PREFIX" ]; then
    echo "[FRAMEWORK] Removing GCC $VERSION from $PREFIX"
    rm -rf "$PREFIX"
    echo "[FRAMEWORK] GCC $VERSION removed"
else
    echo "[FRAMEWORK] GCC $VERSION not found at $PREFIX"
fi

if [ -f "$MODULEFILE" ]; then
    echo "[FRAMEWORK] Removing modulefile $MODULEFILE"
    rm -f "$MODULEFILE"
    echo "[FRAMEWORK] Modulefile removed"
fi
