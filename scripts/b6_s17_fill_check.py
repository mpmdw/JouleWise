#!/usr/bin/env python3
"""RL-134 item 9: the three-point mechanical check of PR #748's fill (runbook step 3).

    b6_s17_fill_check.py check [--repo DIR] [--rev REV | --filled-dir DIR] [--base REV] [--s14 HEX]
                               [--entry-date YYYY-MM-DD] [--pin-request REV] [--python PY]
                               [--ignore-path PATH ...] [--allow-blanks] [--mapping-report FILE] [--require-r7]
    b6_s17_fill_check.py fill-cut --s14 HEX --pin-request-commit HEX [--repo DIR] [--filled-dir DIR]
    b6_s17_fill_check.py r7-text --mapping-report FILE --date YYYY-MM-DD [--apply] [--repo DIR] [--filled-dir DIR]

`check` runs on the filled text: the registration `docs/registrations/block6_replication_DRAFT.md` and the
addendum `docs/registrations/block6_freeze_by_commit_addendum.md`, read from `--rev`, from `--filled-dir`
(a directory holding them at their repository paths), or from the working tree of `--repo` (default).

  Point 1 (scope). Every filled span is taken back to the text it replaced (the three OPEN markers S-14-PIN,
    R3-TABLE and R12-FULLSIZE-N, the 20 LOW 5 date stamps, the three LOW 6 pointers, the addendum's
    `b6/analysis` row, S-16 (§14's S-16 row and the §17-S16 line of RL-140 A4, taken back before LOW 5) and,
    if filled, OPEN[R7-SESSION-INDEX]). The result must equal the base (`27b6cacfd`)
    byte for byte, and no other file may differ from the base (`--ignore-path` names exceptions).
  Point 2 (values). Each filled value equals git at the S-14 commit: `git rev-parse` for the commit, its tree
    and the `b6/analysis` tag object; `shasum -a 256` of `git show <S14>:<path>` for the four pinned files
    and the R3 generator; the generator's stdout (run with `-I -B` on a `git archive` of the S-14 commit) for
    the stdout SHA-256 and the "Keys covered" line. R12-FULLSIZE-N equals the number of full roots in the
    pin request's section 3a. Every entry date equals `--entry-date` (default: today, local). The §17-S16
    line's commit token resolves to a commit whose `scripts/b6_s16_block5_pstar.py` is byte-identical to
    `bc62db137`'s (RL-140 A4).
  Point 3 (R3 slot). The R3 stdout SHA-256 in the fill equals the pin request's section 2c slot.

A `⟨CUT: …⟩` blank is reported, never guessed. With `--allow-blanks` a text whose only gaps are blanks exits
3 ("staged"); `--s14` then lets the file and generator values be checked against a candidate commit.
OPEN[R7-SESSION-INDEX] (RL-134 item 9, second paragraph) is reported as open or, if filled, checked against
`--mapping-report` (b6_mapping_build.py's report: its r7 statements and digest); `--require-r7` fails on open.

`fill-cut` writes the four cut blanks (commit, tree, tag object, pin request commit) from git, after step 1.
`r7-text` prints, or with `--apply` writes, the R7 fill from the mapping report's three statements.

Exit: 0 pass; 3 staged (blanks only, `--allow-blanks`); 1 a point fails; 2 usage. Standard library only.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

REG = "docs/registrations/block6_replication_DRAFT.md"
ADD = "docs/registrations/block6_freeze_by_commit_addendum.md"
PIN_REQUEST_PATH = "docs/run_reports/2026-11-13-b6-s14-pin-request.md"
DEFAULT_PIN_REQUEST = "origin/docs/2026-11-13-b6-s14-pin-request"
BASE = "27b6cacfd"
OLD_DATE = "2026-11-12"
PREDECLARED_R3_STDOUT = "1003d87e7b92bc28a38890d75860e0ea0e47ae65862e6d6dd09641d7b3f29840"  # b5ab6a71d
S16_REVIEWED = "bc62db137"  # RL-140 A4: the commit the research lead read
S16_PSTAR = "scripts/b6_s16_block5_pstar.py"
# RL-140 A4's §17-S16 line, verbatim, with its two commit tokens as {S16C} and its entry date as {DATE}.
S16_LINE = (
    "\n- {DATE}, §17-S16 (RL-134 item 17, RL-140). **Kind.** Slot fill: S-16, Block 5's half. Read after t"
    "he Block 5 release (2026-11-08, `RUN_STATE.md` item 231), from Block 5's 3 usable sessions (`v5-b5-a"
    'lpha-a1-20261009T2312Z`, `v5-b5-beta-a6-20261011T2011Z`, `v5-b5-gamma-a1-20261012T0420Z`; 357 runs: '
    '280 science, 77 auxiliary). Counts from the released flags, rosters and exclusion lists, by `scripts'
    "/b6_s16_block5_replay_counts.py` @ `{S16C}`, under Block 5's catalog `5d77c725…` and Block 6's `b5bc"
    "e6c6…`. The desk exclusion from each run's idle-baseline rails, by `scripts/b6_s16_block5_pstar.py` "
    '@ `{S16C}`. Per-pack counts are ALPHA, BETA, GAMMA. **Rules that became flags (counted).** Block 6 t'
    "urns 5 run codes and 25 session codes into flags and drops GAMMA's lost-midpoint rule. As flags they"
    ' remove nothing. Of the 5 run codes only `contention.request_overlap` fired in Block 5: 28 runs (4, '
    '14, 10; 18 science). Block 5 removed all 28, and none carries a code that still removes it. Over Blo'
    "ck 5's flags, Block 6's catalog removes 11 runs (2, 4, 5) where Block 5 removed 39 (6, 18, 15). The "
    '25 session codes fired in 0 of 3 sessions. The midpoint was lost in 0 of 1 GAMMA sessions. `idle.wai'
    'ted`: 0; Block 5 had no waiting admission. **Derived, not read.** The clock-rate hold (14.675 ppm) h'
    "olds 0 of 3: each session was armed under Block 5's gate, |f| ≤ 3.6306 ppm (B5-REG §4.2), and none c"
    'arries `clock.arm_unmeasured`. The b_op stop (139 ms, ALPHA and GAMMA; §8.2 P3) stops 0 of 2: each s'
    'ession is claim-usable, so its smallest target phase passed the unchanged phase check, which every r'
    "un fails above the line (§8.6 S-5), and Block 6's s_bracket is smaller than Block 5's. **Replayed on"
    ' its input.** The desk exclusion at P* (§8.3 item 3, S-9), by the pinned `desk_hazards` (`b5ab6a71d`'
    ") with Block 6's registered line per pack and phase: removes 0 of 357 runs (0, 0, 0); largest baseli"
    'ne mean 1.11 mW against the lowest line 0.0723 W. The rule applies to science runs. 272 of the 280 w'
    'ere examined (98, 98, 76); the other 8 (2, 2, 4) failed, and Block 5 had already removed them. The f'
    "unction also reads each run's status, model name and request span, and the contention journal; its c"
    'ontention result is not reported. **Not replayed.** (a) Grounds N, W, D, S and the pre-check hold (§'
    '8.2 N1, N2, W1, W2, W3, D1, S1; `precheck.certain_exclusion`): no replay is owed and none stands bes'
    'ide them from the rehearsals; the nearest Block 5 codes (`calibration.no_bracket`, `calibration.capt'
    'ure_invalid`, `neg8.bound_not_derived`, `model.identity_mismatch`, `code.executed_differs_from_seale'
    'd`, `neg8.screen_failed`) fired in 0 of 3 sessions. (b) Block 5 did not record the input: `sleep.in_'
    'run`; the agent rule (`agent.presence`, `agent.presence_overlap`, `agent.unit_overlap`), since Block'
    " 5 took no agent census and an agent's presence in it is unknown; the wait skips (`idle.wait_cap_ski"
    'p`, `idle.wait_budget_skip`), since Block 5 had no waiting admission and aborted 9 runs (2, 3, 4) at'
    " admission instead, a kept rule. (c) Contention's labelled alternative (C − k × 0.54 ≥ 0.0874 CPU-s)"
    ': not counted; it removes nothing in Block 6. The desk exclusion is the only excluding rule new in B'
    "lock 6 that was replayed on Block 5's runs by reading its input; the b_op stop is derived, and (a) a"
    'nd (b) were not replayed. Outside the pinned program; changes no Block 6 number.'
)

BLANK = {
    "S14": "⟨CUT: S-14 commit, 40 hex⟩",
    "TAG": "⟨CUT: b6/analysis tag object, 40 hex⟩",
    "TREE": "⟨CUT: S-14 tree, 40 hex⟩",
    "REQ": "⟨CUT: pin request commit at the cut, 40 hex⟩",
}
FILES = {"RC6": "scripts/independent_recompute_b6.py", "RC5": "scripts/independent_recompute_b5.py",
         "PREC": "configs/b6/recompute/precision.json",
         "KEYS": "configs/b6/recompute/production_comparison_keys.json", "GEN": "scripts/b6_r3_table.py"}
VALUE = {
    "S14": r"[0-9a-f]{40}", "TAG": r"[0-9a-f]{40}", "TREE": r"[0-9a-f]{40}", "REQ": r"[0-9a-f]{40}",
    "RC6": r"[0-9a-f]{64}", "RC5": r"[0-9a-f]{64}", "PREC": r"[0-9a-f]{64}", "KEYS": r"[0-9a-f]{64}",
    "GEN": r"[0-9a-f]{64}", "R3OUT": r"[0-9a-f]{64}", "R7SHA": r"[0-9a-f]{64}",
    "KEYSLINE": r"Keys covered: \d+ of \d+; \d+ groups; UNSTATED groups: \d+\.",
    "N": r"\d", "DATE": r"\d{4}-\d{2}-\d{2}", "R7DATE": r"\d{4}-\d{2}-\d{2}",
    "S1": r"[a-z0-9 -]+", "S2": r"[a-z0-9 ,-]+", "S3": r"[a-z0-9 -]+",
    "S16C": r"[0-9a-f]{9,40}",
}

# (file, filled template, base text, allowed match counts). Templates equal the staged fill byte for byte;
# {NAME} is a value (or its ⟨CUT⟩ blank).
SPANS = [
    (REG, "**Filled {DATE} (§17-R4; the S-14 pin, RL-129 and RL-134):** commit `{S14}`, annotated tag "
          "`b6/analysis` (tag object `{TAG}`); SHA-256 of `scripts/independent_recompute_b6.py` `{RC6}`, of "
          "`scripts/independent_recompute_b5.py` `{RC5}`, of `configs/b6/recompute/precision.json` `{PREC}`, of "
          "`configs/b6/recompute/production_comparison_keys.json` `{KEYS}`. The 24-file closure with every SHA-256 "
          "is section 2 of the pin request, `docs/run_reports/2026-11-13-b6-s14-pin-request.md` @ `{REQ}`",
     "OPEN[S-14-PIN: commit, tag, sha256 of scripts/independent_recompute_b6.py, sha256 of "
     "scripts/independent_recompute_b5.py = d49103e8...a2e4e0, sha256 of precision.json and "
     "production_comparison_keys.json]", {1}, "S-14-PIN"),
    (REG, "the stdout of `scripts/b6_r3_table.py` (SHA-256 `{GEN}`) at the S-14 commit `{S14}`\n"
          "  (`python3.13 -I -B scripts/b6_r3_table.py` on a `git archive` of that commit), stdout SHA-256 "
          "`{R3OUT}`, the pin request's slot and the same bytes as its generation at `b5ab6a71d`; \"{KEYSLINE}\"; "
          "printed in `docs/run_reports/2026-11-12-b6-r3-table.md` at that commit. Each key group's producer and "
          "label, the dominance and lines groups included, is that table's row",
     "OPEN[R3-TABLE: producer and label for the dominance and lines key groups;\n  filled at the S-14 pin]",
     {1}, "R3-TABLE"),
    (REG, "{N} of 3 packs, on single-pack roots, per host", "OPEN[R12-FULLSIZE-N] of 3 packs", {1},
     "R12-FULLSIZE-N"),
    (REG, "R7-SESSION-INDEX, filled {R7DATE} from the copy's `attempts.jsonl` by `scripts/b6_mapping_build.py` "
          "(`mapping-report.json` SHA-256 `{R7SHA}`; structure only): order of the three: {S1}; relative to "
          "`r1-gamma`: {S2};\n  t0 order of the nine: {S3}",
     "OPEN[R7-SESSION-INDEX: the t0 order of `r2-beta`, `r2-gamma` and `r3-gamma` among themselves and relative "
     "to\n  `r1-gamma`; committed text on `main` does not give it]", {0, 1}, "R7-SESSION-INDEX"),
    (REG, "| block 5's L9 release tag plus the block-6 additions, reviewed and cold-passed; superseded through "
          "§17-R1 and §17-R4: the analysis commit is the S-14 pin recorded in this row |",
     "| block 5's L9 release tag plus the block-6 additions, reviewed and cold-passed |", {1}, "LOW 6"),
    (REG, "`OPEN[S-14]`, filled: §14 row S-14 and §17-R1", "`OPEN[S-14]`", {2}, "LOW 6"),
    # S-16 (RL-134 item 17, RL-140 A1 and A4): §14's S-16 row and the appended §17-S16 line. The line span is
    # taken back before LOW 5's, so the line's own "\n- {DATE}, §17-" is not counted among LOW 5's 14 stamps.
    (REG, "block 5's usable sessions after its release (structure only): filled {DATE} (§17-S16) |",
     "block 5's usable sessions after its release (structure only) |", {1}, "S-16"),
    (REG, S16_LINE, "", {1}, "S-16"),
    (REG, "\n- {DATE}, §17-", "\n- " + OLD_DATE + ", §17-", {14}, "LOW 5"),
    (REG, "\n- {DATE}: the §17 entries", "\n- " + OLD_DATE + ": the §17 entries", {1}, "LOW 5"),
    (REG, "*Corrected {DATE} (§17-R1", "*Corrected " + OLD_DATE + " (§17-R1", {1}, "LOW 5"),
    (REG, "**Made definite {DATE} (§17-R2", "**Made definite " + OLD_DATE + " (§17-R2", {1}, "LOW 5"),
    (REG, "**Filled {DATE} (§17-R8", "**Filled " + OLD_DATE + " (§17-R8", {1}, "LOW 5"),
    (REG, "(entered in this file {DATE} under §17-R10", "(entered in this file " + OLD_DATE + " under §17-R10", {2},
     "LOW 5"),
    (ADD, "| `b6/analysis` | `{S14}` | `{TREE}` | cut at the S-14 pin (registration §14 row S-14, §17-R4), annotated "
          "tag object `{TAG}`; recorded {DATE} |",
     "| `b6/analysis` | UNRECORDED | UNRECORDED | later: S-14 is `OPEN` (`block6_replication_DRAFT.md:1207`; §13 "
     "line 1186). It is cut when the analysis commit is pinned before the blind dry run |", {1}, "addendum row"),
]


class Usage(Exception):
    pass


def git(repo, *args, binary=False, check=True):
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=False)
    if check and result.returncode != 0:
        raise Usage("git " + " ".join(args) + ": " + result.stderr.decode(errors="replace").strip())
    if result.returncode != 0:
        return None
    return result.stdout if binary else result.stdout.decode().strip()


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def template_regex(template):
    """Escape the template and turn each {NAME} into a numbered group matching a value or its blank."""
    parts, names, pos = [], [], 0
    for m in re.finditer(r"\{([A-Z0-9]+)\}", template):
        parts.append(re.escape(template[pos:m.start()]))
        name = m.group(1)
        alt = VALUE[name] + ("|" + re.escape(BLANK[name]) if name in BLANK else "")
        parts.append("(" + alt + ")")
        names.append(name)
        pos = m.end()
    parts.append(re.escape(template[pos:]))
    return re.compile("".join(parts)), names


def read_filled(args, path):
    if args.rev:
        return git(args.repo, "show", args.rev + ":" + path, binary=True).decode("utf-8")
    root = Path(args.filled_dir) if args.filled_dir else Path(args.repo)
    return (root / path).read_text(encoding="utf-8")


def unfill(texts):
    """Point 1's core: take every filled span back to its base text; collect the values and the span counts."""
    values, counts = {}, {}
    out = dict(texts)
    for path, template, original, allowed, label in SPANS:
        rx, names = template_regex(template)
        found = []

        def back(m, names=names, found=found):
            found.append([m.group(i + 1) for i in range(len(names))])
            return original

        out[path] = rx.sub(back, out[path])
        counts.setdefault(label, []).append((len(found), allowed))
        for row in found:
            for name, val in zip(names, row):
                values.setdefault(name, []).append(val)
    return out, values, counts


