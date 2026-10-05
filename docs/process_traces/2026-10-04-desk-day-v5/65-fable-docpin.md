FINAL PASS: PASS

Cold final pass on `3180dafb` (PR branch fix/2026-10-04-doctrine-pin-network-time-off) against parent `85d67b12`.
Seat: Fable 5.1, one session, read-only. Scratch: /tmp/dd5-fable-dp/ (probe script `probe.py`).

Ruling in one paragraph: merge. The change does what it says: the live v2 registry row is renamed, the
deriver refuses whenever any of the five governing §5A sentences is absent, the archival v1 registry, all
nine historical packs and the retired predicate are byte-identical, and I found no path by which the live
system turns network time ON after a window. Two MEDIUM findings are real and should be closed in a
follow-up, but neither lets a clock step reach a measurement: the "rejects contradictory restore
instructions" half of the check is a narrow phrase list, not a general guard (F1), and the deriver
silently stopped checking that the pack carries exactly two backup commands (F2).

TEST STATUS: see the last section of this file.

---------------------------------------------------------------------------------------------------------

## Answers to the four questions

1. PASS exactly when §5A states the doctrine? — Half yes. The "required" half is strict and fail-closed;
   the "refuse a contradictory restore" half is leaky (F1).
2. Archival replay unchanged? — Yes. No historical byte is rewritten (evidence under Q2 below).
3. Does anything else that admits or refuses a window change? — Yes, one thing: the pack-side two-backup
   check left the deriver (F2). Nothing else.
4. Can a freeze PASS while the live system would restore network time? — Not today. No stage-graph command
   and no live script turns network time ON after a window (evidence under Q4 below). The deriver itself
   does not look at stage-graph commands, so this rests on the generator and the scripts, not on the row (F3).

---------------------------------------------------------------------------------------------------------

## Findings

### F1 — MEDIUM (non-blocking): the restore guard is a phrase list; most rewordings pass
File: `joulewise/arm_readiness_evidence.py:847-856`; claim at `docs/contracts/arm_readiness_network_time_policy.md:20-22`.

How the check works: the deriver flattens §5A (strips `*` and backticks, collapses whitespace), then
(a) requires five literal sentences to be present, and (b) searches the lower-cased text for a small set
of restore phrasings and refuses on a hit.

Part (a) is sound. Removing or rewording any of the five sentences refuses (probe: 6 of 6 clause removals
REFUSE; a pure re-wrap of the bullet still PASSES, as it should). It is brittle in the safe direction: the
harmless rewording "Network time remains OFF" also refuses.

Part (b) is not what the contract says it is. I appended one extra checklist line to the end of the
current §5A, leaving all five required sentences in place, and ran the committed regex:

| Added line | Result |
|---|---|
| After both backups, restore ON. | REFUSE |
| After the verdict, turn on network time. | REFUSE |
| After each window, restore network time. | REFUSE |
| After both backups, turn network time back on. | **PASS** |
| After the whole-window verdict, enable network time. | **PASS** |
| After the whole-window verdict and both backups, set network time ON. | **PASS** |
| Once the window closes, run `/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime on`. | **PASS** |
| When the window is complete, switch automatic network time back on and verify it. | **PASS** |
| After the second backup, reenable network time. | **PASS** |
| After the verdict, network time is re-enabled. | **PASS** |
| At close-out, network time goes back ON. | **PASS** |
| After the backups, resume network time synchronisation. | **PASS** |
| Following the verdict, re-enable automatic time sync. | **PASS** |
| After the window, undo the OFF toggle. | **PASS** |
| After the verdict. Then enable network time. | **PASS** |
| Restore the network-time setting once both backups verify. | **PASS** |

13 of 16 contradictory restore lines derive PASS. Why: the first alternative only matches the verbs
`restore` / `re-enable` followed directly by `it`, `on` or `network time`; the third only fires when the
sentence starts its clause with the exact anchors `after (the) window|capture|verdict|(both) backups` or
`close-out` and then contains `enable|re-enable|restore|turn on` before the next full stop. "the
whole-window verdict", "the second backup", "back on", "set ... ON" and a literal `systemsetup ... on`
command all fall outside it.

Three further edits that weaken the doctrine without adding a restore line also PASS, because the
sentences they touch are not among the five required ones:
- deleting "No ON command is permitted after the first capture of a window." (runbook :614-615);
- changing "the arm step uses ON only for a needed resync and finishes with OFF" to "...may finish with ON" (:577);
- changing the manual ON from "between windows only" to "at any time, including during a window" (:629-630).
The first of these is the one sentence in §5A that speaks directly to the physical hazard (an ON command
while samples are being timestamped), and it is not pinned.

Also: only §5A is read. A restore step added to §11/§12 (the back-up and close-out sections, where an
operator would actually look for one) derives PASS.

