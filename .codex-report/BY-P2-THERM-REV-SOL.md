gpt-6
VERDICT: ACCEPT

BY-P2-THERM independent executing review, 2026-10-28.

Reviewed `de35f6403e2e9e7ef335b92379b65a759a26e95c..defd9f9a3bfbf01f62fe66fc52c8e91c3e3edec5` and the builder's `.codex-report/BY-P2-THERM.md`. Authority: `docs/registrations/bytes_pack_v1.md` §21 item 3 at `93aad7b197b908b98682cbd0c508ac0ac4aa80fa`. Report branch: `codex/2026-10-28-by-p2-therm-rev-sol`, cut from `defd9f9a3`.

## Findings

No BLOCKER, MAJOR, MINOR, or NIT findings. No fixes requested.

## Executed

All Python execution used Python 3.13.5, `JW_B5_SYNTHETIC_ONLY=1`, and `PYTHONDONTWRITEBYTECODE=1`. Commands ran from `/workspace/JouleWise`; no compound command used `cd`. Only the two touched test modules and independent review scripts ran. No production BYTES archive, energy, or power value was read, and no hardware collection ran.

1. **Selection — `joulewise/b5/harvest.py:3990`.** Ran real `build_roster` with copied repository-shaped plan trees, including conflicting live and preserved copies. The preserved tree won in both directions. The committed-plan test also checked all six pass-2 trees, all six pass-1 trees, and the actual ALPHA/BETA/GAMMA trees. Pass 1, non-BYTES groups, and block 5 kept the hull. Missing `bytes_pass`, explicit null, strings `"2"`/`"two"`, Boolean values, lists, and objects did not select request-end. JSON numeric `2.0` did select it: Python numeric equality makes it equal to the specified `2`; this is not string coercion or a different pass. Missing or malformed whole trees left the selector false and recorded a harvest fault.

   Reproduction:

   ```sh
   JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -B /tmp/by_p2_sol_probe.py
   JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -B /tmp/by_p2_sol_selection.py
   ```

   Output excerpts:

   ```text
   SELECT 1 request_end False
   SELECT 2 request_end True
   SELECT None request_end False
   SELECT '2' request_end False
   SELECT 'two' request_end False
   SELECT True request_end False
   SELECT False request_end False
   SELECT {} request_end False
   SELECT [] request_end False
   SELECT 2.0 request_end True
   SELECT wrong group alpha/beta/gamma/null/list/dict: hull
   PRESERVED pass2 / live pass1: request-end selected from preserved copy
   PRESERVED pass1 / live pass2: hull selected from preserved copy
   EXPLICIT_NULL bytes_pass: hull
   MALFORMED_TREE '[]' selector false; harvest fault recorded
   MALFORMED_TREE 'null' selector false; harvest fault recorded
   MALFORMED_TREE '{not-json' selector false; harvest fault recorded
   MISSING_TREE selector false; harvest fault recorded
   ```

2. **Window — `joulewise/b5/harvest.py:6231`.** My independent script constructed controller clock-anchor metadata and idle-baseline/sentinel events, called real `member_spans`, serialized `joulewise.hazard_journal.v1` journals, and ran real `record_thermal_hull` and the `monitor_joins` member loop. Hull was [20 s, 100 s], request [40 s, 80 s]. Polls had 5 s cadence, including a separate stream with one 5.3 s gap.

   | Case | Pass-2 OS flag | Pass-1 OS flag |
   |---|---|---|
   | Nonzero only at 90 s, with clean request-end bracket | absent | present |
   | Same late-only case on shifted 5.3 s-gap stream | absent | present |
   | Inside request, 60 s | present | present |
   | Exactly request end, 80 s | present | present |
   | Before request but inside hull, 30 s | present | present |
   | Left bracket at 17 s on offset cadence | present | present |
   | Right bracket at 82 s on offset cadence | present | present |
   | Request span absent, nonzero at 90 s | present | present |
   | Reference member, nonzero at 90 s | present | present |

   The right bracket is deliberately counted even though it is after request end. A failed probe at 80 s, or a nonnumeric level there, correctly advanced the bracket to the successful numeric 85 s read. Independently tried `None`, string, Boolean, object, list, NaN, and infinity levels. A post-request coverage hole emitted exactly the same `thermal.unmeasured` record in both passes. The touched tests additionally covered missing journals, unknown hulls, clean hulls, and 780 deterministic subset cases without a request-end-only exclusion.

   Output tail from `/tmp/by-p2-sol-probe.log`:

   ```text
   WINDOW reference, failed and seven nonnumeric levels, full-hull unmeasured: PASS
   REFACTOR 1800 exact base comparisons: PASS; flag display 8 / hull evidence 17
   SOURCE stability after assessment-time read: records.source_changed_during_harvest
   CATALOG 01767fe4e75ed961798f4e6b68cf055a5b3946a474129e93d2b5e7c239a1dd0c
   ```

