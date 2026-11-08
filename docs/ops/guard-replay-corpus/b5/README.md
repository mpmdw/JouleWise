# Block 5 guard-replay corpus (R18): what is here and what is still owed

Written 2026-11-08 by the Block-5 lessons seat (Opus 5.5) for `docs/analysis/b5/LESSONS-FOR-V4-V5.md` §1.4.

## Status: the replayable traces are NOT generated yet

The process names, CPU-s/s values and 10 s interval stamps behind every `contention.request_overlap` flag
are stored only in the Block 5 harvest archives:

- `~/night-archive/harvest-v5-b5-{alpha-a1-20261009T2312Z,beta-a6-20261011T2011Z,gamma-a1-20261012T0420Z}/`,
  specifically `derived/flags.jsonl`, `withheld/spans.json` and
  `sources/night-custody/hazards/monitor/contention.jsonl` plus 1,746-2,485 raw `ps` snapshots per window.

`recompute.json` names these archive roots. The custody manifests and supply census list the files only by
path. The lessons brief and `RUN_STATE.md` item 231 keep every `night-*` path sealed for this seat, so it did not
open them. **One authorized run of the extractor below produces the corpus.** No new collection is needed.

## Files

| File | What it is |
|---|---|
| `extract_b5_guard_corpus.py` | Stdlib extractor. It reads only the four files named above in each harvest root, keeps an allowlist of process and timing keys (the same `CPU_KEYS` / `PROCESS_KEYS` as `joulewise/guard_replay_corpus.py` on `ops/2026-11-08-guard-replay`), and writes a `joulewise.guard_replay.corpus.v1` corpus plus a culprit table. It never reads an energy, power, token or outcome field. A numeric field from a flag's `observed` block is dropped unless it is an offender key. |
| `b5-loss-timeline.json` | What the permitted read gives. It lists every lost GAMMA, ALPHA and BETA unit with its codes, stage, within-stage index, request duration and estimated local time window, plus the stage schedules, per-window flag counts and per-attempt `PHYSICS_IN_SPAN` counts. It is a label and timing skeleton and cannot be replayed. |

## Run it (lead or magistrate; Air, after the restore copy if R17 applies)

```sh
cd docs/ops/guard-replay-corpus/b5
python3 -I -B extract_b5_guard_corpus.py \
  --window alpha=$HOME/night-archive/harvest-v5-b5-alpha-a1-20261009T2312Z \
  --window beta=$HOME/night-archive/harvest-v5-b5-beta-a6-20261011T2011Z \
  --window gamma=$HOME/night-archive/harvest-v5-b5-gamma-a1-20261012T0420Z \
  --corpus-out corpus-b5.json --culprits-out culprits-b5.json > culprits-b5.md
```

Then commit `corpus-b5.json`, `culprits-b5.json` and `culprits-b5.md` here, paste the Markdown into
LESSONS §1.2, and replay it on the guard-replay branch:

```sh
python3.13 -B scripts/guard_replay.py run docs/ops/guard-replay-corpus/b5/corpus-b5.json --run-seconds 830 \
  --guard contention-request
```

`--run-seconds 830` is the v4 D member's active span (LESSONS §2.3). Candidate guards are added as trusted
`module:function` adapters (GUARD-REPLAY.md, "Adapter and trace contract").

## Checks already done on the extractor

- **Synthetic run.** It ran on a synthetic harvest root built from the committed FakeMac journal
  (`tests/fixtures/b5_harvest/l1_monitor/contention.jsonl`), with two members: one clean, one overlapping the
  injected `fseventsd` burst. It produced one window run and two member runs, and the culprit row was
  `fseventsd` at 0.900 CPU-s/s with a 20 s episode.
- **No energy leak.** An `energy_j` field planted in the synthetic flag did not reach either output.
- **Harness check.** The output passes `joulewise.guard_replay.validate` on `ops/2026-11-08-guard-replay`.
  The real `contention_request` adapter returns PASS for the clean member and REFUSE
  (`contention.request_overlap`) for the overlapped member.

## Labels and how to use them

- **Member runs.** These carry the B5 harvest's own verdict as their label: `contended` if the member had
  `contention.request_overlap`, otherwise `benign`. That label is **circular for the B5 predicate**: it was
  produced by that predicate, so it says nothing new about that predicate's accuracy. It is meant for
  replaying a **different** candidate guard against real traces, and every `label_basis` field says so. The
  main candidates are:
  - ruling 8 (≥ 0.5 core sustained ≥ 60 s);
  - a 30 s interval;
  - an energy-scaled bar (LESSONS §1.3).

  Each member run carries `request` (its real span in monotonic ns), so the replay judges the actual span. It
  also keeps 60 s of trace on each side of the request.
- **Window runs.** These are labelled `unknown`. Each is a complete monitor journal of about 4.5-5 h at a 10 s
  cadence. Under GUARD-REPLAY.md, they can be sliced once, by a predeclared non-overlapping schedule, into
  run-length trials for the shadow-mode bound.
- **Strata.** The windows are one host (Mac15,9), one OS build (25G83), displays asleep, on AC. They are
  three nights in October 2026, before photoanalysisd and mediaanalysisd were SIGSTOPped
  (`RUN_STATE.md` item 188).
