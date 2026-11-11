The real shared harvest derived identity for all 18 synthetic W1 science members and emitted no `model.identity_underivable`, but it excluded all 18 for missing synthetic physics evidence and 25 unrun auxiliary members for missing bundles.
Removing ordinal 5's canonical model-identity records added exactly that member's `model.identity_underivable` in the full harvest and isolated identity control; the full synthetic session still ended `HARVEST_FAULT` on its unresolved bound-runs root.

# RL-65: W1 harvest execution and window-code reading

## Scope and authority

Read RL-65 verbatim with the exact command in the brief. Read audit section 8
and the state-machine lane plan. This is evidence for the harvest lifecycle
gap in audit §8.2(8), within the narrower tests-only RL-65 assignment. It does
not implement a production fail-closed harvest or settle the research lead's
classification ruling.

Base: `ff6f349d6320d41978896f3d3cfe677d4d5ee4ff` (W1 plus unbound CI fixes).
Branch: `test/2026-11-11-w1-harvest-exec`. No network, remote host, model download,
measurement collection, results ref, or real custody was used. Coordination
state and CANONICAL were left to the lead, as the specific seat requires.

Also read the arm-stack code by `git show` on both refs, without checkout:
`origin/main` = `711467824395b689216ab24481d8f6e0a1d36ab4` and
`origin/align/2026-11-08-v4-r11` = `b4a6c217f0285a20aff33a8407160dd77af2a8a6`.
The W1 `run_night.py` has `courier.delivery.json` and `chain_exit_nonzero:<rc>`;
main's older records need neither. No production outcome classifier was added.

## Question 1: executed path

The existing fixtures are complementary. WP22's `dry.collect` calls the real
kit, `MlxRuntimeAdapter.prepare`, ALIGN workload, and `controller.run_benchmark`
for all 18 W1 members. Its fake native module, tokenizer, task, clock, SMC,
thermal status, power rail, package versions, and battery command are stand-ins.
Its tiny `weights.safetensors` is synthetic text. No MLX device is used.
The fake stream still goes through the real artifact hashing and bundle writer.

`tests/align/test_harvest_off.py:880` creates controller bundles, but its
end-to-end test substitutes the harvest at lines 954–959. Its real-harvest
equality fixture at lines 405–435 uses the B5 window fixture instead of W1.
The review fixtures likewise exercise that B5 fixture. None is already the
requested full W1 harvest proof.

The new module connects WP22 to the real
`scripts/bytes_h_session.py:113` measurement-view builder. That is the prepare
path shared by `align_pilot_session` and v4. The source checkout is temporary
and contains only staged config/code inputs, never a real runs directory.
The builder resolves dispatches, copies configs into the pack, fills auxiliary
manifests, and creates the real identity projection. The synthetic member
config bytes and manifest digests are rebound in that temporary source.

The initial test attempt used the source kit tree directly. It failed at
`build_roster`: `external_inputs` was still the source placeholder list
`["artifacts", "manifests"]`. The actual view builder is necessary. This was a
fixture-construction error, not evidence that the production desk uses that
placeholder tree.

The test calls real `joulewise.b5.harvest.harvest`, real `assess_member`, real
`_Harvest.model_identity`, and real `joulewise.flags.exclusions.compute`.
Workers and I/O workers are both 1. Assessment observation wraps the real
function and records its return; it does not replace its result.
The terminal envelope, harvest threshold block, and absent ledger/capture
locations are explicit synthetic inputs. `prepare_desk=False` omits the
whole-window verdict child. B6 acceptance/export and the complete v4 desk CLI
are not executed by this test.

The registration directory is the generated v4 directory in that view.
It has no `acceptance.json`. The test follows the exact resolution at
`scripts/harvest_b6_session.py:44–55`: failed `registration.load`, then
`registration.DEFAULTS['catalog']`, and that directory's `identity_pins.json`.
The harvest-recorded catalog is:

```
/Volumes/JW-EXT/jw-wt/sol-w1-harvest-exec/configs/b6/flag_catalog_b6.json
01767fe4e75ed961798f4e6b68cf055a5b3946a474129e93d2b5e7c239a1dd0c
```

