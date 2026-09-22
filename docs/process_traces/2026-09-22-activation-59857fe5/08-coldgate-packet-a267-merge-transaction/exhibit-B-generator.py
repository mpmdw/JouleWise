"""Exhibit B generator — verbatim controlling-authority extracts, located by anchor.

Every extract is cut from `git show <rev>:<path>` between two PRINTED anchor
strings (never a hand-typed line range) and printed with 1-based line numbers of
the file at that revision.  For each excerpt the generator prints the five
fields the cold-gate charter §4 requires of a bounded excerpt: source path,
immutable revision, exact line range, the proposition it addresses, and why
non-narrative primary evidence is unavailable.

    python3 exhibit-B-generator.py [repo_path] > exhibit-B-authorities.md
"""
import hashlib
import subprocess
import sys
from pathlib import Path

REPO = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
REV = "c8812172"                  # main; every document below landed at or before it
FEATURE_REV = "489b0953"
TRACE = "docs/process_traces/2026-09-22-activation-59857fe5"

DL = "docs/decision_log.md"
R14 = ("docs/process_traces/2026-09-22-activation-d9990b3c/"
       "01-coldgate-packet-a267-clock-discipline-anchor/14-coldgate-fable-rebuttal-ruling.md")
A269 = ("docs/process_traces/2026-09-22-activation-e4b4ead6/"
        "03-coldgate-packet-a269-start-drift/10-coldgate-fable-ruling.md")
BRIEF = "docs/process_traces/2026-09-22-activation-e4b4ead6/06-a267-fix-round-1-brief.md"
FIXTURE = "tests/fixtures/qpe01_pilot_n1_20260922/exhibit-D-timed-log.txt"
D2 = f"{TRACE}/07c-exhibit-D2-timed-log-0210-0435-syslog.txt"
D3 = f"{TRACE}/07c-exhibit-D3-timed-log-zero-match-syslog.txt"

WHY = ("The cited text is itself the object of the question: the packet asks the judge "
       "to apply, amend or ratify these exact words. No non-narrative primary artifact "
       "states a ruling's or a brief's text; the code implements it but cannot evidence "
       "what was ordered.")


def show(rev, path):
    return subprocess.run(["git", "-C", str(REPO), "show", f"{rev}:{path}"],
                          capture_output=True, text=True, check=True).stdout


def find_one(lines, needle, start=0):
    hits = [index for index in range(start, len(lines)) if lines[index].startswith(needle)]
    if not hits:
        raise SystemExit(f"anchor {needle!r} not found")
    return hits[0]


def excerpt(label, rev, path, start_anchor, end_anchor, proposition, fence="text"):
    source = show(rev, path)
    lines = source.splitlines()
    first = find_one(lines, start_anchor)
    last = (find_one(lines, end_anchor, first + 1) - 1 if end_anchor is not None
            else first)
    while last > first and not lines[last].strip():
        last -= 1
    print(f"## {label}\n")
    print(f"- Source path: `{path}`")
    print(f"- Immutable revision: `{rev}` (file sha256 at that revision: "
          f"`{hashlib.sha256(source.encode()).hexdigest()}`)")
    print(f"- Exact line range: {first + 1}-{last + 1}")
    print(f"- Anchors: start = the single line beginning `{start_anchor}`; end = "
          + (f"the line before the next line beginning `{end_anchor}`"
             if end_anchor else "the same line"))
    print(f"- Proposition it addresses: {proposition}")
    print(f"- Why non-narrative primary evidence is unavailable: {WHY}\n")
    print(f"```{fence}")
    for index in range(first, last + 1):
        print(f"{index + 1:5d}  {lines[index]}")
    print("```\n")


print("# Exhibit B — controlling authorities (verbatim, anchor-located extracts)\n")
print("Generator output. Each extract is bounded by printed anchor strings and carries "
      "the five fields the charter requires of a bounded excerpt from a document whose "
      "own words are the object of a question. Nothing below is paraphrased.\n")

