VERDICT: PROCEED-AFTER-DICTATED-CLOSURES

Cold Fable 5.1 ruling on lane A277 (ZERO-CAPTURE-EVIDENCE-WRITER-01), branch feat/2026-09-23-a277-successor-facts at 408b96c3, base 313efcca. Judged from records 04, 05, 06, 07, 34, 35, 36, 43 and from what I executed in a detached worktree at 408b96c3 plus scratch copies made with `git archive` under /tmp/fable277 (the worktree was never edited; `git status` clean at the end). No launchctl, sudo, night-custody or measurement path was touched; the only launchctl-related act was `shutil.which("launchctl")` and `os.path.samefile` on the binary's path.

Executed closure diffs (apply cleanly to 408b96c3, checked with `git apply --check`):
- .seat-out/47-fable-ruling-a277-closure-evidence_night.diff (joulewise/evidence_night.py)
- .seat-out/47-fable-ruling-a277-closure-arm_retry.diff (joulewise/arm_retry.py)
- .seat-out/47-fable-ruling-a277-closure-tests.diff (tests/test_evidence_night.py, tests/test_arm_retry.py, tests/test_zero_capture_facts.py)

## Q1. F1 and F2: confirmed by execution; closures dictated

**F1 CONFIRMED.** Probe (subclass of `tests.test_evidence_night.LifecycleTests`, real fixture tree, release latched, installer runner mocked, `entry.run` patched for the LaunchctlAdapter probe):

```
F1 check:   {'fake_launchctl': True, 'rehearsal_ready': True, 'armable': False, 'successor': 'pass'}
F1 publish: {'outcome': 'rehearsal_installed', 'installed': False, 'fake_launchctl': True,
             'claim_exists': False, 'installer_launchctl_args': ['/bin/launchctl', '/bin/launchctl']}
```

With `launchctl_bin="/bin/launchctl"` the check records a rehearsal, publish_install records `rehearsal_installed`, creates no claim, skips the production-veto requirement, and hands `--launchctl-bin /bin/launchctl` to the installer, which resolves it with `shutil.which` and would drive the real launchd (night_agent_install.py:1249-1252). This classification (`str(launchctl_bin) != "launchctl"`) predates A277 and already skipped the veto gate at 313efcca; A277 added a second safety gate on it, so it is now a blocker and must close in this lane.

**F1 closure (executed):** one classifier, `rehearsal_launchctl(launchctl_bin)` in evidence_night.py, replaces all four `str(launchctl_bin) != "launchctl"` sites (check, verify_state, require_fresh_check, publish_install). Rule: the literal `launchctl` is the only real spelling and returns False. Any other spelling is resolved the way the installer resolves it (absolute path as given, otherwise `shutil.which`) and compared with the real binary (`os.path.samefile` or equal `Path.resolve()`); if it is the real binary, the call raises `Refused("real launchctl must be spelled exactly 'launchctl'; a path to it is not a rehearsal: ...")`. Only a spelling that is not the real binary is a rehearsal. "Rehearsal" is therefore determined by resolving the path, not by a caller flag, and the ambiguous case refuses instead of being classified either way. Because check refuses before writing check.json, and require_fresh_check and publish_install refuse again, a real publication can only ever run under the literal spelling, and the claim gate `if not fake` is then exactly "real publication". The rehearsal regression from Z5 keeps its meaning.

Regression `test_f1_real_launchctl_under_another_spelling_is_refused_not_rehearsed` (skipped if no launchctl on PATH): check with the real path, with a symlink to it, and with its resolved path each refuse with that message and write no check.json; `/fixture/launchctl` still yields `rehearsal_ready`; publish_install under the real path refuses before the installer runner is ever called and no claim exists. Counterfactual at 408b96c3: FAIL (executed). Mutant "compare never matches" (`if False:`): killed.

**F2 CONFIRMED.**

```
F2 before removal: pass pre:decessor
F2 after removal (colon id): pass None None
F2 control (plain id) after removal: fail released predecessor custody is missing
```

The watchdog key is `f"{plan_id}:{custody_root}:{sha256}"` (magistrate_watchdog.py `_release_key`); `split(":", 2)` in successor_check misreads a plan id containing a colon, so the missing-custody guard is silently skipped and a fresh candidate passes with no predecessor and no claim. Plan ids are only required to be non-empty strings (night_gate.py:424).

