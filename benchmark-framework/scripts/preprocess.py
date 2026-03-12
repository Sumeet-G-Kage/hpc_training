import subprocess
import os

CONFIG = "config/components.conf"

# Read components list
with open(CONFIG) as f:
    components = [line.strip() for line in f if line.strip()]

for component in components:

    comp_dir = f"components/{component}"
    detect_script = f"{comp_dir}/detect.sh"
    install_script = f"{comp_dir}/install.sh"

    flag_file = f"state/{component}.flag"
    log_file = f"logs/{component}.log"

    print(f"\n[FRAMEWORK] Checking component: {component}")

    # Run detection script
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

            # Stream output live
            for line in process.stdout:
                print(line, end="")
                log.write(line)

            process.wait()

        # Verify installation
        verify = subprocess.run(["bash", detect_script])

        if verify.returncode == 0:

            print(f"[FRAMEWORK] {component} installation completed successfully")

            with open(flag_file, "w") as f:
                f.write("1")

        else:

            print(f"[FRAMEWORK] ERROR: {component} installation failed")
