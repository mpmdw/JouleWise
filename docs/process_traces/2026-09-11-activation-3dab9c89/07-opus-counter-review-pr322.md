# 07 — Opus counter-review (contract + physics-of-the-gate) of PR #322 at HEAD `1f8c1174`

Lane NIGHT-C1-REGISTRATION-DOCS-01, branch `fix/2026-09-11-c1-registration-seam`,
two commits over `origin/main` `1dddcfea`. Read-only in
`/Users/edr/code/JouleWise-wt-c1-seam`; working tree clean before and after
(`git status --porcelain` → empty); temp artifacts only under `/tmp/opus-322/`.
Lens distinct from refuter 01: I did not redo its contract table. I executed the
gate, the runbook's own commands, and the generator.

---

## A. Does the cure close B-1 in the live path?

**Yes for the gate; the plan the runbook now tells the operator to author passes C1 at HEAD.**

What row C1 reads (`joulewise/night_gate.py`):

- `night_gate.py:1300` — `if plan.receipt_class in {"DIAGNOSTIC_NO_PACK", "REHEARSAL_STUB"}:` — one
  branch, both classes, no chain/plan-field awareness.
- `night_gate.py:1302` — `registration_text = probes.read_text(plan.registration_path)`;
  `:1305-1307` — `hashlib.sha256(registration_text.encode("utf-8")).hexdigest()`.
- `night_gate.py:1315` — compares against `D166_REGISTRATION_SHA256`
  (`night_gate.py:34-36` = `dfe55f8d…ac265`); mismatch →
  `night_gate.py:1320-1322` `Refusal("night_refused_registration", …)`.
- `night_gate.py:1327-1328` — on match `C1` PASS, detail `"D-166 registration hash passed"`.
- The compared constant is the **D-166 literal only**. There is no pre-registration constant
  anywhere in the gate.

Executed (`/tmp/opus-322/exec_c1.py` — my own plan author + my own `Probes` bundle, no test
fixtures imported; `read_text` goes to the real filesystem so the digest is the file's true bytes;
plans written to `/tmp/opus-322/plan-*.json` and parsed through the production
`NightPlan.from_mapping`):

```
$ PYTHONDONTWRITEBYTECODE=1 python3 /tmp/opus-322/exec_c1.py
gate constant D166_REGISTRATION_SHA256 = dfe55f8d96cd21e07cd1c7fe230fef34f485f027f3920ce96b8a9ebacc1ac265
  on-disk sha256 D-166 literal     = dfe55f8d96cd21e07cd1c7fe230fef34f485f027f3920ce96b8a9ebacc1ac265
  on-disk sha256 pre-registration  = ca2430ddd04b4a95b3ea0420ecf4d0897e1d1409f9d4f9f102414d00c37a5da7

DIAGNOSTIC_NO_PACK   D-166 literal     C1=PASS detail='D-166 registration hash passed' refusal=None
DIAGNOSTIC_NO_PACK   pre-registration  C1=FAIL detail=None refusal='night_refused_registration'
REHEARSAL_STUB       D-166 literal     C1=PASS detail='D-166 registration hash passed' refusal=None
REHEARSAL_STUB       pre-registration  C1=FAIL detail=None refusal='night_refused_registration'
```

So: the equivalence night's class (`DIAGNOSTIC_NO_PACK`) and tonight's stub class
(`REHEARSAL_STUB`) take the identical branch; the D-166 literal PASSES, the pre-registration
REFUSES. The pre-`1dddcfea` runbook armed the second row; HEAD arms the first.

**Does the runbook produce exactly that path?** Executed end-to-end: I took the plan shape the
operator is told to author (the generated runsheet example at
`docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:1667`, filling only the two
`<40-hex …>` blanks), then ran the runbook arm block's two new registration assertions
(`docs/phase_2/derivation_night_runbook.md:1305-1308`) verbatim against it with
`MEASUREMENT_ROOT` = the worktree:

```
authored registration_path: configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json
arm-block registration lines:
  assert plan.registration_path == night_gate.D166_REGISTRATION_PATH
  assert hashlib.sha256((Path(os.environ['MEASUREMENT_ROOT']) / night_gate.D166_REGISTRATION_PATH).read_bytes()).hexdigest() == night_gate.D166_REGISTRATION_SHA256
rc= 0 ARM-BLOCK REGISTRATION ASSERTIONS PASS
```

