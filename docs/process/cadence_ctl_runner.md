# ctl-01 runner (draft kit, no collection authority)

Originally built from `2d347f721552fe03bdd19f113e7bad7a7c24908e` and integrated
with the admitted qualification pin `6e9d42f1dd3d308bc9239143d0d634ab965e50e1`.
The resulting ctl runner is a new pin under RL-179 F-11.
Authority: RL-174 **B.4**, read in full on
`origin/audit/2026-11-10-fable` at `ebff15ad27e831499dd65796b3727d8c5d451e21`;
RL-155 §5.3; RL-172 (b), (i); RL-149 §2.5–2.6; RL-151 §3.3;
RL-169a §1 (sampled recovery), and RL-186 §2 (audit commit `5a1151544`).
The ruling is `docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md`
on the audit branch, not an outcome file.

The new runner kind is **`cadence-ctl-v1`**, kit schema
`joulewise.cadence_campaign_kit.ctl.v1`. It uses the existing
`scripts/cadence_legs_runner.py` / `scripts/launch_cadence_span.py` route.
The span runner selects the scripted child through `--scripted-ctl`, and
`scripts/cadence_leg_runtime.py` dispatches it to
`joulewise/align/apple/cadence_ctl.py`. Ordinary legs retain the original
child invocation. This is a class A candidate with synthetic verification.

## Script and evidence contract

The kit supplies each script's physical decode caps, unlogged decode cap,
one-core CPU seconds, split gaps, and sampled recovery seconds. Caps are exact:
an early model return records the delivered dose and leaves the leg unadmitted;
the remaining span continues (RL-149 §2.4). The CPU dose uses one thread's CPU
clock. The existing child and workload deadlines bound wall time. Timed
intervals require observed monotonic elapsed time, and CPU work also
requires the requested thread CPU time. Tests advance synthetic time.

Each leg has one G0, then its q0 history and its script, with one resident model
and uninterrupted member sampling. The physical calls use the same step prompt
and seed, freshly rendered for each call; there is no growing conversation.
There is no G1 or type-T claim. Hidden work occurs after G0 and before the
visible call. CPU work occurs between its two visible calls. Recovery follows
the last decode **inside that member's active sampler**, before teardown.
It does not call R1's temperature-only `observe_recovery` or open another model.
Recovery length is kit data. The draft retains 600 s pending `lm-inst-01`.

The inherited episode contains **one logged envelope**: its counts sum the
visible physical calls; hidden work is deliberately absent from those counts.
For split and extra-turn scripts this envelope is not an individual physical
turn. `script-work.json` is the separate ground-truth record of physical turn
counts and monotonic intervals, each call's starting context token count,
hidden calls, CPU work, gaps and recovery. It
contains no generated text, rail value, fit, score or outcome word. It stays
in the leg runtime directory, is hashed by terminal runtime custody, and is
identified by `script_record_sha256` in the operational result. The record
also binds the canonical leg spec digest. Before invoking the workload the
scripted child checks that digest against the span's planned spec. The
parent checks the authenticated record against the same plan and derives
completion from the ordered calls and intervals before desk admission. A
short dose stays on disk and is excluded. An unrelated or unbound result
refuses the span. The future
controls print uses the custody-bound record for physical calls. RL-186 §2.3
allows only script kind, doses, physical call counts and durations, logged
counts, phase values above baseline on the four channels it lists, joules per
hidden token, dose-response slope and range, floor units, the 1% closure
check and the qualifier. It excludes generated text, token IDs, K and S
thresholds, scores and words, detection words, and series members. The
split/plain display labels the same prompt, seed and total counts, describes
the different context depth, and prints each starting context count. The
print, output schema and manifest are separate deliverables.

The runtime binds the scripted endpoint for the life of that child process,
restores the original binding on every exit, and uses the existing deadline,
signal cleanup and custody machinery. Incomplete scripts never become admitted
complete legs. A G0 timeout dispatches no script. A bad consumer reference
refuses before work. The outer runner retains the existing load-redo quota,
create-once directories, cleanup reserve, host restore and desk projection.
Neither doses nor ground-truth records are added to the desk's allowlist.

## Draft, reproducible kit

`docs/process/cadence/kits/cl-ctl-01.draft.json` is **UNFROZEN**, with
`status: draft`, `authorizes_spans: false`, and zero pin/hash placeholders.
Production preflight refuses it before Git or host commands. Launch and
checklist also refuse the draft. The production runner verifies the issued
kit's Git pin and frozen paths before host work.

The 12 scripts use six hidden-dose legs, one extra-turn script, CPU doses
10/30/90 s, and one split/plain pair. RL-186 accepts visible totals of 1,024
(2,048 across two calls for extra-turn), CPU turns 512 + 512, and split turns
342 + 341 + 341. The draft still carries hidden doses 128, 256 and 512 twice
each, a 2,000-token prefill, 10 s split gaps and 600 s recovery.

