```json
{"schema":"claude-codex-report/v1","genre":"implementation","status":"clean","completion":"complete","summary":"All four fact findings and pedagogy F1–F26 cured; prospective methods moved, bindings retained, 38 focused tests pass.","workspace":{"base_requested":"fde18861","base_mode":"exact","head_start":"fde188618acb9e88b0909b0fc324a671e8e7aa4d","head_end":"fde188618acb9e88b0909b0fc324a671e8e7aa4d","upstream_end":"fde188618acb9e88b0909b0fc324a671e8e7aa4d","branch":"feat/2026-09-05-paper-m"},"pathspec":["docs/paper/draft-v2-skeleton.md","docs/paper/figures/README.md","docs/paper/figures/build_mechanism_figures.py","docs/paper/figures/fig1_boundary_attribution.svg","docs/paper/figures/fig2_window_timeline.svg","docs/paper/figures/fig3_decision_gates.svg","docs/paper/figures/fig5_phase_record_overlap.svg","docs/paper/figures/figA3_block_corners.svg","docs/paper/figures/figA4_clock_polygon.svg","docs/paper/figures/figA5_shared_signs.svg","docs/paper/figures/figA6_pulse_fit.svg","docs/paper/figures/pulse-table.md","docs/paper/figures/reproduce_worked_examples.py","docs/paper/figures/worked-examples.json","docs/paper/fill-rehearsal/select_outcome_branches.py","docs/paper/protocol/first-use-audit-ledger.md","docs/paper/protocol/prospective-comparison-protocol.md","docs/paper/results-fill-registry.md","docs/process_traces/2026-09-05-paper-m/03-fix-round-1-report.md","scripts/check_paper_replay_fence.py","tests/test_paper_first_use_ledger.py","tests/test_paper_replay_fence.py","tests/test_paper_terms_lint.py","tests/test_select_outcome_branches.py"],"unowned_dirty":[],"verdict":{"implementation":"implemented","acceptance":"ready"},"verification":[{"id":"V1","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_paper_first_use_ledger","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 11 tests in 2.169s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},{"id":"V2","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_paper_terms_lint","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 12 tests in 2.029s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},{"id":"V3","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_select_outcome_branches","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 5 tests in 0.811s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},{"id":"V4","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_paper_replay_fence","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 10 tests in 26.687s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},{"id":"V5","kind":"other","cmd":"python3 -B scripts/check_paper_replay_fence.py --corpus-root /Users/edr/code/JouleWise --draft docs/paper/draft-v2-skeleton.md --json /tmp/paper-m-fence.json","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["MEMBER 20260722T145535-e941c821","COMPARED 43","MISMATCHES 0"]},"expected":{"exit_code":0,"tail_regex":"COMPARED 43\\nMISMATCHES 0"}},{"id":"V6","kind":"other","cmd":"python3 -B docs/paper/figures/reproduce_worked_examples.py --corpus-root /Users/edr/code/JouleWise --output-dir /tmp/paper-m-worked-replay && cmp docs/paper/figures/worked-examples.json /tmp/paper-m-worked-replay/worked-examples.json && cmp docs/paper/figures/pulse-table.md /tmp/paper-m-worked-replay/pulse-table.md","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["REPLAYED synthetic compositions, 8 sign cases, current pulse 9, record 0, old pulse 0, and 2 overlap geometries","PRIMARY FINGERPRINTS MATCH; wrote worked-examples.json and pulse-table.md"]},"expected":{"exit_code":0,"tail_regex":"PRIMARY FINGERPRINTS MATCH; wrote worked-examples.json and pulse-table.md"}},{"id":"V7","kind":"lint","cmd":"python3 -B docs/paper/fill-rehearsal/select_outcome_branches.py --check-rendered docs/paper/draft-v2-skeleton.md","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["METHODS_DIAGNOSTIC validated; abstract_words=220, limit=250"]},"expected":{"exit_code":0,"tail_regex":"METHODS_DIAGNOSTIC validated; abstract_words=220, limit=250"}},{"id":"V8","kind":"inspection","cmd":"git diff --check","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}}],"flags":[]}
```