3. **Byte identity — independent rerun of the builder's replay.** Loaded the base harvest source using `git show de35f6403:joulewise/b5/harvest.py`. Base and reviewed code harvested identical synthetic sources at identical paths, with the same fixed audit clock, boot identity, and checkout-provenance seam. Compared every relative filename and every file byte, with no exclusions or normalization. The pass-1 replay included late thermal reads and the 5.3 s gap. Extended the builder's block-5/ALPHA replay to BETA/GAMMA groups in my own script.

   ```sh
   JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -B -m unittest -v tests.b6.test_bytes_p2_thermal_window
   JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -B /tmp/by_p2_sol_replication.py
   ```

   All five comparisons passed, **177 archive files per lane**, including raw copies, assessments, reductions, flags, exclusions, and harvest receipts. Manifest SHA-256 values:

   ```text
   pass1  da004d6a95f5d47051a0d20a0b36a97bde98eef74692020692eac56ecf90d998
   block5 cd77b10b353ed8810cb8029bf36d747dbffa84251802fbb470ab4619ab661ed1
   alpha  2bb40def210238452b868e9b30f42454ccfa90bbe0fda22e06afd872fb754341
   beta   a54d659865f97c92c4f1b4c6ab739ad68a99a02b091d95c323eb9676cedcf065
   gamma  2c4d51ee05bf7b782f693cc9aae30d96e5d932a6f568c47fc0492b97da0f7152
   ```

   These are replication-lane synthetic replays using the six-member strict-valid harvest fixture, not full collected replication archives. Real replication trees were exercised for selection separately. Manifest construction matches the builder: sorted relative path, NUL, and SHA-256(file bytes). Temporary absolute paths occur inside archive files, so these digests identify these executions, not portable golden archives. Ordinary invocations at different heads/times naturally have different provenance.

4. **Full-hull evidence and unchanged analysis — `joulewise/b5/harvest.py:4087`.** The new field records the hull span, exclusion result, all nonzero samples, and journal availability for assessed science members. Unknown spans are null. For an unavailable journal, `excluded: false` must be read alongside `journal_available: false`; it does not assert measured clean coverage. The existing `thermal.unmeasured` path remains responsible for missing coverage. References receive no new field; wholly missing science bundles already have their existing exclusion and no assessment to enrich.

   Built a separate 1,000-run, two-pass BYTES synthetic campaign through the existing real mock-trace reducer/archive fixture. Added production-shaped thermal journals, derived spans with `member_spans`, and ran the real member loop: pass 1 used the hull; pass 2 used request-end and carried 500 hull assessment records. Each model had one late-only repeat and one late-only quad member. Reopened the sealed assessment JSON, joined by session/run ID, ORed the hull outcome with existing exclusions, and called the bound `bytes_analysis.reduce_models` unchanged for the second set. Existing exclusions were preserved; the registered whole-quad behavior removed the other three quad members. No flag code was fabricated for the descriptive line.

   ```sh
   JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -B /tmp/by_p2_sol_analysis.py
   ```

   Output tail:

   ```text
   ANALYSIS ingress unchanged with additive assessments: 1000 records exactly equal
   ANALYSIS unchanged reduce_models: 40 primary / 40 hull rows; pass2 n_r,n_b 10,10 -> 9,9; pass1 9,9 unchanged; all computed
   member-hull OS window (pass-1 registered window): {"model": "Llama-3.3-70B-Instruct-4bit", "pass_id": 2, "n_r": 9, "n_b": 9, "mean_j": 204.0081184558639, "h_j": 0.1974905445931236, "B_j": 0.19366666666666255}
   ANALYSIS module unchanged sha256=18582818c7e03bad148b54dce8b8d60a62e2ffc5597e701ae3ab0418dffc0a71
   ```

   Thus the evidence is sufficient to supply the other exclusion set and print the required labelled line without changing the bound estimator. **This is not automatic CLI sensitivity support:** `bytes_analysis.load_records` at line 1098 treats an assessment filename as an archive locator; it does not interpret the new field. My small review adapter supplied the alternate record exclusions and printed the label. Wiring that presentation into an analysis workflow remains a consumer responsibility, not functionality delivered by this harvest diff.

   Catalog bytes are unchanged from the base, with SHA-256 `01767fe4e75ed961798f4e6b68cf055a5b3946a474129e93d2b5e7c239a1dd0c`. No new flag code or effect was added. Existing assessment readers in `b6/acceptance.py:460` and `b6/export_runs.py:567` select named fields and do not enforce an exact key set. Export's existing assessment checksum verification remains at `b6/export_runs.py:361`. Inspection found no projection of the new field into the blinded CSV. The field stays in the existing restricted assessment store; it introduces no energy or hidden-offset value or new access path. Analysis ingress equality was executed; acceptance/export reader compatibility was inspected, not claimed as an additional integration-test run.

