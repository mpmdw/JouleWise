# LIVE launchctl smoke for the transactional night-agent installer

Drafted 2026-09-15 (not yet run). Lead-only: execute the moment the final engine lands in
`/Users/edr/code/JouleWise-wt-iw-txn/joulewise/night_agent_install.py`. The script drives the
REAL `LaunchctlAdapter` (real `/bin/launchctl`, real `gui/501` domain) through one full install
transaction and one uninstall, with THROWAWAY labels `com.joulewise.smoke.night` and
`com.joulewise.smoke.night.deadman` and a throwaway plist directory under this scratchpad.

What it never touches: `~/Library/LaunchAgents` (where `com.joulewise.magistrate.plist` lives),
`~/night-custody`, `~/JouleWise-measurement-*`, the canonical `~/code/JouleWise`, the production
labels `com.joulewise.night*`. Everything it writes is under `smoke/live/`:

```
smoke/live/LaunchAgents/<label>.plist            the two published plists (+ .prior sidecars during a txn)
smoke/live/custody/night_plan.json               throwaway plan, t0 = now + 3 h (minute-aligned)
smoke/live/custody/night/                        mkdir'd by the engine (StandardOut/ErrPath targets)
```

The plists' `ProgramArguments[0]` is `/usr/bin/true` (the engine renders the real template with
`python=/usr/bin/true`, `courier=/usr/bin/true`); `RunAtLoad` false, no `KeepAlive`;
`StartCalendarInterval` is t0's local Month/Day/Hour/Minute (>= 3 h ahead), the dead-man's is
Hour/Minute of t0 + 1 h. The script refuses to bootstrap unless a `plistlib` parse of BOTH rendered
payloads confirms this (exit 2 "rendered plist is not harmless"). Even if a plist fired it would
run `true`.

Bypassed on purpose: `validate_install` (git pin checks, driver preflight, template lookup) — the
smoke builds `Prepared` directly the way `tests/test_night_agent_install.py` does, with a
`SimpleNamespace` plan and `spans_for_day = lambda day: [(now-60, install_close)]`. The smoke
pins the launchd WIRE, not the plan-validation logic (the fake-launchctl suite pins that).

## Commands

```zsh
SMOKE=/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/smoke
# 0. preconditions (read-only): magistrate label is the only joulewise agent; smoke tree absent
ls ~/Library/LaunchAgents | grep joulewise ; ls "$SMOKE"
# 1. the smoke (10 engine launchctl calls + 8 raw evidence queries, < 30 s)
python3.11 "$SMOKE/live_smoke.py" 2>&1 | tee "$SMOKE/smoke-$(date +%Y%m%dT%H%M%S).log"; echo "exit=${pipestatus[1]}"
# 2. only after a failure, or if a run died mid-way (Ctrl-C, kill, crash):
python3.11 "$SMOKE/live_smoke.py" --cleanup 2>&1 | tee -a "$SMOKE/cleanup-$(date +%Y%m%dT%H%M%S).log"; echo "exit=${pipestatus[1]}"
```

Use `python3.11` (3.11.15 at `/opt/homebrew/opt/python@3.11/bin/python3.11`); the engine itself
is 3.9-compatible, the smoke uses 3.11 syntax. `--help` runs no launchctl. Keep the `tee` log:
it IS the evidence artefact for the process trace.

## What each printed line proves

