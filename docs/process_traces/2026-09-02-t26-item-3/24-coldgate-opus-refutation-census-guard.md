# Opus 5 contract-lens refutation — census-guard packet (file 22), 2026-09-02

Seat: Opus 5 (Agent tool, read-only, packet + primary evidence only). Custodied verbatim from the task transcript; scratchpad paths redacted.

## Contamination disclosure (charter §2)

I am not doctrine-free. This session auto-loaded `~/.claude/CLAUDE.md`, the repo `CLAUDE.md`, `CLAUDE.local.md` (rule 11 and the standing escalation trigger verbatim) and the memory index, including a one-line summary of D-161. I ran from the main-checkout session context, not a clean worktree. Mitigations: I read D-161 from `docs/decision_log.md:207` rather than from memory, and every claim below is executed or quoted from a named file. I did not open trace files 01-21 (round-1/round-2 seat reports), per the read scope; my Q1 classification rests on the code, the ruling, and the packet's own summaries of those findings.

## Charter digest

Verified independently of the packet.

```
$ shasum -a 256 docs/process/coldgate_charter.md
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81  docs/process/coldgate_charter.md
$ sed -n '16p' docs/process/coldgate_charter_registry.md
| sha256 | `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` |
```

Match. Registry status RATIFIED, v2 (2026-08-03). Checkout at `a5040ed0`; parent `e17ea794` is the code head named. Digest as stated in the packet: **correct**.

## Q1 classification

Answered before and independently of Q2-Q4.

**Rule applied.** Two findings are the same defect class iff the root cause named by the first, cured correctly in the kind of cure the first implies, would also have prevented the second. Class is fixed by root cause and cure-shape, not by node type or by who found it.

**Root cause of Sol 256 F1**, as the shipped code itself states at `tests/test_arm_readiness_evidence_t0.py:887-892`: "The census counts direct calls, so it is only complete if direct calls are the ONLY way the module reaches `_fresh_probe`." The defect is that the completeness argument is carried by a hand-enumerated list of reference forms.

**Terra 257 F1** is an omitted entry in that same hand-enumerated list — `ast.alias` joins `Name`, `Attribute`, `Constant`. Same assumption, same enumeration, same cure shape (extend or replace the enumeration).

**Verdict: SAME defect class. Rule 11's mandatory trigger is MET** — the bench cure at `e17ea794` was fix round 1; a cure of terra's F1 is a second fix round on the same defect. Convening this gate was correct, and the standing escalation trigger ("two consecutive rounds failing with the SAME SIGNATURE ... the next spend is a CONSULT, not round three") is independently satisfied: two rounds, one signature — "another missed reference form."

**But Q1 as posed is a false binary, and I decline to stop there.** Both findings are members of a proper subclass — "reference forms of the literal name `_fresh_probe` that the enumeration omits" — of a larger defect whose root is one level up: **the test is a static lexical census being asked to certify a runtime quantity (how many 45-second bounded waits actually elapse between R1 completion and the validity-origin stamp).** Every cure inside the subclass leaves the superclass untouched. Q2 shows this is not theoretical: six executed mutants change the runtime envelope while passing both the current guard and the candidate whitelist, and none of them uses a computed name or any indirect reference form at all.

So: yes, same class; and the class as the packet names it is the wrong altitude at which to cure.

## Q2 closure shape

Both guards re-implemented as pure functions over source text (`<scratch>/harness.py`), the current one transcribed line-for-line from `tests/test_arm_readiness_evidence_t0.py:871-920`. Baseline sanity: `current=True post_r1=11 | whitelist=True tokens=13 post_r1=11`, and the real test passes at HEAD (`Ran 1 test ... OK`). Mutations are applied to an in-memory copy of the module source; nothing under any checkout was written.

`dS(s)` is the change in the governed R1-to-stamp wait envelope, in seconds. "BENIGN" mutants change nothing and should NOT fail; a kill there is a false alarm, which is a defect of the guard.