## Change

Implemented the magistrate’s accepted fact and pedagogy findings at exact head
`fde188618acb9e88b0909b0fc324a671e8e7aa4d`. Mission M0 read the active stop
card (NONE), project/workspace/restart sections, Current Queue and Do-Not-Do-Yet,
playbook, source-of-truth map, orchestration and bridge scope rules. This is the
lead-selected PAPER-M [AGENT] fix round; the exhaustive WRITE_SCOPE overrides
lead-owned bookkeeping. No agent, Claude, Codex subprocess, discovery suite,
quiet-machine capture, Git commit, push, or merge was started.

The article is now 1,421 lines, compared with 2,013 at intake. Its Section 3
states the evidence scope and cites the prospective protocol exactly once.
Section 4 retains the sensitivity arithmetic, expanded with numerical inputs,
all eight sign cases, and the convex block-endpoint construction. The protocol
is explicitly PROSPECTIVE / UNPERFORMED; its examples confer no campaign result.
The editorial ledger is outside the article and still executable: the test
reads the article followed by the protocol, with the external ledger excluded
from its own search. Footer: `Terms inventoried: 260; FAILS: 0.`

The registry retains all 202 prior DG/DS/DX/SYN/PE/PG/V5/OB/OR/TR row identifiers,
adds 13 exact DERIVE rows (SYN-02–08 and DG-129–134), and records moved
placements with dated notes. No registry row was deleted. The submission has
zero reader-facing fills, one PE-01 comment, zero empirical outcome branches,
and only the METHODS_DIAGNOSTIC selector. Historical excursion and P1 SVG bytes
are unchanged. The raw evidence stayed immutable. Both generated worked-example
parents replay byte-for-byte, including native whole-second labels, full clock
constraints, current pulse-9 local scores, older-anchor pulse-0 disclosures,
record-0 arithmetic, r03/r08 geometry, and synthetic member-envelope integrals.

### Cure map

Line numbers below refer to the final uncommitted files. “Old” quotes the
refuted wording or names the exact omission at intake; “New” records the cure.
FACT and PED identifiers are separate namespaces. Every accepted finding is
included; associated production sites are listed together when a cure spans prose,
registry, artwork, or a checker.

