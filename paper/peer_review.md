# Referee Report

**Manuscript:** Clock Skew Scheduling: Formulations and Algorithms
**Author:** Wai-Shing Luk
**Length:** 23 pp., 26 references
**Recommendation:** Major revision (bordering on reject-and-resubmit)

---

## 1. Summary

The manuscript surveys clock skew scheduling (CSS) through a single lens: the
timing constraints are a system of difference constraints, feasibility is the
absence of a negative cycle in the timing constraint graph (TCG), and the
optimization variants (minimum period, maximum slack, maximum yield) are
parametric potential problems solvable by ratio-cycle and separation-oracle
methods. It then extends the core to delay padding, yield-driven scheduling
under process variation, GEV delay models, and clock-tree co-optimization, and
closes with a "common misconceptions" section and an open-problems list.

The narrative is coherent and the organizing idea is the right one. But the
manuscript is not yet a reliable survey: several of the mathematical statements
that an implementer would act on are wrong or internally inconsistent, the
central "one parametric family" claim does not hold as stated, the key
separation-oracle theorem is asserted rather than proved, the literature base
omits the field's canonical works (including the author's own recent papers on
exactly the GEV topic), and the evidence policy is not defensible.

## 2. Strengths

- The difference-constraint/negative-cycle framing is correct and is the right
  spine for such a survey.
- §8.2's *target skew vs. actual skew* distinction is genuinely useful, is
  rarely stated this crisply, and is the best original expository contribution
  in the paper.
- §8.1's honesty about the physical cost of large skews (power, wirelength,
  congestion) is exactly the caveat most algorithmic papers omit.
- Table 1 (once corrected) is a good pedagogical device, and the
  "criticality hierarchy" from minimum balancing is a good thing to foreground.
- The stated limitations in §10.3 are the right list; the problem is that the
  paper argues with the reader about them rather than just stating them.

## 3. Major concerns

### M1. The mathematics contains sign and quantifier errors that would break an implementation

This is the most serious issue. The manuscript is a *formulations* paper; a
reader will implement from it. Several displayed results are wrong or mutually
inconsistent.

**(a) The hold-time equivalent in the GEV section is reversed.** At L1272 the
manuscript writes `T_hold − T_skew ≥ Q_d(1−β)`. From
`Pr{T_skew ≥ T_hold − d̃} ≥ β` one obtains
`Pr{d̃ ≤ T_hold − T_skew} ≤ 1−β`, hence `T_hold − T_skew ≤ Q_d(1−β)`. The
printed `≥` makes the constraint vacuous (it is satisfied by every negative
margin). Given that §7 is the manuscript's showcase extension, this error is
fatal as written.

**(b) The C-PROP "most critical cycle" is backwards.** At L999–1001 the
critical cycle is said to be the one *maximizing* `Σμ/Σσ`. From
`t_j − t_i ≤ μ_e − σ_e β`, feasibility requires `Σ(μ_e − σ_e β) ≥ 0` on every
cycle, i.e. `β ≤ min_C Σμ/Σσ`. The binding cycle therefore *minimizes* the
ratio — which is consistent with L998 ("minimum mean cycle") and contradicts
L1000.

**(c) Two different arc conventions coexist.** §2.3 encodes the setup constraint
as an `s`-edge `j→i` with `u_i − u_j ≤ w̄`. But EVEN (L919) and C-PROP (L1003)
are written as `t_j − t_i ≤ …`, while the Table 1 caption (L1050) says "every
constraint reads `t_i − t_j ≤ f_e(β)`", and §6.6 (L1079–1080) uses a third
pattern. The arrival-time symbol also switches between `u` and `t` with no
statement that they are the same object (L83 vs. L453 vs. L1099), and skew is
variously `y_ij`, `T_skew`, and `skew_ij` (L10, L899, L932). A global sign and
notation audit is mandatory, and a notation table is needed.

**(d) The PROP hold expression is the negated bound.** §2.2 defines
`w̲ = T_hold − d`. At L967–968 the manuscript writes
`w̲^PROP = −T_hold + (d − α√d σ)`, which is the *h-edge weight*
(`d − T_hold − …`), not the FSR lower bound. Also `α√(D_ij)·σ` is
dimensionally inconsistent (√time × time) unless σ is defined per √time, which
it is not; and `√D` is being used as a proxy for the number of stages, which
requires `D ∝ n`, never stated.

