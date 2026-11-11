# BYTES blinding check before the stage-1 commitment (RL-7 (g); `P1-AUTO-BLINDCHECK`)

**What this is.** This record holds the check that research lead ruling RL-7 (g) requires:

> The check behind `P1-AUTO-BLINDCHECK` (whether any held-out model's timing was read before the commitment) is
> made by a seat that reads structure only, recorded before the commitment, and printed whichever way it falls.

RL-33 item 4 adds: "It is a disclosure for the paper. It is not a journal event, and the journal starts empty".
The source for both is `docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md` on
`audit/2026-11-10-fable`. The stage-1 commitment commit should cite this file by path and commit. The question
comes from Paper 1's fill index (`P1-AUTO-BLINDCHECK`) and from the 2026-10-27 pipeline-audit critique, item 3
(`docs/process_traces/2026-10-27-pipeline-audit/CRITIQUE.md` on `main`).

- **Who.** Paper 1 seat 11: an Opus 5.5 builder (Claude Code session `session_015ASG1SrSpw9XS9iFbCppXf`) working
  under the Fable 5.2 research lead's plan (RL-24 #11). It ran on the Air, in the worktree
  `jw-wt/p1-seat11`. The seat did not connect to the MBP.
- **When.** 2026-11-11, 00:06 to 00:20 PST (times from `date`).
- **Against what.** Every commit reachable from the Air's `origin` remote-tracking refs (1,695 refs, stale ones
  included), after a full `git fetch origin` made between 00:06 and 00:12 PST. At that fetch `origin/main` was
  `62a87aaad`, the PR #701 head `lane/2026-11-07-bytes-stage1` was `912cf8c3a`, and the run lineage
  `lane/2026-11-07-bytes-stage1-run` was `f161857fe`. The check also listed the branch names of the
  JouleWise-data repository (names only).
- **Window.** Commits from 2026-10-25 00:00 PDT onward. The first BYTES session was armed on 2026-10-25
  (`RUN_STATE.md` item 70). Before that date no registered BYTES session existed. The earlier H sessions were pre-registration sizing runs.

## Answer

**Yes, a held-out model's timing was read before the commitment.** The commitment does not exist yet. All the
reads below concern **Llama-3.3-70B-Instruct-4bit**, a held-out dense model (registration §2), in its pass-1
session `r1-bytes-s5-p1`. Sub-pack s5 holds that model alone.

1. **M2, 2026-10-28: per-request decode durations, recorded in git.**
   - Who and why: magistrate activation 39206674 (Opus 5.5, headless). The thermal cold judge's ruling required a
     "structural read" of s5-p1 before s5-p2 armed (registration §21 item 6). A local Sonnet agent did the read,
     and the lead ran the judge's criterion on its output.
   - What was read: from each of the 50 science members, the decode `phase_start` and `phase_end` events, the
     clock anchor, and the frequency, residency and idle fields of `rich_telemetry.jsonl.zst`. Power-like keys
     were dropped at load.
   - What was written: the report printed each member's **decode span in seconds** (column "dec s" of its §2
     table), a range of decode lengths in its method text, and a comparison of decode spans for the members in
     "fast mode".
   - Where it is: `docs/process_traces/2026-10-28-magistrate-39206674/M2.md`, committed in `de31fd0b5`
     (2026-10-28 04:30 PDT, before any pass-2 t0). It has been on `main` since then (blob `2dbc18fb…`), and 357
     origin refs contain that commit. The scripts (`m2-scripts/`) were removed from `main` by the prune
     `71dea4e09` (2026-11-06). M2.md is not on the run lineage at `f161857fe`.
   - How this seat established it: from the print statements of `m2-scripts/report.py` at `de31fd0b5` (code) and
     from a count of duration-shaped lines (`tools/duration_scan.py`). This seat did not open M2.md.
