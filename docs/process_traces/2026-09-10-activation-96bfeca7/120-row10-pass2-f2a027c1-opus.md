# 120 — Gate ledger row 10, PASS 2 (final head): fresh-eyes review

- **Tree:** `/Users/edr/code/JouleWise-wt-epoch-integration`
- **HEAD (verified):** `$ git rev-parse HEAD` → `f2a027c12d714296adcc24dcaa37ea36ae06fe7d`; `git status --porcelain` empty.
- **Range reviewed:** `1e15a3a5..HEAD` — 3 commits (`6c581738` S6 docs, `f31f24d8` S4 round 7, plus the two merges), 4 files, +87/−8.
- **Mode:** strictly read-only. No edits, no cuts, no git state changes, no other worktree written. Three test targets run (two named singles + `tests.test_docs_freshness`); the suite was NOT run.
- **Reviewer:** Opus 5 (1M), same reviewer as report 117 (pass 1 covered `d9612e68..1e15a3a5`).

## VERDICT: **CLEAN**

Both pass-1 should_fix items (S-1 in-place ruled-text edit, S-3 contract sentence) and the pass-1 nit N-1 (nights fence counting flag repetitions) are cured. No new defect, no seam break, no regression of a reviewed property, no new line pins, no scope excursion. Three nits below, all doc-cosmetic; none blocks the merge.

---

## (1) Decision log: does the change amend any ruled text beyond restoring it? — **NO. The in-place edit is fully undone, byte-identical.**

Mechanically compared the V7 clause body (regex-extracted from `- **V7 — the successor's screen and ceiling.**` up to the next top-level bullet) across four revisions:

```
$ python3 - <<'PY'  (git show <rev>:docs/decision_log.md, sha256 of the extracted V7 clause)
6c581738^  a9c77d166aab3655  1069 bytes     <- state BEFORE the seat's in-place edit
6c581738   2302fda60b7aec4c  1148 bytes     <- the in-place edit (pass-1 S-1)
1e15a3a5   2302fda60b7aec4c  1148 bytes
HEAD       a9c77d166aab3655  1069 bytes     <- identical to 6c581738^
PY
```

And against the ORIGINAL introduction of the clause (`git log -S` finds exactly one commit that ever added it, `3c60f0ec` "Seat S6 (Opus) complete, UNREVIEWED"):

```
3c60f0ec   a9c77d166aab3655  1069 bytes     <- identical to HEAD
```

So HEAD's V7 is byte-for-byte the text as first transcribed, not a paraphrase of it. "predecessor ceiling" / "carried on the successor's generation row as `predecessor_ceiling_s`" are gone from the clause body; "inherited ceiling" is back in both places (`docs/decision_log.md:6655-6656`, `:6663`).

**Against the cold gate 46 primaries** (`/Users/edr/code/JouleWise-wt-bk-96bfeca7/docs/process_traces/2026-09-10-activation-96bfeca7/46-coldgate-packet-epoch-bootstrap/`):

