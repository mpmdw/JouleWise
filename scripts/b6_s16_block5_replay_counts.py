#!/usr/bin/env python3
"""S-16, Block 5's half: replay counts of Block 6's new or changed §8 rules over Block 5's usable sessions.

RL-134 item 17 (runbook B-6, step 10). For each condition of the Block 6 registration's §8.2 and §8.3 that is new
or changed (§8.7 item 1), this counts the runs and sessions it removes over Block 5's three usable, released
sessions, in the rehearsal's format ("removes X of N runs; Y of M sessions"). Counts only.

Inputs, and nothing else, per session (a Block 5 harvest root):

- ``derived/flags.jsonl``: the released flags (code, scope level, run id; for two derived rows, the structural
  fields ``observed.reference_counts`` and ``observed.planned_reference_counts`` of ``neg8.reference_lost``);
- ``derived/roster.json``: member run ids and kinds, for the denominators;
- ``derived/exclusions.json``: only ``claim_usable`` and the length of ``members_excluded``, as a cross-check.

and the two flag catalogs (Block 5's, which the harvests used, and Block 6's at the pin). No energy, no estimate,
no timing value is read.

A rule whose condition Block 5's flags cannot show (its code has no Block 5 emitter, or its input is not a flag)
prints ``not evaluated`` with the reason and, where one exists, the nearest Block 5 code's count. It never prints a
silent 0.

Usage::

    python3 scripts/b6_s16_block5_replay_counts.py \\
        --b5-catalog configs/campaigns/v5_claim_25g83/flag_catalog.json \\
        --b6-catalog <file: git show b9de23a2c:configs/b6/flag_catalog_b6.json> \\
        --session <harvest root> --session <harvest root> --session <harvest root> \\
        --json-out counts.json --md-out counts.md

By default the inputs must equal the released Block 5 files and the pinned catalogs by SHA-256 (``PINS``);
``--unpinned`` lifts that for synthetic fixtures. Exit 0 on success, 2 on usage, 4 on a refusal.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

SCHEMA = "joulewise.b6_s16_block5_replay.v1"

# The released Block 5 inputs, as the blind dry run's input census (B5-BLIND-DRY-RUN-RECORD.json, dry-m) and the
# release check list them, and the two catalogs. Block 6's catalog is the one the release record ties (b5bce6c6…),
# at the Block 6 pin b9de23a2c.
PINS: dict[str, Any] = {
    "b5_catalog": "5d77c725d4bf482bd667ca4c3a926e2f6471d55d196cd4b4addee435da01ee8d",
    "b6_catalog": "b5bce6c64bbc1d079ecf6fed02bf4c214b76a8f7d279d44eea5984e4a389a42b",
    "sessions": {
        "v5-b5-alpha-a1-20261009T2312Z": {
            "derived/flags.jsonl": "ad97122ce352fadeccae267d833f46a33c8ebb35b391c0abe01c6434ae65d0a1",
            "derived/roster.json": "f8170bf46cf976b246dad299967e38e0c4279fff41e056364d0ede6e834a184c",
            "derived/exclusions.json": "3c102f57cfe951af4b11a3726232ada164d106facee1083f5d1e90da4aa25189",
        },
        "v5-b5-beta-a6-20261011T2011Z": {
            "derived/flags.jsonl": "e4e3fc49cff76a6cc3ff5d99313df85e423174a526dd6d415a5ec8fc0152df9a",
            "derived/roster.json": "e67c15600998b1672e31ddbe795560ae989b42cb68411e55e1f7141b7edf3577",
            "derived/exclusions.json": "ca547afa76f98294d54a97bcb2fc24a4791611c084cfde78a76f9d2f402bad87",
        },
        "v5-b5-gamma-a1-20261012T0420Z": {
            "derived/flags.jsonl": "264999236a99d5f76a9deff86d011a0a4d837a0b8532555d1da9522a3fa2b321",
            "derived/roster.json": "87961bc79d9d6c475ac6f4944047d27efddb88d5fbcdefad19bb69d985c502e2",
            "derived/exclusions.json": "a9954365ef44c1b8a65603dd0ba52140109b45569fc795783ca6663d54586f46",
        },
    },
}

PACK_ORDER = ("alpha", "beta", "gamma")
EXCLUDING = ("EXCLUDE_MEMBER", "EXCLUDE_WINDOW")

# Methods.
FLAG_CODES = "flag_codes"            # evaluated: the codes' Block 6 effect applied to Block 5's flags
NO_EMITTER = "no_b5_emitter"         # not evaluated unless Block 5's catalog has one of the codes
NOT_A_FLAG = "input_not_a_flag"      # not evaluated: the rule's input is a value or raw byte, not a flag
DISCLOSE_ONLY = "disclose_only"      # the rule removes nothing in Block 6 (a flag); Block 5 has no such condition
CLOCK_HOLD = "clock_hold"            # derived: Block 5's arm frequency gate is stricter than Block 6's hold
GAMMA_MIDPOINT = "gamma_midpoint"    # derived from neg8 reference counts in the flags

SIX_FIVE_TWENTY = (
    "calibration.acceptance_mismatch", "calibration.binding_failed", "calibration.bracket_acceptance_failed",
    "calibration.capture_invalid", "calibration.historical_custody_mismatch", "calibration.ledger_snapshot_refused",
    "calibration.no_bracket", "calibration.session_not_bound", "clock.systematic", "code.executed_differs_from_sealed",
    "code.identity_unmeasured", "instrument.precal_screen_failed", "lineage.plan_tree_digest_differs",
    "model.identity_inconsistent_in_window", "model.identity_mismatch", "model.identity_unmeasured",
    "model.identity_unpinned", "neg8.bound_not_derived", "neg8.screen_failed", "pack.identity_mismatch",
    "pack.identity_unmeasured", "records.malformed_flag_exclusion_possible", "roster.duplicate_run_id",
    "whole_window.member_failures_unreadable", "whole_window.verdict_absent",
)


@dataclass(frozen=True)
class Rule:
    rule_id: str
    section: str
    label: str
    change: str                      # new | changed | dropped
    scope: str                       # session | run
    method: str
    codes: tuple[str, ...] = ()
    b5_effect: str | None = None     # asserted against the catalogs for FLAG_CODES rows
    b6_effect: str | None = None
    counterparts: tuple[str, ...] = ()   # nearest Block 5 codes, counted for information (author's reading)
    reason: str = ""


RULES: tuple[Rule, ...] = (
    # §8.2 session exclusions and the §8.6 lines that feed them.
    Rule("8.2-P3", "§8.2 P3, §8.6 S-5", "b_op above the stop line (139 ms ALPHA and GAMMA; none for BETA)", "new",
         "session", NOT_A_FLAG, ("calibration.operative_bound_above_stop",), b6_effect="EXCLUDE_WINDOW",
         reason="needs each session's operative bound b_op (derived/bracket-binding.json), a value, not a flag; "
                "Block 5's flags carry no b_op line"),
    Rule("8.2-N1", "§8.2 N1", "calibration capture missing or its refit failing", "new", "session", NO_EMITTER,
         ("calibration.bracket_incomplete",), b6_effect="EXCLUDE_WINDOW",
         counterparts=("calibration.no_bracket", "calibration.capture_invalid"),
         reason="Block 5's harvest has no emitter for this code"),
    Rule("8.2-N2", "§8.2 N2", "fewer than 6 clean corpus runs or 2 surviving start or end references", "new",
         "session", NO_EMITTER, ("neg8.survivor_screen_undefined",), b6_effect="EXCLUDE_WINDOW",
         counterparts=("neg8.bound_not_derived",), reason="Block 5's harvest has no emitter for this code"),
    Rule("8.2-W1", "§8.2 W1", "model files differ from the registered files", "new", "session", NO_EMITTER,
         ("model.files_differ_from_registered",), b6_effect="EXCLUDE_WINDOW",
         counterparts=("model.identity_mismatch",), reason="Block 5's harvest has no emitter for this code"),
    Rule("8.2-W2", "§8.2 W2", "executed runtime stack differs from the registered one", "new", "session",
         NO_EMITTER, ("model.stack_differs_from_registered",), b6_effect="EXCLUDE_WINDOW",
         reason="Block 5's harvest has no emitter for this code"),
    Rule("8.2-W3", "§8.2 W3", "a number-bearing file changed without an executing review", "new", "session",
         NO_EMITTER, ("code.number_bearing_unreviewed",), b6_effect="EXCLUDE_WINDOW",
         counterparts=("code.executed_differs_from_sealed",), reason="Block 5's harvest has no emitter for this code"),
    Rule("8.2-D1", "§8.2 D1", "the drift screen fails on the surviving references", "new", "session", NO_EMITTER,
         ("neg8.survivor_screen_failed",), b6_effect="EXCLUDE_WINDOW", counterparts=("neg8.screen_failed",),
         reason="Block 5's harvest has no emitter for this code"),
    Rule("8.2-S1", "§8.2 S1", "structural failure (§4)", "new", "session", NO_EMITTER,
         ("structure.chain_crashed", "structure.missing_stage_bundles", "structure.no_capture_records",
          "structure.no_roster"), b6_effect="EXCLUDE_WINDOW", reason="Block 5's harvest has no emitter for these codes"),
    Rule("8.2-PRE", "§8.2, §8.7 item 3", "pre-check certain exclusion (a hold before t0, never a session loss)",
         "new", "session", NOT_A_FLAG, ("precheck.certain_exclusion",), b6_effect="EXCLUDE_WINDOW",
         reason="computed before t0 from the registered acceptance on a nominal synthetic session; no Block 5 "
                "flag carries it"),
    Rule("8.6-S7", "§8.6 S-7", "clock-rate hold at |r| > 5 ms / 335 s - 0.25 ppm = 14.675 ppm", "changed",
         "session", CLOCK_HOLD,
         reason="each session passed Block 5's arm frequency gate (|f| <= 3.6306 ppm, B5-REG §4.2), stricter than "
                "the hold; a session with clock.arm_unmeasured is not evaluated"),
    Rule("8.2-25", "§8.2", "25 of Block 5's 32 session-removing codes become flags", "changed", "session",
         FLAG_CODES, SIX_FIVE_TWENTY, b5_effect="EXCLUDE_WINDOW", b6_effect="DISCLOSE"),
    Rule("8.2-MID", "§8.2", "GAMMA: a lost midpoint reference no longer removes the session", "dropped",
         "session", GAMMA_MIDPOINT, ("neg8.midpoint_lost",)),
    # §8.3 run and unit exclusions.
    Rule("8.3.1-CEU", "§8.3 item 1", "member.cooldown_evidence_unverified becomes a flag", "changed", "run",
         FLAG_CODES, ("member.cooldown_evidence_unverified",), b5_effect="EXCLUDE_MEMBER", b6_effect="DISCLOSE"),
    Rule("8.3.1-BIN", "§8.3 item 1", "instrument.binary_identity_unmeasured becomes a flag", "changed", "run",
         FLAG_CODES, ("instrument.binary_identity_unmeasured",), b5_effect="EXCLUDE_MEMBER", b6_effect="DISCLOSE"),
    Rule("8.3.1-MAL", "§8.3 item 1", "records.malformed_flag_member_exclusion_possible becomes a flag", "changed",
         "run", FLAG_CODES, ("records.malformed_flag_member_exclusion_possible",), b5_effect="EXCLUDE_MEMBER",
         b6_effect="DISCLOSE"),
    Rule("8.3.1-CAP", "§8.3 item 1", "a cooldown that reaches its 300 s cap becomes a flag", "changed", "run",
         FLAG_CODES, ("member.cooldown_cap_hit",), b5_effect="EXCLUDE_MEMBER", b6_effect="DISCLOSE"),
    Rule("8.3.3-CON", "§8.3 item 3, S-8", "outside processor work in the request: a flag for round 1", "changed",
         "run", FLAG_CODES, ("contention.request_overlap",), b5_effect="EXCLUDE_MEMBER", b6_effect="DISCLOSE"),
    Rule("8.3.3-CONALT", "§8.3 item 3, S-8", "labelled alternative: C - k x 0.54 >= 0.0874 CPU-s", "new", "run",
         NOT_A_FLAG, reason="needs every run's monitor outside CPU-seconds C and interval count k, not flags"),
    Rule("8.3.2-SLP", "§8.3 item 2", "the machine slept more than 1 ms in the run", "new", "run", NO_EMITTER,
         ("sleep.in_run",), b6_effect="EXCLUDE_MEMBER", reason="Block 5's harvest has no emitter for this code"),
    Rule("8.3.2-AGT", "§8.3 item 2", "the run's unit overlapped an agent's presence", "new", "run", NO_EMITTER,
         ("agent.presence", "agent.presence_overlap", "agent.unit_overlap"), b6_effect="EXCLUDE_MEMBER",
         reason="Block 5's harvest has no emitter for these codes (Block 5 took no agent census)"),
    Rule("8.3.2-SKP", "§8.3 item 2", "skipped at the 1,500 s wait cap or by the spent wait budget", "new", "run",
         NO_EMITTER, ("idle.wait_cap_skip", "idle.wait_budget_skip"), b6_effect="EXCLUDE_MEMBER",
         counterparts=("member.admission_aborted",),
         reason="Block 5 had no waiting admission; its admission aborted the run instead (a kept rule)"),
    Rule("8.3.3-PST", "§8.3 item 3, S-9", "outside graphics or neural-engine power above P*, the desk exclusion",
         "new", "run", NOT_A_FLAG,
         reason="needs each bundle's preserved idle-baseline rails, raw bytes, not flags"),
    Rule("8.3.3-WAI", "§8.3 item 3, S-6", "a run admitted after waiting: disclosed only (d = +0.180 J)",
         "new", "run", DISCLOSE_ONLY, ("idle.waited",), b6_effect="DISCLOSE",
         reason="Block 5 had no waiting admission"),
)


class Refusal(Exception):
    """An input that does not match its pin or its expected shape."""


@dataclass
class Session:
    plan_id: str
    pack: str
    root: Path
    runs_all: set[str]
    runs_science: set[str]
    member_codes: dict[str, set[str]] = field(default_factory=dict)   # run_id -> codes
    session_codes: set[str] = field(default_factory=set)              # every code, any scope
    reference_lost: list[dict[str, Any]] = field(default_factory=list)  # structural fields only
    claim_usable: bool = False
    b5_members_excluded: int = 0
    digests: dict[str, str] = field(default_factory=dict)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def pack_of(plan_id: str) -> str:
    m = re.match(r"v5-b5-(alpha|beta|gamma)-a\d+-", plan_id)
    if not m:
        raise Refusal(f"plan_id_unparsed: {plan_id}")
    return m.group(1)


def load_catalog(path: Path) -> dict[str, dict[str, Any]]:
    data = json.loads(path.read_text())
    codes = data.get("codes")
    if not isinstance(codes, dict) or not codes:
        raise Refusal(f"catalog_shape: {path}")
    return codes


def load_session(root: Path) -> Session:
    roster = json.loads((root / "derived/roster.json").read_text())
    plan_id = roster["plan_id"]
    runs_all = {m["run_id"] for m in roster["members"]}
    runs_science = {m["run_id"] for m in roster["members"] if m.get("kind") == "science"}
    if len(runs_all) != len(roster["members"]):
        raise Refusal(f"roster_duplicate_run_id: {plan_id}")
    s = Session(plan_id=plan_id, pack=pack_of(plan_id), root=root, runs_all=runs_all, runs_science=runs_science)
    with (root / "derived/flags.jsonl").open() as fh:
        for line in fh:
            if not line.strip():
                continue
            flag = json.loads(line)
            code, scope = flag["code"], flag["scope"]
            if scope.get("plan_id") not in (None, plan_id):
                raise Refusal(f"flag_foreign_plan: {plan_id}: {scope.get('plan_id')}")
            s.session_codes.add(code)
            if scope.get("level") == "member":
                run_id = scope.get("run_id")
                if run_id not in runs_all:
                    raise Refusal(f"flag_run_not_in_roster: {plan_id}: {code}")
                s.member_codes.setdefault(run_id, set()).add(code)
            if code == "neg8.reference_lost":
                obs = flag.get("observed") or {}
                s.reference_lost.append({
                    "reference_counts": obs.get("reference_counts"),
                    "planned_reference_counts": obs.get("planned_reference_counts"),
                })
    excl = json.loads((root / "derived/exclusions.json").read_text())
    s.claim_usable = bool(excl.get("claim_usable"))
    s.b5_members_excluded = len(excl.get("members_excluded") or [])
    return s


def check_pins(sessions: list[Session], b5_path: Path, b6_path: Path) -> None:
    if sha256_file(b5_path) != PINS["b5_catalog"]:
        raise Refusal("b5_catalog_digest_mismatch")
    if sha256_file(b6_path) != PINS["b6_catalog"]:
        raise Refusal("b6_catalog_digest_mismatch")
    if sorted(s.plan_id for s in sessions) != sorted(PINS["sessions"]):
        raise Refusal("session_set_differs_from_released_three")
    for s in sessions:
        for rel, want in PINS["sessions"][s.plan_id].items():
            if s.digests.get(rel) != want:
                raise Refusal(f"session_input_digest_mismatch: {s.plan_id}: {rel}")


def check_rules_against_catalogs(b5: dict[str, Any], b6: dict[str, Any]) -> None:
    """Every rule's asserted effects hold, and every catalog change is covered by a rule."""
    for rule in RULES:
        for code in rule.codes:
            if rule.b6_effect and code in b6 and b6[code]["effect"] != rule.b6_effect:
                raise Refusal(f"rule_b6_effect_differs: {rule.rule_id}: {code}")
            if rule.method != GAMMA_MIDPOINT and rule.b6_effect and code not in b6:
                raise Refusal(f"rule_code_not_in_b6_catalog: {rule.rule_id}: {code}")
            if rule.b5_effect and b5.get(code, {}).get("effect") != rule.b5_effect:
                raise Refusal(f"rule_b5_effect_differs: {rule.rule_id}: {code}")
            if rule.method == NO_EMITTER and code in b5:
                # Block 5 could emit it: then it must be evaluated, not printed as not evaluated.
                raise Refusal(f"rule_marked_no_emitter_but_b5_has_code: {rule.rule_id}: {code}")
    covered = {c for r in RULES for c in r.codes}
    changed = {c for c in set(b5) & set(b6) if b5[c]["effect"] != b6[c]["effect"]}
    new_excluding = {c for c in set(b6) - set(b5) if b6[c]["effect"] in EXCLUDING}
    dropped_excluding = {c for c in set(b5) - set(b6) if b5[c]["effect"] in EXCLUDING}
    missing = sorted((changed | new_excluding | dropped_excluding) - covered)
    if missing:
        raise Refusal("catalog_change_not_covered_by_a_rule: " + ", ".join(missing))


