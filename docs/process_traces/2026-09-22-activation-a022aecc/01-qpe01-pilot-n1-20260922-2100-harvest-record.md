# Record 01 — pilot night `qpe01-pilot-n1-20260922-2100`: harvest, uninstall, diagnosis and ruling (activation a022aecc, 2026-09-22 23:39–23:50 PDT)

Terms used in this record: an *envelope* is one 600 s capture of the machine
sitting idle, and this night ran twelve of them one after another; an
envelope's *interior* is the 480 s slice measured from 60 s after the
envelope's scheduled start, so that the recorder is already running when the
measured slice opens; the *wall clock* is the host's settable calendar time
and the *monotonic clock* is the host's unsettable elapsed-time counter; a
*clock anchor* is the derived mapping from the power sampler's own timestamps
onto the wall clock, and it is *bounded* when the deriver can prove that
mapping lies inside a stated interval; an envelope is *retained* when its
anchor is bounded and its interior has complete native sample support, and
only retained envelopes carry a joule number into the summary; *start drift*
is how late an envelope actually began relative to the instant the schedule
named for it, and it is reported twice, once by the chain that spawns the
collector (the *chain-level* figure) and once by the collector itself after
it has started (the *session-level* figure, which is always the larger of the
two because it is stamped later); *busy cores* is the machine-wide count of
fully-occupied processor cores, so 1.000 means exactly one core's worth of
work was running somewhere on the machine; the *agent census* is the
watchdog's and the driver's repeated check, run as
`pgrep -lf '[c]odex|[c]laude|[t]3'`, that no AI-agent process of this project
is alive during a measurement; a *daemon* is a background operating-system
service that starts itself and answers to nobody in the project.

## §1 Launch

The watchdog's attempt 84 spawned activation
`a022aecc-f172-4890-b70c-ee6b8ad25288` at 23:39:02 PDT. Evidence:
`/Users/edr/night-custody/magistrate/state.json`, fields
`activation_spawn_epoch_s` 1790145542.316635 (= 2026-09-22 23:39:02 PDT),
`attempt` 84, `resident_session.supervisor_pid` 29407 and
`resident_session.pid` 29411. The same file records the predecessor's exit
class in `last_exit_class`: `usage_exhausted`, meaning the previous
activation ended because its model-usage budget ran out, not because anything
failed.

The heartbeat was written first:
`/Users/edr/night-custody/magistrate/heartbeat` carries
`{"pid":29411,"activation_id":"a022aecc-…","epoch_s":1790145552}`, that is
23:39:12 PDT, ten seconds after the spawn.

