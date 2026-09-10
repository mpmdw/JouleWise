# 10 — Cold-gate Fable ruling on packet 31: the 07:00 dead-man firing of 2026-09-10 and NIGHT-REHEARSAL-01 item 5

Cold Fable adjudicator (rule 11), single non-interactive foreground session, worktree detached at `58d4696b`,
2026-09-10 07:05–07:12 PDT. Packet digest verified: `sha256(00-PACKET.md ++ exhibit-A)` = `a4dba85d627c5a81…` (matches
the convening prompt). No background tasks, no subagents, no git writes; nothing under `/Users/edr/night-custody` was
written, moved or deleted. Everything in §Executed probes was run in this session; anything not listed there is NOT EXECUTED.

## Contamination disclosure

Before I opened the packet, the session harness had injected into my context: the global `~/.claude/CLAUDE.md` (writing
standard and multi-model orchestration notes), this worktree's project `CLAUDE.md` (Codex bridge notes), the auto-memory
index `MEMORY.md` (one-line pointers only, including a "Checkpoint 2026-09-10" line that names T38g, PR #313, D-180 and
"NEXT = short real G2-a window"), and a git-status snapshot listing the five most recent commits (all GATE-SENSIBILITY-SWEEP-01
fix rounds). None of that material mentions the dead-man, item 5, launchd stream files or packet 31. I opened no memory file
body, no RUN_STATE.md, no TASK_QUEUE.md, nothing under `.claude/`, and no process trace outside the packet directory and the
lineage files named in the convening prompt. The only touch on `docs/decision_log.md` was a `grep -n 'D-175'` that returned
the index row and the section heading; I did not read the eight conditions because this ruling does not turn on them.

## Terms used below

- **Dead-man**: the launchd job `com.joulewise.night.deadman`, which runs `run_night.py dead-man` daily at 07:00 and exists
  to send a courier email if the night finished without one. Before the night's completion epoch it must do nothing but log.
- **Driver**: the Python process `scripts/run_night.py` that launchd starts. "Driver records" are the files the driver
  itself writes into `night/`: the write-once list `receipt.json, go_receipt.json, go-census.json, result.json, refusal.json,
  chain.started, chain.exited, courier.json` (`run_night.py:66–75`) plus `courier.sent` and `censuses.jsonl`.
- **Stream files / launchd handles**: the two files launchd itself opens as the child process's standard output and standard
  error, at the `StandardOutPath` / `StandardErrorPath` given in the plist. launchd creates them when it spawns the job,
  before the driver's first instruction runs; they receive bytes only if the driver prints or crashes with a traceback.
- **Completion epoch**: `t0 + window_max_s + COURIER_DEADLINE_S` = 1789120560 + 900 + 300 = 1789121760 (`_completion_epoch_s`).

## Q1 — Ruling: (c) MET, with a registered follow-up that makes the criterion mechanical

**Item 5 is MET by the 2026-09-10 07:00 observation.** Reasoning, sized to what the criterion guards:

1. **What the criterion guards.** The kernel text (the authority; ruling 61/65/67 are its glosses) reads: the pre-night
   07:00 dead-man firing "is observed standing down without writing anything but a log line (coldgate-d1 R-7 amendment)".
   The hazard R-7 fenced is a dead-man that fires the morning before t0, mistakes the situation for "night over, no courier",
   and writes `refusal.json`, `courier.json` or `courier.sent` into `night/`. Any of those would poison the night: the
   driver's run path refuses on an existing write-once record by name (`_existing_record`, `run_night.py:962`, called at
   1068 and 1430) and the installer refuses on the same names (`install_night_agent.sh:181–189`). Ruling 61's own item-5
   paragraph spells out exactly this meaning in its parenthetical: "`night/` containing nothing from that firing (no
   `refusal.json`, no `courier.sent`, no `courier.json` before t0)". Synthesis 65 and runbook 67 compressed that
   parenthetical to "`night/` holds nothing from that dead-man firing"; the compression, not the criterion, is what the
   observation collides with.

2. **What the driver did.** `dead_man` (`run_night.py:1727–1747`) loaded the plan, called `night_dir.mkdir(exist_ok=True)`
   on an already-existing directory (no filesystem change), found no `courier.sent`, compared `time.time()` (≈1789048802)
   with the completion epoch 1789121760, and took the stand-down branch, whose only side effect is `_append_log`, which
   writes one line to `custody_root/night.log` (`run_night.py:142–145`), not into `night/`. It returned before any code that
   writes a record. The observed `night.log` line is byte-exact to the runbook 67 expectation and carries the correct
   completion epoch. So the driver wrote a log line and nothing else. The kernel criterion is satisfied on its own terms.