The recorded path is absolute under this clone. Its bytes and effects are
unchanged. `model.identity_underivable` is `EXCLUDE_MEMBER`;
`model.identity_mismatch`, `model.identity_unpinned`, and
`member.cooldown_evidence_unverified` are `DISCLOSE`.

### Full observed exclusions

The complete `members_excluded` projection (run ID and all codes) was:

| Run ID | Codes |
|---|---|
| `align-pilot-v3-episodes-a-e01` | `battery.unmeasured`, `contention.unmeasured`, `member.anchor_recompute_mismatch`, `member.bytes_missing`, `member.strict_validation_failed` |
| `align-pilot-v3-episodes-a-e02` | `battery.unmeasured`, `contention.unmeasured`, `member.anchor_recompute_mismatch`, `member.bytes_missing`, `member.strict_validation_failed` |
| `align-pilot-v3-episodes-a-e03` | `battery.unmeasured`, `contention.unmeasured`, `member.anchor_recompute_mismatch`, `member.bytes_missing`, `member.strict_validation_failed` |
| `align-pilot-v3-episodes-a-e04` | `battery.unmeasured`, `contention.unmeasured`, `member.anchor_recompute_mismatch`, `member.bytes_missing`, `member.strict_validation_failed` |
| `align-v4-episodes-a-e05` | `battery.unmeasured`, `contention.unmeasured`, `member.anchor_recompute_mismatch`, `member.bytes_missing`, `member.strict_validation_failed` |
| `align-v4-episodes-a-e06` | `battery.unmeasured`, `contention.unmeasured`, `member.anchor_recompute_mismatch`, `member.bytes_missing`, `member.strict_validation_failed` |
| `align-v4-episodes-a-e07` | `battery.unmeasured`, `contention.unmeasured`, `member.anchor_recompute_mismatch`, `member.bytes_missing`, `member.strict_validation_failed` |
| `align-v4-episodes-a-e08` | `battery.unmeasured`, `contention.unmeasured`, `member.anchor_recompute_mismatch`, `member.bytes_missing`, `member.strict_validation_failed` |
| `align-v4-episodes-a-e09` | `battery.unmeasured`, `contention.unmeasured`, `member.anchor_recompute_mismatch`, `member.bytes_missing`, `member.strict_validation_failed` |
| `align-v4-episodes-b-e10` | `battery.unmeasured`, `contention.unmeasured`, `member.anchor_recompute_mismatch`, `member.bytes_missing`, `member.strict_validation_failed` |
| `align-v4-episodes-b-e11` | `battery.unmeasured`, `contention.unmeasured`, `member.anchor_recompute_mismatch`, `member.bytes_missing`, `member.strict_validation_failed` |
| `align-v4-episodes-b-e12` | `battery.unmeasured`, `contention.unmeasured`, `member.anchor_recompute_mismatch`, `member.bytes_missing`, `member.strict_validation_failed` |
| `align-v4-episodes-b-e13` | `battery.unmeasured`, `contention.unmeasured`, `member.anchor_recompute_mismatch`, `member.bytes_missing`, `member.strict_validation_failed` |
| `align-v4-episodes-b-e14` | `battery.unmeasured`, `contention.unmeasured`, `member.anchor_recompute_mismatch`, `member.bytes_missing`, `member.strict_validation_failed` |
| `align-v4-episodes-b-e15` | `battery.unmeasured`, `contention.unmeasured`, `member.anchor_recompute_mismatch`, `member.bytes_missing`, `member.strict_validation_failed` |
| `align-v4-episodes-b-e16` | `battery.unmeasured`, `contention.unmeasured`, `member.anchor_recompute_mismatch`, `member.bytes_missing`, `member.strict_validation_failed` |
| `align-v4-episodes-b-e17` | `battery.unmeasured`, `contention.unmeasured`, `member.anchor_recompute_mismatch`, `member.bytes_missing`, `member.strict_validation_failed` |
| `align-v4-episodes-b-e18` | `battery.unmeasured`, `contention.unmeasured`, `member.anchor_recompute_mismatch`, `member.bytes_missing`, `member.strict_validation_failed` |
| `neg8-refcorpus-r01` | `member.bytes_missing` |
| `neg8-window-end-r1` | `member.bytes_missing` |
| `neg8-window-midpoint` | `member.bytes_missing` |
| `neg8-window-start-r1` | `member.bytes_missing` |
| `neg8-refcorpus-r02` | `member.bytes_missing` |
| `neg8-window-end-r2` | `member.bytes_missing` |
| `neg8-window-start-r2` | `member.bytes_missing` |
| `neg8-refcorpus-r03` | `member.bytes_missing` |
| `neg8-window-end-r3` | `member.bytes_missing` |
| `neg8-window-start-r3` | `member.bytes_missing` |
| `neg8-refcorpus-r04` | `member.bytes_missing` |
| `neg8-refcorpus-r05` | `member.bytes_missing` |
| `neg8-refcorpus-r06` | `member.bytes_missing` |
| `neg8-refcorpus-r07` | `member.bytes_missing` |
| `neg8-refcorpus-r08` | `member.bytes_missing` |
| `neg8-refcorpus-r09` | `member.bytes_missing` |
| `neg8-refcorpus-r10` | `member.bytes_missing` |
| `neg8-refcorpus-r11` | `member.bytes_missing` |
| `neg8-refcorpus-r12` | `member.bytes_missing` |
| `neg8-refcorpus-r13` | `member.bytes_missing` |
| `neg8-refcorpus-r14` | `member.bytes_missing` |
| `neg8-refcorpus-r15` | `member.bytes_missing` |
| `neg8-refcorpus-r16` | `member.bytes_missing` |
| `neg8-refcorpus-r17` | `member.bytes_missing` |
| `neg8-refcorpus-r18` | `member.bytes_missing` |

