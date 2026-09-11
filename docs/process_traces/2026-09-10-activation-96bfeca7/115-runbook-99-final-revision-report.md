# 115 — Runbook 99 final revision (WRITER seat, dictated fills)

Scope: `/Users/edr/code/JouleWise-wt-bk-96bfeca7`, one file edited —
`docs/process_traces/2026-09-10-activation-96bfeca7/99-derivation-night-runbook-draft.md`.
No Git state changed (`git status --porcelain` shows exactly one ` M` line for
that file). Canonical `/Users/edr/code/JouleWise` and `/Users/edr/night-custody`
untouched. All sources read read-only via `git -C <worktree> show HEAD:<path>`.

`git diff --stat`: **365 insertions, 36 deletions**, 23 hunks.

## Changelog (as written under the DRAFT banner, now revision 3)

Revision 3 revises against the lane's INTEGRATION head, which moved three
things the runbook operates: the chain now dispatches on the writer's exact
status; the issuer now enforces the pre-registration and the campaign's
declared shape at `prepare-candidate`; the generator now parses (not merely
hashes) the two desk-produced JSON inputs. Revision 2's substance is retained
in one sentence. **All four `[UNVERIFIED]` blocks are kept verbatim** — live
`check` strings (§0.3), identity-epoch / T1-bindings producer (§0.8), the 06:05
cutoff (§1.3), the complete night-gate refusal list (§5) — and the changelog
now names four rather than three, because revision 2's §0.8 addition is one.

## The five dictated changes, and what each is verified against

**1. Writer-status dispatch (§2.1 table row, §2.4 rewritten, §5 chain table).**
§2.4 is retitled "The writer-status dispatch: how a slot ends, and how a night
ends early" and opens with a four-column table: status `0` → finalized
`disposition=valid`, continue; status `1` → **finalized**, `slot_end …
disposition=non-valid`, continue identically (stated as a normal record, with
"expect these in a healthy night's log"); status `≥ 2` → **not finalized**,
`slot_refused slot=dNN rc=<status>`, chain exits with the writer's status and
the session stays OPEN, with no `abort-session` call. Two "why" paragraphs
follow — slots are independent, so one non-valid capture must not cost the
eleven after it, and the writer runs as an `if` condition so `set -e` cannot
pre-empt the dispatch; an unfinalized row would otherwise leave a hole nothing
accounts for, so the chain stops and leaves the disposition to the desk. The
operator action is a named `desk recovery` block (`recover_calibration_ledger.py
… abort-session --reason <named>`), with the explicit instruction to name the
real reason and NOT `window_exhausted`, and the consequence that an unclosed
session blocks the next night's head-equals-pin open (§3 item 4). The
`window_exhausted` material is retained inside §2.4 under its own bolded
heading. §5 gains three new rows (non-valid = not a failure; `rc=2` refusal;
`rc ≥ 3` crash) and the old "Non-zero exit mid-night" row is replaced by one
keyed on a `session_open` line with no `session_abort`. The exit-64 row now
states that the positivity guard covers `SLOT_CAPTURE_BUDGET_S` and why (at 0
the window test is vacuous, so a slot could start one second before the window
ends and capture past it). The wrapper's `FAIL <reason>` rows are unchanged.
Source: `calibration_derivation_only.zsh` at the integration head.

