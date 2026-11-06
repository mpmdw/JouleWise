# Sol burn review — ALIGN v4 W1 blockers

Review date: 2026-11-06. Review head before this repair: `b2e60ebd`. Scope:
`w1_disk_gate`, R1-derived `sizing_b5.json`, WP11 identity pins, WP18 X/Y,
and the R0 effort instruction. This review used repository files and synthetic
temporary data only; it did not read experiment custody, archive, restricted,
or model directories.

## Verdict

**BLOCKED pending Mac-owned inputs, with three additional fail-closed repairs
landed here.** The existing disk-gate wiring is suitable for the first arm, but
the branch would have admitted (1) a stale sizing file, (2) an unbound WP11 pin
document, and (3) WP18 digest strings with no retained fixture bytes. The R0
message also named the wrong completion boundary. These four gaps are repaired
below. W1 remains deliberately blocked on the values already listed by the kit:
WP18 X/Y, the selected R0 D-ladder rung, R1 measurements/plan, and the WP15
entrypoint (`scripts/align_v4_kit.py:89-111`, `:116-139`).

## Findings and dispositions

### 1. `w1_disk_gate` wiring — no production-code gap; synthetic-test repair

The install path first rechecks W1 readiness and AC powermode, then calls the
disk gate, writes its receipt, and only then invokes the shared installer
(`scripts/align_v4_session.py:85-96`). The CLI makes the R0 desk config required
(`scripts/align_v4_session.py:99-105`). The gate itself samples free space
against exactly 80,000,000,000 bytes and re-inventories every configured
offload; any failed row makes the receipt fail
(`joulewise/align/r0_host.py:195-212`, `:243-266`). This is fail-closed at the
arm boundary because the wrapper accepts only `status == "pass"`
(`scripts/align_v4_session.py:59-82`).

The regression test previously copied the production config's host disk path,
which could make a supposedly synthetic test stat a machine-specific path.
It now overrides `disk_path` with its temporary directory before exercising the
real gate (`tests/align/test_v4_kit.py:751-780`). Production bytes and behavior
are unchanged by this test-only correction.

### 2. `sizing_b5.json` — BLOCKER fixed: stale plan/size pair admitted at arm

Derivation is sound: member seconds come from the validated R1 W1 plan; the
code computes the maximum member duration, programmed span, and two-copy disk
estimate while pinning the W1-plan and pilot-3 disk-law sources
(`scripts/align_v4_kit.py:306-354`). Before this review, however,
`require_sizing` checked only that both files existed. A changed `w1_plan.json`
could therefore be paired with an old `sizing_b5.json` after prepare and still
pass the install-time readiness call.

The readiness gate now parses sizing provenance and requires its path and
SHA-256 to equal the current W1-plan bytes; malformed or stale provenance
refuses with a regeneration instruction (`scripts/align_v4_kit.py:360-377`). A
synthetic mutation test proves that an initially valid pair passes and a
one-byte plan change is refused (`tests/align/test_v4_kit.py:718-730`). The
derivation and all happy-path numeric assertions remain unchanged: 26,927 s
programmed span, 44,640 s window maximum, 1,800 s maximum member, and 18.71 GB
per copy are still asserted by `tests/align/test_v4_kit.py:680-700`.

### 3. WP11 identity pins — BLOCKER fixed: receipt did not bind pin-file bytes

The prior validator correctly compared all six shard names, hashes, sizes, the
folded artifact digest, source root, revision, and verified status
(`scripts/align_v4_kit.py:239-284`). It did not compare the
`local_file_verification.hf_pins.sha256` receipt to the actual committed pins
file. Thus the identity could be internally consistent with a changed pins
object while its claimed pin-document receipt was stale.

Both W1 readiness and prequalification now pass the raw committed pin bytes.
The validator requires the receipt's path/repository/revision and exact SHA-256
to match those bytes (`scripts/align_v4_kit.py:256-263`, `:380-388`;
`joulewise/align/prequal.py:496-503`). Synthetic mutations of the receipt digest
and raw bytes are refused (`tests/align/test_v4_kit.py:540-553`). No model files
are opened by this check.

### 4. WP18 X/Y — BLOCKER fixed: digests were orphan metadata

The branch required positive `max_turns` and 64-hex fixture digests
(`scripts/align_v4_kit.py:169-175`), but nothing required the fixture bytes to
exist or match. A plausible digest string could therefore satisfy readiness,
leaving the first window without auditable pilot-7 token identity.

Readiness now names fixed, repository-relative X and Y fixture locations
(`scripts/align_v4_kit.py:41-44`) and requires each committed file's SHA-256 to
match its WP18 input (`scripts/align_v4_kit.py:287-303`, `:380-388`). The
fixtures are intentionally not fabricated here: the Mac owner must derive and
commit them from the two historical members named in the existing message.
Synthetic files prove success, tamper refusal, and missing-file refusal
(`tests/align/test_v4_kit.py:626-642`).

### 5. R0 effort message — BLOCKER fixed: wrong dependency boundary

R0's ladder is the producer of the effort selection; unrelated R0 checks do
not select that field. Saying “until R0 passes” could leave the operator waiting
on an unrelated failed check even after the D ladder had recorded a valid
selection. The message now requires precisely `status=pass` and a selected D
ladder rung, states that unrelated checks do not gate this field, and retains
the allowed `xhigh`, `medium`, and `low` validation
(`scripts/align_v4_kit.py:128-129`, `:176-179`). The test verifies both the
operator message and rejection of an unruled value
(`tests/align/test_v4_kit.py:615-624`).

## Equivalence and remaining first-window work

Focused tests ran **109 tests, 0 failures, 6 skips**. The skips are the existing
optional tokenizer/model tiers; no live or hardware claim is made. Generated
kit bytes were regenerated because the corrected R0 instruction is embedded in
the plan's pending-reasons metadata; the resulting identity-pins tree digest was
regenerated with it. Runtime member configurations, sizing arithmetic, and disk
gate behavior were not changed.

The exact Mac-owned next steps are:

1. Fill WP18 X/Y with the two recorded pilot-7 turn counts and commit the two
   token-id fixture files at the paths enforced above.
2. Fill `R0.reasoning_effort` from a passing D-ladder receipt's selected rung.
3. Complete R1, commit the filled W1 plan, regenerate the kit, and retain the
   matching `sizing_b5.json`.
4. Fill WP15's runtime entrypoint, run `scripts/align_v4_kit.py --check`, then
   run the offline prequal. Hardware/native gates remain separate and must run
   only in the lead-controlled quiet-machine workflow.
