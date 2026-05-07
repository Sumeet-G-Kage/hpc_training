import os
import subprocess
import yaml
import time
import datetime
from scripts.sbatch_generator import generate_sbatch

BASE = os.getcwd()

SRC_DIR     = f"{BASE}/builds/hpl/src"
HPL_VERSION = "2.3"
HPL_TARBALL = f"hpl-{HPL_VERSION}.tar.gz"
HPL_URL     = f"https://www.netlib.org/benchmark/hpl/{HPL_TARBALL}"
HPL_SRC     = f"{SRC_DIR}/hpl-{HPL_VERSION}"


# -----------------------------
# LOAD CONFIG
# -----------------------------
def load_config():
    with open("configs/hpl.yaml") as f:
        return yaml.safe_load(f)


# -----------------------------
# BINARY PATH
# -----------------------------
def binary_path(arch):
    return f"{HPL_SRC}/bin/{arch}/xhpl"


# -----------------------------
# CHECK BUILD
# -----------------------------
def is_built(arch):
    bp = binary_path(arch)
    return os.path.exists(bp) and os.path.getsize(bp) > 0


# -----------------------------
# BUILD HPL.dat STRING FROM YAML
# -----------------------------
def make_hpl_dat(N, NB, P, Q, dat):
    return (
        "HPLinpack benchmark input file\n"
        "Innovative Computing Laboratory, University of Tennessee\n"
        "HPL.out      output file name (if any)\n"
        "6            device out (6=stdout,7=stderr,file)\n"
        "1            # of problems sizes (N)\n"
        f"{N}          Ns\n"
        "1            # of NBs\n"
        f"{NB}         NBs\n"
        "0            PMAP process mapping (0=Row-,1=Column-major)\n"
        "1            # of process grids (P x Q)\n"
        f"{P}          Ps\n"
        f"{Q}          Qs\n"
        f"{dat['threshold']}         threshold\n"
        "1            # of panel fact\n"
        f"{dat['pfact']}            PFACTs (0=left, 1=Crout, 2=Right)\n"
        "1            # of recursive stopping criterium\n"
        f"{dat['nbmin']}            NBMINs (>= 1)\n"
        "1            # of panels in recursion\n"
        f"{dat['ndiv']}            NDIVs\n"
        "1            # of recursive panel fact.\n"
        f"{dat['rfact']}            RFACTs (0=left, 1=Crout, 2=Right)\n"
        "1            # of broadcast\n"
        f"{dat['bcast']}            BCASTs (0=1rg,1=1rM,2=2rg,3=2rM,4=Lng,5=LnM)\n"
        "1            # of lookahead depth\n"
        f"{dat['depth']}            DEPTHs (>=0)\n"
        f"{dat['swap']}            SWAP (0=bin-exch,1=long,2=mix)\n"
        f"{dat['swap_threshold']}           swapping threshold\n"
        f"{dat['l1']}            L1 in (0=transposed,1=no-transposed) form\n"
        f"{dat['u']}            U  in (0=transposed,1=no-transposed) form\n"
        f"{dat['equilibration']}            Equilibration (0=no,1=yes)\n"
        f"{dat['alignment']}            memory alignment in double (> 0)\n"
    )


# -----------------------------
# RESULT PARSER
# -----------------------------
def parse_results(log_file):
    results = {}

    if not os.path.exists(log_file):
        return None

    with open(log_file) as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith("WR") or stripped.startswith("WC"):
                parts = stripped.split()
                if len(parts) >= 7:
                    try:
                        results["N"]      = int(parts[1])
                        results["NB"]     = int(parts[2])
                        results["P"]      = int(parts[3])
                        results["Q"]      = int(parts[4])
                        results["Time"]   = float(parts[5])
                        results["Gflops"] = float(parts[6])
                    except (ValueError, IndexError):
                        continue
                break

    return results if results else None


# -----------------------------
# RESULT DISPLAY
# -----------------------------
def print_result_box(results, compiler, np):
    print("\n" + "=" * 50)
    print(f" HPL RESULT | {compiler.upper()} | {np} MPI RANKS ")
    print("=" * 50)
    print(f"{'N':<10}: {results['N']}")
    print(f"{'NB':<10}: {results['NB']}")
    print(f"{'P x Q':<10}: {results['P']} x {results['Q']}")
    print(f"{'Time':<10}: {results['Time']:.2f} s")
    print(f"{'Gflops':<10}: {results['Gflops']:.4e}")
    print("=" * 50 + "\n")


