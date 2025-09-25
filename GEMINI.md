# Gemini Code Assistant Context

## Project Overview

This is a Python project for **Network Optimization**. It uses `networkx` for graph-related operations. The project is set up using `PyScaffold`, and the packaging is configured in `setup.cfg`.

The project's source code is located in the `src` directory, and the tests are in the `tests` directory.

## Building and Running

### Dependencies

The main dependencies are:
- `networkx`
- `ellalgo`
- `mywheel`
- `digraphx`
- `numpy`

To install all the necessary dependencies, you can use the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### Running Tests

The project uses `pytest` for testing. To run the tests, use the following command:

```bash
pytest
```

You can also use `tox` to run the tests in an isolated environment:

```bash
tox
```

### Building the Project

To build the project, you can use the `build` environment in `tox`:

```bash
tox -e build
```

This will create a `dist` directory with the built package.

## Development Conventions

### Code Style

The project uses the following tools to maintain code quality:

- **Formatting:** `black` is used for code formatting.
- **Import Sorting:** `isort` is used to sort imports automatically.
- **Linting:** `flake8` is used for linting the code.

These tools are configured in the `.pre-commit-config.yaml` file and are run automatically before each commit.

### Contribution Guidelines

The `CONTRIBUTING.md` file provides guidelines for contributing to the project. It is recommended to read this file before making any contributions.
