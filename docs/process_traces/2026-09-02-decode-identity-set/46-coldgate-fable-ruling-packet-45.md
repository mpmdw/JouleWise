# Cold Fable ruling — packet 45 (decode-identity lineage paragraph: Cure C, F-N5/F-N6, first-use gate rule)

Seat: cold adjudication instance, Claude Fable 5.1 (`claude-fable-5-1`), fresh session, no operating-loop context. Charter: `docs/process/coldgate_charter.md`. Date: 2026-09-02.

## 0. Contamination disclosure (charter convening procedure)

The harness auto-loaded the following into my context before I read anything: `/Users/edr/.claude/CLAUDE.md` (global rules incl. a "writing standard" section), `/Users/edr/code/JouleWise/CLAUDE.md` (project Codex-bridge notes), `/Users/edr/code/JouleWise/CLAUDE.local.md` (private orchestration doctrine, "rules 1–11"), and `/Users/edr/.claude/projects/-Users-edr-code-JouleWise/memory/MEMORY.md` (session-memory index). Charter §4 forbids private doctrine files and session memory. I used none of that material for any ruling below; every citation is to the packet, its manifest exhibits, the charter, or code I executed or read at the pinned commit. Where the packet's own text uses "rule 11" (packet §3 of exhibit 38, exhibits 40–42), I read that as the packet's label for the same convening triggers the charter enumerates in §3, and I rule on the charter's text only.

Sealing note (charter §5): at the final listing of the scratch directory I observed seven files I did not create (`contract_at_fc52bda6.md`, `probe_fn6.py`, `probe_hops.py`, `probe_order.py`, `probe_trigger.py`, `probe_trigger2.py`, `probe_universals.py`, timestamps 20:56–21:05 interleaved with mine), presumably the paired refuter's working files in the same directory. I did not open, read, or execute any of them; my scripts are the five named in §1 and this ruling.

## 1. Pre-merits verification (charter §9, third bullet)

| Item | Expected | Observed | Method |
|---|---|---|---|
| Charter sha256 | `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` | `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` | `shasum -a 256 docs/process/coldgate_charter.md` |
| Registry carries the digest | same | `coldgate_charter_registry.md:16` `| sha256 | \`099de884…\` |` | `grep -n` |
| Checkout HEAD | `04e45f68` | `04e45f68`, branch `fix/2026-09-02-decode-identity-set` | `git rev-parse --short HEAD` |
| Packet sha256 | `b31dec0c7fed3c1dcc4ad64f2c8dfc8289368be1c99d38c425435d13cc17381b` | `b31dec0c7fed3c1dcc4ad64f2c8dfc8289368be1c99d38c425435d13cc17381b` | `shasum -a 256` |
| Packet pin `fc52bda6` vs HEAD `04e45f68` | — | `git diff --stat fc52bda6 HEAD` touches only trace files 44, 45, 45a, 45c; `git diff fc52bda6 HEAD -- docs/contracts/identity_pin_projection.md joulewise/arm_readiness.py joulewise/analysis_engine/inputs.py` is empty | `git` |
| Exhibit 45a vs live contract | — | `diff` empty: exhibit 45a is byte-identical to `docs/contracts/identity_pin_projection.md` (1042 lines), so packet line numbers resolve directly | `diff` |

Validator receipt (pasted verbatim, rc=0):

```
$ python3 scripts/validate_gate_packet.py --packet docs/process_traces/2026-09-02-decode-identity-set/45-coldgate-packet-fn4-cure-c.md --charter docs/process/coldgate_charter.md --expected-packet-sha256 b31dec0c7fed3c1dcc4ad64f2c8dfc8289368be1c99d38c425435d13cc17381b --expected-charter-sha256 099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81
{"binding_scope":"validation_time_observation_only","details":[],"digests":{"charter_sha256":"099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81","exhibit_manifest_sha256":"5201b7ff0a28791807f811f7f75292b6c87ffa5f5d92c7dcb4956bc36969811b","exhibits":[{"expected_sha256":"4db7e3da039b591b3b66307733a94d09116662fb0628fb5059cd9853504c0152","observed_sha256":"4db7e3da039b591b3b66307733a94d09116662fb0628fb5059cd9853504c0152","path":"37-terra-267-delta-re-audit-3-report.md"},{"expected_sha256":"b20cba048f9e75ec26bf7be7eda75f3e96538414e384d9d460df87276eae963f","observed_sha256":"b20cba048f9e75ec26bf7be7eda75f3e96538414e384d9d460df87276eae963f","path":"38-consult-packet-fn4-fourth-prose-signature.md"},{"expected_sha256":"d7c5484cbec7c8c2cdf72e99977bd73800c8502ac32633355e299f6dda126e3a","observed_sha256":"d7c5484cbec7c8c2cdf72e99977bd73800c8502ac32633355e299f6dda126e3a","path":"40-luna-268-consult-fn4-report.md"},{"expected_sha256":"808bd3b0534698ce5aba75b21d7d2636b5a86ea79996ccfb44118efdb922452a","observed_sha256":"808bd3b0534698ce5aba75b21d7d2636b5a86ea79996ccfb44118efdb922452a","path":"41-opus-seat-consult-fn4-report.md"},{"expected_sha256":"4ece4e126851489e237d334aec657daf5e78e7f2eb18354c3b49faafbda6ce07","observed_sha256":"4ece4e126851489e237d334aec657daf5e78e7f2eb18354c3b49faafbda6ce07","path":"42-blind-fable-seat-consult-fn4-report.md"},{"expected_sha256":"0739baebb1635891e29a98f1674e3790f52fda5c4358318dac9687c7d2937a1e","observed_sha256":"0739baebb1635891e29a98f1674e3790f52fda5c4358318dac9687c7d2937a1e","path":"44-magistrate-synthesis-fn4-consult.md"},{"expected_sha256":"fcc9051523fbced6e66da1deaf2b97e5d72ec6c0aaeda8aa4f145717543497ea","observed_sha256":"fcc9051523fbced6e66da1deaf2b97e5d72ec6c0aaeda8aa4f145717543497ea","path":"45a-exhibit-identity_pin_projection-at-fc52bda6.md"},{"expected_sha256":"b7dc210c77909965c6abad3a820146ad0b5afd07e86d78690306543a9da5c3e9","observed_sha256":"b7dc210c77909965c6abad3a820146ad0b5afd07e86d78690306543a9da5c3e9","path":"45c-exhibit-ed-ruling-2026-09-02-verbatim.md"},{"expected_sha256":"93e90920ffeaaaa32306fd191d861255633beaec4354c725c9c08ad0c371d553","observed_sha256":"93e90920ffeaaaa32306fd191d861255633beaec4354c725c9c08ad0c371d553","path":"32-magistrate-synthesis-s1-s3.md"}],"packet_sha256":"b31dec0c7fed3c1dcc4ad64f2c8dfc8289368be1c99d38c425435d13cc17381b"},"expected_charter_sha256":"099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81","expected_packet_sha256":"b31dec0c7fed3c1dcc4ad64f2c8dfc8289368be1c99d38c425435d13cc17381b","inputs":{"charter":"coldgate_charter.md","packet":"45-coldgate-packet-fn4-cure-c.md"},"judge_handoff_bound":false,"packet_charter_path":"coldgate_charter.md","packet_charter_pin_sha256":"099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81","reason":null,"result":"PASS","schema":"coldgate-validator-receipt/v2"}
rc=0
```