Prose the operator copies from is consistent at every site: `runbook:500-507` (§0.5),
`:781` (§1.1 table), `:1256-1259` (§1.4), `:1305-1308` (arm block), `:1419` (arm record),
`:2113-2117` (§5 gloss).

**One live-path detail neither the ruling nor refuter 01 states.** The plan's
`registration_path` is *repo-relative*, and the production probe resolves it against the process
cwd: `scripts/run_night.py:296` — `read_text=lambda path: Path(path).read_text(encoding="utf-8")`.
The cwd is the launchd `WorkingDirectory`, rendered from `@@REPO@@`
(`configs/launchd/com.joulewise.night.plist.template:18-19`), where `repo` is the checkout that
holds the installer (`scripts/install_night_agent.sh:31-32`). The runbook installs from inside the
clone (`runbook:1275` `cd "$MEASUREMENT_ROOT"`, `:1331-1333` "Install both agents FROM the clone"),
so the resolution lands inside the measurement clone and matches the bytes the arm block hashed.
The operator check at `runbook:1341-1345` ("`WorkingDirectory` (the clone)") is what keeps that
true; nothing in the arm block asserts it. See NIT N3.

---

## B. Is the pre-registration "bound by H"? What is and is not protected

**Where the comparison happens.** `joulewise/night_gate.py:1006` calls
`probes.measurement_head(plan.measurement_root)`; the production implementation is
`scripts/run_night.py:284-290` — `git -C <measurement_root> rev-parse HEAD`. At
`night_gate.py:1019-1030`, if that differs from `plan.measurement_head` the night refuses with
`night_plan_stale`. The driver checkout's own head (`probes.checkout_head()`,
`run_night.py:278-282`) is only *recorded* into `C5.measured` for this class; the equality check
`probes.checkout_head() != plan.repo_head` lives at `run_night.py:1206`, inside
`_produce_pack_go`, i.e. `TRANSACTION_PACK` only. Executed:

```
--- B: what the gate reads, and what a moved HEAD does ---
verdict: GO | files the gate read: ['/tmp/opus-322/custody/chain.zsh',
  '/tmp/opus-322/custody/chain.zsh.sha256',
  'configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json']
pre-registration read at t0? False
clone HEAD != plan.measurement_head -> REFUSED night_plan_stale
driver checkout HEAD != plan.repo_head -> GO None
```

**In plain words a professor could follow.**

*Protected.* The plan names one commit, `H`. Three seconds before the night starts, the gate asks
the measurement clone "what commit are you on?" and refuses the whole night if the answer is not
`H`. The pre-registration is a tracked file inside that commit's tree. Therefore **any change to
the pre-registration that was committed in the measurement clone between arm and t0 is detected** —
committing it moves the clone's HEAD, and the night refuses (`night_plan_stale`). The detection is
coarse but fail-closed: it refuses on *any* commit in that clone, whatever the file.

*Not protected.* An **uncommitted edit** to
`configs/calibration/preregistration_d079_epoch_25g83_rev1.md` in the clone's working tree after the
arm is **not** detected at t0. HEAD does not move; the gate hashes only the chain, its sidecar and
the D-166 JSON (executed read list above); the chain never opens the pre-registration
(`grep -rn 'pre-registration' scripts/night_chains/` → comments at lines 145 and 211 only). The
working-tree edit is also harmless to the captures, because nothing the night runs reads that file.
It only becomes visible later, and only at the desk: the arm-time clean-tree check
(`runbook:1281` `test -z "$(git status --porcelain=v1 --untracked-files=all)"`, and
`runbook:538-539`) establishes at arm that the working copy *equals* the committed bytes; §2.5's
new re-hash reads the committed object (`git show "$H:…"`), not the working copy; and
`prepare-candidate --preregistration-sha256`
(`scripts/issue_calibration_acceptance_generation.py:1178-1181`) refuses issuance if the bytes it
is handed differ from the arm-record pin.

So the synthesis's claim is true with one qualification that the runbook should state: **H binds
the committed bytes, not the file on disk.** The clean-tree check at arm is the only thing that
makes those the same thing, and after the arm nothing re-checks it that night.

---

## C. Dissent check — is there any night-time consumer of the pre-registration's bytes?

**No. None at all.** Exhaustive search of the night path:

```
$ grep -rn 'preregistration' --include='*.py' --include='*.zsh' --include='*.sh' scripts joulewise | grep -v test
```
returns hits in exactly one file, `scripts/issue_calibration_acceptance_generation.py` (a desk
tool): `check --preregistration` at `:299-342` (rc 3 on mismatch) and `prepare-candidate` at
`:1169-1184` with `--preregistration-sha256` `required=True` at `:1796`. The hyphenated spelling
adds only comments (`scripts/night_chains/calibration_derivation_only.zsh:145,211`;
`scripts/epoch_equivalence_check.py:369`). `scripts/epoch_equivalence_check.py`'s parser
(`:670-710`) has no pre-registration argument at all.

Astra's dissent is factually right for this class — C1 authenticates the `_v5` contrast campaign's
registration, which no calibration-derivation capture depends on, so for this night C1 is a
ceremony. The PR does not change that and was not supposed to.

The guards that remain, precisely:

- **PASS route:** the only guard is the new prose at `runbook:1750-1755` — a *human* re-hash by the
  magistrate at harvest, compared against the arm record. No tool enforces it (the equivalence
  checker takes no pre-registration input). So yes: the desk-time re-hash is the only guard on the
  PASS route, and it is unmechanised.
- **FAIL route:** the desk re-hash at `runbook:1814-1819` plus one *mechanical* backstop where the
  data are actually consumed — `prepare-candidate` refuses issuance on a digest mismatch.

---

## D. Pedagogy — first-use test over the changed sentences

Method: mechanical first-use census of every term of art in the new prose
(`grep -n -m2 -i -- "<term>" docs/phase_2/derivation_night_runbook.md`), then read the gloss at
that line.

Built or glossed correctly at first use (no action):

| Term | First use | Gloss |
|---|---|---|
| measurement head | `:13` | "(the commit the plan pins)" |
| SHA-256 digest | `:14` | "(a fingerprint of the file's bytes)" |
| Git blob id | `:17` | "(the identifier of its stored file bytes)"; rebuilt at `:1414-1415` |
| PASS continuation | `:18` | "(extending the existing acceptance to the new instrument configuration)" |
| receipt class | `:505` | "the plan's category, and it selects which gate checks apply"; `DIAGNOSTIC_NO_PACK` named there — refuter 01 F1 correctly cured |
| `REHEARSAL_STUB` | `:2116` | "(a rehearsal using a stub chain)" |
| arm record | `:1411` (definition) | "the committed account of the plan and fixed inputs before capture" |
| FAIL route (in §1.5) | `:1413` | "(the three-night derivation after §2.5 returns FAIL)" |

Defects: S1 and S2 below (accuracy inside a gloss, and an ambiguous one), plus N1 (changelog first
uses). No other new operational sentence lacks a source or a procedure.

---

## E. Regeneration

```
$ PYTHONDONTWRITEBYTECODE=1 python3 scripts/gen_derivation_night.py --check
PASS generated derivation-night wrapper region matches
rc=0
```

Region bounds are `scripts/gen_derivation_night.py:52-53`
(`<!-- BEGIN/END GENERATED: derivation-night-wrapper -->`); in the runsheet they are lines
1615 and 1846. The single changed line is 1667, inside the region:

```
$ git diff --numstat origin/main..HEAD
76      10      docs/phase_2/derivation_night_runbook.md
1       1       docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md
2       2       scripts/gen_derivation_night.py
7       3       tests/test_gen_derivation_night.py
66      0       tests/test_night_gate.py
```

The runsheet's one-line delta is exactly the example literal
(`"<repo-relative path of the committed pre-registration>"` → the D-166 path); the surrounding
sentence "The angle-bracket values are the ones the arm fills in" stays true (two angle-bracket
values remain: `repo_head`, `measurement_head`). Independently re-run at HEAD:
`python3 -m unittest tests.test_gen_derivation_night tests.test_night_gate` → `Ran 97 tests … OK`;
`git diff --check origin/main..HEAD` rc 0; `git status --porcelain` empty.

---

## Findings

### BLOCKER B1 — both new `git` commands are broken in zsh: `"$H:path"` is not `<hash>:<path>`