def first_differences(a, b, limit=5):
    la, lb = a.split("\n"), b.split("\n")
    diffs = [i + 1 for i in range(max(len(la), len(lb))) if (la[i] if i < len(la) else None) != (lb[i] if i < len(lb) else None)]
    return diffs[:limit], len(la), len(lb)


def generator_stdout(repo, commit, python):
    tmp = Path(tempfile.mkdtemp(prefix="b6-s17-fill-check-"))
    try:
        archive = git(repo, "archive", "--format=tar", commit, binary=True)
        subprocess.run(["tar", "-x", "-C", str(tmp)], input=archive, check=True)
        result = subprocess.run([python, "-I", "-B", "scripts/b6_r3_table.py"], cwd=str(tmp), capture_output=True,
                                check=False, stdin=subprocess.DEVNULL)
        if result.returncode != 0:
            return None, "generator exit " + str(result.returncode)
        return result.stdout, None
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def pin_request_text(repo, rev):
    data = git(repo, "show", rev + ":" + PIN_REQUEST_PATH, binary=True, check=False)
    return data.decode("utf-8") if data is not None else None


def section(text, start, end):
    i = text.find(start)
    j = text.find(end, i + 1) if i >= 0 else -1
    return text[i:j] if i >= 0 and j > i else None


def r3_slot(request):
    part = section(request, "### 2c.", "### 2d.")
    m = re.search(r"^\| Stdout SHA-256 \| `([0-9a-f]{64})`", part or "", re.M)
    return m.group(1) if m else None


