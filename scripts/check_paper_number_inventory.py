#!/usr/bin/env python3
"""Paper-number inventory checker with bound-slot enforcement and count ratchets.

``--check`` fails on a slot mismatch, missing/ambiguous anchor, refused
source, invalid binding, failed cross-check, or growth above the inventory's
unbound-results / unaccounted ceilings. Existing unresolved literals and the
spelled-out census are informational. ``--report`` always exits 0 (default).

THE PROBLEM IT ADDRESSES.  The existing paper checkers compare a printed number
with its source only where the number carries a ``[FILL:...]`` marker or sits
after a quoted sentence head.  A census on 2026-09-28 changed each of the 1,106
numeric literals in ``docs/paper/draft-v2-skeleton.md`` one at a time and found
241 printed results numbers that no checker notices when they change (for
example ``49 of 59`` and ``+13.0 ms`` in Section 2).  The numbers were right;
nothing would have caught them going wrong.

THE MECHANISM, in the order the checker runs it.

1. **Extract.**  Every numeric literal in the visible text is found with the
   census extractor (ported below unchanged in effect: HTML comments, the
   reference list, heading numbers, URLs, identifiers such as ``DX-010``,
   cross-references such as ``Section 4``, month-name dates, model sizes such
   as ``1.5B``, LaTeX command names, hashes and run ids are masked first).  On
   the 2026-09-28 skeleton it finds 1,106 literals, the census count.
   Spelled-out numbers (``zero`` ... ``twenty``, tens, ``hundred``,
   ``thousand``) are found separately.

2. **Account.**  The inventory file ``docs/paper/number-inventory.json`` holds
   *entries*.  An entry is an **anchor**: a short piece of the paper's text in
   which each number is replaced by a named **slot** written ``⟦name⟧``.  For
   example ``Their medians are ⟦onset_median⟧ ms and ⟦offset_median⟧ ms.``
   The checker turns the anchor into a pattern (any run of whitespace in the
   anchor matches any run of whitespace in the paper, so line wrapping does not
   matter; a slot matches any number-shaped token) and requires it to match
   the visible text exactly once.  Each slot then *claims* the extracted
   literals inside the text it matched.  A slot has one of three classes:

   - ``bound``: its expected text is re-derived from a hash-pinned source
     artefact with a named **rendering rule** (``signed_1`` prints an explicit
     sign, ``+`` or the Unicode minus ``−``, and one decimal; see RENDERERS).
   - ``tied``: its expected text comes from a named code constant or fixture
     field (a method constant, not a measurement).
   - ``classed``: a reviewed non-result (notation, index, date, framing); its
     expected text is the fixed literal written in the inventory, with a
     reason.

   A literal that no slot claims may instead be listed in ``unbound_results``
   (a results number that is known and not yet bound; the census list).
   Anything else is **unaccounted**.

3. **Compare.**  For every slot of a found anchor, the printed text must equal
   the expected text character for character: ``MATCH`` or ``MISMATCH``.  If
   an anchor is not found (the surrounding words changed), the entry is
   ``ANCHOR_MISSING`` and its numbers fall through to unaccounted: a moved or
   rewritten number is never silently passed.  An anchor found more than once
   is ``ANCHOR_AMBIGUOUS``.

4. **Refuse bad sources.**  Before any value is read, each source file's
   SHA-256 must equal the inventory's pin, and the inventory's pin must equal
   the pin in its authority (a registry line, or a named code constant).  A
   source failing either is ``REFUSED``: none of its slots can MATCH.

5. **Cross-check.**  ``predicates`` re-derive summary numbers from the raw rows
   of the same artefact (for example the offset median recomputed from the 59
   per-pulse lags) and ``registry_checks`` require the registry row's printed
   value to equal the rendering, the row's supplier text to name the same field
   path, and the row not to be retired.

Worked example (Section 2, 2026-09-28): XD's ``summary.offset_best_fit_lag``
has ``count_negative`` 49 and ``count`` 59.  The anchor ``⟦neg⟧ of ⟦off_n⟧
offset lags are negative`` matches ``49 of 59 offset lags are negative``; the
slot ``neg`` renders 49 with rule ``integer`` as ``49`` and the printed text is
``49``: MATCH.  Edit the paper to ``50 of 59`` and the same anchor still
matches, the printed text is ``50``, the expected text is ``49``: MISMATCH,
reported with the line and anchor.
"""

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass, field
from decimal import ROUND_HALF_EVEN, Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import re
import statistics
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INVENTORY = ROOT / "docs" / "paper" / "number-inventory.json"
SCHEMA = "joulewise-paper-number-inventory/v1"
MINUS = "−"

