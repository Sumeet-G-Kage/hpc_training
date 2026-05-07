import os
import subprocess
import yaml
import time
import datetime
from scripts.sbatch_generator import generate_sbatch

BASE = os.getcwd()

SRC_DIR = f"{BASE}/builds/stream/src"
BUILD_DIR = f"{BASE}/builds/stream/build"
INSTALL_DIR = f"{BASE}/builds/stream/install"

BINARY = f"{INSTALL_DIR}/bin/stream_c.exe"


# -----------------------------
# LOAD CONFIG
# -----------------------------
def load_config():
    with open("configs/stream.yaml") as f:
        return yaml.safe_load(f)


# -----------------------------
# CHECK BUILD
# -----------------------------
def is_built():
    return os.path.exists(BINARY) and os.path.getsize(BINARY) > 0


# -----------------------------
# RESULT PARSER
# -----------------------------
def parse_results(log_file):
    results = {}

    if not os.path.exists(log_file):
        return None

    with open(log_file) as f:
        for line in f:
            if line.startswith("Copy:"):
                results["Copy"] = float(line.split()[1])
            elif line.startswith("Scale:"):
                results["Scale"] = float(line.split()[1])
            elif line.startswith("Add:"):
                results["Add"] = float(line.split()[1])
            elif line.startswith("Triad:"):
                results["Triad"] = float(line.split()[1])

    return results if results else None


# -----------------------------
# RESULT DISPLAY
# -----------------------------
def print_result_box(results, compiler, threads):
    print("\n" + "=" * 50)
    print(f" STREAM RESULT | {compiler.upper()} | {threads} THREADS ")
    print("=" * 50)
    for k, v in results.items():
        print(f"{k:<10}: {v:>10.2f} MB/s")
    print("=" * 50 + "\n")


# -----------------------------
# BUILD SBATCH
# -----------------------------
def generate_build_sbatch(compiler, config, run_dir):

    comp = config["compilers"][compiler]

    modules = "\n".join([f"module load {m}" for m in comp["modules"]])
    env = "\n".join([f"export {k}={v}" for k, v in comp["env"].items()])

    array_size = config["stream"]["array_size"]
    ntimes = config["stream"]["ntimes"]

    build_sbatch = f"{run_dir}/build.sbatch"
    build_log = f"{run_dir}/build.log"

    commands = f"""
{env}

mkdir -p {SRC_DIR}
mkdir -p {BUILD_DIR}
mkdir -p {INSTALL_DIR}

if [ ! -d "{SRC_DIR}/STREAM" ]; then
    git clone https://github.com/jeffhammond/STREAM.git {SRC_DIR}/STREAM
fi

cd {SRC_DIR}/STREAM

cat <<EOF > CMakeLists.txt
cmake_minimum_required(VERSION 3.10)
project(STREAM C)

set(CMAKE_C_STANDARD 99)

add_executable(stream_c.exe stream.c)

target_compile_options(stream_c.exe PRIVATE
    -O3
    -mcmodel=large
    -DSTREAM_ARRAY_SIZE={array_size}
    -DNTIMES={ntimes}
)

install(TARGETS stream_c.exe DESTINATION bin)
EOF

cmake -S . -B {BUILD_DIR} -DCMAKE_INSTALL_PREFIX={INSTALL_DIR}
cmake --build {BUILD_DIR} -j
cmake --install {BUILD_DIR}
"""

    generate_sbatch(
        "scripts/templates/sbatch_base.sh",
        build_sbatch,
        {
            "job_name": f"stream_build_{compiler}",
            "log_file": build_log,
            "module_loads": f"module purge\n{modules}",
            "commands": commands
        }
    )

    return build_sbatch


