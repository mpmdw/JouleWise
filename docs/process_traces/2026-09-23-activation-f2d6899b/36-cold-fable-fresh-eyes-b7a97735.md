# Cold final pass (Fable 5.1), gate-ledger row 10 — candidate b7a97735 (bookkeeping cures on c7edbfdd, branch docs/2026-09-23-f2d6899b)

Worktree `/Users/edr/code/wt-f2d6899b-finalpass3`, detached at `b7a977356cb9d8aaa7f4d7b7b6b9848486be7484`, clean before and after. One non-interactive foreground session, no subagents, no background tasks, nothing committed. Wall ≈ 12 min.

## 0. Contamination disclosure

Loaded by the harness before I acted: the global `/Users/edr/.claude/CLAUDE.md`, the project `CLAUDE.md` at b7a97735, and the auto-memory index `MEMORY.md`. The index's first line names activation f2d6899b, "#393 (A234 early release) + #394 (A271 corecaptured) merged; A277 zero-capture evidence writer next". I opened no memory file body, no council log, no skill. I read, per the charge: `git diff c7edbfdd..b7a97735`, `/tmp/f2d6899b/finalpass-verdict-c7edbfdd.md`, record 32 §4, records 34 and 35, record 33 head, record 32 lines 8–20, record 28 lines 155–165; code on `origin/main` (`c741678b`): `scripts/magistrate_watchdog.py` (census/driver argv, `_zero_capture_disk_facts`, release key, latch), `joulewise/arm_retry.py` (C5 / `zero_capture_evidence`), `joulewise/night_gate.py` (`AGENT_CENSUS_ARGV`, C5 rows, `_QUIET_RECEIPT_KEYS`), `joulewise/evidence_night.py` (supervisor_check, licensing guard at 665d3bd7), `docs/contracts/pack_night_go_receipt.md` (C5 definition), `docs/process/NIGHT_HANDBACK.md` 264–271, `docs/decision_log.md` D-182/D-183 rows; `gh pr view 393/394`, `gh run list --branch main`.

## 1. Diff scope

`git diff --stat c7edbfdd..b7a97735`: 6 files, +163/−16. `RUN_STATE.md` (one line, the f2d6899b block rewritten), `TASK_QUEUE.md` (generated rows), `docs/process/state_kernel.json` (A276 acceptance + status_note, A277 goal, A278 goal, A279 authority label + status_note), `tests/test_gen_state.py` (one comment), new records 34 and 35. No code, contract, skill, decision log or orchestration doc.

## 2. Check (1): arm-notice duty vs record 32 §4

Record 32 §4 ruling text: "Until v4 lands, the next arm notice names the new refusal in plain words ('the night is refused at its start if launchd spawned the Wi-Fi log-capture helper corecaptured more than twice in the previous ten minutes')". At b7a97735:

- A276 status_note: "Until registration v4 (A278) lands, every arm notice carries that sentence; the magistrate appends it by hand until A276's generated notice includes it." Sentence byte-identical to record 32. MATCH.
- A276 acceptance summary now ends: "The rendered arm notice contains, verbatim: …" with the same sentence. MATCH (and this is the right home: A276 is the notice-text lane).
- RUN_STATE: "THE NEXT ARM NOTICE MUST APPEND (record 32 §4: until registration v4, lane A278, lands; by hand until A276's generated notice carries it)". MATCH.

The c7edbfdd wording ("Until A276 lands") is gone from all three places. PASS.

## 3. Check (2): both c7edbfdd cures applied

- **C1 (mandatory)**: `tests/test_gen_state.py` comment now reads "merge c741678b" (diff hunk; `gh pr view 394` mergeCommit `c741678b47e8…`). APPLIED, exact text as the cure specified.
- **C2 (should-fix)**: RUN_STATE action (3) now reads "The finding is N-3 of the Opus counter-review of A271 at 665d3bd7 (record 34), not record 13's N3." The cure allowed "If the lead can name the real source of the Wi-Fi-on question, cite that instead." Record 34 N-3 is exactly that question ("A post-toggle threshold of >= 1 assumes that turning Wi-Fi on never spawns corecaptured … Log the first live toggle"). Record 34 N-4 keeps record 13 N3 as the arm-to-t0 latent risk, so the two are now distinguished. APPLIED via the permitted alternative.

Record 35 is byte-identical to `/tmp/f2d6899b/finalpass-verdict-c7edbfdd.md` (`diff` empty). PASS.

## 4. Check (3): new or changed facts against primary evidence

