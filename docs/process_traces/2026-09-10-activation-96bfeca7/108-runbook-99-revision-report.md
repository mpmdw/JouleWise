# 108 — Runbook 99 revision (WRITER seat, dictated-fills), revision 2

Worktree `/Users/edr/code/JouleWise-wt-bk-96bfeca7`, branch
`bookkeeping/2026-09-10-activation-96bfeca7`. One file edited:
`docs/process_traces/2026-09-10-activation-96bfeca7/99-derivation-night-runbook-draft.md`.
No git state changes by this seat, no captures, nothing touched in
`/Users/edr/code/JouleWise` or `/Users/edr/night-custody`.

**Note on the diff base.** The magistrate committed this seat's in-flight edits
at `0ba69efc` while the seat was still working (331 changed lines). The full
revision is therefore `git diff 78c2ef71 -- <file>` (pre-revision blob → working
tree); `git diff` alone shows only the last three hunks.

## Changelog (as written into the file, under the DRAFT banner)

Revision 2 is driven by seat S7's landed wrapper generator
`scripts/gen_derivation_night.py` and its generated runsheet region, which
**close** the §1.1 `[UNVERIFIED]` on how the night driver supplies the chain's
environment. The answer is that it does not, by design: the driver hands the
launched file four variables and no argv, and a generated per-night wrapper
carries the rest. That block is deleted.

| § | Change |
|---|---|
| Banner | Changelog block added. |
| 0.5 | New paragraph: `[CHAIN_SHA256]` is the TRACKED chain's digest, one value for all three nights, not any night's wrapper digest — three nights produce three wrappers, and the registration reserves one blank. |
| 0.8 (new) | Clean-tree precondition (`git -C "$MEASUREMENT_ROOT" status --porcelain` empty, recorded verbatim in the arm materials, procedure not code — the gate binds `HEAD` only) + the two desk-produced JSON inputs + one NEW `[UNVERIFIED]` on their provenance. |
| 1.1 | `chain_path` = `<NIGHT_ROOT>/chain.zsh` (the emitted wrapper); `chain_sha256_path` = that path + `.sha256`, the only value the generator accepts. |
| 1.1a (new) | The wrapper mechanism: forcing problem (4 driver variables vs 13 chain variables + 24 argv), the five things the wrapper does in order, `exec`-not-`source` and why, `FAIL <reason>`/rc 1, and the three emitted files with their roles. |
| 1.1b (new) | The five-step arm order with the generator's real commands and flags, `--verify` rc 0 `VERIFIED` / rc 3 `FAIL`, `/bin/zsh -n`, one wrapper per night. |
| 1.2 | Generator's window-fit floor (7680 + 300 = 7980 s) added; 9000 s kept as the value to author; pre-settle allowance built and explicitly distinguished from the courier allowance. |
| 1.4 | Email contents: the wrapper's digest and sidecar path, plus the tracked chain's digest the wrapper pins. |
| 5 | Two new tables ahead of the chain-exit table: generation-time refusals (rc 2, nothing written; rc 3 for `--verify`) and launch-time wrapper refusals (`FAIL <reason>`, rc 1). Stale `exit 1 on a :?required guard` row rewritten as an ambiguity to disambiguate from `chain.stderr.log`. |
| 7 | Three source rows added (generator by SYMBOL not line, per S7's own S-2 lesson; scout 101 / refuter 105 line facts attributed to those reports, not re-derived); "not verified" list updated with an explicit "closed since revision 1". |
| 8 | Nine terms added: clean tree, wrapper, night root, sidecar, advisory, tripwire, `zsh -n`, census substring, programmed span, pre-settle allowance; the courier row amended to contrast the two 300 s budgets. |

### `[UNVERIFIED]` accounting

- **Deleted (closed by S7):** §1.1's driver-environment/per-slot-argv block.
- **Kept, still true:** §0.3 live `check` output strings; §1.3 the 06:05
  last-start cutoff's status; §5 the complete night-gate refusal list.
- **Added:** §0.8 — which tool produces `identity_epoch.json` and
  `t1_bindings.json` for a derivation night and where their custody copy lives
  (`generate_g2a_probe_inputs.py bind-window`, the new epoch issuer, or a third
  desk tool), with the arm-time actions that follow once it is named.

## Two corrections to the brief, made against the source

1. **There is no `--repo-root` flag.** The generator digests the tracked chain
   from `plan.measurement_root` — the clone the night runs — never from the
   checkout it executes in. Written into §1.1b step 3 as such.
2. **`--ledger` and `--head-pin` are optional, not required.** They default to
   `<measurement_root>/runs/calibration_observation_ledger.jsonl` and
   `<measurement_root>/configs/calibration/calibration_ledger_head.json`. The
   required emit flags are exactly six: `--plan`, `--session-id`,
   `--evidence-root-id`, `--calibration-plan`, `--identity-epoch-json`,
   `--t1-bindings-json` (`REQUIRED_EMIT_ARGS` plus `--plan`; omission prints
   `FAIL emit mode requires --…` and exits 2). §1.1b says which four flags have
   defaults and that `--out` must not be passed.

## Verification commands (all read-only, all run this session)

```
git -C /Users/edr/code/JouleWise-wt-s7-night-wrapper show HEAD:scripts/gen_derivation_night.py > /tmp/gdn.py
PYTHONPATH=/Users/edr/code/JouleWise-wt-s7-night-wrapper python3 /tmp/gdn.py --help   # exact flag list + module docstring
git -C /Users/edr/code/JouleWise-wt-s7-night-wrapper show HEAD:docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md \
  | sed -n '/BEGIN GENERATED: derivation-night-wrapper/,/END GENERATED: derivation-night-wrapper/p'
sed -n '28,135p;240,340p;395,560p;697,827p' /tmp/gdn.py    # constants, render_wrapper, build_spec, verify, main
rm -f /tmp/gdn.py                                          # done; file removed
```

Facts each command established, as used in the revision:

- `PRE_SETTLE_ALLOWANCE_S = 300`; `programmed_span_s(12) = 600 + 11×600 + 480 =
  7680`; refusal fires on `plan.window_max_s < required_span + 300 = 7980`.
- `COURIER_DEADLINE_S = 300`, `DEADMAN_HOUR/MINUTE = 7/0`; dead-man refusal is
  `not (t0 + window_max_s + 300 < next local 07:00)`.
- Exit codes: `GenerationRefusal` → 2; missing required emit flag → 2;
  `--verify` mismatch → 3; `--verify` match → 0 with `VERIFIED <path> sha256=…`;
  emit success → 0 with `emitted <path> sha256=…`; region `--check` drift → 1.
- `CENSUS_SUBSTRINGS = ("codex", "claude", "t3")`, case-folded, applied to plan
  id, window id, session id, evidence root id, frozen plan id and every
  absolute path literal.
- `emit()` writes three files: wrapper (mode 0755), `<name>.sha256`, and
  `<name>.chain-source.sha256` whose second token is the chain's
  repository-relative path (so a hand `shasum -a 256 -c` works from the clone).
- `verify()` compares the re-rendered wrapper AND its sidecar, writes nothing.
- The wrapper's own refusals, read from `render_wrapper`: `route_refuse()` prints
  `FAIL %s` to stderr and exits 1; the digest literals compared are the frozen
  calibration plan's, the identity epoch's, the T1 bindings' and the tracked
  chain's.

File-level checks after editing:

```
cd /Users/edr/code/JouleWise-wt-bk-96bfeca7
git status --porcelain          # only the one draft file, unstaged
git rev-parse --abbrev-ref HEAD # bookkeeping/2026-09-10-activation-96bfeca7
grep -n UNVERIFIED docs/.../99-derivation-night-runbook-draft.md   # 4 blocks: §0.3, §0.8, §1.3, §5
grep -c '^```' docs/.../99-derivation-night-runbook-draft.md       # 26, balanced
```

## Diff (78c2ef71 → working tree)

```diff
diff --git a/docs/process_traces/2026-09-10-activation-96bfeca7/99-derivation-night-runbook-draft.md b/docs/process_traces/2026-09-10-activation-96bfeca7/99-derivation-night-runbook-draft.md
index ec4f9e3e..2e0d80a8 100644
--- a/docs/process_traces/2026-09-10-activation-96bfeca7/99-derivation-night-runbook-draft.md
+++ b/docs/process_traces/2026-09-10-activation-96bfeca7/99-derivation-night-runbook-draft.md
@@ -12,6 +12,21 @@ head is green and the lane's PR is merged.** Sections marked
 `[UNVERIFIED: …]` are facts this seat could not establish from the sources it
 was given; they are open questions for the operator, not instructions.
 
+**Changelog — revision 2 (2026-09-10, writer seat), one line: revised against
+seat S7's landed wrapper generator `scripts/gen_derivation_night.py` and its
+generated runsheet region, which CLOSE the §1.1 `[UNVERIFIED]` on how the night
+driver supplies the chain's environment (answer: it does not, by design — a
+generated wrapper carries it), now deleted.** What that forced: §1.1 restates
+`chain_path` as the emitted wrapper and adds the mechanism (§1.1a) and the
+five-step arm order with the generator's real flags (§1.1b); §1.2 adds the
+generator's window-fit refusal and separates the pre-settle allowance from the
+courier allowance; §5 gains the generation-time and launch-time refusal tables
+and rewrites the old exit-1 row; §0.8 adds the clean-tree precondition and one
+NEW `[UNVERIFIED]` on identity-epoch / T1-bindings provenance; §7 and §8 are
+updated. The three other `[UNVERIFIED]` blocks — the live `check` output
+strings (§0.3), the 06:05 last-start cutoff (§1.3) and the complete night-gate
+refusal list (§5) — are still true and are kept verbatim.
+
 Audience: the operator is the **next magistrate activation** — the Claude
 session that a relaunch prompt starts, holding the frozen triple and the
 project's standing authorities. It is a desk operator: it prepares, notices,
