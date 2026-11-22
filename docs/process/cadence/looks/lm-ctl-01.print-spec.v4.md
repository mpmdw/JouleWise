# lm-ctl-01 synthetic print specification, revision 4

PR #853 returns to spec under PIPELINE §3 because round three verified two
HIGH findings. The audit sequence ends at round three. This revision
freezes the episode and U1 acceptance invariants for the next build.
Revision 3, the instrument look-time parameters, and the lead-approved
v3.1 suite continue to govern the other controls-print checks.

## Episode provenance

The source freeze `860eb6b` requires a receipt-backed kit, runner, span,
leg, and attempt join. RL-187 §3.1 permits the visible-call projection
after authentication of the logged envelope and physical record. Apply
that join to the episode and its trace inputs before dispatch to the
scientific print.

1. The committed controls roster binds the terminal provenance for each
   eligible episode to the same kit ID, issued kit digest, runner commit,
   span, leg ID, and attempt used for `script-work.json`. Resolve the
   expected evidence from the committed roster and its closed receipt.
   A matching episode label, claimed attempt, or matching script digest
   alone supplies insufficient evidence about the episode bytes.
2. Before reservation, verify the blind bindings and existence and
   identity of their receipt commitments. Inside the reserved stage-2
   read, verify the actual payload against the authenticated artifact
   commitment and use the episode decoded from those bytes. The episode
   and input traces used for attribution must belong to that member.
   Verify the joined inputs before dispatch to the phase code or
   qualifier. Use the inherited post-open failure boundary if a returned
   object fails its committed identity check. The existing dispositions
   for explicitly unrun or excluded positions still apply.
3. The synthetic restart can use invented byte commitments. At operational
   freeze, pin the exact closed receipt field and episode artifact source
   admitted with the runner. The PR #808 draft points to
   `outputs/align_episode.json` in its member-bundle reader. That source
   reference identifies an artifact type and path. The closed receipt
   establishes the binding to the issued attempt.

## Registered U1

Derive U1 from the registered cadence and verified sample-support metadata
bound to the same attempt and channel. Use the registered rail gap limit
`max(1 s, 5 × nominal period)` (RL-166 Q7 and its registered U1 source).
Use the registered 2 s DC-in/sidecar gap limit where applicable. For a
registered mixed-cadence interval, compare each rail gap part against
its own segment limit when that rule is admitted for the input. The
registered evaluator or an equality-tested copy supplies the comparison.

The worker resolves its own limits. A map supplied by a caller cannot
override the registered cadence. The next freeze pins the cadence
evidence source, including the interval/transition information needed by
the admitted U1 evaluator. Refuse a missing, contradictory, or unpinned
cadence binding when required for the read. RL-197a §4 retains its exact
window, reason precedence, and per-channel null behavior. A rail gap
strictly over U1 in the baseline window makes both that above-baseline
energy and its floor units null. The absolute table remains available
under the existing rule.

## Failed-first acceptance

Run the added checks from the checkout with one worker.

```sh
python3 -B -m unittest -v tests.contracts.cadence_looks.ctl_print_binding_acceptance
```

| Invented worker input | Expected result at restart |
| --- | --- |
| Swap L002 and L005 episode payloads while preserving the exact two committed script digests. Repeat with each foreign episode relabelled to match the intended position. | Both substitutions fail after the first read and before analysis. Status 1, inherited two-line notice and zero public writes. The blocked head instead prints L002 at 6 J and `qualified: yes`. The audit's matched control prints 14 J. |
| Identical qualified gapped L002 GPU trace in two invocations. Registered 1 Hz means 5 s U1. Samples at 99 and 105 s bound the 6 s gap in the final recovery window. The stale caller presents 10 s in the second invocation. | Both print `gap_over_u1` with null baseline, hidden above-baseline joules and floor units. The public bytes match. The blocked head prints 3 W, 14 J and 7.0 floor units with the stale limit. |

The two worker checks stay explicit at this freeze. Bind their invented
receipt and cadence inputs to the implemented verifier when the build
resumes. Add stale-attempt and changed-episode-bytes cases to that
interface, and check a gap exactly at the registered limit, one tick
above it, and a gap outside the relevant window. The frozen v3.1
inventory still contains the original 846 cases. The shared dispatcher
route remains a separate integration follow-up.
