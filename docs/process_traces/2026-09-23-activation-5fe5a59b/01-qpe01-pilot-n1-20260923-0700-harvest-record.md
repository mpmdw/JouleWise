# Record 01 — pilot night `qpe01-pilot-n1-20260923-0700`: harvest, uninstall and the registered result (activation 5fe5a59b, 2026-09-23, from 09:35 PDT)

Terms used in this record. A *night* is one scheduled, unattended measurement run on this Mac; this one began at
07:00 PDT (its *t0*). An *envelope* is one 600 s capture of the machine sitting idle; the night ran twelve, one
every 620 s, after a 600 s settle. An envelope's *interior* is the 480 s slice starting 60 s after the envelope's
scheduled start, and every joule figure below is the energy of that slice. An envelope is *retained* when no
registered exclusion fires on it; only retained envelopes enter the summary statistics. A *disjoint pair* is
envelopes (1,2), (3,4) … (11,12); a pair counts only when both members are retained, and its *delta* is the right
envelope's joules minus the left's. *Busy cores* is processor time in use divided by elapsed time, so 1.0 means one
core's worth of work; the load recorder samples it every 30 s, both for the whole machine (*machine-wide busy
cores*) and for each of the heaviest processes (*per-process busy cores*). *Core-seconds* for one process is its
per-process busy cores times the sample length, summed over the samples inside one envelope: 30 core-seconds is
0.05 of a core held for all 600 s. The *apparatus* (also called the *observer*) is the measurement's own
processes: the collector, the 100 ms power recorder (`powermetrics`), the agent census and the 30 s load recorder.
The *observer floor* is the apparatus's own CPU use as a share of one core, averaged over the night. The *agent
census* is `pgrep -lf '[c]odex|[c]laude|[t]3'`, run repeatedly to prove no AI-agent process of this project is
alive during measurement. The *watchdog* is the resident launchd job that starts headless agent sessions
(*activations*) of the project's supervising agent (the *magistrate*); to *arm* a night is to install its two launchd jobs (the driver and a probe) so the machine runs it unattended at t0; to *uninstall* is to remove them, after which nothing is scheduled ("nothing is armed"); the *courier* is a separate agent session
the night's driver launches at the end to email the result and carry out the "next lane" section of
`docs/process/NIGHT_HANDBACK.md` (the *handback*, the per-night instruction sheet). The *custody root*
(called C) is the directory the night wrote into; the *results clone* is a throwaway git clone inside C whose
commit the driver pushes to the project's GitHub remote. *Registration v3* is the pre-registered rule file
`configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v3.json`; every rule quoted below comes from it.

C = `/Users/edr/night-custody/qpe01-pilot-n1-20260923-0700-20260923-0700-1790172000-26fb4280b1e2b3ab5b239884a2c1abbd5f9e1f15`

## §1 Launch

