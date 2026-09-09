# 30 — FINAL-HEAD REFUTER (CONTRACT lens, Opus, fresh non-author, read-only): PR #308 @ 191f4c43

**Head reviewed:** `191f4c43b0364b63c72574989a89b37fe3245452` in the detached worktree
`/Users/edr/code/JouleWise-wt-ref-308-astra` (`git rev-parse HEAD` confirmed; working tree clean, no edits made there).
`gh pr view 308` reports `headRefOid` = `191f4c43…`, `state` OPEN, `mergeable` MERGEABLE — so this is the live head.

**Lens:** CONTRACT. Does the committed prose claim more than a committed artifact shows; does the PR ratify, amend or
reinterpret a standing rule (relaunch prompt line 20 / rule 11); is the "nothing is armed" statement true; is any
unmerged-branch behaviour described as present behaviour on main.

**Prior lenses read before starting** (so closed items are not re-litigated): `06-ref-308-opus-contract-review.md`
(B1 CURED, S5 CURED, S1–S4 open at `1f4c4492`) and `21-delta-308-round3-astra-report.md` (F1–F4 raised, S2/S4/N1–N7
dispositioned). I also read `18-brief-kernel-fold-astra.md`, `20-seat-kernel-fold-astra-report.md` and
`24-brief-kernel-fold-part2-astra.md` to establish where the kernel fold actually lives.

---

## Independent execution performed

All commands run read-only in `/Users/edr/code/JouleWise-wt-ref-308-astra` (or as bare `git`/`gh` queries).

1. `git rev-parse HEAD` → `191f4c43b0364b63c72574989a89b37fe3245452`; `git status --porcelain` → empty.
2. `shasum -a 256 -c SHA256SUMS` in `…/21b-rehearsal-20260909-bench/night-harvest`:
   ```
   night-receipt.json: OK
   night-result.json: OK
   night.log: OK
   night_plan.json: OK
   pre-uninstall-observations.txt: OK
   ```
   17/17 OK, 0 failed. `ls -1 | wc -l` → `21` (17 listed + `SHA256SUMS` + `uninstall-output.txt` +
   `removal-output.txt` + `watchdog-events-excerpt.txt`).
3. `night.log` digest re-derivation (python3, hashlib over line prefixes):
   ```
   result-recorded night.log sha : f894b3a4d731e3a794795251fb596b442cb498964ea468c307346f0bee5bae13
   full-file sha                 : 28ee7ad60ea6c45a584398266cf8b8c93cb15eb096da7d0b5d39c619d680e57a
     prefix 2 lines: f894b3a4d731e3a794795251fb596b442cb498964ea468c307346f0bee5bae13  <== MATCH
   SHA256SUMS night.log          : 28ee7ad60ea6c45a584398266cf8b8c93cb15eb096da7d0b5d39c619d680e57a
   receipt recorded vs harvested : 7671d526… 7671d526… True
   night/chain.started        recorded==harvested: True
   night/chain.exited         recorded==harvested: True
   night/censuses.jsonl       recorded==harvested: True
   night/chain.stdout.log     recorded==harvested: True
   night/chain.stderr.log     recorded==harvested: True
   ```
4. Epoch→PDT conversion of every epoch quoted in 21h/21i/00-DURABLE-STATE (python3 zoneinfo `America/Los_Angeles`):
   ```
   1788944349.678694 2026-09-09 01:59:09.678694 PDT  784a764e clean exit seq9
   1788945977.006024 2026-09-09 02:26:17.006024 PDT  b1e2fd2f exit seq17
   1788947760.0      2026-09-09 02:56:00.000000 PDT  t0
   1788947872.637474 2026-09-09 02:57:52.637474 PDT  seq20 HOLD
   1788948173.967854 2026-09-09 03:02:53.967854 PDT  seq21 FENCED
   1788949981.162783 2026-09-09 03:33:01.162783 PDT  628c2eed spawn seq23
   1788950204.064847 2026-09-09 03:36:44.064847 PDT  state last_clock
   1788950218        2026-09-09 03:36:58.000000 PDT  uninstall
   1788950258        2026-09-09 03:37:38.000000 PDT  removal
   uninstall-state delta: 13.935153007507324
   ```
