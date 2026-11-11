# W1 reliability round 3 — local Sol seat `w1-reliability-3`

Implemented the kernel-frequency preflight on the explicitly requested existing
branch `ops/2026-11-10-w1-reliability`, starting at its pushed head `80eb99714`.
No arm, installation, sudo invocation, host setting change, measurement,
analysis pipeline, model download, network access or push was performed.
Hardware behavior remains **PROVISIONAL**.

## Authority and intake

Read round 2's report and `origin/main:RUN_STATE.md` item 251, including the
correction of item 250's slew diagnosis. The in-session lead ruling supplies
the prospective authority: check the frequency word before install, zero
only after network time OFF when the narrow sudo capability permits it,
otherwise refuse as `clock.frequency_word_nonzero`; retain terminal ON
restoration. No scientific threshold or hazard gate changes are authorized
or made.

Mission M0: root AGENTS/CLAUDE conventions, the targeted restart, workspace,
queue and do-not-do sections, playbook, orchestration, source-of-truth map,
phase pointers and D-050/D-115/D-127/D-186 inspected. No active stop card.
The explicit brief selects this bounded AGENT task and overrides ordinary
coordination-state updates and full-suite requirements. RUN_STATE.md,
TASK_QUEUE.md, docs/process/state_kernel.json and tests/test_gen_state.py
remain unchanged; no kernel task was registered. No child agent or consult
was used. No external data path printed in repository text was followed.

## Implementation and clause map

1. **Pre-arm preflight.** `scripts/align_v4_session.py` checks each STAGED
   prepare and each public install. The install check runs under HostLock,
   before High Power entry, the meter probe and quiet dwell. The prepare
   check also holds HostLock. INPUTS_ONLY preparation has no armable plan and
   does not attempt correction. A failed prepare preserves its selected
   frozen-series window as well as its clock record.

   The preflight reads the actual night plan, checks its digest against
   session.json, requires t0 still in the future, then calls the hazard's
   `clock.read_frequency` and `kernel_clock.validate_probe`. It projects the
   word with the existing `clock.frequency_bound` and this plan's complete
   clock thresholds, including its actual stream span and h term. There is
   no hard-coded 5,764-second policy and no threshold change. For the item-251
   synthetic values (word -648908, span 5,764 s, h = 0), the exact projection
   is 58.513535888671875 ms; zero projects to 1.441 ms.

   A passing word is a no-op with a fresh second read. This includes a small
   nonzero word whose projection passes: no extra word-equals-zero gate is
   introduced. A failing projection first requires the existing launchd
   census to prove the night job absent. It then sets network time OFF,
   authenticates an OFF read-back, invokes the fixed helper through sudo -n,
   and re-reads using the same hazard reader. Helper success requires both
   an actual zero word and a passing projection. A denial, missing helper,
   timeout, failed OFF read-back, bad kernel read, stale plan or failed
   projection returns the named refusal with its detailed reason.

   session.json holds `clock_frequency_preflight` after prepare. The install's
   fresh result is included in the ordinary create-once
   staging/v4-arm-NNN.json before the dwell stamp and shared installer;
   frequency refusal sets admitted=false and prevents installer invocation.
   Records include before/after probes with their raw word and preserved
   timex bytes, projected bounds, command argv/status/output and errors.
   Failed re-reads remain explicitly absent with an error. A successful
   prepare record never substitutes for a new install check.

2. **Narrow helper.** `scripts/zero_ntp_frequency.c` is source for a fixed
   Darwin native executable. It rejects all arguments and non-root callers,
   sets exactly MOD_OFFSET|MOD_FREQUENCY with offset=0/freq=0, and performs a
   read-only zero verification. Syscall status TIME_ERROR (5) is accepted;
   -1 is an error. It accepts no file, shell, interpreter, model or arbitrary
   frequency input. Provisioning is lead-owned and was not attempted here.

3. **A-05.** `scripts/run_night.py` still restores network time ON and
   authenticates its ON query on the existing terminal/dead-man paths. Its
   network-time restore record now states `next_arm_owns_zeroing: true` and
   names the next-arm preflight cause. No zeroing occurs at window close.

4. **Tests.** The new round-3 module covers nonzero -> OFF/query/zero/read,
   unavailable helper -> named refusal before install, zero -> no-op,
   passing nonzero words, stale prepare evidence, expired t0, plan tampering,
   bad/missing probes, OFF/query failures, helper timeout, unsuccessful zero
   read-back, prepare persistence, public-install ordering and ON restoration.
   The native helper is compiled against the Darwin SDK in a harness that
   replaces both privileged syscalls; argument/root checks, exact modes and
   zero operands, status 5, syscall failure and nonzero read-back are tested
   without touching the real clock. Legacy power/series fixtures explicitly
   inject a synthetic frequency preflight so their unrelated gate tests
   never invoke real OS clock operations.

