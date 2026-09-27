# Cold gate BFGS-S1-R2-01, erratum: the paired refuter's RB-1, RS-1 to RS-5 and RN-1 to RN-4 against amendments 49–54

You are a COLD judge: a fresh session with no loop context. Do not read RUN_STATE.md, TASK_QUEUE.md, CLAUDE*.md, AGENTS.md, the decision log, or memory or skill files. **Write the contamination disclosure first.**

**Your working tree** is detached @ `49d77c74` (S1: round 2 plus fix round 2). No one will move it during your session.

**Why you are convened.** A cold Fable instance ruled BFGS-S1-R2-01 and wrote amendments 49–54. The paired Opus contract refuter agrees with it on every question, and then reports **one BLOCKER**, five SHOULD-FIXes and four NITs against it. Every item touches ruled text, so it comes to a cold judge as an erratum. The magistrate has not adjudicated them.
- **RB-1 (BLOCKER, amendment 49(c)):** a deleted or altered quarantined bundle does not raise custody on the production path. Supersession validation returns False, the bundle id resolves `ambiguous`, and the verdict row is written `failed` with a condition string; in `inputs.py` the member gets a refusal reason. Custody becomes a status. R49-3 builds the resolution by hand, so it cannot see this. The refuter proposes separating record validity from quarantine custody (rows R49-3b, R49-3c, R49-7b at production call sites). It established this by reading the code, not by running a full campaign.
- **RS-1 (51(d)):** the ruling's own sweep prototype is silent when a gate is swallowed by `try/except Exception`, under `contextlib.suppress`, or when the read sits in the `except` handler.
- **RS-2 (52):** `joulewise/analysis_manifest_v3.py:3712` and `:4499` still convert the gate's exceptions into finalization refusals; that file is outside S1's WRITE_SCOPE (add by name, or register a lane).
- **RS-3 (53(b), `inputs.py:3133`, 49(b)3/(e)):** member lists still come from the disk; a recorded finalized member that was deleted becomes `bundle_missing` rather than custody.
- **RS-4:** the premise "a supersession is recorded only after collection" misses the rerun's own final analysis (the operator workflow is quarantine, rerun, record); proposed: no claim licence for a member id the log records more than once. Not executed.
- **RS-5 (51(c)):** `BundleReader(a).metadata()` followed by a raw read of `BundleReader(b)` counts as gated; bind the gate to the same reader.
- **RN-1..RN-4:** R50-8's marker count (six, not five); 49(f)'s safety reason; `non_claim` (ii) rows checked against where their output goes; a round-F warning about all-simulated campaigns driven through final analysis.

**Packet** (absolute, under `/Users/edr/code/JouleWise-wt-bk-92472459/docs/process_traces/2026-09-26-activation-92472459/20-bfgs-s1/80-coldgate-r2/`): `00-charge.md` (the original charge and its packet), `21-coldgate-fable-ruling.md` (the ruling under review), `11-opus-contract-refuter.md` (Section A = independent answers; Section B = the findings with replacement texts). Probes: `/tmp/oc2/` (q2.py, q1b.py, sweep4.py, sweep_holes.py, gate_try.py).

**Rule.** For each finding: UPHOLD or REJECT; executed evidence (for RB-1 and RS-3, drive the real production path, not a hand-built resolution, and say so if you cannot); the exact text change. Then **restate amendments 49–54 in full as they stand after your rulings, plus any new amendment (55 onward)**, each self-contained with test rows and production call sites, and restate **the S1 order of remaining work** (fix round 3 contents; round F; anything that becomes its own lane). Keep intact: custody is never a status; authentication precedes every exclusion decision; `joulewise/battery_float.py` and FT §E's excluded list byte-identical; the eight consumers do not import `battery_float`.

**Output.** End with a 5-line plain summary for Ed (technical, no project grounding; gloss every internal id).

**Protocol.** A single non-interactive session: no background tasks, no subagents, every probe in the foreground. Edit no repository file. Scratch under `/tmp`. Write the ruling with the Write tool to `/Users/edr/code/JouleWise-wt-bk-92472459/docs/process_traces/2026-09-26-activation-92472459/20-bfgs-s1/80-coldgate-r2/30-erratum/21-coldgate-fable-erratum-ruling.md`; ending before that file exists is a protocol failure. Budget: 50 minutes; mark anything not run as NOT EXECUTED.
