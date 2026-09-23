# Cold-gate ruling 10 — QPE01-DAEMON-CONTAMINATION-01 (Fable 5.1, cold judge, 2026-09-23 00:00–00:2x PDT)

Worktree `JouleWise-wt-coldgate-a022aecc` at `258c90ed`, clean. Read-only except this file. No subagents, no background tasks, no systemsetup/sudo/powermetrics/launchctl.

## 0. Disclosure and trust anchors

Auto-loaded before any action: `~/.claude/CLAUDE.md`, the worktree `CLAUDE.md`, and the memory index `MEMORY.md` (index lines only; those lines mention this night's harvest outcome and the fseventsd finding). Not opened: CLAUDE.local.md, RUN_STATE.md, TASK_QUEUE.md, memory bodies, any other process trace or council log. Read: charter, packet, exhibits A/B/C, harvest record §6 tail + §7 (`01-…-harvest-record.md:521-597`), both archive roots (read-only).

Validator, method `python3 scripts/validate_gate_packet.py …` (receipt schema `coldgate-validator-receipt/v2`):
- Run 1, expected charter `…5813a880ff…` (typo): result REFUSE, reason `charter_trusted_observed_mismatch`, rc 2. Observed charter sha `099de884…a870ff…95d81`.
- Run 2, expected charter `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81`, packet `7083c815f103e2361aaa8ec51ef1b421fc7428bf2e7aa95ff7b5d8382c6725fa`: PASS, rc 0, all five exhibit digests observed == expected.
- Independent `shasum -a 256`: charter `099de884…95d81`, packet `7083c815…25fa`. Match. Merits read after this.

## 1. Verified evidence (executed this session)

- Archive digests: `summary.json` `84bfcafb…`, `evidence_busy_cores.jsonl` `4ad71d0b…`, `receipt.json` `64ed9c4d…`, `result.json` `ea1b5565…`, prior `summary.json` `9121f080…`, prior journal `39224eb5…` — all equal to C9.
- Sizing re-derived from `summary.json` envelopes with my own gamma inversion: deltas [−342.890, 2.033, −3.485, 7.417, −9.349, 42.088], s_pair 144.2791, χ²₀.₁₀(5) 1.610308, s_upper 254.2342, pairs 517081. Equal to C2/C7.
- Journal, per-envelope join (rows with metrics whose `monotonic_start` ∈ [scheduled, scheduled+600)): tonight `fseventsd` median 0.998–0.999 cores in all twelve envelopes (19–20 rows each); busy-core-seconds Σ(busy_cores·interval_s) per envelope 574.7–605.8; `mediaanalysisd` envelope 1: 528.1 core-s, samples 1.44, 1.75, 1.73, 1.76, 1.76, 1.67, 1.45, 1.32, 1.78, 1.79, 0.94 at t+243…t+547 s. Prior night: largest non-observer per-envelope integral `launchd` 5.2–6.1 core-s, `WindowServer` 3.8–6.3; largest per-envelope median other than the power sampler 0.009.
- **Observer flag: zero rows carry `observer: true` in either journal (243 and 236 rows with metrics).** Cause at `91f80870`: `record_covariates` calls `sample_interval(protocol["sample_interval_s"])` (A3a:853) without `observer_pid`; `quiet_admission.py:240` defaults it to the recorder's own pid, and `interval_metrics:136-141` marks only that pid's descendants. `powermetrics` is launched by the collector (sibling pgid 17874, `evidence_processes.jsonl` kind `power`) so it is never marked. Consequence: the prior (clean) night's `powermetrics` median is 0.111–0.115 cores in every envelope.
- Unified log (`/usr/bin/log show --last 30h … "scan_old"`): first line 2026-09-22 04:49:03.306, last 2026-09-23 00:01:09, 810 lines. `ps`: pid 341 `fseventsd` 100.1 % CPU, 1291 CPU-min, etime 4d06h. Confirms C6.
- `tests.test_quiet_predicate_campaign`: 128 tests OK in 12.8 s (one run).

## 2. Q1 — standing of night 20260922-2100: AFFIRM (c), with corrected label text

Deciding evidence: the registration's premise (A5:33 `load_generator: false`; README B7 "idle energy observations"; notice A4:271 "twelve idle envelopes") describes an idle machine; C3 and my join show one non-observer process at a full core in every sample of every envelope, 16 h into a documented failure loop that predates the arm (C6). The rules were applied exactly (A3d `hard_exclusions` never reads busy cores; my re-derivation matches), so the numbers are correct for the machine measured. Charter §9: a machinery/precondition defect does not flip the recorded outcome; it supports a separately authorised rerun under corrected machinery, and the original stays in the record. That is (c). (a) REJECTED: it would make a daemon fault the paper's finding about idle variance, and the summary's own `clean_machine_busy_cores` p50 1.22 (vs 0.24 prior) shows the "clean machine" its deliverable describes was not clean. (b) REJECTED: nothing measured is void; "void" is the post-hoc reasoning rules-before-data forbids.

Label text (harvest record §2 and the paper's pilot section, verbatim):

> MEASURED ON A NON-IDLE MACHINE. All twelve envelopes were captured while the system daemon `fseventsd` (pid 341) held 0.998–1.000 busy cores in 243 of 243 load-journal samples that carried metrics (2 of 245 rows carried none), in a `scan_old` failure loop logged from 04:49:03 PDT on 2026-09-22, 16 h before t0; `mediaanalysisd` additionally ran at 1.3–1.8 busy cores in ten consecutive 30 s samples and 0.9 in an eleventh (t+243 s to t+547 s of envelope 1). The registered rules (registration v2, sha256 2c539240…) name no exclusion for non-observer processes, so every envelope is retained and the registered summary is reported as computed. This night is NOT used to size block two; the pilot is re-run under registration v3, which adds the non-observer-process rule fixed before that night runs. Both nights are reported side by side.

The stop-branch sentence (`block_two_stop.outcome` "no cutoff qualifies", causes `sized_pairs_above_24`, `observer_floor_above_smallest_holdable_share`) may be quoted ONLY immediately followed by this label, never alone; the same applies to `clean_machine_busy_cores`, whose field name must be glossed as "envelopes passing census, AC and thermal probes" (A3d:1093), not as an idle-machine distribution.

## 3. Q2 — machine-state predicate: AFFIRM (a) in shape, REJECT three of its details, ruled rules below

(b) rejected as argued (the total is the number the pilot sizes; the observer's own 0.11 sits inside it). (c) rejected: 1.03 passed tonight (C5). (d) rejected: unattended operation cannot depend on hands; hygiene recommended to Ed, not a gate.

**BLOCKER (Q2, regressions).** The packet's premise "the observer set is what `sample_interval(observer_pid=…)` already marks" is false at `91f80870` (§1). Under (a)(ii) as drafted with ENV_SHARE 0.10 over the journal as written, the prior clean night is excluded twelve times naming `powermetrics` (median 0.111–0.115). The packet's sentence "the previous night's top non-observer consumer never exceeded 0.06 cores mean (C4)" is contradicted by C4's first row (`powermetrics` mean 0.1118). Cure (mandatory in v3): the executor passes its own pid to the recorder (`record_covariates(protocol, night_dir, observer_pid=<chain root pid>)` → `sample_interval(interval, observer_pid=…)`; the CLI already accepts `--observer-pid`, `quiet_admission.py:334`), so collector, `sudo`, `powermetrics`, `top`, census and recorder are all marked `observer: true` by ancestry; the summary's rule reads that flag and nothing else. A regression proves a real chain marks the power recorder.

**MATERIAL (Q2 bar).** Ruled rule (ii) is an integral, not a median: a 5-min burst at 1.5 cores is excluded by both, but an 8-sample (4-min) burst adds ≈ 1.1 W × 240 s ≈ 270 J and passes a 20-sample median. Rule: for each envelope, for each non-observer process identity, `Σ busy_cores × interval_s` over the journal rows joined to that envelope ≥ **30 core-seconds** → exclusion `non_observer_process_busy`. Arithmetic: 30 core-s = 0.05 core (registered `smallest_holdable_share`, the effect block two is built to detect) × 600 s; at the measured 0.3125 W per busy core (C8: 150 J per core-interior; an efficiency-core rate, so a floor) that is ≈ 9.4 J per envelope, ≈ 7.5 J inside the 480 s interior, above the ≈ 5 J claim bar (B2b) and not microscopic; the clean night's largest non-observer integral is 6.3 core-s (`WindowServer`, envelope 2), 4.8× headroom; tonight's `fseventsd` 575–606 and `mediaanalysisd` 528 are 18–20× over. The lead's 0.10-core median would admit a process costing ≈ 15 J, three times the claim bar — its own arithmetic argues against it. Observed below-bar case, kept as idle variance by design: `XprotectService` 10.7 core-s in envelope 12 (that envelope reads +42 J; report as a diagnostic).

**(i) t0 and arm check.** AFFIRM T0_SHARE = **0.5** busy cores over one 30 s `sample_interval` observation (`observer_pid=os.getpid()`; no powermetrics exists yet, so the default is correct there). Arithmetic: 0.5 core is 5× the largest single-sample transient seen on either night outside the daemons (`corespotlightd` 0.104), half the runaway signature (1.0), and ≈ 75 J per interior; anything admitted below it is caught per envelope by (ii). Applies at both the arm `check` (`armable: false`, same predicate, same text) and t0 (`_check_machine`, binding), for v2 and v3 plans alike since it is a gate predicate, not a registration field. Refusal text (exact):

`night_refused_not_quiet`, detail `non-observer process busy: <basename> pid <pid> at <busy_cores:.3f> busy cores over <interval_s:.1f> s (bar 0.5); observation in top_consumers_at_decision`. The receipt row C3 carries `top_consumers_at_decision` (already in `_QUIET_RECEIPT_KEYS`, A1e:245; absent from tonight's receipt, C5).

**Registration v3 field texts (exact):**
- `"exclusions"` gains `"non_observer_process_busy"` (eleventh entry).
- `"non_observer_process_busy": {"statistic": "per non-observer process identity: sum over journal rows joined to the envelope of busy_cores * interval_s", "bar_core_seconds": 30, "bar_basis": "0.05 core (block_two.smallest_holdable_share) * 600 s; ~7.5 J per 480 s interior at 0.3125 W per busy core (night 20260922-2100, C8), above the 5 J claim bar", "observer": "top_consumers[].observer == true (recorder run with observer_pid = chain root pid)", "abort_after_consecutive": 2}`
- `"t0_non_observer_share_max": 0.5`
- `"busy_cores_role"`: unchanged (`covariate_only`); the new rule reads per-process shares, never the total.
- `"ruling"` appends `"; cold gate 10 QPE01-DAEMON-CONTAMINATION-01 (2026-09-23) Q1(c)/Q2/Q3(a)"`.

**Abort count:** AFFIRM 2 consecutive `non_observer_process_busy` exclusions → chain abort with a typed refusal document, reason `non_observer_process_busy`, ≈ 31 min after t0 (600 s settle + 2 × 620 s). Counterfactual: one such exclusion then a clean envelope → no abort (envelope 1 tonight alone would not have aborted a night that was otherwise clean).

**REJECT the "zero-capture class" label.** D-182 (B1b:122-125) defines zero capture as no capture writer ran; two `powermetrics` captures will have run. The abort is a machine-state abort AFTER capture, which D-182 does not license. Proposed addendum text for Ed's ratification (outside this gate's authority to enact): "A chain abort on `non_observer_process_busy` with fewer than `minimum_retained` envelopes captured licenses one new-plan successor on the same terms as a zero-capture refusal (new plan id, fresh notice, ≥ 60 s spacing, bounded by install close, every NO stops); the captured envelopes stay in the archive under the Q1 label." Until ratified, the abort ends the span with no automatic successor.

**mediaanalysisd class:** nothing beyond ruled (ii); the integral catches a 20 s burst at 1.5 cores (30 core-s). No basename list: naming Apple daemons is a guard against a moving target and would miss the next one.

## 4. Q3 — retroactive diagnostic and pilot count: AFFIRM (a)

The v3 rule may be run over tonight's journal as a labelled diagnostic only. Because tonight's rows carry no observer marks (§1), the diagnostic must state its observer set explicitly: consumers whose command basename is in {`powermetrics`, `Python`, `top`, `sudo`, `ps`, `pgrep`, `sysctl`} are treated as observer, labelled as an assumption the v3 recorder replaces with pid ancestry. Executed expectation (my join): twelve exclusions each naming `fseventsd` (575–606 core-s), envelope 1 also naming `mediaanalysisd` (528); prior night: zero exclusions (max 6.3). Label text: "DIAGNOSTIC ONLY — registration v3 rule applied after the fact to night 20260922-2100 under an explicit observer basename set; not a registered result, sizes nothing." Pilot count: re-run ONCE under v3 on a machine passing the t0 predicate; "no cutoff qualifies" becomes a registered outcome only from that night. (c) REJECTED: no clean pilot has produced a sizing; two contaminated/inconclusive nights are not an exhausted pilot.

## 5. Regressions (each must FAIL at `91f80870`; production call site named)

0. Real-chain observer marking: run the executor's recorder path with the chain root pid; a synthetic sibling `powermetrics` row with ppid = collector → `observer: true`. Fails today (flag never set). Site: `quiet_predicate_campaign.record_covariates` → `quiet_admission.sample_interval`.
1. Tonight's archived journal + session scheduled instants through v3 `pilot_summary` → twelve `non_observer_process_busy` naming `fseventsd`; prior night's rows (with regression 0's marking, or the explicit observer set) → zero. Fails today (no such reason). Site: `pilot_summary` exclusion loop (A3d:951-1046).
2. Synthetic t0 observation, non-observer at 0.6 cores → `night_refused_not_quiet` with the ruled detail text and `top_consumers_at_decision` populated; same consumer `observer: true` → admitted. Site: `night_gate._check_machine` (both `legacy_load` branches) and the arm `check`.
3. Two consecutive exclusions → typed abort `non_observer_process_busy` after envelope 2; one exclusion then clean → no abort, twelve envelopes attempted. Site: the evidence executor's envelope loop.
4. v3 digest in `RULED_REGISTRATIONS`; a NEW plan pinned to v2's digest → `night_refused_registration`; a retained custody root recorded under v2 still classifies retained in `check`. Site: `night_gate` table lookup (B4 Q1).
5. Summary re-derived from disk under v3 equals the executor's exclusion set (tonight: 12/12). Site: `pilot_summary`.
6. Burst counterfactual that kills the median variant: 8 rows at 1.5 cores then 12 at 0.0 for one non-observer pid → excluded (360 core-s); the same 8 rows at 0.09 → not excluded (21.6 core-s).

## 6. Packet hygiene

- BLOCKER: the observer-set claim (Q2 text) is argument stated as fact and is false at the pinned revision; it changes the Q2 bar and regression 1's counterfactual.
- MATERIAL: "never exceeded 0.06 cores mean (C4)" contradicts C4 row 1 (0.1118); unsupported paraphrase.
- MATERIAL: "zero-capture-class stop" relabels D-182's defined term.
- NIT: label draft "1.4–1.8 for five minutes" vs data 1.3–1.8 with a 0.94 eleventh sample; "100 % of samples" should read 243 of 243 with metrics.
- NIT: packet does not name the summary's `clean_machine_busy_cores` misnomer, which the paper would otherwise quote.
- No omitted contrary evidence found; C7's counterfactual is correctly labelled inadmissible; the neutral presentation of (a)–(d) is adequate.

NOT EXECUTED: none. Every number above was recomputed from the archive or read from `git show 91f80870:<path>`.
