# DRAFT · RL-181 dated transfer block

Hold for effective freeze 2. Twenty possible date places, each with one
six-leg span and its own kit, queue and item. The [date-place roster](date-place-roster.json)
binds every artifact and pinned plan. No dates or issues are assigned.
The existing 132-leg campaign ceiling and its allocations remain in force.

[RL-181 §§3 and 4(a)](../../RESEARCH-LEAD-DECISIONS.md#3-the-transfer-block)
and [RL-183 §3](https://github.com/mpmdw/JouleWise/blob/d7c436930ec1a3a29b262990837e6154058b5add/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#31-the-last-windows-close-date-eligible)
govern the page amendments. RL-180 row 10
closed when Fable confirmed the design was blind. Read [Issue and Check](ISSUE.md)
for the operator gates and [the look draft](looks/lm-transfer-01.json) for Fable's cold pass.
The [draft ledger row](looks/LOOKS.json) records the proposed registered destination.

The generator uses the pinned qualification law with one span. It starts the
seed search at 2026111800 for each kit and skips used master seeds and any
candidate whose leg seeds collide. It checks the planned family by decode
caps, since both ratios use p1. The first leg captures and the other five
consume. The four-place order cycle retains its ordinal even after a miss.
The [pinned-plan date](https://github.com/mpmdw/JouleWise/blob/4e5c2ad1d6a1dec2ebb0d39620fdc5b4cc3a79c5/docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/dated-transfer/build_kits.py) is synthetic and supplies timing only.
The plan estimates govern contention.

The closed v1 queue format requires a finite expiry and has no date-authority
fields. Every draft uses a deliberately expired timestamp and an explicit
halt. The issued item will carry the date bounds and predecessor proof,
and the lead will commit a fresh single-span queue with the actual date.

## Final window and look validation

The final window's close date replaces its t0-date if it holds the host
past midnight and no transfer span started on the t0-date. Place 20 can
therefore move to the close date. A transfer t0 on the original date
uses the opportunity once. If the substitute date expires unused, the
date map gives that place the missed disposition.

The closed v2 transfer variant and the new dispatch module validate the
draft. Final transfer validation requires the exact registered bytes and
allows changes only in the code hash slots. `scores.json`, `stdout` and
`stderr` are the closed private success inventory. A pre-read refusal
exits 2. A handled post-read failure exits 1 after the two-line notice.
Synthetic worker tests exercise publication, confinement through process
shutdown, and exclusive reservation. The look stays a draft for Fable.
Final admission includes wiring the authenticated caller and scorer to
the boundary and pinning the shared freeze-2 reader, execution host and
stage-1 inputs.

## Reproduce

Run these commands from the audited transfer checkout at
`4e5c2ad1d6a1dec2ebb0d39620fdc5b4cc3a79c5`, which holds the draft
generation and verification tools. Use a private external seat
directory for synthetic inputs.
[Audited source](https://github.com/mpmdw/JouleWise/tree/4e5c2ad1d6a1dec2ebb0d39620fdc5b4cc3a79c5)

```sh
T=docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/dated-transfer
python3.13 -B "$T/build_kits.py" validate-kit --seat-dir "$SEAT_DIR"
python3.13 -B "$T/validate_look.py" validate
python3.13 -B -m joulewise.cadence_looks.manifest_dispatch validate "$T/looks/lm-transfer-01.json"
TMPDIR="$SEAT_DIR" python3.13 -B -m unittest tests.test_cadence_manifest_dispatch tests.test_cadence_transfer_release
python3.13 -B -m unittest discover -s "$T/tests"
python3.13 -B "$T/build_kits.py" mock --seat-dir "$SEAT_DIR"
```

For a final candidate, use the new module's `validate CANDIDATE --final
--registration REGISTERED`, with the trusted registration bytes from main.