**(e) The §6.15 linearization silently discards the nonlinearity the paper
exists to handle.** At L1178–1185, `β ≤ Pr{y_ij ≤ d_ij + p_ij}` is declared
"equivalent to the linear program `y ≤ d − βs + p`". That holds only for the
linearized quantile `Q(β) = d − βs`, not for the Gaussian quantile of §6.12
(`μ + σ√2 erf⁻¹(2β−1)`) nor the GEV quantile of §7. The dual at L1189–1191
inherits the error. Additionally, `c` denotes the padding cost in the primal
and the capacity vector in the dual, `s` is called a "variance" but used as a
scale, and `β` is a probability in one line and a σ-multiple in the next.

**(f) The co-optimization sentence at L1155–1156 is backwards.** "the hold bound
grows with the yield": the hold bound is `F⁻¹(1−β)`, which *shrinks* as β grows
(hence tightening). The subsequent claim that the program is convex for
`β ≥ 0.8` may well be true for Gaussian marginals (because `Φ⁻¹` is convex above
the median and `1−β < 1/2` lands in the concave branch), but the manuscript
gives no argument, and the condition is distribution-dependent (for log-normal,
`F(mode) = Φ(−σ)`, so `β ≥ 0.8` is not sufficient when σ is large).

**(g) Two smaller but still operative errors.** The "useful sufficient
condition" at L414–420 — "if g and every f_e are monotone decreasing, the
parametric problem has a unique solution" — is false: with `f_e` decreasing the
feasible set in β is downward closed, so a decreasing `g` is optimized at the
*left* end (generically unbounded), and the potential `u` is never unique
because of gauge freedom. The same claim recurs at L1066–1067. And at L390–393,
"the smallest feasible period is a *maximum* cycle ratio … This is the
minimum-cost-to-time-ratio cycle problem" is a terminology inversion; the code
resolves it by negating a column (as admitted at L1497–1499), but the text
should say so.

### M2. The "one parametric family" claim (Table 1) does not hold

This is the paper's synthesis centerpiece and it is not established.

- The **Min. CP** row has `f_ij(β) = β − D − T_setup`, which is *increasing* in
  β, whereas the family is defined (L402–403, L1066) by *decreasing* right-hand
  sides. The row is only an instance after the substitution `β = −T_CP`, i.e. a
  different parametrization. Either state the substitution explicitly or drop
  the "differing only in g and f" claim.
- The table has **three** rows, but L1496 refers to "the four rows of the family
  table". The code (`digraphx/css.py`) has four adapters (min-CP, EVEN, PROP,
  C-PROP); the table omits PROP — the method the section spends most space on —
  and includes Min. CP, which is not a yield method.
- `β` carries four different meanings and units across the paper (period; time
  margin; multiple of σ; probability). A table that puts them in one column
  without units is misleading.

### M3. The separation-oracle argument is asserted, not proved

The claim that the ellipsoid method applies (L465–490) is the technical heart of
§4.4 and it is not correct as written:

> "either the TCG is feasible, or it contains a negative cycle C; in the latter
> case `Σ_{e∈C} f_e(β) < 0` is a violated constraint that separates β from the
> feasible set."

A negative cycle certifies infeasibility of the *fixed* β. It does not, by
itself, separate anything in β-space. Separation requires that
`β ↦ Σ_{e∈C} f_e(β)` be convex and that the cut be the subgradient inequality
`gᵀ(β′ − β) ≤ 0` with `g = Σ_e ∇f_e(β)`. That is precisely what
`netoptim/network_oracle.py:115` and `css_oracle.py:63–65` implement, so the code
is ahead of the text. The manuscript must state the convexity hypothesis, give
the subgradient, and prove the implication.

Two related conflations run through §3.3–§4.4:

- L473: "never requires all `|E|` constraints — indeed, all path delays — to be
  known in advance." The oracle does require the graph (all arcs); what is lazy
  is the *evaluation of weights*, not the *generation of constraints*. Lazy
  weight evaluation and lazy constraint generation are different ideas and the
  paper uses one phrase for both.
- The ellipsoid update (L486–487) gives only the center update; the matrix
  update is omitted, as is any complexity statement, so the displayed
  "algorithm" cannot be implemented or checked.

### M4. §3.2's cycle characterization is stated for the wrong graph and is neither proved nor cited