```
mutant                                     dS(s)  current   whitelist note
--------------------------------------------------------------------------
1 alias (Sol 256)                          45     killed    killed    aliased binding, one extra governed probe
2 globals() string literal                 45     killed    killed    string-literal global lookup
3 stored callback                          45     killed    killed    callback stored in a dict
4 twelfth direct call                      45     killed    killed    plain twelfth post-R1 site (the control)
5 ImportFrom shadow (terra 257)            n/a    SURVIVES  killed    rebinds the name; census counts a site that is not the local helper
5b module-level ImportFrom shadow after def n/a   SURVIVES  killed    terra's form at module scope
6 import x as _fresh_probe                 n/a    SURVIVES  killed    asname rebinding
7 decorator application                    0      killed    killed    decorator reference is a bare Name, not a Call.func
8 nested redefinition                      0      killed    killed    shadowing def inside a deriver
9 __all__ string                           0      killed    killed    name as an export string
10 docstring mention            (BENIGN)   0      SURVIVES  killed    false alarm on the whitelist
11 computed name via globals()             45     SURVIVES  SURVIVES  runtime-computed name
12 importlib-constructed lookup            45     killed    SURVIVES  REGRESSION: whitelist loses a form the current guard kills
13 comment mention              (BENIGN)   0      SURVIVES  killed    false alarm on the whitelist
14 implicit string concat "_fresh_" "probe" 45    killed    SURVIVES  REGRESSION: parse-time fold makes one Constant; regex sees none
15 loop around one site                    unbnd  SURVIVES  SURVIVES  one static site, N runtime governed waits
16 _execute_probe bypass on the post-R1 path 45   SURVIVES  SURVIVES  same 45 s timeout, reached without _fresh_probe at all
17 second _boot_probe moved into the window 45    SURVIVES  SURVIVES  _boot_probe also spends _PROBE_TIMEOUT_SECONDS
18 deriver registered for a second row     135    SURVIVES  SURVIVES  same three static sites run twice
19 nested helper wrapping one call (BENIGN) 0     killed    killed    census double-counts calls inside nested defs
20 module-level rebinding to a partial     0      killed    killed    Name-target assignment rebinding
21 f-string computed name                  45     SURVIVES  SURVIVES  f-string-computed name
22 unreachable extra site       (BENIGN)   0      killed    killed    static site never on the R1->stamp path
23 site moved to a sibling module          45     SURVIVES  SURVIVES  governed wait relocated out of the censused file
24 timeout constant raised 45->90          495    killed    killed    [corrected run, see below]
25 nested-helper hide + 1 comment token    45     SURVIVES  SURVIVES  literal names only; survives BOTH
26 mutant 25 without the comment           45     SURVIVES  killed    shows 25's token arithmetic is a one-token rebalance
```

Corrections to my own harness, stated rather than hidden: the first pass modelled only source text and therefore mis-scored mutant 24, because the real test reads `t0._PROBE_TIMEOUT_SECONDS` off the imported module. Re-run with that assertion modelled (`<scratch>/extra.py`): `24 timeout raised 45->90 : current=(False, 'timeout 90 != 45') | whitelist=(False, 'timeout 90 != 45')` — killed by both, as the table now records.

**Answer to Q2: the token-count whitelist does NOT close the literal-name class, and it is not a superset of the guard it would replace.** Three separate results:

1. **It regresses.** Mutants 12 and 14 are killed by the current `ast.Constant` check and survive the whitelist. Python folds adjacent string literals at parse time, so `globals()["_fresh_" "probe"]` is a single `ast.Constant` with value `"_fresh_probe"` — visible to the AST check, invisible to `\b_fresh_probe\b` over the source text. The packet says the census and the `FunctionDef == 1` pin "stay" and never discloses that replacing the enumerated block loses forms already killed. Adopting the whitelist as written is a net loss on two named forms in exchange for a gain on three (5, 5b, 6).

2. **It admits a named literal-only survivor.** Mutant 25 uses nothing but ordinary `_fresh_probe` calls and one comment. It exploits a bug inside the census both guards share: `for node in ast.walk(tree)` yields nested `FunctionDef`s, and `ast.walk(node)` on the enclosing function descends into them, so every call inside a nested def is counted twice. Wrapping two of `_derive_power`'s three calls in a nested one-line helper called three times leaves `sites_by_function` summing to 11 while the runtime performs 12 governed waits; the token count falls by one, and one benign comment naming the helper puts it back. Executed: `25 ... current=(True, 'post_r1 = 11') whitelist=(True, 'tokens=13 post_r1=11')`. Mutant 26 (same, no comment) shows the whitelist's inequality is doing only a one-token bookkeeping job, not a structural one. The packet's claim that the inequality "closes the whole 'literal name appears somewhere the census does not count' class" is refuted by execution.

