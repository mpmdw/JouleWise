# Item-H inputs and session runner — non-claim

Nothing here enters `configs/b6/packs` or the block-6 queue. This is neither
an issued C4 identity nor a C5 registration. The governed kit pack name is
`bytes-mac-check`; its source campaign directory is `bytes_mac_check`.

## Item-H session runner

Run `python3.13 -B scripts/bytes_h_session.py prepare --measurement-root R
--session-root S` as one command. It reads local model payloads, collects desk
identity with R's interpreter, and stages the existing window writer in S.
It prints the candidate t0, maximum duration, derived footprint and free disk.
The physical disk check includes the R6 150 GiB reserve. Model absence and
insufficient space refuse; identity/record differences print flags. If a
calibration ledger or another required record is absent, `INPUTS_ONLY` and
`plan.not_written` retain the inputs; there is no installable plan. A printed
candidate t0 is not an authored plan when preparation stops.

The disposable `S/measurement` view reads R's code/configs and copies its
calibration ledger and head pin independently. Its kit tree adds only the
existing fourteen launch bindings and uses the governed `bytes-mac-check`
pack directory spelling; all 123 members/configs/manifests remain unchanged.
The repository tree stays fixed. `staging/measurement-view.json` records both
tree hashes and the binding-template source. Source checkout record/identity
differences remain flags. Dedicated runs, custody, backups and desk outputs
are under S; no pack joins the replication queue.