@@ -194,6 +209,14 @@ committed inside H with `[DD]`, `[MLX_VERSION]`, `[SEQ]`, `[DIGEST]` and
 was written; filling them reopens no scientific rule. The plan's
 `registration_path` points at this file (`joulewise/night_gate.py:38`).
 
+`[CHAIN_SHA256]` takes the **tracked chain's** SHA-256 — one value shared by all
+three nights — and NOT any night's wrapper digest. The registration reserves a
+single blank for it, and three nights produce three different wrappers (three
+plans, three session IDs, three `t0`s), so only the tracked chain's digest can
+fill it. That digest is also the literal each night's wrapper compares against
+before it `exec`s (§1.1a step 4), which is what makes the registered value and
+the value in force at capture the same number.
+
 **V3 requires Ed's affirmative written acknowledgment before the first
 capture's arm — silence is not consent for V3.** V3 is the night count, the
 slots per night, and the retained-corpus minimum: three nights × 12 slots,
@@ -232,6 +255,56 @@ discoverable prior plan root, no active or indeterminate measurement ownership.
 Remove every `REHEARSAL_STUB` plan root before arming any real plan
 (`docs/process/MAGISTRATE_WATCHDOG.md:329`).
 
+### 0.8 The clone's tree is clean, and the two desk-produced JSON inputs exist
+
+**Clean tree** means: the measurement clone has no uncommitted change of any
+kind — no modification, no staged file, no untracked file. Check it and record
+the output verbatim in the night's arm materials:
+
+```zsh
+git -C "$MEASUREMENT_ROOT" status --porcelain
+```
+
+The expected output is **nothing at all**, zero bytes. Any line is a stop:
+stand the night down and re-cut the clone (§0.2).
+
+Why this is a precondition and not a nicety: the night gate binds the clone by
+its committed `HEAD` only — it checks `git rev-parse HEAD` equals the plan's
+`measurement_head` and nothing more (`joulewise/night_gate.py:1006–1029`, read
+by the S7 contract refuter, report 105 §5.2). Nothing anywhere excludes
+uncommitted edits. The wrapper of §1.1a closes this for exactly one file, the
+capturing chain, by comparing its bytes against a digest baked in at arm time;
+`recover_calibration_ledger.py`, `reserve_calibration_window_bracket.py` and
+`validate_powermetrics_fiducial.py` — the three programs that actually open the
+session, reserve the slots and write the captures — remain bound by `HEAD`
+alone. So an edited working copy of any of them would run all night with no
+signal. **This check is procedure, not code**: no tool enforces it, which is
+precisely why it is written here and recorded in the arm record.
+
+The night root `<NIGHT_ROOT>` must also hold two desk-produced JSON files
+before the wrapper can be generated: `identity_epoch.json` (the six-field
+identity vector) and `t1_bindings.json` (the T1 bindings block). The
+reservation copies the CONTENTS of both verbatim into every slot record
+(`scripts/reserve_calibration_window_bracket.py:216–220`, report 105 §2), so
+their bytes are part of what every capture is bound to, and the generator pins
+each one's SHA-256 into the wrapper as a literal.
+
+`[UNVERIFIED: which tool produces <NIGHT_ROOT>/identity_epoch.json and
+<NIGHT_ROOT>/t1_bindings.json for a DERIVATION night, and where their custody
+copy lives. The exact question to answer before the first arm: is the producer
+`scripts/generate_g2a_probe_inputs.py bind-window` — the G2-a analogue, which
+records `{"identity_epoch": {"path", "sha256"}, "t1_bindings": {"path",
+"sha256"}}` and replays them under its own `check` (report 105 §5.1) — or the
+new epoch issuer `scripts/issue_calibration_acceptance_generation.py`, or a
+third desk tool? Seat S7 left this open deliberately and made both files
+explicit required inputs rather than inventing a producer (report 103 §7.1).
+Once the producer is named: run it IN the measurement clone at arm time,
+record both paths AND both SHA-256 digests in the arm record, and re-derive
+both if `os_build`, `powermetrics_sha256`, `mlx_version`, `estimator_revision`
+or `protocol_sha256` moved since the previous night — the writer compares its
+measured bindings against the reserved slot's, so a drift between arm and t0
+refuses at slot `d01` and costs the whole night.]`
+
 ---
 
 ## 1. Night 1 arm
