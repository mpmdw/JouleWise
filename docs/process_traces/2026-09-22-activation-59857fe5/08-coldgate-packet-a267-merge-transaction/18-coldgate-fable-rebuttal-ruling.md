# 18 — Cold Fable rebuttal ruling (charter §5 bounded post-seal round) on charge 17

Judge: fresh Fable 5.1 session, worktree `JouleWise-wt-coldgate-59857fe5-r2` at `6ecba15a`, 12:35–12:40 PDT 2026-09-22. Foreground only; no subagents; read-only except this file.

## 0. Trust anchors and disclosure

- Charter `docs/process/coldgate_charter.md`: expected `099de884…c95d81`, observed `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` (`shasum -a 256`). MATCH.
- Charge `17-rebuttal-charge-carried-items.md`: expected `1ccd3333…fbb30`, observed `1ccd33332973ee6a538ead6f0a4704ae30d5e0a0f041c8e9910ebf87839fbb30`. MATCH.
- Auto-loaded before I acted (not read, not used): `~/.claude/CLAUDE.md`, repo `CLAUDE.md`, memory index `MEMORY.md`. Read set: charter, charge, ruling 10 §Q3/§Q5, synthesis 15 (Q3/Q5 rows), records 13a/13b, `git show 56ea8ae0:` for `joulewise/quiet_predicate_campaign.py` and `tests/test_quiet_predicate_campaign.py`, `489b0953` for one counterfactual.
- Optional test run: NOT EXECUTED. `/Users/edr/code/JouleWise-wt-a267-review2` is at `3e299b85`, not `56ea8ae0`, so the charge forbids the run.

## 1. Charge citations verified at `56ea8ae0`

- `:766` `temporary.unlink(missing_ok=True)` is the first statement of `except OSError` (`:753`), before `:767-768` set `asserted`/reason. Confirmed.
- `:1168` `record_attestation(out, attestation)` unguarded inside `execute`; outer `except (OSError, ValueError, …)` at `:1179` sets `error` → night refused. `PermissionError` is an `OSError`, so 13b SHOULD-FIX 2's path is real. Confirmed by reading; 13b executed it.
- `:603` `ATTESTATION_TIMEOUT_FLOOR_S = 5`, `:1042` `CLEANUP_BUDGET_RESERVE_S = 5`, `:1048` `max(1, gap − RESERVE)`, `:638` `max(FLOOR, gap − cleanup_budget_s)`. Own probe (python3, gaps 1…1399): the set of returned values is `{5}`. SHOULD-FIX 1 confirmed.
- Schedule is absolute: `:1115` `scheduled = first + (index−1)·pitch`; abort at `:1129` when `drift > start_drift_abort_s`, envelopes ≥ 2.
- Syslog fixtures at `56ea8ae0`: `dba7fb7c…eb63`, `da1b28ef…718b` (own shasum), matching 13b NIT 6.

## 2. Rulings

### Q1 (C1) — AFFIRM the lead's (a), with the handler text amended below. MATERIAL.

(b) REJECTED: broader than the defect, masks programming errors, and would still leave the stale claim-bearing `.tmp` beside the record. (c) REJECTED: leaves a refusal path the ruled cure introduced (absent at `489b0953`).

Exact replacement for `:753-769` (comment block kept; body replaced):

```python
    except OSError as exc:
        # (existing comment, then:) The withdrawal comes FIRST: nothing below
        # may raise before the envelope has lost its claim-bearing state.
        attestation["state"] = "asserted"
        attestation["reason"] = f"session rewrite failed: {type(exc).__name__}: {exc}"
        # A landed write and a failed rename leave a COMPLETE session.json.tmp
        # carrying the state just withdrawn; remove it, and if that fails too,
        # say so in the reason rather than refuse the night.
        try:
            temporary.unlink(missing_ok=True)
        except OSError as unlink_exc:
            attestation["reason"] += (f"; stale {temporary.name} not removed: "
                                      f"{type(unlink_exc).__name__}: {unlink_exc}")
        return False
```