3. **It fires on documentation.** Mutants 10 and 13 are benign — a maintainer writing `# ... uses _fresh_probe like every other census row`, or a docstring on `_boot_probe` saying "like `_fresh_probe` but for the boot session." The whitelist fails the build for both. This is perverse in the specific case at hand: the single most useful comment anyone could add to this module is one on `_boot_probe` warning that it also spends `_PROBE_TIMEOUT_SECONDS` — which is exactly mutant 17's hazard — and the candidate cure forbids writing it.

**The six that survive both, and what they are.** Mutants 15, 16, 17, 18, 23, 25 change the governed envelope by +45 s to unbounded while both guards pass. None is an adversary construction; all are ordinary maintenance:

- **16 / 17** — `_PROBE_TIMEOUT_SECONDS` is spent by `_execute_probe` (`joulewise/arm_readiness_evidence_t0.py:449`, `:466`), which has exactly two callers: `_fresh_probe` (`:493`) and `_boot_probe` (`:501`). The census guards the wrapper, not the resource. `_boot_probe` is called twice (`:2284` before the row loop, `:2359` after the `validity_origin` stamp at `:2324`), so today's 495 s is correct **by accident of statement ordering**, not by anything the test checks. Moving the second `_boot_probe` three lines earlier adds 45 s silently.
- **15** — the R1 site at `:1101` already sits inside a `for` loop and runs once per server. The static/dynamic gap is not hypothetical; it is present in the very function the test special-cases.
- **18** — `_DERIVERS` (`:1944-1960`) is a 15-row dispatch table that is currently injective. Nothing pins that. Registering an existing deriver against a second row runs its sites twice.
- **23** — the ruling's own 2026-09-02 correction records that the fixed subtotal includes "220 s of eleven 20 s git ceilings"; those `timeout=20` calls live in `joulewise/arm_readiness.py:2723, 3039, 4379, 5210`, a file the census never parses. Relocating a wait across the module boundary is invisible by construction.

**Shape I would install instead.** Not the whitelist. In descending value per line:

- (i) **Rewrite the docstring** to state what is and is not protected (see Q4 — this is the highest-value line in the whole item).
- (ii) **Fix the census's two internal bugs**: accumulate with `+=` keyed by `(name, node.lineno)` rather than assigning to `sites_by_function[node.name]` (the current keying silently collides on duplicate names — the module already has two `__init__`s), and skip nested `FunctionDef`s when walking an enclosing one, so mutant 19 stops false-alarming and mutant 25's offset disappears.
- (iii) **Add `ast.alias` to the existing `indirect` enumeration** — one line, kills mutants 5, 5b, 6, regresses nothing. Keep the `Constant` and `Attribute` checks that the whitelist would have discarded.
- (iv) **Census `_execute_probe` too**: assert exactly two direct call sites and that they are inside `_fresh_probe` and `_boot_probe`. This pins the actual resource and closes 16; it is stable (two sites for the life of the module) and about eight lines.
- (v) Optionally assert `len(set(map(id, _DERIVERS.values()))) == len(_DERIVERS)` (closes 18) and that no `_fresh_probe` call has a `For`/`While`/comprehension ancestor outside `_fresh_clock_reference_batch` (closes 15).

(i)-(iii) are bench-sized. (iv)-(v) are a judgment call the gate should make explicitly rather than by default; see Q4.

## Q3 residual

**The packet asks the wrong question about the wrong residual, and I disagree with terra's classification on both halves.**