3. **What launchd did.** The two zero-byte files `launchd.deadman.out` / `.err` were born at 07:00:01.948, 144 ms before
   the driver's log line at 07:00:02.092, at the paths the installer rendered from the tracked template
   (`configs/launchd/com.joulewise.night.plist.template:32–35`: `@@CUSTODY_ROOT@@/night/@@LOG_STEM@@.out|.err`,
   committed 2026-09-02 at 8c802bde, a week before ruling 61). Their mtime equals their birth instant and they hold zero
   bytes: nothing was ever written through them. They are not driver records, they carry no driver state, no code path in
   `run_night.py` or `joulewise/night_gate.py` lists the directory or reacts to unknown names (probe 9: no `iterdir` /
   `listdir` / `glob` on `night_dir`), and the same design already served as the courier transcript in record 21i line 21.
   They are therefore not "writing" by the dead-man and not the poison the criterion guards against.

4. **Why not (a) alone.** Runbook 67 and checklist 13 say "do not silently exempt a file from this wording". The exemption
   must therefore be recorded, non-silent, and mechanical, which is (c). The literal "holds nothing" gloss is unmeetable by
   construction with the installed plist, and a criterion that a correct system cannot pass is a defect in the gloss, not
   evidence against the system; but the right cure is to record the reading here and register the hygiene fix, not to let
   the harvesting activation reinterpret it alone.

5. **Why not (b).** A third stub night after relocating the stream paths would cost a day and prove nothing the guarded
   hazard needs: the stand-down branch's behaviour is fully observed. Relocating the paths is worthwhile hygiene (it makes
   `night/ == []` literally true and keeps the driver's record namespace pure) but it is not a precondition for item 5, and
   it cannot change the already-installed rehearsal-20260911 agents anyway.

**No rule change is needed.** The kernel acceptance text stands unamended and is satisfied. This ruling is a dated addendum
to the 61→65→67 gloss "and `night/` holds nothing from that dead-man firing", read henceforth as the Q2 predicate. Ed may
veto. Registered follow-up (recommendation, not a gate on the 09-11 harvest or the 09-12 G2-a arm): NIGHT-STREAM-PATHS-01,
change the template so `StandardOutPath` / `StandardErrorPath` render outside `night/` (for example
`@@CUSTODY_ROOT@@/launchd/@@LOG_STEM@@.out`), with a unit test asserting neither rendered path starts with
`<custody_root>/night/` (extend the existing test at `tests/test_run_night.py:1504–1505`), and update the harvest rows that
name `night/launchd.night.out` so the courier transcript keeps being preserved from its new location. Until that lands,
the Q2 predicate is the criterion.

## Q2 — The exact mechanical predicate for the 09-11 harvest, and the sentence to record

Let `R = /Users/edr/night-custody/rehearsal-20260911`, `F = 1789048800` (07:00:00 PDT 09-10), `T0 = 1789120560`
(02:56:00 PDT 09-11). Harvest takes an `lstat` inventory of `R/night/` (name, type, size, birth, mtime_ns) BEFORE any
copy, per checklist 13. Item 5 is MET if and only if P1–P4 all hold; any failure is NOT MET, recorded with the exact
names/sizes/mtime_ns, and escalated (no local cure, no re-reading).

- **P1 (the log line).** `R/night.log` contains exactly one line matching
  `^(\S+) dead-man fired before the night's completion epoch 1789121760; standing down$` whose ISO timestamp lies in
  `[F, F + 60 s]`. Observed today: `2026-09-10T07:00:02.092553-07:00`, which is F + 2.09 s.
- **P2 (ordering).** In `R/night.log`, that line appears before the first line containing `night gate verdict=`, and no
  other line containing `dead-man` lies between them (the dead-man did not fire a second time before t0). If the night
  refuses `night_refused_agent_present`, P2 is evaluated against the refusal's own log line instead of the verdict line,
  and item 5 may still close (item 6 stays open), per refuter 62 and synthesis 65.
- **P3 (pre-t0 entries of `night/`).** Let `S` be the set of `R/night/` entries with `mtime_ns < T0` (baseline at install
  was `[]`, so every pre-t0 entry is attributable to the 07:00 firing). `S` must equal exactly
  `{launchd.deadman.out, launchd.deadman.err}`, each a regular file (not a symlink), size 0 bytes, birth in `[F, F + 60 s]`,
  and mtime_ns equal to the value inventoried today (1789048801.948138143 and 1789048801.948226143). A non-zero size on
  either file means the driver printed or crashed during the firing: NOT MET, and read the bytes as a finding. Any other
  pre-t0 name (in particular `refusal.json`, `courier.json`, `courier.sent`, `result.json`, `receipt.json`) is NOT MET.