Regression R-C1 (unit, on `record_attestation` with a real `session.json` in a tmp dir): `patch.object(campaign.os, "replace", side_effect=OSError("disk full"))` and `patch.object(Path, "unlink", side_effect=PermissionError("immutable"))`; assert the call returns `False` without raising, `state == "asserted"`, `"session rewrite failed" in reason`, `"not removed" in reason`, and `session.json` bytes unchanged. Counterfactual at `56ea8ae0` (executed by 13b, confirmed by reading `:766`): `PermissionError` escapes and `state` stays `authenticated`. The ruled R5.2 `.tmp`-absent assertion stays on the replace-raises-only variant.

### Q2 (C2) — AFFIRM the lead's (a), strengthened to a two-point pin. MATERIAL.

`cleanup_budget_s` reads the module global at call time (`:1048`), so `patch.object(campaign, "CLEANUP_BUDGET_RESERVE_S", 10)` reaches it. Under that patch assert BOTH: `attestation_timeout_s(PROTOCOL) == 10` (gap 20) AND `attestation_timeout_s({**PROTOCOL, "slot_pitch_s": 603}) == 5` (gap 3). Own probe: `[10, 5]`. The single-point pin kills `return FLOOR` only; the pair also kills `return CLEANUP_BUDGET_RESERVE_S`, `return max(FLOOR, RESERVE)`, and the unfloored `gap − cleanup_budget_s` (gives 2 at gap 3). Execute the `return ATTESTATION_TIMEOUT_FLOOR_S` swap as the kill. (b) and (c) rejected as the lead argues; (c) additionally would delete the only thing Q2's pin protects.

### Q3 (C3–C6)

- **C3 — AMEND. MATERIAL.** "Detected by the drift abort" is not generally true at the next spawn: per-slot overrun is `6 − gap` and only accumulates because the schedule is absolute (`:1115`), so at gap 5 with a 2 s bar the first late spawn is 1 s late and passes; detection arrives only after enough slots compound. The regression must (i) use a gap with `6 − gap > start_drift_abort_s` (gap 3 with the SCALED bar of 2, `test:985-986`, matches the existing pitch-603 negative pin at `test:1409-1416`) under a faked monotonic clock in which teardown and query each spend their whole floor, and assert the `start_drift_abort` journal row and REFUSED outcome at the FIRST eligible spawn; and (ii) rewrite `:628-634` to say the overrun accumulates across slots and is detected when the accumulated drift exceeds `start_drift_abort_s`, not "the spawn then drifts past". Replace `assertIn("start_drift_abort_s", PROTOCOL)` at `test:1416` with that regression.
- **C4 — AFFIRM, form fixed. NIT.** `test:1548` becomes `for v in summary["envelopes"]: self.assertIn("network_time_unattested", v["excluded"])` — membership, not equality, because the test's own comment (`test:1545-1547`) says the summary also prints the lost-interior exclusion.
- **C5 — AFFIRM. NIT.** Delete the clause at the fold paragraph's "`log show` is handed the same strings … agree either way" (`:476-478` per 13a; docstring shown at `timed_log_window_epoch_s`); state that how `log show` resolves a fold-ambiguous string is not established.
- **C6 — AFFIRM. NIT.** `SOURCES.md` gains both syslog fixtures with the digests above, their archive source paths, and line counts.

## 3. Findings outside the charge (not ruled; carry as C7/C8)

- **C7 NIT:** on a failed rewrite the amended reason lives only in memory; the envelope journal row (`:1169-1173`) carries `state` but no reason, and `session.json` is unchanged, so no durable record says why. Add `network_time_attestation_reason` to the row.
- **C8 NIT (pre-existing at `489b0953:702`):** `json.loads` accepts `NaN` and `json.dumps(allow_nan=False)` at `:751` then raises `ValueError`, which `except OSError` does not catch; a collector-written NaN refuses the night via `:1179`. Not delta-introduced; same class as C1.

## 4. Packet hygiene and §9

Charge 17 is complete and neutral for Q1–Q3: options labelled, lead's disposition marked as argument, both records cited with executed evidence. No defect found. Charter §9: this round amends this gate's own ruled cure text for §Q5 item 2 and adds pins under §Q3; no prior gate's verdict is reinterpreted, and ruling 10's Q3 expression at `:638` stands unchanged. Two-rounds-same-signature: not present (C1 is a defect of the ruled text, not a repeat of round 1's).

Tier summary: MATERIAL ×3 (Q1, Q2, C3), NIT ×5 (C4, C5, C6, C7, C8), BLOCKER none.
