# Cold-gate packet: D-176 seat 2 rulings — the frozen PRODUCTION_CUSTODY_ROOTS census and the driver's input locators

Assembled mechanically by the interactive magistrate at 2026-09-08 ~13:20 PDT. Trigger: design-bearing contract
amendments on the unattended pack-night launch path (D-176), returned as NEEDS_RULING by the implementing seat
(exhibit A, F1/F2). Checkout = main at the D-176 contract merge (docs/contracts/pack_night_go_receipt.md governs;
read §§2–6, §7.1 seat-2 row, §10 S4, §10.1, §10.2 if present).

## Q1 — PRODUCTION_CUSTODY_ROOTS (contract §6/§10 S4)
The contract requires "a NEW frozen PRODUCTION_CUSTODY_ROOTS constant in joulewise/arm_readiness.py" as the common
source of the production-root census: G6 (joulewise/t0_rehearsal.py ~:779–787) derives `bundle.production_roots`
from it, and the consumer refuses a T0_REHEARSAL purpose whose plan `measurement_root` or `custody_root` lies under
any production root. Today the roots are CALLER-SUPPLIED manifest entries {role, path} (scripts/rehearse_t0_unattended.py
~:149–175). The contract does not enumerate the roots. Facts to reconcile: the magistrate watchdog's mutable root is
`~/night-custody/magistrate/` (docs/process/MAGISTRATE_WATCHDOG.md:3); window custody dirs live under
`~/night-custody/<window-id>/` and the REHEARSAL night rehearsal-20260909 ALSO lives there
(docs/process_traces/2026-09-08-handoff-redo/27-scout-v5-readiness-astra-report.md:296), so "custody parent" cannot be
the whole of `~/night-custody`; the measurement clone (runs root) is per-clone (`/Users/edr/JouleWise-measurement-v5-<date>-<sha>`),
so a literal path constant would go stale per clone; the iCloud backup default root is the JOULEWISE_BACKUP_ROOTS
default in the paper producers; the calibration ledger custody has its own root (grep calibration_ledger.py /
calibration custody store defaults). Charge: rule the SHAPE of the constant (roles → how each production path is
derived: literal, home-relative, plan-declared, or clone-derived), the exact disjointness predicate (path-prefix after
resolve? realpath? symlinks?), how a rehearsal id/roots pass while production roots are a superset parent, and how G6
reads it — such that the constant is frozen (a reviewed diff to change) yet true across clones. Name the roles and
their derivation with file:line evidence.

## Q2 — the driver's governed lookup of pack_root, the selected ARM receipt, launch_manifest and the preparation entry
The exact v3 plan carries pack identity and record bindings (sha256s) but no LOCATORS for pack_root, the ARM receipt
to present, the launch manifest, or the preparation entry point; run_night today executes chain_path directly, while
the launcher needs explicit --pack-root/--arm-receipt/--launch-manifest paths (scripts/launch_window.py ~:39–58).
Charge: rule a deterministic, ambiguity-refusing lookup — options: (a) the v3 plan carries explicit absolute
locators inside custody_root for each (a wire amendment, §10.3); (b) locators are derived from custody_root by fixed
relative names (name them; refuse if absent/duplicated); (c) the ARM receipt is never "selected" — it is the one the
driver's own ARM step wrote this night under a fixed name, and any other is refused. State ARM-before-GO sequencing
(preparation → ARM verify → GO issue → launcher argv) with the exact files each step reads/writes and the refusal
for each missing/duplicate/mismatched input. Prefer the option that makes forging or substituting an input a
detectable digest mismatch rather than a lookup ambiguity.

Write the ruling to ./coldgate-packet/10-coldgate-fable-ruling.md (under 900 words, numbered decisions Q1.1…/Q2.1…,
one-line verdict last). NOT EXECUTED for anything unverifiable.
