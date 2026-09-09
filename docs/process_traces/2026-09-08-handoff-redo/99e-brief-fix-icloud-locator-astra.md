WRITE_SCOPE: ["joulewise/calibration_ledger.py","joulewise/calibration_bracketing.py","tests/test_calibration_ledger_custody.py","tests/test_calibration_bracketing.py","docs/contracts/calibration_ledger_append.md","docs/paper/round7/fill-checklist.md","docs/guides/tutorial-replicate-the-calibration-bound.md"]

# Fix-round brief — ICLOUD-CUSTODY-LOCATOR-01, Opus contract-refuter findings (gpt-6-astra, medium)
HEAD = 42b0d235 (part 3). Astra execution refuter: clean. Opus contract refuter (trace 93): LAND-WITH-FIXES, verbatim:
SF-1 `joulewise/calibration_ledger.py:4766, :5218, :1781` — a timed-out probe is indistinguishable from genuine
absence in every receipt and log; the outcome silently becomes `RefusalCode.CUSTODY_PARTIAL` or
`calibration_ledger_custody_invalid`, whose registry rows read as ledger CORRUPTION. Cure: emit a distinguishable
`custody_locator_unreachable reason=timeout|exception locator=… budget_s=…` stderr line (the sibling landing's
`backup_root_unavailable` shape) at the probe site, WITHOUT changing the decision/state (absent-equivalence stays;
the Astra refuter's 16 comparisons must still hold); add the reason to any structured log the entry point already
writes if one exists (do not add new receipt fields).
SF-2 `:4720-4736` — `probe_custody` docstring must name the responsive-but-slow case (> 2 s on exists/is_dir →
reported absent while the tree is complete) as the sibling design's addendum does.
SF-3 — document the ledger-side `JOULEWISE_BACKUP_ROOTS` semantics (lexical root replacement; empty = treat
backup-rooted locators absent without probing) and `CUSTODY_PROBE_TIMEOUT_S` in docs/contracts/calibration_ledger_append.md
(dated addendum) and, by one dated line each, in the fill checklist and the calibration-bound tutorial.
SF-4 `:4677-4680`; `scripts/validate_powermetrics_fiducial.py:1425,1455` — `artifact_hashes()` now honours the
override, so with a NON-EMPTY override a MINTING path hashes bytes at the mapped root while the caller records the
ORIGINAL locator: a receipt claiming locator L with digests of bytes at M. Cure: on any minting/issuing path, an
active non-empty override REFUSES with a named reason before hashing (or the override is ignored for minting and
honoured only for read/replay paths — choose the option that keeps evidence fail-closed and say why); regression:
non-empty override + mint → refusal; empty override → unchanged behaviour.
N-1 move `artifact_hashes` and `_assert_absolute_nonsymlink_directory` wrappers back adjacent to their bodies (the
"line-pinned sentinel" they were moved for does not exist). N-2 add `probe_custody` to `__all__`. N-4 replace the
self-declared constant test with a behavioural assertion or delete it.
Acceptance = `tests.test_calibration_ledger_custody tests.test_calibration_bracketing tests.test_calibration_ledger
tests.test_authentication_io` to a log with rc; never touch the real iCloud path; never the repository-wide suite;
no `git commit`; header < 8192 bytes; genre implementation verdict keys; body = per-finding cure, counterfactual,
fail-before/pass-after tails.