def b5_excluded_runs(s: Session, b5: dict[str, Any]) -> dict[str, set[str]]:
    """run_id -> the Block 5 member-excluding codes it carries."""
    out: dict[str, set[str]] = {}
    for run_id, codes in s.member_codes.items():
        for code in codes:
            if code not in b5:
                raise Refusal(f"b5_flag_code_not_in_b5_catalog: {s.plan_id}: {code}")
        exc = {c for c in codes if b5[c]["effect"] == "EXCLUDE_MEMBER"}
        if exc:
            out[run_id] = exc
    return out


def per_pack(sessions: list[Session], fn) -> dict[str, Any]:
    return {s.pack: fn(s) for s in sessions}


def evaluate_rule(rule: Rule, sessions: list[Session], b5: dict[str, Any], b6: dict[str, Any]) -> dict[str, Any]:
    row: dict[str, Any] = {
        "rule_id": rule.rule_id, "section": rule.section, "label": rule.label, "change": rule.change,
        "scope": rule.scope, "method": rule.method, "codes": list(rule.codes),
        "b6_effect": rule.b6_effect or ({b6[c]["effect"] for c in rule.codes if c in b6} or {None}).pop(),
    }
    codes = set(rule.codes)

    def flagged_runs(s: Session, cs: set[str]) -> set[str]:
        return {r for r, have in s.member_codes.items() if have & cs}

    def flagged_session(s: Session, cs: set[str]) -> bool:
        return bool(s.session_codes & cs)

    if rule.counterparts:
        cp = set(rule.counterparts)
        row["b5_counterpart"] = {
            "codes": list(rule.counterparts),
            "runs": per_pack(sessions, lambda s: len(flagged_runs(s, cp))),
            "sessions_flagged": sum(flagged_session(s, cp) for s in sessions),
        }

    evaluable = rule.method in (FLAG_CODES, DISCLOSE_ONLY, CLOCK_HOLD, GAMMA_MIDPOINT)
    if rule.method == NO_EMITTER and codes & set(b5):
        evaluable = True   # unreachable while check_rules_against_catalogs holds; kept for safety
    row["evaluated"] = evaluable
    if not evaluable:
        row["reason"] = rule.reason
        return row

    if rule.method == CLOCK_HOLD:
        unmeasured = [s.pack for s in sessions if "clock.arm_unmeasured" in s.session_codes]
        row["sessions_removed"] = 0
        row["sessions_removed_by_pack"] = {s.pack: (None if s.pack in unmeasured else 0) for s in sessions}
        row["sessions_not_evaluated"] = unmeasured
        row["runs_removed"] = 0
        row["runs_removed_by_pack"] = {s.pack: 0 for s in sessions}
        row["basis"] = rule.reason
        if unmeasured:
            row["evaluated"] = "partial"
        return row

    if rule.method == GAMMA_MIDPOINT:
        gamma = [s for s in sessions if s.pack == "gamma"]
        lost = 0
        for s in gamma:
            hit = "neg8.midpoint_lost" in s.session_codes
            for ref in s.reference_lost:
                have = (ref.get("reference_counts") or {}).get("midpoint")
                plan = (ref.get("planned_reference_counts") or {}).get("midpoint")
                if have is not None and plan is not None and have < plan:
                    hit = True
            lost += hit
        row.update(runs_removed=0, runs_removed_by_pack={s.pack: 0 for s in sessions}, sessions_removed=0,
                   sessions_removed_by_pack={s.pack: 0 for s in sessions}, gamma_sessions=len(gamma),
                   b5_rule_would_remove_sessions=lost,
                   basis="rule dropped in Block 6; midpoint read from neg8.midpoint_lost and the reference counts "
                         "of neg8.reference_lost")
        return row

    # FLAG_CODES and DISCLOSE_ONLY: apply each code's Block 6 effect to Block 5's flags.
    runs_removed: dict[str, int] = {}
    sessions_removed: dict[str, int] = {}
    runs_flagged: dict[str, int] = {}
    runs_flagged_science: dict[str, int] = {}
    sessions_flagged: dict[str, int] = {}
    b5_runs_removed: dict[str, int] = {}
    b5_sessions_removed: dict[str, int] = {}
    for s in sessions:
        runs = flagged_runs(s, codes)
        runs_flagged[s.pack] = len(runs)
        runs_flagged_science[s.pack] = len(runs & s.runs_science)
        sessions_flagged[s.pack] = int(flagged_session(s, codes))
        b6_member = {c for c in codes if b6.get(c, {}).get("effect") == "EXCLUDE_MEMBER"}
        b6_window = {c for c in codes if b6.get(c, {}).get("effect") == "EXCLUDE_WINDOW"}
        b5_member = {c for c in codes if b5.get(c, {}).get("effect") == "EXCLUDE_MEMBER"}
        b5_window = {c for c in codes if b5.get(c, {}).get("effect") == "EXCLUDE_WINDOW"}
        runs_removed[s.pack] = len(flagged_runs(s, b6_member))
        sessions_removed[s.pack] = int(flagged_session(s, b6_window))
        b5_runs_removed[s.pack] = len(flagged_runs(s, b5_member))
        b5_sessions_removed[s.pack] = int(flagged_session(s, b5_window))
    row.update(
        runs_removed=sum(runs_removed.values()), runs_removed_by_pack=runs_removed,
        sessions_removed=sum(sessions_removed.values()), sessions_removed_by_pack=sessions_removed,
        runs_flagged=sum(runs_flagged.values()), runs_flagged_by_pack=runs_flagged,
        runs_flagged_science=sum(runs_flagged_science.values()),
        sessions_flagged=sum(sessions_flagged.values()),
        b5_runs_removed=sum(b5_runs_removed.values()), b5_runs_removed_by_pack=b5_runs_removed,
        b5_sessions_removed=sum(b5_sessions_removed.values()),
    )
    if rule.method == DISCLOSE_ONLY:
        row["basis"] = "a flag in Block 6, so it removes nothing; " + rule.reason
    return row


