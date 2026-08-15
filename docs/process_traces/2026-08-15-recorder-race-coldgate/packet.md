# RECORDER-RACE COLD-GATE PACKET — WO-MARGIN-RECORDER-AUTHZ

Mechanically assembled 2026-08-15 by an Opus mechanic (NON-AUTHOR assembly per
`docs/process_traces/2026-08-15-m2-coldgate/composed-verdict.md` section 4 — the magistrate is a
reviewed party: its round-1 fix is under review and its round-2 design is a submission below).
The extraction script is committed beside this file as `assemble.py`; every primary is a scripted
extraction. There is no mechanic prose in the primaries and no magistrate prose anywhere except
inside PRIMARY 4, which is explicitly labeled as the reviewed party's submission.

**Rule-11 trigger:** second fix round on the same defect class (symlink/aliasing of the governed
extraction-spec grant). Round 2 has NOT been implemented; this gate sits before it.

## THE QUESTION FOR THE PAIRING

1. **Threat model and severity.** Is the check-to-grant race (a concurrent local writer
   retargeting the selected extraction-spec path between the resolution-invariance guard and the
   grant) inside the instrument's threat model? Is `blocker` the correct severity, or should it
   be recorded should-fix with the closure landing as defense-in-depth?
2. **Closure soundness.** Is the reviewed party's proposed content-binding closure (PRIMARY 4
   step 2: pre-grant `O_RDONLY|O_NOFOLLOW` read + hash-vs-pin refusal) sound? Is the fd-identity
   alternative (`st_dev`/`st_ino` before grant, re-stat after read) better? Is a third shape
   better than either?
3. **License or redirect.** License the second fix round with an EXACT specification, or order a
   different shape (including "no code change; record the residual and close").

## PRIMARY 1 — original Sol review, finding F1 + closing "Other attack lines passed"

Source: `sol-recorder-review.md` (session scratchpad), lines 111-138, verbatim.
Reviewed head: `8aaa5be11f2d0d9ae39071aac5ef60c94657f564` (pre-fix; the parent of PRIMARY 2).

````
### F1 — blocker · CONFIRMED

The grant is not path-confined under an in-repository symlink.

At [window_duration_margins.py:394](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/review-recorder/joulewise/window_duration_margins.py:394), `_safe_relative_path` resolves the selected pathname. An ALPHA-spec symlink targeting BETA therefore produces BETA’s canonical path, which is granted at [window_duration_margins.py:403](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/review-recorder/joulewise/window_duration_margins.py:403).

The replay observed:

```text
reason=pack_pin_invalid
grant_calls=1
granted_relative=configs/floor_mint/d117_qwen25_7b_extraction_spec.json
```

The SHA comparison at line 413 correctly prevents census processing and receipt publication, but that occurs after BETA received the governed-vocabulary grant. This violates adoption clause 1’s explicit “never granted … the other floor pack’s spec” boundary and the F2 threat table’s required other-spec refusal.

The new sibling-spec regression at [test_window_duration_margins.py:192](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/review-recorder/tests/test_window_duration_margins.py:192) does not catch this: it reads BETA after granting a normal ALPHA file rather than aliasing ALPHA’s selected pathname to BETA.

Required fix: reject symlinked components before authorization and bind the grant/read to one race-safe, no-follow identity. Add an ALPHA→BETA symlink regression requiring zero grant calls.

Other attack lines passed:

- Pack identity and exactly-one-source validation both precede the grant.
- Relative/external escape refuses before any grant; GAMMA receives none; there is one recorder call site.
- Returned bytes are compared directly with the plan-tree `extraction_spec.sha256` before census or membership work. Independent tampering refused without output.
- Frozen fixture hashes, cell IDs, block counts, members, and estimator IDs match the committed ALPHA/BETA/GAMMA bytes. Removing the grant would break the real floor-pack regression.
- No existing assertion was weakened without replacement by stronger frozen-pack coverage.
````

## PRIMARY 2 — fix round 1, the commit under review (verbatim `git show`)