| New/changed claim | Evidence | Result |
|---|---|---|
| PR #393 MERGED → ea4995d5; PR #394 MERGED → c741678b | `gh pr view`: MERGED, 20:09:04Z / 21:20:36Z; c741678b = origin/main | TRUE |
| Session "10:15 → ~14:50 PDT"; records 01-35 | c7edbfdd 14:21:09, b7a97735 14:27:48 PDT; 35 numbered records on disk | TRUE (≈) |
| Census = "a `pgrep` scan for codex/claude/t3 processes" | `night_gate.py:164` `AGENT_CENSUS_ARGV = ("/usr/bin/pgrep","-lf","[c]odex|[c]laude|[t]3")` | TRUE |
| Driver probe = "a separate `pgrep` for `run_night.py`" | `magistrate_watchdog.py:72` `DRIVER_PROBE_ARGV = ("/usr/bin/pgrep","-lf","[r]un_night\\.py")` | TRUE |
| Tick = one every 300 s | watchdog comment line 87 "launchd's 300 s StartInterval" | TRUE |
| Zero capture on disk: no `chain.started`; no `*.consumed.json` (reservation marker); no capture under `RUNS_ROOT/instrument_validation` or `night/evidence`; empty or absent `night/evidence_envelopes.jsonl`; symlinks count as present | `_zero_capture_disk_facts` 851–870, `_reservation_absent` 831, `_calibration_capture_absent` 836, `_evidence_capture_absent` 840–848 (lstat, size 0), `exists()`/`is_symlink()` at 279 | TRUE |
| Release recorded in `state.json`, keyed to sha256 of `result.json`, never reversed for that result | `_release_key` 893–898 (`plan_id:custody_root:sha256`), `released_zero_capture_refusals` 1610–1626 with the one-way comment; keys pruned only when the plan is no longer loaded | TRUE |
| Both `pgrep`s empty on the same tick | 1619–1625: one census + one driver probe per pass, release iff both empty | TRUE |
| "that loop makes the file-system event daemon `fseventsd` burn a core" | NIGHT_HANDBACK.md 267–269; `evidence_night_entry.md:286` | TRUE |
| A271 t0 / arm-check numbers (2 spawns, 10 min, 180 s, 1+ spawn, `sudo -n`, real arm + nothing loaded + every earlier check) | verified at c7edbfdd by record 35; unchanged in meaning, only reworded | TRUE |
| "D-182's rule allows one replacement night after a refusal that captured nothing" | `docs/decision_log.md:228` D-182 row | TRUE |
| "Post-merge CI on `c741678b` was still running at registration; the successor confirms it" | `gh run list`: c741678b `in_progress` (created 21:20:40Z), still in progress now | TRUE |
| A279 authority "PR #393 body, gate-ledger row 9" | PR #393 body row 9 = lead full-suite replay, 6,940 tests | TRUE |
| A279 status_note "QUEUED as a watch item" | kernel `status: queued` | TRUE (now consistent) |
| Supervisor staleness: "the running supervisor still holds pre-merge code, and D-183's check refuses to arm under it" | `evidence_night.py:665–706` `supervisor_check` refuses "stale resident supervisor pid … started …, H arrived …"; header comment 28–30 attributes the freshness rule to activation records 19/21 and D-183 to `check` doing the fast-forward itself | TRUE in effect; attribution loose (nit N1) |
| **A277 goal gloss: `zero_capture_evidence` is "a field in the refusal receipt's C5 row, the night gate's record that no measurement started"** | `docs/contracts/pack_night_go_receipt.md:43,224`: "C5 the no-retry bound"; `night_gate.py:1206–1224` C5.measured = t0/window/observed epoch, authored epoch, chain provenance. C5 is the no-retry-bound row; `zero_capture_evidence` is a harvested block placed under it (`arm_retry.py:205–206, 250–251, 267–270`). Nothing at the gate records "no measurement started" in C5. | **FALSE (cure C1 below)** |

