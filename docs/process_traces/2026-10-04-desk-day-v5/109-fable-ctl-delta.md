FINAL PASS: FAIL

Cold, delta-limited final pass on `32ee573a` (PR #482) against the previous
head `9b08ecf6`. Reviewer: Fable 5.1, one foreground session, no subagents,
checkout left clean (`git status --short` empty at the end).

One sentence: F1 is closed exactly as written, but the rule that closes it
also refuses the reference and bound-corpus stages of the real G2-b chain, so
the chain would stop at its first stage after pre-calibration. Nothing wrong
can be measured (the refusal happens before a bundle exists); the cost is a
lost G2-b night.

Terms used below:
- "Revision-5 capture": a calibration capture whose evidence carries a
  `battery_float` record or the Revision-5 identity epoch. `main` refuses to
  attach one to any run unless the G2-a diagnostic route authenticates it
  (`joulewise/controller.py:464-472`).
- "marker": the run-metadata tag `launch_lineage_required`
  (`joulewise/arm_readiness.py:11454-11461`).
- "lineage root": a runs directory holding `.joulewise-launch-lineage.json`.
  A launch publishes one in the claim root and one in the bound root.
- "the exception": PR #482's new route that lets a Revision-5 capture be
  attached when it is the launch's own finalized pre-calibration slot.

## What I ran

- Sol's repro, pointed at this checkout (`/tmp/dd5-fable-ct3/regressions.py`,
  only the `sys.path` line changed; log `/tmp/dd5-fable-ct3/regressions.log`):
  - `test_plain_member_should_retain_legacy_refusal`: **ok**. The untagged,
    unregistered config in the authenticated root is now refused with
    `revision_five`, as on `b2ff2f36`.
  - `test_reserved_directory_symlink_is_refused`: reported FAIL, but it is a
    harness artifact, not a regression. The script calls the loader with the
    old signature (no `config`), so the route declines and the capture is
    refused with the ordinary `revision_five` message instead of the
    `finalized pre slot` message the script greps for. It is still refused.
    The in-tree copy of this test, which goes through `run_benchmark` with a
    config, passes.
- `tests/test_controller_g2b_attachment.py`, `tests/test_g2a_calibration_attachment.py`,
  `tests/test_revision_five_b_readers.py`: 27 passed, 9 subtests passed (268 s).
- A scratch probe of my own (`/tmp/dd5-fable-ct3/refstage.py`, log
  `refstage.log`), described under B1.
- NOT run: the whole suite, `tests/test_controller.py`, the battery tests
  (the delta does not touch them; budget).

## Question 1 — is F1 closed?

Yes, as specified.

`_authenticate_g2b_pre_slot_attachment` (`joulewise/controller.py:556-568`)
now authenticates the lineage, then calls the bundle writer's own member
check, `_writer_launch_lineage` (`joulewise/bundle.py:87-165`), and returns
"no exception" unless that check returns a lineage. That check requires all
of:
1. the running config carries the marker (`bundle.py:93`);
2. the process was started as `… run <config-path> …`, the path is not a
   symlink, and the file parses to a config equal to the running one
   (`bundle.py:96-122`);
3. that file's bytes are listed, by path and SHA-256, in the pack's
   authenticated config inventory (`bundle.py:123-146`).

When the route returns "no exception", the loader falls to main's refusal
line (`controller.py:464-472`); the G2-a route is not tried (the `elif` at
`controller.py:460`). Each ineligible shape has a passing test that also
checks no bundle directory was created: untagged and unregistered (F1
itself), tagged but not in the inventory, in the inventory but untagged,
and running config differing from the file named on the command line
(`tests/test_controller_g2b_attachment.py:210-237`).

The campaign runner starts members as `[python, -m, joulewise, run, <path>, …]`
(`scripts/run_campaign.py:1551-1552`), which is the shape check 2 needs.

## Question 2 — did the fix refuse anything genuine G2-b members need?

**Yes. This is the blocker.**

