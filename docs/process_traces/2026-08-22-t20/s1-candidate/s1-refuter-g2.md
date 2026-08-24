```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "REFUTED: 1 blocker, 3 should-fix findings, and 1 nit.",
  "workspace": {"base_requested":"55230038dd517e250e47d0685b093110f610b3e8","base_mode":"exact","head_start":"c1b87f63fd47507dd1504693ad45347a4f2c55aa","head_end":"c1b87f63fd47507dd1504693ad45347a4f2c55aa","upstream_end":"c1b87f63fd47507dd1504693ad45347a4f2c55aa","branch":"impl/s1-candidate"},
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "final": "REFUTED",
    "blocker_count": 1,
    "findings": [
      {"id":"G2-1","severity":"blocker","title":"Caller-authored C plus a self-sidecar impersonates Ed","anchors":["docs/contracts/d117_step6_confirmation_table.md:21","joulewise/arm_readiness.py:4226","joulewise/arm_readiness.py:10057","joulewise/arm_readiness.py:10433","joulewise/arm_readiness.py:10591"],"attack":"Render C with literal ED/YES and attacker S/M digests, then render C.sha256 from C. No consumer receives Ed's confirmed hC, so subtraction and publication accept the forgery."},
      {"id":"G2-2","severity":"should_fix","title":"Conditional refusal escapes arm/G7 raw","anchors":["joulewise/arm_readiness.py:1055","joulewise/arm_readiness.py:6357","joulewise/arm_readiness.py:7310","joulewise/arm_readiness.py:10199","joulewise/scheduler_gates.py:908"],"attack":"Omit or corrupt C after fixation; EvidenceLifecycleError escapes instead of becoming a governed refusal."},
      {"id":"G2-3","severity":"should_fix","title":"Unenumerated pinset override can return PASS","anchors":["joulewise/arm_readiness.py:3174","joulewise/arm_readiness.py:3367","scripts/verify_receipt_histsem.py:25"],"attack":"Pass an unenumerated copy via pinset_path/--pinset; the public verifier returns PASS."},
      {"id":"G2-4","severity":"should_fix","title":"Missing generation threshold disengages freeze gate","anchors":["joulewise/arm_readiness.py:1852","joulewise/arm_readiness.py:6554","joulewise/arm_readiness.py:6574"],"attack":"A threshold-less v2 registry validates; freeze sets threshold=None and skips publication."},
      {"id":"G2-5","severity":"nit","title":"G7 records mutable post-verify re-reads","anchors":["joulewise/scheduler_gates.py:865","joulewise/scheduler_gates.py:892"],"attack":"Swap custody paths after verification; the PASS block can bind unverified bytes."}
    ]
  },
  "verification": [
    {"id":"V1","kind":"inspection","cmd":"git diff --no-ext-diff --no-color 5523003...HEAD","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["27 files changed, 6295 insertions(+), 140 deletions(-)"]},"expected":{"exit_code":0,"tail_regex":"27 files changed"}},
    {"id":"V2","kind":"test","cmd":"python3 -m unittest -v <12 focused security tests>","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 12 tests in 1.799s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 12 tests.*OK"}},
    {"id":"V3","kind":"test","cmd":"python3 -m unittest tests.test_receipt_histsem tests.test_family_marker tests.test_scheduler_gates","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 77 tests in 108.628s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 77 tests.*OK"}},
    {"id":"V4","kind":"other","cmd":"adversarial override/exception/closure probe","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["UNENUMERATED_OVERRIDE PASS","FAMILY_MEMBER_PROPAGATES EvidenceLifecycleError","G7_PROPAGATES EvidenceLifecycleError","REGISTRY_CLOSURE 8 True","G7_CLOSURE 29 True"]},"expected":{"exit_code":0,"tail_regex":"G7_CLOSURE 29 True"}}
  ],
  "flags": [
    {"id":"F1","kind":"verification_gap","level":"nonblocking","text":"Real S-0 _v4 packs are absent, so literal end-to-end GO was unavailable; the blocker was directly replayed at the subtraction boundary.","needs":"Add an S-0 end-to-end falsifier with independently supplied Ed-confirmed hC."}
  ]
}
```

## Findings

Final verdict: **REFUTED — 1 blocker**.

1. **G2-1 — blocker — Ed's confirmed table digest is never authenticated.** The contract says Ed confirms `hC = SHA256(C)` over the exact final table bytes (`docs/contracts/d117_step6_confirmation_table.md:21-25,37-41`). No relevant API accepts that expected digest. `_read_external_canonical` only hashes supplied bytes and checks a sidecar derived from the same bytes (`joulewise/arm_readiness.py:10433-10443`); the validator treats literal `authority == "ED"` and `decision == "YES"` as confirmation (`:10057-10068`). The subtraction then compares committed S only to the digest inside caller-supplied C (`:4226-4247`), and marker replay repeats the same trust (`:10591-10620`).

   Attack: commit attacker S; render canonical C with the actual S digest, actual Git/registry/member values, and literal ED/YES; render `C.sha256` from C. If publication is needed, render M from actual pack bytes and put `sha256(M)` into C. Nothing requires Ed or an independently supplied `hC`. The candidate's own test manufactures C this way and successfully subtracts S (`tests/test_receipt_histsem.py:579-605`). With otherwise valid S-0 packs, forged M+C also passes the direct arm publication gate and G7.

   The other (a) attacks survive narrowly: `None` refuses (`:4221-4224`); missing/malformed C is converted to `DEPENDENCY_CHANGED_SET` inside the helper (`:4225-4235`); wrong path/schema is rejected (`:10036-10045`); wrong digest is rejected; the digest covers the blob at immutable `current_head`, not marker/worktree bytes (`:4236-4247`); and `outstanding.discard` occurs only after the helper returns (`:4297-4306`). There is no narrow check-to-discard TOCTOU because both C's parsed section and the Git blob are in memory. Marker replay does read mutable C multiple times for different edges, so one authenticated, single-snapshot C is still required.