The manuscript defines upper/lower spans over an oriented cycle `P` and asserts
`d⁻(P) ≤ 0 ≤ d⁺(P)` for every cycle, then says "conversely, these cycle
conditions are sufficient". But the TCG construction of §2.3 has already folded
the lower bounds into negated arcs, so the graph on which §3.2 reasons is not the
graph of §3.3. The correct statement is a circulation theorem (feasibility of
`w̲ ≤ Au ≤ w̄` iff every circulation has nonnegative cost with respect to the
box), i.e. Hoffman's theorem; it should be stated precisely, cited, and proved
or at least sketched. As written, the sufficiency direction is a gap, not a
result.

### M5. The deterministic and statistical models are never reconciled

§2 defines `D_ij` and `d_ij` as extrema "over the relevant operating
conditions" (corners). §6 redefines them as random variables with `(μ, σ)` from
SSTA. The relationship (corner = high quantile) is never stated, and the paper
slides between worst-case corner analysis and statistical analysis without
comment.

Worse, §8.2 introduces random clock arrivals `δ_i` and correctly writes the
actual skew as `y*_ij + (δ_i − δ_j)`, but the yield formulation of §6 attributes
*all* uncertainty to data delays. So §6 optimizes a surrogate for a quantity
that §8.2 says is not the realized skew. Either fold clock variation into the
edge statistics, or state the assumption `σ_clock ≪ σ_data` explicitly. As it
stands, the two halves of the paper use incompatible models.

There is a second modelling gap in the same area: the LP has no bound on the
skew *spread*. Because the constraints are translation-invariant, an optimal
solution may require `u_i − u_j` comparable to `T_CP`, which is not physically
realizable (and is exactly the constraint that clock-tree construction methods
such as Held et al. 2003 impose). The manuscript discusses the *cost* of spread
in §8.1 but never the *feasibility* constraint.

### M6. The literature base is not adequate for a survey, and it omits the author's own recent work

Twenty-six references for a 23-page survey spanning timing analysis, network
optimization, statistics, and physical design is an order of magnitude too thin.
The following are not optional:

- **Retiming and the cycle bound** — the direct ancestor of the paper's
  L386–388 formula: Leiserson & Saxe (FOCS 1981; *Algorithmica* 1991);
  Sapatnekar & Deokar (TCAD 1996); Liu, Papaefthymiou & Friedman (DAC 1999,
  "Maximizing performance by retiming and clock skew scheduling"); Sakallah,
  Mudge & Olukotun (TCAD 1992); Burns (Caltech PhD thesis, 1991). The
  retiming–skew equivalence is the single most conspicuous omission.
- **Delay padding** — Shenoy, Brayton & Sangiovanni-Vincentelli (ICCAD 1992;
  and the 1993 minimum-padding paper). §6 presents a four-way taxonomy as if it
  were self-evident; it has a literature and should be attributed.
- **Parametric shortest path** — Karp & Orlin (1981), Megiddo (1979),
  Gusfield (1983), Carstensen (1983). Citing only YTO 1991 for the parametric
  machinery is not a survey.
- **Difference constraints** — Hoffman (1960) for the circulation theorem used
  implicitly in §3.2; Shostak (1981); Pratt (DAC 1977); Dechter, Meiri & Pearl
  (1991); Cherkassky & Goldberg (1999).
- **Statistical timing** — Agarwal, Blaauw & Zolotov (ICCAD 2003); Chang &
  Sapatnekar (TCAD 2005); Blaauw, Chopra, Srivastava & Scheffer (TCAD 2008);
  Bowman, Duvall & Meindl (JSSC 2002); Orshansky et al. (TCAD 2002); Liu,
  Nassif, Pileggi & Strojwas (DAC 2000). Declaring spatial correlation an "open
  problem" (L1590–1592) is only true at the level of joint-yield optimization;
  at the level of the models the paper claims to survey, it is a solved topic
  with a literature.
- **Non-Gaussian / GEV** — this is the most serious omission because it involves
  the author's own record. There is a 2025 ASP-DAC paper "Yield-driven Clock
  Skew Scheduling Based on Generalized Extreme Value Distribution" (Zhu, Luk &
  Wang, pp. 425–432, DOI 10.1145/3658617.3697739), a 2026 TCAD paper "Timing
  Yield-Driven Clock Skew Scheduling Based on Hybrid Distributions" (Zhu, Li,
  Wang & Luk, 45(11):5601–5614, DOI 10.1109/TCAD.2026.3694340), and a 2008 DAC
  paper by Wang, Luk, Zeng, Tao, Yan, Tong, Cai & Ni on non-Gaussian
  critical-path delays. §7 cites **only Jenkinson (1955)**. A survey that
  reproduces six pages of a topic without citing the papers that established
  it — particularly when the author is a co-author of those papers — raises a
  duplicate-publication question, not merely a citation question.
