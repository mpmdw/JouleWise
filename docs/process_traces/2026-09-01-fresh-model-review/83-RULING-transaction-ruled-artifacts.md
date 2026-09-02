# 83 — Magistrate ruling: TRANSACTION-RULED-ARTIFACTS-01 design (pre-decision three-seat consult)

Date: 2026-09-01. Seats: Sol xhigh (`79-sol-consult-txn.md`), terra xhigh
(`80-terra-consult-txn.md`), blind Fable (`82-fable-blind-consult-txn.md`);
all read-only on `main` @ `3b0e23f0`. Lieutenant triage that framed the
questions: `76-opus-triage.md`. Synthesized by the magistrate (Fable), who
was not a seat.

## What the seats agreed on (installed as ruled, no dissent)

1. **All three artifacts are absent at HEAD** — `campaign-close.json`
   (zero hits outside the kernel row), the A1 fixation literal + guard
   (prose only: `tests/test_receipt_histsem.py:237-241`, runbook `:189-192`),
   and the A6 window CLOSE (only the OPEN side — the marker's exactly-one
   derivation head, `joulewise/arm_readiness.py:11265-11270,11384-11386` —
   and a reason-code vocabulary entry, `:202`, `arm_readiness_evidence.py:2356`).
2. **The triage's "NR-13 absent" is wrong.** The sentinel guard IS landed
   in shell: `scripts/window_status.sh:34,95-107`, regression
   `tests/test_window_status_guard.py:49-86`. It guards only that script's
   `git add/commit/push`; nothing in the repo guards a bare `git commit`.
3. **Neither `order_manifest.json` (members, `run_campaign.py:205`) nor
   analysis-manifest `arms[]` (scientific A/B cells,
   `analysis_manifest_v3.py:3124-3137`) is the transaction arm census.**
   "Arm" carries three meanings in this codebase; A6/NR-8's arm is the
   arm-readiness arm (`generate_arm_receipt`, `arm_readiness.py:8182`).
4. **The A1 guard cannot live in CI or the arm gate** — CI observes a bad
   commit after it exists; no arm runs after the close. It must execute at
   commit time, custody-external, with a committed test as the durable
   loud-fail and a verifier at sentinel-off.
5. **The kernel row is stale**: still spelled `_v4`, `dependencies: []`,
   cites `window_runbook.md` §11 (duration margins, `:2155`) where the
   close-out text is §12 (`:2222-2240`).

## Rulings

**R-1 (question a — the census and "last consuming arm").** The
authenticated family-publication marker's `members[]` — built only from the
registry roster (`arm_readiness.py:11323,11334-11338`; registry
`successor_pack_ids`, `d117_row_registry_v2.json:532-536`) — is the SOLE arm
census. No new census artifact (terra's `campaign_arm_plan` is declined: it
would add a second authority to a roster the marker already authenticates).
Each roster pack is consumed exactly once (`arm_receipt_unsuperseded`,
`:9655-9661`), so the campaign has exactly `len(members)` consuming arms.
At arm-issue time the current arm is LAST iff it is the sole roster member
without a completed launch lineage (arm receipt + `.consumed.json` +
`-completion` receipt, `:9700-9720,9966-9975`). After the fact, the close
record names the last consuming arm as the consumption receipt with the
greatest `consumed_at_monotonic_ns` once every member holds a completion
receipt; the two definitions must agree and the validator asserts it. The
gate learns closure from PRESENCE of `campaign-close.json` in the transaction
custody root: present-and-valid → refuse every later arm with a new
custody-class reason code `readiness_r1_campaign_closed`; present-and-invalid
→ refuse (fail closed). Timestamps never decide closure.

**R-2 (question b — where the A1 guard executes).** Outside the tree, at
commit time. A tracked `scripts/commit_freeze_guard.py` with two
subcommands: `pre-commit`, installed by the runbook's C11.1 step into the
measurement checkout's `.git/hooks/pre-commit` (outside the worktree, hence
not changed-set residue — the NR-13 argument, runbook `:331-334`; Sol's
tracked `.githooks/` + `core.hooksPath` is declined for exactly that
residue reason), refusing — while the sentinel exists and `HEAD ==
attestation_head` — any staged diff that is not fixation-shaped (exactly
`tests/test_receipt_histsem.py`, hunks limited to the literal line and the
guard test, trailer `Campaign-Close-Sha256:` present); and `close-freeze`,
the mandatory H5 step-6 tool that fetches and refuses to remove the
sentinel unless the first commit in `attestation_head..origin/main` is
fixation-shaped and its trailer equals the close digest. The durable
loud-fail is a non-conditional test `test_successor_pinset_bytes_match_fixation_literal`
(absent successor = FAIL, not skip). CI replays the history validator as a
backstop only. Regressions run on a temp repo (`test_window_status_guard.py:36-60`
pattern).

