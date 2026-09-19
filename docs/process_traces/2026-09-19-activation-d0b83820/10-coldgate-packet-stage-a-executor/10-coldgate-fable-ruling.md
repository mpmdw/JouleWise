# Cold-gate ruling 10 — Stage A evidence executor (Fable 5.1 cold seat, 2026-09-19 12:22–12:27 PDT)

**Judge disclosure.** Auto-loaded: `~/.claude/CLAUDE.md`, worktree `CLAUDE.md`, `MEMORY.md` index. Not used as evidence. CLAUDE.local.md, RUN_STATE.md, TASK_QUEUE.md not read.

**Validator.** Convening-prompt charter sha (`…a880…`): `REFUSE`, `charter_trusted_observed_mismatch`, rc=2. Re-run with `…a870…`: `PASS`, rc=0, packet `496bc885…`, five exhibit digests observed = expected, manifest `01525618…`. Judged only after that PASS.

**Probes (`git show 0c529f99:`).** `night_gate.py` :37–44, :118–136, :238–250, :1333–1363 (detail literal "D-166 registration hash passed"); `night_agent_install.py` :716–729, :750–771, :800–835; `run_night.py` :3263–3300; harness census/`sample_interval` sites; `sha256(d166_dominance_criterion_registration.json) = dfe55f8d…265 = D166_REGISTRATION_SHA256`. All checked citations accurate.

---

## Q1 — RULED: (a′) a ruled-registration TABLE, chain-bound by the registration file. (b) is REFUSED.

**Deciding exhibit:** A `night_gate.py:1349,1362–1363` plus my digest check. Under (b) the evidence plan's `registration_path` must point at the D-166 dominance-criterion file itself (only that byte string hashes to the constant), and the receipt writes evidence `registration:<that path>` and detail "D-166 registration hash passed". That receipt attests a pre-registration the night does not run under. The refuter is right: (b) is a false C1 attestation.

**How the gate knows which digest applies — no v2 key.** The plan already names the registration (`registration_path`) and the gate already measures the chain digest (`_check_chain_identity`). The missing link is registration→chain, and it belongs in the registration file, not the plan: an evidence registration JSON carries `"chain_sha256"` naming the exact chain it was frozen for. The gate checks that the named registration hashes to a ruled digest AND, when the table entry demands it, that the registration's bound chain digest equals the chain digest it measured. D-166 stays a legacy entry without chain binding (not reopened here).

