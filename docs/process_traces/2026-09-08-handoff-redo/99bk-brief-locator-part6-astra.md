WRITE_SCOPE: ["tests/test_custody_mode_inventory.py","tests/fixtures/custody_read_replay_allowlist.json","joulewise/calibration_ledger.py","joulewise/calibration_bracketing.py","joulewise/whole_window.py","scripts/extract_detection_floors.py","tests/test_calibration_ledger_custody.py","tests/test_calibration_bracketing.py","tests/test_floor_extraction.py","tests/test_whole_window.py","docs/contracts/calibration_ledger_append.md"]

# ICLOUD-CUSTODY-LOCATOR-01 part 6 — fix round on part 5 (gpt-6-astra, HIGH, genre implementation)
Head 96bfb448 on fix/2026-09-08-icloud-custody-locator. Two refuters reviewed part 5 (read both at absolute paths):
/Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99bi-ref-locator-5-opus-contract-review.md (Opus: LAND-WITH-FIXES, blocker = census hatch)
/Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99bj-delta-locator-5-astra-report.md (Astra delta: F1 census escapes + misclassified fixture entries, F2 extraction CLI lost replay).
Cure ALL, verifying every line by reading the code:
1. CENSUS (Opus 2 + Astra F1): rewrite tests/test_custody_mode_inventory.py so the inventory is keyed PER CALL
   (file, enclosing function, call line) and resolves the `mode=` value through the existing `_keyword_modes`
   resolver for Name / IfExp / assignment aliases / local dict / `**kwargs` literal dicts; an `ast.Name` is treated as
   opaque ONLY when its id is a PARAMETER of the enclosing FunctionDef (a forwarded caller mode); a local variable
   named `mode` is resolved to its assigned value(s). Every call resolving to read_replay (possibly) must be in the
   allowlist keyed by (file, function, line, reason); a second replay call inside an allowlisted function needs its
   own row. Add `calibration_readiness` (calibration_ledger.py ~:4972/:4974/:5029) rows. Add the executed-in-memory
   escape cases from Astra F1 as counterfactual tests: local `mode="read_replay"` literal, assignment alias,
   factory-returned **kwargs, forwarded **kwargs, second call in an allowlisted function, shared(mode) called with
   replay from an issuing entry — each must be DETECTED (violation or forced allowlist edit). State honestly in the
   report which dynamic shapes an AST census cannot see (e.g. a dict built at runtime) and pin those by the runtime
   guard instead.
2. ISSUING-REACHABLE REPLAY LITERAL (Astra F1, decisive): joulewise/calibration_bracketing.py ~:1101
   `load_calibration_candidate` passes `mode="read_replay"` and is reachable from
   `AuthenticatedConsumptionSession._prepare` (whole_window.py ~:692) → mint and manifest-finalization constructors.
   Make `load_calibration_candidate` (and `_candidate_from_observation` / discovery / bracket evaluation in that
   chain) take a caller-supplied `mode` defaulting to issuing, forwarded from the session's `mode`; only genuinely
   replay sessions pass read_replay (allowlist rows). Regression: with a non-empty override, original absent,
   planted replacement, an issuing session's candidate discovery observes ABSENT (never the replacement path);
   the replay session observes the replacement. Also re-word the fixture reasons Astra found too broad
   (`calibration_session_status` reaches ledger append via recovery abort-session — either forward a mode there
   with issuing on the abort path, or justify precisely in the reason and add the guard test).
3. EXTRACTION CLI (Astra F2): scripts/extract_detection_floors.py ~:140 passes `mode="read_replay"` explicitly
   (retained-corpus extraction; allowlist row with the traced chain) plus a relocated-custody regression in
   tests/test_floor_extraction.py showing extracted floors are NOT suppressed under an override.
4. ADDENDUM (Opus 5 + 4a): docs/contracts/calibration_ledger_append.md — add a forward pointer at the top of the
   part-4 table (~:407–455) saying part 5 inverted the snapshot default; state that the boundary EXCLUDES
   claim-verdict derivation (analyze_claims writes claim verdicts under explicit read_replay, unchanged from base);
   the empty-override diagnostic must ALSO fire for separator-only values (":" etc.) which take the absent shortcut
   (calibration_ledger.py ~:4768) — fix the code and the regression.
5. Nit (Opus 6): move the `_refuse_custody_override_mint` import in joulewise/analysis_manifest_v3.py into the
   existing import paragraph — OUT OF SCOPE here; report it as a follow-up line instead of editing.
Acceptance (rc-gated to a log): tests.test_custody_mode_inventory tests.test_calibration_ledger_custody
tests.test_calibration_bracketing tests.test_calibration_ledger tests.test_authentication_io tests.test_whole_window
tests.test_floor_extraction tests.test_analysis_manifest_v3 tests.test_mint_floor_artifact tests.test_analysis_integration
tests.test_run_campaign; run every counterfactual above in memory and report kills; git diff --check; no commit;
header < 8192 bytes; body = per-item change list with file:line and tails.
