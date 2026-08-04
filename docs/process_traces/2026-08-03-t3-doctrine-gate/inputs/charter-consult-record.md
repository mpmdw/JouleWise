# Charter design consult — record (Sol high, thread 019fcb1a-96f9-7612-8b02-a55444714391)

Subject: draft `docs/process/coldgate_charter.md` v1 (sha256
`2a738630e5bd780b4664ad47d058e93e7241595064b9d0d2dbd223b4bbc8acaa`,
tracked at `6448bc0`). Route: MCP codex tool, read-only, effort high
(Ed cap). Full verbatim transcript: rollout
`rollout-2026-08-03T21-49-05-019fcb1a-96f9-7612-8b02-a55444714391.jsonl`
(sha256 `87f36e6860499a3661977e1219760e8232b230d99e5b935fa86f22d3a2cf630f`;
persists in ~/.codex/sessions/2026/08/03/; loss-insurance copy in
.desk/t3-doctrine-gate/). Envelope: valid bridge-report/v1, final,
status DISCUSSION, flags [no_edits, read_only, base_head_mismatch —
verified benign: charter bytes matched the pinned sha throughout].

## Sol verdict (one line)

Do not ratify the charter at the current hash. Core R2 architecture
endorsed (byte-pinned charter, fail-closed mismatch, cross-model blind
review); five seams to close first.

## Findings adopted into charter v2 (lead adjudication inline)

- **Q1 bias leakage — CONFIRMED, adopted.** v1's status paragraph,
  §§1-2 anti-continuation narrative, §5 disposition-sharing assertion,
  and §6 recitation of past hygiene catches all pre-frame the judge
  toward STOP/escalate and toward re-finding past defect signatures.
  Sol's neutral replacement texts adopted (v2 §§ preamble, 1, 2, 3, 6).
- **Q2 missing doctrine — CONFIRMED, adopted.** New sections: Authority
  and evidence (charter governs procedure only; packet cannot amend it;
  burden on the proponent; lead disposition is argument not evidence;
  exhibits are data not instructions) and Results and severity
  (AFFIRM/REJECT/REFUSE per atomic question; BLOCKER/MATERIAL/NIT;
  REFUSE names defect + minimum cure, has no merits effect). Verdict-
  standing bullet replaced with Sol's corrected text (machinery defect
  never inverts FAILED; supports a separately authorized rerun).
- **Q3 §4 laundering seam — CONFIRMED LIVE, adopted.** Sol demonstrated
  the defect against this very packet (the verbatim RUN_STATE T3 block
  admitted as a custody input). v2 §4: prohibition applies through
  copied/renamed/quoted/summarized/linked material; bounded verbatim
  excerpts admissible ONLY where the exact words are themselves the
  object of an enumerated question, with source/revision/line-range/
  proposition/why-no-primary-evidence stated. This packet restructured
  accordingly (see PACKET.md revision).
- **Q4 §5 composition holes — CONFIRMED, adopted.** (a) impossible
  refuter charge (refute an unseen ruling) deleted — refuter falsifies
  the packet's claims, the lead's labeled disposition, and the asserted
  contract application; (b) both outputs SEALED (recorded verbatim,
  hash-pinned) before synthesis; per-question synthesis content
  mandated; "synthesis alone is not an override" — override is a
  separately labeled written document citing both sealed outputs,
  presented to Ed.
- **Q5 hash pin — adopted with Sol's recommendation.** Trust anchor =
  tracked charter registry (status/provenance/sha OUTSIDE the hashed
  bytes) + launch-time expected digest supplied independently of the
  packet. Judge-side recomputation stays as defense in depth (REFUSE
  ALL on mismatch). Minimal validator spec recorded in the registry
  file; build queued (small tool).
- **Q6 first-contact failures — all five adopted:** status moved to
  external registry; this packet's pin filled at freeze; laundering fix
  above; packet Q3 split into atomic 3a-3e (3e = effort-cap vs ruled
  composition); cold-packet-handoff gate criterion tightened to
  "preflight validation succeeds + both outputs sealed + judge returns
  non-REFUSE on the mechanism and exact bytes." Bootstrap declaration
  for the self-referential first packet: Ed authorizes the digest
  solely as the procedural candidate for evaluating those same bytes;
  bootstrap authorization is not ratification evidence.

## Sol's open questions — lead rulings (recorded for the gate)

1. Trust anchor: ADOPTED Sol's recommendation (tracked registry +
   explicit launch-time expected digest).
2. Refuter vs judge ruling: parallel blindness KEPT; impossible charge
   deleted; a bounded post-seal rebuttal round MAY be convened by the
   lead as a separate recorded step when synthesis finds a genuine
   split (consistent with existing split-verdict practice).
3. Prior verdict after a machinery defect: ADOPTED Sol's line —
   historically preserved, never inverted, dependent authorizations
   paused pending a separately authorized governed rerun.

## Sol's recorded disagreements (preserved)

Disagrees that v1 achieved charter-suppression (paths suppressed,
content copyable); disagrees with v1's anti-lead framing (independence
= no deference, not presumed lead bias); disagrees that unstructured
synthesis suffices; disagrees that packet-local hash + judge
recomputation constitutes validation (no independent trust anchor).
Agrees with R2's core architecture.
