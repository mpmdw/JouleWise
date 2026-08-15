#!/usr/bin/env python3
"""Mechanical assembly of the WO-MARGIN-RECORDER-AUTHZ recorder-race cold-gate packet.

NON-AUTHOR ASSEMBLY per the standing protocol adopted in
docs/process_traces/2026-08-15-m2-coldgate/composed-verdict.md section 4: the magistrate is a
reviewed party here (its round-1 fix is under review and its round-2 proposal is a submission),
so an Opus mechanic assembles the packet and commits this script beside it.

Every primary below is extracted by rule (heading span, git show, fixed line count, JSON key
selection). No primary is hand-typed. Anomalies are detected mechanically and emitted into
packet-index.md so there are no silent gaps (the M-2 gate's B1 defect class).

Usage:  python3 docs/process_traces/2026-08-15-recorder-race-coldgate/assemble.py
Writes: packet.md, packet-index.md in this script's directory.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SCRATCH = Path(
    "/private/tmp/claude-501/-Users-edr-code-JouleWise/"
    "e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad"
)
BRANCH = "impl/wo-margin-recorder-authz"

REVIEW = SCRATCH / "sol-recorder-review.md"
DELTA = SCRATCH / "sol-recorder-delta.md"
PROPOSAL = SCRATCH / "recorder-round2-proposal.md"
LEDGER = REPO / "docs/contracts/calibration_ledger.md"
DECLOG = REPO / "docs/decision_log.md"

anomalies: list[str] = []


def note(text: str) -> None:
    anomalies.append(text)


def fence(body: str) -> str:
    """Wrap body in a code fence longer than any backtick run it contains."""
    longest = max((len(m) for m in re.findall(r"`+", body)), default=0)
    bar = "`" * max(3, longest + 1)
    return f"{bar}\n{body.rstrip()}\n{bar}"


def span(path: Path, start_re: str, stop_re: str, *, to_eof_ok: bool = True) -> tuple[str, int, int]:
    """Lines from the first match of start_re up to (excluding) the next match of stop_re."""
    lines = path.read_text().splitlines()
    start = next((i for i, ln in enumerate(lines) if re.match(start_re, ln)), None)
    if start is None:
        sys.exit(f"FATAL: start pattern {start_re!r} not found in {path}")
    stop = next((i for i in range(start + 1, len(lines)) if re.match(stop_re, lines[i])), None)
    if stop is None:
        if not to_eof_ok:
            sys.exit(f"FATAL: stop pattern {stop_re!r} not found in {path}")
        stop = len(lines)
    return "\n".join(lines[start:stop]).rstrip(), start + 1, stop


def json_envelope(path: Path) -> dict:
    """Parse the leading ```json ... ``` report envelope."""
    m = re.search(r"^```json\n(.*?)^```", path.read_text(), re.S | re.M)
    if not m:
        sys.exit(f"FATAL: no leading json envelope in {path}")
    return json.loads(m.group(1))


def git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(REPO), *args], check=True, capture_output=True, text=True
    ).stdout


# ---------------------------------------------------------------- primaries

# P1 - original review finding F1 + the "Other attack lines passed" list that closes it.
#      Extraction rule: the "### F1" heading span, terminated by the next level-2 heading.
p1, p1_a, p1_b = span(REVIEW, r"^### F1 ", r"^## ")
review_env = json_envelope(REVIEW)
p1_head = review_env["workspace"]["head_end"]
if "Other attack lines passed" not in p1:
    note("P1: the 'Other attack lines passed' list did NOT fall inside the F1 heading span; "
         "the extraction rule may no longer match the source layout.")
if str(SCRATCH) in p1:
    note("P1: the review's line citations point at a TEMPORARY review checkout under the "
         f"session scratchpad ({SCRATCH}/review-recorder/...), not at repository paths. Those "
         "links are not resolvable from the repo; the corresponding repo file is "
         "joulewise/window_duration_margins.py on " + BRANCH + ".")

# P2 - the fix-round-1 commit, whole (message + diff).
head = git("rev-parse", BRANCH).strip()
subject = git("log", "-1", "--format=%s", head).strip()
if not subject.startswith("Fix round 1 (review F1)"):
    note(f"P2: {BRANCH} HEAD subject is {subject!r}, which does not start with "
         "'Fix round 1 (review F1)'. The branch may have advanced since assembly.")
p2 = git("show", "--format=fuller", "--find-renames", head).rstrip()
p2_parent = git("rev-parse", f"{head}^").strip()
if p2_parent != p1_head:
    note(f"P1/P2 CHAIN: the original review's reviewed head ({p1_head}) is not the parent of the "
         f"fix-round-1 commit ({p2_parent}). The fix may not sit directly on the reviewed code.")

# P3 - delta re-audit: verdict envelope (decision + F1 + flags) and the prose sections.
env = json_envelope(DELTA)
p3_json = json.dumps(
    {k: env[k] for k in ("status", "completion", "summary", "verdict", "flags") if k in env},
    indent=2,
)
p3_findings, p3f_a, p3f_b = span(DELTA, r"^## Findings", r"^## ")
p3_residual, p3r_a, p3r_b = span(DELTA, r"^## Residual risk", r"^## ")
if env.get("completion") != "complete":
    note(f"P3: the delta re-audit is completion={env.get('completion')!r} - it is NOT a complete "
         "audit. Its own confirming mutation (V5, guard removal) was sandbox-blocked and "
         "reported not_run.")
for fl in env.get("flags", []):
    if fl.get("level") == "blocking":
        note(f"P3: delta flag {fl.get('id')} is BLOCKING ({fl.get('kind')}): {fl.get('text')}")

# P4 - the magistrate's round-2 proposal, in full, as the reviewed party's submission.
p4 = PROPOSAL.read_text().rstrip()

# P5 - threat-model primary: the ledger contract's opening statement of what it does NOT defend.
LEDGER_LINES = 10
p5 = "\n".join(LEDGER.read_text().splitlines()[:LEDGER_LINES]).rstrip()
note(f"P5 is a HAND-SPECIFIED WINDOW: the first {LEDGER_LINES} lines of "
     "docs/contracts/calibration_ledger.md, chosen by the assembly order, not by a heading rule. "
     "It is an excerpt of a longer contract; the pairing should read the full file if the "
     "trusted-writer boundary is load-bearing to its ruling.")

# P6 - the adoption ruling: decision_log entry span, heading to next level-3 heading.
p6, p6_a, p6_b = span(DECLOG, r"^### WO-MARGIN-RECORDER-AUTHZ contract ADOPTED", r"^### ")
if "M-2 GATE AMENDMENT" in p6:
    note("P6: the WO-MARGIN-RECORDER-AUTHZ decision-log entry has an 'M-2 GATE AMENDMENT' block "
         "appended INSIDE it that concerns a different instrument (the M-2 draft_status "
         "override), not this work order. It is reproduced verbatim because the entry has no "
         "internal heading to cut at - it is NOT part of the recorder authorization ruling.")

declog_rel = "docs/decision_log.md"

# S1 - MECHANIC-ADDED SUPPLEMENT, beyond the six-primary assembly order. PRIMARY 1 convicts the
#      code on "the F2 threat table's required other-spec refusal", and that table is the
#      instrument's own enumeration of required results - it bears directly on gate question (i).
#      Attached rather than left as a dangling citation; declared as an addition in the index.
CONSULT = REPO / "docs/process_traces/2026-08-15-recorder-authz-consult/consult.md"
s1, s1_a, s1_b = span(CONSULT, r"^### F2 ", r"^### ")
note("SUPPLEMENT S1 IS A MECHANIC ADDITION beyond the six-primary assembly order: the F2 threat "
     f"table from {CONSULT.relative_to(REPO)} lines {s1_a}-{s1_b}. Reason: PRIMARY 1 convicts the "
     "code against this table, which the order did not attach. Extracted by heading span, not "
     "hand-picked rows.")

# ---------------------------------------------------------------- packet

packet = f"""# RECORDER-RACE COLD-GATE PACKET — WO-MARGIN-RECORDER-AUTHZ

