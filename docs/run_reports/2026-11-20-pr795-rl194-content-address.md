# PR #795: stage 1 admits by content address (RL-194), and audit round 1

RL-194 (research lead, 2026-11-20) rules that `lm-interim-01` may meet RL-184 §3.3 by content hash, because its
inputs are a closed set of eleven collected spans. This round builds that, keeps the grammar validator behind it as
defense in depth, and carries the audit-1 fixes that are still sound. Every test input is generated; no custody,
energy, meter or restricted file was opened.

## What changed

| Piece | Where | Role |
| --- | --- | --- |
| Pin list and first act | `joulewise/cadence_looks/custody_pins.py` | The pin-list format, its chain checks, `PinnedCustody.verify` and the guarded reads |
| Manifest | `lm-interim-01.json` `inputs.pins`, `lm-interim-01.inputs.json`, `manifest.py`, `look_manifest.schema.json` | The manifest pins one inputs file; that file pins every file of every roster span. It is unfilled in this draft: the lead fills it with `pin-inputs` |
| Pin tool | `scripts/cadence_look_manifest.py pin-inputs`, `check-inputs` | Writes the inputs file from the offload manifests without opening custody; follows the chain to each Check item |
| Stage 1 and stage 2 | `scripts/cadence_look_run.py` `admit_custody` | The first act on custody in both stages, before any other roster read and before the reservation |
| Twin | `scripts/cadence_interim_twin.py` `CustodyPins` | The child checks the pins itself on every custody read |
| Review record | `scripts/cadence_look_input_review.py`, `lm-interim-01.input-review.template.json` | The one-time record RL-194 §1 specifies |
| CI | `.github/workflows/ci.yml` | The two jobs that gated on the 101,889-case matrix are removed |

## How the six conditions are met

| # | Condition | Here |
| --- | --- | --- |
| 1 | The pins cover every roster file either stage or the twin opens; an open outside the list refuses | The pins are each span's whole offload inventory. The first act refuses a file that is not pinned. For the rest of the stage an open of a roster path outside the list refuses, and so does a raw open that bypasses the served bytes |
| 2 | Each pin chains to a public Check item; none is hashed fresh | A span's pins are its offload manifest's lines in order, so they rebuild that manifest's sha256. `pin-inputs` copies the digests and reads sizes from directory entries. A committed run requires the Check item on `origin/main` to name the digest |
| 3 | Hash the bytes that are parsed; a mismatch, a missing file or a symlink refuses first | Each pinned file is read once into memory, hashed and compared. Later reads are served from those bytes |
| 4 | The twin checks the pins itself | `CustodyPins` in the child: the pin list from the manifest, the inventory of each span directory, and a hash check on every read |
| 5 | The once-only review opens operational files only | `cadence_look_input_review.py review` reads receipts, soak references, leg records, summaries and bundle journals, each through its pin, and refuses any other path |
| 6 | An inadmissible real file comes to the research lead as a count and a shape | `check` fails on an inadmissible span or a disagreement and says so; nothing edits the roster |

## Decisions the lead should know

- **The reviewed #816 twin child changed.** Condition 4 requires it. Its sha256 was `91ca54ab…0aab` and is now the
  value `fit.twin.sha256` carries in the manifest. Every custody read in the child goes through `pinned_bytes`.
- **The pins are the whole offload inventory of each span,** not only the files a stage opens. That is what lets the
  pin list rebuild the offload manifest digest with no other file, and it makes "extra file" a total check.
- **Stage 1 holds every pinned byte in memory** from the first act to the end of the stage. The sum of the pinned sizes
  is known from the pin list before the run.
- **Staging.** `--stage-archives` hashes each member as it is written and never reopens it. Its per-file digests are
  the same offload-manifest lines the pins are, and the first act then reads the staged copy back.
- **Draft runs** name a generated custody's pin list with `--custody-pins`. A committed run cannot.

## The grammar validator on real data: a risk to settle before the run

The validator's controller-journal grammar was mirrored from the frozen packet's writer productions. Those drive the
bundle serializer directly. The real leg runtime runs the whole controller (`joulewise/align/apple/r1_runtime.py`
1537-1546 at `6e9d42f1d` calls `controller.run_benchmark`), which also writes `sampling_started`, `sampling_stopped` and
`timing_boundary` rows and stage rows with metadata. The validator refuses those today ("not an event a pinned writer
records"). I did not open real custody, so this is read from the pinned source, not observed. If it holds, the
validator refuses every real span after the pins have admitted it.

RL-194 §2 says the builder's closed list shrinks to the shapes present in the eleven spans. The review record is
where those shapes come from. Until the validator mirrors them, a real stage 1 will stop at the validator.

## Audit round 1

| Finding | Disposition |
| --- | --- |
| H4: a genuine deadline result refused | Fixed. `finish_reason` is text or null; the deadman's stop needs its flag. A fixture generated by the pinned writers at all three revisions is committed with its generator |
| Same class: hand-written `FailureReason` list | Fixed. It is the writers' ten members, checked against the pinned sources when they are in history |
| H2: an unfinalized failure journal admitted | Fixed. A failure row is followed by `run_finalized`; a journal with no failure closes every stage it opened |
| H3: a contradictory display status admitted | Fixed, with the same class across the step results (feed constants, host checks, meter-stop evidence) |
| H1: archive staging read protected files before refusal | Superseded by RL-194: the hash of every file is now the ruled first act. Staging no longer reopens a member to hash it |

Under RL-194 a shape no pinned file can hold is a low finding. H2 and H3 are kept because they are sound and cheap.

## Verification

Local runs were limited: the build host carried a load average near 140 from other lanes, so one CLI test took
minutes. These passed locally: `test_custody_pins` (28), `test_input_review` (7), `test_look_run.Staging` (7), the
staged stage-1 CLI test, and `test_interim_admission.AuditOne` (9). The full suite is hosted CI's.

## Follow-ups

- Mirror the real controller's journal rows in the validator, from the shapes the review record lists.
- The frozen 101,889-case packet stays in the tree unedited. It drives the CLI without a pin list, so it cannot run as
  it stands; its productions still feed the in-process validator tests.
