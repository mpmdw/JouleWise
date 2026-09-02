# PR #265 post-review fresh pass (16fb6504 -> ad07bd5c) — contract lens, read-only

**VERDICT: CLEAN** — the post-review commits are correct and add nothing beyond the
main merge plus one CI step. One SHOULD-FIX (pre-existing, non-gating, stage 2), one
observation, two nits. Nothing blocks tonight's rehearsal.

## A. Commit 5fda96be — clock pin

**A1 (nit, accuracy of the comment/commit message).** `tests/test_run_night.py:701-704`
and the commit subject frame the defect as "already past on a UTC runner." It is a
**date bomb, not a TZ quirk**: `self.t0_epoch_s = datetime(2026, 9, 2, 1, 0).timestamp()`
(`tests/test_run_night.py:147`) is a *naive local* datetime, so `_next_deadman_epoch`
(`scripts/run_night.py:858-868`) always yields 07:00 **local** on 2026-09-02 in every
zone. Failure scenario absent the pin: any run after 2026-09-02T07:00 local — i.e.
**everywhere from 2026-09-03 onward**, LA included — `run_courier` breaks at
`scripts/run_night.py:721` and the test dies `AssertionError: 0 != 4`. The fix is
complete; only the note understates its reach. Suggest: "the fixture's absolute t0 is a
fixed 2026-09-02 date, so the dead-man is in the past for any real clock after that
morning."

**A2 (no finding) — the value is semantically right.** `self.t0_epoch_s + 1` = one second
into the night, matching the fixture's own `ProbeSource(self.t0_epoch_s + 1)`
(`tests/test_run_night.py:148`), and sits ~6 h before the dead-man. Neither the
pre-attempt guard (`scripts/run_night.py:721`) nor the retry-crossing guard (`:772`,
delays 60/180/600 → max t0+601) can trip, so `attempted == 4`
(`tests/test_run_night.py:717`) is earned, not forced.

**A3 (no finding) — masking check.** The pin freezes only *record timestamps* that this
test never asserts: `started_epoch_s` (`run_night.py:727`), `ended_epoch_s` (`:811`),
courier-lock epochs (`:670`, `:676`), rerun-refusal epoch (`:883`). It does **not** mask
the completion-epoch logic: `_completion_epoch_s` (`run_night.py:871`) is consulted in
run_night's preflight at `:1043-1044`, which is clock-free (plan arithmetic only), and in
`dead_man` at `:1271`, which this test never calls. `_wait_for_courier`'s wall-clock reads
(`:618`, `:633`) are unreachable here regardless — `COURIER_DEADLINE_S = 0` breaks on
monotonic immediately, and the courier `Popen` raises before the wait is entered.

**A4 (nit).** With a constant `return_value`, all four attempt records in
`courier.attempts.jsonl` share one `started_epoch_s`. Harmless today; if a future
assertion wants attempt ordering, switch to a `side_effect` counter.

**A5 (no finding) — hand-off path is covered.**
`tests/test_run_night.py:965 test_run_path_courier_hands_off_at_the_dead_man_epoch`
asserts `attempted == 0`, `calls == []`, and no leftover `courier.lock`. It passes
`deadman_epoch_s=time.time() - 1` — *relative*, so it is TZ- and date-independent and
carries no bomb of its own.

## B. Commit ad07bd5c — resolved courier path

**B1 (SHOULD-FIX, pre-existing in `scripts/install_night_agent.sh:52-53`, stage 2, not
gating).** The installer resolves and *then* takes the parent:
`courier_bin="${courier_bin:A}"` → `courier_path="${courier_bin:h}:/usr/bin:..."`. On the
real machine `command -v claude` = `/Users/edr/.local/bin/claude`, a symlink to
`/Users/edr/.local/share/claude/versions/2.1.252` — a *file named by version*. So `:h` is
`.../claude/versions`, a directory that contains **no executable named `claude`**. The
rendered PATH entry therefore cannot resolve the courier by name; pre-`:A` it would have
been `~/.local/bin`, which can. Inert today only because both the night and dead-man
renders share `configs/launchd/com.joulewise.night.plist.template:16` and pass an absolute
`--courier-bin`, and `_resolve_courier_bin` (`scripts/run_night.py:571-583`) falls back to
`shutil.which` only when that argument is absent. Failure scenario: any future render that
drops `--courier-bin`, or a courier session that shells `claude` by name, gets
`which("claude") is None` → `courier_unavailable` → the night publishes nothing.
Fix: keep `:A` for `--courier-bin`, derive `courier_path` from the **unresolved**
`command -v` parent.

**B2 (observation, stage 2, not gating tonight).** `:A` pins one exact version file, so a
`claude` self-update between arming (morning) and the 02:00 fire could leave
`--courier-bin` pointing at a deleted binary → both plists refuse `courier_unavailable`
and the night's results are never published. Measured mitigation: the installer keeps ~5
versions (`2.1.243` … `2.1.252`, back to 08-24), so same-night GC is unlikely — **not a
blocker for tonight**. Stage-2 option: on a missing pinned `--courier-bin`, fall back to
`shutil.which("claude")` and record the substitution in `courier.json` instead of refusing.

**B3 (observation).** `courier.resolve()` is the *right* expectation for what the
installer does, but the fixture (`tests/test_run_night.py:1053-1063`) creates a **real
file**, so `resolve()` is a no-op whenever TMPDIR is already resolved. The `:A` behavior is
thus exercised only incidentally via macOS's `/var → /private/var`, and never in the
symlink shape production actually has. Stage 2: add a `bin/claude -> versions/x` symlink
fixture asserting both the resolved `--courier-bin` and the intended PATH.

## C. Merge / range provenance

**C1 (observation — brief undercount).** The range holds **four** branch commits, not
three: `9f9985db` (CI: install zsh in the `test` and `pr-fast` jobs) is also post-review
and is the only non-test, non-merge change beyond the merge. Reviewed it independently:
correct and complete — `test` and `pr-fast` are the only jobs that run driver tests
(`calibration-*-exclusive` run single calibration modules; `build`/`installed-wheel` run
none), and `test -x /bin/zsh` fails loudly rather than silently.

**C2 (no finding).** Everything else non-test in `16fb6504..ad07bd5c` is exactly main's
`c5fa8a49` (two process-trace docs + `scripts/generate_g2a_probe_inputs.py`).
`git diff-tree --cc 3ac2064c` prints no hunks → no evil merge; `git diff 5fda96be
3ac2064c` excluding main's four paths is empty → the merge contributed nothing branch-side.
The `.github/workflows/ci.yml` hunk in the range is byte-identical to `9f9985db`.

## Test tails

TMPDIR=<fresh scratchpad dir>:
```
...................................................................................................................s...
Ran 119 tests in 2.932s
OK (skipped=1)
```
TMPDIR unset (`env -u TMPDIR`, default macOS `/var/folders/...`):
```
...................................................................................................................s...
Ran 119 tests in 2.800s
OK (skipped=1)
```