**Code shape (`joulewise/night_gate.py`):**
```python
QPE01_PILOT_REGISTRATION_SHA256 = "<sha256 of the frozen pilot protocol file, set in the same PR that tracks it>"
QPE01_PILOT_REGISTRATION_PATH = "configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v1.json"
# Digest -> ruling. Amended ONLY by cold-gate ruling (NIGHT_HANDBACK.md:134); every entry cites its ruling.
RULED_REGISTRATIONS = {
    D166_REGISTRATION_SHA256: {"label": "D-166 dominance criterion", "binds_chain": False, "ruling": "D-165/D-166"},
    QPE01_PILOT_REGISTRATION_SHA256: {"label": "QPE-01 idle-variance pilot protocol v1", "binds_chain": True,
                                      "ruling": "cold gate 10 Q1/Q2 (2026-09-19)"},
}
```
In `_check_registration`, replace the single comparison (:1349) with: `ruled = RULED_REGISTRATIONS.get(registration_sha256)`; `None` → `Refusal("night_refused_registration", f"registration sha256 {x} is not a ruled registration")`. If `ruled["binds_chain"]`: `json.loads(registration_text)["chain_sha256"]` must equal the chain digest already measured by `_check_chain_identity` (read it from that row's `measured`; do not re-hash); absent/malformed/mismatch → `night_refused_registration`, message `registration binds chain <a>; plan chain is <b>`. Then `rows["C1"].measured` gains `registration_label`, `registration_ruling`, `registration_bound_chain_sha256` (or `null`); `detail = f"registration hash passed: {label}"`. C1 target for `DIAGNOSTIC_NO_PACK` stays `PASS`. `REHEARSAL_STUB` is unchanged.

**Receipt row text (C1):** evidence `registration:<path>`; measured `{registration_path, registration_sha256, registration_label, registration_ruling, registration_bound_chain_sha256}`; detail `registration hash passed: QPE-01 idle-variance pilot protocol v1`.

**Docs clauses:** NIGHT_HANDBACK.md :88 refusal row → "`night_refused_registration` | The plan's registration is not a ruled registration digest, or the registration's bound chain digest differs from the plan's chain." NIGHT_HANDBACK.md :134 → append: "The ruled-registration table in `night_gate.py` is amended only by cold-gate ruling; each entry names its ruling." Runbook :3048 row → see Q3. Ordering: protocol file, digest constant and ruling reference land in ONE PR; the plan pins a head containing them.

## Q2 — RULED: (a) the idle-only variance pilot is the first window; block two is a SECOND plan authored only after the pilot's spread is measured (i.e. (c) in order, never both authored now). (b) refused: one pair yields no spread.

**Deciding exhibits:** D §3–4 (n ≈ 8 s²/δ², 1 J ≈ 0.0004 core lies below the observer floor); B `night_quiet_admission.md:45–56`.

**Frozen pilot protocol v1 (the registration file of Q1):**

| Parameter | Value |
|---|---|
| Plan class | v2 `DIAGNOSTIC_NO_PACK`, `window_max_s` 5400 |
| Settle after GO (inside chain) | 600 s |
| Envelopes N | 6 × 600 s consecutive, no gap by design; no load generator |
| Interior analysis interval | 480 s starting 60 s into each envelope (60 s lead, 60 s tail) |
| Recorder | `quiet_admission.sample_interval` at 30 s inside the chain, journal file `evidence_busy_cores.jsonl` (NOT `quiet_samples.jsonl`) |
| Total | 600 + 3600 = 4200 s ≈ 70 min plus teardown; fits 5400 s |
| Minimum retained | ≥ 4 envelopes (≥ 3 adjacent pairs) else INCONCLUSIVE; no top-up; rerun as a fresh plan |

**Exclusion rules (per envelope, decided by named mechanism at issuance):** (1) any round census not clean → excluded; census `None` (no census completed) → excluded and counted as "unknown"; (2) AC probe not "AC Power", or any `CPU_Speed_Limit` < 100, or the AC/thermal probe erroring → excluded (harness must RETAIN per-round probe results; it discards them today, E item 4; fix before the pilot); (3) envelope start drift > 5 s from schedule, or powermetrics sample count/anchor outside the declared alignment bound → excluded; (4) fewer samples than declared inside the interior 480 s → excluded as incomplete support; (5) `busy_cores` from the recorder is a COVARIATE, never an exclusion criterion; a descriptive "recorder-quiet subset" summary is permitted, labelled PROVISIONAL.

**Summary must report:** per-envelope J over the interior 480 s (CPU+GPU+ANE sum, and combined as cross-check); adjacent-pair ΔJ, its SD `s_pair`, max |ΔJ|, and the SD of the six single-envelope values; observer cost as whole-round cpu-s (sampler + census, self + reaped children, never subtracted); busy-core distribution (median, max, per round); cadence distribution (actual vs planned start, samples per interior); `boot_id`, `os_build` (harness fix required before the pilot: rows lack it, E item 4), `sw_vers`, powermetrics identity; census results; every exclusion with its rule number.

**Sizing block two from `s = s_pair`:** n = ⌈8 s²/δ²⌉ pairs with δ = 1 J, floor n = 3.

| s (J/480 s) | 0.3 | 0.6 | 1.0 | 2.0 | 3.0 |
|---|---|---|---|---|---|
| n pairs | 3 | 3 | 8 | 32 | 72 |
| windows at ~10 pairs/window (20 min/pair, ~3.5 h) | 1 | 1 | 1 | 4 | 8 |

Block two = 2 levels (0 and the smallest holdable share, 0.05 core), one profile, one QoS, each load envelope bracketed idle–load–idle, n pairs from the table, reported as a one-sided 95 % upper bound `mean ΔJ + t₀.₉₅,ₙ₋₁ · s/√n`.

**"No cutoff qualifies" branch (pre-registered, acceptable outcome):** declare it when any of: (i) `s_pair` > 2 J (n > 32, more than four windows for one scalar); (ii) the observer floor's own busy cores exceed the tested share, so the level is unresolvable; (iii) the block-two upper bound at the smallest share exceeds 1 J. Then the deliverable is the upper bound and the clean-machine busy-core distribution; ruling 70 proposition 4 stays refused; no `cutoff_authority` may cite this campaign. If `s_pair` alone exceeds 5 J, the machine cannot support the claim bar and the finding escalates to Ed before any block two.

## Q3 — RULED: (a) a typed evidence probe receipt as a SECOND probe kind, dispatched by payload identity. It IS a contract amendment.

**Deciding exhibits:** A `night_agent_install.py:750–771` (literal `CALIBRATION_LEDGER`/`LEDGER_HEAD_PIN` exports, ledger head re-derived), `run_night.py:3255–3300` (`NIGHT_VERIFY_ONLY=1`, receipt schema v1).

**Dispatch:** by ONE literal export in the pinned chain, parsed with the same single-literal rule as `chain_literal_paths`: `export NIGHT_PAYLOAD_KIND=quiet_predicate_evidence`. Absent → calibration probe (today's path, byte-for-byte unchanged); present exactly once → evidence probe; present with `CALIBRATION_LEDGER` also exported, or more than once → install refusal `probe payload kind ambiguous`. Never dispatch on chain filename.

**Receipt schema `joulewise.night_evidence_probe_receipt.v1`:** `plan_id, plan_sha256, measurement_head, chain_sha256, chain_source_sha256, manifest_sha256` (the sealed evidence manifest) and its per-file digests, `harness_digests` (`scripts/sample_quiet_predicate_evidence.py`, `joulewise/quiet_admission.py`), `registration_sha256, registration_label` (Q1 table), `driver_python, chain_python` identities, `powermetrics_path`, `started_epoch_s, finished_epoch_s, outcome, refusal_code, launchd_label, verify_only: true, collect_started: false, load_started: false`. Custody fields (`custody_budget_s, custody_elapsed_s, observations`) MUST be absent; their presence refuses.

**Admission gates in `validate_evidence_probe_receipt`:** schema literal; `outcome == "ok"`; mtime and `finished_epoch_s` freshness identical to v1 (:805–816, reuse); `plan_sha256` equals the installed plan; `chain_sha256` equals the sidecar; `manifest_sha256` equals the digest embedded in the chain; harness digests equal the tracked files at `measurement_head`; `registration_sha256` ∈ `RULED_REGISTRATIONS` with `binds_chain` satisfied; the chain's verify-mode stdout must contain exactly one `VERIFY_ONLY_OK manifest=<sha>` line matching `manifest_sha256`, and the chain in `NIGHT_VERIFY_ONLY=1` may perform file reads and interpreter import checks only. Its `outcome: ok` is non-authorizing, never `ready_to_arm`, as the calibration row says.

**Amendment scope:** runbook :3048 gains a second row "Evidence verify-only probe receipt — verifies manifest, harness, chain, registration bindings; never starts `collect`, `load` or power sampling"; NIGHT_HANDBACK.md arm steps (:88–110 region and the :563–575 "binds … ledger head" sentence per D) gain "or, for an evidence payload, the sealed manifest, harness and registration digests"; installer §1.3 refusals gain `probe receipt kind does not match payload kind` and `probe payload kind ambiguous`. `night_quiet_admission.md` is NOT amended.

**Authoring tool:** lead authority once this receipt kind is ruled, as a NEW `scripts/gen_evidence_night.py` (not a flag on `gen_derivation_night.py`, whose refusals at :475–505 are correct for derivations). Constraints: refuses any class but `DIAGNOSTIC_NO_PACK`; reads N, settle, interval and cadence from the tracked protocol file, never from CLI (an override flag → refuse, protocol stays frozen); writes the registration path/label; and bench-checks every chain argv token, custody path and `plan_id` against the census regex `codex|claude|t3` (D §4 caution), refusing on any match.

**Sampler as in-chain recorder:** plain code, lead authority, not a contract matter under `night_quiet_admission.md:20–60`, on three conditions: it admits nothing, it journals to a file not named `quiet_samples.jsonl`, and its numbers are reported as PROVISIONAL covariates. It becomes a contract matter the moment any exclusion or admission rule reads `busy_cores`, which Q2 rule 5 forbids.

## Not executed
Nothing. No tests, live collection, `sudo` or `powermetrics`; no writes outside this file.
