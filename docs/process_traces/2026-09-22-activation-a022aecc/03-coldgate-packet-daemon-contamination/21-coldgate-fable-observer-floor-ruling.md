# Ruling 21 — cold gate QPE01-DAEMON-CONTAMINATION-01, round 2 (Q4, observer-floor stop branch)

Cold Fable judge (claude-fable-5-1), single foreground session, 2026-09-23 00:15–00:22 PDT, worktree at `69315e79`. Disclosure: the harness auto-loaded `~/.claude/CLAUDE.md`, the project `CLAUDE.md` and the memory index `MEMORY.md`; none was used for the merits. Not opened: CLAUDE.local.md, RUN_STATE.md, TASK_QUEUE.md, memory files, council logs, run reports, other trace directories.

## 0. Trust anchors (before the merits)

| item | expected | observed | method |
|---|---|---|---|
| charter | `099de884…70ff…95d81` (out-of-packet) | `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` | `shasum -a 256`; validator receipt |
| charge 20 | `fbf4b9b9…10cb` | `fbf4b9b90f0662dc898d501aaca23be2854e8dd0fba23b3374c9ea54631210cb` | same |

Run 1 with the deliberately mistyped charter sha (`…a880ff…`): validator `REFUSE`, reason `charter_trusted_observed_mismatch`, rc 2. Run 2 with the true sha: `PASS`, rc 0, all eight manifest exhibits observed = expected; `SEALED-SHA256SUMS.txt` all OK. Judged on that basis.

## 1. Executed evidence (mine)

- D1 verbatim at `git show 258c90ed:joulewise/quiet_predicate_campaign.py` 925–940 and 1064–1073; HEAD is byte-identical for that file and the test module (`git diff --stat` empty). Comparison is a bare `observer_floor > smallest_share` (936), no tolerance.
- D2 verbatim from `258c90ed:configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v2.json`, sha `2c539240…79f1` = `night_gate.QPE01_PILOT_REGISTRATION_SHA256`. No `pilot_protocol_v3.json` exists at HEAD.
- D3 recomputed from both archive `summary.json` (sha `9121f080…`, `84bfcafb…` match C9): Σ observer_cpu_s / observer_support_s = 376.367/7088.11 = **0.053098** (clean 02:17) and 379.353/7181.62 = **0.052823** (2100); equal to the stored `observer_floor_cores`. Stop causes as stated (clean night: observer floor ONLY). Recorder share from the envelope rows 0.0073 (D4 says 0.0076 from journal rows; same thing to the precision that matters).
- **The rate.** `0.3125 W per busy core` does NOT appear in exhibit C8. C8 gives +0.3194 W (153.3338 J / 480 s, medians) and +0.3110 W (minimum envelope). 0.3125 = 150/480, the packet's rounded "150 J" (00-PACKET.md:19) carried in from ruling 10:47. It is a between-night energy difference attributed to `fseventsd` at 0.995–0.999 cores (C:208–209), i.e. a derived, E-core-class rate for one daemon; it is not a measurement of the observer processes. The pilot records no watts-per-core value (no such key in either summary; grep over all keys). Refuter M7 already noted envelope 1 implies ≈ 0.48 W/core.
- Sensitivity (my arithmetic, excess × W × 480 s): clean night 0.465 J at 0.3125, 0.475 J at 0.3194, 0.714 J at 0.48, **1.487 J at 1.0 W/core**; 2100 night 0.423 / 0.433 / 0.65 / 1.355 J. Synthetic floor 0.10: 7.50 J at 0.3125, 7.67 J at 0.3194. The constant decides the outcome anywhere in 0.67–1.0 W/core.
- One run of `tests.test_quiet_predicate_campaign`: 128 tests OK in 11.4 s. Existing test at line 286 asserts `observer_floor=.051` → "no cutoff qualifies"; under any tolerance form it must change (0.001 core ≈ 0.15 J).

## 2. Q4 — verdict

**AFFIRM the lead's disposition (a) in shape; REJECT two of its limbs; rule (a) as corrected below.**

Deciding evidence: D1:936 is a strict share comparison with no tolerance; my recomputed floors show a clean night fails it by 0.0031 cores, which at every rate the packet can support (0.31–0.48 W/core) is 0.42–0.71 J, below the ≈ 1 J boundary-attribution limit (B2b:218, D-078 cl.11) and below block two's own `sizing.delta_j` = 1. That is the microscopic-gate shape B2b forbids. (b) trades science for accounting, (c) tunes the instrument to a threshold, (d) removes a real guard, (e) is a foregone conclusion — I concur with the lead on all four.

Rejected limbs (MATERIAL): (1) "the measured 0.3125 W per busy core (exhibit C8)" — not in C8, not a measurement, not of the observer; (2) "the night's own measured rate (the pilot records it)" — the pilot records nothing of the kind at 258c90ed, so this source is empty and would make regression (iii) the live path on every night. Cure: a registered constant with its true lineage and a rate-independent ceiling, below.

**Registration v3 field text (exact, added to `block_two`):**
```
"observer_floor_tolerance": {
  "statistic": "observer_excess_j = max(0, observer_floor_cores - smallest_holdable_share) * observer_watts_per_core * interior_s",
  "bar_j": 1,
  "bar_basis": "sizing.delta_j = 1 J = boundary-attribution limit (D-078 cl.11; sensible gates B2b)",
  "observer_watts_per_core": 0.3194,
  "observer_watts_per_core_source": "registered constant: exhibit C8 at 258c90ed, (306.2873 - 152.9535) J / 480 s = 0.3194 W for fseventsd at 0.995-0.999 busy cores (E-core class); no pilot measures this rate; a night MUST refuse, never pass, if this field is absent",
  "share_ceiling": 0.10,
  "share_ceiling_basis": "2 x smallest_holdable_share; at 0.10 cores the excess is 7.67 J at the registered rate, above the 5 J claim bar at every rate >= 0.21 W/core, so the outcome no longer depends on the constant"
}
```
`stop_branches` keeps the key `observer_floor_above_smallest_holdable_share` → "no cutoff qualifies" (the cause name is unchanged so archived summaries stay comparable).