Read set: the charter in full; the packet; all nine manifest exhibits in full (32, 37, 38, 40, 41, 42, 44, 45a, 45c); code at HEAD (byte-identical to `fc52bda6` for the object files): `joulewise/arm_readiness.py` lines 200–262 (reason-code families), 342–354 (`PACK_KEYS`), 669–752 (receipt key sets), 1201–1219, 2541–2586, 4162–4190, 5242–5265 (`_pack_record`), 8687–8720, 8835–9060, 9304–9436 (`_replay_consumed_arm`), 9740–9770, 9781–9900, 10078–10460 (`authenticate_launch_lineage`, locator), 10598–10670 (`authenticate_bundle_launch_lineage`); `joulewise/analysis_engine/inputs.py` 2735–2850 (`_read_bundle`), 3880–3905, 4030–4095; `tests/test_analysis_inputs.py` 706–760; `tests/test_arm_readiness_lifecycle.py` 748–860 (fixture shape only); `tests/test_analysis_integration.py` 157–190 (helper index only). Not read: `RUN_STATE.md`, `docs/council_log.md`, run reports, any scratchpad, `docs/orchestration.md`, `docs/phase_2/window_runbook.md`, trace files 33/34/39. No file under the checkout was modified; `git status --short` was empty after every command. All scratch scripts live under `<scratchpad>/coldgate45/` (`hops.py`, `cascade.py`, `bundle.py`, `q3.py`, `extras.py`); every run used `python3 -B`, `PYTHONDONTWRITEBYTECODE=1` and `TMPDIR` inside that directory.

## 2. Executed evidence

Long temp paths are abbreviated `…` in the pasted output; nothing else is altered. Each block is the script's output as printed.

### P1 — `hops.py`: the five packet hops, plus four files the packet's five do not name

```
$ TMPDIR=$S/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B $S/hops.py
== A. the five hops named by the packet, each executed on a nonexistent path
H1 consumption receipt gone                  reason_code='launch_consumption_missing' :: launch-lineage receipt is absent: …
H2 pack root gone (real _replay_consumed_arm) reason_code='launch_binding_mismatch' :: consumed arm pack root cannot be authenticated: [Errno 2] No such file or directory: …
H3 launch manifest gone                      reason_code='launch_consumption_invalid' :: bound launch artifact is unreadable: …
H4 window plan root gone (real authenticate_launch_lineage) reason_code='launch_binding_mismatch' :: launch manifest window root is unavailable: [Errno 2] No such file or directory: …
H5a lifecycle START receipt gone             reason_code='launch_lifecycle_incomplete' :: launch-lineage receipt is absent: …
H5b lifecycle SETTLE receipt gone            reason_code='launch_lifecycle_incomplete' :: launch-lineage receipt is absent: …
H5c lineage stamp omits start (ref None)     reason_code='launch_lifecycle_incomplete' :: launch lineage omits start
== B. files the same path also reads that the packet's five do not name
X1 arm receipt gone (real _replay_consumed_arm, no stub) reason_code='launch_consumption_invalid' :: consumption predecessor is invalid: cannot read arm receipt: [Errno 2] No such file or directory: …
X2 window.env gone                           reason_code='launch_consumption_invalid' :: bound launch artifact is unreadable: …
X3 launch-lineage locator gone               reason_code='launch_consumption_missing' :: launch-lineage receipt is absent: …
X4 consumption sidecar gone (primary present) reason_code='launch_consumption_missing' :: launch-lineage receipt is absent: …
== C. reason-code family membership
LAUNCH_LINEAGE_REASON_CODES = ['launch_binding_mismatch', 'launch_consumption_invalid', 'launch_consumption_missing', 'launch_handoff_invalid', 'launch_lifecycle_incomplete', 'launch_lineage_axi_unsupported', 'launch_lineage_conflict']
```

How H2 and H4 were executed (they are inline, not separate readers): H2 runs the real `_replay_consumed_arm` body with only `_read_arm_with_sidecar` stubbed to return an arm whose `pack.pack_root` does not exist, so control reaches the `Path(str(arm["pack"]["pack_root"])).resolve(strict=True)` line (`arm_readiness.py:9333`) and its `except (ArmReadinessError, OSError)` (`:9348–9352`). H4 runs the real `authenticate_launch_lineage` body with `_read_v2_consumption`, `_replay_consumed_arm` and `_read_exact_launch_reference` stubbed to succeed; the manifest bytes pass the real `validate_launch_manifest` and name a nonexistent `window_plan_root`, so control reaches `:10199–10205`. H1, H3, H5a/b/c, X1–X4 call the real readers with no stubs.

### P2 — `cascade.py`: execution order (real `authenticate_launch_lineage` body; each stage restores one more hop, all later files nonexistent)

