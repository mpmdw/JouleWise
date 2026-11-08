# Static pre-arm packets (engineering, v1)

Authority: Ed's eng-prearm brief and RUN_STATE 213–215; D-181's existing
physics, evidence, registration, notice, census and veto fences remain in force.
This cache is **not an ARM receipt, GO receipt or native qualification**. No
measurement rule, threshold or result schema changes.

`scripts/prearm_packet.py build` runs the original deterministic static
validators on the laptop. `verify` rehashes their complete input inventory on
the measurement host, checks plan and checkout pins and expiry, and returns
their original outputs in their original order. It executes no validators.
Every mismatch refuses; it never silently regenerates or substitutes a result.

## Trust and dependency boundary

A lead-reviewed recipe is an explicit dependency closure. It must include
validator code and imports, kit generator inputs **and generated outputs**,
lock/config files, plan, identity pins, validated receipts, and every ledger or
revocation input that can make a receipt stale. File trees bind added/removed
files and empty directories as well as file bytes and executable status.
Git HEAD is checked separately. Git blobs read by a generator are bound by
their immutable commit IDs in those inputs. Model weights and observations
from physical checks do not belong in the packet.

Neither arbitrary check names nor a successful process exit prove that the
recipe is complete. The lead must select the existing validators and audit
their dependencies before enabling a cache at an arm entrypoint. A validator
that exits zero for a refused/pending result needs an adapter that preserves
its existing refusal. Untracked external dependencies, ambient environment,
native observations and commands that produce time-dependent evidence cannot
be memoized by this interface. Use deterministic validators with locked
dependencies; retain host-local native/import/runtime verification.

The recipe SHA-256 and packet SHA-256 must come from independent reviewed
handoff/notice custody. Reading a digest from an adjacent transferred sidecar
does not establish trust. The API caller must provide the independently
reviewed recipe object, not one obtained from the packet. Hashing establishes
identity to that handoff; it is not a signature or an approval decision.

The packet stores canonical JSON, including exact stdout/stderr bytes encoded
in base64, validator exit codes, recipe digest, input digests and build/expiry
epochs. It binds plan_id, repo_head and measurement_head through the recipe
and plan. Paths inside plan fields are treated as text, never followed by the
packet implementation. Recipe input paths are relative to the supplied root;
symlinks, traversal and restricted/custody/archive namespaces are refused.

Build snapshots before and after validation must agree. Publication is an
fsynced, read-only file linked exclusively into its final name; an existing
packet is never replaced. A consumer must keep verified inputs immutable
through its subsequent arm operation, as with existing identity checks.

## Recipe and expiry

The exact recipe keys are:

```json
{
  "schema": "joulewise.prearm_recipe.v1",
  "identity": {"plan_id": "...", "repo_head": "<40 hex>", "measurement_head": "<40 hex>"},
  "plan": "staging/night_plan.json",
  "files": ["staging/night_plan.json", "staging/static-receipt.json"],
  "trees": ["scripts", "joulewise", "configs/your-kit"],
  "receipts": [{"path": "staging/static-receipt.json", "expires_field": "valid_until_epoch_s"}],
  "not_after_epoch_s": 0,
  "checks": [
    {"name": "kit_regeneration", "argv": ["{python}", "-B", "{root}/scripts/your-validator.py", "kit"], "timeout_s": 60},
    {"name": "plan_identity", "argv": ["{python}", "-B", "{root}/scripts/your-validator.py", "identity"], "timeout_s": 60},
    {"name": "receipt_validation", "argv": ["{python}", "-B", "{root}/scripts/your-validator.py", "receipts"], "timeout_s": 60},
    {"name": "static_config", "argv": ["{python}", "-B", "{root}/scripts/your-validator.py", "config"], "timeout_s": 60}
  ]
}
```

This is a shape example, **not a production ALIGN recipe**. `your-validator.py`
does not exist. Set a real handoff expiry and replace it with the original
validators, preserving their failure semantics. An intrinsically timeless
receipt can instead have `{"path": "...", "immutable": true}`. This classification
cannot be used for single-use, boot-bound, monotonic-expiring or
ledger-dependent evidence. Those require fresh host-local checks.

The usable interval starts at the build epoch and ends, exclusively, at the
earliest of the handoff expiry, the plan's authored epoch plus existing
`PLAN_MAX_AGE_S`, and each declared receipt expiry. A future-authored plan,
future-built packet, stale receipt or packet expiring during build/verification
refuses. These are cache validity limits; they never extend an arm rule's
validity. The ordinary driver's plan-window, clock/boot, receipt-consumption
and physical predicates still run at their existing points.

## Operation and integration

On the laptop, with independently reviewed `RECIPE_SHA`:

```sh
python3.13 -B scripts/prearm_packet.py build --root "$STATIC_ROOT" \
  --recipe "$RECIPE" --recipe-sha256 "$RECIPE_SHA" --packet "$PACKET"
```

Retain its emitted `packet_sha256` in the reviewed handoff. Transfer the
packet and identical static inputs without rewriting absolute paths inside
their bytes. On the MBP, in an authorized gap:

```sh
python3.13 -B scripts/prearm_packet.py verify --root "$STATIC_ROOT" \
  --recipe "$RECIPE" --recipe-sha256 "$RECIPE_SHA" \
  --packet "$PACKET" --packet-sha256 "$PACKET_SHA"
```

Only `STATIC_VERIFIED` permits the owning adapter to reuse the matching static
results. No production arm entrypoint in this main snapshot uses the cache;
existing checks remain enabled. ALIGN v4 modules are on the separate
integration lane. Freeze that lane's recipe and connect its static boundary
before claiming an arm speedup. Do not cache `evaluate_static` wholesale: it
also checks the current time/window and measurement checkout state.

## Terminal wake

The night installer includes `JOULEWISE_TERMINAL_WAKE_ROOT` in authenticated
rendered plist bytes. It defaults to the watchdog's usual magistrate root;
`MAGISTRATE_WATCHDOG_CUSTODY_ROOT` must be identical when rendering both jobs
if a nondefault root is used. No destination means no notification for direct
or historical driver invocations.

After terminal reporting, the driver atomically publishes `terminal-wake.json`
there. The marker contains structural identifiers and a nonce; it contains no
measurements. `WatchPaths` requests an ordinary watchdog tick. The installer
seeds an inert file before bootstrap so the watch target exists.

Under the existing service lock, a new event no older than 60 s allows at most
30 additional one-second retries of `FENCED`/`HOLD_CENSUS`, covering a driver
that has not quite exited. Probe execution can add to this nominal interval.
All terminal release proofs, stop checks, plan fences, backoff, clock checks
and process censuses still apply. An event for an open chain cannot release
it. Replays dedupe; malformed, stale or lost notifications retain normal
watchdog behaviour. A failure to persist the event acknowledgement also falls
back to the ordinary tick. `StartInterval=300` and `RunAtLoad` remain enabled.
No continuous agent or event listener is introduced.
