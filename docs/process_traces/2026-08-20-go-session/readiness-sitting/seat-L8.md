# SEAT L8 — OPERATOR + RECOVERY HUMAN FACTORS (xhigh, GATING)
## READY-CANDIDATE COUNCIL SITTING, 2026-08-20 — seat report

**Head this verdict attaches to:** `5bd7acf` (merge of PR #160,
`integration/phase2-transaction`). Verified in the read-only worktree
`…/scratchpad/wtRC-OPUS`, `git status --porcelain` empty. Every SHA the packet
called branch-only is now an ancestor of the sitting head: `5e38f1e`, `eb7f6c6`,
`94dc3b3` (freeze-0003 family), `0e96dbb` (D-149), `79a4cd0` (GO-receipt
template), `a61ac92` (WO-T0-PRODUCER), `a59c795` (#154), `ad14ac4` (rehearsal
builder), `f392ff6`/`bd333de` (WO-LAUNCH-BINDING stages 1–3). The `_v3` packs
and `freeze-0003.json` are present in the tree. **P-13 is cured; every
disposition below was re-verified at `5bd7acf`, not inherited from the packet.**

**ROW VERDICT: STILL-OPEN** — which under charter amendment 11 is recorded as
**NOT-READY (+ work orders)**. CONDITIONALLY-READY is not an available verdict:
READY-WITH-CONDITIONS was deleted precisely because a fleet returning one
conditional pass is a fail-open hazard (`01-SESSION-BRIEF.md` §2.1).

---

## 1. ENUMERATED EVIDENCE UNIVERSE (independent, at `5bd7acf`)

The 2026-08-15 seat's 24-item universe is **not inherited**. It was drawn at
`ac3fe1d` and is stale by construction — it predates `scripts/capture_t0_step.py`
(1,060 ln), `scripts/launch_window.py` (304 ln), `scripts/joulewise-network-time.sudoers`,
`docs/process/rehearsal-operator-card.md`, `scripts/ed_session/build_rehearsal_env.sh`,
`docs/process/d149-go-receipt-template.md`, `docs/process/window-run-cards/`,
the PACK_AUTHENTICATION environment fingerprint, and the D-148.5 r3 halt trigger.
**Adversarial re-count executed: the audited denominator omits at least 9 of
today's 31 operator-path items — ≈29% of the surface it purports to cover.**
That is the L2 attack applied to this seat, and the old denominator falls.

My universe, 31 items in four classes:

*A. Operator-facing documents (8):* window_runbook.md (§4/§5/§5A/§5C/§6/§10/§11/§12);
rehearsal-operator-card.md; d149-go-receipt-template.md;
window-run-cards/shakedown-v3-first-light.md; ed-evening-checklist.md;
ed-batch-packet.md; alpha_arm_readiness.md; the one arm packet
(`~/JouleWise-window-custody/t4-session-20260810/arm-packet-alpha-FINAL-20260813.md`).

*B. Operator-path executables (11):* capture_t0_step.py; author_arm_evidence_t0.py;
generate_arm_readiness.py; launch_window.py; prewindow_check.sh; quiet_mac_prep.sh;
backup_runs.sh; joulewise-network-time.sudoers; ed_session/build_rehearsal_env.sh;
ed_session/sampler-checklist.sh; ed_session/rail-probe.sh.

*C. Machine surfaces the operator trips (6):* arm_readiness_evidence_t0.py (censuses,
horizons, clock probe, `_quiet_capture`); arm_readiness.py (arm/verify/consume, the
300 s fuse at `:6101`); arm_readiness_evidence.py (PACK_AUTHENTICATION fingerprint,
new under D-148.5 r3); runbook §10 refusal-row set incl. four `launch_*` rows;
window-chain.zsh template + FD-198 handoff; capture-era / D-146 claim-barrier refusals.

*D. ED / automation (6):* `~/JouleWise-window-custody/ed-qual-20260817/`; the
(absent) rehearsal custody root; quiet_mac_prep live-run evidence; D-149 auto-GO
condition set and GO-receipt filling; the D-148.5 r3 mandatory halt trigger
(T-0→arm ≤ 15 min, p99 arm→consume ≤ 4 min); the seat's own 22-cell (A–V)
error-injection matrix.