Source: `git -C <repo> show --format=fuller --find-renames eff85f8da7ca31301121aa5f47c16c9e43f00573` on `impl/wo-margin-recorder-authz`.
Parent (the reviewed pre-fix head): `8aaa5be11f2d0d9ae39071aac5ef60c94657f564`.

```
commit eff85f8da7ca31301121aa5f47c16c9e43f00573
Author:     Ed R <edr@Eds-MacBook-Pro.local>
AuthorDate: Sat Aug 15 13:31:08 2026 -0700
Commit:     Ed R <edr@Eds-MacBook-Pro.local>
CommitDate: Sat Aug 15 13:31:08 2026 -0700

    Fix round 1 (review F1): resolution-invariance guard before the governed grant + ALPHA->BETA symlink regression (zero grants)
    
    The selected spec path must equal its own resolution and traverse no
    symlinked component from the repository root down; refusal
    authoritative_input_invalid fires BEFORE allow_governed_extraction_spec.
    Regression plants BETA's real spec in ALPHA's repo, aliases ALPHA's
    selected path to it, asserts refusal + grant.assert_not_called().
    Full focused suite: 34 tests OK.
    
    Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
    Claude-Session: https://claude.ai/code/session_01YWXnMks3CfSkUKHgWty5EJ

diff --git a/joulewise/window_duration_margins.py b/joulewise/window_duration_margins.py
index 5ed7ade..4f496ab 100644
--- a/joulewise/window_duration_margins.py
+++ b/joulewise/window_duration_margins.py
@@ -399,6 +399,23 @@ def _pack_inventory(
         expected_sha = _require_sha256(
             extraction.get("sha256"), label="downstream extraction-spec sha256"
         )
+        # The grant must bind the literal committed file: the selected path
+        # must be resolution-invariant (no symlinked component anywhere from
+        # the repository root down), so an in-repo alias can never retarget
+        # the governed-vocabulary grant to a different pack's spec (adoption
+        # clause 1: never granted the other floor pack's spec).
+        unresolved = repository_root / Path(
+            *PurePosixPath(str(extraction.get("path"))).parts
+        )
+        if unresolved.resolve(strict=False) != registry_path or any(
+            parent.is_symlink()
+            for parent in [unresolved, *unresolved.parents]
+        ):
+            _refuse(
+                "authoritative_input_invalid",
+                "governed extraction-spec path is not resolution-invariant "
+                "(symlinked component)",
+            )
         try:
             authentication.allow_governed_extraction_spec(registry_path)
         except (ValueError, RuntimeError) as exc:
diff --git a/tests/test_window_duration_margins.py b/tests/test_window_duration_margins.py
index c039191..10e3de7 100644
--- a/tests/test_window_duration_margins.py
+++ b/tests/test_window_duration_margins.py
@@ -261,6 +261,31 @@ class FrozenPackRecorderAuthorizationTests(unittest.TestCase):
         self.assertEqual(caught.exception.reason, "pack_pin_invalid")
         grant.assert_called_once_with(spec_path.resolve())
 
+    def test_symlinked_spec_path_refuses_before_any_grant(self) -> None:
+        """ALPHA's selected spec aliased to BETA's real spec: refuse, ZERO grants."""
+        repository_root, pack_root, spec_path, _tree = self._copy_floor_pack("1p5b")
+        beta_spec_path = self._floor_spec_path("7b", root=repository_root)
+        beta_spec_path.parent.mkdir(parents=True, exist_ok=True)
+        shutil.copy2(self._floor_spec_path("7b"), beta_spec_path)
+        spec_path.unlink()
+        spec_path.symlink_to(beta_spec_path)
+        with V2AuthenticationReadSession() as authentication:
+            with mock.patch.object(
+                authentication,
+                "allow_governed_extraction_spec",
+                wraps=authentication.allow_governed_extraction_spec,
+            ) as grant:
+                with self.assertRaises(margins.WindowDurationMarginsRefusal) as caught:
+                    margins._pack_inventory(
+                        authentication,
+                        repository_root,
+                        pack_root,
+                        str(FROZEN_FLOOR_PACKS[0]["pack_identity"]),
+                    )
+        self.assertEqual(caught.exception.reason, "authoritative_input_invalid")
+        self.assertIn("resolution-invariant", str(caught.exception))
+        grant.assert_not_called()
+
     def test_wrong_path_grant_attempt_is_normalized_to_refusal(self) -> None:
         repository_root, pack_root, spec_path, tree = self._copy_floor_pack("1p5b")
         wrong_path = spec_path.with_suffix(".txt")
```