The launch email went to the single address
`claude2.glaring610@passmail.net` and carries Gmail message id
`1a0ccfe8cb5c59ee` (verified by fetching that message: one recipient, no cc,
`internalDate` 1790145629000 = 23:40:29 PDT, subject "[JouleWise magistrate]
Launch a022aecc 23:39 PDT 09-22: pilot night 21:00 COMPLETE (GO, 12/12
retained), harvesting + uninstalling next").

The email carried the one queued notice, `transition-349-hold_census`. That
notice's subject is a state change in the watchdog, and the watchdog's own
event log explains it. In
`/Users/edr/night-custody/magistrate/events.jsonl`, the census row stamped
under sequence 348 at epoch 1790136199.54 (21:03:19 PDT) is the first
non-empty census of the night: its `stdout` names pid 17751 running
`scripts/run_night.py run --plan …` from the measurement clone. That is the
night's own driver, not a stray agent. The next line, sequence 349 at epoch
1790136200.554784 (21:03:20 PDT), is the transition `FENCED -> HOLD_CENSUS`
with reason "production census non-empty inside plan span". In plain words:
the watchdog saw a process matching its agent pattern, correctly refused to
launch a new agent session on top of a running measurement, and waited.

The notice was acknowledged at 23:40:43 PDT: `events.jsonl` line 966,
`kind` `notice_acknowledged`, `notice_ids` `["transition-349-hold_census"]`,
epoch 1790145643.6849.

No stand-down request and no STOP file exist: `ls` of
`/Users/edr/night-custody/magistrate/standdown.request` and
`/Users/edr/night-custody/magistrate/STOP` both return "No such file or
directory", and `state.json` records `remote_stop.state` `CLEAR` with detail
"stop branch absent; positive control present". No owner directive issue is
open (see §9 for the one open issue, which is not a directive).

A second email went out on the same thread at 23:44:47 PDT: Gmail id
`1a0cd027cacb7206`, `threadId` `1a0ccfe8cb5c59ee`, same single recipient,
subject "[JouleWise magistrate] OWNER ACTION (sudo): fseventsd pegged at one
full core since 04:49 today; it contaminated the 21:00 pilot night; nothing
armed". It asks Ed for the one action this activation cannot take (§6, §7d).

## §2 Verdict (executed evidence, read at the bench 23:40–23:50 PDT from the custody root)

Custody root (called C below):
`/Users/edr/night-custody/qpe01-pilot-n1-20260922-2100-20260922-2100-1790136000-dbd5cd59517fe6088bd316a2ea1e66e9cb4d9432`

`C/night_plan.json` (schema `joulewise.night_plan.v2`): `plan_id`
`qpe01-pilot-n1-20260922-2100`; `measurement_head` = `repo_head` =
`dbd5cd59517fe6088bd316a2ea1e66e9cb4d9432`; `t0_epoch_s` 1790136000.0
(= 21:00:00 PDT); `window_max_s` 9000; `receipt_class` `DIAGNOSTIC_NO_PACK`
(the night is explicitly a diagnostic run that produces no claim pack);
`registration_path`
`configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v2.json`.

The arm that produced this plan is recorded on `main` at
`docs/process_traces/2026-09-22-activation-ca45291d/01-arm-record-qpe01-pilot-n1-20260922-2100.md`.
Quoting its own identifiers: the night was installed by
`publish-install --candidate $STAGE --notice-accepted 1a0cc3fa26b13a44`,
"`rc 0`, `outcome: installed`, `installed: true`, `phase: complete`,
published 20:12:28 (epoch 1790133147.9), 22 min before install close"; the
notice to Ed was "Gmail `1a0cc3fa26b13a44` accepted ≈20:11:30, one recipient
`claude2.glaring610@passmail.net`, no cc"; the arm-readiness check carries
"check id `3f8ccb3136fd` at 20:10:35"; the plan sha256 is
`280c811fbc27369b5c4219d3eece2e1b47f423e5d51fa4c36b9566d87e34939b` and the
registration sha256 is
`2c5392401a7956dfbb30f316a084541e0f53f214a4ce98c7d56d595ddb2779f1`.

**Driver log** (`C/night.log`, six lines, read in full):

- `2026-09-22T21:00:01.429482-07:00 night driver started`
- `2026-09-22T21:00:01.497460-07:00 night gate verdict=GO`
- `2026-09-22T21:00:01.497601-07:00 night chain digest verified`
- `2026-09-22T23:13:52.762675-07:00 night result verdict=GO`
- `23:15:57.263095` and `23:20:15.645661` — two identical "durable record
  failed" lines, each a `CalledProcessError` from
  `git -C C/results-clone push origin HEAD:night-results/qpe01-pilot-n1-20260922-2100`
  returning exit status 1 (§5)
- `23:19:09.082485 courier attempt=1 heartbeat=True sent=True`

**Chain** (the shell program that runs the twelve envelopes in order).
`C/night/chain.started`: epoch 1790136001.498666 (21:00:01.50 PDT), pid and
process-group id both 17762. `C/night/chain.exited`: epoch 1790144031.724853
(23:13:51.72 PDT), `exit_code` 0. `C/night/chain.stderr.log` is empty
(`wc -c` returns 0). `C/night/chain.stdout.log` records, in order: the
network-time control record being written; `evidence_settle seconds=600` (a
600 s quiet settle before the first envelope); then twelve
`envelope_start` / `envelope_end` pairs, every `envelope_end` reading
`rc=0 cleanup_proven=True clock_attestation=authenticated`; `recorder_pgid`
is 17862 on every one of the twelve lines, so a single power recorder spanned
the whole night; and finally
`evidence_end outcome=complete cleanup_proven=True network_time_restored=True`.

"Cleanup proven" means the chain showed that every process group it spawned
was gone afterwards, not merely that it asked them to stop.
"`clock_attestation=authenticated`" means the harness queried the operating
system's own log for the capture window and confirmed what the wall clock did
during it; that check is new work landed as A267.

**Result** (`C/night/result.json`): `verdict` `GO`; `aborted_reason` `None`;
`refusal_documents` `[]`; `calibration_refusal` `None`; `receipt_class`
`DIAGNOSTIC_NO_PACK`; `census_count` 267; `census_hits` `[]`. An empty
`census_hits` list is the important one: across the whole night the driver
never once saw an agent process of this project alive.
`C/night/receipt.json` exists, 5156 bytes, written 21:00.
`C/night/launchd.night.err` is empty (`wc -c` returns 0), and
`C/night/launchd.night.out` holds the courier's closing summary, whose first
line is: "Delivery complete. The night result email to Ed was accepted
(Gmail message id 1a0cceaea8afe162) and the delivery record is written."

**Evidence outcome** (`C/night/evidence_outcome.json`): `outcome` `complete`,
`envelopes_attempted` 12, `cleanup_proven` `true`, `error` `null`,
`network_time_restored` `true`, `recorder_kind` `powermetrics`.
**Cleanup** (`C/night/evidence_cleanup.json`): `groups` `[17862]`, `residue`
`[]`, `errors` `[]`, `signal_errors` `[]`, `budget_s` 30.

**Network time** (`C/night/network_time_control.json`). Network time is the
operating system's habit of correcting the wall clock against internet time
servers; left on, it can move the clock in the middle of a capture, which is
exactly the defect that ruined the previous night. The harness turns it off
for the measurement and back on afterwards, and records both acts:
`off` — `sudo -n /usr/sbin/systemsetup -setusingnetworktime off` at epoch
1790136001.770985 (21:00:01.77 PDT), `exit_code` 0, stdout
"setUsingNetworkTime: Off"; `on` — the same command with `on` at epoch
1790144031.628076 (23:13:51.63 PDT), `exit_code` 0, stdout
"setUsingNetworkTime: On".

**Courier** (`C/night/courier.sent`): `gmail_message_id`
`1a0cceaea8afe162`, `sent_epoch_s` 1790144348 (= 23:19:08 PDT),
`courier_pid` 29085, `verdict` `GO`, `chain_exit_code` 0,
`results_branch_on_origin` `false`.

**Censuses** (`C/night/censuses.jsonl`): 268 rows, counted by parsing the
file. Every row runs `/usr/bin/pgrep -lf '[c]odex|[c]laude|[t]3'` and every
row has `exit_code` 1 with an empty `stdout`; `pgrep` exits 1 when it matches
nothing, so all 268 checks found no agent process. (`result.json` reports
`census_count` 267; see §9.)

**Summary** (`C/night/evidence/summary.json`, schema
`joulewise.quiet_predicate_pilot_summary.v1`). `status` `SPREAD_RECORDED`,
`evidence_status` `PROVISIONAL`, `retained` 12, `retained_pairs` 6.

- `pair_sd_j` 144.2791108429115 on `pair_df` 5 degrees of freedom. This is
  the standard deviation of the six pair differences below, and it is the
  spread the sizing formula consumes.
- `s_upper` 254.23420803393725, with `s_upper_factor` 1.7620999086329474 and
  `s_upper_reason` "one-sided upper 90% chi-square bound; independent normal
  pair differences assumed". In plain words: with only five degrees of
  freedom the true spread could be considerably larger than the one measured,
  so the method inflates it by a factor of 1.762 before sizing anything.
- `block_two_pairs` 517081, with `block_two_pairs_reason` verbatim:
  "ruling 46b: max(3, ceil(8 * s_upper\*\*2 / delta_j\*\*2)); delta_j=1; stop
  above 24 pairs". Arithmetic check: 8 × 254.234² / 1² = 517,080.1, rounded up
  to 517,081. Block two would need half a million pairs to resolve a 1 J
  difference at this spread, and the method refuses at anything above 24.
- `block_two_stop.outcome` "no cutoff qualifies", `block_two_stop.causes`
  `["sized_pairs_above_24", "observer_floor_above_smallest_holdable_share"]`,
  `block_two_stop.pairs` 517081. `cutoff_authority` `false`; `top_up` `false`.
- `single_envelope_sd_j` 98.86580418386548 (identical to
  `unfiltered_single_envelope_sd_j`); `first_to_last_retained_drift_j`
  −301.8268101329849; `max_abs_delta_j` 342.8903855583943;
  `adjacent_pair_sd_j` 105.48810110894335.
- `busy_cores`: `p10` 1.1987199999999993, `p50` 1.2207999999999988, `p90`
  1.3321599999999993, `max` 3.0976, `min` 1.1647999999999996.
  `clean_machine_busy_cores` holds the identical five numbers.
- `observer_floor_cores` 0.05282276792404742 over `observer_support_s`
  7181.620632706385; `whole_campaign_observer_cpu_s` 1239.619517.

The four role strings, quoted verbatim, because they are what forbids the
obvious reaction to §6:

- `busy_cores_role`: "covariate_only; never excluded"
- `single_envelope_role`: "diagnostic_only; never used for sizing"
- `adjacent_pairs_role`: "diagnostic_only; never used for sizing"
- `block_two_pairs_reason`: "ruling 46b: max(3, ceil(8 * s_upper\*\*2 /
  delta_j\*\*2)); delta_j=1; stop above 24 pairs"