There are 43 rows. Every one of the 18 science bundles lacks the raw
`raw/powermetrics.plist` that the synthetic GPU rail does not write. This
causes `member.bytes_missing`, `member.strict_validation_failed`, and
`member.anchor_recompute_mismatch`: the synthetic bounded clock cannot be
recomputed from native bytes. There is no global battery or contention
journal, causing `battery.unmeasured` and `contention.unmeasured`. The latter
is stripped by the actual v4 desk under R22-1; the other four still exclude.
All 25 auxiliary bundles were intentionally not collected by WP22, so each
has `member.bytes_missing`. No exclusion effect was overridden.

`derived/exclusions.json.reasons` was exactly `["cell.below_minimum"]`.
The recorded final window reasons were exactly
`["cell.below_minimum", "harvest.fault"]`. The sole collector error was
`lineage: HarvestFault: bound_runs_root_unresolved`. The synthetic envelope
does not provide the calibrated bound root or production lineage; no such
root is fabricated to make this test green. Harvest yield was 43 planned,
18 present, 18 succeeded, zero raw-valid; the stage journal was absent.
The test asserts these observed exclusions and fault, and therefore uses
`test_ACTUAL_synthetic_w1_identity_derives_but_missing_physics_excludes`.
It does not assert an empty full-harvest exclusion list.

### Identity provenance for every W1 member

All 18 assessments had status `succeeded` and a non-null identity. Each
row below uses **W** = `metadata.workload_provenance.model.artifact_identity`
(`folded_sha256`) and **S** = the recorded runtime stack fields described
below. Each bundle also had the same artifact object in adapter prepare
metadata. The test asserts both equality and the full derived hash pair.

Synthetic model artifact hashes:

- 30B: `fd5bb085e95100779ad5ca5ad6c854421bc423402ca5aacec577f7d22a9520e9`.
- D: `e19ca94798692411ed918f8d8ff78f43637dcf590112e110172ccbe5599c79c3`.