**Replacement for D1:936–937 (exact):**
```
    tol = protocol["block_two"].get("observer_floor_tolerance")
    if observer_floor is not None:
        if tol is None or type(tol.get("observer_watts_per_core")) not in (int, float):
            raise ValueError("observer-floor stop branch needs a registered observer_watts_per_core; absent evidence is never a pass")
        excess_j = max(0.0, observer_floor - smallest_share) * tol["observer_watts_per_core"] * protocol["interior_s"]
        if excess_j > tol["bar_j"] or observer_floor >= tol["share_ceiling"]:
            causes.append("observer_floor_above_smallest_holdable_share")
```
and the return dict gains `"observer_excess_j": excess_j` (None when no floor) and `"observer_watts_per_core_source": tol[...]`. The 1073 call site is unchanged; `pilot_summary` writes both new keys.

**The two bars, sized to the instrument:** bar 1, energy: fires when excess_j > 1 J = `sizing.delta_j`, the smallest difference the instrument attributes; the clean night sits at 0.475 J (47 % of it), the 2100 night at 0.433 J. Equivalent share at the registered rate: 1/(0.3194 × 480) = 0.0065 cores, so the branch fires at floor > 0.0565. Bar 2, share ceiling 0.10 cores: rate-independent; 0.05 × 0.3194 × 480 = 7.67 J > 5 J claim bar, and it holds down to 0.21 W/core, below any rate the packet or physics supports. Bar 2 exists because the constant is unmeasured (§1): a low registered constant cannot silence the guard against a grossly heavy observer.

**Regressions (each must FAIL at 258c90ed; site `stop_branch` via `pilot_summary` at 1073):**
- (i) Both archived summaries re-derived under a v3 protocol dict → cause ABSENT, `observer_excess_j` = 0.475 ± 0.01 and 0.433 ± 0.01. Fails today: D1 fires on 0.053098 > 0.05 and the key does not exist. Counterfactual input: the clean night's twelve `observer_cpu_s` rows (376.367 s over 7088.11 s).
- (ii) Synthetic floor 0.10 → cause PRESENT and `observer_excess_j` = 7.67 ± 0.01. Fails today only through the missing key (the bare comparison also fires at 0.10), so the joule assertion is what makes it defect-shaped. Counterfactual: floor 0.056 → ABSENT (0.92 J) and 0.057 → PRESENT (1.07 J), pinning bar 1's edge.
- (iii) Protocol dict without `observer_floor_tolerance`, or with a non-numeric `observer_watts_per_core`, and any floor → `ValueError`, never "no decision". Fails today (no error, silent fire).
- (iv) Sensitivity: same clean-night rows with `observer_watts_per_core` = 1.0 → PRESENT (1.487 J); at 0.48 → ABSENT (0.714 J). Records that the registered constant is decision-bearing and pre-registered. Fails today (key missing).
- (v) Ceiling: floor 0.10 with `observer_watts_per_core` = 0.01 (a bad constant) → PRESENT via bar 2. Fails today (key missing).
- Amend test line 286: `{"observer_floor": .051}` becomes `{"observer_floor": .10}`; add `.051` → "no decision" (0.15 J).

**Same v3 registration as round 1's fields:** AFFIRM. No v3 exists at HEAD, so this is one re-registration and one ruled digest, not an amendment of a registered document; the lane already waits on this round (synthesis 15, action 1). Pre-registration is preserved because the constant and both bars are fixed before the re-run captures data.

## 3. Findings

- **MATERIAL** — the load-bearing rate is mis-cited ("measured", "C8", 0.3125); the true C8 figure is 0.3194 W and it is a daemon-derived E-core-class rate. Verdict unaffected (0.475 J < 1 J) but the field text must carry the real lineage (cured above).
- **MATERIAL** — "the pilot records it" is false at 258c90ed; a source that never exists would route every night through the refusal path. Cured by the registered constant + bar 2.
- **MATERIAL** — regression (ii) as charged is not defect-shaped by itself (passes at 258c90ed); cured by asserting the joule field.
- **NIT** — D4 recorder share 0.0076 vs 0.0073 from envelope rows; D3's "31.6 s per 600 s" is 31.4–31.6 s per ≈ 590 s of support.
- **NIT** — refuter M7 (0.48 W/core from envelope 1) was not carried into the charge; regression (iv) covers it.

## 4. Packet hygiene

One defect: the charge presents a number as measured and cited to an exhibit that does not contain it (see §1, §3). Effect on Q4: none on the option ruled, material on the field text, cured here. Otherwise neutral: all five options stated, contrary evidence (refuter B2, M7) exhibited, executed evidence reproducible, question atomic. Round 1 is not reopened; the convening prompt's round-1 items (label text, abort count, t0 bar) are outside this charge and not re-ruled.

## 5. Probes

`/usr/bin/log` not needed; no `systemsetup`, `sudo`, `powermetrics`, `launchctl`; reads limited to the packet directory, the two archive roots and `git show`. One file written: this ruling.