## Provisioning and exact sudoers requirement — lead only

Build the reviewed C source on the target Mac with its SDK, for example
`cc -O2 -Wall -Wextra -Werror scripts/zero_ntp_frequency.c -o <staged-binary>`.
Authenticate the reviewed source and staged binary by SHA-256 and retain
that provenance with the provisioning record (D-115). Install the executable
root:wheel, mode 0755, **without setuid**, at the fixed path below. Its
parent directories must be root-owned and unwritable by the operator. Do
not grant sudo to a repository script or a Python interpreter.

The additional rule is exactly one root operation with **no arguments**;
the `""` argument constraint is intentional:

```sudoers
edr ALL=(root) NOPASSWD: /Library/PrivilegedHelperTools/joulewise-zero-ntp-frequency ""
```

The preflight also needs these exact existing systemsetup operations:

```sudoers
edr ALL=(root) NOPASSWD: /usr/sbin/systemsetup -setusingnetworktime off
edr ALL=(root) NOPASSWD: /usr/sbin/systemsetup -getusingnetworktime
```

A-05 continues to require the corresponding exact ON setter. The lead must
review/provision these capabilities under the repository's privileged-install
conditions; this run neither inspected nor edited sudoers. Without usable
noninteractive access, a failing frequency projection refuses before install.
An attempt that has already set OFF can leave network time OFF on a later
helper failure; its command evidence says so. It installs no job that could
restore ON later, so the lead must restore ON after abandoning that attempt.

## 4. Replacement post-window runbook text — destination needs a lead pointer

The §4 referenced in item 251 could not be located in the tracked runbooks
of this branch or origin/main. Its apparent native arm scripts are also not
tracked here. No external runbook or custody path was accessed. A destination
question was raised while implementation continued. To avoid changing an
unrelated historical runbook, the requested replacement is supplied here:

> After chain exit has been proved and the host lock permits restoration,
> read the result's verdict/refusal and the chain's own status first. Restore
> AC powermode Automatic and network time ON, authenticate both read-backs,
> and retain the restoration evidence, including failures or deferrals. ON
> restores wall-clock accuracy between windows and can repopulate the kernel
> NTP frequency word; turning it OFF later does not clear that word. The
> **next arm's prepare/install preflight owns zeroing**: read the kernel word
> through the clock hazard's reader, project it through that plan's existing
> 5 ms budget, and, if it fails, set network time OFF, run the fixed
> noninteractive root zero helper and verify the zero word and bound. If
> that capability is unavailable or verification fails, refuse before
> install with `clock.frequency_word_nonzero`. Keep before/after words in
> the arm record. The existing OFF receipt, settle and hazard dwell gates
> remain required; this preflight does not replace them. Do not zero the
> clock during an installed or measuring night.

The lead still needs to identify and update that owning §4. This is a
documentation-location blocker, not an unresolved engineering-policy choice.

**NEEDS_RULING:** Which repository file owns this post-window §4? Options
considered: edit the identified owner; create a new W1 runbook; put the
reviewable replacement here while preserving unrelated historical runbooks.
Recommendation: supply the owning path and apply the replacement there.
Blocked work: the actual owning-runbook edit only. The code/tests and local
commits are independent and complete.

## Changed files and registration boundary

- Production: scripts/align_v4_session.py, scripts/run_night.py,
  scripts/zero_ntp_frequency.c (new native-helper source).
- Tests: tests/test_w1_reliability_r3.py (new), tests/align/test_v4_kit.py,
  tests/align/test_v4_series.py, tests/align/test_v4_series_e2e.py.
- Handoff: this report, including the proposed §4 text and provisioning rule.

The two modified Python entry points are already STRICT-bound. Final W1
STRICT re-registration remains required at the integrated head. The native
helper is a newly provisioned external executable; the existing Python/shell
closure test does not track C source or that installed binary. Preserve its
reviewed source/binary identity in provisioning evidence; do not treat the
closure test as proof that the external helper is registered. No registration
code/text, seeds, analysis/engine code or clock hazard/kernel gate was changed.

## Verification

Only targeted unittest modules/classes ran, using Python 3.13. **120 focused
tests passed** (unique cases across the commands below); all development
reruns and the interrupted invocation kept total test time below five
minutes. No full suite was run. Each table entry follows
`python3.13 -B -m unittest`:

