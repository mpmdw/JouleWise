"""Lenient reader of RUN_STATE numbered-item headings and pointer blocks.

This is not `scripts/gen_current.py`. That generator refuses a malformed block;
a watcher must keep reading. Here a block's `key: value` lines are taken as
written, a value that does not parse as a time is kept as text, and nothing is
refused. Only headings (the bold first sentence of an item) and pointer blocks
are read, never the item bodies.

Heading classes are matched on upper-case words, which is how the magistrate
and the lead mark state in headings ("R1 ARMED", "RE-ARMED", "NIGHT IS CLOSED",
"REFUSED", "FAULT:", "FAILED"). Lower-case uses ("Nothing is armed", "not
armed") are prose and do not match.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import re

ITEM_RE = re.compile(r"^(\d{1,4})([a-z]?)\. \*\*(.*)$")
FENCE_RE = re.compile(r"^(`{3,}|~{3,})(.*)$")
STAMP_RE = re.compile(
    r"(\d{4}-\d{2}-\d{2})[ T]~?(\d{1,2}):(\d{2})(?::\d{2})?(?:-\d{1,2}:\d{2})?\s*(Z|UTC|PST|PDT)?")
TZ_AFTER_RE = re.compile(r"\b(PST|PDT|UTC)\b|\dZ\b")
OFFSETS = {"PST": -8, "PDT": -7, "UTC": 0, "Z": 0}

ARMED_RE = re.compile(r"(?<![A-Za-z])(?:RE-)?ARMED\b|\bINSTALLED\b")
NEGATION_RE = re.compile(r"(?:\bNOT|\bNEVER|\bnot|\bnever|[Nn]othing is|\bNOTHING IS|\bNO)\s*$")
CLOSED_RE = re.compile(r"\bCLOSED\b|\bCOMPLETED?\b")
CODE_SPAN_RE = re.compile(r"`[^`]*`")
REFUSED_RE = re.compile(r"\bREFUSED\b|\bREFUSAL\b")
FAULT_RE = re.compile(r"\bFAULT\b|\bFAILED\b|\bSTRANDED\b|\bNEVER MEASURED\b")
LAUNCH_WORD_RE = re.compile(r"\b(?:install|installs|arm|arms|re-arm|arming)\b", re.I)
CODE_CHANGE_RE = re.compile(r"\bPR #\d+|\bmerged\b|\bfix(?:es|ed)?\b|\bkit\b|\bbuil[dt]\b|\bnew bytes\b", re.I)


@dataclass
class Item:
    number: int
    letter: str
    line: int
    heading: str
    author: str
    stamp: float | None
    classes: frozenset
    pointer: dict | None = None
    pointer_times: dict = field(default_factory=dict)

    @property
    def key(self):
        return (self.number, self.letter)

    @property
    def label(self):
        return f"{self.number}{self.letter}"


def parse_stamp(text: str) -> float | None:
    """First `YYYY-MM-DD HH:MM` in the text, with PST/PDT/UTC/Z; naive times read as Pacific."""
    match = STAMP_RE.search(text)
    if not match:
        return None
    day, hour, minute, tz = match.groups()
    if tz is None:
        after = TZ_AFTER_RE.search(text, match.end(), match.end() + 60)
        if after:
            tz = after.group(1) or "Z"
    try:
        base = datetime.strptime(f"{day} {int(hour):02d}:{minute}", "%Y-%m-%d %H:%M")
    except ValueError:
        return None
    if tz is None:
        tz = _pacific_abbrev(base)
    return base.replace(tzinfo=timezone(timedelta(hours=OFFSETS[tz]))).timestamp()


def _pacific_abbrev(naive: datetime) -> str:
    try:
        from zoneinfo import ZoneInfo
        return naive.replace(tzinfo=ZoneInfo("America/Los_Angeles")).tzname() or "PST"
    except Exception:  # noqa: BLE001 - no tz database: winter default
        return "PST"


def parse_time(value: str | None) -> float | None:
    if not value:
        return None
    text = value.strip()
    try:
        moment = datetime.fromisoformat(text.replace("Z", "+00:00") if text.endswith("Z") else text)
    except ValueError:
        return None
    if moment.tzinfo is None:
        return None
    return moment.timestamp()


def heading_text(rest: str) -> str:
    end = rest.find("**")
    return (rest if end < 0 else rest[:end]).strip()


def author_of(heading: str) -> str:
    lowered = heading.lower()
    if lowered.startswith("magistrate"):
        return "magistrate"
    if lowered.startswith("laptop lead") or lowered.startswith("lead "):
        return "lead"
    if lowered.startswith("ed's") or lowered.startswith("ed ") or lowered.startswith("ed,"):
        return "ed"
    if lowered.startswith("research lead"):
        return "research-lead"
    return "other"


def classify(heading: str) -> frozenset:
    """Classes from the heading's prose; code spans (paths, file names, commands) are ignored."""
    heading = CODE_SPAN_RE.sub(" ", heading)
    classes = set()
    for match in ARMED_RE.finditer(heading):
        if not NEGATION_RE.search(heading[max(0, match.start() - 14):match.start()]):
            classes.add("armed")
            break
    if CLOSED_RE.search(heading):
        classes.add("closed")
    if REFUSED_RE.search(heading):
        classes.add("refused")
    if FAULT_RE.search(heading):
        classes.add("fault")
    return frozenset(classes)