5. **Refactor and sealing — `joulewise/b5/harvest.py:3062`, `:4079`, `:7624`.** Independently compared base and reviewed `thermal_member_flags` on 600 seeded noisy journals at three spans each: 1,800 exactly equal complete flag results, including failed probes and invalid/numeric levels. The selector preserves the old numeric conversion, success filter, ordering, bracketing, and nonzero test. Executed a case retaining 17 full-hull nonzero samples while the flag displayed only eight. The flag interval still derives from the complete list, as in the base.

   The extra journal read happens only for selected pass-2 packs and before the one-time assessment write. The assessment digest is created after enrichment and before member flags reference it; no sealed assessment is rewritten. Later monitor joins and source-stability checking remain in their original order. An independent persistent journal mutation after the assessment read was detected by real `sources_unchanged` as `records.source_changed_during_harvest`. This does not claim atomic filesystem snapshots or detection of a transient mutation restored before the final check; that is the existing stability mechanism's limit.

   Powermetrics-pressure emission in `member_flags` and battery/clock handling are untouched. The existing contention join already uses `request or member_span` at `harvest.py:6221`, identically on the base. I treated “everything else stays” as preservation of that registered existing behavior; I did not report an unchanged request-window contention rule as a defect introduced by this diff.

6. **Focused test results and numerical bars.** Actual test output tails:

   ```text
   # /tmp/by-p2-sol-new.log
   Ran 11 tests in 229.569s
   OK

   # /tmp/by-p2-sol-harvest.log
   Ran 187 tests in 464.330s
   OK (skipped=11)
   ```

   Second command:

   ```sh
   JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -B -m unittest -v tests.test_harvest_b5_window
   ```

   No new tolerance was introduced. Archive identity, base-flag equivalence, unchanged analysis ingress, field contents, and unit counts were checked exactly. Synthetic analysis numbers above demonstrate execution, not agreement against a numerical oracle. The existing campaign fixture internally retains its pre-existing `1e-6` relative/absolute mock-reducer sanity check; I added no such bar. The 5 s cadence and 5.3 s gap are test stream shapes, not acceptance tolerances. The existing 15 s coverage bar is registered in `configs/campaigns/v5_claim_25g83/registration_block5.md` and described at `harvest.py:219` as three 5 s polls; choosing three polls is inherited policy, with no new physical derivation supplied here. The eight-sample cap is display policy, and the five-unit minimum is unchanged registered policy.

   `git diff --check` passed. An inline review script called the repository's read-only fixture census and found `{"count": 0, "rows": []}`. No unrelated test modules or full suite ran. The known base `tests/test_b6_loop.py` failure was ignored as instructed; that file was not edited or executed.

## Review artifact locations

The independent scripts and their logs remain local `/tmp` review artifacts; they are not repository changes. Reproduction commands above refer to those files in this workspace. Script SHA-256 values:

```text
eacb8b130fec3f8e8e56d41213b1213f0f6e7598a97da771d043c28289e11080  /tmp/by_p2_sol_probe.py
01c230f297656b61f35bd619e7312f2f60cad4ed9628b7f74a512759a13bbfcc  /tmp/by_p2_sol_selection.py
7a4d93b187b20ec551cdcd94e0f84d7bf3b42768a815f9c736291587647f3c92  /tmp/by_p2_sol_analysis.py
58143ef41a5980a9a20609794ddd52a5eaa3ab3ffc4647b6cab498b791fcbb2b  /tmp/by_p2_sol_replication.py
```

Logs: `/tmp/by-p2-sol-{new,harvest,probe,selection,analysis,replication}.log`. Temporary generated data was cleaned by the fixtures. The analysis script was tightened after an initial successful demonstration so only pass 2 carries the new field and pass 1 uses its registered hull. No implementation change was made.

## Decisions I made

- Reviewed and executed the pinned diff independently; did not delegate or consult the other blind reviewer.
- Used the corrected authority at `93aad7b19`; did not treat the builder's report as authority.
- Used the preserved plan values and exact specified equality; did not invent pack-name inference, string coercion, a new integer-type rule, tolerance, or thermal threshold.
- Kept missing-observation indicators and existing exclusions when reconstructing the descriptive hull set. Did not use flagged-inclusive reduction as a substitute, since that would restore unrelated excluded members.
- Distinguished executed synthetic replays and analysis from static reader inspection and from live validation. Ordinary provenance differences were controlled only through the same explicit audit seams as the builder's replay.
- Kept repository writes to this report. Did not edit implementation, tests, registrations, state/queue documents, or the known base failure. Commit/push authority came from the user's explicit request; no merge or PR comment is authorized or attempted.
- Used the cloud-environment runtime skill for environment/network setup. `gpt-6` is the model family disclosed by this session's instructions; a more precise served-model identifier was not exposed, so I have not invented a suffix.
