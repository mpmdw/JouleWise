# L8 — OPERATOR + RECOVERY HUMAN FACTORS (xhigh) — readiness-fleet seat report

**Audit baseline:** `docs/process/audit-baseline-manifest.json`, `head_commit ac3fe1d2fb46ab02b2f70eba387165d63bc1de6b` (= origin/main), runbook sha `25a4e809…` (verified byte-identical in this worktree), row-registry sha `d248fdc5…`, ALPHA pack digest `f4c02c8a…`, arm packet cited off-repo at `~/JouleWise-window-custody/t4-session-20260810/arm-packet-alpha-FINAL-20260813.md`.
**Worktree head:** `8937dec9` — three commits past the manifest head; `git diff ac3fe1d2..HEAD --stat` touches only `README.md`, `RUN_STATE.md`, and the manifest itself, so **no artifact in this seat's scope drifted from the baseline** (runbook sha recomputed and matched). Worktree left byte-identical (`git status` clean at exit).
**Charter:** instrument-readiness-audit-charter.md v2, seat 8 (amendment 7). Question audited: what a fatigued operator can do wrong at 2am that no receipt catches, across runbook §5/§5A/§5C, the FINAL arm packet, and the ED-session scripts, plus the 20-minute volatile-horizon implications.

---

## 1. Evidence universe (enumerated before findings) — 24 items

| # | Artifact / behavior | Status |
|---|---|---|
| 1 | Runbook §5 machine/operator preflight (:357-431) | examined |
| 2 | Runbook §5A clock stabilization (:432-596) | examined |
| 3 | Runbook §5B pre-flight calibration screen (:597-685, chain-owned context) | examined |
| 4 | Runbook §5C manual arming + quiet handoff (:686-905) | examined |
| 5 | Runbook §4 freeze-plan contract incl. window.env example (:156-256) | examined |
| 6 | Runbook §6 chain template + launch recipe (:906-1159) | examined |
| 7 | Runbook §10/§11/§12 morning + failure-playbook operator surface | partial (ordering read; §10 rows are L2/L10 primary) |
| 8 | FINAL arm packet, 696 lines, incl. Ed tap script §3 | examined |
| 9 | scripts/ed_session/rail-probe.sh (224 ln) | examined + executed |
| 10 | scripts/ed_session/sampler-checklist.sh (144 ln) | examined + executed |
| 11 | scripts/prewindow_check.sh (199 ln) | examined + executed |
| 12 | scripts/quiet_mac_prep.sh (126 ln) | static only (live run needs sudo/display) |
| 13 | scripts/author_arm_evidence_t0.py (86 ln) | examined + executed |
| 14 | joulewise/arm_readiness_evidence_t0.py (2043 ln — all 15 derivers, capture contract, publication crash matrix) | examined |
| 15 | scripts/generate_arm_readiness.py (159 ln) | examined + executed |
| 16 | joulewise/arm_readiness.py operator surface (generate/verify/consume/discovery/root-policy, ~:2400-4110) | examined (sections) |
| 17 | ALPHA pack operator surface (freeze-0001.json, README self-description, plan bindings) | examined |
| 18 | Behavior: T-0 capture-input production route | examined (absent — B1) |
| 19 | Behavior: 20-min volatile horizon + 5-min arm-receipt fuse timeline | examined |
| 20 | Behavior: reboot fence at verify/consume | examined via executed shipped tests |
| 21 | Behavior: consumption single-use / race | examined via executed shipped tests |
| 22 | Behavior: launch-license enforcement at/after launch | examined (grep + chain read — B7) |
| 23 | Behavior: morning two-tap restore ordering (E-15/E-18/E-16) | examined (procedural only) |
| 24 | ED-session live sudo paths (ABBA arms, supervised sampler) | NOT executed (no sudo) → ED-QUALIFICATION |

**Coverage: 21 / 24** examined; items 7 and 12 partial, item 24 unexecuted (rows below). Unexecuted obligations listed in §5.

---

## 2. Executed probes

