# Opus 5 counter-review of the round-7 fence after fix round 1 (report 207)

Magistrate's transcription of the Opus agent's returned findings (the agent
ran against `feat/2026-09-02-dx-registry` @ `3f1677b7` in a detached
worktree; raw command outputs are in `../opus207/{lit,full,absent}.txt`).
Verdict: NOT CLEAN. The four round-1 fix regressions were confirmed
defect-shaped; identity traces DX-010/016/021/003/023 bound; module suite 21
tests OK (481 s); full replay `R7F COMPARED 184 / MISMATCHES 0` EXIT 0.

Items B1, B2, S3, N1–N5 are dictated as closures in `../fix-dx-2a.md`
(Sol 216, in flight) and are NOT before the cold gate. S1 and S2 are.

## S1 (should-fix) — type-laxness survives at uncured sites

- `scripts/check_paper_round7_artifacts.py:369-370` `_decimal(value)`:
  `return value if isinstance(value, Decimal) else Decimal(str(value))`
  accepts `str` (and `float`, `bool`) — a re-issued artifact that changes a
  numeric field to the string `"4.05"` or the boolean `True` still compares
  equal to the registry literal after `Decimal(str(...))`.
- `:155` `_comparison(...)`: `match = expected == observed` with Python
  equality — in `check_gates` (`:493-506`) a gate value `True` matches an
  expected `1` or `1.0`, and `1` matches `True`.
- Same signature as luna 189's round-1 finding (an `int()` call truncating
  `4.9 → 4` on count fields), which round 1 cured ONLY at `_exact_int`
  (`:385-388`, rejects `bool` and non-`int`). The class is "scalar reads
  coerce instead of refuse"; round 1 patched one site of it.
- Cheapest regression: a gate JSON with `true` where `1` is expected →
  must be MISMATCH/REFUSED; a per-pulse value `"4.05"` (string) where a
  number is expected → REFUSED.

## S2 (should-fix) — the skeleton literal check has nothing to check

- `check_skeleton_literals` (`:581-604`) compares only literals that follow a
  `[FILL:DX-nnn]` marker; `docs/paper/draft-v2-skeleton.md` contains ZERO
  such markers today, so the check emits zero comparisons and passes
  vacuously (the "literals-only" tail counts registry rows, not placements).
- No placement census: nothing asserts each of the 16 non-identity DX rows is
  placed at least once, so a row can simply never reach the paper.
- No bare-prose scan: a DX value typed into prose WITHOUT a marker
  (e.g. "…refused 59 of 599 pulses…") is invisible to the fence — the exact
  failure mode the fence exists to catch (a number in the paper that no
  registry row governs).
- Suggested acceptance: a census (each DX row placed ≥ 1, flag-gated so the
  unfilled skeleton does not fail today) and a scan that flags each row's
  rendered literal appearing outside a marker.

## Not before the cold gate (for context)

B1 absent-corpus tail collision (`:799-804`, `--corpus-root` default `:774`,
checklist `:24-25`); B2 prefix match `observed = suffix[: len(expected)]`
(`:600-603`); S3 substring sniff of producer output (`:711-714`, `:739-742`);
N1 `pulses[index]` TypeError (`:534-537`, `:573`); N2 hardcoded gate paths;
N3 tautological `source_sha256_*` renderer (`:404-408`); N4 hardcoded English
"(all …)/(both …)" (`:445`, `:456`, `:463-464`); N5 pinned replay command not
the executed argv.
