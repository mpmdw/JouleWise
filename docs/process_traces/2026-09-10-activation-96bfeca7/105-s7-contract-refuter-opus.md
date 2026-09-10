# 105 — Seat S7 CONTRACT-LENS refuter (Opus), read-only

Worktree `/Users/edr/code/JouleWise-wt-s7-night-wrapper`, scope
`git diff aea38b1a 94e4fc89`. No file edits, no git state changes, no mutation
cuts, no writes outside `/tmp/s7-refuter-check`. Every file:line below was
re-read in this worktree at this HEAD.

**Contamination note.** While I worked, the execution refuter's live cut
`exec` → `source` was present in the tree
(`git diff scripts/gen_derivation_night.py` = 1 line, `:245`). My first
`gen_derivation_night.py --check` therefore printed FAIL; I re-ran the check
against the **committed** bytes in a temp tree
(`/tmp/s7-refuter-check`, HEAD copies of the generator, the chain and the
runsheet, `joulewise` symlinked) and it prints
`PASS generated derivation-night wrapper region matches`, rc 0. The seat's
`--check` claim stands; the FAIL was the other refuter's mutation.

## VERDICT: MERGEABLE AFTER FIXES

Two blockers, both cheap and both inside the seat's existing design; four
should-fixes; the code as landed is sound in shape, refuses in the right
places, and its 12-cut kill table is honest. Nothing here is a redesign.

---

## Clause table

Authority → clause → code site (✓ satisfied / MISSING / DIVERGENT).