5. `git fetch --no-write-fetch-head origin refs/heads/night-results/20260909:refs/tmp/nr20260909` then
   `git log --oneline -3` / `git merge-base --is-ancestor 83ab38ed refs/tmp/nr20260909`:
   ```
   a84e0f7f record night 20260909
   d4d494ec record night 20260909
   83ab38ed Merge checkpoint T38c into main …
   83ab38ed IS ancestor of a84e0f7f
   ```
6. Code citations re-read at `83ab38ed` (`git show 83ab38ed:<file> | sed -n`):
   ```
   1046	chain_text = probes.read_text(plan.chain_path)
   1047	sidecar_text = probes.read_text(plan.chain_sha256_path)
   1540	    rehearsal_effective = rehearsal or plan.receipt_class == "REHEARSAL_STUB"
   1567	    if rehearsal_effective:
   1570	        command = ["/bin/zsh", "-c", "sleep 2; echo REHEARSAL"]
    414	    def test_a_fully_green_rehearsal_can_never_yield_go(self) -> None:
     61	EXIT_REFUSED = 3
   ```
7. Cure-branch state: `git rev-parse fix/2026-09-09-night-gate-stub-chain` →
   `5db38b5816bce05b67cabfe3eb621bf2b22aa3e6`; `git merge-base --is-ancestor bb7090e2 5db38b58` →
   `bb7090e2 IS ancestor of 5db38b58`; `gh pr view 309` →
   `{"headRefOid":"5db38b58…","mergedAt":null,"number":309,"state":"OPEN"}`.
   `git log -1 --format='%ci'`: `bb7090e2` = 03:44:57, `1b56c9d2` (fix round 2) = 03:52:36, `5db38b58` = 04:00:20,
   `191f4c43` (fix round 4) = 04:15:04 — i.e. the branch had already advanced to `5db38b58` fifteen minutes before the
   final commit was written.
8. Kernel row at this head (`python3 -c "json.load(...)['tasks']['NIGHT-REHEARSAL-01']"`):
   ```
   status: blocked
   status_note: … Remains blocked pending the fresh post-watchdog REHEARSAL_STUB night; rehearsal-20260909 is prepared
   for 2026-09-09 02:56 PDT on activation branch 1ae91b4d, trace 21b. …
   dependencies[0]: {"evidence": null, … "state": "pending", "target": "POST-WATCHDOG-REHEARSAL-20260909"}
   ```
   `grep -c NIGHT-GATE-STUB-CHAIN-01 docs/process/state_kernel.json TASK_QUEUE.md` → `0` and `0`.
   `git rev-parse bookkeeping/2026-09-09-kernel-fold` → `63a2739f…` (the fold exists, on a different branch).
9. Diff scope check: `git diff --name-only 83ab38ed..191f4c43 | grep -Ev '^docs/process_traces/'` →
   `docs/process/NIGHT_HANDBACK.md` only. No `docs/decision_log.md`, no `state_kernel.json`, no skill file.

### Q1 claim sample — 24 factual claims re-derived from bytes