# --------------------------------------------------------------------------
# 1. Extraction (the 2026-09-28 census extractor, ported; offsets preserved)
# --------------------------------------------------------------------------

_NUM = re.compile(
    r"(?<![\w.\\])[+\-−±]?(?:(?:\d{1,3}(?:,\d{3})+(?!\d)|\d+)(?:\.\d+)?|\.\d+)"
    r"(?:[eE][+\-−]?\d+)?%?(?![\w])(?!\.\d)"
)
_WORDS = (
    "zero one two three four five six seven eight nine ten eleven twelve "
    "thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty "
    "thirty forty fifty sixty seventy eighty ninety hundred thousand"
).split()
_WORD_RE = re.compile(r"\b(" + "|".join(_WORDS) + r")\b", re.IGNORECASE)
WORD_VALUES = {w: i for i, w in enumerate(_WORDS[:21])}


def _blank(s: str) -> str:
    return re.sub(r"[^\n]", "\x00", s)


def _mask(pattern: str, t: str, flags: int = re.DOTALL) -> str:
    return re.sub(pattern, lambda m: _blank(m.group(0)), t, flags=flags)


def visible_text(text: str) -> str:
    """The text with HTML comments blanked (same length, newlines kept)."""
    return _mask(r"<!--.*?-->", text)


def census_mask(text: str) -> str:
    masked = visible_text(text)
    try:
        ref_start = text.index("## 9. References")
        ref_end = text.index("## Appendix A.")
        masked = masked[:ref_start] + _blank(masked[ref_start:ref_end]) + masked[ref_end:]
    except ValueError:
        pass
    masked = re.sub(
        r"(?m)^(#+ )((?:Appendix )?[A-Z]?\d+(?:\.\d+)*\.?)",
        lambda m: m.group(1) + "\x00" * len(m.group(2)),
        masked,
    )
    masked = _mask(r"https?://\S+", masked)
    masked = _mask(r"\]\([^)]*\)", masked)
    masked = _mask(r"\b[A-Z][A-Za-z]*-\d+(?:[–/-]\d+)*\b", masked)
    masked = _mask(
        r"\b(?:Section|Sections|Figure|Figures|Table|Tables|Appendix|Appendices|"
        r"Algorithm|Step|step|Equation|Eq\.)\s+[A-Z]?\d+(?:\.\d+)*"
        r"(?:[–-][A-Z]?\d+(?:\.\d+)*)?",
        masked,
    )
    masked = _mask(
        r"\b(?:January|February|March|April|May|June|July|August|September|"
        r"October|November|December)(?:\s+\d{1,2},)?\s+\d{4}\b",
        masked,
    )
    masked = _mask(r"\b\d+(?:\.\d+)?B\b", masked)
    masked = _mask(r"\\[A-Za-z]+", masked)
    masked = _mask(r"\b[A-Za-z_][\w./-]*\d[\w./-]*", masked)
    masked = _mask(r"\b(?=[0-9a-f]*[a-f])(?=[0-9a-f]*\d)[0-9a-f]{7,64}\b", masked)
    masked = _mask(r"\b\d{8}T\d{6}-[0-9a-f]{8}\b", masked)
    masked = _mask(r"\[\d+(?:\s*[,–-]\s*\d+)*\]", masked)
    masked = re.sub(
        r"(?m)^(\s*)(\d+)(\. )",
        lambda m: m.group(1) + "\x00" * len(m.group(2)) + m.group(3),
        masked,
    )
    return masked


@dataclass
class Literal:
    start: int
    end: int
    line: int
    lit: str
    ctx: str
    kind: str  # "digit" or "word"
    claim: str | None = None  # class that accounted for it
    claimed_by: str | None = None


def _ctx(text: str, start: int, end: int) -> str:
    ls = text.rfind("\n", 0, start) + 1
    le = text.find("\n", start)
    le = len(text) if le < 0 else le
    return text[max(ls, start - 40) : min(le, end + 30)]


def extract_literals(text: str) -> list[Literal]:
    masked = census_mask(text)
    out: list[Literal] = []
    for m in _NUM.finditer(masked):
        s = m.group(0)
        if not re.search(r"\d", s):
            continue
        tok = s.rstrip(".,")
        start = m.start()
        end = start + len(tok)
        out.append(
            Literal(start, end, text.count("\n", 0, start) + 1, tok, _ctx(text, start, end), "digit")
        )
    return out