**COVERAGE: 22 / 31 examined against primary evidence at `5bd7acf`.**
Not examined (9, named): launch_window.py internals; author_arm_evidence_t0.py;
backup_runs.sh; build_rehearsal_env.sh; the FINAL arm packet's 67,081 bytes
re-read; arm_readiness_evidence.py fingerprint code; the D-146 capture-era
operator refusal surface; window-run-cards/shakedown-v3-first-light.md content;
the 22-cell matrix re-score (that is a work order, not a seat probe).

**Honesty on the denominator:** 31 is my own enumeration and therefore
self-nominated in exactly the way the verdict warns about. I attacked the *prior*
denominator and it fell; I have not had mine attacked. Treat 22/31 as a floor.

---

## 2. EXECUTED PROBES (all at `5bd7acf`)

| # | Probe | Result |
|---|---|---|
| **P1** | *(negative, F13)* Ran check-8's exact pattern against the live process table | Pattern `codex exec\|codex-run\|run_campaign\|window-chain` does **not** match live `claude daemon`, `codex mcp-server`, or `scripts/claude-bridge-mcp.mjs`. Reproduced at head. |
| **P2** | *(negative, ED-Q-L8-1 / T16)* `sudo -n /usr/sbin/systemsetup -getusingnetworktime` | **`sudo: a password is required`.** The read vector is still ungranted at the merged head. |
| **P3** | *(A/B executed, F6)* Loaded `capture_t0_step._parse_window_environment` and fed it the runbook's own §4 block | **B:** §4 verbatim (25 keys) → PARSED OK. **A:** §4 + the two keys §6 `:1191-1192` orders → **REFUSED** `window.env exact keys differ; missing=[], unknown=['ARM_RECEIPT','LAUNCH_MANIFEST']`. |
| **P4** | *(negative, F5 + ED-Q-L8-2)* Custody enumeration | No rehearsal root anywhere under `~/JouleWise-window-custody/` (glob: no matches). FINAL arm packet mtime **Aug 13 20:21**, unchanged; no successor packet. |
| **P5** | *(negative, ED-Q-L8-4)* `grep -rl quiet_mac_prep ~/JouleWise-window-custody/` | Only source copies inside a repo clone. **Zero execution artifacts.** |
| **P6** | *(negative, ED-Q-L8-3)* Timeline reconstruction | Sampler logs `…T010430Z`/`T011634Z`/`T011840Z` and rail probe `…T011943Z` = 18:04–18:19 PT, inside the decisive-replay span (work dirs 17:46 & 18:12 PT; log final 21:52 PT). `rail-probe-load-note.txt`: `concurrent_load=decisive_replay_unittest` + charge-termination mid-sequence. |
| **P7** | *(positive, F9)* Fuse visibility | `validity_ns: int = 300_000_000_000` alive at `arm_readiness.py:6101`; **zero** operator-visible hits in window_runbook.md, rehearsal-operator-card.md, alpha_arm_readiness.md. |
| **P8** | *(staleness count, F6)* Family/checkout binding | runbook names `…-20260813` **×10**, `…-20260818` **×0**; `_1p5b_v2` **×5**, `_1p5b_v3` **×0**. freeze-0003 `pack_identity.pack_root` = `/Users/edr/JouleWise-measurement-20260818/…_v3`. `capture_t0_step.py:344-348` refuses when the pack's repo ≠ the executing tool's repo; `:465-475` requires the chain's single literal `REPO=` to equal the resolved repository. |
| **P9** | *(negative, D-148.5 r3)* Post-packet ruling consequences | `evidence_author_environment_changed` / environment-noise guidance: **absent from every operator surface**. Mechanical halt-trigger gate: **absent from `scripts/` and `joulewise/`**. D-149 GO evaluator: unbuilt (`d149-go-receipt-template.md:63` "MAY be built"); only `## WO-D149-GO-EVALUATOR` at `TASK_QUEUE.md:373`. |
| **P10** | *(desk probe, ED-Q-L8-4 — the cheap half)* Diffed `quiet_mac_prep.sh` OK literals against `_quiet_capture` | The three required literals (`arm_readiness_evidence_t0.py:1052-1055`) match `quiet_mac_prep.sh:48,99,115` **verbatim — this half PASSES.** But see F16 below: the same predicate refuses on **any** `FAIL:` substring, and the repo's own record calls one of this script's FAILs a known false signal. |
| **P11** | *(positive, P-13)* Merge verification | All ten packet-named branch-only SHAs are ancestors of `5bd7acf`; `_v3` packs and `freeze-0003.json` present. |

