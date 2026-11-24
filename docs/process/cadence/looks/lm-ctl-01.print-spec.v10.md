# lm-ctl-01 pre-reservation specification, revision 10

The lead resolved the ancillary metadata boundary in revision 9. The commit
introducing this specification and its failing synthetic cases is the
revision 10 freeze. PR #957 remains draft.
[Revision 9](lm-ctl-01.print-spec.v9.md) · [PIPELINE §3](../../PIPELINE.md#3-tier-2-only-spec-freeze-and-convergence)

## Metadata

- The top-level metadata envelope is closed. Optional `extra` must be an
  object when present. The adapters envelope is closed and admits only
  `runtime` and `telemetry`. Either adapter may be absent. Both require a
  string `name` when present. Runtime also requires object
  `prepare_metadata`. Enforce the pinned writer's declared fields in these
  records even though their extension keys are allowed.
- Producer-defined keys in metadata are confined to `extra`,
  `adapters.runtime`, and `adapters.telemetry`. Where the pinned producer
  defines ancillary record keys and variants, enforce that inventory.
  An extension does not substitute for a declared field or permit a
  second spelling of a key.
- Validate extension values lexically under strict JSON with unique decoded
  keys, the existing depth limit, and the revision 9 numeric rules. Bind
  the original bytes by digest. Extension keys and values stay out of
  the projection, decisions, logs and public output.
  [Pinned controller](https://github.com/mpmdw/JouleWise/blob/043b972f999913d248769237f1901d78119ceb72/joulewise/controller.py#L3624-L3644)

## Acceptance

Run the same valid sentinel in each approved extension object with a
guard against whole-document decoding, conversion and projection of the
sentinel. Move the key to the metadata envelope and then to the adapters
envelope. Reject both siblings, missing adapter names, missing or
non-object runtime prepare metadata, invalid declared types, escaped
duplicate keys, excessive nesting and `1e309`.

Record coverage by field, variant, and entry point. For every declared
field and applicable record variant exercise required removal and wrong
type, optional absence and invalid presence, and relevant numeric
boundaries. Rebind each synthetic mutation before evaluation. At stage 1,
standalone preflight and direct stage 2, structural faults give exit 2,
empty stdout and exactly `REFUSE PREFLIGHT INPUT_CHANNELS` on stderr.
Status stays fresh with absent reservation, marker and publication and
zero claim or value-read events. Retain the ruled positive and per-leg
cases, frozen byte identity and receipts, the passing F4 and F6 cases,
and the open LOW orphan-marker race.

Tier 2 executing review, the installed byte pass and bound-host blind
preflight remain lead gates before reservation.