# -----------------------------
# RUN SBATCH
# -----------------------------
def generate_run_sbatch(compiler, threads, config, run_dir):

    comp = config["compilers"][compiler]

    modules = "\n".join([f"module load {m}" for m in comp["modules"]])
    omp = f"export OMP_NUM_THREADS={threads}" if threads else ""

    run_sbatch = f"{run_dir}/run.sbatch"
    run_log = f"{run_dir}/run.log"

    commands = f"""
{omp}
cd {INSTALL_DIR}/bin
./stream_c.exe
"""

    generate_sbatch(
        "scripts/templates/sbatch_base.sh",
        run_sbatch,
        {
            "job_name": f"stream_run_{compiler}_{threads}",
            "log_file": run_log,
            "module_loads": f"module purge\n{modules}",
            "commands": commands
        }
    )

    return run_sbatch, run_log


# -----------------------------
# SUBMIT
# -----------------------------
def submit_job(script, dependency=None):
    if dependency:
        out = subprocess.check_output(["sbatch", f"--dependency=afterok:{dependency}", script])
    else:
        out = subprocess.check_output(["sbatch", script])
    return out.decode().strip().split()[-1]


# -----------------------------
# WAIT
# -----------------------------
def wait_for_job(job_id):
    while True:
        result = subprocess.run(["squeue", "-j", job_id], capture_output=True, text=True)
        if job_id not in result.stdout:
            break
        time.sleep(2)


# -----------------------------
# MAIN
# -----------------------------
def run(compiler=None, threads=None):

    config = load_config()

    compiler = compiler or "gcc"
    threads  = threads or 1

    print(f"[INFO] Compiler={compiler}  Threads={threads}")

    if compiler not in config["compilers"]:
        raise ValueError(f"Unknown compiler: {compiler}")

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # -----------------------------
    # CASE DIRECTORY
    # -----------------------------
    log_root = f"{BASE}/logs/stream"
    os.makedirs(log_root, exist_ok=True)
    existing = [d for d in os.listdir(log_root) if d.startswith("case_") and os.path.isdir(f"{log_root}/{d}")]
    numbers  = []
    for d in existing:
        try:
            numbers.append(int(d.split("_")[-1]))
        except ValueError:
            pass
    case_num  = max(numbers) + 1 if numbers else 1
    case_name = f"case_stream_{timestamp}_{case_num:03d}"
    final_dir = f"{log_root}/{case_name}"
    os.makedirs(final_dir, exist_ok=True)

    print(f"[INFO] Case    : {case_name}")
    print(f"[INFO] Log dir : {final_dir}")

    # -----------------------------
    # BUILD CHECK
    # -----------------------------

    if not is_built():
        print("[INFO] Binary not found → submitting build job")

        build_sbatch = generate_build_sbatch(compiler, config, final_dir)
        build_id     = submit_job(build_sbatch)

        print(f"[INFO] Build Job ID: {build_id}")
        print("[INFO] Waiting for build job to finish before checking binary...")
        wait_for_job(build_id)

        if not is_built():
            print(f"[ERROR] Build job finished but binary not found at: {BINARY}")
            print(f"[ERROR] Check build log in: {final_dir}/build.log")
            return

        # Generate run sbatch inside same directory after build succeeds
        run_sbatch, run_log = generate_run_sbatch(compiler, threads, config, final_dir)

        # -----------------------------
        # RUN (build path)
        # -----------------------------
        run_id = submit_job(run_sbatch)

    else:
        print("[INFO] Binary exists → skipping build, submitting run directly")

        run_sbatch, run_log = generate_run_sbatch(compiler, threads, config, final_dir)

        # -----------------------------
        # RUN (run-only path)
        # -----------------------------
        run_id = submit_job(run_sbatch)

    print(f"[INFO] Run Job ID : {run_id}")
    print(f"[INFO] Waiting for job {run_id}...")

    wait_for_job(run_id)

    # -----------------------------
    # RESULTS
    # -----------------------------
    results = parse_results(run_log)

    if results:
        print_result_box(results, compiler, threads)
    else:
        print(f"[WARNING] Could not parse results. Check: {run_log}")
