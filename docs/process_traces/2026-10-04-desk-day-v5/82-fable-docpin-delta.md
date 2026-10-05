FINAL PASS: PASS

Cold, delta-limited final pass on `dd46b1a7` (PR branch fix/2026-10-04-doctrine-pin-network-time-off) against the
previously passed head `3180dafb`. Seat: Fable 5.1, one session, foreground only, read-only on the checkout.
Scratch: /tmp/dd5-fable-dp2/ (`probe2.py`, `test_probe_real.py`, `probe_real_out.json`).

Ruling in one paragraph: merge. F1–F5 from the first pass are closed as asked. The current runbook and every
current pack still derive; the runbook edit keeps the line count at 2387 and `scripts/gen_g2_phase_d.py --check`
passes. I found no new way for a pack to freeze or arm that it should not, and no refusal of a correct current
pack. One thing must be said plainly so nobody over-reads the fix: the guard is much wider than before, but it
is still a text match, not an understanding of the instruction. It does NOT refuse "any" instruction that would
turn network time ON after a window; six rewordings still derive PASS through the real deriver (G1). None of
them lets a clock step reach a measurement, for the same reason as last time: the physical guard is the live OFF
receipt at ARM plus the arm step's final OFF and 600-second dwell, and this diff does not touch those.

---------------------------------------------------------------------------------------------------------

## Answers to the lead's questions

1. Are F1–F5 closed? — Yes, all five (table below).
2. Does the guard refuse any runbook instruction that would turn network time ON after a window, without
   refusing the current doctrine? — The current doctrine derives (real deriver, committed test green). All 16
   lines from my first probe now refuse. "Any" is not true: see G1.
3. Any new way to freeze or arm that should not? — No. One small loosening against the pre-PR parent
   `85d67b12`, disclosed in the contract (G3).
4. Any refusal of a correct current pack? — No. All nine committed plan trees and the three v5 generators clear
   both new pack-side checks. Future benign edits can be refused (G2); that fails closed.
5. `scripts/gen_g2_phase_d.py --check` — `PASS generated Phase D matches pinned runbook bytes`, exit 0.
   `git status --porcelain` is empty afterwards (the check mode only reads).

---------------------------------------------------------------------------------------------------------

## F1–F5 closure

About the probe: `/tmp/dd5-fable-dp/probe.py` carries its own copy of the OLD regex, so run verbatim it
reproduces the old table on any checkout (I ran it: 13 of 16 still "PASS", which says nothing about this head).
I therefore rewrote it as `/tmp/dd5-fable-dp2/probe2.py`, which calls the committed `_extract_section`,
`_doctrine_sentences`, allow-list and three regexes from this checkout, with the same inputs. Its verdicts
matched the real `_derive_doctrine_pin` on every case I ran through both (11 of 11).

| Finding | Status | Evidence at `dd46b1a7` |
|---|---|---|
| F1 restore guard was a phrase list | CLOSED as asked; residual in G1 | 16 of 16 original restore lines REFUSE (was 3 of 16). The three weakening edits that used to pass (delete "No ON command is permitted after the first capture of a window."; "may finish with ON"; manual ON "at any time") all REFUSE, because those sentences are now required (`joulewise/arm_readiness_evidence.py:936-950`). The negating prefix "It is no longer required that Network time stays OFF…" REFUSES, because a required sentence must now be a whole sentence, not a substring (`:951`). A restore line appended to §11 or §12 REFUSES (`:887`, `:957-967`). A pure re-wrap still PASSES. |
| F2 two-backup check was dropped | CLOSED | Restored at `:898-926`. Committed test refuses 0, 1 and 3 backup commands and a required count of 0, 1, 3, `"2"`, `null`, `true`. |
| F3 the row never inspected commands | CLOSED | `:927-932` refuses if the serialized launch recipe plus stage graph contains `setusingnetworktime`, `systemsetup`, `sntp` or `timed` (case-insensitive). Committed test covers both locations and two key spellings. |
| F4 operator card still said restore ON | CLOSED | `docs/process/rehearsal-operator-card.md:121-130` now opens §11 with "SUPERSEDED — do not turn network time back ON", states the reason and the current rule, and labels the old text as history. |
| F5 orphaned fixture | CLOSED | `tests/fixtures/historical_clock_restore_5a.md` is used by `test_retired_fixture_doctrine_refuses` (`tests/test_arm_readiness_evidence.py:950-956`). |

---------------------------------------------------------------------------------------------------------

## New findings on this delta

### G1 — MEDIUM (non-blocking): the guard is still lexical; six restore instructions derive PASS
File: `joulewise/arm_readiness_evidence.py:841-866` (allow-list and regexes), `:957-967` (the scan).

How the scan decides: it cuts each scanned section into sentences and code lines. A sentence is "sensitive" if
it contains a clock word (`network time`, `time sync…`, `setusingnetworktime`, `systemsetup`, `sntp`, `timed`)
AND an enabling word (`on`, `enable`, `re-enable`, `restore`, `resume` and their endings), or one of three
fixed shapes (`restore … on`, `undo … off`, `on command`). A sensitive sentence refuses unless it is in §5A and
is byte-equal to one of seven allow-listed sentences.

