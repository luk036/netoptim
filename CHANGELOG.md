# Changelog

## Version 0.4 (2026-10-09)

### Features
- **Oracle facades + `EdgeOracle` protocol**: Added `_typing.py` (`EdgeOracle` Protocol + `Cut` alias), re-exported the oracles from `__init__.py`, and added `solve_network_feas` / `solve_opt_scaling` facades. `OptScalingOracle.Ratio` gained its missing `update()` no-op. (#9137d2f)
- **Tighter default optimizer settings**: `DEFAULT_TOLERANCE` tightened to `1e-10` (was `1e-8`; measured ~1e-5 vs ~1e-4 objective error for ~10–15 extra iterations), and `solve_opt_scaling`'s `gamma` now defaults to `float('inf')`. (#1d36ef0)

### Performance
- **Oracle hot path + Options forwarding**: Forward `Options` through the facades (default `1e-8` vs ellalgo's `1e-20`: 51→27 iterations on the stress graph); added an optional `EdgeOracle.make_weight_fn` hook with `Ratio` binding `x[0]`/`x[1]` once per assessment to avoid NumPy scalar indexing in the per-edge loop. Measured ~300 ms → ~90 ms (3.4×) on the 250-node / 1844-edge optscaling stress graph with identical gamma. (#505fab2)

### Bug Fixes
- **`solve_network_feas` facade**: It called `cutting_plane_optim` (needs `assess_optim`) and raised `AttributeError`; now calls `cutting_plane_feas` and drops the unused `x0` argument. `NetworkOracle` now nominally subclasses `OracleFeas`, making mypy clean. (#505fab2)
- **`Ratio.update()` latent `AttributeError`**: Added the missing no-op. (#9137d2f)
- **mypy config**: Removed the duplicate `ignore_missing_imports` entry. (#8aa12b1)
- **RTD docs build**: Added matplotlib to `docs/requirements.txt`. (#be689e8)

### Testing & Code Quality
- **Oracle tests**: Added tests for the `make_weight_fn` hook, Options forwarding, and the feasibility facade. (#505fab2)

### Code Cleanup
- **Removed AI slop**: Stripped docstring/comment boilerplate and expanded the `EdgeOracle` protocol stubs to multi-line. (#94f68b0, #d62cc66)

### Documentation
- **Clock-skew scheduling survey paper + slides**: Added a 16-page two-column Pandoc survey (`paper/clock_skew_scheduling.md`) and a 30-minute Beamer deck (41 frames) with a vendored IEEE CSL, TikZ figures, offline build Makefiles, and reference-availability notes. (#1f0df97, #59b61e2, #ab91ef7, #1fc930c, #25981dd)
- **Tunable parameter reference**: Added `tunable_parameter.md`. (#7afef62)
- **AGENTS.md**: Added agent guidelines. (#6e36a7f)

### Build & CI
- **Updated GitHub Actions**: `checkout`→v4, `setup-python`→v5, `codecov-action`→v4; removed the stale `.bak` workflow files. (#6016c29, #5351aa8)

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