- **P4 (post-t0 sanity, not part of item 5's object but needed to attribute).** Every entry of `R/night/` not in `S` has
  `mtime_ns >= T0`. If any entry has a timestamp between `F + 60 s` and `T0`, attribution is ambiguous: report it, do not
  treat it as empty evidence (checklist 13 §2).

Sentence to record under NIGHT-REHEARSAL-01 (harvester fills the bracketed values from the inventory; if P1–P4 fail, record
"Item 5 NOT MET" with the failing predicate and the exact inventory instead):

> Item 5 MET on rehearsal-20260911 (cold gate 31, ruling 10): agents installed 04:10:58 PDT 09-10 with `night/` baseline
> `[]`; the 07:00:02.092 PDT 09-10 dead-man firing wrote only the stand-down line to `night.log` (completion epoch
> 1789121760), which precedes the 09-11 `[night gate verdict= | refusal]` line at `[timestamp]`; the only pre-t0 entries of
> `night/` were launchd's two zero-byte stdio handles `launchd.deadman.out` / `.err` (birth 07:00:01.948, mtime unchanged,
> 0 bytes), installer-rendered `StandardOutPath` / `StandardErrorPath` targets and not driver records; no `refusal.json`,
> `courier.json` or `courier.sent` existed before t0. Read per cold gate 31: "writing anything but a log line" means driver
> records; zero-byte launchd handles at the rendered stream paths are the only permitted `night/` entries from a pre-night
> firing. Follow-up NIGHT-STREAM-PATHS-01 registered (render stream paths outside `night/`, with test).

## Q3 — The night agent's own `launchd.night.out` / `.err` at 02:56 on 09-11

Yes, the same reasoning covers them, and they need no exemption at all. They are launchd handles at installer-rendered
paths (`123-arm-evidence/com.joulewise.night.plist:32–35`), created by the night's OWN firing at t0, so their birth and
mtime are `>= T0` and they never enter the item-5 set `S` (P3/P4 exclude them by time, not by name). Item 5's object is
the pre-night dead-man firing only. Item 6's criterion (receipt not refused, verdict `REHEARSAL_ONLY`, C5 stub digests
null) says nothing about `night/` being empty, and record 21i line 21 already used `launchd.night.out` as the courier
transcript that proves the driver was launchd-started. Two consequences for the harvester: preserve both files byte-exact
with sizes and mtime_ns (checklist 13 §2 row), and read `launchd.night.err`; non-empty stderr from the night's run is
diagnostic content for item 6 (a traceback would be a finding), not an item-5 matter. Unlike the dead-man handles, these
two files are expected to be NON-empty, because the courier's transcript goes to stdout by design.

## Executed probes

All run in the foreground from `/Users/edr/code/JouleWise-wt-coldgate-gate-prose` on 2026-09-10 between 07:05 and 07:12 PDT.

1. `git rev-parse HEAD` → `58d4696bbcd4b95cdc40e06d4163628d5d29c78a`. `git status --short` → only the two untracked packet
   directories (24 and 31). `git ls-files --error-unmatch` on `scripts/run_night.py`, `scripts/install_night_agent.sh`,
   `docs/process/state_kernel.json`, ruling 61, runbook 67, record 21i → `all-tracked`; `git diff --stat HEAD -- scripts
   docs/process` → empty (lineage files are at HEAD, unmodified).
2. `cat 00-PACKET.md exhibit-A-observation-record-30.md | shasum -a 256` →
   `a4dba85d627c5a813dcea226549da22f6c537670440a7cae928606f935769a60` (prefix matches the convening digest).
3. `python3` walk of `docs/process/state_kernel.json` for NIGHT-REHEARSAL-01 → acceptance evidence[4]: "A rehearsal with
   the agents installed the MORNING BEFORE the armed night, so the pre-night 07:00 dead-man firing is observed standing
   down without writing anything but a log line (coldgate-d1 R-7 amendment)"; dependencies[1] (REHEARSAL-20260911-HARVESTED,
   pending): "… the pre-night 07:00 dead-man stand-down observed with nothing written into night/ (item 5) …".