Each line below was added to the committed runbook with all ten required sentences left in place, then run
through the REAL `_derive_doctrine_pin` via the committed fixture (`test_probe_real.py`; output in
`probe_real_out.json`). All six derive PASS:

| Added instruction | Why it passes |
|---|---|
| §5A: "After both backups, run:" followed by a new fenced block holding `/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime on` | The lead-in has no clock word. The command line is on the allow-list, and the allow-list tests identity only, not position or count. A second copy anywhere in §5A is accepted. |
| §5A: "After both backups, re-enable NTP." | `NTP` is not a clock word (only `sntp` is). |
| §5A: "After the verdict, switch automatic date and time back on." | No clock word. |
| §5A: "After the verdict, run `sudo sntp -sS time.apple.com`." | Clock word present, but no enabling word. A one-shot sync command needs no "on". |
| §9 (the whole-window verdict section): "After the verdict, turn network time back ON." | §1–§4, §7–§9, §13, §14 are not scanned. The same line REFUSES in §5, §5A, §5B, §5C, §6, §10, §11, §12. |
| §5A: "After both backups, turn network time", blank line, "back on." | The paragraph break puts the clock word and the enabling word in different blocks. |

The first row is the one worth fixing, because it is the least contrived and the contract speaks to it:
`docs/contracts/arm_readiness_network_time_policy.md:60-61` says the cold-credential command line "is allowed
only together with the required between-windows, finishes-OFF sentence". That is true only as co-presence in
the section; nothing ties the command line to that sentence.

Why this does not block the merge:
- The contract now says what the check is: "exact text checks; the deriver does not interpret synonyms"
  (`:19`). The over-claim I objected to in F1 is gone, apart from the one sentence quoted above.
- Each of these needs a self-contradictory runbook merged at origin/main: §5A would say "do not restore ON",
  "No ON command is permitted after the first capture of a window" and the opposite at once. The realistic
  drift, the retired §5A text returning through a bad merge, is refused (committed fixture test).
- The physical guard is unchanged: `clock.network_time_off` still needs a live OFF receipt at ARM, and the arm
  step ends by commanding OFF and then waits out the 600-second dwell before any capture.

Ask (follow-up, small; none of it needed before merge):
1. Require every allow-listed sentence to occur exactly once in §5A. Today each occurs exactly once (I
   counted all seven), so this refuses nothing current and closes the first row.
2. Scan every `## ` section, not eight. A whole-runbook scan of today's text flags exactly one benign sentence,
   in §14: "The generic admission preserves network-time OFF, its 600 s settle on both clocks, the overlapping
   clean dwell, and the physical night gate." (clock word plus the preposition "on"). Reword or allow-list it.
3. Add `ntp` as a clock word (no governed section uses it today), and treat a sentence holding `sntp` or
   `-setusingnetworktime` as sensitive without needing an enabling word. The second half needs three more §5A
   allow-list entries first: the `…-setusingnetworktime off` code line, the sentence naming
   `systemsetup -getusingnetworktime` and `systemsetup -setusingnetworktime`, and "A password prompt, any
   nonzero exit, or any other permitted systemsetup argv…".

### G2 — LOW: benign future edits are refused, and the refusal does not say which sentence
Confirmed through the real deriver (all REFUSE):
- §12: "The verdict depends on network time staying OFF." ("depends **on**" next to "network time").
- §10: "Do not turn network time on to fix a failed anchor." (a prohibition; a negation outside the allow-list
  is refused by design, contract `:50`).
- §11: "Verify you can restore the archive on the second destination." (the `restore … on` shape needs no
  clock word at all, so any backup-restore sentence containing the preposition "on" trips it).
- Pack side: an argv `--skip-untimed-warmup` refuses with "contains a clock-control command", because the four
  tokens are matched as substrings of the serialized recipe (`:928-932`). `timed` is inside `untimed`.

Also fragile, though passing today: the runbook's own new line 640 names `clock.network_time_policy` and
`clock.restore_recipe` and passes only because the `_policy` / `_recipe` suffixes defeat the word-boundary
match; written as prose ("the network time policy row replaces the restore row … from §5A") it would not.

All of this fails closed: the cost is a refused freeze and a runbook reword, never a wrong number. No current
pack or text is affected (evidence under "Current packs" below). Two cheap improvements: put the offending
sentence in the refusal text (`:965-967` names only the section), and match `timed` / `sntp` on word
boundaries in the pack scan.

### G3 — LOW: one loosening against the pre-PR parent, disclosed
At `85d67b12` a pack whose `closeout_attachments.backup_requirements` existed but had no
`required_successful_backups` key was refused (`None == 2` is false). At `dd46b1a7` the absent key defaults to
2 and derives (`:913-915`; committed test asserts it; contract `:65-67` states it). The stage graph must still
hold exactly two backup commands, so this cannot admit a one-backup pack. No committed pack has that shape:
six floor packs carry the integer 2, three contrast packs have no `backup_requirements` at all (accepted before
and after).

