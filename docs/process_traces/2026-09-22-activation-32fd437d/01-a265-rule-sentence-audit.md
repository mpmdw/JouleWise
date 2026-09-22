# A265 CANONICAL-REFUSAL-STRINGS-01 — rule-sentence audit of the D-183 paragraph

Branch: `fix/2026-09-22-canonical-refusal-strings`
Base sha: `d45378c6`
Date: 2026-09-22 (activation 32fd437d)

## What this record is

Contract item 1 of `docs/contracts/evidence_night_entry.md` contains one
paragraph headed **Self fast-forward (D-183, Ed 2026-09-21)**. That paragraph
states, as rules, what the `check` command does when the canonical checkout —
the working copy of this repository at `/Users/edr/code/JouleWise`, the one the
night arm reads from — is clean but does not yet contain candidate H (the commit
a night is being armed at). This record takes that paragraph one sentence at a
time, names the code line each sentence asserts something about, names the
probe that was run against that code line, and gives the sentence's truth value
before this change (the text at base `d45378c6`) and after it.

"Probe" here means a command that was actually executed in this worktree during
this session; every probe's output is pasted verbatim under **Executed
evidence** below. No file:line is cited that was not opened.

"Refusal string" means the text of the `Refused` exception the code raises. The
`check` command stores that text as the failing check's `reason` field in
`lifecycle/check.json` and, unless the cause is re-raised by name, exits with
the generic line `pre-arm checks failed: <failed check names>; see <path>`.

## The defect this lane closes

Finding N-1 of the Opus contract-lens refutation of the 2026-09-21 round-3 cold
gate (`docs/process_traces/2026-09-21-activation-ce7c57a9/02-coldgate-packet-retained-root-round3/11-opus-contract-refuter.md`,
§Rule-sentence audit item 3 and §Findings N-1): the contract said all four
failure causes refuse with `canonical fast-forward failed: …`. Three of the
seven causes the code can actually raise do not use that prefix, the dirty-tree
cause among them, and no test pinned any of the three.

## Audit table

| # | Sentence (text at base d45378c6) | Code line(s) at branch head | Probe | Before | After |
|---|---|---|---|---|---|
| S1 | "when the canonical checkout is clean but does not contain H, and item 0 passed (no night label loaded, no plist or sidecar present, label discovery known), `check` runs `git -C <canonical> pull --ff-only` itself" | `joulewise/evidence_night.py:642-646` (the not-contains-H branch and its licence argument), `:912-913` (`may_fast_forward=nothing_loaded`), `:831-838` (`require_no_night_agents`: a non-ABSENT job, any plist, or a non-zero discovery exit code refuses), `:621-622` (the pull argv) | `python3 -m unittest tests.test_evidence_night.LifecycleTests.test_canonical_fast_forwards_itself_when_nothing_is_loaded` (probe B) | TRUE | TRUE (unchanged) |
| S2 | "bounded to 120 s with `GIT_TERMINAL_PROMPT=0` so an unreachable remote or a credential prompt refuses instead of hanging" | `:31` (`FAST_FORWARD_TIMEOUT_S = 120`), `:620-624` | `python3 -m unittest tests.test_evidence_night.LifecycleTests.test_canonical_fast_forward_is_bounded_and_prompt_free` (probe B); new `test_canonical_fast_forward_branch_refusal_strings_are_pinned` asserts `FAST_FORWARD_TIMEOUT_S == 120` | TRUE | TRUE (unchanged) |
| S3 | "and records `fast_forward: {before, after, pull, clean_before}` in the evidence" | `:630-631` (the four keys), `:649` (`fast_forward=` in the check evidence) | `python3 -m unittest tests.test_evidence_night.LifecycleTests.test_canonical_fast_forwards_itself_when_nothing_is_loaded` (probe B) | TRUE | TRUE (unchanged) |
| S4 | "A dirty tree, a missing or divergent upstream, a timeout, or a pull that still lacks H refuses with `canonical fast-forward failed: …`; the still-lacks-H cause names the before and after shas because the tree did move." | `:602-605`, `:614-617`, `:620-626`, `:627-629`, `:595-598`, `:632-634` — see the per-cause table below | probe A (direct call of `canonical_fast_forward` on every branch) plus the four new tests | **FALSE** | TRUE (sentence replaced) |
| S5 | "With item 0 failed the pull is not licensed and the check refuses without moving anything." | `:642-646`, `:912-913` | `python3 -m unittest tests.test_evidence_night.LifecycleTests.test_canonical_fast_forward_refuses_dirty_tree_and_loaded_agents` (probe B) | TRUE | TRUE (unchanged) |
| S6 | "A checkout that already contains H records `fast_forward: null`." | `:641-642`, `:649` | `python3 -m unittest tests.test_evidence_night.LifecycleTests.test_canonical_fast_forwards_itself_when_nothing_is_loaded` (probe B, `assertIsNone`) | TRUE | TRUE (unchanged) |
| S7 | "The pull may make the resident supervisor stale under item 2; that refusal names the hand-off (`… commit, push and exit so the watchdog's successor arms`) and `check` re-raises that stale case as its own cause (other supervisor causes stay under the generic `pre-arm checks failed` line) — the session exits and the watchdog's successor arms — never an owner action." | `:692-694` (the stale refusal text), `:933-935` (the re-raise by prefix), `:936-937` (the generic line) | `python3 -m unittest tests.test_evidence_night.LifecycleTests.test_fast_forward_makes_the_resident_supervisor_stale_and_says_so` (probe B) | TRUE | TRUE (unchanged) |