def full_roots(request):
    part = section(request, "### 3a.", "### 3b.")
    packs = set(re.findall(r"^\| (ALPHA|BETA|GAMMA) ", part or "", re.M))
    return len(packs) if part else None


def check(args):
    out, status = [], {"fail": [], "blank": set()}
    texts = {p: read_filled(args, p) for p in (REG, ADD)}
    base = {p: git(args.repo, "show", args.base + ":" + p, binary=True).decode("utf-8") for p in (REG, ADD)}

    # ---- point 1
    unfilled, values, counts = unfill(texts)
    p1 = []
    for path in (REG, ADD):
        if unfilled[path] != base[path]:
            lines, na, nb = first_differences(unfilled[path], base[path])
            p1.append(path + " differs from " + args.base + " outside the fill (lines " + ",".join(map(str, lines))
                      + "; " + str(na) + " against " + str(nb) + " lines)")
    for label, rows in counts.items():
        for n, allowed in rows:
            if n not in allowed:
                p1.append(label + ": " + str(n) + " spans, expected " + "/".join(map(str, sorted(allowed))))
    if args.rev:
        changed = git(args.repo, "diff", "--name-only", args.base, args.rev).splitlines()
    elif not args.filled_dir:
        changed = git(args.repo, "diff", "--name-only", args.base, "--").splitlines()
        changed += git(args.repo, "ls-files", "--others", "--exclude-standard").splitlines()
    else:
        changed = []
    extra = sorted(set(changed) - {REG, ADD} - set(args.ignore_path or []))
    if extra:
        p1.append("other files differ from " + args.base + ": " + ", ".join(extra))
    spans = ", ".join(label + " x" + str(sum(n for n, _ in rows)) for label, rows in counts.items())
    out.append("point1 scope: " + ("pass" if not p1 else "fail") + " (" + spans + ")")
    out += ["  " + line for line in p1]
    if p1:
        status["fail"].append("point1")

    # ---- point 2
    p2, detail = [], []

    def one(name):
        vals = values.get(name, [])
        if not vals:
            return None
        if len(set(vals)) != 1:
            p2.append(name + " inconsistent across spans: " + ", ".join(sorted(set(vals))))
            return None
        v = vals[0]
        if name in BLANK and v == BLANK[name]:
            status["blank"].add(name)
            return BLANK[name]
        return v

    v = {name: one(name) for name in VALUE}
    s14 = v["S14"]
    if args.s14:
        args.s14 = git(args.repo, "rev-parse", "--verify", args.s14 + "^{commit}")
    if s14 == BLANK["S14"]:
        s14 = args.s14
    elif args.s14 and s14 != args.s14:
        p2.append("S14 in the text " + str(s14) + " is not --s14 " + args.s14)
    if s14:
        full = git(args.repo, "rev-parse", "--verify", "--quiet", s14 + "^{commit}", check=False)
        if full != s14 and v["S14"] != BLANK["S14"]:
            p2.append("S14 " + s14 + " is not a full commit id (git: " + str(full) + ")")
        s14 = full
    if not s14:
        p2.append("no S-14 commit to check against (fill it, or pass --s14 with --allow-blanks)")
    else:
        detail.append("S14 = " + s14 + (" (from --s14; the text holds the blank)" if v["S14"] == BLANK["S14"] else ""))
        tree = git(args.repo, "rev-parse", s14 + "^{tree}")
        tag_obj = git(args.repo, "rev-parse", "--verify", "--quiet", "refs/tags/b6/analysis", check=False)
        tag_commit = git(args.repo, "rev-parse", "--verify", "--quiet", "b6/analysis^{commit}", check=False)
        tag_type = git(args.repo, "cat-file", "-t", tag_obj, check=False) if tag_obj else None
        if v["TREE"] == BLANK["TREE"]:
            detail.append("TREE blank (git gives " + tree + ")")
        elif v["TREE"] != tree:
            p2.append("TREE " + str(v["TREE"]) + " != git " + tree)
        if v["TAG"] == BLANK["TAG"]:
            detail.append("TAG blank (git gives " + str(tag_obj) + ")")
        else:
            if v["TAG"] != tag_obj:
                p2.append("TAG " + str(v["TAG"]) + " != refs/tags/b6/analysis " + str(tag_obj))
            if tag_type != "tag":
                p2.append("b6/analysis is not an annotated tag (" + str(tag_type) + ")")
            if tag_commit != s14:
                p2.append("b6/analysis^{commit} " + str(tag_commit) + " != S14 " + s14)
        for name, path in FILES.items():
            got = sha256(git(args.repo, "show", s14 + ":" + path, binary=True))
            if v[name] != got:
                p2.append(name + " (" + path + ") " + str(v[name]) + " != shasum at S14 " + got)
        stdout, err = generator_stdout(args.repo, s14, args.python)
        if err:
            p2.append("R3 generator at S14: " + err)
        else:
            got = sha256(stdout)
            if v["R3OUT"] != got:
                p2.append("R3OUT " + str(v["R3OUT"]) + " != generator stdout at S14 " + got)
            keys = [ln for ln in stdout.decode("utf-8").splitlines() if ln.startswith("Keys covered:")]
            if keys != [v["KEYSLINE"]]:
                p2.append("KEYSLINE " + repr(v["KEYSLINE"]) + " != generator " + repr(keys))
            detail.append("R3 generator stdout at S14 " + got)
    if v["S16C"]:
        s16 = git(args.repo, "rev-parse", "--verify", "--quiet", v["S16C"] + "^{commit}", check=False)
        if not s16:
            p2.append("S16C " + v["S16C"] + " is not a commit in this repository")
        else:
            got = git(args.repo, "show", s16 + ":" + S16_PSTAR, binary=True, check=False)
            ref = git(args.repo, "show", S16_REVIEWED + ":" + S16_PSTAR, binary=True, check=False)
            if got is None or ref is None or got != ref:
                p2.append("S16C " + v["S16C"] + ": " + S16_PSTAR + " is not byte-identical to " + S16_REVIEWED
                          + "'s (RL-140 A4)")
            else:
                detail.append("S16C = " + s16 + " (" + S16_PSTAR + " byte-identical to " + S16_REVIEWED + ")")
    request_rev = v["REQ"] if v["REQ"] and v["REQ"] != BLANK["REQ"] else args.pin_request
    if v["REQ"] and v["REQ"] != BLANK["REQ"]:
        if git(args.repo, "rev-parse", "--verify", "--quiet", v["REQ"] + "^{commit}", check=False) != v["REQ"]:
            p2.append("REQ " + v["REQ"] + " is not a full commit id in this repository")
    elif v["REQ"] == BLANK["REQ"]:
        detail.append("REQ blank; pin request read from " + args.pin_request)
    request = pin_request_text(args.repo, request_rev)
    if request is None:
        p2.append("pin request " + PIN_REQUEST_PATH + " not found at " + request_rev)
    else:
        n = full_roots(request)
        if v["N"] is None or n is None or int(v["N"]) != n or n != 3:
            p2.append("R12-FULLSIZE-N " + str(v["N"]) + " != full roots in the pin request's section 3a (" + str(n)
                      + "), expected 3")
    dates = sorted(set(values.get("DATE", [])))
    if dates != [args.entry_date]:
        p2.append("entry dates " + ",".join(dates) + " != --entry-date " + args.entry_date)
    out.append("point2 values: " + ("fail" if p2 else "blanks " + ",".join(sorted(status["blank"]))
                                    if status["blank"] else "pass"))
    out += ["  " + line for line in p2] + ["  " + line for line in detail]
    if p2:
        status["fail"].append("point2")

    # ---- point 3
    slot = r3_slot(request) if request else None
    if slot is None:
        out.append("point3 r3_slot: fail (no Stdout SHA-256 row in the pin request's section 2c at " + request_rev + ")")
        status["fail"].append("point3")
    elif v["R3OUT"] != slot:
        out.append("point3 r3_slot: fail (fill " + str(v["R3OUT"]) + ", slot " + slot + ")")
        status["fail"].append("point3")
    else:
        out.append("point3 r3_slot: pass (" + slot + ", pin request at " + request_rev
                   + ("; equals the predeclared b5ab6a71d value" if slot == PREDECLARED_R3_STDOUT else
                      "; NOTE differs from the predeclared b5ab6a71d value " + PREDECLARED_R3_STDOUT) + ")")

    # ---- R7 (RL-134 item 9, second paragraph; not one of the three points)
    r7n = sum(n for n, _ in counts["R7-SESSION-INDEX"])
    if r7n == 0:
        out.append("r7: open (OPEN[R7-SESSION-INDEX] is filled from the nine's attempts.jsonl before the gate run)")
        if args.require_r7:
            status["fail"].append("r7")
    else:
        r7 = []
        if v["R7DATE"] != args.entry_date:
            r7.append("R7 date " + str(v["R7DATE"]) + " != --entry-date " + args.entry_date)
        if args.mapping_report:
            raw = Path(args.mapping_report).read_bytes()
            report = json.loads(raw)["r7"]
            st = report["open_statements"]
            if sha256(raw) != v["R7SHA"]:
                r7.append("mapping report SHA-256 " + sha256(raw) + " != fill " + str(v["R7SHA"]))
            for key, name in (("1_order_of_the_three", "S1"), ("2_relative_to_r1_gamma", "S2"),
                              ("3_t0_order_of_the_nine", "S3")):
                if st.get(key) != v[name]:
                    r7.append(name + " differs from the report's " + key)
            if not (report.get("stated_order_holds") and report.get("pairing_equals_r7") and report.get("nine_counting")):
                r7.append("the report departs from §17-R7 (comes to the research lead)")
        else:
            r7.append("filled, but no --mapping-report given to check it")
        out.append("r7: " + ("filled, equal to the mapping report" if not r7 else "departs"))
        out += ["  " + line for line in r7]
        if r7:
            status["fail"].append("r7")

    blanks = sorted(b for p in (REG, ADD) for b in re.findall(r"⟨CUT:[^⟩]*⟩", texts[p]))
    out.append("blanks: " + str(len(blanks)) + ("" if not blanks else " (" + "; ".join(sorted(set(blanks))) + ")"))
    if status["fail"]:
        out.append("fill-check: fail " + ",".join(status["fail"]))
        code = 1
    elif blanks:
        out.append("fill-check: " + ("staged" if args.allow_blanks else "fail blanks"))
        code = 3 if args.allow_blanks else 1
    else:
        out.append("fill-check: pass")
        code = 0
    print("\n".join(out))
    return code