| Ordinal | Run ID | Derived / fields | Artifact | Runtime identity SHA-256 |
|---|---|---|---|---|
| 1 | `align-pilot-v3-episodes-a-e01` | yes; W + S | 30B | `156f50a5e1dc9e3e80d8ee9fecd86a1078bf0164774ad36f5f978e3238c551aa` |
| 2 | `align-pilot-v3-episodes-a-e02` | yes; W + S | 30B | `ee99534a52675f996d2f4f4517da32bd7836a596469e62ad47c855abf3ceb463` |
| 3 | `align-pilot-v3-episodes-a-e03` | yes; W + S | 30B | `156f50a5e1dc9e3e80d8ee9fecd86a1078bf0164774ad36f5f978e3238c551aa` |
| 4 | `align-pilot-v3-episodes-a-e04` | yes; W + S | 30B | `ee99534a52675f996d2f4f4517da32bd7836a596469e62ad47c855abf3ceb463` |
| 5 | `align-v4-episodes-a-e05` | yes; W + S | D | `67af539f5b7a3e1ed6ca63868730021a0e1ae9a9d943bff4df0392ed2337f5b6` |
| 6 | `align-v4-episodes-a-e06` | yes; W + S | 30B | `dff310bf209790a0910403b7add380e881c68d17fdb7490955e6775031b82cc4` |
| 7 | `align-v4-episodes-a-e07` | yes; W + S | 30B | `34668ce458c061cbd864bc93394e6c5f3058f7f12252a38b58860ed9f5266a50` |
| 8 | `align-v4-episodes-a-e08` | yes; W + S | D | `81cb4f0b4cc6327f06b0ddc4012b0065dc341fba2cadca5c4327e51e5030e48f` |
| 9 | `align-v4-episodes-a-e09` | yes; W + S | 30B | `95b9440039bcccaf603763f2866d7f414df223838fb9fbac16ea222193ef7b21` |
| 10 | `align-v4-episodes-b-e10` | yes; W + S | 30B | `8a0db7d2057d198a6696f97dafce4640f8cad90e5e27eaf31ab5b2f1662b17d3` |
| 11 | `align-v4-episodes-b-e11` | yes; W + S | D | `b4888e52d45673f36eef1838cdb2f74953525346350a49d79df937bc1f5c8cdf` |
| 12 | `align-v4-episodes-b-e12` | yes; W + S | 30B | `8a0db7d2057d198a6696f97dafce4640f8cad90e5e27eaf31ab5b2f1662b17d3` |
| 13 | `align-v4-episodes-b-e13` | yes; W + S | 30B | `95b9440039bcccaf603763f2866d7f414df223838fb9fbac16ea222193ef7b21` |
| 14 | `align-v4-episodes-b-e14` | yes; W + S | D | `81cb4f0b4cc6327f06b0ddc4012b0065dc341fba2cadca5c4327e51e5030e48f` |
| 15 | `align-v4-episodes-b-e15` | yes; W + S | 30B | `34668ce458c061cbd864bc93394e6c5f3058f7f12252a38b58860ed9f5266a50` |
| 16 | `align-v4-episodes-b-e16` | yes; W + S | 30B | `dff310bf209790a0910403b7add380e881c68d17fdb7490955e6775031b82cc4` |
| 17 | `align-v4-episodes-b-e17` | yes; W + S | D | `b4888e52d45673f36eef1838cdb2f74953525346350a49d79df937bc1f5c8cdf` |
| 18 | `align-v4-episodes-b-e18` | yes; W + S | D | `1529488795323b4fbb5ee227a1f838151bb1394e91c809b268cb2127a88d1776` |

The adapter hashes the local synthetic weights at
`joulewise/adapters/mlx_runtime.py:302` and records
`prepare_metadata.model_artifact_identity` at line 314. The controller persists
the prepare metadata at `joulewise/controller.py:3625–3633`. The ALIGN
provenance also carries `workload_provenance.model.artifact_identity`.

`assess_member` sets `result['identity']` at
`joulewise/b5/harvest.py:2346–2350`, by calling
`derive_model_runtime_config_from_metadata`. Despite the historical word
“triple”, this assessment returns the model and runtime hashes only. The
identity function also computes the config hash. Its stack builder reads the
artifact from **workload provenance**, not by reopening `model.source` and not
by falling back to the adapter's prepare record
(`joulewise/identity_pins.py:301–340,392–413`). Runtime identity includes the
recorded adapter/version, tokenizer, sampler/output policy, quantization,
device/boundary, OS, and telemetry fields at lines 352–383.