| Module/class arguments | Result |
|---|---|
| tests.test_kernel_clock | 4 passed, 0.000 s (baseline) |
| tests.test_w1_reliability_r3 | 14 passed, 0.660 s |
| tests.test_w1_reliability_r2 | 18 passed, 4.817 s |
| tests.align.test_v4_kit.SessionParameterTests tests.align.test_v4_kit.W1HighPowerTests tests.align.test_v4_kit.W1DiskGateTests | 23 passed, 1.311 s |
| tests.align.test_r1_round6_power | 25 passed, 0.309 s |
| tests.align.test_r1_round7_install | 6 passed, 1.265 s |
| tests.align.test_v4_executed_closure | 4 passed, 2.335 s |
| tests.align.test_v4_series_e2e | 10 passed, 26.211 s |
| tests.align.test_v4_series | 16 passed, 39.665 s (serial rerun) |

Additional successful checks:

```sh
python3.13 -B -m compileall -q joulewise tests
python3.13 -B -m py_compile scripts/align_v4_session.py scripts/run_night.py
cc -Wall -Wextra -Werror -fsyntax-only scripts/zero_ntp_frequency.c
git diff --check
git diff --exit-code -- RUN_STATE.md TASK_QUEUE.md docs/process/state_kernel.json tests/test_gen_state.py
```

The C harness test ran successfully here; it did not skip. It linked fake
ntp_adjtime/geteuid functions, so this is ABI/build/operation-shape evidence,
not native privileged-operation validation. Existing series fixtures print
`full_desk_gate: fail` while testing negative cases; their unittest outcomes
above are successful. An initial new-test run caught an incorrect literal
expected projection (58.5123 versus 58.5135 ms); only the assertion was
corrected, with the production bound implementation unchanged.

An operational mistake briefly overlapped the start of test_v4_series with
the still-running test_v4_series_e2e. The former was interrupted (exit 130),
then rerun alone; it is not counted as a passing check. The long blinded job
was never inspected or signaled. All other test invocations were serial.

## Native checks and remaining uncertainty

All checks below are lead-owned, after the long job and outside any installed
or measuring window. No live clock probe, correction, arm or 180-second rate
measurement was run here.

1. Review/provision the authenticated native binary and exact sudo rules.
   Verify ownership, parent permissions, absence of setuid, no-argument-only
   authorization and sudo -n behavior without relying on a cached ticket.
2. Between windows, reproduce network-time ON -> OFF leaving a nonzero word.
   Run the final candidate's prepare/install preflight: require OFF evidence,
   helper success, before/after words, zero read-back and a passing projected
   bound before any installer/High Power/meter/dwell handoff.
3. With helper authorization absent (or helper unavailable), require the
   named refusal and no new launchd job. Check the preserved session/arm
   records; restore network time ON if abandoning an attempt left it OFF.
4. With the word already zero, require no zero-helper invocation and unchanged
   hazard admission. Between prepare and install, turn ON then OFF again:
   install must read afresh and correct/refuse rather than trust prepare.
5. Independently repeat the magistrate's 180 s wall-vs-RAW rate witness in a
   clean lead-controlled session after zeroing. The synthetic projection and
   fake-syscall C harness are not evidence of live clock-rate behavior.
6. After normal completion, refusal and scheduled dead-man recovery, verify
   Automatic and network time ON read-backs plus the next-arm-owns-zeroing
   annotation. Repeat an arm cycle to prove that restoration does not strand
   the next window. Round 2's other native meter/kill/restore gates still apply.

No MLX code changed and no MLX tests ran. Native MLX limitations are unchanged;
this change introduces no new MLX-specific test command. Hardware clock,
sudoers, timed races and privileged provisioning remain unverified. The
unmodified t0 hazard dwell still owns measured-rate admission if host state
changes after this earlier preflight.

Next exact step: the lead reviews/integrates these local changes, supplies the
owning runbook §4 path and installs its replacement text, provisions the
reviewed helper, re-registers the final W1 head and runs the native gates
before arming. No push or deployment is authorized by this handoff.

## Local commits

- `ae2760684` — `fix(w1): preflight and zero persistent kernel NTP frequency`
  (the seven production/test files listed above).
- This report is the separate `docs: record W1 frequency preflight handoff`
  commit; its identity is available as this file's latest Git commit.

Both commits are local on the requested continuation branch. Nothing was
pushed. Coordination-state paths remain unchanged.