### READY-falsification attempts (mandatory, one per finding I was minded to pass)

- **F1 (producer):** attempted to pass on "shipped, merged, sequence-enforcing".
  **Falsified for the operator limb** — P3 shows the tool's *first* step (E-4
  context load) refuses on a `window.env` authored per the runbook's own §6
  instruction; and no human or machine has run the tool end-to-end (P4).
  Mechanism limb survives; operator-path limb does not.
- **F2 (dwell):** attempted to pass on `MIN_CLEAN_DWELL_S=600` + `clean_since`
  reset + the untouched 600 s author floor. **Partially falsified** — P1 shows
  the dwell's admission test (check 8) cannot see `claude`/`t3`/`mcp-server`, so
  600 continuous "clean" seconds can accumulate on a machine running the exact
  agent fleet D-149's lead-driven posture keeps alive. The arithmetic
  contradiction (540 s gap) *is* closed; the dwell is not the quietness
  guarantee it appears to be. Compensating layer (the T-0 author's own
  `codex|claude|t3` census) is real, so the night still fails closed — later,
  after the operator has spent the ten minutes.
- **F3 (clock privilege):** attempted to pass on the installed, ground-truth-verified
  D-127 write grant. **Falsified as to the row and as to D-149** — P2 proves the
  read vector still prompts; E-4's prior-state read is an interactive paste;
  a no-hands window cannot perform it.
- **F6 (templates):** attempted to pass on "four of four contract violations
  cured". **Falsified** — three live guaranteed-refusal vectors at head (P3 key
  set; P8 REPO literal; P8 family/checkout). Same defect class as the original
  blocker, not documentation lag.

---

## 3. PER-FINDING DISPOSITIONS (15 findings + 1 seat-new)

Vocabulary: **DISCHARGED** (repair verified at head) · **NOT-DISCHARGED** ·
**STRUCK** (2026-08-15 Disposition 4).