### S4 expanded: one row per refusal the code can raise

Each row is a branch of `canonical_fast_forward` (including the two helpers it
calls, `canonical_status` and `contains_head`). "Named before" asks whether the
sentence at base `d45378c6` gave this cause its actual text.

| Cause | Refusal string (verbatim, from probe A) | Code line | Named before | Named after |
|---|---|---|---|---|
| tracked modification, or the `status` probe itself failing — checked before anything moves | `canonical checkout is dirty or unreadable: ` + the probe's stdout and stderr, unstripped | `:604-605` (raised from `:614`) | **NO** — the sentence claimed `canonical fast-forward failed: …` | yes |
| `git rev-parse HEAD` fails before the pull | `cannot read canonical HEAD: ` + stderr | `:616-617` | **NO** — cause absent from the sentence entirely | yes |
| the 120 s bound expires | `canonical fast-forward failed: timed out after 120 s` | `:623-624` | yes (prefix correct) | yes (full text) |
| `pull` exits non-zero (no upstream, divergent upstream, refused credential prompt) | `canonical fast-forward failed: ` + stderr, or stdout when stderr is empty | `:625-626` | partly — prefix correct, the stdout fallback was unstated | yes |
| `git rev-parse HEAD` fails after the pull | `cannot read canonical HEAD after fast-forward: ` + stderr | `:628-629` | **NO** — cause absent from the sentence entirely | yes |
| `git merge-base --is-ancestor` exits neither 0 nor 1 | `cannot determine canonical ancestry: ` + stderr | `:597-598` (raised from `:632`) | **NO** — cause absent from the sentence entirely | yes |
| the pull moved HEAD but H is still absent | `canonical fast-forward failed: HEAD moved <before> -> <after> but still does not contain candidate H` | `:632-634` | yes | yes |

### Tests added (all in `tests/test_evidence_night.py`, class `LifecycleTests`)

Each asserts the refusal text with `assertEqual`, so any rewording of the string
in `joulewise/evidence_night.py` fails the test (demonstrated by probe D).

- `test_canonical_dirty_tree_refusal_string_is_pinned` — end-to-end through
  `entry.check`: a tracked modification on a checkout behind H gives exactly
  `canonical checkout is dirty or unreadable:  M tracked\n`, contains no
  "fast-forward failed" text, moves nothing, attempts no pull, and surfaces
  under the generic `pre-arm checks failed: canonical…` line.
- `test_unreadable_canonical_head_before_the_pull_refusal_string_is_pinned` —
  `cannot read canonical HEAD: fatal: bad HEAD`, no pull attempted.
- `test_unreadable_canonical_head_after_the_pull_refusal_string_is_pinned` —
  `cannot read canonical HEAD after fast-forward: fatal: bad HEAD`, the pull
  having already moved the fixture checkout to its tip.
- `test_canonical_fast_forward_branch_refusal_strings_are_pinned` — direct calls
  of `canonical_fast_forward` with a scripted runner: the timeout text, both
  pull-failure texts (stderr and the stdout fallback), the ancestry-probe text,
  and the moved-but-lacks-H text with both shas.