**2. Arm-gate fences (§0.3, §0.5, §4.1, §4.2, §5 issuer table).**
§0.3 gains the `check --preregistration` desk step with the appended line
`pre-registered powermetrics sha256 …: match` / `MISMATCH — the registration is
void`, and — load-bearing — the warning that **the return code cannot report
it**: rc is 3 whenever any field mismatches or any error exists, and the
`os_build` mismatch already forces 3 for this whole lane, so a sampler mismatch
merely adds an error to a code that was 3 already. §0.5 gains the pinned
pre-registration digest (`shasum -a 256` of the file in the clone, made
equivalent to the committed bytes by §0.8's clean-tree check), with the reason:
`prepare-candidate --preregistration-sha256` refuses on any drift, and that pin
is what makes "the rules were fixed before the data" checkable later. §4.1
carries `--preregistration` into the final dry run. §4.2 carries the exact flag
set (adds `--preregistration-sha256`), then names the four fences — document
digest, three sessions, twelve DECLARED slots per session (declared, not filled,
so a window-shortened night still passes), and the `os_build` + sampler-digest
`the registration is void` checks — and glosses the **written-ruling escape**
with the rule for when it applies (only after the ruling exists; never to make
a shortfall issue). §4.2's screen challenge is corrected: the level screen is
no longer an issuer literal, it is read from the authenticated predecessor at
`decimal_derivation.ratified_operatives.preflight_level_screen_s`, and
`R6_MAXIMUM_PLUS_RANGE_S` is re-checked against the predecessor's
`source_statistics`. §5's issuer table gains a row carrying all six new refusal
texts. These are report 109's BLOCKER-BEFORE-ARM items B-1/B-2/B-3, now
enforced; §7 records that.

**3. Generation-time validation (§1.1b step 3).** Two new paragraphs: the
generator parses `identity_epoch.json` (keys exactly the six
`IDENTITY_EPOCH_FIELDS`, values present and scalar — a number is admissible
because `sampling_interval_ms` is an integer — and `power_policy` exactly
`ac_high_power`), with all three refusal texts quoted, and parses
`t1_bindings.json` as an object only, because the ledger owns that block's
shape. The forcing problem is stated from the refusal message itself: the same
JSON used to fail at `d01`, after the gate, the reservation and 600 s of settle;
it now fails at the desk for the price of a re-written file. Second paragraph:
`MAX_DECLARED_SESSION_SLOTS` (99) as a desk-time ceiling, refused here so the
reservation cannot refuse it after the settle. A related paragraph was added at
the END of §1.1a (after the three-file table) on the generator's `CHAIN_ANCHORS`
anchor-text citation discipline, including that two anchors pin the dispatch
itself.

**4. §1.2 Δ.** The d12 worked example no longer idealises chain start = `t0`.
Δ is named and built as three enumerated components (driver gate work; chain
preflight — wrapper checks, input preflight, `--phase pre-reserve`; the session
reservation, after which `chain_start` is logged and the settle begins), then
every schedule time is restated as `t0 + Δ + <offset>`, and the chain's own
admission test collapses to **Δ ≤ 1320 s (22 min)**. The worked block now shows
three rows — Δ = 0 (labelled as the idealisation), Δ = 1320 (admitted, nothing
left), Δ = 1321 (d12 recorded unused) — and states how Δ is measured at harvest
(`chain_start` timestamp minus `t0`), which §2.1's log row now also carries. The
1320 s allocation is tied to Δ, and the 300 s pre-settle allowance is described
as a mandatory floor on the part of Δ the generator can reason about; the
courier allowance's separate 300 s (spent AFTER the window ends) was already
distinguished in the dead-man paragraph and is unchanged. §1.2 also gains the
registration's three-duration reconciliation stated together — 7680 s (128 min)
/ 7980 s (133 min) / 9000 s (150 min) — plus the note that 210 min is the
install span and not a window.

**5. §6 non-authorizations.** Substance unchanged; new clause 11 forbids
departing from three nights or twelve declared slots without the written rulings
the two tools require, naming both flag pairs and stating that the flags exist
so a ruled departure is RECORDED, not so a campaign can reshape itself around
what the nights produced. §4.3 also gains packet item 8, the pre-registration's
display-state known condition (recorded, edits no membership, licenses no
re-capture).

**§8 first-use table** gains seven rows: dispatch (writer-status), desk
recovery, written-ruling escape, Δ, known condition, anchor text — plus the
existing rows left intact. §7's fact table gains five rows (integration-head
chain dispatch and positivity guard; `chain_start` position; issuer arm-gate
fences and predecessor-read level screen; generator input parsing + slot ceiling
+ anchors; Δ ≤ 1320 corroborated by report 104 §7; the three-duration
reconciliation and the display-state known condition) and drops the stale
`R6_PREFLIGHT_LEVEL_SCREEN_S = …` citation.

## Diff hunk headers (`git diff -U0`)

```
@@ -15,14 +15,23 @@    changelog → revision 3
@@ -192,0 +202,35 @@   §0.3 check --preregistration
@@ -219,0 +264,20 @@   §0.5 pinned pre-registration digest
@@ -418,0 +483,18 @@   §1.1a anchor-text discipline
@@ -457,0 +540,35 @@   §1.1b step 3 input parsing + slot ceiling
@@ -555,0 +673,9 @@    §1.2 three durations reconciled
@@ -585,3 +711,32 @@   §1.2 Δ named and built
@@ -590,3 +745,13 @@   §1.2 Δ inequality
@@ -593,0 +759,17 @@   §1.2 three-row worked example + harvest measurement
@@ -672 +854 @@       §2.1 chain-log row
@@ -727 +909,53 @@     §2.4 dispatch table + desk recovery
@@ -741,3 +975,5 @@    §2.4 closing paragraph on open sessions
@@ -789,0 +1026 @@     §4.1 --preregistration
@@ -798,0 +1036,5 @@   §4.1 read the appended line
@@ -804,0 +1047 @@     §4.2 --preregistration-sha256
@@ -812,0 +1056,40 @@   §4.2 four fences + two written-ruling escapes
@@ -817,0 +1101,3 @@   §4.2 --predecessor-acceptance note
@@ -833,7 +1119,15 @@   §4.2 screen challenge read from predecessor
@@ -866,0 +1161,10 @@   §4.3 packet item 8 (known condition)
@@ -927 +1231 @@       §5 exit-64 positivity guard
@@ -931,2 +1235,5 @@    §5 dispatch rows
@@ -953,0 +1261 @@     §5 issuer arm-gate refusal row
@@ -990,0 +1299,8 @@   §6 clause 11
@@ -1001,0 +1318,2 @@   §7 chain dispatch rows
@@ -1008 +1326,2 @@     §7 issuer rows (level screen no longer a literal)
@@ -1012,0 +1332,4 @@   §7 generator / Δ / durations / display rows
@@ -1074,0 +1398,6 @@   §8 first-use rows
```

