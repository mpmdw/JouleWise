FINAL PASS: PASS

Cold, delta-limited final pass on `ea6e93a8` (PR #482) against the previous
head `32ee573a`. Reviewer: Fable 5.1, one session, no subagents, checkout left
clean (`git status --short` empty at the end).

One sentence: B1 is closed — every stage of the G2-b chain now receives the
pre-calibration attachment in the root the plan assigns it — and every shape
outside the lead's ruling that I could construct is still refused with main's
own refusal text. No blocker, no high or medium finding. Four
low/informational notes follow the two answers.

Terms used below (same meanings as the round-2 ruling):
- "Revision-5 capture": a calibration capture whose evidence carries a
  `battery_float` record or the Revision-5 identity epoch. `main` refuses to
  attach one to a run ("revision_five evidence cannot be attached as
  instrument calibration", `joulewise/controller.py:464-472`).
- "marker": the run-metadata tag `launch_lineage_required`.
- "lineage root": a runs directory holding `.joulewise-launch-lineage.json`.
  A launch publishes one in the claim root (science and window-reference
  bundles) and one in the bound root (the NEG-8 bound-corpus bundles).
- "the exception": PR #482's route that lets a Revision-5 capture be attached
  when it is the launch's own finalized pre-calibration slot.
- "auxiliary config": a config that is not a member of the science pack but
  that the pack's plan tree (`plan_tree.json`, authenticated by its SHA-256
  sidecar) lists under `external_inputs`, each with a repository path and a
  SHA-256. In the tracked plans these are the 12 bound-corpus configs and the
  3 + 1 + 3 start/midpoint/end window-reference configs: 19 per plan.
- "root role": which of the two lineage roots a run is in, as the lineage
  authenticator derives it (`claim_runs_root` or `bound_runs_root`,
  `joulewise/arm_readiness.py:11395-11406`). It is derived from the arm
  context, not taken from the caller.

## What changed in the delta

`joulewise/controller.py:612-623`: the route still asks the bundle writer's
member check first (marker + command-line source equality + pack inventory).
If that yields nothing, it now asks a second question,
`_g2b_auxiliary_config_matches` (`controller.py:539-586`), and returns "no
exception" (so main's refusal fires) only if both say no. The second question
requires all of:
1. the process was started as `… run <config-path> …`, the path is not a
   symlink, and the file parses to a config equal to the running one
   (`joulewise/bundle.py:87-115`, the writer's own check, moved into a shared
   function with no change in behaviour);
2. the file sits inside the pack's git worktree and its repository-relative
   path AND SHA-256 equal one `members` entry of one external input in the
   authenticated plan tree (`controller.py:551-566`);
3. a `campaign_collection` stage in the plan's stage graph consumes that same
   external input, and that stage's command passes `--runs-dir` bound to the
   root role the run is actually in (`controller.py:567-585`).

Everything after eligibility (session status, finalization receipt, byte
digests, battery pair) is unchanged and applies to auxiliaries exactly as to
science members.

## What I ran

All logs in `/tmp/dd5-fable-ct4/`.

- **Sol's repro** (`regressions.py`, only the `sys.path` line changed; log
  `regressions.log`):
  - `test_plain_member_should_retain_legacy_refusal`: **ok** — F1's untagged,
    unregistered config in an authenticated root is refused with
    `revision_five`, as on `b2ff2f36`.
  - `test_reserved_directory_symlink_is_refused`: reported FAIL, the same
    harness artifact as in round 2 — the script calls the loader with the old
    signature (no `config`), so the capture is refused with main's ordinary
    message instead of the "finalized pre slot" message the script greps for.
    Still refused. The in-tree test of the same case
    (`tests/test_controller_g2b_attachment.py:362`) passes.
