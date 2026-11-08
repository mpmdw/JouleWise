# Item-H inputs and session runner — non-claim

Nothing here enters `configs/b6/packs` or the block-6 queue. This is neither
an issued C4 identity nor a C5 registration. The governed kit pack name is
`bytes-mac-check`; its source campaign directory is `bytes_mac_check`.

## Item-H session runner

Run `python3.13 -B scripts/bytes_h_session.py prepare --measurement-root R
--session-root S` as one command. It reads local model payloads, collects desk
identity with R's interpreter, and stages the existing window writer in S.
It prints the candidate t0, maximum duration, derived footprint and free disk.
The physical disk check uses statvfs `f_bavail * f_frsize`, purgeable excluded,
and refuses only below P = 86,236,568,521 B under H-DISK-RULING (283e9802).
It prints every term, c = 2, free bytes and purgeable bytes (null with
`disk.purgeable_unreadable` if the volume capacity API is unreadable). Model absence and
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
below their current allocated size. To regenerate only the ruled disk terms
from committed evidence while preserving the fixed allowance, run:

```sh
PYTHONDONTWRITEBYTECODE=1 python3.13 -B configs/campaigns/bytes_mac_check/registration/derive_sizing.py --disk-only
```

H-DISK-RULING (activation 283e9802, 2026-10-21) adopts
`P = c * (B + WAIT) + fixed`, with no reserve. Each model contributes its own
count times stream allowance and count times member-wall allowance. The
reference stream allowance uses the mean reference request plus the maximum
observed non-request stream time, with the same observed-spread margin.
Multiply the summed stream allowances by maximum observed bytes/stream second,
and the summed member-wall allowances by maximum observed bytes/member-wall
second. Round each complete basis up once; B is their maximum. WAIT uses the
stream rate times the registered 7,200 s, rounded up once. Rates and products
use exact rational arithmetic from committed JSON decimal values.

For the committed evidence, stream basis = 27,802,317,346 B and wall basis =
26,878,191,539 B, so B = 27,802,317,346 B. WAIT = 13,292,701,363 B per copy.
The two physical copies are raw plus the roster-partitioned rsync backups;
the harvest archive is an APFS `cp -c` clone. Fixed artifacts retain the
committed 4,046,531,103 B, originally derived from the non-bundle footprint
scaled by maximum window / observed member-wall sum (at least one).
Thus P = 2 * (27,802,317,346 + 13,292,701,363) + 4,046,531,103 =
86,236,568,521 B. This ruling governs H only; BYTES pass R6 goes to J/C5.

H-DISK-RULING addendum 1 encodes P in the native arm's existing caller fields.
Its three budgeting targets each use the whole roster, while the physical
backups partition one roster copy. H uses q = floor(2B / (3 * 123)) =
150,690,066 bytes per member. The remainder is 338 B; headroom =
338 + 2 * 13,292,701,363 + 4,046,531,103 = 30,631,934,167 B.
Thus native total = 3 * 123 * q + headroom = P exactly. This is a budget
encoding derived from P, recorded in `session.json.disk.native_arm_budget`
and printed with `disk.budget_encoded_from_p`; q is not a physical per-copy
member estimate. The registered physical estimate and native driver/writer
remain governed by their existing interfaces.

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

Before harvest, desk prints session-volume `free_at_arm_bytes -
free_at_desk_start_bytes` beside c = 2, and retains it in `desk.json.disk`.
The arm value comes only from a matching-device native arm receipt; if absent,
allocation is null with `disk.arm_free_unavailable`. Desk-start free is sampled
once before desk outputs; later harvest allocations never replace it. This
whole-window drawdown includes every writer and does not add a refusal.

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