| # | Claim (path:line) | Artifact | Result |
|---|---|---|---|
| 1 | `21i:3` "pid 82637" | `pre-uninstall-observations.txt:48` `"pid": 82637` | match |
| 2 | `21i:3` "watchdog attempt 5" | `pre-uninstall-observations.txt:15` `"attempt": 5` | match |
| 3 | `21i:3` "spawned 03:33:01 PDT" | excerpt:24 epoch `1788949981.162783` → 03:33:01.162783 PDT | match |
| 4 | `21i:3-4` "events.jsonl seq 22–23" | excerpt:23 (seq 22 LAUNCHING), :24 (seq 23 ACTIVE, activation 628c2eed) | match |
| 5 | `21i:9-10` plan v2/`REHEARSAL_STUB`/t0 1788947760/window 900/root/`ae8f074f` | `night_plan.json:6-15` | match |
| 6 | `21i:11-12` six `night.log` events with times | `night.log:1-6` verbatim | match |
| 7 | `21i:14-17` `28ee7ad6…` vs `f894b3a4…`, "FIRST TWO lines", four appends at 02:56:03.367167 / 02:56:10.980604 / 02:57:33.117809 / 02:57:35.070205 | python re-derivation (§3) + `night.log:3-6` | match |
| 8 | `21i:18-20` result fields; `chain.started` pid/pgid 82053; `chain.exited` rc 0; stdout `REHEARSAL`; one clean census (pgrep exit 1, empty stdout) | `night-result.json`, `night-chain.started:3-4`, `night-chain.exited:3`, `night-chain.stdout.log:1`, `night-censuses.jsonl:1` | match |
| 9 | `21i:22-24` branch at `a84e0f7f`, parent `d4d494ec`, both "record night 20260909", on top of main `83ab38ed` | §5 fetch + ancestry | match |
| 10 | `21i:25-26` message/thread `1a08599a4ff4d005`, sent epoch 1788947852, courier pid 82210, attempted 1/heartbeat true/sent true | `night-courier.sent:1-5`, `night-courier.json:2-5` | match |
| 11 | `21i:28-29` seq 20 FENCED→HOLD_CENSUS (1788947872), seq 21 →FENCED (1788948174) | excerpt:20 (`1788947872.637474`), :22 (`1788948173.967854`, rounds to …174) | match |
| 12 | `21i:33-35` receipt verdict/reason/detail, C1+C4 "not evaluated after refusal", C2 `NOT_APPLICABLE`/`no_pack_by_design`, C3 clean-but-FAIL, C5 three heads `ae8f074f` | `night-receipt.json:8-79` | match |
| 13 | `21i:36-40` `night_gate.py:1046-1047`, `run_night.py:1567-1570`, `:1540`, `test_night_gate.py:414` at main `83ab38ed` | §6 | match |
| 14 | `21i:52-53` `last_clock.epoch_s 1788950204.064847` precedes uninstall `1788950218` by "exactly 13.935153 s" | `pre-uninstall-observations.txt:29`, `uninstall-output.txt:1`, arithmetic §4 | match |
| 15 | `21i:58` "last exit status 3 = `EXIT_REFUSED`" | `pre-uninstall-observations.txt:1` `- 3 com.joulewise.night`; `run_night.py:61` | match |
| 16 | `21i:60-62` results-clone == origin, worktree remove rc 0, plan root removed, custody parent = four dirs, "Nothing is armed" | `removal-output.txt:6-20`, `uninstall-output.txt:3-6` | match |
| 17 | `21i:21` "launchd-started … `night-launchd.night.out` is the courier's transcript" | `arm-blockB-output.txt:29` (`stdout path = …/night/launchd.night.out`) + the file's courier prose | match |
| 18 | `21i:13` "No 07:00 dead-man line (agents installed 01:57 on 09-09)" | `night.log` has no dead-man line; `pre-uninstall-observations.txt:5-6` plists dated `Sep 9 01:57` | match |
| 19 | `21h:3` "Written 1788944302 2026-09-09 01:58:22 PDT" | `arm-launchctl-and-state.txt:1` identical string | match |
| 20 | `21h:14` frozen triple (`rehearsal-20260909`, `/private/tmp/joulewise-rehearsal-20260909-checkout`, `ae8f074f`) | `arm-launchctl-and-state.txt:19-23` | match |
| 21 | `00-DURABLE-STATE.md:633` b1e2fd2f spawn 1788945764/seq 16/attempt 4; exit `1788945977` (02:26:17, seq 17) | excerpt:14, :16 | match |
| 22 | `00-DURABLE-STATE.md:656-657` pid 82106 in seq-19 census stdout; pid 82210 "recorded in its heartbeat and sent marker" | excerpt:19 argv; `night-courier.heartbeat:1`; `night-courier.sent:5` | match (round-3 F4 cured — no process-type claim survives) |
| 23 | `00-DURABLE-STATE.md:610` foreign-agent gate `[]`, informational `[]`, own MCP pair 83123/83143 | `arm-blockB-output.txt:3-7` | match |
| 24 | `NIGHT_HANDBACK.md:83` "the cure is committed on branch `fix/2026-09-09-night-gate-stub-chain` at `bb7090e2`" | branch head is `5db38b58` (§7) | **MISMATCH** |

