# CONSULT — coldgate validator: F3 closure shape + B1 scope + prune adjudication (NOT a fix round)

## Role and bounds

You are Sol, consulted as design peer under JouleWise rule 2 (bounded
pre-decision consult, 1 round, explicit license to disagree with the
magistrate's positions below). This is a DESIGN CONSULT, not an
implementation task: produce a written recommendation only. WRITE_SCOPE:
none — do not modify any file. Read-only inspection of the repo is
licensed. Branch under discussion: `impl/coldgate-validator` @ 38b6570
(`scripts/validate_gate_packet.py`, `tests/test_validate_gate_packet.py`;
registry: `docs/process/coldgate_charter_registry.md`).

## Why a consult, not fix round 4

Three successive fix rounds failed with the SAME defect signature — an
absolute-path bypass of the attestation privacy denylist (F3). Latest
(delta audit of round 3): predicate at `scripts/validate_gate_packet.py:73`

    ABSOLUTE_PATH_RE = re.compile(r"/(?=\S)|(?:~|[A-Za-z]:)[\\/]|\\\\(?=\S)")

lets `--launch-environment-attestation "cwd='/ secret'"` exit 0 with a
PASS receipt containing `/ secret`. The `(?=\S)` exists to satisfy
`test_accepts_space_surrounded_lone_slash_and_schema_id` (~line 551),
which requires `"input / output"` to PASS verbatim into the receipt.

Magistrate's analysis: the positive requirement and the privacy invariant
are mutually unsatisfiable — POSIX filenames may contain spaces, so every
`/` (including space-surrounded) prefixes some legal absolute path;
`"input / output"` itself contains the legal path `/ output`. No denylist
regex closes the class while that test stands.

## New input that reframes the question

A concurrent oversight/overbuild audit (fresh Sol, same head) returned:

1. **B1 (blocker): PASS does not bind the judge to the validated bytes.**
   Registry line ~57 requires the judge be invoked only with the exact
   sealed bytes validated. The validator hashes exhibits, emits PASS, and
   exits; exhibits can be substituted before judge launch under a
   still-valid receipt. No snapshot, descriptor handoff, or launch-time
   revalidation exists.
2. **Prune recommendation: delete the attestation privacy subsystem
   entirely** (`:71-73`, `:126-170`, `:409-422`, `:552-553`, `:577-619`
   + tests `:519-606`): optional free-text attestation fields do not
   discriminate any registry invariant (clean-environment verification
   and contamination disclosure are convener duties). If the fields go,
   F3 closes by construction — the third-round bug lives in code that
   may not deserve to exist.
3. **S1 (should-fix):** fence-unaware heading scans — a fenced example
   containing `## Charter pin` causes a false `charter_pin_duplicate`
   refusal of a valid packet.
4. **S2 (should-fix):** `--help` exits 2 with human text, violating the
   documented every-nonzero-result-is-a-JSON-receipt contract.
5. Additional prune items: move `--receipt-out` persistence to the
   convening runner; drop internal call-shape test assertions. Keep the
   independent packet digest and dirfd/symlink/hard-link custody checks.

## Questions to answer (rank your confidence on each)

1. **F3 closure shape, given the prune option.** Which do you recommend:
   (A) keep attestations, refuse ALL `/` `\` `~` drive-prefixes (invert
   the `input / output` test); (B) keep attestations under a strict
   allowlist grammar; (D) delete the attestation subsystem per the prune
   recommendation, making F3 moot; or something better? If you keep any
   attestation channel, enumerate the residual bypass surface (encodings,
   Unicode lookalikes, control chars, length tricks) and state which
   residuals are accepted. Note the deletion option interacts with the
   registry's convener-duty framing — say whether the receipt loses
   anything an adjudicator actually needs.
2. **B1 scope.** Is sealed-byte judge handoff in-scope for THIS branch
   (e.g. a validate-and-exec mode holding descriptors open, or
   launch-time revalidation), or is it structurally a convening-runner
   duty to register as a follow-on row (a CGV-HARDEN-01 sibling; that row
   already covers receipt-write TOCTOU + fsync)? Recommend the minimal
   in-branch change (if any) that makes the receipt honest about what it
   does and does not bind — e.g. explicit receipt language or a
   registry-visible limitation — versus what belongs to the follow-on.
3. **S1/S2 disposition.** Fix in this branch now, or defer? For S1,
   recommend the minimal fence-aware scan; for S2, recommend whether
   --help emits a receipt, is exempted in the contract text, or is
   removed.
4. **Regression vectors.** For whatever shape you recommend, specify the
   minimal discriminating test set that would have caught fix rounds
   1-3's bypasses and your shape's own residuals — the following fix
   round must carry defect-shaped regressions.

## Output

claude-codex-report/v1 envelope, genre=consult. A ranked recommendation
per question with rationale; disagreement with the magistrate's analysis
is explicitly licensed and valued. One round; the magistrate synthesizes,
decides, and records dissent if any.

Emit the report as your FINAL MESSAGE.

(Effort-tier record: rule-10 tier for a design-bearing consult is xhigh;
Ed's standing directive caps Sol at high — high applied, deviation
recorded at launch per skill §Effort selection.)
