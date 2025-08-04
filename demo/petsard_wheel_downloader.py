#!/usr/bin/env python3
"""
PETsARD Wheel Downloader

A simple module to download PETsARD and all its dependencies for specific platforms.
Supports cross-platform wheel downloading with detailed logging.

Usage:
    # Command line - basic usage
    python petsard_wheel_downloader.py --branch main --python-version 3.11 --os linux

    # Command line - with dependency groups
    python petsard_wheel_downloader.py --branch main --python-version 3.11 --os linux --groups pytorch jupyter

    # In Python/Jupyter - basic usage
    from petsard_wheel_downloader import download_petsard_wheels
    download_petsard_wheels(branch="main", python_version="3.11", os_type="linux")

    # In Python/Jupyter - with dependency groups
    download_petsard_wheels(branch="main", python_version="3.11", os_type="linux",
                           dependency_groups=["pytorch", "jupyter"])
"""

import argparse
import os
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path


def run_command(cmd, cwd=None):
    """Execute a system command and return the result."""
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd, capture_output=True, text=True, check=True
        )
        return result.stdout.strip(), result.stderr.strip(), 0
    except subprocess.CalledProcessError as e:
        return e.stdout, e.stderr, e.returncode


def get_platform_info(os_type):
    """Get pip platform parameters for the specified OS."""
    platform_map = {
        "linux": {
            "platform": "manylinux2014_x86_64",
            "abi": "cp{py_ver}",
            "implementation": "cp",
        },
        "windows": {
            "platform": "win_amd64",
            "abi": "cp{py_ver}",
            "implementation": "cp",
        },
        "macos": {
            "platform": "macosx_10_9_x86_64",
            "abi": "cp{py_ver}",
            "implementation": "cp",
        },
        "macos-arm": {
            "platform": "macosx_11_0_arm64",
            "abi": "cp{py_ver}",
            "implementation": "cp",
        },
    }
    return platform_map.get(os_type)


def get_git_info(branch):
    """Clone repository and get git information."""
    print(f"🔄 Cloning PETsARD repository (branch: {branch})...")

    with tempfile.TemporaryDirectory() as temp_dir:
        repo_dir = os.path.join(temp_dir, "petsard")

        # Clone repository
        clone_cmd = f"git clone --depth 1 --branch {branch} https://github.com/nics-tw/petsard.git {repo_dir}"
        stdout, stderr, code = run_command(clone_cmd)

        if code != 0:
            print(f"❌ Failed to clone repository: {stderr}")
            raise RuntimeError(f"Git clone failed: {stderr}")

        # Get commit hash
        hash_cmd = "git rev-parse HEAD"
        commit_hash, _, _ = run_command(hash_cmd, cwd=repo_dir)

        # Get commit date
        date_cmd = "git log -1 --format=%ci"
        commit_date, _, _ = run_command(date_cmd, cwd=repo_dir)

        # Get PETsARD version from pyproject.toml
        version_cmd = "grep '^version = ' pyproject.toml | cut -d'\"' -f2"
        version, _, _ = run_command(version_cmd, cwd=repo_dir)

        return {
            "commit_hash": commit_hash,
            "commit_date": commit_date,
            "version": version or "unknown",
        }


def check_output_directory(output_dir):
    """Check and prepare output directory."""
    output_path = Path(output_dir)

    if output_path.exists():
        if not output_path.is_dir():
            raise ValueError(
                f"Output path '{output_dir}' exists but is not a directory"
            )

        # Check if directory is not empty
        if any(output_path.iterdir()):
            raise ValueError(
                f"Output directory '{output_dir}' already exists and is not empty. "
                "Please use an empty directory or remove existing files."
            )
        print(f"📁 Using existing empty directory: {output_dir}")
    else:
        output_path.mkdir(parents=True, exist_ok=True)
        print(f"📁 Created new directory: {output_dir}")


