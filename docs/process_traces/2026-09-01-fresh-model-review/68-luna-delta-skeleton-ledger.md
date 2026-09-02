```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "37 omitted Term alternatives: 15 FAILS-grade and 22 built/glossed.",
  "workspace": {
    "base_requested": "fe2fdc9cc424682d7a962e7b06a10dd59865a5be",
    "base_mode": "exact",
    "head_start": "fe2fdc9cc424682d7a962e7b06a10dd59865a5be",
    "head_end": "fe2fdc9cc424682d7a962e7b06a10dd59865a5be",
    "upstream_end": "fe2fdc9cc424682d7a962e7b06a10dd59865a5be",
    "branch": "feat/2026-09-01-skeleton"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "finding_count": 37,
    "findings": [
      {"id":"F01","severity":"should_fix","text":"trace-coverage; line 124; ### Bracketed pulse-train algorithm; FAILS — defined only later by edge-coverage prose."},
      {"id":"F02","severity":"should_fix","text":"unbounded; line 126; ### Bracketed pulse-train algorithm; FAILS — no set-theoretic meaning is supplied before the refusal list."},
      {"id":"F03","severity":"should_fix","text":"degrees of freedom; line 128; ### Bracketed pulse-train algorithm; FAILS — no meaning is supplied before the Student-t cutoff is used."},
      {"id":"F04","severity":"should_fix","text":"curvature; line 132; ### Bracketed pulse-train algorithm; FAILS — its meaning as nonlinear drift arrives only later."},
      {"id":"F05","severity":"should_fix","text":"provenance; line 673; ### Every input and every refusal remains visible; FAILS — third-party provenance is invoked without explaining its evidence."},
      {"id":"F06","severity":"should_fix","text":"three-record minimum; line 766; ### Why the selected prompt length is not yet stated; FAILS — required overlap count is explained only later."},
      {"id":"F07","severity":"should_fix","text":"count floor; line 786; ### Why the selected prompt length is not yet stated; FAILS — fixed minimum-count criterion lacks first-use explanation."},
      {"id":"F08","severity":"should_fix","text":"manifest; line 881; ## Appendix A. Reproducing this work; FAILS — its role and contents are not defined before later steps."},
      {"id":"F09","severity":"should_fix","text":"admission predicates; line 887; ### A.1 What a reader needs; FAILS — admission predicates are not defined before Section 5."},
      {"id":"F10","severity":"should_fix","text":"property-list; line 908; ### A.3 Formal calibration algorithms; FAILS — file format is named without explaining property-list documents."},
      {"id":"F11","severity":"should_fix","text":"cumulative counter; line 913; ### A.3 Formal calibration algorithms; FAILS — cumulative accumulation is not defined."},
      {"id":"F12","severity":"should_fix","text":"Seidel-type; line 1005; ### A.3 Formal calibration algorithms; FAILS — solver variant is named without explaining its algorithm or role."},
      {"id":"F13","severity":"should_fix","text":"nonconvergent; line 1063; ### A.3 Formal calibration algorithms; FAILS — termination status is named without explaining exhaustion means failure."},
      {"id":"F14","severity":"should_fix","text":"argmin; line 1093; ### A.3 Formal calibration algorithms; FAILS — optimization operator is used without a plain-language meaning."},
      {"id":"F15","severity":"should_fix","text":"custody; line 1173; ### A.4 Executable verification order; FAILS — verification step lacks an evidence-chain meaning."},
      {"id":"F16","severity":"nit","text":"members; line 132; ### Bracketed pulse-train algorithm; glossed-at-first-use."},
      {"id":"F17","severity":"nit","text":"reintegrate; line 341; ### Comparing the boundary-moved and point-only bounds; glossed-at-first-use."},
      {"id":"F18","severity":"nit","text":"ulp; line 367; ### Comparing the boundary-moved and point-only bounds; glossed-at-first-use."},
      {"id":"F19","severity":"nit","text":"serially correlated; line 550; ### Adding publication safeguards after the ratio; glossed-at-first-use."},
      {"id":"F20","severity":"nit","text":"MLX; line 599; ### Outcome sentence forms; glossed-at-first-use."},
      {"id":"F21","severity":"nit","text":"ppm; line 904; ### A.3 Formal calibration algorithms; glossed-at-first-use."},
      {"id":"F22","severity":"nit","text":"interval aggregate; line 913; ### A.3 Formal calibration algorithms; built-before."},
      {"id":"F23","severity":"nit","text":"half-width; line 925; ### A.3 Formal calibration algorithms; glossed-at-first-use."},
      {"id":"F24","severity":"nit","text":"rollover; line 943; ### A.3 Formal calibration algorithms; built-before."},
      {"id":"F25","severity":"nit","text":"van der Corput sequence; line 947; ### A.3 Formal calibration algorithms; glossed-at-first-use."},
      {"id":"F26","severity":"nit","text":"affine; line 961; ### A.3 Formal calibration algorithms; glossed-at-first-use."},
      {"id":"F27","severity":"nit","text":"Fourier–Motzkin elimination; line 999; ### A.3 Formal calibration algorithms; glossed-at-first-use."},
      {"id":"F28","severity":"nit","text":"first-parse lag; line 1014; ### A.3 Formal calibration algorithms; glossed-at-first-use."},
      {"id":"F29","severity":"nit","text":"admissible; line 1027; ### A.3 Formal calibration algorithms; built-before."},
      {"id":"F30","severity":"nit","text":"MAD; line 1061; ### A.3 Formal calibration algorithms; glossed-at-first-use."},
      {"id":"F31","severity":"nit","text":"Amplitude; line 1069; ### A.3 Formal calibration algorithms; glossed-at-first-use."},
      {"id":"F32","severity":"nit","text":"Significance; line 1098; ### A.3 Formal calibration algorithms; glossed-at-first-use."},
      {"id":"F33","severity":"nit","text":"monotone; line 1107; ### A.3 Formal calibration algorithms; glossed-at-first-use."},
      {"id":"F34","severity":"nit","text":"bisect; line 1108; ### A.3 Formal calibration algorithms; glossed-at-first-use."},
      {"id":"F35","severity":"nit","text":"depth-first; line 1108; ### A.3 Formal calibration algorithms; glossed-at-first-use."},
      {"id":"F36","severity":"nit","text":"Projection; line 1109; ### A.3 Formal calibration algorithms; glossed-at-first-use."},
      {"id":"F37","severity":"nit","text":"percentile; line 1131; ### A.3 Formal calibration algorithms; glossed-at-first-use."}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_paper_first_use_ledger",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 3 tests in 0.227s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 3 tests.*OK"}
    }
  ],
  "flags": []
}
```

## Findings

- F01–F15: should-fix omissions listed in the envelope.
- F16–F37: nit omissions listed in the envelope.
## Magistrate disposition (bench, 2026-09-01)

Audience-vocabulary boundary (ruling 59f: the magistrate's): F03 degrees of
freedom, F11 cumulative counter, F14 argmin are textbook/plain vocabulary for
the metrology/CS reader and join the preamble's class list. The other twelve
FAILS (F01, F02, F04-F10, F12, F13, F15) were glossed at first use on the
skeleton branch, commit `c8509d84`. All 37 rows are added to the ledger by
Sol (trace 72) with dictated statuses; the count sentence becomes 189.
