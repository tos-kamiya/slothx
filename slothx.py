#!/usr/bin/env python3

import ast
import os.path as op
import sys
import subprocess
import shutil
import tempfile
import argparse
import venv
from typing import Set, Tuple, List


def find_third_party_packages(imports: Set[str]) -> List[str]:
    """
    Create a virtual environment, detect third-party packages, and then remove the virtual environment.

    Args:
        imports (Set[str]): A set of imported module names from the target script.

    Returns:
        List[str]: A list of third-party packages that are not part of the standard library.
    """
    third_party_packages = []

    # Create a temporary directory and set up a virtual environment
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create the virtual environment
        venv_dir = op.join(temp_dir, "venv")
        venv.create(venv_dir, with_pip=False)  # Create virtual environment without pip
        venv_python = op.join(venv_dir, "bin", "python")

        # Add to the list if the package cannot be imported in the virtual environment (i.e., third-party package)
        for package in imports:
            if not is_package_in_venv(package, venv_python):
                third_party_packages.append(package)

    # The virtual environment is automatically deleted when the with block exits
    return third_party_packages


def is_package_in_venv(package_name: str, venv_python: str) -> bool:
    """
    Check if a package is part of the standard library by attempting to import it in a clean virtual environment.

    Args:
        package_name (str): The name of the package to check.
        venv_python (str): The path to the Python interpreter in the virtual environment.

    Returns:
        bool: True if the package is part of the standard library, False if it's a third-party package.
    """
    try:
        subprocess.run(
            [venv_python, "-c", f"import {package_name}"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True  # If import succeeds, it's part of the standard library
    except subprocess.CalledProcessError:
        return False  # If import fails, it's a third-party package


def analyze_script(filepath: str) -> Tuple[Set[str], bool]:
    """
    Parse the script to find all import statements and check for the presence of a 'main' function.

    Args:
        filepath (str): The path to the Python script to analyze.

    Returns:
        Tuple[Set[str], bool]: A tuple containing a set of imported modules and a boolean indicating whether a 'main' function exists.
    """
    with open(filepath, "r", encoding="utf-8") as file:
        tree = ast.parse(file.read(), filename=filepath)

    # Collect imported modules
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)

    # Check if a 'main' function is defined
    has_main = any(
        isinstance(node, ast.FunctionDef) and node.name == "main"
        for node in ast.walk(tree)
    )

    return imports, has_main


def generate_pyproject_toml(script_name: str, dependencies: List[str]) -> str:
    """
    Generate the content for a pyproject.toml file.

    Args:
        script_name (str): The name of the Python script.
        dependencies (List[str]): A list of third-party dependencies.

    Returns:
        str: The generated content of the pyproject.toml file.
    """
    # Replace underscores with hyphens for the tool/package name
    tool_name = op.splitext(op.basename(script_name))[0].replace("_", "-")
    # Replace hyphens with underscores for the module name
    module_name = tool_name.replace("-", "_")

    pyproject_content = f"""
[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{tool_name}"
version = "0.1.0"
description = "Auto-generated project for {tool_name}"
dependencies = {dependencies}

[project.scripts]
{tool_name} = "{module_name}:main"
"""
    return pyproject_content


def create_pyproject_toml_file(
    script_name: str, dependencies: List[str], output_dir: str
) -> str:
    """
    Create a pyproject.toml file in the given output directory.

    Args:
        script_name (str): The name of the Python script.
        dependencies (List[str]): A list of third-party dependencies.
        output_dir (str): The directory in which to create the pyproject.toml file.

    Returns:
        str: The path to the generated pyproject.toml file.
    """
    pyproject_content = generate_pyproject_toml(script_name, dependencies)
    pyproject_path = op.join(output_dir, "pyproject.toml")
    with open(pyproject_path, "w", encoding="utf-8") as f:
        f.write(pyproject_content)
    return pyproject_path


def install_with_pipx(temp_dir: str, force: bool = False) -> None:
    """
    Use pipx to install the package from the temporary directory.

    Args:
        temp_dir (str): The path to the temporary directory containing the script and pyproject.toml file.
        force (bool): Whether to force installation using pipx.
    """
    cmd = [
        sys.executable,
        "-m",
        "pipx",
        "install",
    ]  # Use the current Python interpreter to invoke pipx
    if force:
        cmd.append("--force")
    cmd.append(temp_dir)

    # Run pipx, but do not print "installation complete" automatically
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"Error: pipx installation failed with exit code {result.returncode}")
        sys.exit(result.returncode)


