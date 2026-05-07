import subprocess
import os
import argparse
import sys

BASE   = os.getcwd()
CONFIG = "configs/components.conf"

parser = argparse.ArgumentParser()
parser.add_argument("--component")
parser.add_argument("--version")
args = parser.parse_args()


# ------------------------------------------------
# BUILD-FROM-SOURCE COMPONENTS (openmpi, gcc)
# These have build.sh + versions.conf
# Command: python3 run.py preprocess --component openmpi --version 5.0.7
# ------------------------------------------------
def handle_build_component(component, version):
    comp_dir      = f"{BASE}/components/{component}"
    build_script  = f"{comp_dir}/build.sh"
    versions_conf = f"{comp_dir}/versions.conf"
    modulefile_dir = os.path.expanduser(f"~/modulefiles/{component}")
    builds_path   = f"{BASE}/builds/{component}/{version}"
    log_file      = f"{BASE}/logs/{component}_build_{version}.log"

    # Load supported versions
    with open(versions_conf) as f:
        supported = [line.strip() for line in f if line.strip()]

    if not version:
        print(f"[FRAMEWORK] Please provide --version. Supported versions:")
        for v in supported:
            print(f"             {v}")
        sys.exit(1)

    if version not in supported:
        print(f"[FRAMEWORK] Version '{version}' not in versions.conf")
        print(f"[FRAMEWORK] Supported: {', '.join(supported)}")
        sys.exit(1)

    # ---- BUILD ----
    binary = "mpicc" if component == "openmpi" else "gcc"
    if os.path.exists(f"{builds_path}/bin/{binary}"):
        print(f"[FRAMEWORK] {component} {version} already built — skipping build")
    else:
        print(f"[FRAMEWORK] Building {component} {version}...")
        os.makedirs(f"{BASE}/logs", exist_ok=True)

        with open(log_file, "w") as log:
            process = subprocess.Popen(
                ["bash", build_script, version],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            for line in process.stdout:
                print(line, end="")
                log.write(line)
            process.wait()

        if process.returncode != 0:
            print(f"\n[FRAMEWORK] ERROR: {component} {version} build failed")
            print(f"[FRAMEWORK] Check log: {log_file}")
            sys.exit(1)

        print(f"\n[FRAMEWORK] {component} {version} built successfully")
        print(f"[FRAMEWORK] Installed at : builds/{component}/{version}")
        print(f"[FRAMEWORK] Build log    : {log_file}")

    # ---- MODULEFILE ----
    modulefile_path = f"{modulefile_dir}/{version}"
    if os.path.exists(modulefile_path):
        print(f"[FRAMEWORK] Modulefile already exists for {component}/{version} — skipping")
    else:
        print(f"[FRAMEWORK] Creating modulefile for {component}/{version}...")
        create_modulefile(component, version, builds_path, modulefile_path)


def create_modulefile(component, version, prefix, modulefile_path):
    os.makedirs(os.path.dirname(modulefile_path), exist_ok=True)

    if component == "openmpi":
        content = (
            f"#%Module1.0\n"
            f"##\n"
            f"## OpenMPI {version} - built by benchmark-framework\n"
            f"##\n\n"
            f"module-whatis   {{OpenMPI {version} built from source}}\n\n"
            f"prepend-path    PATH            {prefix}/bin\n"
            f"prepend-path    LD_LIBRARY_PATH {prefix}/lib\n"
            f"prepend-path    MANPATH         {prefix}/share/man\n"
        )
    elif component == "gcc":
        content = (
            f"#%Module1.0\n"
            f"##\n"
            f"## GCC {version} - built by benchmark-framework\n"
            f"##\n\n"
            f"module-whatis   {{GCC {version} built from source}}\n\n"
            f"prepend-path    PATH            {prefix}/bin\n"
            f"prepend-path    LD_LIBRARY_PATH {prefix}/lib\n"
            f"prepend-path    LD_LIBRARY_PATH {prefix}/lib64\n"
            f"prepend-path    MANPATH         {prefix}/share/man\n"
        )

    with open(modulefile_path, "w") as f:
        f.write(content)

    print(f"[FRAMEWORK] Modulefile created : {modulefile_path}")
    print(f"[FRAMEWORK] Load with          : module load {component}/{version}")


# ------------------------------------------------
# SYSTEM COMPONENTS (slurm etc.)
# These have detect.sh + install.sh
# Command: python3 run.py preprocess
# ------------------------------------------------
def handle_system_components():
    if not os.path.exists(CONFIG):
        print(f"[FRAMEWORK] No components.conf found at {CONFIG}")
        sys.exit(1)

    with open(CONFIG) as f:
        components = [line.strip() for line in f if line.strip()]

    for component in components:
        if args.component and component != args.component:
            continue

        comp_dir        = f"components/{component}"
        detect_script   = f"{comp_dir}/detect.sh"
        install_script  = f"{comp_dir}/install.sh"
        flag_file       = f"state/{component}.flag"
        log_file        = f"logs/{component}.log"

        print(f"\n[FRAMEWORK] Checking component: {component}")

        result = subprocess.run(["bash", detect_script])
        if result.returncode == 0:
            print(f"[FRAMEWORK] {component} already installed")
            print("[FRAMEWORK] Skipping installation")
            with open(flag_file, "w") as f:
                f.write("0")
        else:
            print(f"[FRAMEWORK] {component} not found")
            print(f"[FRAMEWORK] Installing {component}...")
            with open(log_file, "a") as log:
                process = subprocess.Popen(
                    ["sudo", "bash", install_script],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )
                for line in process.stdout:
                    print(line, end="")
                    log.write(line)
                process.wait()

            verify = subprocess.run(["bash", detect_script])
            if verify.returncode == 0:
                print(f"[FRAMEWORK] {component} installation completed successfully")
                with open(flag_file, "w") as f:
                    f.write("1")
            else:
                print(f"[FRAMEWORK] ERROR: {component} installation failed")

    print("\n[FRAMEWORK] Preprocess stage completed")


# ------------------------------------------------
# MAIN DISPATCH
# ------------------------------------------------
if args.component:
    comp_dir = f"{BASE}/components/{args.component}"

    # If component has build.sh → build from source
    if os.path.exists(f"{comp_dir}/build.sh"):
        handle_build_component(args.component, args.version)

    # If component has detect.sh → system install
    elif os.path.exists(f"{comp_dir}/detect.sh"):
        handle_system_components()

    else:
        print(f"[FRAMEWORK] Unknown component '{args.component}'")
        sys.exit(1)

else:
    # No component specified → run all system components
    handle_system_components()
