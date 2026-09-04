# Floor workload sizing

Status: scoped design for `FLOOR-WORKLOAD-SIZING-01`; production selection
remains governed by D-166 and live evidence remains pending.

## Forcing problem

An attribution-limited floor is a detection floor widened by uncertainty in
where phase boundaries fall on the power trace. D-078 records that this
uncertainty is approximately independent of phase duration, while the energy
effect of interest can grow with workload. A longer prompt-processing
(`prefill`) or token-generation (`decode`) phase can therefore provide a
larger measured effect without changing the instrument.

Two denominators must remain distinct. The **operative floor** is the widened
floor published for the measurement cell. The **effective clearable effect**
is the operative floor plus the claim-side measurement bound. D-083 rules that
the second quantity is a disclosure obligation, not a new acceptance gate.
`joulewise.workload_sizing.measured_margin_ratios` reports both descriptive
ratios and emits no verdict.

## Later authority and present stage decision

D-166 superseded the earlier idea that this row could choose production sizes
directly. For the Qwen3 `_v5` campaign:

- Every decode stage generates the forced budget of 512 tokens from the
  pinned real prompts.
- Every prefill stage uses one common prompt length selected from the G2-a
  diagnostic ladder of 512, 1024, 2048, and 4096 prompt tokens.
- The prefill selector chooses the shortest rung for which at least five
  small-model members exist and every such member overlaps at least five
  power-sampling intervals. If no rung qualifies, it records a refusal and
  the ruled collection fallback is 4096 prompt tokens.
- G2-a is diagnostic and non-claim-bearing. Its large-model probes are
  retained but do not choose the rung. Its bytes cannot be promoted into a
  later floor or claim input.

These values and rules come from the D-166 ruling, its later amendment, and
the state-kernel acceptance and fences for `V5-G2A-PREFILL-PROBE-01` and
`V5-DESK-DAY-01`. The exact prefill size is not yet known because the live
G2-a record has not been issued. The frozen Qwen2.5 `_v3` packs must not be
rewritten; successor Qwen3 packs are generated only after the selection
record exists.

## Options for the older effect-to-floor acceptance

1. **Retire the row as superseded by D-166 (recommended).** Keep the ratio
   arithmetic as a reporting aid, but do not create another selection gate.
   This preserves the current pre-registration and avoids spending an extra
   quiet-machine window on evidence that cannot alter `_v5`.
2. **Keep a separate diagnostic margin study.** Pre-register paired
   conditions, candidate sizes, the effect estimand, the operative floor
   artifact for each candidate, and the claim-side bound source. Collect it
   after the claim-bearing transaction or in a separately authorized window.
   Report both ratios without changing the D-166 size.
3. **Amend D-166 so an energy ratio selects workload size.** This would need
   a new ruling that defines the effect, denominator, threshold, candidate
   set, and interaction with phase resolvability before any collection. It
   would also require newly generated packs and a new freeze. This option is
   not recommended because the current campaign already has a settled,
   mechanically implemented selector.

## Worked example

Let an issued pilot artifact provide a signed energy effect `E`, an issued
floor artifact provide the operative floor `F`, and the claim evidence provide
the claim-side bound `B`. The desk calculation is:

```text
effect-to-floor ratio = |E| / F
effective clearable effect = F + B
effect-to-effective-clearable ratio = |E| / (F + B)
```

The sign of `E` remains part of the scientific result; its magnitude is used
only for the two margins. Neither ratio selects a workload without an
additional ruling. The helper refuses a non-positive floor, a negative bound,
or a non-finite input, and it does not authenticate artifacts; the caller must
obtain all three values from issued, hash-bound evidence.

## Remaining evidence checklist

- Run the already queued, lead-owned G2-a quiet-machine window and preserve
  its pre/post calibration brackets, member bundles, count receipt, and
  four-rung summary unchanged.
- Run `scripts/select_g2a_prefill_length.py` on that summary and preserve the
  selection record and digest.
- Generate the three successor Qwen3 `_v5` packs only after the selection
  record exists; verify that all decode stages use the ruled forced budget and
  all prefill stages use the selected length.
- If the magistrate keeps a separate effect-to-floor study, issue its
  pre-registration before collection, then compute both ratios from the
  authenticated pilot, floor, and claim-bound artifacts.

## NEEDS_RULING

Question: should `FLOOR-WORKLOAD-SIZING-01` be retired as superseded by D-166,
or should it remain as a separate diagnostic margin study that cannot alter
the `_v5` workload?

Recommendation: retire it as superseded. If it remains, choose option 2 above
and separately rule the effect estimand, artifact bindings, candidate set, and
whether the study runs before or after the claim-bearing transaction. No
production configuration change is safe until that choice is recorded.