## PRIMARY 3 — Sol delta re-audit of fix round 1

Source: `sol-recorder-delta.md` (session scratchpad). Part (a) is the report envelope's
`status`/`completion`/`summary`/`verdict`/`flags` keys, emitted by `json.dumps` from the parsed
envelope — the F1 finding and the audit's own completeness flags travel together deliberately.
Parts (b) and (c) are verbatim heading spans (lines 146-166 and 167-171).

### (a) verdict envelope

```
{
  "status": "findings",
  "completion": "partial",
  "summary": "REJECT: static symlink attacks are cured, but a check-to-grant race can still authorize the retargeted spec; the required guard-removal mutation run was sandbox-blocked.",
  "verdict": {
    "decision": "REJECT",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "Resolution guard has a check-to-grant race",
        "evidence": "HEAD checks unresolved.resolve()/is_symlink(), then separately calls allow_governed_extraction_spec(registry_path). That method resolves the pathname again, and the subsequent authentication read follows symlinks. Replacing ALPHA with an ALPHA-to-BETA symlink after the guard but before the grant therefore grants BETA before the later SHA mismatch.",
        "recommendation": "Bind authorization and reading to one no-follow filesystem identity, or otherwise make symlink refusal and the governed read atomic."
      }
    ]
  },
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The mandatory guard-only mutate-and-check could not be executed because apply_patch was forbidden in the clean temporary export; the repository checkout could not be mutated under WRITE_SCOPE [].",
      "needs": "Lead should remove only HEAD lines 402-418 in an isolated writable export and rerun test_symlinked_spec_path_refuses_before_any_grant; it should fail because the grant is called once and refusal changes to pack_pin_invalid."
    },
    {
      "id": "E1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The supplied checkout already had staged reverse changes deleting both the guard and its regression. All branch-head evidence therefore came from a clean git archive of eff85f8.",
      "needs": ""
    }
  ]
}
```

### (b) Findings section, verbatim

```
## Findings

F1 — blocker: the static F1 attack is cured, but the authorization invariant remains vulnerable to a concurrent retarget.

The sequence at `HEAD` is:

1. Check `unresolved.resolve()` and every lexical component for symlinks.
2. Call `allow_governed_extraction_spec(registry_path)`, which resolves the pathname again.
3. Read through `_json_object`, whose authentication read uses ordinary `open()` and follows symlinks.
4. Compare the bytes against the pinned SHA.

If ALPHA is replaced by an ALPHA→BETA symlink between steps 1 and 2, the grant resolves to BETA. The subsequent SHA mismatch refuses, but only after the forbidden grant—the same contract violation F1 was meant to eliminate. This should be repaired with an atomic/no-follow identity binding.

The requested static cases otherwise behaved correctly:

- Exact ALPHA→BETA replay: `authoritative_input_invalid`, zero grant calls.
- Symlinked `configs/floor_mint` parent: same refusal, zero grants.
- Alias to a byte-correct ALPHA file: same refusal, zero grants. This is acceptable under the adopted “literal committed path” contract.
- No `/tmp`/`/private/tmp` or case-variant false positive was observed. The public §11 derivation path resolves all roots at `derive_window_duration_margins` lines 922–924 before calling `_pack_inventory`; the CLI reaches that public path through `record_window_duration_margins`.
- Semantic diff: no unrelated behavior changes or paths were present. The only production change is the resolution guard, and the only test change is its regression.
```

### (c) Residual risk section, verbatim

```
## Residual risk

The guard-removal regression was not dynamically demonstrated because the sandbox rejected editing the clean temporary export. Static tracing predicts a discriminating failure: without the guard, the test reaches one BETA grant and then receives `pack_pin_invalid`, violating both its expected reason and `grant.assert_not_called()`.

No repository files were modified by this audit.
```