The watchdog's attempt 94 spawned activation `5fe5a59b-2ac4-4aac-b0f7-62cdce87df8d` at 09:35:26.19 PDT.
Evidence: `/Users/edr/night-custody/magistrate/state.json` fields `attempt` 94, `activation_spawn_epoch_s`
1790181326.192262, `resident_session.supervisor_pid` 29843 and `resident_session.pid` 29847 (`ps` shows both started
"Wed Sep 23 09:35:26 2026"), and `last_exit_class` `usage_exhausted` (the class the watchdog stored for the previous
activation's exit; see §7 item 5). `events.jsonl` line 1061, sequence 395, is the transition `LAUNCHING -> ACTIVE`,
reason "spawned activation 5fe5a59b-…".

Heartbeat: written at epoch 1790181335 (09:35:35) per the magistrate. The file has since been rewritten by the same
session; at 09:39 it read `29847 5fe5a59b-… 1790181560`. Launch email: Gmail id `1a0cf204a538d7dd` to
`claude2.glaring610@passmail.net` only, per the magistrate (not verifiable from disk).

The one pending notice was `transition-392-hold_census`, named after the watchdog's state change number 392. In
`events.jsonl`:

- line 1026, sequence 391, epoch 1790172284.09 (07:04:44 PDT): the first non-empty census after t0. Its `stdout` is
  pid 18001 running `scripts/run_night.py run --plan C/night_plan.json …` from the measurement clone. That is the
  night's own driver, not a stray agent.
- line 1027, sequence 392, epoch 1790172285.10 (07:04:45 PDT): transition `FENCED -> HOLD_CENSUS`, reason
  "production census non-empty inside plan span". In plain words: the watchdog saw a process matching its agent
  pattern and correctly declined to start a session on top of a running measurement.
- 28 non-empty census rows in all (07:04:44 to 09:20:21), every one naming pid 18001. The last of them (09:20:21)
  also lists the courier's `claude -p` session, pid 29161, which the design expects at that point.
- First empty census: epoch 1790180722.59 (09:25:22), then transition `HOLD_CENSUS -> FENCED` (sequence 393,
  09:25:23, "plan span active and census empty"); one more empty census at 1790181023.93 (09:30:23); then
  `FENCED -> LAUNCHING` (sequence 394, 09:35:26, "all launch predicates clear").
- line 1062, epoch 1790181407.20 (09:36:47): `notice_acknowledged`, `notice_ids` `["transition-392-hold_census"]`.
  This event is how `notice.ack` shows on disk: the watchdog reads that file, logs this event and deletes it
  (`scripts/magistrate_watchdog.py`, `consume_notice_ack`). `state.json` now has `notice_pending` `[]`.

## §2 Verdict (executed evidence, read at the bench 09:36–09:45 PDT)

`C/night_plan.json`: `plan_id` `qpe01-pilot-n1-20260923-0700`; `repo_head` = `measurement_head` =
`26fb4280b1e2b3ab5b239884a2c1abbd5f9e1f15`; `t0_epoch_s` 1790172000.0 (07:00:00 PDT); `window_max_s` 9000;
`receipt_class` `DIAGNOSTIC_NO_PACK` (a diagnostic night that produces no claim pack); `registration_path`
`…/pilot_protocol_v3.json`. The arm is recorded at
`docs/process_traces/2026-09-23-activation-4e8918fa/01-arm-record-qpe01-pilot-n1-20260923-0700.md` (notice Gmail
`1a0ce4522dbdbf03`, published 05:37:32).

**Driver log** (`C/night.log`, seven lines, read in full):

- `07:00:03.360382 night driver started`
- `07:00:33.835455 night gate verdict=GO`; `07:00:33.835610 night chain digest verified`
- `09:14:23.923942 night result verdict=GO`
- `09:16:03.018006` and `09:22:20.278502`: two "durable record failed" lines, each a `CalledProcessError` from
  `git -C C/results-clone push origin HEAD:night-results/qpe01-pilot-n1-20260923-0700` returning exit status 1 (§3)
- `09:20:59.177851 courier attempt=1 heartbeat=True sent=True`

**Chain** (the shell program that runs the twelve envelopes in order). `C/night/chain.started`: epoch
1790172033.84 (07:00:33.84), pid = process group 18019. `C/night/chain.exited`: epoch 1790180063.037181
(09:14:23.04), `exit_code` 0. `chain.stderr.log` and `launchd.night.err` are empty (0 bytes).
`C/night/chain.stdout.log`: network time switched off; `evidence_settle seconds=600`; twelve `envelope_start` /
`envelope_end` pairs, each `envelope_end` reading `rc=0 cleanup_proven=True clock_attestation=authenticated`, all
twelve with `recorder_pgid=18112` (one power recorder for the whole night); then
`evidence_end outcome=complete cleanup_proven=True network_time_restored=True`. "Cleanup proven" means the chain
showed every process group it spawned was gone afterwards. "Authenticated" means the harness read the operating
system's own log for each capture window and found no clock correction applied inside it.

**Result** (`C/night/result.json`): `verdict` `GO`, `aborted_reason` null, `refusal_documents` `[]`,
`calibration_refusal` null, `census_count` 267, `census_hits` `[]`. `C/night/censuses.jsonl` holds 268 rows, all
exit code 1 with empty output (`pgrep` exits 1 when it matches nothing): the driver never saw an agent process
during the night. (267 against 268 is the same one-row difference recorded for the previous night.)

**Evidence outcome** (`C/night/evidence_outcome.json`): `outcome` `complete`, `envelopes_attempted` 12,
`cleanup_proven` true, `error` null, `network_time_restored` true, `recorder_kind` `powermetrics`. Cleanup
(`evidence_cleanup.json`): `groups` `[18112]`, `residue` `[]`, `errors` `[]`.

**Network time** (`C/night/network_time_control.json`). The operating system normally corrects its clock against
internet time servers, which can move the clock mid-capture; the harness turns that off for the night and back on
after. `off`: `sudo -n /usr/sbin/systemsetup -setusingnetworktime off` at 07:00:34.09, exit 0; `on`: the same with
`on` at 09:14:22.70, exit 0.

**Courier** (`C/night/courier.sent`): `gmail_message_id` `1a0cf11d4855b21a`, `verdict` `GO`, `chain_exit_code` 0,
`sent_epoch_s` 1790180459 (09:20:59), `courier_pid` 29224 (the same pid as `courier.heartbeat`; that is the shell the courier session spawned to write those files, not the `claude -p` process itself, which the watchdog census recorded as pid 29161 (§1)).
`courier.attempts.jsonl`: one attempt, started 09:16:03, `sent` true.

### The summary

`C/night/evidence/summary.json` (schema `joulewise.quiet_predicate_pilot_summary.v1`), all figures PROVISIONAL and
descriptive, as its `evidence_status` says:

- `status` `SPREAD_RECORDED`; `retained` 11 of 12; `retained_pairs` 5. Pair (9,10) is lost because envelope 9 is
  excluded.
- `pair_sd_j` 0.8710 J on `pair_df` 4: the standard deviation of the five pair deltas −0.748, +0.855, −0.150,
  −1.501 and −0.669 J (recomputed: 0.8710407632338234, exact).
- `s_upper` 1.6892 J = 0.8710 × `s_upper_factor` 1.9393, "one-sided upper 90% chi-square bound; independent normal
  pair differences assumed". With only four degrees of freedom the true spread could be larger than the one
  measured, so the method inflates it before sizing.
- `block_two_pairs` 23 by "ruling 46b: max(3, ceil(8 * s_upper\*\*2 / delta_j\*\*2)); delta_j=1; stop above 24
  pairs" (the sizing formula the registration fixed in advance, quoted as summary.json prints it): 8 × 1.6892² = 22.83, rounded up to 23. *Block two* is the planned follow-on experiment that holds a small
  fixed CPU load and measures its energy against idle; this is the number of pairs it would need to resolve 1 J.
  23 is under the 24-pair stop bar, so that branch does not fire.
- `block_two_stop`: `outcome` "no cutoff qualifies", `causes` `["observer_floor_above_smallest_holdable_share"]`
  (see below), `pairs` 23. `cutoff_authority` false, `top_up` false.
- `observer_floor_cores` 0.1784 over `observer_support_s` 7277.6; `observer_variation_cores` 0.00096;
  `observer_floor_including_load_recorder_cores` (the companion figure that adds the 30 s load recorder, which runs
  beside the collector rather than under it; reported, never a stop input) 0.1859.
- Machine-wide `busy_cores` over the night: p10 0.2295, p50 0.2480, p90 0.3398, max 1.6912 (envelope 9).
  `busy_cores_role` "covariate_only; never excluded".
- Diagnostics, never used for sizing: `single_envelope_sd_j` 1.8438 (retained only) and
  `unfiltered_single_envelope_sd_j` 2.8184 (all twelve); `adjacent_pair_sd_j` 3.8830; `max_abs_delta_j` 9.838 (8→9);
  `first_to_last_retained_drift_j` +2.509. `pairs_above_3_pair_sd` names 8→9 (+9.84) and 9→10 (−6.39), both
  touching the excluded envelope.

### Per-envelope table

Joined from `summary.json` `envelopes[]` (joules, exclusions, chain-level start drift, attestation, busy cores) and
`C/night/evidence/envelope-NN/session.json` (wall span from `start_stamp`/`end_stamp`, `power.anchor.status`,
`interior.status`, `interior.native_samples`). *Start drift* is how late the envelope began against its scheduled
instant, as measured by the chain. The last column is the largest per-process core-seconds of any non-apparatus
process in that envelope, recomputed from `C/night/evidence_busy_cores.jsonl`.

| env | wall span (PDT) | joules | excluded | anchor | interior | native samples | start drift s | busy median | busy max | top non-apparatus core-s |
|---|---|---|---|---|---|---|---|---|---|---|
| 01 | 07:10:34–07:20:40 | 158.98 | — | bounded | complete | 2045 | 0.1988 | 0.241 | 0.398 | WindowServer 7.54 |
| 02 | 07:20:54–07:31:01 | 158.23 | — | bounded | complete | 2042 | 0.1501 | 0.266 | 0.381 | WindowServer 5.78 |
| 03 | 07:31:14–07:41:21 | 156.44 | — | bounded | complete | 2052 | 0.1501 | 0.254 | 0.382 | WindowServer 5.74 |
| 04 | 07:41:34–07:51:40 | 157.29 | — | bounded | complete | 2040 | 0.1501 | 0.246 | 0.376 | launchd 5.02 |
| 05 | 07:51:54–08:02:00 | 158.54 | — | bounded | complete | 2038 | 0.1501 | 0.245 | 0.390 | WindowServer 5.61 |
| 06 | 08:02:14–08:12:21 | 158.39 | — | bounded | complete | 2048 | 0.1501 | 0.242 | 0.432 | WindowServer 6.91 |
| 07 | 08:12:34–08:22:40 | 158.02 | — | bounded | complete | 2059 | 0.1501 | 0.250 | 0.342 | WindowServer 7.15 |
| 08 | 08:22:54–08:33:00 | 156.52 | — | bounded | complete | 2041 | 0.1501 | 0.243 | 0.411 | WindowServer 5.59 |
| 09 | 08:33:14–08:43:20 | 166.36 | `non_observer_process_busy` | bounded | complete | 2043 | 0.1501 | 0.251 | 1.691 | **mobileassetd 61.51** |
| 10 | 08:43:34–08:53:40 | 159.97 | — | bounded | complete | 2058 | 0.1501 | 0.251 | 0.387 | WindowServer 5.88 |
| 11 | 08:53:54–09:04:01 | 162.15 | — | bounded | complete | 2055 | 0.1501 | 0.254 | 0.355 | WindowServer 5.76 |
| 12 | 09:04:14–09:14:20 | 161.49 | — | bounded | complete | 2071 | 0.1501 | 0.248 | 0.379 | WindowServer 8.94 |

Every envelope's `network_time_attestation` is `authenticated` with reason "no applied clock correction inside the
capture window". The eleven retained envelopes span 156.44–162.15 J (median 158.39). For contrast, the previous
pilot night (09-22 21:00) read ~305 J per envelope at a machine-wide busy-core median of 1.221 while a stuck system
daemon held one core; tonight's median is 0.248.

### Why envelope 9 was excluded

Registration v3 carries a per-envelope rule, `non_observer_process_busy`: `statistic` "per non-observer process
identity: sum over journal rows joined to the envelope of busy_cores \* interval_s", `bar_core_seconds` 30,
`abort_after_consecutive` 2 (two such envelopes in a row end the night). Its `bar_basis`: 0.05 core held for 600 s,
about 7.7 J of the 480 s interior, above the 5 J claim bar. A process is *non-observer* when the load recorder did
not mark it as a descendant of the night's own chain.

Envelope 9's row in `summary.json`: `excluded` `["non_observer_process_busy"]`; `non_observer_process_busy` and
`executor_non_observer_process_busy` both `[{"process": "mobileassetd", "pid": 439, "start_identity": "Fri Sep 18
17:41:18 2026", "core_seconds": 61.51, "bar_core_seconds": 30}]`; `non_observer_verdict_disagreement` false (the
driver's in-chain decision and the summary's re-derivation agree). `mobileassetd` is macOS's downloader for system
assets; pid 439 started at boot. Recomputed from `evidence_busy_cores.jsonl`: three consecutive 30 s samples, at
481.5–511.9 s, 511.9–542.3 s and 542.3–572.7 s after envelope 9's scheduled start, at 0.693, 0.896 and 0.440
per-process busy cores, whose core-seconds sum to 61.51. The interior ends at 540 s, so the first two samples
overlap its last ~58 s and the third lies after it. No other non-apparatus process reached 10 core-seconds in any
envelope (largest elsewhere: WindowServer 8.94 in envelope 12). The next envelope, 10, is clean, so the
two-in-a-row abort did not fire.

### Sol's finding F2: the `summary.md` sentence

At the arm gate for this night (the three-reviewer check before installing it; activation 4158e658, record 08, the
reviewer seat run on OpenAI's Sol 6.0 model), finding F2 reads:
"The pinned campaign generates summary.md with 'Busy cores are recorded covariates and never an exclusion input.'
That is false for v3 and would misdescribe the night's own exclusions." The arm synthesis (4158e658 record 01 §2)
kept the arm, registered the fix as lane NOTICE-SUMMARY-V3-TEXT-01 (A276), and required this record to name it.

`C/night/evidence/summary.md` does contain, verbatim: "Busy cores are recorded covariates and never an exclusion
input." It is written unconditionally by `joulewise/quiet_predicate_campaign.py` line 1441.

What the exclusion actually used, from that file's `non_observer_busy` function and the registration's `statistic`:
the input is a **per-process core-seconds integral**, built from each non-apparatus process's per-process busy-core
readings (`top_consumers[].busy_cores` in the load recorder's journal) times each sample's `interval_s`. The
**machine-wide** busy-core figure (the journal row's `metrics.busy_cores`, summarised as `busy_cores` in
`summary.json`) is not read by the rule. So, precisely:

- Read as a statement about the machine-wide busy-core covariate, the sentence is literally true: that figure is
  never an exclusion input, matching `busy_cores_role` "covariate_only; never excluded" (the cold Fable final pass
  in 4158e658 record 01 §10 made the same caveat).
- It is misleading, and false on its plain reading, because the exclusion input is made of busy-core readings from
  the same journal (the per-process field is itself named `busy_cores`), and a reader of `summary.md` alone would
  conclude that no load measurement excluded anything, while envelope 9 was excluded on exactly that. The next
  sentence ("Every exclusion … is retained in summary.json") is true: the exclusion is there.

This record corrects no file; the fix belongs to A276.

### The stop cause is the expected clean-night outcome

The stop branch `observer_floor_above_smallest_holdable_share` fires when the observer floor exceeds block two's
`smallest_holdable_share`, 0.05 cores (registration v3 `block_two`, levels `[0, 0.05]`). Tonight 0.1784 > 0.05.
"No cutoff qualifies" is the registration's outcome string for every stop branch; in plain words, this pilot does
not hand block two a usable size at the registered 0.05-core level.

This was predicted before the night ran. The magistrate's synthesis of round 3 of a *cold gate* (a review by a fresh
agent session with no prior context)
(`docs/process_traces/2026-09-22-activation-a022aecc/03-coldgate-packet-daemon-contamination/35-magistrate-synthesis-round-3.md`,
"synthesis 35") says, item 3: "Consequence, stated plainly: the next clean pilot will report "no cutoff qualifies"
on the observer floor (0.16–0.18 > 0.05) — the honest registered result that block two at a 0.05-core level is not
holdable above this apparatus — while still delivering the pilot's other products (retained spread, `s_upper`, the
clean-machine busy-core distribution, and the first exercise of the non-observer-process rule)." Tonight delivered
each of those: a retained spread (0.871 J), `s_upper` (1.689 J), the busy-core distribution above, and the first
exclusion under the non-observer rule. The observed floor, 0.178, lies inside the predicted 0.16–0.18. What block
two does about it is Ed's decision (synthesis 35 §"Decision brief for Ed") and lane BLOCK-TWO-DESIGN-01. This
record makes no ruling on it.

## §3 Results branch not published

The driver commits the night's artefacts into `C/results-clone` and pushes that commit to a branch on GitHub, so the
evidence has a home off this machine. The push failed twice (`night.log` 09:16:03 and 09:22:20). The courier's
closing summary (`C/night/launchd.night.out`) says its own single retry failed the same way.

- `git -C C/results-clone log --oneline -3` → `82fbcd3 record night qpe01-pilot-n1-20260923-0700`,
  `a751312 record night qpe01-pilot-n1-20260923-0700`, `af879ef Merge pull request #391 …`. `status --short`
  prints nothing; the branch is `night-results/qpe01-pilot-n1-20260923-0700`. Both commits exist only locally.
- `git ls-tree -r -l HEAD` over 100,000,000 bytes → exactly **12 files**, the raw power-recorder output
  `…/evidence/envelope-NN/raw/powermetrics-idle-N.plist`, one per envelope, 133,200,246 to 135,234,716 bytes
  (133.2–135.2 MB, which is 127.0–129.0 MiB, the courier's "127 to 129 MB").
- `git ls-remote origin 'refs/heads/night-results/*'` lists thirteen branches;
  `night-results/qpe01-pilot-n1-20260923-0700` is **absent**.

GitHub rejects any single file over 100 MiB (104,857,600 bytes); all twelve exceed it. The driver's captured error
is only the exit status; the size reading is this record's and the courier's. The bytes are intact in C and in the
archive (§4). Publication waits on Ed's choice of destination, as for both earlier pilot nights (lane A268, the registered work item for publishing these results).

## §4 Harvest and uninstall

The courier did both, as the handback's next lane directs (its `launchd.night.out` summary: "After the driver exited
at 09:22:20 PDT, I harvested the custody root byte-exact …"). The same summary says a follow-up email on the result
thread, Gmail `1a0cf15b1cd41e0f`, reported the harvest and uninstall (not verifiable from disk).

**Harvest** to archive A = `/Users/edr/night-archive/qpe01-pilot-n1-20260923-0700-harvest-20260923`. A holds the same
top-level entries as C plus `SHA256SUMS` (modified 09:24:29) and `SHA256SUMS-check-against-live-root.txt` (09:24:37).
Checked: `wc -l SHA256SUMS` → 16,018; `grep -c 'results-clone/\.git/'` → 0 (git internals are excluded);
`find C -type f -not -path '*/results-clone/.git/*' | wc -l` → 16,018. The check file has 16,018 lines,
`grep -c ': OK$'` → **16,018**, and no line that is not OK. At 09:24:37 every covered file in A was byte-identical
to C.

One file has changed in C since then. `C/night/launchd.night.out` was last written at 09:25:12 (2,033 bytes: the
courier's closing summary); A's copy is 0 bytes (sha256 `e3b0c442…b855`, the digest of an empty file). Re-running
`shasum -a 256 -c A/SHA256SUMS` in C at about 09:40 gives one `FAILED`, that file, and all others OK. The courier's
summary therefore exists only in C. This record does not touch A; see §7 item 1.

**Uninstall.** `/Users/edr/night-plan-staging/…-26fb4280…/lifecycle/uninstall.json`: `argv` = the clone's
`scripts/install_night_agent.sh --plan C/night_plan.json --uninstall --launchctl-bin launchctl`, `exit_code` 0,
started 1790180621.57 (09:23:41.57), finished 09:23:41.69, empty stdout and stderr. The magistrate confirmed at 09:36
that `launchctl list | grep -c com.joulewise.night` → 0 and no `com.joulewise.night*` plist is in
`~/Library/LaunchAgents`. Re-run by this record at 09:40: count 0; the directory holds
`com.joulewise.magistrate.plist` and four third-party plists, no night plist.

**NOTHING IS ARMED.** C and the measurement clone are RETAINED: envelopes were captured.

## §5 Canonical fast-forward

D-183, the project's rule against queueing for the owner anything the agent can do itself, lets the magistrate
fast-forward the canonical checkout `/Users/edr/code/JouleWise` once no night is loaded. The magistrate confirmed no
`com.joulewise.night` label loaded and no night plist on disk (§4), then fast-forwarded. The shared reflog shows
`main@{2026-09-23 09:37:05 -0700}: pull --ff-only -q: Fast-forward` to `af879efb`, from `9e816173`
(`main@{05:26:40}`). `git rev-parse main origin/main` → `af879efb7f52f3abc57d4d2597bd2cda9b1a0198` for both.
`git diff --stat 9e816173 af879efb` → 5 files, 225 insertions: `RUN_STATE.md`, `docs/process/NIGHT_HANDBACK.md`,
the arm record, `02-verify-stdout.json` and `03-cold-fable-final-pass-1479b50a.md`; nothing under `joulewise/`,
`scripts/` or `configs/`.

What "stale supervisor" means here, precisely. Before any arm, `supervisor_check` in `joulewise/evidence_night.py`
refuses when the resident supervisor process started at or before the moment the canonical checkout first
continuously contained the next night's head, whatever the diff holds. Supervisor 29843 started at 09:35:26, before
this fast-forward at 09:37:05. It passes for any next-night head the checkout already held before 09:35:26
(`9e816173` or older); it would refuse `af879efb` or any later head. The docs-only diff means the code this
supervisor runs is unchanged, not that the check passes. This activation arms nothing.

Consequence. The activation's launch instruction says that if the fast-forward makes the resident supervisor stale,
the activation commits, pushes and exits, so that the watchdog's next activation starts under a fresh supervisor and
can arm. That condition holds. The magistrate learned it from this record's verification at about 09:45, after it had
already launched one implementation seat (the change to the watchdog's refusal handling, lanes A234+A212, on OpenAI's
Sol 6.0 model at high effort, in the linked worktree `/Users/edr/code/wt-5fe5a59b-a234`). No night plan is staged,
so an arm cannot happen sooner however quickly this session exits. The magistrate's call is therefore to start no
new work slice, let that one seat finish within its bound or stop it, make its output durable on a pushed branch,
and then exit. This is a sequencing choice inside the instruction, not an exemption from it.

## §6 Next action

Quoted from `docs/process_traces/2026-09-23-activation-4158e658/01-activation-record.md` §4: "THROUGHPUT-01 item
1(b) A234+A212 together, then 1(c) A271 (window machinery). The headline critical path (item 2: scored-campaign
night kind, MATH importer, AP-5 amendment) runs in parallel. After those come NOTICE-SUMMARY-V3-TEXT-01,
BLOCK-TWO-DESIGN-01 once the pilot result is in, and A270." The pilot result BLOCK-TWO-DESIGN-01 waits for is this
record's §2. NOTICE-SUMMARY-V3-TEXT-01 (A276) owns F2 and should also take §7 item 2.

State at this activation's exit is carried by the RUN_STATE top block, which names the A234+A212 seat branch and
what its output needs next.

## §7 Anomalies found while verifying

Before verification, the magistrate handed this record's writer a numbered list of facts it believed true (the *dictated facts*), taken from its own bench reads at 09:36–09:45. Items 6–9 below are the places where the primary evidence differs from that list; the closing paragraph names what matched. The list itself is not a record; only the verified statements above are.

1. **The archive lacks the courier's final summary.** `A/night/launchd.night.out` is empty; C's copy (2,033 bytes,
   09:25:12) was written after the checksum check at 09:24:37. Nothing in A is corrupt; A is one file behind C.
   Re-harvesting that file is a decision for the magistrate; this record writes nothing outside its own path.
   **Magistrate cure (09:47 PDT):** the file was copied, additively, to
   `A/night/launchd.night.out.supplement-5fe5a59b` (`cp -p`), with its digest in the new file
   `A/SHA256SUMS-supplement-5fe5a59b`: sha256 `3743e5fa6c5cf70ba55fa4771d150a7cc6d18c5b2975c319f2345c4212a16b24`,
   equal to `shasum -a 256 C/night/launchd.night.out` run at the same moment. The original empty copy, `SHA256SUMS`
   and the check file are untouched, so the 09:24 harvest stays as it was.
2. **`summary.md` labels the unfiltered figure as the single-envelope SD.** It prints "single-envelope SD
   2.818357264496011 J", which is `unfiltered_single_envelope_sd_j` (all twelve, including excluded envelope 9);
   `summary.json`'s `single_envelope_sd_j` (retained only) is 1.8438. `quiet_predicate_campaign.py` line 1438 passes
   the unfiltered key under that label. It is generated prose of the same kind as F2.
3. **Uninstall ran before the checksums were written.** RUN_STATE's successor step (B) and the handback say to
   harvest, verify `SHA256SUMS`, then uninstall. The uninstall finished at 09:23:41; `SHA256SUMS` is dated 09:24:29
   and its check 09:24:37. The copy time itself cannot be recovered (the copy keeps source timestamps). The later
   check passed on every file, so no evidence was at risk. The deviation is recorded, not cured.
4. **The courier's "rule 2".** The courier's summary says envelope 9 "was excluded under rule 2". Registration v3
   lists `non_observer_process_busy` as the eleventh of its eleven `exclusions`; the code cites it as "cold gate
   10, 2026-09-23, Q2". "Rule 2" most likely means that question 2; the facts it states (mobileassetd, pid 439,
   61.51 core-seconds against the bar of 30) are all correct.
5. **Six short activations between arm and t0.** `events.jsonl` shows activations spawned at 05:54, 06:04, 06:14,
   06:24, 06:34 and 06:44 (attempts 88–93), each exiting within about one minute with reason "clean activation
   exit", followed each time by `BACKOFF_USAGE` (the watchdog's waiting state after an exit it classes as usage exhaustion). The last, `f3b4a769-…`, exited at 06:45:30, before REQUEST
   (06:52:00, the time from which every agent session must be gone), and both watchdog censuses between then and t0 (06:54:41, 06:59:43) were empty. The stored `last_exit_class` `usage_exhausted` sits
   beside a "clean activation exit" transition reason; this record does not diagnose the watchdog.
6. **Census detail in dictated fact 2.** Dictated: the census rows under sequence 392 name pid 18001. Observed:
   the first such row carries sequence 391 (07:04:44, the census that caused transition 392); the rest carry 392.
   Dictated: the last census at 09:25 was empty. Observed: 09:25:22 was the first empty census; a second empty one
   followed at 09:30:23, before the launch.
7. **"Not stale" in dictated fact 10.** See §5: the docs-only diff does not decide supervisor staleness; the reflog
   time does. Supervisor 29843 would refuse to arm on `af879efb` or any later head.
8. **F2 wording in dictated fact 8.** Dictated: the sentence is false for this night. Observed: literally true of
   the machine-wide covariate, misleading (false on its plain reading) as a description of this night, as set out
   in §2.
9. **Heartbeat.** The dictated first heartbeat epoch 1790181335 cannot be checked on disk; the file has been
   rewritten since (1790181560 at 09:39, same pid and activation).

Everything else dictated matched the primary evidence: the spawn fields, the notice id and its acknowledgement, all
seven `night.log` lines, both chain records, twelve `rc=0 cleanup_proven=True clock_attestation=authenticated`
lines, the evidence outcome, the courier record, the courier's thread and retry account, the twelve oversized files
and both local commits, the 16,018 / 16,018 checksum result, the uninstall exit code, every summary figure (11/12,
5 pairs, 0.871 J on 4 df, 1.689 J, 23 pairs, 0.178 cores, envelope 9 on mobileassetd pid 439 at 61.51 against 30),
the synthesis 35 prediction, and the fast-forward `9e816173` → `af879efb` at 09:37 with its 5-file, 225-line diff.