### One-member negative control

Copy only ordinal 5's controller bundle to another temporary directory.
Remove its recorded artifact identity from both prepare metadata and workload
provenance. Assess the copy with real `assess_member`. Run the real
`model_identity` collector over the roster of assessed W1 members with only
that assessment replaced, then the real catalog/exclusion engine.

Both controls passed. The identity-only clean control's `members_excluded`
was `[]`; after removal it was exactly:

```json
[{"run_id": "align-v4-episodes-a-e05", "codes": ["model.identity_underivable"]}]
```

The expanded control also reran the **full real harvest** on a temporary copy
of all 18 science bundles. Exactly one assessment then had `identity: null`:
`align-v4-episodes-a-e05`. Its excluded codes were exactly:

```json
["battery.unmeasured", "contention.unmeasured", "member.anchor_recompute_mismatch", "member.bytes_missing", "member.strict_validation_failed", "model.identity_underivable"]
```

The other 42 exclusion rows were unchanged. The test asserts that complete
list, so removing the orchestration's model-identity step fails the test.
Before removing workload provenance, a separate assessment with only the
adapter prepare copy removed still derived the original identity. That
control identifies the actual field consumed, rather than assuming that
prepare metadata itself is the reader's fallback.

This isolates identity causality from missing synthetic physics. It does not
claim that deleting one identity makes the already physically incomplete full
harvest have only one excluded member. There is no model-source fallback.

## Question 2: proposed classification of all 19 codes

These are proposals for the research lead, not installed policy. “Can fire”
means the registered plan/scaffold permits the condition. The table also
distinguishes emissions added only by B6 acceptance. With the checked-in v4
directory's missing `acceptance.json`, that acceptance evaluation returns
`UNAVAILABLE` first (`joulewise/b6/session.py:29–50`). A catalog entry alone
does not prove that this desk call emitted it. Raw harvest window reasons
and B6 acceptance's `excluding` list are distinct outputs.

V4 **does** retain pre/post calibration captures, a NEG-8 corpus/bound, and
start/midpoint/end reference stages. See
`configs/campaigns/align_v4/plan_tree.json:616,686,689,801,952,1154,1356,1365,1435`.
It has no extraction spec or analysis-manifest cell input in this kit.
The shared roster builder nevertheless creates fallback cells by stage and
role (`joulewise/b5/harvest.py:1819–1833`). Those are not v4's own estimands.