- `11-ruling-addendum-opus-amendments.md:22-26` (amendment **A-3**, the text that created V7's C half): "`C = max(inherited ceiling, new Q99)`… and the generation row carries the **inherited ceiling**."
- `12-opus-pairing-refuter-on-ruling-46.md:59` (A-3 verbatim, same wording).
- `10-coldgate-fable-ruling.md:41` (V7 row) uses "inherited S / inherited C".

HEAD's decision-log wording uses exactly the ruled term in both positions. The transcription's expansions ("where the inherited ceiling is the predecessor generation's `maximum_budgetable_drift_s`", the r6 worked number, the D-126 cl.3 cap) all pre-date this range and trace to A-3's own text; nothing in this range touches them.

The correction now lives where it belongs — as a **dated addendum**, `docs/decision_log.md:6685-6688`, transcribing ruling 69 / 69-A1 and explicitly self-labelling "not an amendment by the seat… The wording above is cold gate 46's and stands as ruled."

The V4 210-minute open item is likewise a dated note, `docs/decision_log.md:6689-6691`, not an edit: V4 at `:6646-6652` is untouched (`git diff 1e15a3a5..HEAD -- docs/decision_log.md` shows no V4 hunk), and it still reads "…is 128 of a 210 min window."

**Every factual number the new note asserts was executed against the code** (the note is new prose in a ruled record, so it has to be true):

```
$ python3 -c "import sys; sys.path.insert(0,'scripts'); import gen_derivation_night as m; ..."
programmed_span_s(12) = 7680
min window = 7980            # programmed_span_s(12) + PRE_SETTLE_ALLOWANCE_S (=300, gen_derivation_night.py:90)
EXAMPLE_WINDOW_MAX_S = 9000
settle/cadence/budget = 600 600 480
```

matching `scripts/gen_derivation_night.py:515-521` (`required_window = required_span + PRE_SETTLE_ALLOWANCE_S`) and the pre-registration's three-durations section (`configs/calibration/preregistration_d079_epoch_25g83_rev1.md:98-124`). Both addenda sit inside D-102's record (nearest preceding heading `docs/decision_log.md:6449`, next at `:6700`) — correct home.

`$ python3 -m unittest tests.test_docs_freshness -q` → `Ran 31 tests … OK` (rc 0).

## (2) Repeated-session refusal: reachable, fail-closed, before blindness, no leak — **YES on all four**

```
$ python3 -m unittest tests.test_issue_calibration_acceptance_generation.PrepareCandidateTest.test_a_repeated_registration_session_refuses \
    tests.test_issue_calibration_acceptance_generation.PrepareCandidateTest.test_the_night_count_fence_counts_distinct_sessions -v
test_a_repeated_registration_session_refuses … Three flags naming one night are not three nights. ... ok
test_the_night_count_fence_counts_distinct_sessions … With the repetition refusal disabled, the count still sees ONE night. ... ok
----------------------------------------------------------------------
Ran 2 tests in 26.151s

OK
```

Both tests drive the real CLI through `run_issuer` (`tests/test_issue_calibration_acceptance_generation.py:794-821`), which already supplies one `--registration-session-id SESSION`; the extras add two more of the SAME id, and passing `--nights-ruling ""` suppresses the helper's default ruling so the falsy value leaves the count fence armed. So the first test reaches `refuse_repeated_sessions`, and the second — with that function monkeypatched to a no-op, the only way to get duplicates past it — reaches the count fence and gets `registration names 1 sessions, not the pre-registered 3`. The two checks are genuinely independent: deleting either does not silently restore the other's defect. That is the shape a mutation probe would want, achieved without one.

**Order (read at `scripts/issue_calibration_acceptance_generation.py:1179-1183`):**

```
1179    session_ids = tuple(args.registration_session_id)
1180    refuse_repeated_sessions(session_ids)
1181    refuse_open_registration(snapshot, session_ids)
1182    if snapshot.refusal_reasons:
1183        raise PrepareRefusal("ledger: " + ", ".join(snapshot.refusal_reasons))
```

The new refusal runs one line before the blindness gate. **No leak:** `refuse_repeated_sessions` (`:953-976`) takes only `Sequence[str]` — it never receives or touches `snapshot`, reads no observation, computes no statistic, and its message (`:971-975`) echoes back only ids the caller typed on its own command line. Blindness's actual property (no member value, screen or statistic observable before every registration session is terminal) is unchanged; the only behavioural difference is that a caller who both typed duplicates and has an open session now sees the malformed-input refusal instead of the blindness refusal — both refusals, neither carrying data.

**Fail-closed:** there is no override flag. `--nights-ruling` and `--slot-count-ruling` do NOT relax it — `refuse_repeated_sessions` is unconditional, so even a ruling permitting four nights cannot admit a duplicated id. It is the sole call site (`grep -n "refuse_repeated_sessions"` → definition `:953`, call `:1180`), and the only other consumer of the tuple, the emitted row `"registration_session_ids": list(session_ids)` at `:1447`, is now unreachable with duplicates.

**Nights fence (`:1218-1224`)** now computes `distinct_nights = len(set(session_ids))` and both tests and refuses on that, closing pass-1 N-1 exactly as suggested.

## (3) Contract sentence vs code — **MATCHES, and it now names the right record**

`docs/contracts/calibration_ledger.md:143-149`:

> "…refuses when the pre-registration's recorded `os_build` differs from the registration's target identity epoch, or when any registration row's recorded T1 bindings carry a `/usr/bin/powermetrics` SHA-256 other than the pre-registered one (the sampler digest is a T1 binding, not one of the six identity-epoch fields, so it is checked on every row rather than once)."

Code (`scripts/issue_calibration_acceptance_generation.py:1237-1251`):

```
1237    observed_powermetrics = {
1238        observation.t1_bindings.get("powermetrics_sha256")
1239        for observation in observations
1240    }
1241    if target_epoch.get("os_build") != registered_os_build:      -> "the registration is void"
1246    if observed_powermetrics != {registered_powermetrics}:       -> "the registration is void"
```

Every clause of the sentence lands: `os_build` is compared once against the unanimous target epoch (unanimity enforced at `:1211-1214`); the sampler digest is read per observation from `t1_bindings` and the set must equal the singleton, so ANY row differing — including a row missing the key, which contributes `None` — refuses. The parenthetical is true: `IDENTITY_EPOCH_FIELDS` (`joulewise/calibration_ledger.py:110-117`) is exactly six fields (`os_build`, `hardware_model`, `power_policy`, `sampling_interval_ms`, `estimator_revision`, `pulse_protocol_id`) and `powermetrics_sha256` is not among them; it lives in `T1_FIELDS` (`:118`). Pass-1 S-3 is cured, and the replacement sentence meets the writing standard's replication bar — a reader now knows which record to open.

## (4) Line pins and scope — **CLEAN**

```
$ git diff 1e15a3a5..HEAD | grep -E '^\+' | grep -nE '[A-Za-z_/]+\.(py|zsh|md):[0-9]+'
(no output; rc=1)
```

Zero new `<file>:<digits>` citations in added lines. The new decision-log addendum cites ruling 69 and 69-A1 by name, the contract bullet cites no line, and the new docstrings cite symbols (`refuse_repeated_sessions`, `MAX_DECLARED_SESSION_SLOTS`) rather than positions.

Files touched in this range: `docs/contracts/calibration_ledger.md`, `docs/decision_log.md` (S6); `scripts/issue_calibration_acceptance_generation.py` + its test module (S4). No production file outside the epoch lane, no `joulewise/` change, no receipt-writing or ledger code, nothing in another seat's footprint. `docs/decision_log.md` was the pass-1 rule-11 flag; this range's touch of it is a net restoration plus two self-labelled dated notes, which is the sanctioned mechanism — the magistrate call S-1 asked for has been answered in the direction that needs no ratification.

## Nits (no action required to merge)

**N-1 — the two dated notes attach to the wrong bullet.** `docs/decision_log.md:6685-6691` are indented continuation lines of the **Exclusions** bullet (which ends `…after seeing it.` at `:6684`), with no blank line before them, so in rendered Markdown they run on as the same paragraph as Exclusions. But the first says "the quantity **this clause** calls the 'inherited ceiling'" (that is V7, `:6655`) and the second "**this clause's** '210 min window'" (that is V4, `:6649`). Neither phrase resolves to the bullet they sit under. Under the writing standard's no-unpaid-work rule, "this clause" is doing work the placement contradicts. Cure without touching ruled text: name the clause explicitly ("V7's 'inherited ceiling'", "V4's '210 min window'"), and/or move the notes to a blank-line-separated block after the list.

**N-2 — "the armed window IS 9000 s" overstates the current state.** `docs/decision_log.md:6689`. No night under this registration is armed; 9000 s is the pre-registration's *recommended* value (`configs/calibration/preregistration_d079_epoch_25g83_rev1.md:110`, "**Recommended `window_max_s` — 9000 s**") and the generator's `EXAMPLE_WINDOW_MAX_S` (`scripts/gen_derivation_night.py:663`); the only tracked plan carrying it is the runsheet example (`docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:1659`). The arithmetic is right; only the tense is ahead of the facts. "the window these nights are to be armed with" would be exact.

**N-3 — `refuse_repeated_sessions` is O(n²) with a list rebuilt per element.** `scripts/issue_calibration_acceptance_generation.py:963-968` calls `list(session_ids).count(session_id)` inside a set comprehension. With n ≤ 4 this is free; a `collections.Counter` would be clearer. Cosmetic only — noted so a later reader does not mistake it for intent.

(Pass-1 nits N-2 "chain rc-1 branch assumes finalized" and N-3 "`_identity_epoch_value_ok` admits floats" are untouched by this range and still stand as recorded in report 117.)

## Bottom line for the magistrate

The final head cures everything pass 1 raised. The seat's in-place edit to cold gate 46 clause V7 is undone byte-identically to the clause's original transcription (sha `a9c77d16…`, 1069 bytes, matching `3c60f0ec`), and the terminology correction and the 210-minute open item now sit as dated, self-labelled addenda that claim no amending force — with every number in them executed against `gen_derivation_night.py`. The contract's epoch-match sentence now describes what the code does, including the per-row T1 sampler-digest check that the previous sentence mislocated. The repeated-session refusal is reachable, unconditional, ahead of the blindness gate, and leaks nothing; the nights fence independently counts distinct ids, and each check is tested with the other disabled. No new line pins, no scope excursion. **CLEAN.**
