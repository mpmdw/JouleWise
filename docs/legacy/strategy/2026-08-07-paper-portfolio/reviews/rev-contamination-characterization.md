# Counter-review: "Quiet Is a Measured State" (prop-contamination-characterization)

Reviewer: Opus 5, counter-review pass. Charge: kill it.
Ground truth: `desk/` @ main. Every number below was checked against primary repo bytes.

**VERDICT: WEAK** (one notch from KILL; survives only in the shrunken forms in §Strengthening).

| axis | score |
|---|---:|
| novelty | 3 |
| feasibility | 3 |
| mvp_leverage | 6 |
| venue_fit | 4 |
| original_goals | 2 |

---

## What is actually right (stated first, because it is unusual)

The arithmetic is clean and I could not break it. `0.1923 W` mean, between-capture
SD `0.0008 W`, max `6.74–7.47 W` reproduce exactly from
`docs/process_traces/2026-08-04-t3-char-pair/ANALYSIS-APPUP-R01R02.md`. The
screensaver figure (`43/50` bundles, `~+30%` energy) reproduces from
`RUN_STATE.md:2118-2119` and `PROJECT_STATUS.md:376`. `5 J / 93 s = 0.054 W` and
`0.1923 W × 93 s ≈ 18 J` are both correct. The proposal correctly refuses to use
the n=2 permanently-non-claim captures as claim evidence, correctly says no wall
meter is needed, and correctly declines to divert the D-117 windows. The
guard-confusion-matrix idea (contribution 3) is the one genuinely novel item in
the document.

That is the whole of the good news. The design does not survive contact with the
project's own rules.

---

## Fatal flaws

### FF1 — The window as specified cannot produce a claim-bearing result. Its own project would refuse it.

The design is 12 Williams-balanced epochs, 3 per state, 2 members per epoch:
**6 LLM observations per cell, and at most 3 paired contrasts per state-pair.**

`docs/paper/draft-v1.md:78`, the project's own floor rule:

> "fewer than five valid bundles or blocks are treated only as development
> evidence, not as a claim gate."

Three blocks is below five. The comparative side of every state contrast — the
side that carries the entire thesis — is *development evidence by the paper's own
§4*. The absolute side (n=6) clears the threshold by one and still eats the
pre-registered small-sample guard factor. Compare the ratified standard: D-117
alpha/beta/gamma each run **10 absolute + 10 ABBA blocks**
(`DESIGN-MEMO.md:246-263`). To reach that standard across four states you need
4 × (10 + 40) = 200 members, i.e. **four-plus windows, not one**. The proposal's
"approximately 3.4 h" is understated by roughly 4×.

This is not a tuning quibble. The proposal asks Ed to spend a night on a design
that his own §4 will classify as non-claim-bearing before the data is reduced.

### FF2 — There is no floor for the condition family this paper needs, and the proposal never notices.

The `~5 J` bar the whole Experiment Plan is sized against is the **phase-contrast**
effective bar, `F_cell + B_claim`, for `phase_energy_j.decode` on the 1.5B stack
(`draft-v1.md:109-115`). An environment-state contrast on gross member energy is a
**different condition family**. The project's rule is explicit and repeated:

- `draft-v1.md:60` — a floor governs "the same telemetry backend, metric, window
  type, workload profile, and stack identity. One such family forms a measurement cell."
- `DESIGN-MEMO.md:366` — "Never sum components and **never borrow a decode floor
  for prefill**." If a decode floor cannot transport to prefill on the *same
  members*, it certainly cannot transport to a new environment-state estimand.

So the contamination cells need their own minted absolute and comparative floors —
which requires null-ABBA members for an `env_state_contrast` family that appear
**nowhere in the proposed member list**. The list carries 12 NEG-8 bound members
(the bracket-drift corpus, not a floor) and 7 references. Either the headline
result has no decision bar at all, or a second window's worth of floor members
must be funded. This is the single largest cost omission in the document and it is
completely silent.

### FF3 — This is not an operator-bookend window. It needs Ed awake, or an unbuilt controller plus a rule waiver.

Twelve within-window state transitions, three of them into cell A (**app DOWN**).
The repo's own protocol for that exact transition
(`2026-08-04-t3-char-pair/PROTOCOL.md`, §Design):

> "Arm B (app-DOWN), collected **with Ed present** ... Arm B is deliberately NOT
> collected unattended tonight: quitting t3 would kill Ed's own observation
> threads, and the app-death-recovery acceptance gate wants Ed present for the
> quit/relaunch."

Cells C and D are worse. C requires *starting an agent session inside a
measurement window*; the repo's binding rule (`CLAUDE.md`, enforcement boundaries)
reads "Never start or continue a `[QUIET-MAC]` measurement while an agent session
is active." Treating the agent as a deliberate treatment is scientifically
defensible, but relaxing that boundary is a ratification act, not a design choice
— and under CLAUDE.local.md rule 11 the lieutenant is forbidden to self-exempt
from a mandatory trigger. The proposal's one-line "detached state controller" is
QUIET-GUARD-01 (still unbuilt, named as unbuilt in the very PROTOCOL it cites,
limitation 1) plus a detached agent-session launcher plus 12 supervised process
transitions with identity custody. None of it is costed.

Add the settle time the proposal omits: the project's convention is a 180 s settle
after operator/stage activity (`draft-v1.md:151`, `DESIGN-MEMO.md:309`). Twelve
transitions × 3 min = **36 min** that does not appear in the 3.4 h figure. With
FF1's member count and FF2's floor members, the honest number is 3–4 nights.

