# Cold gate BFGS-S1-SWEEPCLASS-01: how amendment 51's sweep classifies the gate's own reads, and whether `BundleReader.raw_summary` is gated

You are a COLD judge: a fresh session with no loop context. Do not read RUN_STATE.md, TASK_QUEUE.md, CLAUDE*.md, AGENTS.md, the decision log, or memory or skill files. **Write the contamination disclosure first.**

**Your working tree** is detached @ `cbfa9dc3` (S1 fix round 3, partial: amendments 49, 50, 52–56 implemented; 51 blocked). No one will move it during your session. Base `1417c0c4`.

**Why you are convened.** The S1 fix-round-3 seat implemented amendments 49–56 of the BFGS-S1-R2-01 erratum except amendment 51 (the read sweep), which it returned as NEEDS_RULING. Its prototype of the ruled detector reports 120 read sites in 89 functions. Three of them fit none of amendment 51's four allowlist classes:

| Site | Why no class fits (seat's words) |
|---|---|
| `joulewise/battery_float.py::authenticate_bundle`, `direct:_required_object`, `metadata.json` | Returns a `PairVerdict`; it *is* the authentication; `battery_float.py` is frozen byte-identical. |
| `joulewise/bundle_read.py::BundleReader.metadata`, `direct:_strict_json`, `metadata.json` | Returns full metadata to claim consumers and is itself the reader-form gate. |
| `joulewise/bundle_read.py::BundleReader.raw_summary`, `direct:_tolerant_json`, `summary_metrics.json` | Returns energy-bearing summary content and is callable without a preceding gate. |

The seat recommends a narrow `gate_implementation` class with named functions and reasons. The magistrate has not adjudicated this. The third row may be a gap rather than a classification question: Final texts v1.1 text 8 gates "the four energy accessors" through `BundleReader.metadata()`. Is `raw_summary` one of them, or is it an ungated energy read that text 8 or amendment 51 must close?

**Packet** (absolute, under `/Users/edr/code/JouleWise-wt-bk-92472459/docs/process_traces/`):
- Amendment 51 as it stands: `2026-09-26-activation-92472459/20-bfgs-s1/80-coldgate-r2/30-erratum/21-coldgate-fable-erratum-ruling.md` §10 (and §5 on RS-1/RS-5). Its first version, with the prototype and the 120-site count: `../21-coldgate-fable-ruling.md` §6 and §10.
- Text 8: `2026-09-26-activation-6bec2aa6/40-bfgs-consult/50-coldgate/30-addendum/21-coldgate-fable-addendum-ruling.md` §4 C.
- The seat's brief and report: `2026-09-26-activation-92472459/20-bfgs-s1/85-fix3/10-fix-brief.txt`, `11-seat-report.md`.

**Questions.**
- **Q1.** Rule how amendment 51 treats reads inside the authentication and reader functions themselves (a new class, a detector exemption, or something else), with exact text numbered as amendment 57 onward. Keep every read inventoried or state why not, and make the rule self-verifying so a new function cannot claim it by name alone.
- **Q2.** Is `BundleReader.raw_summary` (and any other `BundleReader` method returning energy-bearing content) gated as text 8 requires? List every public `BundleReader` method with whether it can return energy-bearing content and whether it passes through `metadata()` first. Find its production callers. If any is an ungated energy read, rule the closure (gate it, or show that every caller is gated and pin that) with test rows and their counterfactuals.
- **Q3.** Is anything else among the 120 reported sites of the same kind (a read that returns energy-bearing content with no gate first) that no class should admit? Execute the prototype yourself (the seat's scripts under `/tmp` if present, or the ruling's own).

Keep intact: custody is never a status; `joulewise/battery_float.py` and FT §E's excluded list byte-identical; the eight consumers do not import `battery_float`.

**Output.** End with the resumed fix-round-3 contents for amendment 51 and a 5-line plain summary for Ed (technical, no project grounding; gloss every internal id).

**Protocol.** A single non-interactive session: no background tasks, no subagents, every probe in the foreground. Edit no repository file. Scratch under `/tmp`. Write the ruling with the Write tool to `/Users/edr/code/JouleWise-wt-bk-92472459/docs/process_traces/2026-09-26-activation-92472459/20-bfgs-s1/90-coldgate-sweep/21-coldgate-fable-ruling.md`; ending before that file exists is a protocol failure. Budget: 40 minutes; mark anything not run as NOT EXECUTED.
