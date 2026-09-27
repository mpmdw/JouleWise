# SWEEPCLASS-SAMESIG-01: Opus 5.5 seat (blind, parallel)

Seat: Opus 5.5. Charge `00-consult-charge.md` @ `7a341228`. Code read at `/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96` @ `315364b2`, read-only (`git status --short` = 0 lines after every probe). Scratch `/tmp/samesig-3ba66eeb-opus/`. Read in full: the round-2 refuter (`3057d03c`), the round-2 ruling §4 and §7 to §12, the round-2 charge, `bundle_read.py:280-670`, `envelope_gate.py:71-150, 228-236, 651-660`, and the sweep test at `315364b2`. The round-1 files were not opened. Contamination: the harness loaded Ed's CLAUDE files and memory index. I used D-161 and the 09-24 "prevent bad science" goal only as the charge states them.

**Executed evidence** (cwd = worktree, `.venv/bin/python`):
| Id | Probe (sha256 prefix) | Output |
|---|---|---|
| P1 | `p1.py` (41d207a0c458de03): repository `sweep_source` at `315364b2` run on B-1 forms, plus idiom counts over 209 tracked files | lambda, def under `if`, def under `try`, `__main__` call, `__main__` open, `map(lambda r: r.raw_summary())`: **all SILENT**. Control def: reported. Tree: **103 `if __name__ == "__main__"` blocks**, 51 compound statements that hold a nested def, 274 lambdas, 9 `map(<named fn>, …)`, 1 `partial` |
| P2 | `p2.py` (8c2d7cb982c51597): a runtime prototype that binds the gate to the reader's path and slot, patched in-process (no repo edit), on the charging-bundle fixture | current code: B-3 re-point **RETURNED**, `_cache.update` forgery **RETURNED**. Prototype: pass bundle returns rows (unchanged); charging bundle, re-point and forgery each **raised BatteryStatusRefusal** |
| P3 | `p3.py` (b6afc1f02b32a890): my literal implementation of the refuter's B-2 (iii) and B-3 texts, run on six "round-3" forms | the controls are reported. **SILENT:** `importlib.import_module('joulewise.battery_float').authenticate_bundle = f`; `sys.modules[...].authenticate_bundle = f`; `m = battery_float; m.authenticate_bundle = f`; `battery_float.authenticate_bundle.__code__ = g.__code__`; `vars(battery_float)[...] = f`; `r.__dict__['_path'] = b` |
| P4 | `p4.py`: every tolerant call or watched-literal read in the tree, checked against the scopes the repository detector visits | 100 watched call sites; **0 in unvisited scopes**. So B-1's closure is GREEN (passes on today's tree unchanged) |
| R1 | read `envelope_gate.py:95-133, 228-236, 651-654` | every reader that reaches `:133` or `:654` has passed `_manifest_record`, which calls `reader.metadata()` (`:233`); a `None` record refuses the run (`:104`). The behaviour-identity argument for B-4 holds |
| R2 | read `bundle_read.py:410-670`; `git grep raw_summary()` | `BundleReader` has **no gated `summary()`**. The charge's "`summary()`" does not exist. Energy in `summary_metrics.json` is reachable only through the ungated accessor `raw_summary`, which has 17 production call sites. The claim consumers call it after a separate gate call (e.g. `aggregate.py:155-156`) |

