# Scout 101 — how a night chain gets its environment, and the derivation-night seam

Read-only scout in `/Users/edr/code/JouleWise-wt-epoch-integration` (HEAD `aea38b1a`).
No edits, no git state changes, no captures. Rehearsal custody read only.

## 0. The headline

**There is no environment plumbing from a v2 plan to a chain, and there never was.**
The night driver hands the chain exactly four variables and no argv. Every other
variable a night chain uses is an `export` line **inside the chain file's own bytes**,
and the chain file's bytes are what the plan pins and the driver digests.

`scripts/run_night.py:430-444` is the whole of it:

```python
environment = os.environ.copy()
environment["NIGHT_PLAN_ID"]    = plan.plan_id
environment["MEASUREMENT_ROOT"] = plan.measurement_root
environment["MEASUREMENT_HEAD"] = plan.measurement_head
environment["PY"] = f"{plan.measurement_root}/.venv/bin/python"
process = subprocess.Popen(
    command if command is not None else ["/bin/zsh", str(chain_path)],
    stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
    env=environment, start_new_session=True)
```

Pinned by test at `tests/test_run_night.py:348-380`: the child env carries those four
keys overwritten from the plan (inherited stale values are replaced), and the argv is
asserted **exactly** `[["/bin/zsh", str(self.chain)]]` — no trailing arguments (`:358`,
`:373`).

Two consequences for the derivation chain:

1. Ten of its thirteen `:?required` variables have no supply line today. It would exit 1
   on the first guard (`scripts/night_chains/calibration_derivation_only.zsh:43`) before
   spending window time — safe, but a burned night.
2. Its per-slot bindings are `"$@"` (`:155`), and the driver passes no argv. Under the
   current driver, `"$@"` is empty, and `reserve_calibration_window_bracket.py` refuses a
   derivation session whose repeated `--slot-attempt-id` / `--slot-custody-locator` counts
   do not equal `--slot-count` (`scripts/reserve_calibration_window_bracket.py:172-186`,
   reason `declared_slot_flag_count_mismatch`). So the argv gap is a hard refusal, not a
   soft default.

This closes the `[UNVERIFIED]` block in
`/Users/edr/code/JouleWise-wt-bk-96bfeca7/docs/process_traces/2026-09-10-activation-96bfeca7/99-derivation-night-runbook-draft.md:268-281`.
The answer is: there is no such production code; the G2-a route does not need any,
because the chain carries its own environment.

## 1. The two launch routes, and which one a DIAGNOSTIC_NO_PACK night uses

### Route A — packless (`DIAGNOSTIC_NO_PACK`, `REHEARSAL_STUB`): what G2-a actually uses

`scripts/run_night.py:1576-1610`:

- `chain_path = Path(plan.chain_path)` (`:1577`)
- digest the file (`:1578`), read `plan.chain_sha256_path` (`:1579-1582`)
- `expected = _sidecar_digest(sidecar_text, chain_path.name)` — strict `shasum` form,
  1 or 2 whitespace tokens, `token[0]` a 64-hex digest, `token[1]` (if present) equal to
  the chain's **basename** (`scripts/run_night.py:95-105`)
- mismatch → refusal `chain_digest_mismatch` (`:1584-1607`)
- `command = ["/bin/zsh", str(chain_path)]` (`:1609`)

That is the entire attestation on this route: **plan-pinned path + GNU-format sidecar
digest of the exact bytes**, plus the gate's independent check that the measurement
checkout's git HEAD equals `plan.measurement_head`
(`joulewise/night_gate.py:1006-1029`) and `repo_head`.

`window.env`, `window-chain.zsh`, `launch-manifest.json`, `launch_window.py`,
`window_chain_sha256` and `_read_exact_launch_reference` are **not on this route at all**.

### Route B — `TRANSACTION_PACK`: the D-117 window chain (not what a derivation night is)

