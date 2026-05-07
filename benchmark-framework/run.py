import argparse
import os
import sys
import subprocess

BASE = os.getcwd()


# -----------------------------
# CUSTOM HELP
# -----------------------------
HELP_TEXT = """
Benchmark Framework
===================

USAGE:
  python3 run.py build      --app <app> [options]
  python3 run.py cleanup    --app <app>
  python3 run.py preprocess --component <component> --version <version>
  python3 run.py -p <logdir>

─────────────────────────────────────────────────────

ACTIONS:
  build           Build and run a benchmark app or install a component
  cleanup         Clean up builds and logs for an app
  preprocess      Run preprocessing steps for an app

POSTPROCESS:
  -p <logdir>     Display results for a previous run (auto-detects app)
                  Example: python3 run.py -p 282_20260423_110415_aocc_t1

─────────────────────────────────────────────────────

BUILD OPTIONS:
  --app           App name          (stream, hpl)
  --compiler      Compiler to use   (gcc, aocc, intel)
  --threads       OpenMP threads    (STREAM and HPL)

  HPL only:
  --np            Number of MPI ranks         (must equal P * Q)
  --N             Problem size
  --NB            Block size
  --P             Process grid rows
  --Q             Process grid cols

─────────────────────────────────────────────────────

EXAMPLES:

  # STREAM
  python3 run.py build --app stream --compiler aocc --threads 4
  python3 run.py build --app stream --compiler intel --threads 1

  # HPL — defaults from configs/hpl.yaml
  python3 run.py build --app hpl --compiler aocc
  python3 run.py build --app hpl --compiler aocc --np 4 --N 20000 --NB 256 --P 2 --Q 2 --threads 2
  python3 run.py build --app hpl --compiler intel --np 1 --N 10000 --NB 256 --P 1 --Q 1

  # Postprocess — just give the log directory name
  python3 run.py -p 282_20260423_110415_aocc_t1
  python3 run.py -p 277_20260423_103434_aocc_np4_t1

─────────────────────────────────────────────────────
"""


# -----------------------------
# PARSER
# -----------------------------
parser = argparse.ArgumentParser(add_help=False)

parser.add_argument("action", nargs="?", choices=["build", "cleanup", "preprocess"])
parser.add_argument("-p", metavar="LOGDIR", help="Postprocess: display results for a log directory")
parser.add_argument("-h", "--help", action="store_true", help="Show this help message")
parser.add_argument("--logdir")
parser.add_argument("--component")
parser.add_argument("--app")
parser.add_argument("--version")
parser.add_argument("--compiler")
parser.add_argument("--threads", type=int)
parser.add_argument("--np",  type=int)
parser.add_argument("--N",   type=int)
parser.add_argument("--NB",  type=int)
parser.add_argument("--P",   type=int)
parser.add_argument("--Q",   type=int)

args = parser.parse_args()


# -----------------------------
# POSTPROCESS
# -----------------------------
def postprocess(logdir_name):

    # Auto-detect which app this log belongs to
    # by searching all subdirs under logs/
    found_app  = None
    found_path = None

    logs_root = f"{BASE}/logs"

    if os.path.exists(logs_root):
        for app in os.listdir(logs_root):
            candidate = f"{logs_root}/{app}/{logdir_name}"
            if os.path.isdir(candidate):
                found_app  = app
                found_path = candidate
                break

    if not found_app:
        print(f"[ERROR] Could not find '{logdir_name}' under logs/")
        print(f"[INFO]  Available apps in logs/: {', '.join(os.listdir(logs_root))}")
        sys.exit(1)

    run_log = f"{found_path}/run.log"

    if not os.path.exists(run_log):
        print(f"[ERROR] No run.log found in: {found_path}")
        sys.exit(1)

    print(f"[INFO] App     : {found_app}")
    print(f"[INFO] Log dir : {found_path}")
    print(f"[INFO] Log file: {run_log}")

    if found_app == "stream":
        parse_and_display_stream(run_log, logdir_name)
    elif found_app == "hpl":
        parse_and_display_hpl(run_log, logdir_name)
    else:
        print(f"[ERROR] No postprocess handler for app '{found_app}'")
        sys.exit(1)


def parse_and_display_stream(run_log, logdir_name):
    results = {}
    with open(run_log) as f:
        for line in f:
            if line.startswith("Copy:"):
                results["Copy"]  = float(line.split()[1])
            elif line.startswith("Scale:"):
                results["Scale"] = float(line.split()[1])
            elif line.startswith("Add:"):
                results["Add"]   = float(line.split()[1])
            elif line.startswith("Triad:"):
                results["Triad"] = float(line.split()[1])

    if not results:
        print("[WARNING] Could not parse STREAM results from log")
        return

    parts    = logdir_name.split("_")
    compiler = next((p for p in parts if p in ("aocc", "intel", "gcc")), "unknown")
    threads  = next((p[1:] for p in parts if p.startswith("t") and p[1:].isdigit()), "?")

    print("\n" + "=" * 50)
    print(f" STREAM RESULT | {compiler.upper()} | {threads} THREADS ")
    print("=" * 50)
    for k, v in results.items():
        print(f"{k:<10}: {v:>10.2f} MB/s")
    print("=" * 50 + "\n")


def parse_and_display_hpl(run_log, logdir_name):
    results = {}
    with open(run_log) as f:
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
                        pass
                break

    if not results:
        print("[WARNING] Could not parse HPL results from log")
        return

    parts    = logdir_name.split("_")
    compiler = next((p for p in parts if p in ("aocc", "intel", "gcc")), "unknown")
    np       = next((p[2:] for p in parts if p.startswith("np") and p[2:].isdigit()), "?")

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
# BUILD DISPATCH
# -----------------------------
def run_script(script):
    cmd = ["python3", script]
    if args.component:
        cmd += ["--component", args.component]
    if args.app:
        cmd += ["--app", args.app]
    if args.version:
        cmd += ["--version", args.version]
    if args.compiler:
        cmd += ["--compiler", args.compiler]
    if args.threads:
        cmd += ["--threads", str(args.threads)]
    if args.np:
        cmd += ["--np", str(args.np)]
    if args.N:
        cmd += ["--N", str(args.N)]
    if args.NB:
        cmd += ["--NB", str(args.NB)]
    if args.P:
        cmd += ["--P", str(args.P)]
    if args.Q:
        cmd += ["--Q", str(args.Q)]
    subprocess.run(cmd)


# -----------------------------
# MAIN DISPATCH
# -----------------------------
if args.help:
    print(HELP_TEXT)
elif args.p:
    postprocess(args.p)
elif args.action == "build":
    run_script("scripts/build.py")
elif args.action == "cleanup":
    run_script("scripts/cleanup.py")
elif args.action == "preprocess":
    run_script("scripts/preprocess.py")
else:
    print(HELP_TEXT)