| Code | Emitter and exact condition | Can fire for W1; relation to v4 numbers | Proposed class |
|---|---|---|---|
| `calibration.bracket_incomplete` | `joulewise/b6/calibration.py:91–92`: either capture has no value or is not valid. Also `joulewise/b6/acceptance.py:287–289` on a calibration stop; `joulewise/b6/capture_screen.py:35` emits it when the opening bound is absent. | Yes, the inherited bracket runs. No bracket-bound/acceptance input to the traced v4 estimands. A resulting missing collection is separately structural. | DOES-NOT-MATTER |
| `calibration.capture_battery_pair_failed` | `joulewise/b5/harvest.py:4477–4483`: authenticated capture pair is battery-confounded. Current-only discharge can later be superseded after a successful journal join at `6425`. | Yes, on calibration captures. Guards their calibration validity. Member battery evidence has separate v4 exclusions. | DOES-NOT-MATTER |
| `calibration.capture_battery_span` | `joulewise/b5/harvest.py:6414–6416`: capture battery join finds member-span discharge or accumulator excursion. | Yes. Capture-only validity; no bracket consumer found in the v4 number paths. | DOES-NOT-MATTER |
| `calibration.capture_battery_unmeasured` | `joulewise/b5/harvest.py:6417–6419`: pair is not pass and its span/journal join cannot establish coverage. Reasons include no span, no journal, join failure, or gap (`6388–6411`). | Yes. Same capture-only scope; not the v4 member battery-window rule. | DOES-NOT-MATTER |
| `calibration.operative_bound_above_stop` | `joulewise/b6/calibration.py:94–102`: `max(pre,post)+max(abs(pre-post),screen)` exceeds a supplied stop. Also `joulewise/b6/acceptance.py:290–292` for the named chain stop. | Conditional on a sized stop. No v4 estimand consumes this bound. A collection stopped before required members still raises structural concerns. | DOES-NOT-MATTER |
| `cell.below_minimum` | `joulewise/flags/exclusions.py:349–370`: a target cell has fewer kept units than its minimum. Acceptance also records disclosed-cell failures at `joulewise/b6/acceptance.py:254–258`. | Yes, fallback cells exist. Their B6 minimum is not v4's U1–U6, contrast, or residual population rule. | DOES-NOT-MATTER |
| `clock.step_overlap_calibration` | `joulewise/b5/harvest.py:6327–6332`: a detected clock-step interval overlaps a capture span. | Yes. This guards the bracket. Steps overlapping science members separately emit `clock.step_overlap` at `6321–6326`; those member effects remain relevant. | DOES-NOT-MATTER |
| `code.number_bearing_unreviewed` | `joulewise/b6/code_check.py:57–69`: a changed number-bearing file is dirty or its last executed commit is not reviewed. Acceptance emits it at `joulewise/b6/acceptance.py:348–351`. | Possible in acceptance or recorded flags. Changed reducers/controller can change v4 energy and gates. The current missing acceptance registration does not make that hazard harmless. | MATTERS |
| `model.files_differ_from_registered` | `joulewise/b6/model_files.py:101–106`: observed model hash is outside the source's pinned hashes. Acceptance also promotes artifact mismatches/inconsistency at `joulewise/b6/acceptance.py:320–335`; precheck maps hash mismatch at `joulewise/b6/precheck_lane.py:93–94`. | Yes, through those paths. The v4 model identity and its energy/work would differ from registration. | MATTERS |
| `model.stack_differs_from_registered` | `joulewise/b6/model_files.py:108–149`: package version differs, or every matching artifact's candidate stack differs. Acceptance emits compare results at `joulewise/b6/acceptance.py:338–347`. | Possible in acceptance/recorded flags. Runtime, tokenizer, policy or device changes can change v4 work and numbers. | MATTERS |
| `neg8.survivor_screen_failed` | `joulewise/b6/survivor_screen.py:131–145,80–85`: either reference-energy family's endpoint mean difference exceeds its survivor-count-adjusted corpus bound. Acceptance emits/excludes at `joulewise/b6/acceptance.py:306–312`. | The inherited reference scaffold permits it, when acceptance runs. No traced v4 number or gate reads this NEG-8 screen. | DOES-NOT-MATTER |
| `neg8.survivor_screen_undefined` | `joulewise/b6/survivor_screen.py:87–89,126–147`: too few clean corpus/start/end members, unreadable energies, or unavailable bound. Same acceptance emission at `306–312`. | Possible through that scaffold/acceptance. This is not the registered v4 replay or U3 screen. | DOES-NOT-MATTER |
| `precheck.certain_exclusion` | `joulewise/b6/precheck_lane.py:90–99`: maps unresolved dispatch or an unclassified certain-exclusion reason to this code. Sources include model/dispatch errors (`joulewise/b6/precheck.py:513–517`) and nominal acceptance exclusions (`289–297,550–553`). | Dispatch failure could affect the registered v4 roster; some acceptance reasons guard unused B6 estimands. Need the actual reason and proof of which precheck path supplied the flag. One blanket harmless classification is not supported by this reading. | UNSURE |
| `records.source_changed_during_harvest` | `joulewise/b5/harvest.py:4127`: early-assessment source changed; `5543–5548`: desk changed disallowed bytes/log prefix; `7678–7684`: final source inventory differs. | Yes. V4 numbers could refer to different bytes from the archived/assessed ones. | MATTERS |
| `roster.no_science_bundles` | `joulewise/b5/harvest.py:4322–4325`: science was planned but none of its run IDs was assessed. | Yes. There is no science population supporting the intended W1 numbers. | MATTERS |
| `structure.chain_crashed` | `joulewise/b6/acceptance.py:200–204`: stop reason is neither completed, physics stop, nor calibration stop. Terminal exit parsing is at `533–558` and accepts both nested and top-level exit records. | Possible in acceptance/recorded flags on either record generation. The intended sequence may be incomplete. | MATTERS |
| `structure.missing_stage_bundles` | `joulewise/b6/acceptance.py:209–223`: an expected collection stage is entirely absent but a later stage succeeded; reference-only and recorded idle-skip stages are exempt. | Yes, including either W1 episode stage. Changes the registered sequence/population. | MATTERS |
| `structure.no_capture_records` | `joulewise/b6/acceptance.py:205–206`: no capture evidence, unless a named physics/calibration stop explains it. | Yes. No direct bracket-number consumer found, but this is an incomplete registered scaffold. RL-65 explicitly treats this structure condition as hold-worthy. | MATTERS |
| `structure.no_roster` | `joulewise/b6/acceptance.py:207–208`: empty member evidence. | Yes. No registered population can be checked or counted. | MATTERS |