**R-3 (literal name).** `SUCCESSOR_PINSET_SHA256 = "<hS>"` in
`tests/test_receipt_histsem.py` — the file the runbook fixes (`:189-192`) —
never `PINSET_SHA256`: the refresh lane's `^`-anchored regex demands exactly
one such literal (`refresh_receipt_histsem_pinset.py:37-39,428-437`) and a
second would break the D-161 refresh lane. Rendered by a new
`--write-successor-test-pin` (generate, don't type); the reviewer recomputes
independently.

**R-4 (`campaign-close.json`).** Schema id `joulewise.campaign_close.v1`,
create-only with `.sha256` sidecar at `$CUSTODY_ROOT/campaign_close/`
(mirrors the marker's `output_collision`, `arm_readiness.py:11305-11306`).
Written at runbook H5 step 1 (`:1298-1304`). Planned set = marker members;
executed set = per-pack arm receipt + consumption + completion +
whole-window verdict + bracket binding, each `{path, sha256}` of raw bytes;
`changed_set_window {opens_at_head, closes_at_arm_receipt_id,
closes_at_monotonic_ns}`; `predicate {executed_equals_planned, missing[],
unplanned[]}`; `declared_by`, `ed_escape`. Refusals as the blind seat lists
(`82-…` Q1), plus Sol's `boot_mismatch`/`unplanned_arm`. The exact field
list is the S1 contract's to fix inside this envelope.

**R-5 (record order, mechanically).** Hash-chained step records, never
wall-clock: close record → `commit_freeze_close.json {campaign_close_sha256}`
→ `notification.json {commit_freeze_close_sha256, sent_at_utc}` → fixation
commit (parent == `attestation_head`, trailer carries the close digest) →
bookkeeping (descendants). Regression permutations P1-P4 (bookkeeping first;
fixation without close digest; sentinel removed with fixation local-only;
notification naming a different digest) each refuse with a distinct reason.

**R-6 (clarification, not reinterpretation): "freeze-off" in the NR-8 order
is the logical declaration; the physical sentinel is removed at H5 step 6
after the fixation is on `origin/main`** (runbook `:1305,1314-1315`, Sol seat
`nr-seat-sol.md:37`). Consequently the pre-commit guard runs with the
sentinel PRESENT and must admit the fixation shape. Both texts already say
this; the ruling only names the two events distinctly.

**R-7 (NR-13 "refuse-before-write").** `window_status.sh` writes
`WINDOW_STATUS.md` before checking the sentinel (`:59-93` then `:95`). Move
the sentinel check ahead of the file write (S2 scope, one hunk) so the
ruling's literal wording holds; the regression's untracked-write expectation
(`test_window_status_guard.py:49-64`) is updated accordingly.

**R-8 (`_v5` transfer).** All three shapes transfer unchanged under
D-164/D-167; pack ids, custody root, heads, receipt ids are parameters. But
the parameters are hard-coded `_v4` in code, registry, tests and contract:
registry roster `d117_row_registry_v2.json:532-536`; `family_id ==
"d117-v4"` and the three-pack roster in `arm_readiness.py:10773-10778,
10850-10856`; marker/table file names `:76-77`; successor pinset path
`legacy_receipt_histsem_pinset_v4_v1.json` and `SUCCESSOR_PACK_IDS`
(`tests/test_receipt_histsem.py:56-66`); contract
`docs/contracts/d117_step6_confirmation_table.md:44,111,118-130`. RULED:
replace `_v4` with `_v5` (D-164 — `_v4` is never collected; a never-minted
chain member enumerated forever is dead code; the `3×37+1 = 112` allowlist
count is unchanged). Canonical pack-id spelling is the generator's
underscore form (`generate_configs.py:1104,1123`); `v5-artifact-flow.md:9`'s
hyphens are a doc error to fix. This is a NEW prerequisite lane,
`V5-IDENTITY-REPARAM-01`, sequenced FIRST. The `_v4` S-0 clone proof does
not transfer as evidence (D-167 installs a `_v5` re-proof).

**R-9 (sequencing — the blind seat's largest finding).** Every code path
above is outside the 112-path allowlist, so anything merged after the
`_v5` `EVIDENCE_DERIVATION_HEAD` is changed-set residue refusing every arm
(runbook `:322-325`, gate `arm_readiness.py:4726-4733`). All lanes here
therefore gate `V5-DESK-DAY-01`; the kernel row gains that dependency and
`V5-DESK-DAY-01` gains this row as a start dependency. Sessions, serialized:
S0 `V5-IDENTITY-REPARAM-01`; S1 close record + A6 gate (shared custody read
path in `generate_arm_receipt`); S2 fixation guard + R-7. Two code sessions,
not three (Sol/terra's three split the `generate_arm_receipt` edit across
sessions for no gain). `docs/process/state_kernel.json` is in NO session's
scope — bench edits only.

## To Ed (batched, not blocking the build)

1. The `_v5` transaction-custody root name (the `_v4` convention was
   `d117-gamma-YYYYMMDD`, runbook `:1357-1360`) and confirmation that ONE
   custody root persists across every arm and night.
2. Consent to a pre-commit hook installed in the measurement checkout's
   `.git/hooks` at C11.1, and its NR-10 prompt-inventory entry.
3. Whether the D-150a phone notification can leave any receipt beyond
   `notification.json` (only Ed can attest delivery).

## Dissent recorded

terra (new `campaign_arm_plan` census; three sessions) — declined per R-1
and R-9. Sol (tracked `.githooks/`; new `tests/test_receipt_histsem_fixation.py`
carrying `PINSET_SHA256`) — declined per R-2 and R-3. No seat disputed any
ruled NR-8/A1/A6 shape; every ruling above installs a ruled shape or fixes a
parameter — none reinterprets one, except R-6, which is a clarification the
runbook text already carries.
