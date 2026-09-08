# Delta 4 review — PR #295, a2be9591..6c4a77d5 (read-only, Opus)

Worktree `/Users/edr/code/JouleWise-wt-magistrate-1ef89702`, head `6c4a77d5` (committer 2026-09-08 02:48:44 -0700).
Nothing edited; no git writes; `~/night-custody` read only. Bench repros ran under `mktemp -d /private/tmp/...`.

## 1. Every changed line: token TRUE? new fact?

Verified by opening the artifact or running the computation. `TZ=America/Los_Angeles date -r <e>`:
1788853915=00:51:55, 1788854136=00:55:36, 1788854247=00:57:27, 1788856408=01:33:28, 1788856918=01:41:58,
1788944160=2026-09-09 01:56:00, 1788948960=2026-09-09 03:16:00. All match the prose.

| line | token | true? | R4 |
|---|---|---|---|
| 21:1 | `events.jsonl seq 3, epoch 1788853915` | TRUE — copied events.jsonl seq 3 `epoch_s 1788853915.398713` | token only |
| 21:6 | `21-activation-1ef89702/process-census-0055.txt` | TRUE — file tracked, is the 00:55 census | token only |
| 21:18 | `00-DURABLE-STATE.md` CHECKPOINT step 1 | TRUE — that file line 503: "Ed said fixed 09-08 ~00:40" | token only |
| 21:19 | `epoch_s 1788854247.5 = 00:57:27` | TRUE — state.json `last_clock.epoch_s 1788854247.49973` | token only |
| 21:32 | `process-census-0055.txt` | TRUE — census is nonempty, holds joulewise-53 + bg-job daemon tree | token only |
| 21:43 | `events.jsonl epoch 1788854136.9` | TRUE — that record is in the copied events.jsonl | inference, not a new fact |
| 21:52 | `lstart in process-census-0055.txt` | TRUE — row `83953 1282 Tue Sep 8 00:46:54 2026 claude` | token; "By 00:52" deleted, good |
| 21:53 | "ACCEPTED (cross-session reply)" | unverifiable — no message id | **R4 violation (nit), N3** |
| 21:55 | "by its own estimate live for some hours more" | unsourced replacement of "at least 02:30" | **R4 violation (nit), N4** |
| 21b:35 | `(recorded in commit dbd49c1d)` | commit date is 2026-09-08 02:03:37 — bounds the RECORDING, not the selection | token; see N5 |
| 21b:42 | `epoch 1788944160` | TRUE = 09-09 01:56:00; t0 1788947760 − 3600 | token only |
| 21b:133 | `(t0 + 1200 s = 1788948960)` | arithmetic TRUE, but certifies a FALSE difference claim | **see N2** |
| 21b:305 | `events.jsonl seq 5, epoch 1788856408` | TRUE only against LIVE custody, not any PR artifact | **see N1** |
| 21b:310 | `epoch 1788856918` | same | **see N1** |

Also re-derived, unchanged but load-bearing: all 14 shas in the 21b timeline table have committer dates exactly
equal to the printed times (4ac5d981 01:05:11, ae8f074f 01:10:44, a8cc6e68 01:20:08, 9a15338e 01:48:16,
a6bff232 01:48:47, dbd49c1d 02:03:37, 82622e70 02:11:53, and the rest). The four Gmail `internalDate` values
convert correctly (1788854108=00:55:08, 1788854721=01:05:21, 1788855059=01:10:59); I could not query Gmail
(connector unauthenticated), so the internalDate values themselves are unverified by me.

## 2. Remaining HH:MM with no R1 token on the line

Trace 21: `~20:15` (21:3) = (i), verbatim heading `00-DURABLE-STATE.md:254`. `00:51 PDT` (21:41) = (i), email
subject. `00:39:32` (21:69) = (ii), `pmset-sleep-tail.txt` last Maintenance Sleep row confirmed. `04:53` (21:70)
= (ii), census row `48645 1 Fri Sep 4 04:53:15 2026`.
21b: 01:05:21/01:10:44/01:10:59 (21b:31) = (iii), all three in the table above; the stated 5 min 23 s and 15 s
gaps are arithmetically correct. 01:05:21 (21b:61) = (iii). 02:00 (21b:81) = (iii) and DEAD — inside the
superseded block, whose first executable line is `exit 1`. 02:31/02:40/02:41/02:45-03:30 (21b:120) and
02:31 (21b:280) = (iii), constants off t0 02:56 (02:31 = t0 − 25 min). 02:56 (21b:138) = (i), email subject.
03:16 (21b:147) = (iii), corroborated by H: `git show ae8f074f:docs/process/NIGHT_HANDBACK.md` line 43
"courier deadline `t0 + 900 + 300` = 03:16 PDT". 01:56/02:15 (21b:163-164) = (iii), enforced with bare epochs at
21b:172 and 21b:248. `~1-2 h after 01:48` (21b:329) = (iii), anchored at 21b:322.
**No category (iv) remains in either file.** E1 is cured on the merits.

## 3. pass3-lead-benches.txt — verified and independently reproduced

First and last lines are both `1788860841 2026-09-08 02:47:21 PDT`, i.e. 83 s before 6c4a77d5's committer date
02:48:44 -0700 — consistent. (The two bookends are the SAME second, so the pair does not actually bracket a
duration; nit N7.) The benches were run at head `a2be9591`, but the guard and census source lines are byte-identical
at 6c4a77d5 (the delta touches only prose lines 35, 42, 133, 305, 310), so the artifact still applies.

