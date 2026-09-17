# Cold-gate packet 69 — PREREG-CHAIN-DIGEST-ADDENDUM-01 (kernel rank 227, P1): may the sealed pre-registration's chain-digest field be re-pinned by a dated revision, and what must that revision say (assembled mechanically by activation 9853dd2b, 2026-09-17 12:50 PDT)

Convened under rule 11 because a sealed pre-registration is not the magistrate's to amend, and the owner has directed (directive issue 353) that the next equivalence night be armed without further owner input. Nothing is armed. The night gate refuses an arm whose tracked chain bytes differ from the plan's digest pin, and the plan's pin is written at arm time from the tracked chain; the pre-registration's own digest sentence is the SCIENCE pin, and it now names bytes the repository no longer carries (exhibit A, B).

## What was found (from the exhibits; the judge verifies)

- Revision 1 of `configs/calibration/preregistration_d079_epoch_25g83_rev1.md` (sealed) pins the derivation chain at SHA-256 `b8bf5b0a…` (exhibit A lines 143–144). Revision 2 (2026-09-10, Ed's ruling by directive 316, "recorded by the magistrate; not a magistrate amendment (rule 11)") is the established shape for a dated addition: revision 1 is not edited; the addition states what it changes and nothing else (exhibit A).
- The tracked chain moved three times on 2026-09-17 (exhibit B): PR #350 added custody budget and deadline flags, the strict pre-reserve flag, `NIGHT_VERIFY_ONLY`, the refusal-document path and the custody-budget marker export; the abort lane (branch `feat/2026-09-17-wallclock-abort`, not yet merged) adds `--custody-budget-s` to the end-of-window abort. Main today is `4f1ede1e…`; after the abort lane merges it will be `b5beea46…`.
- The night's timing literals live in `scripts/gen_derivation_night.py`, whose regenerated runsheet region is checked byte-exact by `python3 scripts/gen_derivation_night.py --check`; exhibit C shows the region's diff since sealing and the literal lines at both heads.
- The corrected handback paragraph (exhibit D) already tells an arm operator that the sealed pin is stale and that a dated addendum is required before the next arm; lane 227 (exhibit E) registers that requirement; exhibit F shows what the gate actually binds.

## Q1 — may the sealed chain-digest field be re-pinned by a dated revision 3? (rule one)

(i) AFFIRM: the chain changes are operational (bounding reads, typed refusals, verify-only mode, a bounded abort) and touch no science rule of revision 1 — one 600 s settle, 12 slots at a 600 s start-to-start cadence, fixed order, protocol `powermetrics_pulse_fiducial_v3` unmodified, the `--sleep-display-before-capture` omission, the DIAGNOSTIC_NO_PACK class — so a dated revision 3 may re-pin the digest to the tracked chain without re-opening any sealed rule; state what evidence the revision must cite so a reader can verify that claim (exhibit C's literal lines? the runsheet check? the diff?). (ii) REFUSE: the digest was sealed as part of the sample definition; a changed chain is a changed instrument and the campaign must be re-registered (say what "re-registered" means concretely and what it costs against directive 353). (iii) AFFIRM WITH A CONDITION you name (for example: the revision pins the digest of the chain AS MERGED, so it can only be written after the abort lane lands; or the revision must also pin the generator's timing literals so the science rules and the bytes are bound separately).

## Q2 — the exact text of revision 3

Write it, in the register of revision 2 (exhibit A): a heading with the date and authority ("cold-gate ruling 69, packet 69; recorded by the magistrate; not a magistrate amendment (rule 11)"), a provenance paragraph naming this packet and its exhibits, the one-sentence rule change (the digest sentence's replacement or override — quote the old sentence, give the new one), what evidence proves no science rule moved, and an explicit statement of what the revision does NOT change. If your Q1 answer is (iii) with the as-merged condition, write the text with a placeholder `<CHAIN_SHA256_AT_ARM_HEAD>` and say who fills it and how it is verified (the runsheet check, the plan sidecar, a regression).

## Q3 — should the pre-registration keep pinning chain bytes at all? (name text, do not rule)

Revision 1 binds the sample to a byte digest of an executable that also carries operational plumbing. An alternative is for the pre-registration to pin the science-bearing literals (settle, cadence, slot count, order, protocol id, the writer flag omission) and leave the byte digest to the plan sidecar the gate already checks. Rule only whether this is a mechanism choice or a contract change, and give the sentence a future revision would need; do not decide it.

## Q4 — the regression

Rule the mechanism that prevents silent drift: (a) a test asserting the pre-registration's digest sentence equals the tracked chain's digest (so every chain edit forces a dated revision, or the test fails); (b) a test asserting the generator's timing literals equal the values quoted in the pre-registration (science pin) while the byte digest is checked only by the plan sidecar; (c) both. State what each forces on the next person who edits the chain.

## Constraints on the judge

Rule only the questions above; do not amend any rule, decision-log entry, skill doctrine or the pre-registration file itself (write the revision text INTO YOUR RULING for the magistrate to apply verbatim). Cite exhibits by name; code by file:line only if you read it in this checkout (main `5472ff53`; the abort-lane head `a4d530cd` is readable with `git show a4d530cd:<path>`). For Q1, execute at least one probe in the foreground: run `python3 scripts/gen_derivation_night.py --check` here, and diff the generator's timing literals between `3015cb39` and `a4d530cd` yourself. Under 14 KB. Write the ruling to `docs/process_traces/2026-09-16-activation-9853dd2b/69-coldgate-packet-prereg-chain-digest/10-coldgate-fable-ruling.md`.

## Charter pin

Charter: `docs/process/coldgate_charter.md`
sha256:
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

The judge independently checks this digest against the separately supplied pin in the convening prompt.

## Exhibit manifest

```
d1ed28c85bff971de0e107f58a7cfbb5984dba477993dfc06769e3dafa72b203  exhibit-A-prereg-sealed-digest-and-revision-2-shape.md
e624295e7fc58a45e4858a421a0ebdcc437f66254ea930635947f58771d911d4  exhibit-B-chain-digest-history-and-diff.md
bbc0ab8834179b6b7c42949f1dd04b7eb6350bb05afcca9d06f7e27dcf4c9073  exhibit-C-runsheet-region-diff-and-timing-literals.md
cb664b7ada82077dfaaa9342af593a87c747bc9cb67af2a16b7aa93f28c2ccd2  exhibit-D-handback-corrected-paragraph.md
2d5ef88ee2eb54fb701881b5895449c358e21206334c1d22130717ef8ed27695  exhibit-E-lane-227.md
c8d37c4f0d1cee1272299634548fa1948324f7a23d69fd0436c6ce98eacb24a9  exhibit-F-gate-digest-binding.md
```