| Finding | Final site(s) | Old | New |
|---|---|---|---|
| FACT F1 | `docs/paper/draft-v2-skeleton.md:671`; `docs/paper/results-fill-registry.md:983`; `docs/paper/results-fill-registry.md:984`; `docs/paper/results-fill-registry.md:985`; `docs/paper/results-fill-registry.md:990`; `docs/paper/results-fill-registry.md:991` | “five units give … 1.6656 J … 1.7656 J”; five-energy, ten-delta, record-0 and old pulse-0 placements lacked exact bindings. | Register five zeros and five 0.5-J widths with both exact floor calls and downstream g(5)/0.4-J composition. Register the separate five-energy and ten-delta datasets, each raw/derived record-0 field, and every earlier-anchor pulse-0 placement. Preserve existing SYN-01/PE-01 authority. |
| FACT F2 | `docs/paper/draft-v2-skeleton.md:925`; `docs/paper/results-fill-registry.md:677` | Only runs_window_a10_20260725 was named for all 50 members. | Name ten a10 decode_absolute and forty window-C decode_abba members; cite results.json’s per-file fingerprints. Correct population labels DG-066–069/072–073/076–077; r03-only rows correctly remain a10. |
| FACT F3 | `scripts/check_paper_replay_fence.py:134`; `scripts/check_paper_replay_fence.py:561`; `tests/test_paper_replay_fence.py:79` | Extractor accepted only the current-capture heading; default and test targeted v1; submission replay failed. | Recognize unique historical/current heading, rejecting duplicates; default and test target v2; honor R7F_CORPUS_ROOT. Execute this draft: 43 comparisons, zero mismatches. Keep REPLAY_FENCED only on that observed basis. |
| FACT F4 | `docs/paper/draft-v2-skeleton.md:401` | 2.776×1.581139×√1.2=4.808173. | Use the unrounded SD: 2.776√(10/4)√1.2≈4.808173 J. Exact replay returns 4.808173041811203 J. |
| PED F1 | `docs/paper/figures/fig1_boundary_attribution.svg:3`; `docs/paper/draft-v2-skeleton.md:169` | Artwork used 0.030 s × 33-W power step ≈1 J and claimed energy in the wrong physical phase. | Redraw a full 30-W record with a 0.010-s-wide, full-height hatched slice =0.30 J. Print both phase assignments and unchanged 3.00-J total. Remove universal physical phase-power claims; all power levels are illustrative. |
| PED F2 | `docs/paper/draft-v2-skeleton.md:1298`; `docs/paper/results-fill-registry.md:994`; `docs/paper/results-fill-registry.md:995` | “Everything below is stated as the code executes it”; clock/command/native/local-fit inputs were missing. | Supply Table A3’s current pulse-9 command triples, numeric native/causal constraints, every local record, predicted average and Huber loss. Sidecar supplies all 1665 native constraints, five stamps, commands and full precision. Explicitly distinguish the earlier-anchor pulse-0 example. |
| PED F3 | `docs/paper/draft-v2-skeleton.md:766`; `docs/paper/results-fill-registry.md:992`; `docs/paper/results-fill-registry.md:993` | “Two is less than the required three” without geometry. | Print r03 phase/record endpoints and 0.0533655/0.0676686-s overlaps, both zero-overlap neighbors, plus r08’s three positive overlaps and zero-overlap neighbors from retained bytes. Explain decimal-vs-binary64 last-digit convention. |
| PED F4 | `docs/paper/draft-v2-skeleton.md:305`; `docs/paper/protocol/prospective-comparison-protocol.md:1`; `docs/paper/protocol/first-use-audit-ledger.md:1` | Unperformed characterization, identities/census, claims, operational fields, dependence/custody and supply chain occupied the article; editorial ledger followed the article. | Move the specified sections and adjacent comparison-only appendix material into the labelled protocol; cite it once. Keep Section 4. Condense future work and prefill selection. Move the editorial ledger into its own appendix file and retain executable first-use auditing. Full move map follows. |
| PED F5 | `docs/paper/draft-v2-skeleton.md:413`; `docs/paper/figures/figA3_block_corners.svg:1` | “choose … every admitted energy”; 16 units left 2^(4n) versus 2^n ambiguous. | Form each block’s difference interval, then enumerate 2^n block endpoints. Explain convexity through centered norms, absolute means and maxima. Show four numerical corners, statistics, maximum 45.014875 J, n>16 refusal, and the diagnostic-only n=2 limit. |
| PED F6 | `docs/paper/draft-v2-skeleton.md:1065` | Network synchronization off “excluded” an invisible between-stamp excursion. | Disabling correction removes one adjustment source; constant clock rate between stamps remains unverified. |
| PED F7 | `docs/paper/draft-v2-skeleton.md:11` | Undefined output tokens in the Abstract. | Introduce tokens as pieces of generated text at first use. |
| PED F8 | `docs/paper/draft-v2-skeleton.md:51` | “bounds neither physical phase energy … inference transfer … future-error coverage.” | Say the range does not locate actual energy within records, establish pulse-to-model timing agreement, or guarantee future-error containment frequency. |
| PED F9 | `docs/paper/draft-v2-skeleton.md:106` | Absolute floor, comparative floor and science contrast first appeared as unexplained table entries. | Explain repeat false differences and threshold construction before the table; define centered-repeat, same-model block and two-model sources. |
| PED F10 | `docs/paper/draft-v2-skeleton.md:180` | “far enough,” “better,” “accepted,” and “No uncommanded plateau” had no nearby numeric predicates. | Build b and σ first; show the 5-W plateau example, ≥10-W and SNR≥10 checks, strict half-flat-loss check, 0.499/0.500-s shift example, and 0.75-s coverage requirement before their summary use. |
| PED F11 | `docs/paper/draft-v2-skeleton.md:163`; `docs/paper/draft-v2-skeleton.md:199` | CPU/neural engine were unglossed; stage came after its first use. | Gloss both processors where first named; define a stage and admission before the timeline’s entry-check sentence. |
| PED F12 | `docs/paper/draft-v2-skeleton.md:213`; `docs/paper/figures/fig2_window_timeline.svg:157` | “Curvature remains covered”; Figure A2 said drift is bounded by the allowance. | References sample selected epochs; their empirical allowance cannot bound an arbitrary unobserved rise and fall. Update text, caption and artwork. |
| PED F13 | `docs/paper/protocol/prospective-comparison-protocol.md:78`; `docs/paper/draft-v2-skeleton.md:359` | Admission was equated with an independent observation. | Runs or complete blocks are model observations; admission does not establish statistical independence. |
| PED F14 | `docs/paper/protocol/prospective-comparison-protocol.md:189`; `docs/paper/results-fill-registry.md:987` | Unexplained weights (−2,0,+2) gave 28–48 J/token. | Give least-squares weight formula; counts 1,2,3 yield (−0.5,0,+0.5) per token and the printed intervals give 7–12 J/token. |
| PED F15 | `docs/paper/draft-v2-skeleton.md:568`; `docs/paper/draft-v2-skeleton.md:597`; `docs/paper/figures/figA5_shared_signs.svg:1` | Block 2 q/local width and M were supplied answers; no full enumeration. | Print both extrema, all four block-2 residuals, four enlarged-window integrals per block and M construction. Retained trimmed traces recompute each M. Print all eight sign/delta/mean/SD/bound rows and the (+1,−1,+1) maximum; distinguish full-precision 8.8304376431 from rounded-input 8.8304376433. |
| PED F16 | `docs/paper/protocol/prospective-comparison-protocol.md:298`; `docs/paper/protocol/prospective-comparison-protocol.md:305`; `docs/paper/figures/fig3_decision_gates.svg:56` | “the adjusted test passes” had no matching 10-J test data; Gate 2 omitted Holm. | Geometry gives a sign pass only. Supply h=tcritical×SE and a complete ten-value symmetric 10-J dataset, t=45.24 and computed p; pair it with the earlier ten-delta computed p for an explicit Holm pass. Gate 2 includes both intervals and Holm. |
| PED F17 | `docs/paper/protocol/prospective-comparison-protocol.md:373`; `docs/paper/figures/fig3_decision_gates.svg:28` | Refusal list included below-floor effects; artwork said “no result of any kind.” | Separate invalid-evidence refusal from usable below-floor not-resolvable outcomes. Refusal produces no authorized comparison result. |
| PED F18 | `docs/paper/draft-v2-skeleton.md:708` | Count and three-record minimum were described as the same test. | Separate count from chosen cutoff. Explain the middle-record rationale, exclude boundary-only allocation support, and state that three records prove neither adequate precision nor three complete records. |
| PED F19 | `docs/paper/draft-v2-skeleton.md:742` | IQR digits had no interpolation/rounding convention. | Interpolate quartiles at zero-based (n−1)p using exact decimal timestamps, subtract, round milliseconds to four decimals ties-to-even; digits describe stored values rather than physical resolution. |
| PED F20 | `docs/paper/draft-v2-skeleton.md:887` | Related work claimed calibration of runtime phase boundaries and a resulting empirical claim gate. | State the actual contribution: GPU edge fits and phase-allocation sensitivity; transfer to inference is untested, with Sections 2/4 references. |
| PED F21 | `docs/paper/draft-v2-skeleton.md:992` | “released revision” and archive requirements implied available public replay; release caveats repeated. | Give the exact development code baseline and existing source locators; distinguish repository-only synthetic replay from unreleased historical bytes. Consolidate article release statements and preserve removed detail in protocol P.10. |
| PED F22 | `docs/paper/draft-v2-skeleton.md:1058`; `docs/paper/draft-v2-skeleton.md:1305`; `docs/paper/figures/figA4_clock_polygon.svg:1` | A was said to be expressed uniquely through the affine relation. | Search A, α, β; eliminate α; jointly solve A and β. Print real native/causal constraints and a labelled synthetic polygon showing axes, rows, intersection, projections and empty-set refusal. |
| PED F23 | `docs/paper/draft-v2-skeleton.md:1199`; `docs/paper/draft-v2-skeleton.md:1356`; `docs/paper/figures/figA6_pulse_fit.svg:1` | Huber’s linear tail meant “a single wild sample cannot dominate”; no numeric prediction/loss illustration. | Describe reduced influence relative to squared error and unbounded loss. Print every prediction/loss and x=1/2 branch arithmetic; show command times, records, best model averages and projected enclosure in Figure A6. |
| PED F24 | `docs/paper/draft-v2-skeleton.md:1223` | “data cannot distinguish” and a guaranteed enclosure were overinterpreted physically. | Define the tolerance set as a model set; split rectangles and reject via lower-bound cutoff. Explicitly deny confidence-region, physical-edge and future-error guarantees, including the earlier pulse example. |
| PED F25 | `docs/paper/draft-v2-skeleton.md:1249` | The anchor error was asserted independent of per-edge error. | Adding allowance magnitudes bounds combined displacement without an independence assumption. |
| PED F26 | `docs/paper/figures/fig5_phase_record_overlap.svg:12`; `docs/paper/figures/fig2_window_timeline.svg:13` | Embedded titles said Figure 5 and Figure 2. | Embedded titles now match article captions Figure 4 and Figure A2. |