Mechanically assembled 2026-08-15 by an Opus mechanic (NON-AUTHOR assembly per
`docs/process_traces/2026-08-15-m2-coldgate/composed-verdict.md` section 4 — the magistrate is a
reviewed party: its round-1 fix is under review and its round-2 design is a submission below).
The extraction script is committed beside this file as `assemble.py`; every primary is a scripted
extraction. There is no mechanic prose in the primaries and no magistrate prose anywhere except
inside PRIMARY 4, which is explicitly labeled as the reviewed party's submission.

**Rule-11 trigger:** second fix round on the same defect class (symlink/aliasing of the governed
extraction-spec grant). Round 2 has NOT been implemented; this gate sits before it.

## THE QUESTION FOR THE PAIRING

1. **Threat model and severity.** Is the check-to-grant race (a concurrent local writer
   retargeting the selected extraction-spec path between the resolution-invariance guard and the
   grant) inside the instrument's threat model? Is `blocker` the correct severity, or should it
   be recorded should-fix with the closure landing as defense-in-depth?
2. **Closure soundness.** Is the reviewed party's proposed content-binding closure (PRIMARY 4
   step 2: pre-grant `O_RDONLY|O_NOFOLLOW` read + hash-vs-pin refusal) sound? Is the fd-identity
   alternative (`st_dev`/`st_ino` before grant, re-stat after read) better? Is a third shape
   better than either?
