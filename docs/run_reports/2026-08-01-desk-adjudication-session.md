# 2026-08-01 — Desk session: machinery adjudication ruled (D-100), commit-3 pipeline, CI shard-budget fix

Session: 2026-08-01 daytime PT, Fable magistrate directing; three Sol
xhigh sessions, one cold-gate pair (fresh Fable + Opus refuter), all
delegated work consumed as final reports. Repo main `8129a2b` →
(this report's commit). Ed context recorded: project started ~3 weeks
ahead of its nominal schedule; horizon is December — timeline pressure
LOW.

## Outcome in one paragraph

The three-part machinery adjudication over the two FAILED-as-issued
metrology verdicts is COMPLETE: an independent read-only Sol xhigh audit
(magistrate bench-verified on every load-bearing claim) classified the
question groups — (a) CONTRACT GAP, (b) MACHINERY DEFECT with a CORRECT
retry rejection, (c) CORRECT for window B plus one latent fail-open —
and group (a) ran the full rule-11 cold gate, synthesized as **D-100**:
salvage-dangler exclusion under a mechanical measurand-existence
license, landed in the consumption-semantics-dispatch shape so the
original FAILED rows stand as issued by construction. Window A is
permanently non-claim-bearing (immutable T1-incompatible post-cal
retry); window B's re-evaluation is licensed behind the D-100 repair.
Three repair rows were queued, gauntlet commit 3 went from design
consult to implementation in one session, and a CI capsule shard-budget
failure introduced by the session's own queue rows was diagnosed and
fixed at the bench.

## 1. The adjudication (MET-VERDICT-ADJ-01 → completed)

Packet mechanically assembled (`.desk/adjudication_packet_20260801/`,
untracked custody copy; verdict rows + close-outs + question groups),
then an independent read-only Sol xhigh audit at `8129a2b`:

- **(a) Dangling quarantined-without-replacement — CONTRACT GAP.** The
  A-vs-B behavioral difference is accidental count-dependence: ONE
  failed invoked declaration (window A) is accepted without a presence
  check and excluded late by strict validation; TWO declarations
  (window B) route to the duplicate path, whose unsatisfiable
  requirements discard the ENTIRE candidate group — including B's
  valid, unrelated `mtnull-o0512-b04-b2` supersession. No contract
  defined the terminal semantic when D-087 salvage closure makes the
  §10 replacement impossible.
- **(b) Deviation post-cal — MACHINERY DEFECT, but the observed
  rejection was CORRECT.** Window A's retry calibration is standalone
  valid but binds `power_policy` to the policy file path where the
  window binds `ac_high_power` (collection-time invocation error,
  bench-verified); T1 exact stationarity makes it ineligible, and the
  empty-side selector nulls the valid pre too. **Window A can never
  form a bracket; its FAILED verdict is permanent.** The actual defect
  is adjacent: the selector hard-refuses above the obsolete 0.010
  policy value with no D-079 derived-screen/budget path — a NON-SALVAGE
  severity escalator (it is what failed old window B at 11.58 ms).
  Queued as `CAL-BRACKET-D079-01`.
- **(c) Window B membership — CORRECT.** All five conditions are pure
  cascade from the twice-declared dangler ("stale" is the contract's
  umbrella term for unresolved bindings, not an age claim; the
  in-window bound's horizon was intact). One latent fail-open (malformed
  supersession/manifest records silently skipped) queued as
  `MEMBERSHIP-READER-FAILOPEN-01`.

Magistrate bench verification confirmed: the power-policy mismatch, the
0.010 hard-cliff code path, the r08 double-declaration, and (later, for
the cold gate) the danglers' event sequences.

## 2. The cold gate (rule 11, full shape) → D-100

Convened on group (a) because one candidate semantic could license a
verdict re-evaluation (reversal territory) and because a contract rule
was being proposed — both mandatory triggers.

1. **Cold Fable ruling:** S2-A, admission-bounded terminal exclusion —
   fail-closed default everywhere; a salvage dangler is excludable only
   under mechanical conditions (D-087 closure binding, admission-class
   failures only, exhaustive evidence, cap of ONE, verdict-row payload).
2. **Bounded factual follow-up:** the magistrate's custody sweep (the
   ruling's own deferred condition 4) found both r08 attempts left
   quarantined idle-phase bundles — the drafted "zero bytes" license
   line was unsatisfiable for every real admission failure. The
   instance re-drew condition (b) on the merits to the
   **measurand-existence line** (b-i launcher refusal with zero bytes /
   b-ii pre-workload admission abort: no workload `stage_started`,
   `admitted: false`, zero measurand fields, phase-bounded telemetry;
   unclassifiable voids), added R5a/R5b, and put enforcement weight on
   the real-shape regression over prose.
3. **Independent Opus contract refutation (14 findings):** S1 dominated
   (a `flagged` shape gives identical claim outcomes without ratifying
   a permanently false custody condition); S2 unratifiable as written
   (a re-run verdict without a new pinned basis manufactures
   `whole_window_verdict_conflict`); use the ALREADY-RATIFIED
   `consumption_semantics_id` dispatch instead; closed-registry
   amendment required; identity-binding (all 8 window B manifests carry
   `analysis_manifest_id: null`) and ledger-honesty (strict_valid/clean
   rows for byteless bundles) defects; two factual challenges (R1, R2).
4. **Magistrate synthesis (D-100):** S2-A as redrawn, carried in the
   refuter's S3 semantics-dispatch shape (`salvage_dangler_exclusion_v1`,
   new pinned basis; original FAILED rows stand by construction).
   **R2 resolved against the refuter from primary evidence** — the
   danglers' event sequences terminate at `idle_baseline` with no
   `warmup`/`measured_run` stage; the suspicious ~97 s durations are the
   admission gate's two ~36 s baseline attempts. **R1 confirmed for the
   three `p2048-o0128` cells** (frozen `minimum_claim_n: 8`, 7 present —
   barred regardless; that shape re-collects) **and corrected in
   scope** (the other six additivity cells and both null rungs remain
   the live stake). Prospectivity decided explicitly; dissents recorded
   in the entry. Repair queued as `MET-DANGLER-DISPOSITION-01`;
   `MET-WINDOW-C-01` now depends on it.