### Moved-section map

All old ranges were checked against the intake head; blank separator lines explain
the one-line extensions beyond the brief. The operational move takes the complete
section (909–940), encompassing the requested 917–938 fields.

| Intake article lines | Material | Final protocol home |
|---|---|---|
| 150–191 | Prospective campaign identities and ratio census | `docs/paper/protocol/prospective-comparison-protocol.md:10` |
| 326–498 | Instrument characterization | `docs/paper/protocol/prospective-comparison-protocol.md:54` |
| 803–908 | Directional comparison and claim gates | `docs/paper/protocol/prospective-comparison-protocol.md:229` |
| 909–940 | Operational admission and refusal | `docs/paper/protocol/prospective-comparison-protocol.md:350` |
| 1099–1188 | Campaign dependence and custody limitations | `docs/paper/protocol/prospective-comparison-protocol.md:382` |
| 1288–1300 | Prospective publication supply chain | `docs/paper/protocol/prospective-comparison-protocol.md:474` |
| 1193–1237 | Future validation designs | `docs/paper/protocol/prospective-comparison-protocol.md:489` |
| 1371–1373 | Comparison archive objects | `docs/paper/protocol/prospective-comparison-protocol.md:536` |
| 1680–1681 | Comparison refusal interpretation | `docs/paper/protocol/prospective-comparison-protocol.md:541` |
| 1682–1689 | Historical release-status note | `docs/paper/protocol/prospective-comparison-protocol.md:545` |
| 1362–1362 | Fresh collection prerequisites | `docs/paper/protocol/prospective-comparison-protocol.md:555` |
| 1731–2013 | Editorial first-use ledger | `docs/paper/protocol/first-use-audit-ledger.md:1` (separate audit appendix; not protocol prose) |
| 1034–1041 | Prefill ladder detail condensed to actual-overlap principle | `docs/paper/draft-v2-skeleton.md:811` |
| 1193–1236 | Detailed future studies condensed in article, preserved in P.7 | `docs/paper/draft-v2-skeleton.md:874` |