### Positive (mechanism works, shown by running it)
- **P1** `sampler-checklist.sh --dry-run --no-sudo` → full staged walkthrough, exit 0.
- **P2** `rail-probe.sh --dry-run --no-sudo` → ABBA order/argv/parser staged, exit 0.
- **P3** `prewindow_check.sh` single-shot → 0.156 s, correctly **BLOCK**ed the busy audit machine (load 4.96).
- **P4** `author_arm_evidence_t0.py` runs through repo-identity, reviewed-main, pack-digest and boot-probe validation and emits a structured, named refusal at the first missing input.
- **P5** Shipped suites at this head: `test_arm_readiness_evidence_t0` **22/22 OK** (includes the full synthetic ACID authored-fifteen → arm → **GO** path — the machinery can reach GO when its inputs exist) and `test_arm_readiness_lifecycle` **12/12 OK**.

### Negative / READY-falsification (minimum two required; eight executed)
- **F1 (skipped steps):** author with empty custody → REFUSE `evidence_author_t0_clock_attestation_missing`, exit 2.
- **F2 (READY-falsification):** three `arm` attempts (clean, dirty-custody, double-tap) at the baseline → all REFUSE `readiness_freeze_receipt_mismatch`, exit 2. **The ALPHA pack cannot arm at the audit baseline.**
- **F3 (typo):** ARM_CONTEXT key misspelling → REFUSE with exact-key detail.
- **F4 (bad flag):** rail-probe `--bogus` → usage, exit 2.
- **F5 (stray sampler, organic):** both ED scripts' censuses REFUSEd on real lookalike processes (other seats' test fixtures with 'powermetrics' in argv) at every census point.
- **F6 (rm -r unset vars):** runbook :823-827 literal with both vars unset → `//arm_readiness.*` no-such-file, exit 1, nothing deleted.
- **F7 (prewindow claims):** measured per-check cost 0.156 s ⇒ `--wait` READY in ~61 s on a clean machine (3 checks × 30 s), falsifying the "this wait IS the ≥10-minute idle" claim; check 4 WARNs (not blocks) without admin; check 8 printed OK **while this live Claude session ran**.
- **F8 (deep cells via shipped harness):** horizon expiry, tamper/coordinated rewrite, publication crash matrix, boot-session voiding of verify/consume, atomic single-consumer race, superseded-receipt refusal — all executed OK (34 tests).
- **F9 (attempted, substituted):** direct monkeypatch falsifiers of verify-expiry/boot-fence against a real baseline receipt could not run because F2 means no receipt exists; covered by F8. Reported, not hidden.

---

## 3. ERROR-INJECTION MATRIX (per-cell catch / no-catch)

Legend: **C** = caught by machine refusal/receipt · **C\*** = caught but the honest path cannot pass either (dead-end) · **P** = partial/indirect · **N** = no machine catch · evidence: (E)=executed here, (T)=executed shipped test, (R)=code read.