**First, D-161 does not govern this.** D-161 (`docs/decision_log.md:207`) rules on *refusals* — "custody mechanisms whose ONLY defended-against actor is the trusted operator touching a file are over-engineering," with fail-closed retained "where the failure is PHYSICS/EVIDENCE or PRE-REGISTRATION." Its subject is what the production tool refuses to do at mint time, against an actor, at a cost measured in "three hand edits and blocked the mint twice." A unit test refuses nobody and blocks no mint; it fails CI for a developer. Its own decision-log elaboration at `:10508` says the job "targets the MISTAKE class." Reading D-161's operator-only carve-out onto test coverage is a category error, and the packet's Q3 embeds that error in its premise ("Are the computed-name forms operator-only under D-161?"), which is a compound question in charter §6's sense: it presupposes that D-161 is the governing rule.

**Second, on the merits of the computed-name forms specifically (mutants 11, 21, and the surviving half of 12): I agree they need no guard.** Writing `globals()["_fresh_" + "probe"]` inside this module is not a mistake anyone makes; it is a construction. No static literal check can see it, and the cost of chasing it is unbounded. Record and move on. To that extent terra's classification is right, and the packet's Q3 conditional ("If yes, the test's docstring records the residual and no further guard is built") is the correct disposition **for that subset**.

**Third, and this is the refutation: that subset is not the residual.** The residual after either guard is mutants 15, 16, 17, 18, 23 and 25 — refactors a careful maintainer performs on purpose, with no adversary anywhere in the picture. They are squarely in D-161's own MISTAKE class, so even granting the packet's framing, its answer comes out the other way. The packet's sentence "Residual: computed names (`"_fresh_" + "probe"`, `importlib`-constructed lookups) — invisible to any static literal check" is not merely incomplete; it names the harmless residual and omits the harmful one, which is the effect §6 asks me to identify.

**What closes it.** Nothing closes it completely, because the property is dynamic and the test is static — that is the Q1 superclass restated. What bounds it cheaply is Q2 (iv) and (v): census the resource (`_execute_probe`) rather than the wrapper, pin `_DERIVERS` injectivity, and forbid loop ancestry on governed call sites. Those three convert the surviving set from {15,16,17,18,23,25} to {23} plus the computed names. Mutant 23 — the wait relocated into `arm_readiness.py` — is not closable by a single-file census at all, and is the honest reason the docstring must say what it says.

And the deeper bound is already registered and does not need this test: the ruling's own 2026-09-02 correction withdraws the safety premise, records the true fixed subtotal as 715 s (495 probe + 220 git) against a ruled 600 s, and assigns the obligation to kernel row `T0-LIVENESS-BOUND-EMPIRICAL-01` — "no retained receipt yet carries both stamps, so the real R1→stamp interval is unmeasured." Measurement, not a better static census, is what actually closes this. The census test's correct scope is provenance fidelity: it should certify that the two numbers in the ruling's provenance sentence still have the values the sentence names, and say so.

## Q4 merge gating

**Answer: (b) with a bounded exception — merge, after one bench commit that fixes the docstring and adds `ast.alias`. Do not install the token whitelist, in-PR or on main.**

Stated as Q4 requires, in terms of what a maintainer of `arm_readiness_evidence_t0.py` loses during the interval:

**What they do not lose.** Everything the cold gate actually ruled is installed and independently tested. Item 3's Enforcement paragraph names three things: the `<= 600_000_000_000` conjunct in the `_predicate_passes` clock branch, boundary controls at 600 s ± 1 ns at both the issuance and arm sites, and two documentation updates. The conjunct is at `joulewise/arm_readiness.py:6484` against the constant at `:6349`; the boundary controls are at `tests/test_arm_readiness.py:60,63` and `tests/test_t0_rehearsal.py:564,570`. **The census test is not among them.** The ruling cites "§6.3's AST census" as the *source* of the number eleven; it does not mandate a test that re-derives it. So the maintainer loses no ruled protection under (b), and a reader of the packet would not know this, because the packet never says it.

**What they do lose: a docstring they will believe.** `tests/test_arm_readiness_evidence_t0.py:856-867` tells the maintainer that "a twelfth post-R1 site (or a removed one) fails here instead of silently changing the governed envelope." A maintainer reads that as "this test protects the envelope," and it does not. Six executed mutants change the envelope while it passes. The one closest to real work is mutant 17: moving the second `_boot_probe` above the `validity_origin` stamp — a plausible tidy-up, since the two boot probes bracket the derivation and someone will eventually want them adjacent — adds 45 s to a 600 s budget the ruling's own correction already records as over-subscribed at 715 s. The test goes green. That is the loss: not an uncaught form, but **a maintainer who declines to think because a docstring told them a test was thinking for them.** Terra's F1 costs that maintainer nothing during the interval; the docstring costs them the reason to check.

