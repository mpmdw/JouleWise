# Synthesis 15 — cold gate QPE01-DAEMON-CONTAMINATION-01, round 1 (magistrate a022aecc, 2026-09-23 00:10 PDT)

Inputs, sealed by digest in `SEALED-SHA256SUMS.txt`: packet `00-PACKET.md` (sha `7083c815…`), Fable ruling `10-coldgate-fable-ruling.md`, Opus contract-lens refuter `11-opus-contract-refuter.md`, exhibits A–C. Every disposition below is the magistrate's adjudication of the two seats; the seats' findings are theirs.

## Where the seats agree (adopted as ruled)

- **Q1 (c):** the night is recorded as registered, carries the judge's verbatim label "MEASURED ON A NON-IDLE MACHINE …", is not used to size block two, and the pilot is re-run under registration v3. The stop-branch sentence and `clean_machine_busy_cores` are quoted only with that label and gloss.
- **Q2 (a) in shape, with the judge's corrections:** the per-envelope rule is an INTEGRAL — per non-observer process identity, Σ busy_cores × interval_s over the rows joined to the envelope ≥ 30 core-seconds (0.05 core × 600 s ≈ 7.5 J per interior at the measured 0.3125 W per busy core) → exclusion `non_observer_process_busy`; t0 and the arm `check` refuse at 0.5 busy cores for any single non-observer process over one 30 s observation, with the ruled detail text; abort after two consecutive exclusions. The lead's 0.10-core median is withdrawn (its own arithmetic admitted ≈ 15 J).
- **BLOCKER, both seats (verified at the bench by the magistrate, `01-…` record §6 and this synthesis):** no journal row ever written carries `observer: true` — `record_covariates` calls `sample_interval` without `observer_pid`, so only the recorder's own descendants would be marked and the power sampler (a sibling) reads 0.094–0.112 cores as a "non-observer" on both nights. Registration v3 must run the recorder with the chain root pid so collector, `sudo`, `powermetrics`, `top`, census and recorder are marked by ancestry; regression 0 proves it.
- **"Zero-capture class" REJECTED (both seats):** D-182 licenses a successor only when no capture writer ran. The judge's addendum text goes to Ed for ratification (below); until then the abort ends the span with no automatic successor.
- **Q3 (a):** the v3 rule may be run over the 2100 rows as a labelled diagnostic under an explicit observer basename set; the pilot is re-run once under v3.

## Where the refuter goes beyond the judge (magistrate's adjudication)

- **Refuter B2 — the observer-floor stop branch fires on every pilot by construction. VERIFIED and material; it changes the plan.** Exhibit D3: the clean 02:17 night stopped on `observer_floor_above_smallest_holdable_share` alone (0.05310 > 0.05), and tonight's floor is 0.05282. The floor is the collector's own CPU (self plus reaped children, including the power sampler) per envelope, ≈ 31.6 s per 600 s round; the excess over the registered 0.05-core share is 0.0028–0.0031 cores ≈ 0.42–0.47 J per 480 s interior — below the ≈ 1 J attribution limit. As written, the registered stop branch makes "no cutoff qualifies" the outcome of a clean pilot too, so "re-run once under v3" would stop on the same cause. This was not in the packet and the judge did not reach it; it is a registration design question (10a Q2 / ruling 46b) and goes to a BOUNDED ROUND 2 (charge 20) rather than being decided here.
- **Refuter M1 — the packet's "for v2 plans the legacy load-average predicate is not applied" is FALSE.** Exhibit D5: `evaluate_night` (t0) calls `_check_machine` with the default `legacy_load=True`, so LOAD_MAX 2.0 was enforced at t0 and passed at 1.03; the arm `check` (line 1530) is the path that omits it. The packet is corrected by this synthesis; the judge's rejection of option (c) stands on the number (1.03 < 2.0), unaffected.
- **Refuter M2 — missed option (c′) lower LOAD_MAX:** not adopted. The load average is a host-wide 1-minute mean that includes the observer and every burst; the ruled per-process predicate names the process and is sized to the block-two effect. Recorded as dissent-considered.
- **Refuter B3** = the judge's D-182 rejection; adopted as above.

## Actions registered

1. Lane **QPE01-NONOBSERVER-PREDICATE-01** (p1, blocks the next pilot): registration v3 with the ruled fields, observer marking by chain-root pid, per-envelope integral exclusion, t0 + `check` predicate, abort after two, seven regressions (ruling §5) — implemented under its own gate AFTER round 2 rules the observer-floor question, because v3 must carry both.
2. Bounded round 2 (charge `20-charge-observer-floor.md`): the observer-floor stop branch.
3. To Ed (email, ratification): the D-182 addendum text (ruling §3) and the owner hygiene items (restart `fseventsd`; consider disabling Photos analysis on the measurement Mac).
4. Harvest record §2 gains the ruled label verbatim (dated addendum, next bookkeeping commit).