## Verification commands run this session

| # | Command | Result |
|---|---|---|
| V1 | `git -C /Users/edr/code/JouleWise-wt-epoch-integration show HEAD:scripts/night_chains/calibration_derivation_only.zsh` | dispatch read verbatim: `writer_rc == 0` → `disposition=valid`; `== 1` → `disposition=non-valid` with the comment "the session stays open and the next declared slot runs on the unchanged start-to-start cadence"; else `slot_refused slot=$slot rc=$writer_rc` + `exit $writer_rc`; positivity guard includes `SLOT_CAPTURE_BUDGET_S < 1` |
| V2 | `… show HEAD:scripts/issue_calibration_acceptance_generation.py` + targeted greps | `--preregistration-sha256 required=True`; `PREREGISTERED_NIGHT_COUNT = 3`, `PREREGISTERED_SLOTS_PER_NIGHT = 12` with `--nights-ruling` / `--slot-count-ruling`; `os_build` and `powermetrics` void refusals; `check --preregistration` appends one line and appends an error (rc unchanged in practice); level screen read from the predecessor artifact |
| V3 | `grep -n 'R6_PREFLIGHT_LEVEL_SCREEN_S' <issuer at integration HEAD>` | **0 hits** — the literal is gone; the runbook's old "script line 326" citation was stale and is replaced |
| V4 | `… show HEAD:scripts/gen_derivation_night.py` | `_validated_identity_epoch` (six exact fields, scalar rule, `power_policy == ac_high_power`), `_validated_json_object` for T1 bindings, `MAX_DECLARED_SESSION_SLOTS` ceiling refusal, `CHAIN_ANCHORS` incl. `    if (( writer_rc == 0 )); then` |
| V5 | `grep -n MAX_DECLARED_SESSION_SLOTS joulewise/calibration_ledger.py` | `:76` → `99` |
| V6 | `… show HEAD:configs/calibration/preregistration_d079_epoch_25g83_rev1.md` | 128/133/150 reconciliation and the 210-min install-span note at `:99–124`; display-state known condition at `:257–274`; sampler digest `b762e5bf…30c5` |
| V7 | report 104 §7 | independent derivation of the same 1320 s Δ tolerance ("up to 1320 s of launch delay … before d12 is dropped") |
| V8 | Markdown structural check (python: ragged-pipe-count scan over every contiguous table block; fence parity) | `ragged tables: []`, 38 fences (19 balanced blocks), 1412 lines |
| V9 | `git -C /Users/edr/code/JouleWise-wt-bk-96bfeca7 status --porcelain` | exactly ` M docs/process_traces/2026-09-10-activation-96bfeca7/99-derivation-night-runbook-draft.md` |

## Writing-standard notes

- First-use test run mechanically over the new terms. `dispatch` is glossed at
  its first appearance in the changelog and built in §2.4; its earlier §1.1a
  mention was rewritten to carry an inline gloss ("its branch on the exact
  status number a capture returns, built in full at §2.4") rather than a bare
  forward reference. `desk recovery`, `written-ruling escape`, `Δ`, `known
  condition` and `anchor text` are each built at first use and listed in §8.
- No number in the new text is asserted without its source: 1320 s is derived
  from the chain's own admission test in the text, 7980 from the generator's
  own message, 99 from the ledger constant, and the sampler digest is quoted.
- Two residual weaknesses the operator should know about, neither introduced
  here: (a) Δ is unmeasurable before the fact, so §1.2's rule is stated as an
  after-the-fact diagnostic; (b) `check --preregistration` reports through a
  printed line only — the runbook now says so twice (§0.3, §4.1) because an
  operator reading rc alone would draw the wrong conclusion.