### G4 — NIT
- The allow-list entry "D-127 authorizes only the exact off and on writes; …" (`:842-843`) can never be
  consulted: that sentence holds no clock word, so the scan never marks it sensitive. Harmless, because the
  same sentence is on the required list.
- `desk.arming_procedure.v1.runbook_sections` still lists six sections while eight hashes are pinned. The
  contract says so (`:37-38`) and the predicate in `joulewise/arm_readiness.py:1002` expects six, so this is
  consistent; a reader of the fact alone will not learn that §11 and §12 are bound.

---------------------------------------------------------------------------------------------------------

## Evidence for the clean answers

### Current doctrine derives
- Real deriver on the committed runbook: `test_current_runbook_derives_new_fact_and_rederives_at_arm` and
  `test_pure_rewrap_passes` green. The first also re-derives at ARM with the eight-hash pin material.
- §5A holds six sensitive sentences; all six are allow-listed. Each of the seven allow-list entries occurs
  exactly once. The other seven scanned sections hold zero sensitive sentences.
- No other code reads `pack_pin_material` or `runbook_section_sha256`
  (`git grep` over `joulewise` and `scripts`: only the deriver itself), so the two extra hashes cannot break a
  consumer.

### Current packs
Applied the two pack-side checks to every committed `plan_tree.json` under `configs/campaigns`:

| Packs | Clock-token hits in launch recipe + stage graph | Backup commands | Required count |
|---|---|---|---|
| contrast v1, v2, v3 | 0 | 2 | no `backup_requirements` (accepted) |
| floor 1p5b v1–v3, floor 7b v1–v3 | 0 | 2 | 2 |

The three v5 packs have a generator and no committed plan tree. In all three `generate_configs.py` files and in
`joulewise/campaign_generator_core.py`, a case-insensitive search for `timed`, `sntp`, `systemsetup` and
`networktime` returns nothing. Each generator emits exactly two `backup` commands under one stage's
`launch.commands` (floor: `beta-backup.claim` / `.bound`, with `required_successful_backups: 2`; contrast:
`gamma-backup.claim` / `.bound`, no `backup_requirements`). I did not generate the v5 trees; the doctrine test
fixture named `d117_floor_qwen3-1p7b_v5` is a synthetic tree, not generator output.

### Runbook line count and the G2 anchors
- `wc -l docs/phase_2/window_runbook.md`: 2387 at `dd46b1a7`, 2387 at the pre-PR parent `85d67b12`, 2391 at
  `3180dafb`. Against `85d67b12` the runbook diff is a single hunk `@@ -640,2 +640,2 @@`: two lines replaced
  by two, so no line after 641 moves.
- `scripts/gen_g2_phase_d.py --check`: PASS, exit 0.
- The new lines 640–641 carry the same statements as the six-line paragraph they replace and do not trip the
  scan (but see the fragility note in G2).

---------------------------------------------------------------------------------------------------------

## Test status

Run from the detached checkout with `/Users/edr/code/JouleWise/.venv/bin/python -B -m pytest -q -p no:cacheprovider`, TMPDIR=/tmp/dd5-fable-dp2.

GREEN (completed):
- `tests/test_arm_readiness_evidence.py::NetworkTimePolicyDoctrineTests` (all seven) plus
  `tests/test_receipt_histsem.py::…::test_archival_restore_fact_keeps_its_predicate_after_live_replacement`:
  **8 passed, 63 subtests passed in 83.78 s**.
- All of `tests/test_arm_readiness_registry.py`, the two 35-row tests in `tests/test_arm_readiness_schemas.py`,
  and `tests/test_arm_readiness_evidence_author.py -k "arm_only_resync_doctrine or first_authoring"`:
  **16 passed, 220 subtests passed in 63.59 s**.
- My scratch matrix through the real deriver (`/tmp/dd5-fable-dp2/test_probe_real.py`): ran to completion, 11
  verdicts recorded in `probe_real_out.json` (it records, it does not assert).

NOT RUN (said plainly): the whole files `tests/test_arm_readiness_evidence.py`,
`tests/test_arm_readiness_evidence_author.py`, `tests/test_arm_readiness_dry_run.py`,
`tests/test_arm_readiness_schemas.py` and `tests/test_receipt_histsem.py` beyond the selections above, and the
lifecycle/integration files. The restored two-backup check and the new token scan run for every fixture that
authors a DOCTRINE_PIN receipt, so those whole-file results should come from the seat or CI before merge. I did
not generate v5 plan trees and ran no measurement, clock or privileged command.

Reproduce the probe: `PYTHONPATH=<checkout> python -B /tmp/dd5-fable-dp2/probe2.py` (in memory only), and
`PYTHONPATH=<checkout> python -B -m pytest -q -p no:cacheprovider --rootdir=<checkout> /tmp/dd5-fable-dp2/test_probe_real.py -k test_probe_real_matrix`.
