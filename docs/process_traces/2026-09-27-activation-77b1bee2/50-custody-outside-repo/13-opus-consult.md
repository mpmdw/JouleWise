# ISSUANCE-CUSTODY-OUTSIDE-REPO-01: Opus 5.5 blind consult

Seat: opus. Read-only; blind to the other seats. I stayed outcome-blind: I opened no `b_fiducial_s`, no ledger value field, and no value field in `manifest.json` or `instrument_evidence.json`. The only ledger fields I projected were `custody_locator` and `attempt_id`. My scratch probes used synthetic files under `/tmp/custody-consult-opus-77b1bee2/`. Tree: `/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2` @ `670756f3`; it was clean when I finished.

## Terms, built before use

- **Member directory**: one capture's evidence folder, for example `.../d079-epoch-25g83-derivation-w1-20260927/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-d01`. It holds `manifest.json`, `instrument_evidence.json` and `raw/powermetrics.plist`.
- **`source_directory`**: the string the issued artifact stores for each member. A verifier later joins it onto a root directory that the verifier's caller supplies (`root / source_directory`). It then re-hashes the two primary files against the SHA-256 digests the artifact stores for that member.
- **Corpus root**: the root directory in that join. Today the issuer requires it to be the git checkout (`repo_root`).
- **Night root**: the runbook's own name for the per-night directory `/Users/edr/night-custody/<PLAN_ID>`. The night plan calls this `custody_root` (runbook :227, :410, :919). This naming matters for the flag name, as the second SHOULD-FIX below explains.

## 1. Design choice, and corrections to the scout's map

**I recommend C: a declared corpus-root parameter on the issuer only.** It is the smallest version of A. The issuer gains `--corpus-root` (default: `--repo-root`). Each `source_directory` is stored relative to it. For this corpus the operator passes `/Users/edr/night-custody`, which gives members such as `d079-epoch-25g83-derivation-w1-20260927/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-d01`. The first path component is the night's plan ID, so each path names its own night.

C needs no new resolver in the verifier or in reissue, because both **already** take a caller-supplied root. This is the main correction to the scout's map:

| Consumer | Scout said | Actual (evidence) |
|---|---|---|
| Corpus verifier | Must learn to "select that logical root from a caller-supplied archive location" | It already does. `verify(repo_root, artifact)` joins `repo_root / member["source_directory"]`, then resolves and contain-checks it (`tests/verify_calibration_acceptance_corpus.py:84-86`). `--repo-root` is simply a caller-supplied root (:160). Probe P3 shows the equivalent reissue path authenticating two sibling night roots from their common parent with **no code change**. |
| Reissue tool | "One root is supported, but no artifact-declared map selects external night roots" | That single root is enough. `--corpus-root` (alias `--repo-root`) is documented as "root containing the predecessor's source_directory paths" (`scripts/reissue_calibration_acceptance.py:559-567`). A reader who places both night roots under any one parent can verify them (P3). |
| Production validator | Needs a change to accept the descriptor | Under C, no change is required. It checks only that `source_directory` is a `str` (`joulewise/calibration_bracketing.py:885`), and it checks no key set on `derivation_corpus` or on the top level. A hardening change is optional; see §2. |
| Issuer `check` dry run | Not listed | **Missed consumer, and a false GO.** The dry run reads member evidence (`scripts/issue_calibration_acceptance_generation.py:305-317`) but never calls `_repo_relative_custody`. So it printed `registration admissible for prepare-candidate: yes`, although all 24 members will refuse (the scout's own executed evidence shows both facts). |
| Issuer `--repo-root` | Replace `_repo_relative_custody` with a custody-root check | Correct, but the scout did not show why pointing `--repo-root` at `/Users/edr/night-custody` fails. `--repo-root` does two jobs. It is the path base, and it is the git checkout from which the battery verdicts are loaded: `authenticate_battery_epoch(repo_root=…)` (:1380-1400) calls `battery_float.load_committed_verdict(repo_root, …)`, which runs `_git(root, "show", f"HEAD:{rel}")` (`joulewise/battery_float.py:563-587`). `/Users/edr/night-custody` is not a git repository, so a separate parameter is necessary. |
| r6/r7 custody | "Sampled directory is absent from both this checkout and W2" | True for those two trees, but misleading. The `runs_window_a*_2026072x` directories exist, untracked, in the canonical checkout `/Users/edr/code/JouleWise`. Meanwhile the ledger's `custody_locator` for those same members points at a **flattened** iCloud layout: `~/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup/runs-20260727/instrument_validation/<id>`. Of the ledger's 86 locators, 38 are in iCloud (probe P0). So r6/r7 can be re-verified today only from one machine's untracked directories. The bar in the charge ("repository plus archived night roots") is **stricter** than anything r6/r7 ever met. C meets it. |
| Precedent | "No issuance-side resolver found" | **Missed precedent.** r3 through r7 each carry `derivation_notes.derivation_method.corpus_root: "/Users/edr/code/JouleWise"`, which records the root as provenance and is not machine-consumed (`configs/calibration/calibration_acceptance_d079_v2_n17_r6.json:520`). r6 also records the sanctioned principle, in its own words: *"Location is not authority; content identity is"* (`raw_custody` note, r6 :523). C follows that precedent exactly: it records the root as provenance and lets the digests carry the authority. |

**Why not B.** Per-night roots only add something if a reader cannot put the two night archives under one parent directory. Any reader can: `mkdir parent; extract W1 and W2 into it`. B adds a member key, which breaks the validator's exact member key set at `calibration_bracketing.py:876-883`. It also adds an ID-to-path map to the CLI and a larger test surface, all for no verification power beyond C.

**Why not A as written.** A's validator-enforced logical `source_root` descriptor adds a load-time check that cannot prove anything about custody, because the loader never opens a member directory. It costs a generation-conditional validator branch and does nothing that C's provenance note and the digests do not already do.

## 2. Minimum change set

The C change set is 1 BLOCKER-fix and 2 SHOULD-FIX items, all value-free.

1. **Issuer, BLOCKER-fix.**
   - Generalize `_repo_relative_custody(locator, attempt_id, repo_root)` (:896-912) to `_root_relative_custody(locator, attempt_id, corpus_root)`. The body is unchanged: `Path(locator).resolve().relative_to(Path(corpus_root).resolve()).as_posix()`, and it refuses otherwise.
   - Thread `corpus_root` through `_select_members` (:1203-1247) and its caller (:1828).
   - Add `prepare.add_argument("--corpus-root", type=Path, default=None)` next to :2386. `None` means `args.repo_root`, which keeps r6-era behaviour byte-identical.
   - Also apply the projection in `check` (:305-317), so that the dry run's "admissible" verdict covers member paths too.
   - Move the projection **before** `_read_member_evidence` in `_select_members`, so that a path refusal can never fire after a member value has been loaded (NIT-grade hygiene; nothing is printed either way).
   - Never skip a member whose locator lies outside the root: the whole preparation refuses, as it does today.

2. **Artifact schema delta (issuer-emitted, provenance only).** In `derivation_notes`, following the r3–r7 `derivation_method.corpus_root` precedent, add:
   ```json
   "corpus_root": {"relative_to": "caller-supplied corpus root",
                   "issuance_path": "/Users/edr/night-custody",
                   "layout": "<plan_id>/runs/instrument_validation/<attempt_id>",
                   "verify": "tests/verify_calibration_acceptance_corpus.py --repo-root <directory holding both plan-id directories> --artifact <this file>"}
   ```
   This key falls inside `derivation_sha256` (the whole-artifact digest at :2244) and therefore inside the D-138 byte pin. It stays outside `derivation_input_sha256`, which by design excludes paths (:2258). No new member key is added, and the validator is untouched.

3. **Consumer hardening, SHOULD-FIX (small).** Probes P4 and P9 show that both consumers **accept an absolute `source_directory` that happens to lie under the supplied root**. `pathlib` discards the root, and the containment check then passes on this machine. That is exactly the hazard the issuer's docstring warns about (:899-903). Add one guard to `verify` (:85) and to `authenticate_derivation_corpus` (:173):
   - refuse unless `not PurePosixPath(sd).is_absolute()`;
   - refuse if `sd` has a `..`, `.` or empty component;
   - refuse unless `sd.rsplit("/",1)[-1] == member_id` (the verifier lacks this basename check; reissue has it at :176).

   Optionally add the same predicate to the validator at `calibration_bracketing.py:885`. I probed all seven issued artifacts in `configs/calibration/` (v2, r2, r3–r7): **0 of 123 members** violate it, so r6/r7 and every older pin stay valid and unchanged.

**How r6/r7 stay valid unchanged.**
- Their bytes and pins are not touched.
- The issuer default (`--corpus-root` absent) keeps the repo-relative behaviour.
- The verifier and reissue keep the same flags and semantics.
- The new guard admits all of their paths (probe above).

**What a future reader can re-verify, and how.** The reader needs the repository and the two archived night roots. They place both plan-ID directories under any directory `P` (physically, not through symlinks; see §3). Then they run `python3 tests/verify_calibration_acceptance_corpus.py --repo-root P --artifact configs/calibration/<new>.json`. For each of the 12 members this re-hashes `manifest.json` and `instrument_evidence.json`, checks the content-id link to `prior_observation_set`, and recomputes the statistics against a banked expectation. The banked `EXPECTED_BY_ACCEPTANCE_ID` entry for the new acceptance ID (verifier :24-65) is value-bearing, so it is added inside the D-138 transaction, not in this repair. `scripts/reissue_calibration_acceptance.py --corpus-root P` does the same for the reissue path.

## 3. Science and custody risks

- **Can a choice depend on measured values? No, under C.** The root is one fixed parent, named by the runbook before the arm. `source_directory` is a pure string function of the ledger locator and that root. Membership still turns only on the ledger disposition and the anchor-v3 replay outcome (:1216-1233). Any locator outside the root refuses the whole run and never drops a member, so no path choice can change which members are counted. Rerunning `prepare-candidate` after today's refusal is not contaminated either: the refusal text contains only the locator and the attempt ID (:909-912).
- **Evidential chain: intact, and unchanged.** The issuer still reads the bytes at the ledger's absolute `custody_locator`. It authenticates them against the row's `artifact_sha256` (:1033-1052) and checks `raw/powermetrics.plist` against its ledger hash (:1508-1513), before any path projection matters. The artifact then pins each member's two primary digests, and every later verification re-hashes them. So the chain runs: ledger row, then the `instrument_evidence.json` digest, then the raw bytes. The path is only a way to find the files and never a source of trust.
- **Archive, iCloud offload and relocation after issuance.** These are safe under one condition: preserve the sub-path `<plan_id>/runs/instrument_validation/<attempt_id>`. The historical offload broke exactly this. It flattened `runs_window_a*/instrument_validation/<id>` into `runs-20260727/instrument_validation/<id>`, which is why r6/r7 verify only from the canonical checkout. SHOULD-FIX for the archive runbook, not the code: archive whole plan-ID directories and keep a `MANIFEST.sha256` listing each `source_directory` and its digests. With that done, relocation is free, because the root is supplied at verification time.

  Two failure modes remain, and both fail loudly rather than silently:
  1. A file that iCloud has evicted (downloaded on demand) raises `OSError` when offline, and the member fails authentication.
  2. A reader who assembles `P` as a **symlink farm** is refused, because `resolve(strict=True)` follows the link and `relative_to(root)` then fails (probe P6).

  The ledger's `custody_locator` goes stale once custody moves, since the ledger is append-only. That is the same state the 38 historical iCloud rows are already in. It only matters to a future issuer that re-reads these rows as members, and that issuer would face the same question again.
- **Runbook compliance.** Nothing is copied, moved, symlinked or re-rooted. The unissued-epoch rule ("never moved, relocated or offloaded", runbook :2569) is untouched.

## 4. Defect-shaped tests (`tests/test_issue_calibration_acceptance_generation.py` plus the two consumers)

- **RED today, GREEN after.** Build a synthetic fixture: a ledger in a git checkout `T/repo`, and two sibling night roots `T/nc/planA/runs/instrument_validation/planA-d01…` and `T/nc/planB/...`, both **outside** `T/repo`. Run `prepare-candidate --corpus-root T/nc`.
  - Today this refuses with "lies outside the repository" (probe P1 reproduces it with the real helper).
  - After the change, assert that it emits `planA/runs/instrument_validation/planA-d01`-shaped paths, that `derivation_notes.corpus_root.issuance_path == str(T/nc)`, and that `verify(T/nc, candidate)` and `authenticate_derivation_corpus(candidate, corpus_root=T/nc)` authenticate every member.
  - Then move `T/nc` to `T/moved` and verify again from `T/moved`. This proves relocation works.
- **The `check` false GO.** The same fixture without `--corpus-root` must make `check` print a member-custody blocker and not `admissible … yes`. This is RED today.
- **Default preserved.** The existing `test_custody_outside_the_repository_refuses` (:1539) and `test_member_source_directory_is_repo_relative_and_re_resolves` (:1518) stay GREEN unchanged.
- **Refusal cases.** Each is exercised in the issuer, the verifier and reissue. Today's behaviour comes from my probes P4–P9 against the real reissue function.

| Case | Setup | Today | After the change |
|---|---|---|---|
| Undeclared root | `--corpus-root` absent, or a root that one member lies outside | Refuses (P1) | Must refuse the whole run, not drop the member |
| `..` | `source_directory = "../elsewhere/<id>"`, with the target existing | Refused by containment (P5′) | Also refused earlier, by the canonical-path guard |
| Absolute path | Absolute path under the root | **Accepted** (P4, P9); this is the defect | Refused |
| Symlink escape | A symlink inside the root pointing outside it | Refused (P6) | Keep refusing |
| Wrong basename | Directory name differs from `member_id` | Reissue refuses (P7); the verifier has no such check | Verifier also refuses |
| One-byte mutation | Flip one byte in the second member's `manifest.json` | That member fails and the other passes (P8) | Verifier raises `manifest sha256 mismatch` |

- **Mutation cut.** Revert the projection to `repo_root` (collapse `corpus_root` to its default operand). The RED test must fail. Delete the absolute-path guard. P4 must fail.

## 5. Reasons not to change code

I found no already-sanctioned mechanism that makes a code change unnecessary.
- Pointing `--repo-root` at the parent breaks the battery-verdict git reads (§1).
- Repo-relative `../../d079-…` paths from the measurement root at `/Users/edr/night-custody/measurement/…` would require removing the containment check, which is worse.
- The r6 precedent (a provenance root, with authority resting on content digests) is the sanctioned *pattern*, and C adopts it.

The change is small and value-free: one helper generalized, one flag, the dry run aligned, one provenance note, and two consumer guards. It does not alter selection, statistics, or the input seal.

## Findings

- **BLOCKER B1.** The issuer cannot express a non-repo corpus root. `_repo_relative_custody` (:896-912, called at :1244) is tied to `--repo-root`, which is also the battery-verdict git checkout (`battery_float.py:587`). Probe P1 refuses 2/2 synthetic members; the scout counted 24/24 real ones. **Cure:** C, item 1.
- **SHOULD-FIX S1.** The `check` dry run gives a false GO. It never projects `source_directory` (:305-317), so it reported `admissible … yes` while all 24 members will refuse. **Cure:** run the same projection in the dry run.
- **SHOULD-FIX S2.** The verifier (:85) and reissue (:173) accept an absolute `source_directory` under the supplied root (P4, P9 True). The verifier also lacks the basename check. **Cure:** add a canonical relative-path guard. 0 of 123 issued members would be affected.
- **SHOULD-FIX S3.** The flag name `--custody-root` in the scout's A collides with the runbook's `custody_root`, which means the per-night root (runbook :227, :919). Name the parent root `--corpus-root`, matching reissue (:562).
- **SHOULD-FIX S4.** Archive and offload plans must preserve `<plan_id>/runs/instrument_validation/<attempt_id>` and ship a digest manifest. The r6 corpus shows what happens otherwise: its offload flattened this layout, and r6 now verifies only from the canonical checkout's untracked directories.
- **NIT N1.** Scout map corrections: the verifier and reissue need no resolver change; the validator needs no change; the r3–r7 `derivation_method.corpus_root` precedent was missed; and "sampled r6 directory absent" holds only for the scout and W2 trees, not the canonical checkout.
- **NIT N2.** Hoist the path projection above the evidence read in `_select_members`.
- **NIT N3.** Alias the verifier's `--repo-root` as `--corpus-root`, for honesty of naming.

## Executed probes (synthetic, `/tmp/custody-consult-opus-77b1bee2/probe.py`, `probe2.py`, real module code from the scout tree)

```text
P0 ledger locator projection (W2 ledger; custody_locator + attempt_id only):
   86 unique locators; 24 under night-custody w1/w2 (basename == attempt_id 24/24);
   38 under ~/Library/Mobile Documents/.../JouleWise-backup/runs-20260727/instrument_validation/
P1 issuer today REFUSES: member plan-w1-d01: custody ... lies outside the repository (x2)
P2 relative to custody parent: ['plan-w1/runs/instrument_validation/plan-w1-d01', 'plan-w2/runs/instrument_validation/plan-w2-d01']
P3 reissue authenticates from parent: [True, True]        # no code change
P4 absolute path UNDER root: [(True, '')]                  # defect S2
P5' existing '..' target: False '... is not in the subpath ...'
P6 symlink escape: [(False, '.../elsewhere/...')]
P7 wrong basename: [(False, 'source directory basename does not equal member_id')]
P8 one-byte mutation: [('plan-w1-d01', True, 'PASS'), ('plan-w2-d01', False, 'FAIL')]
P9 verifier join accepts absolute source_directory under root: True   # defect S2
Issued-artifact canonical-path audit: v2, r2, r3, r4, r5, r6, r7 -> bad: 0 each (123 members)
```

RECOMMEND: C
