gpt-6.1-sol

# BYTES item H — round-2 implementation

Activation 283e9802; 2026-10-21. Branch
`lane/2026-10-21-bytes-h-session`; requested/start/end HEAD
`20e6984c949a90305725182244d8dfa72e8f3ef9`; upstream remains
`origin/lane/2026-10-20-bytes-mac-kit`. Round-1 authorized files were retained.
The lead-created `.venv` symlink is unowned and must never be committed.
No commits or push attempts in round 2, per F5. No out-of-scope writes,
watchdog changes, production installation, launchd mutations, powermetrics or
quiet-machine collection. All delivery files remain uncommitted for the lead.

## Outcome

The three-subcommand non-claim runner and kit-local inputs are implemented.
The real dry prepare was executed and correctly refused the physical disk
hazard; it authored no plan. The candidate t0 and maximum allowance printed
before that refusal are reproduced below. The dry directory was deleted.
Successful preparation, the real synthetic harvest/export/measurement/gate
chain, missing-receipt behavior, and the stubbed installer are tested. No
live measurement, C4 execution stack, completed C5 registration or live
stand-down validation is claimed.

## Changed files

- `scripts/bytes_h_session.py`
- `tests/test_bytes_h_session.py`
- `configs/gates/hazard_refusals.json`
- `configs/campaigns/bytes_mac_check/registration/README.md`
- `configs/campaigns/bytes_mac_check/registration/acceptance.json`
- `configs/campaigns/bytes_mac_check/registration/derive_identity_pins.py`
- `configs/campaigns/bytes_mac_check/registration/derive_sizing.py`
- `configs/campaigns/bytes_mac_check/registration/identity_pins.json`
- `configs/campaigns/bytes_mac_check/registration/model_artifact_inventory.json`
- `configs/campaigns/bytes_mac_check/registration/sizing_b5.json`
- `configs/campaigns/bytes_mac_check/registration/sizing_evidence.json`
- `configs/campaigns/bytes_mac_check/registration/smoke_keep.json`
- `.codex-report/bytes-h-session.md`

The unchanged round-1 file identities/acceptance/smoke inputs are part of the
retained delivery. New/updated round-2 material is the session runner, its
tests, complete sizing generator/evidence/row, registration README, refusal
registry enrollment and this report. No shared B6 implementation, alpha/beta/
gamma input, global smoke map, kit generator, generated kit README or fixed
source tree was changed. Existing registration-dir parameters already cover
plan inputs, precheck and harvest; the kit row is keyed by its governed pack
id so the precheck reads the same allowance; unused loop lanes need no new parameter.

## Rechecked integration seams

- pack_registration.py:169-196 discovers only configs/b6/packs registrations;
  the isolated kit inputs are invisible to that loop.
- plan_inputs.py:85-87 needs a sizing row; the new registration now supplies it
  through the existing explicit registration_dir argument. Its row key is the
  governed bytes-mac-check pack id, which also satisfies the precheck lookup.
- model_files.py:90-94 reports an unseen source; eleven file-identity units now
  cover every dispatched config source, including the reference.
- compose.py:217-225 already has a campaign-keyed smoke lookup and the base
  already has a bytes_mac_check row; the local map preserves that selection.
- DriverLane.prepare_session/launch (driver_lane.py:67-190) supply desk identity,
  plan inputs, the real writer, launch lead and installer interface reused here.
- desk_lane.py:185-216 omits --non-claim; this one-off runner uses the existing
  harvest CLI's --non-claim and --registration-dir instead of changing the loop.
- scripts/b6_precheck.py:20-28 already forwards registration-dir. The nearest
  one-off prepare example remains scripts/b6_machine_test.py:103-213.

The brief's docs/registrations/block6_replication_DRAFT.md is absent at this
HEAD. Existing plan/driver contracts, the kit README, block-6 design section
14, BYTES R1-R8/Addenda and the explicit F1-F5 rulings determine this bounded
non-claim tooling; no replacement registration or new counted policy is issued.

## Item 1 — identities and planning inputs

The governed provenance code freshly hashed all eleven local sources in
round 1 (ten roster models plus the Qwen2.5 reference), retaining per-file
inventory, resolved symlink targets, byte sizes and folded identities:
215,449,636,568 weight-file bytes total. All source files still exist at the
real dry prepare. Current worktree `.venv` runtime versions were observed
read-only in round 2 and exactly match those stored: Python 3.13.1, mlx
0.31.2, mlx-lm 0.31.3, mlx-metal 0.31.2, numpy 2.5.1, safetensors 0.8.0,
tokenizers 0.22.2 and transformers 5.12.1. No model was loaded/executed.
`runtime_stack_unobserved` and non-claim labels remain explicit.

