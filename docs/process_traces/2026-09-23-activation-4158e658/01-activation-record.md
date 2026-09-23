# Activation 4158e658 — handback for the v3 pilot, lanes registered, v3 pilot staged and arm-gated; exit for a fresh supervisor (2026-09-23 04:24 → ~05:35 PDT)

Headless magistrate activation `4158e658-9697-41bb-98e6-f6d92d038308` on Opus 5.5, spawned by the watchdog at
04:24:18 PDT (attempt 86) after activation 7a0f14bd's clean exit at 04:15. Launch email Gmail `1a0ce0301bb047c1`;
`notice.ack` written. Pending notices at launch: none. Ed's NO: none observed (Gmail, last day, no inbound NO/stop;
no `standdown.request`, no `STOP`). Machine: census-clean (only this session's `claude -p` and its MCP helpers);
`top` shows no process above 6 % of a core; no `com.joulewise.night*` label loaded and no night plist on disk.

## 1. Landed

**PR #389 → main `26fb4280b1e2b3ab5b239884a2c1abbd5f9e1f15` (H of the next night).**

- `docs/process/NIGHT_HANDBACK.md` §Purpose / §Where the results are / §Next lane (head) rewritten per R-9 for the
  v3 pilot re-run `qpe01-pilot-n1-20260923-0700`. Writer: an Opus 5.5 subagent (dictated-fills; every number
  checked against its primary record). A non-author Opus 5.5 lens checked facts and pedagogy (record 02):
  MERGEABLE AFTER FIXES, 0 blockers, 6 material, 9 nits. Fix round 1 applied everything (record 03). The cold Fable
  5.1 final pass on the exact head `2ddf85ae` (record 04) returned **APPROVE, no cures**.
- Kernel: THROUGHPUT-01 (A272), BLOCK-TWO-DESIGN-01 (A273), PROMPT-AUDIT-01 (A274), CENSUS-MULTILINE-ARGV-01 (A275).
  QPE01-ABORT-SUCCESSOR-01 (A270) moved to ready. This is registration only; no process rule is ratified.
  Seat: Sol 6.0 high via `codex-run-v3`, done in ~2 min. It early-returned on an out-of-scope test inventory, which
  the magistrate fixed at the bench.
- Pins check: `git diff --stat 3a411784..26fb4280 -- joulewise scripts configs` prints nothing. The code that runs
  is byte-identical to the v3 merge the reviews covered.
- Tests: 10 modules touching the handback or kernel, `Ran 785 tests … OK (skipped=73)` on a77fb8fa.
  `test_gen_state` and `test_docs_freshness` OK on 2ddf85ae. Hosted gate-ledger, quick, fences, build and
  installed-wheel all green before the merge.
- Directive #386 was commented with the outcome and closed (go recorded as BLOCK-TWO-DESIGN-01; lanes registered).

## 2. The v3 pilot re-run: staged and arm-gated, not armed

Canonical checkout fast-forwarded by hand, `3d668e98` → `26fb4280`. Before the move, no night label was loaded and
no night plist was on disk (D-183). That move makes this activation's resident supervisor (pid 2913, started 04:24)
older than H's arrival. `joulewise/evidence_night.py:supervisor_check` therefore refuses this session: *"this
session cannot arm — commit, push and exit so the watchdog's successor arms (D-183)"*. The arm is handed to the
successor.

`python3 -B -m joulewise.evidence_night prepare --kind quiet_predicate_evidence --t0 1790172000 --head 26fb4280…`
returned rc 0 at 05:13:36 PDT.

| Field | Value |
|---|---|
| plan_id | `qpe01-pilot-n1-20260923-0700` (attempt 3 of pilot night one; the tool's notice counter says attempt 1 for this date) |
| repo_head = measurement_head = H | `26fb4280b1e2b3ab5b239884a2c1abbd5f9e1f15` |
| measurement_root | `/Users/edr/JouleWise-measurement-20260923-0700-1790172000-26fb4280b1e2b3ab5b239884a2c1abbd5f9e1f15-qpe01-pilot-n1` |
| custody root | `/Users/edr/night-custody/qpe01-pilot-n1-20260923-0700-20260923-0700-1790172000-26fb4280b1e2b3ab5b239884a2c1abbd5f9e1f15` |
| staging ($STAGE) | `/Users/edr/night-plan-staging/qpe01-pilot-n1-20260923-0700-20260923-0700-1790172000-26fb4280b1e2b3ab5b239884a2c1abbd5f9e1f15` |
| staged file digests | record 09 (`night_plan.json` `6193c6b6…b566`, `prepare.json` `39b9382f…f067`) |
| registration | `pilot_protocol_v3.json` `69321c693b3370b949b0a4a1b8548e35dd081a36165ba8f6799a387c2d813616` |
| t0 | 2026-09-23 07:00:00 PDT = 1790172000; `window_max_s` 9000 |
| install close (excluded) / REQUEST / TERM / KILL | 06:50:00 / 06:52:00 / 06:54:00 / 06:55:00 PDT |
| window end / courier deadline / dead-man | 09:30 / 09:35 / 10:35 PDT |

**Arm gate (THROUGHPUT-01 item 5: arms get the full shape).** Charge: record 05. All three reviewers ran read-only
and in parallel on the staged bytes, 05:13–05:17.

- **Cold Fable 5.1 judge (record 06): ARM.** Bindings, wrapper/chain and schedule all PASS. Every sealed digest was
  re-verified. The clone is clean at H, the chain bytes equal the v3 `chain_source_sha256`, and v2/v1 carry
  `superseded_by`. Retained roots are terminal. NIT-1/NIT-2: the notice's hard-coded "7,800-second program"
  (evidence_night.py:283; the true span is 8,020 s) and its omission of the v3 rules. Fable: "not worth this window:
  lane it".
- **Opus 5.5 contract lens (record 07): ARM.** It reports the same two notice defects as nits.
- **Sol 6.0 execution refuter (record 08): ARM AFTER CURES (dissent).**
  - F1: the notice says busy cores are only descriptive, gives 7,800 s, calls this the first evidence night, and
    claims exactly one `git show`.
  - F2: the pinned campaign writes `summary.md` with "Busy cores are recorded covariates and never an exclusion
    input", which is false under v3.
  - Sol's proposed cure: a new head, clone and plan.

**Magistrate synthesis.** Fable's verdict prevails (topology line, Ed 09-23): ARM. Sol's dissent is recorded here
and becomes lane NOTICE-SUMMARY-V3-TEXT-01 (A276). Both defects are generated prose. No gate, measurement, exclusion
or summary.json field is affected. Curing them needs a claim-bearing code change (`quiet_predicate_campaign.py`),
a new H, a new clone, plan and gate, and so a later window. What stands in for the notice cure is that the
successor appends exactly ONE correction line to the notice email. The precedent is ca45291d's one appended line
(ruling 21 C2). The text is in §3. F2's false `summary.md` sentence must be named in the harvest record.

## 3. SUCCESSOR'S EXACT ARM PROCEDURE (install close 06:50:00 PDT; if it cannot finish by 06:45, do not arm — re-prepare with a new t0)

All commands run from `/Users/edr/code/JouleWise` as `python3 -B -m joulewise.evidence_night …`, with
`STAGE=<staging above>`.

0. Write the heartbeat, send the launch email, write `notice.ack`. Run `env | grep EVIDENCE_POWER_RECORDER`; it
   must print nothing. Confirm with `launchctl list | grep joulewise` that no night label is loaded. Read Gmail and
   the directives for NO, and write any observed mailbox NO to `$STAGE/lifecycle/NO` before `veto`. Confirm canonical HEAD contains `26fb4280`.
1. Do not re-prepare. Verify that the staged bytes still match record 09:
   `cd $STAGE && shasum -a 256 night_plan.json prepare.json render/*.plist`.
2. Terminate only your own `codex mcp-server` helpers. Follow the procedure in NIGHT_HANDBACK §Purpose ("Before
   running `check`…"). Record the PIDs.
3. `check --candidate $STAGE`. It needs rc 0 and `armable: true`. The supervisor check must pass: your supervisor
   started after H arrived at about 05:13 PDT. So must the 0.5-core machine-quiet predicate.
4. `notice --candidate $STAGE`. Send the body of `lifecycle/notice.txt` VERBATIM via Gmail to
   `claude2.glaring610@passmail.net`, no cc, with the tool's Subject. Append exactly this one line at the end:

   ```
   Correction appended by the magistrate (arm gate of activation 4158e658, Sol 6.0 finding F1; the generated text is being fixed in lane NOTICE-SUMMARY-V3-TEXT-01): under registration v3 busy cores are not only descriptive — a process outside the measurement apparatus at or above 0.5 busy cores at the arm check or at t0 refuses the night, one that uses 30 or more core-seconds inside an envelope excludes that envelope, and two such envelopes in a row end the night; the programmed span is 8,020 s (600 s settle + 11 × 620 s slot pitch + 600 s), not 7,800 s; this is attempt 3 of pilot night one, not the first evidence night.
   ```
5. `veto --candidate $STAGE` → `clear: true`.
6. `publish-install --candidate $STAGE --notice-accepted <gmail id>` → `outcome: installed`.
7. `verify --candidate $STAGE` → both labels LOADED, plist sha256 == render sha256 (record 09), calendar
   `Month 9 Day 23 Hour 7 Minute 0` and dead-man `Hour 10 Minute 35`.
8. Write the arm record and the Executed block for this plan id in NIGHT_HANDBACK. Commit and push on a
   bookkeeping branch, never in the canonical root, which must not move after the arm. Stop every child and exit
   before REQUEST at 06:52:00.

After the night: harvest byte-exact to `/Users/edr/night-archive/qpe01-pilot-n1-20260923-0700-harvest-<date>`,
verify `SHA256SUMS`, then run `uninstall --candidate $STAGE` from the clone. The expected registered outcome on a
clean night is the stop cause `observer_floor_above_smallest_holdable_share` (synthesis 35). That is a
pre-registered finding about block two, not a defect. The harvest record must also name F2's false `summary.md`
sentence.

## 4. Not done this activation (next, after the night)

THROUGHPUT-01 item 1(b) A234+A212 together, then 1(c) A271 (window machinery). The headline critical path (item 2:
scored-campaign night kind, MATH importer, AP-5 amendment) runs in parallel. After those come NOTICE-SUMMARY-V3-TEXT-01,
BLOCK-TWO-DESIGN-01 once the pilot result is in, and A270. No agent work on the Mac inside the window, 06:52–09:35.

## 5. Scorecard (same packet, Opus 5.5 vs Fable 5.1)

- PR #389: the Opus lens found 6 material pedagogy/fact defects. The Fable final pass found none left after the
  fix round and confirmed every fix.
- Arm gate: Fable and Opus agree (ARM, notice nits). Sol 6.0 alone found the `summary.md` sentence (F2) and the
  notice's "first evidence night" and "one git show" claims. That is a unique catch by the cross-family seat.

## 10. Cold Fable final pass on this close (head 53ee687c), verbatim

```
**Verdict: APPROVE WITH CURES** (one cure, outside the arm path).

**(1) Facts.** Record 01 and the RUN_STATE block hold against records 02–09, the code and the staging. I recomputed all five digests in the staging directory named in record 01. They match record 09 byte for byte. The plan binds H for both heads, the v3 path and ruled digest, t0 1790172000, window 9000, and the named roots. The boundaries in prepare.json match the table. The tool's attempt counter reads 1 with no prior candidates, as record 01 says. The CLI takes `--candidate` on every post-prepare command, `--notice-accepted` only on publish-install, and notice writes `lifecycle/notice.txt`. The supervisor refusal text quoted in §2 is verbatim from supervisor_check. Verdict lines in records 02, 04, 06, 07, 08 are as summarised. gen_state check rc 0, test_gen_state 44 OK.

One false clause: the kernel status_note for A276 says the 07:00 pilot "is armed". It is staged, not armed. RUN_STATE says NOTHING ARMED.

**(2) Procedure.** §3 steps 0–8 follow the tracked order in NIGHT_HANDBACK §Purpose and the ca45291d record step for step, including helper termination, notice verbatim plus one appended line, and the bookkeeping branch. Nothing missing that check or publish-install refuses on. Notice.txt will be newer than check.json because check precedes notice. Nit: the handback says to relay any mailbox NO into `<staging>/lifecycle/NO` before veto. §3 step 0 reads Gmail but does not name that file.

**(3) Correction line.** True in every clause. Gate constant 0.5 applies at check and t0 with a greater-or-equal test. The campaign excludes at a total of 30 or more core-seconds and aborts at 2 consecutive. The fit rule computes 600 + 11 × 620 + 600 = 8020. Attempt 3 is established in the handback. One caveat, not a falsehood: v3 still carries `busy_cores_role: covariate_only` for the aggregate statistic. The line's per-process qualifier makes it accurate.

**(4) Synthesis.** Sound. Sol's cures need a new head and window. The defects are prose only, and the appended-line precedent is exact. Fable's verdict prevailing follows the existing topology. A276 is registration only. No rule is ratified or amended.

**Cures:**
- In state_kernel.json, A276 status_note: change "is armed with" to "is staged to be armed with", regenerate, and re-run the gen_state check.
- Optional: add "write any mailbox NO to `$STAGE/lifecycle/NO`" to §3 step 0.
```

Both cures applied in the next commit (A276 status note "staged to be armed"; §3 step 0 names `$STAGE/lifecycle/NO`).
