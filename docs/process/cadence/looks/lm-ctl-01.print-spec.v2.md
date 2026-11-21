# lm-ctl-01 synthetic print specification, revision 2

The source freeze at `860eb6bb920c09bb85f484e4162082288d8d9a0a`, RL-186 §2.3
and RL-187 §3.1 govern this revision. It closes the synthetic envelope
projection and its acceptance checks. The production release inventory
and freeze receipt remain with the existing cold-pass and lead gates.

## Envelope validation and projection

1. Validate the authenticated logged envelope against the visible physical
   calls before passing a leg to attribution, phase computation or the
   qualifier. The logged object has one logged turn with an exact Boolean
   `true` flag and empty tool calls. Its context, prefill and decode counts
   are exact nonnegative integers. Its `hidden_tokens` is an exact integer
   equal to zero. A nonzero count or wrong count type fails `envelope_counts`.
2. The visible physical calls supply the projected prompt count from the sum
   of their context counts and the projected decode count from the sum of
   their delivered counts. Check the projected prompt count against the
   logged context plus prefill and the projected decode count against the
   logged decode. Apply RL-187 §3.1's exact start and first-token checks
   with reason `envelope_stamps`.
3. A failed envelope check prints only the leg's identity, script kind,
   `not_evaluable` disposition and the fixed reason. Exclude the leg from
   attribution, phase computation and the qualifier. Keep the logged and
   physical input records intact.
4. An accepted leg's synthetic private `envelope` has exactly two keys,
   `prompt_tokens` and `decode_tokens`. Construct both integers from the
   validated visible physical calls. The scientific print uses explicit
   projections of approved fields. A source record, a generic object dump
   or an incidental new member of either source cannot supply extra print
   fields. The per-visible-call phase view and the authorized `calls`
   projection retain their separate roles.

## Failed-first acceptance

Run the following from the checkout:

```sh
python3 -B -m unittest -v tests.contracts.cadence_looks.ctl_print_disclosure_acceptance
```

| Case | Expected result |
| --- | --- |
| Native synthetic L010 CPU envelope round-tripped through the frozen record codec with hidden count 37 | `not_evaluable`, `envelope_counts` |
| In-memory L010 with each of `detected`, `K_outcome` and `S_score` in the logged hidden-count field | `not_evaluable`, `envelope_counts`, zero attribution and phase calls, zero members passed to the qualifier |
| Substituted booleans or nonintegral types and matching-sum noninteger visible counts | Same refusal before the phase path |
| Valid L010 with two visible 2,000-prompt, 512-decode calls | Accepted envelope equals `{"prompt_tokens":4000,"decode_tokens":1024}` |

The native codec case uses the pinned RL-176 source overlay until the
integration checkout contains it. This acceptance module stays outside
ordinary test discovery while the draft is blocked. The next build must
make it pass and move the cases into the discovered contract suite. Update
the shared-stamp regression to assert the closed envelope projection while
retaining its phase and qualifier routing checks. Keep the original frozen
fixture byte-identical.
