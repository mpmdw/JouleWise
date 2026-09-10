# 89 — Seat S1 contract-lens refuter (Opus), `--derivation-only` writer mode

Scope: `git diff 1e43d1cc 12f1d1cf` in `/Users/edr/code/JouleWise-wt-s1-writer-derivation`
(HEAD `12f1d1cf`, fix round 1 included). STRICTLY READ-ONLY: no edits, no git
state change, no live capture, no mutation cuts, and the full
`tests.test_calibration_exits` module was NOT executed (another refuter is
cutting in this tree).

**VERDICT: MERGEABLE AFTER FIXES.** No blockers. Every ruled clause that is
S1's to implement is implemented, and the two clauses the seat itself flagged
(the `--allow-live` ordering argument, the skipped TRUE branch) hold up under a
contract reading. The fixes are one false comment inside S1's own file, one
witness execution the registry contract requires before the abort-class row can
be called complete, and three documentation clauses that belong to seat S6 /
the integration tree, not to this diff.

## Executed evidence (this session, this worktree, read-only)

1. `python3 scripts/validate_powermetrics_fiducial.py --help` → `--derivation-only`
   present; every flag the S5 chain passes (`--allow-live --derivation-only
   --ledger --head-pin --session-id --slot --attempt-id --output-root
   --power-policy`) is accepted; no positional args. Chain source read at
   `/Users/edr/code/JouleWise-wt-s5-chain-watch/scripts/night_chains/calibration_derivation_only.zsh:189-199`.
2. `python3 -c "... _derivation_only_screen_basis()"` →
   `level: '0.032898493715362'`;
   basis keys exactly `['acceptance_id','artifact_sha256','epoch','preflight_level_screen_s']`;
   `acceptance_id d079_calibration_acceptance_v2_n17_r6`; epoch the six fields
   with `os_build 25F84`. Matches ruling 46 A1's four-key shape and V2's quoted
   screen `0.032898493715362` character for character.
3. `python3 -m unittest tests.test_docs_freshness` → `Ran 31 tests ... OK` (rc 0):
   the regenerated registry block in `docs/contracts/calibration_ledger_append.md`
   is byte-fresh against `REFUSAL_INVENTORY`.
4. Read of `_derive_preflight_systematic_screen_s`
   (`scripts/validate_powermetrics_fiducial.py:364-436`): the returned
   comparator is `decimal_derivation.ratified_operatives.preflight_level_screen_s`,
   i.e. the LEVEL screen, not the A-4 sum `0.04262208300415633`. The
   `preflight_level_screen_s` key name in `screen_basis` is therefore correct.
5. Statement order read in `main`: `--allow-live` gate `:1770` → derivation
   branch `:1830-1882` → `_CaptureLedgerLifecycle(...)` `:1920-1931`. The
   ordinary-path epoch refusal (`FROZEN_PROTOCOL_INVALID`, `:1884-1890`)
   therefore fires strictly before the new lifecycle guard `:1378-1395`,
   which is the load-bearing premise of the third code's class (see §1).

Not executed by me, and so not corroborated here: the parameterized public-CLI
witness case for the new abort-class code (see SF-2), and the end-to-end admit
path (execution refuter 87 reports both; different lens, not re-run).

## Clause table