def extract_spelled(text: str) -> list[Literal]:
    masked = census_mask(text)
    out = []
    for m in _WORD_RE.finditer(masked):
        out.append(
            Literal(
                m.start(), m.end(), text.count("\n", 0, m.start()) + 1, m.group(0),
                _ctx(text, m.start(), m.end()), "word",
            )
        )
    return out


# --------------------------------------------------------------------------
# 2. Sources, expressions and renderers
# --------------------------------------------------------------------------


class SourceRefused(Exception):
    pass


class ExprError(Exception):
    pass


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def python_constant(path: Path, name: str) -> Any:
    """Read a top-level ``NAME = <literal>`` from a module without importing it."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        targets: list[ast.expr] = []
        if isinstance(node, ast.Assign):
            targets = list(node.targets)
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets = [node.target]
        for t in targets:
            if isinstance(t, ast.Name) and t.id == name:
                return ast.literal_eval(node.value)  # type: ignore[arg-type]
    raise ExprError(f"constant {name} not found in {path}")


_TOKEN = re.compile(r"\.?([A-Za-z_][A-Za-z0-9_]*)|\[(\d+|\*|[A-Za-z_][A-Za-z0-9_]*=[^\]]+)\]")


def walk_path(obj: Any, path: str) -> Any:
    pos = 0
    cur: Any = obj
    mapped = False
    while pos < len(path):
        m = _TOKEN.match(path, pos)
        if not m:
            raise ExprError(f"bad path syntax at {path[pos:]!r} in {path!r}")
        pos = m.end()

        def step(o: Any) -> Any:
            if m.group(1) is not None:
                if not isinstance(o, dict) or m.group(1) not in o:
                    raise ExprError(f"missing key {m.group(1)!r} in {path!r}")
                return o[m.group(1)]
            sel = m.group(2)
            if sel.isdigit():
                if not isinstance(o, list) or int(sel) >= len(o):
                    raise ExprError(f"missing index [{sel}] in {path!r}")
                return o[int(sel)]
            k, v = sel.split("=", 1)
            hits = [x for x in o if isinstance(x, dict) and str(x.get(k)) == v]
            if len(hits) != 1:
                raise ExprError(f"selector [{sel}] matched {len(hits)} items in {path!r}")
            return hits[0]

        if m.group(2) == "*":
            if not isinstance(cur, list):
                raise ExprError(f"[*] on non-list in {path!r}")
            mapped = True
            continue
        cur = [step(x) for x in cur] if mapped else step(cur)
    return cur


FUNCS = {
    "len": len,
    "last_index": lambda xs: len(xs) - 1,
    "median": lambda xs: statistics.median(xs),
    "max": max,
    "count_pos": lambda xs: sum(1 for x in xs if x > 0),
    "count_neg": lambda xs: sum(1 for x in xs if x < 0),
    "count_zero": lambda xs: sum(1 for x in xs if x == 0),
    "strip_unit": lambda x: re.sub(r"\s*(?:ms|s|%)$", "", x),
    "float": float,
    "x1000": lambda x: x * 1000,
    "round6": lambda x: round(x, 6),
}


class Sources:
    """Loads pinned sources lazily; a source is either OK or REFUSED."""

    def __init__(self, inventory: dict, repo_root: Path, registry_text: str,
                 overrides: dict[str, Path] | None = None):
        self.spec = inventory["sources"]
        self.root = repo_root
        self.registry_text = registry_text
        self.overrides = overrides or {}
        self.data: dict[str, Any] = {}
        self.status: dict[str, str] = {}
        for name in self.spec:
            self._load(name)

    def path_of(self, name: str) -> Path:
        return self.overrides.get(name) or (self.root / self.spec[name]["path"])

    def _authority_pin(self, spec: dict) -> str:
        pin = spec["pin"]
        if pin["kind"] == "registry_line":
            # Every listed registry line must be present and carry the same pin.
            patterns = pin["pattern"] if isinstance(pin["pattern"], list) else [pin["pattern"]]
            found = set()
            for pat in patterns:
                m = re.search(pat, self.registry_text, re.MULTILINE)
                if not m:
                    raise SourceRefused(f"registry pin line not found ({pat!r})")
                found.add(m.group(1))
            if len(found) != 1:
                raise SourceRefused(f"registry pin lines disagree: {sorted(found)}")
            return found.pop()
        if pin["kind"] == "python_constant":
            return str(python_constant(self.root / pin["file"], pin["name"]))
        raise SourceRefused(f"unknown pin kind {pin['kind']!r}")

    def _load(self, name: str) -> None:
        spec = self.spec[name]
        path = self.path_of(name)
        try:
            if not path.is_file():
                raise SourceRefused(f"file missing: {path}")
            authority = self._authority_pin(spec)
            if authority != spec["sha256"]:
                raise SourceRefused(
                    f"inventory pin {spec['sha256'][:12]}… differs from authority pin {authority[:12]}…"
                )
            actual = sha256_file(path)
            if actual != spec["sha256"]:
                raise SourceRefused(f"sha256 {actual[:12]}… differs from pin {spec['sha256'][:12]}…")
            self.data[name] = json.loads(path.read_text(encoding="utf-8"))
            self.status[name] = f"OK sha256 {actual}"
        except SourceRefused as exc:
            self.status[name] = f"REFUSED: {exc}"

    def refused(self, name: str) -> bool:
        return name not in self.data

    def eval(self, expr: str) -> Any:
        """``SRC:path|func|func`` or ``CONST:file#NAME``."""
        head, *funcs = expr.split("|")
        src, _, path = head.partition(":")
        if src == "CONST":
            file, _, name = path.partition("#")
            value = python_constant(self.root / file, name)
        elif src == "REG":
            row = registry_row(self.registry_text, path)
            if row is None or len(row) < 7:
                raise ExprError(f"registry row {path} not found")
            if row[4].startswith("RETIRED"):
                raise ExprError(f"registry row {path} is retired")
            value = row[1]
        else:
            if src not in self.spec:
                raise ExprError(f"unknown source {src!r}")
            if self.refused(src):
                raise SourceRefused(f"{src} refused: {self.status[src]}")
            value = walk_path(self.data[src], path)
        for f in funcs:
            if f not in FUNCS:
                raise ExprError(f"unknown function {f!r}")
            value = FUNCS[f](value)
        return value


