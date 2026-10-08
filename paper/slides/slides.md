# Introduction

## Why clock skew scheduling? ⏰

:::: {.columns}

::: {.column width="57%"}
- The clock is **periodic**: only the *relative* arrival times
  $y_{ij}=u_i-u_j$ matter
- **Useful skew** borrows slack from non-critical paths and lends it to
  critical ones
- It buys higher frequency, larger margin, or higher **yield**
- Design-flow view: run CTS first, then re-route; **placement is the lever**
- "A railway **timetable**, not a single departure time"
:::

::: {.column width="41%"}
![](../figures/fig01.pdf){width=110%}
:::

::::

## The central idea 💡

- The timing constraints are a **system of difference constraints**
  $$u_i - u_j \;\le\; w_e \qquad \text{for every arc } e=(j,i)$$
- Feasible $\iff$ the **timing constraint graph** (TCG) has **no negative cycle**
- Network form: a **feasible potential problem**
  $$\underline{w} \;\le\; y = A u \;\le\; \overline{w}$$
- Optimization: a **parametric potential problem**
  $$\max\{\, \beta \;:\; y \le d(\beta),\;\; A u = y \,\}$$
- A negative cycle is not only a certificate --- it is the **most critical paths**

## Outline 🗺️

1. Preliminaries: constraints and the timing constraint graph
2. Feasibility, clock-period minimization, parametric methods
3. Multi-parameter problems and the ellipsoid method
4. Delay padding
5. Yield-driven scheduling under process variations
6. Multi-corner and multi-mode robustness
7. Algorithms, clock-tree synthesis, open problems

# Preliminaries

## Local data path

:::: {.columns}

::: {.column width="55%"}
![](../figures/fig01.pdf){width=110%}
:::

::: {.column width="43%"}
- Register $R_i$ launches data; $R_j$ captures it
- Combinational delay in $[d_{ij},\, D_{ij}]$
- Clock arrival times $u_i$, $u_j$; skew $y_{ij} = u_i-u_j$
- Only the **difference** matters --- the clock is periodic
:::

::::

## Setup- and hold-time constraints

- **Setup** (avoids cycle-time violation / zero clocking):
  $$y_{ij} \;\le\; T_{\mathrm{CP}} - D_{ij} - T_{\mathrm{setup}} = \overline{w}_{ij}$$
- **Hold** (avoids a race / double clocking):
  $$y_{ij} \;\ge\; T_{\mathrm{hold}} - d_{ij} = \underline{w}_{ij}$$
- **Feasible skew region (FSR):** $\;\underline{w}_{ij} \le y_{ij} \le \overline{w}_{ij}$
- These are exactly **difference constraints** on the arrival times $u$

## Clock waveforms

:::: {.columns}

::: {.column width="52%"}
![](../figures/fig04.pdf){width=100%}
:::

::: {.column width="46%"}
- Source clock $\mathrm{CLK}_{\mathrm{src}}$
- Arrivals at $i$ and $f$ delayed by $t_i$, $t_f$
- Skew ${}= t_i - t_f$
- A common shift is **physically meaningless**
:::

::::

## The timing constraint graph (TCG)

- One vertex per register; arc weights in the **difference constraints**
- **$s$-edge** $j \to i$ of weight $\overline{w}_{ij}$ (setup)
- **$h$-edge** $i \to j$ of weight $d_{ij}-T_{\mathrm{hold}}$ (hold)

:::: {.columns}

::: {.column width="45%"}
```{=latex}
\resizebox{\linewidth}{!}{\input{../figures/tcgraph.tikz}}
```
:::

::: {.column width="53%"}
> **Theorem.** The constraints are satisfiable $\iff$ the TCG has **no negative cycle**.

- Around any cycle $C$, $\sum (u_{\mathrm{head}}-u_{\mathrm{tail}}) = 0$, so a
  cycle is feasible only if its weight is $\ge 0$
- A negative cycle certifies that **no schedule exists**
:::

::::

# Feasibility and Period Minimization

## Feasible potential problem

