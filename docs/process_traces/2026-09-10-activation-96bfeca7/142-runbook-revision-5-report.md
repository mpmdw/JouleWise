# 142 — derivation-night runbook, revision 5 (writer seat, dictated fills)

- File edited, in place, and nothing else:
  `/Users/edr/code/JouleWise-wt-s8-night-inputs/docs/phase_2/derivation_night_runbook.md`
- `git status --porcelain` in that worktree: `M docs/phase_2/derivation_night_runbook.md` — one file.
- Size: 1593 → 1996 lines. No git operations performed.
- Kept: the DRAFT banner, hyphenated filenames, symbol-and-record citations,
  the verified arithmetic. Verified absent after the edit:
  `grep -nE 'PR #|Ran [0-9]+ tests|\bCodex\b|\bSol\b|\bAstra\b|\bOpus\b|\bFable\b'` → zero hits;
  `grep -nE '\.py:[0-9]+|\.md:[0-9]+|\.zsh:[0-9]+'` → zero hits.

## Changelog as it now stands at the top of the file

> **Changelog — revision 5 (2026-09-10), one line: the operational defects a
> contract review found are closed, so the arm can be run from this file alone,
> without the operator supplying values the file never defined.** What that
> forced: §0.2 now exports every variable a later runnable block interpolates —
> `NIGHT_DATE`, `PLAN_ID`, `NIGHT_ROOT`, `STAGE`, `STAGED_PLAN`, `SESSION_ID`,
> `EVIDENCE_ROOT_ID`, `CALIBRATION_PLAN`, `CALIBRATION_LEDGER` and
> `LEDGER_HEAD_PIN` — each with a gloss and a rule for choosing it, and creates
> the night root rather than telling the operator it must already exist; the
> night plan is authored at a STAGING path and reaches its discoverable place
> only at §1.4's atomic move, which removes the collision between §1.1b's
> `--plan` INPUT and §1.4's "target must not pre-exist", and keeps §0.7's
> discoverability precondition true; §1.4 carries the install commands
> themselves instead of deferring to an unlocated runbook, and every citation of
> that runbook is now a repository path; §1.5 states the frozen checkout triple's
> exact contract fields and the new §2.0 derives from them every further value
> the harvest needs; `fence` is split into its two senses and the watchdog sense
> is stated as the contract states it, which is why a `t0` inside the
> 02:45–03:30 belt is correct rather than forbidden; `Session` is disambiguated
> from the thing a fence blocks; `wrapper`, `night root` and `tracked chain` are
> built in §Terms before §0 uses them, and §0.5 gives the tracked chain's path
> and its `shasum` command at first use; and §0.8 always names which writer it
> means.

Revision 4's paragraph was demoted to the same past-tense form as revision 3.
The "two `[UNVERIFIED]` blocks remain" note now says *unchanged in substance*
and discloses the one word changed inside §1.3 (its arm-runbook citation gained
a path, like every other citation of that runbook).

## Fix by fix, with the source each claim was verified against

### S-1 — every variable a runnable block uses is built before use

New subsection in §0.2, "Every other variable this runbook's commands
interpolate": one `zsh` block assigning `PLAN_ID`, `SESSION_ID`,
`EVIDENCE_ROOT_ID`, `NIGHT_ROOT`, `STAGE`, `STAGED_PLAN`, `CALIBRATION_PLAN`,
`CALIBRATION_LEDGER`, `LEDGER_HEAD_PIN`, plus a ten-row table giving each one
line and the rule for choosing it. `NIGHT_DATE` was added to §0.2's first block
(it was already interpolated into `MEASUREMENT_ROOT` as a bare `<NIGHT_DATE>`)
and its `YYYYMMDD` meaning stated, which also closes the review's Minor note on
that format. The block additionally asserts the two directories do not
pre-exist, creates them, and asserts they share a filesystem device.