### Consumption trace and limits of the negative search

The common desk applies `derived/exclusions.json.members_excluded` to each
member (`scripts/align_pilot_session.py:346–365`) and passes the resulting
`excluded` field into `pilot_analysis.residual_analysis` (lines 385–389).
That analysis selects registered members at
`joulewise/align/apple/pilot_analysis.py:189–224`; it fits benign turn rows and
uses episode joules and half-widths. It does not select by window reasons.
V4's contention policy is installed at `scripts/align_v4_session.py:572–574`.

The thermal desk reads controller trace, episode, thermal journal and native
PM evidence (`joulewise/align/apple/thermal_desk.py:789–824`). Its
`calibration_exclusions` name v4 member state/energy hazards (`734–750`), not a
fiducial calibration bracket. U1–U6 consume those observations, replay
energies, signed U3 bar, and supplied cross-window fits (`676–725,884–909`).
U4–U6 are explicitly inconclusive in W1 (`897–901`).

U3 derives its scale from separated-session 30B replay-energy pairs and a
qualified R1 D transfer screen (`joulewise/align/apple/v4_u3.py:112–167`);
the signed derivation is checked at `275–289`. It is not NEG-8 drift screening.
`v4_estimands.py:77–95` calibrates ranks of residual scores;
`196–207` uses residuals and the registered cell residual SD for U6.
The energy-residual model consumes attributed turn energy and additive
half-widths (`joulewise/align/energy_residual.py:146–163,234–250`). These uses of
“calibration”, “cell”, and “bound” do not imply a B6 bracket dependency.

There is an important bound that **is** consumed. `read_episode_bundle`
passes member-local `metadata.uncertainty_evidence` into the power/clock join
(`joulewise/align/apple/workload.py:899–918`).
`joulewise/align/apple/sampler.py:99–121` uses that member's
`effective_clock_anchor_bound_s`, and attribution propagates mapping uncertainty
(`joulewise/align/attribution.py:441–473`). That is not the calibration
bracket's operative bound or its acceptance. The six requested files had no
matches for this exact search:

```sh
rg -n 'operative_bound|bracket_binding|bracket_screen|alignment_reference|acceptance_corpus|neg8|survivor_screen|window_reasons|exclude_window_reasons' \
  joulewise/align/apple/pilot_analysis.py joulewise/align/apple/v4_estimands.py \
  joulewise/align/apple/v4_u3.py joulewise/align/apple/thermal_desk.py \
  joulewise/align/energy_residual.py scripts/align_v4_thermal_desk.py
```

The shared reducer still authenticates a member's attached fiducial artifact
(`joulewise/reduce.py:1813–1838`) and composes that artifact's bound
(`1859–1864`). This is a separate dependency from B6's window operative bound.
Its private two-capture override belongs to the governed consumption session
(`2715–2745`), not the traced v4 desk. The common harvest's target-precheck
reader skips null fallback target paths (`joulewise/b5/harvest.py:4237–4245`);
the common desk mirrors that selection
(`joulewise/align/apple/diagnostics.py:115–131`). Capture battery verdicts are
explicitly window flags while members measure their own battery state
(`joulewise/controller.py:1014–1037`). The proposed harmless classes do not
waive member artifact authentication or member clock/battery exclusions.

