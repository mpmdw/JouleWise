# Opus pairing refuter on cold-gate ruling 10 (packet 69) — Opus 5, read-only, independent answers first, 2026-09-17 12:33–12:48 PDT

Verbatim report:

# Opus pairing refuter — cold-gate packet 69 (contract lens)

Trust anchors I verified myself: charter sha256 `099de884…c95d81` matches; all six exhibit digests match the manifest; packet sha256 `a77c4ab3eb64c1f4da9f344a2fc247d18e1798be1c0c44e9fb59dc8f100410b0`. Exhibit B's embedded chain diff is **byte-identical** to `git diff 3015cb39..a4d530cd -- scripts/night_chains/calibration_derivation_only.zsh` (132 lines, compared programmatically), and all four chain digests in its table reproduce. Probes run: `gen_derivation_night.py --check` → `PASS`, rc 0; generator literal diff between `3015cb39` and `a4d530cd`; chain read at both heads; writer/gate/driver call-site reads; three parser probes against candidate revision texts.

## Independent answers

**Q1 — AFFIRM, option (iii), with conditions.** Is "operational only" honest? **Almost, but not as written.** Nothing in exhibit B's diff alters *what* is measured or *how long*: the four science constants are byte-identical (`PRE_REGISTERED_SLOT_COUNT = 12`, `DEFAULT_SETTLE_S = 600`, `DEFAULT_SLOT_CADENCE_S = 600`, `DEFAULT_SLOT_CAPTURE_BUDGET_S = 480`; also `DERIVATION_RECEIPT_CLASS = "DIAGNOSTIC_NO_PACK"` at `scripts/gen_derivation_night.py:80` and `PRE_SETTLE_ALLOWANCE_S = 300` at :95, unchanged), the chain still performs exactly one `settle` after the reservation, re-anchors `next_start` to each slot's actual start, and the reservation remains the last machine action before the settle at both heads.

Two changes **do** touch slot admission, and the decisive mechanism is one neither the packet nor the ruling states: in `scripts/validate_powermetrics_fiducial.py`, every `custody_deadline.check()` sits in the ledger lifecycle's `_begin_once` (1558, 1623, 1641), `abandon` (1679) or `finalize` (1718) — all **outside** the `_sampler_lifetime` context manager opened at 2297. **No custody check can run between the sampler's spawn and its teardown**, so a budget/deadline refusal cannot truncate or perturb a sample. Its worst case is a *fully captured* slot whose ledger row is left unfinalized (writer rc 2 → `slot_refused`, chain exits with the session open) for desk recovery. Second, `--pre-reserve-strict` refuses sessions the sealed chain might have opened after a retry/recovery. Both act in one direction only: they can subtract a slot by a typed, logged refusal; they can never admit an observation the sealed rules exclude. Also note the added `--custody-deadline-epoch-s $((WINDOW_END_EPOCH_S - 10))` is *slacker* than the pre-existing `slot_start + SLOT_CAPTURE_BUDGET_S > WINDOW_END_EPOCH_S` guard, so it binds only on a capture overrun or a blocked read.

Conditions: (C1) pin the chain **as merged** — main is `4f1ede1e…`, `b5beea46…` exists only on the unmerged abort lane, so placeholder now, filled at the arm head; (C2) the admission-boundary change must be named in the revision, with the spawn/teardown mechanism; (C3) do **not** cite `--check` as proof the constants are unchanged.

**Q3 — contract change, not a mechanism choice** (agreeing with the ruling). Where the byte digest is *enforced* is already a mechanism (exhibit F, `scripts/run_night.py:1799-1816`: the gate reads the plan sidecar, never the pre-registration). What the sealed sentence *binds* is contract, amendable only by a dated revision under this gate's or Ed's authority.

**Q4 — (c) both**, plus three requirements the ruling omits (below).

## Paired verdicts, blocker-grade first