## PRIMARY 4 — REVIEWED PARTY'S SUBMISSION: the magistrate's round-2 proposal

Source: `recorder-round2-proposal.md` (session scratchpad), in full, verbatim.
**This is the design under adjudication, not evidence.** It is the reviewed party's own
statement of both the proposed closure and the severity question. The pairing owes it no
deference; the alternative it names, and any shape it does not name, are equally open.

```
PROPOSED SECOND FIX ROUND (magistrate design, submitted to the cold gate — NOT implemented):

Content-binding closure of the check-to-grant race, without touching authentication_io.py
(adoption clause: no public authentication API change):

1. Keep the resolution-invariance guard (round 1).
2. BEFORE the grant: open the unresolved selected path with os.open(..., O_RDONLY|O_NOFOLLOW)
   (final component no-follow; parents already symlink-refused by the guard), read the bytes from
   that fd, hash them, and REFUSE unless the hash equals the plan-tree pin. Close the fd.
3. Grant allow_governed_extraction_spec(registry_path); session-read; keep the EXISTING
   post-read session-bytes-vs-pin refusal unchanged.

Race analysis submitted for adjudication: after step 2, any mid-race swap must produce
session-read bytes that hash to the committed pin to survive step 3's existing check — i.e. the
adversary gains nothing beyond what the committed ALPHA bytes already authorize; a swapped BETA
read is hash-refused before any census processing, and the momentary session-local lexical
exemption is never consumed (refusal is immediate and terminal, the session exits). The residual
"grant issued for a path momentarily aliasing another file" has no consumer.

Alternative the gate may prefer: fd-identity binding (fstat st_dev/st_ino before grant, re-stat
after session read, refuse on mismatch) — stronger identity claim, but still cannot bind the
SESSION's own internal open; the content-bind (above) is the closure that does not depend on
which open raced.

Threat-model context for severity adjudication: the recorder runs single-operator on Ed's
machine under the documented trusted-writer model (docs/contracts/calibration_ledger.md:3 — the
L2 falsely-clean attack's custody note deemed writer-signature work orders unjustified without a
threat-model ruling). The race requires a concurrent local adversary mutating the repo mid-
process. The gate rules whether that is in-model (and the blocker stands, requiring the closure)
or out-of-model (and the closure is defense-in-depth landing anyway, with severity recorded
should-fix).
```

## PRIMARY 5 — threat-model primary (docs/contracts/calibration_ledger.md, first 10 lines)

Verbatim excerpt. This is the contract text PRIMARY 4 cites (line 3) for the trusted-writer
boundary that governs question 1.

```
# Calibration observation ledger

The canonical calibration ledger is an immutable SHA-256 receipt chain under
`joulewise.calibration_observation_ledger.v1`. D-109 R1 and R2 are controlling.
The ledger closes workflow omission, unregistered evidence, and rollback or
stale-head consumption; it does not defend against a malicious trusted writer
or an authority that rewrites both Git and the complete ledger history.

Live capture remains reservation-first: a `reservation` receipt with
`disposition=pending` precedes hardware state, and exactly one `finalization`
```

## PRIMARY 6 — the adoption ruling that defines the violated boundary

Source: `docs/decision_log.md`, lines 9056-9094, verbatim — the entry span from its heading to the
next entry heading. Clause 1's "Never granted: ... the other floor pack's spec" is the boundary
both review rounds test against. See the index for what is and is not part of this ruling.