Dated registry relocation notes accompany V5-ID-001/002 and V5-WL-001–004
(P.1), characterization method context DS-02/03/05/06 (P.2; their old result
anchors stay retired), DG-027’s future-study repetition (P.7), and DS-34’s
removed A.6 statement (P.10). The new SYN-04/SYN-06 rows directly name P.3/P.5
and P.2. Existing retired results are neither reactivated nor given phantom
placements. All other active historical placements remain in the article.

### Clause map

| Production site / proposition | Biting assertion | Counterfactual |
|---|---|---|
| `scripts/check_paper_replay_fence.py:134` — unique historical heading | `tests/test_paper_replay_fence.py:79` | Remove historical support or admit duplicate headings; the extraction test fails. |
| `tests/test_paper_replay_fence.py:37` — corpus-root replay actually runs | `tests/test_paper_replay_fence.py:157` | Change a fenced digit in the draft; primary-byte equality fails (43 compared values). |
| `docs/paper/fill-rehearsal/select_outcome_branches.py:49` — external ledger and one protocol citation | `tests/test_select_outcome_branches.py:54` | Return the ledger or operational heading to the article, remove/duplicate the protocol link; selector mutation checks fail. |
| `docs/paper/results-fill-registry.md:983` — complete DERIVE census and exact input arithmetic | `tests/test_paper_terms_lint.py:395` | Delete a new row, change its DERIVE column, mutate a pinned sidecar value, or narrow an integral; numerical/hash/row assertions fail. |
| `docs/paper/protocol/first-use-audit-ledger.md:284` — external zero-FAIL ledger | `tests/test_paper_first_use_ledger.py:487`; `tests/test_paper_first_use_ledger.py:538` | Delete a first-use defining phrase, move it later, change a home, or increment FAILS; existing ledger tests fail. |
| `docs/paper/draft-v2-skeleton.md:305` — structural cut and semantic qualifications | `tests/test_paper_terms_lint.py:453` | Reintroduce a moved section or remove the clock-rate/independence/loss/record-cutoff qualifications; structure/prose assertions fail. |