def run_script(
    script_path: str, script_args: List[str], dependencies: List[str]
) -> None:
    """
    Run the specified script with the provided arguments.

    Args:
        script_path (str): The path to the Python script to run.
        script_args (List[str]): A list of arguments to pass to the script.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        venv_dir = op.join(temp_dir, "venv")
        venv.create(venv_dir, with_pip=True)
        venv_python = op.join(venv_dir, "bin", "python")

        cmd = [venv_python, "-m", "pip", "install", "wheel"]
        subprocess.run(cmd)

        for package in dependencies:
            cmd = [venv_python, "-m", "pip", "install", package]
            subprocess.run(cmd)
        print("---", file=sys.stderr, flush=True)

        # Use the current Python interpreter to run the script with the provided arguments
        cmd = [venv_python, script_path] + script_args
        result = subprocess.run(cmd)
        return result.returncode


def main() -> None:
    """
    Main function to handle 'install' and 'run' subcommands.
    """
    # Command-line argument parsing
    parser = argparse.ArgumentParser(
        description="Install and run standalone Python scripts with pipx."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Install subcommand
    install_parser = subparsers.add_parser(
        "install", help="Install the script using pipx."
    )
    install_parser.add_argument(
        "script", help="Python script file to analyze and install."
    )
    install_parser.add_argument(
        "--pyproject-toml",
        action="store_true",
        help="Output pyproject.toml content to stdout instead of installing.",
    )
    install_parser.add_argument(
        "--force",
        action="store_true",
        help="Pass the --force option to pipx command to force installation.",
    )

    # Run subcommand
    run_parser = subparsers.add_parser("run", help="Run the script with arguments.")
    run_parser.add_argument("script", help="Python script file to run.")
    run_parser.add_argument(
        "script_args", nargs=argparse.REMAINDER, help="Arguments to pass to the script."
    )

    args = parser.parse_args()

    script_file = args.script

    # Check if the script file exists
    if not op.isfile(script_file):
        print(f"Error: {script_file} not found.")
        sys.exit(1)

    # Analyze the script for imports and the existence of a main function
    imports, has_main = analyze_script(script_file)

    # Check for the presence of a 'main' function
    if not has_main:
        print(f"Error: 'main' function not found in {script_file}.")
        sys.exit(1)

    # Detect third-party packages
    third_party_packages = find_third_party_packages(imports)

    if args.command == "install":
        if args.pyproject_toml:
            # Output the pyproject.toml content to stdout or install with pipx
            pyproject_content = generate_pyproject_toml(script_file, third_party_packages)
            print(pyproject_content)

        # Use the absolute path of the script to avoid issues with relative paths
        abs_script_path = op.abspath(script_file)

        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Copy the script to the temporary directory, replacing '-' with '_' in the filename
            filename_for_module = op.basename(abs_script_path).replace("-", "_")
            shutil.copy(abs_script_path, op.join(temp_dir, filename_for_module))

            # Generate pyproject.toml in the temporary directory
            create_pyproject_toml_file(abs_script_path, third_party_packages, temp_dir)

            # Install with pipx
            print("Installing with pipx...")
            install_with_pipx(temp_dir, args.force)
    elif args.command == "run":
        # Run the script with the provided arguments
        exit_code = run_script(script_file, args.script_args, third_party_packages)
        sys.exit(exit_code)
    else:
        print("Error: Unknown command.")
        sys.exit(1)


if __name__ == "__main__":
    main()