23 of 24 match the bytes. The single mismatch is S-A below.

---

## Blockers

None. Nothing in this diff arms anything, moves a pinned root, touches watchdog-owned state, or asserts a physical or
claim-bearing result. Every artifact the record cites is committed and hashes 17/17.

---

## Should-fix

### S-A — `NIGHT_HANDBACK.md` names a superseded cure head; the two documents in this PR disagree about the same fact

(a) Quote — `docs/process/NIGHT_HANDBACK.md:83`:
> "the cure is committed on branch `fix/2026-09-09-night-gate-stub-chain` at `bb7090e2` under review, not yet merged"

against `docs/process_traces/2026-09-02-hands-free-week/21i-rehearsal-20260909-harvest-record.md:84`:
> "Once NIGHT-GATE-STUB-CHAIN-01 lands (branch `fix/2026-09-09-night-gate-stub-chain`, fix head `5db38b58`, PR #309)"

Executed evidence: `git rev-parse fix/2026-09-09-night-gate-stub-chain` = `5db38b58`; `gh pr view 309` `headRefOid` =
`5db38b58`; `bb7090e2` is its ancestor, committed 03:44:57, superseded by the fix-round-1 commit at 04:00:20 — fifteen
minutes *before* this PR's final commit `191f4c43` (04:15:04). Round 4 updated 21i to `5db38b58` and left
`NIGHT_HANDBACK` at `bb7090e2`.

(b) Governing text — `NIGHT_HANDBACK.md:16-17`: "If this file and the result record disagree, the result record is right
and the courier says so." The file is written for a reader who cannot check; naming a superseded commit sends a reviewer
of "the cure under review" to code that has since been changed by an Opus-review fix round. This is also the exact shape
of round-3's S3 (two PR documents, two values for one fact).

(c) Correction: change `NIGHT_HANDBACK.md:83` to `… at `5db38b58` (PR #309) under review, not yet merged`, or drop the
sha and name PR #309 alone so the sentence cannot go stale again.

### S-B — `NIGHT_HANDBACK.md` declares the §Next lane harvest DONE, but §Next lane's harvest includes recording under `NIGHT-REHEARSAL-01`, and the kernel row is untouched at this head

(a) Quote — `docs/process/NIGHT_HANDBACK.md:84-85`:
> "The §Next lane harvest, `--uninstall` from the stub checkout, and removal of the stub checkout and plan root are DONE
> (record 21i)"

(b) Governing text — the same file's `:106-108` defines what that harvest is:
> "harvests `result.json`, the receipt or refusal, the courier message id and the results-branch evidence, **records them
> under `NIGHT-REHEARSAL-01`**, then runs `scripts/install_night_agent.sh … --uninstall`"

At `191f4c43` the machine-readable `NIGHT-REHEARSAL-01` row still reads `status_note` "rehearsal-20260909 **is prepared
for** 2026-09-09 02:56 PDT on activation branch 1ae91b4d" with `dependencies[0]` (`POST-WATCHDOG-REHEARSAL-20260909`)
`state: "pending"`, `evidence: null`, and `NIGHT-GATE-STUB-CHAIN-01` appears 0 times in `state_kernel.json` and 0 times
in `TASK_QUEUE.md`. The fold exists but on `bookkeeping/2026-09-09-kernel-fold` (`63a2739f`), outside this PR. This is
06's S1 surviving to the final head, now compounded because the standing file asserts the step complete. The operational
hazard is concrete: a future headless activation resuming from `RUN_STATE`/kernel per relaunch-prompt line 3 reads that
the night "is prepared" and looks for a plan root that `removal-output.txt:13` shows was deleted at 03:37:38.

