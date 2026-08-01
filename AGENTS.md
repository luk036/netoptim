# AGENTS.md - Agent Guidelines for netoptim

## Build/Lint/Test Commands

### Testing
```bash
# Run all tests (coverage on by default)
pytest

# Run single test
pytest tests/test_network_oracle.py::test_network_oracle_update

# Run tests matching a pattern
pytest -k "cycle_finder"

# With explicit coverage
pytest --cov netoptim --cov-report term-missing

# Run via tox (isolated environment)
tox
```

### Linting & Formatting
```bash
# Run all pre-commit hooks (recommended before committing)
pre-commit run --all-files

# Individual tools
black .               # Format code (line length 256)
isort .               # Sort imports
flake8 .              # Lint (max_line_length=256, ignores E203/W503)
mypy src/             # Type check (Python 3.12 target)
```

### Build & Docs
```bash
tox -e build          # Build sdist + wheel
tox -e clean          # Remove build artifacts
tox -e docs           # Build HTML docs
tox -e doctests       # Run doctests
tox -e linkcheck      # Check for broken doc links
```

## Code Style Guidelines

### Project Structure
- Source code: `src/netoptim/`
- Tests: `tests/` (test_network_oracle.py, test_optscaling.py, test_cycle_finder.py, test_ratio.py, test_delay_padding.py, test_stress_*.py)
- Version managed via setuptools_scm (`no-guess-dev` scheme)

### Naming Conventions
- **Classes**: PascalCase (e.g., `NetworkOracle`, `OptScalingOracle`)
- **Inner classes**: Nested PascalCase for helpers (e.g., `OptScalingOracle.Ratio`)
- **Functions/Methods**: snake_case (e.g., `assess_feas`, `assess_optim`, `update`)
- **Type aliases**: Short PascalCase (e.g., `Cut = Tuple[Any, float]`, `Graph = Dict[...]`, `Arr = np.ndarray`)
- **Private attributes**: Single underscore prefix (e.g., `_gra`, `_potential`, `_ncf`)

### Type Hints
- **Required**: All function parameters and return types
- Type aliases documented with module-level string docstrings
- Oracle interfaces typed against `ellalgo.ell_typing` (`OracleOptim`, `OracleFeas`)
- Generic types used where appropriate (e.g., `NegCycleFinder[Any, Any, float]`)

### Docstrings
- **Primary style**: Sphinx/reStructuredText with `:param:`, `:type:`, `:return:`
- **Alternative**: Google-style `Args:`/`Returns:` sections
- **Examples**: doctest blocks with `>>>` (use `unittest.mock.Mock` for graph oracles)
- **Diagrams**: `.. svgbob::` ASCII art for constraint descriptions

### Imports
- **Order**: stdlib → third-party → local (PEP8, enforced by isort)
- Relative import for package-local module:
  ```python
  from .network_oracle import NetworkOracle
  ```

### Error Handling
- **Minimal explicit error handling** — rely on natural exceptions
- Oracles return `(Cut, value)` tuples; `None` value signals infeasible/continuing
- No `assert` preconditions or `try/except` in algorithm code

### Python Version
- Minimum: Python 3.9 (setup.cfg `python_requires`)
- CI tests on Python 3.9 and 3.11

### Configuration Files
- `setup.cfg`: package metadata, pytest options, flake8 config
- `.flake8`: formatter-friendly (ignores E1/E2/E3/E501/W1/W2/W3/W5)
- `.pre-commit-config.yaml`: pre-commit hooks
- `mypy.ini`: Python 3.12 target, ignores setuptools/matplotlib/digraphx/ellalgo/mywheel
- `pyproject.toml`: build system (setuptools_scm)
- `tox.ini`: task automation (test, build, clean, docs, doctests, linkcheck, publish)
- `.coveragerc`: branch coverage, excludes `__repr__`, debug, and assertion code

### Pre-commit Hooks
- trailing-whitespace
- check-added-large-files
- check-ast
- check-json / check-yaml / check-xml
- check-merge-conflict
- debug-statements
- end-of-file-fixer
- requirements-txt-fixer
- mixed-line-ending (auto-fix)
- isort
- black
- flake8

### Testing Patterns
- Framework: pytest with coverage (addopts: `--cov netoptim --cov-report term-missing --verbose`)
- Custom mock oracle classes (e.g., `MockOracle` in tests) replace external oracles
- Graph fixtures built from `networkx` (`nx.DiGraph`)
- Stress tests (`test_stress_*.py`) exercise iteration bounds

## Key Project Context

netoptim solves parametric network flow optimization problems using cutting-plane/ellipsoid methods:
- **NetworkOracle**: feasibility oracle that detects negative cycles via Howard's algorithm (from `digraphx`) and emits a cutting plane `(gradient, intercept)` for each infeasible point
- **OptScalingOracle**: optimal matrix scaling (Orlin & Rothblum) built on the network oracle, exposing `assess_optim` for `cutting_plane_optim`
- **Solver backend**: `ellalgo` cutting-plane and ellipsoid routines; `digraphx` for negative-cycle search; `mywheel` for graph adapters
- **Key dependencies**: `digraphx`, `ellalgo`, `mywheel`, `networkx`, `numpy`