def _dec(v: Any) -> Decimal:
    if isinstance(v, bool):
        raise ExprError("boolean where a number was expected")
    if isinstance(v, str):
        return Decimal(v)
    if isinstance(v, int):
        return Decimal(v)
    if isinstance(v, float):
        return Decimal(repr(v))
    raise ExprError(f"not a number: {v!r}")


def _int(v: Any) -> int:
    if isinstance(v, bool):
        raise ExprError("boolean where an integer was expected")
    if isinstance(v, int):
        return v
    if isinstance(v, float) and v.is_integer():
        return int(v)
    raise ExprError(f"not an integer: {v!r}")


def _signed(d: Decimal, text: str) -> str:
    if d > 0:
        return "+" + text
    if d < 0:
        return MINUS + text.lstrip("-")
    return text.lstrip("-")


def r_integer(v: Any) -> str:
    return str(_int(v))


def r_signed_int(v: Any) -> str:
    i = _int(v)
    return _signed(Decimal(i), str(abs(i)))


def r_signed_1(v: Any) -> str:
    d = _dec(v).quantize(Decimal("0.1"), rounding=ROUND_HALF_EVEN)
    return _signed(d, format(abs(d), "f"))


def r_word_int(v: Any) -> str:
    i = _int(v)
    for w, n in WORD_VALUES.items():
        if n == i:
            return w
    raise ExprError(f"no word for {i}")


def r_decimal_string(v: Any) -> str:
    if not isinstance(v, str):
        raise ExprError(f"decimal_string needs a stored string, got {v!r}")
    try:
        Decimal(v)
    except InvalidOperation as exc:
        raise ExprError(f"not a decimal string: {v!r}") from exc
    return v


def r_s_to_ms_exact(v: Any) -> str:
    """Seconds to milliseconds by an exact decimal shift of the stored digits."""
    return format(_dec(v).scaleb(3), "f")


def r_binary64_diff_s_to_ms_repr(a: Any, b: Any) -> str:
    """repr of the binary64 value (a - b) * 1000, a and b in seconds."""
    return repr((float(a) - float(b)) * 1000)


def r_positive_overlap_decimal(ps: Any, pe: Any, rs: Any, re_: Any) -> str:
    """max(0, min(phase_end, record_end) - max(phase_start, record_start)) in exact decimal."""
    ov = min(_dec(pe), _dec(re_)) - max(_dec(ps), _dec(rs))
    return "0" if ov <= 0 else format(ov, "f")