**Record 34 (condensed Opus counter-review) internal consistency**, judged against records 25/32/33 and the tree at 665d3bd7:
- "123 passed with 163 subtests (test_corecaptured_loop, test_night_gate, test_arm_retry)" = record 32 line 15 baseline at 665d3bd7. CONSISTENT.
- "two-dot and three-dot diffs against ea4995d5 have the same sha": executed `git diff ea4995d5..665d3bd7 | shasum -a 256` and `...` form: identical (`ae36e231…`). The recorded prefix `cbed1ce0…` differs from mine, which is expected across git versions/paths; the claim that the two forms agree is TRUE here as well. CONSISTENT.
- "B1 closed … evidence_night.py:1096": at 665d3bd7 line 1096 is `if nothing_loaded and all(row["verdict"] == "pass" …)`. TRUE.
- "S3 closed as a recorded deviation (record 28:161)": record 28 line 161 is the "S3, busy-core re-sample | DONE as documented deviation" row. TRUE.
- "S-1 … LifecycleTests.kw uses `launchctl_bin="/fixture/launchctl"` … asserts one off and one on": `tests/test_evidence_night.py` 823, 896, 908–909 at 665d3bd7. TRUE.
- "S-1/S-2/S-3/N-1 cured in 7e29eb0d": 7e29eb0d's message names S-1, S-3, S-2, N-1. TRUE; record 33 verifies the cures.
- "night_quiet_admission.md:261" stale: file is `docs/contracts/night_quiet_admission.md`; line 261 carries the legacy not-quiet definition. CONSISTENT (path basename only).
- "`_QUIET_RECEIPT_KEYS`" exists (`night_gate.py:283`). CONSISTENT.
- N-3 / N-4 split matches record 35 C2 and record 13 N3. CONSISTENT.
No contradiction with records 25, 32 or 33 found.

NOT EXECUTED: Gmail id `1a0cf447f67567e5`; the Opus counter-review source text (not available); re-review of record 34's "owner's single bench cure (0 spawns in 4 min)" claim.

## 5. Check (4): mechanical gates

```
/Users/edr/code/JouleWise/.venv/bin/python scripts/gen_state.py --check   → rc=0
PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m pytest -q -p no:cacheprovider tests/test_gen_state.py tests/test_docs_freshness.py
  → 75 passed, 404 subtests passed in 2.08s
```
PASS.

## 6. Check (5): no rule ratified or amended

Files touched are RUN_STATE, the generated queue, the kernel, one test comment, two records. Grep of added lines in RUN_STATE/kernel/test for ratif/amend/addendum/decision-log/supersed: no hit. The A276 acceptance change adds a rendered-text requirement that carries record 32 §4's cold ruling into the lane that implements it; that is registration of an existing ruling, not a new rule. The A276 authority label still says "registration by the magistrate, not a ruling". PASS.

## 7. Cures

**C1 (mandatory).** In `docs/process/state_kernel.json`, task `ZERO-CAPTURE-EVIDENCE-WRITER-01`, `goal`, replace

```
nothing writes the harvested zero_capture_evidence block (a field in the refusal receipt's C5 row, the night gate's record that no measurement started), so
```

with

```
nothing writes the harvested zero_capture_evidence block (a field the harvest is meant to add under the refusal receipt's C5 row, the no-retry-bound row of docs/contracts/pack_night_go_receipt.md; the block is what would prove no measurement started), so
```

Then regenerate `TASK_QUEUE.md` with `scripts/gen_state.py`, and re-run `scripts/gen_state.py --check` (expect rc 0) and the two test modules (expect 75 passed).

**Nits (not blocking).**
- N1. RUN_STATE header: "D-183's check refuses to arm under it" — the refusal is the supervisor-freshness row of `check` (records 19/21, `supervisor_check`); D-183 is what makes `check` perform the fast-forward. Optional: "the supervisor-freshness row of `check` (records 19/21) refuses to arm under it; D-183 has `check` do that fast-forward itself".
- N2. A278 goal: nested parentheses "(block two (the next planned block of measurement nights) or …)". Readable; optional reflow.

## VERDICT

**DO NOT MERGE — one cure (C1), then MERGE.** The arm-notice duty now runs until registration v4 (A278) lands in all three places and matches record 32 §4 verbatim; both c7edbfdd cures are applied (the SHA filled; the N-3 source found, filed as record 34 and cited); record 35 is the prior verdict byte-for-byte; record 34 is internally consistent with records 25, 32, 33 and the tree at 665d3bd7; `gen_state.py --check` is rc 0 and the two test modules pass; nothing ratifies or amends a rule. Every new RUN_STATE gloss is true against the watchdog and gate code on `origin/main`, except one: the new A277 goal describes receipt row C5 as "the night gate's record that no measurement started", and the receipt contract defines C5 as the no-retry-bound row. That is a false fact in the goal text of the P1 lane the successor picks up next, introduced by this cure commit, and a bookkeeping PR whose standard is "every fact true" should not ship it. The cure is one phrase plus a regenerate; no other gate row is affected.
