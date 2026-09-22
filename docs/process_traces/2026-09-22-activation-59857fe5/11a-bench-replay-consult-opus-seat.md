# Design consult — §Q7 daytime bench replay (Opus seat, activation 59857fe5)

Read: cold gate 3 ruling 10 §Q7 (P7.1–P7.3); A269 ruling 10 §Q3 replacement R6 clause and
§Q4/A1; `quiet_predicate_campaign.py` (`execute`, `establish_network_time_off`,
`attestation_timeout_s`, `cleanup_budget_s`, `pilot_summary`),
`scripts/sample_quiet_predicate_evidence.py` (`collect`, `PowerRecorder`, `power_argv`,
`network_time_provenance`, `main`), `scripts/run_night.py` (`_chain_environment`),
all at `489b0953`. No writes outside this file; no sudo, no `log`, no powermetrics, no tests run.

**What the replay actually measures.** Under v2 the gap is `slot_pitch_s − envelope_s` = 20 s,
`cleanup_budget_s` = 15 s, and under the Q3 ruling `attestation_timeout_s` = `max(5, 20−15)` = 5 s.
The budget is exactly the gap with **zero slack**. Drift does not accumulate (`scheduled = first +
(i−1)·pitch` is absolute), so each slot's `start_drift_s` is its predecessor's tail overhang:
collector reap + `cleanup_groups` census + `log show`. The replay is the first and only measurement
of that tail's wall cost against a 20 s gap — which is also the unmeasured-cost residual the
execution lens raised as B1. Design for that, not merely for a number ≤ 0.5.

## Q1 — Where the seam lives, and what pins the production path

**Recommended: exactly one seam, in the sampler, substituting the recorder's *argv*, not the
recorder class; and zero seam in `quiet_predicate_campaign.py` for the sudo path.**

*Collector side.* The collector is a fresh subprocess (`execute` launches
`[sys.executable, "-B", <sampler>, "collect", …]`), so an environment variable is the only channel
into it. But do not swap the class: `PowerRecorder` builds `self.argv = power_argv(path,
interval_ms)` in `__init__` and everything else — first-complete-`</plist>` wait, `identity()`/`ps`
lookup, the `threading.Timer` deadline, `request_stop` SIGTERM, the 5 s kill timer, `finish()`'s
parse and `align_frames` anchor derive — is argv-independent. Substituting only `power_argv`'s
return value leaves **every line of `PowerRecorder` executing unmodified**, which is strictly more
faithful than the sketch's `ReplayRecorder` and shrinks the seam to ~8 lines:

```python
REPLAY_ENV = "EVIDENCE_POWER_RECORDER_REPLAY"          # absent on every real night
def power_argv(path, interval_ms=100):
    source = os.environ.get(REPLAY_ENV)
    if source:                                          # bench replay only; never evidence
        return [sys.executable, "-B", str(REPO_ROOT / "scripts/replay_powermetrics_frames.py"),
                "--source", source, "--out", str(path), "--interval-ms", str(interval_ms)]
    adapter = object.__new__(pm.PowermetricsTelemetryAdapter); …   # unchanged
```
plus `session["recorder_kind"] = "replay" if os.environ.get(REPLAY_ENV) else "powermetrics"` and
`session["replay_source_sha256"]`, written into `session.json` before any child is launched.

*Chain side.* No change is needed at all. `execute(plan, protocol, night_dir)` is callable
in-process, and the module already documents and tests the rebinding seam: "*A test substitutes its
own executables by rebinding these names — PATH cannot fake an absolute path*" (`SUDO`,
`SYSTEMSETUP`, `:24-34`). The bench driver imports the module, rebinds `campaign.SYSTEMSETUP` to a
tracked stub, and calls the real `execute`. `establish_network_time_off`, `set_network_time`,
`write_control_record`, `restore_network_time` and the collector's `network_time_provenance()`
check then all run for real, with no sudo and nothing toggled. The stub must print exactly
`EXPECTED_NETWORK_TIME_OFF_STDOUT` or every envelope refuses at exit 3 before the recorder spawns —
so gate the stub on the *same* variable: prints the OFF line only when `REPLAY_ENV` is set in its
own environment, else exits 2 with empty stdout. One variable, two interlocked uses.

*What pins "untouched when absent":* R1/R2 below — `power_argv()` with the variable absent returns
an argv containing `sudo` and `pm.POWER_METRICS` and `collect` records `recorder_kind:
"powermetrics"`; counterfactual = give the variable a default value, test fails.

## Q2 — Fail-closed: exact refusal points

1. **Arm / driver.** `scripts/run_night.py`: refuse the night with a named reason if `REPLAY_ENV`
   is present in `os.environ` at driver start (a refusal, not a silent fix), **and** add it to the
   `_chain_environment` pop list beside `NIGHT_VERIFY_ONLY` / `EVIDENCE_PROCESS_JOURNAL` (:590-593)
   so an inherited desk-shell value can never reach the chain. Both: pop is defence, refusal is
   evidence.