excerpt("B1 — D-138 (the merge-staging rule this transaction is built on)",
        REV, DL,
        "### D-138 — D-079-pinned estimator-input changes are merge-staged",
        "### D-138 implementation note",
        "Q1: whether a branch that changes a D-079-pinned estimator input may merge, "
        "and in what transaction shape.")

excerpt("B2 — A267 rebuttal ruling 14, R3 and R4 (the corpus-replay bar and the "
        "attestation argv this packet's Q2 and Q6 turn on)",
        REV, R14, "## R3 — Consult R2/R3 bars", "## R5 — Q3 corrections",
        "Q2 and Q6: the ruled `log show` argv (including `--style syslog`) and the "
        "twelve-envelope / 34-member replay requirements.")

excerpt("B3 — A269 cold ruling 10, Q1 (cure, with amendments A1 and A2)",
        REV, A269, "## Q1 — Cure.", "## Q2 — Registration.",
        "Q1 and Q7: the cure that fixes the 20 s inter-slot gap this packet's Q3 "
        "budgets, and the measured-not-budgeted standard the judge may apply.")

excerpt("B3b — A269 cold ruling 10, Q2 (the ruled registration v2 and the merge order)",
        REV, A269, "## Q2 — Registration.", "## Q3 — R6 precondition shape.",
        "Q1 and Q7: what registration v2 contains, and the ruled ordering "
        "constraint that both A267 Part 3 and A269 must be merged before any arm.")

excerpt("B4 — A269 cold ruling 10, Q3 (the replacement R6 clause) and Q4 "
        "(attestation mechanics i–iii)",
        REV, A269, "## Q3 — R6 precondition shape.", "## Q5 — Record correction.",
        "Q4 and Q7: what `window_epoch_s` was ruled to mean, and whether the re-run "
        "night is itself the live check.")

excerpt("B5 — Fix-round brief 06: WRITE_SCOPE and the Forbidden line",
        REV, BRIEF, "SESSION_MODE: delegated", "## Magistrate triage",
        "Q3 and Q5: the scope the fix-round seat was bound to, and the freeze on "
        "`joulewise/uncertainty_evidence.py` that makes the r7 estimator pin final.")

# Items 1, 2, 6 and 14 are each exactly one numbered line in the brief.
brief_source = show(REV, BRIEF)
brief_lines = brief_source.splitlines()
print("## B6 — Fix-round brief 06: items 1, 2, 6 and 14 (the dictated closure shapes "
      "this packet's Q2, Q3, Q4 and Q5 amend or ratify)\n")
print(f"- Source path: `{BRIEF}`")
print(f"- Immutable revision: `{REV}` (file sha256: "
      f"`{hashlib.sha256(brief_source.encode()).hexdigest()}`)")
print("- Anchors: each item is the single line beginning `N. ` under `## Items`; the "
      "line range of each is printed beside it.")
print("- Proposition it addresses: Q2 (item 2's header guard), Q3 (item 1's attestation "
      "bound), Q4 (item 14's window keys), Q5 (item 6's rewrite guard).")
print(f"- Why non-narrative primary evidence is unavailable: {WHY}\n")
print("```text")
for number in ("1. ", "2. ", "6. ", "14. "):
    index = find_one(brief_lines, number)
    print(f"{index + 1:5d}  {brief_lines[index]}")
    print()
print("```\n")

print("## B7 — First lines of the three saved log bodies (`repr`, exact bytes)\n")
print("- Sources: the fixture at `" + FEATURE_REV + "` and the two saved live-capture "
      "exhibits at `" + REV + "`'s successor bookkeeping head (tracked paths below).")
print("- Proposition it addresses: Q2 and Q6 — whether the guard's constant matches the "
      "header the ruled argv actually produces.")
print("- Why non-narrative primary evidence is unavailable: not applicable; these ARE "
      "primary artifacts. Their digests are printed in exhibit C3.\n")
print("```python")
fixture_text = show(FEATURE_REV, FIXTURE)
print(f"# {FIXTURE} @ {FEATURE_REV}")
print(f"{fixture_text.splitlines()[0]!r}")
for path in (D2, D3):
    text = (REPO / path).read_text()
    print(f"\n# {path}")
    print(f"{text.splitlines()[0]!r}")
print("```")