| # | Clause (authority, quoted) | Site | Status |
|---|---|---|---|
| 1 | Plan is an exact v2 plan; key set closed (`joulewise/night_gate.py:111-127` `_PLAN_KEYS`) | `gen_derivation_night.py:293` `NightPlan.from_mapping(raw)` | ✓ validated through the driver's own parser; no invented field names |
| 2 | A derivation night is `DIAGNOSTIC_NO_PACK`, not `TRANSACTION_PACK` (prereg `:115` "DIAGNOSTIC_NO_PACK class") | `:296-299` | ✓ refuses pack plans. Nit N-1: `REHEARSAL_STUB` is *accepted*, and for a rehearsal the driver never runs the chain (`run_night.py:1573-1575` `chain_path = /dev/null`) — emitting is harmless but silently pointless |
| 3 | The plan pins the artifact the driver launches: `chain_path` (`run_night.py:1577`, `night_gate.py:1057`) | `:320-325` `--out` must equal `plan.chain_path` | ✓ (D7) |
| 4 | Launch digest: sidecar must be strict `shasum` form, 1–2 tokens, hex64, token 2 = `chain_path.name` (`run_night.py:95-105`; gate `night_gate.py:1076-1091`) | `_sidecar_text :252-255`, `emit :266-268` (`out_path.name`) | ✓ exact form; verified against both readers |
| 5 | `chain_sha256_path` is the sidecar of `chain_path` | `:326-331` requires `chain_path + ".sha256"` | ✓ stricter than the driver (which accepts any path). Acceptable: it refuses rather than mis-writes |
| 6 | Dead-man: `t0 + window_max_s + 300 < next local 07:00` (`run_night.py:945-955`, `:958-959`, `:1464-1465` refuses on `>=`) | `_next_deadman_epoch :93-102`, check `:311-318` (`not completion < deadman`) | ✓ boundary-identical to the driver, same local-time base, same `COURIER_DEADLINE_S = 300` (`run_night.py:51`) |
| 7 | Agent census `pgrep -lf "codex\|claude\|t3"` every 30 s aborts the night (`night_gate.py:42` `AGENT_CENSUS_ARGV`; driver `night_aborted_agent_present`) | `_census_clean :82-91`, applied to plan id, window id, session id, evidence root id, frozen plan id and **every** absolute path via `_require_absolute :278-281` | ✓ complete over the emitted literals (D8); case-folded, so stricter than the case-sensitive `pgrep` |
| 8 | Pre-registration: 12 declared slots per night ("12 slots at a 600 s start-to-start cadence", prereg `:116-117`) | `:302-306` refuses any other count | ✓ with an explicit `--allow-slot-count` escape (nit N-2: the escape is unrecorded and has no counterpart window check — see B-2) |
| 9 | Pre-registration: one 600 s settle, 600 s cadence, ~8 min capture (prereg `:95-96`, `:116-117`) | `DEFAULT_SETTLE_S/CADENCE/BUDGET :63-65`, exported as literals `:158-160` | ✓ pinned rather than inherited (D5); correctly motivated by `run_night.py:426` `os.environ.copy()` |
| 10 | Pre-registration: "The schedule fits a 210 min window with margin: one 600 s settle + 11 × 600 s cadence + one ~8 min capture is **128 min**" (prereg `:94-96`); "All three nights run all 12 declared slots regardless of interim values" (prereg `:145`) | — | **MISSING** — no check that `window_max_s` can hold the programmed span. See **B-2** |
| 11 | Pre-registration binds ONE chain digest for all three nights: "Three agent-free [QUIET-MAC] windows on distinct calendar days, DIAGNOSTIC_NO_PACK class, **chain digest [CHAIN_SHA256]**" (prereg `:115-116`; identical clause in cold-gate 46 `10-coldgate-fable-ruling.md:59`) | wrapper `:238-240` checks a sidecar **path**; `WrapperSpec.chain_sha256 :131` is computed at `:383` and **never rendered** | **DIVERGENT** — see **B-1** |
| 12 | The wrapper supplies the chain's 13 `:?required` variables (`calibration_derivation_only.zsh:49-61`) | `render_wrapper :143-155` | ✓ all thirteen, in the chain's declaration order, names exact |
| 13 | Per-slot bindings: repeated `--slot-attempt-id` / `--slot-custody-locator`, count must equal `--slot-count` or `declared_slot_flag_count_mismatch` (`reserve_calibration_window_bracket.py:99-110`, `:173-186`) | `:164-171`, 12 + 12 flags, `SLOT_COUNT` exported from the same integer | ✓ single source of truth (scout Q4 closed) |
| 14 | The chain must run as `$0` at its in-clone path (`calibration_derivation_only.zsh:46-47` `cd "${0:A:h:h:h}"`) | `exec /bin/zsh "$REPO/<relpath>"` `:245` | ✓ `exec`, not `source` — correct, and the concurrent execution cut confirms a test kills the inversion |
| 15 | Routing preamble parity with reviewed G2-a source (runsheet "Emitted routing and common variables") | `:186-213` | ✓ plus three literal-equality refusals (D6) that G2-a does not have — a strict improvement |
| 16 | Desk-produced inputs are authenticated before window time is spent (G2-a source `gen_g2_phase_d.py:247-252`) | `:222-233` — `PLAN` id **and** digest re-derived and compared; `IDENTITY_EPOCH_JSON` / `T1_BINDINGS_JSON` only `test -f` | **PARTIAL** — see **S-1** |
| 17 | `WINDOW_END_EPOCH_S` is the exclusive window end the chain enforces (`calibration_derivation_only.zsh:43`, `:178`, `:190`); runbook draft §1.2 "`WINDOW_END_EPOCH_S = t0 + WINDOW_MAX_S`" | `:310` `int(plan.t0_epoch_s + plan.window_max_s)`, exported as an integer string (chain's `<->` guard `:75-81`) | ✓ matches the runbook draft's derivation exactly, including the integer form |
| 18 | Install window 03:00–06:30, fixed fences, NIGHT_HANDBACK email-then-arm (runbook draft §1.3, `:725`) | — | Out of the generator's scope by construction; but the **arm order** it implies is unstated anywhere in this diff — see **S-4** |

---

## Answers to the five questions

### (1) Does the attestation chain satisfy "reviewed chain"? — NO, one link short (B-1)

Claimed chain: plan pins wrapper digest → wrapper pins chain digest → exec.
Actual chain: plan pins wrapper digest → wrapper names a **file path** →
that file (`<night_root>/chain.zsh.chain-source.sha256`) holds the digest, and
**nothing pins that file**. I verified this by rendering:

```
chain digest = d6d23bff48d410144e74c19307dde79aebdd3a4fbf6e8eea97f34217ef470a65
digest in wrapper: False
wrapper unchanged when chain digest changes: True
```

(`python3 -c "import gen_derivation_night as m; …m.render_wrapper(…)"`, HEAD
bytes.) `WrapperSpec.chain_sha256` (`:131`) is computed at `:383` and consumed
only by the runsheet prose at `:452`. The wrapper is byte-identical for two
different capturing chains, so the plan-pinned digest does **not** move when the
capturing bytes move — which is exactly what the wrapper's own comment asserts
it does:

> `# The plan pins THIS wrapper's digest; the wrapper pins the capturing`
> `# chain's, so the plan-pinned digest transitively covers the bytes that`
> `# actually capture.` — `gen_derivation_night.py:235-237`, rendered into
> every night's artifact

That comment is false as written. Residual real protection is genuine but
narrower than claimed: a **committed** chain change moves `HEAD`, which the
wrapper refuses (`:205-208`) and the gate refuses (`night_gate.py:1019-1026`);
an **uncommitted** chain edit is caught by the sidecar *provided the sidecar was
not rewritten*. But `emit :269-274` rewrites that sidecar on every emission, so
"edit the chain, re-emit" produces an identical wrapper, an identical plan-pinned
digest, and no signal anywhere that the capturing bytes changed.

The pre-registration makes this decisive rather than cosmetic: it reserves ONE
blank, `chain digest [CHAIN_SHA256]`, for all three nights (prereg `:115-116`).
Per-night wrapper digests cannot fill a single blank (three nights = three
session ids, three t0s, three wrappers). The only digest that can fill it is the
tracked chain's — the one digest the night never attests.

**Fix (≤3 lines, no redesign):** render `spec.chain_sha256` as a literal and
compare it in-wrapper, e.g.
`expected_chain_sha256='<hex>'` +
`observed="$(/usr/bin/shasum -a 256 "$REPO/<relpath>" | /usr/bin/awk '{print $1}')"` +
equality → `route_refuse`. Then the wrapper's bytes move whenever the chain
moves, the plan-pinned digest genuinely covers the capturing bytes, the runsheet
example changes visibly under `--check`, and `[CHAIN_SHA256]` has one stable
value to be filled with. Keep the sidecar too if you like; it is then redundant
rather than load-bearing. A cut deleting the literal must kill a test.

### (2) Semantics of the 13 exports against their consumers — one gap, one question closed

| Variable | Consumer, verified | Verdict |
|---|---|---|
| `WINDOW_END_EPOCH_S` | `calibration_derivation_only.zsh:178` and `:190` (`slot_start + BUDGET > WINDOW_END` → `slot_unused` + `abort_window_exhausted`) | Correct: absolute, exclusive, integer. Matches runbook draft §1.2 |
| `RUNS_ROOT` | chain `:88` mkdir, `:204` `--output-root "$RUNS_ROOT/instrument_validation"`; writer requires the basename `instrument_validation` (`validate_powermetrics_fiducial.py:919`) and requires its parent to exist (`:931-932`, `resolve(strict=True)`) | Correct; default `<custody_root>/runs` is G2-a parity |
| `WINDOW_CUSTODY_ROOT` | chain `:87` `operator_logs` only | Correct |
| `EVIDENCE_ROOT_ID` | `reserve_calibration_window_bracket.py:81` `required=True`, passed into `validate_bracket_session_reservation_inputs` | Value is not derivable; required flag is the right call (see Q5) |
| `IDENTITY_EPOCH_JSON`, `T1_BINDINGS_JSON` | `reserve_calibration_window_bracket.py:110-111` (required), `:200-201` read, `:216-220` the **file contents are copied verbatim into every slot record** | **Not produced at t0 — and correctly so**, see below. But their digests are unpinned: **S-1** |

**No variable the wrapper fixes at arm time is one a consumer expects to be
produced at t0.** I checked the runbook writer's gap directly: the T1 vector is
`T1_FIELDS = V2_BINDING_FIELDS` = `{hardware_model, os_build, powermetrics_sha256,
sampling_interval_ms, anchor_method_version, mlx_version, pulse_protocol_id,
power_policy, estimator_revision, protocol_sha256}`
(`joulewise/powermetrics_fiducial.py:106-120`) and the epoch is the six-field
`IDENTITY_EPOCH_FIELDS` (`joulewise/calibration_ledger.py:110-117`). Every field
is stable machine/tool identity; none is a t0 measurement. Arm-time production is
therefore semantically right. The live risk is **drift, not timing**: the writer
compares its measured bindings against the reserved slot's
(`calibration_ledger.py:1688`), so an OS or `powermetrics` change between arm and
t0 — precisely the 25G83 episode — refuses at slot `d01` and burns the night.
That belongs in the arm checklist as a re-derive-at-arm step, not as a code
change.

**Scout Q5 / seat open item 5 is now CLOSED (verified, not asserted):** the
writer computes `validation_id = args.attempt_id if bracket_mode else <timestamp-uuid>`
and `out_dir = args.output_root / validation_id`
(`validate_powermetrics_fiducial.py:1996-2001`); `--derivation-only` requires
`--session-id/--slot/--attempt-id`, i.e. `bracket_mode`
(`:1944-1955`). So artifacts land at
`$RUNS_ROOT/instrument_validation/${SESSION_ID}-dNN` — byte-identical to the
custody locator the wrapper declares (`gen_derivation_night.py:167`) and to the
G2-a t0 step's construction (`capture_t0_step.py:534-544`). No mid-night
mismatch.

### (3) First-use test on `--help`, docstring, header comments, region — PASS with one defect

A next-activation operator can replicate the arm from the region alone: it gives
the exact command with every required flag, a fully rendered example wrapper, the
`zsh -n` verification step, and the live chain digest. The module docstring
builds its forcing problem (four driver variables vs thirteen chain variables)
before using "wrapper", and explains `exec`-not-`source` with the reason. The
chain header now reads as landed surface. This is above the bar.

The defect is factual, not pedagogical: **every file:line citation the generator
makes into the chain is stale by the +6 lines its own header edit introduced**
(**S-2**), and three of them are baked into every night's artifact.

### (4) Scope and rule 11 — clean; the `argv=` keyword is acceptable

Footprint is exactly the five WRITE_SCOPE files. No ruled rule is amended: the
chain header's "whether the pinned night chain is generated from a runbook
section instead is the lead's call at the integration replay" was an open
question *about this seat's own deliverable*, and recording its outcome is
in scope. D2 (region in the runsheet, appended at EOF) is the right call and I
confirmed it costs nothing: `gen_g2_phase_d.py --check` still prints PASS at
HEAD.

`run_chain(argv=…)` (`tests/test_issue_calibration_acceptance_generation.py:352,395`)
is **acceptable**: additive keyword, `None` default, every pre-existing call site
unchanged, 91 tests still green, and cut #11 proves the new test kills the
deletion of `"$@"`. Duplicating a 40-line harness to avoid one keyword would be
the worse outcome. Flagging it rather than assuming was right.

One deletion deserves a note, not a finding: the header's
"Confirm with S1 before the integration replay" about the absent
`--arm-countdown-s` / `--sleep-display-before-capture` was replaced with "the
writer requires neither". Verified: both are optional
(`validate_powermetrics_fiducial.py:1700`, `:1706`), so the claim is true.

### (5) The three open items — governing contract and required checklist text

1. **Identity-epoch / T1-bindings provenance.** Governing contract:
   `reserve_calibration_window_bracket.py:110-111,200-220` (required inputs whose
   contents enter every slot record) and the existing G2-a custody mechanism
   `generate_g2a_probe_inputs.py bind-window`, which records
   `{"identity_epoch": {"path", "sha256"}, "t1_bindings": {"path", "sha256"}}`
   (`:971-972`) and replays them under `check` (`:1226-1232`). The checklist must
   say: *produce both from the measurement clone at arm time, record path AND
   sha256 in the night's arm record, and re-derive them if any of `os_build`,
   `powermetrics_sha256`, `mlx_version`, `estimator_revision` or `protocol_sha256`
   changed since the last night — a drift between arm and t0 refuses at d01 and
   costs the whole night.*
2. **Clean tree.** Governing contract: `night_gate.py:1006-1029` binds `HEAD`
   only; nothing excludes uncommitted edits. The wrapper's `shasum -c` closes it
   for the capturing chain alone (and only as far as B-1 allows);
   `recover_calibration_ledger.py`, `reserve_calibration_window_bracket.py` and
   `validate_powermetrics_fiducial.py` remain bound by `HEAD` only. Checklist:
   *run `git -C <CLONE> status --porcelain` and record it verbatim in the arm
   record; a non-empty result stands the night down.*
3. **`EVIDENCE_ROOT_ID`.** Governing contract:
   `reserve_calibration_window_bracket.py:81` `required=True`; there is no
   derivable default and the seat was right not to invent one. Checklist: *state
   the literal value and the record that registers it, alongside `SESSION_ID`,
   in the arm record before emitting.*

Also for the checklist: **one wrapper per night** (D6 is right — three nights,
three plans, three wrappers) and the **arm order**, which no document currently
states: author the night plan → emit the wrapper with the generator → `zsh -n`
the emitted file → verify the emitted sidecar equals `plan.chain_sha256_path` →
install. The plan must exist first (the generator reads `t0`, `window_max_s`,
`custody_root`, `chain_path` from it); the wrapper must exist before the gate
runs (it reads `chain_path`).

---

## Findings, severity-tiered

### BLOCKER

**B-1 — The wrapper does not carry the chain digest, and asserts that it does.**
`gen_derivation_night.py:131,383` (computed, unrendered), `:235-240` (the false
comment and the path-only check). Authority: prereg `:115-116` "chain digest
[CHAIN_SHA256]" — one digest, three nights; cold-gate 46 `10-coldgate-fable-ruling.md:59`
identical. Evidence: rendered wrapper is byte-identical when the chain digest
changes (reproduced above). Fix: bake the literal digest and compare in-wrapper;
delete or correct the comment; add a cut that kills the missing literal.

**B-2 — No refusal when `window_max_s` cannot hold the programmed span.**
`gen_derivation_night.py:301-318` checks the slot count and the dead-man but
never checks that the window fits `settle + (N-1)·cadence + budget`. Executed
evidence (temp tree, HEAD bytes, `/tmp/s7-refuter-check`): a `DIAGNOSTIC_NO_PACK`
plan with `window_max_s = 3600` emitted a 12-slot wrapper, rc 0,
`WINDOW_END_EPOCH_S='1789120800'`, `SLOT_COUNT='12'`. That night would open the
session, settle 600 s, run ~5 slots and hit `abort_window_exhausted`
(`calibration_derivation_only.zsh:178-182`) — a partial night out of the three
the corpus has. Authority: prereg `:94-96` ("programmed span … 128 min", 210 min
window) and `:145` ("All three nights run all 12 declared slots regardless of
interim values"); runbook draft §1.2 derives `WINDOW_MAX_S = 7680 + 1320 = 9000`.
This is a pre-registration-fidelity fence, the class D-161 keeps fail-closed.
Fix: refuse unless
`window_max_s >= settle_s + (slot_count - 1) * slot_cadence_s + slot_capture_budget_s`,
report both numbers in the refusal, and make `--allow-slot-count` recompute rather
than bypass it.

### SHOULD-FIX

**S-1 — `IDENTITY_EPOCH_JSON` and `T1_BINDINGS_JSON` are presence-checked, not
digest-pinned,** `gen_derivation_night.py:223-224` — while `PLAN` next to them
gets both an id and a digest comparison (`:227-233`). Their bytes are copied
verbatim into every slot record (`reserve_calibration_window_bracket.py:216-220`),
and the neighbouring G2-a mechanism already pins path+sha256 for exactly these two
artifacts (`generate_g2a_probe_inputs.py:971-972`). Two literals and four lines of
zsh make the three desk-produced inputs uniformly attested. (G2-a source parity is
the counter-argument — `gen_g2_phase_d.py:247-249` also only `test -f`s them — so
this is a should-fix, not a blocker.)

**S-2 — Every chain citation in the generator is stale by +6 lines, including
three baked into each night's artifact.** The seat's own header edit moved the
chain's code down six lines; the citations were not re-derived:

| Cited | Claimed content | Actual line at this HEAD | What is really at the cited line |
|---|---|---|---|
| docstring `:17-18` → `zsh:40-41` | `cd "${0:A:h:h:h}"` | `:46-47` | a comment about display actions |
| `render_wrapper :142` → `zsh:43-55` | the 13 `:?required` | `:49-61` | `set -euo pipefail` / `cd` |
| `:60-62` → `zsh:60-65` | chain defaults | `:63-71` | `SLEEP`/`DATE`/`SLOT_COUNT` start at `:64` |
| **emitted wrapper** `:243-244` → `zsh:40-41`, `(:155)` | `cd`, `"$@"` | `:46-47`, `:161` | `:155` is `--plan-sha256 "$PLAN_SHA256" \` |

Verified by `grep -n 'cd "${0\|"\$@"'` at HEAD (46, 161) and at base (40, 155).
The chain header's own new citations are sound (reserve `:99-110`, `:173-186`;
writer `:1759-1762`, `:1772`, `:1944-1955` — the two that look off-by-one point at
the enclosing statement and are fine). Per the standing bench-verified-facts rule,
a header advertising "LANDED SURFACE, re-read at this HEAD" must not ship stale
anchors. Cheapest durable fix: cite symbol names, or add a test that resolves each
cited line.

**S-3 — The runbook draft's plan table is now wrong and must be amended before any
arm.** `99-derivation-night-runbook-draft.md:260` still says
`chain_path` = `<CLONE>/scripts/night_chains/calibration_derivation_only.zsh`.
Under this landing that plan would launch the tracked chain with none of its
thirteen variables — `exit 1` on the first `:?required` guard, a safely wasted
night. `chain_path` must be the emitted wrapper at the night root and
`chain_sha256_path` its `.sha256`, both enforced by the generator
(`:320-331`). The draft's `[UNVERIFIED]` at `:268-277` ("did not find the
production code that derives `WINDOW_END_EPOCH_S` … nor the code that supplies the
per-slot binding argv") **is closed by S7**, and the §1.2 arithmetic
(`WINDOW_END_EPOCH_S = t0 + WINDOW_MAX_S`, 9000 s, d12 admitted) matches
`gen_derivation_night.py:310` exactly — no arithmetic change needed. The
troubleshooting row at `:641` (exit 1 ⇒ ":?required guard") needs a second cause:
exit 1 is now also the wrapper's `route_refuse`, and a bare `test -f` failure at
`:222-224` exits 1 **silently**.

**S-4 — Nothing in the diff states the arm order or the emission's custody
side-effect.** `emit :269-274` writes a third file,
`<chain_path>.chain-source.sha256`, into the night custody root; no document
records that it exists, that the night refuses without it, or in what order the
plan and the wrapper are produced. One paragraph in the region (or the arm
checklist) closes it. (If B-1 is fixed by baking the digest, this file can simply
disappear.)

### NITS

- **N-1** `REHEARSAL_STUB` plans are accepted (`:296-299` refuses only pack);
  for a rehearsal the driver runs `sleep 2; echo REHEARSAL`
  (`run_night.py:1573-1575`), so the wrapper is never launched. Refuse, or say so.
- **N-2** `--allow-slot-count` (`:485`) bypasses the pre-registration fence with no
  recorded reason and no re-check of the window (see B-2).
- **N-3** `test -f "$PLAN"` / `"$IDENTITY_EPOCH_JSON"` / `"$T1_BINDINGS_JSON"`
  (`:222-224`) exit 1 under `set -e` with no message. This is G2-a parity
  (`gen_g2_phase_d.py:247-249`), so it is a nit, but the chain's own preflight
  prints `derivation_chain_input_missing: <path>` and exits 66
  (`calibration_derivation_only.zsh:119-125`); routing these three through
  `route_refuse` would make a 3 a.m. failure legible and would fix the ambiguity
  S-3 flags in the troubleshooting table.
- **N-4** `/usr/bin/jq`, `/usr/bin/shasum`, `/usr/bin/awk` all exist on this
  machine (checked); no finding, recorded so the next reviewer need not re-check.

## What I verified by execution

- `gen_derivation_night.py --check` at **HEAD bytes** in `/tmp/s7-refuter-check`:
  PASS, rc 0 (the in-tree FAIL is the concurrent refuter's `exec`→`source` cut).
- `gen_g2_phase_d.py --check`: PASS, rc 0. `zsh -n` on the chain: rc 0.
- Rendered the example wrapper from HEAD bytes; confirmed the chain digest is
  absent from it and that the rendered bytes are invariant under a chain-digest
  change.
- Emitted a wrapper from a synthetic `window_max_s = 3600` plan: accepted, rc 0.
- Line anchors at HEAD vs base for `cd "${0:A:h:h:h}"` (46 vs 40) and `"$@"`
  (161 vs 155).
- `validation_id`/`out_dir` derivation in the writer, closing scout Q5.

No file in any worktree was modified; the only writes were under
`/tmp/s7-refuter-check`.