- Find $u$ such that $\;\underline{w} \le y \le \overline{w},\;\; A u = y$
- **Feasibility condition:** $d^{+}(P) \ge 0$ for every cycle $P$
- An infeasible instance returns a **negative cycle**
- **Bellman--Ford** decides one instance in $O(nm)$

## Bellman--Ford and lazy evaluation

```
for each v:  u[v] := 0 ;  pi[v] := nil
repeat |V| times:
    for each edge (p,q):
        if u[q] > u[p] + w[p,q]:  u[q] := u[p] + w[p,q] ; pi[q] := p
for each edge (p,q):
    if u[q] > u[p] + w[p,q]:  ->  negative cycle (trace pi)
```

- A negative cycle is detected only at the **end** of a full pass
- **Lazy evaluation**: run the analysis on demand, and
  **stop at the first negative cycle**
- This turns a global scan into a targeted repair tool

## Minimizing the clock period

- Minimize $T_{\mathrm{CP}}$ subject to the FSR being satisfiable
- For a cycle $C$ with $k$ setup edges, nonnegativity is
  $$T_{\mathrm{CP}} \;\ge\;
    \frac{\sum_{e \in C^{\mathrm{s}}} (D_e + T_{\mathrm{setup}})
        - \sum_{e \in C^{\mathrm{h}}} (d_e - T_{\mathrm{hold}})}{k}$$
- Smallest feasible period $=$ a **maximum cycle ratio**
- Constant denominator $\Rightarrow$ the **minimum mean cycle** problem

## The parametric potential problem

- $$\max\{\, \beta \;:\; y \le d(\beta),\;\; A u = y \,\},
    \qquad d(\beta) \text{ monotone decreasing}$$
- Affine $d(\beta) = m - s\beta$ $\Rightarrow$ **minimum cost-to-time ratio**
- Constant $s$ $\Rightarrow$ **minimum mean cycle**
- Monotone $g$ and $f$ $\Rightarrow$ a **unique** solution

## Lawler's binary search

:::: {.columns}

::: {.column width="52%"}
![](../figures/lawler.pdf){width=100%}
:::

::: {.column width="46%"}
- Keep a bracket $[\beta_{\min}, \beta_{\max}]$
- Test the TCG for a negative cycle at the midpoint
- Update a bound and repeat to tolerance
- Simple and robust; one Bellman--Ford pass per test
:::

::::

## Howard's policy iteration

:::: {.columns}

::: {.column width="45%"}
![](../figures/howard.pdf){width=100%}
:::

::: {.column width="53%"}
- One chosen outgoing arc per vertex (a **policy**)
- Its cycle yields an improved ratio $\Rightarrow$ a new $\beta$
- Recompute shortest paths, then update the policy
- Fast in practice; returns a **criticality hierarchy**
- Hybrid / improved variants interleave bisection pivots
:::

::::

## Minimum mean cycle and slack maximization

- **Karp (1978):** closed-form minimum cycle mean in $O(nm)$
- The canonical subroutine for EVEN and slack maximization
- **Slack maximization:** maximize the uniform margin
  $$u_i - u_j \;\le\; \mu_{ij} - \beta$$
- **Minimum balancing:** distribute slack on the critical cycle, contract it to a
  super-vertex, repeat --- the contraction order is the **criticality hierarchy**

# Multi-Parameter Problems

## Multi-parameter problems and the ellipsoid method

:::: {.columns}

::: {.column width="52%"}
- Real designs have **several** parameters (period, slack, several yields)
  $$\max\{\, g(\beta) : t_i - t_j \le f_{ij}(\beta)\,\},\quad \beta \in \mathbb{R}^{p}$$
- A **negative-cycle test is a separation oracle** --- one violated cut per step
- **Ellipsoid method:** multi-dimensional bisection; needs only separation
- Scalar bisection $\to$ **Newton / ellipsoid** when $p > 1$
- Realized by `netoptim`'s `NetworkOracle` + `ellalgo`
:::