- **My probe, rerun** (`refstage.py`, log `refstage.log`). The round-2 script
  named configs at the checkout path; under round 3 a config must sit inside
  the launch's repository, so I pointed it at the same tracked bytes inside
  the fixture's launch repository (the real chain runs them from `$REPO`,
  which also holds the pack) and kept the old shape as case C1. Fixture
  lineage, real block-3 capture bytes, the real `d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5`
  plan tree's external inputs and stage graph, loader called exactly as
  `run_benchmark` calls it, `sys.argv` as the campaign runner sets it.
  Results (38 loader calls, 663 s):

  | case | root | result |
  |---|---|---|
  | bound corpus r01–r12 (12 configs, untagged) | bound | 12/12 ATTACHED |
  | start triplet r1–r3 (untagged) | claim | 3/3 ATTACHED |
  | midpoint (untagged) | claim | ATTACHED |
  | end triplet r1–r3 (untagged) | claim | 3/3 ATTACHED |
  | science tagged pack member | claim, bound | ATTACHED, ATTACHED |
  | bound corpus r01 | claim (wrong) | REFUSED `revision_five` |
  | start r1, midpoint, end r1 | bound (wrong) | REFUSED `revision_five` ×3 |
  | C1 pinned bytes, path outside the launch repository | bound | REFUSED `revision_five` |
  | C2 unpinned file name, pinned bytes, inside the pinned directory | bound | REFUSED `revision_five` |
  | C3 pinned path, `run_id` changed, running config equal to the changed file | claim | REFUSED `revision_five` |
  | C4 pinned path, one trailing newline added | claim | REFUSED `revision_five` |
  | C5 pinned file on the command line, different running config | claim | REFUSED `revision_five` |
  | C6 untagged config that IS in the pack inventory but is not an auxiliary | claim | REFUSED `revision_five` |
  | C7 F1: untagged, unregistered config | claim | REFUSED `revision_five` |
  | C9a command line is not `run` | bound | REFUSED `revision_five` |
  | C9b command line names a symlink to the pinned file | bound | REFUSED `revision_five` |
  | C11 loader called with no config | bound | REFUSED `revision_five` |

  Every refusal is a `ValueError` carrying main's text; none attached wrongly,
  none of the 19 + 2 genuine shapes was refused.
- **Static sweep of every tracked plan** (`static_plans.py`, log
  `static_plans.log`): the production matcher called directly, repository =
  this checkout, for all 12 tracked `plan_tree.json` files (4 contrast packs,
  list-shaped external inputs; 8 floor packs, dict-shaped) × 19 auxiliary
  members × both root roles. In all 12: bound corpus matches the bound role
  12/12 and the claim role 0/12; start, midpoint and end references match the
  claim role 3/3, 1/1, 3/3 and the bound role 0. The tracked bytes of all
  228 member files equal their pinned SHA-256 (0 stale), and none carries the
  marker. Negative control: the 1,657 other tracked JSON files under
  `configs/` that parse as a config, tried in both roles against the contrast
  v5 plan: 0 matches.
- **Unit tests**: `tests/test_controller_g2b_attachment.py` — 23 passed,
  33 subtests passed (652 s). This includes the eight new round-3 tests and
  the round-2 refusal tests, unchanged and still passing.
- NOT run: `tests/test_g2a_calibration_attachment.py`,
  `tests/test_revision_five_b_readers.py`, `tests/test_controller.py`, the
  battery tests, the whole suite (not touched by the delta; budget).

Process disclosures: the probe and the unit-test run each exceeded the 600 s
tool limit and the harness moved them to background on its own; I waited for
both to finish and read their logs. They overlapped, so the timings above are
inflated. Total elapsed was past the 25-minute budget because of those two
runs. No powermetrics, sudo, launchctl or model; this test file uses the mock
backend and calls the loader directly.

## Question 1 — does every stage of the real G2-b chain now attach?

Yes, for the chain as the runbook and generator define it.

The chain hands the same pre-calibration directory to five kinds of stage
(`docs/phase_2/window_runbook.md:1656-1677`; the G2-b generator replaces only
the science call and the completion step, `scripts/gen_g2_phase_d.py:515-553`).
Row by row:

| stage | root in the chain | plan's root for that input | result |
|---|---|---|---|
| `neg8-bound-corpus` (12) | bound | bound | attaches (probe 12/12; static 12/12 in 12 plans) |
| `start-reference-triplet` (3) | claim | claim | attaches (3/3) |
| science stage | claim | pack member, marker | attaches (unchanged from round 2) |
| `midpoint-reference` (1) | claim | claim | attaches |
| `end-reference-triplet` (3) | claim | claim | attaches (3/3) |

The three facts the real chain must supply, and where I checked each:
- configs are started as `… run <absolute path> …`: `scripts/run_campaign.py:1551-1552`,
  with paths from `config_dir.glob("*.json")` (`:1877`) under the absolute
  `$REPO/configs/campaigns/…` directories (`window_runbook.md:1496-1497`);
- those directories are inside the same git worktree as the pack: `REPO` and
  `PACK_ROOT` share the measurement checkout (`window_runbook.md:202, 1364`),
  and the repository is derived from the pack root
  (`joulewise/arm_readiness.py:3063-3073`);
- the plan pins exactly those paths and the bytes tracked at this commit:
  static sweep, 0 stale of 228.

## Question 2 — is everything outside the ruling still refused as on main?