| # | Injected error (phase) | Catch? | Mechanism and evidence |
|---|---|---|---|
| A | Skip E-4/E-5 — network time still On | **C** (fragile) | prewindow check 4 WARNs without admin (E); real catch is the authoring CLOCK_PROBE — which itself cannot run under D-004 sudoers (B3): refuses, for the wrong reason (R) |
| B | Skip E-6 — agent/browser/caffeinate alive | **C** | T-0 PROCESS_CENSUS fresh pgrep probes (T: real-census tests); prewindow layer misses claude/t3 (E — observed OK with live Claude) |
| C | Skip/short E-7b idle — clean machine | **C\*** | author refuses capture < 600 s (R, t0:954-957); but the frozen command cannot honestly run ≥600 s on a clean machine (E: F7) — guaranteed dead-end (B2) |
| D | Skip T-0 authoring, go to ARM | **C** | rows with no receipts → REFUSE (T: ACID row tests; E: F1/F2 refuse even earlier) |
| E | Skip arm/verify/consume, LAUNCH directly | **N** | chain performs no receipt check; nothing downstream reads `arm_readiness.consumptions` (R + grep); human close-out item 5 only → **B7** |
| F | Consume after launch (wrong order) | **C** | consume re-runs `_root_policy_refusals`; roots now non-empty → refuse (R: arm_readiness.py:4033-4040) |
| G | Double-tap author | **C**/safe | complete-namespace path re-derives and authenticates byte-identity (`mutated:false`) or refuses `existing_stale`/collision (T: byte-idempotent + append-only tests) |
| H | Double-tap ARM | **C** | numbered receipts + supersession; superseded predecessor refuses at verify (T: semantic-successor test) |
| I | Double-tap consume | **C** | exclusive-write collision → `readiness_record_consumed`; race test proves exactly one consumer (T) |
| J | Relaunch chain / second launch | **P** | campaign locks + occupied roots + writer custody refuse downstream; chain quarantines only stale (dead-pid) locks (R) — cross-confirm at L2/L3 |
| K | Reboot mid-sequence | **C** | boot_session_id checked at evidence discovery, verify, consume → `readiness_record_expired` (T: boot-session voiding test) |
| L | E-8/E-9 from the wrong directory (dev repo) | **C** if capture honest | deriver requires capture cwd == reviewed checkout and exact argv script paths (R: t0:1153-1156, 1181-1184); hazard reverts to B1 (captures hand-produced) |
| M | Launch from wrong plan root / altered chain | **P** | launch-manifest binds exact chain path + REPO literal at authoring (R); the physical launch itself is unchecked (cell E) |
| N | Hand-typed ARM_CONTEXT typo | **C** | exact-key validation (E: F3) |
| O | Hand-edit / tamper a receipt | **C** | sidecar + canonical-bytes + full semantic replay at verify (T: tamper and coordinated-rewrite tests) |
| P | Pause > 20 min after authoring | **C** | volatile horizon at discovery → REFUSE (T: short-horizon consumption + expiry tests) |
| Q | Pause > 5 min between arm and consume | **C** | arm-receipt `validity_ns` = 300 s → `readiness_record_expired` (R: :3596, :3952-3955) — fuse documented **nowhere** operator-visible (should-fix) |
| R | New process started inside the horizon | **N** (bounded) | probes are not re-run at arm/verify/consume; 20-min TOCTOU accepted by design (R: t0:45-47) — prohibition needs an ABORT row in the recut packet |
| S | Re-author `rm -r` on a wrong-but-existing path | **N** | no shape check, no confirmation, irreversible (E: F6 shows only the unset-vars case is benign) |
| T | E-16 restore before magistrate finishes | **N** | systemsetup succeeds silently; only honest §12 item-20 timestamps reveal it — purely procedural two-tap guard |
| U | Return early / wake display mid-window | **P** | no operator-side catch; consequences fall to member environment/CPU admission (L3/L9 scope) — window-loss, not corruption |
| V | Stray sampler at ED-qualification | **C** | census refusal before any capture (E: F5, organic) |

**Summary:** 14 C, 1 C\*, 4 P, 4 N. The four N cells are findings B7 (launch license), S (rm -r), T (restore order), R (bounded TOCTOU, by design).

---

## 4. Findings (severity-tiered; each with location and concrete failure scenario)

