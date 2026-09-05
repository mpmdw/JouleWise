# Opus counter-review — PAPER-CUSTODY-SEAM-01 (gate ledger row 6, contract lens)

Seat: Opus 5, read-only counter-review. Tree: `/Users/edr/code/JouleWise-wt-paper-custody`,
branch `feat/2026-09-04-paper-custody-seam`, HEAD `002353a9`, working tree clean at audit
start. Lens: the six questions the two Sol refuters did not test (caller authority through
any public entry, what the git anchor actually anchors, per-family returned evidence, the
AST lint's real reach, D-173/contract vs code, and the D-165 producer-emission closure).

## Verdict

**LANDABLE** for the ruled scope of this mission (ruling 15 items 1–6 plus the contract
doc, built against fixtures only), subject to the two gate conditions below.

The central claim holds and I verified it by execution, not by reading: no caller-authored
value becomes authority through `open_paper_input`. `ref.role` is regex-gated and must key
a git-anchored map (`joulewise/paper_custody.py:1068-1073`, `:596-680`); `ref.runs_root`
only relocates the search, and every byte read under it is pinned by a digest that came
from the map, checked before the parser sees it
(`joulewise/authentication_io.py:457-486`); there is no path, digest, receipt, mapping,
bytes, or supply-map parameter on any public function; the supply-map path is a module
constant (`paper_custody.py:32`) with no caller channel; and the production lane is
refused unconditionally (`paper_custody.py:1214-1219`), so no fixture consistency can ever
become paper authority. The four named test modules pass: 100 tests, OK, 91 s
(`python3 -m unittest tests.test_paper_custody tests.test_authentication_io
tests.test_analysis_inputs tests.test_d165_dominance_closeout`).

**Gate conditions** — both must close before the paper-supply cold gate consumes these
traces, and before any supplier re-lands on the seam:

- **G1 (C-01).** Ruling 16.3's "closed by construction" is not delivered for the D-165
  producer; the installed cross-check tests two constants against each other, never the
  producer. Counter-proof executed below.
- **G2 (C-05).** Landing report `01` and refuter trace `02-refuter-execution` state a
  refusal code for the reseal arm that the code does not emit. Ten table cells are wrong
  in a trace the packet will carry. Correct them before the packet is assembled.

Everything else below is should-fix or a note.

---

## C-01 — should-fix (blocker-adjacent). The D-165 producer CAN emit a refusal code outside the closed enumeration, and the funnel then launders it into a wrong cause

`joulewise/dominance_closeout.py:1007` — `_build_independent_record` writes
`"refusal_reason": str(exc)`, the raw `ValueError` text from `dominance_ratio`, with no
pass through `_closed_refusal_code` (`:354-363`). That funnel is called at exactly one
record-construction site in the module, `:1410` (the *common* record), and once over
already-closed source errors at `:1921`. The independent-ratio record — the one that
carries the headline dominance refusal — bypasses it.

Today every path lands inside the enumeration, but only by coincidence of exception-message
text. Executed evidence, this session:

```
=== _build_independent_record per-record refusal_reason ===
zero_denominator      status=refused  reason='dominance_ratio_zero_denominator'                  in_enum=True
negative_denominator  status=refused  reason='dominance_ratio_nonfinite_or_negative_denominator' in_enum=True
nan_denominator       status=refused  reason='dominance_ratio_nonfinite_or_negative_denominator' in_enum=True
negative_numerator    status=refused  reason='dominance_ratio_nonfinite_or_negative_numerator'   in_enum=True
nan_numerator         status=refused  reason='dominance_ratio_nonfinite_or_negative_numerator'   in_enum=True
inf_numerator         status=refused  reason='dominance_ratio_nonfinite_or_negative_numerator'   in_enum=True
```

**Counterfactual** (executed): reword one `dominance_ratio` `ValueError` message — the
ordinary maintenance act the enumeration exists to survive — so that both the builder and
the validator see the same reworded function:

```
per-record reason: dominance_ratio_zero_denominator_v2
in closed enumeration: False
has OR-01 sentence:   False
validator errors:     []          <- validate_d165_closeout accepts it
contrast: the funnelled GLOBAL field for the same record:
  'closeout_input_malformed: source.census_or_block_membership'
```

Two defects in one probe. First, an unenumerated code reaches the close-out artifact's
per-record `refusal_reason` and `_validate_closeout_common_record`
(`:1466-1469`) accepts it, because the validator only requires a nonempty string, never
membership in `D165_CLOSEOUT_REFUSAL_CODES`. Second — the sharper half — the global field
*is* funnelled, so `_closed_refusal_code`'s `fallback=CLOSEOUT_INPUT_MALFORMED_SOURCE`
silently replaces an unknown code with a *specific and wrong* professor-facing cause: a
zero-denominator refusal is reported as a malformed source census. A fallback that names a
concrete cause is worse than one that names none.

`tests/test_d165_dominance_closeout.py:2074-2098`
(`test_real_module_reason_enum_and_or01_registry_map_are_bidirectional`) cannot catch
either: it asserts `set(D165_OR01_REASON_SENTENCES) == D165_CLOSEOUT_REFUSAL_CODES` and
mutation-probes by patching those two constants. Both constants stay consistent while the
producer walks out of them. Ruling 16.3 asked for closure *by construction*; what landed is
closure between two literals.

**Fix shape** (small): route `:1007` through `_closed_refusal_code`; give
`_closed_refusal_code` a fallback that does not assert a cause it did not observe; add one
assertion to `_validate_independent_record` / `_validate_closeout_common_record` requiring
`refusal_reason in D165_CLOSEOUT_REFUSAL_CODES`; and make the cross-check test drive the
*producer* over each refusal path rather than the constants.

## C-02 — should-fix. Ruling 16.1's "every supplier joins the AST lint list" is not installed; two supplier modules carry 37 unlinted direct-read sites

Addendum 5 item 1 is explicit: "the new module **and every supplier** join
`tests/test_authentication_io.py`'s enforced list." Only the seam joined
(`tests/test_authentication_io.py:30`). Executed census of the modules named in the seam's
own validator census (`paper_custody.py:367-442`):

```
joulewise/analysis_engine/inputs.py         MISSING   12 direct readable-IO sites
joulewise/analysis_manifest_v3.py           MISSING   25 direct readable-IO sites
joulewise/analysis_engine/artifact.py       MISSING    0
joulewise/dominance_closeout.py             MISSING    0
joulewise/floor_extraction.py               MISSING    0
joulewise/whole_window.py                   ON
joulewise/campaign_provenance.py            ON
joulewise/paper_custody.py                  ON
```

Examples from the two live ones: `analysis_engine/inputs.py:1436`, `:1514`, `:3925`,
`:3927`; `analysis_manifest_v3.py:3562`, `:3184-3185`, `:3695`. One of them is the floor
loader this very landing rewrote: `load_floor_artifact` still reads through
`Path(path).read_bytes()` (`joulewise/analysis_engine/inputs.py:949`) — the ruling closed
its *return-type* downgrade but left its read channel outside the guard, while the sibling
lane `floor_extraction._read_summary` was converted to `read_authentication_input` in the
same commit. The asymmetry is the tell.

This is the ruled-not-installed pattern: the clause was decided, the code shipped without
it, and nothing in the tree fails. If the intent is to defer these to the per-supplier
re-landings, say so in the contract doc and name the gate — an undocumented deferral is
indistinguishable from an omission at the next audit.

**Positive control, so the lint's reach is not overstated.** I mutation-proved that the
guard does refuse a direct read *in the seam*: injecting
`return Path(repository, relative).read_bytes()` into `_git_blob` yields
`('_git_blob:556:read_bytes',)`, where the unmutated module yields `()`. The guard works;
its *list* is the gap.

## C-03 — should-fix. The verified result and its evidence are forgeable by exactly the mechanism the seam uses, while the contract asserts they are not

`docs/contracts/paper_supply_custody.md` states: "only the private seam factory can create
a populated instance." Executed:

```
B1 public CustodyEvidence(issuance_authorized=True): True
B2 forged VerifiedD165Closeout via object.__new__ + object.__setattr__:
     issuance_authorized=True, payload=_FrozenObject((('headline','supplier-authored'),))
B3 paper_custody._construct_verified importable and returns the same: True
```

`CustodyEvidence` (`paper_custody.py:131-139`) is a public, exported dataclass with an
ordinary generated `__init__`; nothing stops a supplier from constructing one with
`issuance_authorized=True`. The `Verified*` classes block `__init__`
(`:151-192`) but not `object.__new__` + `object.__setattr__`, which is precisely what
`_construct_verified` (`:1022-1030`) does, and that function is importable. The existing
test (`tests/test_paper_custody.py:395-407`) only probes `output_type()`.

Under D-161 I am not calling this an adversary hole — an operator who writes
`object.__new__` is not making a mistake. But the contract sentence is false as written,
and the *cheap* half of the exposure is not exotic: `CustodyEvidence(...)` is the
sort of thing a supplier author writes without thinking. Give `CustodyEvidence` the same
`__init__ = _refuse_verified_construction` treatment the `Verified*` types have, and
soften the contract sentence to what Python can deliver.

## C-04 — should-fix. Verified results do not carry the anchor that authorized them, and the anchor accepts an unpushed branch HEAD

Item (2) of this seat's brief, answered by execution:

```
anchor repository: /Users/edr/code/JouleWise-wt-paper-custody   <- the checkout it ran from
anchor head:       002353a9d61169fdef398ac8557dc6430c2f4b81
origin/main contains HEAD?  False                                <- accepted anyway
CustodyEvidence fields: family, inputs, receipt_sha256,
                        validator_source_sha256, mode, issuance_authorized
   anchor commit carried?      False
   supply-map digest carried?  False
```

What is anchored (`joulewise/identity_pins.py:819-842` →
`scripts/mint_floor_artifact_generalized.py:1331-1354`): the 40-hex `HEAD` of the checkout
the module was *imported from* — `REPO_ROOT = Path(__file__).resolve().parents[1]` — plus
`git status --porcelain --untracked-files=all` being empty. `origin/main` containment is
recorded and explicitly not a gate, which the contract doc does disclose.

So: the "fixed repository" is whichever clone or worktree the paper build happens to run
in, and a stale or unmerged commit satisfies the anchor completely. Right now, in this
worktree, it *would*: HEAD is on a feature branch that `origin/main` does not contain. That
is defensible as a build-time property. What is not defensible is that the verified object
records none of it. D-173 promises "frozen verified objects carrying the digests actually
verified" — they carry the five-to-six input digests and the receipt digest, but not the
commit and not the supply-map blob digest, so a paper fill produced from this branch is
indistinguishable, downstream, from one produced from canonical main. The supply map is
ingested into the session under identity `git:<head>:configs/...`
(`paper_custody.py:605-610`) and then dropped from the census, because `_record_tuple`
(`:492-516`) walks only `bindings`, which never includes it.

Add `anchor_head` and `supply_map_sha256` to `CustodyEvidence`. It is a two-field change
and it is the difference between a custody chain and a digest list.

## C-05 — should-fix (gate condition G2). Two mission traces state a refusal code the code does not emit

`docs/process_traces/2026-09-04-paper-custody/01-seat-landing-report.md:26-30` — all five
table rows — and `02-refuter-execution.md:72` both assert that the full-caller-reseal arm
yields `paper_custody_anchor_mismatch`. The installed test asserts
`paper_custody_digest_mismatch` (`tests/test_paper_custody.py:335-338`), and that is what
the code does: a reseal changes bytes, so `read_nofollow_pinned` fails against the
map-pinned digest long before any inventory comparison runs.

This matters beyond bookkeeping. The refuter reported having *proved* the reseal arm; the
code it names is not the code that ran, which means the reseal arm's semantics were not
actually examined. And the distinction is the interesting one:
`digest_mismatch` says "bytes disagree with the pin," `anchor_mismatch` says "the inventory
disagrees with the git-anchored map." The reseal arm is meant to demonstrate the second.
It demonstrates the first, which the raw-flip arm already demonstrates — so the census
currently has two arms testing one gate and no arm exercising the inventory-vs-map gate on
a *coherently* resealed tree.

Related dead code: `paper_custody.py:1117-1126` is unreachable. By the time it runs, the
bytes have passed `read_nofollow_pinned` against `binding.expected_sha256` (`:697-703`) and
`_validate_inventory` has already required `row["sha256"] == binding.expected_sha256`
(`:812-821`), so `row["sha256"] != _sha256(raw)` cannot hold.

## C-06 — should-fix. The "single normative home" does not contain the closed refusal enumeration it governs

`docs/contracts/paper_supply_custody.md` §"Closed refusals" says every failure carries "a
code from the closed `paper_custody_*` set" and never lists the set. Three sources now
disagree:

- code (`paper_custody.py:41-62`): **18** codes;
- packet 14 §10: **15** codes;
- code adds three the packet never enumerated — `paper_custody_supply_map_invalid`,
  `paper_custody_role_unregistered`, `paper_custody_blocked_pending_receipt`. The last is
  the *terminal* code for a whole family, and packet 14 §7 / Q-C-4 both say whole-window
  returns `paper_custody_receipt_unissued`.

And two code-declared codes are unreachable: `paper_custody_derivation_mismatch` and
`paper_custody_identity_not_v5` appear only inside the frozenset — no raise site anywhere
in the tree. `identity_not_v5` is addendum 5 item 4's `_v5` gate, which has not been built
(reasonably — no supplier is on the seam yet), but declaring the code now makes the "closed
enumeration" look complete when it is not.

Note the asymmetry with C-01: the D-165 enumeration at least gets a bidirectionality test.
The seam's own refusal namespace gets `test_refusal_namespace_is_closed_and_nonrendering`
(`tests/test_paper_custody.py:497-510`), which checks the prefix and one membership — not
that each declared code is reachable, nor that each raise site uses a declared code (the
constructor at `:207-208` silently rewrites an unknown code to `request_invalid`, so a typo
at a raise site degrades to a generic refusal rather than failing).

Put the enumeration in the contract doc, one row per code with its meaning and the
condition that raises it, and add a reachability test.

## Notes (no action required this landing, but they should be recorded)

**N-1. `authority: "git_blob"` is inert, and the governed-file half of ruling 15.2 is
unexercised.** `authority` is validated (`paper_custody.py:472-482`, `:797`, `:817`) and
constrained so that `git_blob` implies `base: repository`, but it never dispatches
anything: a `repository`-based binding is read from the *working tree* via
`read_nofollow_pinned(repository, ...)`, not from a git blob. The clean-tree anchor makes
those byte-identical in practice, so this is correct-by-consequence rather than
correct-by-construction. `git_blob` appears **0** times in
`configs/paper_supply/supply_map.json` (all five fixture roles are
`generated` / `runs_root`), so the branch has never run. Ruling 15.2's "governed files are
authorized through clean Git blobs" is, today, a claim about a path with no traffic.

**N-2. The real anchor is never exercised by any test.** Every fixture patches
`custody._mint_git_anchor` to a synthetic throwaway repo
(`tests/test_paper_custody.py:210-214`); the only unpatched-path test injects an
`IdentityPinProjectionError` (`:446-455`). So the root of the entire trust chain — clean
tree, real `git show`, real `REPO_ROOT` — has no coverage at the seam. One test that calls
`identity_pins._mint_git_anchor()` for real and asserts `paper_custody_anchor_unavailable`
on a deliberately dirtied tree would close it. Operationally this also means any untracked
file in the checkout — a mission trace file, an unignored `runs/` directory — refuses every
paper read; that is the intended fail-closed behaviour, but it deserves a line in the
contract's operational notes so it is not diagnosed as a bug at 2 a.m. Executed, after
writing this trace file and nothing else:

```
$ git status --porcelain -uall
?? docs/process_traces/2026-09-04-paper-custody/08-opus-counter-review.md
$ python3 -c "from joulewise import identity_pins as ip; ip._mint_git_anchor()"
REFUSED: generalized mint Git anchor refused identity projection:
         v2 issuance requires a clean Git working tree
         (dirty: ?? docs/process_traces/2026-09-04-paper-custody/08-opus-counter-review.md)
```

One untracked markdown file in `docs/` disables every paper-supplier read in the tree, and
the seam's own test suite does not notice — `tests.test_paper_custody` still reports 10
tests OK with the tree in this state, because it mocks the anchor away. That pair is the
whole of N-2 in two lines.

**N-3. The AST lint is blind to subprocess reads, and the seam's own supply-map read is
one.** `direct_read_violations` recognises `open`, `read_bytes`, `read_text`, `os.open`,
`io/codecs.open`, `os.fdopen` (`joulewise/authentication_io.py:706-753`). Executed: a
function reading through `subprocess.run(["git","show",...])` yields `()`. That is exactly
`_git_blob` (`paper_custody.py:542-556`). The bytes are then passed to `session.ingest`, so
the seam is not evading its own session — but "the authentication AST guard includes
`joulewise/paper_custody.py`" (contract, §Lower-boundary closures) reads stronger than what
the guard can see. Worth one sentence in the contract.

**N-4. The enforcement lists are hand-maintained literals with no closure test.**
`AUTHENTICATION_SURFACE` (`tests/test_authentication_io.py:29-42`) and
`marked_functions={"open_paper_input"}` (`:429-435`) are tuples a future author must
remember to extend. C-02 is what happens when someone doesn't. Whatever mechanism replaces
them — a module-level marker decorator, a manifest, an import-graph derivation — should
land with the first supplier, not after the third omission.

**N-5. `parse_campaign_log_bytes(raw: bytes)` survives the campaign-log closure.**
`load_campaign_log_rows`'s `raw_bytes=` channel is genuinely gone
(`joulewise/campaign_provenance.py:453`, no remaining callers pass bytes — verified
repo-wide), but the public byte-taking parser it delegated to is still module-public
(`:410-412`) and would be flagged by the signature guard if the guard were pointed at it
(`parse_campaign_log_bytes:raw:annotation:bytes`). Not a live bypass — no supplier is on
the seam — but it is the next place this class reappears.

**N-6. Production is blanket-refused, not registry-gated.** `paper_custody.py:1214-1219`
raises `paper_custody_receipt_unissued` for *any* `mode == "production"`, unconditionally
and for all five families. The contract (§8) says production "still refuses until that
family's governed producer is registered," which implies a condition that does not exist in
code — a future producer mission must delete a hard-coded raise. This fails closed and is
right for now; the contract sentence should describe the mechanism that is actually there.

## What I checked and found sound

- **Caller-authority closure** (brief item 1): no public channel for a path, digest,
  receipt, mapping, bytes object, or alternate supply map. `open_paper_input({})`,
  `(b"{}")`, `(object())`, and `object.__new__(Verified…)` all refuse with
  `paper_custody_request_invalid` (`tests/test_paper_custody.py:473-484`, re-run here).
  The supply map's own load is anchored, session-ingested, strict-schema'd, and
  duplicate-checked (`paper_custody.py:596-680`), and a dirty tree does refuse — through
  the mint's `git status --porcelain --untracked-files=all` gate, translated to
  `paper_custody_anchor_unavailable`.
- **The no-follow read is genuinely hardened**: dirfd component walk with `O_NOFOLLOW` at
  every level plus an `S_ISREG` check (`joulewise/authentication_io.py:281-320`), so
  symlink and non-regular-file substitution are closed below the seam. Digest is checked
  *before* strict parsing (`:472-478`), which is the right order and is tested
  (`tests/test_authentication_io.py:348-366`).
- **Returned objects reach no raw bytes** (brief item 3): the payload is
  `_FrozenObject`/`_FrozenArray` of strict JSON scalars only (`paper_custody.py:348-357`),
  and `CustodyEvidence.inputs` carries `VerifiedDigest` records — role, relative path,
  sha256, read_count, strict_parse_succeeded — with `read_count == 2` asserted for every
  record of every family, which is the reopen actually happening.
- **The validator-source digest census is mutation-proved per member**
  (`tests/test_paper_custody.py:410-433`): each of the 3 common + per-family owning
  validators, source-mutated one at a time, moves `_validator_source_sha256`. This is the
  strongest single mechanism in the landing.
- **Both named lower bypasses are closed with no stale callers** (verified repo-wide):
  `load_floor_artifact` returns `AuthenticatedFloorArtifact` and all four call sites take
  the capability; `load_campaign_log_rows(log_path)` has one parameter and every caller in
  `joulewise/`, `scripts/`, and `tests/` passes a path.
- **The whole-window block is placed before any object construction**
  (`paper_custody.py:1208-1213`) and returns records without a payload, so no verdict row
  can be rendered — ruling 15.3 delivered, modulo the code-name divergence in C-06.

## Executed evidence

All commands run in `/Users/edr/code/JouleWise-wt-paper-custody` at HEAD `002353a9`,
`python3` = 3.14, working tree clean.

1. `python3 -m unittest tests.test_paper_custody tests.test_authentication_io
   tests.test_analysis_inputs tests.test_d165_dominance_closeout` → **Ran 100 tests in
   91.006s — OK**.
2. D-165 producer probe over six real refusal inputs, then the reword counterfactual
   (C-01) — outputs quoted inline above.
3. `direct_read_violations` on the unmutated and mutated seam, on a subprocess-read
   function, and across the eight supplier modules (C-02, N-3) — outputs quoted above.
4. `CustodyEvidence` / `Verified*` / `_construct_verified` construction probe (C-03).
5. `identity_pins._mint_git_anchor()` and the mint's `_actual_v2_git_state()` against the
   live checkout; `git branch -r --contains HEAD` (C-04).
6. `paper_supplier_signature_violations` applied to the six supplier validator entry points
   (N-4, N-5).
7. After writing this trace: `git status --porcelain -uall` plus a live
   `_mint_git_anchor()` call (refuses), and `python3 -m unittest tests.test_paper_custody`
   (10 tests, OK, unaffected) — the N-2 pair.

No file in this worktree was modified except this trace. No commit, no push.