| Clause | Authority text (short) | Code site | Status |
|---|---|---|---|
| Ruling 46 A1 — pass `None` | "`_derive_preflight_systematic_screen_s(identity_epoch=None)` … while skipping the epoch equality" | `validate_powermetrics_fiducial.py:456-458` (in `_derivation_only_screen_basis`, `:439`) | IMPLEMENTED |
| A1 — still authenticate bytes/role/protocol/estimator | "already authenticates the active artifact's bytes, role, protocol digest, and estimator-code digest" | `:364-436` called unchanged with `None` | IMPLEMENTED (probe 4) |
| A1 — compute the stale-field list locally | "compute the stale-field list locally" | `:1840-1844` | IMPLEMENTED |
| A1 — refuse when EMPTY | "refuse when it is EMPTY (a matching epoch means an ordinary capture is possible and derivation-only would be a bypass)" | `:1845-1850` → `DERIVATION_ONLY_EPOCH_UNCHANGED` | IMPLEMENTED |
| A1 — `derivation_only: true` + `screen_basis{acceptance_id, artifact_sha256, preflight_level_screen_s, epoch}` in the hashed `instrument_evidence.json` | verbatim in A1 | `:2358-2362`, written at `:2372` before hashing | IMPLEMENTED (probe 2 = exact four keys) |
| A1 — same in `manifest.json` | verbatim in A1 | `:2389-2393` | IMPLEMENTED |
| A1 — "Nothing else in the capture path changes" | verbatim | only the `is not None` conjunct at `:2413`, vacuously true whenever a screen exists | IMPLEMENTED |
| Ruling 46 A7 extension rule (S1's half) | "Derivation-only mode therefore REQUIRES a derivation-kind session slot and refuses standalone use and bracket-kind sessions" | standalone `:1851-1858`; kind `:1866-1877` → `DERIVATION_ONLY_SESSION_KIND_REQUIRED` | IMPLEMENTED |
| V1 — rows carry the provenance fields, ordinary `valid` disposition, no parallel schema | "ordinary `valid` rows carrying `derivation_only: true` and `screen_basis` in the hashed evidence and manifest" | as above; no new schema version, no new ledger field | IMPLEMENTED |
| V1 — the structural barrier (`discover_calibration_candidates` + `registered_valid` skip) | "Both sites must change together" | `joulewise/calibration_ledger.py` — S2/S3 scope | NOT IN THIS DIFF (correctly; verify on those seats) |
| V2 — `preflight_systematic_screen_s = None`, comparison skipped | "the writer sets `preflight_systematic_screen_s = None`, skips the comparison at `:2213-2219`" | `:1881`; guard at `:2412-2417` | IMPLEMENTED |
| V2 — disposition is `valid` or `ordinary-invalid` only | verbatim | `:2412-2417` (`systematic-invalid` unreachable when the screen is `None`) | IMPLEMENTED |
| V2 — record whether the bound exceeded r6's level screen `0.032898493715362` | verbatim | `:2363-2368`, mirrored to manifest `:2391-2393` | IMPLEMENTED (probe 2 confirms the lexeme) |
| Addendum A-1 — recovery finalization path binds the same rule | "`resume_finalize_bracket_session` … the caller passes `None`" | `calibration_ledger.py:5477-5488` (S2, pre-existing in this base); the LIVE path passes a computed `disposition`, never a screen (`:2419`), so no prior-epoch screen can reach a derivation row on S1's path | OUT OF S1 SCOPE / CONSISTENT |
| Addendum A-1 — `slot == "pre"` auto-abort suppressed for derivation | verbatim | S2's session-shape routing; S1 changed nothing here | NOT IN THIS DIFF (correctly) |
| Addendum A-5 — mutation-kill counterfactual for the barrier | "a derivation row present in the `registered_valid` universe with the skip removed at one site only" | S2/S3 seats | NOT IN THIS DIFF (correctly) |
| Brief (a) — requires `--allow-live` | brief verbatim | enforced by ORDER: `:1770` `QUIET_MAC_AUTH_REQUIRED` precedes `:1830` | IMPLEMENTED-BY-ORDERING (see N-3) |
| Brief (b) — derivation-kind slot required; standalone and bracket-kind refuse; two new `RefusalCode`s | brief verbatim | `calibration_exits.py:96-102`; `:1851`, `:1872` | IMPLEMENTED |
| Brief (c) — `identity_epoch=None`, local stale list, refuse when empty | brief verbatim | `:456-458`, `:1840-1850` | IMPLEMENTED |
| Brief (d) — screen `None`; provenance + `exceeds_prior_level_screen` (diagnostic only) in both hashed files | brief verbatim | `:1881`, `:2358-2368`, `:2389-2393` | IMPLEMENTED |
| Brief (e) — `--rederive-from` refuses with the flag | brief verbatim | `:1721-1732` (also covers bare `--output`) | IMPLEMENTED (see N-2) |
| Fix round 1 — third code (beyond the brief) | not ruled; the writer-side converse of A-1's principle "The derivation-only classification rule binds every finalization path, not just the live writer's" | `calibration_exits.py:100-102`, `:279`; guard `validate_powermetrics_fiducial.py:1378-1395` | DEFENSIBLE EXTENSION, class consistent (see §1) |

## §1 — Is the third code's `abort-session` / `session_aborted` class consistent with the registry contract?

**Yes, on the merits, and the brief's `preflight`/`ready_to_arm` would have been
WRONG here.** The contract's completeness rule is what decides it
(`docs/contracts/calibration_ledger_append.md:25-29`):

> "Cross-layer exit completeness is owned by the immutable registry in
> `joulewise/calibration_exits.py`, whose generated projection appears below.
> Reservation, recovery, writer, and supervisor refusals are complete only when
> their registry witness reaches its **declared terminal result** in a fresh
> public CLI process."

A `correct-preflight` row obliges the witness to reach `ready_to_arm` by
correcting the invocation on the SAME durable state — that is what the
`Correction surface` and `Corrected success` columns are for, and it is why
`_route` fills them only for `_PREFLIGHT` codes
(`calibration_exits.py:502-539`). Verified by reading statement order (probe 5):
the guard at `:1378-1395` is reachable ONLY when the live epoch MATCHES the
active acceptance, because on a differing epoch the ordinary preflight raises
`acceptance_artifact_epoch_mismatch` → `FROZEN_PROTOCOL_INVALID` at `:1884-1890`,
before the lifecycle is even constructed (`:1920`). In the matching-epoch state
there is no forward correction: adding `--derivation-only` refuses
`DERIVATION_ONLY_EPOCH_UNCHANGED` by design (A1), and a second session cannot be
opened while one is open. The only governed exit really is
`recover_calibration_ledger.py abort-session`, and `night_loss: true` is the
honest value. `Correction surface`/`Corrected success` are empty, exactly as
they are for every other `abort-session` row (`:277`, `:310-314`, `:319`).

Two consequences worth recording rather than fixing:

- The real 25G83 campaign never reaches this code. An operator who forgets
  `--derivation-only` at a derivation slot on the NEW epoch gets
  `FROZEN_PROTOCOL_INVALID` (`correct-preflight`, `night_loss: false`) and
  simply re-runs with the flag. No night is lost in the scenario the mechanism
  exists for; the abort-class row governs only the mis-opened-session world.
- The contract's operator-CLI gloss of the class,
  `calibration_ledger_append.md:361` — "`abort-session`: preserve partial
  custody and close under the same lease" — presupposes partial custody, and
  here there is none (the guard raises before `writer_lease.acquire()`;
  nothing is appended). That looseness predates this diff
  (`calibration_ledger_bracket_session_open` and
  `calibration_reservation_identity_conflict` are in the same position), so it
  is a nit, not a divergence introduced by S1.

## §2 — Are the provenance fields documented, and is anything stale?

**In THIS tree: no.** `grep 'derivation_only|screen_basis|exceeds_prior_level_screen'
docs/contracts/*.md` in the S1 worktree hits only the three generated registry
rows. The schema owner is `docs/contracts/powermetrics_fiducial.md` §Artifact
layout / §Binding (`:129-185`), which currently names neither field. That is
correct for S1 (its WRITE_SCOPE excludes contracts) and is seat S6's row.

**In the integration tree: mostly yes.** `JouleWise-wt-epoch-integration/docs/contracts/powermetrics_fiducial.md:118-141`
lands the paragraph: "Both `instrument_evidence.json` and `manifest.json` carry
`derivation_only: true` and a `screen_basis` object naming the prior
acceptance's ID, its file SHA-256, its `preflight_level_screen_s` … and its
epoch", plus "The prior artifact's level screen is not applied to the capture."
Gaps (SF-3, SF-4 below): the third key's NAME `exceeds_prior_level_screen` is
never written — only described as "recorded in the hashed evidence as a
diagnostic" — so a reader cannot map contract to bytes; and the finalize
kind-check is described as refusing "`systematic_screen_kind_mismatch`", which
is a context REASON on `RESERVATION_INPUT_INVALID`
(`joulewise/calibration_ledger.py:5478-5488`), not a registered code:
`recover_calibration_ledger.py explain systematic_screen_kind_mismatch`
resolves to nothing and the generated table has no such row.

**Stale statements hunted and NOT found:** no contract asserts that every
ledger row was judged by the active screen. `calibration_ledger.md:86` lists
`"disposition": "valid | systematic-invalid | ordinary-invalid"`, still a
superset; `:231` is a historical count of the issued D-079 prefix, untouched.

**One under-description that IS now real (SF-5):** the reduce-time acceptance
list at `powermetrics_fiducial.md:168-185` (S1 tree; `:251` ff. in the
integration tree) fails closed unless ALL of
"`schema_version` is `joulewise.instrument_evidence.v1`; … `status` is
`valid`; … every binding field is present and non-empty; and the
bundle-supplied environment fields … match the artifact bindings". A
derivation-only artifact satisfies every one of those on a 25G83 bundle. The
real barrier is ledger-side (V1's discovery/`registered_valid` skips and
`evaluate_calibration_bracket`'s unbound-endpoint refusal, A-5), but the
contract that owns the artifact schema now describes a `valid` v3 artifact
class it does not mention, and the same section still says "A single valid
calibration remains usable only for explicitly non-claim-bearing probe or
exploratory reduction" (S1 tree `:118-120`; integration `:203-204`) without excepting derivation-only bytes.

## §3 — Does `--help` pass the first-use test for `derivation-only`?

Marginal pass. The text is: "capture to BUILD a future acceptance for an
identity epoch no issued acceptance binds; requires --allow-live and a declared
derivation-kind session slot, and licenses no measurement"
(`:1696-1704`). From the help alone a reader learns what it licenses (nothing)
and its two preconditions. Two pedagogy defects (N-3): "derivation-kind session
slot" is a term of art used without a gloss or a pointer, and "licenses no
measurement" is the compressed form of the contract's "never to license a
measurement window" — the shorter phrase leaves open "no measurement *now*".
The module docstring (the `--help` preamble, `:1-35`) does not mention the mode
at all, so the reader who scans the preamble sees only the ordinary protocol.

## §4 — Ordinary-path prose/comments whose meaning changed

One, and it is the SF-1 fix: `scripts/validate_powermetrics_fiducial.py:482-484`

> "Recovery's resume-finalize path imports this historical public symbol. It
> remains available as an authenticated derivation, never as a copied scalar;
> **the live writer below independently derives and epoch-checks its local
> value.**"

The new `_derivation_only_screen_basis` was inserted immediately ABOVE this
comment, and it is precisely the path on which the live writer derives WITHOUT
the epoch check. The final clause is now false in one mode and reads as a
guarantee. Nothing else changed meaning: the module docstring's "the run is
refused without --allow-live" (`:20`) still holds (`:1770`);
`_derive_preflight_systematic_screen_s`'s docstring "Authenticate the active
acceptance and derive its level comparator" is unchanged and accurate; the
`_CaptureLedgerLifecycle.begin` "Early warning only" comment (`:1375-1376`) is
untouched and the new guard is correctly placed under it, before
`_validate_slot()` and before the lease.

## §5 — Is the diagnostic field's contract ("never a refusal") stated anywhere?

In code, yes: `:2359-2362` — "DIAGNOSTIC ONLY. This never changes the
disposition: excluding a valid capture of the new epoch because it exceeds the
old epoch's threshold would fit the new screen to the old one." In prose, yes
in the integration tree (`powermetrics_fiducial.md:128-136`), but without the
key's name (SF-3). In tests, **no** — and that is the sharper half of the
`@unittest.skip` (`tests/test_validate_powermetrics_fiducial_derivation_only.py:721-739`).
Because the field is `False` in every executed test, a mutant that folds it
into the disposition, e.g.

```python
disposition = "systematic-invalid" if evidence_payload["exceeds_prior_level_screen"] else "valid"
```

SURVIVES the whole suite: the property "diagnostic, never a refusal" is proven
only for the FALSE case, which is the case where the property is vacuous. The
skip reason is exemplary about WHY the TRUE branch is unreachable here (fixture
bound ~9.3e-05 s vs a 0.0329 s screen; `_valid_acceptance_bound` forbids
rewriting the screen; a test-only `--acceptance-path` override correctly
REJECTED as an epoch bypass) and names two out-of-scope cures. Where the
contract for the field should live: (i) name the key in
`powermetrics_fiducial.md` beside the `screen_basis` sentence; (ii) name it in
the pre-registration's screen-challenge rule, which is its only consumer; and
(iii) once seat S4's issuer can mint a synthetic issued acceptance, cure (a)
from the skip reason and delete the skip — that is the only thing that kills
the mutant above.

## Findings

### Blockers
None.

### Should-fix

- **SF-1 (S1's file, 3 words).** `:482-484` comment is now false on the
  derivation path (§4). Suggested: "… the live writer below independently
  derives and epoch-checks its local value on the ordinary path; the
  derivation-only mode above skips only that equality, by ruling 46 A1."
- **SF-2 (verification, S1's tests, no edit needed).** The abort-class row is
  contractually complete only when its witness "reaches its declared terminal
  result in a fresh public CLI process" (`calibration_ledger_append.md:25-29`).
  The new `WitnessCase(DERIVATION_SESSION_REQUIRES_DERIVATION_ONLY,
  "_state_derivation_kind_writer", "writer-derivation-session")`
  (`tests/test_calibration_exits.py:1223-1227`) drives the `abort-session` CLI
  branch and asserts `terminal == "session_aborted"` (`:5823`) after driving the `abort-session` CLI (`:5593-5600`), and it opens a
  derivation-kind session with ZERO finalized slots — a shape
  `abort_bracket_session` has not been exercised on before. The magistrate's
  post-fix bench run was the 41-test focused set, which does not include it.
  Run `python3 -m unittest
  tests.test_calibration_exits.PublicGovernedExitWitnessTests.test_parameterized_durable_public_cli_witnesses`
  once before merge. (I did not run it: the brief forbids me the module.)
- **SF-3 (S6 / integration).** Name the key `exceeds_prior_level_screen` in
  `docs/contracts/powermetrics_fiducial.md` (integration tree `:132-135`, the sentence at `:133-135`)
  beside the `screen_basis` sentence, so the contract maps to the bytes.
- **SF-4 (S6 / integration).** The same section says the finalize kind-check
  "refuses `systematic_screen_kind_mismatch`"; that string is a context reason
  on `RESERVATION_INPUT_INVALID` (`calibration_ledger.py:5478-5488`), not a
  registry row, and the writer-side pre-lease half —
  `calibration_derivation_session_requires_derivation_only`, the code THIS diff
  adds — is not named in the prose at all. A reader of the contract concludes
  the only guard is at finalization. Name both, and mark the reason string as a
  reason, not a code.
- **SF-5 (S6 / integration, one sentence).** `powermetrics_fiducial.md:203-204` (integration tree; `:118-120` in S1's)
  ("A single valid calibration remains usable only for explicitly
  non-claim-bearing probe or exploratory reduction") and the reduce-time ALL-of
  list at `:251` ff. now admit a `valid` v3 artifact class they never mention.
  Add: a derivation-only artifact is never a bracket endpoint and never
  licenses a window; the enforcement is ledger-side (V1's discovery and
  `registered_valid` skips, and `evaluate_calibration_bracket`'s unbound-endpoint
  refusal), not the `derivation_only` field, which is provenance.
- **SF-6 (magistrate ruling, not a code fix).** Either accept the skipped TRUE
  branch as a registered limitation with the surviving mutant of §5 written
  down, or schedule cure (a) after seat S4's issuer lands. Do not let it merge
  as an unrecorded gap: the skipped clause is the one that proves "diagnostic,
  never a refusal".

### Nits

- **N-1.** `_derivation_only_screen_basis` (`:439-479`) opens the artifact three
  times: authenticated inside `_derive_preflight_systematic_screen_s` (`:456`),
  re-loaded at `:459`, hashed at `:475`. The recorded `artifact_sha256` is
  therefore not provably the bytes that were authenticated. Under D-161
  (operator-only-adversary refusals are over-engineering) this is explicitly
  not worth a refusal; it would be free if the authenticator returned the
  loaded artifact.
- **N-2.** `--derivation-only --output X` (no `--rederive-from`) now refuses
  `calibration_writer_bracket_rederive_conflict`, whose registry description is
  "bracket session parameters apply only to live capture" and whose
  `corrected_success` is `rederive_valid_then_writer_capture_valid_slot_finalized`
  — the operator is pointed at a re-derivation when the cure is to drop a flag.
  Bare `--output` still gets the accurate `OUTPUT_REQUIRES_REDERIVE` (`:1754`).
  Same finding as execution refuter 87 nit 1; independent second lens.
- **N-3.** Help-text pedagogy (§3): gloss or cross-reference "derivation-kind
  session slot" at first use, and spell out "never licenses a measurement
  window" rather than "licenses no measurement". One clause in the module
  docstring naming the mode would let the `--help` preamble stand alone.
- **N-4.** `derivation_bound_lexeme` (`:2353-2357`) re-serializes the whole
  evidence payload to recover `b_fiducial_s`, which `:2405` recovers again 50
  lines later as `bound_lexeme` from the same round-trip. Same value, twice the
  work; the diagnostic and the disposition are comparing the identical lexeme
  (checked), so this is style only.

## Chain compatibility (S5, `calibration_derivation_only.zsh:189-199`)

Every flag and value the chain passes is accepted (probe 1); the chain passes no
positional argument and no flag the writer lacks. Slot names `d01…dNN` are free
strings to the writer and are validated against the session's declared list, so
the `args.slot == "post"` special case (`:1933`) is correctly inert for
derivation nights. The chain runs under `set -e`, never inspects a printed
reason, and documents that any nonzero leaves the session open for the desk
tool — which matches S1's refusals (all `process_exit=2`) exactly. The one
alignment note: on the real 25G83 epoch a chain invocation that lost
`--derivation-only` would print `calibration_frozen_protocol_invalid`, not the
new code (§1); a reader of the night log should not expect
`calibration_derivation_session_requires_derivation_only` to be the signature of
that mistake.

## Scope note

`docs/contracts/calibration_ledger_append.md` is outside the seat brief's
`WRITE_SCOPE`; record 84 grants it for the regenerated registry block, and the
generated block is the only thing that changed there (3 rows, all projections of
`REFUSAL_INVENTORY`, freshness executed at probe 3). No prose in that contract
was edited. Report 76 describes commit `73eab3f8`, not HEAD: its claim
"`_CaptureLedgerLifecycle` needed **no change**" and its two-new-codes
inventory are both superseded by fix round 1 — read 86 alongside it.