### Blockers
- **B1 — No shipped producer for the T-0 inputs** (`arm_readiness_evidence_t0.py:448-499,595-724` vs runbook :802-838). The author consumes nine **byte-canonical** JSON inputs (six E-step command captures with monotonic bounds and boot id, clock-attestation, arm-context, launch-manifest) in `…/arm_readiness.t0.inputs/`. No tool writes them; no runbook or packet step mentions them; tests fabricate them. Executed: the documented E-sequence dead-ends at REFUSE (F1). Fail-closed, but the only 2am path forward is hand-forging canonical JSON with invented `monotonic_ns` — which the receipts cannot distinguish from honest capture. *This is the fatigue-shaped hole: absence of tooling converts an honest operator into a forger or ends the night.*
- **B2 — E-7b cannot prove the ≥10-minute idle** (`prewindow_check.sh:36-37,177-198` vs `t0.py:49,954-957`; runbook :366-373, :780-789 claims the wait *is* the idle). Clean machine → READY in ~61 s (measured 0.156 s/check) → author refuses `< 600 s`. Better prep ⇒ certain refusal. If the author check were removed instead, the window would launch into the XProtect idle band that took a9's first member — now fatal, since the one-launch capability makes relaunch a newly frozen session.
- **B3 — CLOCK_PROBE cannot run under D-004 sudoers** (`t0.py:884-905`; decision_log :316; runbook :509-514). `sudo -n systemsetup -getusingnetworktime` at authoring time: sudo timestamp is >10 min cold (E-7b sits between E-5 and the author) and the NOPASSWD entry covers only powermetrics → probe fails → author REFUSE → no GO, no documented recovery at night.
- **B4 — Stale freeze receipt: the pack cannot arm at the baseline** (freeze-0001.json binds `pack_root=/Users/edr/JouleWise-measurement-20260813/…`, pre-#149 schema; current digest `f4c02c8a…`). Executed three ways: every arm refuses `readiness_freeze_receipt_mismatch` (F2). Plus the pack still reads "unfrozen draft / **The pack is not armable.**" (M-2/D-13, magistrate ruling still open) against a §5C entry gate that treats placeholder text as NO-GO. Work: re-freeze at the final head + written M-2 ruling.
- **B5 — The FINAL arm packet is stale and would run the wrong night** (packet frozen tree `49dcc49a`/digest `6246b618` vs baseline `ac3fe1d2`/`f4c02c8a`). Its §3 tap script — expressly "written to be executed without reading the runbook" — has no T-0 authoring step, no 20-minute horizon, no 5-minute fuse, no re-author rule, and expects §0.6's now-false "no shipped authoring route." A tired Ed following it verbatim dead-ends (or improvises) exactly where the current runbook inserts the author.
- **B6 — Runbook §4/§6 templates fail the author's machine contract** (runbook :181-206, :971 vs `t0.py:571-593,652-676,1138-1156`). Four independent guaranteed refusals if the freeze-step copies the runbook: `$`-containing window.env values (parser refuses); missing `CUSTODY_ROOT`/`CLAIM_BACKUP_DEST`/`BOUND_BACKUP_DEST` (example has `WINDOW_CUSTODY_ROOT` + single `BACKUP_DEST`); `FROZEN_PLAN` pointed at a custody reservation JSON while the deriver requires the pack's `calibration_plan.json` byte-identity for E-8/E-9; chain `REPO="${MEASUREMENT_REPO:-…}"` fails the exact-binding regex. All fail closed; all are night-discovered dead-ends.
- **B7 — Launch license is not machine-enforced** (chain :964-1148 checks nothing; `arm_readiness.consumptions` referenced nowhere outside the arm-readiness modules). A launch with zero arm ceremony collects a normal-looking window; the required consumption receipt neither traces through a machine consumer nor fails closed — human close-out only. Cross-confirm the consumer side with L5/L6/L7/L10; the cheap fix is a chain-preamble receipt check.

### Should-fix
- **S1 — ARM_CONTEXT must be retyped inline** though the authenticated `arm-context.json` already sits in custody (`generate_arm_readiness.py:58-70`); accept a custody path or freeze the `--arm-context "$(cat …)"` literal.
- **S2 — 5-minute arm-receipt fuse undocumented** (`arm_readiness.py:3596`); a benign pause between E-9a and E-9c refuses and nothing tells Ed the licensed recovery (re-arm within the surviving horizon).
- **S3 — Re-author `rm -r` has no shape guard** (runbook :823-827); a mistyped `$PACK_ID` hitting a sibling pack's custody deletes it irreversibly, receipt-free.
- **S4 — Morning restore-before-handback has no machine catch** (runbook :557-568; packet §3.5); two-tap ordering is purely procedural.
- **S5 — In-horizon TOCTOU** (design-bounded, `t0.py:45-47`): post-authoring process starts are never re-probed; the prohibition needs an explicit ABORT row in the recut packet.

### Nits
- **N1** prewindow check 8 omits claude/t3 (observed passing with a live Claude session); check 4 WARN-only without admin.
- **N2** E-14 do-not-return-before time is 2am hand arithmetic (6.28 h = 6 h 16.8 m); freeze a `date -v+377M` literal.
- **N3** ED-script census is substring-based → spurious refusals beside any dev activity (fails closed; observed live).

---

## 5. Unexecuted obligations
1. `quiet_mac_prep.sh` live run (sudo + display sleep) — static review only.
2. Live sudo arms of `rail-probe.sh` / `sampler-checklist.sh` — ED-QUALIFICATION.
3. E-9 reservation double-reserve/live-writer behavior against a ledger copy — code/tests only; L2 primary.
4. Runbook §10 refusal-row completeness for the operator (packet O-9's missing one-page extract) — flagged to L2/L6/L7.
5. Morning §9/§11 magistrate procedures beyond ordering — L10 scope.
6. Real custody artifacts in `~/JouleWise-window-custody` read, deliberately not touched.

## 6. ED-QUALIFICATION rows (stable capabilities; close before the sitting)
- **ED-Q-L8-1:** privileged read path for the CLOCK_PROBE (`systemsetup -getusingnetworktime` scoped sudoers entry, or ratified `sudo -v` warm-up literal) — decided AND exercised once in a tap block (binds B3).
- **ED-Q-L8-2:** full arm-sequence dress rehearsal on the recut packet (capture wrapper → author → arm → verify → consume, scratch custody/synthetic roots, real ≥10-min wait), timed against the 20-min horizon + 5-min fuse.
- **ED-Q-L8-3:** live sampler-checklist + rail-probe executions (charter steps 2-3; dry-run staging verified here).
- **ED-Q-L8-4:** live `quiet_mac_prep.sh` confirming its three OK literals match `_quiet_capture`'s verbatim requirements.

## 7. 20-minute volatile-horizon operator implications (seat deliverable)
The horizon starts at the author's post-derivation `validity_origin`, so the full 20 min is available at publication. Ceremony inside it: `arm` (seconds) → `verify` → `consume` → physical launch, with the **separate 5-minute arm-receipt fuse** (B/S2) nested inside. It is adequate **only with paste-ready literals**: the sole live-substituted token is the arm-receipt path (copy error → namespace/io refusal — caught). Expiry mid-flow refuses cleanly; re-arm inside the surviving horizon is licensed but undocumented; full re-authoring after expiry requires the `rm -r` (S3) and — because a REFUSE arm receipt then occupies the namespace (`t0.py:1511-1517`) — is intentionally impossible after any refused ARM: refusal genuinely ends the night, mechanically. The prohibition on starting new processes inside the horizon is un-re-probed (S5). All of this must appear in the recut packet (B5), which today contains none of it.

## 8. Verdict — **NOT-READY** (work orders WO-L8-1 … WO-L8-8)
The refusal machinery itself is excellent — every executed and test-executed injection failed **closed**, and the synthetic ACID path proves GO is reachable when inputs exist. What is not ready is the **operator path to a legal launch**: at the audit baseline the documented night procedure cannot produce a GO receipt for at least four independent mechanical reasons (B1 missing input producer, B2 idle contradiction, B3 clock-probe privilege, B4 stale freeze receipt), the tap script Ed would actually hold is stale (B5), the runbook's own templates refuse against the shipped contract (B6) — and the one true fail-open, launch-without-license (B7), is exactly the cell the council question exists to catch. Work orders: **WO-L8-1** capture wrapper + §5C rewrite; **WO-L8-2** prewindow min-idle floor + re-frozen literal; **WO-L8-3** clock-probe privilege route + rehearsal; **WO-L8-4** re-freeze pack + M-2 ruling; **WO-L8-5** recut FINAL packet at the final head (horizon, fuse, paste-ready literals, E-14 date literal); **WO-L8-6** align §4/§6 templates with the author contract (or generate them mechanically); **WO-L8-7** machine-enforce the launch license; **WO-L8-8** governed `reauthor-clean` replacing raw `rm -r`.

*Seat L8, xhigh. Tree byte-identical at exit; all probe writes confined to the session scratchpad and /tmp/ed-session (removed).*