| # | Finding | Disposition | Evidence at `5bd7acf` |
|---|---|---|---|
| **F1** | No shipped T-0 input producer *(blocker)* | **DISCHARGED (mechanism) / NOT-DISCHARGED (operator path + authenticity)** | `capture_t0_step.py` merged (`a61ac92`); §5C rewritten; nine inputs, no-clobber, `_require_sequence`. Authenticity limb was **not engineered away** — superseded as a claim (#154 `a59c795`) and ACCEPTED as a registered limitation (D-148 rul.6). I accept the risk-acceptance as legitimate authority but record it as a **relabel, not a repair**. Operator path unproven: never executed end-to-end (P4), and refuses at E-4 under the runbook's own §6 instruction (P3). |
| **F2** | E-7b cannot prove the ≥10 min idle *(blocker)* | **DISCHARGED (narrow)** | `prewindow_check.sh:37,177-199` implements the ruled `clean_since` remedy; author floor untouched; a third 600 s span check at the capture layer. Narrow because the admission test is blind (P1) and no live 600 s dwell has ever been recorded. |
| **F3** | CLOCK_PROBE sudo gap *(blocker)* | **DISCHARGED (code contract) / NOT-DISCHARGED (row + D-149)** | Probe re-shaped to the granted `-setusingnetworktime off` write; grant installed, digest `7dfe980b…`, ground-truth flips in custody. But P2: the read still prompts; ED-Q-L8-1 as written is unmet; hands are required at E-4 under a no-hands ruling. |
| **F4** | Stale freeze receipt | **STRUCK** (`council-verdict.md:44`) | Nothing to adjudicate. Note only: its M-2 clause was routed to a cold gate that ruled (D-140), and the pack world has since moved `_v1`→`_v2`→`_v3` and is now ruled to move again to `_v4` (D-148.5 FINAL). |
| **F5** | FINAL arm packet stale *(blocker)* | **NOT-DISCHARGED — no repair of any kind** | P4: the packet is byte-unchanged since 2026-08-13 20:21 and is still the only arm packet. Its nearest substitute (rehearsal card) is `_v2`/freeze-0002-bound, self-declared non-claim, and missing the fuse and the re-author rule. Everything WO-L8-5 bundled — paste-ready E-9a/b/c literals, horizon, fuse, re-author rule, E-14 `date(1)` literal, F12 ABORT row — still has no home. |
| **F6** | §4/§6 templates fail the author's contract *(blocker)* | **NOT-DISCHARGED — and the class is live at head with executed proof** | Four original refusals cured, but **three new/residual guaranteed refusals**: (a) P3 — §6 `:1191-1192` orders two keys that `_ENV_KEYS` refuses as `unknown`; the two operative documents cannot both be satisfied by one `window.env`; (b) P8 — the §6 chain's literal `REPO=/…-20260813` cannot equal the repository resolved from a freeze-0003 pack at `…-20260818`; (c) P8 — §4 binds `_v2` at the retired checkout, ×10 vs ×0. |
| **F7** | Launch without ceremony not machine-caught *(blocker)* | **NOT-DISCHARGED (by the repo's own text)** | Large, cold-gated, merged repair (`launch_window.py`, FD-198, atomic no-clobber primary, four `launch_*` refusal rows). But `window_runbook.md:1087-1088`: "**not current authority to launch**: every D-117 physical launch remains NO-GO"; `:1129` "E-10 remains NO-GO"; `TASK_QUEUE.md:543` A1 `READY [AGENT]`, "remaining: stage 4 successor flag inside the transaction. **Launch stays NO-GO**". |
| **F8** | ARM_CONTEXT inline only *(should-fix)* | **NOT-DISCHARGED** | `generate_arm_readiness.py:47,65` unchanged: "--arm-context must be the JSON object itself, not a path". The producer now writes the authenticated `arm-context.json` to custody and the arm CLI still refuses to read it from there. The `$(cat …)` literal lives only in a rehearsal card. |
| **F9** | 5-minute fuse invisible *(should-fix)* | **NOT-DISCHARGED — and newly load-bearing** | P7. Worse post-packet: D-148.5 r3 B-3 installs 300 s as the status-quo V5 default **and makes the first shakedown window measure the T-0→arm and arm→consume gaps against a mandatory halt trigger**. A number the operator cannot see now gates a campaign-halting bound. |
| **F10** | Raw `rm -r` re-author cleanup *(should-fix)* | **NOT-DISCHARGED** | `window_runbook.md:1017` `/bin/rm -r --` over three `$PACK_ID`-interpolated namespaces; guard is the prose "first verify". No `reauthor-clean` anywhere in `scripts/`, `joulewise/`. WO-L8-8 unbuilt and unowned. |
| **F11** | Restore-before-close-out *(should-fix)* | **NOT-DISCHARGED (documentation-only)** | Runbook `:627-637` orders and requires recording the restore; no machine catch. Sibling's added fact stands: the shakedown driver restores on an **EXIT trap**, i.e. immediately — the very premature restore S4 warns of, now realised in tooling. |
| **F12** | In-horizon TOCTOU *(should-fix)* | **NOT-DISCHARGED** | Prohibition prominent (`:1003-1009`); no re-probe at arm/verify/consume; no ABORT row because there is no packet. D-149 checks quietness **once at T-0**; the enforcement was a human reading a sentence, and D-149 removes the human. |
| **F13** | prewindow check-8 pattern *(nit → I RAISE to should-fix)* | **NOT-DISCHARGED, severity raised** | P1, executed live. Check 4 was properly restructured under D-127; check 8 is byte-unchanged at `:150`. Severity raised because B2's repair made check 8 the admission test for the 600 s dwell — the blast radius grew after the finding was scored. Its owning WO (A4) is BLOCKED on ED-Q-L9-3, but this is a four-token regex edit, not census semantics: the blockage is a scheduling artifact. |
| **F14** | E-14 hand arithmetic *(nit)* | **NOT-DISCHARGED** | No `date(1)` literal anywhere; the anchor (E-14) no longer exists in the runbook after renumbering, so the nit survives only inside the un-recut packet. Possibly mooted for no-hands windows — **not formally retired by any ruling**, so it rides into the night if the successor packet is cut from the old one. |
| **F15** | ED-session substring census *(nit)* | **NOT-DISCHARGED (fails closed)** | `sampler-checklist.sh:48-50` / `rail-probe.sh` unchanged; over-match confirmed as fixture ground truth 2026-08-17. A4 still `BLOCKED — ED-Q-L9-3` at `TASK_QUEUE.md:545` although the fixture was captured 2026-08-17 — a stale kernel row or an unstated stricter precondition; either way the queue misrepresents the state. |
| **F16** | **SEAT-NEW (blocker-shaped): `_quiet_capture` refuses on a FAIL the repo itself calls a known false signal** | **OPEN** | `arm_readiness_evidence_t0.py:1056-1058` refuses if **any** `FAIL:` substring appears in stdout *and* requires the literal "OK: display verification reports all online displays asleep." Those are the two exclusive branches of the same `if/elif` at `quiet_mac_prep.sh:96-99`. `RUN_STATE.md:3714` and `:3858-3861` record that script's "Graphics capability" FAIL as "**the known false signal on this build**", with `pmset -g log` named as the authoritative check. If that signal still fires, E-7a authoring refuses **deterministically and twice over**, with no documented recovery — the exact F1/F2/F6 shape. Unverified whether it still fires on the current build: that is precisely what ED-Q-L8-4 exists to establish, which promotes ED-Q-L8-4 from a documentation row to a blocker precondition. |

### Concrete failure scenario per open finding (compressed)

- **F5/F8/F9/F12/F14:** Ed follows the only arm packet that exists, dead-ends at
  the point the current runbook inserts the author step, improvises, pauses six
  minutes to report a receipt sha, and reads `readiness_record_expired` as a dead
  night because the 300 s fuse and its licensed re-arm are written nowhere.
- **F6 (executed, P3):** Ed authors `window.env` per §4, appends the two keys §6
  orders, and E-4 — the first capture — refuses
  `evidence_author_t0_capture_environment_invalid … unknown=['ARM_RECEIPT','LAUNCH_MANIFEST']`.
  Omitting them instead, `window-chain.zsh` aborts unbound under `set -euo pipefail`.
  Either way the night ends, and the refusal arrives after quiet-prep and the
  ten-minute dwell are already spent.
- **F7:** stage 4 lands after a READY, calibration-slot writer enforcement is
  still absent, and a window is armed against documents that say NO-GO.
- **F10:** a mistyped `$PACK_ID` deletes a sibling pack's three T-0 namespaces
  irreversibly, receipt-free, at 2 a.m.
- **F11:** automation restores network time on exit while §9/§11 close-out is
  still reading clock-anchored evidence.
- **F13 (executed, P1):** the loop's own `claude`/`t3`/`mcp-server` processes are
  invisible to check 8; the dwell certifies 600 "clean" seconds; the T-0 census
  refuses ten minutes later.
- **F15:** any dev activity beside a qualification run refuses it spuriously.
- **F16:** E-7a refuses on a benign, previously-documented display signal.

---

## 4. SIBLING-DIVERGENCE ADJUDICATION (`rows/ROW-L8.md` vs `17-ROW-L8-…`)

The two assemblies are independent; where they disagree the disagreement is
evidence. Eight material divergences, adjudicated:

1. **ED-Q-L8-1.** `rows/` = "CLOSED WITH DIRECT PRIMARY EVIDENCE (one contract
   caveat)". Sibling/`30-…` = **PARTIAL**. **SIBLING UPHELD, and extended:** P2
   executes the row's own literal probe and it prompts for a password. The row
   asked to prove a read path *or* ratify a `sudo -v` warm-up; neither was done,
   and the substitute (interactive paste) collides with D-149. `rows/` frames a
   contract re-shape as a closure; that is the fail-open direction.
2. **ED-Q-L8-3.** `rows/` = "CLOSED (partial on one clause)". Sibling = **PARTIAL**
   ("not a quiet machine"). **SIBLING UPHELD, and extended:** P6 shows *both*
   halves — sampler as well as rail probe — ran inside the 3 h 40 m decisive
   replay. `rows/` credits "cadence mean 1.0128 s, zero orphans" without noting
   the sampler's own load overlap.
3. **The new B6-class defect (`ARM_RECEIPT`/`LAUNCH_MANIFEST` vs the exhaustive
   25-key set).** Present **only** in the sibling; `rows/` concluded F6's
   "residual is family-staleness, **not contract violation**". **SIBLING UPHELD
   AND ELEVATED:** P3 executes it. It is a contract violation, it is guaranteed,
   it fires at the first capture, and both sides of the contradiction are in the
   sitting head. This is the sharpest divergence in the row and it changes F6's
   disposition from residual to NOT-DISCHARGED.
4. **Terminal-review trailer.** Carried as a sub-row only by the sibling.
   **SIBLING UPHELD:** `capture_t0_step.py:288-316` is a strict, early-firing
   consumer (three exact trailers + `reviewed_main` clean *and* exact_match) with
   no producer tool and its manifest-pinning half unstarted Phase-3 work. The
   sibling's own probe 3 ("can E-4 pass while the re-freeze is branch-only?") is
   now **moot in the right direction** — the merge cures the branch-only limb;
   the producer gap survives it.
5. **Coverage.** `rows/` does not re-enumerate; sibling attacks the 24-item
   denominator (~1,700 new lines). **SIBLING UPHELD;** I re-enumerate to 31 and
   record 22/31 (§1).
6. **Reading head.** `rows/` read at `b92b43d`; sibling at `79a4cd0` and
   additionally diffed `main`↔HEAD across the eight L8 files (only D-079
   constants differed). **No divergence survives** — both are superseded by
   `5bd7acf`, at which I re-verified every disposition. The sibling's diff
   discipline was the better method and its conclusion is now moot by merge.
7. **F13 severity.** `rows/` = "PARTIALLY ADDRESSED"; sibling notes check 8 now
   gates the B2 dwell. **SIBLING UPHELD** and I raise the severity to should-fix
   on executed evidence (P1).
8. **F1 framing.** `rows/` = "FULLY ADDRESSED as a producer"; sibling splits it
   into mechanism-READY + fabrication-limb-superseded-by-ruling and adds that
   `TASK_QUEUE.md:106` is stale prose. **SIBLING'S SPLIT ADOPTED**, with my
   addition that the operator limb is independently unproven.

**Pattern worth recording for the sitting:** on all six substantive divergences
the sibling assembly is the more conservative and the more correct, and `rows/`
errs consistently in the fail-open direction (closing ED rows that are partial,
demoting a contract violation to staleness). That is the same falsely-clean
signature the 2026-08-15 verdict warned about, reproduced inside the packet.

---

## 5. THE FOUR SUDO ED-QUALIFICATION ROWS

Charter § Ed rows (amendment 10): ED-QUALIFICATION rows are **stable
capabilities** performed *before* the sitting — "stable evidence cannot be
deferred"; **only T0 (perishable) rows may remain open**. None of this seat's
four is a T0 row.

| Row | Status | Evidence / basis |
|---|---|---|
| **ED-Q-L8-1** (privileged read path for CLOCK_PROBE) | **PARTIAL — not closed as written** | Real and verified for the *write* vector: `sudoers-digest.txt` = `7dfe980b…`, `sudoers-vector-{on,off}.txt`, `vector-{on,off}-confirmed.txt` (ground-truth flips), `clock-{prior,post}-state.txt` both restored. But the row's own object — the **read** path — is ungranted (**P2 executed: password required**), was never ratified, and the substitute (interactive paste at E-4) is **hands-required**, which collides head-on with D-149's no-hands auto-GO. This is the **T16 Ed-decision item**: the `-getusingnetworktime` sudoers one-liner is a **precondition of any D-149 auto-GO window**, not an optional convenience. |
| **ED-Q-L8-2** (full dress rehearsal E-4→E-9 + author→arm→verify→consume) | **OPEN** | **P4: no rehearsal custody root exists anywhere** under `~/JouleWise-window-custody/`. Builder + card exist on main (`ad14ac4`); the card's own status table marks every substantive step ED-FIRST (= nobody has run it). Mechanism is `_v2`/freeze-0002-bound and, after D-148.5's deferral of the registry install to `_v4`, will be **two generations stale**. E-9a→E-10 remains structurally unreachable without a lead-approved committed scratch-ledger route that does not exist. The verdict called this "the program's most valuable Ed hour"; it is unspent. |
| **ED-Q-L8-3** (live sampler-checklist + rail probe **on a quiet machine**) | **PARTIAL** | Live sudo demonstrably ran: 264,911-byte `.plist`, ABBA directory, cadence 1.0128 s, zero orphans, backlight literals. Fails the row's stated condition: **P6** places both halves inside the decisive-replay span, with a charge-termination step mid-sequence; the rail probe is self-declared documentation-grade; `rail-probe-load-note.txt` was lead-restored after the operator's paste overwrote it; no separate teardown-census artifact exists. Both halves re-run in ~12 minutes on a genuinely quiet machine. |
| **ED-Q-L8-4** (live `quiet_mac_prep.sh` three-OK-literals check) | **OPEN — and now blocker-adjacent** | **P5: zero execution artifacts** in custody at any date after 2026-07-17; the one post-council quiet-machine event bypassed the script (`shakedown-driver.sh:44` bare `pmset displaysleepnow`). **P10 discharges the cheap half at the desk:** the three literals match `_quiet_capture` verbatim. The row is nonetheless promoted, not closed, by **F16**: the same predicate refuses on any `FAIL:` substring, and the repo's own record calls this script's Graphics FAIL a known false signal. The live run is now the only way to know whether E-7a refuses deterministically. |

**ED roll-up for this seat: 0 CLOSED / 2 PARTIAL / 2 OPEN.** The consolidated
file's 3 CLOSED / 12 PARTIAL / 8 OPEN across 23 rows is consistent with mine
except that it scores ED-Q-L8-1 and ED-Q-L8-3 PARTIAL where `rows/` scored them
closed — and I concur with the consolidated file.

Two structural facts about these rows the sitting must see: (i) **none of the
four ED-Q-L8 IDs is tracked anywhere in the repository** outside the council
trace, so D-149 condition C1 ("ED-QUALIFICATION rows closed") has no mechanical
list to read and would evaluate against nothing; (ii) **D-149 C1 conditions its
auto-GO on the very rows this sitting adjudicates**, a circularity recorded
nowhere in D-149's own text.

---

## 6. POST-PACKET EVENTS IN SCOPE

- **Merge wave (`5bd7acf`).** The single genuine improvement: P-13 is cured and
  every branch-only dependency of this row is now on main. It changes no
  finding's disposition — every NOT-DISCHARGED item above was re-verified at the
  merged head.
- **D-148.5 FINAL (r3), custody `docs/process_traces/2026-08-20-go-session/`.**
  Three operator-facing consequences, none of which has a home:
  1. **B-1 recorded consequence** — PACK_AUTHENTICATION's fingerprint digests the
     full sorted `os.environ`, so re-use "will effectively always refuse across
     shell sessions and re-author", and "**operators must not misread routine
     environment-noise refusals as pack corruption**". **P9: that sentence exists
     in no operator surface.** A routinely-firing refusal whose correct reading
     and recovery live only in a council ruling is precisely this seat's subject
     matter, and it is a new open item.
  2. **B-3 mandatory halt trigger** — bounds T-0→arm ≤ 15 min and p99
     arm→consume ≤ 4 min, and under D-149 unattended auto-GO the trigger must be
     "**a MECHANICAL GATE IN THE WINDOW SCHEDULER … not prose (prose halt
     triggers are how stop signals get eaten)**". **P9: no such gate exists in
     `scripts/` or `joulewise/`.** The bound is currently prose, which the
     ruling itself declares insufficient.
  3. **Two-coordinate `_v3` archival replay + the `_v4` re-freeze.** The
     operator surface is already two coordinates wrong (`_v2`/`…-20260813`,
     P8); after the compelled `_v4` re-freeze it will be three generations
     stale, and the rehearsal mechanism (ED-Q-L8-2) must be regenerated again
     before the hour can even be scheduled.
