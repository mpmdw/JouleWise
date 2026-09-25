# ex-06 — verbatim R16-a text with source and context

Source: `docs/process_traces/2026-09-25-activation-152c9255/24-finalpass-packet-prl/20-fable-final-pass-prl.md` (tracked on branch docs/2026-09-25-152c9255), file sha256 `98621b0621e3f24bd04f5b190fbfadda595ff74d3b8c846b39574df0e26382c3`, rule text at line 42; lines 34–48 quoted below verbatim (context ≥ 5 lines each side).

```
## 2. L2 — the magistrate's provisional T0_REHEARSAL reading

**Verdict: AFFIRM**, with the rule text below (the charge asks for text; adopt it verbatim as the durable rule so nothing rests on a narrative record).

Deciding evidence (code, not the reviews): `night_gate.py:1248-1260` grants the exemption only if `receipt_class == "TRANSACTION_PACK"`, `pack_night is not None`, and `_pack_object(path, "authorization_record", sha256)` returns a mapping whose `purpose == "T0_REHEARSAL"`. `_pack_object` → `_pack_bytes` refuses non-absolute or symlinked paths and any digest mismatch (`sha256 mismatch`), so an unauthenticated or tampered record cannot exempt. The plan parser already requires `pack_night.authorization_record` to have exactly `{path, sha256}`, absolute, inside custody (`:484-505`), so the exemption branch cannot raise an uncaught KeyError. Disjointness survives the exemption: `evaluate_night` → `_evaluate_pack_conditions` → `_authenticate_pack_records` re-reads the same record under the same digest and requires `claim_eligible == False` for any non-CAMPAIGN purpose (`:988-989`), then `_pack_rehearsal_roots` requires the rehearsal window-id prefix, refuses containment against every production custody root (`rehearsal_roots_not_disjoint: measurement_root`), and requires the rehearsal clone prefix. Quiet-admission plans are packless by construction (`:1793`), so they never reach the exemption. Tests executed here and passing: `test_new_pack_rehearsal_exempts_only_authenticated_t0_purpose`, `test_pack_rehearsal_exemption_requires_real_authorization_digest` (real file, correct sha → R16 skipped and plan still refused later; `0`*64 → `measurement_root_outside_custody`), and the end-to-end `test_post_cutoff_t0_inside_measurement_custody_refuses_disjointness_end_to_end` in `test_run_night` (driver exits REFUSED, no launch calls, no go_receipt, detail `rehearsal_roots_not_disjoint: measurement_root`). This is both directions.

**Rule text (adopt verbatim as R16 addendum R16-a):**

> R16-a. The `measurement_root_outside_custody` refusal does not apply to a plan authored at or after epoch 1790340000 when all of the following hold: (a) its `receipt_class` is `TRANSACTION_PACK` and `pack_night` is present; (b) the bytes at `pack_night.authorization_record.path` hash to `pack_night.authorization_record.sha256`; (c) that record's `purpose` is exactly `T0_REHEARSAL`. If the record is missing, symlinked, mismatched, or not a JSON object, the exemption is forfeited and R16 applies. The exemption removes only R16. The T0 rehearsal rules continue to apply unchanged: rehearsal window-id prefix, `rehearsal_roots_not_disjoint` against every production custody root including `/Users/edr/night-custody/measurement`, rehearsal clone prefix, and `claim_eligible = false`; an exempted plan therefore cannot produce a claim-eligible measurement. No other purpose, no packless plan, and no quiet-admission plan receives the exemption.

## 3. L3 — tests run by the judge

All in `/tmp/coldgate-prl-judge` at `99495ba9`; no sudo, launchctl or real powermetrics (the fixtures shim `sudo` to a fake 300-frame emitter); foreground; `tests.test_night_agent_install` split into three class slices to fit the per-command limit.

| Modules | Result |
```