RENDERERS = {
    "integer": r_integer,
    "signed_int": r_signed_int,
    "signed_1": r_signed_1,
    "word_int": r_word_int,
    "decimal_string": r_decimal_string,
    "s_to_ms_exact": r_s_to_ms_exact,
    "binary64_diff_s_to_ms_repr": r_binary64_diff_s_to_ms_repr,
    "positive_overlap_decimal": r_positive_overlap_decimal,
    "text": lambda v: str(v),
}

# Slot patterns: what text a slot may match in the paper.  Deliberately
# permissive, so a wrong value still matches its anchor and is reported as a
# MISMATCH rather than as a missing anchor.
SLOT_PATTERNS = {
    "number": r"[+\-−±]?\d[\d,]*(?:\.\d+)?|[+\-−±]?\.\d+",
    "word": r"[A-Za-z]+",
    "text": r"[^\s`|]+",
}


def slot_kind(slot: dict) -> str:
    if slot.get("kind"):
        return slot["kind"]
    if slot.get("render") == "word_int":
        return "word"
    return "number"


# --------------------------------------------------------------------------
# 3. The check
# --------------------------------------------------------------------------

_SLOT = re.compile(r"⟦([A-Za-z0-9_]+)⟧")
_REF = re.compile(r"⟦([A-Za-z0-9_.]+)⟧")  # entry_id.slot references in registry checks


def anchor_regex(anchor: str, slots: dict) -> re.Pattern:
    parts: list[str] = []
    pos = 0
    for m in _SLOT.finditer(anchor):
        parts.append(_literal_pattern(anchor[pos : m.start()]))
        name = m.group(1)
        if name not in slots:
            raise ExprError(f"anchor slot ⟦{name}⟧ has no slot definition")
        parts.append(f"(?P<{name}>{SLOT_PATTERNS[slot_kind(slots[name])]})")
        pos = m.end()
    parts.append(_literal_pattern(anchor[pos:]))
    body = "".join(parts)
    # The anchor may not begin or end inside a longer number or word.
    return re.compile(r"(?<![\w.])" + body + r"(?![\w])")


def _literal_pattern(s: str) -> str:
    return r"\s+".join(re.escape(chunk) for chunk in re.split(r"\s+", s)) if s.strip() else (
        r"\s+" if s else ""
    )


OK_STATUSES = ("MATCH", "PREDICATE_OK", "REGISTRY_OK")


@dataclass
class Finding:
    status: str  # MATCH MISMATCH ANCHOR_MISSING ANCHOR_AMBIGUOUS REFUSED ERROR PRED_FAIL REG_FAIL STALE ...
    where: str
    detail: str
    line: int | None = None


@dataclass
class Report:
    skeleton_sha256: str
    sources: dict[str, str]
    literals: list[Literal]
    spelled: list[Literal]
    slots: list[dict] = field(default_factory=list)  # per-slot outcomes
    findings: list[Finding] = field(default_factory=list)
    spelled_expected_total: int | None = None

    def by_status(self, status: str) -> list[Finding]:
        return [f for f in self.findings if f.status == status]

    def counts(self) -> dict[str, int]:
        c = {"literals": len(self.literals)}
        for cls in ("bound", "tied", "classed", "unbound-results"):
            c[cls] = sum(1 for l in self.literals if l.claim == cls)
        c["unaccounted"] = sum(1 for l in self.literals if l.claim is None)
        c["spelled_total"] = len(self.spelled)
        c["spelled_claimed"] = sum(1 for l in self.spelled if l.claim)
        return c

    def unaccounted(self) -> list[Literal]:
        return [l for l in self.literals if l.claim is None]

    def check_failures(self) -> list[str]:
        # Stale unresolved contexts and the spelled-out census are diagnostics;
        # only count growth makes unresolved numeric literals fail the gate.
        informational = {"STALE", "CLASS_COUNT_CHANGED"}
        return [f"{f.status} {f.where}" for f in self.findings
                if f.status not in OK_STATUSES and f.status not in informational]


