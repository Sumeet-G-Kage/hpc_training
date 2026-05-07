#!/bin/bash
#SBATCH --job-name=stream_build_aocc
#SBATCH --output=/home/sumeet/benchmark-framework/logs/stream/case_stream_20260507_042509_001/build.log
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=01:00:00

echo "[JOB] Starting stream_build_aocc"

module purge
module load aocc/5.1
module load aocl/5.2
module load openmpi/5.0.9-aocc


export CC=clang
export CXX=clang++

mkdir -p /home/sumeet/benchmark-framework/builds/stream/src
mkdir -p /home/sumeet/benchmark-framework/builds/stream/build
mkdir -p /home/sumeet/benchmark-framework/builds/stream/install

if [ ! -d "/home/sumeet/benchmark-framework/builds/stream/src/STREAM" ]; then
    git clone https://github.com/jeffhammond/STREAM.git /home/sumeet/benchmark-framework/builds/stream/src/STREAM
fi

cd /home/sumeet/benchmark-framework/builds/stream/src/STREAM

cat <<EOF > CMakeLists.txt
cmake_minimum_required(VERSION 3.10)
project(STREAM C)

set(CMAKE_C_STANDARD 99)

add_executable(stream_c.exe stream.c)

target_compile_options(stream_c.exe PRIVATE
    -O3
    -mcmodel=large
    -DSTREAM_ARRAY_SIZE=80000000
    -DNTIMES=10
)

install(TARGETS stream_c.exe DESTINATION bin)
EOF

cmake -S . -B /home/sumeet/benchmark-framework/builds/stream/build -DCMAKE_INSTALL_PREFIX=/home/sumeet/benchmark-framework/builds/stream/install
cmake --build /home/sumeet/benchmark-framework/builds/stream/build -j
cmake --install /home/sumeet/benchmark-framework/builds/stream/build


echo "[JOB] Completed"
