#!/bin/bash

VERSION=$1
BASE="$HOME/benchmark-framework/builds/openmpi"

if [ -z "$VERSION" ]; then

    echo "[FRAMEWORK] Removing all OpenMPI builds"

    rm -rf "$BASE"

    echo "[FRAMEWORK] All OpenMPI builds removed"

else

    TARGET="$BASE/$VERSION"

    if [ -d "$TARGET" ]; then

        echo "[FRAMEWORK] Removing OpenMPI $VERSION"

        rm -rf "$TARGET"

        echo "[FRAMEWORK] OpenMPI $VERSION removed"

    else

        echo "[FRAMEWORK] OpenMPI $VERSION not found"

    fi

fi