# -----------------------------
# BUILD SBATCH
# -----------------------------
def generate_build_sbatch(compiler, config, run_dir):
    comp    = config["compilers"][compiler]
    arch    = comp["arch"]
    modules = "\n".join([f"module load {m}" for m in comp["modules"]])

    la_dir  = comp["la_dir"]
    la_inc  = comp["la_inc"]
    la_lib  = comp["la_lib"]
    mpi_dir = comp["mpi_dir"]
    cc      = comp["cc"]
    linker  = comp["linker"]

    build_sbatch = f"{run_dir}/build.sbatch"
    build_log    = f"{run_dir}/build.log"

    commands = f"""
mkdir -p {SRC_DIR}

# ---- Download & extract ----
if [ ! -f "{SRC_DIR}/{HPL_TARBALL}" ]; then
    wget -q {HPL_URL} -O {SRC_DIR}/{HPL_TARBALL}
fi

if [ ! -d "{HPL_SRC}" ]; then
    tar -xf {SRC_DIR}/{HPL_TARBALL} -C {SRC_DIR}
fi

cd {HPL_SRC}

# ---- Copy the provided base Make file ----
cp setup/Make.Linux_PII_CBLAS Make.{arch}

# ---- Patch only the fields that need to change ----
sed -i "s|^ARCH\\s*=.*|ARCH         = {arch}|"                   Make.{arch}
sed -i "s|^TOPdir\\s*=.*|TOPdir       = {HPL_SRC}|"              Make.{arch}
sed -i "s|^MPdir\\s*=.*|MPdir        = {mpi_dir}|"               Make.{arch}
sed -i "s|^MPinc\\s*=.*|MPinc        = -I\\$(MPdir)/include|"    Make.{arch}
sed -i "s|^MPlib\\s*=.*|MPlib        = -L\\$(MPdir)/lib -lmpi|"  Make.{arch}
sed -i "s|^LAdir\\s*=.*|LAdir        = {la_dir}|"                Make.{arch}
sed -i "s|^LAinc\\s*=.*|LAinc        = -I{la_inc}|"              Make.{arch}
sed -i "s|^LAlib\\s*=.*|LAlib        = -L\\$(LAdir) {la_lib}|"   Make.{arch}
sed -i "s|^CC\\s*=.*|CC           = {cc}|"                       Make.{arch}
sed -i "s|^LINKER\\s*=.*|LINKER       = {linker}|"               Make.{arch}
# Intel icx aggressively optimizes the epsilon detection loop in HPL_dlamch.c
# causing eps=0.0 and division by zero in residual check → FAILED.
# -fp-model precise disables that optimization and fixes it.
if [ "{compiler}" = "intel" ]; then
    sed -i "s|^CCFLAGS\\s*=.*|CCFLAGS      = \\$(HPL_DEFS) -O3 -fp-model precise|" Make.{arch}
else
    sed -i "s|^CCFLAGS\\s*=.*|CCFLAGS      = \\$(HPL_DEFS) -O3 -fomit-frame-pointer|" Make.{arch}
fi

# ---- Build (single-threaded: HPL Makefile creates dirs sequentially) ----
make arch={arch}

echo "[BUILD] Result: $(ls {HPL_SRC}/bin/{arch}/xhpl 2>/dev/null && echo OK || echo FAILED)"
"""

    generate_sbatch(
        "scripts/templates/sbatch_base.sh",
        build_sbatch,
        {
            "job_name":     f"hpl_build_{compiler}",
            "log_file":     build_log,
            "module_loads": f"module purge\n{modules}",
            "commands":     commands
        }
    )

    return build_sbatch


# -----------------------------
# RUN SBATCH
# -----------------------------
def generate_run_sbatch(compiler, np, threads, N, NB, P, Q, config, run_dir):
    comp    = config["compilers"][compiler]
    arch    = comp["arch"]
    modules = "\n".join([f"module load {m}" for m in comp["modules"]])
    dat     = config["hpl"]["dat"]

    bin_dir    = f"{HPL_SRC}/bin/{arch}"
    run_sbatch = f"{run_dir}/run.sbatch"
    run_log    = f"{run_dir}/run.log"

    # Build HPL.dat content from yaml config + runtime N/NB/P/Q
    hpl_dat_content = make_hpl_dat(N, NB, P, Q, dat)

    # Write HPL.dat to bin/<arch>/ before the job runs
    hpl_dat_path = f"{bin_dir}/HPL.dat"
    os.makedirs(bin_dir, exist_ok=True)
    with open(hpl_dat_path, "w") as f:
        f.write(hpl_dat_content)

    print(f"[INFO] HPL.dat written to: {hpl_dat_path}")

    commands = f"""
export OMP_NUM_THREADS={threads}
cd {bin_dir}

echo "[RUN] HPL.dat:"
cat HPL.dat

mpirun -np {np} ./xhpl
"""

    generate_sbatch(
        "scripts/templates/sbatch_base.sh",
        run_sbatch,
        {
            "job_name":     f"hpl_run_{compiler}_np{np}_t{threads}",
            "log_file":     run_log,
            "module_loads": f"module purge\n{modules}",
            "commands":     commands
        }
    )

    # Patch --ntasks to match np so SLURM allocates correct MPI slots
    with open(run_sbatch) as f:
        content = f.read()
    content = content.replace("#SBATCH --ntasks=1", f"#SBATCH --ntasks={np}")
    with open(run_sbatch, "w") as f:
        f.write(content)

    return run_sbatch, run_log


