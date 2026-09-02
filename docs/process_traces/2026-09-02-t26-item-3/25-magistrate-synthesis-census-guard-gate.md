# Magistrate synthesis of the census-guard cold gate (files 22–24), 2026-09-02

Packet: file 22. Seats: cold Fable ruling (file 23) and Opus 5 contract-lens
refutation (file 24), both read-only, packet + primary evidence only. Both
seats disclosed harness contamination (rule-11 doctrine auto-loaded); both
grounded every conclusion in executed evidence, and both are custodied
verbatim. This file is the magistrate's synthesis of a SPLIT verdict —
synthesized, not majority-voted — with the disposition of every question and
every hygiene finding against the packet.

## Where the seats agree (adopted without further deliberation)

| Question | Both seats | Adopted |
| --- | --- | --- |
| Q1 | Same defect class as Sol 256 F1 ("the guard's hand-enumeration of reference forms is incomplete"); the round-1 bench cure was fix round 1; rule 11 met; standing escalation trigger (two rounds, one signature) independently satisfied. Both seats reject terra's own proposed cure ("also reject `ast.alias`") as a same-shape round three. | Yes. No third enumerated node type is installed. |
| Q2, whitelist | REJECTED by execution. The packet's raw-text token-count whitelist (a) REGRESSES against the current guard because it replaces the `ast.Constant` check: Fable M27 (escaped string `"\x5ffresh_probe"`), M29 (NFKC homoglyph alias), Opus 12 (`importlib` with a literal constant), Opus 14 (implicit string concatenation `"_fresh_" "probe"`, parse-time folded into one `Constant`) are killed today and would survive; (b) fails on harmless comments and docstrings naming the helper (Fable M16/M17, Opus 10/13); (c) is only a one-token bookkeeping inequality (Opus 25/26). | The whitelist is NOT installed, in-PR or ever. |
| Q2, census arithmetic | NEW MATERIAL DEFECT found independently by both seats (Fable M35, Opus 19/25): the site loop walks every `FunctionDef` and `ast.walk(node)` re-walks nested defs, so a call inside a closure is counted twice. Bench-confirmed this session (executed evidence below): one closure site in `_derive_power` reports `{'_derive_power': 4, '_inner': 1}` = 13 for 12 real sites. Direction: the census overstates, so the bound loosens silently — not a physics hazard, but the equality the test claims is false of the code. | Cured in the same bench commit: post-R1 count derived from the DISTINCT set of direct-call `Name` nodes, not the per-function sum. |
| Q3, computed names | Operator-only / deliberate-only: `"_fresh_" + "probe"`, `importlib` lookup, f-string names, star-import rebinding. No guard; recorded in the docstring. | Yes. |
| Q4, docstring | The current docstring overclaims ("a twelfth post-R1 site … fails here instead of silently changing the governed envelope") and states no limits. Opus: the highest-value line in the item is the docstring rewrite. Fable: "the test lies about its guarantee". | Rewritten in the same bench commit (text below). |
| Q4, one more §5 pass | Both: one bench commit, one more fresh pass over its delta. | Yes; the pass is by a model that has not seen this item (Sol or luna). |

## Where the seats split, and the synthesis

### Closure shape (Q2)

- Fable: replace the enumerated `indirect` block by a GENERIC IDENTIFIER-FIELD
  CENSUS — walk every node, every str-valued field (`ast.iter_fields`, lists
  included); any value equal to `"_fresh_probe"` is a mention; the only
  permitted mentions are the single `FunctionDef.name` and the `Name.id` of
  each counted direct `Call.func`. 36-mutant table: kills every literal-name
  form including M27/M28/M29 (parser-normalised), stays comment/docstring-
  blind, needs no node-type list, covers binder fields added by future
  grammar. Same line count as the current block.
- Opus: keep the enumeration, add `ast.alias` (one line), fix the census bugs,
  rewrite the docstring; put larger additions on a kernel row because "adding
  eight-plus lines of new census logic inside the merge gate is how a fix
  round introduces the next defect."