- **`_v3` fuse lapse ~17:00Z.** Not a finding of this seat, but it converts the
  pre-fuse `_v3` rehearsal harvest into the only pre-commitment measurement
  opportunity for the r3 B-3 bounds (r3 `:70-71`) — i.e. the one chance to
  measure the horizons this row's F9/F12 are about is expiring.
- **T16 Ed-decision item (`RUN_STATE.md:59-63`).** Correctly surfaced there and
  correctly scoped: the `-getusingnetworktime` one-liner is "required before any
  D-149 auto-GO window". My P2 confirms it is still owed. I record it as a
  **hard precondition**, not a convenience item.

---

## 7. UNEXECUTED OBLIGATIONS (mine, listed)

1. End-to-end `capture_t0_step.py` run against a real pack (needs custody roots,
   a terminal-review attestation commit, and sudo — Ed-hands, and it *is*
   ED-Q-L8-2).
2. Live 600 s `prewindow_check.sh --wait` dwell.
3. Re-score of the 22-cell (A–V) error-injection matrix against the rewritten
   §5C / E-9b / E-9c / E-10 / FD-198 / capture-era / D-146 surface. **This is
   the seat's own instrument and it is stale**; I record it as a work order
   rather than pretending a seat pass substitutes for it.
4. Root verification of the installed `/etc/sudoers.d/joulewise-network-time`
   bytes' digest (Ed-hands).