After `lm-inst-01`, `joulewise.cadence.ctl.apply_instrument_read` takes the
lead's scalar inputs and regenerates a draft for review. It keeps the three
default doses unless 128 falls below both the GPU rail and DC-in floors. In
that case the research lead supplies the three raised doses. Common recovery
is five times the printed return time clamped to 120–600 s. The split gap is
the larger of 10 s and five times the decode-end lag rounded up to whole
seconds. Prefill uses 2,000 if represented in the look and the nearest
represented size otherwise. An equidistant pair needs a research-lead
choice. The helper runs no look and leaves issuance and pinning to the lead.

`sha256-scripts-v1` uses separate SHA-256 draw tags for shuffle units, seeds and
the pair order. RL-186 accepts master seed 2026111601 and the 3 + 9 layout.
L001–L003 is the counted pilot and first native run. Its F-3(c) hand-read
holds L004–L012 until PASS. The first native split leg is read before the
look. Each span has a fresh soak and a capture. The extra-turn and CPU legs
capture, and the hidden and split/plain legs consume. The split/plain pair
is adjacent under the same reference, with the same prompt, total cap and
split leg's deterministic seed. Each split call starts at the plain call's
logical turn zero for native seed derivation. A cold kit seat assesses capture and
consumer balance before issue. Each requested roster must equal one kit
layout span, and the nine-leg cap and 12 h launch ceiling apply.

## Launch authority

Use the selected span's `kit.sha256` from the validated queue as
`--kit-sha256` for both ctl checklist and launch. Both compare the exact
kit bytes they read to that digest. The checklist also checks the
observations against it. A mismatch at launch refuses before host probes,
ledger changes, fence creation or bootstrap.

The lead obtains the predecessor from the shared launcher's `close-proof`
command. Export the current close checks using the existing RL-179 item
variables `HOST_RESTORE_OK`, `FEEDS_STOPPED`, `GROUPS_ABSENT` and
`FOREIGN_PROCESSES_ABSENT` as `1`, with `CLOSE_PROOF_RECEIPT` set to the latest
attempt's exact receipt path. The CLI and ctl launch require that proof. They
also refuse failed or contradictory shutdown evidence in the receipt, even
when all four checks are supplied. A native cadence receipt must record a
successful restore command and an integer AC Automatic readback of 0.
For ctl the launcher requires `--attempt-ledger`,
`--previous-close-receipt`, `--span-id` and `--t0-not-before-ns`. Under the
fence lock it re-proves that the receipt belongs to the latest attempt, its
restore succeeded, and the receipt path and exact close time match the
supplied proof. It publishes the successor attempt before bootstrap, and
passes the verified queue digest to the child. The child refuses
substituted bytes before creating production dependencies or output. It
checks both the wall reading and the full interval projected from the
sleep-inclusive arm clock against the exact close time before creating its
output. RL-179 F-2 allows start at the proven close with no timed gap. ctl
uses free t0, with the launch deadline and any explicitly requested batch
window. Qualification retains its date and time bounds.

Safe local rehearsal (output must be a fresh directory):

```sh
python3.13 -B scripts/cadence_queue.py validate-kit \
  docs/process/cadence/kits/cl-ctl-01.draft.json --batch-window 02:00-02:35
python3.13 -B scripts/cadence_legs_runner.py plan \
  --kit docs/process/cadence/kits/cl-ctl-01.draft.json \
  --legs L001,L002,L003 --batch-window 02:00-02:35 --t0 1794912000
python3.13 -B scripts/cadence_legs_runner.py mock \
  --kit docs/process/cadence/kits/cl-ctl-01.draft.json \
  --legs L004,L005,L006,L007,L008,L009,L010,L011,L012 \
  --batch-window 02:00-02:35 --t0-local 2026-11-17T02:40 --output /tmp/ctl-rest-mock
```

The CLI mock executes the outer runner with fake legs. The stronger
`tests.cadence.test_ctl` rehearsal runs **all twelve real scripted leg runtimes**
on the existing synthetic backend through both spans, authenticated consumer
references, close, and the desk. Tests inspect only synthetic counts, clocks,
custody hashes and stage markers, never rail samples. Native launch and
process-signalling behavior is stubbed in ctl tests; existing fixture process
tests are not a substitute for the eventual lead-controlled native smoke.

## Review and issue

1. An independent executing Astra 6.2 seat reviews the runner candidate
   under RL-186 §2.6.
2. After runner admission, the research lead reads `lm-inst-01` and records
   the freezing line for doses, recovery and gap. The prompt size is also
   checked at the read.
3. The lead obtains the cold kit review, then issues the pinned kit and
   counted pilot. The pilot requires its hand-read before the remaining
   span is eligible.
4. The controls print code, schema and manifest hash are committed before
   any ctl energy is read. The lead then commits the research lead's blind
   disclosure amendment after the final close and before the look.