3. **License or redirect.** License the second fix round with an EXACT specification, or order a
   different shape (including "no code change; record the residual and close").

## PRIMARY 1 — original Sol review, finding F1 + closing "Other attack lines passed"

Source: `sol-recorder-review.md` (session scratchpad), lines {p1_a}-{p1_b}, verbatim.
Reviewed head: `{p1_head}` (pre-fix; the parent of PRIMARY 2).

{fence(p1)}

## PRIMARY 2 — fix round 1, the commit under review (verbatim `git show`)

Source: `git -C <repo> show --format=fuller --find-renames {head}` on `{BRANCH}`.
Parent (the reviewed pre-fix head): `{p2_parent}`.

{fence(p2)}

## PRIMARY 3 — Sol delta re-audit of fix round 1

Source: `sol-recorder-delta.md` (session scratchpad). Part (a) is the report envelope's
`status`/`completion`/`summary`/`verdict`/`flags` keys, emitted by `json.dumps` from the parsed
envelope — the F1 finding and the audit's own completeness flags travel together deliberately.
Parts (b) and (c) are verbatim heading spans (lines {p3f_a}-{p3f_b} and {p3r_a}-{p3r_b}).

### (a) verdict envelope

{fence(p3_json)}

### (b) Findings section, verbatim

{fence(p3_findings)}

### (c) Residual risk section, verbatim

{fence(p3_residual)}

## PRIMARY 4 — REVIEWED PARTY'S SUBMISSION: the magistrate's round-2 proposal

Source: `recorder-round2-proposal.md` (session scratchpad), in full, verbatim.
**This is the design under adjudication, not evidence.** It is the reviewed party's own
statement of both the proposed closure and the severity question. The pairing owes it no
deference; the alternative it names, and any shape it does not name, are equally open.

{fence(p4)}

## PRIMARY 5 — threat-model primary (docs/contracts/calibration_ledger.md, first {LEDGER_LINES} lines)

Verbatim excerpt. This is the contract text PRIMARY 4 cites (line 3) for the trusted-writer
boundary that governs question 1.

{fence(p5)}

## PRIMARY 6 — the adoption ruling that defines the violated boundary

Source: `{declog_rel}`, lines {p6_a}-{p6_b}, verbatim — the entry span from its heading to the
next entry heading. Clause 1's "Never granted: ... the other floor pack's spec" is the boundary
both review rounds test against. See the index for what is and is not part of this ruling.

{fence(p6)}

## SUPPLEMENT S1 (MECHANIC ADDITION, not in the assembly order) — the F2 threat table

Source: `{CONSULT.relative_to(REPO)}` lines {s1_a}-{s1_b}, `^### F2 ` heading span, verbatim.
PRIMARY 1 convicts the code against "the F2 threat table's required other-spec refusal" but the
assembly order did not attach that table. It is the instrument's own enumeration of required
results and bears directly on question 1. Attached by the mechanic and declared as an addition;
the pairing may disregard it.

{fence(s1)}
"""

(HERE / "packet.md").write_text(packet)

# ---------------------------------------------------------------- index

index = f"""# PACKET INDEX — recorder-race cold gate (WO-MARGIN-RECORDER-AUTHZ)

