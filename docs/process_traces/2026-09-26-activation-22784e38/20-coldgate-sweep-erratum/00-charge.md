# Cold gate BFGS-S1-SWEEPCLASS-01, erratum: the paired refuter's RSW-1 to RSW-9 against amendments 57–59

You are a COLD judge: a fresh session with no loop context. Do not read RUN_STATE.md, TASK_QUEUE.md, CLAUDE*.md, AGENTS.md, the decision log, or memory or skill files. **Write the contamination disclosure first.**

**Your working tree** is `/Users/edr/code/JouleWise-wt-s1swcg-92472459`, detached @ `cbfa9dc3` (S1 fix round 3, partial: amendments 49, 50, 52–56 implemented; 51 blocked). It is the same tree the ruling under review was written against. No one will move it during your session.

**Why you are convened.**
- A cold Fable instance ruled BFGS-S1-SWEEPCLASS-01. It wrote amendments 57–59, which change test code only: the self-verifying `gate_body`/`tolerant_definition` classes, the closed list of `BundleReader` public methods, the caller-that-returns-energy rule, and two sweep-rule amendments.
- The paired Opus contract refuter found **no BLOCKER**: on every path it traced, no energy value reaches a claim artifact without a battery gate. It then reports five SHOULD-FIXes and four NITs. Every one touches ruled text, so it comes to a cold judge as an erratum. The magistrate has not adjudicated them.

**The findings:**
- **RSW-1 (57 (d)):** a tolerant accessor used without a call expression (a bound-method alias, `getattr` by string, or `map(BundleReader.raw_summary, …)`) is not a read site, so a new ungated energy read would be silent. Proposed: report any non-callee reference to `raw_summary`/`raw_metadata`/`raw_artifact_bytes` as `ref:<name>`. The tree has zero such references today.
- **RSW-2 (57 (b) 4):** the cache-slot guard sees only the subscript write form. `r._cache.update(metadata=r.raw_metadata())` fills the slot, and `trace_rows()` then returns a charging bundle's rows (executed, B3). Proposed replacement text for rule 4.
- **RSW-3 (57 (b) 1):** a gate **call** can be claimed by rebinding `authenticate_window_members` or `BundleReader` outside `bundle_read.py`, through a module-level assignment or a local `def` (executed silent, B5). Proposed binding rule.
- **RSW-4 (51 (g) 4 / §6):** two row groups keep `historical` although its condition is false:
  - the two `envelope_gate.py` rows (which re-point to any `bundle_dirs`, and whose gate sits in the callee `_manifest_record`);
  - the `make_figures.py` rows.

  Proposed: reclassify them as `non_claim` (i)/(ii), and add a "gate in a callee" limitation to 51 (h). Also a lane outside S1: `envelope_gate` reports a battery refusal as `suite_manifest_missing`.
- **RSW-5 (58):** raw meter-capture path reads (`raw/powermetrics.plist`, `raw/powermetrics_idle.plist`, `nvidia_smi` CSVs) are a second, unwatched energy channel: 28 functions at `cbfa9dc3`. Proposed: a new 58 (f) with a computed-equals-constant `RAW_CAPTURE_READERS` set.
- **RSW-6..RSW-9 (NITs):**
  - RSW-6: the `events.jsonl` screen in 58 (e) is ambiguous by one function.
  - RSW-7: `events` is filed as `other` against 58 (b)'s own sentence; a new kind, `journal`, is proposed.
  - RSW-8: `request_rows`/`request_token_rows` hold no energy key (no change).
  - RSW-9: a handler ending in an always-raising helper (no change).

**Packet** (absolute, under `/Users/edr/code/JouleWise-wt-bk-92472459/docs/process_traces/2026-09-26-activation-92472459/20-bfgs-s1/90-coldgate-sweep/`):
- `00-charge.md`: the original charge and its packet.
- `21-coldgate-fable-ruling.md`: the ruling under review.
- `11-opus-contract-refuter.md`: Section A holds the independent answers; Section B holds the findings, with replacement texts and test rows (B.2).

Probes: `/tmp/oc_sw92/` (`alias.py`, `cache_probe.py`, `envelope_probe.py`, `rebind.py`, `try_return.py`, `journal58e*.py`, `q2_probe.py`, `proto_cbfa.txt`). Amendment 51 as it stands: `../80-coldgate-r2/30-erratum/21-coldgate-fable-erratum-ruling.md` §10.

**Rule.** For each finding give:
- UPHOLD or REJECT;
- executed evidence (re-run the refuter's probes on this tree, and write your own where its evidence is only a reading);
- the exact text change.

Then:
- **restate amendments 57–59 in full as they stand after your rulings**, plus any new amendment (60 onward), each self-contained with test rows, their counterfactuals, and production call sites;
- **restate the resumed S1 fix-round-3 contents for amendment 51** (what the seat implements, in order), and name anything that becomes its own lane outside S1.

Keep intact:
- custody is never a status;
- authentication precedes every exclusion decision;
- `joulewise/battery_float.py` and FT §E's excluded list stay byte-identical;
- the eight consumers do not import `battery_float`;
- amendments 57–59 change test code only, unless you rule that production code must change, and then say so explicitly with the reason.

**Output.** End with a 5-line plain summary for Ed (technical, no project grounding; gloss every internal id).

**Protocol.**
- A single non-interactive session: no background tasks, no subagents, every probe in the foreground.
- Edit no repository file. Scratch goes under `/tmp/cg_sw_erratum/`.
- Write the ruling with the Write tool to `/Users/edr/code/JouleWise-wt-22784e38/docs/process_traces/2026-09-26-activation-22784e38/20-coldgate-sweep-erratum/21-coldgate-fable-erratum-ruling.md`. Ending before that file exists is a protocol failure.
- Budget: 50 minutes. Mark anything not run as NOT EXECUTED.
