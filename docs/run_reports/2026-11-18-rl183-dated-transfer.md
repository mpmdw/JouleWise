# RL-183 dated transfer follow-up · 2026-11-18

[RL-183 §3](https://github.com/mpmdw/JouleWise/blob/d7c436930ec1a3a29b262990837e6154058b5add/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#31-the-last-windows-close-date-eligible)
settles both points in the [RL-181 draft report](2026-11-18-dated-transfer-drafts.md).
The target branch matched its remote at 42adff078 on intake. This
follow-up keeps all 20 planned spans in draft status, held for effective
freeze 2, scientific registration and dated issue.

The final window is treated like every other window. Its verified close
date replaces its t0-date after a midnight crossing if a transfer span
had not already started on the t0-date. There is no additional place.

The canonical v2 schema follows the qualification sibling at
6ffcb3c3d, where the registered manifest's v2 schema hash was still
pending. The qualification definition and its validator were carried
over verbatim. That sibling had only the qualification variant. The
description shape encodes RL-181's filler kit, channel and output
boundaries. Transfer has its own closed variant. The new
`joulewise.cadence_looks.manifest_dispatch` entry point routes by schema
ID. It delegates v1 to the original CLI and validates v2 here. Final
transfer validation compares the supplied trusted scientific
registration byte-for-byte, allowing only the code hash fills.

The transfer manifest binds the seven prints to `scores.json` and the
closed success directory also contains `stdout` and `stderr`. It declares
post-read failure exit 1 with the two-line notice, and its pre-read
validator returns exit 2 on refusal. The stage-2 scorer and execution
boundary remain due before final admission, including the shared
freeze-2 reader in RL-183 §2.3 and the type, once and failure tests at
the scoring entry point.

| Finding | Regression check | Result |
| --- | --- | --- |
| Final midnight crossing keeps place 20. | A 19-place fixture gives the final window one place on its verified close date. A t0 already taken on the original date precludes the substitution. | PASS |
| The v2 dispatcher enforces the ruled transfer contract. | Audit draft and ledger validation. Closed fields, ordered kit IDs, signed interval, destinations, both failure statuses, and exact hash-only finalization on generated inputs. The actual draft refuses final validation at exit 2. | PASS |
| Existing look layouts retain their routes. | Qualification registration and a generated hash-only final passed using the sibling's definitions and validator. Description closed-field fixtures passed. Pinned v1 direct and dispatched output matched, and the pinned v1 tool refused the v2 draft. | PASS |
| v1 schema pin. | The new suite checks the digest on an integrated tree. The audit tree has v1 on its separate line. Direct verification from the pinned v1 source gave SHA-256 5c0724bd39cb41d2a0e155de31b9930a850286d395213e658be3e0e0e231b723. | PASS on the pinned source |
| Draft content and synthetic span. | Re-validated all 20 pinned kit, queue, item and plan sets. The synthetic mock closed six legs with exit 0 and zero stops. | PASS |
| Queue and state projections. | Canonical generated-state check and focused generator tests passed. | PASS |
| Session-end fixture census. | Environment denied ps access, exit 2. | FAIL |

The targeted tests cover the desk-only validator, its sibling routing,
the draft scheduling rules and the unchanged pinned runner's synthetic
path. The full project suite was outside this tooling-only follow-up.
The first kit SHA-256 remains
`62188932ab4011804d72bdce2d65c144e748f7ac62e45f0ebf4b747a47dddd9f`.
The ordered roster SHA-256 is
`cc2a29a95a0028f78ce85aaf9b7a7dd7f019130ddf75dcf02bdb589cb13cf6f6`.

NEEDS_SPEC is clear for the two decisions. The next step is the lead's
scientific registration, then final scorer and schema pins and Fable's
cold pass on the final manifest before the terminal read.