def parse_pointer_body(lines: list[str]) -> dict:
    body = {}
    for line in lines:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key, value = key.strip(), value.strip()
        if key and value and key not in body:
            body[key] = value
    return body


def parse_items(text: str) -> list[Item]:
    """Every numbered item outside fenced examples, with its pointer block if any."""
    lines = text.splitlines()
    items: list[Item] = []
    fence = None  # (char, length) of the open non-pointer fence
    current = None
    index = 0
    while index < len(lines):
        line = lines[index]
        fence_match = FENCE_RE.match(line)
        if fence is not None:
            if fence_match and fence_match.group(1)[0] == fence[0] and len(fence_match.group(1)) >= fence[1] \
                    and not fence_match.group(2).strip():
                fence = None
            index += 1
            continue
        if fence_match:
            marker, info = fence_match.groups()
            if marker == "```" and info.strip() == "pointer" and current is not None and current.pointer is None:
                body = []
                index += 1
                while index < len(lines) and lines[index].rstrip() != "```":
                    body.append(lines[index])
                    index += 1
                current.pointer = parse_pointer_body(body)
                current.pointer_times = {k: parse_time(current.pointer.get(k))
                                         for k in ("t0", "latest_end", "deadline")}
                index += 1
                continue
            fence = (marker[0], len(marker))
            index += 1
            continue
        match = ITEM_RE.match(line)
        if match:
            number, letter, rest = match.groups()
            heading = heading_text(rest)
            current = Item(int(number), letter, index + 1, heading, author_of(heading),
                           parse_stamp(heading), classify(heading))
            items.append(current)
        index += 1
    return items


@dataclass
class Session:
    plan_id: str
    item: Item
    t0: float | None
    latest_end: float | None
    deadline: float | None
    closed_by: Item | None


@dataclass
class RunState:
    items: list[Item]

    def ordered(self) -> list[Item]:
        return sorted(self.items, key=lambda item: item.key)

    def latest(self) -> Item | None:
        ordered = self.ordered()
        return ordered[-1] if ordered else None

    def latest_by(self, author: str) -> Item | None:
        found = [item for item in self.ordered() if item.author == author]
        return found[-1] if found else None

    def pointer_item(self) -> Item | None:
        found = [item for item in self.ordered() if item.pointer is not None]
        return found[-1] if found else None

    def after(self, item: Item) -> list[Item]:
        return [other for other in self.ordered() if other.key > item.key]

    def arm_items(self) -> list[Item]:
        return [item for item in self.ordered()
                if "armed" in item.classes or (item.pointer and item.pointer.get("armed"))]

    def session(self) -> Session | None:
        """The latest arm (an ARMED heading or a pointer `armed` key) and the item that ended it.

        The plan id, t0 and latest end come from the pointer keys when present,
        else from the heading and pointer prose ("t0 Fri 13 Nov 07:08 PST",
        "latest end 2026-11-14T18:21:00-08:00"), else from earlier arm items of
        the same session (no close item between them).
        """
        arms = self.arm_items()
        if not arms:
            return None
        latest = arms[-1]
        closer = next((other for other in self.after(latest) if other.classes & {"closed", "refused"}), None)
        fields = {"plan_id": None, "t0": None, "latest_end": None, "deadline": None}
        for item in reversed(arms):
            if item is not latest and any(o.classes & {"closed", "refused"}
                                          for o in self.ordered() if item.key < o.key <= latest.key):
                break
            for name, value in arm_fields(item).items():
                if fields.get(name) is None and value is not None:
                    fields[name] = value
            if all(v is not None for v in fields.values()):
                break
        return Session(fields["plan_id"] or f"item-{latest.label}", latest, fields["t0"],
                       fields["latest_end"] or fields["deadline"], fields["deadline"], closer)

    def last_session_end(self) -> Item | None:
        found = [item for item in self.ordered() if item.classes & {"closed", "refused"}]
        return found[-1] if found else None