2. **Run / collector.** The seam itself refuses the combination "replay variable set **and**
   `EVIDENCE_PLAN_PATH`/`NIGHT_PLAN_ID` present" — a replay recorder inside a real night's chain
   environment is a protocol failure, never a degraded run.
3. **Summary / harvest.** `pilot_summary` already reads each envelope's `session.json` (:855).
   Three lines there: `recorder_kind` not `"powermetrics"` → `raise ValueError`. In `execute`'s
   `finally` that sets `outcome, error = "refused", …`, writes `refusal.json`, and returns 2. A
   refused night is *already* unlabelable by the harvester, so **no harvester change is needed**.
   Crucially, `evidence_envelopes.jsonl` is appended per slot inside the loop, so the twelve
   `start_drift_s` values survive the refusal intact.
4. **Structural, free.** The archived frames carry the 2026-09-22 02:xx wall timestamps; emit them
   **verbatim** and every envelope's anchor derives `unresolved`. Never rewrite frame timestamps to
   "now" — that would fabricate measurement data and is the one change that could make replay output
   resemble evidence. Verbatim bytes make the output self-identifying (its sha256 is the archived
   plist's).

**Do NOT add a new exclusion reason** (e.g. `replay_recorder`). A269 §Q2 byte-pins the
registration's `exclusions` list and rules that a pinned list omitting an emitted reason "must never
exist on main"; a new reason forces a registration v3 and reopens a just-ruled artifact. Refuse the
summary instead — same fail-closed effect, zero registration cost.

## Q3 — Its own PR, after the transaction

**Own PR, merged after the D-138 transaction, replay executed at that PR's merge sha.** Three
reasons: (a) §Q7 P7.1 itself orders the replay "executed after merge, at the merged head", so the
replay code cannot be a precondition of that merge; (b) the transaction's ruled nine-part proof set
(C1 digests, neutrality re-execution at the rebased head, clause-(3) test-diff statement) would have
to be re-run wholesale if unrelated sampler/`run_night` bytes joined the tree; (c) the sampler is
manifest-pinned only via `manifest_for`'s per-file digests computed **at arm time** — the byte-pinned
registration pins `chain_source_sha256` (the zsh) only, so a sampler change needs no re-pin and no
registration ruling. Consequence to state in the arm notice: **main must be frozen between the
replay PR's merge and the arm**; any commit landing in between voids P7.1 and costs another 2 h 14.

## Q4 — Scaled smoke yes, as a smoke only; the full run's artifact

A scaled rehearsal is admissible and advisable, and is *not* evidence for the bar: the bar is
produced by the 20 s gap, and any scaling changes the gap. Run it as plumbing proof —
`execute(plan, {**frozen, "envelope_s": 30, "slot_pitch_s": 50, "envelopes": 3, "settle_s": 10},
…)`, ~3 minutes; `execute` takes `protocol` as an argument so no digest is bypassed, and A269
regression #1 already establishes the scaled-protocol pattern. The full run uses `frozen_protocol()`
verbatim.

Artifact `docs/process_traces/2026-09-22-activation-59857fe5/<nn>-bench-replay-start-drift.md` must
carry the ruled five items (merged sha; archived plist sha256 — the ruling says *the* plist,
singular, so pin **one** and reuse it for all twelve slots; twelve chain-level `start_drift_s`; the
max; `max ≤ 0.5 s`) **plus**: `git status --porcelain` empty at that sha; the registration digest and
the derived gap/cleanup/attestation budget (20/15/5 s); the twelve **session-level**
`start_drift_s` and their max — A269 §A1 rules the R6 bar is the session-level figure and it runs
~0.12–0.16 s higher, so a chain-level pass with a session-level figure above 0.5 s must be escalated,
not silently passed; the twelve `network_time_attestation_wall_s` and their max against the 5 s
timeout (this is the B1 residual's first measurement); per-slot cleanup wall and `cleanup_proven`;
the final outcome (`refused`, reason = replay recorder) as proof of the interlock; and the machine
state at start/end (`uptime`, `pgrep -c claude`). On load: extra daytime load **lengthens** the
inter-slot tail, so a pass under load is a fortiori evidence for a quiet night, while a **fail** under
load is inconclusive and must be retried on a census-clean machine. Record the load so that
distinction can be made after the fact.

## Q5 — Brief skeleton

`WRITE_SCOPE: ["scripts/sample_quiet_predicate_evidence.py", "scripts/replay_powermetrics_frames.py", "scripts/bench_replay_start_drift.py", "scripts/bench_replay_systemsetup_stub.py", "scripts/run_night.py", "joulewise/quiet_predicate_campaign.py", "tests/test_sample_quiet_predicate_evidence.py", "tests/test_quiet_predicate_campaign.py", "tests/test_run_night.py"]`
(linked worktree, never canonical; the archive path is read-only input and must not be copied.)

Items: (1) `power_argv` seam + `recorder_kind`/`replay_source_sha256` in `session.json`;
(2) feeder `replay_powermetrics_frames.py` — stream the source incrementally (never load 130 MB),
split on NUL, write one frame per `--interval-ms` to `--out`, hold until SIGTERM when the source is
exhausted, exit cleanly on SIGTERM, emit bytes verbatim; (3) `bench_replay_systemsetup_stub.py`
gated on the same variable; (4) driver `bench_replay_start_drift.py` — assert clean tree at the
expected sha, build the `NightPlan`, rebind `campaign.SYSTEMSETUP`, set the variable, call the real
`execute`, then read `evidence_envelopes.jsonl` and the twelve `session.json` files and emit the
artifact markdown with a PASS/FAIL verdict at 0.5 s; (5) `run_night` pop + refusal;
(6) `pilot_summary` refusal; (7) the seven regressions.

Regressions (counterfactual → production call site): **R1** variable absent ⇒ argv contains `sudo`
and `POWER_METRICS`, `recorder_kind == "powermetrics"` (default-on seam → fail; `collect`
recorder_factory, sampler ~:912). **R2** variable set ⇒ argv is the feeder, and no `sudo`/
`powermetrics` token anywhere (leave `power_argv` unmodified → fail; `PowerRecorder.__init__`).
**R3** feeder output byte-identical to the source prefix, parses under `parse_frames`, clean SIGTERM
exit (rewrite timestamps to now → byte assert fails; feeder `main`). **R4** driver refuses with the
variable in `os.environ`, and `_chain_environment` output lacks the key when `os.environ` has it
(drop either → fail; `run_night:574-594`). **R5** scaled end-to-end `execute` with a stub collector
writing `recorder_kind: "replay"` ⇒ `pilot_summary` raises, `evidence_outcome.json` outcome
`refused`, rc 2, **and the twelve journal rows still present** (`"powermetrics"` → outcome
`complete`; `pilot_summary` :855). **R6** stub exits 2 with empty stdout when the variable is absent
(drop the guard → prints the OFF line → fail). **R7** verdict function FAILs on a fixture journal
carrying one 0.6 s row (compare against the 2 s abort threshold instead → PASS → fail; driver).

## Q6 — Cost

Implementation: one Sol xhigh seat, ~2–3 h including the seven regressions, plus one delta re-audit
(the seam touches two manifest-pinned files, so C-028 applies). Run: `600 + 11×620 + 600` = 8020 s =
**2 h 13 m 40 s**, plus ~1 min of start/teardown; plus the 3-minute scaled smoke first. Disk:
12 × ~130 MB ≈ 1.6 GB of replayed plists in the bench night dir — put it on local scratch, record the
sizes, delete after the artifact lands. **Nothing can be shortened without violating the ruled
text.** The 600 s settle is the only tempting cut and it is load-bearing: envelope 01's drift is
measured from `first = go + settle_s`, and cutting it means the run no longer uses the frozen
registration. The run needs no attendance — launch it detached, poll, and keep working (see the
load argument in Q4).

## Disagreements with the sketch

1. **Swap the argv, not the recorder class.** Keeps 100 % of `PowerRecorder` — deadline timer, TERM,
   kill timer, parse, anchor derive — executing production code. Smaller seam, more faithful test.
2. **No env-gated no-ops for `establish_network_time_off`/`restore`.** That would put a
   replay-shaped branch in the most safety-critical function in the chain. Use the module's existing,
   documented `SUDO`/`SYSTEMSETUP` rebinding seam from an in-process driver and run the real
   functions against a variable-gated stub — zero new branches in `quiet_predicate_campaign.py`
   except the three-line summary refusal.
3. **The replay must run the real `log show` attestation.** The sketch is silent on it. The
   attestation is the new inter-slot work that created both the A269 drift and the B1 residual; a
   replay that stubs it measures the wrong path. It is not sudo and not measurement, and its twelve
   wall-costs are the most valuable numbers the run will produce.
4. **Verbatim frames, stale timestamps, anchors `unresolved`** — a safety property, not a defect;
   state it in the artifact so a reader does not read it as a failure.
5. **Record session-level drift too** (A269 §A1) and escalate a chain-pass/session-fail split.
6. **Own PR, and freeze main between its merge and the arm** — the sketch left the sequencing open;
   P7.1's "at the merged head" only binds if nothing lands after it.
7. **No new exclusion reason** — it would force a registration v3 re-pin.