2. **G2-2 — should-fix — missing/bad C can fail ugly.** `EvidenceLifecycleError` is not an `ArmReadinessError` (`arm_readiness.py:1028-1055`). It can leave `_load_freeze_reference` at `:6357-6369`; direct arm calls that loader before its later lifecycle catches (`:7310-7317`); `_family_member` catches only `ArmReadinessError` there (`:10199-10211`); and G7 does not catch `EvidenceLifecycleError` (`scheduler_gates.py:908-938`). The probe reproduced raw `readiness_r1_dependency_changed_set` from both marker replay and G7. This is not GO, but it is an explosion instead of clean refusal.

3. **G2-3 — should-fix — unenumerated pinsets govern the override lane.** Admission correctly iterates only the constant tuple and refuses cross-member duplicates (`arm_readiness.py:3651-3699`). However, supplying `pinset_path` replaces the tuple with an arbitrary file (`:3174-3180`), and both public verifiers plus CLI expose it (`:3367-3371`; `scripts/verify_receipt_histsem.py:25-49`). The probe copied a valid pinset to unenumerated `receipt_histsem_pinset_rogue.json` and got `PASS`, contradicting the unqualified closed-enumeration contract (`receipt_histsem_verifier.md:28-31`). This is should-fix because arm/freeze admission has no override.

4. **G2-4 — should-fix — dormant threshold fails open at freeze.** The threshold is optional and a v2 registry without it validates (`arm_readiness.py:609-617,1833-1857`; `tests/test_family_marker.py:419-430`). Freeze catches the missing-threshold error, sets `None`, and skips publication (`:6554-6578`). A future roster edit with an omitted/mis-stated threshold can freeze over an unpublished predecessor. The current committed registry contains `4`, so today's v5-over-v4 predecessor gate engages.

5. **G2-5 — nit — G7 has a receipt-binding TOCTOU.** It verifies at `scheduler_gates.py:865-875`, then re-reads marker/table paths for recorded digests at `:892-903`. A swap can make a PASS block bind bytes not verified. The load-bearing arm replay prevents this alone from authorizing an arm.

Lens survival details:

- **(b):** exact keys and within-member identity uniqueness are enforced at `arm_readiness.py:3065-3171`; both chain readers reject cross-member duplicates; absent members continue and all-absent returns normally. The settled committed-deletion test (`tests/test_receipt_histsem.py:445-467`) passed.
- **(c):** direct arm appends the registry CUSTODY refusal on publication failure (`:7342-7357`), verification mirrors it (`:7565-7580`), and freeze gates the predecessor before writes (`:6574-6599`). Marker absence cannot disengage a current roster member (`:10735-10751`). Histsem's `require_published=False` is the separately ruled pre-arm ancestry advisory, not the family marker gate (`receipt_histsem_verifier.md:80-94`). G2-1 breaks authenticity; G2-4 is the dormant edge.
- **(d):** `readiness_r1_family_publication` is registered and typed CUSTODY (`:203,216-242`). Registry load closes code/type at `:1946-1957`; all 8 roles closed. All 29 marker diagnostics map to one of 6 registered CUSTODY G7 codes (`scheduler_gates.py:100-140,836-847`); all 29 closed. No unregistered new code was found. G2-2 is exception routing, not vocabulary mismatch.
- **(e):** the registry has 112 sorted unique paths: one legitimate successor pinset and zero table, family-publication, test, or `PINSET_SHA256` paths. Both changed-set contracts explicitly prohibit C from allowlists (`d117_step6_confirmation_table.md:8-12`; `receipt_histsem_verifier.md:146-152`). Condition 7 survives.

## Residual risk

The three real `_v4` packs/custody artifacts are S-0 outputs and absent at this head, so literal end-to-end direct-arm GO was not runnable. The exact subtraction path, every current consumer, 12 focused tests, and all 77 receipt-histsem/family-marker/scheduler tests were replayed. The full repository suite was not rerun for this read-only security lens.

BRIDGE_REPORT_V1
{"status":"DISCUSSION","summary":"REFUTED: 1 blocker; Ed's externally confirmed step-6 table digest hC is never authenticated, with 3 should-fix findings and 1 nit.","pathspec":[],"verification":["full 5523003...c1b87f6 diff and rulings inspected","12 focused security tests: OK","77 relevant tests: OK","adversarial probes reproduced override and raw-exception defects; closures 8/8 and 29/29"],"flags":["no_repo_edits","one_blocker","s0_real_v4_artifacts_unavailable"]}