::: {.column width="46%"}
```{=latex}
\begin{center}
\begin{tikzpicture}[font=\scriptsize, node distance=5mm]
\node[nblue] (q) {trial $\beta$};
\node[nred, below=9mm of q] (c) {negative\\cycle?};
\node[ngreen, below=9mm of c] (cut) {cutting\\plane};
\node[nyellow, right=13mm of c] (up) {shrink\\ellipsoid};
\draw[ar] (q) -- (c);
\draw[ar] (c) -- node[above]{yes} (cut);
\draw[ar] (cut) -- (up);
\draw[ar] (up) -- node[right]{new $\beta$} (q);
\end{tikzpicture}
\end{center}
```
:::

::::

# Delay Padding

## Delay padding

- If the TCG has a negative cycle, **no skew schedule fixes it**
- Change the physical delays: find $p \ge 0$, $u$ with
  $$y \;\le\; d + p, \qquad A u = y$$
- Minimizing $\sum p$ is the **dual of min-cost flow** --- but *impractical*:
  - delay is inserted by **swapping cells**, so $\sum p$ is not the true cost
  - some paths have **no valid position** for insertion

## Four structural configurations (PRA)

- Decide **where** delay may be inserted *before* deciding *how much*

:::: {.columns}

::: {.column width="25%"}
```{=latex}
\resizebox{\linewidth}{!}{\input{../figures/no_delay.tikz}}
```
Type (a): none
:::

::: {.column width="25%"}
```{=latex}
\resizebox{\linewidth}{!}{\input{../figures/independent.tikz}}
```
Type (b): $p_s, p_h$
:::

::: {.column width="25%"}
```{=latex}
\resizebox{\linewidth}{!}{\input{../figures/same_delay.tikz}}
```
Type (c): $p_s=p_h$
:::

::: {.column width="25%"}
```{=latex}
\resizebox{\linewidth}{!}{\input{../figures/setup_greater.tikz}}
```
Type (d): $p_s \ge p_h$
:::

::::

- The modified TCG makes this a **feasibility problem** again

## Discrete padding and its complexity

- Real padding is **quantized**: cell substitution or whole buffer stages
- The true feasible set of $p$ is **discrete** (and per-path non-convex)
- The exact problem is a **MILP**, not a network flow
- The continuous relaxation is
  - a **lower bound** on the achievable period, and
  - a guide to *which* paths are worth padding
- "Positions first, then values" keeps the discrete sub-problem tractable

# Yield-Driven Scheduling

## Timing yield

- **Yield** $=$ fraction of chips meeting **all** setup/hold constraints
- Different from a nominal period: we must reason about **distributions**
- Primitive solutions (margin pre-allocation, LCES, incremental slack)
  all ignore **path-delay variance**

## EVEN / PROP / C-PROP

- **EVEN:** equal variances; maximize the uniform margin $\beta$
  $\Rightarrow$ minimum mean cycle
- **PROP:** margin proportional to $\sqrt{D_{ij}}$; equalizes margins
- **C-PROP:** maximize $\beta$ with
  $u_i - u_j \le \mu_{ij} - \sigma_{ij}\beta$
  $\Rightarrow$ minimum cost-to-time ratio
- C-PROP **reduces to EVEN** when all variances are equal

| Problem | $d^{\mathrm{s}}_{ij}(\beta)$ | $d^{\mathrm{h}}_{ij}(\beta)$ |
|---|---|---|
| Min CP | $T_{\mathrm{CP}}-D_{ij}-T_{\mathrm{setup}}$ | $d_{ij}-T_{\mathrm{hold}}$ |
| EVEN | $T_{\mathrm{CP}}-D_{ij}-T_{\mathrm{setup}}-\beta$ | $d_{ij}-T_{\mathrm{hold}}-\beta$ |
| C-PROP | $T_{\mathrm{CP}}-D_{ij}-T_{\mathrm{setup}}-\sigma_{ij}\beta$ | $d_{ij}-T_{\mathrm{hold}}-\sigma_{ij}\beta$ |

## Spatial correlation

- These formulations use per-edge **marginals** and assume **independence**
- Silicon is **correlated**: nearby gates share systematic variation
- Correlation changes both the variance and the effective criticality of a cycle
- It becomes significant at 3 nm and below
- The max-min objective is thus a **surrogate** for the true timing yield

# Non-Gaussian Delay Models

## Why the Gaussian model fails

:::: {.columns}

::: {.column width="47%"}
![](../figures/non-gaussian.png){width=100%}
:::