Would a maintainer reading the current docstring know what it does and does not protect? **No.** It states one guarantee it cannot deliver, and states no limits at all. It is also, in one respect, better than the packet: it explicitly declines to pin the `_MIN_IDLE_NS` coincidence, calling it "a coincidence of two unrelated quantities." That instinct — pin the derivation, refuse the accident — is the right one and should be extended to the whole docstring.

**Therefore the exception.** One bench commit, three edits, no new logic to fresh-pass:

1. Docstring rewritten to say: this test pins the **provenance arithmetic** of cold gate T26 item 3 (eleven static post-R1 `_fresh_probe` call sites × `_PROBE_TIMEOUT_SECONDS` + 105 s = the constant), so an edit to either factor fails here; it does **not** bound the runtime envelope, because a loop, a second call of a deriver, a direct `_execute_probe` caller such as `_boot_probe` moved into the window, or a wait in another module all change the envelope invisibly; the runtime interval is unmeasured and is carried by kernel row `T0-LIVENESS-BOUND-EMPIRICAL-01`; the ruling's 2026-09-02 correction records the fixed subtotal as 715 s.
2. `ast.alias` added to the `indirect` enumeration (kills 5/5b/6; regresses nothing).
3. The two census bugs from Q2 (ii) fixed.

That is squarely under rule 9's bench-vs-session threshold — smaller than the contract needed to delegate it. Q2 (iv)-(v) go to main as the kernel row, not in-PR: they are real coverage but they are additive design, and adding eight-plus lines of new census logic inside the merge gate is how a fix round introduces the next defect.

**Grading, honestly.** No blocker against merging PR #274. Terra 257 F1 on its own merits is a **nit** — it needs a maintainer to import a name that shadows a function defined earlier in the same file, which `pyflakes` F811 already flags, and by itself it changes the envelope by zero (it makes the census measure a different function). I grade it **should-fix** only because the cure is one list entry. The docstring overclaim is **should-fix** and is the item I would actually spend the round on. The candidate token whitelist is a **blocker against adoption** — it is a strict weakening on mutants 12 and 14 and a false-alarm generator on 10 and 13.

## Contract-lens findings against the packet (charter §6)

**H1 — unsupported assertion, material.** "This closes the whole 'literal name appears somewhere the census does not count' class in one inequality instead of naming node types." Refuted by execution: mutant 25 uses only literal `_fresh_probe` names and survives. Effect: leads Q2 to a false premise.

**H2 — omission, material (blocker-grade).** The packet presents the whitelist as strictly stronger ("The AST census and the `FunctionDef == 1` pin stay") without disclosing that discarding the `ast.Constant` check loses mutants 12 and 14 — including one form the round-1 cure was specifically built to kill. A seat reading only the packet would adopt a net regression. Effect: dispositive for Q2 and Q4.

**H3 — omission, material.** No mention that the whitelist fails on comments and docstrings naming the helper (mutants 10, 13), i.e. that it forbids the documentation which is the only cure available for mutant 17. Effect: Q3's own remedy ("the test's docstring records the residual") sits in tension with the cure the packet proposes, and the packet does not notice.

**H4 — misleading framing, material.** "Residual: computed names ... invisible to any static literal check" names the harmless residual and omits six survivors that change the envelope with no computed names at all. Effect: Q3 as posed cannot reach the right answer.

**H5 — omission, material.** `_execute_probe` and `_boot_probe` appear nowhere in the packet. `_PROBE_TIMEOUT_SECONDS` is spent at `arm_readiness_evidence_t0.py:449`, inside `_execute_probe`, which `_boot_probe` calls directly at `:501`. The census guards the wrapper and not the resource, and today's arithmetic holds only because both `_boot_probe` calls (`:2284`, `:2359`) happen to fall outside the window. Effect: the whole mechanism section is built around the wrong symbol.