Re-ran all three myself under `mktemp -d`, nothing written under `~/night-custody`:
- window guard (21b:172/248 verbatim): 1788945299 PROCEED rc=0; 1788945300 ABORT rc=1; 1788944159 ABORT rc=1;
  1788944160 PROCEED rc=0. Matches pass3 exactly. Half-open bound is correct: 01:56:00 in, 02:15:00 out.
- installer: `scripts/install_night_agent.sh --plan <mktemp>/absent.json --hour 2 --minute 56 --uninstall`
  printed `plan not found: ...`, rc=2 (`install_night_agent.sh:29`). Matches.
- census block (21b:254-267 verbatim, fake lock pid + fake `ps`): reparented `claude daemon run` (ppid 1) ->
  `foreign census matches: [(9001, 'claude daemon run')]` rc=1; own-tree-only -> `[]` rc=0. Matches.
`ls ~/night-custody` after: magistrate, magistrate-bench, retired-v1 — unchanged.

## 4. Same-signature statement

- hand-typed times: **SURVIVES** — 21b:24, 21b:25, 21b:305, 21b:310 (N1).
- hard-coded pids: **SURVIVES** — 21b:173 `ps -p 48645`; fail-closed only (a recycled pid can just abort the arm),
  and the census derives its own pid from the lock at 21b:257. Not treated as a defect.
- non-fatal guards: **NONE SURVIVES** — every command in blocks A and B carries `|| { print "ABORT: ..."; exit 1; }`;
  the only bare `|| true` sits inside the un-publish handler where it is intended.
- real-custody writes before the move: **NONE SURVIVES** — block A writes only `$STAGE`/`$SCRATCH`; the single
  `mkdir -p "$NIGHT_CUSTODY"` is at 21b:275, immediately before `os.replace`.
- duplicated authoritative text: **NONE SURVIVES** — 21b:133 is a pointer to H; no draft body remains.
- cure in the wrong block: **NONE SURVIVES** — `un-publishing the plan this session authored` occurs exactly once,
  21b:277, inside block B; the historical block aborts on its first line. Three ```zsh blocks, all `zsh -n` clean.
- false commit-message claim: **NONE SURVIVES** — every clause of 6c4a77d5's message checks out.

## 5. New defects from this delta

**N1 — should-fix. `events.jsonl` cited for records that are not in the PR.** 21b:24, 21b:25, 21b:305, 21b:310 cite
seq 5 / seq 7-8; the committed `21-activation-1ef89702/events.jsonl` ends at the notice_acknowledged record. Those
sequences exist only in the live, mutable `/Users/edr/night-custody/magistrate/events.jsonl` (I read it: seq 5
`epoch_s 1788856408.777019`, seq 8 `1788856918.677485` — both TRUE today). `21-activation-784a764e/` is an EMPTY,
untracked directory, so the succession activation has zero committed artifacts. R1 is met by the bare epochs, but
reproducibility dies at the next custody rotation. Cure: copy the current custody events.jsonl into
`21-activation-784a764e/` and cite that basename on those four lines.

**N2 — should-fix. Delta 4 attached a true derivation to a false claim.** 21b:133 says the removed draft "differed
from [H] (thread id, courier deadline 03:16 PDT (t0 + 1200 s = 1788948960), ...)". H's own text sets the courier
deadline to 03:16 PDT, and the removed draft (`git show 2987a626:docs/.../21b-...md`, section NIGHT_HANDBACK)
contains no courier deadline at all — zero matches for "courier deadline". So 03:16 is not a difference in either
direction, and the new parenthetical now makes the false item look derived. R4 licenses attaching a token or
deleting, not certifying. Cure: delete `courier deadline 03:16 PDT (t0 + 1200 s = 1788948960), ` from that list.

**N3 — nit (R4).** 21:53 `(cross-session reply)` is a new unsourced assertion, no message id. Cure: delete, or cite
the reply's id as was done for `a869e477`.

**N4 — nit (R4).** 21:55 "by its own estimate live for some hours more" swaps one unsourced claim for another and
adds an attribution. Cure: cite 21b:329 ("~1-2 h after 01:48 PDT") or delete the parenthetical.

**N5 — nit.** 21b:35 "selected Option B at 02:03 PDT (recorded in commit dbd49c1d)": the commit date bounds the
recording, not the selection, and the sentence now reads "(recorded in ...), as recorded in ...". Cure: "recorded
at 02:03 PDT in commit dbd49c1d, in `21c-ref-295-opus-contract.md` ...".

**N6 — nit (rule letter, not fact).** R1 admits "the basename of an artifact committed in the same commit"; 21:18,
21:32 and 21:52 cite `00-DURABLE-STATE.md` and `process-census-0055.txt`, committed EARLIER in the PR, and the R3
pre-commit gate prints all three. Contents verified true. Cure: widen the gate's alternation rather than re-edit.

**N7 — nit.** pass3-lead-benches.txt bookends are the identical epoch, so they do not bracket the run; costless
here because I reproduced all three benches independently.

VERDICT: LANDABLE — no blockers; N1 (events.jsonl seq 5/7-8 have no committed artifact) and N2 (false courier-deadline difference at 21b:133) are should-fix.
