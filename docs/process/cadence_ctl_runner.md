# ctl-01 runner (draft kit, no collection authority)

Built from `2d347f721552fe03bdd19f113e7bad7a7c24908e`, the
`cadence-legs-v1.1` line. Authority: RL-174 **B.4**, read in full on
`origin/audit/2026-11-10-fable` at `ebff15ad27e831499dd65796b3727d8c5d451e21`;
RL-155 §5.3; RL-172 (b), (i); RL-149 §2.5–2.6; RL-151 §3.3;
RL-169a §1 (sampled recovery if the instrument look requires it).
The ruling is `docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md`
on the audit branch, not an outcome file.

The new runner kind is **`cadence-ctl-v1`**, kit schema
`joulewise.cadence_campaign_kit.ctl.v1`. It uses the existing
`scripts/cadence_legs_runner.py` / `scripts/launch_cadence_span.py` route.
`scripts/cadence_leg_runtime.py` dispatches ctl specs to
`joulewise/align/apple/cadence_ctl.py`. Other leg schemas retain the original
runtime. The gate, R1 runtime, controller and workload files are unchanged.
This is class A, not evidence of native hardware validation.

## Script and evidence contract

The kit supplies each script's physical decode caps, unlogged decode cap,
one-core CPU seconds, split gaps, and sampled recovery seconds. Caps are exact:
an early model return records the delivered dose and leaves the leg unadmitted;
the remaining span continues (RL-149 §2.4). CPU work uses one thread in the leg process, bounded
by wall time; tests advance synthetic time. No worker process needs signalling.

Each leg has one G0, then its q0 history and its script, with one resident model
and uninterrupted member sampling. The physical calls use the same step prompt
and seed, freshly rendered for each call; there is no growing conversation.
There is no G1 or type-T claim. Hidden work occurs after G0 and before the
visible call. CPU work occurs between its two visible calls. Recovery follows
the last decode **inside that member's active sampler**, before teardown.
It does not call R1's temperature-only `observe_recovery` or open another model.
Recovery length is kit data; the draft requests 600 s, pending `lm-inst-01`.

The inherited episode contains **one logged envelope**: its counts sum the
visible physical calls; hidden work is deliberately absent from those counts.
For split and extra-turn scripts this envelope is not an individual physical
turn. `script-work.json` is the separate ground-truth record of physical turn
counts and monotonic intervals, hidden calls, CPU work, gaps and recovery. It
contains no generated text, rail value, fit, score or outcome word. It stays
in the leg runtime directory, is hashed by terminal runtime custody, and is
identified by `script_record_sha256` in the operational result. The future
controls print must consume this explicit contract, not interpret the envelope
as a single physical turn. No controls print or energy reader is supplied here.

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
Production preflight refuses it before Git or host commands; launch refuses
before publishing a fence. The checklist also refuses it. `pin-kit` alone
cannot issue a draft. No queue, arm record, release or measurement is produced.

The 12 scripts are the ruled six hidden doses (128, 256, 512, two each), one
extra-turn script, CPU doses 10/30/90 s, and one split/plain pair. The proposed
data uses a 2,000-token prefill, visible totals 1,024 (2,048 for extra-turn),
CPU turns 512 + 512, split 342 + 341 + 341 with 10 s gaps, and 600 s recovery.
These unruled numeric choices are **draft proposals**, not newly settled policy.

`sha256-scripts-v1` uses separate SHA-256 draw tags for shuffle units, seeds and
the pair order. Proposed layout: L001–L003 pilot, L004–L012 remainder (3 + 9),
two fresh soaks/cold starts. The captures are extra-turn and CPU; all six hidden
legs and both split/plain legs consume. The pair stays adjacent in the second
span under the same reference. Every roster must equal a kit layout span;
partial, crossing and arbitrary subset rosters refuse. The nine-leg cap and
12 h launch ceiling apply. The cold seat must assess this layout's balance;
it is not frozen by this draft. New laws/layouts require a schema change, not
editing the leg order after observing a result.

This branch inherits the v1.1 pin's explicit `--batch-window` and older soak
fence behavior. RL-171's newer qualification runner removes those bounds.
Integration onto the lead's single runner pin is a pre-issue engineering step;
this draft must not be used to authorize an old fence rule as current policy.

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

## Decisions still owed before issue or energy access

Research lead:

1. Read `lm-inst-01`, then confirm/change hidden doses and required recovery.
   RL-174 B.4 prohibits freezing the kit before that read.
2. Confirm the visible prompt/caps, extra-turn shape, CPU intervening shape,
   split gaps and count matching versus literal token-sequence replay. The
   candidate uses fresh identical prompts and equal total decode counts.
3. Accept or replace the one-envelope plus physical-call ground-truth contract
   for the future controls print. No existing K/S outcome rule is amended here.

Lead:

4. Integrate onto the single current phase pin, then select and freeze the kit
   layout, seed, cold starts, dates and consumer balance, including the pilot's
   hand gate. The proposed 3 + 9 layout is not a release decision.
5. Pin the complete executed source/config closure, record authorization, issue
   the kit/queue with their current stop and host-state gates, and run the class
   A native smoke and hand read in an agent-free measurement window.
6. Register and freeze the controls print code/schema/manifest before **any ctl
   energy is read** (RL-174 B.4, RL-149 §2.6). The controls remain print-only and
   outside the series and all fits. The registration's disclosure amendment
   remains the research lead/lead's work; K/S words do not change here.
