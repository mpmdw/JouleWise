# Part C one-shot handoff

**DRAFT / INELIGIBLE.** The lead issues this handoff to the magistrate for
one native Part C on one changed W1-line pin. The registered smoke starts
with a fresh TV0h/TV1h soak and runs Part C only. It is diagnostic and
produces no slots or counted span. A successful Check supplies the
new-pin smoke evidence for W1's separate READY record.

```pointer
owner: magistrate
wait: UNFILLED (R1 post-close Check, latest proven clean close and lawful native interval)
deadline: UNFILLED (issued deadline, if applicable, from the pinned route)
on_early_or_refused: record the disposition, preserve the evidence and select the next eligible entry under the current ladder and stop scope
next_observable: one-shot launch record, then the terminal receipt, restore readback, automatic desk result and independent first-pin read
```

## Lead fills before issue

| Field | Fill |
|---|---|
| Typed header | `schema` `joulewise.run_state_item.v1`, `owner` `magistrate`, `status` `DRAFT`. `number`, `issued_epoch_s`, `expires_epoch_s`, `supersedes` and `sets` all UNFILLED. |
| Issuing lead and authority item | UNFILLED |
| Prior issued W1-line SHA (full) | UNFILLED |
| One new issued W1-line SHA (full) | UNFILLED |
| Promotion record and clean checkout/tree verification for that new SHA | UNFILLED |
| Registered fresh-soak/Part C route and kit pointers at the new SHA | UNFILLED |
| Final candidate's synthetic launch-to-close CI result and tested SHA | UNFILLED |
| Condition-13 and Part C executed-source check, including disposition for any differences | UNFILLED |
| Authorized independent first-pin reader and hand-read template pointer | UNFILLED |
| R1 post-close Check and retirement of standing F0 | UNFILLED |
| Permitted predecessor, latest attempted predecessor's close proof and native interval | UNFILLED |
| Expected duration, planned start and worst-case end from the pinned route | UNFILLED |

The new SHA must differ from the prior SHA. Record the first native run
on the new pin under this handoff. A prior pin's Part C or F0 evidence
cannot discharge this run. A refusal or terminal result closes this
handoff's authority. Any further run on the same SHA needs separate
authority.

## Magistrate records launch and Check

| Observation | Evidence pointer or disposition |
|---|---|
| Pre-launch readback of the latest attempted predecessor's receipt, restore, stopped feeds, absent fence and process group, and absence of foreign processes or applicable stops | UNFILLED |
| Actual launch record and observed checkout SHA | UNFILLED |
| Terminal receipt and clean-close Check, including soak and Part C completion | UNFILLED |
| Restore readback, stopped feeds, fence and process-group absence | UNFILLED |
| Automatic desk report at the issued SHA and verdict | UNFILLED |
| Step D, D_bank and X_G/G1 reconciliation and verdict | UNFILLED |
| Independent first-pin hand-read, reader, exact SHA and verdict | UNFILLED |
| Final disposition and lead's evidence pointer for the separate W1 record | UNFILLED |

Close as successful only with the registered automatic desk PASS, the
independent read passing, reconciled Step D, D_bank and X_G/G1, and
proven terminal close and restoration on the new SHA.

## Refusal or non-pass

| Field | Fill |
|---|---|
| Refusal or non-pass record, reason and applicable stop scope | UNFILLED |
| Next eligible filler, its authority and date fit, or the reason no eligible entry can arm | UNFILLED |

At a refusal, return selection to the current ladder immediately. An
applicable host-wide stop still holds the host. After R1's post-close
Check, take the first lawful rung from the first `f2-stab` leg of the
local date, remaining `f2-inst-01` then `-02` and `-03`, `hp-02` if
`lm-hp-01` has yet to run, then further `f2-stab` legs. Counted work
retains its priority and date protection.

[Registered Part C shape (RL-155 §3.1)](https://github.com/mpmdw/JouleWise/blob/f9b03c33d/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L14206-L14214) ·
[First-pin read, one-shot Part C and filler ladder (RL-179 F-3/F-4)](https://github.com/mpmdw/JouleWise/blob/f9b03c33d/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L18699-L18742) ·
[Synthetic CI and first native smoke (RL-179 F-11)](https://github.com/mpmdw/JouleWise/blob/f9b03c33d/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L18836-L18844)
