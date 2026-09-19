# Opus contract-lens refutation of consult 44 (Astra, Stage A campaign)

Read-only, worktree at main `0c529f99`; no repo writes, no `sudo`/`powermetrics`/`collect`.

## Recommendation (first)

Adopt **option (a′)** — a `DIAGNOSTIC_NO_PACK` v2 plan whose `chain_path` runs the evidence payload, with an evidence-specific probe receipt — but **reject two contract claims and the campaign sizing**:

1. **"No schema or serialization change" is true of the key set and misleading about the gate.** `_check_registration` requires a `DIAGNOSTIC_NO_PACK` plan's `registration_path` bytes to hash to the single hard-coded D-166 calibration digest (`joulewise/night_gate.py:1333-1352`; constant `:37-44`). An evidence night declares either the **D-166 dominance-criterion registration as its own pre-registration — a false C1 attestation** — or the gate learns a second registered digest, a **pre-registration guard change that `docs/process/NIGHT_HANDBACK.md:134` puts on the cold-gate path by name.** His "keep the existing D-166 gate; separately bind the campaign's protocol through the reviewed head and manifest digest" silently picks the false attestation. That is the blocker.
2. **Run an idle-only variance pilot before any load matrix.** His 60 nonzero + 72 idle slots / 28 h / 12 windows carries **no variance estimate**, so "three repeats per cell" is a guess; the arithmetic below shows it is almost certainly underpowered for a 1 J effect while spending the budget on breadth no cutoff needs.

Sequence: (i) idle-only pilot night (~75 min, no load generator); (ii) cold-gate ruling on the registration/probe amendment; (iii) depth-first two-level campaign sized from the pilot's spread.

## 1. Does plan schema v2 really need no change?

**The JSON schema: no. The gate contract: yes.**

- `NightPlan.from_mapping` compares the key set for **exact equality** against `_PLAN_KEYS` (`night_gate.py:120-135`, `:240-247`); any new field refuses `night_plan_malformed`. `chain_path` does select the payload (`:1074-1105`); `night_plan_writer.py:19-40` needs nothing. He is right to avoid a bump.
- But three gate behaviours are **calibration-specific by construction** and all fire for `DIAGNOSTIC_NO_PACK` regardless of payload:
  - **Registration (C1).** `class_table()` requires `C1: PASS` for `DIAGNOSTIC_NO_PACK` (`:467-473`); `_check_registration` accepts exactly `D166_REGISTRATION_SHA256` (`:1349`), path `configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json` (`:41-44`). **Cold-gate matter.**
  - **Install probe.** `probe_bindings` parses the chain for `CALIBRATION_LEDGER` and `LEDGER_HEAD_PIN` literals, re-derives the ledger head, and requires `calibration_derivation_only.zsh` to carry `NIGHT_VERIFY_ONLY` and `NIGHT_RESERVATION_ARGV_ONLY` (`joulewise/night_agent_install.py:750-771`). A harness chain cannot satisfy it honestly — his F1 is correct and the strongest item in his answer. Receipt kind `joulewise.night_probe_receipt.v1` is validated at `:795-830`, produced at `scripts/run_night.py:3263-3300`.
  - **Authoring.** The only plan authoring tool is calibration-shaped: it refuses any non-derivation receipt class and any slot count but the pre-registered twelve absent a named ruling (`scripts/gen_derivation_night.py:480-500`). A campaign author/verify tool is *forced*, not optional (his file 2).

**Documents amended by a new probe kind or payload identity:** `docs/process/NIGHT_HANDBACK.md:563-575` (receipt "binds … ledger head"; refusal-code table `:92-107`) and `docs/phase_2/derivation_night_runbook.md:2068-2092`, `:3048`. `docs/contracts/night_quiet_admission.md` is **not** amended while v2 admission is retained. There is no plan-schema file under `docs/contracts/`; the gate contract lives in those two process docs.

**Cold-gate clauses (rule 11): (a)** `NIGHT_HANDBACK.md:134` — "every capture, clock, custody, ledger or **pre-registration** guard stay on the cold-gate path" — any change to the accepted `registration_path` digest; **(b)** `derivation_night_runbook.md:3048`, the verify-only probe row, which a new probe kind rewrites; **(c)** `night_quiet_admission.md:24-27` (ruling 70 proposition 4) only if a cutoff is sealed. Seat-level work (chain, manifest, tests, dispatch) is lead authority.

## 2. Is the "borrowed predicate" circularity real?

**Yes, and the brief's escape hatch does not exist in code.** There is no v4 state meaning "bind window, no cutoff activated":

- `validate_policy` requires **exactly** seven keys including `busy_core_max`, extras refuse (`quiet_admission.py:22-24`, `:38-40`).
- `is_quiet` returns `policy["busy_core_max"] > 0 and busy <= policy["busy_core_max"]` (`:165-170`) — **zero admits nothing** (contract `:82-83`). A v4 plan either seals a positive cutoff (activation, refused by ruling 70, `:24-27`) or never reaches GO.
- `cutoff_authority` must name the ruling that **affirmed** the sealed limit (`quiet_admission.py:43-44`; contract `:22`). None exists for any positive value.

