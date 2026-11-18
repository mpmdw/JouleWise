# F2 stability kits for the qualification runner

Unissued product fillers for the first native run on `df261f6a235e976be8859ab5314af737a08f6d7d` (RL-179 F-11).
The leg is ordinary `f2-stab` product, sealed under RL-179 row 12 and in no fit or count under RL-180 row 9.
The first run owes the F-3 (c) hand-read. [Earlier pin's hand-read template](../../desk-cq-dev-04-s01-a1/hand/hand_table.py).

Queue expiry **2026-11-24T12:43:05-08:00**.

| Kit | One-leg drafts | Queue | Queue SHA-256 |
| --- | --- | --- | --- |
| [f2-stab-15](f2-stab-15.v1.1.json) | [items](items/ITEM-f2-stab-15.md) | [queue](queues/f2-stab-15.json) | `95d068dcbe20e49dc3abd0fe927762be491801d306f2dd4e40269141fe8d22cf` |
| [f2-stab-16](f2-stab-16.v1.1.json) | [items](items/ITEM-f2-stab-16.md) | [queue](queues/f2-stab-16.json) | `da1aacc285c75943dd77fa24aa51981c8160cee9b542f816f6804e4b685ed49c` |

## Issue template on this pin

Use the [shared issue template](../ISSUE.md) with the selected item's pin and the filled queue above.
The pin's own `validate-kit --repo` verifies the staged kit. The builder records the separate RL-180 cell comparison.
The pin defaults to no batch window. Its plan prints `launch_deadline_epoch_s` in place of the legacy fence field.
The synthetic plans give a work bound of 5,850 s and a minimum launch budget of 8,360 s including retry and cleanup.
Carry the shared template's 900 s margin over the pinned minimum and use that total for the dated-block census.

Regenerate from the audit checkout root with `MERGED_PIN` set to the locally available merged runner SHA.

`python3.13 -I -B docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/f2-stab/tools/build_qual_pin_kits.py --pin "$MERGED_PIN"`

[Synthetic verification](VERIFICATION.json)
