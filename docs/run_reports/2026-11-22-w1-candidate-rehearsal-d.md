# ALIGN v4 W1 signing-candidate rehearsal D · 2026-11-22

**Provisional.** This is the Tier 0 rehearsal for the W1 critical path. The
candidate starts at issued PR #734,
`b2e01464d6d4fbf2901ff4d4154df9455104a12a`. Rehearsal D carries the requested
PR #897. The production-track comparison uses its W1 successor, PR #904, as
required by RL-193 §3. [Rehearsal C](https://github.com/mpmdw/JouleWise/blob/e2ce69e6c2e18c1113f9c808042948f3a8e3a767/docs/run_reports/2026-11-20-w1-candidate-rehearsal-c.md) · [RL-193 §3](https://github.com/mpmdw/JouleWise/blob/bceb204a1ec65d7ef2e815e4f929135ede868a80/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L23138)

## Component pins and assembled trees

| Order | Component | Pushed head |
|---:|---|---|
| 1 | [PR #826](https://github.com/mpmdw/JouleWise/pull/826) desk-seal successor | `1fc28324d51f8057fa6228e6e7d42b5ea331d52c` |
| 2 | [PR #839](https://github.com/mpmdw/JouleWise/pull/839) step-4 restore proof | `70b795954a4876c828cb6d6b3de7941e9d726768` |
| 3 | [PR #831](https://github.com/mpmdw/JouleWise/pull/831) S rows | `b38cef8286c7772e970760103debf187174fbad6` |
| 4 | [PR #813](https://github.com/mpmdw/JouleWise/pull/813) S/Q amendment | `82542232dbb7459b0320c37380925e9372afb7e8` |
| 5 | [PR #897](https://github.com/mpmdw/JouleWise/pull/897) contrast writer | `f32326af2b902fe7060d98b3a28240d0665bc4fa` |
| 6 | [PR #944](https://github.com/mpmdw/JouleWise/pull/944) Option C registration | `16f10ade2ad57ca17c9f15a3773764741a6b2369` |
| 7 | [PR #809](https://github.com/mpmdw/JouleWise/pull/809) Part C source, audit pending | `cea5fb6957c8755c9596e94afb638f82357ff5be` |
| Lead comparison at 5 | [PR #904](https://github.com/mpmdw/JouleWise/pull/904) | `a2c6800bc5a503b6ca1141f3cc3d19ef485d3546` |

PR #809 advanced from C's last blocked pin `2e036f9401ea0afee41b567bd355f28c23bec926`
before D's intake. Its new changes include the frozen oracle, episode stamp
ordering, and journal derivations. PR #944 was new to D. The Part C port uses
`09b1ddbd515bcea1ecf2384cbc885bd2c137817c` as the W1 scaffold and applies the
scoped delta from upstream `3f7f7c8493a21fd8cd296f4dda18becc67512bd9`.

| Checkpoint | Rehearsal commit | Exact tree | Condition 13 |
|---|---|---|---|
| First four components | `ae1c58bd252bbc1e8b3af31567abc831b72da729` | `3652381ee416a621ac76388bc54d48abb11efc4e` | PASS 10/10 |
| Add #897 | `538984b48a4dbaa79b8c9b45e981396474116666` | `7b5ce9560758909fe3693afdee5b1c4039155d53` | PASS 10/10 |
| Add #944 | `1da35a16f7c62c6d8b0a924dca61607a6c48b317` | `d471ee7f762f5d7f95889ec142ad7bd16af0ccd7` | PASS 10/10 |
| Add #809 port | `5eed5e388d3a3078caed432394766037e601e588` | `675016cee6c3986e37475142b9cc13b38c7ec52c` | PASS 10/10 |

The assembler parsed the issued `R1_EXECUTED_SOURCES` assignment and compared
its ten Git blobs after each of the seven component steps. The pinned rerun
reproduced all four commits, trees and counts. The #904 comparison produced the
same four trees, with final commit `cdd990053f10d31427fb9092a8cb4bae8becf6d6`.
The pinned object-only replay took 24 seconds from snapshot to result.
Applying the three #904-track first-parent diffs to #813 in a scratch
index reproduced the candidate tree. The published PR #823 signing
comparator independently returned 10/10 for both final projections. The
step-4 comparator's rehearsal control returned 3/3 across the #813 and
full-candidate checkpoints. The first two trees also match C's. The #813 public unsigned template exception
uses the same Git blob checks as C. [RL-183 §1](https://github.com/mpmdw/JouleWise/blob/71a83f666024c26e89cdce09dfb7a7e80d299794/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L20084)

## Resolutions and Part C port

- **Host-command inventory.** The three-way port had 221 base entries, 337
  W1 entries and 222 entries in pushed #809. W1 inventories its own host
  call sites. #809 adds the isolated D-018 Python child
  `scripts/align_r1_part_c.py / _pinned_trace_problems:2bd56ab03eeb3e96 /
  python-isolated` to the upstream inventory. The resolver parses the three
  JSON stages, validates each row and keys it by `(file, locator, command)`.
  The union retains all 337 W1 entries and all 222 upstream entries, with
  197 common, 140 W1-only, 25 upstream-only and 362 distinct sites. It
  preserves the reviewed seam text and uses the base to adjudicate one-sided
  seam edits. It stops on competing descriptions. The final-tree check
  independently guards against dropping any key from the pre-port candidate,
  W1 projection or upstream. Only the D-018 site is new in #809 relative
  to its upstream base. The other 24 upstream-only entries were inherited.
- **Option C protocol.** Two overlaps in `docs/align/pilot_protocol_v4.md`
  required a scoped resolution. The first preserves RL-149's item 9 before
  adopting #944's B8 verbatim. The second takes #944's B9 K disclosure and
  keeps the W1 amendment's adjacent S wording about the decoded portion of
  each reference-state row. The script checks the shapes of the two diff3
  hunks and stops if they change. B10 and the RL-198a council-row edit apply
  cleanly. [RL-198a](https://github.com/mpmdw/JouleWise/blob/5aedc3c55ac48584836b62db5c11ad31ec688e16/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L24376)

The W1 port `7944b5025bd7fb278a2e0b65525be1bfa8533c6a` has these nine
paths. The first seven are byte-equal to pushed #809 on the final assembled
tree. The last two carry the recorded union and W1-only fixture.

| Path | Role |
|---|---|
| `scripts/align_r1_part_c.py` | Evaluator and judged invoker |
| `scripts/align_r1_part_c_evidence.py` | Evidence, pinned validations and descriptor binding |
| `tests/align/partc_audit_probe.py` | Synthetic audit probes |
| `tests/align/partc_derived_sweep.py` | Audit-2 derivation sweep |
| `tests/align/test_partc_frozen_differential.py` | Unchanged pushed frozen v3.1 suite |
| `tests/test_part_c_evidence_ledger.py` | Evidence regressions |
| `tests/test_part_c_gate_evidence.py` | Gate regressions |
| `tests/host_command_sites.json` | Keyed union described above |
| `tests/align/test_rl145_part_c.py` | W1-only synthetic descriptor mirror in the launcher fixture |

The scaffold also carries the W1 launcher and follow-up changes from C. The
scoped upstream delta has no new launcher hunk. The two added synthetic
probe files applied directly and the other upstream hunks applied cleanly
apart from the inventory. The upstream `CANONICAL.md` and upstream run
report are outside the code/test port. [PR #809 handoff](https://github.com/mpmdw/JouleWise/blob/cea5fb6957c8755c9596e94afb638f82357ff5be/docs/run_reports/2026-11-19-pr809-rl189.md)

## Verification

Local results as of 2026-11-22 01:54 PST.
All local inputs were synthetic or source/policy files. The checks used
Python 3.13, isolated temporary directories, offline model caches, the host
command tripwire and the seat's file-access fence.

| Check | Assembled W1 tree |
|---|---|
| Option C protocol and gate ledger | PASS (50 tests) |
| Host-command synthetic scanner | PASS (1 test) |
| Host-command exact census | FAIL (0 missing, 24 stale) |
| Frozen v2 | FAIL (clean control, zero mutations executed) |
| Pushed v3.1 clean control and descriptors | PASS (16 cases, 4 expected passes, 12 expected refusals, 0 false passes) |
| Pushed audit-2 derivation sweep | PASS (443/443 expected refusals) |
| Registration | FAIL (25 tests) |
| Named condition-13 tests | PASS (2 tests) |
| Executed closure | FAIL (6 tests) |
| Dynamic closure | FAIL (10 tests) |
| Refusal census | FAIL (24 tests, 1 skipped) |
| W1 synthetic | PASS (22 tests, 15 skipped) |
| Opus cold witnesses | PASS (1 tests) |
| W1 reliability | PASS (13 tests) |
| Desk release | PASS (63 tests) |
| Next-arm packet | PASS (49 tests) |
| W1 blockers and U3 | PASS (18 tests) |
| Desk offload | FAIL (105 tests) |
| Synthetic step-4 restore | PASS (11 tests) |
| RL-176 | PASS (28 tests) |
| RL-182 registration | PASS (4 tests) |
| S rows | PASS (67 tests, 4 skipped) |
| Contrast writer | PASS (15 tests) |
| Part C attack reproductions | PASS (15 tests) |
| Part C evidence ledger | PASS (80 tests) |
| Part C gate evidence | PASS (21 tests) |
| Part C legacy launcher tests | FAIL (90 tests) |
| Full synthetic WP22 opt-in | PASS (23 tests) |
| Ordinary synthetic PREQUAL subset | FAIL |
| W1 PREQUAL selected probes | IN PROGRESS |

- Frozen v2 SHA-256 was
  `f35c7bb08814785079008acd3a47a3c85993083da1e7ba731e7d2bee486d768d`.
  Its predecessor fixture fails the accepted D-018 CSV check with
  `other_failure / bundle_binding`. RL-193 §1 confirms the check.
- Pushed v3.1 SHA-256 was
  `12ca35d36d527607fb2b50edc79fad7ee0fb17dfe3608c11488d39092b231588`.
  The clean control had four of four matching descriptor digests. Each of
  predecessor, Step D, D-bank and X-G had one expected pass and three
  expected refusals across its descriptor cases. The complete v3.1 matrix
  remains part of #809's exact-head audit.
- `test_d_max_turns_is_part_of_frozen_kit` was refused by the slot-read
  fence on both issued W1 and the assembled tree. The other registration
  cases passed. Both named condition-13 tests passed at both pins.
- The issued and candidate fresh-process dynamic trace controls hit the
  same 300-second timeout. The nine remaining checks passed. The candidate
  executed-closure census found one missing strict binding for
  `scripts/align_r1_part_c_evidence.py`. All six executed-closure checks
  passed on issued W1.
- The final evaluator changed the refusal-site counts and import scope.
  `test_every_refusal_site_is_listed_with_its_exact_count` and
  `test_the_scan_covers_every_module_the_hazard_path_imports` failed.
  C recorded both checks passing on issued W1.
- The offload test `test_git_and_restricted_members_refuse_without_entering`
  could not create its synthetic directory in this seat. The same
  error occurred on issued W1.
- Full WP22 passed with its single expected failure. The ordinary
  PREQUAL subset passed the R0 config and D pin checks. The stack,
  template and checkpoint checks reported local dependency/input failures.
- The legacy W1 Part C suite ran 90 tests and reported 234 failed
  assertions including subtests, plus four errors. Issued W1's earlier
  version of the module passed all 31 cases. The failing candidate
  run includes legacy clean controls rejected by the newer evaluator
  and evidence-shape mismatches. The #809 builder and W1 port owner
  must adjudicate the legacy fixtures before exact-tree CI.
- The full canonical suite requires archived capture fixtures. Local
  verification uses the scoped synthetic runs. Ordinary and W1 PREQUAL
  have additional native or lead-input rows. The workflow launches CI on
  main pushes and PRs. The rehearsal has local results. The session-end
  fixture census exited 2 because this seat cannot execute `ps`.

The first two assembled trees reproduce C's tested trees. The end-of-run
scoped fetch and comparison are recorded in the seat. The scoped component heads matched the recorded snapshot at the latest check.
The seat's `test-exceptions.tsv` records failed and skipped test IDs
alongside issued observations where available.

Local `assemble.sh` SHA-256 is `52016ae5ad9933ad6661350b287c08f7ab440d02d932538cc03e82252632d059`.

## Promotion gates and owners

| Gate | Owner | Required evidence |
|---|---|---|
| Approve the component set | W1 lead and component reviewers | Exact accepted diffs for #826, #839, #831, #813, #904 and #944. Close #826's direct and successor unpack-receipt and digest-only gate, #839's binding, and #813's E1–E17 audit and CI. #944 includes RL-198a. RL-200 §1.3(c) leaves the optional earlier dose edit to the lead if it fits the signing schedule. |
| Accept #809 | Opus builder, independent executing auditor, W1 lead | Zero false passes on the adopted v3 family and six-column positive supplement, D1–D6, audit-2 regressions and independent admission at the exact head. Keep the seven ported files byte-equal and resolve the legacy W1 launcher failures before rerunning exact-tree CI. Lead records the two protected stored replays of counted Part C and F0 run 11 as verdict and failing check names, with the archived native limit marked unattested. |
| Command-site gate | #809 builder and W1 lead | All 362 declarations are preserved in D. The live scan has 338 sites, and rejects exactly the 24 inherited upstream rows. Audit and dispose those rows before promotion so the active inventory equals the W1 scan. |
| R0 binding | #824 builder and auditor, then W1 lead | Admit the R0 sampler on its own lane and bind the authorized R0 record, including `R0.record_sha256`, on the W1 candidate. |
| R1 fill and anti-hindsight | W1 lead | Incorporate approved #886, RL-189 §2.5 planning release, backfilled slot record from the designated session, DEC2 inputs, unchanged `INCONCLUSIVE` contrast, and both anti-hindsight lines. Run derive-contrast and regenerate on the final source tree. |
| Step-4 provenance and registration inputs | W1 lead, U3 independent reviewer | Compare exporter, selection and roster blobs at actual step 4 vs signing. Rerun step 4 if any differs. Bind U3 transfer, sources and gate, WP19, R0, battery policy and gate reports. Confirm the allowed publication file list. |
| Strict closure and hash refresh | W1 lead | Update `joulewise/align/apple/v4_registration.py` executed artifact inventory for `scripts/align_r1_part_c_evidence.py` and any other final paths. Regenerate the full `docs/align/v4/dynamic_closure_trace.json` on the candidate. Re-census the approved refusal sites and imports in `configs/gates/hazard_refusals.json`, then bind the reader-census code and evidence. Refresh strict receipt artifacts, gate A/B hashes, regenerated kit and template member bindings. Regenerate and sign the receipt against the approved candidate pin. |
| Signing admission | W1 lead and research lead | Run final `--check`, exact-tree tests and CI. Submit the head, ten-blob and accepted-diff proof, v3 plus supplement results, #813 diff list and allowed publication file list for the research lead's cold pass. |
| E3 install-only rehearsal and smoke | W1 lead and authorized magistrate | After candidate promotion, issue E3's typed authorization and perform the real install-only rehearsal at the candidate pin, with absence before/after, future start, no process launch and a burned session ID. Bind its three hashes, applicability and the authorized record to PREQUAL. E3 gates the smoke. The lead authorizes the one counted Part C and W1 smoke. |

The signing list comes from RL-193 §3 and the R1 conditions from RL-189
§2.5. The E3 timing and seven conditions are in RL-193 §2. The C1 pieces
#887, #889, #894 and #896 land under the C1 re-signing sequence. [RL-193 §§2–3](https://github.com/mpmdw/JouleWise/blob/bceb204a1ec65d7ef2e815e4f929135ede868a80/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L23120) · [RL-189 §2.5](https://github.com/mpmdw/JouleWise/blob/bceb204a1ec65d7ef2e815e4f929135ede868a80/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L22186)

## Rerun and promotion sequence

From any JouleWise worktree, use a new scratch directory. The assembler fetches
the named refs only, records the exact heads, builds Git objects with ordered
parents and makes a detached checkout. A moved W1 pin or unclassified Part C
path stops assembly. The test runner records per-group outcomes in
`exits.tsv`. Run these groups sequentially to keep worker counts bounded.

```sh
seat=/Volumes/JW-EXT/scratch/d-w1-candidate-rehearsal-d
run="$seat/replay-$(date +%Y%m%d-%H%M%S)"
"$seat/assemble.sh" --heads "$seat/assembled/heads.json" --output "$run"
cat "$run/heads.json" "$run/variants.json"
"$seat/run-checks.sh" "$run/worktree" replay-variant3 focused "$run/focused"
"$seat/run-checks.sh" "$run/worktree" replay-variant3 differential "$run/differential"
"$seat/run-checks.sh" "$run/worktree" replay-variant3 closure "$run/closure"
```

For promotion, the integration lead uses Bash and supplies the approved
integration branch name and ordered array `approved_fill_commits` from #886.
Use `set -euo pipefail` and compare `heads.json` to the approved pins before
applying commits. This inserts
the fill directly after #813. The three subsequent first-parent diffs are
#904, #944 and the accepted Part C projection.

```bash
seat=/Volumes/JW-EXT/scratch/d-w1-candidate-rehearsal-d
run="$seat/lead-$(date +%Y%m%d-%H%M%S)"
"$seat/assemble.sh" --contrast-pr 904 --no-checkout --output "$run"
cat "$run/heads.json" "$run/variants.json"

# Run the rest only after exact-head acceptance and pin comparison.
base=$(python3.13 -c 'import json,sys; print(json.load(open(sys.argv[1]))["variant1"]["head"])' "$run/variants.json")
source=$(python3.13 -c 'import json,sys; print(json.load(open(sys.argv[1]))["variant3"]["head"])' "$run/variants.json")
git rev-list --first-parent --reverse "$base..$source" > "$run/post-fill-commits"
test "$(wc -l < "$run/post-fill-commits" | tr -d " ")" -eq 3
git worktree add -b "$W1_INTEGRATION_BRANCH" "$run/worktree" "$base"
cd "$run/worktree"
git cherry-pick "${approved_fill_commits[@]}"
while IFS= read -r commit; do
  git cherry-pick -m 1 "$commit" || exit 1
done < "$run/post-fill-commits"
git rev-parse HEAD 'HEAD^{tree}'
```

Verify each applied diff after the fill. A conflict goes to the lead before
generation. RL-193 §3 permits the lead to choose the application order and
requires generation after the accepted #809 port.

- Run the approved [R1-to-W1 chain](../align/R1-TO-W1-CHAIN.md) with the
  lead's authorized operands. For mechanical replay of steps 1–5 use
  `python3.13 -B scripts/align_r1_to_w1_chain.py --run-dir "$R1_RUN" --slots "$R1_SLOTS" --work "$R1_WORK" --write-contrast --until derive-contrast`.
  Compare step 4 with the recorded `STEP4_CHECKOUT` and candidate commit
  using `J="$PWD" STEP4_CHECKOUT="$STEP4_CHECKOUT" SIGNING_COMMIT="$(git rev-parse HEAD)" sh "$seat/check-signing-step4.sh"`.
  This is the block in [the signing checklist](../align/v4/W1-BLOCKERS-merged.md#w1-signing-checklist-additions).
  Apply the approved decision inputs and U3, WP19, R0, receipt and gate bindings.
- Regenerate and verify on the final approved source tree. The commands below
  assume the lead has installed the reviewed closure and input updates.
  The lead uses the authorized signing process for the receipt and gate reports.
  Use `python3.13 -B -m tests.hazards.refusal_census` to produce the change
  candidates for the reviewed refusal census.
  The seat copies the comparison commands from [PR #823](https://github.com/mpmdw/JouleWise/blob/2acbb013567e2d97232497791419f61264dbf831/docs/run_reports/2026-11-18-w1-integration-evidence.md#reproduce-on-approved-bytes) and the step-4 checklist.

```sh
python3.13 -B scripts/align_v4_kit.py
python3.13 -B scripts/align_v4_dynamic_trace.py --out docs/align/v4/dynamic_closure_trace.json
python3.13 -B -m unittest -v tests.align.test_v4_executed_closure \
  tests.align.test_v4_dynamic_closure tests.test_host_command_sites \
  tests.hazards.test_refusal_allowlist tests.align.test_protocol_v4_doc
python3.13 -B scripts/align_v4_kit.py --check
git diff --check
```

- Repeat condition 13 with the approved comparator on the exact signing
  target using `python3.13 -B "$seat/check-condition13.py" "$SIGNED_W1_HEAD"`.
  Verify the accepted component diffs and final hashes, and have the
  independent auditor and research lead clear the signing gates. Run final
  exact-tree CI. The lead publishes the approved integration ref with
  `git push origin "HEAD:refs/heads/$W1_INTEGRATION_BRANCH"` after its normal
  audit and readback. For a lead-authorized fast-forward of the issued W1 ref,
  the following verifies both endpoints. `SIGNED_W1_HEAD` is the approved
  final commit after the receipt and gate bindings.

```sh
w1=refs/heads/ops/2026-11-11-w1-presign
issued=b2e01464d6d4fbf2901ff4d4154df9455104a12a
test "$(git ls-remote --exit-code origin "$w1" | cut -f1)" = "$issued"
git merge-base --is-ancestor "$issued" "$SIGNED_W1_HEAD"
git push origin "$SIGNED_W1_HEAD:$w1"
test "$(git ls-remote --exit-code origin "$w1" | cut -f1)" = "$SIGNED_W1_HEAD"
```

Then complete E3 and the lead-controlled PREQUAL sequence on the exact
candidate before the W1 smoke. [PREQUAL commands](../align/v4/W1-SMOKE.md#part-a-next-arm-prequal-air)

```sh
python3.13 -B scripts/align_v4_prequal.py --w1-next w1 --jobs 4 \
  --output "$W1_PREQUAL_OUTPUT" --series-projection "$W1_SERIES_PROJECTION" \
  --deadline-projection "$W1_DEADLINE_PROJECTION"
```

## NEEDS_SPEC

- **Inventory retention.** Choose how to preserve the 24 inherited
  upstream declarations while satisfying the exact W1 census. The proposed
  disposition is to record them as upstream-only review evidence and remove
  them from the active signing inventory with lead approval. The rehearsal
  keeps every row. The exact keys are in the seat's `host-sites-stale.tsv`.
- **Part C audit boundaries.** The builder's current handoff calls out the
  incomplete synthetic soak/gated census and the null derived exit slope on
  an unobserved gate. The independent auditor and lead own those dispositions
  and the accepted frozen-suite pin. They also own the compatibility
  disposition for the legacy W1 launcher fixtures. [PR #809 handoff](https://github.com/mpmdw/JouleWise/blob/cea5fb6957c8755c9596e94afb638f82357ff5be/docs/run_reports/2026-11-19-pr809-rl189.md#open-for-the-lead)