`scripts/run_night.py:1612-1620` replaces `command` with `_produce_pack_go(...)` →
`_pack_launcher_argv` (`:1256-1264`), an eight-flag `scripts/launch_window.py` call.
`launch_window.py:169-190` reads `window_root/window.env` and `window_root/window-chain.zsh`
for hashing only, and `os.execve(argv[0], argv, dict(os.environ))` at `:264` execs
`manifest["launch_command"]` — the reviewed
`/usr/bin/caffeinate -is /bin/zsh …/window-chain.zsh "$WINDOW_PLAN_ROOT"` argv
(`docs/phase_2/window_runbook.md:1731`). There the chain gets its environment by
`source "$WINDOW_PLAN_ROOT/window.env"` (runbook `:1477`), an **exact 25-key** file
(`joulewise/arm_readiness_evidence_t0.py:63-91`, parser `:767-803`) whose values are
cross-checked against the arm context at `:865-884`, plus two paths (`ARM_RECEIPT`,
`LAUNCH_MANIFEST`) exported by the operator before E-10 and crossing `execve`
(runbook `:1440-1442`, `:1478-1479`).

The pack-only bindings the brief asked about:
- `plan["chain_path"]` equality against the attested chain reference:
  `joulewise/arm_readiness.py:10051-10052` (inside `_admit_pack_launch_go`), and
  `scripts/run_night.py:1168-1169` (`refs["window_chain"]["path"] != plan.chain_path`).
- `_read_exact_launch_reference` for `window.env` / `window-chain.zsh`:
  `joulewise/arm_readiness.py:10993-11006`, mirrored at `:10248-10268`.
- `_attested_launch_artifact_references` classification by filename:
  `joulewise/arm_readiness.py:9522-9529`; argv/path agreement at `:9585-9620`.
- `window_chain_sha256` published in the pack GO receipt: `scripts/run_night.py:1240`.

**None of these fire for a derivation night.** Asking for "the same attestation the
G2-a window chain has" resolves to Route A's sidecar+HEAD attestation, because that is
what G2-a itself has — G2-a is `DIAGNOSTIC_NO_PACK`, not a pack night.

## 2. How the G2-a chain actually gets its 30-odd variables

`scripts/gen_g2_phase_d.py --emit-chain OUT --night-date YYYYMMDD`
(`:392-400`, `emit_g2a_night_chain` `:152-165`) writes an executable chain **and** its
sidecar `f"{digest}  {output_path.name}\n"` (`:163-165`) — precisely the format
`_sidecar_digest` accepts.

`render_g2a_night_chain` (`:120-150`) concatenates, in order:

| Piece | Source | Content |
|---|---|---|
| shebang + `set -euo pipefail` | generator literal `:143` | — |
| runsheet L1534-1598 | `SHAKEDOWN-G2-RUNSHEET.md:1534-1598` "Emitted routing and common variables" | the **routing preamble**: validates `MEASUREMENT_ROOT`/`MEASUREMENT_HEAD` (the driver's two), `git rev-parse HEAD` equality, then `export REPO/PY/PYTHONPATH` and ~35 `export` lines for roots, ledger, pins, IDs, `POWER_POLICY`, `SETTLE_S=600` |
| runsheet L328-351 | runsheet `:328-351` | the G2-a-specific `export G2A_*` block; `20260830` is substituted with `--night-date` (`:135`) |
| arm-time input assertions | generator literal `:137-141` | `test -f` on the three desk-produced inputs |
| runsheet L389-564 | the `g2a-governed-bracket` generated region | the chain body: plan-id/sha derivation, helpers, input check, reservation, settle, slots |
| runsheet L575-587 | runsheet | summarizer |

`render_g2a_night_chain` refuses unless the runsheet's shell-fence inventory is exactly
`[(1534,1598),(328,351),(374,385),(389,564),(575,587)]` (`:126-132`) — a drift tripwire.

So: **the chain file contains its own environment as literal exports, derived at
generation time from a reviewed markdown source, and validated as bytes at launch.**

The generated bracket derives two values at run time rather than pinning them
(`scripts/gen_g2_phase_d.py:248-253`):

```
G2A_PLAN_ID="$(/usr/bin/jq -er '.plan_id' "$G2A_FROZEN_PLAN")"
G2A_PLAN_SHA256="$(/usr/bin/shasum -a 256 "$G2A_FROZEN_PLAN" | /usr/bin/awk '{print $1}')"
```

preceded by `test -f` on the plan, identity-epoch and T1 files (`:245-247`).

The runbook's generated regions are `g2-phase-d-governed-chain` and
`g2a-governed-bracket`, both written **into the runsheet**, extracted from the runbook
under `PINNED_ANCHORS` line-and-byte-exact validation
(`scripts/gen_g2_phase_d.py:26-38`, `validate_pinned_anchors` `:169-178`), with
`--check` as the CI gate (`:404-418`).

## 3. Variable table — where each of the 13 comes from

`P` = "produced at arm time by the desk/lead"; the chain reads it from an export line
in its own bytes unless noted.

| Variable | Source in the G2-a analogue | Producer | When |
|---|---|---|---|
| `SESSION_ID` | analogue `G2A_BRACKET_SESSION_ID`, literal export, runsheet `:344` (`"$G2A_WINDOW_ID-calibration"`) | lead, in the runsheet/exports block; substituted per night | arm time (chain generation) |
| `WINDOW_ID` | `G2A_WINDOW_ID`, runsheet `:343` | lead | arm time |
| `PLAN_ID` | derived in-chain: `jq -er '.plan_id' "$…FROZEN_PLAN"`, generator `:249` | the frozen calibration plan | mid-chain, pre-reserve |
| `PLAN_SHA256` | derived in-chain: `shasum -a 256` of the frozen plan, generator `:250-251` | same file | mid-chain, pre-reserve |
| `PLAN` | `G2A_FROZEN_PLAN`, runsheet `:339` (`$G2A_WINDOW_PLAN_ROOT/calibration_plan.json`) | `generate_g2a_probe_inputs.py bind-window` (runsheet `:378-385`); for a derivation night, whatever desk tool freezes the derivation plan | desk, pre-arm; path exported at arm time |
| `EVIDENCE_ROOT_ID` | `G2A_EVIDENCE_ROOT_ID`, runsheet `:347` | lead | arm time |
| `RUNS_ROOT` | `G2A_RUNS_ROOT`, runsheet `:330`; base `RUNS_ROOT` at runsheet `:1558` | lead | arm time |
| `WINDOW_CUSTODY_ROOT` | runsheet `:1557` (`export WINDOW_CUSTODY_ROOT="$CUSTODY_ROOT"`) | lead | arm time |
| `CALIBRATION_LEDGER` | runsheet `:1573` (`$MEASUREMENT_CHECKOUT/runs/calibration_observation_ledger.jsonl`) | derived from `MEASUREMENT_ROOT` (driver-supplied) | arm time, value depends on driver var |
| `LEDGER_HEAD_PIN` | runsheet `:1574` (`$MEASUREMENT_CHECKOUT/configs/calibration/calibration_ledger_head.json`) | same | arm time |
| `IDENTITY_EPOCH_JSON` | `G2A_IDENTITY_EPOCH_JSON`, runsheet `:340` | desk (`bind-window` / the new issuer) | desk, pre-arm; path exported at arm time |
| `T1_BINDINGS_JSON` | `G2A_T1_BINDINGS_JSON`, runsheet `:341` | same | desk, pre-arm |
| `WINDOW_END_EPOCH_S` | **no analogue** — G2-a has no in-chain window deadline | must be computed at arm time from `t0_epoch_s + window_max_s` | arm time (see §5c) |
| *(per-slot argv)* | **no analogue** — G2-a's bracket uses fixed `--pre-*`/`--post-*` flags | must be emitted as 2×N literal flags | arm time |
| `MEASUREMENT_ROOT`, `MEASUREMENT_HEAD`, `PY`, `NIGHT_PLAN_ID` | the **only** four the driver supplies | `scripts/run_night.py:431-435` | launch |
| `SLOT_COUNT`/`SETTLE_S`/`SLOT_CADENCE_S`/`SLOT_CAPTURE_BUDGET_S` | chain defaults 12/600/600/480, overridable by env | chain `:60-65` | in-chain defaults |

Note the chain sets `REPO` itself: `cd "${0:A:h:h:h}"; REPO="${PWD}"` (`:40-41`) — i.e.
the repository is the grandparent of the chain file's own directory. That is why the
chain must be executed **at its in-clone path** `<CLONE>/scripts/night_chains/…`, and why
a wrapper must `exec` it rather than `source` it (`source` would leave `$0` as the
wrapper and point `REPO` at the night root's grandparent).

## 4. Rehearsal precedent

`/Users/edr/night-custody/rehearsal-20260911/night_plan.json` (read only):
`schema joulewise.night_plan.v2`, `receipt_class REHEARSAL_STUB`,
`chain_path /Users/edr/night-custody/rehearsal-20260911/chain.zsh`,
`chain_sha256_path …/chain.zsh.sha256`, `t0_epoch_s 1789120560.0`, `window_max_s 900`,
`custody_root /Users/edr/night-custody/rehearsal-20260911`,
`measurement_root /private/tmp/joulewise-rehearsal-20260911-checkout`.
**No env-bearing field.** (A `REHEARSAL_STUB` never runs its chain anyway:
`scripts/run_night.py:1572-1575` substitutes `["/bin/zsh","-c","sleep 2; echo REHEARSAL"]`.)

The v2 key set is closed and exact — `joulewise/night_gate.py:112-127`, enforced by
`NightPlan.from_mapping` `:219-231` ("plan keys are not exact"). **There is nowhere to put
env in a plan without a schema v4.**

The G2-a arm recipe (record 04, the packet Astra produced, at
`/Users/edr/code/JouleWise-wt-bk-96bfeca7/docs/process_traces/2026-09-10-activation-96bfeca7/04-g2a-first-window-packet-astra-report.md:645-700`)
is the precedent to copy verbatim:

```sh
"$PY" -B scripts/gen_g2_phase_d.py --check
"$PY" -B scripts/gen_g2_phase_d.py --emit-chain "$NIGHT_ROOT/chain.zsh" --night-date "$NIGHT_DATE"
/bin/zsh -n "$NIGHT_ROOT/chain.zsh"
```

then a `write_night_plan` block that asserts, before publishing the plan
(same file `:672-694`):

```python
chain = Path(plan.chain_path)
expected = generator['render_g2a_night_chain'](RUNSHEET_PATH.read_text(), NIGHT_DATE).encode()
assert chain.read_bytes() == expected
assert Path(plan.chain_sha256_path).read_text() == sha256(expected).hexdigest() + '  chain.zsh\n'
```

i.e. **the arm re-derives the chain from source and requires byte equality**. That is the
real attestation: generator determinism + sidecar + git HEAD equality, all checked twice
(arm time and launch time). Runbook 68 (record 12 of that trace, referenced at
`10-brief-g2a-arm-materials-astra.md:22` and reported at `14-g2a-arm-materials-astra-report.md:94`)
is the operator-facing rendering of the same block; the file itself is not present in the
bookkeeping worktree's trace directory (records 11, 12 and 13 are absent from the listing),
so the packet `04-…:600-720` is the primary source I used.

## 5. The seam statement — what a derivation-night arm must produce

### (a) The recipe

An **emitted night chain** at `$NIGHT_ROOT/chain.zsh` (+ `chain.zsh.sha256`) whose bytes are:

1. the same routing preamble as G2-a (validate `MEASUREMENT_ROOT`/`MEASUREMENT_HEAD`,
   `git rev-parse HEAD` equality, derive `REPO`/`PY`/`PYTHONPATH`) — reusable verbatim
   from runsheet `:1534-1598`;
2. literal `export` lines for the 10 arm-known variables: `SESSION_ID`, `WINDOW_ID`,
   `EVIDENCE_ROOT_ID`, `RUNS_ROOT`, `WINDOW_CUSTODY_ROOT`, `PLAN`, `IDENTITY_EPOCH_JSON`,
   `T1_BINDINGS_JSON`, and `CALIBRATION_LEDGER`/`LEDGER_HEAD_PIN` derived from
   `$MEASUREMENT_ROOT`;
3. `export WINDOW_END_EPOCH_S=<integer>` — the arm-computed constant;
4. in-chain derivation of `PLAN_ID` and `PLAN_SHA256` from `$PLAN` with the same
   `jq`/`shasum` two-liner G2-a uses (generator `:248-253`), so a swapped plan file is
   caught rather than trusted;
5. `test -f` assertions on `$PLAN`, `$IDENTITY_EPOCH_JSON`, `$T1_BINDINGS_JSON`;
6. a terminal `exec /bin/zsh "$REPO/scripts/night_chains/calibration_derivation_only.zsh" \`
   followed by 2×`SLOT_COUNT` literal binding flags:
   `--slot-attempt-id "$SESSION_ID-dNN" --slot-custody-locator "$RUNS_ROOT/instrument_validation/$SESSION_ID-dNN"`
   for `NN = 01..12`, matching the header's declared convention
   (`calibration_derivation_only.zsh:30-31`) and the reserve script's list-flag contract
   (`reserve_calibration_window_bracket.py:167-186`).

`exec`, not `source`, so `$0` inside the tracked chain is the in-clone path and
`REPO="${PWD}"` (`:40-41`) resolves to the clone.

### (b) Generated region vs standalone file — recommendation

**Recommended: a new generated region + emitter, modelled exactly on `gen_g2_phase_d.py`,
NOT a hand-written standalone file.** Concretely: a `scripts/gen_derivation_night.py`
(or a second `--emit-derivation-chain` mode on `gen_g2_phase_d.py`) that renders the
wrapper from a reviewed markdown source region under pinned anchors, writes the sidecar
in `shasum` form, and is `--check`ed in CI; the arm step then re-derives and asserts byte
equality before `write_night_plan`, exactly as record 04 `:672-694` does.

*Why.* The attestation this night can have is only as strong as "the bytes the driver runs
equal bytes a reviewer approved." A standalone hand-written wrapper gets a sidecar and a
review, but nothing detects later drift between the reviewed prose and the file, and
nothing lets the arm re-derive-and-compare — which is the step that caught nothing this
time only because it existed. A generated region buys: a `--check` CI tripwire, the
line-and-byte pinned anchors that refuse silent source movement
(`gen_g2_phase_d.py:169-178`), the fence-inventory refusal (`:126-132`), and an arm-time
byte-equality assertion that is mechanical rather than a human diff. The cost is one
generator plus a runbook section — small, and the G2-a generator is a working template.

*The alternatives I weighed.* (i) **Standalone reviewed file in `$NIGHT_ROOT`** — cheapest,
loses drift detection and arm-time re-derivation; acceptable only for a one-off, and this
is a three-night campaign. (ii) **Extend the v2 plan schema with an `environment` map** —
the cleanest conceptually, since the plan is already the frozen authority; but it is a
schema version bump touching `night_gate.NightPlan`, `night_plan_writer`, the pack path,
and every plan test, and it changes the driver's trust surface (`os.environ` handed to a
child from JSON). Reject for this campaign; note as the right H2 shape. (iii) **Teach the
driver to pass argv** (e.g. a plan `chain_argv` field) — same schema-bump cost, and it
solves only the per-slot half. (iv) **Put the exports in the tracked chain itself** —
would make the tracked chain night-specific and destroy its reusability; reject.

### (c) `WINDOW_END_EPOCH_S`

`WINDOW_END_EPOCH_S = int(t0_epoch_s + window_max_s)` — the exclusive end of the plan's
acquisition allocation. It is **not** the dead-man epoch and **not** the courier deadline:

- the dead-man is the next local 07:00 (`scripts/run_night.py:945-955`), independent of
  the plan;
- the courier deadline is `t0 + window_max_s + COURIER_DEADLINE_S` (`:958-959`), and the
  gate refuses `plan_overruns_deadman` when that crosses the dead-man (`:1463-1474`);
- `t0 + window_max_s` is the same boundary the pack GO uses for expiry
  (`:1199-1200`, `conditions.C5.window_expired`).

Both numbers live in the plan (`t0_epoch_s`, `window_max_s`), so the arm computes the
constant and bakes it into the emitted chain. The draft runbook already states this rule
and the arithmetic:
`99-derivation-night-runbook-draft.md:341-352` — with `window_max_s = 9000` derived at
`:283-315` (programmed span 600 + 11×600 + 480 = 7680 s, plus 1320 s margin), and the d12
admission check at `:346-352`.

Two things the implementation must get right: it must be an **integer** string (the chain
rejects anything not matching `<->` at `:69-75`, exit 64), and the value must be an
absolute epoch, so the arm-to-t0 interval does not shift it.

### (d) `SESSION_ID`

**Input, not minted.** The chain never generates it: it passes `--session-id "$SESSION_ID"`
to the pre-reserve readiness check (`:138`) *before* the reservation, and again to
`reserve_calibration_window_bracket.py --session-id` (`:146`), and derives every attempt id
from it (`:197`, `${SESSION_ID}-${slot}`). "Reserve the session" means *open a
pre-declared ledger session*, not *allocate an identifier*. The lead chooses it at arm
time, exactly as G2-a chooses `G2A_BRACKET_SESSION_ID` (runsheet `:344`), and the same
value must appear in the per-slot binding argv attempt ids.

### (e) What the chain's tests already pin

`tests/test_issue_calibration_acceptance_generation.py`, class `DerivationChainSkeletonTests`
(`:316-…`), drives the real chain against fake `date`/`sleep`/`python3` on a fake clock:

- the env fixture is the exact 13 variables plus `PY`/`SLEEP`/`DATE` (`:367-388`);
- the chain is invoked as `[zsh, CHAIN]` with **no argv** (`:392-395`) — so the per-slot
  binding forwarding is *not* pinned by any current test; `"$@"` is exercised only as
  empty;
- order: readiness with `--phase pre-reserve` first, reservation second, both **before**
  the single settle (`:412-424`);
- reservation shape: `--session-kind derivation` present, `--slot-count` == "12" (`:419-421`);
- capture shape: `--derivation-only`, `--allow-live`, `dNN`, `ac_high_power` on every slot
  (`:430-434`);
- exactly one 600 s settle, then 11 cadence sleeps of 120 s (`:425-429`);
- operator-log transcript, verbatim (`:436-449`);
- refusals: missing file → 66 with nothing run (`:450-460`); unready ledger → 3 after
  exactly one call (`:461-469`); zero settle/cadence → 64 before anything (`:470-482`);
  window exhaustion → abort once, `--reason window_exhausted` (`:485-…`); a slot that
  cannot *finish* is never started (`:511-…`);
- **source-shape tests that an implementation seat will have to amend**:
  `test_chain_source_carries_no_pack_probe_or_git_step` (`:556-572`) asserts the SKELETON
  banner line is present and that the non-comment code matches none of
  `\bgit\b`, `\bpack\b`, `generate_g2a_probe_inputs`, `launch_window`, and contains exactly
  one `\nsettle\n`; `test_chain_header_pins_its_hand_written_and_unlanded_flag_warnings`
  (`:574-…`) pins the "HAND-WRITTEN and is NOT a generated region" and the
  unlanded-`--slot` warnings.

The S1/S2 surfaces the skeleton header calls unlanded **have landed at this HEAD**:
`reserve_calibration_window_bracket.py:84-108` (`--session-kind`, `--slot-count`,
`--slot-attempt-id`, `--slot-custody-locator`) and
`validate_powermetrics_fiducial.py:1772`, `:1947` (`--derivation-only` requiring
`--session-id`/`--slot`/`--attempt-id`). So the header's warnings and the two source-shape
tests are now **stale**, and un-skeletonizing is part of the seat's job.

## 6. Non-launchability checks under the current driver

| Concern | Finding |
|---|---|
| **Argv** | Blocking. Driver passes none (`run_night.py:438`); reserve refuses on count mismatch (`reserve_…:172-186`). Cured by the wrapper's `exec … <flags>`. |
| **Environment** | Blocking. Ten of thirteen unsupplied. Cured by the wrapper's exports. |
| **fd inheritance** | Fine. The derivation chain never calls `launch_window.py`, so FD 198 (`launch_window.py:36`, `_read_one_use_handoff` `:238-256`) is irrelevant. The driver gives the chain `stdin=DEVNULL` and file stdout/stderr (`run_night.py:439-441`); the chain writes its own operator log (`:81-91`) and does not read stdin. |
| **`start_new_session=True`** | Fine, and required for the driver's `_terminate_process_group` kill on census hit (`run_night.py:472-480`). |
| **Settle step** | Fine. `SETTLE_S=600` default (`:61`), one settle after the reservation (`:164`). Note the *window budget* must absorb it: `WINDOW_END_EPOCH_S` is compared against slot starts only, so a window shorter than settle+480 silently aborts at d01 (test `:534-544`). |
| **`--phase pre-reserve`** | Fine. The phase exists: `scripts/recover_calibration_ledger.py:171` (`choices=("pre-reserve","pre-slot","terminal")`), handled at `:422`. |
| **Census** | Watch. `agent_census` runs every 30 s during the chain and aborts the night on any hit; the probe is `("/usr/bin/pgrep","-lf","codex|claude|t3")` and passes **only** on exit 1 with empty stdout (`joulewise/night_gate.py:42`, `:498-525`; `run_night.py:459-482`, `abort_on_census=True`). The chain spawns only `python3`, `sleep`, `date`, `mkdir` — no match. The real risk is unchanged: no agent session may be alive, and `pgrep -lf` matches full command lines, so a wrapper whose argv or paths contain the substrings `codex`, `claude` or `t3` would abort its own night. **Do not name the night root, session id, or wrapper anything containing those substrings.** |
| **Clean-checkout** | Open. The gate verifies the measurement checkout's HEAD equals `measurement_head` (`night_gate.py:1006-1029`) but I did not find a dirty-tree check. The tracked chain's bytes are therefore bound by HEAD only if the clone is clean — the arm must verify that (the G2-a clone-cut record does: `05-clone-cut-record.md`). |
| **`REPO` derivation** | Watch. `cd "${0:A:h:h:h}"` (`:40`) requires the chain to sit exactly two directories below the repo root. Any relocation silently retargets `REPO`. The wrapper must `exec` the in-clone path. |

## 7. Files an implementation seat would touch

Suggested `WRITE_SCOPE` (a linked worktree, never canonical):

```
WRITE_SCOPE: [scripts/gen_derivation_night.py, scripts/night_chains/calibration_derivation_only.zsh, docs/phase_2/derivation_night_runbook.md, tests/test_gen_derivation_night.py, tests/test_issue_calibration_acceptance_generation.py]
```

- `scripts/gen_derivation_night.py` — **new**. The emitter: render the wrapper from the
  reviewed markdown source under pinned anchors, `--check` mode, `--emit-chain OUT`
  writing the `shasum`-form sidecar. Template: `scripts/gen_g2_phase_d.py:120-166`
  (rendering + emission), `:169-178` (anchor validation), `:392-418` (CLI/`--check`).
- `docs/phase_2/derivation_night_runbook.md` (or a new section of the existing runbook) —
  **new/edited**. The reviewed source region the emitter reads: the routing preamble, the
  export block, the plan-derivation two-liner, and the `exec` line with its 24 binding
  flags. If the seat instead extends `gen_g2_phase_d.py`, the anchors dict at `:26-38`
  gains entries and every existing anchor line number shifts — a strong argument for a
  separate generator and a separate source file.
- `scripts/night_chains/calibration_derivation_only.zsh` — **edited**: drop the SKELETON
  banner (S1/S2 have landed at this HEAD), update the "UNLANDED SURFACE" paragraph
  (`:22-34`) to record the landed flags, and resolve the open question at `:19-20`
  ("whether the pinned night chain is generated from a runbook section instead is the
  lead's call") in favour of the wrapper.
- `tests/test_issue_calibration_acceptance_generation.py` — **edited**: amend
  `test_chain_source_carries_no_pack_probe_or_git_step` (`:556-572`) and
  `test_chain_header_pins_…` (`:574-…`) to the post-skeleton header; **add** a test that
  the chain forwards a non-empty `"$@"` verbatim into the reservation argv (today nothing
  pins the forwarding at all).
- `tests/test_gen_derivation_night.py` — **new**: determinism (same input → same bytes),
  sidecar format accepted by `run_night._sidecar_digest`, the emitted wrapper passes
  `zsh -n`, the 13 variables are all exported, `WINDOW_END_EPOCH_S` is an integer literal,
  and the binding-flag count equals 2×`SLOT_COUNT`.
- **Not touched**: `scripts/run_night.py`, `joulewise/night_gate.py`,
  `joulewise/night_plan_writer.py`, `joulewise/arm_readiness*.py`,
  `scripts/launch_window.py`. The recommended shape needs no driver or schema change —
  that is its main argument.

The arm-time procedure (a runbook, not code) mirrors record 04 `:645-700`: `--check`,
`--emit-chain "$NIGHT_ROOT/chain.zsh"`, `zsh -n`, then the `write_night_plan` block with
the re-derive-and-compare assertions, with `chain_path` = `$NIGHT_ROOT/chain.zsh` and
`chain_sha256_path` = `$NIGHT_ROOT/chain.zsh.sha256`.

## 8. Open questions for the magistrate

1. **Wrapper location vs `chain_path`.** Under the recommendation the plan pins the
   *wrapper*, and the tracked derivation chain is bound only transitively (git HEAD +
   clean clone). Is that acceptable, or must the plan-pinned digest cover the chain that
   actually captures? (An alternative: have the wrapper `shasum -c` the tracked chain
   against an arm-pinned digest baked into the wrapper's own bytes — cheap, and it closes
   the gap without a schema change. I would take this; it is four lines.)
2. **Does the gate need a clean-tree check?** HEAD equality does not exclude uncommitted
   edits in the clone (§6). Today only the arm procedure guards this.
3. **Generated region location.** Extending `gen_g2_phase_d.py` shifts its
   `PINNED_ANCHORS` line numbers and couples two nights' generators. Separate generator +
   separate source file, or one generator?
4. **`SLOT_COUNT` authority.** The chain defaults to 12 (`:60`) and the wrapper would not
   need to set it; but the wrapper *must* emit exactly `2 × SLOT_COUNT` binding flags. Do
   we pin `SLOT_COUNT` explicitly in the wrapper so the two can never disagree? (Yes, I
   think — an implicit default and an explicit flag list is exactly the shape that drifts.)
5. **Custody-locator convention.** The chain header (`:30-31`) says attempt ids are
   `${SESSION_ID}-dNN` with custody under `${RUNS_ROOT}/instrument_validation`, and the
   chain's own `--output-root` is `$RUNS_ROOT/instrument_validation` (`:198`). Confirm the
   locator the reservation is given must equal the directory the writer will create
   (`$RUNS_ROOT/instrument_validation/${SESSION_ID}-dNN`) — I did not verify the writer's
   directory-naming rule, and a mismatch is a mid-night refusal.
6. **Three nights, three session ids.** The draft runbook (`:508`) has three sessions each
   with its own `SESSION_ID`. Is one emitted wrapper per night (three emissions, three
   plans), or one parameterised wrapper? One per night matches the "frozen bytes" model.
7. **Record 12 / runbook 68 is absent** from
   `/Users/edr/code/JouleWise-wt-bk-96bfeca7/docs/process_traces/2026-09-10-activation-96bfeca7/`
   (records 11, 12, 13 are not in the directory), though records 10, 14 and 21 refer to it.
   Was it never committed, or is it elsewhere? I used the packet (record 04) instead.
8. **`ACCEPTANCE-EPOCH-25G83-01` still blocks any arm** (record 39 `:35`); this seam work
   is desk work that can land ahead of it, but nothing here authorizes a night.