`acceptance.json` retains the disclosed block-6 calibration input and its
original derivation/source hash. Operative T10 remains null for this kit.
The local smoke map is the existing kit selection. No pack is registered or
enqueued under `configs/b6/packs`.

F2 is implemented without fitting. Weight-file bytes (inventory size_bytes):
8B-8bit = 8,703,048,996; lower dense Qwen3-14B-4bit = 8,307,898,514; upper
dense Qwen3-32B-4bit = 18,429,850,874. The fraction is
0.03903895888322478. Every repeat's total_s and the load_s are interpolated
as low + fraction * (high-low). Both source paths and SHA-256 receipts are
stored beside the values. Interpolated requests are
18.930114798513518, 18.851969236958926 and 18.783480037248857 seconds;
load is 0.614296995327281 s. The row is flagged
`sizing.planning_bound_interpolated`. It only sets allowances.

The same measured-spread margin applies to every model/reference:
max(max(request)/min(request)-1) over each pilot group and archived reference
group = 0.08343839553709143. Full-member and stream overheads come from 125
successful r4-alpha archive members; failed member spans are also included
when subtracting member time from collection stages. Exact 123-member counts
come from dispatched configs: 86 non-reference model members and 37
references (including twelve test-7 references).

The sizing evidence preserves clock/stage/compression journal source hashes,
event/metadata hashes per observed member, original file-size receipts and
allocation quanta (statvfs.f_frsize). Original uncompressed file allocation
is conservatively reconstructed upward from the compression journal; current
allocated disk bytes are a lower bound, not compressed logical sizes.
Maximum original bundle = 162,971,648 B; maximum original bundle/wall rate =
1,300,115.2977829832 B/s. Longest planned member gives 308,543,416 B per
copy. Peak data have three copies: raw + archive + combined disjoint claim/
bound backups. Fixed artifacts use the measured original non-bundle session
footprint, scaled by maximum-window / observed-member-time sum (at least one). A further
28,082,490,435 B budgets the registered 7,200 s session WAIT at the observed
maximum original bundle-byte rate across three copies; WAIT can retain a live
sampler. T0/pause/WAIT growth of continuous meter/monitor journals is included
in the maximum-window fixed allowance.
No arbitrary fixed percentage or guessed 8-bit runtime is introduced.

Programmed span = 27,370.23694186782 s; the writer rounds it up to 27,371 s.
T_stream_max = 190.96428714294734 s. The unmodified writer independently
adds T0 3,300 s, agent-pause 7,200 s and session-WAIT 7,200 s, then rounds up
to a minute: maximum 45,120 s. This is a conservative planning allowance,
not an observed H duration. Native disk arm receives per-copy bytes and the
150 GiB reserve plus fixed artifacts and WAIT sampler growth as headroom; the prepare check budgets
all three peak copies directly.

## Item 2 — prepare / install / desk

`prepare` uses real desk identity collection, plan_inputs.build and
write_window_plan. Its outputs stay under S. The fixed source kit has two
representation gaps that would prevent a real prepare/harvest: empty launch
bindings, and external_inputs containing the strings `manifests`/`artifacts`
instead of manifest objects. The disposable S/measurement view adds the
existing fourteen launch bindings from the ALPHA interface, adjusts root
leaves, and reconstructs the same 25 scaffold members from the actual
collection dispatch manifests. It uses the tree's governed hyphenated pack
name so the native exporter and C5 agree. The 98 kit members and every
manifest/config byte remain unchanged. Source/staged tree hashes and template
hash are recorded in staging/measurement-view.json. Source code/configs are
read-only links; calibration ledger and head pin are independent copies.
No missing ledger is fabricated. Missing/stale record conditions print flags
and retain INPUTS_ONLY; only STAGED has a usable plan. On this worktree the
source calibration ledger is absent; after freeing disk the lead must supply
the real matching ledger before a plan can be staged. No measurement checkout
or global night custody was repaired implicitly.

`install` calls install_night_agent.sh with exactly the DriverLane interface:
--plan, --python, --courier-bin scripts/b6_courier.sh and --launchctl-bin
launchctl. It records stdout/stderr/exit and prints both installed plist paths.
The item-H installer is tested only with its subprocess stub. Existing B6
regression tests use copied installers, temporary homes and fake launchctl;
no production LaunchAgent was installed. No collection.active marker
is written, per F1. This command belongs to the lead's last act before exit.