- **Two entries already in `refs.bib` are never cited**: `held2003clock` (clock
  scheduling *and* clock-tree construction — exactly §8) and `wang2006extensive`
  (front-end awareness of CSS — exactly the §1 "tool-chain contract" and the
  §8.3 placement claim). `luk2026lecture` is also uncited although the figure
  captions refer to "the lecture". Uncited entries in a bibliography indicate
  unfinished integration.

### M7. The evidence policy is not defensible

The manuscript declares itself a survey (L130–135) and then (L1543–1551)
pre-empts the "no experiments" criticism with the argument that enabling data
"costs millions". That argument does not survive contact with current practice:
public benchmark suites (ISCAS-89, ITC-99), an open PDK (SkyWater 130), and an
open RTL-to-GDS flow (OpenROAD) make a controlled comparison feasible; and the
algorithms in question are a few hundred lines. A 2-page study on random TCGs
plus one open design — network formulation vs. an LP solved by HiGHS, with
runtime and cycle counts — would transform the paper's credibility. Without it,
the survey's central practical claim (that the parametric/network route beats
generic LP/convex solvers) rests on a single 2015 citation, presented
mid-derivation at L494–498 as though it were established fact.

The related "Experimental results" subsection (§6.13) is unacceptable as it
stands: a figure that "reproduces the lecture's experimental results" with no
benchmark, no instance sizes, no PDK, no runtime, and no machine. Either
describe the experiment and cite its source, or remove the figure.

### M8. The manuscript argues with its referees in the text

§10.4 is titled "Common misconceptions" and includes "a reviewer who asks 'why is
the arrival time not a random variable when the method is statistical?' has
mistaken the deterministic target for the random outcome" (L1441–1445). This is
not scholarly prose; it is a rebuttal to a prior review embedded in the
manuscript. State the modelling assumptions positively in §6 and §8.2 and delete
§10.4. The same applies to "the absence of benchmark experiments is a matter of
cost and access rather than relevance": it reads as a pre-emptive defense and
invites exactly the objection it tries to forestall.

There is also an unresolved contradiction about novelty: the abstract says
"**We extend** the core with delay padding, statistical methods, GEV delay
models"; L130 says the article "organizes and explains known formulations …
rather than reporting new experiments"; §9.2 says "the code is not a
contribution of this article"; and §7 is, in fact, the author's own recent
research presented as survey. Pick one position and make it true throughout.

### M9. §5 is five pages of textbook material that never touches the stated subject

Cycle canceling, line search, convex costs, and the barrier method are presented
generically (L593–739) and connected to CSS by three sentences of assertion
(L631–637). The two correspondences that would justify the section are never
derived: (i) the LP dual of the padding problem
`find p,u: y ≤ d + p, p ≥ 0, min Σp`, whose dual is the min-cost circulation the
text invokes; and (ii) the asserted duality between the statistical *flow*
problem (L690–708) and the per-edge *potential* constraints of §6. The former is
a half-page derivation; the latter is not obviously true (one constrains flows,
the other tensions) and needs either a proof or an explicit statement that the
analogy is structural only. As it stands, §5 reads as notes from a different
course, and the table-of-contents promise at L118–120 is not kept.

### M10. Physical and practical coverage is thinner than the paper's framing implies

- **Latches.** The opening sentence says the clock must reach "every flip-flop
  (FF) and latch"; latches then disappear. Level-sensitive latches admit time
  borrowing, which changes the constraint system (soft constraints) and is a
  substantial part of the scheduling literature. Either cover it or remove the
  mention.
- **Multi-cycle paths** are absent, although they are the natural graph
  modification alongside padding.
- **Hold fixing** is the practical reason useful skew is hard to deploy:
  aggressive skew frequently creates hold violations, which then require
  buffering. This is mentioned only as "double clocking".
- **MCMM / OCV / POCV** sign-off is the industrial framing in which skew
  schedules are actually accepted or rejected; per-edge `(μ, σ)` does not map
  onto it, and the paper never says how.
- **Multi-domain** scheduling is mentioned at L447 and then dropped
  (Ravindran, Kuehlmann & Sentovich, ICCAD 2003, is the obvious citation).

## 4. Specific corrections

