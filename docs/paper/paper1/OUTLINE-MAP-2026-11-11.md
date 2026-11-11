# Paper 1 outline map — 11 November 2026

Base manuscript: `62a87aaad3e3b2bf0d7f61e534a5b87b0c51a642` (`origin/main` at intake, seat 6 corrections merged).
Ruling snapshot: `2eb2df03699e815e4634ce41fd62ac7d77d0d226` on `origin/audit/2026-11-10-fable`.
Original `paper1.md` SHA-256: `219769092577192ac47007bc8cb91493e7bef0c976544e894763a71f3079551b`.

Authority: `RESEARCH-LEAD-DECISIONS.md` RL-8, RL-24 seat 10, RL-39 and RL-40, and
`paper-audit.md` §8.1 and title discussion, under
`docs/research-audits/2026-11-10-fable/` at the ruling snapshot. Read with `git show`; these are committed documents, not data inputs.

## Working title and subtitle

**Title:** What a Laptop's Power Counters Can Resolve

**Subtitle:** A Pre-registered, Blinded Measurement of LLM Inference Energy on Apple Silicon

The manuscript H1 joins these with a colon, following the working wording approved through E4 and RL-24.
RL-8 puts the instrument, its boundaries and its resolution first. The title names neither replication nor
BYTES results while their release gates remain open. It removes the old “Attribution Limits” wording and
the contingent attribution-limited subtitle. Final wording remains Ed’s; naming additional results waits
for the 5 December scope freeze. No tripwire finding or title is introduced; RL-9 permits the tripwire phrase
only as a question or hypothesis.

## Section moves

| Old location | New location | Treatment / authority |
|---|---|---|
| Title; subtitle slot | H1 above; slot cut | RL-8 / RL-24; C1 below |
| Abstract; §§1–2 | Abstract; §§1–2 | Body retained; paper section references maintained |
| §3 lead-in | §4 lead-in | Move |
| §3.1 | §3.1 | Instrument boundary first, RL-8 |
| §3.9 | §3.2 | DC-input boundary beside rails, RL-8 |
| §6.6 | §3.3 | Known-bytes test beside boundaries; template remains unfilled |
| §5.6 whole-machine cross-check paragraph | §3.4 | Existing rail-share placeholder beside boundaries; no new result |
| §3.2 | §4.1; Appendix D.1 | Overlap example and historical record-support paragraph moved to appendix |
| §3.3 | §4.2; Appendix D.2 | Calibration fit, coverage rationale, monotonicity argument and examples moved to appendix |
| §3.4 | §4.3; Appendix D.3 | Estimator steps and interval example moved to appendix |
| §3.5 | §4.4 | Attribution-floor definition and fixed sentence retained |
| §3.6 | §4.5; Appendix D.4 | Floor formulae, corner widening, guard and example moved to appendix |
| §3.7 | §4.6; Appendix D.5 | Definition and distinction retained; example, replay and branch rules moved; C2/C3 below |
| §3.8 | §4.7; Appendix D.6 | Drift-bound derivation and scaled sensitivity line moved to appendix |
| §3.10 | §4.8; Appendix D.7 | Contrast estimator, outcome precedence and claims ladder retained; descriptive checks moved |
| §4.1–§4.7 | §5.1–§5.7 | Registered design, blinding, release and recomputation; no rewrite |
| §5.1–§5.6 | §6.1–§6.6 | Instrument validation; cross-check paragraph moved as above |
| §5.8 | §6.7 | Recompute agreement before replication, RL-8 outline |
| §5.7 | §6.8 | Replication template moved; no tier or result selected |
| §6.1–§6.5 | §7.1–§7.5 | BYTES as second results section; §6.6 moved above |
| §7.1–§7.3 | §8.1–§8.3 | Automation text moved only; rewrite remains seat 9 |
| §8 | §9 | Existing limitations moved; no missing-item prose added |
| No old section | §10 | Empty outlook heading reserved for seat 13 under RL-24 / RL-9 |
| §9 | §11 | Conclusion moved; Ed retains authorship |
| Evidence / code availability; References | Same unnumbered sections | Unchanged |
| Appendix A | Appendix A | First-use section pointers updated |
| Appendices B–C | Appendices B–C | Unchanged |

Headings and explicit paper section references change only to support these moves, except the §8 body
references handed to seat 9 below under RL-43. Appendix pointers are
in subsection headings. Original branch identifiers (including `5.4.B`, `5.5.1`, `6.6.*` and `9.*`) stay
stable as template locators even when their containing section moves. FACT comments remain byte-identical;
their historical source locators are not renumbered.

## Review fixes F-1–F-3 (seat 10 rounds 2–3)

**F-1 / RL-43:** §8's title wording and body are restored byte-identical to `origin/main`'s §7;
only the four heading numbers change from 7.x to 8.x. The following 11 body references are
**handed to seat 9** for its rebase and renumbering pass. Ten need renumbering; the §1.2 pointer
already has its final number and stays unchanged. FACT source locators stay unchanged.

| Reference in restored §8 | Old number → new number | Disposition |
|---|---|---|
| Figure 5 caption: release verification | 4.6 → 5.6 | handed to seat 9 |
| Figure 5 caption: uncovered-quantity checks | 4.7 → 5.7 | handed to seat 9 |
| §8.2 item 1: change disclosure | 4.5 → 5.5 | handed to seat 9 |
| §8.2 item 2: primary-block blinding | 4.6 → 5.6 | handed to seat 9 |
| §8.2 item 2: BYTES commitment | 6.3 → 7.3 | handed to seat 9 |
| §8.2 item 5: uncovered-quantity checks | 4.7 → 5.7 | handed to seat 9 |
| §8.2 item 5: BYTES twin | 6.3 → 7.3 | handed to seat 9 |
| §8.2 item 7: claims ladder | 3.10 → 4.8 | handed to seat 9 |
| §8.2 item 7: correction provenance | 1.2 → 1.2 (unchanged) | handed to seat 9 |
| §8.3 clock-mapping bullet | 3.3 → 4.2 | handed to seat 9 |
| §8.3 process-overhead bullet | 7.2 → 8.2 | handed to seat 9 |

**F-2 / RL-47 (round 3):** Supersede round 2's first option with the ruled second option:
restore P088 whole in §4.8 and return P089's numbered estimator list directly after its lead-in,
with a blank line after the list. Both units are byte-identical to `origin/main`. D.7 retains only
the leave-one-quad-out and registered descriptive-estimates paragraphs (P092–P093); the later seat
owns leave-one-quad-out. The §4.8 heading parenthetical changes from “estimation details in Appendix D.7”
to “descriptive checks in Appendix D.7”; D.7's heading changes from “Contrast estimator and descriptive checks”
to “Contrast descriptive checks” to match its remaining content. P089 item 5's cross-reference `Section 3.6` is renumbered to `Section 4.5` by the section-move table
(lead orchestrator edit after round 3), like every other body cross-reference outside §8.

**F-3:** Tier E's keep list now includes §3.1–§3.2 and its replace list includes §3.4,
the moved `P1-B5-METER` paragraph. The variants README row matches both lists.

## Cuts

