# Record 28 — final fresh-eyes pass on round 2 (`f5013dd9`), EVIDENCE-NIGHT-ENTRY-01 slice A, 2026-09-20 ≈09:05 PDT

Auditor: Opus 5 subagent (same auditor as record 27; read-only; /tmp copy). Verbatim:

VERDICT: PASS — round 2 (f5013dd9) closes F1–F6; nothing new.

(1) Preflight claim CONFIRMED. `joulewise/night_agent_install.py:1118-1121` runs `[python, -B, scripts/run_night.py, preflight, --plan, …]` and raises `Refused(2, "night driver preflight failed")` on nonzero. It sits in `validate_install` (def at :1083) **before** any render-only branch (`args.render_only` first consulted at :1143/:1148), so it is unconditional on the render-only path the entry invokes at `joulewise/evidence_night.py:443`. F1 was indeed documentation, not a missing call. One environmental precondition, unchanged by this round: the same function requires `shutil.which("claude")` at :1114 or refuses "courier unavailable" — so the entry's render step needs the courier on PATH.

(2) Contract paragraph accurate. `docs/contracts/evidence_night_entry.md:98-108`: preflight sentence matches the code above; the four named resume refusals match `evidence_night.py:346, 351, 373, 397` verbatim; the install-close ordering claim matches `:463` (last check, after clone/venv/render); the 40-minute floor is named as superseded by the runway warning (`:307-308`, consult 18). No overclaim found.

(3) Tests, /tmp copy at f5013dd9 (`PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_evidence_night -v`), tail:
```
test_unexpected_builder_is_error_exit_one ... ok
----------------------------------------------------------------------
Ran 23 tests in 65.669s

OK
```
Test edits verified: `CENSUS_SUBSTRINGS` imported from `scripts.gen_derivation_night` with fallback (:19-22), `dir="/tmp"` on the recipe fixture (:87), dead redraw loop gone (:106).

(4) Same-signature statement, class "the entry point silently diverges from the bench procedure": NOT reproduced in round 2. Round 1 cured it in code (C3, mutation-killed); round 2 is docs+tests only and adds no code path, so no second instance and no re-audit-worthy delta. F3 accepted as out of lane on the stated handbook-rewrite grounds. No further round warranted on this signature.

## Magistrate note
The courier-on-PATH precondition (`shutil.which("claude")` in `validate_install`) is inherited from the installer and applies to the bench today as well; it is carried to slice B's pre-arm checks, not changed here.