`desk` requires the terminal record and runs harvest_b6_session.py --non-claim
with the kit registration directory. The real harvester enforces chain-group
readiness and retains all planned rows. MEASUREMENTS.json contains every v1
field, uses the exact native bracket session id, and hashes the export,
sidecar, native journals, event/metadata sources and optional floor/CPU
receipts. Request seconds come from native sampling markers, full-member
seconds from collection run-clock pairs, stream spans from the actual native
pre_spawn/post_parse paired stamps, thermal level from overlapping OS records,
and C/k from the same whole census quanta overlapping the native request
span (contention.flags support, null on gaps/duplicates). C uses each native
rate times its recorded elapsed_s; no unobserved sub-quantum distribution is
assumed or prorated.
The clock line uses the worst signed per-member fitted rate and worst signed
kernel word. Pre-arm free bytes come from the actual arm disk receipt, never
the earlier prepare snapshot. Raw/archive allocated bytes are counted with
inode deduplication. Fixed retained bytes include final desk outputs, and C5
is rerun only when that integer disk allocation changes, preserving its final
MEASUREMENTS hash.

Unobserved floor, census-power coefficient/resolution, calibration or fixed
verdict/backup timing stays null with a named flag. Session-bound measured
floor/CPU derivation receipts may be retained in S/receipts; their schemas,
accepted fields and provenance rules are documented in registration/README.md.
They never supply another pack's T10/T_phase. No planning number is copied
into measured H receipts. bytes_gates.py is actually invoked; missing inputs
produce gates_exit 1 and unavailable desk status, not a fabricated candidate.

## Item 3 — stand-down fence (F1 applied)

Round-1 F1 and its watchdog reproduction are withdrawn. No watchdog patch is
made. The lead ruled that installed external plans are resident stand-down
candidates and supplied the r4-alpha live evidence: IDLE -> FENCED, "plan span
active and census empty", 409 seconds after t0. That ruling governs this
handoff; this agent session performs no live installation/collection check.

The installer source chooses Path.home()/Library/LaunchAgents
(joulewise/night_agent_install.py, main) and publishes:

- /Users/edr/Library/LaunchAgents/com.joulewise.night.plist
- /Users/edr/Library/LaunchAgents/com.joulewise.night.deadman.plist

The watchdog's _installed_agent_plans at scripts/magistrate_watchdog.py:784
reads those exact files and the absolute --plan ProgramArguments value.
The unchanged installer render/publish route is what this runner calls;
stub tests confirm that exact argv and the printed plist paths. Its ordinary
launch template and deadman argv carry the same absolute session plan.
The watchdog's _write_request at :2397 writes
/Users/edr/night-custody/magistrate/standdown.request with plan_id, t0, TERM/
KILL deadlines and request timestamps. The previously inspected activation
state was ACTIVE with resident_session.status ACTIVE and no standdown_phase
or resident_hold_drain. No state/fence file there was written by this worker.
The lead exits after installation; installed plists fence relaunch; the
in-chain census is the backstop. No local marker is substituted for that route.

## Item 4 — verification

Final runner module: 16 tests, exit 0 (88.858 s). It includes real writer preparation,
physical disk/model failures, missing-ledger flags, stubbed installer and a
real 123-bundle synthetic harvest CLI -> acceptance -> native export ->
MEASUREMENTS -> bytes_gates chain. The missing-floor/calibration case correctly
returns unavailable; a separately fully supplied native synthetic export
extracts every measured field and clears real C5. Four synthetic harvest
workers use the CLI's existing pool; no harvest/acceptance/export result is
stubbed. Fault checks also preserve nulls/flags for truncated journals,
wrong-shaped metadata and nonfinite receipt values. Fixture metadata/
calibration boundaries are synthetic; none is live
hardware evidence. New numeric agreement checks use 1e-6 relative/absolute;
exact checks are integers, identities, membership or identical source bytes.

Every focused module runs in a separate fresh TMPDIR with
JW_B5_SYNTHETIC_ONLY=1 and PYTHONDONTWRITEBYTECODE=1. The new module also
isolates/restores its own TMPDIR and environment. Exact per-module replay is
`python3.13 -B -m unittest MODULE` under those environment settings.