Assembled by `assemble.py` in this directory (non-author assembly; run it to regenerate).
Repo head at assembly: `{git("rev-parse", "HEAD").strip()}`; reviewed branch `{BRANCH}` at
`{head}`.

## Contents and what each primary is FOR

| # | Primary | Source + extraction rule | What it is FOR |
|---|---------|--------------------------|----------------|
| 1 | Review F1 + "Other attack lines passed" | `sol-recorder-review.md` lines {p1_a}-{p1_b}; `^### F1 ` heading span to next `^## ` | Establishes the ORIGINAL defect class (grant escapes the selected-path boundary via aliasing) and, critically, the NEGATIVE space: the attack lines that already pass, so the pairing can see what round 2 must not regress. |
| 2 | Fix round 1 commit | `git show --format=fuller {head[:7]}` | The code actually under review — the resolution-invariance guard and its regression. Lets the pairing judge round 1 on the diff rather than on either party's description of it. |
| 3 | Delta re-audit verdict, F1, residual risk | `sol-recorder-delta.md`: envelope keys `status`/`completion`/`summary`/`verdict`/`flags`, plus verbatim `## Findings` and `## Residual risk` spans | The independent finding that round 1 left a check-to-grant race — i.e. the second fix round's justification. The `flags` key is included so the pairing sees that this audit is `completion={env.get('completion')!r}` with a BLOCKING verification gap, rather than reading its REJECT as fully demonstrated. |
| 4 | Magistrate round-2 proposal | `recorder-round2-proposal.md`, full file | The design under adjudication (content-binding closure + fd-identity alternative + the reviewed party's own severity framing). LABELED as the reviewed party's submission; it is the thing to be ruled on, not evidence for it. |
| 5 | Threat-model primary | `docs/contracts/calibration_ledger.md`, first {LEDGER_LINES} lines | The contract's own statement that it "does not defend against a malicious trusted writer". This is the text that decides question 1 (is a concurrent local adversary in-model), and therefore whether `blocker` is the right severity. |
| 6 | Adoption ruling | `{declog_rel}` lines {p6_a}-{p6_b}, heading span | The boundary the defect violates: clause 1's exhaustive never-granted list and the narrower-than-mint invocation shape; clause 2's "no change to `joulewise/authentication_io.py` or any public API", which is the constraint PRIMARY 4 designs around. Fixes the question of what round 2 is even allowed to touch. |
| S1 | F2 threat table (MECHANIC ADDITION) | `{CONSULT.relative_to(REPO)}` lines {s1_a}-{s1_b}, `^### F2 ` heading span | The required-result table PRIMARY 1 convicts the code against, which the assembly order left as a dangling citation. It is the closest thing the instrument has to a written threat enumeration, so it is second evidence on question 1 alongside PRIMARY 5. |

## Flagged gaps, hand-selections, and anomalies

No silent gaps. Everything below was detected or declared during assembly:

{chr(10).join(f"{i}. {a}" for i, a in enumerate(anomalies, 1)) if anomalies else "(none)"}

## Deliberate scope limits of this packet (mechanic's declaration)

- **Not attached:** the WO-MARGIN-RECORDER-AUTHZ consult trace
  (`docs/process_traces/2026-08-15-recorder-authz-consult/`), which PRIMARY 6 names as the ONE
  home for the mechanism detail, and the current text of
  `joulewise/window_duration_margins.py`. Both are in the repo and readable by the seats; the
  assembly order enumerated six primaries and this script attaches exactly those six. The
  pairing should read the live file before licensing an exact specification.
- **Attached beyond the order:** the F2 threat table (SUPPLEMENT S1) — see the anomaly list.
  Nothing else was added.
- **Round 2 is unimplemented.** There is no round-2 diff to attach; PRIMARY 4 is a design
  statement, and the gate sits BEFORE the implementation by rule-11 order.
- **The mechanic did not verify any claim in any primary.** This is an assembly record. The
  seats verify against the live repo.
"""

(HERE / "packet-index.md").write_text(index)

print(f"wrote {HERE/'packet.md'} ({len(packet)} bytes)")
print(f"wrote {HERE/'packet-index.md'} ({len(index)} bytes)")
print(f"branch head {head} | anomalies flagged: {len(anomalies)}")
for a in anomalies:
    print(f"  - {a[:110]}")