def replay(sessions: list[Session], b5: dict[str, Any], b6: dict[str, Any]) -> dict[str, Any]:
    sessions = sorted(sessions, key=lambda s: PACK_ORDER.index(s.pack))
    if len({s.pack for s in sessions}) != len(sessions):
        raise Refusal("two_sessions_of_one_pack")
    check_rules_against_catalogs(b5, b6)
    for s in sessions:
        if not s.claim_usable:
            raise Refusal(f"session_not_claim_usable: {s.plan_id}")
        b5_exc = b5_excluded_runs(s, b5)
        if len(b5_exc) != s.b5_members_excluded:
            raise Refusal(f"b5_member_exclusion_count_differs: {s.plan_id}: flags {len(b5_exc)} "
                          f"exclusions.json {s.b5_members_excluded}")
        if s.session_codes & {c for c, v in b5.items() if v["effect"] == "EXCLUDE_WINDOW"}:
            raise Refusal(f"usable_session_carries_b5_window_exclusion: {s.plan_id}")
    rows = [evaluate_rule(r, sessions, b5, b6) for r in RULES]

    # Summary: Block 6's catalog over Block 5's flags, every member code at once.
    summary_runs: dict[str, Any] = {}
    for s in sessions:
        b5_exc = b5_excluded_runs(s, b5)
        b6_exc = {r for r, have in s.member_codes.items()
                  if any(b6.get(c, {}).get("effect") == "EXCLUDE_MEMBER" for c in have)}
        released = set(b5_exc) - b6_exc
        summary_runs[s.pack] = {
            "runs": len(s.runs_all), "science_runs": len(s.runs_science),
            "b5_runs_removed": len(b5_exc), "b6_catalog_runs_removed": len(b6_exc),
            "kept_by_block6_changes": len(released),
            "kept_by_block6_changes_science": len(released & s.runs_science),
            "b6_catalog_sessions_removed": int(bool(
                {c for c in s.session_codes if b6.get(c, {}).get("effect") == "EXCLUDE_WINDOW"})),
        }
    totals = {k: sum(v[k] for v in summary_runs.values()) for k in next(iter(summary_runs.values()))}
    return {
        "schema": SCHEMA,
        "sessions": [{"plan_id": s.plan_id, "pack": s.pack, "runs": len(s.runs_all),
                      "science_runs": len(s.runs_science), "inputs_sha256": s.digests} for s in sessions],
        "rules": rows,
        "summary_by_pack": summary_runs,
        "summary_totals": totals,
        "not_evaluated": [r["rule_id"] for r in rows if r["evaluated"] is False],
    }