Synthesis: **the Fable shape is installed.** Reason: Opus's (iii) "add
`ast.alias`" is by both seats' own Q1 reasoning the same-shape round three
the standing escalation trigger forbids — Python binds identifiers through
at least eleven string-valued AST fields (Fable's table: `alias.name`,
`alias.asname`, `ClassDef.name`, `AsyncFunctionDef.name`, `arg.arg`,
`keyword.arg`, `ExceptHandler.name`, `Global.names`, `MatchAs.name` …), and a
fourth enumerated entry leaves the other seven open (Fable M18–M23, M36).
Opus's economy argument is honoured in its substance: the field census is not
"eight-plus lines of new logic" — it is a shorter, list-free replacement of
the existing block, and it is a strict superset of what the current block
kills (it kills M27/M29 which the whitelist would have lost). Opus's
additive proposals (iv)–(v) — census `_execute_probe` as the actual resource,
pin `_DERIVERS` injectivity, forbid loop ancestry on governed sites — are
NOT installed in-PR; they go to a kernel row (below).

### Residual (Q3) and the altitude of the defect

- Fable: residual = computed names (D-161, no guard) + wall-time changes
  inside/around `_fresh_probe` (M14 decorator on the def, M34 retry inside
  the body; NIT, optional two-line pin) — recorded, not built.
- Opus: D-161 governs production REFUSALS against an actor, not test coverage
  for a developer — applying its operator-only carve-out to a unit test is a
  category error; and the real residual is the MISTAKE-class set that
  changes the runtime envelope with no computed names at all: a loop around
  a site (the R1 site at line 1101 is already in a `for` loop), a deriver
  registered for a second row, a direct `_execute_probe` caller such as
  `_boot_probe` (line 2359) moved above the `validity_origin` stamp (line
  2324), a wait relocated into `arm_readiness.py` (the 20 s git ceilings at
  2723/3039/4379/5210 were never in the censused file). The census is a
  static lexical check being asked to certify a runtime quantity; the
  ruling's own 2026-09-02 correction already records the fixed subtotal as
  715 s against the ruled 600 s and assigns the runtime question to
  `T0-LIVENESS-BOUND-EMPIRICAL-01`.

Synthesis: **Opus is right about the altitude and Fable is right about the
disposition of the computed-name subset.** The packet's Q3 was a compound
question (it presupposed D-161 governs); the answer that survives is: the
test pins the PROVENANCE ARITHMETIC of the ruling (eleven static post-R1
sites × 45 s + 105 s = the constant) and nothing about the runtime envelope.
The docstring says exactly that, names both residual classes (deliberate
name construction — no guard; ordinary-maintenance envelope changes —
carried by the empirical row and the new kernel row), and cites the 715 s
correction. Whether D-161 formally governs test coverage is a process
question and is NOT ruled here; it is noted for Ed with the two process
proposals already in the PR body.

### Merge gating (Q4)

- Fable: (a) install in-PR + M35 fix + one delta pass; severity MATERIAL not
  blocker.
- Opus: (b) with exception — merge after one bench commit (docstring +
  `ast.alias` + census bugs); no blocker; terra F1 alone is a nit; the
  whitelist is a blocker against adoption; the census test is NOT a ruled
  enforcement (item 3's Enforcement paragraph names the `<= 600 s` conjunct
  at `arm_readiness.py:6484` and the boundary controls at
  `tests/test_arm_readiness.py:60,63` and `tests/test_t0_rehearsal.py:564,570`
  — the census test is a discretionary provenance pin).

Synthesis: the two answers coincide operationally — one bench commit to the
test, one §5 fresh pass over its delta, then merge. The commit carries the
field census (Fable), the distinct-node count (both), and the docstring
rewrite (Opus). Nothing else changes in the PR. Severity: no blocker against
#274; the guard gap and the double count are MATERIAL/should-fix and are
cured before merge because the cure is bench-sized.

## New kernel row (main, after merge)