Why this does not block the merge:
- It needs a self-contradictory runbook (the text would say "do not restore ON" and "restore" at once),
  committed and merged at origin/main; the §5A hash is then pinned in the pack and re-derived at ARM, so the
  text cannot drift between freeze and arm.
- The one drift that is actually likely — the retired §5A text coming back through a bad merge — is refused
  twice over (required sentences missing; "re-enable it" and "the restore comes last" both hit).
- The physical guard is elsewhere and untouched: `clock.network_time_off` still needs a live OFF receipt at
  ARM, and every arm step ends by commanding OFF (`scripts/capture_t0_step.py:762-766`, in a `finally`)
  followed by the ≥600 s dwell. A stray ON between windows is undone before the next capture.

Ask (follow-up, small): either (i) change the contract sentence to say what is true — "rejects the retired
restore phrasings" — or (ii) make the guard structural instead of lexical: require that every occurrence
of the token `on` adjacent to "network time" / `-setusingnetworktime` in §5A lies inside an allow-listed
sentence (the sudoers bytes, the cold-credential exercise, the arm-step resync sentence, the supervised
between-windows sentence). Also add "No ON command is permitted after the first capture of a window." to
the required list. The test at `tests/test_arm_readiness_evidence.py:877-884` only exercises three phrasings
the regex was written for, which is why it did not show this.

### F2 — MEDIUM (non-blocking): the deriver no longer checks the pack's two backups
File: `joulewise/arm_readiness_evidence.py` (removed lines 837-859 of the parent; nothing replaces them).

Before: DOCTRINE_PIN refused unless the frozen stage graph held exactly two commands of kind `backup` and
`closeout_attachments.backup_requirements.required_successful_backups` was 2 (or absent). Because one
derivation feeds both rows, that refusal also took down `desk.arming_procedure`.
After: neither is read. `git grep -nE "required_successful_backups|backup_requirements|command_kind" -- joulewise scripts`
returns nothing at `3180dafb`; the only remaining readers are test fixtures. A pack whose generator emits
one backup command, or three, now freezes where it used to refuse.

This is the one change in what admits a window beyond the renamed row, and neither the contract nor the
runbook paragraph mentions it. The new facts still say "...and both backups" in prose, but nothing ties
"both" to the pack any more.

What still stands: PACK_AUTHENTICATION replays the committed generator, so a hand-edited plan tree is
refused (`tests/test_arm_readiness_evidence_packauth.py:763-775`); the ARM-time row
`t0.storage_backup_capacity` still requires two distinct writable destinations
(`joulewise/arm_readiness.py:8517-8531`); all nine committed plan trees carry exactly two backup commands.
Backups protect custody after the window, not the truth of a measured number, so I do not hold the merge.

Ask (follow-up): put the two-backup count back as part of `desk.arming_procedure` (about ten lines), or
record its removal in the contract with the reason.

### F3 — LOW (pre-existing, not a regression): the row never inspects commands
The policy fact is derived from prose alone. `frozen_launch_recipe_sha256` binds the launch recipe and stage
graph by hash, but nothing rejects a stage command that would run an ON toggle; the D-127 sudoers fragment
makes `sudo -n systemsetup -setusingnetworktime on` passwordless, so such a command would succeed. The old
deriver did not check this either (under the old doctrine the restore was a manual step). Today there is
nothing to catch — see Q4 evidence — but the fact name `restore_on_after_window: false` reads as stronger
than "§5A does not say to". A cheap closing check: refuse if any `argv_template` in the stage graph or launch
recipe contains `setusingnetworktime` or `systemsetup`.

### F4 — LOW (pre-existing, outside the diff): a live operator card still says restore ON
`docs/process/rehearsal-operator-card.md:119-125`, section "11. Restore and reset for retry": "Restore
network time immediately after the final step, including a refusal; expected final line is
`Network Time: On`", followed by the literal ON command. Last touched 2026-08-28, before the permanent-OFF
ruling. It is a dress-rehearsal card pinned to an old v2 pack, and the next arm step would command OFF again,
but it is the one remaining instruction in a non-archival doc that contradicts §5A, and the doctrine row
cannot see it. Fix in a docs follow-up.

### F5 — NIT: orphaned fixture
`tests/fixtures/historical_clock_restore_5a.md` lost both of its users in this diff
(`tests/test_arm_readiness_dry_run.py`, `tests/test_arm_readiness_evidence_author.py`) and is now referenced
by nothing. Either delete it or use it in `NetworkTimePolicyDoctrineTests` as the "retired doctrine refuses"
case, which would be a better negative test than the three hand-written lines.

---------------------------------------------------------------------------------------------------------

## Evidence for the questions that came back clean

