WRITE_SCOPE: ["joulewise/calibration_ledger.py","joulewise/whole_window.py","joulewise/analysis_engine/inputs.py","joulewise/analysis_manifest_v3.py","joulewise/floor_mint_estimator.py","scripts/mint_floor_artifact.py","scripts/mint_floor_artifact_generalized.py","scripts/build_bracket_binding.py","scripts/run_campaign.py","scripts/recover_calibration_ledger.py","scripts/check_window_provenance.py","scripts/generate_g2a_probe_inputs.py","tests/test_calibration_ledger_custody.py","tests/test_custody_mode_inventory.py","tests/fixtures/custody_read_replay_allowlist.json","docs/contracts/calibration_ledger_append.md"]

# ICLOUD-CUSTODY-LOCATOR-01 part 5 — issuing boundary by construction (gpt-6-astra, HIGH, genre implementation)
Head ae09cad7 on fix/2026-09-08-icloud-custody-locator. A rule-11 cold gate ruled this design; read the ruling and
its refutation at the absolute paths
/Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99ak-coldgate-packet-locator-boundary/10-coldgate-fable-ruling.md,
/Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99ak-coldgate-packet-locator-boundary/11-coldgate-opus-refutation.md,
/Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99ak-coldgate-packet-locator-boundary/13-magistrate-synthesis.md
(the synthesis governs where they differ). Verify every line number by reading the code; never inherit one.
Implement, in this order:
1. Invert the defaults: `load_calibration_ledger_snapshot` and `_custody_reasons` default `mode="issuing"`. Every
   `probe_custody`/`_custody_probe_paths`/`_custody_state` default stays `issuing`.
2. Replay opt-ins (`mode="read_replay"`) ONLY at genuinely-replay callers: scripts/run_campaign.py loader kwargs
   (~:4817), scripts/recover_calibration_ledger.py (~:233, :264), scripts/check_window_provenance.py (~:322, :854;
   verify_custody False there — add the kwarg only if custody is probed, else leave and record as inert),
   scripts/generate_g2a_probe_inputs.py (~:675; same rule), ledger-internal :4853/:5242 (status, resume-finalize
   snapshot; keep the explicit issuing state check after :5242).
3. SHARED validators take a caller-supplied `mode: Literal["read_replay","issuing"] = "issuing"` and forward it:
   `AuthenticatedConsumptionSession.__init__` (joulewise/whole_window.py ~:477/:512), `bind_floor_artifact_evidence`
   and `load_analysis_inputs` (joulewise/analysis_engine/inputs.py ~:1610/:1630, :3089/:3125), and the mint module's
   own loads at scripts/mint_floor_artifact.py ~:969 and ~:1745. Issuing constructors (mint_floor_artifact.py ~:452,
   :1089; analysis_manifest_v3.py ~:3695; floor_mint_estimator.py ~:429, :630, :672) pass nothing (issuing).
   Replay consumers of those shared functions (find them by grep; e.g. analysis-engine replay CLIs, paper producers)
   pass `mode="read_replay"` explicitly — list each in the report.
4. Defence in depth: `_refuse_custody_override_mint()` as the first statement of `mint_floor_artifact`
   (scripts/mint_floor_artifact.py ~:2010), `mint_multi_cell_floor_artifact` (generalized ~:3983),
   `build_bracket_binding.main` (~:416) and `_authenticate_finalization_inputs` or its public entry
   (analysis_manifest_v3.py ~:3525/:4045 — pick the public entry and say why).
5. Pins in tests/test_calibration_ledger_custody.py and a NEW tests/test_custody_mode_inventory.py:
   (a) signature-default pin for the five functions (counterfactual: flip any default → fails);
   (b) AST inventory over joulewise/ and scripts/: every call of load_calibration_ledger_snapshot / probe_custody /
   _custody_state / _custody_reasons / the three shared validators either omits `mode`, passes `mode="issuing"`,
   forwards a variable named `mode`, or appears in tests/fixtures/custody_read_replay_allowlist.json keyed by
   (file, enclosing function) with a one-line reason — a new opt-in must edit the allowlist (counterfactual: add
   `mode="read_replay"` at mint_floor_artifact.py's mint snapshot load → fails);
   (c) planted-replacement fixture on the bare snapshot load: non-empty override, original absent, valid replacement
   bytes → `calibration_ledger_custody_invalid` and ZERO opens under the replacement root (instrument via a
   monkeypatched `Path.open`/`os.open` counter or the existing touch-recorder); with `mode="read_replay"` → valid;
   (d) one planted-replacement fixture per issuing entry of step 4 asserting the guard refuses BEFORE any probe.
6. Empty override: unchanged behaviour; when an issuing probe returns absent under `JOULEWISE_BACKUP_ROOTS=""`,
   emit ONE stderr line `custody_backup_roots_disabled: <path>`; regression.
7. Contract addendum (docs/contracts/calibration_ledger_append.md): a dated 2026-09-08 addendum stating the inverted
   default, the allowlist as the executable census (replacing the two-module prose census), the entry guards as
   defence in depth (not the invariant), and the empty-override diagnostic.
Acceptance (rc-gated, logged, never piped): `PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS='' python3 -B -m unittest tests.test_calibration_ledger_custody tests.test_custody_mode_inventory tests.test_calibration_bracketing tests.test_calibration_ledger tests.test_authentication_io tests.test_whole_window tests.test_analysis_manifest_v3 tests.test_build_bracket_binding tests.test_mint_floor_artifact` (drop any module name that does not exist and say so); run each counterfactual of step 5 in memory and report kills; `git diff --check`; no commit; header < 8192 bytes; body = per-step change list with file:line, the replay-consumer list of step 3, and tails.
