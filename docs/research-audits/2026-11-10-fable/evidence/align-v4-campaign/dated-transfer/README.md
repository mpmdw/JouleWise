# DRAFT · RL-181 dated transfer block

Hold for effective freeze 2. Twenty possible date places, each with one
six-leg span and its own kit, queue and item. The [date-place roster](date-place-roster.json)
binds every artifact and pinned plan. No dates or issues are assigned.
The existing 132-leg campaign ceiling and its allocations remain in force.

[RL-181 §§3 and 4(a)](../../RESEARCH-LEAD-DECISIONS.md#3-the-transfer-block)
governs the page amendments, including the midnight clause. RL-180 row 10
closed when Fable confirmed the design was blind. Read [Issue and Check](ISSUE.md)
for the operator gates and [the look draft](looks/lm-transfer-01.json) for Fable's cold pass.
The [draft ledger row](looks/LOOKS.json) records the proposed registered destination.

The generator uses the pinned qualification law with one span. It starts the
seed search at 2026111800 for each kit and skips used master seeds and any
candidate whose leg seeds collide. It checks the planned family by decode
caps, since both ratios use p1. The first leg captures and the other five
consume. The four-place order cycle retains its ordinal even after a miss.
The [pinned-plan date](build_kits.py) is synthetic and supplies timing only.
The plan estimates govern contention.

The closed v1 queue format requires a finite expiry and has no date-authority
fields. Every draft uses a deliberately expired timestamp and an explicit
halt. The issued item will carry the date bounds and predecessor proof,
and the lead will commit a fresh single-span queue with the actual date.

## NEEDS_SPEC

- RL-181 §3.2 substitutes a crossing window's actual close date. §3.1 and
  register row 13 end the opportunity at the series' last W1/C/T t0-date.
  Confirm whether the substitute survives that cutoff for the series' last
  window if a place remains. The draft date checker refuses that case.
- RL-181 §2.1 names only qualification and description variants of v2.
  The named pinned look tool has only v1 and cannot validate transfer.
  Confirm where the closed transfer variant and final preflight dispatch
  belong. The audit-only transfer shape and ledger are submitted for the
  cold pass. The scorer, stage-1 implementation, final schema pins and
  execution host are pending their owners' registration and admission.

## Reproduce

Use a private external seat directory. These commands open only tracked
source and draft bytes or create synthetic inputs.

```sh
T=docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/dated-transfer
python3.13 -B "$T/build_kits.py" validate-kit --seat-dir "$SEAT_DIR"
python3.13 -B "$T/validate_look.py" validate
python3.13 -B -m unittest discover -s "$T/tests"
python3.13 -B "$T/build_kits.py" mock --seat-dir "$SEAT_DIR"
```
