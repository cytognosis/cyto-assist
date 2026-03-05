#!/usr/bin/env python3
"""
Setup Cytognosis Development Environment
Python wrapper for Cytoskeleton environment management.
"""

import argparse
import subprocess
import sys
from pathlib import Path
import shutil


def main():
    parser = argparse.ArgumentParser(description="Setup Cytognosis Development Environment")
    parser.add_argument(
        "--strategy",
        choices=["empty", "prelocked", "resolve"],
        help="Environment setup strategy",
    )
    parser.add_argument(
        "--env-name",
        type=str,
        help="Specific environment name (e.g., ml, cytognosis, default)",
    )
    parser.add_argument(
        "--compute-backend",
        choices=["rocm", "cuda", "cpu"],
        default="rocm",
        help="Target hardware backend compute logic (e.g., rocm, cuda, cpu)",
    )

    args = parser.parse_args()

    # Colors
    GREEN = "\033[0;32m"
    BLUE = "\033[0;34m"
    NC = "\033[0m"

    print(f"{BLUE}═══════════════════════════════════════════════════════════{NC}")
    print(f"{BLUE}  Cytognosis Environment Setup                           {NC}")
    print(f"{BLUE}═══════════════════════════════════════════════════════════{NC}")

    project_root = Path(__file__).parent.parent
    cyto_module = project_root / "modules" / "cytoskeleton"

    env_name = args.env_name
    compute_backend = args.compute_backend

    if not cyto_module.is_dir() and args.strategy in ["prelocked", "resolve"]:
        print(f"Warning: Cytoskeleton submodule not found at {cyto_module}")
        print("Falling back to 'empty' strategy (standard uv environments).")
        strategy = "empty"
    elif args.strategy:
        strategy = args.strategy
    else:
        print("Available strategies:")
        print(f"  1) {GREEN}prelocked{NC} (Fastest, deterministic lockfiles from Cytoskeleton)")
        print(f"  2) {GREEN}resolve{NC}   (Resolve components on the fly)")
        print(f"  3) {GREEN}empty{NC}     (Standard virtual environment)")

        choice = input("Select strategy [1]: ").strip() or "1"
        strategy_map = {"1": "prelocked", "2": "resolve", "3": "empty"}
        strategy = strategy_map.get(choice, "prelocked")

        if strategy != "empty" and not cyto_module.is_dir():
             print(f"Warning: Cytoskeleton submodule not found at {cyto_module}")
             print("Falling back to 'empty' strategy.")
             strategy = "empty"

    if strategy in ["prelocked", "resolve"] and not env_name:
        print("\nAvailable environments:")
        print(f"  1) {GREEN}ml{NC} (Default): Core machine learning frameworks including PyTorch")
        print(f"  2) {GREEN}cytognosis{NC}: Full stack with all standard tools")
        print(f"  3) {GREEN}basic{NC}: Data engineering and exploration (no ML)")
        print(f"  4) {GREEN}custom{NC}: Provide your own environment name")

        env_choice = input("Select environment [1]: ").strip() or "1"
        env_map = {"1": "ml", "2": "cytognosis", "3": "basic"}
        if env_choice == "4":
            env_name = input("Enter custom environment name: ").strip()
        else:
            env_name = env_map.get(env_choice, "ml")

    print(f"\nInitializing environment using strategy: {GREEN}{strategy}{NC}...")

    try:
        # Create .venv if it doesn't exist, allow existing
        subprocess.run(["uv", "venv", "--allow-existing"], check=True, cwd=project_root)

        if strategy == "empty":
            print("Running uv sync...")
            subprocess.run(["uv", "sync"], check=True, cwd=project_root)

        elif strategy == "prelocked":
            print(f"Initializing prelocked environment '{env_name}' from Cytoskeleton...")

            os_target = "mac" if sys.platform == "darwin" else "linux"
            lock_dir = cyto_module / "locked" / "environments"
            # Format: {env}-{os}-{backend}.uv.lock
            lock_name = f"{env_name}-{os_target}-{compute_backend}.uv.lock"
            lock_file = lock_dir / lock_name

            if not lock_file.exists() and os_target == "mac" and compute_backend != "cpu":
                # Fallback to mac-cpu if cuda/rocm requested on mac
                print(f"Warning: {compute_backend} unsupported on Mac. Falling back to CPU.")
                compute_backend = "cpu"
                lock_name = f"{env_name}-{os_target}-cpu.uv.lock"
                lock_file = lock_dir / lock_name

            if not lock_file.exists():
                print(f"Warning: Specific lock file {lock_file} not found.")
                lock_file = lock_dir / f"{env_name}.uv.lock"

            if lock_file.exists():
                print(f"Using lockfile: {lock_file.name}")

                cmd = [
                    "uv",
                    "pip",
                    "sync",
                    str(lock_file),
                    "--index-strategy",
                    "unsafe-best-match",
                    "--python",
                    ".venv",
                ]

                if compute_backend == "cpu":
                    cmd.extend(["--extra-index-url", "https://download.pytorch.org/whl/cpu"])
                elif compute_backend == "cuda":
                    cmd.extend(["--extra-index-url", "https://download.pytorch.org/whl/cu128"])
                elif compute_backend == "rocm":
                    cmd.extend(
                        [
                            "--extra-index-url",
                            "https://download.pytorch.org/whl/rocm6.1",
                        ]
                    )

                subprocess.run(cmd, check=True, cwd=project_root)
            else:
                print(f"Warning: Lock file {lock_file} not found locally.")
                print("Falling back to standard uv sync.")
                subprocess.run(["uv", "sync"], check=True, cwd=project_root)

        elif strategy == "resolve":
            print(f"Resolving environment '{env_name}' for compute hardware: {compute_backend}...")
            cli_path = cyto_module / "scripts" / "env_manager.py"
            env_config = cyto_module / "configs" / "environments" / f"{env_name}-{compute_backend}.yaml"
            if not env_config.exists():
                env_config = cyto_module / "configs" / "environments" / f"{env_name}.yaml"
            cmd = [
                "uv",
                "run",
                "--python",
                "3.12",
                "python",
                str(cli_path),
                "--env-config",
                str(env_config),
                "--components-dir",
                str(cyto_module / "configs" / "components"),
                "--backend",
                "uv",
                "--env-name",
                ".venv",
            ]
            subprocess.run(cmd, check=True, cwd=project_root)

        print(f"\n{GREEN}Setup Complete!{NC}")
        print("Environment is active via uv.")
        print("To run commands in environment:")
        print("  uv run <command>")
        print("  nox -s <session>")

    except subprocess.CalledProcessError as e:
        print(f"Error during environment setup: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