So the campaign runs under **v2 one-shot admission**, as he says. **What he missed:** v2's activity predicate is the legacy one-minute load average ≤ `LOAD_MAX = 2.0` (`night_gate.py:60`, `:1218-1245`) — the exact predicate the contract documents as defective, since load 1.3–1.5 passed while `fseventsd` held 85–100% of a core (`night_quiet_admission.md:38-44`). A v2-admitted evidence night can therefore begin with a core-eating daemon **contaminating the idle reference the campaign rests on**. Cure without activating anything: run `quiet_admission.sample_interval` inside the evidence chain as a **recorder only** (already a pure sampler, `:231-280`), stamp each round with measured busy cores, exclude post hoc. Recording is not admission and seals no cutoff.

## 3. Campaign arithmetic against the instrument bar

Unit conversions are right (1 J/480 s = 2.083 mW; 5 J = 10.417 mW). The consequence he does not draw: at the contract's illustrative 5 W per busy core, a **1 J** ceiling is **0.0004 core** — "below even the sampler's measured cost" (`night_quiet_admission.md:45-56`). **The 1 J bar sits below the observer floor.** The realistic deliverable is therefore an **upper bound** on ΔJ per 480 s at small loads plus the clean-machine busy-core distribution, not a measured transition point; a design that maps a six-level curve optimises for the wrong output.

Sizing: a paired contrast detecting δ = 1 J at 80% power needs roughly `n ≈ 8 s²/δ²` pairs, `s` = between-slot spread of paired ΔJ. `n = 3` per cell is adequate only if `s ≲ 0.6 J`, i.e. 0.04% stability on a ≈1440 J idle slot. Nobody has measured `s` on 25G83. At `s = 3 J`, `n ≈ 72` and the 28 h plan is ~24× too small. **`s` must be measured before the matrix is frozen.** Breadth also costs: 5 levels × 2 profiles × 2 QoS = 20 cells, while a cutoff is one scalar on *total* busy cores (`night_quiet_admission.md:122`) — profile and QoS are covariates to record, not cells to replicate.

**Idle reference:** he is right that r6's 25F84 idle is context, not a baseline, and right to bracket with adjacent same-session idle. His 600 s envelope with an interior 480 s analysis interval improves on the harness's duration-normalised `delta_j_480`; keep it.

**Smallest defensible campaign:** pilot → **2 levels** (0 and the smallest resolvable share), one profile, one QoS, paired, `n` from the pilot's `s`, reported as a one-sided upper bound with its coverage. Typically 12–20 pairs ≈ 4–7 h, splittable across windows; cross-boot replication opportunistic only.

## 4. The smaller thing he missed

**An idle-only variance pilot: one night, `n ≈ 6` consecutive 600 s envelopes (480 s interior), no `load` invocation at all.** ~75 min including settle. It is strictly smaller than his 44-minute `idle → 0.2 → idle` block in *contract surface*, which is what matters here:

- no synthetic-load process group, so the teardown extension he flags (collector + load workers + recorder + sampler vs `_terminate_process_group`'s single-group proof, `scripts/run_night.py:461-480`) reduces to collector + recorder;
- it yields the number that sizes everything else (`s`), the 25G83 idle reference, and observer cost with census — none of which his 44-min block yields, since one pair has no spread.

Gates, all pre-existing: v2 `DIAGNOSTIC_NO_PACK` admission; the §1 registration amendment (cold gate) or an explicit lead-recorded decision to run it **rehearsal-class** instead; the evidence probe receipt; arm-time and in-window census; courier descriptive-only. One caution nobody raised: the in-window census is `pgrep -lf "codex|claude|t3"` over full command lines (`joulewise/night_gate.py:45`; loop `scripts/run_night.py:880-905`) — the evidence chain's argv and custody paths must be checked against that regex before arming, or the night aborts itself mid-run. Also confirmed: the fixed artifact inventory (`scripts/run_night.py:959-990`) lists no harness outputs, so campaign artefacts are invisible to the durable publish and courier until extended — his blast-radius item is real.

## 5. Strongest disagreement

**The 28 h / 132-slot matrix is false precision.** Sized without a spread estimate, aimed at an effect the project's own contract places below the sampler's cost, and spending 4× its slots on profile/QoS cells a scalar cutoff never consumes. Replace with: idle-only pilot → measured `s` → depth-first two-level paired campaign reporting an upper bound, with "no cutoff qualifies at the 1 J bar" pre-registered as an expected, acceptable outcome.

Concession: his F1 (calibration-specific probe) and F2 (`os_build` never copied into rows; hard-probe results discarded) are correct and load-bearing.

## Commands run

`git log -1`; `sed -n` over `joulewise/{night_gate,night_plan_writer,night_agent_install,quiet_admission}.py`, `scripts/{run_night,gen_derivation_night}.py`, `night_quiet_admission.md`, `NIGHT_HANDBACK.md`, `derivation_night_runbook.md`; `grep -n` for `cutoff_authority|busy_core_max|LOAD_MAX|AGENT_CENSUS_ARGV|D166_REGISTRATION|night_probe_receipt`; `ls docs/contracts/`. No repo files modified; no tests, no live collection, no power sampling.
