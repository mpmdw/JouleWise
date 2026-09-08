SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["docs/process/NIGHT_HANDBACK.md","docs/process_traces/2026-09-02-hands-free-week/21-first-launchd-activation-1ef89702.md","docs/process_traces/2026-09-02-hands-free-week/21b-rehearsal-20260909-arm-plan.md"]

# Fix round 1 for PR #295 (docs-only trace) — dictated cures for the Opus refutation in trace 21c

Worktree: this checkout, branch bookkeeping/2026-09-08-activation-evidence at 83b3ec5e. Read first, in full:
docs/process_traces/2026-09-02-hands-free-week/21c-ref-295-opus-contract.md (the findings F1–F15 with file:line).
Then the three scoped files. Do NOT commit. Do NOT touch anything under ~/night-custody. Do not edit any other file.
Commit ae8f074f (H) is pinned by a ruling and is NOT rewritten; you edit the branch head only.

## Facts of record (from primary artifacts; use these verbatim, never the times currently in 21b)
| event | time PDT | source |
|---|---|---|
| launch email 1ef89702 (1a0800383847cde1) | 00:55:08 | Gmail internalDate 1788854108 |
| commit 67cbf5fe (trace 21) | 00:57:32 | git committer date |
| commit 4a7a768c (21a scout) | 01:02:02 | git |
| bench plan authored | 01:04:01 | bench-night_plan.json authored_epoch_s 1788854641.57 |
| commit 4ac5d981 (21b created) | 01:05:11 | git |
| ARM EMAIL 1a0800cdb282c3f1 | 01:05:21 | Gmail internalDate 1788854721 |
| commit f9679fb4 (arm email id recorded) | 01:05:39 | git |
| commit ae8f074f = H (handback rewritten) | 01:10:44 | git |
| pins follow-up email 1a08012045894ef7 | 01:10:59 | Gmail internalDate 1788855059 |
| commit b0c88632 | 01:11:22 | git |
| commit a8cc6e68 (cold-gate AMEND relayed) | 01:20:08 | git |
| commit 2987a626 | 01:20:19 | git |
| activation 1ef89702 terminated | 01:33:28 | events.jsonl seq 5 epoch 1788856408.777 |
| activation 784a764e spawned | 01:41:58 | events.jsonl seq 8 epoch 1788856918.677 |
| commits 9a15338e / a6bff232 / 83b3ec5e | 01:48:16 / 01:48:47 / ~01:58 | git |

## Cures (apply every one; cite the finding id in a short HTML comment or parenthesis where the edit lands)
F1+F2: In 21b replace EVERY self-reported "~HH:MM PDT" time with the table value and add a section
  "## Timeline of record (from commit and Gmail timestamps; the approximate times earlier in this file were 15–30 min
  ahead of the artifacts and are corrected in place)" containing the table above. Under it add one paragraph: the
  first arm email (01:05:21) preceded H (01:10:44) by 5 min 23 s; the pins follow-up (01:10:59) followed H by 15 s;
  whether D-175 cond. 1 is satisfied on the follow-up or requires a new arm notice after H is REFERRED to the
  synthesis author (joulewise-53) by activation 784a764e; NO ARM until that ruling is recorded here. Change the
  sentence "(1) satisfied at ae8f074f" to "(1) DISPUTED — see Timeline of record".
F3: Edit the step-4 census code block IN PLACE: replace `me = 84232` with
  `me = json.load(open(os.path.expanduser("~/night-custody/magistrate/magistrate.lock")))["pid"]` and add `json, os` to
  the imports on the first line of that block. Delete the prose correction bullet that begins "CORRECTION to step 4"
  and replace it with ONE imperative sentence: "Step 4 derives `me` from the lock the live activation holds; never a
  constant." (also cures F14)
F4: In both zsh blocks of the arm-time sequence, give every guard an explicit abort:
  `... || { print "ABORT: <short reason>"; exit 1; }` — for each `test`, `test !`, `git ... cat-file -e`, the
  rev-parse equality test, and `mkdir -p "$STAGE"`. Do not add `set -e` (the blocks are pasted into a tool shell).
F5 (as RULED by the synthesis author, 02:03 PDT): nothing may be created under the real custody root before the
  atomic move; cond. 2's staging rule covers the WHOLE validation. Rewrite steps 2–3 so that: (a) the PY block authors
  TWO plans with write_night_plan — the REAL one to "$STAGE/night_plan.json" (custody_root = $NIGHT_CUSTODY, chain paths
  under it) and a VALIDATION TWIN to "$SCRATCH/night_plan.json" where SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/jw-rehearsal-
  validate.XXXXXX") and the twin's custody_root/chain_path/chain_sha256_path point under $SCRATCH/custody, every other
  field byte-identical; (b) step 3 runs `--render-only "$SCRATCH/render"` against the TWIN only (so the installer's
  `mkdir -p "$custody_root/night"`, install_night_agent.sh:119-122, lands under $SCRATCH), lints both plists, then
  proves the twin and the real plan differ ONLY in the three custody-derived fields with a python json diff that exits
  1 on any other difference; (c) keep the step-2 guard `test ! -e "$NIGHT_CUSTODY"` (now valid again: nothing touches
  it before the move) and add the abort cleanup "On any abort: rm -rf "$STAGE" "$SCRATCH"". State in a comment that
  the real custody root is first created by the `mkdir -p` immediately before the os.replace in step 6.