The remaining line-level prose/artwork cures in the 30-row map received direct
inspection; the tests do not claim to mechanically prove prose quality. This
seat implemented and checked the fixes; independent refutation and the final
landing decision remain with the lead.

## Verification notes

Preflight ran only the four named modules, separately and in the requested
order: 11 OK; 10 OK; 5 OK; 9 OK (one primary-corpus test skipped because the
old test ignored R7F_CORPUS_ROOT). The final four modules above run 38 tests
with no skips. No discovery suite was run, as explicitly forbidden by the brief.

During implementation, the first temporary worked-input builder unpacked a
three-item helper result into two variables; corrected before committing any
reported parent. The added numerical regression initially compared dataclass
tuples directly with JSON lists; it now compares the JSON serialization that
the artifact actually stores. That focused test reran green. Native labels
explicitly use plist whole-second metadata, not parser-interpolated time.

macOS Quick Look failed to initialize its sandbox and `sips` could not decode
SVG; CUA reported no browser. Local rasterization succeeded with the installed
`sharp` package. All eight changed/new SVGs were inspected at native size:
Figure 1’s hatching has the full 30-W height and 10-ms width; A3/A4/A5 expose
their inputs and operations; A6’s records/model lines and printed enclosing
rectangle are distinct; A2, Figure 3 and Figure 4 have readable corrected
labels. The existing PNG directory is historical, not used by this draft,
and its status is now explicit in the figure README. No external integration
was installed or invoked to upload anything.

Full historical replay still needs the unreleased source corpus, as the
article already discloses. The pulse-0 fields remain explicitly stored
**earlier-anchor** values; the new pulse-9 table is freshly derived with the
current anchor. Nothing here establishes transfer to inference, independence,
physical within-record allocation, or a new comparison result.

Next exact step: the lead reviews this scoped, uncommitted diff and submits it
to the paper-M follow-up refuters. HEAD and upstream remain fde18861.