Process note: the packet's explicitly-deferred residual (the custody
sweep) is what caught the cold ruling's disk-shape miscalibration — the
"defer, never assume" packet discipline earned its keep, and the
follow-up cost one 64-second resumed turn.

## 3. Gauntlet commit 3 (COOLDOWN-JOIN-GAUNTLET-01)

- **Design consult (Sol xhigh, read-only, D-097-mandated):** complete
  design delivered and magistrate-ratified — writer v2 outcome enum
  (required on `existing`, forbidden otherwise), per-snapshot
  writer-external attestation binding manifest raw bytes by SHA-256, a
  new shared `joulewise/campaign_provenance.py` authenticated-catalog
  module used by all six reader call sites, the D-094 v2 truth-table
  row, C3 authorship parity via the join-owned representative
  projection, and the real-manifest relabel probe. Both D-097 riders
  ruled: (i) classification is NOT consumed beyond authentication;
  (ii) the attestation is anti-malformation, distinct from the
  source-manifest-hash tamper layer. Two consult disagreements with the
  D-097 sketch accepted on the record (per-snapshot over terminal-only
  attestation; "authenticated" ≠ anti-tamper).
- **Implementation (Sol xhigh, workspace-write, 6-path WRITE_SCOPE):**
  running at report time on `impl/cooldown-gauntlet-c3` (worktree off
  `44f0744`); the directing subagent correctly held the gate commit for
  itself after a sandbox probe showed the linked gitdir non-writable —
  independently rediscovering the multi-stream-worktrees
  lead-commits-at-the-gate rule. Harvest chain on completion: lead
  verification (full suite + canonical mapping hashes 57/57
  `aa48a122…`, 47/47 `5005816a…`) → independent read-only delta audit →
  PR under the D-072 gate. MANIFEST-CONTRAST v3 stays sequential behind
  it (shared write surface, D-095).

## 4. CI failure: capsule shard budget (fixed at the bench)

All five of the session's pushes failed the release-chain job:
`pack_capsule.py: page exceeds 30000-byte runtime shard budget:
/roadmap.html`. Cause: the roadmap page rendered every queue row's FULL
combined Evidence/Acceptance cell, duplicating the Queue page inside a
worse-compressing layout; the session's four dense new rows pushed the
single-page shard over budget (31,052 → 32,904 bytes as rows landed).
Fix in `scripts/build_site.py`: roadmap cards now render the
acceptance-summary sentence with a link to the full row on the Queue
page (`roadmap_acceptance_summary()`), which matches the page's own
flight-plan framing. Verified in a scratch clone: capsule packs clean
(0.24 MiB content; advisory Lakebed estimate under cap), roadmap raw
103.7 → 67.2 kB. Tracked `docs/site/` was NOT regenerated (D-068); CI
rebuilds in its own snapshot. Full suite re-run at the head carrying
the fix.