::: {.column width="51%"}
- The maximum path delay is **asymmetric and heavy-tailed** below 65 nm
- Setup failures depend on the **upper** tail (slow corners)
- Hold failures depend on the **lower** tail (fast corners)
- Gaussian fits the bulk but **misses the tails** --- wrong yield
:::

::::

## The GEV distribution

- **Generalized Extreme Value:** location $\mu$, scale $\sigma > 0$, shape $\xi$
  $$F(x) = e^{-t(x)}, \qquad t(x) = \Bigl[1 + \xi\,\frac{x-\mu}{\sigma}\Bigr]^{-1/\xi}$$
- Quantile:
  $$Q(\beta) = \mu + \frac{\sigma}{\xi}\Bigl((-\ln\beta)^{-\xi} - 1\Bigr)$$
- Deterministic equivalents via quantiles, e.g.
  $T_{\mathrm{CP}} - T_{\mathrm{setup}} - T_{\mathrm{skew}} \ge Q_D(\beta)$
- Monotone $Q$ $\Rightarrow$ a single scalar $\beta$; the graph machinery **survives**

# Robust Scheduling

## Multi-corner and the ping-pong effect

- Require timing for **all** corners $k$:
  $$y \le d^{(k)},\quad A u = y,\quad \forall k$$
  which is the single-corner problem with $y \le \min_k d^{(k)}$
- Fixing corners one by one can create violations in another:
  the non-convergent **ping-pong** effect
- Padding across corners is **not** a pure network flow (shared $p$)

## Dual decomposition and multi-mode

- Relax $y_k = y_{\mathrm{shared}}$ with multipliers $\lambda_k$
- Per-corner **min-cost potential** sub-problems, solved in parallel
- Updates:
  $$y_{\mathrm{shared}} \leftarrow \frac{1}{K}\sum_{k=1}^{K} y_k,
    \qquad \lambda_k \leftarrow \lambda_k + \rho\,(y_k - y_{\mathrm{shared}})$$
- Reported: about **6%** period reduction vs. a single worst-case corner
- **Multi-mode + ADB:** each mode has its own arrival times --- the hard part is
  the clock tree and the ADB **range**

# Algorithms and Clock Trees

## Algorithms at a glance

| Method | Strategy | Cost / behavior |
|---|---|---|
| Bellman--Ford | single feasibility test | $O(nm)$ |
| Karp | minimum mean cycle | $O(nm)$ |
| Lawler | binary search + feasibility test | $O(nm \log(1/\epsilon))$ |
| Howard | policy iteration / cycle cancellation | fast in practice, exact |
| Young--Tarjan--Orlin | parametric shortest path | $O(nm + n^2 \log n)$ |

- All share one primitive: **detect and cancel negative cycles**

## From schedule to clock tree

- Realize the arrival times by **DME** + buffer insertion
- Large skews between distant registers are **expensive**:
  detours, **power**, routing **congestion**
- The schedule is a **delay-only** optimum; a production flow must re-optimize
- **Criticality-ordered topology:** the deepest branch has the smallest
  variation --- let placement follow the tree

# Closing

## Open problems and limitations

- **Open:** minimum ADB range; criticality under modes; physical cost of skew;
  discrete (MILP) padding; correlation-aware yield; hierarchical / CDC / gated
  designs; independent evaluation on modern benchmarks
- **Limitations (this survey):** no new experiments
- Four idealizations the framework makes:
  1. **physical realizability** (free continuous arrival times)
  2. **discrete delay** (quantized padding)
  3. **statistical independence** (no spatial correlation)
  4. **flatness** (one synchronous graph)
- The framework is the exact **algorithmic core** of a larger physical problem

## Conclusion

- One mathematical core: **difference constraints** $+$ **negative cycle**
- Min period, max slack, max yield all reduce to a **parametric
  shortest-path** problem
- Fast combinatorial solvers; the critical cycle is directly actionable
- Extends to delay padding, multi-corner/multi-mode, heavy-tailed (GEV)
  statistics, and multi-parameter scaling via the **ellipsoid method**

## Q&A 🎤

**Thank you! Questions?**
