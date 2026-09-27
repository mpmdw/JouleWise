# Cold gate SWEEPCLASS-SAMESIG-01: the S1 read-site sweep after two same-signature rounds

You are a COLD judge: a fresh session with no loop context. Do not read RUN_STATE.md, TASK_QUEUE.md, CLAUDE*.md, AGENTS.md, the decision log, or memory or skill files. The one exception: you may grep `docs/decision_log.md` for the D-161 entry only. **Write the contamination disclosure first.**

**Your working tree** is `/Users/edr/code/JouleWise-wt-samesig-cg-3ba66eeb`, detached @ `315364b2` (the S1 head: `feat/2026-09-26-bfgs-s1-bundles`, which includes main `97082508`). The partial fix-round-3 tree `cbfa9dc3` is its parent; read it with `git show`.

**Why you are convened (rule-11 standing escalation).** Two consecutive rounds failed with the same signature:
- The cold ruling BFGS-S1-SWEEPCLASS-01 was followed by refuter RSW-1..9.
- The erratum ruling that followed was then hit by refuter B-1..B-9.

Each round's paired Opus refuter found 0 BLOCKER and 5 SHOULD-FIX latent evasion forms against a static, syntax-based sweep of read sites. Both refuters found no ungated energy read reaching a claim artifact in the tree. Rule 11 makes the next spend a consult, not round three. That consult has run: three blind seats (Sol 6.0, Astra 6, Opus 5.5) answered the same charge. **You rule.**

**Packet** (absolute, under `/Users/edr/code/JouleWise-wt-22784e38/docs/process_traces/`):
- `2026-09-27-activation-3ba66eeb/30-sweepclass-samesig/00-consult-charge.md`: the consult charge. It builds the background (the gate, the tolerant accessors, the sweep) and asks Q1–Q6.
- `…/11-sol-consult.md`, `…/12-astra-consult.md`, `…/13-opus-consult.md`: the three seat reports. Opus's probes are in `…/probes-opus/`.
- The round-2 erratum: `2026-09-26-activation-22784e38/20-coldgate-sweep-erratum/`, holding `00-charge.md`, `21-coldgate-fable-erratum-ruling.md` (§6 amendments 57–60, §8 fix-round-3 contents) and `11-opus-contract-refuter.md` (Section B, B-1..B-9).
- The round-1 ruling, charge and refuter: `/Users/edr/code/JouleWise-wt-bk-92472459/docs/process_traces/2026-09-26-activation-92472459/20-bfgs-s1/90-coldgate-sweep/`.

**Where the seats agree:**
- Q1: an exhaustive static guarantee is not closable, and this is the same signature.
- B-1 (unvisited scopes) and B-5 (references counted as well as calls) guard plausible accidents: close them.
- B-2 (patching the gate's behaviour, `type()` subclasses) is deliberate evasion under D-161: record it as a limitation.
- No current leak.
- The sweep is currently failing at the S1 head on an allowlist inventory mismatch. Sol and Astra both report it; Astra names `evaluate_member/direct:read_text` (unlisted) and `run_axi_spec_campaign/direct:read_bytes` (stale). This blocks S1's merge.

**Where they differ:**
- **B-3** (`_path` re-point). Sol: a narrow static rule. Astra: a runtime immutable reader root in `bundle_read.py`. Opus: D-161 limitation now, with an optional ~6-line path binding in `BundleReader.metadata`.
- **B-4** (envelope rows falsely `non_claim` (ii)). Sol and Opus: the behaviour-identical production edit (`reader.metadata()` before `envelope_gate.py:133` and `:654`) before S1's allowlist closes. Astra: reclassify under a closed, evidenced callee form of `behind_gate`, with the production edit optional.
- **Stop rule.** Sol: accidental-edit mutations. Astra: one finite judge-approved acceptance predicate. Opus: a four-clause deliberate-evasion test in 51 (h), with the gated-`summary()` redesign as the next spend if B-1/B-5 fail again.
- **Opus root cause:** there is no gated `summary()` accessor, so energy in `summary_metrics.json` is reachable only through the ungated `raw_summary()`. The proposed redesign lane is a gated `summary()` with claim consumers moved onto it.

**Rule** (executed evidence where the reports' evidence is only a reading; re-run at least the B-1 and inventory-failure probes on this tree):
1. Q1–Q2: adopt, amend or reject the consensus. State the narrowed promise of amendment 51 in exact text: what the sweep guarantees and what it does not.
2. B-1..B-9 dispositions under that promise, each with exact text or "limitation" wording for 51 (h).
3. B-3 and B-4: choose, with reasons. If you rule a production change (in `bundle_read.py` or `envelope_gate.py`), say so explicitly and name its lane and order relative to S1's merge.
4. The inventory failure: what fix round 3 does about it (the consumers-form reasoning, not blind acceptance of keys).
5. **Fix round 3, restated as an ordered, self-contained list** the implementing seat can follow, with test rows, counterfactuals and production call sites, and the finite acceptance predicate that ends the lane (the stop rule).
6. The gated-`summary()` redesign: its own lane, or not needed? Does it block anything?

Keep intact:
- custody is never a status;
- authentication precedes every exclusion decision;
- `joulewise/battery_float.py` and FT §E's excluded list stay byte-identical;
- the eight consumers do not import `battery_float`.

**Protocol.**
- One non-interactive session: no background tasks, no subagents, every probe in the foreground.
- Edit no repository file. Scratch goes under `/tmp/cg_samesig/`.
- Write the ruling with the Write tool to `/Users/edr/code/JouleWise-wt-22784e38/docs/process_traces/2026-09-27-activation-3ba66eeb/30-sweepclass-samesig/21-coldgate-fable-ruling.md`. Ending before that file exists is a protocol failure.
- Budget: 50 minutes. Mark anything not run as NOT EXECUTED.
- End with a 5-line plain summary for Ed (technical, no project grounding; gloss every internal id).