def run_check(
    repo_root: Path = ROOT,
    skeleton_text: str | None = None,
    inventory: dict | None = None,
    source_overrides: dict[str, Path] | None = None,
    registry_text: str | None = None,
) -> Report:
    if inventory is None:
        inventory = json.loads(DEFAULT_INVENTORY.read_text(encoding="utf-8"))
    if inventory.get("schema") != SCHEMA:
        raise SystemExit(f"inventory schema {inventory.get('schema')!r} != {SCHEMA!r}")
    if skeleton_text is None:
        skeleton_text = (repo_root / inventory["skeleton"]).read_text(encoding="utf-8")
    if registry_text is None:
        registry_text = (repo_root / inventory["registry"]).read_text(encoding="utf-8")

    sources = Sources(inventory, repo_root, registry_text, source_overrides)
    literals = extract_literals(skeleton_text)
    spelled = extract_spelled(skeleton_text)
    rep = Report(
        hashlib.sha256(skeleton_text.encode("utf-8")).hexdigest(),
        dict(sources.status), literals, spelled,
        spelled_expected_total=inventory.get("spelled_out_expected_total"),
    )
    for name, st in sources.status.items():
        if st.startswith("REFUSED"):
            rep.findings.append(Finding("REFUSED", f"source {name}", st))

    visible = visible_text(skeleton_text)
    all_lits = sorted(literals + spelled, key=lambda l: l.start)
    expected_by_slot: dict[str, str] = {}

    def claim(span: tuple[int, int], cls: str, who: str, kind: str) -> int:
        n = 0
        for lit in all_lits:
            if lit.start >= span[0] and lit.end <= span[1] and lit.claim is None:
                if kind == "word" and lit.kind != "word":
                    continue
                if kind != "word" and lit.kind == "word":
                    continue
                lit.claim, lit.claimed_by = cls, who
                n += 1
        return n

    for group in inventory["groups"]:
        for entry in group["entries"]:
            eid = entry["id"]
            slots = entry["slots"]
            try:
                rx = anchor_regex(entry["anchor"], slots)
            except (ExprError, re.error) as exc:
                rep.findings.append(Finding("ERROR", eid, f"bad anchor: {exc}"))
                continue
            matches = list(rx.finditer(visible))
            if len(matches) != 1:
                status = "ANCHOR_MISSING" if not matches else "ANCHOR_AMBIGUOUS"
                lines = [skeleton_text.count("\n", 0, m.start()) + 1 for m in matches]
                rep.findings.append(Finding(
                    status, eid, f"anchor {entry['anchor']!r} found {len(matches)} times {lines}"
                ))
                # still compute expected values so registry checks can run
                for sname, slot in slots.items():
                    _expected(sources, slot, f"{eid}.{sname}", expected_by_slot, rep)
                continue
            m = matches[0]
            for sname, slot in slots.items():
                sid = f"{eid}.{sname}"
                span = m.span(sname)
                printed = m.group(sname)
                sline = skeleton_text.count("\n", 0, span[0]) + 1
                cls = slot["class"]
                exp = _expected(sources, slot, sid, expected_by_slot, rep)
                n = claim(span, cls, sid, slot_kind(slot))
                if slot_kind(slot) != "text" and n != 1:
                    rep.findings.append(Finding(
                        "ERROR", sid, f"slot text {printed!r} covers {n} extracted literals (expected 1)", sline
                    ))
                rec = {"slot": sid, "class": cls, "printed": printed, "expected": exp, "line": sline,
                       "group": group["id"]}
                rep.slots.append(rec)
                if exp is None:
                    continue  # REFUSED/ERROR already recorded
                if printed == exp:
                    rep.findings.append(Finding("MATCH", sid, f"{printed!r}", sline))
                else:
                    rep.findings.append(Finding(
                        "MISMATCH", sid,
                        f"printed {printed!r} expected {exp!r} ({slot.get('expr') or slot.get('inputs') or 'fixed'}; "
                        f"rule {slot.get('render', 'fixed')}) | anchor: {entry['anchor']!r}",
                        sline,
                    ))

        for pred in group.get("predicates", []):
            _predicate(sources, pred, group["id"], rep)
        for rc in group.get("registry_checks", []):
            _registry_check(rc, registry_text, expected_by_slot, rep)

    # unbound results: known, not-yet-bound results numbers (census list)
    for ub in inventory.get("unbound_results", []):
        # ctx is the census context string (raw text; it may run into a
        # comment); ``occurrence`` picks among repeated identical contexts.
        hits = _find_all(skeleton_text, ub["ctx"])
        occ = ub.get("occurrence", 0)
        target = None
        if len(hits) == ub.get("occurrences", 1) and occ < len(hits):
            s = hits[occ] + ub["offset"]
            target = next((l for l in literals if l.start == s and l.lit == ub["literal"]), None)
        if target is None:
            rep.findings.append(Finding(
                "STALE", "unbound_results", f"{ub['literal']!r} ctx {ub['ctx']!r} not located ({len(hits)} ctx hits)",
                ub.get("line"),
            ))
        elif target.claim is None:
            target.claim, target.claimed_by = "unbound-results", ub.get("why", "census")
    if rep.spelled_expected_total is not None and len(spelled) != rep.spelled_expected_total:
        rep.findings.append(Finding(
            "CLASS_COUNT_CHANGED", "spelled-out total",
            f"{len(spelled)} spelled-out numbers, inventory pins {rep.spelled_expected_total}",
        ))
    counts = rep.counts()
    for name in ("unbound-results", "unaccounted"):
        ceiling = inventory.get("ratchet", {}).get(name)
        if type(ceiling) is not int or ceiling < 0:
            rep.findings.append(Finding("ERROR", f"ratchet {name}", "missing or invalid ceiling"))
        elif counts[name] > ceiling:
            rep.findings.append(Finding(
                "RATCHET_GROWTH", name, f"{counts[name]} exceeds ceiling {ceiling}",
            ))
    return rep