@@ -257,26 +330,167 @@ The v2 plan's required keys are exactly (`joulewise/night_gate.py:112–127`):
 | `repo_head` | `<H>` |
 | `measurement_root` | `<CLONE>` — the §0.2 clone path, absolute |
 | `measurement_head` | `<H>` — equal to `repo_head` |
-| `chain_path` | `<CLONE>/scripts/night_chains/calibration_derivation_only.zsh` (see the DRAFT banner) |
-| `chain_sha256_path` | the sidecar holding that file's SHA-256 |
+| `chain_path` | `<NIGHT_ROOT>/chain.zsh` — the **emitted wrapper** of §1.1a, NOT the tracked chain |
+| `chain_sha256_path` | `<NIGHT_ROOT>/chain.zsh.sha256` — exactly `chain_path` plus `.sha256`; the generator refuses any other value |
 | `custody_root` | `<NIGHT_ROOT>` — e.g. `/Users/edr/night-custody/<PLAN_ID>` |
 | `registration_path` | the committed pre-registration of §0.5 |
 
 The plan carries no pack block: `_PACK_NIGHT_KEYS` belongs to pack nights, and
 this night has no pack.
 
-`[UNVERIFIED: how the night driver supplies the chain's environment. The chain
-requires SESSION_ID, WINDOW_ID, PLAN_ID, PLAN_SHA256, PLAN, EVIDENCE_ROOT_ID,
-RUNS_ROOT, WINDOW_CUSTODY_ROOT, CALIBRATION_LEDGER, LEDGER_HEAD_PIN,
-IDENTITY_EPOCH_JSON, T1_BINDINGS_JSON and WINDOW_END_EPOCH_S, and forwards its
-own argv verbatim to the reservation as the per-slot bindings. The tests
-construct that whole environment themselves
-(tests/test_issue_calibration_acceptance_generation.py:322–345). This seat did
-not find the production code that derives WINDOW_END_EPOCH_S from the plan, nor
-the code that supplies the per-slot binding argv. Establish both before
-arming; a chain launched without WINDOW_END_EPOCH_S exits 1 on the
-`:?required` guard before any window time is spent, which is safe but is a
-wasted night.]`
+### 1.1a The wrapper: what `chain_path` actually points at, and why
+
+**The forcing problem.** The night driver launches the file the plan names in
+`chain_path` with a fixed, four-variable environment and NO command-line
+arguments: it sets `NIGHT_PLAN_ID`, `MEASUREMENT_ROOT`, `MEASUREMENT_HEAD` and
+`PY` from the plan, and runs `/bin/zsh <chain_path>` with nothing after it
+(`scripts/run_night.py:430–444`, pinned by `tests/test_run_night.py:348–380`,
+which asserts the argv is exactly `["/bin/zsh", <chain_path>]`; scout report 101
+§0). The tracked derivation chain
+`scripts/night_chains/calibration_derivation_only.zsh` needs far more than
+that: **thirteen** further environment variables, each behind a
+`: "${NAME:?required}"` guard, and **twenty-four** command-line arguments — one
+`--slot-attempt-id` and one `--slot-custody-locator` per slot — which it
+forwards verbatim to the session reservation as `"$@"`. There is no production
+code that bridges the gap, and there never was: G2-a does not need one, because
+its chain carries its own environment inside its own bytes (scout 101 §2).
+
+So a plan whose `chain_path` named the tracked chain directly would launch a
+chain with ten of its thirteen variables unset. It would exit 1 on the first
+`:?required` guard before spending any window time — safe, but a burned night
+out of the three the corpus has.
+
+**The mechanism.** A night is armed by pinning a **wrapper**: a generated zsh
+file, one per night, written into the night root (the custody directory the
+plan calls `custody_root`), which carries that night's whole environment as
+literal `export` lines and then hands control to the tracked chain. The
+generator is `scripts/gen_derivation_night.py`. In order, the wrapper:
+
+1. **Refuses any night but its own.** It checks that `MEASUREMENT_ROOT` is
+   present, absolute and free of control characters, that `MEASUREMENT_HEAD` is
+   a 40-character lowercase hex SHA-1, and then that each of `NIGHT_PLAN_ID`,
+   `MEASUREMENT_ROOT` and `MEASUREMENT_HEAD` equals the literal frozen into
+   these bytes at arm time. It then reads the clone's actual
+   `git rev-parse --verify HEAD` and requires it to equal `MEASUREMENT_HEAD`,
+   and requires `<MEASUREMENT_ROOT>/.venv/bin/python` to exist and be
+   executable.
+2. **Exports the thirteen chain variables as literals** — `SESSION_ID`,
+   `WINDOW_ID`, `PLAN_ID`, `PLAN_SHA256`, `PLAN`, `EVIDENCE_ROOT_ID`,
+   `RUNS_ROOT`, `WINDOW_CUSTODY_ROOT`, `CALIBRATION_LEDGER`, `LEDGER_HEAD_PIN`,
+   `IDENTITY_EPOCH_JSON`, `T1_BINDINGS_JSON`, `WINDOW_END_EPOCH_S` — plus six
+   more the chain would otherwise default from whatever shell armed the night:
+   `SLOT_COUNT`, `SETTLE_S`, `SLOT_CADENCE_S`, `SLOT_CAPTURE_BUDGET_S`, `SLEEP`
+   and `DATE`. The last six are pinned because the driver hands the child
+   `os.environ.copy()`, so an inherited `SETTLE_S` from the arming operator's
+   shell would silently retime the night. `WINDOW_END_EPOCH_S` is
+   `int(t0_epoch_s + window_max_s)` — the same derivation §1.2 does by hand.
+3. **Authenticates the three desk-produced inputs before any window time is
+   spent.** For the frozen calibration plan `PLAN`: it must exist, parse as
+   JSON, carry a `plan_id` equal to the `PLAN_ID` literal, and hash to the
+   `PLAN_SHA256` literal. For `IDENTITY_EPOCH_JSON` and `T1_BINDINGS_JSON`:
+   each must exist and hash to its own baked-in SHA-256 literal.
+4. **Verifies the tracked chain's bytes** — `shasum -a 256` of
+   `<CLONE>/scripts/night_chains/calibration_derivation_only.zsh` must equal a
+   SHA-256 literal inside the wrapper. This is the link that makes the
+   attestation transitive: the plan pins the wrapper's digest, the wrapper's
+   own bytes contain the chain's digest, so the plan-pinned digest moves
+   whenever the capturing bytes move.
+5. **`exec`s the tracked chain** with the twenty-four per-slot bindings as
+   argv: `--slot-attempt-id '<SESSION_ID>-dNN'` and
+   `--slot-custody-locator '<RUNS_ROOT>/instrument_validation/<SESSION_ID>-dNN'`
+   for `dNN` = `d01`…`d12`. `exec`, never `source`: the chain derives its
+   repository root from its own `$0` with the line `cd "${0:A:h:h:h}"`, so it
+   must run as `$0` at its in-clone path.
+
+Every refusal above prints `FAIL <reason>` to stderr and exits 1. That stream
+is the driver's `<NIGHT_ROOT>/night/chain.stderr.log`, and on an agent-free
+night it is the only forensic record a 3 a.m. refusal leaves.
+
+**The three emitted files.** One generator run writes exactly three files into
+the night root. A **sidecar** here means a small companion file holding another
+file's SHA-256 in `shasum` output form — the digest, two spaces, a name:
+
+| File | Role |
+|---|---|
+| `<NIGHT_ROOT>/chain.zsh` | The wrapper. The plan's `chain_path` must be this exact path. |
+| `<NIGHT_ROOT>/chain.zsh.sha256` | The wrapper's sidecar. The plan's `chain_sha256_path` must be this exact path; the driver refuses the night unless the wrapper's bytes still hash to it. |
+| `<NIGHT_ROOT>/chain.zsh.chain-source.sha256` | **Advisory only** — the tracked chain's digest, named by its repository-relative path so an operator can run `shasum -a 256 -c` on it by hand from the clone. **Advisory** means nothing reads it at launch: the wrapper carries the same digest as a literal in its own bytes, so deleting or rewriting this file changes nothing about what the night will accept. |
+
+### 1.1b Arm order: five steps, each depending on the one before
+
+1. **Cut the clone at H** (§0.2) and record `git -C "$MEASUREMENT_ROOT" status
+   --porcelain`; it must be empty (§0.8).
+2. **Author the night plan** (§1.1 table), with `chain_path` =
+   `<NIGHT_ROOT>/chain.zsh` and `chain_sha256_path` = that path plus `.sha256`.
+   The plan must exist FIRST: the generator reads `t0_epoch_s`,
+   `window_max_s`, `custody_root`, `measurement_root`, `measurement_head`,
+   `receipt_class`, `chain_path` and `chain_sha256_path` out of it, and refuses
+   if `chain_path` is anything else.
+3. **Generate the wrapper**, run from the measurement clone. Six flags are
+   required and there are no others to supply for an ordinary twelve-slot
+   night:
+
+   ```zsh
+   cd "$MEASUREMENT_ROOT"
+   "$PY" -B scripts/gen_derivation_night.py \
+     --plan "$NIGHT_ROOT/night_plan.json" \
+     --session-id "$SESSION_ID" \
+     --evidence-root-id "$EVIDENCE_ROOT_ID" \
+     --calibration-plan "$NIGHT_ROOT/calibration_plan.json" \
+     --identity-epoch-json "$NIGHT_ROOT/identity_epoch.json" \
+     --t1-bindings-json "$NIGHT_ROOT/t1_bindings.json"
+   ```
+
+   On success it prints `emitted <NIGHT_ROOT>/chain.zsh sha256=<64 hex>` and
+   exits 0. Notes on the flags, because getting them wrong is a refusal:
+   `--out` defaults to the plan's `chain_path` AND is refused if it is anything
+   else, so do not pass it. `--window-id` defaults to the plan's `plan_id`;
+   `--runs-root` to `<custody_root>/runs`; `--ledger` to
+   `<measurement_root>/runs/calibration_observation_ledger.jsonl`; `--head-pin`
+   to `<measurement_root>/configs/calibration/calibration_ledger_head.json` —
+   pass any of these four only to override a default, and re-record the value
+   if you do. `--slot-count` defaults to 12. There is **no `--repo-root`
+   flag**: the generator digests the tracked chain from the clone the night
+   will run, i.e. from `plan.measurement_root`, never from the checkout the
+   generator happens to execute in. `--evidence-root-id` has no derivable
+   default; state its literal value and the record that registers it in the arm
+   record alongside `--session-id`.
+4. **Re-derive and assert byte equality** — the arm-time **tripwire**, meaning
+   a check that writes nothing and whose only job is to fail loudly if an input
+   drifted between generation and arming. Same command as step 3 plus
+   `--verify`:
+
+   ```zsh
+   "$PY" -B scripts/gen_derivation_night.py --plan "$NIGHT_ROOT/night_plan.json" \
+     --session-id "$SESSION_ID" --evidence-root-id "$EVIDENCE_ROOT_ID" \
+     --calibration-plan "$NIGHT_ROOT/calibration_plan.json" \
+     --identity-epoch-json "$NIGHT_ROOT/identity_epoch.json" \
+     --t1-bindings-json "$NIGHT_ROOT/t1_bindings.json" \
+     --verify
+   ```
+
+   It renders the wrapper again from the same inputs and compares both the
+   wrapper and its sidecar byte-for-byte with the installed files. **rc 0**
+   prints `VERIFIED <path> sha256=<64 hex>`. **rc 3** prints `FAIL wrapper
+   bytes differ from re-derivation: re-derived sha256=… installed sha256=… at
+   <path>`, with `<absent>` in place of the installed digest if the file is
+   missing. Emission is deterministic, so a difference means an input drifted —
+   the tracked chain, the frozen calibration plan, the identity-epoch or
+   T1-bindings bytes, or the plan's own coordinates. Do not re-emit over the
+   difference; find it.
+5. **Syntax-check the wrapper, then install the plan.**
+
+   ```zsh
+   /bin/zsh -n "$NIGHT_ROOT/chain.zsh"
+   ```
+
+   `zsh -n` parses the file and runs none of it; rc 0 is the only acceptable
+   result. Then install the plan (§1.4). From here the plan pins the wrapper's
+   digest and the wrapper pins the chain's, so the plan's attestation reaches
+   the bytes that actually capture.
+
+One wrapper per night: three nights means three plans, three session IDs and
+three wrappers, and the generator refuses to reuse one wrapper across plans.
 
 ### 1.2 WINDOW_MAX_S, with the arithmetic
 