## 5. Landed on main this session

| Commit | Content |
|---|---|
| `1ea651f` | D-098/D-099, council addendum III (knife-edge consult), kernel rows MET-VERDICT-ADJ-01 + MET-WINDOW-C-01 |
| `44f0744` | DRIFT 2026-08-01 refresh; PROJECT_STATUS plain-language metrology update |
| `1694eb9` | Repair rows CAL-BRACKET-D079-01, MEMBERSHIP-READER-FAILOPEN-01 |
| `209201c` | D-100 synthesis; MET-VERDICT-ADJ-01 retired to the completed table; MET-DANGLER-DISPOSITION-01 queued |
| `c7e9611` | CLAIMS_STATUS second refresh (post-D-100); RUN_STATE desk checkpoint |
| (this) | CI shard-budget fix + this report + sweep results |

## 6. Claim-state consequences (CLAIMS_STATUS is the ONE home; summary)

- Window A: permanently non-claim-bearing; C1 re-collects; the 40-run
  ramp survives as micro_delta DESIGN input + corroboration diagnostics.
- Window B: re-evaluation licensed behind the D-100 repair; if it
  passes, C2's two rungs and C4's two complete shapes become
  licensable; the `p2048-o0128` shape re-collects regardless.
- The deviation-retry procedure gains a fence candidate: retry
  invocations must pin byte-identical T1 binding arguments (the window
  A loss class); encode during MET-WINDOW-C prep.

## 7. Records

- Adjudication custody: `.desk/adjudication_packet_20260801/` (packet,
  audit, cold ruling + follow-up, refutation summary with bench checks)
  — untracked; retained on this machine.
- Decisions: D-098, D-099, D-100. Council: C-039 addendum III.
- Ed owes: network-time restore. Wall-meter purchase (D-092) open,
  non-blocking.

## 8. Runway continuation (2026-08-01 evening → 08-02): the commit-3 gauntlet arc

Appended during the Ed-authorized ~26 h autonomous runway. Full custody
in `.desk/coldgate_c3_structural/` and `.desk/coldgate_c3_round4/`.

- Composed commit `ddd7e5b` → delta audit FAIL (3 blockers) → fix round
  1 `690acd0` → fresh re-audit FAIL, same signature → **escalation
  trigger honored** → cold gate 1 → **D-103** (root cause in the design
  text: attest-after-publish ordering; WAL inversion ruled; cold
  instance OVERRULED on B2 with recorded dissent — the verdict path's
  pointwise byte-pinned dereference stands; two named aggregation
  policies; origin-binding registered as fallback).
- Fix round 2 `7e44c1b` → fresh re-audit: structural shapes PASS; three
  narrow new blockers → triage: trigger not fired (first-round fixes
  for round-2 adjacencies) → fix round 3 `48aeca3` → fresh re-audit: 2
  blockers remain (lock token unbound to root; torn-tail still
  enumeration-shaped) → **both rule-11 triggers hit → cold gate 2 →
  D-104** (CONVERGENT: both instances rejected both magistrate
  candidates; acquisition-identity lock tokens ruled; positive
  writer-grammar recognizer ruled; the refuter discovered the
  whitespace-preservation hole that survived four reviews; packet's
  B3/NUL precedent citation corrected on the record).
- Fix round 4 implemented D-104 (no NEEDS_RULING; the
  assert-without-acquire path resolved as non-minting, lead-verified);
  lead gate in progress at report time.
- Parallel landings: PR #92 MERGED (D-096 F2 --k hardening);
  related-work draft committed (Phase 2 complete); D-102 (CAL-BRACKET
  pins, all arithmetic lead-replayed; n=19 corpus reconstructed with
  member-level hashes); D-100 addendum (mechanical spellings +
  fail-open fold); D-100 repair design consult complete and
  implementation-ready.
- Process observations for the council log: FOUR directing-subagent
  stalls after background Sol runs (harvest-from-disk is now standing
  practice + memory); MCP 1800 s idle-timeout on xhigh rounds — use the
  audited CLI route for >30 min implementations; the "deferred
  residual" packet discipline (unswept evidence named, not assumed)
  caught a cold ruling's disk-shape miscalibration for the second time.
