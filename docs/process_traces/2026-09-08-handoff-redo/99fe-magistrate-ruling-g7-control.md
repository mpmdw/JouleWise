# Magistrate ruling — D-176 seat 4, G7 presentation semantics (2026-09-08 ~17:20 PDT)

Question (seat 4 intake, 99fd F1): synthesis 99ey/13 item 8 says "present the rehearsal GO to a production-plan launcher
after the night"; contract §6 says G7 presents the six-key rehearsal-class receipt and requires custody-wide absence of
consumption and chain.started — which the completed rehearsal custody cannot satisfy.

Ruling: G7 is a SEPARATE production-plan CONTROL, never the completed rehearsal custody.
1. Control custody: `~/night-custody/<rehearsal_window_id>-g7-control/` (a SIBLING_CHILD of the night-custody parent, basename
   = the rehearsal window id + `-g7-control`), holding a production-class plan (`TRANSACTION_PACK`, an UNPREFIXED window id,
   the production clone's measurement_root/head, purpose CAMPAIGN_TRANSACTION in its authorization record) and nothing else
   at the start. The absence predicates (no consumption record, no `chain.started`) apply to THIS custody.
2. Two presentations, both recorded in `<control>/night/g7_refusal.json` (create-once, 0600): (a) the six-key rehearsal-class
   receipt per §6 (the contract's form), and (b) the completed rehearsal's own 26-key GO bytes copied into the control custody
   as `<control>/night/presented_go_receipt.json` — presented to the production launcher, which must refuse on purpose/class
   (`rehearsal_purpose_on_production_id` / class refusal) AFTER digest authentication of the bytes and BEFORE any ARM verify.
   Both refusals must be the FIRST refusal recorded (no prior consumption attempt in the control custody).
3. The launcher invocation for G7 uses the eight-flag argv with the control plan and the presented receipt; no ARM receipt is
   required to exist for the control (the class refusal precedes ARM verify) — if the launcher requires an ARM path to parse,
   pass a nonexistent path inside the control custody and assert the refusal is the class refusal, not the missing ARM.
4. The rehearsal bundle's G7 evidence is a locator {path, sha256} of `<control>/night/g7_refusal.json`; `t0_rehearsal`'s G7
   acceptance (~:790–793) re-reads those bytes, verifies the digest, and requires: two refusals, both class/purpose, both
   first, control custody free of consumption and chain.started at presentation time (recorded in the artifact).
5. The completed rehearsal's consumption and capture records are preserved untouched.

## Addendum (2026-09-08 ~17:35) — answers to seat 4's F1/F2 (99fh)
6. PRE-ARM ADMISSION (F1): the consumer's order for a TRANSACTION_PACK launch becomes: read the pinned plan bytes and
   the presented GO bytes → authenticate the GO's digest and exact 26-key shape → ADMISSION on class/purpose against the
   plan (a T0_REHEARSAL purpose or a rehearsal-prefixed window id presented to an unprefixed production plan refuses
   `launch_go_receipt_invalid` detail `rehearsal_purpose_on_production_id`; the six-key rehearsal receipt presented as a
   GO refuses on shape as `launch_go_receipt_invalid` detail `receipt_class`) → THEN ARM verify → the remaining ordered
   GO checks. A missing ARM receipt therefore cannot mask the class refusal. scripts/launch_window.py parses all eight
   flags but the consumer performs admission before touching the ARM path. Regression: absent ARM + rehearsal GO on a
   production plan → the class refusal, not launch_consumption_missing.
7. G7 ARTIFACT SCHEMA (F2): `joulewise.pack_night_g7_control.v1`, exact keys: `schema_version`, `control_custody_root`,
   `rehearsal_window_id`, `control_plan_sha256`, `presented` (exactly two objects, exact keys `kind` ∈
   {rehearsal_receipt, rehearsal_go}, `path`, `sha256`, `refusal` {`reason`, `detail`}, `first_refusal` (bool),
   `presented_monotonic_ns`), `absence` {`consumption_absent` (bool), `chain_started_absent` (bool),
   `checked_monotonic_ns`}, `verdict` ∈ {PASS, FAIL}. PASS iff both presentations refused with the class/purpose reason,
   both first, both absence flags true. §6's eight-key form is SUPERSEDED by this schema (dated in §10.5).
8. BUNDLE LOCATOR (F2): the rehearsal bundle's closed record-name set gains `g7_control` = {`path`, `sha256`} pointing at
   `<control>/night/g7_refusal.json`; the loader authenticates the bytes; G7 acceptance re-validates the schema and the
   PASS conditions from those bytes only.
9. Scope: seat 4 gains scripts/launch_window.py, joulewise/arm_readiness.py (admission only; the census seat's edits
   must be preserved — seat 4 resumes AFTER the census seat lands), scripts/rehearse_t0_unattended.py and its test.