**H6 — omission, dispositive for Q4.** The packet never states that item 3's Enforcement paragraph does not mandate a census test. Q4 asks the seats to choose between installing "the ruled shape in-PR" and merging with the finding recorded — language that presupposes the census guard is ruled. It is not. Effect: pushes the seats toward gating a merge on a discretionary artifact.

**H7 — cherry-picked excerpt, material.** The packet quotes item 3's provenance sentence but omits the correction appended to that same ruling on the same day the packet was assembled, which records the fixed subtotal as 715 s (495 probe + 220 git) — i.e. the ruling has already withdrawn the claim that 11 × 45 + 105 bounds anything. The packet's §"The mechanism under review" nonetheless says the test exists so an edit cannot "silently chang[e] the governed envelope." Effect: overstates what the test could ever be worth, in both directions.

**H8 — evidence hygiene, nit, but it is the assembler's own rule.** The `## Executed evidence` block's third command is transcribed, not pasted: it prints `1101 (R1 batch), 1216, 1318, 1365, 1801, 1836, 1837, 1838 ... + \`def _fresh_probe\`` with the ellipsis trailing, whereas `grep -n` returns `476, 1101, 1216, 1318, 1365, 1723, 1724, 1725, 1726, 1801, 1836, 1837, 1838` in that order. The count 13 is correct and the conclusion is unaffected, but 1723-1726 and the `def` line at 476 are dropped from a list a checking reader would use, and the ellipsis is in the wrong place. Item 4's own 2026-09-02 addendum makes the `## Executed evidence` section custody input; a paraphrased command output is precisely the hazard it addresses, and the duty it assigns falls "on whoever ASSEMBLES the packet."

**H9 — compound/leading question, material.** Q1 offers "same class or distinct?", a binary whose either answer keeps the deliberation inside "which reference forms to enumerate." The classification that determines the shape is one level up. Q3 likewise presupposes D-161 governs. Both are charter §6 compound questions. I answered inside and outside each.

**One thing the packet does well, recorded for symmetry.** Its framing choice — that the party proposing to continue should not classify its own defect, so Q1 goes to the seats — is correct and is applied consistently; and the packet volunteers the whitelist's computed-name residual rather than claiming total closure. The hygiene defects above are of omission and altitude, not of advocacy.

## Executed evidence

```
$ shasum -a 256 docs/process/coldgate_charter.md
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81  docs/process/coldgate_charter.md
$ sed -n '16p' docs/process/coldgate_charter_registry.md
| sha256 | `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` |
$ git log --oneline -3
a5040ed0 t26-b: terra 257 delta fresh pass custody (file 21) + cold-gate packet ...
e17ea794 t26-b: Sol 256 §5 fresh pass (file 19) + disposition (file 20) ...
7488a3c0 T26 item 3: Opus item-6 cures at the bench (file 18)
exit 0
```

```
$ grep -n "_fresh_probe" joulewise/arm_readiness_evidence_t0.py
476:def _fresh_probe(
1101:        probe = _fresh_probe(context, kind, f"R1 {server}", argv)
1216:    probe = _fresh_probe(
1318:    probe = _fresh_probe(
1365:    probe = _fresh_probe(context, kind, "thermal", ("/usr/bin/pmset", "-g", "therm"))
1723:        _fresh_probe(context, kind, "keep-awake", ("/usr/bin/pgrep", "-x", "caffeinate")),
1724:        _fresh_probe(context, kind, "agent", ("/usr/bin/pgrep", "-lf", "codex|claude|t3")),
1725:        _fresh_probe(context, kind, "browser", ...),
1726:        _fresh_probe(context, kind, "monitor", ...),
1801:    probe = _fresh_probe(
1836:    batt = _fresh_probe(context, kind, "AC state", ("/usr/bin/pmset", "-g", "batt"))
1837:    custom = _fresh_probe(context, kind, "low-power mode", ("/usr/bin/pmset", "-g", "custom"))
1838:    profiler = _fresh_probe(
$ python3 -c "import re;s=open('joulewise/arm_readiness_evidence_t0.py').read();print(len(re.findall(r'\b_fresh_probe\b',s)))"
13
exit 0
```

