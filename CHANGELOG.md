# Changelog

## Version 0.3 (2026-07-16)

### Documentation
- **plot_directive with network flow examples**: Enabled matplotlib plot_directive for auto-generated figures. Added network flow and network oracle example plots. (#4ae94a8)

### Bug Fixes
- **mypy type annotation fixes**: Annotated `NegCycleFinder` with `float Domain` to prevent `int` default. Fixed `NetworkOracle.__init__` parameter types to `Dict[Any, float]`. (#336ef29)
- **Float literal normalization**: Normalized integer literals to float in test graph data across cycle_finder, ratio, and stress_optscaling tests for type consistency. (#30f5d7a)
- **Re-enabled disabled tests**: Fixed type annotations in `test_delay_padding` and re-enabled `test_maximize_slack`, `test_maximize_effective_slack`. (#8a76500)

### Testing & Code Quality
- **Delay padding implementation**: Added delay padding with enhanced cycle finder test cases. (#9df6788)
- **Additional cycle finder tests**: Added extra test cases for cycle finder algorithms. (#9df6788)

### Code Cleanup
- **Removed PyScaffold boilerplate**: Deleted `skeleton.py`/`test_skeleton.py`, removed Python < 3.9 compat, dead entry points, stale `IFLOW.md`, duplicate `LICENSE`. (#4cd5756)

### Build & CI
- **CI repair**: Fixed broken entry_points and remaining skeleton imports. (#c2bf0d3)
- **Dependency fixes**: Added explicit `mywheel` dep, PyPI-compatible version pins, removed redundant git+https installs. (#81b59c8, #2d232b7, #f07e1bf)
