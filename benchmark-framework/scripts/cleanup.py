import subprocess
import os
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("--component")
parser.add_argument("--version")

args = parser.parse_args()

CONFIG = "config/components.conf"
builds_dir = "builds"

# ------------------------------------------------
# BUILD CLEANUP (openmpi, gcc, etc.)
# ------------------------------------------------

if args.component and os.path.exists(f"{builds_dir}/{args.component}"):

    if args.version:

        target = f"{builds_dir}/{args.component}/{args.version}"

        if os.path.exists(target):

            print(f"[FRAMEWORK] Removing {args.component} version {args.version}")
            subprocess.run(["rm", "-rf", target])
            print("[FRAMEWORK] Removal completed")

        else:

            print(f"[FRAMEWORK] Version {args.version} not found")

    else:

        print(f"[FRAMEWORK] Removing all builds for {args.component}")
        subprocess.run(["rm", "-rf", f"{builds_dir}/{args.component}"])
        print("[FRAMEWORK] All builds removed")

    exit()


# ------------------------------------------------
# COMPONENT CLEANUP (slurm etc.)
# ------------------------------------------------

if os.path.exists(CONFIG):

    with open(CONFIG) as f:
        components = [line.strip() for line in f if line.strip()]

    for component in components:

        if args.component and component != args.component:
            continue

        print(f"\n[FRAMEWORK] Processing cleanup for component: {component}")

        flag_file = f"state/{component}.flag"
        comp_dir = f"components/{component}"
        log_file = f"logs/{component}.log"
        uninstall_script = f"{comp_dir}/uninstall.sh"

        if os.path.exists(flag_file):

            with open(flag_file) as f:
                value = f.read().strip()

            if value == "1":

                print(f"[FRAMEWORK] {component} was installed by the framework")
                print("[FRAMEWORK] Starting removal...")

                with open(log_file, "a") as log:
                    subprocess.run(
                        ["sudo", "bash", uninstall_script],
                        stdout=log,
                        stderr=log
                    )

                print(f"[FRAMEWORK] {component} removed successfully")

            else:

                print(f"[FRAMEWORK] {component} not installed by framework")
                print("[FRAMEWORK] Skipping for safety")

        else:

            print(f"[FRAMEWORK] No state record for {component}. Skipping")

print("\n[FRAMEWORK] Cleanup stage completed")
