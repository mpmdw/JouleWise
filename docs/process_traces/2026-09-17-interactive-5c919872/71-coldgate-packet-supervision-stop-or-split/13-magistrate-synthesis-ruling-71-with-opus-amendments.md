# Magistrate synthesis of cold-gate ruling 71 with the Opus pairing refuter's amendments (interactive session 5c919872, 2026-09-18 00:1x PDT)

Inputs: `10-coldgate-fable-ruling.md` (cold Fable judge), `12-opus-pairing-refuter-on-ruling-71.md` (Opus, contract lens). No verdict is reversed.

| Q | In force | Amendments carried |
|---|---|---|
| Q1 | REJECT: the round-3 invariant (record 20 line 18) is the right bar; a bookkeeping-length in-process mutex is not a violation; replacement bar as the ruling states it (bounded small against the 30 s cadence; REFUSED receipt within one tick + 1 s cleanup) | The clause "a lock held by another thread" was verbatim in the MAGISTRATE'S audit brief (record 22 line 9), not invented by the packet: brief drift between the implementation contract and the audit bar, owned by the magistrate. Delta-23 F1 dissolves; F2 is a NIT (comment). |
| Q2 | AFFIRM one scoped round 4 (F1–F6), fifth forbidden; F3 (exec wait on the return path) is the real BLOCKER; conditions: F3 regression crosses the production boundary; round-4 audit on its own interpreter with a green six-module run; full replay on the round-4 head | The packet's "11 of 14 operation rows accepted" was wrong (7–8 of 13; 12 of 13 once F1/F2 dissolve) — strengthens Q2. Sharper F3 statement: `poll_cleanup`'s own comment at :2179 ("neither launch completion nor exit is awaited") is contradicted by :2192. Round-4 brief (record 24) already implements these dispositions. |
| Q3 | AFFIRM the split as FALLBACK with four boundary conditions | `run_night.py:298` is NOT a v4 dispatch site (it is inside `_write_driver_refusal`); the dispatch is :2755–2758. Carried into any PR-1 brief. |
| Q4 | AFFIRM: code-enforced fail-closed v4 refusal + two regressions if split | same :298 correction |
| Q5 | REJECT: `--observation` is the worker entry, not a sampling CLI; lane 232 samples through a harness that supplies the pipe, and quotes no observer floor from it | — |

Decision: round 4 first (running as record 24); the split is taken only if a BLOCKER survives round 4. The round-4 delta audit brief will quote the ruling's bar verbatim (never the record-22 clause) and name the audit's interpreter.

Field note for codex-delegation: Astra's design consult (19) was adopted and its round left one real blocker of the pre-drawn class and two false positives from my own stricter audit wording; the cold gate's value here was catching the magistrate's brief drift, which neither seat nor auditor could see.