```
$ grep -n "_execute_probe\|_PROBE_TIMEOUT_SECONDS" joulewise/arm_readiness_evidence_t0.py
54:_PROBE_TIMEOUT_SECONDS = 45
427:def _execute_probe(argv: _Sequence[str], *, cwd: _Path) -> _ProbeResult:
449:                process.wait(timeout=_PROBE_TIMEOUT_SECONDS)
466:        raise ValueError(f"probe timed out after {_PROBE_TIMEOUT_SECONDS} seconds")
493:        return _execute_probe(argv, cwd=context.repository)
501:        result = _execute_probe(
$ grep -n "_boot_probe\|_MIN_IDLE_NS" joulewise/arm_readiness_evidence_t0.py
51:_MIN_IDLE_NS = 600 * 1_000_000_000
498:def _boot_probe(repository: _Path) -> tuple[str, _ProbeResult]:
2284:    boot_session, boot_probe = _boot_probe(repository)
2359:    second_boot, _second_boot_probe = _boot_probe(repository)
exit 0
```
(`validity_origin = context.clock.monotonic_ns()` is at `:2324`; `:2284` is pre-R1, `:2359` is post-stamp.)

```
$ python3   # enclosing-scope census of every _fresh_probe call
1101 ['<<LOOP:For>>', '_fresh_clock_reference_batch']
1216 ['_derive_clock_probe']      1318 ['_maintenance_probe']
1365 ['_thermal_probe']           1723-1726 ['_derive_process_census'] x4
1801 ['_derive_powermetrics']     1836-1838 ['_derive_power'] x3
duplicate FunctionDef names in module: {'__init__': 2}
total FunctionDefs: 73
_execute_probe direct call sites: [493, 501]
exit 0
```

```
$ python3 -m unittest tests.test_arm_readiness_evidence_t0 \
    -k test_t0_liveness_constant_is_derived_from_the_post_r1_probe_census -v
test_t0_liveness_constant_is_derived_from_the_post_r1_probe_census ... ok
Ran 1 test in 0.033s
OK
exit 0
```

```
$ python3 <scratch>/harness.py     # full mutant table above
BASELINE  current=True post_r1 = 11 | whitelist=True tokens=13 post_r1=11
  12 importlib-constructed lookup   cur:indirect [('Constant', 1367)] | wl:tokens=13 post_r1=11
  14 implicit string concat setattr cur:indirect [('Constant', 1366)] | wl:tokens=13 post_r1=11
  15 loop around one site           cur:post_r1 = 11 | wl:tokens=13 post_r1=11
  16 _execute_probe bypass          cur:post_r1 = 11 | wl:tokens=13 post_r1=11
  17 _boot_probe into the window    cur:post_r1 = 11 | wl:tokens=13 post_r1=11
  18 deriver registered twice       cur:post_r1 = 11 | wl:tokens=13 post_r1=11
  23 site moved to sibling module   cur:post_r1 = 11 | wl:tokens=13 post_r1=11
exit 0
$ python3 <scratch>/extra.py
24 timeout raised 45->90 : current=(False, 'timeout 90 != 45') | whitelist=(False, 'timeout 90 != 45')
26 nested-helper hide, no comment  tokens=12 current=(True,'post_r1 = 11') whitelist=(False,'tokens=12 != 1+ast_calls=13')
25 nested-helper hide + 1 comment  tokens=13 current=(True,'post_r1 = 11') whitelist=(True,'tokens=13 post_r1=11')
exit 0
```

```
$ grep -n "timeout=20" joulewise/arm_readiness.py
2723:            timeout=20,   3039:            timeout=20,
4379:            timeout=20,   5210:            timeout=20,
$ grep -n "_T0_R1_TO_VALIDITY_ORIGIN_LIVENESS_NS" joulewise/arm_readiness.py
6349:_T0_R1_TO_VALIDITY_ORIGIN_LIVENESS_NS = 600_000_000_000
6484:        <= _T0_R1_TO_VALIDITY_ORIGIN_LIVENESS_NS
$ grep -rn "600_000_000_001\|599_999_999_999" tests/
tests/test_t0_rehearsal.py:564,570   tests/test_arm_readiness.py:60,63
exit 0
```

No file under any checkout was created, modified, or deleted; all mutation ran against in-memory copies of the module source, with scratch files confined to `<scratch>`.
