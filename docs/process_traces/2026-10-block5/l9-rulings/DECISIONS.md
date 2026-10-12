# Lane L9: what was ruled and decided before code (2026-10-12)

Magistrate activation 658a40bd (Opus 5.5, headless). This file binds every stage brief of the lane together
with the design (`/Users/edr/night-archive/gate-prune/wave-1007b/l9/L9_DESIGN.md`, sha256 `3465acf9…2e7d`).
Where this file and the design differ, this file wins. Where a cold ruling and this file differ, the ruling
wins. No measured value was read by this session or by any seat; each seat's report says so.

## 1. Cold rulings (the judge decides; nothing here restates them in full)

- `RULING.md` (sha256 `1dff6537…2860`), a cold Fable 5.1 session, last line `RULING: ALL RULED`. In one line each:
  - **J1**: a stored condition is set aside only when a record of the harvest archive has decided the same
    thing again. Member conditions are set aside at member level; a member the verdict row failed and the
    exclusion function kept is a tooling stop (`member_code_on_kept_unit`). The consumer's own re-derivation of
    a removed member's admission is recorded, not refused (item 9; the design had missed that this path
    refuses the window). `admitted` is redefined on a block-5 root with a context (item 11).
  - **J2**: a reference whose config is not the registered one is lost. On block 5 the pinned harvest stays
    and a tripwire enforces it; if it fires, that window alone is harvested again at a new pin after a cold gate.
  - **J3**: the harvest is not changed; tripwire `kept_member_outside_verdict_membership`.
  - **J4**: no analysed window is harvested again unless a tripwire fires; a three-way parity test on dropped
    references; items 5 to 9 say what happens after a forced re-harvest, including a pack left with no
    analysed attempt.
  - **J5**: the minted floor carries the floor window's whole gross drift allowance (the code stands; plan
    lines 133 to 135 are corrected by addendum).
  - **J6**: each window under its own sensitivity bound; both floor forms; D re-derived.
  - **J7**: the archived ledger copy is bound by its line in `sources/SHA256SUMS`, pinned by the dry run's census.
  - **J8**: reading (i).
  - **P9**: the pinned analysis program may read the three restricted `derived/` files before the release
    event as the blind dry run; item 2 lists what may reach an unrestricted record. No seat opens them.
  - **Z1**: on an analysed window, a harvest checkout that was not clean is a refusal
    (`harvest_checkout_not_clean`) and a cold gate. This overrides the design's T6 for analysed windows.
  - **Z2**: stage S5 must make the leave-one-out magnitude threshold read the floor on a block-5 root, or
    refuse a manifest that carries a numeric `mde`.
- `ERRATUM-RULING.md` (the one erratum; charge `ERRATUM-CHARGE.md`): X1, a reference the exclusion function
  removed that the screen still used; X2, the two adapter-continuity sites; X3, the stored-bracket replay on a
  block-5 row. Its outcome is recorded in section 4 when it exists. Stage S3 is not briefed before it.

## 2. The two-seat consult (design item O2; brief `CONSULT-BRIEF.md`; reports `seat-sol.md`, `seat-fable.md`)

Both seats were blind to each other and to the judge. Dispositions:

| Finding | Seat | Disposition |
|---|---|---|
| A stored-bracket replay that requires a positive stored allowance refuses every block-5 row | Sol F1 (executed probe); Fable Q1, catalog path | To the erratum, X3 |
| A reference the exclusion function removed can still be a survivor of the screen and set the allowance | Sol F2 (executed probe); Fable Q1 (constructed row) | To the erratum, X1. The two seats reached it through different codes |
| The clause "or is a NEG-8 reference or spare" is wrong for the twelve member reasons that name an included member | Fable Q1 | To the erratum, X1 (c) |
| The adapter-continuity mismatch (near `whole_window.py` 5416) is provenance; only the stored decision (near 6920) is disclosed-only | Fable Q1 | To the erratum, X2 |
| One consumption session per context; the context and `member_scope` never change after a session caches an admit; the sensitivity pass builds a new session per context | both | Adopted; requirement on S3 and S9, with a test |
| The likeliest silent wrong number: every timing bound computed under the pre-capture bound, or another window's bound, by every consumer alike | both, independently (Q4) | Adopted, section 3 item B1 |
| O6 (unreadable historical capture) | both: safe with conditions | Adopted with the conditions, section 3 item O6 |
| O13 (load-correlated sensitivity line) | both: the contrast form is defensible; "no floor line" is a reading, not settled text | Adopted with additions, section 3 item O13 |

## 3. The orchestrator's decisions (design section 8.3)

- **O1**: adopted. The lane's first commit merges the pinned harvest program `b039c0257` (done: `3a745e8dc`
  on `lane/2026-10-07-l9-analysis`; the four pinned harvest files are identical to the pin's blobs), and the
  lane merges to main through the six merge keys. Collection is closed, so no window can arm from these bytes;
  the measurement clone and the desk root are not touched.
