import argparse
import subprocess

parser = argparse.ArgumentParser()

parser.add_argument("action", choices=["preprocess", "build", "cleanup"])
parser.add_argument("--component")
parser.add_argument("--version")

args = parser.parse_args()

if args.action == "preprocess":

    subprocess.run(["python3", "scripts/preprocess.py"])

elif args.action == "cleanup":

    cmd = ["python3", "scripts/cleanup.py"]

    if args.component:
        cmd += ["--component", args.component]

    if args.version:
        cmd += ["--version", args.version]

    subprocess.run(cmd)

elif args.action == "build":

    cmd = ["python3", "scripts/build.py"]

    if args.component:
        cmd += ["--component", args.component]

    if args.version:
        cmd += ["--version", args.version]

    subprocess.run(cmd)