**B1. Charter-coldness defect in the convening mechanism — not the judge's fault, and it recurs for every future gate.** The ruling's §0 discloses that `~/.claude/CLAUDE.md`, the project `CLAUDE.md` and `MEMORY.md` auto-loaded. The charter says (lines 9-12) "This document is the ONE process context a cold adjudication instance receives. The project's operating doctrine is deliberately withheld from you," and §4 forbids "private doctrine files, session memory," "whether the material arrives directly or through copied, renamed, quoted, summarized, or linked form." `01-convene-script.sh` runs `claude -p` with `cd /Users/edr/code/JouleWise-wt-coldgate-a221` — a JouleWise checkout carrying tracked `CLAUDE.md` — and asks the judge to *disclose* auto-loads rather than preventing them. The judge complied honestly and refused `CLAUDE.local.md`. **Verdict: the ruling should stand.** I independently re-derived every load-bearing probe and they all check out, so the contamination did not produce a wrong answer. But record it, and convene gate 70 from a doctrine-free tree (no project `CLAUDE.md`, no memory) — otherwise "cold" is nominal. (Credit where due: the deliberate charter-sha typo trap worked; the judge caught it and refused first.)

**B2. Q2 text is not applicable verbatim (blocker against the packet's explicit requirement).** Three defects, all in the Provenance paragraph: the packet path is split mid-path across lines 16-17, so it renders as a space-broken, non-resolvable path; the filename is hyphen-split across lines 18-19 and renders as `10-coldgate-fable- ruling.md`, which does not exist; and the packet digest appears ellipsised as `a77c4ab3…0410b0` inside what becomes a sealed evidence record. **DISAGREE → AGREE-WITH-AMENDMENT.** Replace the Provenance paragraph verbatim with:

```
Cold-gate packet 69, sha256
a77c4ab3eb64c1f4da9f344a2fc247d18e1798be1c0c44e9fb59dc8f100410b0, at
`docs/process_traces/2026-09-16-activation-9853dd2b/69-coldgate-packet-prereg-chain-digest/00-PACKET.md`,
with its exhibits A-F, adjudicated by the cold Fable judge in
`10-coldgate-fable-ruling.md` of the same directory. The chain digest
history is exhibit B; the generator literal comparison is the judge's
probe P3, reproduced independently by the paired Opus refuter.
```

**B3. Q4(a)'s parse is order-dependent over a document that will then hold the superseded digest twice.** Executed: appending the ruling's text (placeholder filled) yields **three** `chain digest <64hex>` matches — sealed, sealed-as-quoted, new — and five bare 64-hex strings. The ruling's "take the digest from the LATEST revision" therefore becomes an unstated "last match wins" contract inside a sealed file. **AGREE-WITH-AMENDMENT.** Either (i) elide the quoted superseded digest to its 12-character prefix and add one uniquely-labelled machine-readable line, or (ii) keep the ruling's quotation and add the labelled line anyway. I verified (i) mechanically: exactly one `chain digest <hex>` match remains (the untouched sealed one, so any legacy consumer keyed on that phrasing is unaffected) and exactly one match for `^Chain digest in force \(revision 3\): ([0-9a-f]{64})$`. Add this line verbatim to the "one change" section:

```
Chain digest in force (revision 3): <CHAIN_SHA256_AT_ARM_HEAD>
```

and specify in Q4(a) that the test parses **that anchored line** with exactly-one-match semantics, falling back to revision 1's line 144 only while the line is absent.

**B4. Q4(a) as specified turns main red, and the ruling does not say when the placeholder is filled relative to the test landing.** The ruling says the placeholder is filled "in the same commit that arms the night," but the test compares the pre-registration to the tracked chain — so from the moment the abort lane merges until the arm commit, main fails CI. **AGREE-WITH-AMENDMENT:** the abort lane merges first, then revision 3 (filled) and the regression land in **one commit**; arming is a later, separate act.

**B5. `--check` is cited as evidence for a proposition it cannot support — and the citation would be sealed into the registration.** The ruling uses P1 in §3 ("runsheet region regenerates byte-exact") and in the revision text ("the runsheet check regenerates byte-exact") as proof no science rule moved. I ran it at main `5472ff53`: `PASS`, rc 0 — at a head whose chain digest is already `4f1ede1e…`, i.e. it passes *with* the sealed pin broken. `tests/test_gen_derivation_night.py:979` states its own purpose: "`--check` is the drift tripwire: editing the chain re-runs the emitter." It proves present-tense consistency and forces re-emission; it is not evidence about the constants. The probative items are exhibit C's **region diff** (whose only changes are prose and the rendered digest) and the generator literal diff. **DISAGREE on the evidentiary claim; AGREE-WITH-AMENDMENT on the text.** In the revision's "Why no science rule moved," replace "the runsheet check regenerates byte-exact" with:

```
the runsheet's generated region changes over the same interval only in
prose and in the rendered chain digest, not in any rendered constant
(exhibit C); `gen_derivation_night.py --check` is the tripwire that
forces that region to be re-emitted after any chain edit, and its
passing is not itself evidence about the constants;
```

**B6. The Q1 ground is slightly overclaimed.** §3 rests AFFIRM on P6 — that revision 1's "Fields filled at commit" lists `[CHAIN_SHA256]` as "a fact that does not exist yet; none is a scientific choice, and filling them does not reopen any rule above" (verified at lines 279-284). **This is the best evidence in the record and I did not find it independently — credit the judge.** But it licenses the *initial* fill of a placeholder, not a *re-pin* of a filled value; if it already contemplated re-filling, no gate ruling would be needed, which contradicts §3's own closing (a contract change needing this gate's authority). **AGREE-WITH-AMENDMENT:** ground the AFFIRM on the field being *designated non-scientific* — so re-pinning reopens no sealed rule — with authority supplied by this ruling, rather than on revision 1 "already contemplating" it.

**B7. Mechanism precision in the revision text (Ed's replicability bar).** The text says "a capture whose custody read cannot finish before the deadline is now a typed refusal," which locates the refusal vaguely in the capture and omits the budget's value. **AGREE-WITH-AMENDMENT:** replace that sentence with:

```
One consequence is stated so it cannot be read as hidden: a governed
custody read that cannot be bounded within its allowance (CUSTODY_BUDGET_S,
default 120 s, threaded from the plan by scripts/run_night.py) now refuses
in a typed, logged way where the sealed chain could block without limit.
Every such check runs in the ledger lifecycle's begin, abandon or finalize
step, never between the sampler's spawn and its teardown, so no refusal can
truncate or perturb a capture; its worst case is a fully captured slot whose
ledger row is left unfinalized (slot_refused, session open) for desk
recovery. That is a stop condition, not a tuning: it changes no value any
capture records, and it can only subtract a slot, never admit one the sealed
rules exclude.
```

Relatedly, §2's "where before it would have run past the window" is imprecise — before, the read could block indefinitely (the 2026-09-16 stall), and the pre-existing 480 s guard already barred admitting a slot that could not finish inside the window.

**B8. Q4 addition the ruling misses.** `preregistration_epoch_pins` (`scripts/issue_calibration_acceptance_generation.py:806-822`) refuses issuance (`preregistration_failed`) if the text yields anything but exactly one distinct `os_build:` value and one distinct `/usr/bin/powermetrics sha256 in force is <64hex>`. Any future revision quoting a different epoch breaks issuance with a confusing refusal. I probed both candidate texts: both still return `('25G83', 'b762e5bf…')`. **AGREE-WITH-AMENDMENT:** add to the Q4 module an assertion that the pre-registration yields exactly one of each pin. Cheap, and it makes the append-safety property enforced rather than lucky. Also: appending revision 3 changes the pre-registration's own sha256 (live `84b820b9…`), which the issuer checks against an operator-supplied `--preregistration-sha256`; the r6 acceptance artifact does **not** record it, so nothing existing breaks, but the next issuance must use the new value.

**Agreements with no amendment:** Q1 option (iii) and the rejection of (ii); Q3 contract-change classification and the proposed future sentence; Q4 ruling (c) with the (a)/(b) division of labour and the "each parsed from the pre-registration's own text" requirement — implementable, since the pre-registration carries 600/12/600/480 and `DIAGNOSTIC_NO_PACK` at lines 75, 101-102, 143; §2's identification of exhibit C's **empty** `a4d530cd` literal block as a material packet defect (I hit it too and cured it the same way — this is the packet's worst assembly flaw, since an empty evidence block could be read as "the literals are gone"); the nit that exhibit F calls the digest sentence a "SCIENCE pin" while revision 1 calls it non-scientific — the primary text governs, and exhibits D/E/lane 227 should be reworded to match. The ruling's register matches revision 2 and it edits no word of revision 1 — both requirements met.

**Net:** ratify Q1/Q3/Q4 as ruled; apply the Q2 text with amendments B2, B3, B5, B7 (and B6 to the ruling's reasoning, B4/B8 to the Q4 spec); record B1 and fix convening before the next gate.
