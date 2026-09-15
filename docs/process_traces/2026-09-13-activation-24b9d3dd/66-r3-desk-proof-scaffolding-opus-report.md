# 66 — Desk-proof scaffolding executed (research 64 steps A1/A3/A5; A2 registry patch and A4 terminal-review commit HELD for cold gate 65) — Opus 5 mechanic, delivered 2026-09-14 ~17:13 PDT

Verbatim final report. Clone `/Users/edr/JouleWise-desk-proof-20260915` (main = origin/main 3b53478a, venv from the lock, tree clean); roots under `/Users/edr/desk-proof-arm-census/` (nothing under night-custody); canonical root untouched (HEAD 1d4045b4, status clean). Two dry-gate refusals recorded verbatim; five corrections to the research report.

---

Done. Report below.

---

# Desk-proof scaffolding — A1 / A3 / A5 executed (A2 and A4 deliberately NOT done)

## 1. What exists now

| Path | State |
|---|---|
| `/Users/edr/JouleWise-desk-proof-20260915` | new clone, 774 MB, branch `main`, tree clean incl. untracked |
| `/Users/edr/desk-proof-arm-census/` | roots layout, 276 KB total |
| `/Users/edr/code/JouleWise` | untouched — HEAD still `1d4045b4`, `git status --porcelain` = 0 lines |

Clone refs after `git remote set-url origin https://github.com/mpmdw/JouleWise && git fetch origin main`:

```
HEAD                     3b53478a330f0d7ab9d5e2657b641b6723d07072
refs/heads/main          3b53478a330f0d7ab9d5e2657b641b6723d07072
refs/remotes/origin/main 3b53478a330f0d7ab9d5e2657b641b6723d07072
3b53478a Activation 24b9d3dd: PR #330 gate records 53/54 ...
```

**Deviation to flag:** canonical's *local* `main` is **behind** GitHub's `origin/main` (`1d4045b4` vs `3b53478a`; `1d4045b4` is an ancestor of `3b53478a`). A plain clone of canonical therefore lands on `1d4045b4` and `HEAD != origin/main`. I ran `git merge --ff-only origin/main` in the clone only — a fast-forward, **no commit object created** — to satisfy the `reviewed_main` identity the parent asked me to confirm. `3b53478a` is one commit after the report's expected `6d2d62d8`.

## 2. A1 — clone + venv

```
git clone --no-hardlinks /Users/edr/code/JouleWise /Users/edr/JouleWise-desk-proof-20260915
python3.13 -m venv .venv                                    # Python 3.13.1
.venv/bin/python -m pip install -c env/mac-measurement-lock.txt -e ".[mac]"
.venv/bin/python -m pip install -c env/mac-measurement-lock.txt charset-normalizer requests urllib3
```
pip exit 0. Only notices: pip-upgrade notice ×2, and `charset-normalizer 3.4.8` is a **yanked** PyPI release (installed anyway; it is what the lock pins).

Freeze diff — **empty** (nothing printed between the two markers):
```
$ diff -u <(grep -Ev '^(#|[[:space:]]*$)' env/mac-measurement-lock.txt | sort) \
          <(.venv/bin/python -m pip freeze --exclude-editable | sort)
FREEZE_DIFF_EXIT=0
```

`.venv` gitignored — `.gitignore:6` = `.venv/`; `git status --porcelain=v1 --untracked-files=all` prints **nothing** (0 lines). Report §D5's open worry is closed: A4's clean-tree check will not trip on `.venv`.

## 3. A3 — roots layout