| # | Location | Problem | Fix |
|---|---|---|---|
| 1 | L12–14 | Common-shift invariance attributed to clock *periodicity* | It is translation invariance of the potential problem; periodicity is a different (mod-`T_CP`) statement |
| 2 | L73–74 | "New machinery only if a constraint is placed on absolute time, a situation that current practice does not produce" | False: interface timing and clock-domain crossings impose absolute-time constraints routinely |
| 3 | L311–321 | Cycle-span criterion stated on the wrong graph; sufficiency unproved | State the circulation theorem on the doubled graph; cite Hoffman (1960) |
| 4 | L341–359 | Algorithm 1 runs all `n` passes, then tests — it does *not* implement the "stop as soon as a negative cycle is found" recommended at L335–338; the `π`-trace is not guaranteed to yield a negative cycle | Give the early-exit algorithm, or delete the recommendation |
| 5 | L390–393 | Max ratio mislabelled "minimum cost-to-time ratio" | Fix, and cross-reference the negation used at L1497 |
| 6 | L414–420, L1066–1067 | "Monotone decreasing ⇒ unique solution" | False; and `u` is never unique (gauge) |
| 7 | L473 | "Never requires all `\|E\|` constraints … to be known in advance" | It requires the graph; only weight evaluation is lazy |
| 8 | L486–487 | Ellipsoid update missing the `A_{k+1}` update and any complexity statement | Complete the update; state `O(p² log(1/ε))` |
| 9 | L919, L1003 vs. L1050 | Arc direction `t_j − t_i` vs. `t_i − t_j` | Global sign audit; single convention |
| 10 | L999–1001 | Critical cycle "maximizes" `Σμ/Σσ` | It minimizes |
| 11 | L1052–1061, L1496 | Min-CP row has increasing `f`; three rows, not four; PROP missing; `β` units | Restate the family with the `β = −T_CP` substitution made explicit |
| 12 | L1099–1103 | PROP hold line is the negated FSR bound; `α√D·σ` dimensionally inconsistent | Fix and define σ's units |
| 13 | L1155–1156 | "Hold bound grows with the yield" | It shrinks |
| 14 | L1178–1185 | "Equivalent to the LP" drops the quantile nonlinearity; `c` and `s` overloaded | Derive under a stated linearization, or delete |
| 15 | L1271–1272 | Hold equivalent inequality reversed (`≥` should be `≤`) | Fix; as printed the constraint is vacuous |
| 16 | L1130, L1156–1159 | "Efficiently by binary search" and "is convex" asserted | Quantify the cost; prove the convexity condition, including the distribution-dependent case |

## 5. Complexity claims: verified facts

These were checked against the primary sources and change the status of §9.1
from "needs clarification" to "incorrect".

- **Young, Tarjan & Orlin (1991)** solve the parametric shortest path problem
  with costs `c(e) − λ` on a subset of arcs, i.e. slopes in `{0, −1}`, in
  `O(nm + n² log n)`. Their §6 extends this to concave costs with derivatives in
  `{−K, …, 0}`, giving `O(Knm + K n² log n)` — pseudo-polynomial in `K`. They
  observe that the minimum average weighted length (min cost-to-time ratio)
  problem reduces to this generalized problem by taking the edge cost as
  `λ·t_e − c_e`, but the resulting guarantee carries the factor `K`; the clean
  `O(nm + n² log n)` does not apply to arbitrary real times.
- **Karp & Orlin (1981)** likewise assume unit coefficients (`t_e ∈ {0,1}`),
  with `O(nm log n)` and `O(n³)` variants.
- **Megiddo (1979)** solves the general min-ratio-cycle problem in
  `O(|E||V|² log|V|)`, strongly polynomial, assuming positive denominators
  (all `t_e > 0`). Megiddo (1983) and Bringmann–Hansen–Krinninger (2017,
  `Õ(m^{3/4} n^{3/2})`) improve it.
- **Carstensen (1983)** shows that parametric shortest path with arbitrary
  slopes can have `n^{Ω(log n)}` breakpoints, so no `O(nm + n² log n)`
  pivot-based bound exists in general.
- For the **minimum mean cycle**, Karp's `O(nm)` is better than
  `O(nm + n² log n)`, so "attains the best worst-case bound among them" is not
  even internally coherent: the table mixes min-mean-cycle, binary-search, and
  parametric-shortest-path problems, and the winner differs per problem.

- **Howard's policy iteration** is exact in exact arithmetic, but **no
  polynomial worst-case bound is known**; the published bounds are exponential
  or pseudo-polynomial. Lower bounds for the deterministic min-mean-cycle case
  are only quadratic (Hansen–Zwick 2010; Asadi et al. 2025); exponential lower
  bounds exist only for the more general stochastic-MDP / strategy-iteration
  setting (Friedmann 2009; Fearnley 2010). Empirically, Dasdan (2004) found YTO
  fastest overall, with Howard and Valdes nearly as fast on circuit instances.