and, for completeness, `observer_definition`: "SELF + reaped CHILDREN,
including collector, recorder, sampler and census; never subtracted";
`clean_machine_definition`: "envelopes passing census, AC and thermal hard
probes; independent of energy retention".

`sizing_pairs` — the six disjoint pairs, `delta_j` = right envelope minus
left:

| pair | envelopes | delta_j |
|---|---|---|
| 1 | 1 → 2 | −342.8903855583943 |
| 2 | 3 → 4 | +2.032679574884412 |
| 3 | 5 → 6 | −3.4848107134944257 |
| 4 | 7 → 8 | +7.417157320020522 |
| 5 | 9 → 10 | −9.348957464205228 |
| 6 | 11 → 12 | +42.0877441105564 |

`adjacent_pairs` — the eleven overlapping neighbour differences, diagnostic
only: 1→2 −342.8903855583943; 2→3 −4.195247311911658; 3→4
+2.032679574884412; 4→5 +3.841467379644371; 5→6 −3.4848107134944257; 6→7
−2.776523414952919; 7→8 +7.417157320020522; 8→9 +3.0061963597275394; 9→10
−9.348957464205228; 10→11 +2.4838695851403827; 11→12 +42.0877441105564. All
eleven are marked `retained: true`. `pairs_above_3_pair_sd` is empty.

### Per-envelope table

Columns joined from three files: `C/night/evidence/summary.json` field
`envelopes[]` (joules, excluded, network-time attestation, chain-level start
drift, busy cores, observer CPU), `C/night/evidence_envelopes.jsonl` (the
chain's own `start_drift_s`, which agrees with the summary to every digit
printed), and `C/night/evidence/envelope-NN/session.json` (wall-clock span
from `start_stamp.epoch_s` and `end_stamp.epoch_s`, interior status, native
sample count, anchor status, and the session-level `start_drift_s`).

| env | wall span (PDT) | joules (480 s interior) | excluded | anchor | interior | native samples | chain drift s | session drift s | attestation | busy median | busy max | observer CPU s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 01 | 21:10:02–21:20:09 | 649.69 | [] | bounded | complete | 2156 | 0.19118 | 0.3554 | authenticated | 2.7280 | 3.0976 | 31.93 |
| 02 | 21:20:22–21:30:28 | 306.80 | [] | bounded | complete | 2151 | 0.15011 | 0.3154 | authenticated | 1.2112 | 1.3552 | 31.31 |
| 03 | 21:30:42–21:40:48 | 302.60 | [] | bounded | complete | 2163 | 0.15010 | 0.3142 | authenticated | 1.2160 | 1.2912 | 31.61 |
| 04 | 21:41:02–21:51:09 | 304.64 | [] | bounded | complete | 2178 | 0.15008 | 0.3123 | authenticated | 1.2152 | 1.3344 | 31.66 |
| 05 | 21:51:22–22:01:28 | 308.48 | [] | bounded | complete | 2170 | 0.15009 | 0.3156 | authenticated | 1.2192 | 1.4048 | 31.55 |
| 06 | 22:01:42–22:11:49 | 304.99 | [] | bounded | complete | 2179 | 0.15006 | 0.2805 | authenticated | 1.2144 | 1.3296 | 31.63 |
| 07 | 22:12:02–22:22:09 | 302.22 | [] | bounded | complete | 2140 | 0.15011 | 0.3156 | authenticated | 1.2064 | 1.2848 | 31.65 |
| 08 | 22:22:22–22:32:29 | 309.63 | [] | bounded | complete | 2189 | 0.15012 | 0.3111 | authenticated | 1.2496 | 1.3328 | 31.55 |
| 09 | 22:32:42–22:42:49 | 312.64 | [] | bounded | complete | 2174 | 0.15011 | 0.3141 | authenticated | 1.2272 | 1.5040 | 31.64 |
| 10 | 22:43:02–22:53:08 | 303.29 | [] | bounded | complete | 2201 | 0.15008 | 0.3130 | authenticated | 1.2224 | 1.3520 | 31.62 |
| 11 | 22:53:22–23:03:28 | 305.78 | [] | bounded | complete | 2158 | 0.15009 | 0.3106 | authenticated | 1.2112 | 1.3088 | 31.60 |
| 12 | 23:03:42–23:13:49 | 347.86 | [] | bounded | complete | 2156 | 0.15010 | 0.3151 | authenticated | 1.2176 | 1.5744 | 31.61 |