This is source-reading evidence within the requested path, not proof that
every possible future analysis consumer ignores those values. Acquisition
stops and missing structure remain separate concerns.

## Verification, changes and handoff

Executed one module at a time with Python 3.13, `-B`, synthetic custody fencing,
Git global/system config disabled, and lazy Git fetching disabled. Unit runs
used `unittest.defaultTestLoader.loadTestsFromName` and
`unittest.TextTestRunner(verbosity=2)` in a stdin driver with a process alarm.
They are the same unittest selections as the commands below. No pytest or
full discovery was used.

| Selection / command | Result |
|---|---|
| Ad hoc `python3.13 -B -` WP22 member-5 / real `assess_member` probe | Identity derived; strict physics invalid because raw PM is absent; zero forbidden custody accesses. |
| `python3.13 -B -m unittest tests.align.test_v4_harvest_exclusions_exec` (first construction) | 2 tests, 169.489 s; 1 failure and 1 error. Source-tree placeholders were not a measurement view. Corrected by reusing the real view builder. |
| Same selection (second construction) | 2 tests, 241.518 s; 1 error. Full harvest executed and all identities derived. The isolated control passed the harvester's Catalog to L4 directly. Corrected to use the production `_l4_exclusions` adapter, which reloads the real catalog. |
| Same selection, with exact exclusions and terminal-generation controls | 3 tests, 260.221 s; PASS. Eight terminal subcases cover both generations and exits 0, 3, 917, and null. Zero forbidden custody accesses. |
| `python3.13 -B -m unittest tests.align.test_v4_harvest_exclusions_exec.SyntheticW1HarvestTests.test_one_removed_recorded_identity_is_underivable` after adding the full negative harvest | 1 test, 288.977 s; PASS. Full baseline harvest plus full negative harvest, with isolated clean/negative identity controls. Zero forbidden custody accesses. |
| `PYTHONPYCACHEPREFIX=/private/tmp/rl65-pycache python3.13 -m compileall -q joulewise tests scripts` | PASS. Bytecode stays outside source directories. Repeated after final test edits. |
| `python3.13 -B -m unittest tests.test_fixture_orphan_census` (180 s subprocess cap) | 16 tests, 0.643 s; PASS, 2 skipped. |
| `python3.13 -B -m unittest tests.test_gen_state` (180 s subprocess cap) | 44 tests, 12.880 s; PASS. |

The run-specific identity hashes in the table come from the final synthetic
session. Runtime hashes of reference-consuming members vary across fresh
temporary namespaces because their recorded thermal policy includes the
rebound source-config digest. These hashes are observations, not portable
identity pins. The tests compare actual recorded fields within one session.
No throughput change, cache, or cross-namespace byte-equality claim is made.

Total reported unittest time, including failed construction runs, was 973.728 s
(16.23 min). Both capped checks finished well below three minutes.

The timing entry is 288.977 s, one local observation of the expanded control
including shared fixture setup. The other two tests add only assertions and
small terminal fixtures. It is a CI scheduling hint under concurrent host
load, not a speed or hardware result. Python 3.11 grammar parsing passed;
only Python 3.13 was executed locally.

Only the new test module, one alphabetical timing entry, and this report are
in scope. No full unittest discovery was run. No production code is changed.
MLX native tests are not run in this sandbox; the new tests use explicit fake
MLX seams. The lead still owes a native v4 smoke through the actual prepare,
collect, and `harvest_b6_session --non-claim` desk argv, with the recorded
catalog digest, identity fields, complete member exclusions, and window
reasons checked. After collecting that smoke in a clean lead-controlled
session, the desk command is:

```sh
python3.13 -B scripts/align_v4_session.py desk --session-root <native-smoke-session> --harvest-workers 1
```

No newly added unit test exercises native MLX. A clean synthetic identity is not that live gate.

Research-lead actions: confirm or amend the 19 proposed classes, especially
the reason-dependent `precheck.certain_exclusion`; install any held-window
rule in the lead-owned deviation/arm/seal surfaces under RL-65. No authority
decision is delegated to this test.