Yes. Each case the lead named, with the evidence:

- unpinned config: C2 (probe) and `test_unpinned_auxiliary_path_is_refused`;
  plus 0 of 1,657 unpinned tracked configs match;
- pinned path with changed bytes: C3 (semantic change, running config equal
  to the changed file — the strongest form, since the equality check passes
  and only the digest refuses), C4 (whitespace only), and
  `test_pinned_auxiliary_with_changed_bytes_is_refused`;
- auxiliary in the wrong root: four probe rows, one per stage kind, and
  `test_auxiliary_in_wrong_root_is_refused`, on both plan shapes
  (`test_floor_plan_manifest_descriptors_assign_auxiliary_roots`);
- untagged non-auxiliary: C6 (in the pack inventory, untagged) and the
  round-2 test at `tests/test_controller_g2b_attachment.py:346`;
- F1's unregistered config: C7, Sol's repro, and the test at `:333`.

All refuse through the unchanged line `controller.py:464-472`, before a
bundle directory exists, with no fall-through to the G2-a route (the `elif`
at `controller.py:460`).

Nothing an auxiliary stamps, samples or reduces is touched: the delta is the
eligibility decision plus a behaviour-preserving extraction in `bundle.py`;
the added work runs inside the loader call (`controller.py:298`), before the
bundle is created.

## Findings

**L1 (low) — eligibility needs the config inside the pack's git worktree.**
`joulewise/controller.py:552`. The pinned path is compared after making the
command-line file relative to the repository that holds the pack. Identical
bytes at any other location are refused (case C1). The runbook chain
satisfies this (`REPO` holds both). A future chain that ran reference configs
from a different checkout than the pack would stop at its first stage, fail
closed. Not a defect under the ruling ("repository path … pinned"); recorded
so the dependency is known.

**L2 (nit) — non-ValueError escapes on a malformed plan tree.**
`controller.py:577-584`: `stage.get("launch", {}).get(…)`, `command.get(…)`
and `.get("argv_template", {}).get(…)` raise `AttributeError` if those values
are not objects. The tree is sidecar-authenticated and the launch is already
authenticated at this point, so reaching this needs a committed, malformed
plan; it would refuse with a traceback rather than the route's `ValueError`.
Same class as round-1 L3.

**L3 (info) — a marker-bearing config that fails the writer's check now gets
the auxiliary question too.** `controller.py:614-617, 622`. Round 2 returned
"no exception" immediately; round 3 sets `member_lineage = None` and asks the
auxiliary matcher. No tracked auxiliary carries the marker (0 of 228), so
this is unreachable today. If one ever did, the loader would attach and the
writer's own check (`bundle.py:118-170`, repeated at bundle creation) would
then refuse the bundle — fail closed either way.

**L4 (info) — what I did not verify.**
- A rendered, live G2-b chain. I read the runbook and the generator, as in
  round 2.
- The pack the next arm will actually use. The runbook's example names
  `d117_floor_qwen25_1p5b_v4`, which has no tracked plan tree at this commit;
  I swept the 12 that exist. A pack whose plan omits `members` under an
  external input, or binds `--runs-dir` differently, would be refused (fail
  closed) — worth one run of `static_plans.py` against the armed pack.
- The CLI end to end (`python -m joulewise run`); the probe enters at the
  loader with `sys.argv` patched, which is the level the eligibility check
  reads.
- Readers of the reference and bound bundles after collection (the
  `--derive-neg8-drift-bound` step, harvest). Those bundles now carry a
  Revision-5 attachment with the `g2b_pre_slot` record and the two battery
  raw files; on main they could never carry a Revision-5 capture. No file
  under `joulewise/` or `scripts/` other than `controller.py` reads
  `g2b_pre_slot` (grep), which matches round 1's observation for science
  bundles, but I did not run the bound derivation over such a bundle. Outside
  this delta; it is the next place the chain could stop.
- Cost: each chain member, auxiliary or science, pays the slot authentication
  (lineage, session status, ledger snapshot, hashing the capture) before its
  bundle exists. In my probe that was roughly 17 s per call on a loaded
  machine, so the order of 5 minutes across the 19 auxiliaries of a night,
  outside every measured phase. Not measured on a quiet machine.

## Verdict

B1: closed — 19 of 19 auxiliary configs attach in their assigned roots, on
both plan shapes, alongside the science members. F1 and the four other
out-of-ruling shapes: refused with main's text. New stamps, samples or
reductions: none. Safe to merge on the question asked; the one thing I would
do before the arm is the L4 sweep of the armed pack's plan tree.