First run (manifest path nonexistent):
```
S1 everything gone                              : reason_code='launch_consumption_missing' :: launch-lineage receipt is absent: …
S2 +consumption ok; arm-receipt file gone        : reason_code='launch_consumption_invalid' :: consumption predecessor is invalid: cannot read arm receipt: [Errno 2] No such f…
S3 +consumption ok, arm ok; pack root gone       : reason_code='launch_binding_mismatch' :: consumed arm pack root cannot be authenticated: [Errno 2] No such file or directory
S4 +replay ok; manifest gone                     : reason_code='launch_consumption_invalid' :: bound launch artifact is unreadable: …
S5 +manifest ok; window plan root gone           : reason_code='launch_binding_mismatch' :: launch manifest window root is unavailable: [Errno 2] No such file or directory: …
(S6 aborted by a harness artifact, see NIT-2 below)
```
Second run (manifest file present with wrong bytes, so S6/S7 are reachable):
```
S1 everything gone                              : reason_code='launch_consumption_missing' :: launch-lineage receipt is absent: …
S2 +consumption ok; arm-receipt file gone        : reason_code='launch_consumption_invalid' :: consumption predecessor is invalid: cannot read arm receipt: [Errno 2] No such f…
S3 +consumption ok, arm ok; pack root gone       : reason_code='launch_binding_mismatch' :: consumed arm pack root cannot be authenticated: [Errno 2] No such file or directory
S4 +replay ok; manifest gone                     : reason_code='launch_binding_mismatch' :: bound launch artifact bytes changed: …      <- manifest PRESENT, bytes differ
S5 +manifest ok; window plan root gone           : reason_code='launch_binding_mismatch' :: launch manifest window root is unavailable: [Errno 2] No such file or directory: …
S6 +window plan root ok; start receipt gone      : reason_code='launch_lifecycle_incomplete' :: launch-lineage receipt is absent: …
S7 +start ok; settle receipt gone                : reason_code='launch_lifecycle_incomplete' :: launch-lineage receipt is absent: …
bundle path passes require_completion=False? -> True
```
Order pinned by execution: consumption receipt → arm receipt → pack root → launch manifest → window plan root → start receipt → settle receipt. (The bundle-level locator precedes all of these: P3/B2.) A manifest that is *gone* emits `launch_consumption_invalid` (first-run S4, P1 H3); a manifest that is *present with changed bytes* emits `launch_binding_mismatch` (second-run S4).

### P3 — `bundle.py`: the `_read_bundle` seam

```
B1 lineage-required bundle, stamp absent      : RAISED AnalysisInputError: launch_consumption_missing: bundle-1: bundle launch-lineage stamp is absent
B2 stamp present, root locator file absent    : RAISED AnalysisInputError: launch_consumption_missing: bundle-1: launch-lineage receipt is absent: …
B3 bundle directory itself missing            : RETURNED BundleEvidence inclusion='excluded' base_reason_codes=('bundle_missing',) launch_lineage=None
B4 NOT lineage-required, no stamp             : RETURNED BundleEvidence inclusion='excluded' base_reason_codes=('config_hash_mismatch',) launch_lineage=None
```
B1/B2: a bundle whose `config.json` carries the `launch_lineage_required` tag is refused by a raised `AnalysisInputError` prefixed with the launch-lineage reason code, before any `BundleEvidence` row is built. B3: a missing bundle *directory* returns an evidence row (`bundle_missing`) without lineage authentication — so "before any evidence row exists" (landed `:610`) is falsifiable by this branch. B4: a bundle without the tag is never lineage-authenticated (`launch_lineage=None`).

### P4 — `q3.py`: pack-root provenance

```
'pack_root' in PACK_KEYS (arm receipt's pack record): True
'pack_root' in ARM_RECEIPT_KEYS top level: False | 'pack' in ARM_RECEIPT_KEYS: True
'pack_root' in CONSUMPTION_RECEIPT_KEYS: False
'pack_root' in LAUNCH_LIFECYCLE_RECEIPT_KEYS: False
'pack_root' in LAUNCH_LINEAGE_KEYS (bundle stamp): False
_pack_record(pack) keys: ['pack_digest_algorithm', 'pack_id', 'pack_root', 'pack_sha256', 'plan_id', 'plan_tree_path', 'plan_tree_sha256', 'plan_tree_sidecar_path', 'plan_tree_sidecar_sha256', 'window_id']
_pack_record(pack)['pack_root'] = …/coldgate45-q3-l502rsyd/repo/configs/campaigns/pack-z
equals str(pack.resolve()): True
generate_arm_receipt calls _pack_record: True | stores under receipt['pack']: True
--- generate_arm_receipt: pack lines
8238:    pack = _pack_record(root)
8430:        "pack": pack,
```
`_pack_record` was executed on a scratch git-committed pack (plan_tree.json + sidecar, one commit); `generate_arm_receipt` (`def` at `:8204`) calls it at `:8238` and stores it at `:8430`.

### P5 — direct-seam unit test (read-only run, TMPDIR in scratchpad)

```
$ python3 -B -m unittest tests.test_analysis_inputs.FrozenConsumerIdentitySetTests.test_missing_pack_root_refuses_with_unauthenticated_label
.
----------------------------------------------------------------------
Ran 1 test in 2.996s

OK
```
The test (`tests/test_analysis_inputs.py:706–727`) sets `row.launch_lineage["pack_root"]` to a nonexistent path and asserts `_frozen_consumer_identity_set(...) == frozenset()` and `resolution.reason_codes == ("consumer_identity_set_unauthenticated",)`.

### P6 — `extras.py` (+ E2a rerun): one-use write, env/chain path binding, lifecycle chaining

```
E1a _exclusive_write first write                     NO ERROR -> None
E1b _exclusive_write second write, same path         reason_code='readiness_output_collision' :: refusing to overwrite …
E2a' recorded window.env exists elsewhere, root's window.env present: reason_code='launch_binding_mismatch' :: bound launch artifact path changed: …
E2b window.env under root, bytes match               NO ERROR -> (PosixPath('…/wpr/window.env'), b'x')
E2c window.env under root, bytes changed             reason_code='launch_binding_mismatch' :: bound launch artifact bytes changed: …
E3a settle.predecessor == start ref (well-chained)   NO ERROR -> {'schema_version': 'joulewise.launch_lineage.v1', 'consumption_id': 'c-1', …
E3b settle.predecessor != start ref                  reason_code='launch_consumption_invalid' :: settle receipt predecessor/order differs
```
E1: the consumption writer's primitive (`_exclusive_write`, used at `:9758`; the writer maps the collision to `readiness_record_consumed` at `:9761–9764`). E3 runs the real `authenticate_launch_lineage` body through to its return with start/settle stubbed present; E3b flips only `settle["predecessor"]`.

### P7 — definition grep for the first-use tables (contract at HEAD)