def write_filled(args, path, text):
    root = Path(args.filled_dir) if args.filled_dir else Path(args.repo)
    (root / path).write_text(text, encoding="utf-8")


def fill_cut(args):
    s14 = git(args.repo, "rev-parse", "--verify", args.s14 + "^{commit}")
    req = git(args.repo, "rev-parse", "--verify", args.pin_request_commit + "^{commit}")
    tag = git(args.repo, "rev-parse", "--verify", "refs/tags/b6/analysis")
    if git(args.repo, "rev-parse", "b6/analysis^{commit}") != s14:
        raise Usage("b6/analysis does not point at " + s14)
    fill = {"S14": s14, "TREE": git(args.repo, "rev-parse", s14 + "^{tree}"), "TAG": tag, "REQ": req}
    for path in (REG, ADD):
        text = read_filled(args, path)
        for name, value in fill.items():
            text = text.replace(BLANK[name], value)
        write_filled(args, path, text)
    print("fill-cut " + " ".join(k + "=" + val for k, val in fill.items()))
    return 0


def r7_text(args):
    raw = Path(args.mapping_report).read_bytes()
    report = json.loads(raw)["r7"]
    st = report["open_statements"]
    template = SPANS[3][1]
    text = template.format(R7DATE=args.date, R7SHA=sha256(raw), S1=st["1_order_of_the_three"],
                           S2=st["2_relative_to_r1_gamma"], S3=st["3_t0_order_of_the_nine"])
    for name, val in (("S1", st["1_order_of_the_three"]), ("S2", st["2_relative_to_r1_gamma"]),
                      ("S3", st["3_t0_order_of_the_nine"])):
        if not re.fullmatch(VALUE[name], val):
            raise Usage("statement " + name + " has characters the check does not accept: " + repr(val))
    if not (report.get("stated_order_holds") and report.get("pairing_equals_r7") and report.get("nine_counting")):
        print("r7: departs from §17-R7; comes to the research lead before any run (RL-134 item 9)")
        return 1
    if args.apply:
        reg = read_filled(args, REG)
        if reg.count(SPANS[3][2]) != 1:
            raise Usage("OPEN[R7-SESSION-INDEX] marker not found exactly once")
        write_filled(args, REG, reg.replace(SPANS[3][2], text))
        print("r7-text applied to " + REG)
    else:
        print(text)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    default_repo = str(Path(__file__).resolve().parents[1])
    c = sub.add_parser("check", help="the three points of RL-134 item 9")
    c.add_argument("--repo", default=default_repo)
    src = c.add_mutually_exclusive_group()
    src.add_argument("--rev", help="read the filled files at this revision (default: the working tree)")
    src.add_argument("--filled-dir", help="read the filled files under this directory")
    c.add_argument("--base", default=BASE)
    c.add_argument("--s14", help="the S-14 commit; required to check values while the text still holds its blank")
    c.add_argument("--entry-date", default=datetime.date.today().isoformat())
    c.add_argument("--pin-request", default=DEFAULT_PIN_REQUEST, help="revision of the pin request while REQ is blank")
    c.add_argument("--python", default=sys.executable, help="interpreter for the R3 generator")
    c.add_argument("--ignore-path", action="append", help="a changed file outside point 1's scope to ignore")
    c.add_argument("--allow-blanks", action="store_true")
    c.add_argument("--mapping-report")
    c.add_argument("--require-r7", action="store_true")
    f = sub.add_parser("fill-cut", help="write the four ⟨CUT⟩ blanks from git after the tag exists")
    f.add_argument("--repo", default=default_repo)
    f.add_argument("--filled-dir")
    f.add_argument("--s14", required=True)
    f.add_argument("--pin-request-commit", required=True)
    r = sub.add_parser("r7-text", help="the OPEN[R7-SESSION-INDEX] fill from b6_mapping_build.py's report")
    r.add_argument("--repo", default=default_repo)
    r.add_argument("--filled-dir")
    r.add_argument("--mapping-report", required=True)
    r.add_argument("--date", required=True)
    r.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    if not hasattr(args, "rev"):
        args.rev = None
    try:
        return {"check": check, "fill-cut": fill_cut, "r7-text": r7_text}[args.cmd](args)
    except Usage as exc:
        print("fill-check: usage " + str(exc))
        return 2


if __name__ == "__main__":
    sys.exit(main())