`docs/phase_2/derivation_night_runbook.md:1428` (the §1.5 blob-id command, inside a ```zsh block)
and `:1755` (the §2.5 re-hash command). In zsh, an unbraced `$H` followed by `:` is parsed as a
history-style modifier, so the colon and one character of the hash are eaten. Both lines are new in
this PR (`git show origin/main:docs/phase_2/derivation_night_runbook.md | grep -n '\$H:'` → no
matches).

```
$ /bin/zsh -c 'MEASUREMENT_ROOT=/Users/edr/code/JouleWise-wt-c1-seam
  H="$(git -C "$MEASUREMENT_ROOT" rev-parse HEAD)"
  git -C "$MEASUREMENT_ROOT" rev-parse "$H:configs/calibration/preregistration_d079_epoch_25g83_rev1.md"'
fatal: ambiguous argument '1f8c11748c620f0c0c6e6c45a9ca7a1b7990364configs/calibration/preregistration_d079_epoch_25g83_rev1.md': unknown revision or path not in the working tree
rc=128

$ … git show "$H:configs/calibration/preregistration_d079_epoch_25g83_rev1.md" | shasum -a 256
fatal: ambiguous argument '1f8c1174…364configs/…rev1.md': …
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  -      <-- sha256 of EMPTY input

$ … with "${H}:…" instead:
ac56d931c025f639df4aeab98f32681fb02e83ba                                  <-- blob id
ca2430ddd04b4a95b3ea0420ecf4d0897e1d1409f9d4f9f102414d00c37a5da7  -       <-- correct digest
```

Why this is a blocker and not a nit: `:1428` is prescribed for **every arm record** (ruling 12 §5
item 2) and fails rc 128, stalling the arm-record step at the desk; `:1755` is worse, because git
writes its error to stderr while `shasum` still prints `e3b0c442…` to stdout — a magistrate
capturing the command's output at harvest gets a plausible-looking digest that is the hash of
nothing, which can never equal the arm record's `ca2430dd…`, producing a **false STOP on the PASS
route** (or, if pasted into a record, a fabricated digest).

**Cure (dictated, two edits, no semantics change):**
- `:1428` → `git -C "$MEASUREMENT_ROOT" rev-parse "${H}:configs/calibration/preregistration_d079_epoch_25g83_rev1.md"`
- `:1755` → `` `git -C "$MEASUREMENT_ROOT" show "${H}:configs/calibration/preregistration_d079_epoch_25g83_rev1.md" | shasum -a 256` ``

Defect-shaped regression (`tests/test_night_gate.py`, `RegistrationSeamTests`): assert that no
line of the runbook matches `\$H:` (require `\$\{H\}:` for any `git` revision:path argument). Fails
at HEAD on lines 1428 and 1755.

### SHOULD_FIX S1 — `runbook:503` misdescribes the file C1 authenticates

> "D-166 records the D-117 contrast campaign's workload-comparison rule."

The file is
`configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json`, whose bytes are
`canonical_json_bytes(dominance_criterion_registration())` (`night_gate.py:37-38`); its content is
the pre-registered attribution-**dominance criterion** — `head -c 700` shows
`"ratio_id":"attribution_dominance_ratio_common_mode.v1"`, `"applies_to":"comparative_abba"` — i.e.
the falsifier ruled in **D-165** ("a dominance RATIO R … gate R ≥ 2 per component per cell",
`docs/decision_log.md:211`, and the gate's own comment "D-165 v2 relabel supersedes the v1
registration digest", `night_gate.py:32`). **D-166** is a different decision — "THE WORKLOAD"
(`docs/decision_log.md:10751-10758`: pinned prompts, Qwen3 chat template, forced 512). "Workload-
comparison rule" is neither. Under the writing standard the gloss has to be built from what the
file actually is; as written a reader forms a wrong model of what C1 checks.

**Cure (dictated):** replace the sentence with — "The file is the `_v5` contrast campaign's
registered dominance criterion: the rule, fixed before that campaign's data, that a measured
energy difference counts only if it is at least twice the widened uncertainty bound (D-165's
falsifier, carried in a file named for D-166). It has nothing to do with this calibration night's
physics; it is simply the one document the night gate is coded to authenticate for this receipt
class."

### SHOULD_FIX S2 — `runbook:1419` says "the frozen plan" in a cell that has just said "plan_id, the night's identifier"

Item 1 of the arm-record table reads: "`plan_id`, the night's identifier; the frozen plan's
SHA-256, equal to the wrapper's `PLAN_SHA256` literal (its recorded plan digest)…". `PLAN_SHA256`
is the **frozen calibration plan's** digest (`scripts/gen_derivation_night.py:287` —
`("PLAN_SHA256", spec.frozen_plan_sha256)`; `runbook:374`, `:834-836`), not the digest of this
night's `night_plan.json`. Two different objects both called "the plan" in one sentence, twelve
words apart; the parenthetical "(its recorded plan digest)" does not disambiguate. Refuter 01 spotted
the same ambiguity and passed it as correct-by-vocabulary; it is correct, and it is still the kind
of sentence that costs a revision round.

**Cure (dictated):** "… the SHA-256 of the **frozen calibration plan** of §0.2 (`$CALIBRATION_PLAN`
— the committed capture plan the captures run under, *not* this night's `night_plan.json`), equal
to the wrapper's `PLAN_SHA256` literal …".

### NIT N1 — changelog introduces four terms before the file builds them

`:12` "the night gate" (built at `:504`), `:13` "the scientific pre-registration" (built in §0.5),
`:13-14` "the arm record" (built at `:1411`), `:15` "the arm block" (never defined in the file;
inferable). The changelog is now the first prose a reader meets. Cheapest cure: at `:12` write "the
night gate (the pre-launch check suite in `joulewise/night_gate.py` that can refuse the night)", and
at `:13` "the scientific pre-registration (the committed document that fixes this campaign's rules
before any data are taken)".

### NIT N2 — the arm assertion and the gate hash the registration through different pipelines

The gate hashes `read_text(...).encode("utf-8")` (`night_gate.py:1302-1307`, newline-normalising);
the new arm assertion hashes `read_bytes()` (`runbook:1306-1308`). They agree today only because
the file contains no CR (`grep -c $'\r'` → 0; both digests `dfe55f8d…`). Already registered as lane
NIGHT-GATE-REGISTRATION-BYTES-01; no action in this PR, but the arm block is now a second site that
would have to move with it.

### NIT N3 — C1's file resolution depends on a launchd setting the arm block does not assert

Per §A, `registration_path` is repo-relative and resolves against the launchd `WorkingDirectory`;
the gate does **not** enforce `checkout_head() == plan.repo_head` for `DIAGNOSTIC_NO_PACK`
(executed: driver-head mismatch → GO). The runbook covers this by installing from the clone and by
the plutil read at `:1341-1345`. Suggested one clause at `:1343`: "`WorkingDirectory` (the clone) —
this is what makes the plan's repo-relative `registration_path` resolve inside the measurement
checkout rather than in some other tree."

### NIT N4 — the arm record does not require the night plan's own digest

Items 1–5 record the frozen calibration plan's digest, the pre-registration's, the wrapper chain's,
the desk inputs' and the evidence-root id, but never `sha256(night_plan.json)` — the one artifact
that names all the others. It is reconstructible (the arm block's `cmp` at `:1351` proves the
published bytes equal the reviewed ones) but not recorded. Ruling 12 §5 did not require it, so this
is out of scope for the PR; worth one line in item 1 if the magistrate wants it.

### Follow-up outside this PR

Record 13 (`13-arm-runbook-stub-20260912.md:93`, `:404-417`) still holds
`<<REGISTRATION_PATH per ruling 12>>`; it must be filled with the D-166 literal before tonight's
stub arm, which is then the first live exercise of C1 (C1 has never passed live — the
rehearsal-20260911 refusal is `night_refused_agent_present` at C3, before C1).

---

VERDICT: MERGEABLE AFTER FIXES

**Residual risk.** After B1's two-character fix and S1/S2's prose, the substance is sound: I
executed the real gate on plans I authored and confirmed both night classes PASS C1 on the D-166
literal and refuse on the pre-registration, and I ran the runbook's own arm-block assertions
against the plan shape the runbook tells the operator to write. The risk that remains is not in the
diff. First, everything here is desk verification — no night has ever reached C1 live, so the
first real evidence that this branch is armed correctly arrives with tonight's stub, and the stub's
`registration_path` placeholder (record 13) is still unfilled. Second, the PASS-route binding of the
pre-registration is now one sentence of prose executed by a human at harvest, with no tool that can
refuse; a magistrate who skips it leaves the "rules fixed before data" claim resting entirely on
`H` plus the arm-time clean-tree check, which do bind the committed bytes but say nothing about a
working-copy edit made after the arm. Third, the runbook's C1 correctness depends on the launchd
`WorkingDirectory` being the clone — an operator-checked property, not an asserted one.