2. **M1, 2026-10-27: request-relative thermal timing, not request durations.**
   - Who and why: magistrate activation a46602ae (Opus 5.5, headless) ran `thermal_locate.py` and `tail_len.py`
     on all 50 science members. The purpose was to locate the OS thermal readings that removed ten members.
   - What was read: `metadata.json`, `events.jsonl` and `hazards/thermal.jsonl`, through
     `joulewise.b5.harvest.member_spans`.
   - Request spans were computed in memory and **not printed**. The scripts' print statements and the masked
     output format show what was printed: the thermal read count and largest poll gap; for each member, the
     category of each nonzero read; each episode's length and its onset after the latest request end, both
     rounded to 5 s; and the minimum, median and maximum of the post-request tail (member end minus request
     end). That tail is the protocol's post-request stage. It is not the request.
   - Where it is: commit `fe904b556` (2026-10-27 12:27 PDT). The `m1/` files were removed by `71dea4e09`. The
     episode lines are still on `main` in `docs/process_traces/2026-10-27-magistrate-a46602ae/brief-thermal70-r2.md`,
     which briefed the round-2 thermal council seats.
   - What it motivated: M1 led to the pass-2 thermal window of registration §21 item 3, which names s5-p1 as its
     "forcing problem". So that rule **was motivated by structure seen on a held-out model**, as the critique
     asked to be stated.
3. **Session-level timing, by design.** The operational record carries each session's arm, start and end clock
   times and its chain minutes:
   - where: `RUN_STATE.md`, the magistrate `RECORD.md` files, `docs/process_traces/2026-10-27-pipeline-audit/segments.json`,
     and the `night-results/r{1,2}-bytes-*` record branches;
   - what this means: s5 (Llama-70B) and s6 (Qwen3.5-122B) each hold one held-out model, so their session
     totals bound that model's member wall time coarsely. These are session totals, not per-request durations;
   - what was already known: planned member wall times per sub-pack were registered before collection
     (registration §5 sizing), and the decode time of every model was measured without power before
     registration (the BYTES pilot of 2026-10-14, registration §2).
4. **Registered programs.** The desk harvests and the BY-THERM-LINES run on all 12 sessions (activation 39cdeb12,
   2026-10-31) read every clock by construction. In the committed record their output is acceptance, counts and
   flags. A masked scan of the 39cdeb12 record found no timing line. Their own outputs stay off the repo and
   were not examined.
5. **No guarded unblinding has happened.** On every origin ref:
   - no commit touches `docs/bytes/stage1/`, the commitment guard's metadata path (`scripts/bytes_commitment.py`
     constants `METADATA`, `JOURNAL`, `RELEASE`);
   - the protected records ref `refs/heads/records/2026-11-bytes-stage1` does not exist (`git ls-remote`, about
     00:15 PST);
   - no `predictions.json` or `predictions.sha256` is committed.

   The stage-1 commitment and the unblinding journal therefore do not exist yet, which matches RL-33's "the
   journal starts empty".

No held-out **energy, power or cell value** was found in the committed record by this check. That statement is
limited to the scans named below. This seat read no energy.

## Why none of this can change the committed lines

- **What is committed.** Registration §11 lists the commitment's content (`predictions.json`): the manifest's
  SHA-256, the estimator's SHA-256, the NEG-8 inputs, the fit points, the rival lines, the fit-model tier inputs,
  the H1 and H2 family sizes and the dense-linearity note. Stage 1 releases the three fit-set models' keys and
  `neg8_reference` only. "A held-out configuration's raw meter samples are not loaded".
- **How it is computed.** `joulewise/bytes_analysis.py` computes it at SHA-256 `18582818…0a71` (verified in this
  tree). The file was last changed on 2026-10-24 (`86a0185da`), before the first BYTES session and before M1 and
  M2. The frozen manifest `configs/bytes/bytes_manifest.json` (SHA-256 `76452108…6264`, verified) was last
  changed on 2026-10-22. Neither has changed since.
- **Where held-out decode time enters.** It enters the time rival only at stage 2, as the held-out model's own
  measured τ evaluated against the committed line. It is not an input to the commitment.
- **What changed after the reads.** Every change, after M1, to the registration, the pack registrations, the
  manifest, the estimator or the analysis drivers on the run lineage:
  - `e624d67c7` (10-27 19:10): the end date;
  - `de35f6403` and `93aad7b19` (10-28 04:20 and 04:34): §21, pass 2 registered. Item 3's window had already been
    ruled by the cold judge before M2 ran, and M2 could only withdraw it, by a criterion fixed in advance. It
    held, 1 of 9;
  - `7b622eb95` (10-28 06:20): pass-2 sizing rows;
  - `276d05201` and `eb22ccac0` (11-10): the commitment and probe guards of RL-7 (a). RL-33 records that these add
    no arithmetic and that the estimator digest is unchanged.