- **"Returns the sequence of critical cycles in decreasing order of
  criticality"** is not a property of Howard's algorithm: a critical cycle is
  one attaining the optimum, and Howard returns exactly one (Boost's
  `maximum_cycle_ratio` and LEMON's `HowardMmc` both return a single cycle).
  The sequence property belongs to the minimum-balance algorithm of Albrecht et
  al., which contracts a min-ratio cycle at each step, producing ratios that are
  **nondecreasing** — i.e. running from the most critical (smallest slack) to
  the least.

## 6. Minor points

- Figure quality: six figures are raster PNGs (one is 1 MB, evidently a
  screenshot), several use `\resizebox`-scaled TikZ with mismatched fonts, and
  `fig:cprop` / `fig:uncertainty` are never referenced in the text. Journal
  production will require vector figures with consistent type sizes and captions
  that state what is plotted.
- Notation collisions beyond `t/u`: `A` (incidence matrix vs. ellipsoid matrix
  `A_k`), `d` (min delay, `d(β)`, min-cost-flow cost vector, differential), `c`
  (capacity, cost), `w` (FSR bound, arc weight, random slack `W̃`), `T` (period,
  setup, hold, skew, frozen arrival time `T_v`, `T_i^final`), `s` (slope, σ,
  capacity vector). A notation table is required.
- L141–147: "a data path … traverses the logic in a delay that ranges between
  `d_ij` and `D_ij`" — the setup bound uses the slowest path and the hold bound
  the fastest; these are generally *different* paths, not one path with a range.
- L188–198: "race condition" is loose for a hold violation; use "hold violation
  / double clocking".
- L465: "the negative-cycle test is a separation oracle" — the test is not an
  oracle; the procedure that returns a violated cycle is.
- L1324–1328, L1346–1348: "converges locally in the sense that each test is
  global but the bracket shrinks slowly" is not a meaningful statement about
  convergence.
- The abstract is only in `metadata.yaml`; the body opens directly with
  "# Introduction". Include the abstract in the manuscript, and add a
  "Contributions" paragraph.
- `classoption: twocolumn` in `metadata.yaml` contradicts the Makefile's
  "comfortable single-column page" comment. Decide.
- `fig:hierachy` is misspelled (label and filename); it is used consistently,
  so this is cosmetic, but it will propagate.

## 7. Questions to the authors

1. §7's GEV material overlaps substantially with the 2025 ASP-DAC and 2026 TCAD
   papers by (in part) the same author. What is the delta, and why are they not
   cited?
2. What exactly is the separation oracle's guarantee in the nonlinear
   multi-parameter case? State the convexity assumption and give the cut.
3. Is the "one parametric family" claim meant to include Min. CP under the same
   monotonicity hypothesis, or three separate problems united only after a
   change of variable?
4. How are the corner-based `D_ij, d_ij` of §2 related to the `(μ_ij, σ_ij)` of
   §6? Is `D_ij` a 3σ point, a corner, or a max over corners?
5. What constrains the skew spread in the optimization? Without such a
   constraint the LP optimum is not physically realizable.
6. Which of the four family members does the reference implementation actually
   solve, and does it match the equations in §6?

## 8. Verdict

The paper has a good spine and a real expository contribution in §8.2. It is not
publishable in its present form because a reader cannot safely implement from it
(M1), its central unification is not established (M2), its key theorem is
asserted (M3–M4), its two halves use incompatible models (M5), its literature
base is inadequate and omits the author's own prior work on the paper's most
novel-looking section (M6), and its evidence policy is not defensible (M7).

**Major revision**, with the following as conditions for acceptance:

1. A full sign/notation audit and correction of every item in the table in §4.
2. A proof of the separation-oracle claim with explicit convexity hypotheses.
3. A corrected and honest statement of the family/unification result.
4. Resolution of the overlap with the 2025/2026 GEV papers and citation of the
   group's 2008 DAC paper.
5. A proper related-work section covering retiming, padding, parametric
   optimization, and SSTA.
6. At least a modest computational study on open benchmarks or random TCGs.
7. Deletion of §10.4 and of the pre-emptive defense in §10.3.
8. A corrected complexity table with per-problem hypotheses and deletion of the
   YTO "best bound" claim.
9. Correction of the Howard row and of the critical-cycle-sequence sentence.
