# Slothx, quick and lazy installer for standalone scripts

![](slothx-mascot-hf.png)

**Slothx** is a Python script that helps you easily generate a `pyproject.toml` file for your Python script, detect third-party dependencies, and install the script using `pipx`.
This tool simplifies the process of packaging and **installing standalone Python scripts**, especially for lazy developers who want a quick way to package and deploy their scripts.

## Features

- Installs your script using `pipx` with automatic detection of third-party dependencies.
- Runs your script with its dependencies.
- Allows viewing the generated `pyproject.toml` without installing, using the `--pyproject-toml` option.

## Requirements

- Python 3.10 or later
- `pipx` (version 1.6 or later if you prefer pinning the installed script)

## Installation

Since **Slothx** is just a Python script, you can download the script and use it directly.

If you want to run it as a command, put the script in any directory of your choice (e.g., `~/bin`) and make sure that the file has execute permissions (`chmod +x slothx.py`).

## Usage

### 1. Install your Python script with `pipx`

To install a Python script using **Slothx**, you now need to use the `install` subcommand. **Slothx** will analyze the script for third-party dependencies, generate a `pyproject.toml` file, and install the script using `pipx`:

```bash
python3 slothx.py install your_script.py
```
By default, **Slothx** will attempt to **pin** the installed package version. See [Pinning support](#pinning-support) for more information on pinning.

### 2. Run your Python script with dependencies

You can run a Python script directly with the `run` subcommand. **Slothx** will create a temporary virtual environment, install the script's third-party dependencies, and execute the script with any provided arguments:

```bash
python3 slothx.py run your_script.py [script_options]
```

For example, if your script accepts options or arguments:

```bash
python3 slothx.py run your_script.py --option value
```

### 3. View the generated `pyproject.toml` without installing

If you want to see what `pyproject.toml` would be generated without actually installing the script, use the `--pyproject-toml` option with the `install` subcommand:

```bash
python3 slothx.py install your_script.py --pyproject-toml
```

This will output the contents of `pyproject.toml` to the standard output.

## Command-Line Options

### Subcommands

- `install`: Install the Python script using `pipx`.
- `run`: Run the Python script in a temporary virtual environment with its dependencies.

### Options for `install` subcommand

- `script`: The Python script you want to analyze and install.
- `--pyproject-toml`: Outputs the generated `pyproject.toml` file to the standard output without installing the script.
- `--force`: Forces the installation using `pipx`, even if the script is already installed.
- `--no-pinning`: Skips pinning the installed package.

### Options for `run` subcommand

- `script`: The Python script you want to run.
- `[script_options]`: Any arguments or options to pass to the script during execution.

## Example

### Installing a Script

Let's say you have a script called `to_moodle_html.py` that imports the `requests` library. You can install it using **Slothx** as follows:

```bash
python3 slothx.py install to_moodle_html.py
```

**Slothx** will:

1. Analyze the script for imports.
2. Identify each dependency as a third-party package or part of the standard library.
3. Generate a `pyproject.toml` file, including the `dependencies` section.
4. Install the script using `pipx`.

### Running a Script with Dependencies

You can run the script directly in a temporary virtual environment, with all necessary dependencies installed:

```bash
python3 slothx.py run to_moodle_html.py section-1.md
```

This will automatically create a virtual environment, install the `requests` library (and any other dependencies), and execute the script.

### Viewing the `pyproject.toml` Without Installing

You can view the generated `pyproject.toml` without installing:

```bash
python3 slothx.py install to_moodle_html.py --pyproject-toml
```

This will output something like:

```toml
[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "to-moodle-html"
version = "0.1.0"
description = "Auto-generated project for to-moodle-html"
dependencies = ["requests"]

[project.scripts]
to-moodle-html = "to_moodle_html:main"
```

## How It Works

The installation process with **Slothx** goes through the following steps:

1. **Script Analysis**: **Slothx** uses Python's `ast` module to parse the script and extract all `import` statements. It checks for the existence of a `main` function in the script.
2. **Dependency Detection**: It creates a temporary virtual environment to differentiate between standard library modules and third-party packages. Third-party packages are identified as those that cannot be imported in a clean virtual environment.
3. **Pyproject Generation**: It generates a `pyproject.toml` file with the script's name and its detected third-party dependencies.
4. **Installation with Pipx**: It uses `pipx` to install the script as a globally accessible command.

## Notes

- Ensure that `pipx` is properly installed and available in your `PATH` before using Slothx. 
- The tool assumes that your Python **script has a `main` function** as the entry point.
- Some Python packages have **different names for the import statement and the pip package**. For example, the `opencv-python` package is installed via `pip`, but imported as `cv2` in your script. Slothx may fail to detect third-party dependencies correctly in such cases.

## Pinning Support<a id="pinning-support"></a>

Pinning requires `pipx` version 1.6 or later. If you are using an older version (e.g., `pipx` 1.4 on Ubuntu 24.04 via `apt`), the pinning feature will not be available.

Pinning prevents `pipx upgrade-all` from attempting to upgrade the installed package. Since `Slothx` installs scripts from a temporary directory, there will be no updates available for these packages, and attempting to upgrade them will result in warnings like the following:

```bash
$ pipx upgrade-all
Warning: Error encountered when upgrading to-moodle-html:
Unable to parse package spec: /tmp/tmpdlhciagh

...

Some packages encountered issues during upgrade.
    See specific warning messages above.
```

This warning occurs because the package was installed from a temporary directory that no longer exists. By pinning the package, you can avoid these warnings.

## License

This project is licensed under the MIT License.
