# 03 — Staged (NOT published) REHEARSAL_STUB plan `rehearsal-20260916` (2026-09-15 23:21–23:24 PDT, activation `08ca8197`)

Requested by the interactive session `b0ae8462` (cross-session message ~23:20
PDT) as parallel prep while it finishes the transactional installer: author
and stage the first post-merge night plan, class REHEARSAL_STUB, through the
desk block, stopping before the notice, before publication and before any
installer step. Rules kept: no seats, nothing armed, launchd untouched, the
installer lane stays with the interactive session, nothing staged here may be
published until it hands off.

## What exists now (paths, digests, heads)

| Item | Value |
|---|---|
| H (remote main at clone time, pinned in `03-stage-evidence/H.txt`) | `1f721fbf7b8f96b90c64c7fe576592e5dbda098a` |
| Measurement root (fresh `git clone --no-hardlinks`, detached at H, `.venv` Python 3.13.1 from `env/mac-measurement-lock.txt`, lock diff EMPTY, mlx 0.31.2 / mlx_lm 0.31.3, tree clean) | `/Users/edr/JouleWise-measurement-rehearsal-20260916` |
| Ledger restored byte-exact from the canonical ledger FILE (no canonical git op): sha256 `aa806848…`, 76 records; custody authentication PASS sequence 76 digest `08456d50…` | `<root>/runs/calibration_observation_ledger.jsonl` |
| Staged plan (`joulewise.night_plan.v2`, `REHEARSAL_STUB`, `window_max_s` 900 as the 09-12 stub precedent) | `/Users/edr/night-plan-staging/rehearsal-20260916/night_plan.json` |
| Staged plan sha256 | `53b021b2138b3d5021fd9ba11daff936177abe0885ce17e379cac6a57862be69` |
| Plan fields | `repo_head` = `measurement_head` = H; `measurement_root` as above; `custody_root` `/Users/edr/night-custody/rehearsal-20260916`; `chain_path` `<custody_root>/chain.zsh` (a stub never runs a chain); `registration_path` `configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json`; `authored_epoch_s` 1789539821.713 |
| t0 PLACEHOLDER (derived at author time as now + 85-minute floor, rounded up to 5 minutes) | `1789545000` = 2026-09-16 00:50:00 PDT |
| Custody root | created EMPTY (no `night_plan.json` under night-custody; the watchdog glob and the arm block cannot see the staged plan) |
| Driver preflight from the clone against the staged path | `{"preflight": "ok", "python": "<root>/.venv/bin/python", "version": "3.13.1", …}` rc 0 |
| `check` / `check --preregistration …rev1.md` from the clone (informational for a stub) | rc 3 / rc 3: `os_build 25F84 → 25G83 MISMATCH`, `powermetrics_sha256` and `mlx_version` MISMATCH against the r6 acceptance, hardware match, pre-registered powermetrics sha `b762e5bf…` match — the same shape record 50 recorded on 09-14 |

Scripts and their outputs are in `03-stage-evidence/` (`exports.zsh`,
`20-clone.zsh`, `21-ledger.zsh`, `30-stage.zsh`, the three `*-output.txt`,
`staged-night_plan.json`). Live copies: `/tmp/magistrate-08ca8197/stage/`.

## Re-deriving t0 in one command (when the merged install rules are known)

```zsh
rm /Users/edr/night-plan-staging/rehearsal-20260916/night_plan.json   # this session's own staged file
ARM_TO_T0_FLOOR_S=<new floor in s> /bin/zsh /tmp/magistrate-08ca8197/stage/30-stage.zsh
```

`30-stage.zsh` re-authors the plan with `t0 = ceil((now + floor) / 300) * 300`
and re-runs preflight. To move to a new H (the installer merge), re-run
`20-clone.zsh` + `21-ledger.zsh` with a fresh `H.txt` and a new
`MEASUREMENT_ROOT` name in `exports.zsh` (never fast-forward a provisional
clone, runbook §0.2), then `30-stage.zsh`.

## Why no wrapper step

`scripts/gen_derivation_night.py` refuses any plan whose class is not
`DIAGNOSTIC_NO_PACK` (its allow-list at `:479-485`): a `REHEARSAL_STUB`
never runs a chain (`run_night.py:1572-1575`, `chain_path` becomes
`/dev/null`), so §1.1b steps 3–5 do not apply. The 09-12 stub plan
(`~/night-archive/rehearsal-20260912-plan-root-retired-1789198658/night_plan.json`)
is the precedent for the field values.

## FINDING for the handoff — a stale plan root is still discoverable

`/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260915/night_plan.json`
(the 09-15 equivalence night: REFUSED at t0, harvested by activation
`1acf2aee`, both agents uninstalled) is still one level under
`night-custody`, exactly the watchdog's `*/night_plan.json` glob and the arm
block's "existing plan" abort (runbook §1.4 precondition "after any prior stub
or plan root is retired"; record 48 retired the 09-13 root the same way).
`launchctl list` shows only `com.joulewise.magistrate`; no night agent is
loaded, so nothing is armed. This activation did NOT move it: it is not a
plan this session authored, and the retirement is the arming session's
step under the record-48 procedure (byte-exact archive to
`~/night-archive/…-plan-root-retired-<epoch>` with `SHA256SUMS`, then the
§0.7 assertion). Staging therefore ran §0.7 as report-only and asserted only
that the discoverable set is unchanged by staging.

## What was NOT done

No notice email. No publication (`os.replace` into the custody root). No
`NIGHT_HANDBACK.md` rewrite. No installer or launchd action. No seat.