def download_wheels(python_version, os_type, output_dir, dependency_groups=None):
    """Download PETsARD and all its dependencies."""
    groups_info = (
        f" with groups: {', '.join(dependency_groups)}" if dependency_groups else ""
    )
    print(
        f"📦 Downloading wheels for Python {python_version} on {os_type}{groups_info}..."
    )

    # Get platform info
    platform_info = get_platform_info(os_type)
    if not platform_info:
        raise ValueError(f"Unsupported OS: {os_type}")

    # Prepare Python version for ABI
    py_ver = python_version.replace(".", "")[:3]  # 3.11.5 -> 311
    abi = platform_info["abi"].format(py_ver=py_ver)

    # Check and prepare output directory
    check_output_directory(output_dir)

    # Build pip download command
    cmd = [
        "pip",
        "download",
        "petsard",
        "--platform",
        platform_info["platform"],
        "--python-version",
        python_version,
        "--abi",
        abi,
        "--implementation",
        platform_info["implementation"],
        "--only-binary=:all:",
        "--dest",
        output_dir,
    ]

    # Add dependency groups if specified
    if dependency_groups:
        for group in dependency_groups:
            cmd.extend(["--extra", group])

    print(f"🔄 Running: {' '.join(cmd)}")

    # Execute download
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Count downloaded files
    wheel_files = list(Path(output_dir).glob("*.whl"))

    if result.returncode != 0:
        print(f"❌ Download failed with return code: {result.returncode}")
        # Return both wheel files and error info for logging
        return wheel_files, {
            "success": False,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "command": " ".join(cmd),
        }

    print(f"✅ Successfully downloaded {len(wheel_files)} wheel files")

    # Return successful result
    return wheel_files, {
        "success": True,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "command": " ".join(cmd),
    }