- **Fit-set members and the pass-2 window.** §21 item 3 also applies to the fit-set packs' pass-2 members (s1-p2
  and s2-p2). It was registered before any pass-2 t0, blind to every energy. Its window is a sub-span of the
  hull, so it can only keep members that the hull would remove. `RUN_STATE.md` item 155 says that the 2026-10-31
  BY-THERM-LINES run found every pack other than s5 equal to its registered line. *Relayed, not verified by this
  seat.*

## Draft text for `P1-AUTO-BLINDCHECK`

**Ruling.** Research lead RL-44 (2026-11-11, on `audit/2026-11-10-fable`): ADMIT. BYTES keeps its confirmatory
status. The exposure is logged as deviation BY-BLIND-1 (`docs/registrations/bytes_deviation_log.md`).
Llama-3.3-70B stays in the registered families and is marked in every table, and the H1 summary is also stated
over the other six held-out models. This draft carries RL-44's two additions: the timing closure covered analysis
exports while these were reads of raw session records, and the check covers only the committed record.

> One held-out model's per-request timing was read and published before the stage-1 commitment. The
> registration's timing closure kept clock times out of analysis exports. These were not exports: an operations
> agent diagnosing a thermal hazard read the raw session records, which the closure did not cover.
> - On 2026-10-28, a structural check required by the pass-2 thermal ruling read each of the 50 science members
>   of Llama-3.3-70B's pass-1 session. It read GPU and CPU frequency and residency during decode, and each
>   member's decode duration, which it committed to the project record. It read no energy or power field.
> - A day earlier, a thermal diagnosis on the same session read when the OS thermal level rose relative to each
>   request's end. That reading motivated the pass-2 thermal window.
>
> Separately, the public operational record of every BYTES session carried one timestamp per session stage. From
> these, the wall time of a held-out stage can be derived coarsely, but no per-member or per-request duration.
> Whether anyone derived it is not known.
>
> Each model's approximate decode time was measured without power in the design pilot and registered before
> collection. A stage's wall time, which includes loads, waits and cool-downs, tells a reader less than the
> registration already did.
>
> None of this can change the committed predictions. They are computed from the three fit-set models only, by an
> estimator whose digest was fixed on 2026-10-24, before the first BYTES session, from a manifest frozen on
> 2026-10-22. Held-out decode time enters the time hypothesis only as that model's own measured value at stage 2.
> Our check covers the committed project record only. It cannot show that held-out timing was never read by other
> means.

*Draft limitations sentence for Paper 1 §8.*

> BYTES's blinding was breached once, on timing and not on energy: before the predictions were committed, the
> decode times of one held-out dense model, Llama-3.3-70B, were read from raw session records and published in the
> project record, and the public operational records carried per-stage timestamps of every session. The committed
> predictions could not depend on either. That model is marked in every table, and the
> held-out summary is also stated without it. Our check of whether held-out timing was read covers only the
> committed record.

(Draft only. The fill belongs to the Paper 1 fill seat, and the research lead checks it. The order follows RL-45: the
per-request read of one model, then the per-stage stamps of every session, then the pilot registration.)

## night-results structure probe

RL-44 (b) item 2. The probe was run by the lead and is appended verbatim. This seat did not run it and did not open
these branches.

> Structure-only probe (lead, 2026-11-11 ~00:40 PST), 14 branches `origin/night-results/r{1,2}-bytes-*` after a fresh fetch, files under docs/process_traces/night-results/<session>/ only, key paths only, no values read. Every branch carries the same operational files: arm_collectors.json, arm_decision.json, censuses.jsonl, chain.exit-census.json, chain.exited/started, courier.*, executed_inventory.json, hazard_result.json, lineage.json, meter_supervision.jsonl, monitor_supervision.jsonl, network_time_off.action.json, result.json, stage_yield.jsonl (plus refusal.json on r1-bytes-s6-p1). **Per-stage clock: YES.** stage_yield.jsonl holds one record per stage (7 per session) with keys {stage_id, role, ordinal, planned, present, succeeded, min_valid, status, rc, counted_at, at.{wall_s, monotonic_ns, monotonic_raw_ns}}. The `at` stamp per stage means differences between consecutive stages give coarse per-stage wall time, including stages that ran held-out models. **Per-member or per-request duration: NO.** No file carries a member-, request- or run-level clock or duration. The other time-like keys are arm, census, courier, supervision and stop-request timestamps (hazard_result.json *.stop.requested.*, lineage/supervision requested.*), plus the executed_inventory taken.* stamp. Consequence for the paper sentence (RL-44 (b)2): the public session records allow per-stage, not per-member, timing of held-out stages.