def read(text: str) -> RunState:
    return RunState(parse_items(text))


PLAN_RE = re.compile(r"\b[a-z][a-z0-9]*(?:-[a-z0-9]+)*-\d{8}T\d{4,6}Z\b")
ISO_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?(?:Z|[+-]\d{2}:\d{2})")
MONTHS = {m: i for i, m in enumerate(("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct",
                                      "nov", "dec"), start=1)}
DAY_MONTH_RE = re.compile(r"^(?:[A-Z][a-z]{2},? )?(\d{1,2}) ([A-Z][a-z]{2}) (\d{1,2}):(\d{2})(?::\d{2})? ?(PST|PDT|UTC|Z)?")
MONTH_DAY_RE = re.compile(r"^(?:[A-Z][a-z]{2},? )?(\d{1,2})-(\d{1,2}) (\d{1,2}):(\d{2})(?::\d{2})? ?(PST|PDT|UTC|Z)?")
TIME_ONLY_RE = re.compile(r"^(\d{1,2}):(\d{2})(?::\d{2})? ?(PST|PDT|UTC|Z)?")


def _phrase_time(snippet: str, reference: float | None) -> float | None:
    """A time at the start of `snippet`: ISO, "Fri 13 Nov 07:08 PST", "Thu 11-12 03:25 PST" or "14:51 PST"."""
    snippet = snippet.lstrip(" :(~`")
    iso = ISO_RE.match(snippet)
    if iso:
        return parse_time(iso.group(0))
    ref = datetime.fromtimestamp(reference, timezone(timedelta(hours=-8))) if reference else None
    year = ref.year if ref else None
    match = DAY_MONTH_RE.match(snippet)
    if match and year:
        day, mon, hh, mm, tz = match.groups()
        month = MONTHS.get(mon.lower())
        return _local(year, month, int(day), int(hh), int(mm), tz) if month else None
    match = MONTH_DAY_RE.match(snippet)
    if match and year:
        month, day, hh, mm, tz = match.groups()
        return _local(year, int(month), int(day), int(hh), int(mm), tz)
    match = TIME_ONLY_RE.match(snippet)
    if match and ref:
        hh, mm, tz = match.groups()
        value = _local(ref.year, ref.month, ref.day, int(hh), int(mm), tz)
        if value is not None and reference is not None and value < reference - 3600:
            value += 86400
        return value
    return None


def _local(year, month, day, hh, mm, tz):
    try:
        naive = datetime(year, month, day, hh, mm)
    except ValueError:
        return None
    tz = tz or _pacific_abbrev(naive)
    return naive.replace(tzinfo=timezone(timedelta(hours=OFFSETS[tz]))).timestamp()


def _after_label(text: str, label: str, reference: float | None) -> float | None:
    for match in re.finditer(label, text, re.I):
        value = _phrase_time(text[match.end():match.end() + 60], reference)
        if value is not None:
            return value
    return None


def arm_fields(item: Item) -> dict:
    """plan_id, t0, latest_end and deadline for an arm item, from pointer keys first, then prose."""
    pointer = item.pointer or {}
    times = item.pointer_times or {}
    prose = item.heading + " " + " ".join(pointer.get(k, "") for k in ("wait", "next_observable", "on_early_or_refused"))
    plan = pointer.get("armed") or next(iter(PLAN_RE.findall(item.heading)), None) \
        or next(iter(PLAN_RE.findall(prose)), None)
    return {
        "plan_id": plan,
        "t0": times.get("t0") or _after_label(prose, r"\bt0\b", item.stamp),
        "latest_end": times.get("latest_end") or _after_label(prose, r"\blatest end\b", item.stamp),
        "deadline": times.get("deadline"),
    }


def arm_expected(pointer_item: Item | None) -> bool:
    """A magistrate-owned pointer without `armed` whose wait or next observable is an arm or install."""
    if pointer_item is None or not pointer_item.pointer:
        return False
    pointer = pointer_item.pointer
    if pointer.get("armed") or pointer.get("owner", "").strip().lower() != "magistrate":
        return False
    text = " ".join(pointer.get(key, "") for key in ("wait", "next_observable"))
    return bool(LAUNCH_WORD_RE.search(text))


def code_changed(items: list[Item]) -> bool:
    return any(CODE_CHANGE_RE.search(item.heading) for item in items)
