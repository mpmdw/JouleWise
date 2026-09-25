# Paired cold contract refuter (Opus 5.5), A291-FIX2-01 addendum 2, Final texts v3 (delta scope)

**Verdict: 0 BLOCKER, 1 MATERIAL, 4 NIT.** Both B1 cures hold under executed probes. R4d is RED at 20cd29de and GREEN under the specified cure. A cure that only catches `ZeroDivisionError` stays RED. No legal roster newly refuses, and every similarity number reproduces exactly. The MATERIAL finding: several texts rely on a `detail` attribute that `PackingRefusal` does not have, so each seat has to decide what "detail" means. One of those choices silently disables property 7(f).

Evidence came from `git archive 20cd29de` into `/tmp/278ebc9e/v3ref/code` under Python 3.14.7. `v3probe.py` is a literal model of texts 1, 2, 2a and 3, reusing the production `_structure` and `_replay_roster`. It can switch three parts on and off: the `_structure` clause, the `_lever` emptiness rule, and the `ArithmeticError` handler.

## Findings

| # | Sev | Text | Finding and evidence | Exact replacement |
|---|---|---|---|---|
| F1 | **MATERIAL** | 6 (R4b, R4d, R4d-facts); 7(f); interacts with 2 | "detail" is used as though it were a field, but at 20cd29de `PackingRefusal.__init__` sets only `self.code` and a message `f"{code}: {detail}"` (`scored_packer.py:17-20`). My first probe crashed with `AttributeError: 'PackingRefusal' object has no attribute 'detail'`. ex-10 B4 shows K only the signature `PackingRefusal(code, detail)`, so K may assume `exc.detail` exists. If K uses `exc.detail` and P does not add the attribute, K's fuzz crashes on integration. If either seat instead tests `str(exc).startswith("internal:")`, the result is always False because the message starts with `inv_`. Property 7(f) and R4d's "not `internal:`" check then pass however the code behaves: the silent `inv_52 internal:*` backstop that B3(i) says must never fire could fire unseen. | Append to text 2: `Wherever these texts say a refusal's "detail", it means str(exc).partition(": ")[2]; PackingRefusal's message format f"{code}: {detail}" is unchanged, and no test reads an attribute named detail.` This works at 20cd29de and on the integrated head, and needs no change to the packer. |
| F2 | NIT | 6 (R4d) | (a) The call site is misnumbered. Under ex-10 B5, step 2 is the digest and `inv_02`/INV-38 check, and `_structure` is step 3; R2b already says "step 3". (b) R4d does not pin the new `_structure` clause. A `_lever`-only cure passes R4d as written, returning `inv_10` with detail `empty parent large:decode:1:999` (probe row "`_lever` rule only"). The refusal code is the same, so no admissibility changes, but the `_structure` clause has no test witnessing it. (c) The copied block's model and level are right only implicitly: `_roles` returns (8B, 1.7B) and `LEVELS[0]=1`, which the probe confirmed (`blocks0 large 1`). | In R4d replace `raises PackingRefusal with code inv_10 and a detail that does not start with internal:` with `raises PackingRefusal with code inv_10 and detail == "empty block"`. Replace `Call site: _seal step 2 (_structure)` with `Call site: _seal step 3 (_structure)`. Add `model=<8B id>, level=1,` to the update list. Add to the counterfactual: `under the _lever rule without the _structure clause: inv_10, detail "empty parent …"`. |
| F3 | NIT | 3 | The heading "Precondition rows in `_structure`, at its end, in this order: INV-10 as `:135` PLUS … after `:136`" contradicts the line anchors. `:135-137` sit inside the per-block loop, not at the end. Only INV-11 and INV-12 are appended at the end. | `Precondition rows in _structure: INV-10 stays at :135 (…) PLUS one new statement … before the :137 line; INV-03, INV-17, INV-52 as today; then, appended at the end of _structure, INV-11 (a)/(b) … then INV-12 …` |
| F4 | NIT | 8 | The screen only looks at the named functions, so moving the logic into helpers evades it. EV-d rewrites checker `_derived` as `return _lev(g, _pos(g, r))` with the full copy inside `_pos` and `_lev`. Against a v3-shaped packer `_derived` it scores **0/2 = 0.000**, and the helpers are never screened. Against the 20cd29de packer `_derived` the same wrapper is a false FAIL at 1/2 = 0.500, because the `def N ( N , N ) :` line matches. Cheaper edits do not evade it: commutative swaps (EV-a) score 0.818, added temporaries (EV-b) 0.765, and a partial split (EV-c) 0.800 for the wrapper with 0.810 unscreened in the helper. Text 8 already says "a similarity screen, not proof", and K's blindness to the packer source is the primary control, so this is not MATERIAL. | Append to text 8's similarity paragraph: `Every function K adds or changes in tests/scored_roster_checker.py and tests/test_scored_roster_checker.py that has ≥ 5 normalised lines is screened pairwise against the same packer targets as checker _derived, and against _structure as its control; the same PASS rule applies to each.` |
| F5 | NIT | 7, interacting with R4d | R4d on the integrated head calls K's rewritten `check_roster` on the empty-parent roster and expects INV-10. Today the checker survives that roster only because its `:757` catch includes `ZeroDivisionError`, and it reports `INV-52 cross-record structure: ZeroDivisionError`. So the checker's copy has the same division by zero. Nothing requires K's item-centric rewrite to keep returning on that roster. A crash would surface at integration rather than silently, hence NIT. | Append to text 7: `K's test module builds R4d's roster (text 6) and asserts check_roster returns, without raising, a list containing INV-10.` |