# -----------------------------
# NEXT CASE NUMBER
# -----------------------------
def next_case_number():
    log_root = f"{BASE}/logs/hpl"
    os.makedirs(log_root, exist_ok=True)
    existing = [
        d for d in os.listdir(log_root)
        if d.startswith("case_") and os.path.isdir(f"{log_root}/{d}")
    ]
    if not existing:
        return 1
    numbers = []
    for d in existing:
        try:
            numbers.append(int(d.split("_")[-1]))
        except ValueError:
            pass
    return max(numbers) + 1 if numbers else 1


# -----------------------------
# SUBMIT
# -----------------------------
def submit_job(script, dependency=None):
    if dependency:
        out = subprocess.check_output(
            ["sbatch", f"--dependency=afterok:{dependency}", script]
        )
    else:
        out = subprocess.check_output(["sbatch", script])
    return out.decode().strip().split()[-1]


# -----------------------------
# WAIT
# -----------------------------
def wait_for_job(job_id):
    while True:
        result = subprocess.run(
            ["squeue", "-j", job_id], capture_output=True, text=True
        )
        if job_id not in result.stdout:
            break
        time.sleep(2)


# -----------------------------
# MAIN
# -----------------------------
def run(compiler=None, threads=None, np=None, N=None, NB=None, P=None, Q=None):

    config  = load_config()
    hpl_cfg = config["hpl"]

    compiler = compiler or "aocc"
    np      = int(np)      if np      else hpl_cfg["np"]
    N       = int(N)       if N       else hpl_cfg["N"]
    NB      = int(NB)      if NB      else hpl_cfg["NB"]
    P       = int(P)       if P       else hpl_cfg["P"]
    Q       = int(Q)       if Q       else hpl_cfg["Q"]
    threads = int(threads) if threads else hpl_cfg.get("threads", 1)

    if compiler not in config["compilers"]:
        raise ValueError(f"Unknown compiler: {compiler}")

    if P * Q != np:
        raise ValueError(f"P * Q ({P} * {Q} = {P*Q}) must equal np ({np})")

    arch      = config["compilers"][compiler]["arch"]
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    case_num  = next_case_number()
    case_name = f"case_hpl_{timestamp}_{case_num:03d}"
    final_dir = f"{BASE}/logs/hpl/{case_name}"
    os.makedirs(final_dir, exist_ok=True)

    print(f"[INFO] Compiler={compiler}  arch={arch}  np={np}  threads={threads}  N={N}  NB={NB}  P={P}  Q={Q}")
    print(f"[INFO] Case     : {case_name}")
    print(f"[INFO] Log dir  : {final_dir}")

    # ---------------------------
    # BUILD CHECK
    # ---------------------------
    if not is_built(arch):
        print("[INFO] Binary not found → submitting build job")

        build_sbatch = generate_build_sbatch(compiler, config, final_dir)
        build_id     = submit_job(build_sbatch)

        print(f"[INFO] Build Job ID: {build_id}")
        print("[INFO] Waiting for build job to finish before checking binary...")
        wait_for_job(build_id)

        if not is_built(arch):
            print(f"[ERROR] Build job finished but binary not found at: {binary_path(arch)}")
            print(f"[ERROR] Check build log in: {final_dir}/build.log")
            return

        # Generate run sbatch inside same directory after build succeeds
        run_sbatch, run_log = generate_run_sbatch(
            compiler, np, threads, N, NB, P, Q, config, final_dir
        )

        # ---------------------------
        # RUN (build path)
        # ---------------------------
        run_id = submit_job(run_sbatch)

    else:
        print("[INFO] Binary exists → skipping build, submitting run directly")

        run_sbatch, run_log = generate_run_sbatch(
            compiler, np, threads, N, NB, P, Q, config, final_dir
        )

        # ---------------------------
        # RUN (run-only path)
        # ---------------------------
        run_id = submit_job(run_sbatch)

    print(f"[INFO] Run Job ID : {run_id}")
    print(f"[INFO] Waiting for job {run_id} to finish...")

    wait_for_job(run_id)

    # ---------------------------
    # RESULTS
    # ---------------------------
    results = parse_results(run_log)

    if results:
        print_result_box(results, compiler, np)
    else:
        print(f"[WARNING] Could not parse results. Check log: {run_log}")