def write_log(
    branch,
    python_version,
    os_type,
    output_dir,
    git_info,
    wheel_files,
    download_result,
    dependency_groups=None,
):
    """Write installation log."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"PETsARD_download_{timestamp}.log"

    with open(log_file, "w", encoding="utf-8") as f:
        f.write("=== PETsARD Wheel Download Log ===\n")
        f.write(f"Download Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %z')}\n")
        f.write(f"PETsARD Version: {git_info['version']}\n")
        f.write(f"Git Branch: {branch}\n")
        f.write(f"Git Commit Hash: {git_info['commit_hash']}\n")
        f.write(f"Git Commit Date: {git_info['commit_date']}\n")
        f.write(f"Python Version: {python_version}\n")
        f.write(f"Target OS: {os_type}\n")
        f.write(
            f"Dependency Groups: {', '.join(dependency_groups) if dependency_groups else 'None'}\n"
        )
        f.write(f"Downloaded Packages: {len(wheel_files)}\n")
        f.write(f"Output Directory: {os.path.abspath(output_dir)}\n")
        f.write(f"Status: {'SUCCESS' if download_result['success'] else 'FAILED'}\n")
        f.write(f"Return Code: {download_result['returncode']}\n\n")

        f.write("=== Parameters ===\n")
        f.write(f"Branch: {branch}\n")
        f.write(f"Python Version: {python_version}\n")
        f.write(f"OS Type: {os_type}\n")
        f.write(
            f"Dependency Groups: {', '.join(dependency_groups) if dependency_groups else 'None'}\n"
        )
        f.write(f"Output Directory: {output_dir}\n\n")

        f.write("=== Pip Command ===\n")
        f.write(f"{download_result['command']}\n\n")

        f.write("=== Pip Output ===\n")
        if download_result["stdout"]:
            f.write("STDOUT:\n")
            f.write(download_result["stdout"])
            f.write("\n\n")

        if download_result["stderr"]:
            f.write("STDERR:\n")
            f.write(download_result["stderr"])
            f.write("\n\n")

        f.write("=== Downloaded Packages ===\n")
        if wheel_files:
            for wheel_file in sorted(wheel_files):
                f.write(f"{wheel_file.name}\n")
        else:
            f.write("No packages were downloaded.\n")

        f.write("\n=== Git Information ===\n")
        f.write("Repository: https://github.com/nics-tw/petsard.git\n")
        f.write(f"Branch: {branch}\n")
        f.write(f"Latest Commit: {git_info['commit_hash']}\n")
        f.write(f"Commit Date: {git_info['commit_date']}\n")

    print(f"📝 Log written to: {log_file}")
    return log_file


def download_petsard_wheels(
    branch, python_version, os_type, output_dir="./wheels", dependency_groups=None
):
    """
    Main function to download PETsARD wheels.

    Args:
        branch (str): Git branch name (e.g., "main", "dev")
        python_version (str): Python version (e.g., "3.10", "3.11", "3.11.5")
        os_type (str): Target OS ("linux", "windows", "macos", "macos-arm")
        output_dir (str): Output directory for wheels (default: "./wheels")
        dependency_groups (list): Optional dependency groups to include (e.g., ["pytorch", "jupyter"])
                                Available groups: pytorch, jupyter, dev

    Returns:
        dict: Download results with paths and metadata

    Example:
        >>> result = download_petsard_wheels("main", "3.11", "linux")
        >>> print(f"Downloaded {result['wheel_count']} wheels to {result['output_dir']}")

        >>> # With dependency groups
        >>> result = download_petsard_wheels("main", "3.11", "linux", dependency_groups=["pytorch", "jupyter"])
        >>> print(f"Downloaded {result['wheel_count']} wheels with PyTorch and Jupyter support")
    """
    print("🚀 PETsARD Wheel Downloader")
    print("=" * 50)

    print("📋 Configuration:")
    print(f"   Branch: {branch}")
    print(f"   Python Version: {python_version}")
    print(f"   Target OS: {os_type}")
    print(f"   Output Directory: {output_dir}")
    if dependency_groups:
        print(f"   Dependency Groups: {', '.join(dependency_groups)}")
    print()

    try:
        # Validate OS type
        valid_os = ["linux", "windows", "macos", "macos-arm"]
        if os_type not in valid_os:
            raise ValueError(f"Invalid OS type '{os_type}'. Must be one of: {valid_os}")

        # Validate dependency groups
        if dependency_groups:
            valid_groups = ["pytorch", "jupyter", "dev"]
            invalid_groups = [g for g in dependency_groups if g not in valid_groups]
            if invalid_groups:
                raise ValueError(
                    f"Invalid dependency groups: {invalid_groups}. Must be one of: {valid_groups}"
                )

        # Get git information
        git_info = get_git_info(branch)
        print(
            f"✅ Repository info: PETsARD v{git_info['version']} ({git_info['commit_hash'][:8]})"
        )

        # Download wheels
        wheel_files, download_result = download_wheels(
            python_version, os_type, output_dir, dependency_groups
        )

        # Write log (always write log, even if download failed)
        log_file = write_log(
            branch,
            python_version,
            os_type,
            output_dir,
            git_info,
            wheel_files,
            download_result,
            dependency_groups,
        )

        if download_result["success"]:
            print()
            print("🎉 Download completed successfully!")
            print(f"📁 Wheels saved to: {os.path.abspath(output_dir)}")
            print(f"📝 Log file: {log_file}")

            return {
                "success": True,
                "wheel_count": len(wheel_files),
                "wheel_files": [str(f) for f in wheel_files],
                "output_dir": os.path.abspath(output_dir),
                "log_file": log_file,
                "git_info": git_info,
                "download_result": download_result,
            }
        else:
            print()
            print("❌ Download failed!")
            print(f"📝 Error details saved to log file: {log_file}")

            return {
                "success": False,
                "error": f"Download failed with return code {download_result['returncode']}",
                "wheel_count": len(wheel_files),
                "wheel_files": [str(f) for f in wheel_files],
                "output_dir": os.path.abspath(output_dir),
                "log_file": log_file,
                "git_info": git_info,
                "download_result": download_result,
            }

    except Exception as e:
        print(f"❌ Error: {e}")
        return {"success": False, "error": str(e)}


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Download PETsARD wheels for specific platforms"
    )
    parser.add_argument(
        "--branch", required=True, help="Git branch name (e.g., main, dev)"
    )
    parser.add_argument(
        "--python-version",
        required=True,
        help="Python version (e.g., 3.10, 3.11, 3.11.5)",
    )
    parser.add_argument(
        "--os",
        required=True,
        choices=["linux", "windows", "macos", "macos-arm"],
        help="Target operating system",
    )
    parser.add_argument(
        "--output-dir",
        default="./wheels",
        help="Output directory for downloaded wheels (default: ./wheels)",
    )
    parser.add_argument(
        "--groups",
        nargs="*",
        choices=["pytorch", "jupyter", "dev"],
        help="Optional dependency groups to include (e.g., --groups pytorch jupyter)",
    )

    return parser.parse_args()


def main():
    """Command line interface."""
    args = parse_arguments()
    result = download_petsard_wheels(
        branch=args.branch,
        python_version=args.python_version,
        os_type=args.os,
        output_dir=args.output_dir,
        dependency_groups=args.groups,
    )

    if not result["success"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
