import argparse
import subprocess
import os

parser = argparse.ArgumentParser()

parser.add_argument("--component")
parser.add_argument("--version")

args = parser.parse_args()

BUILD_DIR = "build"

# ------------------------------------------------
# Build a specific component/version
# ------------------------------------------------

if args.component and args.version:

    comp_dir = f"{BUILD_DIR}/{args.component}"

    if not os.path.exists(comp_dir):
        print(f"[FRAMEWORK] Unknown component: {args.component}")
        exit(1)

    print(f"[FRAMEWORK] Building {args.component} {args.version}")

    subprocess.run(
        ["bash", f"{comp_dir}/build.sh", args.version],
        check=True
    )

    exit()


# ------------------------------------------------
# Build all versions of one component
# ------------------------------------------------

if args.component:

    comp_dir = f"{BUILD_DIR}/{args.component}"
    versions_file = f"{comp_dir}/versions.conf"

    if not os.path.exists(versions_file):
        print(f"[FRAMEWORK] No versions.conf for {args.component}")
        exit(1)

    with open(versions_file) as f:
        versions = [v.strip() for v in f if v.strip()]

    for version in versions:

        print(f"[FRAMEWORK] Building {args.component} {version}")

        subprocess.run(
            ["bash", f"{comp_dir}/build.sh", version],
            check=True
        )

    print("[FRAMEWORK] Build stage completed")
    exit()


# ------------------------------------------------
# Build all components
# ------------------------------------------------

components = os.listdir(BUILD_DIR)

for component in components:

    comp_dir = f"{BUILD_DIR}/{component}"
    versions_file = f"{comp_dir}/versions.conf"

    if not os.path.exists(versions_file):
        continue

    with open(versions_file) as f:
        versions = [v.strip() for v in f if v.strip()]

    for version in versions:

        print(f"[FRAMEWORK] Building {component} {version}")

        subprocess.run(
            ["bash", f"{comp_dir}/build.sh", version],
            check=True
        )

print("[FRAMEWORK] Build stage completed")
