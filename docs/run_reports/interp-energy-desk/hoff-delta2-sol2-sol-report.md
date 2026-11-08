**HOLD.** Three remaining closure findings:

- **HIGH:** Production CLI admits unbound ignored content beneath `runs/`.
- **HIGH:** Symlink-parent plus `..` resolution binds the wrong file.
- **MEDIUM:** External aliases ending inside the session escape closure binding.

Committed `dfcfae314` on `align/2026-11-08-hoff-delta2-sol2`. Working tree is clean; no push.

Changed files: [report](docs/align/v4/HARVEST-OFF-DELTA2-sol2.md) and [witnesses](tests/align/test_hoff_delta2_sol2.py).

Verification: 89 existing targeted tests passed, including exact equality of all 177 archive files, memo behavior and dwell ordering. `python3.13 -B -m unittest -v tests.align.test_hoff_delta2_sol2` produced seven passes and four failures demonstrating the findings. Total test time was about 6.5 minutes.

The orphan census was unavailable because the sandbox denied `ps`. Native N1/N2, RSS/finalize timing and live quiet-dwell checks remain lead-owned.

Next: fix the three closure gaps and replay the four failing assertions plus the honest CLI control.