```
### WO-MARGIN-RECORDER-AUTHZ contract ADOPTED (magistrate, 2026-08-15; council Phase 0; Sol design consult adopted)

Consult custodied: docs/process_traces/2026-08-15-recorder-authz-consult/
(the ONE home for the mechanism detail). Cures fleet blocker L4-B1.

**Ruling:**
1. NO new authentication primitive: the recorder reuses the mint's
   session-local `allow_governed_extraction_spec`, invoked NARROWER than
   the mint — exactly once, only in the floor-pack branch, only for the
   plan-tree-selected extraction-spec path, after pack-identity and
   exactly-one-source validation, with an immediate hash comparison of
   the returned bytes against the plan-tree pin BEFORE any census/
   membership processing. Never granted: the GAMMA manifest, reports,
   plan tree, bundles, or the other floor pack's spec.
2. The grant exempts only the recursive lexical estimator_registration
   ban for that one file; duplicate-key/UTF-8/finite-number/grammar/
   digest-stability/path-containment checks all survive. No change to
   joulewise/authentication_io.py or any public API.
3. The synthetic census tests are REPLACED by frozen-pack regressions
   modeling the REAL re-specced cell shapes (the green-suite-broken-seam
   specimen dies in the same commit) — per the consult's attempt/result
   table.
4. Execution = WO-MARGIN-RECORDER-AUTHZ (council Phase 1). This
   executes D-133's close-out gate; it amends no scientific semantics.

**M-2 GATE AMENDMENT (magistrate, 2026-08-15, per the remanded cold gate's composed verdict —
docs/process_traces/2026-08-15-m2-coldgate/composed-verdict.md, the ONE home):** the engineering
core is UPHELD (receipts govern over descriptive bytes; frozen bytes are never repaired). The
instrument is NARROWED: (a) the "overrode a NO-GO reading" premise is STRICKEN — no machine gate
or §5C clause reads draft_status; M-2 resolves a human-operator ambiguity only; (b) the "every
arm packet must cite this ruling" duty is STRICKEN — replaced by one informational operator note
in the successor packet; (c) the retirement clause is corrected — retirement occurs at successor
freeze ONLY IF the Phase-2 generator work makes draft_status freeze-aware (currently hardwired at
every JSON emission site); (d) the override's exhaustive scope is the three 2026-08-13 receipt
hashes (ddbbb409…1738, a6dec2c2…7870, 2ef73bf0…106f), retiring per pack — it may never be cited
for any other pack; (e) the contrast pack's pending-ratification/TODO markers are OUTSIDE M-2 and
carry their own RULING-REQUIRED row; (f) the #149 --plan argv divergence must reconcile under R2
before any arm.
```

## SUPPLEMENT S1 (MECHANIC ADDITION, not in the assembly order) — the F2 threat table

Source: `docs/process_traces/2026-08-15-recorder-authz-consult/consult.md` lines 148-166, `^### F2 ` heading span, verbatim.
PRIMARY 1 convicts the code against "the F2 threat table's required other-spec refusal" but the
assembly order did not attach that table. It is the instrument's own enumeration of required
results and bears directly on question 1. Attached by the mechanic and declared as an addition;
the pairing may disregard it.

```
### F2 — should_fix: widening threat and refusal boundaries

The grant exempts the selected file from the recursive lexical ban on `estimator_registration`; it does not weaken duplicate-key, UTF-8, finite-number, grammar, digest-stability, or path-containment checks.

| Attempt | Required result |
|---|---|
| Exact frozen selected spec | Admitted; only `cell_id`, metric, and membership flow into the receipt |
| Other floor spec in the same session | `authoritative_input_invalid`, preserving nested `v2_authentication_forbidden_json_key` detail |
| Registration in plan tree, report, bundle JSON, or GAMMA manifest | Same forbidden-key refusal |
| Selected path with changed bytes | `pack_pin_invalid` before census or bundle discovery |
| Escaping/absolute extraction path or malformed SHA | `pack_pin_invalid` |
| Duplicate keys, invalid UTF-8/JSON, nonfinite values | `authoritative_input_invalid` with the existing nested authentication reason |
| Bad schema or dropped/extra census result | `registered_cell_inventory_invalid` |
| Malformed, incomplete, or duplicated members | Existing `registered_membership_invalid` or `member_non_unique` |

No new public refusal code is warranted. Grant-construction errors must also be normalized rather than leaking `ValueError` or `RuntimeError`.

The widest content that can cross the lexical reader is any occurrence of `estimator_registration` inside the one authorized file. Unexpected bytes cannot affect a receipt under this design because the exact plan-tree SHA is checked before semantic use. A self-consistent replacement of the plan tree, sidecar, and spec remains possible to the single authority; that is the pre-existing D-120 `single_authority_hash_bound_replay.v1` limitation, not a consequence of this grant.
```