- **O3, O4, O5, O7, O8, O9, O10, O11, O12, O14, O15**: adopted as the design recommends.
- **O6**: adopted with these conditions. Only the artifact-aware outcomes `unreadable`, `absent` and
  `absent_or_unreachable` of a historical capture become a recorded flag; `changed` (a present file whose
  digest differs) still stops. The chain, the pin and the baseline-in-chain test stay. The window's own two
  captures are verified by bytes. No observation is dropped from B_max or from any trigger count because its
  file is unreadable: those are computed from ledger rows. A test asserts that the input census lists no file
  under a historical capture's locator. The flag carries the capture ids and is compared with the harvest's
  `derived/historical-custody.json`.
- **O13**: adopted with three additions. The line prints the restored count per stratum (or per contrast) and
  the code families. When the trigger fires and no unit is restored (each was also removed by another code),
  the line prints "no unit restored". For a contrast the line is steps 1 to 4 of plan section 7.1 only (the
  battery-assist precedent, plan lines 558 to 561), and the addendum says so and why. "No line for floor
  cells" is recorded in the addendum as a reading; it changes no number.
- **O16**: decided when stage S0 reports which files the hazard census scans.
- **B1 (new; from both seats' Q4)**: the operative bound gets an owner. Every block-5 consumption session is
  built with the maximum-bracket semantics; its operative bound is the window bracket's `b_fiducial_s` and
  nothing else. Every synthetic window has a post-capture bound different from its pre-capture bound, and the
  three windows of a fixture set have three different operative bounds. The extractor, the mint and the issuer
  refuse a kept member whose consumption provenance lacks the operative bound or carries one different from
  the window bracket's (`operative_bound_not_the_window_bracket`). Stage S8 asserts that one kept member's
  issued timing bound equals an independent reduction under the operative bound and differs from the stored
  summary's. One synthetic fixture goes through the production (non-mock) dispatch, because the mock path
  serves stored summaries without re-reduction. Mutations that must fail: the pre-capture bound substituted;
  another window's bound substituted.

## 4. The erratum's outcome

`ERRATUM-RULING.md` (sha256 `a0336dd9…3f37`), a second cold Fable 5.1 session, last line `RULING: ALL RULED`.

- **X1**: a reference the exclusion function removed may not be a survivor of the screen. The sealed text is
  silent on the general case; the ruling fills the silence by the registration's own test. The pinned
  harvests do not apply it (twenty member-removing codes are outside the loss list at both pins), so the
  analysis checks it by structure: `excluded_reference_in_screen` fires when a window's survivor set and its
  excluded references intersect, whatever the code. It subsumes J2's tripwire. The survivor set is computed
  (basis references less both loss lists) and cross-checked against the recorded counts
  (`survivor_set_count_mismatch`). If the check fires: that window alone is harvested again at a new pin after
  a cold gate, J4 items 5 to 9. J1 item 5 is replaced (a stored member condition naming a reference is answered
  only when that reference is not a survivor) and item 9 amended to match.
- **X2**: the continuity record that the bundles do not reproduce stays a refusal
  (`adapter_continuity_record_mismatch`); only the stored decision word is disclosed and not refused.
- **X3**: on a block-5 root with a context the stored-bracket replay authenticates the endpoint fields that
  do not depend on the bound and takes the allowance, decision and freshness from the authenticated allowance
  record and the withheld re-screen bracket. The consumer never re-runs the survivor screen. On the Erratum 2
  catalog path the authenticated catalog manifests feed the core re-derivation; the judge found by execution
  that an empty manifest list makes today's re-derivation return no reason at all (a silent skip), so it
  becomes the stop `core_rederivation_sources_empty`. Main's evaluator lacks four keyword arguments the
  pinned one has; the lane's base merge already brings the pinned file, so stage S3 starts from it.

Stage S3's brief carries `RULING.md` section J1 as amended by `ERRATUM-RULING.md`, and both files whole.
The seal-record addendum (stage S11) carries every "(d)" sentence of both rulings.

## 5. Gates that ran in this phase, and what each caught that touches a number

| Gate | Caught |
|---|---|
| Cold judge on J1 to J8 | The validator would still refuse every window with a removed member whose admission failed (J1 item 9); the leave-one-out threshold can read a manifest field instead of the floor (Z2); three sealed sentences false of the code, one of which (plan 133 to 135) would have changed every floor had the code been changed to match |
| The one erratum | An empty source list silently skips the consumer's whole admission re-derivation on the catalog path (found by execution) |
| Two-seat consult | A reference the exclusion function removed can set a drift allowance (both seats); the stored-bracket replay refuses every row (Sol); the operative bound has no owner (both) |