### B1 (blocker for the G2-b night; fails closed) — the chain's reference and bound-corpus stages lose the attachment

`joulewise/controller.py:561-568`, with `joulewise/bundle.py:93`.

The forcing fact: the window chain hands the SAME pre-calibration directory
to EVERY campaign stage, not only to the science stage.
`run_stage` passes `--instrument-calibration-dir "$calibration_dir"`
unconditionally (`docs/phase_2/window_runbook.md:1589-1611`, flag at `:1604`),
and the chain calls it with `"$PRE_CAL_CUSTODY"` for five kinds of stage
(`window_runbook.md:1656-1677`):

| order | stage | runs root | config directory | configs carry the marker? |
|---|---|---|---|---|
| 1 | `neg8-bound-corpus` | bound root | `configs/campaigns/neg8_reference_corpus` | no |
| 2 | `start-reference-triplet` | claim root | `configs/campaigns/window_references/start_triplet` | no |
| 3 | science stage(s) | claim root | the pack's stage directory | yes |
| 4 | `midpoint-reference` | claim root | `configs/campaigns/window_references/midpoint` | no |
| 5 | `end-reference-triplet` | claim root | `configs/campaigns/window_references/end_triplet` | no |

(`REF_ROOT` and `BOUND_CONFIG_ROOT` are set at `window_runbook.md:1496-1497`.)
I counted: 0 of the 24 JSON files under those two directories contain
`launch_lineage_required`.

The G2-b chain is rendered from that full runbook chain; the generator
replaces only the two science-stage calls and the completion step
(`scripts/gen_g2_phase_d.py:515-553`). Rows 1, 2, 4 and 5 stay as they are.

Both lineage roots hold a locator after `settle`, so every one of those
stages enters the G2-b route. In G2-b the pre-calibration is a Revision-5
capture. Under `32ee573a` an untagged config gets "no exception" at
`controller.py:567-568` and then main's refusal.

Evidence (executed, fixture lineage, real block-3 capture bytes, tracked
reference configs, the loader called exactly as `run_benchmark` calls it,
`sys.argv` set as the campaign runner would set it):

```
bound-corpus@bound_root   configs/campaigns/neg8_reference_corpus/neg8-refcorpus-r01.json      tagged=False -> REFUSED: revision_five evidence cannot be attached as instrument calibration
window-reference@claim_root configs/campaigns/window_references/end_triplet/neg8-window-end-r1.json tagged=False -> REFUSED: revision_five evidence cannot be attached as instrument calibration
control tagged pack member@claim_root -> ATTACHED g2b_pre_slot=True
control tagged pack member@bound_root -> ATTACHED g2b_pre_slot=True
```

Consequence on a real G2-b night: member 1 of `neg8-bound-corpus` raises
before its bundle exists; the stage runs with `--max-failures 1`
(`window_runbook.md:1608`) and `run_stage … || return $?` under `set -e`, so
the chain stops there — after launch consumption, start, settle and the
pre-calibration, before any reference or science member. No wrong number is
produced. The arm is spent.

Why the existing tests did not show it: the bound-root acceptance test
(`tests/test_controller_g2b_attachment.py:159-162`) runs the TAGGED pack
member in the bound root. In the real chain the only campaign stage that
runs in the bound root is the untagged reference corpus. The new test
`test_authenticated_untagged_member_retains_revision_five_refusal`
(`:223-231`) pins the refusing behaviour for untagged configs as intended.

Why this is a conflict in the requirement, not a slip in the code: `main`
refuses a Revision-5 capture for these reference stages too, so "every
config other than a marker-bearing pack member keeps main's refusal" and
"the G2-b chain can run" cannot both hold while the chain passes the capture
to untagged stages. `9b08ecf6` let the chain run but let any config in a
lineage root through (F1). `32ee573a` closes F1 but stops the chain. The
function's own docstring still says "Both claim and bound members use the
session" (`controller.py:544-546`), which in the real chain can only mean
the untagged bound corpus.