`T0-PROBE-CENSUS-RESOURCE-01` (p3_hardening_candidates, agent lane): census
the RESOURCE, not the wrapper — assert `_execute_probe` has exactly two
direct call sites (inside `_fresh_probe` and `_boot_probe`), that both
`_boot_probe` calls sit outside the R1→stamp window, that `_DERIVERS` is
injective, and that no post-R1 `_fresh_probe` site has a loop ancestor.
Opus (iv)–(v); Fable M14/M34 optional pin. Stop card: the empirical row
supersedes all of it once a retained receipt carries both stamps.

## Findings against the packet — disposition (charter §6)

| Finding | Seat | Disposition |
| --- | --- | --- |
| Whitelist "closes the whole class" asserted without execution; regression undisclosed; docstring false-positive undisclosed | Fable 1–2, Opus H1–H3 | UPHELD. The magistrate assembled a candidate it had not mutation-tested and presented it as a superset. Lesson recorded: a packet may name a candidate cure only with its executed mutant table, or must say "untested". |
| Residual named the harmless subset and omitted the harmful one | Opus H4–H5 | UPHELD. `_execute_probe`/`_boot_probe` absent from the packet; the mechanism section was built around the wrapper. |
| Packet never states the census test is not ruled | Opus H6 | UPHELD; corrected in this synthesis and in the docstring. |
| Packet quotes the provenance sentence but not the same-day 715 s correction | Opus H7 | UPHELD; the docstring cites the correction. |
| Executed-evidence block transcribed, not pasted (lines 1723–1726 and `def` at 476 elided; ellipsis misplaced) | Opus H8, Fable 3 | UPHELD — a PD-1 violation by the assembler. The exact `grep -n` output is pasted below. |
| Q1 phrased with the conclusion embedded; Q3 compound | Fable 4, Opus H9 | UPHELD in form; neither seat's answer was affected. Future packets state the binary and the wider frame separately. |
| Reproduced test body, token count 13, no-other-mentions claim, provenance paraphrase, round-1 mutant set, checkout pins | both | Verified accurate by both seats. |

## Executed evidence (bench, `/Users/edr/code/JouleWise-wt-t26-b`, this session)

```
$ grep -n "_fresh_probe" joulewise/arm_readiness_evidence_t0.py
476:def _fresh_probe(
1101:        probe = _fresh_probe(context, kind, f"R1 {server}", argv)
1216:    probe = _fresh_probe(
1318:    probe = _fresh_probe(
1365:    probe = _fresh_probe(context, kind, "thermal", ("/usr/bin/pmset", "-g", "therm"))
1723:        _fresh_probe(context, kind, "keep-awake", ("/usr/bin/pgrep", "-x", "caffeinate")),
1724:        _fresh_probe(context, kind, "agent", ("/usr/bin/pgrep", "-lf", "codex|claude|t3")),
1725:        _fresh_probe(context, kind, "browser", ("/usr/bin/pgrep", "-lf", "Chrome|Safari|firefox")),
1726:        _fresh_probe(context, kind, "monitor", ("/usr/bin/pgrep", "-lf", "Activity Monitor|top")),
1801:    probe = _fresh_probe(
1836:    batt = _fresh_probe(context, kind, "AC state", ("/usr/bin/pmset", "-g", "batt"))
1837:    custom = _fresh_probe(context, kind, "low-power mode", ("/usr/bin/pmset", "-g", "custom"))
1838:    profiler = _fresh_probe(
$ python3 <in-memory M35b probe: one closure call site inserted at the top of _derive_power; census() re-implemented from the test body at e17ea794>
base ({'_fresh_clock_reference_batch': 1, '_derive_clock_probe': 1, '_maintenance_probe': 1, '_thermal_probe': 1, '_derive_process_census': 4, '_derive_powermetrics': 1, '_derive_power': 3}, 12)
M35b ({'_fresh_clock_reference_batch': 1, '_derive_clock_probe': 1, '_maintenance_probe': 1, '_thermal_probe': 1, '_derive_process_census': 4, '_derive_powermetrics': 1, '_derive_power': 4, '_inner': 1}, 13)
```

(The bench commit that carries this file also carries the cured test; its
mutation probe and module run are pasted in file 26, the disposition of
the bench commit, and the §5 fresh pass over it is file 27.)