**D1: no legal roster newly refuses and no expected code changes.**
- **Legal rosters:**
  - The final short slice passes: `fixture(n=11, block_size=2)` root under the full v3 model returns (the `(7,3)` and `(13,4)` fixtures refuse `spread_minima` at `pack`, so they are not legal).
  - One-item parents pass: `n=5, bs=1`.
  - An executed-mode parent with every item terminal passes: the R4d base through the v3 `executed` path returns.
  - The stress generator produced 5,472 sealed rosters over 60 cases, and the smallest block anywhere had 1 item. Only a split creates new blocks, and it always creates `items=[item]`.
- **Existing expectations:**
  - R4b stays `inv_11` under every configuration I ran.
  - R1, R2, R2b and R3 never build an empty block.
  - `test_typed_static_invariant_refusals` has no case that empties `items`.
  - None of the ten fuzz operators empties `items`, so census (d) and property (e) are unchanged.
  - The new clause runs after the `inv_52` "block items" check, so `len()` is only reached on a list and no `inv_52` expectation moves.

**D2: R4d discriminates correctly.**
- At 20cd29de, `verify_executed_roster` raises a raw `ZeroDivisionError`.
- The catch-only cure gives `inv_52 internal:ZeroDivisionError`, which is RED.
- R4d-facts under a cure with no emptiness rule returns from `_lever`; in production that leads to `stale_derived`, which is RED.
- It is driven through the named production entry, `verify_executed_roster`, and its guard holds (`check_roster == []`, `lever["1"] is None`).

## Changed texts accepted
- **Text 1** (POP-1 edit plus the emptiness paragraph): accepted. The implication "gate count ≥ 1 ⇒ non-empty positions" holds in both modes once every parent is non-empty.
- **Text 2** (boundary): accepted, with the F1 addition.
- **Text 2a** (emptiness before relation, `inv_10` "empty parent …"): accepted. In executed mode the relation check is redundant but harmless.
- **Text 3** (`_structure` clause after `:136`): accepted, with the F3 wording fix.
- **Text 6** (R4d, R4d-facts): accepted, with the F1 and F2 fixes.
- **Text 8** (canonical screen, P1/P2 controls, 0.30 threshold, 0.28 control bound): accepted. The numbers reproduce exactly and the worst control, 0.242424, sits 0.038 below the bound. F4 is advisory.

## Probes (commands and output tails)

```
$ git archive 20cd29de | tar -x -C /tmp/278ebc9e/v3ref/code; cd …/code; python3 v3probe.py
R4d guard checker [] lever1 None blocks0 large 1
R4d-base executed text model RETURN
R4d @20cd29de verify_executed_roster ZeroDivisionError:division by zero checker ['INV-10', 'INV-36', 'INV-50', 'INV-52']
CFG full v3                      R4d inv_10:detail=empty block | R4d-facts inv_10:detail=empty parent p | R4b inv_11:detail=gate parent without full live positions p
CFG catch-only (no emptiness)    R4d inv_52:detail=internal:ZeroDivisionError | R4d-facts RETURN | R4b inv_11:…
CFG _lever rule only             R4d inv_10:detail=empty parent large:decode:1:999 | R4d-facts inv_10:… | R4b inv_11:…
CFG _structure clause only       R4d inv_10:detail=empty block | R4d-facts RETURN | R4b inv_11:…
short-slice roots checked 2 refused 0 min items 1
(first run, before switching to str(exc): AttributeError: 'PackingRefusal' object has no attribute 'detail')

$ python3 screen.py        # pinned via git show 20cd29de, ast.get_source_segment, public ast.unparse only
P1 copy 29/33=0.878788
P2 unparse-equal True score 29/33=0.878788
copy vs executed_status 23/33=0.696970 control _structure 8/33=0.242424
check_executed vs executed_status 27/45=0.600000 control 4/45=0.088889
refresh_derived vs _derived 18/37=0.486486 control 8/37=0.216216
EV-a commutative swap 27/33=0.818182
EV-b temporaries 26/34=0.764706
EV-c split: wrapper _derived 12/15=0.800000 | helper _cell (unscreened) 17/21=0.809524
EV-d wrapper _derived 1/2=0.500000
EV-d wrapper vs v3-shaped packer _derived 0/2=0.000000

$ python3 corpus.py        # spies production _seal across stress run_case(0..59)
rosters sealed 5472 min items over all blocks 1
```

In the "R4d-facts RETURN" rows (catch-only and `_structure`-only), the call went directly to the text-model `_lever`. Through `requeue_overrun` those configurations end at `stale_derived`, which is still RED against `inv_10`.

**Scope:** I wrote nothing outside `/tmp/278ebc9e/v3ref/`. I did not read RUN_STATE, TASK_QUEUE, the council logs, memory, or any other trace directory, and I launched no subagents or background jobs.