| ID | Old text / location | Disposition |
|---|---|---|
| C1 | Entire `CP-X02-headline` placeholder, old line 21 | cut (contingent attribution-limited subtitle forbidden by RL-8; removes one occurrence and one distinct id) |
| C2 | ` and the paper's contingent subtitle`, old §3.7 branch-rule paragraph | cut (removes obsolete subtitle permission under RL-8); rest moves to Appendix D.5 |
| C3 | ` or` followed by `license the contingent subtitle`, old §3.7 final paragraph | cut (same obsolete subtitle permission, RL-8); rest stays in §4.6 |

The H1 replacement is the approved working-title change. No other body text is cut. Method shortening is
relocation, including synthetic examples. RL-39 does not authorize a new fill here; RL-40’s correction
provenance, FACT locators and prior deletions remain intact. All result alternatives remain unselected.

## Size and fill-index accounting

Counting whitespace-separated words after removing HTML comments and FILL placeholders: old §3 = **4,142**;
old phase-method material after taking out boundary §§3.1 and 3.9 = **3,699**;
new §4 = **2,140**, **57.9%** of that phase-method material. Appendix D retains the displaced text.

`python3.13 -B docs/paper/paper1/build_fill_index.py` changes the count tuple
from **235 / 214 / 218 / 173** to **234 / 213 / 217 / 173**
(all occurrences / main-manuscript occurrences / distinct ids / new ids).
Only C1 changes counts. Row ordering and source line locators change with moves; two FILL descriptions
also receive updated paper section pointers. The generator and supplier/status logic are unchanged.

## Exhaustive manuscript paragraph map

The table covers all 303 old blank-line-delimited source units: prose paragraphs, lists, tables, headings,
figures and comment fragments. A multi-paragraph HTML comment is covered by its constituent units.
Line ranges refer to the base manuscript and this restructured `paper1.md`. For a split paragraph,
`[a:b]` is the zero-based, half-open character span within the original source unit, including its original
line breaks; every character span has one destination. Only separating whitespace changes at a split.

