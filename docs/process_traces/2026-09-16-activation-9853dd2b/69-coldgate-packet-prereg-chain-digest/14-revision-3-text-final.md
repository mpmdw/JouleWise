# Revision 3 text to be appended verbatim to configs/calibration/preregistration_d079_epoch_25g83_rev1.md after revision 2's last line (ruling 69 Q2 as amended B2, B3, B5, B7; the placeholder is filled with the merged chain digest in the same commit)

---

# Revision 3 (2026-09-17, cold-gate ruling 69, packet 69)

STATUS: cold-gate ruling 69 (packet 69, activation 9853dd2b), paired Opus
refutation 12 and magistrate synthesis 13; recorded by the magistrate; not a
magistrate amendment (rule 11)

Revision 1 above is sealed and revision 2 stands as written. Not one word of
either is edited here. This revision does one thing and nothing else: it
re-fills the `[CHAIN_SHA256]` field that revision 1 lists under "Fields filled
at commit" as "a fact that does not exist yet; none is a scientific choice, and
filling them does not reopen any rule above." Re-filling a field the sealed
text designates non-scientific reopens no sealed rule; the authority for the
re-fill is this ruling.

## Provenance

Cold-gate packet 69, sha256
a77c4ab3eb64c1f4da9f344a2fc247d18e1798be1c0c44e9fb59dc8f100410b0, at
`docs/process_traces/2026-09-16-activation-9853dd2b/69-coldgate-packet-prereg-chain-digest/00-PACKET.md`,
with its exhibits A-F, adjudicated by the cold Fable judge in
`10-coldgate-fable-ruling.md` of the same directory. The chain digest
history is exhibit B; the generator literal comparison is the judge's
probe P3, reproduced independently by the paired Opus refuter.

## The one change

Revision 1, "Sample.", pins the chain at the digest beginning b8bf5b0a85bb.
For every capture night opened after this revision lands, that sentence is
read with the digest below in place of the sealed value:

Chain digest in force (revision 3): <CHAIN_SHA256_AT_ARM_HEAD>

That value is the SHA-256 of `scripts/night_chains/calibration_derivation_only.zsh`
at the committed head the night is armed from, written by the magistrate in
the same commit that records this revision, and verified three ways: the test
`tests/test_preregistration_chain_digest.py` (ruling 69 Q4) fails unless the
line above equals the tracked chain's digest; `python3
scripts/gen_derivation_night.py --check` passes at that head; and the plan
sidecar the night gate reads at t0 refuses `night_chain_digest_mismatch` if
the bytes move afterwards.

## Why no science rule moved

The chain changed on 2026-09-17 (PR #350 and the end-of-window abort lane)
to: bound every governed custody read by a budget (`--custody-budget-s`) and
a deadline (`--custody-deadline-epoch-s`, window end minus 10 s); fold the
separate pre-reserve readiness command into `--pre-reserve-strict` on the
reservation itself; add a verify-only reservation probe (`NIGHT_VERIFY_ONLY`);
export a refusal-document path and a custody-budget marker; and bound the
session abort to one custody read under one budget.

One consequence is stated so it cannot be read as hidden: a governed
custody read that cannot be bounded within its allowance (CUSTODY_BUDGET_S,
default 120 s, threaded from the plan by scripts/run_night.py) now refuses
in a typed, logged way where the sealed chain could block without limit.
Every such check runs in the ledger lifecycle's begin, abandon or finalize
step, never between the sampler's spawn and its teardown, so no refusal can
truncate or perturb a capture; its worst case is a fully captured slot whose
ledger row is left unfinalized (slot_refused, session open) for desk
recovery. That is a stop condition, not a tuning: it changes no value any
capture records, and it can only subtract a slot, never admit one the sealed
rules exclude.

Evidence, verifiable at the arm head: the generator's timing literals
(PRE_REGISTERED_SLOT_COUNT 12, DEFAULT_SETTLE_S 600, DEFAULT_SLOT_CADENCE_S
600, DEFAULT_SLOT_CAPTURE_BUDGET_S 480, receipt class DIAGNOSTIC_NO_PACK) are
byte-identical between the sealed head 3015cb39 and the arm head; the
runsheet's generated region changes over the same interval only in prose and
in the rendered chain digest, not in any rendered constant (packet 69 exhibit
C); `gen_derivation_night.py --check` is the tripwire that forces that region
to be re-emitted after any chain edit, and its passing is not itself evidence
about the constants; the chain still performs one settle after the
reservation and before slot d01, anchors each next start to the actual slot
start, aborts window_exhausted without compressing a slot, runs the writer
with --derivation-only and --power-policy ac_high_power, and omits
--sleep-display-before-capture.

## What this revision does NOT change

The epoch tuple, the powermetrics and MLX pins, the ledger baseline sentence,
the sample size and window shape (one 600 s settle, 12 slots at 600 s
start-to-start cadence, fixed order, agent-free), the protocol id, the
membership, exclusion, stopping and analysis rules, V3, the known-conditions
section, revision 2's equivalence rule and both of its branches. It authorizes
no window and licenses no measurement.