@@ -316,8 +530,37 @@ This is an operational allocation, not a measured completion guarantee. Do not
 shorten the settle, the cadence, the slot count or the capture budget to fit a
 window; shorten nothing and move `t0` earlier instead.
 
+**The generator's floor under this allocation.** `gen_derivation_night.py`
+refuses to emit a wrapper at all unless the window can hold the programmed
+span plus a **pre-settle allowance** of 300 s. The pre-settle allowance is the
+first of the three margin items above, isolated and made mandatory: the time
+spent INSIDE the window but BEFORE the settle begins — the chain's input
+preflight, its `--phase pre-reserve` readiness check and the session
+reservation, plus the driver's own gate work before it starts the chain at all.
+The refusal is arithmetic, and its message states both numbers:
+
+```
+required window = programmed span + pre-settle allowance
+                = 7680 + 300
+                = 7980 s          ← the generator's hard floor for 12 slots
+```
+
+`window_max_s 3600 < required 7680 + 300 = 7980 s: … lengthen the window rather
+than shortening the schedule` is what a too-short window prints. **7980 is a
+floor, not a recommendation: 9000 s remains the value to author**, because 7980
+leaves nothing for the second margin item — per-capture overrun beyond 600 s,
+which pushes every later slot later and is the realistic way a night loses its
+last slot to `window_exhausted`. A `--allow-slot-count` departure recomputes
+this floor from the new slot count rather than bypassing it.
+
 **The dead-man check.** The rule is `t0 + window_max_s + 300 < the next 07:00`,