**F2 closure (executed), two parts:**
1. `_release_key_interpretations(key)`: anchor the trailing `:[0-9a-f]{64}` digest with a fullmatch, then enumerate every colon split of the remainder as a `(plan_id, custody_root)` pair. The guard refuses if ANY interpretation names a custody root whose resolved parent is this night-custody root, whose `night_plan.json` is missing, and whose plan id has no expired claim. Ambiguity therefore fails closed; a malformed key (no digest, no colon, non-string) refuses as before. The watchdog's key format and the live state.json are untouched (the watchdog only compares whole keys, lines ~840 and ~1538, never parses them).
2. The claim-file-name guard (`[A-Za-z0-9][A-Za-z0-9._-]*`) is also applied in successor_check to the released predecessor's plan id, so a predecessor whose id cannot name a claim file fails the `successor` row at check time with "predecessor plan id cannot name a successor claim" instead of failing inside publish_install after `phase = "publishing"` was saved.

Regression `test_f2_colon_in_plan_id_keeps_missing_custody_guard`: the colon-id predecessor fails at check with the claim-name reason; after `rmtree` it fails with "released predecessor custody is missing"; the interpretation helper's outputs and four malformed keys are pinned. Counterfactual at 408b96c3: FAIL (executed).

## Q2. F3, F4, F5 dispositions

**F3: fix now, on the successor route only; release semantics stay as ruled.** Executed at 408b96c3: an empty `conditions` list gives `watchdog_release=True, successor=pass`. I first tightened `terminal_zero_capture_refusal` and the existing watchdog test `test_f3_receipt_without_c5_does_not_license_or_veto` (tests/test_magistrate_watchdog.py, from commit 3e27057a, cold ruling 16 Q1: "receipt keeps only its veto role", zero capture established from custody) failed. That release behaviour is a standing ruling and stays. The dictated closure therefore lives in `successor_license` after the terminal check: the receipt must carry exactly one `C5` row (the driver writes every refusal receipt with C1-C5, run_night.py ~1869; C5 is the row D-182 names), else `malformed_successor_evidence`. Regression `test_f3_receipt_without_c5_row_licenses_nothing`: empty list, C4-only, and two C5 rows each keep release allowed and refuse the successor; a five-row receipt licenses. Counterfactual at 408b96c3: FAIL (3 subtests, executed). Four-module watchdog suite on the closure copy: 168 tests OK.

**F4: fix now.** After `os.link`, open the claims directory read-only and `os.fsync` it before returning, so the directory entry is durable before the plan is published. Regression `test_f4_claim_directory_entry_is_fsynced_before_publication` records the inode of every fsynced descriptor and asserts both the directory and the final claim were synced. Counterfactual at 408b96c3: FAIL (executed). Mutant "skip directory fsync": killed.

**F5: fix now with the following regressions (all executed on the closure copy; mutant runs below are against the closure copy with the listed new tests plus `test_a277_existing_claim_and_removed_root_still_bound_count`):**

| Mutant | Killing test | Result |
|---|---|---|
| Final claim by plain write (copyfile) | `test_f5_claim_creation_never_overwrites_a_foreign_final_claim` | killed |
| Drop existing-claim digest comparison | `test_f5_each_identity_and_delivery_comparison_refuses` | killed |
| Drop delivery plan-id comparison | same | killed |
| Drop delivery message-id comparison | same | killed |
| Drop candidate/predecessor id comparison | same | killed |
| Drop candidate/predecessor sha comparison | same | killed |
| Force scanner courier fact true | `test_f5_missing_courier_marker_is_a_false_fact_never_clean` | killed |
| Accept another candidate at claim creation | `test_f5_claim_creation_never_overwrites_a_foreign_final_claim` | killed |
| Drop active-claim check after root removal | `test_f5_active_foreign_claim_binds_after_root_removal_and_key_forgotten` | killed (survived every earlier test because the release-key guard shadows it until the watchdog forgets the key; the new test forgets the key) |
| Skip directory fsync | `test_f4_...` | killed |
| Rehearsal classifier never matches | `test_f1_...` | killed |