### FF4 — The novelty is folklore that the literature already formalized.

"Background software corrupts measurements" is not an open question; it is the
premise of every energy-benchmarking standard and the subject of an active
methodology literature. Standard controls are documented and in use: freeze all
non-essential cgroups so only workload and sampler run; subtract idle energy;
randomize/shuffle run order against unnoticed background processes; CPU warm-up
against thermal confounders. Recent work does exactly the framework version of
this ([METRION: A Framework for Accurate Software Energy
Measurement](https://arxiv.org/html/2512.06806); [Measuring Software Performance
on Linux](https://arxiv.org/pdf/1811.01412)), and there is already a paper whose
entire subject is the energy cost of a background feature ([Toward Greener
Background Processes](https://arxiv.org/pdf/2509.11738)). MLPerf Power/SPEC make
environment control an *admission condition*; JouleWise's own `draft-v1.md:125`
already encodes it as an admission gate.

What is left after prior art is: *a macOS-specific numeric budget for one laptop
with one app resident*. That is a paragraph, honestly. Formalization earns
publication only when it changes practice — and the proposal's own contribution 4
anticipates the likely landing as "retain zero-agent operation with a measured
reason," i.e. **no practice change**.

### FF5 — The expected result is "the obvious things are big, the interesting thing is unresolved."

Sort the four cells by (decision relevance × uncertainty):

- **B (dormant app delta)** — the only cell whose answer is both unknown and
  decision-relevant. The proposal itself says its increment over app-down "is
  unknown and may not clear 5 J." Most likely outcome: *unresolved*.
- **C (idle agent)** — largely known already. D-099 puts an idle-waiting session
  at 12–18% CPU of agent load; the banked analysis (`ANALYSIS-APPUP-R01R02.md:49-52`)
  already calls active streaming "two orders of magnitude over the effective bar."
- **D (transcript replay)** — the proposal predicts order-one watts, i.e.
  hundreds of joules. Nobody doubts this. Worse, D is a **proxy**: frozen-rate
  transcript replay is not an agent, so the paper's "background software"
  characterization for the agent regime rests on a simulacrum.

So the modal paper is: two cells confirm the obvious at 100× the bar, one cell
returns "not resolvable," one cell measures a stand-in. The proposal is admirably
honest that "unresolved is a valid outcome" — but you cannot *build* a paper on the
likelihood that its central quantity is unresolvable.

## Non-fatal but worth recording

- **Existing-material compliance is thin on registration.** `docs/research_question_registry.md`
  has no background-contamination RQ; its "contamination" rows (C5-2.5d) are
  *dataset* contamination. The nearest environment RQ is `RQ-POWER-MODE`, banked,
  "analysis-plan-only." D-117 is adopted; this is not registered anywhere.
- **Minor misreport:** proposal says p95 "approximately 0.46–0.48 W"; banked values
  are 0.463 / 0.484 W. Rounding down the top edge in a paper about tails is a bad habit.
- **Roadmap collision.** `docs/strategy/2026-08-06-impressiveness-roadmap.md` ranks
  nine expansions. This direction is not among them, and rank 1 is an explicit
  instruction to "prohibit breadth work from consuming" the core nights.
- **Venue arithmetic.** CSCSU is **5 pages including references**. There is no
  world in which the MVP method + D-117 results + a four-state contamination study
  fit in five pages. The proposal's "capstone paper/chapter" glosses this.

---

## Three strengthening moves

1. **Make it desk work, not a night — and the corpus is already being collected.**
   Every D-117 member carries its own idle capture (lifecycle stage 4,
   `raw/powermetrics_idle.plist` + `rich_telemetry_idle.jsonl`). Three windows
   × 203 captures gives an in-custody, claim-adjacent idle corpus for free.
   Compute the empirical distribution of *asymmetric burst energy* over real
   93 s member durations and publish `P(asymmetric burst > 1 J)` and `P(> 5 J)`,
   plus the same statistic recomputed on the banked n=2 app-up pair as an
   out-of-family cross-check. Zero new nights, zero new floors, zero rule waivers,
   and it is the paper's actual contribution — the burst-asymmetry budget — rather
   than its ceremony.

2. **If a window is funded, fund exactly two states at the ratified standard.**
   A (app-down) vs B (app-up dormant), 10 absolute + 10 ABBA blocks, with a
   pre-registered `env_state_contrast` condition family carrying its own null
   members and its own minted floor. One question, properly powered, with a real
   decision bar. Drop C (answer already known) and D (a proxy) entirely — they buy
   nothing and they are what force the agent-session rule waiver and the
   detached-controller program.

3. **Reframe the headline onto contribution 3, which is the only novel item.**
   Not "background software contaminates measurements" (settled) but *"how good is
   an admission gate?"* — false-accept and false-refuse rates of JouleWise's §5
   quiet-state guard against prospectively labelled environment states. That is an
   instrument-validation result about the project's own machinery, no prior work
   reports it, it is cheap, and a false-accept above the bar would be a genuinely
   publishable negative finding about §5 rather than a restatement of the field's
   standing assumption.

---

Sources: [METRION: A Framework for Accurate Software Energy Measurement](https://arxiv.org/html/2512.06806) · [Toward Greener Background Processes — Measuring Energy Cost of Autosave Feature](https://arxiv.org/pdf/2509.11738) · [Measuring Software Performance on Linux](https://arxiv.org/pdf/1811.01412)