Sources:
- `CALIBRATION_LEDGER` / `LEDGER_HEAD_PIN` values — `scripts/gen_derivation_night.py`,
  the `--ledger` and `--head-pin` defaults in `build_parser` (`<measurement_root>/runs/…jsonl`,
  `<measurement_root>/configs/…json`), read from `--help` and from `build_spec`.
- `NIGHT_ROOT` convention and the `custody_root` identity — §1.1 plan table of
  this runbook and `build_spec`'s `window_custody_root=plan.custody_root`.
- Census-substring rule — `scripts/gen_derivation_night.py`, `_census_clean`
  (already documented in §1.1b/§5 of the runbook).
- Same-device requirement — `docs/process_traces/2026-09-10-activation-96bfeca7/12-arm-runbook-68-g2a-20260912.md`,
  §"Block B", which asserts `Path(STAGE).stat().st_dev == Path(NIGHT_ROOT).stat().st_dev`.
- Staging directory convention `/Users/edr/night-plan-staging/<PLAN_ID>` — same
  record, §"Block A" exports.

Verification of completeness: every `$VAR` inside every ```` ```zsh ```` block in
the file is now either assigned in a block, exported by §2.0's `export`
statement after its `eval`, or guarded with `:?` (`BOOKKEEPING_ROOT`). Checked
mechanically by extracting all fenced `zsh` blocks and diffing used against
assigned names.

Two runnability defects found while doing this and fixed, both because the
§0.8 invocation must run *as written*:
- `test ! -e X && test ! -L X` does not abort under `set -e` when the left side
  fails (POSIX exempts all but the last command of an AND-OR list), so the
  existing §0.2 clone guard would have sailed past an existing clone. Both that
  guard and the new one are now separate statements, and the reason is stated in
  the text.
- The census check is an `if … then … exit 1 fi`, not `! pipeline`, for the same
  reason (`set -e` is likewise ignored for a pipeline beginning with `!`).
- §0.2's uncommanded "build the venv from the lock" now carries the lock-diff
  command that `test -x "$PY"` silently depended on
  (record 12, §"Block A", closing `pip freeze` diff; `env/mac-measurement-lock.txt` confirmed present).

### S-2 — the plan-path collision

§1.1b step 2 now authors the plan at `$STAGED_PLAN`; steps 3 and 4 pass
`--plan "$STAGED_PLAN"`; §1.4 publishes to `$NIGHT_ROOT/night_plan.json`. A new
two-row table in step 2 states both paths and who reads each, followed by two
paragraphs: one establishing that the wrapper's bytes depend on the plan's
CONTENT and not its path, and one establishing that the staged path is outside
discovery.

Sources:
- `--plan` is an input at generation — `scripts/gen_derivation_night.py --help`
  ("frozen v2 night plan JSON (emit mode)"), executed; and the body, where the
  plan path is used only for `json.loads` of its bytes and every wrapper literal
  is rendered from decoded fields in `build_spec`.
- `--verify` compares against the plan's `chain_path` — same `--help`
  ("compare it byte-for-byte with the installed file at the plan's
  `chain_path`"). §1.1b step 4 now says explicitly that only the plan is staged
  and the wrapper lives in the night root, so the pre-move and post-move
  `--verify` render identically; §1.4 re-runs it for that reason.
- The move's constraints — `docs/process/MAGISTRATE_WATCHDOG.md` gives the
  discovery model, and record 12 §"Block B" gives the executed `os.replace` with
  `assert not target.exists() and not target.is_symlink()`.

§0.7 now defines "discoverable" mechanically and keeps its own precondition
true: the watchdog enumerates `*/night_plan.json` in the parent of its state
directory (`glob_plans` in `scripts/magistrate_watchdog.py`, state root
`/Users/edr/night-custody/magistrate`), i.e. exactly
`/Users/edr/night-custody/*/night_plan.json`, one level, that filename. The
staging root `/Users/edr/night-plan-staging/<PLAN_ID>/` is not one level below
`/Users/edr/night-custody`, so it is never enumerated. The night's own driver
discovers nothing at all — launchd passes `scripts/run_night.py` its `--plan`
(`required=True`), so it reads the file it was installed with. §0.7 gains a
one-line check (`print -rl -- /Users/edr/night-custody/*/night_plan.json(N)`,
expected empty).

### S-3 — the frozen checkout triple

§1.5 now states it as the contract does: **exactly `(plan_id, root, head)`**,
three fields, carried on line 9 of the relaunch prompt as
`@@FENCED_CHECKOUTS@@`, which the watchdog itself renders at every launch as a
deterministic JSON list. The runbook cannot widen it, so the remaining harvest
coordinates are *reconstructed*, and a new **§2.0** does that as the first step
of the morning harvest: a runnable block plus a six-row table giving each
value's provenance.

- Derived from the triple: `NIGHT_ROOT` (convention, then confirmed against the
  published plan's `custody_root`), `WINDOW_CUSTODY_ROOT` (= the night root;
  `build_spec` sets the wrapper's export from `plan.custody_root`),
  `CALIBRATION_LEDGER` and `LEDGER_HEAD_PIN` (the generator's `--ledger` /
  `--head-pin` defaults, clone-relative).
- Not derivable, therefore read back out of the wrapper: `SESSION_ID`,
  `EVIDENCE_ROOT_ID`, `PLAN`, `RUNS_ROOT`. The wrapper carries all four as
  single-quoted `export` literals (`render_wrapper`'s export list; shape
  confirmed in the generated `derivation-night-wrapper` region of
  `docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md`). The
  block verifies the wrapper against its sidecar with `shasum -a 256 -c` before
  reading anything out of it, and §2.0 states that a failed check is a stop.
- §2.1/§2.2/§2.4's commands now interpolate `$SESSION_ID` and `$PLAN` rather
  than `<SESSION_ID>` / `<PLAN>`; §4.1's `<S1>…<S3>` are glossed as the three
  nights' `SESSION_ID` values recovered the same way.

Sources: `docs/process/MAGISTRATE_RELAUNCH_PROMPT.md` (the
`@@FENCED_CHECKOUTS@@` line and the movement prohibition on the line after);
`docs/process/MAGISTRATE_WATCHDOG.md`, §"Complete write inventory" (rendering
rule, `plan_conflict`, post-arm move invalidates the pin);
`scripts/gen_derivation_night.py` (`WrapperSpec`, `render_wrapper`,
`build_spec`, parser defaults).

### S-4 — §1.4 gets real commands, and every runbook-68 citation gets a path

§1.4 is rewritten with a numbered foreground block: pins re-asserted, notice
evidence required (`$STAGE/notice-evidence.txt`), wrapper `--verify`, staged-plan
assertions through `NightPlan.from_mapping`, same-device assertion, the final raw
census, the `os.replace` publication, `scripts/install_night_agent.sh --plan
--hour --minute`, `launchctl list`, a label assertion, the post-install `night/`
inventory baseline, `plutil -p` of both plists, and a `cmp` against the retained
staged copy. A separate rollback block gives the `--uninstall` / preserve /
`cmp` / unpublish sequence and says why the retained copy matters.

Sources:
- `docs/process_traces/2026-09-10-activation-96bfeca7/12-arm-runbook-68-g2a-20260912.md`,
  §"Block A" (exports, staging, preconditions) and §"Block B" (notice, census,
  move, install, inspect, rollback) — the executed template, cited by path at
  first use and again in the rollback paragraph and the §7 fact table.
- `scripts/install_night_agent.sh` — read directly: one invocation installs both
  `com.joulewise.night` and `com.joulewise.night.deadman`, `--uninstall` removes
  both, and it refuses `--hour` equal to the dead-man hour with
  `refusing --hour <h>: it is the dead-man hour`. That refusal is quoted in the
  runbook as the reason the dead-man's firing can never be the night's.
- `joulewise/night_gate.py`, `_PLAN_KEYS` — every field the assertion block
  reads (`custody_root`, `receipt_class`, `registration_path`,
  `authored_epoch_s`, `chain_path`, `chain_sha256_path`) is a real v2 key.
- The two changes from record 12 are named in the text: this night's plan
  assertions, and this lane's wrapper `--verify` in place of that runbook's
  G2-a runsheet render.
- The `night/` inventory read is tolerant of the directory not yet existing
  (`sorted(night.iterdir()) if night.is_dir() else []`) so the block cannot
  raise at the one moment recovery matters.

Other citations pathed: §0.2's "Fresh clone at H", §1.2's example coordinates,
§1.3's `[UNVERIFIED]` 06:05 note, and the §7 fact-table row for records 11 and 12.

### S-7 — `fence`, and `Session`

§Terms now carries two entries. **Fence (watchdog sense)** — a period in which
the relaunch watchdog refuses to LAUNCH OR ADOPT a magistrate *agent* session;
three things fence: a valid plan's span (opening at the closed boundary
`t0 − 25 min`), the fixed local belt `[02:45:00, 03:30:00)`, and the fixed local
dead-man minute `[07:00:00, 07:01:00)`, both fixed intervals half-open. The
entry states in bold that a fence forbids an agent starting, never a night
running, and that the night's own two LaunchAgents are not magistrate sessions.
**Blindness fence** is a separate entry, marked as a different object under a
similar name, with the convention that unqualified "fence" means the watchdog
sense; §2.3's sentence now reads "The blindness fence is installed in code".

The 02:56 consistency is stated where the term is built: a capture night wants
precisely the hour in which no agent can be launched or adopted.

Sources: `docs/process/MAGISTRATE_WATCHDOG.md`, §"Safety model and state
machine" (`FENCED`: "a plan span, the 02:45–03:30 belt, or the 07:00 minute
forbids launch"; `FENCED` with `adopt=False`) and §"Fence and deadlines" (the
half-open intervals, the plan-span boundaries, the −25/−16/−15 table).
Corroboration that a night runs inside the belt: `docs/process/NIGHT_HANDBACK.md`,
§"Executed — rehearsal-20260909" — that night fired at 02:56 local and reached
chain exit 0.

**Session** gained a sentence: unqualified it always means the ledger object,
and the watchdog's *agent session* is always written out in full. Two stale
section names were corrected while there: `§Fences` / `§Stand-down ladder` /
`§Arming` do not exist as headings in the watchdog contract; the real ones are
§"Fence and deadlines" (intervals and boundary table) and §"Install handoff"
(the email-then-arm / Ed's-NO paragraph), and the §7 fact table now cites those.

### Nits

- `wrapper`, `night root` and `tracked chain` are now §Terms entries, built
  before §0 uses them; §8 marks them "§Terms, built §1.1a" / "§Terms, exported
  §0.2" / "§Terms" so the first-use table and the prose agree.
- §0.5 gives the tracked chain's path and a `shasum -a 256` command at the point
  `[CHAIN_SHA256]` is first demanded, and glosses `[DD]` as the registration's
  authoring day (`configs/calibration/preregistration_d079_epoch_25g83_rev1.md`,
  §"Fields filled at commit").
- §0.8 opens with the naming convention in bold — **desk-inputs writer** =
  `scripts/write_derivation_night_inputs.py`, **capture writer** =
  `scripts/validate_powermetrics_fiducial.py` — and every bare "the writer" in
  the file is now qualified. The single survivor is inside a generator refusal
  message quoted verbatim, which the convention paragraph accounts for.
- §0.8's `--out-dir` refusal remedy now points at §0.2 (which both assigns
  `NIGHT_ROOT` and creates it) instead of saying "Create it first", which also
  closes the review's ordering-circularity note.

## §8 first-use table — what changed

Rows rewritten:

| Term | Built at | One-line meaning (new text) |
|---|---|---|
| session (ledger) | §Terms | A ledger capability reserving several attempts under one open receipt at a fixed head pin. Unqualified, *session* always means this; the watchdog's *agent session* is always written out in full. |
| fence (watchdog sense) | §Terms | A period in which the watchdog refuses to LAUNCH OR ADOPT a magistrate agent session: a plan span, the half-open belt `[02:45:00, 03:30:00)`, or the half-open dead-man minute `[07:00:00, 07:01:00)`. It forbids an agent starting, never a night running — which is why a `t0` of 02:56 is inside the belt and correct. |
| wrapper | §Terms, built §1.1a | (unchanged text; built-at corrected) |
| night root | §Terms, exported §0.2 | (unchanged text; built-at corrected) |
| frozen checkout triple | §1.5 | Exactly `(plan_id, root, head)` — the three fields the watchdog renders into the relaunch prompt's `@@FENCED_CHECKOUTS@@` list. It fences those checkouts against movement; §2.0 reconstructs every further harvest coordinate from it. |

Rows added:

| Term | Built at | One-line meaning |
|---|---|---|
| blindness fence | §Terms, enforced §2.3 | The code-enforced prohibition on reading any captured value before night 3's ledger session is terminal. Not an interval; no clock clears it. |
| tracked chain | §Terms | `scripts/night_chains/calibration_derivation_only.zsh`, the committed script that runs the twelve captures — identical in every clone at `H`, unlike the per-night wrapper. |
| capture writer | §0.8 | `scripts/validate_powermetrics_fiducial.py`, run twelve times by the chain during the night. Distinguished from the desk-inputs writer everywhere in this file; a bare "writer" survives only inside a tool's own quoted message, where it means this one. |
| `<NIGHT_DATE>` | §0.2 | The eight-digit `YYYYMMDD` of the date `t0` falls on; every dated name in the arm is built from it. |
| staging path / `$STAGED_PLAN` | §0.2, §1.1b step 2 | `/Users/edr/night-plan-staging/<PLAN_ID>/night_plan.json`, where the plan is authored, generated from and `--verify`-ed. Outside the watchdog's discovery glob, so authoring a plan arms nothing. |
| published (plan) | §1.4 | The one instant a night becomes discoverable: `os.replace` of the staged bytes into `<NIGHT_ROOT>/night_plan.json`, a target that must not pre-exist. Everything before it is undone by doing nothing. |

`desk inputs writer` was renamed to `desk-inputs writer` throughout, table row
included.

## §7 fact table — rows added

Nine rows, one per new load-bearing claim: the §1.4 install commands (record 12
§"Block A"/§"Block B" plus `scripts/install_night_agent.sh`); the discovery glob
(`glob_plans`, and `run_night.py`'s `required=True` `--plan`); the plan as a
generation INPUT whose content, not path, determines the wrapper bytes (`--plan`
help text and `build_spec`); the wrapper's `WINDOW_CUSTODY_ROOT` / `RUNS_ROOT` /
`CALIBRATION_LEDGER` / `LEDGER_HEAD_PIN` derivations (`WrapperSpec`,
`build_spec`, parser defaults); the frozen checkout triple's three fields
(`MAGISTRATE_RELAUNCH_PROMPT.md` and the watchdog's §"Complete write
inventory"); the fence semantics plus the 02:56 rehearsal corroboration; the
frozen calibration plan's provenance (`docs/phase_2/window_runbook.md`, the
ALPHA `window.env` example); `[DD]`; and the environment lock diff.

## Test

```
$ cd /Users/edr/code/JouleWise-wt-s8-night-inputs && \
  PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_docs_freshness
...............................
----------------------------------------------------------------------
Ran 31 tests in 0.656s

OK
rc=0
```

## Open, and deliberately not closed here

- The review's C1–C5 enumeration (§2.1 names the row set without listing the
  five conditions) is untouched; it was outside the named fixes.
- S-5 and N-1 are one-line bench fixes inside
  `scripts/write_derivation_night_inputs.py` and were out of this seat's write
  scope.
- The two `[UNVERIFIED]` blocks stand, substance unchanged.
- `EVIDENCE_ROOT_ID` still has no derivable default; §0.2 says so and requires
  the literal plus the record that registers it in the arm materials, and §2.0
  recovers it from the wrapper rather than guessing.