(c) Correction: land the kernel fold in the same merge wave as PR #308, or qualify `:84` — e.g. "the §Next lane harvest,
uninstall and removal are DONE (record 21i); the `NIGHT-REHEARSAL-01` kernel record lands with the fold on
`bookkeeping/2026-09-09-kernel-fold`."

### S-C — one sentence in the standing file rewrites the file's own between-nights invariant, and the three night sections were left holding a night that is over

(a) Quote — `docs/process/NIGHT_HANDBACK.md:86-87`:
> "The standing rules below are unchanged; the next plan's author rewrites §Purpose, §Where the results are and §Next
> lane for that plan under the same procedure."

(b) Governing text — the same file's `:4-8`:
> "**The magistrate** rewrites the three sections below before every armed night (ruling R-9 …) and commits the rewrite
> with the night's plan. **Between nights the sections hold the standing template text, so a courier that reads this file
> on a night nobody armed reports exactly that.**"

and relaunch prompt `docs/process/MAGISTRATE_RELAUNCH_PROMPT.md:20`: "Do not ratify or amend any process rule,
decision-log entry, or skill doctrine; under rule 11 those decisions go to the cold gate or Ed."

Two departures. (i) The new sentence reassigns R-9's bound actor from "the magistrate" to "the next plan's author" — a
broader class, in a standing file, decided by a headless activation. (ii) More substantively it defers the reset: R-9's
invariant is that *between* nights the three sections hold template text, and this head is between nights (nothing
armed). At `191f4c43` those sections instead still read `:51-56` "Plan `rehearsal-20260909` … **is** the fresh
post-watchdog rehearsal", `:67-68` "**Expected**: `result.json` verdict `REHEARSAL_ONLY` … courier deadline … 03:16
PDT", `:91-96` "Custody root: `/Users/edr/night-custody/rehearsal-20260909/night/` … Driver log:
`/Users/edr/night-custody/rehearsal-20260909/night.log`" — a root `removal-output.txt:13` shows removed — and `:104-114`
still instructs the relaunched magistrate to perform a harvest and uninstall that `21i` records as complete. The
reconciliation section mitigates this for a reader who reads top-to-bottom, and review 06 accepted the reconciliation
shape as the cure for its S5; what is new at this head is that the PR now *states a rule* about when the reset happens
instead of doing it.

(c) Correction: delete the clause after the semicolon at `:86` (keeping "The standing rules below are unchanged"), and
either reset §Purpose / §Where the results are / §Next lane to template text now as `:6-8` requires, or refer the
"when does the reset happen after a completed night" question to the cold gate as `21i:47-49` does for D-175 cond. 8.

---

## Nits

- **N-a** `NIGHT_HANDBACK.md:84`: "The §Next lane harvest, `--uninstall` from the stub checkout, and removal … are DONE"
  presents the three steps in §Next lane order, i.e. as executed in that sequence, while `21i:49-50` says "the copies'
  order relative to the uninstall is INFERRED — no transcript of the copy command was captured." Governing:
  `21i:5` "nothing is restated from memory." Correction: write "are DONE (record 21i; harvest-before-uninstall ordering
  inferred, see 21i)".
- **N-b** `21i:56` juxtaposes "17 entries after" with "the byte harvest had copied 14 records + `night.log`". I counted
  the `night-*` entries in `SHA256SUMS`: exactly 14, plus `night.log`, plus `night_plan.json` = 16 custody-root files.
  A reader doing the arithmetic gets 15 or 16, not 17, and `uninstall-output.txt:7-8` records no command, so what the
  `17` enumerates is unknowable. Correction: name the command, or say "17 entries by a count whose command was not
  captured (06 N2); the harvest copied 14 `night/` records plus `night.log` and `night_plan.json`."
- **N-c** `21i:78` still states the cure shape as "record `chain_sha256: null` with basis `stub_by_design` in C5"; the
  landed cure `bb7090e2` records `chain_sha256` null **plus `chain_stub: built_in_stub_by_design`**. That sentence was
  forward-looking when written, but round 4 updated the same document to cite the post-fix head `5db38b58`, so the
  stale formulation now sits beside a post-cure citation. Correction: one clause naming the landed field names.