| Old unit / lines | Locator | New location or cut |
|---|---|---|
| P001, L1–3 | `&lt;!-- PAPER 1 — FULL DRAFT WITH PLACEHOLDERS (written 2026-10-27, b` | Front, L1–3 |
| P002, L5–17 | `How to read this file: - Every measured energy, floor, ratio, outc` | Front, L5–17 |
| P003, L19–19 | `# Dividing a Laptop's Inference Energy Between Phases with On-Chip` | Front, L19–19 |
| P004, L21–21 | `{{FILL: CP-X02-headline / contingent subtitle, printed only under ` | cut (C1; RL-8: no attribution-limited subtitle) |
| P005, L23–23 | `## Abstract` | Abstract, L21–21 |
| P006, L25–56 | `Language-model inference has two phases: *prefill*, in which the m` | Abstract, L23–54 |
| P007, L58–58 | `## 1. Introduction` | 1., L56–56 |
| P008, L60–60 | `### 1.1 The question` | 1.1, L58–58 |
| P009, L62–68 | `A large language model (LLM) generates text one *token* at a time;` | 1.1, L60–66 |
| P010, L70–76 | `Measuring phase energy on a laptop is attractive because the senso` | 1.1, L68–74 |
| P011, L78–78 | `### 1.2 Approach` | 1.2, L76–76 |
| P012, L80–80 | `We treat the instrument's limits as results. Every reported phase ` | 1.2, L78–78 |
| P013, L82–91 | `- an interval that combines run-to-run scatter with three recorded` | 1.2, L80–89 |
| P014, L93–98 | `The registrations fixed the counting and exclusion rules, estimato` | 1.2, L91–96 |
| P015, L100–100 | `### 1.3 Contributions` | 1.3, L98–98 |
| P016, L102–115 | `1. **A phase-attribution method with explicit limits** for interva` | 1.3, L100–113 |
| P017, L117–117 | `### 1.4 What this paper does not claim` | 1.4, L115–115 |
| P018, L119–123 | `All measurements come from one laptop, one operating-system build ` | 1.4, L117–121 |
| P019, L125–125 | `## 2. Background and related work` | 2., L123–123 |
| P020, L127–127 | `### 2.1 Software power counters: gain and time` | 2.1, L125–125 |
| P021, L129–135 | `Running Average Power Limit (RAPL) is an energy counter exposed by` | 2.1, L127–133 |
| P022, L137–142 | `The *time* axis is closer to our problem. Hähnel et al. show that ` | 2.1, L135–140 |
| P023, L144–144 | `### 2.2 Energy of LLM inference` | 2.2, L142–142 |
| P024, L146–156 | `TokenPowerBench reports prefill and decode energy and groups measu` | 2.2, L144–154 |
| P025, L158–158 | `### 2.3 Memory traffic and decode` | 2.3, L156–156 |
| P026, L160–165 | `Decode on a single request is commonly described as memory-bandwid` | 2.3, L158–163 |
| P027, L167–167 | `### 2.4 Benchmark discipline, metrology and pre-registration` | 2.4, L165–165 |
| P028, L169–174 | `JouleSort established that an energy benchmark needs a fixed workl` | 2.4, L167–172 |
| P029, L176–184 | `Georges, Buytaert and Eeckhout make repetition, warm-up, independe` | 2.4, L174–182 |
| P030, L186–186 | `### 2.5 Split inference` | 2.5, L184–184 |
| P031, L188–191 | `Split, or disaggregated, inference runs prefill and decode on diff` | 2.5, L186–189 |
| P032, L193–193 | `## 3. Method` | 4., L250–250 |
| P033, L195–196 | `This section defines every quantity the results print. Numbers in ` | 4., L252–253 |
| P034, L198–198 | `### 3.1 The machine, the sampler and the measurement boundary` | 3.1, L193–193 |
| P035, L200–203 | `All measurements use one Apple M3 Max laptop (model identifier Mac` | 3.1, L195–198 |
| P036, L205–209 | `The power sampler is macOS powermetrics, asked for one record ev` | 3.1, L200–204 |
| P037, L211–215 | `The **measurement boundary** of Part 1 is therefore the *processor` | 3.1, L206–210 |
| P038, L217–217 | `### 3.2 A run and its phases` | 4.1, L255–255 |
| P039, L219–225 | `A **run** is one inference request executed in its own process. It` | 4.1, L257–263 |
| P040, L227–228 | `The runtime stamps each phase edge. Prefill ends, and decode begin` | 4.1, L265–266 |
| P041, L230–236 | `**Phase energy by overlap.** Each power record contributes its ave` | `[0:354]` 4.1, L268–271; `[354:679]` D.1, L1503–1506 |
| P042, L238–238 | `Image: Figure 1. Phase split by overlap, and the energy moved when an e` | 4.1, L273–273 |
| P043, L240–243 | `*Figure 1. Schematic, no measured data. Five power records (grey);` | 4.1, L275–278 |
| P044, L245–248 | `This rule, which we call the **held-average reconstruction**, assu` | 4.1, L280–283 |
| P045, L250–257 | `**Minimum record support.** A phase needs at least three records w` | `[0:436]` 4.1, L285–288; `[436:893]` D.1, L1508–1511 |
| P046, L259–259 | `### 3.3 Where the edges are: calibration, clock mapping and the ti` | 4.2, L290–290 |
| P047, L261–263 | `Power records are stamped by the sampler; phase edges are stamped ` | 4.2, L292–294 |
| P048, L265–278 | `**The fiducial bound b (calibration with commanded pulses).** Befo` | `[0:336]` 4.2, L296–299; `[336:734]` D.2, L1515–1518; `[734:1042]` D.2, L1520–1523; `[1042:1498]` 4.2, L301–305 |
| P049, L280–280 | `b = max(opening, closing) + max(/closing − opening/, s_bracket),` | 4.2, L307–307 |
| P050, L282–284 | `where s_bracket is a fixed minimum allowance for movement between ` | `[0:111]` 4.2, L309–309; `[111:222]` D.2, L1525–1526 |
| P051, L286–291 | `**The clock bounds m and s.** Each run's sampler records carry who` | 4.2, L311–316 |
| P052, L293–302 | `**The edge bound g and the first-kind timing bound.** Each phase e` | `[0:343]` 4.2, L318–321; `[343:554]` D.2, L1528–1529; `[554:1030]` D.2, L1531–1535 |
| P053, L304–306 | `The pulse calibration measures how the sampler places the edges of` | 4.2, L323–325 |
| P054, L308–308 | `### 3.4 Reported phase energy and its interval` | 4.3, L327–327 |
| P055, L310–315 | `A **reported cell** is one energy per model and phase, from that m` | 4.3, L329–334 |
| P056, L317–317 | `For a cell with n_r kept repeats (energies r) and n_b kept quads (` | D.3, L1539–1539 |
| P057, L319–329 | `1. **Mean.** m = 0.2 × mean(r) + 0.8 × mean(q). The weights are fi` | D.3, L1541–1551 |
| P058, L331–336 | `The interval covers run-to-run and quad-to-quad variation inside o` | `[0:321]` 4.3, L336–338; `[321:574]` D.3, L1553–1555 |
| P059, L338–338 | `### 3.5 The attribution floor` | 4.4, L340–340 |
| P060, L340–348 | `The first-kind timing bound enters each interval only through its ` | 4.4, L342–350 |
| P061, L350–350 | `### 3.6 The detection floor` | 4.5, L352–352 |
| P062, L352–353 | `The **detection floor** of a model and phase is the largest differ` | 4.5, L354–355 |
| P063, L355–359 | `- **Absolute form**, from the kept repeats v₁ … v_n: deviations ar` | D.4, L1559–1563 |
| P064, L361–363 | `In both, the **point floor** is max(largest /deviation/, predictio` | D.4, L1565–1567 |
| P065, L365–371 | `**Corner widening.** Each value may lie anywhere within ± its timi` | D.4, L1569–1575 |
| P066, L373–375 | `**Small-sample guard.** For fewer than ten kept units the operativ` | D.4, L1577–1579 |
| P067, L377–380 | `*Synthetic example:* ten repeats with s = 0.2 J and largest deviat` | D.4, L1581–1584 |
| P068, L382–391 | `A **model contrast** (Section 3.10) is judged against a **floor ga` | 4.5, L357–366 |
| P069, L393–393 | `### 3.7 The dominance ratio` | 4.6, L368–368 |
| P070, L395–395 | `For each model, phase and floor form we print` | 4.6, L370–370 |
| P071, L397–397 | `R = (corner-widened floor, unguarded) ÷ (point floor, unguarded).` | 4.6, L372–372 |
| P072, L399–403 | `R ≥ 2 (equality passes) means that letting each value move within ` | `[0:316]` 4.6, L374–376; `[316:455]` D.5, L1588–1590 |
| P073, L405–409 | `For the comparative form we also print R_cm, a sensitivity replay ` | D.5, L1592–1596 |
| P074, L411–416 | `Two models, two phases and two forms give eight R values and four ` | D.5, L1598–1603; cut C2 (RL-8) |
| P075, L418–421 | `The attribution floor of Section 3.5, the detection-floor class a` | 4.6, L378–380; cut C3 (RL-8) |
| P076, L423–423 | `### 3.8 Drift: reference requests, the drift screen and the scaled` | 4.7, L382–382 |
| P077, L425–428 | `The instrument may read differently at the end of a session than a` | 4.7, L384–387 |
| P078, L430–432 | `**Drift bound.** From the clean corpus energies (the first twelve ` | D.6, L1607–1609 |
| P079, L434–434 | `bound(n_s, n_e) = max( max(U_{n_s} − L_{n_e}, U_{n_e} − L_{n_s}), ` | D.6, L1611–1611 |
| P080, L436–437 | `The first term is the widest gap two means of those sizes could sh` | D.6, L1613–1614 |
| P081, L439–441 | `**Drift screen.** The session passes when the absolute difference ` | 4.7, L389–391 |
| P082, L443–446 | `**Drift allowance.** A = max(bound, spread), where the spread is t` | 4.7, L393–396 |
| P083, L448–456 | `**The scaled sensitivity line.** The allowance is measured on refe` | D.6, L1616–1624 |
| P084, L458–458 | `### 3.9 The whole-machine boundary` | 3.2, L212–212 |
| P085, L460–465 | `An inline USB-C power meter (POWER-Z KM003C) sits in the cable bet` | 3.2, L214–219 |
| P086, L467–473 | `In Part 1 the meter is a **descriptive cross-check** that never en` | 3.2, L221–227 |
| P087, L475–475 | `### 3.10 Model contrasts, outcome words and the claims ladder` | 4.8, L398–398 |
| P088, L477–478 | `A **contrast** compares two models on the same workload in **contr` | 4.8, L400–401 |
| P089, L480–490 | `1. d̄ = mean(d_k); se = s_d / √n. 2. **Metrology interval**: d̄ ± ` | 4.8, L403–413 |
| P090, L492–492 | `The outcome is one of four registered words, decided in this order` | 4.8, L415–415 |
| P091, L494–498 | `- **not estimable**: a required input is missing or invalid; - **n` | 4.8, L417–421 |
| P092, L500–502 | `A **leave-one-quad-out** check recomputes the contrast without eac` | D.7, L1628–1630 |
| P093, L504–507 | `Beside each contrast two **registered descriptive estimates** are ` | D.7, L1632–1635 |
| P094, L509–517 | `**The claims ladder** caps how strong a sentence may be. **L1** (i` | 4.8, L423–431 |
| P095, L519–519 | `## 4. Experimental design` | 5., L433–433 |
| P096, L521–521 | `### 4.1 Models, workloads and stack` | 5.1, L435–435 |
| P097, L523–526 | `Part 1 uses two models from the same family, Qwen3-1.7B and Qwen3-` | 5.1, L437–440 |
| P098, L528–535 | `- **Decode workload.** One fixed prompt of 42 tokens, rendered thr` | 5.1, L442–449 |
| P099, L537–538 | `The four **target cells** are decode and 2,048-token prefill for e` | 5.1, L451–452 |
| P100, L540–540 | `### 4.2 Packs and the shape of a session` | 5.2, L454–454 |
| P101, L542–542 | `A **pack** is a frozen, hash-pinned plan for one measurement sessi` | 5.2, L456–456 |
| P102, L544–546 | `- the **1.7B floor pack** measures Qwen3-1.7B's reported cells and` | 5.2, L458–460 |
| P103, L548–555 | `A **session** is one unattended collection of a whole pack on the ` | 5.2, L462–469 |
| P104, L557–557 | `Image: Figure 2. Shape of one measurement session (schematic). — figures` | 5.2, L471–471 |
| P105, L559–562 | `*Figure 2. Schematic, no measured data. One session, left to right` | 5.2, L473–476 |
| P106, L564–564 | `### 4.3 The primary block` | 5.3, L478–478 |
| P107, L566–572 | `The primary block (registered internally as measurement block 5) c` | 5.3, L480–486 |
| P108, L574–584 | `**What refuses, and what is only recorded.** A session is *armed*,` | 5.3, L488–498 |
| P109, L586–589 | `**Attempts.** An *attempt* is one try at a session. An attempt tha` | 5.3, L500–503 |
| P110, L591–591 | `### 4.4 The replication block` | 5.4, L505–505 |
| P111, L593–595 | `A single session says how much a number moves from run to run on o` | 5.4, L507–509 |
| P112, L597–627 | `- **Same experiment.** The same three packs and session shape, wit` | 5.4, L511–541 |
| P113, L629–629 | `Figure 3 shows the order of sessions in the collection period.` | 5.4, L543–543 |
| P114, L631–633 | `Collection closed on 21 October 2026 with three counting sessions ` | 5.4, L545–547 |
| P115, L635–635 | `Image: Figure 3. Order of measurement sessions (schematic ledger). — fig` | 5.4, L549–549 |
| P116, L637–640 | `*Figure 3. Schematic of the registered ordering, with no outcomes.` | 5.4, L551–554 |
| P117, L642–642 | `### 4.5 Pre-registration and changes after registration` | 5.5, L556–556 |
| P118, L644–650 | `Each registration fixes, before its first session, which data coun` | 5.5, L558–564 |
| P119, L652–657 | `Errors found after registration were handled in three ways, each r` | 5.5, L566–571 |
| P120, L659–670 | `- two seals and three prospective errata, with attempt-specific ap` | 5.5, L573–584 |
| P121, L672–677 | `The D5b correction followed a permitted structural read of floor-r` | 5.5, L586–591 |
| P122, L679–679 | `### 4.6 Blinding and release` | 5.6, L593–593 |
| P123, L681–686 | `From each block's first session until its release, no person or AI` | 5.6, L595–600 |
| P124, L688–691 | `Before the primary release, GAMMA floor-resolution status and reas` | 5.6, L602–605 |
| P125, L693–701 | `Before the primary release, the analysis programs ran end to end o` | 5.6, L607–615 |
| P126, L703–703 | `{{FILL: P1-RELEASE / dates of the primary-block release event, the` | 5.6, L617–617 |
| P127, L705–705 | `### 4.7 Independent recomputation` | 5.7, L619–619 |
| P128, L707–710 | `The primary block's **independent recomputation** checks core arit` | 5.7, L621–624 |
| P129, L712–717 | `Seven disclosure families are not fully recomputed: monitor cost a` | 5.7, L626–631 |
| P130, L719–728 | `For Block 5 the bars were **fixed blind before release**, by the l` | 5.7, L633–642 |
| P131, L730–730 | `{{FILL: P1-RECOMPUTE / per block and compared family: applicable b` | 5.7, L644–644 |
| P132, L732–732 | `## 5. Results, Part 1: phase energy, floors and contrasts` | 6., L646–646 |
| P133, L734–735 | `&lt;!-- TEMPLATE. Every value below is a placeholder. Fill only from ` | 6., L648–649 |
| P134, L737–740 | `Every phase energy in this section rests on sampler timing; phase ` | 6., L651–654 |
| P135, L742–742 | `### 5.1 What was collected` | 6.1, L656–656 |
| P136, L744–744 | `{{FILL: P1-B5-ATTEMPTS / attempt history of each primary-block pac` | 6.1, L658–658 |
| P137, L746–748 | `The analysed sessions were {{FILL: P1-B5-ANALYSED / identifiers an` | 6.1, L660–662 |
| P138, L750–757 | `/ Cell / Kept repeats n_r / Kept quads n_b / Removed units (family` | 6.1, L664–671 |
| P139, L759–759 | `*Table 1. Kept and removed units per target cell in the primary bl` | 6.1, L673–673 |
| P140, L761–763 | `**[BRANCH 5.1.a — a pack ended without a claim-usable session]** T` | 6.1, L675–677 |
| P141, L765–765 | `{{FILL: P1-B5-HAZARDS / per session: hazard measurements at arm (n` | 6.1, L679–679 |
| P142, L767–767 | `### 5.2 Reported phase energies` | 6.2, L681–681 |
| P143, L769–774 | `/ Model / Phase / Mean energy (J) / Interval (J) / Per token (J/to` | 6.2, L683–688 |
| P144, L776–781 | `*Table 2. Reported gross phase energy per request on the processor` | 6.2, L690–695 |
| P145, L783–787 | `Each row of Table 2 carries the fixed attribution-floor sentence o` | 6.2, L697–701 |
| P146, L789–789 | `Labelled lines printed beside each cell, none of which replaces it` | 6.2, L703–703 |
| P147, L791–792 | `- *Without battery-assisted units:* {{FILL: P1-B5-BATT-LINE / per ` | 6.2, L705–706 |
| P148, L794–794 | `**[BRANCH 5.2.a — a target cell could not be computed]** The {{FIL` | 6.2, L708–708 |
| P149, L796–796 | `### 5.3 Detection floors` | 6.3, L710–710 |
| P150, L798–803 | `/ Model / Phase / Absolute floor (J) / Comparative floor (J) / Ope` | 6.3, L712–717 |
| P151, L805–810 | `*Table 3. Detection floors, primary block (Section 3.6). Each abso` | 6.3, L719–724 |
| P152, L812–812 | `### 5.4 Is the floor limited by timing attribution?` | 6.4, L726–726 |
| P153, L814–819 | `/ Model / Phase / R, absolute (corner ÷ point, J) / R, comparative` | 6.4, L728–733 |
| P154, L821–824 | `*Table 4. Dominance ratios, primary block, each over the kept unit` | 6.4, L735–738 |
| P155, L826–832 | `**[BRANCH 5.4.A — every one of the eight R and four R_cm is at lea` | 6.4, L740–746 |
| P156, L834–838 | `**[BRANCH 5.4.B — at least one of the twelve ratios is below 2]** ` | 6.4, L748–752 |
| P157, L840–840 | `**[BRANCH 5.4.R — a ratio refused (zero denominator or missing inp` | 6.4, L754–754 |
| P158, L842–842 | `### 5.5 The two model contrasts` | 6.5, L756–756 |
| P159, L844–847 | `/ Contrast (8B − 1.7B) / n quads / d̄ (J) / Metrology interval (J)` | 6.5, L758–761 |
| P160, L849–854 | `*Table 5. Primary contrasts, Qwen3-8B minus Qwen3-1.7B gross phase` | 6.5, L763–768 |
| P161, L856–857 | `Each contrast is reported in exactly one of the following branches` | 6.5, L770–771 |
| P162, L859–865 | `**[BRANCH 5.5.1 — outcome "direction supported", direction positiv` | 6.5, L773–779 |
| P163, L867–871 | `**[BRANCH 5.5.2 — outcome "direction supported", but the claim gat` | 6.5, L781–785 |
| P164, L873–875 | `**[BRANCH 5.5.3 — outcome "unresolved"]** The estimate d̄ = {{FILL` | 6.5, L787–789 |
| P165, L877–880 | `**[BRANCH 5.5.4 — outcome "not resolvable"]** The instrument canno` | 6.5, L791–794 |
| P166, L882–888 | `**[BRANCH 5.5.5 — outcome "not estimable"]** The contrast could no` | 6.5, L796–802 |
| P167, L890–890 | `The floor-related reasons must be kept distinct when selecting the` | 6.5, L804–804 |
| P168, L892–897 | `/ Issued reason code / Branch / Interpretation / /---/---/---/ / ` | 6.5, L806–811 |
| P169, L899–900 | `Other issued codes retain their registered glosses and outcome bra` | 6.5, L813–814 |
| P170, L902–902 | `**Leave-one-quad-out.** {{FILL: P1-B5-CTR-LOO / per contrast: "no ` | 6.5, L816–816 |
| P171, L904–904 | `**Decision interval against the floor.** {{FILL: P1-B5-CTR-DIFLOOR` | 6.5, L818–818 |
| P172, L906–913 | `**Registered descriptive estimates** (decide nothing). The 8B-to-1` | 6.5, L820–827 |
| P173, L915–915 | `### 5.6 Consistency checks beside the claims` | 6.6, L829–829 |
| P174, L917–919 | `**Across sessions within the primary block.** For each model and p` | 6.6, L831–833 |
| P175, L921–921 | `**Reference drift.** {{FILL: P1-B5-NEG8 / per session: drift-scree` | 6.6, L835–835 |
| P176, L923–925 | `**Whole-machine cross-check.** {{FILL: P1-B5-METER / per pack and ` | 3.4, L246–248 |
| P177, L927–929 | `**Monitor cost.** The hazard monitor ran on efficiency cores at ba` | 6.6, L837–839 |
| P178, L931–931 | `### 5.7 Replication` | 6.8, L845–845 |
| P179, L933–934 | `Table 6 places the primary block's value of every Part 1 quantity ` | 6.8, L847–848 |
| P180, L936–936 | `{{FILL: P1-B6-SIDEBYSIDE / Table 6: for each pack and each quantit` | 6.8, L850–850 |
| P181, L938–941 | `The rules for which runs and sessions enter differ between the blo` | 6.8, L852–855 |
| P182, L943–943 | `**Sessions collected.** {{FILL: P1-B6-COUNT / per pack: counting s` | 6.8, L857–857 |
| P183, L945–945 | `**The replication word.** For each contrast:` | 6.8, L859–859 |
| P184, L947–952 | `**[BRANCH 5.7.1 — "replicated"]** The {{FILL: P1-B6-REP-PHASE / "d` | 6.8, L861–866 |
| P185, L954–956 | `**[BRANCH 5.7.2 — "not replicated"]** The {{FILL: P1-B6-REP-PHASE ` | 6.8, L868–870 |
| P186, L958–959 | `**[BRANCH 5.7.3 — the primary contrast was not estimable]** The pr` | 6.8, L872–873 |
| P187, L961–963 | `**[BRANCH 5.7.4 — the contrast pack closed short]** The sentence r` | 6.8, L875–877 |
| P188, L965–967 | `The replication words were {{FILL: P1-B6-REPWORD-decode / replicat` | 6.8, L879–881 |
| P189, L969–969 | `**Dominance across sessions.** {{FILL: P1-B6-DOM / per floor sessi` | 6.8, L883–883 |
| P190, L971–971 | `**Labelled lines in the replication block** (none changes a regist` | 6.8, L885–885 |
| P191, L973–978 | `- *Scaled drift allowance* (Section 3.8): {{FILL: P1-B6-SCALED / p` | 6.8, L887–892 |
| P192, L980–980 | `### 5.8 Agreement of the independent recomputation` | 6.7, L841–841 |
| P193, L982–982 | `{{FILL: P1-RECOMPUTE-SUMMARY / one paragraph per block: compared f` | 6.7, L843–843 |
| P194, L984–984 | `## 6. Part 2, BYTES: what drives decode energy per token?` | 7., L894–894 |
| P195, L986–986 | `### 6.1 The question` | 7.1, L896–896 |
| P196, L988–993 | `During decode, each forward pass reads the weights it uses and the` | 7.1, L898–903 |
| P197, L995–999 | `The hypotheses barely differ on dense models, which read nearly ev` | 7.1, L905–909 |
| P198, L1001–1003 | `"Bytes read" here is a count from the model format, never a readin` | 7.1, L911–913 |
| P199, L1005–1005 | `### 6.2 Design` | 7.2, L915–915 |
| P200, L1007–1012 | `**Boundaries.** Each energy is measured at three boundaries: the *` | 7.2, L917–922 |
| P201, L1014–1019 | `**Models.** Ten 4-bit or 8-bit MLX checkpoints, pinned by revision` | 7.2, L924–929 |
| P202, L1021–1032 | `/ Role / Model / Experts used per token (k of E) / b (GB) / R (GB)` | 7.2, L931–942 |
| P203, L1034–1039 | `*Table 7. BYTES roster. b = W + KV, the format-derived bytes per d` | 7.2, L944–949 |
| P204, L1041–1045 | `**Workload.** Every run is the same request: a prompt of exactly 2` | 7.2, L951–955 |
| P205, L1047–1053 | `**Collection.** Each model is measured in a **floor module** of th` | 7.2, L957–963 |
| P206, L1055–1060 | `**What counts.** BYTES uses the replication block's flag catalog w` | 7.2, L965–970 |
| P207, L1062–1062 | `Image: Figure 4. BYTES design: fit set, frozen rival lines, held-out pr` | 7.2, L972–972 |
| P208, L1064–1067 | `*Figure 4. Schematic, no measured data. Left: three fit-set models` | 7.2, L974–977 |
| P209, L1069–1069 | `### 6.3 Analysis` | 7.3, L979–979 |
| P210, L1071–1074 | `**Cell estimate.** For one model, pass and boundary, over the kept` | 7.3, L981–984 |
| P211, L1076–1080 | `/ Term / Rails / DC input / Rest / /---/---/---/---/ / Phase-edge ` | 7.3, L986–990 |
| P212, L1082–1096 | `- **u, the meter edge term:** u = (P_start + P_end) × (r_max + Δt)` | 7.3, L992–1006 |
| P213, L1098–1099 | `The largest u + v over a cell's kept runs is printed as its **mete` | 7.3, L1008–1009 |
| P214, L1101–1106 | `**Per model.** With two computed passes, the model's energy E is t` | 7.3, L1011–1016 |
| P215, L1108–1124 | `**H1: frozen rival lines.** For each hypothesis x ∈ {b, R, τ}, an ` | 7.3, L1018–1034 |
| P216, L1126–1136 | `**H2: power against bandwidth.** Over models, on each boundary and` | 7.3, L1036–1046 |
| P217, L1138–1143 | `**Meter label-offset alternative.** The meter's clock mapping labe` | 7.3, L1048–1053 |
| P218, L1145–1147 | `**Multiplicity.** The family is the H1 consistency checks plus the` | 7.3, L1055–1057 |
| P219, L1149–1155 | `**Blinding in two stages.** At harvest every science energy and po` | 7.3, L1059–1065 |
| P220, L1157–1166 | `1. **Blinded:** rails only, fit set and references, used to check ` | 7.3, L1067–1076 |
| P221, L1168–1171 | `The required ordering is a recorded prediction commitment before h` | 7.3, L1078–1081 |
| P222, L1173–1176 | `**Two implementations.** The analysis and an independent twin, wri` | 7.3, L1083–1086 |
| P223, L1178–1178 | `### 6.4 Extension models` | 7.4, L1088–1088 |
| P224, L1180–1183 | `Both extension models, Qwen3.8-27B (8-bit) and NVIDIA Nemotron 3.5` | 7.4, L1090–1093 |
| P225, L1185–1185 | `### 6.5 Results` | 7.5, L1095–1095 |
| P226, L1187–1188 | `&lt;!-- TEMPLATE. Fill only from the stage-2 records of the registere` | 7.5, L1097–1098 |
| P227, L1190–1190 | `**Collection.** {{FILL: P1-BY-SESSIONS / per sub-pack and pass: co` | 7.5, L1100–1100 |
| P228, L1192–1192 | `**Per-model quantities.** {{FILL: P1-BY-TABLE / Table 8, per model` | 7.5, L1102–1102 |
| P229, L1194–1194 | `**The committed lines.** {{FILL: P1-BY-LINES / the predictions fil` | 7.5, L1104–1104 |
| P230, L1196–1197 | `**H1 words.** Table 9 gives, for each held-out model and boundary,` | 7.5, L1106–1107 |
| P231, L1199–1199 | `{{FILL: P1-BY-H1-TABLE / Table 9: per held-out model and boundary:` | 7.5, L1109–1109 |
| P232, L1201–1203 | `The words at the processor rails were {{FILL: P1-BY-H1-WORDS-rails` | 7.5, L1111–1113 |
| P233, L1205–1208 | `**[BRANCH 6.5.W1 — word bytes]** Only the line in bytes read per` | 7.5, L1115–1118 |
| P234, L1210–1213 | `**[BRANCH 6.5.W2 — word resident]** Only the line in resident si` | 7.5, L1120–1123 |
| P235, L1215–1217 | `**[BRANCH 6.5.W3 — word time]** Only the line in decode time pre` | 7.5, L1125–1127 |
| P236, L1219–1222 | `**[BRANCH 6.5.W4 — word unresolved]** Two or more lines predict ` | 7.5, L1129–1132 |
| P237, L1224–1228 | `**[BRANCH 6.5.W5 — word neither]** No registered line predicts t` | 7.5, L1134–1138 |
| P238, L1230–1230 | `**[BRANCH 6.5.W6 — no word: the model has no point]** The model ha` | 7.5, L1140–1140 |
| P239, L1232–1233 | `**Active or resident.** {{FILL: P1-BY-AR-rails / the active-or-res` | 7.5, L1142–1143 |
| P240, L1235–1237 | `**[BRANCH 6.5.A1 — active]** On all three MoE models, the reside` | 7.5, L1145–1147 |
| P241, L1239–1241 | `**[BRANCH 6.5.A2 — resident]** On all three MoE models, the byte` | 7.5, L1149–1151 |
| P242, L1243–1244 | `**[BRANCH 6.5.A3 — mixed]** The three MoE models do not agree on` | 7.5, L1153–1154 |
| P243, L1246–1246 | `**H2.** {{FILL: P1-BY-H2-TABLE / Table 10, per boundary and basis:` | 7.5, L1156–1156 |
| P244, L1248–1249 | `The primary energy per byte of bandwidth was ε = {{FILL: P1-BY-H2-` | 7.5, L1158–1159 |
| P245, L1251–1253 | `**[BRANCH 6.5.H1 — "resident adds nothing" on a boundary]** On the` | 7.5, L1161–1163 |
| P246, L1255–1256 | `**[BRANCH 6.5.H2 — ρ positive and its interval excludes zero]** On` | 7.5, L1165–1166 |
| P247, L1258–1261 | `**[BRANCH 6.5.H3 — the two intervals disagree at DC input or rest]` | 7.5, L1168–1171 |
| P248, L1263–1265 | `**[BRANCH 6.5.H4 — a fit refused]** The {{FILL: P1-BY-H2-REFUSED /` | 7.5, L1173–1175 |
| P249, L1267–1268 | `**One pass.** **[BRANCH 6.5.P1 — the one-pass fallback applied to ` | 7.5, L1177–1178 |
| P250, L1270–1270 | `**Commitment record.** {{FILL: P1-BY-COMMIT / the stage-2 record's` | 7.5, L1180–1180 |
| P251, L1272–1272 | `**Agreement of the two implementations.** {{FILL: P1-BY-TWIN / per` | 7.5, L1182–1182 |
| P252, L1274–1274 | `### 6.6 The known-bytes stream test` | 3.3, L229–229 |
| P253, L1276–1278 | `Whether the GPU rail includes the energy of the memory controller ` | 3.3, L231–233 |
| P254, L1280–1281 | `**[BRANCH 6.6.1 — the test ran and the rail responded as registere` | 3.3, L235–236 |
| P255, L1283–1284 | `**[BRANCH 6.6.2 — the test ran and a boundary did not respond as r` | 3.3, L238–239 |
| P256, L1286–1287 | `**[BRANCH 6.6.3 — the test did not run]** The test did not run in ` | 3.3, L241–242 |
| P257, L1289–1289 | `## 7. Research automation: an agent-driven pipeline and its contro` | 8., L1184–1184 |
| P258, L1291–1291 | `### 7.1 How the work was done` | 8.1, L1186–1186 |
| P259, L1293–1301 | `This study was designed, implemented, collected, reviewed and writ` | 8.1, L1188–1196 |
| P260, L1303–1311 | `The work used a measurement laptop, an analysis laptop and cloud m` | 8.1, L1198–1206 |
| P261, L1313–1313 | `Image: Figure 5. The research pipeline (schematic). — figures/fig_p1_pip` | 8.1, L1208–1208 |
| P262, L1315–1319 | `*Figure 5. Schematic of the permitted activities. Agents develop a` | 8.1, L1210–1214 |
| P263, L1321–1321 | `### 7.2 Integrity controls` | 8.2, L1216–1216 |
| P264, L1323–1325 | `An agent can change a result in ways a human might not notice: by ` | 8.2, L1218–1220 |
| P265, L1327–1353 | `1. **Registration before data, by hash.** Every registration, anal` | 8.2, L1222–1248 |
| P266, L1355–1355 | `### 7.3 Failures and lessons` | 8.3, L1250–1250 |
| P267, L1357–1358 | `The controls did not prevent every failure. We report those that c` | 8.3, L1252–1253 |
| P268, L1360–1391 | `- **Agents perturbed the instrument they were studying.** An AI ag` | 8.3, L1255–1286 |
| P269, L1393–1393 | `{{FILL: P1-AUTO-BLINDCHECK / result of the check whether any held-` | 8.3, L1288–1288 |
| P270, L1395–1397 | `The lesson we draw is that agents can run a measurement study with` | 8.3, L1290–1292 |
| P271, L1399–1399 | `## 8. Limitations` | 9., L1294–1294 |
| P272, L1401–1404 | `**Phase attribution was not checked by an independent instrument.*` | 9., L1296–1299 |
| P273, L1406–1409 | `**Pulse-to-inference transfer is untested.** The timing bound come` | 9., L1301–1304 |
| P274, L1411–1413 | `**Calibration coverage is a design rationale.** The 59-pulse maxim` | 9., L1306–1308 |
| P275, L1415–1418 | `**One machine, one stack, one boundary.** All results come from on` | 9., L1310–1313 |
| P276, L1420–1422 | `**Counter gain.** The rail energies are on the sampler's own scale` | 9., L1315–1317 |
| P277, L1424–1425 | `**Workload.** One fixed decode prompt, one prefill length of 2,048` | 9., L1319–1320 |
| P278, L1427–1430 | `**Statistical model.** Repeats and quads are modelled as independe` | 9., L1322–1325 |
| P279, L1432–1435 | `**Floor transfer.** Contrasts are judged against floors measured i` | 9., L1327–1330 |
| P280, L1437–1439 | `**Drift transfer.** The drift allowance is measured on reference r` | 9., L1332–1334 |
| P281, L1441–1442 | `**Gross energy.** Phase energies include the machine's baseline po` | 9., L1336–1337 |
| P282, L1444–1446 | `**Excluded units.** The intervals do not cover bias from which uni` | 9., L1339–1341 |
| P283, L1448–1453 | `**BYTES.** Bytes per token are format-derived counts, not measured` | 9., L1343–1348 |
| P284, L1455–1459 | `**Automation.** The agents that ran the study also wrote much of t` | 9., L1350–1354 |
| P285, L1461–1461 | `## 9. Conclusion` | 11., L1358–1358 |
| P286, L1463–1468 | `A laptop's own power sampler can divide inference energy between p` | 11., L1360–1365 |
| P287, L1470–1470 | `**[BRANCH 9.D — dominance branch]** {{FILL: CP-X02-conclusion / un` | 11., L1367–1367 |
| P288, L1472–1473 | `**[BRANCH 9.C — contrasts]** {{FILL: CP-X08-decode-a-conclusion / ` | 11., L1369–1370 |
| P289, L1475–1475 | `**[BRANCH 9.B — BYTES]** {{FILL: P1-BY-CONCLUSION / one sentence: ` | 11., L1372–1372 |
| P290, L1477–1480 | `The methods (timing bounds carried into every phase energy, floors` | 11., L1374–1377 |
| P291, L1482–1482 | `## Evidence and code availability` | Evidence, L1379–1379 |
| P292, L1484–1485 | `{{FILL: P1-AVAIL / public release: repository revision, archive lo` | Evidence, L1381–1382 |
| P293, L1487–1487 | `## References` | References, L1384–1384 |
| P294, L1489–1515 | `1. A. Tschand et al. "MLPerf Power: Benchmarking the Energy Effici` | References, L1386–1412 |
| P295, L1517–1517 | `## Appendix A. Terms` | Appendix A. Terms, L1414–1414 |
| P296, L1519–1549 | `/ Term / Meaning (section of first use) / /---/---/ / Prefill, dec` | Appendix A. Terms, L1416–1446 |
| P297, L1551–1551 | `## Appendix B. Historical timing diagnostics` | Appendix B. Historical timing diagnostics, L1448–1448 |
| P298, L1553–1559 | `The method was developed on captures from the same laptop collecte` | Appendix B. Historical timing diagnostics, L1450–1456 |
| P299, L1561–1561 | `Image: Figure B1. Historical capture re-derived with the current clock ` | Appendix B. Historical timing diagnostics, L1458–1458 |
| P300, L1563–1565 | `*Figure B1. Fitted edge excursions of one historical GPU pulse cap` | Appendix B. Historical timing diagnostics, L1460–1462 |
| P301, L1567–1567 | `## Appendix C. Fixed disclosure sentences` | Appendix C. Fixed disclosure sentences, L1464–1464 |
| P302, L1569–1571 | `These sentences are registered and printed verbatim where they app` | Appendix C. Fixed disclosure sentences, L1466–1468 |
| P303, L1573–1600 | `- *Conditionality:* "These numbers are conditional on a window tha` | Appendix C. Fixed disclosure sentences, L1470–1497 |

