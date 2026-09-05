# Campaign generator common core

Status: implemented for the three live D-117 `_v5` producers under the
2026-09-04 magistrate ruling.

## Forcing problem

The current tree contains twelve D-117 campaign generators. Nine are
authenticated historical snapshots. The three live `_v5` producers (ALPHA,
BETA, and GAMMA) repeated the same canonical JSON renderer, SHA-256 byte and
sidecar helpers, pack inventory, and desk-time write-boundary validator. A
path-safety correction could therefore drift across the producers, and adding
another producer encouraged another hand-copy.

The generator source is itself part of successor-pack output. Historical pack
generators also preserve frozen pack bytes. The extraction therefore separates
shared executable mechanics from campaign-owned pins without claiming that a
self-emitted generator file can remain byte-identical.

## Boundary

`joulewise.campaign_generator_core` owns only the mechanics shared by all three
live producers:

- `render_json` plus `make_render_json`, which binds the producer's existing
  generation-identity projection;
- `sha256_bytes` and `sidecar_bytes`;
- `actual_pack_paths`; and
- `validate_generation_write_boundary`.

Each producer imports those exact function objects. Scientific pins, campaign
planning, output inventories, write calls, and generation-identity policy stay
in the producer.

The write-boundary implementation contains one inert, test-only observer seam.
When patched, it reports the validated output root and complete relative-path
inventory after every path has passed validation. The default is `None`, so it
does not alter production behavior or bytes. This lets the regression observe
the boundary actually reached by a producer rather than infer use from an
imported name.

The earlier draft identity-class factory is intentionally omitted. ALPHA and
BETA share one identity implementation, but GAMMA's current-target lookup and
default semantics differ. Moving that policy would not be a byte-identical
mechanical extraction and would need behavior coverage for current, successor,
downgrade, preserve, and frozen states. `MODULARITY-01`, not this maintenance
refactor, owns broader producer parameterization.

## Historical custody ruling

The 2026-09-04 magistrate ruling exempts the nine hash-pinned historical
generators. They retain their local helper copies and are enumerated explicitly
by the regression. A newly discovered D-117 generator fails the census until it
is classified as either a live shared-core consumer or a historical custody
snapshot.

## Worked example

A future producer retains its model, workload, cell, and acceptance pins. It
imports `validate_generation_write_boundary` and the byte helpers, then binds
`render_json = make_render_json(thread_generation_identity)`. Before emitting
`calibration_plan.json`, it supplies its closed relative-path inventory to the
shared validator. A symlink in the target ancestry refuses before any write;
changing a scientific pin remains local to the producer.

## Byte-parity boundary

`scripts/check_campaign_generator_core_parity.py --baseline-ref <revision>`
loads the pre-extraction ALPHA, BETA, and GAMMA sources from Git, generates each
baseline and worktree producer into paired temporary roots from the same prompt
pin, and compares every path and byte.

Three self-bound files are excluded: `generate_configs.py`, `plan_tree.json`,
and `plan_tree.sha256`. The imported core necessarily changes the self-emitted
source; the plan tree authenticates that source and its sidecar authenticates
the tree. All other emitted bytes must match exactly.

## Counterfactual regression

`test_counterfactual_local_write_boundary_cannot_bypass_shared_core` names the
failure being prevented. It runs each of ALPHA, BETA, and GAMMA through its
production generation entry point, records the shared boundary call, and
requires its validated inventory to equal every file the producer emitted.
`test_exact_alpha_local_validator_evasion_is_detected` makes a temporary copy
of ALPHA's source, adds the refuter's same-signature differently named local
validator, redirects the production call to it, and proves that the behavioral
contract rejects the mutation. Imported-object identity remains a secondary
check for the other extracted mechanics; it is not the write-path proof.

These regressions guard against accidental divergence by a maintainer; they are
not an adversarial guard. Under D-161 a generator author routing around the core
is an operator-only adversary, and evidence integrity rests on the frozen config
bytes and pre-registration digests, not on this test (magistrate ruling, trace 07).