What I did NOT verify: the CLI's exit code for this `ValueError`, and the
live G2-b chain bytes (I read the generator and the runbook, not a rendered
chain). Things that would change this finding: G2-b reference/bound stages
receive a different, non-Revision-5 calibration directory; or they are meant
to run with no calibration attachment.

Ways out, for the lead to choose (I did not design or test these):
- (a) Widen eligibility to a second, equally authenticated class: an
  untagged config whose command-line source bytes appear in a reference
  inventory that the launch lineage itself pins (if the arm context or
  launch manifest binds the hashes of `window_references` and
  `neg8_reference_corpus`). An unlisted config stays refused, so F1 stays
  closed.
- (b) Stop passing the calibration directory to reference stages in the
  G2-b chain. This changes what those members record (no fiducial bound
  folded into their clock-anchor bound) and what harvest then accepts, so
  it needs its own check.
- (c) Give the reference configs the marker. The 10-04 stop-flag review
  recorded that a G2-b authorization refuses marker-bearing stages that lack
  its flag, and the reference hashes are frozen, so this is the most
  invasive.

Add a test that runs a tracked, untagged reference config in the bound root
whichever way is chosen; my scratch probe is a starting point.

## Question 3 — anything new in what a member stamps, samples or reduces?

No.

- Stamps and metadata: the delta adds no field. `g2b_pre_slot` has the same
  five keys. The acceptance test gained two assertions on fields the writer
  already wrote (`extra.launch_lineage`, `extra.launch_lineage_locator_sha256`).
- Sampling: the added work is one more lineage authentication plus one
  config file read and hash, at `controller.py:564`. It runs inside the
  loader call at `controller.py:298`, before `RunBundleWriter.create`
  (`:339`), so before any stage, sampler or stamp. A tagged member now
  authenticates the lineage three times before its bundle exists (route,
  member check, writer) instead of two.
- Reduction: `joulewise/reduce.py` and the reducer's inputs are not in the
  delta.
- The member check sees the config before suite-manifest preparation
  (`controller.py:304` vs `:308`); the writer repeats the same check on the
  prepared config (`bundle.py:933`). I read only the head of
  `_prepare_suite_manifest_for_new_bundle`; its docstring says `config.json`
  identity is left unchanged. A disagreement between the two would refuse,
  not admit.

## Other findings

**N1 (info) — legacy captures for ineligible configs return to main's behaviour.**
`controller.py:561-568`, `:464-472`. Under `9b08ecf6` every capture in a
lineage root had to pass the slot checks. Under `32ee573a` an ineligible
config skips them, so a capture that is NOT Revision-5 attaches with no
session check, exactly as on `main`. Equal to main; noted because the
previous pass listed it as a tightening that no longer exists.

**N2 (info, unchanged from `9b08ecf6`) — the lineage is authenticated before the member check.**
`controller.py:556`. An untagged run that passes a calibration directory in
a root whose locator is corrupt, from an earlier boot, or already completed
raises `LaunchLineageError`, where `main` would not have looked at the
locator. Fail-closed. If B1 is fixed by widening eligibility, the order is
right as it stands.

**N3 (info) — callers that are not the CLI never get the exception.**
`bundle.py:96-101` reads `sys.argv`. A programmatic `run_benchmark` call, or
a direct loader call without `config`, is refused even for a genuine tagged
member. Same rule the writer already applies; it is why Sol's second repro
test changed message.

**N4 (nit) — cross-module private import.** `controller.py:73` imports
`bundle._writer_launch_lineage`. Reusing the one check is the right call;
a public name would make the dependency visible to whoever edits the writer.

## Verdict

F1: closed. New stamps, samples or reductions: none. Genuine members
refused: yes — every untagged reference and bound-corpus member of the G2-b
chain (B1). Merging `32ee573a` is safe for the numbers and unsafe for the
next G2-b arm; I would not merge it as the last step before that arm without
a ruling on B1.