The plain-write test also pins that a foreign final claim's bytes are untouched both when the reader sees it and when it appears between the read and the link (`_successor_claims` patched to return empty): the second case refuses "concurrent successor claim" and leaves exactly one file in the directory.

## Q3. Structural ruling: keep the claim-file design, with the closures

The two rounds' blockers were not in the claim shape. Round 1 (Opus S1/S4): a wrong-id ledger read and a non-atomic write. Round 2 (refuter F1/F2): the pre-existing rehearsal string test and the watchdog's colon-delimited key. A create-once file per predecessor, outside the predecessor's custody, is the smallest durable one-use token that survives custody removal and cannot be forged by omitting a caller flag (synthesis, record 05). The alternatives are weaker: recording the claim in the successor's own plan bytes dies with the successor's custody and reintroduces a caller-supplied field; a single append-only ledger has the same torn-line and durability questions as the claim file plus a parser. Rule: keep, with Q1/Q2 closures. Note for the record: F1 was a latent property of every rehearsal gate since the lifecycle was written; A277 surfaced it by adding a gate whose failure is silent permissiveness rather than a skipped veto.

## Q4. More permissive than 313efcca?

**Release: no.** `zero_capture_facts(plan).clean` refuses everywhere the old `_zero_capture_disk_facts` refused, and additionally on a missing or symlinked custody root (old: missing root scanned as empty), any symlink inside custody, an unreadable descendant (old raised, new returns an incomplete scan), and non-literal or ambiguous chain values. The refuter's 17-shape parity table and the seat's parity test (tests/test_magistrate_watchdog.py, 168 tests OK on the closure copy) agree: every divergence is stricter. F3's empty-conditions release is identical on main (the terminal predicate is untouched by the branch and pinned by the base's own test).

**Arming: no.** The branch only adds a `successor` row to check and a second successor_check plus claim creation inside publish_install; both can only add refusals. The one place the branch could have been read as more permissive, F2, is a guard that did not exist on main at all; with the closure it refuses. NOT EXECUTED: a full-fixture arm comparison on main for every check row; I read the diff and executed the successor paths only.

## Q5. PROCEED-AFTER-DICTATED-CLOSURES

Apply the three diffs to 408b96c3 exactly, then: (a) run the four named modules in full (NOT EXECUTED here: test_evidence_night was run only for the 22 lifecycle/A277 tests plus the 8 new ones; test_zero_capture_facts, test_arm_retry and test_magistrate_watchdog ran in full, 168 OK); (b) update the contract and the byte-identical policy block for three sentences the closures change: the real launchctl must be spelled `launchctl` and any other spelling that resolves to it is refused rather than treated as a rehearsal; the successor route requires the driver's receipt shape with exactly one C5 row while release keeps the receipt's veto-only role; a predecessor whose plan id cannot name a claim file fails the successor row at check time (NOT EXECUTED: docs are outside what I changed); (c) mechanical check and final pass. No third fix round and no redesign.

## Executed evidence log

- Probe at 408b96c3 (`/tmp/fable277/fable277_probe.py`, run with `PYTHONPATH=/tmp/fable277:.`): F1, F2, F2 control, F3 outputs as quoted above; 4 tests ran.
- Closure copy `/tmp/fable277/head` (git archive 408b96c3 + edits): 8 new tests OK; probe re-run: F1 now `Refused: real launchctl must be spelled exactly 'launchctl'; a path to it is not a rehearsal: /bin/launchctl`; F2 and F3 now `pre-arm checks failed: successor`.
- Counterfactual copy `/tmp/fable277/cf` (408b96c3 code + new tests): `Ran 7 tests ... FAILED (failures=6)`: F1, F2, F4 and the three F3 subtests fail; the three F5 tests pass there by design (they are mutant killers).
- Mutants: 11 of 11 killed (table above); the active-claim mutant killed only after the additional key-forgotten test.
- Focused suites on the closure copy: `tests.test_zero_capture_facts tests.test_arm_retry tests.test_magistrate_watchdog`: `Ran 168 tests ... OK`; 22 LifecycleTests (all `test_a277_*`, d4/e1 rehearsal-veto, check-passes, publish-requires): OK.
- `git apply --check` of the three diffs against the detached worktree at 408b96c3: clean; worktree left unmodified.