| Module | Tests | Exit | Result |
|---|---:|---:|---|
| `tests.test_bytes_h_session` | 16 | 0 | OK |
| `tests.test_bytes_mac_kit` | 4 | 0 | OK |
| `tests.test_bytes_gates` | 7 | 0 | OK |
| `tests.test_b6_loop` | 55 | 0 | OK |
| `tests.b6.test_lane_adapters` | 21 | 0 | OK |
| `tests.b6.test_plan_inputs` | 3 | 0 | OK |
| `tests.b6.test_model_files` | 14 | 0 | OK |
| `tests.b6.test_precheck` | 23 | 0 | OK |
| `tests.b6.test_loop_round_desk` | 5 | 0 | OK |
| `tests.b6.test_desk_resume_finalize` | 6 | 0 | OK |
| `tests.b6.test_session_wrapper` | 6 | 0 | OK |
| `tests.b6.test_export_runs` | 7 | 0 | OK |
| `tests.hazards.test_refusal_allowlist` | 23 | 0 | OK |
| `tests.hazards.test_import_graph` | 6 | 1 | FAILED (failures=1) |
| `tests.test_fixture_orphan_census` | 14 | 0 | OK (skipped=2) |
| `tests.test_digest_pin_census` | 19 | 0 | OK |
| `tests.test_schemas` | 43 | 0 | OK (skipped=1) |

Focused total: 272 tests = 268 pass + 1 failure + 3 skips. The final kit check
is the passing re-run, not the earlier generator self-hash experiment. An
additional nine final registration/prepare/physical-gate/installer checks
passed after the final maximum-window/WAIT disk audit. They include an exact
integer-byte agreement check between prepare and the native arm copy/volume
budget, preventing double counting or a smaller installer-side allowance. A final
six-test registration/prepare check also confirms that the precheck and
plan use the identical stream allowance (1e-6 agreement bar), after the
kit row key was corrected from its internal label to the governed pack id.

The census-dependent failure is exactly:
`tests.hazards.test_import_graph.ImportGraphTests.test_a_complete_arm_and_monitor_run_load_no_retired_module`.
A fresh run of the unchanged Rig, with only its committed fake collector,
confirmed:

```text
decision: NULL
reasons: ("instrument REFUSE: the capture's process group was not proven gone: census_exit_3: sysmon request failed with error: sysmond service not found\npgrep: Cannot get process list",)
```

This is the F4 sandbox process-table limitation. No collector/guard was
weakened. The two orphan-census skips are the same sandbox limitation; the
schema skip is the absent optional jsonschema package. The lead reruns the
named dynamic import-graph test outside the sandbox.

The final canonical command is
`JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -B -m unittest discover -s tests`
under a fresh private TMPDIR. It was intentionally interrupted with SIGINT
(exit 130) because it was an earlier source snapshot, launched before the
final disk/receipt/CPU/precheck corrections. It has no completed final test
count or qualification result. Its partial log remains at
/private/tmp/bytes-h-canonical.log; the temporary suite root was removed.
The final-source discovery contains 10,458 cases. The completed final runner
module and required focused modules are the validation for this bounded desk
tooling/input delivery; shared collectors, estimators, replication code and
default inputs remain byte-identical. This uses the repository's targeted
verification allowance for tooling-only work. The lead owns the final
canonical run outside the sandbox. Unclassified failures in the interrupted
older run are not asserted to share the confirmed focused census cause.

The final staged 123-member plan also passes the existing
`scripts/check_b5_chain.py --plan PLAN --no-live-identity` (exit 0, clean true,
errors 0): launch argv, frozen protocol, config selection, lineage tags,
duplicate run/dispatch checks and desk identity power policy. The checker
warns that it ran from the source checkout rather than the disposable view;
this is a disclosed identity warning. The initial manual fixture lacked the
power_policy field and failed that check; replay with the fixture's required
ac_high_power identity passed. No implementation relaxation was made.

Registry enrollment: configs/gates/hazard_refusals.json scans the new script
and adds eleven reviewed refusal/error sites (two PHYSICS, one NUMBER_INTEGRITY,
eight INTERNAL), plus five desk-only dependency inventory entries. Every
printed entry was added with its count and guard; final refusal census has
empty unlisted/stale/miscounted/guard_changed/scope_gaps lists. The import fence
is tests/hazards/test_import_graph.py; no new collection-root import is added.
Fixture inventory tests/fixture_signatures.json needs no new fixture: this
uses existing synthetic seed bundles and an in-process installer stub, with
no new persistent fixture executable. Digest inventory configs/pins/registry.json
needs no new sealed/digest-bearing path; its census is run. Schemas are checked
by tests/test_schemas.py; the existing measurements schema remains unchanged.
No registry beyond the authorized hazard_refusals.json was written.

`python3.13 -B scripts/bytes_mac_kit.py --check` exits 0. The initial attempt
to add workflow text to its generator exposed the generator self-hash in the
out-of-scope source plan_tree.json. Those two local documentation edits were
reverted; the detailed workflow is instead in the authorized registration
README. The kit generator/README/tree and every alpha/beta/gamma implementation
and input remain byte-identical to HEAD (git diff --exit-code check, exit 0).
`git diff --check` exits 0.