## Contingency-template paragraph map

Only section targets and headings are updated. Trigger dates and historical text are retained for the owning
seats; no variant is applied. The Tier E pointer to §4 of `draft-v2-skeleton.md` remains §4 because it names
another manuscript. FACT comments, FILL ids and branch labels are unchanged.

| File / old unit / lines | Locator | New location |
|---|---|---|
| `README.md` P001, L1–1 | `# Paper 1 contingency variants (Tiers B to E)` | Same file, L1–1; unchanged |
| `README.md` P002, L3–6 | `Short alternative versions of the sections each tier cha` | Same file, L3–6; unchanged |
| `README.md` P003, L8–13 | `/ File / Tier / Use when / Replaces / /---/---/---/---/ ` | Same file, L8–13; structural reference / heading only |
| `README.md` P004, L15–15 | `Tiers combine: C can apply with A or B for Part 2, and D` | Same file, L15–15; unchanged |
| `tierB_bytes_one_pass.md` P001, L1–1 | `# Tier B: BYTES at its registered one-pass minimum` | Same file, L1–1; unchanged |
| `tierB_bytes_one_pass.md` P002, L3–6 | `&lt;!-- Historical contingency template, not the current co` | Same file, L3–6; unchanged |
| `tierB_bytes_one_pass.md` P003, L8–8 | `## Abstract, Part 2 sentence (replaces the full draft's)` | Same file, L8–8; unchanged |
| `tierB_bytes_one_pass.md` P004, L10–13 | `In a second part, BYTES, we test whether decode energy p` | Same file, L10–13; unchanged |
| `tierB_bytes_one_pass.md` P005, L15–15 | `## §6.2, "Collection" (replaces the passes sentence)` | Same file, L15–15; structural reference / heading only |
| `tierB_bytes_one_pass.md` P006, L17–19 | `The registration targets two passes and sets a minimum o` | Same file, L17–19; structural reference / heading only |
| `tierB_bytes_one_pass.md` P007, L21–21 | `## §6.3, "Per model" (replaces the paragraph)` | Same file, L21–21; structural reference / heading only |
| `tierB_bytes_one_pass.md` P008, L23–26 | `For a model with one usable pass, its point is that pass` | Same file, L23–26; unchanged |
| `tierB_bytes_one_pass.md` P009, L28–28 | `## §6.4 (replaces the section)` | Same file, L28–28; structural reference / heading only |
| `tierB_bytes_one_pass.md` P010, L30–32 | `Both extension models were dropped: Nemotron had no load` | Same file, L30–32; unchanged |
| `tierB_bytes_one_pass.md` P011, L34–34 | `## §6.5, opening (adds before "Collection")` | Same file, L34–34; structural reference / heading only |
| `tierB_bytes_one_pass.md` P012, L36–37 | `Models with one usable pass are labelled *one pass*. The` | Same file, L36–37; unchanged |
| `tierB_bytes_one_pass.md` P013, L39–39 | `## Limitations (adds one sentence to §8, BYTES paragraph` | Same file, L39–39; structural reference / heading only |
| `tierB_bytes_one_pass.md` P014, L41–41 | `For a model with only one usable pass, BYTES does not te` | Same file, L41–41; unchanged |
| `tierC_block6_addendum.md` P001, L1–1 | `# Tier C: the replication reported as collected, its rel` | Same file, L1–1; unchanged |
| `tierC_block6_addendum.md` P002, L3–4 | `&lt;!-- Use when the replication release slips past about 2` | Same file, L3–4; unchanged |
| `tierC_block6_addendum.md` P003, L6–6 | `## Abstract (replaces the replication clause)` | Same file, L6–6; unchanged |
| `tierC_block6_addendum.md` P004, L8–12 | `... and an independent recomputation of the core arithme` | Same file, L8–12; unchanged |
| `tierC_block6_addendum.md` P005, L14–14 | `## §1.3, contribution 2 (replaces)` | Same file, L14–14; unchanged |
| `tierC_block6_addendum.md` P006, L16–19 | `2. **A pre-registered, blinded measurement, with a regis` | Same file, L16–19; unchanged |
| `tierC_block6_addendum.md` P007, L21–21 | `## §4.4, closing paragraph (adds)` | Same file, L21–21; structural reference / heading only |
| `tierC_block6_addendum.md` P008, L23–27 | `At submission the replication block had closed with {{FI` | Same file, L23–27; unchanged |
| `tierC_block6_addendum.md` P009, L29–29 | `## §5.7 (replaces the section)` | Same file, L29–29; structural reference / heading only |
| `tierC_block6_addendum.md` P010, L31–31 | `### 5.7 Replication: collected, released later` | Same file, L31–31; structural reference / heading only |
| `tierC_block6_addendum.md` P011, L33–33 | `The replication block ran to its registered close. Its r` | Same file, L33–33; unchanged |
| `tierC_block6_addendum.md` P012, L35–41 | `No replication energy, floor, ratio, contrast estimate o` | Same file, L35–41; structural reference / heading only |
| `tierC_block6_addendum.md` P013, L43–43 | `## §8, Limitations (adds)` | Same file, L43–43; structural reference / heading only |
| `tierC_block6_addendum.md` P014, L45–46 | `At submission the primary results rest on one session pe` | Same file, L45–46; unchanged |
| `tierC_block6_addendum.md` P015, L48–48 | `## §9, Conclusion (replaces the replication clause of th` | Same file, L48–48; structural reference / heading only |
| `tierC_block6_addendum.md` P016, L50–51 | `... The replication, collected and registered before the` | Same file, L50–51; unchanged |
| `tierD_bytes_registered_design.md` P001, L1–1 | `# Tier D: BYTES as a registered design with its instrume` | Same file, L1–1; unchanged |
| `tierD_bytes_registered_design.md` P002, L3–6 | `&lt;!-- Use when the primary-block release lands but the BY` | Same file, L3–6; structural reference / heading only |
| `tierD_bytes_registered_design.md` P003, L8–8 | `## Abstract, Part 2 sentence (replaces)` | Same file, L8–8; unchanged |
| `tierD_bytes_registered_design.md` P004, L10–13 | `In a second part, BYTES, we register a test of whether d` | Same file, L10–13; unchanged |
| `tierD_bytes_registered_design.md` P005, L15–15 | `## §6.5 (replaces the section)` | Same file, L15–15; structural reference / heading only |
| `tierD_bytes_registered_design.md` P006, L17–17 | `### 6.5 Status of the test` | Same file, L17–17; structural reference / heading only |
| `tierD_bytes_registered_design.md` P007, L19–26 | `**[BRANCH D.1 — the fit set was collected; the analysis ` | Same file, L19–26; unchanged |
| `tierD_bytes_registered_design.md` P008, L28–33 | `**[BRANCH D.2 — the fit set itself could not be collecte` | Same file, L28–33; unchanged |
| `tierD_bytes_registered_design.md` P009, L35–38 | `**Instrument-check evidence (not used for claims).** Bef` | Same file, L35–38; unchanged |
| `tierD_bytes_registered_design.md` P010, L40–42 | `**Synthetic validation.** The analysis and its independe` | Same file, L40–42; unchanged |
| `tierD_bytes_registered_design.md` P011, L44–44 | `**When results follow.** {{FILL: P1-BYD-WHEN / the plann` | Same file, L44–44; unchanged |
| `tierD_bytes_registered_design.md` P012, L46–46 | `## §6.6 (replaces)` | Same file, L46–46; structural reference / heading only |
| `tierD_bytes_registered_design.md` P013, L48–49 | `The known-bytes stream test, which decides how the rails` | Same file, L48–49; unchanged |
| `tierD_bytes_registered_design.md` P014, L51–51 | `## §9, conclusion (replaces the BYTES branch)` | Same file, L51–51; structural reference / heading only |
| `tierD_bytes_registered_design.md` P015, L53–54 | `For BYTES we report a registered design whose rival pred` | Same file, L53–54; unchanged |
| `tierE_floor_version.md` P001, L1–1 | `# Tier E (last resort): the method and diagnostic paper ` | Same file, L1–1; unchanged |
| `tierE_floor_version.md` P002, L3–7 | `&lt;!-- Use only when the primary-block release itself slip` | Same file, L3–7; structural reference / heading only |
| `tierE_floor_version.md` P003, L9–9 | `# Dividing a Laptop's Inference Energy Between Phases: A` | Same file, L9–9; unchanged |
| `tierE_floor_version.md` P004, L11–11 | `## Abstract (replaces)` | Same file, L11–11; unchanged |
| `tierE_floor_version.md` P005, L13–25 | `Language-model inference has two phases, prefill and dec` | Same file, L13–25; unchanged |
| `tierE_floor_version.md` P006, L27–27 | `## §1.3, Contributions (replaces)` | Same file, L27–27; unchanged |
| `tierE_floor_version.md` P007, L29–33 | `1. The phase-attribution method with explicit limits (Se` | Same file, L29–33; structural reference / heading only |
| `tierE_floor_version.md` P008, L35–35 | `## §5 (replaces the section)` | Same file, L35–35; structural reference / heading only |
| `tierE_floor_version.md` P009, L37–37 | `### 5. Status of the registered campaigns` | Same file, L37–37; structural reference / heading only |
| `tierE_floor_version.md` P010, L39–44 | `The primary block, the replication block and BYTES were ` | Same file, L39–44; unchanged |
| `tierE_floor_version.md` P011, L46–46 | `### 5.1 Historical diagnostics` | Same file, L46–46; structural reference / heading only |
| `tierE_floor_version.md` P012, L48–48 | `{{FILL: P1-E-HIST / the historical edge-excursion and re` | Same file, L48–48; unchanged |
| `tierE_floor_version.md` P013, L50–50 | `### 5.2 Synthetic demonstrations` | Same file, L50–50; structural reference / heading only |
| `tierE_floor_version.md` P014, L52–54 | `The worked synthetic examples of Section 3 (overlap, fir` | Same file, L52–54; structural reference / heading only |
| `tierE_floor_version.md` P015, L56–56 | `## §6.5 (replaces)` | Same file, L56–56; structural reference / heading only |
| `tierE_floor_version.md` P016, L58–58 | `BYTES is reported as a registered design (Tier D, branch` | Same file, L58–58; unchanged |
| `tierE_floor_version.md` P017, L60–60 | `## §9, Conclusion (replaces)` | Same file, L60–60; structural reference / heading only |
| `tierE_floor_version.md` P018, L62–65 | `A laptop's own power sampler can divide inference energy` | Same file, L62–65; unchanged |

## Handoff boundaries

Seat 9 owns the automation rewrite; seat 12 owns fills and outcome selection; seat 13 owns outlook content
and the introduction/conclusion scaffolds. The map preserves the predecessor’s factual corrections and
does not validate the scientific claims anew. Required review remains Opus, then the research lead.
The empty §10 and retained contingency dates are intentional handoffs, not filled text.