### Q2 — archival replay
- `git diff --quiet 85d67b12 3180dafb -- configs/arm_readiness/d117_row_registry_v1.json configs/campaigns tests/fixtures`
  exits 0: the v1 registry, every campaign pack (receipts, sources, evidence, plan trees) and all fixtures
  are byte-identical. The two histsem pinset files are not in the diff either (14 files changed, listed by
  `git diff --name-status`; none under `configs/` except the v2 registry).
- `joulewise/arm_readiness.py`: the diff removes zero lines (`grep -c '^-[^-]'` = 0). The retired
  `clock.restore_recipe.v1` content requirements (:974-978) and evidence-kind mapping (:1158) are intact; the
  new predicate is added beside them.
- All nine historical freeze receipts name `configs/arm_readiness/d117_row_registry_v1.json` as their
  registry (9 of 9), so none of them resolves through the edited v2 file.
- The changed deriver is reached only through `_DERIVERS` at authoring time and `_r1_rederive_at_arm`
  (`arm_readiness_evidence.py:2731`, called from `arm_readiness.py:6458`), i.e. for new v2-lifecycle receipts.
  The historical-semantics path (`arm_readiness.py:3875`, `_histsem_rederive_pack_authentication`) re-derives
  pack authentication only, not the doctrine pin.

### Q3 — other admission changes
Registry diff: row id, predicate id, the three profile lists and the lifecycle row policy change name only;
phase (`FREEZE_AND_ARM`), applicability (`ALWAYS`), evidence kind (`DOCTRINE_PIN`) and freshness policy
(`r1.re_derivable.v1`) are unchanged. `clock.network_time_off` / `CLOCK_PROBE` is untouched. The only
behavioural change outside the row is F2.

### Q4 — would the live system restore network time?
- Stage-graph command kinds across all nine committed plan trees: `backup`, `bound_derivation`,
  `bracket_reservation`, `calibration_capture`, `campaign_collection`, `whole_window_verdict`. No clock kind.
  No plan tree contains `setusingnetworktime`, `quiet_window_clock`, `network_time` or `sntp`.
- The three v5 packs have no committed plan tree yet (generator only); their `generate_configs.py` files
  contain no `networktime` / `systemsetup` / `sntp` string (0 matches each).
- The only code in `joulewise/` or `scripts/` that issues the ON vector is the arm step's resync,
  `scripts/capture_t0_step.py:757`, which requires empty capture roots (:737-739) and is wrapped in a
  `finally` that commands OFF and writes the write-once receipt (:762-766).
- `scripts/quiet_window_clock.sh` exposes `status` and `disable` only (:140-142); its one write is `off` (:96).
  `joulewise/network_time_off.py:11` defines the OFF argv only.

---------------------------------------------------------------------------------------------------------

## Test status

Run from the detached checkout with `/Users/edr/code/JouleWise/.venv/bin/python -B -m pytest -q -p no:cacheprovider`, TMPDIR=/tmp/dd5-fable-dp.

GREEN (completed):
- `tests/test_arm_readiness_evidence.py::NetworkTimePolicyDoctrineTests` (all three),
  `tests/test_receipt_histsem.py::...::test_archival_restore_fact_keeps_its_predicate_after_live_replacement`,
  `tests/test_arm_readiness_schemas.py::...::test_live_policy_replaces_restore_in_all_35_row_profiles`,
  `tests/test_arm_readiness_schemas.py::...::test_all_35_contract_predicates_require_named_content_and_admissible_sources`,
  and all of `tests/test_arm_readiness_registry.py`: **12 passed, 226 subtests passed in 64.77 s**.
- `tests/test_arm_readiness_evidence_author.py -k "arm_only_resync_doctrine or first_authoring"`:
  **2 passed, 22 deselected in 11.95 s**.

NOT COMPLETED (said plainly): the broad run of the four whole files
(`test_arm_readiness_evidence.py`, `test_arm_readiness_registry.py`, `test_arm_readiness_schemas.py`,
`test_receipt_histsem.py`, with `-x`) was still running after 22 minutes on a machine shared with several
other seats' pytest and codex runs, and I stopped waiting at the budget. It was started with `-x` and had not
exited, so no test had failed up to that point (its progress output shows it a little past 67 % with dots
and one skip only when I stopped it at 22:32), but it never printed a final line and I do not claim it green.
`tests/test_arm_readiness_dry_run.py` and the rest of `tests/test_arm_readiness_evidence_author.py` were not
run by me. The PASS above rests on the code reading, the regex probe and the targeted tests; whoever merges
should have the whole-file results for these six test files from the seat or CI.

The regex probe is reproducible: `PYTHONPATH=<checkout> python -B /tmp/dd5-fable-dp/probe.py` (it imports
`_extract_section` from the checkout and applies the committed sentence list and pattern to mutated copies
of the committed runbook, in memory only).
