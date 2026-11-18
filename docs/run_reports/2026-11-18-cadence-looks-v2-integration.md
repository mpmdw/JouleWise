# Cadence looks v2 integration

The Tier 2 branch started at PR #821's reviewed head `59557d6e8` and rebased
onto `origin/main` at `bbcb1d468` after PR #821 merged at `c07c7a75e`.
Mission M0 found no active stop card. The assigned lane was the manifest
integration, with the magistrate's measurement pointer owned by its existing
lane. The spec freeze is `4d740d77c`. The two ported test modules failed to
import the missing implementation on that commit. The build is `f9d41ea3e`.

## Schema and manifest bytes

`docs/process/cadence/looks/look_manifest.v2.schema.json` holds qualification,
description and transfer. On the reviewed qualification registration,
`pins.schemas.manifest.sha256` is `PENDING:CODE`. Its run report records a
qualification manifest digest and deferred code and schema digests. The
registration and report leave the v2 schema digest unpinned, so RL-183 §3.2
keeps the variants in v2. [Ruling](https://github.com/mpmdw/JouleWise/blob/09c77ae4fc9ae66526dbf752fbd283d8030469a5/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L20323)

The new `joulewise.cadence_looks.manifest_dispatch` CLI chooses validation
from the schema ID. It delegates v1 to the pinned CLI, uses the reviewed
qualification validator for qualification, and validates the other two v2
shapes locally. For final v2 validation it checks decoded strings in values,
arrays and keys for either reserved placeholder. The description roster is
the named filler series for that read. Qualification's independently bound
blocks and transfer's ordered twenty kits still govern their rosters. RL-180
row 9 is implemented by the description registration in RL-181 §2.1.
[Description ruling](https://github.com/mpmdw/JouleWise/blob/09c77ae4fc9ae66526dbf752fbd283d8030469a5/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L19381)

| Look | Candidate manifest SHA-256 |
| --- | --- |
| `lm-transfer-01` | `e5777535e5c330010a5266cc7b4a444b6b05f37c8adf6d489da58753763999c7` |
| `lm-inst-01` | `d23cc01ea197ce310838e66bbf0e565ac23ca68f7a312449cc66bf449f8c5f56` |
| `lm-stab-01` | `d43a05f5d713ed5cb6a31eb2f68e3a086ca5c35487e1e4cc2d6e2b07d34685b5` |

All three candidates are drafts beside `lm-qual-01.manifest.json`. The
transfer draft changes two path references for the new layout. The transfer
output schema and release worker match the bytes at `4e5c2ad1d`.
The qualification manifest remains
`d6fde6918023ea69051da45a6b0e3c06ffcfdafd8975a1773989324fa7c9bdab`
and its validator remains Git blob `35bbd6b2f5`.

`docs/process/cadence/looks/LOOKS.json` is the known merge point with PR #795.
The source-tree comparison found zero other overlapping paths with different
bytes under the two cadence look directories. The merged qualification ledger
is the base for the lead's eventual registration. PR #795 remains the reader
dependency for the descriptions.

## Verification

| Finding | Build | Regression | Result |
| --- | --- | --- | --- |
| Close all v2 object shapes and reject kind/body mismatches | `f9d41ea3e` | `test_v2_variants_are_closed` and Draft 2020-12 validation | PASS |
| Dispatch from schema ID only and reject unresolved final strings | `f9d41ea3e` | `test_dispatch_by_schema_id`, `test_final_refuses_pending_and_open`, pinned v1 CLI refusal of v2 | PASS |
| Enforce filler scope, description channels and each release inventory | `f9d41ea3e` | `test_filler_ban_by_kind`, `test_description_shape` | PASS |
| Preserve the transfer draft, hash-slot finalization and release boundary | `f9d41ea3e` | `test_transfer_candidate_validates`, `test_transfer_exit_statuses`, ported release and dispatch modules | PASS |
| Preserve registered qualification and interim bytes | `f9d41ea3e` | `test_registered_bytes_unchanged`, unchanged `tests.test_qualification_manifest`, pinned v1 schema digest | PASS |
| Preserve both transfer audit repairs | `4e5c2ad1d` plus integration `f9d41ea3e` | Retired stop phrase 20 old matches and zero repaired, all 20 committed kit hashes and replacement clauses, all eight pinned synthetic `DateTests` | PASS |

Audit round 2's arm-bound distinction still reproduces. With a synthetic
00:05 transfer start, 00:10 freeze and 01:00 W1 start, the date map reports
served and the arm-bound check refuses. The lead must check each start
against its authorized bounds when forming stage 1.

The repository shard runner timed both new modules for
`scripts/test_timings.json`. The niced focused check covered both new test
modules, the unchanged qualification suite and the quick and shard module
inventory checks. The integrated-v1 test skips when the v1 schema is on the
separate PR #795 branch, so the pinned v1 CLI and digest were checked
separately. Local execution was limited to synthetic test inputs. The
unfiltered local shard suite includes a test that can open the real
measurement ledger and archive. The hosted PR records repository CI on the
integration head.

## NEEDS_SPEC and lead handoff

The final description manifests must list the exact rail-sum column names
returned by the pinned step-3 loader for the bound host, as RL-181 §2.4
requires. The drafts defer those names to the research lead and reader owner
before finalization.

After the research lead's cold approval, the lead must put the reviewed
transfer registration and matching `LOOKS.json` row on main before the
first transfer arm. Set the manifest and row to `registered`, retain
`PENDING:CODE` in every bindable slot and bind the row to the exact
registered manifest SHA-256. Issue only with effective freeze 2 and the
dated lead authority. Before the terminal reservation, land the scorer and
remaining schemas, fill only the registered hash slots, validate the final
manifest against the exact registration bytes, and satisfy the final
Fable pass and stage-1 bindings under RL-183.