def _find_all(hay: str, needle: str) -> list[int]:
    out, i = [], hay.find(needle)
    while i >= 0:
        out.append(i)
        i = hay.find(needle, i + 1)
    return out


def _expected(sources: Sources, slot: dict, sid: str, cache: dict, rep: Report) -> str | None:
    if sid in cache:
        return cache[sid]
    cls = slot["class"]

    def render(spec: dict) -> str:
        rule = RENDERERS[spec["render"]]
        if "inputs" in spec:
            return rule(*[sources.eval(e) for e in spec["inputs"]])
        return rule(sources.eval(spec["expr"]))

    try:
        if cls == "classed":
            exp = slot["literal"]
        else:
            exp = render(slot)
            if slot.get("case") == "capitalize":
                exp = exp[:1].upper() + exp[1:]
            # A second, independent derivation that must render identically
            # (e.g. an overlap re-derived from endpoints vs. the stored overlap).
            for cross in slot.get("cross", []):
                alt = render(cross)
                ok = alt == exp
                rep.findings.append(Finding(
                    "PREDICATE_OK" if ok else "PRED_FAIL", f"{sid} cross-check",
                    f"{cross.get('expr') or cross.get('inputs')} renders {alt!r}; slot renders {exp!r}",
                ))
    except SourceRefused as exc:
        rep.findings.append(Finding("REFUSED", sid, str(exc)))
        exp = None
    except (ExprError, KeyError, ValueError, TypeError, InvalidOperation) as exc:
        rep.findings.append(Finding("ERROR", sid, f"{type(exc).__name__}: {exc}"))
        exp = None
    cache[sid] = exp
    return exp


def _predicate(sources: Sources, pred: dict, gid: str, rep: Report) -> None:
    where = f"{gid}: {pred['why']}"
    try:
        def ev(side: Any) -> Any:
            if isinstance(side, list):
                return sum(sources.eval(e) for e in side)
            if isinstance(side, str) and ":" in side:
                return sources.eval(side)
            return side

        lhs, rhs = ev(pred["lhs"]), ev(pred["rhs"])
    except SourceRefused as exc:
        rep.findings.append(Finding("REFUSED", where, str(exc)))
        return
    except (ExprError, TypeError, ValueError) as exc:
        rep.findings.append(Finding("ERROR", where, f"{type(exc).__name__}: {exc}"))
        return
    ok = lhs == rhs
    rep.findings.append(Finding("PREDICATE_OK" if ok else "PRED_FAIL", where, f"{lhs!r} == {rhs!r}"))


def registry_row(registry_text: str, key: str) -> list[str] | None:
    for line in registry_text.splitlines():
        if line.startswith(f"| {key} — "):
            return [c.strip() for c in line.strip().strip("|").split(" | ")]
    return None