def _by_pack(d: dict[str, Any] | None) -> str:
    if not d:
        return ""
    return " (" + ", ".join("-" if d.get(p) is None else str(d[p]) for p in PACK_ORDER if p in d) + ")"


def render_markdown(result: dict[str, Any], *, commit: str, date: str) -> str:
    tot = result["summary_totals"]
    n_sessions = len(result["sessions"])
    runs, sci = tot["runs"], tot["science_runs"]
    lines = [
        "# S-16, Block 5's half: replay counts of Block 6's new or changed §8 rules",
        "",
        f"Script `scripts/b6_s16_block5_replay_counts.py` @ `{commit}`, run {date}. Counts only, from the released "
        "flags of Block 5's three usable sessions (RL-134 item 17). Per-pack counts are in the order ALPHA, BETA, "
        "GAMMA.",
        "",
        "| Session | Runs | Science runs | Inputs (flags.jsonl SHA-256) |",
        "|---|---|---|---|",
    ]
    for s in result["sessions"]:
        lines.append(f"| `{s['plan_id']}` | {s['runs']} | {s['science_runs']} | "
                     f"`{s['inputs_sha256'].get('derived/flags.jsonl', '')[:12]}…` |")
    lines += [
        "",
        f"| Rule | Change | Block 6 effect | Runs removed (of {runs}; {sci} science) | Sessions removed "
        f"(of {n_sessions}) | Block 5 flags of the code | Basis |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in result["rules"]:
        codes = ", ".join(f"`{c}`" for c in r["codes"][:4]) + (" and 21 more" if len(r["codes"]) > 4 else "")
        name = f"{r['section']}: {r['label']}" + (f" ({codes})" if codes else "")
        cp = r.get("b5_counterpart")
        cp_txt = ""
        if cp:
            cp_txt = (f"nearest Block 5 code {', '.join('`'+c+'`' for c in cp['codes'])}: "
                      f"{sum(cp['runs'].values())} runs, {cp['sessions_flagged']} sessions")
        if r["evaluated"] is False:
            lines.append(f"| {name} | {r['change']} | {r['b6_effect'] or '-'} | not evaluated | not evaluated | "
                         f"{cp_txt or '-'} | {r['reason']} |")
            continue
        if r["method"] in (FLAG_CODES, DISCLOSE_ONLY):
            b5txt = (f"{r['runs_flagged']} runs{_by_pack(r['runs_flagged_by_pack'])}, "
                     f"{r['runs_flagged_science']} science; {r['sessions_flagged']} sessions")
            if r["b5_runs_removed"] or r["b5_sessions_removed"]:
                b5txt += f"; Block 5 removed {r['b5_runs_removed']} runs, {r['b5_sessions_removed']} sessions"
            basis = r.get("basis", "evaluated from flags, Block 6 catalog effect")
        elif r["method"] == GAMMA_MIDPOINT:
            b5txt = (f"midpoint lost in {r['b5_rule_would_remove_sessions']} of {r['gamma_sessions']} GAMMA "
                     "sessions")
            basis = r["basis"]
        else:
            b5txt = "-"
            basis = r["basis"]
        sess = f"{r['sessions_removed']}{_by_pack(r['sessions_removed_by_pack'])}"
        if r.get("sessions_not_evaluated"):
            sess += f"; not evaluated: {', '.join(r['sessions_not_evaluated'])}"
        lines.append(f"| {name} | {r['change']} | {r['b6_effect'] or '-'} | "
                     f"{r['runs_removed']}{_by_pack(r['runs_removed_by_pack'])} | {sess} | {b5txt} | {basis} |")
    sp = result["summary_by_pack"]
    lines += [
        "",
        "Summary, Block 6's whole catalog over Block 5's flags (the not-evaluated rules excepted): Block 5 removed "
        f"{tot['b5_runs_removed']} of {runs} runs{_by_pack({p: v['b5_runs_removed'] for p, v in sp.items()})}; "
        f"Block 6's catalog removes {tot['b6_catalog_runs_removed']}"
        f"{_by_pack({p: v['b6_catalog_runs_removed'] for p, v in sp.items()})}; the changes keep "
        f"{tot['kept_by_block6_changes']} ({tot['kept_by_block6_changes_science']} science); sessions removed: "
        f"{tot['b6_catalog_sessions_removed']} of {n_sessions}.",
        "",
    ]
    return "\n".join(lines)


def section17_line(result: dict[str, Any], *, commit: str, date: str) -> str:
    tot = result["summary_totals"]
    rows = {r["rule_id"]: r for r in result["rules"]}
    n = len(result["sessions"])
    con = rows["8.3.3-CON"]
    other_four = sum(rows[k]["runs_flagged"] for k in ("8.3.1-CEU", "8.3.1-BIN", "8.3.1-MAL", "8.3.1-CAP"))
    sess25 = rows["8.2-25"]["sessions_flagged"]
    mid = rows["8.2-MID"]
    hold = rows["8.6-S7"]
    ne = [rows[k] for k in result["not_evaluated"]]
    ne_txt = "; ".join(f"{r['section']} ({', '.join('`'+c+'`' for c in r['codes']) or r['label']})" for r in ne)
    plan_ids = ", ".join(f"`{s['plan_id']}`" for s in result["sessions"])
    b6sha = (result.get("catalog_sha256") or {}).get("b6", "")[:8] or "unknown"
    if hold.get("sessions_not_evaluated"):
        hold_txt = f" ({', '.join(hold['sessions_not_evaluated'])} not evaluated: `clock.arm_unmeasured`)"
    else:
        hold_txt = " (each passed Block 5's stricter arm frequency gate)"
    evaluated = [r for r in result["rules"] if r["evaluated"] is not False]
    rem_runs = sum(r.get("runs_removed", 0) for r in evaluated)
    rem_sess = sum(r.get("sessions_removed", 0) for r in evaluated)
    con_by = ", ".join(str(con["runs_flagged_by_pack"][p]) for p in PACK_ORDER if p in con["runs_flagged_by_pack"])
    if other_four:
        four_txt = (f"of which {con['runs_flagged']} carry `contention.request_overlap` ({con_by}) and "
                    f"{other_four} carry the other four codes")
    else:
        four_txt = f"all `contention.request_overlap` ({con_by}; {con['runs_flagged_science']} science)"
    return (
        f"- {date}, §17-S16 (RL-134 item 17). **Kind.** Slot fill: S-16, Block 5's half. Read after the Block 5 "
        f"release (2026-11-08, `RUN_STATE.md` item 231); counts only, from the released flags of Block 5's {n} usable sessions ({plan_ids}; {tot['runs']} runs, "
        f"{tot['science_runs']} science), by `scripts/b6_s16_block5_replay_counts.py` @ `{commit}` under the Block 6 "
        f"catalog `{b6sha}…`. Where evaluated, the new or changed rules remove {rem_runs} of {tot['runs']} runs "
        f"and {rem_sess} of {n} sessions. The five run codes that become flags fire on "
        f"{tot['kept_by_block6_changes']} runs that Block 5 removed and Block 6 keeps, {four_txt}; Block 6's "
        f"catalog over Block 5's flags "
        f"removes {tot['b6_catalog_runs_removed']} runs where Block 5 removed {tot['b5_runs_removed']}. The 25 "
        f"session codes that become flags fire on {sess25} of {n} sessions; GAMMA's dropped midpoint rule would have "
        f"removed {mid['b5_rule_would_remove_sessions']} of {mid['gamma_sessions']}; the clock-rate hold holds "
        f"{hold['sessions_removed']} of {n}{hold_txt}; `idle.waited` is disclosed "
        f"only. Not evaluated from flags (no Block 5 emitter, or the input is not a flag): {ne_txt}. Outside the "
        f"pinned program; changes no Block 6 number."
    )


def git_head(path: Path) -> str:
    try:
        out = subprocess.run(["git", "-C", str(path), "rev-parse", "--short=9", "HEAD"], capture_output=True,
                             text=True, check=True)
        return out.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--b5-catalog", type=Path, required=True)
    ap.add_argument("--b6-catalog", type=Path, required=True)
    ap.add_argument("--session", type=Path, action="append", required=True, help="a Block 5 harvest root")
    ap.add_argument("--json-out", type=Path)
    ap.add_argument("--md-out", type=Path)
    ap.add_argument("--date", default=None, help="date for the §17 line (default: today, local)")
    ap.add_argument("--commit", default=None, help="script commit for the §17 line (default: git HEAD)")
    ap.add_argument("--unpinned", action="store_true", help="skip the released-input pins (synthetic fixtures)")
    args = ap.parse_args(argv)
    try:
        b5 = load_catalog(args.b5_catalog)
        b6 = load_catalog(args.b6_catalog)
        sessions = []
        for root in args.session:
            s = load_session(root)
            s.digests = {rel: sha256_file(root / rel) for rel in
                         ("derived/flags.jsonl", "derived/roster.json", "derived/exclusions.json")}
            sessions.append(s)
        if not args.unpinned:
            check_pins(sessions, args.b5_catalog, args.b6_catalog)
        result = replay(sessions, b5, b6)
    except Refusal as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 4
    except (OSError, KeyError, ValueError) as exc:
        print(f"refused: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 4
    import datetime as _dt
    date = args.date or _dt.date.today().isoformat()
    commit = args.commit or git_head(Path(__file__).resolve().parent)
    result["pinned"] = not args.unpinned
    result["catalog_sha256"] = {"b5": sha256_file(args.b5_catalog), "b6": sha256_file(args.b6_catalog)}
    md = render_markdown(result, commit=commit, date=date)
    line = section17_line(result, commit=commit, date=date)
    result["section17_line"] = line
    md += "\n## The §17 line (kind: slot fill)\n\n" + line + "\n"
    if args.json_out:
        args.json_out.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    if args.md_out:
        args.md_out.write_text(md)
    else:
        print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