-where 300 s is the courier's allowance and 07:00 is the dead-man minute. Worked
+where 300 s is the **courier allowance** and 07:00 is the dead-man minute. Two
+different 300 s budgets appear in this section; they are unrelated and happen
+to share a number. The pre-settle allowance above is spent INSIDE the window,
+before the settle. The courier allowance is spent AFTER the window ends: it is
+the time the driver reserves for the courier to send the night's result before
+the dead-man fires. Neither is a substitute for the other, and widening the
+window consumes dead-man slack while widening nothing else. Worked
 with real numbers, using the coordinates the prior night's runbook 68 pinned
 purely as an arithmetic example (`t0 = 2026-09-12 02:56:00 PDT`, epoch
 `1789206960`; that morning's 07:00 is epoch `1789221600`):
@@ -378,7 +621,8 @@ There is no minimum notice interval beyond that ordering.
 Send Ed the night notice with the activation's mail tool, under its standing
 email authority, containing: plan ID; class `DIAGNOSTIC_NO_PACK`; the full H
 twice; the handback commit (= H); measurement root, night custody root and runs
-root; `t0` local and UTC; `window_max_s` = 9000; the chain digest and sidecar;
+root; `t0` local and UTC; `window_max_s` = 9000; the emitted wrapper's digest
+and its sidecar path (§1.1a), and the tracked chain's digest the wrapper pins;
 the courier deadline; the exit boundary; the planned install span; and the
 cancellation instruction — **launch needs no action from Ed unless he replies
 NO**. Record the actual send acceptance, time, message and thread IDs, and
@@ -632,13 +876,57 @@ turn that prepared the candidate.
 
 ## 5. Failure table
 
+The four tables below are in the order the night can reach them: the generator
+refuses at the desk, the wrapper refuses at launch, the chain exits during the
+night, and the writer and issuer refuse inside a capture or at the desk after.
+
+Generation-time refusals (`scripts/gen_derivation_night.py`, §1.1b step 3).
+Every one prints `FAIL <reason>` on stderr and **exits 2**, and **nothing is
+written** — no wrapper, no sidecar, no advisory sidecar. All of them are desk
+failures with no window cost:
+
+| Refusal (abridged text) | Meaning | Operator action |
+|---|---|---|
+| `emit mode requires --<flag> …` | One of the six required emit flags was omitted. | Supply it; see §1.1b step 3 for the full six. |
+| `night plan is unreadable` / `night plan is not an exact v2 plan: …` | The plan file will not read, or its key set is not exactly the v2 key set. | Re-author the plan against the §1.1 table. The generator validates through the driver's own parser, so this is the same refusal the night would give. |
+| `a derivation night is DIAGNOSTIC_NO_PACK; this plan is <class>` | The plan's `receipt_class` is something else. | A `TRANSACTION_PACK` plan launches a pack launcher instead of the plan's chain, and a `REHEARSAL_STUB` never runs its chain at all, so the wrapper would never execute. Fix the class or stop. |
+| `window_max_s <n> < required 7680 + 300 = 7980 s …` | The window cannot hold the programmed span plus the pre-settle allowance (§1.2). | Lengthen the window or move `t0` earlier. Never shorten the settle, cadence, slot count or capture budget. |
+| `plan overruns the dead-man: t0 + window_max_s + 300 = <n> is not before the next local 07:00 = <n>; move t0 earlier` | The §1.2 dead-man arithmetic fails. | Move `t0` earlier. Never raise `window_max_s` past the strict maximum and never move the dead-man. |
+| `--out <path> is not the plan's chain_path '<path>'` | An output path other than the plan's `chain_path` was requested. | Do not pass `--out`. The refusal exists so the plan and the artifact cannot disagree. |
+| `plan chain_sha256_path '<path>' is not '<chain_path>.sha256'` | The plan's sidecar path is not the wrapper's path plus `.sha256`. | Fix the plan; this is stricter than the driver, and it refuses rather than mis-writing. |
+| `slot count <n> is not the pre-registered 12; pass --allow-slot-count with --slot-count-ruling <ref> to override` | A slot count other than twelve without the two-flag override. | Use twelve. A departure needs a named written ruling and is announced on stderr and in the wrapper's own header. |
+| `--allow-slot-count requires --slot-count-ruling <ref>` / `slot-count ruling reference must be one line of [A-Za-z0-9._:/#@ -]` | The override was requested without an authority, or with one that is not a single line of ordinary reference characters. | Name the ruling in one plain line. The reference is interpolated into the wrapper's header, so a multi-line paste could open a comment and start a live line. |
+| `<field> contains the census substring 'codex' \| 'claude' \| 't3': …` | Some emitted literal — a plan ID, session ID, window ID, evidence root ID, frozen plan ID, or any absolute path — contains one of the three substrings the night's own agent census matches. | Rename it. The census runs every 30 s against the process table and would match the wrapper's own command line and kill the night. |
+| `<field> must be an absolute path: …` | A path literal is relative. | Use absolute paths everywhere; the wrapper runs with no useful working directory. |
+| `frozen calibration plan is unreadable or carries no plan_id` / `a pinned input is unreadable: …` | The frozen calibration plan, the identity-epoch JSON, the T1-bindings JSON, or the tracked chain inside the clone could not be read. | Re-check §0.8 and the night root's contents. The chain is read from the CLONE, so this also catches a mis-cut clone. |
+| `--verify`: `FAIL wrapper bytes differ from re-derivation: …` (**rc 3**, not 2) | The installed wrapper or its sidecar is not what these inputs render (§1.1b step 4). | An input drifted. Find which — chain, frozen plan, identity epoch, T1 bindings, or the plan's coordinates. Do not re-emit over the difference. |
+
+Launch-time refusals (the emitted wrapper, §1.1a). Every one prints
+`FAIL <reason>` on stderr and **exits 1** before the session is opened, so no
+window time and no ledger state is spent. On an agent-free night the only
+record is `<NIGHT_ROOT>/night/chain.stderr.log` — read it first:
+
+| `FAIL <reason>` | Meaning | Operator action |
+|---|---|---|
+| `measurement_root is required` / `must be an absolute path` / `contains control characters` / `measurement_head must be a full 40-character lowercase SHA-1` | The driver's four-variable environment was malformed. | Should be impossible from a valid plan; treat as a driver or plan defect and escalate before re-arming. |
+| `night plan id does not match the wrapper` | `NIGHT_PLAN_ID` is not the plan this wrapper was frozen against. | The wrong wrapper was pinned, or a wrapper was reused across nights. Re-emit per night (§1.1b). |
+| `measurement_root does not match the wrapper` / `measurement_head does not match the wrapper` | The plan's clone path or head is not the one baked in at arm time. | The plan was edited after emission, or the wrong clone was named. Re-cut, re-author, re-emit. |
+| `checkout HEAD cannot be read` / `checkout HEAD does not equal measurement_head` | The clone is gone, is not a repository, or moved off H. | Stand down. Re-cut the clone at H (§0.2) and re-verify §0.8. |
+| `measurement venv Python is missing or not executable` | `<CLONE>/.venv/bin/python` is absent. | The clone was renamed or its venv never built; renaming moves editable-install absolute paths (§0.2). |
+| `frozen calibration plan is missing` / `identity epoch json is missing` / `t1 bindings json is missing` | A desk-produced input is not in the night root. | Produce it before arming (§0.8) — this is the failure that open question makes likely. |
+| `frozen plan is not valid JSON` / `frozen plan has no plan_id` | The frozen calibration plan is corrupt. | Re-freeze at the desk; do not hand-edit. |
+| `frozen plan id does not equal the arm-time literal` / `frozen plan bytes do not equal the arm-time digest` | The plan file in the night root is not the one the wrapper was generated from — a swapped or re-written file. | Stop and account for the change. Then re-emit and re-`--verify`; never edit the wrapper. |
+| `identity epoch bytes do not equal the arm-time digest` / `t1 bindings bytes do not equal the arm-time digest` | One of the two files whose CONTENTS are copied into every slot record changed after emission. | Same: account for it, re-derive both (§0.8), re-emit, re-`--verify`. |
+| `tracked derivation chain bytes do not match the arm-time digest` | The capturing chain inside the clone is not the reviewed bytes — an uncommitted edit, or a clone at the wrong head. | Stand down the night. This is the tripwire §0.8's clean-tree check exists to keep from ever firing at 03:00. |
+| exit 1 with **no** `FAIL` line, on a `:?required` guard | The tracked chain ran without the wrapper's environment — i.e. the plan pinned the tracked chain directly instead of the emitted wrapper. | Re-author the plan per §1.1: `chain_path` is `<NIGHT_ROOT>/chain.zsh`. No window time was spent. |
+
 Chain exits (`scripts/night_chains/calibration_derivation_only.zsh`):
 
 | Signal | Meaning | Operator action |
 |---|---|---|
 | exit 64 | A knob (`SLOT_COUNT`, `SETTLE_S`, `SLOT_CADENCE_S`, `SLOT_CAPTURE_BUDGET_S`, `WINDOW_END_EPOCH_S`) was not a non-negative integer string, or a positivity check failed. Refused before the settle, the reservation and any operator-log write. | The environment or plan is malformed. No window time was spent and no partial night exists. Fix at the desk; author a fresh plan for a later night. |
 | exit 66 `derivation_chain_input_missing: <path>` | One of `PLAN`, `IDENTITY_EPOCH_JSON`, `T1_BINDINGS_JSON`, `CALIBRATION_LEDGER`, `LEDGER_HEAD_PIN` was absent. | The clone is incomplete or a path in the plan is wrong. Re-verify §0.2 and §0.4 before authoring the next night. |
-| exit 1 on a `:?required` guard | A required environment variable was never set. | See the `[UNVERIFIED]` note in §1.1; establish the driver's env plumbing before re-arming. |
+| exit 1 | **Ambiguous — read `chain.stderr.log` to disambiguate.** With a `FAIL <reason>` line it is a wrapper refusal (table above). Without one it is the tracked chain's own `:?required` guard, meaning the chain ran without the wrapper's environment. | Both are pre-window failures costing no window time. Resolve per the matching row above before re-arming. |
 | `readiness --phase pre-reserve` non-zero | The ledger was not ready; nothing was written and no window time was spent. It never authorizes ARM even when it passes. | Desk-repair the ledger; do not re-arm the same night on the same signature. |
 | `slot_unused … reason=window_exhausted` + `session_abort` + exit 0 | The window could not finish a slot's 480 s budget. Slots are recorded unused, never compressed or retried. | Record the count. No top-up, no fourth night (§2.4). |
 | Non-zero exit mid-night, session left OPEN | A capture or ledger call failed under `set -e`. | Desk recovery with `recover_calibration_ledger.py`; never retry inside the window. |
@@ -726,13 +1014,19 @@ files read in the bookkeeping worktree.
 | Supersession banner shape and the "read the newest activation records" instruction | `13-activation-checklist-2026-09-11.md` at the same head |
 | Integration replay RED at `51565cee` | [98-integration-replay-red.md](98-integration-replay-red.md) in this trace directory |
 | Epoch↔local conversions and the four arithmetic results in §1.2 | computed this session with `TZ=America/Los_Angeles date -r <epoch>` and shell arithmetic |
-
-Not verified, and flagged in place: the driver's derivation of
-`WINDOW_END_EPOCH_S` and of the per-slot binding argv (§1.1); the live output
-strings of `check` on this machine (§0.3); the 06:05 last-start cutoff's status
-(§1.3); the complete night-gate refusal list (§5). No dedicated test module for
-the chain exists under a `test_night_chain_*` name; the chain's tests live in
-`tests/test_issue_calibration_acceptance_generation.py`.
+| The wrapper mechanism, the thirteen + six exports, the three emitted files, the five-step arm order, the six required emit flags and their defaults, `--verify` rc 0 / rc 3, every generation-time refusal text, `PRE_SETTLE_ALLOWANCE_S = 300`, `programmed_span_s` = 7680 for twelve slots, `CENSUS_SUBSTRINGS` | `JouleWise-wt-s7-night-wrapper` HEAD: `scripts/gen_derivation_night.py` (module docstring and the symbols `programmed_span_s`, `_census_clean`, `_validated_ruling`, `_next_deadman_epoch`, `build_spec`, `render_wrapper`, `emit`, `verify`, `build_parser`, `main`) and the `derivation-night-wrapper` generated region of `docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md`. `--help` text captured this session by running that file's HEAD bytes read-only from `/tmp`. Cited by symbol, not line: S7's own finding S-2 was that its line citations went stale, and its tests now resolve anchor TEXTS instead |
+| Driver hands the chain four variables and no argv (`scripts/run_night.py:430–444`, `tests/test_run_night.py:348–380`); the gate binds the clone by `HEAD` only (`joulewise/night_gate.py:1006–1029`); the reservation copies the identity-epoch and T1-bindings CONTENTS verbatim into every slot record (`scripts/reserve_calibration_window_bracket.py:216–220`) | scout report 101 §0–§2 and S7 contract-lens refuter report 105 §2, §5 (`/tmp/magistrate-96bfeca7/reports/`). Line numbers are quoted as those reports recorded them and were not re-derived by this seat |
+| Clean tree and identity-epoch / T1-bindings provenance as arm-checklist items, and "one wrapper per night" | S7 seat report 103 §7.1–§7.4 and its fix-round-1 items B-1, B-2, S-1, S-4; refuter 105 §5 |
+
+Not verified, and flagged in place: the live output strings of `check` on this
+machine (§0.3); the producer and custody location of `identity_epoch.json` and
+`t1_bindings.json` (§0.8); the 06:05 last-start cutoff's status (§1.3); the
+complete night-gate refusal list (§5). **Closed since revision 1:** the driver's
+supply of the chain environment and of the per-slot binding argv (§1.1, §1.1a) —
+there is no such driver code by design, and the emitted wrapper supplies both.
+The wrapper generator's tests live in `tests/test_gen_derivation_night.py`; the
+chain's own tests live in `tests/test_issue_calibration_acceptance_generation.py`
+under no `test_night_chain_*` name.
 
 ---
 
@@ -760,9 +1054,19 @@ means. A term is listed only if it does technical work.
 | `[QUIET-MAC]` | §0.6 | The agent-free machine discipline a capture night runs under. |
 | measurement root / measurement head | §0.2, §1.1 | The fresh clone both night agents are installed from, and the commit it is detached at. |
 | `DIAGNOSTIC_NO_PACK` | §1.1 | The receipt class for a night with no measurement pack; only C2 is not-applicable. |
+| clean tree | §0.8 | The measurement clone has no uncommitted change of any kind: `git status --porcelain` prints zero bytes. |
+| wrapper | §1.1a | The generated zsh file, one per night, that carries the night's whole environment as literal `export` lines, authenticates its pinned inputs, and then `exec`s the tracked chain. The plan's `chain_path` names it. |
+| night root | §1.1a | `<NIGHT_ROOT>`, the custody directory the plan calls `custody_root`; the three emitted files and the night's desk-produced JSON inputs live in it. |
+| sidecar | §1.1a | A small companion file holding another file's SHA-256 in `shasum` output form — the digest, two spaces, a name. |
+| advisory (of the third emitted file) | §1.1a | Written for a human's hand-check only; nothing reads it at launch, so deleting or rewriting it changes nothing about what the night will accept. |
+| tripwire | §1.1b step 4 | A check that writes nothing and exists only to fail loudly if an input drifted — here, `--verify` re-deriving the wrapper and comparing it byte-for-byte. |
+| `zsh -n` | §1.1b step 5 | A syntax check: zsh parses the file and runs none of it. |
+| census substring | §1.1b, §5 | `codex`, `claude` or `t3` — the strings the night's own 30 s process census matches; the generator refuses to bake any of them into an emitted literal. |
+| programmed span | §1.2 | Chain start to the end of the last slot's capture budget: settle + (slots − 1) × cadence + one budget = 7680 s for twelve slots. |
+| pre-settle allowance | §1.2 | 300 s INSIDE the window and BEFORE the settle — the chain's input preflight, its pre-reserve readiness check and the session reservation, plus the driver's pre-launch work. The generator refuses a window below programmed span + this. |
 | start-to-start cadence | §1.2 | Slot `d(k+1)` starts 600 s after `dk` STARTED; a long capture is never caught up by compressing a later slot. |
 | window_max_s / `WINDOW_END_EPOCH_S` | §1.2 | The plan's window length in seconds, and the exclusive window end the chain enforces. |
-| courier / courier deadline | §1.2, §2.1 | The process that emails the night's result, and the 300 s allowance the deadline arithmetic reserves for it. |
+| courier / courier deadline / courier allowance | §1.2, §2.1 | The process that emails the night's result; the 300 s the deadline arithmetic reserves for it AFTER the window ends. Distinct from the pre-settle allowance, which is spent inside the window; the two share a number by coincidence. |
 | plan span / exit boundary | §0.6, §1.3 | The interval from `t0 − 25 min` in which no agent may be resident; the activation's hard exit time. |
 | census | §0.6 | The enumerated process inventory proving no foreign or own agent is live. |
 | T1 bindings | §0.3 | The toolchain-identity block a finalization receipt records, including the MLX version in force. |
```
