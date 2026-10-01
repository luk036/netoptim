# Tunable Parameters in `netoptim`

A complete reference of every user-tunable parameter of the algorithms in this
project, together with its default value and source location.

## Key finding

`netoptim` has **no `Options` / config dataclass of its own**. It reuses
**`ellalgo.ell_config.Options`** and adds one module-level override constant,
`DEFAULT_TOLERANCE = 1e-8`, which its two solver facades apply. The genuine
tuning surface is therefore small and split between netoptim's own constant and
the inherited ellalgo `Options`.

---

## 1. netoptim's own tuning surface

| Parameter | Default | Location | Notes |
| --- | --- | --- | --- |
| `DEFAULT_TOLERANCE` | `1e-8` | `src/netoptim/__init__.py:27` | Module constant. Deliberately looser than ellalgo's built-in `1e-20` (rationale documented in the docstring). |
| `options` (facade arg) | `None` → `Options` with `tolerance=1e-8` | `src/netoptim/__init__.py:49-53`, `:72-77` | Both facades fall back to `_default_options()` when `options is None`. |
| `gamma` (facade arg) | required (no default) | `src/netoptim/__init__.py:75` | Initial best-so-far objective; callers pass `float("inf")`. |

### Solver facades

| Function | Signature | Location |
| --- | --- | --- |
| `solve_network_feas` | `(oracle, space, options=None)` | `src/netoptim/__init__.py:49-53` |
| `solve_opt_scaling` | `(oracle, space, gamma, options=None)` | `src/netoptim/__init__.py:72-77` |

Both delegate to ellalgo's `cutting_plane_feas` / `cutting_plane_optim`.

---

## 2. Inherited tuning surface — `ellalgo.Options`

Because netoptim wraps ellalgo, the effective defaults are:

| Field | ellalgo default | netoptim effective default |
| --- | --- | --- |
| `max_iters` | `2000` | `2000` (unchanged) |
| `tolerance` | `1e-20` | `1e-8` (overridden by `DEFAULT_TOLERANCE`) |
| `verbose` | `False` | `False` (declared but unused) |

The search space is also inherited: `Ell(kappa, x_center)` from ellalgo
(`kappa` / center), selected by the caller.

---

## 3. Oracle constructors (all required, no default parameters)

| API | Signature | Location |
| --- | --- | --- |
| `NetworkOracle` | `(gra, u, oracle)` | `src/netoptim/network_oracle.py:56` |
| `OptScalingOracle` | `(gra, utx, get_cost)` | `src/netoptim/optscaling_oracle.py:111` |
| `OptScalingOracle.Ratio` | `(gra, get_cost)` | `src/netoptim/optscaling_oracle.py:36` |

The injectable strategy contract is the `EdgeOracle` protocol
(`src/netoptim/_typing.py:10-27`): `eval(edge, x)`, `grad(edge, x)`,
`update(t)`, plus the optional `make_weight_fn(x)` fast-path hook, which
`NetworkOracle` uses when present (`src/netoptim/network_oracle.py:103-106`).

---

## 4. Test and experiment constants (fixed values, not library defaults)

| Source | Constant | Value |
| --- | --- | --- |
| `tests/test_cycle_finder.py:11-12` | `MAX_ITERS`, `TOLERANCE` | `2000`, `1e-14` |
| `tests/test_delay_padding.py:11-12` | `MAX_ITERS`, `TOLERANCE` | `2000`, `1e-14` |
| `tests/test_cycle_finder2.py:12-13` | `MAX_ITERS`, `TOLERANCE` | `100`, `1e-7` |
| `tests/test_optscaling.py:186,193-194` | `DEFAULT_TOLERANCE`; tight `tolerance` | asserts `1e-8`; tight `1e-20` |
| `tests/test_optscaling.py:83-91` | `N`, `M`, `eta`, `seed`, `xbase`, `ybase` | `75`, `20`, `1.6`, `5`, `2`, `3` |
| `tests/test_stress_optscaling.py:78-86` | `N`, `M`, `eta`, `seed`, `xbase`, `ybase` | `200`, `50`, `1.6`, `5`, `2`, `3` |
| `tests/test_optscaling.py:155`, `tests/test_stress_optscaling.py:108` | `Ell` kappa | `1.5 * t` (or `200 * t` for the fixed graph) |
| `tests/test_ratio.py:78` | `Ell` kappa / center | `100.0`, `[7.5, 1.0]` |
| `tests/test_network_oracle.py:124` | `Ell` kappa / center | `10.0`, `[0.0, 0.0]` |
| `tests/test_cycle_finder*.py` | `bsearch` intervals | `(2.0, 4.0)`, `(0.0, 10.0)`, `(5.0, 10.0)`, `(0.0, 8.0)` |
| `tests/test_optscaling.py:52`, `tests/test_stress_optscaling.py:47` | `form_graph(T, pos, eta, seed=None)` | `seed` default `None` |
| same | `vdc` / `vdcorput(n, base=2)` | `base` default `2` |
| `experiments/plot_node_colormap.py:13` | `spring_layout(..., iterations=200)` | layout only, not solver-related |

---

## Summary of genuine tunables

| Tunable | Default | Location |
| --- | --- | --- |
| `DEFAULT_TOLERANCE` | `1e-8` | `src/netoptim/__init__.py:27` |
| `solve_network_feas(..., options)` | `None` → tolerance `1e-8` | `src/netoptim/__init__.py:52` |
| `solve_opt_scaling(..., gamma)` | required | `src/netoptim/__init__.py:75` |
| `solve_opt_scaling(..., options)` | `None` → tolerance `1e-8` | `src/netoptim/__init__.py:76` |
| `Options.max_iters` (inherited) | `2000` | `ellalgo/ell_config.py` |
| `Options.tolerance` (inherited) | `1e-20`, overridden to `1e-8` | `ellalgo/ell_config.py` |
| `Options.verbose` (inherited) | `False` (unused) | `ellalgo/ell_config.py` |
| Injected `EdgeOracle` strategy (`eval` / `grad` / `update`, optional `make_weight_fn`) | required | `src/netoptim/_typing.py:10-27` |
| `Ell(kappa, x_center)` (inherited search space) | required | `ellalgo/ell_base.py` |

Everything else is problem data (graph, node potentials, `get_cost`, the gamma
value) or a hardcoded constant.