4. `sed -n '115,145p' 61-coldgate-ruling-second-stub-night.md` → item 5 paragraph with the parenthetical "(no
   `refusal.json`, no `courier.sent`, no `courier.json` before t0)". `sed -n '120,135p;150,165p' 62-*.md` → "standing down
   having written nothing but its log line"; agent-present refusal closes item 5 only. `sed -n '18,36p' 65-*.md` → "night/
   holds nothing from that firing". `sed -n '368,408p' 67-arm-runbook-rehearsal-20260911.md` → the verbatim bullet "and
   `night/` holds nothing from that dead-man firing. Record any deviation; do not silently exempt a file from this wording."
5. `sed -n '17,25p' 21i-rehearsal-20260909-harvest-record.md` → line 21: "launchd-started, not shell-started:
   `night-launchd.night.out` is the courier's transcript written by the `com.joulewise.night` agent."
6. `sed -n '1727,1760p' scripts/run_night.py` → `dead_man` as in Exhibit D; `_append_log` (142–145) opens
   `custody_root / "night.log"` in append mode; `_completion_epoch_s` = `t0_epoch_s + window_max_s + COURIER_DEADLINE_S`.
7. `sed -n '155,215p' scripts/install_night_agent.sh` → install refusal loop over the seven named records (181–189);
   `render … "launchd.deadman"` (192). `sed -n '129,158p'` → `render()` substitutes `@@LOG_STEM@@` into the template.
   `grep -n StandardOutPath configs/launchd/com.joulewise.night.plist.template` → lines 32–35:
   `@@CUSTODY_ROOT@@/night/@@LOG_STEM@@.out` / `.err`; `git log -1 -- <template>` → `8c802bde 2026-09-02 02:05:39 -0700`.
8. `sed -n '1495,1508p' tests/test_run_night.py` → the only stream-path assertions are that the night and dead-man
   `StandardOutPath` / `StandardErrorPath` differ (1504–1505); nothing asserts they lie inside or outside `night/`.
9. `grep -n -E 'iterdir|listdir|glob\(|_WRITE_ONCE_RECORDS\s*=|_existing_record\(' scripts/run_night.py` → the only
   `night_dir` checks are `_existing_record` by name (962, called at 1068, 1430); `rglob`/`glob` hits are on
   `namespace`, `pack_custody`, `control` paths, not `night_dir`. `grep -n -E 'iterdir|listdir|night_dir|launchd\.'
   joulewise/night_gate.py` → no output.
10. Custody, read-only: `ls -la R` → `night/` (dir, 07:00), `night.log` (110 B), `night_plan.json` (761 B, 04:10).
    `ls -la R/night` → exactly `launchd.deadman.err` (0 B) and `launchd.deadman.out` (0 B).
    `stat -f '%N size=%z mtime_ns=%Fm birth=%B'` →
    `night.log size=110 mtime_ns=1789048802.092639143 birth=1789048802`;
    `launchd.deadman.out size=0 mtime_ns=1789048801.948138143 birth=1789048801`;
    `launchd.deadman.err size=0 mtime_ns=1789048801.948226143 birth=1789048801`.
    `cat R/night.log` → `2026-09-10T07:00:02.092553-07:00 dead-man fired before the night's completion epoch 1789121760;
    standing down`. `wc -c` on both handles → 0, 0.
    `launchctl list | grep -i joulewise` → `com.joulewise.night 0`, `com.joulewise.magistrate 0`,
    `com.joulewise.night.deadman 0` (all loaded).
    `python3` read of `R/night_plan.json` → `plan_id rehearsal-20260911`, `custody_root R`, `t0_epoch_s 1789120560.0`,
    `window_max_s 900`, `receipt_class REHEARSAL_STUB`. Arithmetic check: 1789120560 + 900 + 300 = 1789121760, equal to the
    logged completion epoch; 1789120560 − 1789048800 = 71760 s = 19 h 56 min, so t0 is 02:56 PDT 09-11 as planned.
    `date +%s; date` → `1789049159`, `Thu Sep 10 07:05:59 PDT 2026`.
11. `grep -n -A1 -E 'StandardOutPath|StandardErrorPath|Hour|Minute' 123-arm-evidence/com.joulewise.night.plist` → Hour 2,
    Minute 56, `…/rehearsal-20260911/night/launchd.night.out` / `.err`. `grep -n baseline 123-rehearsal-20260911-arm-record.md`
    → line 55: "`post-install night/ baseline: []` (empty directory, inventory taken 04:10:58)".

NOT EXECUTED: any launchd firing, any installer run, any unit test, any read of D-175's eight conditions, any read of the
decision log beyond the one grep, any write outside this ruling file.