- **N-d** `NIGHT_HANDBACK.md:83` does not name PR #309 while `21i:84` does; naming the PR makes the sentence
  self-updating for a reader. (Folds into S-A's correction.)

---

## Answers to the briefed questions

1. **Over-claiming.** 23 of 24 sampled claims re-derive exactly from the committed bytes, including every one of the
   round-1-to-3 defect classes (ordering — now marked INFERRED at `21i:49-53`; digests — `f894b3a4…` is provably the
   first-two-line prefix, four appends listed with the right timestamps; pids — 82053/82210/82637/82106 all match their
   artifacts; process types — the "shell pid" claim is gone, replaced by "the pid recorded in its heartbeat and sent
   marker"). The one mismatch is S-A.
2. **Ratification / amendment.** The diff touches exactly one file outside `docs/process_traces/`
   (`docs/process/NIGHT_HANDBACK.md`); no `decision_log.md`, no `state_kernel.json`, no skill. Every reserved question is
   routed correctly: `21i:47-49` refers D-175 cond. 8's scope to the cold gate, `21i:72-74` refers the second-stub-night
   question, `21i:88-89` refers whether the record note belongs in a standing document,
   `00-DURABLE-STATE.md:651-652` refers the plan-aware launch fence "to the cold gate or Ed, not to this activation".
   The single sentence that reads as a rule rather than a record is S-C.
3. **Nothing armed / uninstalled / removed / finding classification.** All correct.
   `uninstall-output.txt:3-6` shows `launchctl` after = only `com.joulewise.magistrate` and the only remaining plist =
   `com.joulewise.magistrate.plist`, so both `com.joulewise.night` and `com.joulewise.night.deadman` are gone;
   `removal-output.txt:10-13` shows `worktree removed rc=0`, the checkout path absent, `plan root removed rc=0`, and the
   custody parent reduced to `active-campaigns`, `magistrate`, `magistrate-bench`, `retired-v1`;
   `pre-uninstall-observations.txt:20-26` shows `fenced_checkouts` = `__canonical_repo__` only.
   `night-receipt.json:76` `night_probe_error` ≠ `night_refused_agent_present`, and `21i:32` heads the section "The
   finding (NOT the acceptable stub refusal)" — matching `NIGHT_HANDBACK.md:112-114`. The dated reconciliation does say
   the cure is "committed on branch … under review, not yet merged" — correct in substance, wrong in sha (S-A).
4. **Unmerged behaviour described as present.** No. `21i:83-89` is explicitly conditional ("**Once**
   NIGHT-GATE-STUB-CHAIN-01 lands …") and closes with "on main at `83ab38ed` the gate still reads the chain
   unconditionally", which I verified at `night_gate.py:1046-1047` by `git show 83ab38ed:`. `NIGHT_HANDBACK.md:83` says
   "not yet merged". Round-3 delta F3 is cured.
5. **Same-signature statement.** Same signature: **one surviving instance.** The class is *a single fact carried at two
   values in two documents of the same PR* — round 3's S3 (courier pid 82106 vs 82210), now recurring as the cure head
   (`bb7090e2` in `NIGHT_HANDBACK.md:83` vs `5db38b58` in `21i:84`), and it recurred because a fix round updated one
   document and not the other. The related class of *bench prose over-stating an artifact* (ordering, digests, pids,
   process types) is extinguished at this head — I could not produce a single new instance in 24 re-derivations. The
   structural cure for the surviving class is to stop restating volatile identifiers (shas, pids) in a second document
   and instead point at the one home (the PR number, the harvest record).

**Verdict: findings** — no blockers; S-A (stale cure sha in the standing file), S-B (`NIGHT_HANDBACK` calls the §Next
lane harvest DONE while the `NIGHT-REHEARSAL-01` kernel row it names still says the night "is prepared"), and S-C (one
sentence reassigning R-9's actor and deferring the between-nights template reset) are document edits that should land
before or with the merge; the arm, the harvest, the uninstall, the removal and the finding's classification are all
compliant on the committed evidence.
