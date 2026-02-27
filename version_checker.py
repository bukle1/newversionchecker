#!/usr/bin/env python3
"""
version_checker.py - Checks for new versions of packages and optionally updates them.

Usage:
    python version_checker.py --package <package_name> [--update]
    python version_checker.py --requirements requirements.txt [--update]
"""

import argparse
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from typing import Optional

from packaging.version import Version


_VALID_PACKAGE_NAME = re.compile(r"^[A-Za-z0-9]([A-Za-z0-9._-]*[A-Za-z0-9])?$")
_REQUIREMENT_LINE = re.compile(r"^([A-Za-z0-9]([A-Za-z0-9._-]*[A-Za-z0-9])?)(\[.*?\])?[^;]*")


def get_installed_version(package: str) -> Optional[str]:
    """Get the currently installed version of a package."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", package],
            capture_output=True,
            text=True,
            check=True,
        )
        for line in result.stdout.splitlines():
            if line.startswith("Version:"):
                return line.split(":", 1)[1].strip()
    except subprocess.CalledProcessError:
        pass
    return None


def get_latest_version(package: str) -> Optional[str]:
    """Fetch the latest available version of a package from PyPI."""
    if not _VALID_PACKAGE_NAME.match(package):
        return None
    url = f"https://pypi.org/pypi/{package}/json"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:  # noqa: S310
            data = json.loads(response.read().decode())
            return data["info"]["version"]
    except (urllib.error.URLError, json.JSONDecodeError, KeyError):
        return None


def update_package(package: str) -> bool:
    """Update a package to its latest version using pip."""
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", package],
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def check_package(package: str, do_update: bool = False) -> dict:
    """Check a single package for updates and optionally update it."""
    result = {
        "package": package,
        "installed": None,
        "latest": None,
        "update_available": False,
        "updated": False,
    }

    installed = get_installed_version(package)
    result["installed"] = installed

    if installed is None:
        print(f"  {package}: not installed")
        return result

    latest = get_latest_version(package)
    result["latest"] = latest

    if latest is None:
        print(f"  {package}: could not fetch latest version")
        return result

    if Version(installed) < Version(latest):
        result["update_available"] = True
        print(f"  {package}: {installed} -> {latest} (update available)")
        if do_update:
            success = update_package(package)
            result["updated"] = success
            if success:
                print(f"  {package}: updated successfully to {latest}")
            else:
                print(f"  {package}: update failed")
    else:
        print(f"  {package}: {installed} (up to date)")

    return result


def check_requirements_file(filepath: str, do_update: bool = False) -> list:
    """Check all packages listed in a requirements file."""
    results = []
    try:
        with open(filepath) as f:
            packages = []
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                match = _REQUIREMENT_LINE.match(line)
                if match:
                    packages.append(match.group(1))
    except FileNotFoundError:
        print(f"Error: requirements file '{filepath}' not found.")
        return results

    for package in packages:
        if package:
            results.append(check_package(package, do_update))
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Check for new versions of Python packages and optionally update them."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--package", help="Name of the package to check")
    group.add_argument(
        "--requirements",
        metavar="FILE",
        help="Path to a requirements.txt file",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Automatically update packages with available updates",
    )
    args = parser.parse_args()

    print("Checking for updates...")
    if args.package:
        results = [check_package(args.package, args.update)]
    else:
        results = check_requirements_file(args.requirements, args.update)

    updates_available = sum(1 for r in results if r["update_available"])
    if updates_available:
        print(f"\n{updates_available} update(s) available.")
        if not args.update:
            print("Run with --update to apply updates.")
    else:
        print("\nAll packages are up to date.")


if __name__ == "__main__":
    main()