```
7:and found is the **receipt**; …
34:A **campaign pack** is the directory containing `plan_tree.json`, its
48:authenticated **receipt**, a JSON record of its inputs, outputs, and checks;
148:  before the readiness decision. **Arm** is the readiness ceremony that may
492:campaign-pack directory (the pack root) before it compares any declaration:
533:then rejects a **committed successor**, meaning another committed pack whose
580:- **U8** is the arm-readiness mapper and record that authenticates the pack's
584:- **Launch lineage** is the authenticated receipt chain from a collected bundle
598:For successor packs, every accepted bundle carries an authenticated launch
599:lineage that resolves one pack root. The analysis input gate follows that
671:digest, **launch manifest** (the JSON declaration of the reviewed command and
672:its inputs), and **one-use consumption record** (the durable proof that this
first uses: "arm receipt" 160 (":158–160 … window custody, outside the pack, holds arm receipts" — a use, not a definition); "consumption receipt" 612; "window plan root" none; "lifecycle receipt" 613; "launch_consumption_invalid" none; "launch_lifecycle_incomplete" none; "input loading" 614; "evidence row" 610
```

## 3. Rulings

Verdict vocabulary per charter §8: AFFIRM / REJECT / REFUSE; severity BLOCKER / MATERIAL / NIT assessed independently. Where I disagree with the magistrate's labeled disposition (exhibit 44 §3) I say so explicitly.

### Q1 — Is a round-4 rewrite of `:609–621` "a second fix round on the same defect" (charter §3 item 1)?

**Answer: NO.** Verdict on the proposition "it is a second fix round on the same defect": **REJECT**. Severity of the question's stakes: NIT for routing (see below).

Individuation: I individuate a *defect* as a specific false or unbuilt proposition in a specific artifact — the unit a fix round targets and an audit re-checks. The charter uses two distinct notions: "second fix round on the same defect" (§3.1) and "two consecutive rounds failing with the same signature" (§9, second bullet). If "same defect" meant "same class," §9 would be redundant; so "same defect" is the narrower notion. Under it:

- F-N4 (terms used before definition at `:609–621`), F-N5 (wrong reason codes at `:614–615`) and F-N6 (wrong provenance at `:609`) are findings against a paragraph that did not exist before round 3 (exhibit 32 §S3 dictates it; exhibit 37 audits it as new text). None has yet had a fix round. Round 4 would be the **first** fix round on each.
- Exhibit 41 Ground 1 individuates by "the proposition the fix is trying to make true" (the section's prose introduces no term before definition). That is a class-level proposition spanning different paragraphs (F2/R-M5 was in the freeze-procedure text; F-N4 is in §Analysis consumption). Exhibit 41 Ground 2 ("dictated text is factually wrong": S1 → F-N5/F-N6) is likewise a class (S1 concerned an ordering claim in the freeze procedure, per exhibit 32 §S1; F-N5/F-N6 concern reason codes and provenance in a different paragraph). Both grounds are exactly the "same signature" the charter's §9 names, not the "same defect" of §3.1.
- Exhibit 42's (c) and exhibit 40's (b) both read §3.1 the same way I do; exhibit 42 then argues the gate is reached anyway — which I agree with, on different clauses.

Why the answer is not load-bearing for routing, so that no one reads NO as a release: (i) charter §3.4 fires on its own — Q6 presents a proposed process rule; (ii) charter §9 second bullet fires — exhibits 37, 41 and 42 establish (and P1 confirms) that rounds 2 and 3 (consult and landing) failed with the same prose signature, so "licensing another same-shape round requires explicit justification," and this ruling supplies the conditions under which round 4 is *not* same-shape (Q4, Q6, Q7). The gate is properly convened; round 4 lands under it.

**Disagreement with the magistrate's disposition:** exhibit 44 §3 adopts YES ("the decisive ground is Opus Ground 2"). I reject that classification for the reason above; it does not change routing.

### Q2 — Execute the five missing-file hops; does the landed paragraph name the wrong code for any?

**Verdict: AFFIRM** (the paragraph names the wrong code for two of the five). Severity: **MATERIAL** (a reader replicating refusal handling from the contract gets 2 of 5 cases wrong; not BLOCKER because `identity_pin_projection.md:10–12` makes the implementation authoritative on conflict and no claim or test is built on the prose).

Executed results (P1 §A; all five executed, none code-read):

| Missing file | Code emitted (executed) | Landed `:614–615` says | Verdict |
|---|---|---|---|
| consumption receipt | `launch_consumption_missing` (H1) | `launch_consumption_missing` | correct |
| pack root | `launch_binding_mismatch` (H2, real `_replay_consumed_arm` body) | `launch_binding_mismatch` | correct |
| launch manifest | **`launch_consumption_invalid`** (H3; cascade S4 first run) | `launch_binding_mismatch` | **wrong** |
| window plan root | `launch_binding_mismatch` (H4, real `authenticate_launch_lineage` body) | `launch_binding_mismatch` | correct |
| start/settle lifecycle receipts | **`launch_lifecycle_incomplete`** (H5a, H5b, H5c; cascade S6, S7) | `launch_binding_mismatch` | **wrong** |

F-N5 stands as stated in exhibits 41 §1 and 42 §0 X1; I add that the bundle path also reads the arm receipt (gone → `launch_consumption_invalid`, X1), the lineage locator (gone → `launch_consumption_missing`, X3, and B2 at the `_read_bundle` seam), `window.env`/`window-chain.zsh` (gone → `launch_consumption_invalid`, X2; wrong path → `launch_binding_mismatch`, E2a'), and every receipt's `.sha256` sidecar (gone → the primary's missing code, X4). The paragraph's enumeration of "the consumption receipt, the launch manifest, the window root and the lifecycle receipts" is therefore also incomplete as a description of what must still exist.

### Q3 — Is the pack root recorded at arm issuance (`_pack_record`), not "when the arm was consumed"? Does the consumption receipt carry one?

**Verdict: AFFIRM** on both halves (recorded at arm issuance; the consumption receipt carries none). Severity: **MATERIAL** (F-N6: the sentence at `:609` attributes the record to the wrong artifact and the wrong moment).

Executed (P4): `_pack_record` emits `pack_root == str(pack_root.resolve())`; `generate_arm_receipt` calls it (`:8238`) and stores it under the arm receipt's `"pack"` key (`:8430`; `PACK_KEYS` carries `pack_root`, `ARM_RECEIPT_KEYS` carries `pack`). `CONSUMPTION_RECEIPT_KEYS`, `LAUNCH_LIFECYCLE_RECEIPT_KEYS` and `LAUNCH_LINEAGE_KEYS` all lack `pack_root`. At consumption/bundle time the root is *read back* from `arm["pack"]["pack_root"]` (`:9333`, executed in H2/S3), not recorded. `_pack_record` is also called by `generate_freeze_receipt` (`:7611`), `generate_dry_run_receipt` (`:7907`) and `_family_member` (`:11301`); the arm receipt is the one the lineage replays.

### Q4 — Which Cure C text may land, with what corrections; grade every sentence

**Verdict:** exhibit 42 §2.3 (i)+(ii) — **AFFIRM with the corrections below (may land only in the corrected form given in §4 of this ruling)**. Exhibit 41 §3 Cure C — **REJECT as written** (three factual failures, one of them execution-proven), though two of its elements are imported into the corrected text. Severity of the defects found in each candidate: MATERIAL.

Convention for grade (ii): EXECUTED = probe in §2 above; CODE-READ = read but not executed by me (the writer must execute it under Q6's rule before landing); UNVERIFIABLE = rests on material outside the packet's read set.

#### 4a. Exhibit 42 §2.3 (ii) — the paragraph, sentence by sentence

| # | Sentence / clause | (i) first-use | (ii) execution | Correction |
|---|---|---|---|---|
| 1 | "That root is the absolute path of the pack directory on the machine that armed it, copied into the arm receipt when the arm was issued." | "arm receipt": built by `**Arm** … may issue a launchable receipt` (`:148`) and used at `:160`; PASS. "pack directory": `**campaign pack**` `:34` + "(the pack root)" `:492`; PASS. | provenance — EXECUTED P4 (`_pack_record` → `generate_arm_receipt` `:8238/:8430`; no other receipt carries it). PROVEN. | none |
| 2 | "Before a bundle is admitted as analysis input, bundle loading authenticates its launch lineage by reading five recorded files by their absolute paths, in this order, and refuses at input loading — so the bundle never reaches this gate — if any is gone:" | "launch lineage" `:584` PASS; "input loading"/"admitted as analysis input" glossed in-sentence PASS; "this gate" = "the analysis input gate" `:599` PASS. | "before … admitted": EXECUTED P3 B1/B2 (raise precedes any row) — PROVEN for tagged bundles, and B4 shows untagged bundles are never lineage-checked, so "a bundle" must be qualified. "**five** recorded files": **FALSE by execution** — the same path also reads the locator (X3/B2), the arm receipt (X1/S2), `window.env` and `window-chain.zsh` (X2), and the sidecars (X4); each refuses. "in this order": EXECUTED P2 — order of the five as a subsequence is PROVEN. "by their absolute paths": validators require absolute (`_validate_launch_artifact_reference` `:2541–2553`, `validate_launch_manifest` `:2577–2580` — exercised by my stubs passing them) — PROVEN. "if any is gone": EXECUTED for all five. | qualify the bundle ("whose configuration carries the `launch_lineage_required` tag"); replace "five recorded files" with the full list or "the recorded files … among them, in this order" |
| 3 | "the consumption receipt (`launch_consumption_missing`);" | built by new bullet; PASS | EXECUTED H1, S1. PROVEN | none |
| 4 | "the pack root recorded in the arm receipt, resolved strictly (`launch_binding_mismatch`);" | "resolved strictly" — unbuilt term of art (`resolve(strict=True)`); FAIL at first use | EXECUTED H2, S3. PROVEN | gloss: "which must exist and re-authenticate" or delete "strictly" |
| 5 | "the launch manifest at the path the consumption receipt recorded (`launch_consumption_invalid`);" | built by new bullet; PASS | EXECUTED H3, S4 (first run). PROVEN. Note: present-but-changed manifest → `launch_binding_mismatch` (S4 second run) — the clause says "gone", which is correct as scoped | none |
| 6 | "the window plan root the manifest names (`launch_binding_mismatch`);" | built by new bullet; PASS | EXECUTED H4, S5. PROVEN | none |
| 7 | "and the start and settle lifecycle receipts (`launch_lifecycle_incomplete`)." | built by new bullet; PASS | EXECUTED H5a/b/c, S6, S7; completion not required on the bundle path (`require_completion=False`, P2 last line; `inputs.py:2777`). PROVEN | none |
| 8 | "Analysis of such bundles therefore runs on the filesystem that armed them;" | "such bundles" — antecedent is the tagged bundle of sentence 2; PASS | consequence, not a probe-able claim; the pack root is arm-time (P4) and the other paths are launch-time (consumption/manifest recorded at launch, `:9740–9747`) | "armed and launched them" is the exact statement |
| 9 | "making the lineage relocatable would be a separate design decision, not a property of this gate." | PASS | non-behavioural | none |
| 10 | "Called directly with a lineage whose pack root does not resolve, the gate refuses with `consumer_identity_set_unauthenticated`, the same label as any pack it cannot authenticate." | code literal glossed in-sentence; PASS | EXECUTED P5 (test OK) for the missing-root case; "any pack it cannot authenticate": CODE-READ — every failure exit of `_frozen_consumer_identity_set` returns `frozenset()` incl. the catch-all at `inputs.py:4039–4048`, mapped to the label at `:4082–4083` | none (writer executes one non-root exit under Q6) |

#### 4b. Exhibit 42 §2.3 (i) — the bullets

| Bullet | (i) first-use | (ii) execution | Correction |
|---|---|---|---|
| consumption receipt: "one-use record written beside the arm receipt (`arm_readiness.consumptions/<arm receipt id>.consumed.json`) when the arm is spent by a launch; it names the launch manifest and the exact command. §What happens after arm calls the same file the one-use consumption record." | builds the term; reconciles the `:672` synonym (P7 shows `**one-use consumption record**` at `:672`); PASS | namespace/name: CODE-READ `:8977–8983`. "beside": the arm receipt lives in the sibling directory `arm_readiness.receipts/` (`:9317`, `consumption_path.parent.parent / arm_reference["path"]`) — loose. "names the launch manifest and the exact command": EXECUTED P4 key set (`launch_manifest`, `exec_argv` in `CONSUMPTION_RECEIPT_KEYS`). "one-use": EXECUTED E1 (second write refused) + CODE-READ `:9761–9764` mapping. | "beside" → "in the custody directory next to the arm receipt's"; add "and carries no pack root of its own" (P4) |
| launch manifest: "JSON declaration of the reviewed command and its inputs; the consumption receipt records its absolute path and digest." | relocates the `:671` definition; PASS | `{path, sha256}` reference: EXECUTED P4 keys + validator (absolute) exercised; `_launch_artifact_reference` returns `str(resolved)` (`:8895`, CODE-READ). PROVEN | demote the bold at `:671` to plain text (else two definitions) |
| window plan root: "absolute directory the launch manifest names as holding the frozen window plan (`window.env`, `window-chain.zsh`); it is created outside the runs roots." | "frozen window plan" — "frozen" unbuilt here; FAIL | absolute: validator exercised (H4). env/chain under it: EXECUTED E2a'/E2b/E2c (`expected_path=window_root/"window.env"`, `:10206–10216`). "created outside the runs roots": **UNVERIFIABLE** — sourced from `docs/phase_2/window_runbook.md`, not in the packet, not enforced by any code I read | delete "frozen" and delete "it is created outside the runs roots" |
| lifecycle receipts: "`start`, `settle` and (when present) `completion` records written as the launched window runs, each chained to its predecessor and to the consumption receipt." | builds the term; PASS | kinds: EXECUTED (expected kinds `launch_start`/`launch_settle` in H5/S6/S7; completion optional per P2 last line and `:10305–10330` CODE-READ). Chaining: EXECUTED E3a/E3b (`settle.predecessor != start_ref` → `launch_consumption_invalid`); `receipt["consumption"] != consumption_ref` CODE-READ `:10259–10263`. PROVEN | use the code's kind names `launch_start`/`launch_settle`/`launch_completion` |
| consuming: "spending its one launch authorization: the launcher writes the consumption receipt and the arm cannot authorize a second launch." | builds "consume"; PASS | EXECUTED E1 (primitive) + CODE-READ `:9755–9764`. Note: the only end-to-end test of this claim, `test_atomic_launch_capability_race_exactly_one_consumer_and_replay_refuses`, is `@unittest.skip`'d (`tests/test_arm_readiness_lifecycle.py:751–755`) | none for the text |

#### 4c. Exhibit 41 §3 Cure C — why not as written

| Clause | Result |
|---|---|
| "for every registered bundle, `_read_bundle` re-reads the consumed arm receipt…" | **FALSE by execution** (P3 B4): untagged bundles are never lineage-authenticated (`launch_lineage_required` `:10598–10606`) |
| "requires every absolute path the lineage records — the pack root, the one-use consumption record, the launch manifest, the window plan root and the lifecycle receipts — to still resolve to the same bytes it recorded" | window plan root has no recorded bytes (it is a directory; only its existence and the env/chain files under it are checked, `:10199–10216`); the enumeration is also incomplete (arm receipt, locator, env/chain, sidecars — P1 §B). Loose |
| "replaying the consumption is what recovers it" | uses "replaying," which the same text's table lists as *deleted* (exhibit 41 §3 first-use table row `replays`); internal inconsistency |
| "input loading raises with the launch-lineage reason code belonging to the artifact that failed" | true but not replicable (see Q5) |
| "and the whole analysis input set is refused" | CODE-READ only: `_read_bundle` raises `AnalysisInputError` (`:2779–2782`); I did not execute the caller. Unproven |
| "It does not re-derive the arm's own PASS/GO decision on this path." | CODE-READ `:10137–10144` (`replay_arm_semantics=False`); true and valuable — imported |
| bullet "launch-lineage reason codes are the seven refusal labels…" | EXECUTED P1 §C (seven members) — imported |

### Q5 — Per-hop codes (exhibit 42 form) or the family (exhibit 41 form)?

**Verdict: AFFIRM the per-hop form.** Weighted consideration: **replication**, because it is the standard the contract itself sets (`:1–8`: "the file it writes … is the receipt; this document is the contract that fixes both") and the standard the packet names; drift risk was weighed and found lighter than claimed. Reasons:

1. Replication: with the family form a reader cannot rebuild which refusal a missing artifact produces; my P1 shows five artifacts map onto three codes in a non-obvious way (a gone manifest is `launch_consumption_invalid`, a changed manifest is `launch_binding_mismatch`; a gone lifecycle receipt is `launch_lifecycle_incomplete` but a mis-chained one is `launch_consumption_invalid`). "The reason code belonging to the artifact that failed" presumes a one-to-one map that the code does not have; it is not merely vague, it is misleading.
2. Drift: the family form is not drift-free either — the family name, its membership (seven today) and the frozenset's name are all literals. The per-hop form names four literals that are already enumerated in one frozenset (`:222–232`) and are exercised by code paths this ruling executed in under 60 lines of scratch; the pre-landing executed-probe rule (Q6) is precisely the mechanism that catches drift at the next edit. Drift caught by a probe is cheaper than a reader misled by prose.
3. Condition: the per-hop text must not claim exhaustiveness. "if any is gone" must be scoped to the named artifacts, and the text must say that other files on the same path (locator, arm receipt, env/chain, sidecars) refuse with their own codes — otherwise the per-hop form re-creates F-N5's shape ("the whole enumeration binds to these codes") one level up.

This concurs with the magistrate's recommendation (exhibit 44 §3 "Cure: Cure C, in the blind-Fable per-hop form") on the choice, but not on the text: the per-hop text as written in exhibit 42 says "five files," which P1 §B falsifies.

### Q6 — Is the proposed rule installable as written? Amended text; drop test

**Verdict on "installable as written": REJECT.** Severity of the defects in the rule text: MATERIAL (an under-specified "first-use table" reproduces the failure mode exhibit 42 §Q3 and exhibit 41 §4 both documented — a hand table by a vocabulary-fluent writer that passes defective text). **REFUSE** the sub-proposition "as ratified by Ed's sentence" *for the paired executed-probe half* — see (e) below; the first-use-table half's ratification is admissible but unverifiable as to completeness (charter §4), which I record rather than rule on, because installability is decidable on the text alone.

Defects in the text as written:

(a) Scope word "contract-prose" is undefined; name the path set (`docs/contracts/*.md`).
(b) "a pre-landing first-use table" does not say what counts as a definition, what text is in scope, or how terms are matched. Exhibit 41 §4 measured four failure modes of the naive rule (case, hyphenation, aliases, scope noise) and exhibit 42 §Q3 measured two false positives in 21 terms; without a mechanical definition the rule is satisfiable by the very artifact (file 34) that missed F-N4.
(c) "an executed probe" does not require the falsifying input; a probe that only shows the happy path proves nothing about a reason-code or order claim (that is how the round-3 clause table passed F-N5: exhibit 41 §4, exhibit 42 §Q3).
(d) "a verifier" must be someone other than the writer, else the second run is a self-grade.
(e) Ratification: exhibit 45c's checklist item 6 reads "pre-landing first-use table as a mandatory gate for defined-term contract edits, yes" and Ed's sentence is "5 and 6 sounds good i trust you." Nothing in the quoted item or sentence mentions the executed-probe pairing; that half comes from exhibit 41 §5 via exhibit 44 §3. The packet's phrase "as ratified by Ed's sentence" therefore overstates what the exhibit shows. Further, the exhibit is a magistrate transcription without an immutable digest of the source transcript; I cannot verify completeness (charter §4). Consequence: the amended text below may be installed as the first-use-table gate only on the strength of exhibit 45c; installing the paired half requires Ed's explicit ratification of the amended text (a single yes/no on the text as amended suffices).

Amended text (exact):

> **Contract-prose gate.** Any edit to a file under `docs/contracts/` that adds, moves, or renames a bold-marked defined term or a backticked code literal must carry, in its landing record under an `Executed evidence` heading and before any verifier sees the text: (1) a **first-use table** built mechanically over the added or moved lines of the diff, listing every noun phrase of two or more words and every backticked literal in those lines, with, for each, the line of its first use in the file and the line of its definition, where a definition is exactly a bold-marked term or a parenthetical gloss on the same or the preceding line, matched case-insensitively with hyphen, space and plural forms treated as equal; declared aliases are listed as rows naming both spellings; any term whose definition line does not precede its first-use line is fixed before landing; and (2) for every **behavioural clause** in the added or moved lines — a clause naming a reason code, an order, a provenance, or containing before / after / first / then / only / never / always / every / all / each / strictly / exactly — an **executed probe**: the command, its pasted output, and the counterfactual input under which the clause would be false, with that input's pasted output; a `file:line` citation is not a probe. A verifier who is not the writer re-runs the table and every probe and diffs the results against the record before the edit lands. Whitespace-only and typo-only edits are out of scope.

Drop test to record with the rule (the two halves are counted separately and dropped separately):

1. Qualifying session: one containing at least one in-scope edit. Sessions with none do not count.
2. Unique catch: a defect the writer's pre-landing table or probe flagged and fixed that the post-landing audit did not independently find. Count writer-side catches (exhibit 42's framing), separately for the table half and the probe half.
3. Retirement question: if a half records zero unique catches across two consecutive qualifying sessions, the retirement of that half is put to Ed with the two session records; no automatic deletion (exhibit 40 Q4).
4. Compliance condition: zero writer-side catches while a post-landing auditor finds a defect of that half's class is a compliance finding, not a drop (exhibit 42 Q4).
5. Noise condition: if table rows marked pre-existing/waived exceed new rows by more than 2:1 across two consecutive qualifying sessions, the scoping clause is re-cut before the half is trusted or dropped (exhibit 41 §5 item 4).

### Q7 — Round-4 formulation (claim list by the magistrate, prose by a seat, different-model verifier re-executing every probe): anything contrary to the charter or the contract's conventions?

**Verdict: AFFIRM (nothing contrary).** Severity: NIT for the two cautions below.

The charter governs adjudication procedure only (§7) and says nothing about who authors fix-round text; the formulation keeps the cold ruling as the landing condition (§5) and adds proof by execution, which is the charter's own evidentiary preference (§7 "Prefer primary evidence"). The contract's conventions — the implementation is authoritative on conflict (`:10–12`), terms are built from physical inputs (`:8`), and the analysis-gate vocabulary lives in the bullet block at `:580–594` — are respected by Cure C(i)+(ii) as corrected.

Cautions (not contrary, but necessary for the formulation to do what it claims):
1. Moving prose authorship does not move *claim* authorship: F-N5 and F-N6 were wrong propositions, not wrong sentences. The claim list must carry, per claim, the probe's expected output written before the probe runs, so a wrong claim fails at probe time rather than being "proved" by a probe written to match it.
2. The claim list must include the non-obvious cases this ruling surfaced (gone vs changed manifest; gone vs mis-chained lifecycle receipt; untagged bundles skip lineage; locator/arm receipt/env-chain/sidecars), or the round-4 text will be correct for exactly the cases the magistrate already knew.

### Q8 — Packet hygiene (charter §6)

**Verdict: REJECT the proposition "complete and neutrally assembled" — the packet is decidable on every question, but carries the following defects.** Effects are named per question.

| # | Defect | Severity | Effect |
|---|---|---|---|
| H1 | Q6's stem "as ratified by Ed's sentence in exhibit 45c" asserts ratification of the *paired* rule; exhibit 45c's quoted item 6 and Ed's sentence cover only the first-use-table half. Leading phrasing. | MATERIAL | Q6: the paired half's ratification is REFUSED (above); installability ruled on the text |
| H2 | Exhibit 45c is a transcription without an immutable digest or line range of its source; completeness cannot be checked (charter §4 requirements for such excerpts). | MATERIAL | Q6: recorded; no ruling rests on completeness |
| H3 | Exhibit 44 (magistrate synthesis) is included "as custody" but contains advocacy on Q1 and Q5 ("The magistrate recommends the per-hop form"; "luna's answer was the one convenient for the branch"). Unlabeled argument inside a packet that says it "offers no diagnosis and no recommendation." | MATERIAL | Q1, Q5: I gave exhibit 44 no weight; the packet should carry seat reports only, or label the synthesis as the proponent's disposition |
| H4 | Packet §5 "Do not lower F-N4's severity" instructs the judge on severity; charter §8 assesses severity independently and §7 says a packet cannot alter authority. | NIT | none (I assess F-N4 MATERIAL on my own reading) |
| H5 | Q2 and Q4 frame the mechanism as "the five missing-file hops," the landed paragraph's own enumeration; the code path reads at least four more files (P1 §B). The framing propagates into exhibit 42's "five recorded files," which Q4 then asks me to grade. | MATERIAL | Q2, Q4: answered with the fuller list |
| H6 | Alternatives treated asymmetrically: Q4 offers only the two Cure C texts; exhibit 40's third cure and exhibit 42's "minimal variant" (family form) are not put as options. Both fail on the same executed facts, so the omission changes no outcome. | NIT | none |
| H7 | Missing exhibits cited by 41/42 as evidence: files 33 and 34 (brief and Sol 266's table — relevant to the "brief-shaped omission" claim in exhibit 44 §4) and `docs/phase_2/window_runbook.md:166–176, 238–241` (relied on by exhibit 42's window-plan-root bullet). | NIT | Q4: the runbook-sourced clause is marked UNVERIFIABLE and struck |
| H8 | Packet pin `fc52bda6` vs checkout `04e45f68`: verified benign (trace files only). | NIT | none |

## 4. Corrected Cure C text (the form that may land)

Every behavioural clause below is tied to an executed probe in §2; the two clauses marked † are code-read and must be executed by the writer under the Q6 rule before landing.

**(i) Add to the bullet block after `**Launch lineage**` (`:584–585`):**

> - The **arm receipt** is the record the arm ceremony writes when it authorizes one launch; its `pack` record carries the **pack root**, the absolute path of the campaign-pack directory on the machine that armed it (`arm_readiness.py` `_pack_record`, stored by `generate_arm_receipt`). [P4]
> - The **consumption receipt** is the one-use record the launcher writes, in the custody directory next to the arm receipt's (`arm_readiness.consumptions/<arm receipt id>.consumed.json`), when it spends that arm's single launch authorization; it names the launch manifest and the exact launch command by absolute path and SHA-256, and carries no pack root of its own. §What happens after arm calls the same file the one-use consumption record. [P4 keys; E1; namespace †`:8977–8983`]
> - The **launch manifest** is the JSON declaration of the reviewed command and its inputs; the consumption receipt records its absolute path and digest. [P4 keys; validator]
> - The **window plan root** is the absolute directory the launch manifest names as `window_plan_root`; the window's `window.env` and `window-chain.zsh` must resolve directly under it. [H4; E2a'/E2b/E2c]
> - The **lifecycle receipts** are the `launch_start`, `launch_settle` and, when present, `launch_completion` records written as the launched window runs; each names the consumption receipt and its predecessor receipt. [H5; E3a/E3b; consumption binding †`:10259–10263`]
> - **Consuming** an arm means spending its one launch authorization by writing the consumption receipt; a second write of the same receipt is refused. [E1]

**(ii) Replace `:609–621` with:**

> That root is the pack root the arm receipt recorded when the arm was issued; the consumption receipt carries no pack root of its own. Before a bundle whose configuration carries the `launch_lineage_required` tag is admitted as analysis input, bundle loading authenticates its launch lineage by reading the recorded files at their absolute paths and refuses at input loading — so the bundle never reaches this gate — if any is gone. In execution order, the artifacts and the reason code each emits when its file is gone are: the lineage locator beside the bundle (`launch_consumption_missing`); the consumption receipt (`launch_consumption_missing`); the arm receipt it names (`launch_consumption_invalid`); the pack root recorded in that arm receipt, which must exist and re-authenticate (`launch_binding_mismatch`); the launch manifest at the path the consumption receipt recorded (`launch_consumption_invalid`); the window plan root the manifest names (`launch_binding_mismatch`); the window's `window.env` and `window-chain.zsh` (`launch_consumption_invalid`); and the start and settle lifecycle receipts (`launch_lifecycle_incomplete`). A receipt whose `.sha256` sidecar is gone refuses with the same code as the missing receipt itself (`joulewise/analysis_engine/inputs.py` `_read_bundle` → `joulewise/arm_readiness.py` `authenticate_bundle_launch_lineage` → `authenticate_launch_lineage`). Analysis of such bundles therefore runs on the filesystem that armed and launched them; making the lineage relocatable would be a separate design decision, not a property of this gate. Called directly with a lineage whose pack root does not resolve, the gate refuses with `consumer_identity_set_unauthenticated`, the same label as any pack it cannot authenticate.

Probe map for (ii): locator B2/X3; consumption H1/S1; arm receipt X1/S2; pack root H2/S3; manifest H3/S4(first run); window plan root H4/S5; env/chain X2; start/settle H5a/b/c, S6/S7; sidecar X4 (consumption sidecar executed; lifecycle sidecars go through the same reader `_read_launch_lineage_primary` `:8835–8859`, †); tag gating B1/B4; refuse-before-row B1/B2; direct call P5. Also demote the bold marks at `:671–672` to plain text so the relocated definitions have one home.

## 5. Observations outside the questions (recorded, no verdict)

- NIT-1: `arm_readiness.py:9020` (`expected_path.resolve(strict=True)`) and `:10222` (`Path(str(consumption["launch_manifest"]["path"])).resolve(strict=True)`) resolve strictly outside any `try`; if the expected file vanishes between the earlier strict resolve and these lines, a raw `FileNotFoundError` escapes `authenticate_launch_lineage`, and `_read_bundle` (`inputs.py:2778–2782`) catches only `LaunchLineageError`. Surfaced by my harness (E2a first attempt; cascade S6 first run), reachable in production only as a race. Not a question in this packet.
- NIT-2: the only end-to-end test of the one-use consumption write, `test_atomic_launch_capability_race_exactly_one_consumer_and_replay_refuses`, is `@unittest.skip`'d ("STRUCTURAL-BLOCKED", `tests/test_arm_readiness_lifecycle.py:751–755`); the "one-use" claim in Cure C(i) rests on the primitive (E1) and a code-read mapping.

## 6. Summary table

| Q | Verdict | One line |
|---|---|---|
| Q1 | REJECT the "second fix round on the same defect" characterization (answer NO; defect = a specific proposition in a specific artifact; F-N4/5/6 are first-round defects of a round-3 paragraph) | gate still mandatory via charter §3.4 and §9; disagrees with exhibit 44 §3 |
| Q2 | AFFIRM: codes executed — consumption `launch_consumption_missing`, pack root `launch_binding_mismatch`, manifest `launch_consumption_invalid`, window plan root `launch_binding_mismatch`, start/settle `launch_lifecycle_incomplete`; landed text wrong on manifest and lifecycle (MATERIAL) | plus four unnamed files on the same path |
| Q3 | AFFIRM: recorded at arm issuance by `_pack_record` → `generate_arm_receipt`; consumption receipt has no pack root (MATERIAL) | executed |
| Q4 | Exhibit 42 (i)+(ii) may land only in the corrected form of §4; exhibit 41 §3 REJECTED as written ("every registered bundle" false by execution) | every sentence graded above |
| Q5 | AFFIRM per-hop form; weighted replication; per-hop text must not claim exhaustiveness | family form is misleading, not merely vague |
| Q6 | REJECT as written; amended text and drop test given; ratification of the paired half REFUSED (exhibit 45c covers the table half only; excerpt completeness unverifiable) | |
| Q7 | AFFIRM: nothing contrary; two cautions (expected outputs in the claim list; non-obvious cases enumerated) | |
| Q8 | REJECT "complete and neutrally assembled": H1/H3/H5 MATERIAL, H2 MATERIAL, H4/H6/H7/H8 NIT; all questions remained decidable | |