## Item 5 — real dry prepare

Exact command:

```sh
PYTHONDONTWRITEBYTECODE=1 python3.13 -B scripts/bytes_h_session.py prepare --measurement-root /Users/edr/code/JouleWise-wt-283-h --session-root /private/tmp/bytes-h-dry
```

Exit 1, physical disk refusal. Exact captured stdout/stderr:

```text
bytes_h_session: not enough disk for the window plus the R6 150 GiB reserve
session_id: bytes-h-20261021T115801002751Z
candidate_t0: 2026-10-21T12:06:00+00:00
maximum_duration_s: 45120; programmed_span_s: 27371
disk: {"derivation": {"estimated_per_copy_bytes": 308543416, "extra_wait_peak_bytes": 28082490435, "extra_wait_raw_bytes": 9360830145, "formula": "ceil(max(max_original_allocated_bundle, max_original_bytes/member_wall_s * longest_planned_member_s)); peak 3 copies (raw + archive + disjoint claim/bound backups); fixed = observed original non-bundle session bytes * max(1, window_max/sum observed member wall seconds); WAIT extra = ceil(max original bytes/wall_s * registered session WAIT budget) * 3 copies", "max_observed_bundle_bytes_per_wall_s": 1300115.2977829832, "max_observed_fixed_session_bytes": 1438707712, "max_observed_original_bundle_bytes": 162971648, "observed_member_wall_sum_s": 16042.009888648987, "peak_copies": 3, "reserve_authority": "BYTES R6 / block-6 design section 15", "reserve_bytes": 161061273600, "session_wait_budget_s": 7200, "time_budget_source": "joulewise.b5.plan: T0_STAGE_CAP_S, PAUSE_LIMIT_S, SESSION_WAIT_BUDGET_S; same minute-rounded window formula", "window_max_s": 45120}, "estimated_footprint_bytes": 145981542042, "member_count": 123, "prepare_free_bytes": 122446086144, "required_free_bytes": 307042815642, "reserve_bytes": 161061273600}
```

No t0 was authored: the printed t0 is explicitly a candidate. The final
required free space is 307,042,815,642 bytes (estimated footprint
145,981,542,042 plus the ruled 161,061,273,600-byte reserve), exceeding the
observed 122,446,086,144 bytes. The arithmetic follows the stored disk
receipt/formula above; no storage was deleted to force a pass. The empty
/private/tmp/bytes-h-dry directory was removed and absence verified, exit 0.

## Decisions I made

- Apply F1 exactly: real installer path, printed plists, lead exit, no watchdog
  change and no collection.active. Keep the arm's census backstop.
- Apply F2 using measured dense weight bytes, only the two bracketing receipts,
  and the same measured-spread margin as every other row. Never count it.
- Keep file identities provisional as execution-stack pins; no model inference
  or quiet-machine measurement in this agent session.
- Preserve all 123 planned members, including all reference/scaffold and
  failed/skipped rows; no model/roster/registered threshold choice is made.
- Use the governed b6_layout pack identity and existing fourteen-binding
  interface in a disposable session view to bridge metadata representations,
  preserving repository source bytes and existing replication paths.
- Reuse existing registration-dir parameters without changing unused B6 lanes.
  Keep complete kit inputs outside the loop registry.
- Include raw/archive/partitioned backups and fixed artifacts in disk planning;
  apply the R6 reserve and native per-volume copy calculation consistently.
- Use the native request-overlap support and whole measured CPU quanta; never
  guess a boundary quantum's within-interval CPU distribution.
- Emit nulls and provenance flags rather than fill unobserved floor/census,
  calibration, skipped-row or fixed-work measurements. Registered T10/T_phase
  remain null. C5 candidates never edit registrations.
- Keep generated kit docs unchanged to preserve its self-hash without an
  unauthorized source-tree update; registration README owns this run kit.
- Leave all files uncommitted and the lead-owned .venv untouched, per F3/F5.

## NEEDS_RULING / NEEDS_SCOPE

None. F1-F5 are applied. No further write scope is requested.

## Residual risk and exact next step

The lead must clear the physical storage gate, provide the authentic matching
calibration ledger in the actual measurement checkout, review this diff and
rerun the listed census-dependent checks outside the sandbox. Then rerun a
fresh prepare (the t0 allowance is the DriverLane launch lead), inspect its
STAGED plan, run install as the lead's last act, and exit. The worker never
runs install. Actual H records, missing measured floor/CPU derivations and
native verdict/backup stamps determine whether C5 can produce candidates.
Final live verification, commits/push and registrations remain lead-owned.