Every `excluded` list is empty, every anchor is `bounded` with no `detail`
string, every interior reads `complete` with reason "complete native
support", and every envelope's `network_time_provenance.attestation.reason`
is "no applied clock correction inside the capture window". Native sample
counts run 2140 (envelope 7) to 2201 (envelope 10). Chain-level start drift
is 0.191 s on envelope 1 and between 0.15006 s and 0.15012 s on envelopes 2
through 12. For scale, the registration
`configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v2.json` sets
`start_drift_abort_s` 2 (from envelope 2 on, the chain aborts the whole night
above this) and `start_drift_max_s` 10 (per-envelope exclusion), and the
ruled daytime bench replay bar is 0.5 s
(`scripts/bench_replay_start_drift.py`, module docstring: "must show
chain-level `start_drift_s` <= 0.5 s on EVERY slot").

The one number that does not belong to the crowd is envelope 1 at 649.69 J
against 302–348 J for the rest. Its busy-core median is 2.728 against
1.206–1.250 for the rest. §6 says why.

### Addendum 2026-09-23 00:20 PDT — the ruled label (cold ruling 10, Q1)

Cold-gate ruling 10 (`03-coldgate-packet-daemon-contamination/10-coldgate-fable-ruling.md`, sealed) affirmed option (c) and fixed the label this record and the paper's pilot section carry, verbatim; the stop-branch sentence quoted in §2 and the field `clean_machine_busy_cores` (which means "envelopes passing census, AC and thermal probes", not an idle-machine distribution) may be quoted only immediately followed by it:

> MEASURED ON A NON-IDLE MACHINE. All twelve envelopes were captured while the system daemon `fseventsd` (pid 341) held 0.998–1.000 busy cores in 243 of 243 load-journal samples that carried metrics (2 of 245 rows carried none), in a `scan_old` failure loop logged from 04:49:03 PDT on 2026-09-22, 16 h before t0; `mediaanalysisd` additionally ran at 1.3–1.8 busy cores in ten consecutive 30 s samples and 0.9 in an eleventh (t+243 s to t+547 s of envelope 1). The registered rules (registration v2, sha256 2c539240…) name no exclusion for non-observer processes, so every envelope is retained and the registered summary is reported as computed. This night is NOT used to size block two; the pilot is re-run under registration v3, which adds the non-observer-process rule fixed before that night runs. Both nights are reported side by side.

Two corrections from the same gate: (i) the t0 gate DID apply the legacy load-average predicate (`evaluate_night` → `_check_machine` with `legacy_load=True`, bar 2.0; tonight's 1.03 passed) — it is the arm `check` that omits it; §6's "what the gates could see" should be read with that correction. (ii) The registered stop cause `observer_floor_above_smallest_holdable_share` fired on the clean 02:17 night too (floor 0.0531 > 0.05) and is independent of any daemon; bounded round 2 (charge 20) rules what registration v3 does about it.

## §3 Harvest

`cp -Rp` of the whole night root, including `results-clone/`, from C to the
archive (called A below)
`/Users/edr/night-archive/qpe01-pilot-n1-20260922-2100-harvest-20260922`,
reported by the magistrate as running 23:41:07–23:41:13 PDT. `A` contains the
same top-level entries as C (`chain.zsh`, `chain.zsh.sha256`,
`chain.zsh.chain-source.sha256`, `evidence_manifest.json`, `night/`,
`night-probe.err`, `night-probe.out`, `night.log`, `night_plan.json`,
`night_probe_receipt.json`,
`night_probe_receipt.pending.json.process.json`, `results-clone/`) plus the
two files the harvest itself wrote.

`A/SHA256SUMS` was written from the copy and covers every file except the
git internals under `results-clone/.git/`. Checked: `wc -l` gives 15,959
lines; `grep -c 'results-clone/\.git/'` gives 0; `grep -c 'results-clone/'`
gives 12,302. It was then checked against the LIVE root C, and the check
output is `A/SHA256SUMS-check-against-live-root.txt`:

- `grep -c ': OK$'` → **15958**
- `grep -v ': OK$'` → three lines, all about one path:
  `shasum: ./SHA256SUMS.tmp: No such file or directory`,
  `./SHA256SUMS.tmp: FAILED open or read`,
  `shasum: WARNING: 1 listed file could not be read`

That single non-OK entry is the temporary sums file that existed only inside
the copy while the list was being built. Its recorded digest is
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, which is
the SHA-256 of zero bytes — an empty scratch file. It never existed in the
live root, so the check could not read it there. The arithmetic closes
exactly: `find C -type f -not -path '*/results-clone/.git/*' | wc -l` gives
**15958**, and 15,958 real files plus the one scratch entry is the 15,959
lines in `SHA256SUMS`. Every real file in the archive is byte-identical to
the live root.

Nothing in the night root was moved, altered or deleted. Both the custody
root C and the measurement clone (called CLONE below)
`/Users/edr/JouleWise-measurement-20260922-2100-1790136000-dbd5cd59517fe6088bd316a2ea1e66e9cb4d9432-qpe01-pilot-n1`
are RETAINED: envelopes were captured. CLONE is clean at the frozen head —
`git -C CLONE status --short` prints nothing and `git -C CLONE rev-parse
HEAD` gives `dbd5cd59517fe6088bd316a2ea1e66e9cb4d9432`, the plan's
`measurement_head`.

## §4 Uninstall

Run from CLONE with CLONE's own virtual environment,
`CLONE/.venv/bin/python -m joulewise.evidence_night uninstall --candidate S`
where S is the staging root
`/Users/edr/night-plan-staging/qpe01-pilot-n1-20260922-2100-20260922-2100-1790136000-dbd5cd59517fe6088bd316a2ea1e66e9cb4d9432`.
Exit code 0, at 23:42:02 PDT.

`S/lifecycle/uninstall.json` records the underlying call:
`argv` = CLONE's `scripts/install_night_agent.sh --plan
C/night_plan.json --uninstall --launchctl-bin launchctl`; `exit_code` 0;
`started_epoch_s` 1790145722.9882398 (23:42:02.99 PDT);
`finished_epoch_s` 1790145723.1605802 (23:42:03.16 PDT); `stdout` and
`stderr` both empty strings.

After it: `launchctl list | grep -c joulewise.night` → **0**. `ls -la
~/Library/LaunchAgents` shows five files — `com.joulewise.magistrate.plist`
and four third-party ones (`com.google.GoogleUpdater.wake.plist`,
`com.google.keystone.agent.plist`, `com.google.keystone.xpcservice.plist`,
`com.valvesoftware.steamclean.plist`) — and **no night plist**, neither
`com.joulewise.night` nor `com.joulewise.night.deadman`.

**NOTHING IS ARMED.**

## §5 Results branch not published

The night's driver commits every artefact into a throwaway clone at
`C/results-clone` and pushes that commit to a branch on the project's remote,
so the evidence has a durable home outside this machine. That push failed
twice (§2, `night.log` 23:15:57 and 23:20:15) and was not retried.

Executed checks:

- `git -C C/results-clone log --oneline -1` → `afc3ab7 record night
  qpe01-pilot-n1-20260922-2100`. `git -C C/results-clone status --short`
  prints nothing: the tree is clean, the commit is intact.
- `git -C C/results-clone ls-tree -r -l HEAD | awk '$4>100000000'` → exactly
  **12 files**, all of them the raw power-sampler output, one per envelope,
  under
  `docs/process_traces/night-results/qpe01-pilot-n1-20260922-2100/evidence/envelope-NN/raw/powermetrics-idle-N.plist`:
  133.8, 134.0, 134.4, 134.9, 134.9, 135.1, 133.3, 135.8, 135.6, 136.3,
  133.6 and 134.3 MB for envelopes 1 through 12 respectively.
- `git -C CLONE ls-remote origin 'refs/heads/night-results/*'` lists thirteen
  branches (`20260902`, `20260903`, `20260909`, `20260911`, `20260912`,
  `20260913`, `20260915`, `d079-epoch-25g83-derivation-n1-20260916`,
  `d079-epoch-25g83-derivation-n1-20260917`,
  `d079-epoch-25g83-derivation-n1-20260919`,
  `d079-epoch-25g83-derivation-n2-20260919`, `qpe01-pilot-n1-20260920`,
  `rehearsal-20260916c`). `night-results/qpe01-pilot-n1-20260922-2100` is
  **absent**.

GitHub rejects any single file above 100 MB, and all twelve of these are
above it; that is this record's reading and the courier's, and the driver's
captured error is only the non-zero exit status. The evidence bytes are
intact in C and in A (§3). Publication needs Ed's choice of destination —
Git LFS, excluding the raw sampler files from the results branch (the
reduced per-envelope records already carry every number the summary uses), or
a different store. That is lane A268, unchanged from the previous night.

## §6 Diagnosis: a runaway system daemon held one full core all night

### The observation

Look again at the busy-core column of §2. The whole night sat at a median of
1.221 busy cores. A machine doing nothing should sit near zero. The previous
night's identical measurement, on the same hardware five hours earlier, sat
at a median of 0.2416 busy cores (`P/night/evidence/summary.json`,
`busy_cores.p50`, where P is
`/Users/edr/night-custody/qpe01-pilot-n1-20260922-0217-20260922-0217-1790068620-d45378c6010b538ca1bb74ae0f2222dceb4df1e4`).
Roughly one extra core's worth of work was running this night from the first
sample to the last.

### Who was doing the work

`C/night/evidence_busy_cores.jsonl` is the night's load diary. It holds
**245 rows**, one every 30 s, each row a `top` sample naming the processes
that consumed the most processor time in that interval. Two rows carry no
metrics and say why in their `error` field: one reads "CPU counter regressed
for the same process identity" (the sample spans monotonic 362600.56 to
362630.89, inside envelope 8), the other reads "Command
`('/usr/bin/top', '-l', '2', '-s', '30', '-n', '0')` died with
`<Signals.SIGTERM: 15>`" at the chain's end (monotonic 365578.58 to
365593.37). Both are marked `admits_nothing: true`, meaning the harness
declines to let a broken sample prove anything. The remaining **243 rows**
carry a `top_consumers` list.

Aggregating every `top_consumers` entry across those 243 rows by the command's
file name:

| process | rows present | mean busy cores | max busy cores |
|---|---|---|---|
| `fseventsd` | 243 | 0.998 | 1.000 |
| `mediaanalysisd` | 20 | 0.874 | 1.789 |
| `XprotectService` | 1 | 0.353 | 0.353 |
| `powermetrics` (the night's own recorder) | 234 | 0.094 | 0.118 |
| `corespotlightd` | 14 | 0.058 | 0.104 |
| everything else (about 70 more names) | — | ≤ 0.042 | — |

`fseventsd` is present in **every single one of the 243 metric rows**, at a
mean of 0.998 busy cores and a maximum of 1.000. It is macOS's file-system
events daemon: the service that watches the disk and tells applications when
files change. Its recorded identity is pid 341, started "Fri Sep 18 17:41:17
2026", which is boot time. It was pinned at exactly one core for the entire
two-hour-fourteen-minute night, and it is not a project process.

`mediaanalysisd` is Apple's Photos-library analysis service, which scans
images in the background. Its twenty rows split cleanly. Eleven rows, from
243 s to 547 s after the first sample, run 0.942 to 1.789 busy cores, and all
eleven fall inside **envelope 1**. The other nine rows, scattered in
envelopes 4, 5 and 10, run 0.002 to 0.019 busy cores, which is nothing.
So a second daemon added between one and 1.8 cores for roughly five minutes,
entirely inside the one envelope that reads 649.69 J instead of ~305 J.

That closes the envelope-1 anomaly with no residue: envelope 1 is the only
envelope with a second heavy daemon in it, and it is the only envelope with
an outlying energy number.

### The previous night, for contrast

`P/night/evidence_busy_cores.jsonl`: 238 rows, 236 with metrics. Aggregated
the same way, the heaviest consumer is `powermetrics` itself at a mean of
0.112 busy cores. **`fseventsd` does not appear among the top consumers at
all.** `mediaanalysisd` does appear, in 7 rows, but at 0.002 to 0.017 busy
cores — negligible (see §9). Nothing on that night exceeded 0.112 mean.
`P/night/evidence/summary.json` gives `busy_cores` `p50` 0.2416 and `max`
0.7392, and its two retained envelopes, 2 and 12, read 154.88 J and 151.03 J
over the same 480 s interior.

So the same machine, same protocol, same interior length, read ~152 J five
hours earlier and ~305 J tonight. The extra ~153 J over 480 s is ~0.32 W of
extra draw, which is the right order for one busy core on this part.

### The daemon is still running, and why it is stuck

At the bench in this activation:

`ps -axo pid,pcpu,time,etime,rss,command | grep '[f]seventsd'`

- as dictated, read at 23:43 PDT: pid 341, 99.9 %CPU, cumulative CPU time
  1271:49 (minutes:seconds), elapsed 04-06:01:03 (four days six hours), RSS
  29168 KB.
- re-run by this record at 23:48:32 PDT: pid 341, **100.0 %CPU**, cumulative
  CPU time **1278:01.87**, elapsed **04-06:07:15**, RSS **29136 KB**.

Five and a half minutes of wall time bought 6 minutes 13 seconds of CPU
time. The daemon is consuming a full core continuously and has been since
before this night began. Memory use is flat at ~29 MB, so this is a spin, not
a leak.

The operating system's own log says what it is spinning on. Using the full
path `/usr/bin/log` (the zsh shell has a builtin named `log` that shadows it
and returns nothing):

`/usr/bin/log show --last 30h --predicate 'process == "fseventsd" AND
eventMessage CONTAINS "scan_old"' --style compact`

- as dictated: 798 lines, first 2026-09-22 04:49:03.306, last 23:42:23.
- re-run by this record at 23:48 PDT: **803 lines of output, 802 of them
  messages** (the first line is the `Timestamp Ty Process[PID:TID]` header).
  First message **2026-09-22 04:49:03.306**, identical to the dictated first
  timestamp. Last message **2026-09-22 23:48:34.494**, six minutes later than
  the dictated one, which is simply the four extra messages the daemon logged
  between the two runs.

Every message is the same text:

```
fseventsd[341:…] [com.apple.fsevents:daemon] scan_old: bailing out because device mounted @ [<private>]<private> has dls 0x0 and dls->fci 0x0
```

Counting by hour of the day: 9 messages in the 04:00 hour (the run starts at
04:49), then 45, 46, 47, 44, 45, 45, 45, 44, 43, 43, 41, 39, 39, 39, 40, 38,
39, 39 for the hours 05:00 through 22:00, and 32 so far in the 23:00 hour.
That is a steady 38 to 47 messages per hour, every hour, from 05:00 onward:
roughly one failed retry every 80 to 95 seconds, forever.

Read plainly, the daemon is repeatedly trying to scan an older-generation
record for some mounted device, finding two of its internal pointers null,
giving up, and starting over. It began at 04:49 today, about 22 minutes after
the previous pilot night's chain finished at 04:27, and has not stopped since.

`mount` at the bench lists nine entries: the sealed read-only system volume
`/dev/disk3s1s1 on /`, `devfs on /dev`, the six system-managed APFS helper
volumes (`VM`, `Preboot`, `Update`, `xarts`, `iSCPreboot`, `Hardware`), the
data volume `/dev/disk3s5 on /System/Volumes/Data`, and the automounted home
map `map auto_home on /System/Volumes/Data/home`. There is no external disk,
no network share and no disk image attached, so nothing can simply be
unmounted to clear it.

A related episode is on record: on 2026-09-15 `fseventsd` ran away on this
same machine with a 61 GB resident set and about 190 % CPU, and only a
restart cleared it (memory note "Checkpoint 2026-09-15 restart (fseventsd)").
This episode has a different shape — flat memory, exactly one core, a
specific repeating log line — but the same daemon and, so far as any
non-sudo path goes, the same remedy.

### What the night's own gates could and could not see

The agent census (§2: 268 rows, all empty) does exactly what it was built to
do: it proves no process of *this project* was running. Its pattern is
`[c]odex|[c]laude|[t]3`. `fseventsd` and `mediaanalysisd` are operating-system
daemons and match nothing in it, so a perfect census score and a machine with
a pegged core are entirely compatible. The gate has no load predicate.

The busy-core figure *was* recorded, faithfully, on every envelope. But the
pre-registered rules say what may be done with it, and the summary states the
rule in its own words: `busy_cores_role` is "covariate_only; never excluded".
It is a number carried alongside the energy for later analysis; it is not
grounds for throwing an envelope away. Nothing in the harness was entitled to
refuse on it, and nothing did.

## §7 Ruling within authority, and what is referred to the cold gate

**(a) As a mechanism test, the night passed.** This night existed to prove
that two pieces of new work hold under real conditions, and both did.

- The A269 start-drift cure held. Chain-level start drift was 0.150 s to
  0.191 s across all twelve envelopes, against a 2 s in-chain abort threshold
  (`start_drift_abort_s`), a 10 s per-envelope exclusion bar
  (`start_drift_max_s`), and the 0.5 s bench-replay bar that the cold gate
  ruled as the precondition for this night. The previous night's chain-level
  drift was 0.16 s on envelope 1 and 7.63 s to 10.11 s on envelopes 2 through
  12 (`P/night/evidence_envelopes.jsonl`); its session-level figures ran 7.75
  to 10.23 s. Tonight's worst chain-level figure is fifty times better than
  the previous night's best non-first one.
- The A267 clock attestation ran and authenticated twelve of twelve. Every
  envelope's `clock_attestation` reads `authenticated` and every session's
  attestation reason reads "no applied clock correction inside the capture
  window".
- Every anchor is bounded; every interior is complete; cleanup was proven on
  every envelope and at the end; network time was turned off at 21:00:01.77
  and restored at 23:13:51.63, both with exit code 0.

Twelve retained envelopes out of twelve, against two out of twelve the night
before. As a test of the machinery, this is the first clean pilot night.

**(b) As science, the twelve envelopes are contaminated, and the summary as
registered still stands.** The measurements were taken on a machine with a
runaway system daemon holding one full core throughout, plus a transient
second daemon at 1.4 to 1.8 cores for about five minutes inside envelope 1.
The agent census cannot see either, and the pre-registered rules make busy
cores a covariate that is never an exclusion. So the summary records what it
records and this activation does not touch it: status `SPREAD_RECORDED`,
`evidence_status` `PROVISIONAL`, twelve retained, six pairs, and
`block_two_stop.outcome` "no cutoff qualifies". Pair 1's 342.89 J difference
— the gap between contaminated envelope 1 and the rest — is what drives
`pair_sd_j` to 144.28, `s_upper` to 254.23, and the sizing formula to 517,081
pairs against a stop bar of 24.

**(c) Referred to the cold gate, not decided here.** Two questions arise and
both are changes to pre-registered rules or to the arm procedure, which
rule 11 places outside this activation's authority:

1. Does a documented non-agent daemon holding a full core invalidate this
   pilot for block-two sizing? The busy-core covariate rule was written for
   ordinary background noise, not for a stuck daemon at 1.0 core.
2. Should the arm-readiness check, or the night gate, refuse to run at all on
   a pegged system daemon — that is, should either acquire a load predicate
   or a top-consumer predicate, and at what threshold?

A packet will be assembled for the cold gate carrying the §6 evidence. This
record makes no change to any rule.

**(d) Within this activation's own authority.** No next pilot night is
prepared while `fseventsd` is pegged. The reason is not a rule, it is the
measurement: the window exists to measure a quiet machine, and this machine
is not quiet. Clearing it needs a restart or equivalent, which needs sudo,
which is an owner action. It was requested by email `1a0cd027cacb7206` at
23:44:47 PDT.

**(e) The results-branch publication stays blocked on Ed** (§5, lane A268).
No courier and no magistrate retries the push.

## §8 Canonical fast-forward and next actions

**Canonical fast-forward (executed).** After the uninstall, with no
`joulewise.night` label loaded (`launchctl list | grep -c joulewise.night`
→ 0) and no night plist on disk (§4), `git -C /Users/edr/code/JouleWise pull
--ff-only` moved the canonical checkout from `48842569` to `91f80870`.
Verified now: `git -C /Users/edr/code/JouleWise rev-parse HEAD` →
`91f80870961ce04a93eee2b451ccdb8bfb53134d`; `git -C /Users/edr/code/JouleWise
rev-parse origin/main` → the same hash; `git log --oneline -1` →
"91f80870 Activation ca45291d: pilot night qpe01-pilot-n1-20260922-2100
ARMED (t0 21:00 PDT, head dbd5cd59) through the tracked entry point; arm
record 01, handback Executed block, RUN_STATE top block". D-183 allows the
agent to make this move by hand under exactly those preconditions: it is an
action the agent can take itself, and queuing it for the owner is the stall
D-183 exists to prevent.

**Next actions for a successor:**

1. Confirm `fseventsd` is quiet before any prepare. Check with `top` or with
   `ps -axo pid,pcpu,time,etime,rss,command | grep '[f]seventsd'`; a quiet
   machine shows it near 0 %CPU, not near 100. If it is still pegged, stop:
   nothing is measurable.
2. Discharge ruling 21 condition C3. The replay-driver amendment is in
   flight in worktree `/Users/edr/code/JouleWise-wt-c3-a022aecc` on branch
   `feat/2026-09-22-replay-driver-fidelity-rule` (both verified: `git
   worktree list` shows the worktree at `91f80870`, and `git rev-parse
   --abbrev-ref HEAD` in it returns that branch name). Its pull request must
   show `verdict()` re-run against
   `docs/process_traces/2026-09-22-activation-59857fe5/24-bench-replay.json`
   producing PASS before any later replay artifact is produced or relied on.
3. Assemble the cold-gate packet on the daemon-contamination questions in
   §7(c).
4. Lane A268: publish the results branch once Ed chooses a destination (§5).
5. Only then write `NIGHT_HANDBACK` for the next pilot night.

## §9 Anomalies found while verifying

Each item below is a place where the dictated fact and the primary evidence
differ. The text above always states what the evidence says.

1. **ANOMALY: dictated `mediaanalysisd` in 20 rows "all inside envelope 1
   between roughly 243 s and 547 s after the first sample"; observed 20 rows
   of which only 11 are inside envelope 1.** The eleven rows from t+243 s to
   t+547 s do fall in envelope 1 and carry the material load (0.942 to 1.789
   busy cores). The other nine rows fall in envelopes 4, 5 and 10 (t+2401 s to
   t+2522 s and t+5986 s to t+6077 s) at 0.002 to 0.019 busy cores. The
   reported mean of 0.874 and max of 1.789 are over all twenty rows and both
   reproduce exactly. The substance of the claim — a transient second daemon
   at 1.4 to 1.8 cores for about five minutes, entirely inside envelope 1 —
   holds.
2. **ANOMALY: dictated "everything else under 0.06 mean"; observed
   `XprotectService` at mean 0.353.** It appears in exactly one row, at
   t+7293 s inside envelope 12, at 0.353 busy cores. The next-highest after
   `powermetrics` is `corespotlightd` at 0.058 mean over 14 rows, so the
   dictated statement holds for every process except this single-sample one.
3. **ANOMALY: dictated the prior night had "no fseventsd or mediaanalysisd
   among top consumers"; observed `mediaanalysisd` present in 7 rows.** Its
   seven values are 0.0165, 0.0096, 0.0089, 0.0020, 0.0128, 0.0092 and 0.0171
   busy cores — two orders of magnitude below its envelope-1 behaviour
   tonight, and negligible. `fseventsd` is genuinely absent from the prior
   night's top consumers, as dictated. The contrast the fact was making
   survives intact.
4. **ANOMALY: dictated 798 log lines with last timestamp 23:42:23; observed
   803 lines of output (802 messages) with last timestamp 23:48:34.494.** The
   first timestamp is identical (2026-09-22 04:49:03.306) and the per-hour
   rate is identical (38 to 47 per full hour from 05:00). The difference is
   the six minutes of extra messages the daemon logged between the dictated
   run and this record's re-run, plus the one-line column header the count of
   803 includes.
5. **ANOMALY: dictated `ps` figures at 23:43 (99.9 %CPU, 1271:49, elapsed
   04-06:01:03, RSS 29168 KB); observed at 23:48:32 (100.0 %CPU, 1278:01.87,
   elapsed 04-06:07:15, RSS 29136 KB).** The re-run was requested, so this is
   expected drift rather than a contradiction; both readings are in §6. The
   6 min 13 s of CPU time accrued over 5 min 29 s of wall time is itself the
   proof that the daemon is pinned above one core.
6. **ANOMALY: dictated `mount` shows "only the sealed system volume, the Data
   volume and the autofs home map"; observed nine entries.** The three named
   are all present. The other six are `devfs on /dev` and the standard
   system-managed APFS helper volumes (`VM`, `Preboot`, `Update`, `xarts`,
   `iSCPreboot`, `Hardware`). There is still no external disk, no network
   share and no disk image, which is the point the fact was making.
7. **ANOMALY: `C/night/censuses.jsonl` has 268 rows but
   `C/night/result.json` reports `census_count` 267.** Both were read
   directly. The dictated facts gave both numbers (fact 5 said to read
   `census_count`, fact 9 dictated 268 rows) so neither is wrong on its own,
   but they disagree by one. The most likely reading is that the driver
   writes its count before appending its final census row. It does not affect
   the verdict: `census_hits` is empty and all 268 rows have `exit_code` 1
   with empty `stdout`.
8. **ANOMALY: dictated "the prior night had 7.75–10.23 s" of start drift;
   observed that this is the session-level range, while the chain-level range
   is 7.63–10.11 s.** Tonight's 0.150–0.191 s figures are chain-level, so
   §7(a) compares chain-level against chain-level (7.63 to 10.11 s) and names
   the session-level range separately. Read from
   `P/night/evidence_envelopes.jsonl` (chain-level) and from the previous
   night's own record 01 table (session-level).
9. **ANOMALY: dictated the second email was sent "23:45"; observed
   `internalDate` 1790145887000 = 23:44:47 PDT.** Same thread
   (`1a0ccfe8cb5c59ee`), same single recipient, same id `1a0cd027cacb7206`.
10. **ANOMALY: dictated "No directive issue open"; observed one open issue,
    #366.** No issue carries a `directive-notice` label, so no *owner
    directive* is open and the dictated fact holds in the sense that governs
    the launch checklist. For the record, issue #366 ("Re your requested
    decision by me via email — the JouleWise magistrate (Claude), activation
    d0b83820", created 2026-09-20T03:40:48Z, no labels) is open; it was
    posted under Ed's GitHub account by the magistrate asking Ed for a
    decision, so it is an outbound ask, not an inbound directive.
11. **Could not verify: the exact harvest copy window 23:41:07–23:41:13
    PDT.** `cp -Rp` preserves the source files' timestamps, so the copy's own
    start and end are not recoverable from the archive, and no command log
    for it survives in `/tmp` for this boot. What is verifiable and
    consistent with it: the archive directory and `A/SHA256SUMS` carry
    modification time 23:41:23 PDT and
    `A/SHA256SUMS-check-against-live-root.txt` carries 23:41:31 PDT, both
    after the dictated window, and the 15,958-file byte-for-byte match
    against the live root (§3) is direct evidence that the copy completed
    correctly whatever its exact clock times.

Everything else dictated matched the primary evidence exactly, including all
plan fields, all six `night.log` lines, both chain records, the empty chain
stderr, all fifteen `chain.stdout.log` claims, the result verdict and its
null fields, the evidence outcome and cleanup records, both network-time
control entries, the courier record, every one of the twelve per-envelope
rows across three source files, all twenty-one summary statistics, the four
verbatim role strings, the six sizing-pair and eleven adjacent-pair deltas,
the 15,958 OK / one non-OK checksum result, the uninstall record and its
aftermath, the results-clone head and its twelve oversized files, the absence
of the results branch on the remote, and the canonical fast-forward to
`91f80870`.

**Addendum (2026-09-23 03:10 PDT, magistrate 7a0f14bd, fix round 1 of lane QPE01-NONOBSERVER-PREDICATE-01, ruling on contract-lens finding S1).** The component split in the addendum above is corrected. `whole_envelope_observer_cpu_s` is the collector's own CPU plus the CPU of the children it reaped; the 30 s load recorder is launched by the executor as a sibling of the collector and is therefore NOT inside that figure. Re-derived from this night's bytes with the v3 code (per-envelope shares, mean over 12 envelopes): round block 0.0521 cores and reaped power recorder 0.107 cores, which sum to the floor 0.159 (unchanged, the ruled statistic); the load recorder's own 0.0071 cores is outside it, so the apparatus including the load recorder is 0.166 cores (reported as `observer_floor_including_load_recorder_cores`, never a stop input). The earlier "≈ 0.101 power recorder" subtracted the sibling's cost from a total that never held it. Ruling 31's `definition` sentence ("including … load recorder") is therefore inaccurate for that one term; the sentence stays as ruled and the inaccuracy is carried to the block-two consult. Nothing measured changes; the stop cause stands.