F6: Insert a new step "3b. Stop every Codex child and every background task of this session BEFORE the census; a
  reparented process of this session's own (ppid 1) is reported foreign by step 4 and MUST abort the arm — this is
  fail-closed by design, no allowlist." Also rewrite the sentence in the joulewise-53-answers bullet that says
  "so no census change is needed" to say the regex matches them AND the ancestry walk reports them foreign because
  they are reparented to pid 1, which is the intended abort.
F7: In trace 21, line ~18: replace "clock_sane_samples: 4" with "clock_sane_samples: 36 (copied state.json,
  last_clock 00:57:27)"; line ~42: replace "33" with "36".
F8: In trace 21 line ~5, strike `notice.ack` from the copied-files list and add "(notice.ack had already been
  consumed by the watchdog; no copy exists)".
F9: In 21b, replace the whole "## NIGHT_HANDBACK.md text for this night" section body with: "Authoritative text:
  `git show ae8f074f:docs/process/NIGHT_HANDBACK.md` (committed 01:10:44). The draft that stood here preceded H and
  differed from it (thread id, courier deadline 03:16 PDT, install-FROM-checkout sentence, pointer to 21b); it is
  removed to avoid two versions."
F10: Add one sentence at the end of the "## Ruling on the scout's NEEDS_RULING" section: "Order of record (PD-1):
  the arm email (01:05:21) was sent under this operational ruling before the cold-gate AMEND and the D-175
  synthesis (a8cc6e68, 01:20:08) existed; nothing was armed; D-175 later ratified the substance."
F11: In docs/process/NIGHT_HANDBACK.md "Next lane" section, restore VERBATIM from `git show main:docs/process/NIGHT_HANDBACK.md`
  these four sentences (keep the per-night text, append them as a short "Standing rules" paragraph at the end of the
  section): (i) "Author every new v2 plan with `joulewise.night_plan_writer.write_night_plan`; invalid-plan tests begin
  with that writer's bytes and apply a named mutation."; (ii) the sentence about the writer emitting both `schema` and
  `schema_version: 2` and "either field missing or inconsistent makes the plan malformed"; (iii) the installer note
  that on install it checks `repo_head` against the driver checkout HEAD and `measurement_head` against the
  measurement_root HEAD "while `--uninstall` checks neither pin and no longer needs `claude` on PATH"; (iv) "Ordinary
  daytime work in the dev checkout no longer invalidates an armed night; only moving the pinned measurement checkout
  does." Copy the exact wording from main.
F12: In trace 21, after the step-6 checks list, add: "Step 6 also says a nonempty census before that tick is a failed
  handoff (MAGISTRATE_WATCHDOG.md:256); the 00:55 census was nonempty (joulewise-53 and the bg-job daemon tree), so
  the handoff is not clean under the doc's own clause until WATCHDOG-CENSUS-01 lands (joulewise-53's lane)."
F13: Replace the heartbeat sentence at trace 21 ~:33 with: "Nothing reads the heartbeat today (no occurrence in
  scripts/magistrate_watchdog.py; MAGISTRATE_WATCHDOG.md:81 names no fields); activation 1ef89702 wrote `epoch_s`,
  784a764e wrote `ts` — recorded, not resolved."
F15: At trace 21 ~:65 replace "`python3 …/T/watchdog` pid 48645" with "pid 48645 (python3.14, alive since 09-04
  04:53 per the census; identified as the leaked 09-04 test stub by joulewise-53, not from this census)".

## Acceptance (run all; paste tails in the report)
1. Extract every ```zsh block from 21b to files and `zsh -n` each; extract every heredoc PY block and
   `python3 -c "compile(open(f).read(), f, 'exec')"`.
2. Bench the corrected census block: write a fake lock `{"pid": 4242}` to a temp path, monkeypatch the
   `os.path.expanduser` target or the path string to that temp file, feed a fake `ps` table where 4242 parents
   a `claude -p` child and 9001 (ppid 1) is `claude daemon run`; expect foreign == [(9001, ...)] and exit 1; with
   only the own tree expect exit 0. Show the code and output.
3. `git diff --check` clean; `grep -n "~0" 21b` returns nothing that is a self-reported approximate time.
Report: claude-codex-report/v1 implementation envelope (JSON header < 8192 bytes), then per-finding disposition
table (F1–F15 → applied / where), then verification tails. Design disagreement welcome in its own section but apply
the cures as dictated unless impossible (then NEEDS_RULING with the blocked item).

## Addendum (magistrate, after the read-only first attempt)
The two remaining approximate times in the "Activation succession" section are the magistrate's own: replace
"~01:50 PDT" with "01:48:16 PDT (commit 9a15338e)" and "~01:52 PDT" with "01:48 PDT (recorded in a6bff232 at 01:48:47)".
Scratch files for the acceptance bench go under ${TMPDIR:-/tmp}; the sandbox is workspace-write this time.