## Q1. Structure
**Verdict: not closable. This is the same signature in the rule-11 sense; round 3 of shape (a) is already predictable (P3).**
- Python lets code reach any object by a computed name or a module registry: `getattr` with a built string, `exec`, `importlib`, `sys.modules`, `vars()`/`__dict__`, `__code__` swaps, descriptors and metaclasses. So a syntactic rule is complete only for a declared list of forms, never for "every way". The ruled 51 (h) already admits this for accessor names built at run time.
- Each round re-finds one defect class at the next site:
  - RSW-1 (alias/`getattr`) became B-5 (`map` reference);
  - RSW-3 (rebinding a gate name) became B-2 (replacing the gate's behaviour);
  - RSW-2 (the `_cache` slot) became B-3 (the `_path` slot).

  P3 carries the chain one step further: six more forms are silent against the refuter's own proposed B-2/B-3 text. That is "same defect class, another missed call site" twice running. SHOULD-FIX stayed at 5, then 5.
- **Exception: B-4 is not this signature.** It is a false class label on a row of today's tree, not a latent evasion form. It gets its own disposition (Q4).

## Q2. Threat model
**Verdict: B-1 and B-5 guard against plausible accidents. B-2 and B-3 guard only against deliberate evasion. B-4 is a truthfulness defect, not a threat-model item.**
- **B-1 (accident, real).** The most natural ungated read in this repository is `print(BundleReader(p).raw_summary()["gross_energy_j"])` in a script's `__main__` block. The tree has 103 such blocks, 51 defs nested under compound statements and 274 lambdas (P1), and today's detector is silent on all of them (P1). The closure costs nothing, because 0 of today's 100 watched sites sit in those scopes (P4).
- **B-5 (accident, plausible).** `list(map(extract_rows, dirs))` or `partial(fn, …)` is ordinary Python, and the tree has 9 `map(<named fn>)` calls (P1). The rule is the same one already ruled for RSW-1, applied to the callers checks. It is GREEN on the tree (round-2 F3).
- **B-2 (deliberate).** Every form needs one of three things: a store to an attribute of `battery_float`/`bundle_read`, a subclass that overrides the gate, or `type()` with three arguments. Nobody writes those while trying to read a number. The only in-tree patch helper (`replaced(module, **kw)`, `scripts/sample_quiet_predicate_evidence.py:541`) is test harness. D-161 puts this beyond fail-closed.
- **B-3 (deliberate, close to the line).** Writing `r._path` on another object's private attribute is not an accident. It can be closed at runtime in about 6 lines (P2) if anyone wants it. It should not become a static rule.
- **The same-signature forms of P3 (W1 to W6) are all deliberate.** Under option (a) they are round 3's SHOULD-FIX list.

## Q3. Recommended design
**Verdict: (b), sharpened by a mechanical boundary for the accident class. Take one optional sliver of (c). Put the structural (c)/(d) moves in their own lanes.**
- **(b′) Freeze at the accident class.** Implement B-1 and B-5. Write the deliberate class into 51 (h) once, as a **grammar**, so no later refuter has to argue it. A form belongs to the deliberate class if its source does any of the following:
  - (i) touches an underscore-prefixed attribute of a `joulewise` object from outside its defining module;
  - (ii) stores to, or deletes, an attribute of a `joulewise` module, class or function;
  - (iii) uses `setattr`/`delattr`/`vars`/`__dict__`/`__code__`/three-argument `type`/`exec`/`eval`/`compile`/`importlib`/`sys.modules`;
  - (iv) builds an accessor or gate name at run time.

  B-2, B-3, W1 to W6 and the existing (h) items fall under it by name.
- **Optional sliver of (c): the smallest runtime check.** It lives in `joulewise/bundle_read.py::BundleReader.metadata`. The gate records the `_path` it authenticated, plus a module-private token in the cache slot. `metadata()` re-authenticates when either is missing or differs.
  - Probe P2: behaviour on honest input is unchanged, and the re-point and slot-forgery forms now raise.
  - It touches no frozen file: `battery_float.py` and the FT §E list are untouched, and no consumer gains a `battery_float` import.
  - It is still a production change against ruling §7 ("reader behaviour unchanged"), so it needs a cold-gate sentence.
  - It does **not** block S1. With it in place, no further static private-state rule is ever needed.
- **Not now.** Capability-token tolerant accessors: this would change 51 call sites in 15 files, including `reduce.py`, which ruling §7 records as identical to base, so it is too heavy for S1.
- **(d), own lane, SHOULD-FIX (structural root cause, R2).** Energy from `summary_metrics.json` has **no gated accessor**. So a correct claim read and an ungated read are the same syntax (`raw_summary()`), and whether a read is safe depends on the order of calls elsewhere. That is why the sweep needs dominance analysis (checking that a gate call precedes the read on every path) and keeps sprouting rules.
  - Fix: add a gated `BundleReader.summary()` (it calls `metadata()` first) and migrate the claim consumers to it. `raw_summary` is then left to non-claim callers, and the sweep's rule for it shrinks to a closed caller inventory.
  - The strongest guarantee is at the level of evidence rather than code: claim artifacts already record `battery_float_members` as {label: status} (`aggregate.py:124`, `inputs.py:3419`, `whole_window.py:683`). A paper-number verifier could assert that every contributing member is listed with an admitted status, and could re-authenticate each member once the verdict digest is also recorded.

## Q4. B-4 (the `envelope_gate.py` rows)
**Verdict: make the production change. It is behaviour-identical (R1), so this is the truthful fix. Do it before S1's allowlist closes if the magistrate will widen WRITE_SCOPE by those two lines; otherwise use a truthful interim label and ship it first in its own lane.**
- Neither `historical` nor `non_claim` (ii) is true. AP-5 makes the envelope verdict license scored campaigns, and a campaign that uses it is queued. The energy it carries is in fact gated in the callee `_manifest_record` (R1; round-2 Y11), so this is a mislabel, not a leak.
- Preferred: S1 fix round 3 gets WRITE_SCOPE += `joulewise/envelope_gate.py`, **exactly** `reader.metadata()` before `:133` and `:654`. Both rows then leave the allowlist, and the reason-code fix stays in BFGS-ENVELOPE-REASON-01.
- Fallback: hold the rows under an **honest** label: "gated in callee `_manifest_record`, pinned by R60-3; exception by cold gate until BFGS-ENVELOPE-REASON-01". That lane lands **before any AP-5 scored campaign arms**. This does not block S1's merge.

## Q5. S1 fix round 3, in order
1. Implement erratum §8 as ruled (amendments 51 and 57 to 60). Do not reopen it.
2. **B-1:** sweep every scope (module body `<module>`, class bodies, defs nested anywhere, lambdas never gated). Report the row delta. P4 predicts 0 for literal reads; a nonzero delta is a return, not an explanation.
3. **B-5:** make both callers checks count **references** as well as calls.
4. **51 (h):** add the deliberate-class grammar of Q3, naming B-2, B-3 and W1 to W6.
5. **B-4:** the two-line edit if the scope is widened; otherwise the honest interim label.
6. NITs that cost nothing: B-6 (widen the regex, and report whether the 48-member count moves), B-7 (wording), B-8 (the "negation under cold gate" sentence). B-9 applies only if the B-4 fallback is used.
7. V1/V2 and the builder's forward check, as the brief already states them.

**Does not block S1's merge:** B-2, B-3 and W1 to W6 (limitation), the runtime binding of P2, the gated-`summary()` and claim-verifier lane, the envelope reason code, and BFGS-RAWCAPTURE-01 (unless step 5 of §8 returns an ungated `energy` member, which is a tree read and so does block).

## Q6. Stop rule
**Verdict: the lane's review ends at the first round that finds (1) no ungated energy read at the tree, (2) no allowlist row held under a false class condition, and (3) no latent form outside the Q3 deliberate-class grammar.**
- Condition (3) makes the accident/evasion split mechanical: a refuter checks its probe source against the four clauses. A form inside the grammar is added to 51 (h) by name and is **not** a finding. It never triggers another round.
- Conditions (1) and (2) keep the science fence: anything that bears on whether a number is true stays mandatory (Ed, #421).
- Rule 11 still applies. If a round-3 review of B-1/B-5 fails with the same signature, the next spend is the gated-`summary()` redesign, not round four.

## Tiered findings of this seat
- SHOULD-FIX (own lane): no gated `summary()` accessor exists (R2). This is the root cause of the sweep's complexity.
- SHOULD-FIX (S1): B-1 and B-5 (accident class). B-4 (truthfulness), by the two-line edit.
- NIT: the charge names a `summary()` accessor that does not exist (R2).
- Limitation, not a finding: B-2, B-3 and W1 to W6 (P3). No BLOCKER. I found no ungated energy read that reaches a claim artifact at `315364b2`, on the paths I read.

## Recommendation
1. Choose (b′): close B-1 and B-5 (accident class; GREEN on the tree), fix B-4 truthfully with the behaviour-identical two-line `reader.metadata()` edit, and write the deliberate-evasion grammar into 51 (h). Do not run round three of shape (a).
2. Stop rule: no ungated read at the tree, no false class, and no latent form outside the grammar. Grammar forms are named limitations and never findings.
3. Open a separate lane for the structural fixes: a gated `BundleReader.summary()` with the consumers migrated to it, the optional ~6-line runtime path and slot binding, and a verifier over `battery_float_members` in claim artifacts. None of these blocks S1.