## What this seat could not establish

- **Reads that left no commit.** Agent transcripts, `~/night-archive` seat directories, MBP shell history, email,
  cloud-session logs, and the JouleWise-data report branches. The last were listed by name and not opened;
  the BYTES-related ones include the thermal council and judge branches `claude/by-thermal70-*`,
  `claude/by-therm-*`, `claude/by-p2-*` and `claude/bytes-*`. Whether any seat read held-out timing outside git
  is not known.
- **Who read M2.md after 2026-10-28.** It is on `main`, so any later seat that read it saw a held-out model's
  decode durations. Git does not record reads.
- **The `night-results/r{1,2}-bytes-*` record branches.** They are committed operational records, including
  `stage_yield.jsonl` for every session. The binding rule for this seat forbids `night-*` paths, so their names
  were listed and their contents were not opened. Whether they carry per-module or per-member timestamps is not
  established. *Answered since by the lead's probe, in the section "night-results structure probe" above: per-stage
  clocks yes, per-member or per-request durations no.*
- **Off-repo outputs.** The outputs of the desk harvests and BY-THERM-LINES on the MBP.
- **The gap between this check and the commitment.** The commitment seat should close it by re-running the
  census from a fresh fetch:

  ```
  git fetch origin
  python3 -I docs/process_traces/2026-11-11-bytes-blindcheck/tools/census.py 2026-11-11T00:00 > hits.tsv
  python3 -I docs/process_traces/2026-11-11-bytes-blindcheck/tools/duration_scan.py <commit:path for each hit>
  ```

  It should then record any new hit in the commitment commit's message. Until the commitment, no seat opens
  `M2.md`, the M1 brief (`brief-thermal70-r2.md`), or the `m1/` and `m2-scripts/` files at their old commits
  (RL-44 (b) item 4). No seat derives stage durations from the `night-results/r{1,2}-bytes-*` branches either
  (RL-45).

## This seat's own exposure (disclosed)

The seat meant to read structure only, and it did not entirely. While reading code, it saw these values:

- **The decode-length range of Llama-70B's s5-p1 members.** It is a literal in the method text of
  `m2-scripts/report.py` at `de31fd0b5`, which the seat read in full to learn what M2 printed (2026-11-11, about
  00:13 PST).
- **In committed text it had to read:**
  - M1's post-request tail and episode ranges (`CRITIQUE.md` item 3; `RUN_STATE.md` item 78);
  - the M2 frequency figures quoted in registration §21;
  - the registered pre-collection sizing rows for s5 (registration §5).

It saw no energy, power or cell value of any held-out or fit-set BYTES model. It did not open M2.md, the `m1/`
outputs, custody, archives, `night-*` paths or the withheld store. Apart from the KB slot record, which is
released, every other file was read either as code or with every digit masked (`tools/masked.py`,
`tools/maskl.py`).

## Method and files in this directory

- `tools/census.py`: for every non-deleted blob changed since the window start on origin refs, outside
  `night-results/` and `.codex-report/logs/`, it counts held-out session and model tokens. It prints the path,
  commit and counts only. Output: `census_hits.tsv` (1,261 blobs).
- `tools/duration_scan.py`: for the 128 process-trace, report and registration blobs among the hits, it counts
  lines that pair a decode, request, member or duration word with a seconds-valued number. It prints counts and
  line numbers only. Output: `duration_scan.tsv`.
- `tools/masked.py`, `tools/maskl.py`: print chosen lines with every digit replaced by `#`. They were used to
  classify each flagged file (BYTES or ALIGN; protocol, sizing, synthetic or measured).
- Classification of the flagged files, beyond items 1 to 4 above:
  - the `2026-11-02-magistrate-0eafdaa2` and `2026-11-03-magistrate-af17111e` hits are ALIGN episodes;
  - the `.codex-report/BY-THERMAL70*`, `BY-P2-THERM-REV-SOL` and `by-therm-lines-rev-sol-*` hits are code
    citations, synthetic streams and the pre-registration sizing operands;
  - the `REGGATE-*` and `KB-*` hits predate collection or concern the known-bytes test.