Built by `/tmp/build_desk_proof_env.sh` (adapted from `scripts/ed_session/build_rehearsal_env.sh:91-175`; the template's hardcoded `/Users/edr/JouleWise-measurement-20260818`, branch `integration/phase2-transaction`, `d117_floor_qwen25_1p5b_v2` and `freeze-0002` pre-flight were replaced/dropped — the freeze-reference check needs the A2 registry patch, so it was omitted).

```
/Users/edr/desk-proof-arm-census/
  arm-readiness-custody/window-plan/  after_midpoint_stages.txt 243  before_midpoint_stages.txt 225
                                      extraction_spec.json 98008   waivers.json 3 ("[]")
                                      window-chain.zsh 8331 (mode 700)  window-chain.zsh.sha256 150
                                      window.env 1658
  backups/claim/  backups/bound/      (empty)
  inputs/  calibration_observation_ledger.jsonl 136253   identity-epoch.json 221   t1-bindings.json 496
  quarantine/  window-custody/        (empty)
  runs_d117_floor_qwen25_1p5b_v3/  runs_d117_floor_qwen25_1p5b_v3_bound/   (empty)
  desk-proof-input-provenance.json 292
```
Builder checks that passed: `R2 resolver OK plan_id=plan-d117-floor-qwen25-1p5b-decode-p128-prefill-rider-v3`; `rows=76 last_sequence=76`; `extraction_spec OK` (source `configs/floor_mint/d117_qwen25_1p5b_v3_extraction_spec.json`, the v3 sibling of the template's v2); `window.env exact-key contract OK (25 keys)`. Free space on the volume: 356 GiB (row 15 needs ≥20 GiB on both backup dests).

**Which derivation tool the T-0 path expects.** Neither. `scripts/capture_t0_step.py:265-368` only requires `IDENTITY_EPOCH_JSON` / `T1_BINDINGS_JSON` to be *absolute literals* in `window.env`; the author's only content requirement is "readable + a JSON object" (`joulewise/arm_readiness_evidence_t0.py:1590-1608`), with the bytes then echoed back in the reservation receipt's slots (`:1624-1640`). `scripts/write_derivation_night_inputs.py` is a **derivation-night** tool: it derives the epoch from *this live machine* (sysctl, `/usr/bin/powermetrics` digest, `import mlx.core`) and **refuses when no identity field is stale** (docstring lines 31-36). That vector would not match the 76-row fixture the scratch ledger is, and `reserve_calibration_window_bracket.py --execute` (Ed's step 6) is what consumes both. I therefore used the `build_rehearsal_env.sh` route — last fixture receipt's `identity_epoch` / `t1_bindings`, schema-checked against `IDENTITY_EPOCH_FIELDS` / `T1_FIELDS`. Flagging it as an unproven assumption: step 6 has never been executed, and if the reservation script cross-checks the epoch against the live 25G83 machine it will refuse.

**window.env exact-key contract** (`WINDOW_ENV_KEYS`, `joulewise/arm_readiness_evidence_t0.py:67-95`, re-exported as `capture_t0_step._ENV_KEYS:90`) — 25 keys, all present: `MEASUREMENT_REPO WINDOW_ID BRACKET_SESSION_ID FROZEN_PLAN PACK_ROOT PACK_ID PLAN_ID EVIDENCE_ROOT_ID IDENTITY_EPOCH_JSON T1_BINDINGS_JSON PRE_ATTEMPT_ID POST_ATTEMPT_ID RUNS_ROOT BOUND_RUNS_ROOT CALIBRATION_LEDGER LEDGER_HEAD_PIN ARM_READINESS_CUSTODY_ROOT CUSTODY_ROOT WINDOW_CUSTODY_ROOT QUARANTINE_ROOT CLAIM_BACKUP_DEST BOUND_BACKUP_DEST WAIVER_PATH POWER_POLICY SETTLE_S`. Additional literal constraints enforced at `capture_t0_step.py:308-360`: `MEASUREMENT_REPO/PACK_ROOT/PACK_ID/PLAN_ID/FROZEN_PLAN/ARM_READINESS_CUSTODY_ROOT/WINDOW_ID/EVIDENCE_ROOT_ID` must equal the resolved pack identity; `CUSTODY_ROOT == WINDOW_CUSTODY_ROOT`; `SETTLE_S == "180"`; twelve named keys must be absolute. The file is pasted in full in §5 below.

**Ledger head verification** (scratch copy vs committed pin):
```
scratch ledger rows        : 76
scratch last .sequence     : 76
scratch last receipt_digest: 08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7
committed pin sequence     : 76
committed pin head_digest  : 08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7
MATCH sequence: True | MATCH digest: True
```
(pin = `configs/calibration/calibration_ledger_head.json`; the row's digest field is `receipt_digest`, there is no `head_digest` key on the row.)

## 4. A5 — the two dry gates (verbatim)

### Run 1 — `configs/campaigns/d117_floor_qwen25_1p5b_v3`
```
EXIT=2
=== STDOUT ===
{
  "detail": "successor ID 'd117_floor_qwen25_1p5b_v3' is not installed by the R1 registry",
  "kind": "AUTHORING_SET",
  "reason_codes": [
    "readiness_row_registry_mismatch"
  ],
  "status": "REFUSE"
}
=== STDERR ===   (empty)
```
Refuses at `joulewise/arm_readiness.py:4469-4472` (`_plan_profile`), i.e. **before** `CLOCK_ATTESTATION` — exactly the consequence the report predicts for skipping A2.

### Run 2 — `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1`
```
EXIT=2
=== STDOUT ===
{
  "detail": "clock-reference command capture is unreadable: /Users/edr/desk-proof-arm-census/arm-readiness-custody/d117_contrast_qwen25_1p5b_vs_7b_v1/arm_readiness.t0.inputs/clock-reference.json: [Errno 2] No such file or directory: '...clock-reference.json'",
  "kind": "CLOCK_ATTESTATION",
  "reason_codes": [
    "evidence_author_t0_clock_attestation_missing"
  ],
  "status": "REFUSE"
}
=== STDERR ===   (empty)
```
Neither run wrote anything: no new path appeared under `/Users/edr/desk-proof-arm-census` (checked with `find -newer`), and the clone stayed clean.

### Extra diagnostic (not requested; read-only, wrote nothing)
`--pack-root configs/campaigns/d117_floor_qwen3-1p7b_v5` (the ALPHA successor the live registry *does* install):
```
EXIT=2  {"status":"REFUSE","kind":"AUTHORING_SET",
         "reason_codes":["readiness_pack_unreadable"],
         "detail":"cannot read plan tree: [Errno 2] ... d117_floor_qwen3-1p7b_v5/plan_tree.json"}
```

## 5. window.env as written

```
MEASUREMENT_REPO=/Users/edr/JouleWise-desk-proof-20260915
WINDOW_ID=plan-d117-floor-qwen25-1p5b-decode-p128-prefill-rider-v3
BRACKET_SESSION_ID=desk-proof-20260915
FROZEN_PLAN=/Users/edr/JouleWise-desk-proof-20260915/configs/campaigns/d117_floor_qwen25_1p5b_v3/calibration_plan.json
PACK_ROOT=/Users/edr/JouleWise-desk-proof-20260915/configs/campaigns/d117_floor_qwen25_1p5b_v3
PACK_ID=d117_floor_qwen25_1p5b_v3
PLAN_ID=plan-d117-floor-qwen25-1p5b-decode-p128-prefill-rider-v3
EVIDENCE_ROOT_ID=evidence-d117-floor-qwen25-1p5b-v3
IDENTITY_EPOCH_JSON=/Users/edr/desk-proof-arm-census/inputs/identity-epoch.json
T1_BINDINGS_JSON=/Users/edr/desk-proof-arm-census/inputs/t1-bindings.json
PRE_ATTEMPT_ID=desk-proof-20260915-pre
POST_ATTEMPT_ID=desk-proof-20260915-post
RUNS_ROOT=/Users/edr/desk-proof-arm-census/runs_d117_floor_qwen25_1p5b_v3
BOUND_RUNS_ROOT=/Users/edr/desk-proof-arm-census/runs_d117_floor_qwen25_1p5b_v3_bound
CALIBRATION_LEDGER=/Users/edr/desk-proof-arm-census/inputs/calibration_observation_ledger.jsonl
LEDGER_HEAD_PIN=/Users/edr/JouleWise-desk-proof-20260915/configs/calibration/calibration_ledger_head.json
ARM_READINESS_CUSTODY_ROOT=/Users/edr/desk-proof-arm-census/arm-readiness-custody
CUSTODY_ROOT=/Users/edr/desk-proof-arm-census/window-custody
WINDOW_CUSTODY_ROOT=/Users/edr/desk-proof-arm-census/window-custody
QUARANTINE_ROOT=/Users/edr/desk-proof-arm-census/quarantine
CLAIM_BACKUP_DEST=/Users/edr/desk-proof-arm-census/backups/claim
BOUND_BACKUP_DEST=/Users/edr/desk-proof-arm-census/backups/bound
WAIVER_PATH=/Users/edr/desk-proof-arm-census/arm-readiness-custody/window-plan/waivers.json
POWER_POLICY=ac_high_power
SETTLE_S=180
```

## 6. Contradictions / corrections to the research report

1. **Report line 80** ("Expected **exactly** … `CLOCK_ATTESTATION` … Any other reason code means A1-A4 are not yet right"). Run 2 produced exactly that refusal **without A2 or A4**, because `d117_contrast_qwen25_1p5b_vs_7b_v1` is in the historical map `_PROFILE_BY_PACK` (`joulewise/arm_readiness.py:415-419`) and so skips the registry gate, and because row 1 (`clock.correct_and_prior_state`) fails on the absent capture long before row 5's root check. So **the CLOCK_ATTESTATION refusal is not a sufficient A1-A4 gate** — it can be reached with a pack the ceremony would still fail at row 5. The A5 gate's discriminating power is lower than the report claims; only Run 1's `readiness_row_registry_mismatch` is diagnostic of A2 being absent.
2. **Report line 50** ("`d117_contrast_qwen25_1p5b_vs_7b_v1` … refusal at row 5, before the census"). Unverifiable from a dry gate — it never reaches row 5 with no captures present. Its `plan_tree.roots` does use `claim_leaf`/`bound_leaf` (confirmed) and `_root_observation` does require `claim_root_leaf`/`bound_root_leaf` (`joulewise/arm_readiness_evidence_t0.py:1014-1020`), so the claim is structurally sound but **untested**.
3. **Report line 51** ("`successor_pack_ids` name three `_v5` Qwen3 packs that **do not exist**"). Imprecise at HEAD `3b53478a`. `freeze_evidence_lifecycle.successor_policy.successor_pack_ids` = `{ALPHA: d117_floor_qwen3-1p7b_v5, BETA: d117_floor_qwen3-8b_v5, GAMMA: d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5}`. The ALPHA and BETA **directories do exist** under `configs/campaigns/`, but contain only `generate_configs.py` — no `plan_tree.json` (extra run above: `readiness_pack_unreadable`). GAMMA has no directory (the nearest is `d117_contrast_v5`). The conclusion stands (no installed successor is usable, A2 is still the blocker), but the stated reason is wrong.
4. **Report line 40** ("expect origin/main = 6d2d62d8 or later"): true, but canonical's *local* `main` was behind origin (§1). A literal `git clone` + no fast-forward yields a clone whose `HEAD != refs/remotes/origin/main` — A4's `reviewed_main` (`joulewise/arm_readiness.py:5542-5564`) would fail. Worth adding to the runsheet.
5. **Report line 55** says to model A3 on `build_rehearsal_env.sh:91-175`; note that script's final validator imports `scripts.capture_t0_step._parse_window_environment` and `_ENV_KEYS`, which **no longer exist** under those names — the live symbols are `parse_window_environment` / `WINDOW_ENV_KEYS` in `joulewise/arm_readiness_evidence_t0.py` (`capture_t0_step.py:29-33`). Running the template as-is would fail there.

## 7. Held for the cold gate

A2 (registry `successor_pack_ids` patch + commit) and A4 (terminal-review empty commit + `update-ref` of `refs/heads/main` and `refs/remotes/origin/main`) were **not** performed. No commit of any kind exists in the clone beyond what was fetched. Until A2 lands, `d117_floor_qwen25_1p5b_v3` cannot reach row 1.
