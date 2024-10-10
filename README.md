# Slothx, quick and lazy installer for standalone scripts

**Slothx** is a Python script that helps you easily generate a `pyproject.toml` file for your Python script, detect third-party dependencies, and install the script using `pipx`.
This tool simplifies the process of packaging and **installing standalone Python scripts**, especially for lazy developers who want a quick way to package and deploy their scripts.

## Features

- Automatically detects third-party dependencies in your script.
- Generates a `pyproject.toml` file with the correct dependencies.
- Installs your script using `pipx`.
- Supports force installation with the `--force` option.
- Allows viewing the generated `pyproject.toml` without installing using `--pyproject-toml`.

## Requirements

- Python 3.6 or later
- `pipx` installed (You can install it via `pip install pipx`)

## Installation

Since **Slothx** is just a Python script, you can download the script and use it directly:

## Usage

### 1. Install your Python script with `pipx`

To install a Python script using **Slothx**, provide the script file as a parameter. **Slothx** will analyze the script for third-party dependencies, generate a `pyproject.toml` file, and install the script using `pipx`:

```bash
python3 slothx.py your_script.py
```

### 2. View the generated `pyproject.toml` without installing

If you want to see what `pyproject.toml` would be generated without actually installing the script, use the `--pyproject-toml` option:

```bash
python3 slothx.py your_script.py --pyproject-toml
```

This will output the contents of `pyproject.toml` to the standard output.

If you want to force the installation (e.g., overwrite an existing installation), use the `--force` option:
```bash
python3 slothx.py your_script.py --force
```

This will pass the `--force` flag to the `pipx install` command.

## Command-Line Options

- `script`: The Python script you want to analyze and install.
- `--pyproject-toml`: Outputs the generated `pyproject.toml` file to the standard output without installing the script.
- `--force`: Forces the installation using `pipx`, even if the script is already installed.

## Example

### Installing a Script

Let's say you have a script called `to_moodle_html.py` that imports the `requests` library. You can install it using **Slothx** as follows:

```bash
python3 slothx.py to_moodle_html.py
```

**Slothx** will:

1. Analyze the script for imports.
2. Identify for each of the dependencies is a third-party dependency.
3. Generate a `pyproject.toml` file, including `dependences` section.
4. Install the script using `pipx`.

### Viewing the `pyproject.toml` Without Installing

You can view the generated `pyproject.toml` without installing:

```bash
python3 slothx.py to_moodle_html.py --pyproject-toml
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

1. **Script Analysis**: **Slothx** uses Python's `ast` module to parse the script and extract all `import` statements. It checks for the existence of a `main` function in the script.
2. **Dependency Detection**: It creates a temporary virtual environment to differentiate between standard library modules and third-party packages. Third-party packages are identified as those that cannot be imported in a clean virtual environment.
3. **Pyproject Generation**: It generates a `pyproject.toml` file with the script's name and its detected third-party dependencies.
4. **Installation with Pipx**: It uses `pipx` to install the script as a globally accessible command.

### Notes

- Ensure that `pipx` is properly installed and available in your `PATH` before using **Slothx**.
- The tool assumes that your Python script has a `main` function as the entry point.

## License

This project is licensed under the MIT License.