| Line | Proves |
|---|---|
| `smoke start … macOS=… build=25G83 kernel=25.6.0 python=… uid=501 launchctl=/bin/launchctl` | the build the wire signature is pinned on |
| `engine=… sha256=…` | which engine bytes produced the evidence (paste into the trace) |
| `EVIDENCE baseline label=<L> rc=113` + `stderr\| Could not find service "<L>" in domain for user gui: 501` | the D2 ABSENT signature on this build BEFORE anything is loaded (raw, outside the adapter). A `Bad request.` line before it is expected noise; the engine matches the signature line by exact `splitlines()` membership |
| `render <L>: ProgramArguments=['/usr/bin/true', …] StartCalendarInterval={…}` | the plists launchd will receive are harmless and >= 2 h out |
| `schedule: t0=… install_close=… deadman=…` | admission/commit arithmetic used (t0-85 min close, as §1.3) |
| `launchctl argv=[…] rc=… / stdout=… / stderr=…` (one block per call) | EVERY argv the engine handed the real binary, verbatim, with the wire result. Expected order: `print`×2 (admission require_absent, rc 113), `bootstrap gui/501 <night.plist>` (rc 0), `bootstrap gui/501 <deadman.plist>` (rc 0), `print`×2 (verification, rc 0) |
| `engine state trace: VALIDATED -> ADMITTED -> STAGED -> PUBLISHED -> NIGHT_LOADED -> DEADMAN_LOADED -> VERIFIED -> SUCCESS(final)` | the transaction walked its states in order and the one `finally` dispatched COMMITTED -> SUCCESS (COMMITTED is set directly by `_commit`, so it is not in the `_enter` trace) |
| `engine install rc=0 adapter_calls=6` | the engine's own verdict; `validated pins: repo_head=000… ` just above it is the pins line the CLI would print |
| `EVIDENCE loaded label=<L> rc=0` + a multi-line `stdout\|` service dump (`program = /usr/bin/true`, `path = …/smoke/live/LaunchAgents/<L>.plist`, `state = …`) | both throwaway jobs are LOADED in gui/501 with the throwaway plist paths |
| `launchctl argv=[… "bootout" …]` ×2, then `print` ×2 rc 113 | uninstall's `verified_bootout`: mutator results are evidence, the two `print`s mint the Absent proofs that authorise plist deletion |
| `engine uninstall rc=0` | `uninstall()` returned 0: bootout, proofs, `remove_plist`×2, `discard_priors` |
| `EVIDENCE absent label=<L> rc=113` + the signature line | the D2 ABSENT signature AFTER a real bootout (the second pin; same bytes as baseline) |
| `EVIDENCE final label=<L> rc=113` | the exit guard: no throwaway label is loaded when the script exits |
| `SMOKE VERDICT exit=0: PASS` | everything above held AND both plists and both `.prior` sidecars are gone |

## Exit codes

| exit | meaning | action |
|---|---|---|
| 0 | PASS | record the log in the trace; the D2 signature is pinned (`rc 113` + exact line, twice) |
| 2 | precondition: python < 3.11, smoke tree exists, root outside scratchpad, plist not harmless | fix/`--cleanup`; nothing was bootstrapped |
| 10 | install transaction returned non-zero (its refusal text is on stderr just above) | engine rolled back (state trace ends ROLLED_BACK/REFUSED) — still run `--cleanup`, then report |
| 11 | LOADED evidence missing, or plist/`.prior` wrong after install rc 0 | ABORT: `--cleanup`, report |
| 12 | uninstall returned non-zero (4 = still loaded after bootout; 1 = exception) | ABORT: `--cleanup`, report |
| 13 | ABSENT signature not seen after uninstall, or files remain | ABORT: `--cleanup`, report |
| 14 | a throwaway label is STILL LOADED at exit (overrides any other code) | `--cleanup` NOW, then report |
| 1 | unexpected exception (engine API drift, import failure) | read the message; adjust `transact()`/`unload()` only |

## Abort rule

Any launchctl `rc` other than the expected (`print`: 113 before load, 0 once loaded; `bootstrap`: 0;
`bootout`: 0), any state trace that is not the sequence above, any `liveness_unknown:` or
`teardown:` warning, or any exit other than 0: STOP. Do not re-run. Run `--cleanup`, confirm its
`SMOKE VERDICT exit=0`, confirm `launchctl print gui/501/com.joulewise.smoke.night` says
`Could not find service` by hand if you like, and report the full log to the lead. Never edit the
engine to make the smoke pass; the smoke is the evidence, the engine is the subject.

`--cleanup` is idempotent: `bootout` each label (rc ignored, printed), require the ABSENT signature
for both (else exit 14 and the files are KEPT so a loaded job never loses its plist), then
`rm -rf smoke/live`. It never lists or touches any other label or directory.

## When the seat's engine rewrite lands

The script binds to: `engine.Shield()`, `engine.Transaction(adapter, validate, clock=, shield=)`,
`engine.Prepared(plan, plan_path, repo, python, template, courier, courier_path, schedule,
spans_for_day)`, `engine.Target.for_mode(launch_dir, labels=)`, `engine.LaunchctlAdapter(target,
executable)`, `engine.uninstall(adapter, shield=)`, `machine._enter`, `machine.state`,
`adapter.outcomes`, `target.path/sidecar`. If only the signal machinery changes per the adopted
design, the sole edit is the two constructor calls in `transact()` and `unload()` (marked ADJUST
ONLY HERE). `shield.release()` after each call exists because `run()`/`uninstall()` quiesce
INT/TERM/HUP to SIG_IGN for in-process callers; without it Ctrl-C would be dead for the rest of
the smoke.