The lead's final action is `python3.13 -B scripts/bytes_h_session.py install
--session-root S`, then exit the agent session. This calls the driver's exact
installer interface, including `--courier-bin scripts/b6_courier.sh`, and
prints the two installed plist paths under `~/Library/LaunchAgents`. Those
plists contain the absolute `--plan` path read by the watchdog's installed
agent fence. No `collection.active` marker is written. The in-chain agent
census remains the backstop. Automated tests stub this installer; no live
installation is part of this implementation.

After the terminal record, run `python3.13 -B scripts/bytes_h_session.py desk
--session-root S`. It calls the real harvest CLI with `--non-claim` and this
kit's registration directory, then writes `MEASUREMENTS.json` and invokes C5.
The native `.runs.csv`/`.session.json` remain together. Every unobserved field
is null with a named flag; gates exit 1 when a required measurement is absent,
and `desk.json` records that unavailable outcome. This never substitutes the
planning row or another pack's registered T10/T_phase. The native session id
is the bracket id (printed plan id plus `-calibration`).

A floor/census derivation that native records cannot supply may be retained
in `S/receipts/regimes.json` or `cpu_contention.json`. Each has
`schema_version: joulewise.bytes_h_regimes.v1` or
`joulewise.bytes_h_cpu_contention.v1`, `non_claim: true`, the native
`session_id`, a nonempty `derivation`, and `values` matching the corresponding
MEASUREMENTS object below. The runner hashes each receipt. The regimes receipt
supplies only F_min_j, census_resolution_w and outside_power_w; the operative
bound comes from the native session sidecar. The CPU receipt supplies only
w_j_per_cpu_s and c_q_cpu_s. Keep their raw derivation evidence with them.
These are measured inputs, never fields filled from planning assumptions.
Missing verdict/backup journal stamps also leave fixed_desk_s null.

The kit-local registration directory contains file identities for eleven
sources, acceptance/smoke inputs, and reproducible planning sizing. Its 8-bit
row is explicitly `sizing.planning_bound_interpolated` (lead F2): interpolate
each pilot repeat and load time linearly in measured weight-file bytes between
the bracketing dense Qwen3 pilots, then use the same observed-spread margin.
The row records both source receipts, bytes, fraction and formula. Planning
allowances never enter the measured desk receipts and do not issue C4/C5.

## Reproduce the file identities

```sh
PYTHONDONTWRITEBYTECODE=1 python3.13 -B configs/campaigns/bytes_mac_check/registration/derive_identity_pins.py --runtime-python /Users/edr/code/JouleWise-wt-283-h/.venv/bin/python
```

The generator resolves all 123 planned dispatches and hashes eleven local
model sources through `joulewise.provenance.model_artifact_identity`. The
per-file inventory records lexical paths, resolved paths, byte counts and
SHA-256s. Runtime package observations use the named interpreter. No model
was executed: empty execution stacks remain `runtime_stack_unobserved`.

`acceptance.json` preserves the current block-6 calibration input and its
source hash and derivation; its operative stop remains null. The kit-local
smoke map copies the existing selection without altering the global map.
After prepare creates the view, `b6_precheck.py --pack bytes-mac-check
--measurement-root S/measurement --registration-dir
S/measurement/configs/campaigns/bytes_mac_check/registration ...` uses its
canonical pack name and the same sizing row. The existing CLI already
forwards the registration directory; no replication lane/default path changes.

## Reproduce planning sizing

```sh
PYTHONDONTWRITEBYTECODE=1 python3.13 -B configs/campaigns/bytes_mac_check/registration/derive_sizing.py --session-root /Users/edr/night-b6/sessions/r4-alpha
```

This reads the archived block-6 records and never restores, edits or
compresses them. The original file sizes come from the compression journal;
file sizes are rounded upward to each volume's allocation quantum and never
below their current allocated size. The peak budget covers raw bundles,
retained archive copies and both backup streams on S's volume. Claim/bound
backups partition the roster, so their combined payload adds one copy: three
peak payload copies total. Fixed session
bytes come from the observed original non-bundle footprint, scaled by the
ratio of the maximum window (including T0, pause and WAIT) to the observed
member-time sum (at least one). The registered session-WAIT budget also adds
`ceil(max observed original bundle bytes/wall_s * SESSION_WAIT_BUDGET_S)` per
raw/archive/backup copy: WAIT can retain a live member sampler. Pauses occur
between members; their continuous meter/monitor cost is in the fixed allowance. The
150 GiB reserve is BYTES R6 / block-6 design section 15. The plan supplies a
per-copy budget to the existing native arm, which multiplies by actual
copies per device; the preparation check covers all three peak copies.

The sizing evidence preserves all 125 successful observed member receipts,
the source clock/stage/compression hashes, and request/stream/wall endpoints.
Full member allowance is `(mean pilot request + pilot load + maximum observed
B6 non-request member time) * (1 + margin)`. The old load is retained in the
residual as a conservative envelope; it is not silently subtracted. The
shared margin is the largest observed request max/min minus one over pilot
groups and archive references. This applies to the 8-bit interpolation too.

Stage overhead is the maximum observed collection-stage duration minus its
member-wall sum, including failed member spans so they are not charged a
second time as overhead. Shell stage endpoints use integer seconds; their
last bucket is [stamp, stamp+1). Fixed work is the union of disjoint archived
non-collection intervals. The span adds the 22 collection overheads and the
registered 23 x 60 s settles. T0/pause/session-WAIT budgets are added by the
unchanged window writer, independently of this programmed span.

`programmed_span_s`, `T_stream_max_s` and the disk estimate are planning
bounds, never measured H numbers. The source's scaffold metadata has two
representation gaps (empty launch bindings and a list of external-input
mapping keys). Only the disposable session view repairs those representations
from the existing launch interface and actual collection manifests. The
source kit and every planned dispatch remain byte-identical. The generated
kit README/generator are deliberately unchanged: changing the generator's
self-hash would require a plan_tree.json write outside this task's scope.

## Measured desk receipts

The generated kit README defines every v1 measurement field. In addition:
pre-arm free bytes are read from the native arm's disk targets, never replaced
by the earlier prepare snapshot; the signed clock fit is the worst absolute
per-member fitted slope, and the live frequency word is the worst absolute
signed observed word. Missing or malformed native observations remain null with flags. Contention
uses the existing native request-overlap support (`contention.flags`): C sums
`outside_total_cpu_s_per_s * elapsed_s` for each whole overlapping census
quantum, and k counts those same quanta. Sub-quantum CPU work is never guessed
by prorating a boundary interval. A missing request span, coverage gap or
duplicate interval leaves both fields null.
Fixed retained bytes include the final desk outputs; C5 is rerun only if that
integer allocation changes, so its final hash binds the final measurement file.

All journals and optional floor/CPU derivation receipts are hashed and retained
with the harvest. Failure/skipped rows remain explicit. A C5 program-input
failure is an unavailable candidate, never success and never guessed sizing.
No install, collection, calibration issuance or final hardware gate is implied.