5. Code audits of `launch_window.py`, `author_arm_evidence_t0.py`,
   `backup_runs.sh`, `build_rehearsal_env.sh`, `arm_readiness_evidence.py`.
6. Operator-visible behaviour of the D-146 capture-era refusals — no L8-scoped
   matrix cell exists for `capture_pipeline_superseded` / `_absent`.
7. Adversarial attack on **my own** 31-item denominator.

---

## 8. WORK ORDERS

| WO | Content | Blocks READY? |
|---|---|---|
| **WO-L8R-1** | Successor/recut arm packet (F5, F8, F9, F12, F14), sequenced behind an end-to-end T-0 pass at the exact reviewed head (Opus W8) and carrying the M-2 informational note the cold gate assigned to it | YES |
| **WO-L8R-2** | Reconcile §4/§6 with `_ENV_KEYS`: the `ARM_RECEIPT`/`LAUNCH_MANIFEST` contradiction, the chain `REPO=` literal, and the family/checkout re-pin to the armable family. **Defect-shaped regression required:** a lint that parses the runbook's own §4 block and §6 chain template against `_ENV_KEYS` and the REPO regex — the recurrence of this class is the argument for mechanically generating the templates from the pack, which WO-L8-6's alternative already permitted and nobody took | YES |
| **WO-L8R-3** | `prewindow_check.sh:150` pattern → `codex\|claude\|t3\|mcp-server`. **Unblock from A4**: this is a regex edit, not census semantics | YES |
| **WO-L8R-4** | Governed `reauthor-clean` with shape verification and a receipt (F10, the never-built WO-L8-8) | YES |
| **WO-L8R-5** | Operator-visible: the 300 s fuse + its licensed recovery; r3 B-1's environment-noise refusal reading; r3 B-3's halt-trigger bounds | YES |
| **WO-L8R-6** | Regenerate the rehearsal against the armable family and obtain the lead-approved committed scratch-ledger ruling, then **execute ED-Q-L8-2**, folding ED-Q-L8-4 in as E-7a and resolving F16 | YES |
| **WO-L8R-7** | Delta re-run of the 22-cell error-injection matrix against the current procedure and code | YES |
| **WO-L8R-8** | Seat-audit D-149's automation, including the **mechanical** halt-trigger scheduler gate r3 requires and the no-hands seam at E-4 (interactive prior-state read + trusted-clock literal) | YES |
| **ED (Ed-hands)** | (a) the `-getusingnetworktime` sudoers one-liner or a ratified alternative — precondition of any auto-GO window; (b) the rehearsal hour; (c) a genuinely quiet ~12-minute re-run of ED-Q-L8-3 | YES |

---

## 9. VERDICT

**STILL-OPEN — charter form: NOT-READY (+ the nine work orders above).**
Findings: 1 STRUCK, 3 DISCHARGED (two of them narrowly, one only as to code
contract), 11 NOT-DISCHARGED, 1 seat-new OPEN. ED rows: 0 closed / 2 partial /
2 open. Coverage 22/31, with the prior denominator adversarially broken.

**Single strongest reason.** The operator path to a legal launch has **never been
walked once, by anyone, end to end** — ED-Q-L8-2, the stable-capability row the
charter says cannot be deferred and the verdict called the program's most
valuable Ed hour, has no custody root anywhere on the machine — and the first
executed probe a seat ran against that path at the merged head found it broken:
a `window.env` authored from the runbook's own §4 plus §6 instructions **refuses
at the very first capture**. Every repair in this row is unit-tested and
unwalked; the one time somebody walked four lines of it, it refused. That is
not a row that can return READY, and no accumulation of merged code changes it
until a human completes the ceremony once.
