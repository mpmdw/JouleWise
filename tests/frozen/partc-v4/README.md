# Part C frozen suite v4 (PR #809, RL-215)

`suite-v4/` is the issued Part C v4 suite, copied byte for byte from the issuing seat's
`astra-partc-invariants-v4-1123/out/suite-v4` (the issuer's `__pycache__` left out). `SUITE-v4.sha256` is the
issuer's digest list as the lead re-recorded it under RL-215 Q3 and Q5 (`legacy/normalized_v32.py` is
`4824c536…f740`). Nothing under `suite-v4/` is edited here; check it before every run:

```sh
cd tests/frozen/partc-v4 && shasum -a 256 -c SUITE-v4.sha256
```

What it holds:

- `cases-v4.tsv`: the 1,550 v4 obligations (1,472 generated, 78 named history), SHA-256 `dcc4428a…2967`.
- `tests/align/test_partc_writer_v4.py`: the writer-produced v4 control and the 1,472 generated cases, each run
  natively and as an archive replay. `JW_V4_PROOF=1` runs only the writer clean proof (62, 62, 82, 62, 62 battery
  rows for idle, predecessor, Step D, D_bank and X_G).
- `tests/align/partc_v4_history.py`: the 78 named audit reproductions on the v4 control (the cases of the
  retired `tests/align/partc_audit_probe.py`).
- `legacy/normalized_v32.py`: the 25,300 inherited v3.2 operands applied to the v4 control. The 40 IDs in
  `legacy/operand-rulings.tsv` print `INAPPLICABLE` and are not counted (RL-215 Q3); parity differences print and
  block nothing (Q5). `legacy/issued_v32.py` is the v3.2 module itself, byte-identical to
  `tests/align/test_partc_frozen_differential.py` (the committed baseline, no longer a gate: RL-215 Q1).

Run from this directory with the candidate checkout and an object database holding both pinned commits
(`b2e01464d`, the R1 writer, and `2d02a6f0e`, the fixture):

```sh
export JW_PARTC_REPO="$(git rev-parse --show-toplevel)"
python3.13 -IB suite-v4/tests/align/test_partc_writer_v4.py      # JW_PARTC_SHARD=i/n, JW_PARTC_CASE=regex
python3.13 -IB suite-v4/tests/align/partc_v4_history.py
python3.13 -IB suite-v4/legacy/normalized_v32.py
```

Hosted CI runs all three in sixteen shards with pinned counts and the clean proof
(`.github/workflows/partc-frozen-differential.yml`). The repo-side checks built on this control are
`tests/align/partc_rl215_checks.py` (RL-215 Q2's outer-row cases and the planted-marker test),
`tests/align/partc_derived_sweep.py` and `tests/align/partc_domain_sweep.py`, run from
`tests/test_part_c_evidence_ledger.py`.
