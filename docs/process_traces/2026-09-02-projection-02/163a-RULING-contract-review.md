# Ruling 163a — terra 163 review of `docs/contracts/identity_pin_projection.md`

Magistrate: Fable, 2026-09-02. Findings in `out/163-terra-proj02-pedagogy.md`.

R-163-1 (P1, BLOCKER — ACCEPTED). The unprojected `identity_pin_projection`
envelope (eight keys, `mode`, `required_before_arm`, null pins/receipt,
supersession shape; `joulewise/identity_pins.py:79-96,474-548`) is added as
a new section before the current §3, with a minimal valid JSON example a
rebuilder can paste into `plan_tree.json` and freeze.

R-163-2 (F1, BLOCKER — ACCEPTED). The scientific-tag normalization is
stated as the exact executable predicates of `identity_pins.py:217-243`
(the two `analysis-replacement-*=` prefixes, the four exact calibration
prefixes, full-match `rep[0-9]+`, and that other `run_metadata` keys are
discarded when tags are normalized) — quote the predicates, not a paraphrase.

R-163-3 (P2, SHOULD-FIX — ACCEPTED). The worked example includes both raw
config files verbatim, the normalized identity JSON, and the eleven-field
stack JSON so that the two config digests, `config_set_sha256`, and
`runtime_identity_sha256` all recompute from the page; plus one non-happy
path beyond the token swap (one model byte changed → the new
`model_artifact_sha256` and the `readiness_identity_environment_dirty`
refusal at arm, with the real recomputed digest).

R-163-4 (T1, SHOULD-FIX — ACCEPTED). `tests/test_identity_pins.py:552-574`
gains an explicit sidecar assertion (sidecar bytes name the receipt file and
its SHA-256) and a mutated-sidecar refusal (one hex digit changed →
`verify_frozen_projection` / arm refuses with the named code; pack
otherwise untouched). Counterfactual input: a sidecar whose digest no
longer matches the receipt bytes; production site: the sidecar read in
`_load_frozen_receipt`.

R-163-5 (T2, SHOULD-FIX — REJECTED, recorded). A test pinning "launch does
not re-derive" would pin the exact boundary that ruling 150a R-150-2 orders
`V5-LAUNCH-REALIZATION-RECHECK-01` to move (re-derive after
`verify_consumed_launch`, before `RunBundleWriter.create`). The map row
stays as written; add one sentence that the boundary is scheduled to move
under that row.

R-163-6 (first-use table — ACCEPTED except line 1). The document title is
not a use; every other listed FAIL is cured by glossing at first use or by
moving the definition ahead of the use. Internal labels (U8/U11, ruling
44c/150a, D-119, "governed observation") are either glossed in plain words
at first use or moved into a closing "Provenance of these rules" note and
removed from the mechanism text. `STACK_IDENTITY_FIELDS`: list the eleven
fields in the document. `execve`: gloss as the point where the launcher
process replaces itself with the reviewed collection command.