def _registry_check(rc: dict, registry_text: str, expected: dict, rep: Report) -> None:
    key = rc["key"]
    row = registry_row(registry_text, key)
    if row is None or len(row) < 7:
        rep.findings.append(Finding("REG_FAIL", f"registry {key}", "row not found or malformed"))
        return
    problems = []

    def fill(template: str) -> str:
        for sid in _REF.findall(template):
            if expected.get(sid) is None:
                problems.append(f"slot {sid} has no expected value")
            template = template.replace(f"⟦{sid}⟧", expected.get(sid) or "?")
        return template

    value = fill(rc["value"])
    if row[1] != value:
        problems.append(f"registry value {row[1]!r} != rendered {value!r}")
    for needle in rc.get("supplier_contains", []):
        needle = fill(needle)
        if needle not in row[2]:
            problems.append(f"supplier text lacks {needle!r}")
    if row[4].startswith("RETIRED") or row[5].startswith("RETIRED"):
        problems.append(f"row is retired ({row[4]})")
    rep.findings.append(Finding(
        "REG_FAIL" if problems else "REGISTRY_OK", f"registry {key}", "; ".join(problems) or row[1]
    ))


# --------------------------------------------------------------------------
# 4. Report
# --------------------------------------------------------------------------


def format_report(rep: Report, list_spelled: bool = False) -> str:
    out = ["PAPER-NUMBER-INVENTORY (bound-slot check; unresolved count ratchets)"]
    out.append(f"skeleton sha256 {rep.skeleton_sha256}")
    for name, st in rep.sources.items():
        out.append(f"SOURCE {name}: {st}")
    c = rep.counts()
    out.append(
        f"LITERALS {c['literals']}: bound {c['bound']}, tied {c['tied']}, classed {c['classed']}, "
        f"unbound-results {c['unbound-results']}, unaccounted {c['unaccounted']}"
    )
    out.append(
        f"SPELLED-OUT {c['spelled_total']} (pinned total {rep.spelled_expected_total}): "
        f"claimed by slots {c['spelled_claimed']}, not inventoried {c['spelled_total'] - c['spelled_claimed']}"
    )
    groups: dict[str, dict[str, int]] = {}
    for s in rep.slots:
        g = groups.setdefault(s["group"], {})
        st = "REFUSED/ERROR" if s["expected"] is None else ("MATCH" if s["printed"] == s["expected"] else "MISMATCH")
        key = f"{s['class']} {st}"
        g[key] = g.get(key, 0) + 1
    for gid, g in groups.items():
        out.append(f"GROUP {gid}: " + ", ".join(f"{k} {v}" for k, v in sorted(g.items())))
    for st in ("PREDICATE_OK", "REGISTRY_OK"):
        out.append(f"{st} {len(rep.by_status(st))}")
    for f in rep.findings:
        if f.status in OK_STATUSES:
            continue
        loc = f" line {f.line}" if f.line else ""
        out.append(f"{f.status} {f.where}{loc}: {f.detail}")
    for l in rep.literals:
        if l.claim == "unbound-results":
            out.append(f"UNBOUND-RESULT line {l.line} {l.lit!r} | {l.ctx}")
    for l in rep.unaccounted():
        out.append(f"UNACCOUNTED line {l.line} {l.lit!r} | {l.ctx}")
    if list_spelled:
        for l in rep.spelled:
            if not l.claim:
                out.append(f"SPELLED-NOT-INVENTORIED line {l.line} {l.lit!r} | {l.ctx}")
    fails = rep.check_failures()
    out.append(f"CHECK {'FAIL' if fails else 'PASS'}: {len(fails)} finding(s)")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--report", action="store_true", help="report only; always exit 0 (default)")
    mode.add_argument("--check", action="store_true", help="enforce slots, source pins and unresolved count ceilings")
    ap.add_argument("--repo-root", type=Path, default=ROOT)
    ap.add_argument("--inventory", type=Path, default=None)
    ap.add_argument("--skeleton", type=Path, default=None, help="check this file instead of the inventory's skeleton")
    ap.add_argument("--source", action="append", default=[], metavar="NAME=PATH",
                    help="read source NAME from PATH (its pin is still enforced)")
    ap.add_argument("--list-spelled", action="store_true", help="also list spelled-out numbers not inventoried")
    args = ap.parse_args(argv)
    inv_path = args.inventory or (args.repo_root / "docs" / "paper" / "number-inventory.json")
    inventory = json.loads(inv_path.read_text(encoding="utf-8"))
    overrides = {}
    for s in args.source:
        name, _, p = s.partition("=")
        overrides[name] = Path(p)
    text = args.skeleton.read_text(encoding="utf-8") if args.skeleton else None
    rep = run_check(args.repo_root, text, inventory, overrides)
    print(format_report(rep, args.list_spelled))
    if args.check and rep.check_failures():
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
