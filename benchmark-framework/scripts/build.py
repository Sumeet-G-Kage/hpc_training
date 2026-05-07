import argparse
import importlib
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

parser = argparse.ArgumentParser()
parser.add_argument("--component")
parser.add_argument("--app")
parser.add_argument("--version")

# Shared
parser.add_argument("--compiler")

# STREAM
parser.add_argument("--threads", type=int)

# HPL
parser.add_argument("--np",  type=int)
parser.add_argument("--N",   type=int)
parser.add_argument("--NB",  type=int)
parser.add_argument("--P",   type=int)
parser.add_argument("--Q",   type=int)

args = parser.parse_args()


def handle_component(component, version):
    try:
        module = importlib.import_module(f"components.{component}.{component}")
        module.run(version=version)
    except ModuleNotFoundError:
        print(f"[ERROR] Component '{component}' not found")
        sys.exit(1)


def handle_app(app):
    try:
        module = importlib.import_module(f"apps.{app}.{app}")

        if app == "stream":
            module.run(
                compiler=args.compiler,
                threads=args.threads
            )
        elif app == "hpl":
            module.run(
                compiler=args.compiler,
                threads=args.threads,
                np=args.np,
                N=args.N,
                NB=args.NB,
                P=args.P,
                Q=args.Q
            )
        else:
            # Generic fallback — pass whatever is available
            module.run(
                compiler=args.compiler,
                threads=args.threads
            )

    except Exception as e:
        print(f"[ERROR] Failed to load or run app '{app}'")
        print("Actual error:", e)
        sys.exit(1)


if args.component:
    handle_component(args.component, args.version)
elif args.app:
    handle_app(args.app)
else:
    print("[ERROR] Provide --component or --app")
    sys.exit(1)
