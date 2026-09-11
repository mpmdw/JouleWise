# 10 — Packet: which registration document must night-gate row C1 bind the equivalence night to? (refuter 07 finding B-1) — 2026-09-11 08:05 PDT, activation 58a3bcfc

Bench-verified by the magistrate this session (commands and outputs below). Design-bearing: it decides which document the night is bound to before data. Under rule 2/11 it goes to a bounded three-seat consult (Opus lens = record 07 §3; Astra consult; cold Fable judge), then the magistrate decides and Ed can veto.

## Facts

F1. `joulewise/night_gate.py:1300-1328` (bench: `sed -n 1300,1330p`): for `receipt_class in {"DIAGNOSTIC_NO_PACK", "REHEARSAL_STUB"}` row C1 reads `plan.registration_path`, sha256s its UTF-8 bytes and refuses `night_refused_registration` unless the digest equals `D166_REGISTRATION_SHA256` = `dfe55f8d96cd21e07cd1c7fe230fef34f485f027f3920ce96b8a9ebacc1ac265` (lines 32–41; comment: "2026-09-05: D-165 v2 relabel supersedes the v1 registration digest"; `D166_REGISTRATION_PATH = configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json`). No class or chain awareness.

F2. Bench digests: `shasum -a 256 configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json` → `dfe55f8d…` (matches F1); `configs/calibration/preregistration_d079_epoch_25g83_rev1.md` → `ca2430ddd04b4a95b3ea0420ecf4d0897e1d1409f9d4f9f102414d00c37a5da7` (does not).

F3. `docs/phase_2/derivation_night_runbook.md` (rev 6): §0.5 lines 484–489 "The plan's `registration_path` points at this file" (the pre-registration md); §1.1 table line 760 "`registration_path` | the committed pre-registration of §0.5"; §1.4 line 1238; the arm block's own assertion lines 1283–1284 `assert plan.registration_path.endswith('configs/calibration/preregistration_d079_epoch_25g83_rev1.md')`; §5 line 2054 glosses `night_refused_registration` as "the `registration_path` did not authenticate". These arrived with revision 4 (commit 7a0511d6, promoted from trace draft 99). Armed as written, the equivalence night refuses at C1 and captures nothing.

F4. `scripts/gen_derivation_night.py:687` — the generator's example plan text says `"registration_path": "<repo-relative path of the committed pre-registration>"`; the generator takes NO pre-registration argument (argparse lines 835–870: plan, session-id, window-id, evidence-root-id, calibration-plan, identity-epoch-json, t1-bindings-json, runs-root, ledger, head-pin, slot-count, out …) and the wrapper's exports (lines 358–372) pin MEASUREMENT_ROOT, PY, the chain sha256 and the per-slot bindings — NOT the pre-registration's digest. The chain `scripts/night_chains/calibration_derivation_only.zsh` mentions the pre-registration only in comments (lines 12, 145, 211).

F5. The pre-registration IS enforced at the desk: `scripts/issue_calibration_acceptance_generation.py` `check --preregistration` parses os_build + sampler digest from the text (lines 299–342, rc 3 on mismatch) and `prepare-candidate --preregistration-sha256` pins its digest at issuance (S4, PR #315). Nothing enforces it between arm and capture on the night itself.

F6. Every night to date (rehearsal-20260909, rehearsal-20260911, the G2-a packet 04 plan) carried `registration_path` = the d166 JSON (harvest evidence `01-harvest-evidence/night_plan.json`), which is why C1 passed on 09-09.

F7. Runbook §0.5 lines 526–528 say of the pre-registration digest: "a change between nights is a stop, not a new pin." The pre-registration's bytes changed on 09-10/11 when revision 2 recorded Ed's ruling (commits 07995051, 12162263). D-166 is the dominance-criterion registration of the D-117 contrast campaign — a different scientific object from the D-079/25G83 calibration pre-registration.

F8. Ed's ruling (issue 316, records 146/147): "blindness for this campaign means every rule is fixed before data, not that no one may look"; the equivalence rule and its constants must be fixed in writing before capture; the smallest change that preserves byte-identity of r6 and its pins is preferred.

## Options

(i) DOCS + PLAN: the equivalence plan's `registration_path` = `D166_REGISTRATION_PATH` (as every night so far); fix runbook §0.5/§1.1/§1.4/arm-assert/§5 and the generator's example text (F4) to say so; the pre-registration stays a desk-enforced object (F5). Cost: the night itself binds to the D-117 campaign registration, which has nothing to do with a calibration derivation night — C1 becomes a ceremony for this class. 
(ii) CODE (night_gate): make C1 accept, for a plan whose chain is the derivation wrapper (or for a new plan field naming the pre-registration), the pre-registration's digest — a new pinned constant or a plan-carried digest verified against the file at t0. Cost: a contract change to `night_gate` C1 semantics + tests + the constant must be re-pinned when the pre-registration changes (F7 says that is a STOP, which is consistent).
(iii) BOTH-LAYERED: C1 keeps D166 (unchanged code, plan carries the d166 path) AND the wrapper generator gains `--preregistration PATH`, exports `PREREGISTRATION_SHA256` as a literal, and the chain refuses at start if the file's sha256 differs (a chain-level pin, like the existing chain sha256 tripwire). Cost: generator + chain + tests; runbook fixed as in (i); the pre-registration is pinned at night by the wrapper, not by the gate.

## Question
Which option binds the equivalence night to the right document with the smallest correct change, and what EXACT evidence must the arm record carry? State for each option what a FAIL-route night 2/3 must do when the pre-registration bytes change (F7). Recommend one; name the WRITE_SCOPE and the defect-shaped tests for it. Do not amend kernel or decision-log text; a magistrate PR under the gauntlet implements the recommendation and Ed can veto on the email.
