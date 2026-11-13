#!/usr/bin/env python3
"""Independent block-6 recompute (B6-REPL sections 9 to 11) and the S-13 comparator.

Only the Python standard library and the independent block-5 recompute
(scripts/independent_recompute_b5.py, loaded by file path) are used. Nothing is
imported from the analysis library, lane L9, the block-6 analysis driver, the
reducer or the validator. The block-6 rules are taken from the registration
text (docs/registrations/block6_replication_DRAFT.md) and the archived record
formats only:

- counting: the session's acceptance record (derived/b6-acceptance.json, the
  harvest's verdict) checked against the loop's attempt record (attempts.jsonl),
  never a block-5 exclusions claim_usable;
- kept units: roster units none of whose runs the acceptance record excludes
  (section 8.3: a removed quad run removes its quad);
- b_op: section 1.7 with block 6's s_bracket of 10.818 ms (section 3.3);
- the drift screen and allowance: section 1.8 (first 12 clean corpus runs in
  committed order, at least 6; at least 2 surviving start and end references;
  no spare references; a lost midpoint narrows the spread, it removes nothing);
- GAMMA's floor pairing: section 6.2, by registered round;
- per-session estimators: block 5's (section 9), from the block-5 script;
- section 9.5 lines, the section 10 summary and the section 11 reporting.

Agreement with the analysis programs is decided by `compare` under S-13
(section 12.3 item 4): each run's phase energy within 1 mJ; every printed
quantity, compared unrounded, within half a unit of its last printed digit.
Observed differences stay in restricted custody beside the bars and never set
them. Public outputs carry structure only.
"""
import argparse
import fnmatch
import hashlib
import json
import math
import os
from pathlib import Path
import re
import statistics
import sys
import tempfile
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from joulewise.b6_analysis_inputs import AuthenticatedInputs, InputRefusal
from joulewise.flags.catalog import load_catalog
from joulewise.flags.exclusions import compute as compute_exclusions

_B5_PATH = Path(__file__).resolve().with_name("independent_recompute_b5.py")
ROOT_DIR = _B5_PATH.parents[1]
B5_SHA256 = "d49103e884ccae47242b8efb91ea1f5764e4505a4ad5e54558cc42a399a2e4e0"


def load_pinned_b5(path=_B5_PATH):
    # Hash and execute the SAME bytes; a second loader read could race an edit.
    source = Path(path).read_bytes()
    if hashlib.sha256(source).hexdigest() != B5_SHA256:
        raise InputRefusal("b5_script_digest_mismatch")
    module = types.ModuleType("independent_recompute_b5_for_b6")
    module.__file__ = str(path)
    exec(compile(source, str(path), "exec"), module.__dict__)
    module.loaded_sha256 = hashlib.sha256(source).hexdigest()
    return module


B5 = load_pinned_b5()
get, objects, strings, mapping, finite = B5.get, B5.objects, B5.strings, B5.mapping, B5.finite

SCHEMA = "joulewise.independent_recompute_b6.v1"
PUBLIC_SCHEMA = "joulewise.independent_recompute_b6.public.v1"
TABLE_SCHEMA = "joulewise.b6_comparison_table.v1"
COMPARE_SCHEMA = "joulewise.b6_s13_comparison.v1"
COMPARE_PUBLIC_SCHEMA = "joulewise.b6_s13_comparison.public.v1"
ACCEPTANCE_SCHEMA = "joulewise.b6_acceptance.v1"
PACKS = ("ALPHA", "BETA", "GAMMA")
FLOOR_PACKS = ("ALPHA", "BETA")
MODELS = B5.MODELS
MODEL_TAG = {MODELS["ALPHA"]: "qwen3-1p7b", MODELS["BETA"]: "qwen3-8b"}
PHASE_LABEL = {"decode": "decode", "prefill": "prefill-p2048"}
REFERENCE_MODEL = "Qwen2.5-1.5B-Instruct-4bit"
# Registration section 3.3 (S-4): block 6's s_bracket, the D-125 floor that binds.
S_BRACKET_S = 0.010818
# Section 1.8: the clean corpus is the first 12 clean runs in committed order; 6 needed
# (threshold council 2026-10-12, row N2); 2 surviving start and end references needed.
CORPUS_CAP, CORPUS_MINIMUM, ENDPOINT_MINIMUM = 12, 6, 2
# Section 5.1 target; section 11.2 prints "short" below it.
TARGET_SESSIONS = 3
# Section 11.4 (i): sessions with a W1, W2, W3 or S1 condition never re-enter.
WRONG_DATA_CODES = frozenset({"model.files_differ_from_registered", "model.stack_differs_from_registered",
                              "code.number_bearing_unreviewed"})
LOAD_CODES = B5.LOAD_CODES
OUTCOME_WORDS = frozenset({"direction_supported", "unresolved", "not_resolvable", "not_estimable",
                           "replicated", "not replicated", "not_replicated", "positive", "negative",
                           "agree", "L1", "L2"})
SYNTHETIC_MARKER = "SYNTHETIC_BLOCK6_FIXTURE"
B6_FLAG_CODES = frozenset("""acceptance_record_missing acceptance_schema_unknown acceptance_session_mismatch
acceptance_pack_unknown loop_attempt_missing counting_disagrees acceptance_kept_count_mismatch
neg8_verdict_disagrees neg8_corpus_count_mismatch neg8_midpoint_lost neg8_reference_lost neg8_spare_present
neg8_idle_family_unavailable excluded_run_not_in_roster kept_unit_not_validated pairing_floor_from_block5
pairing_floor_unavailable pairing_provisional session_id_duplicate b_op_record_unparsed
b6_exclusions_disagree b6_exclusions_unclassified option_c_disagrees""".split())
FLAG_CODES = B5.FLAG_CODES | B6_FLAG_CODES
# Codes that reveal only structure (counts, presence, identity), never an energy-derived pass/fail.
PUBLIC_FLAG_CODES = frozenset("""archive_file_missing trace_plist_missing trace_plist_unreadable phase_events_ambiguous
unit_shape_invalid kept_unit_identity_mismatch cell_below_minimum b_op_from_record calibration_capture_name_fallback
member_pre_bound_missing member_pre_bound_mismatch acceptance_record_missing acceptance_schema_unknown
acceptance_session_mismatch acceptance_pack_unknown loop_attempt_missing counting_disagrees
acceptance_kept_count_mismatch neg8_corpus_count_mismatch neg8_midpoint_lost neg8_reference_lost neg8_spare_present
excluded_run_not_in_roster pairing_floor_from_block5 pairing_floor_unavailable pairing_provisional
session_id_duplicate neg8_survivor_count_mismatch kept_member_token_mismatch loo_kept_n_equals_minimum""".split())
# A failure on these leaves the comparison without a defined recompute side.
STOP_FLAG_CODES = B5.TRACE_STOP_FLAG_CODES | frozenset({
    "acceptance_record_missing", "acceptance_schema_unknown", "acceptance_session_mismatch",
    "acceptance_pack_unknown", "loop_attempt_missing", "counting_disagrees", "session_id_duplicate",
    "b_op_mismatch", "stored_energy_mismatch", "kept_unit_not_validated", "b6_exclusions_disagree",
    "b6_exclusions_unclassified", "option_c_disagrees", "acceptance_kept_count_mismatch",
    "neg8_verdict_disagrees", "neg8_corpus_count_mismatch", "meter_request_mismatch"})
WHOLE_MACHINE_NOT_COMPUTED = {"status": "not_computed", "reason": "synthetic unit fixture supplied no meter streams"}
BLOCK5_CODES_NOT_COMPUTED = {"status": "not_computed", "reason": "needs block 5's list of session-removing codes "
                             "beside the block-6 catalog; structure only, outside this script"}


class SyntheticOnlyRefusal(Exception):
    pass


def present(path):
    return path.is_file() or Path(str(path) + ".zst").is_file()


def session_input_pin(pins, archive):
    """Explicit relocated archive paths disambiguate production's shared basename."""
    exact = pins.get(str(Path(archive).absolute()))
    legacy = pins.get(Path(archive).name)
    if exact is not None and legacy is not None and exact != legacy:
        raise InputRefusal("session_input_pin_ambiguous")
    return exact if exact is not None else legacy


class Reader(B5.Reader):
    """The block-5 reader with a session scope and block-6 codes."""
    def __init__(self, pack, session, flags, inputs=None):
        super().__init__(pack, flags)
        self.session = session
        self.inputs = inputs

    def raw(self, path, scope, required=True):
        if self.inputs is None:
            return super().raw(path, scope, required)
        try:
            data = self.inputs.read(path)
            self.files.add(str(path))
            return data
        except FileNotFoundError:
            if required:
                self.flag("archive_file_missing", scope, "missing or unreadable")
            return None

    def flag(self, code, scope, detail):
        assert code in FLAG_CODES, code
        row = {"code": code, "pack": self.pack, "session": self.session, "scope": str(scope), "detail": detail}
        if row not in self.flags:
            self.flags.append(row)


class MemberPool(B5.MemberPool):
    """Pinned member builder with an external authenticated I/O seam at fork."""
    def __init__(self, workers, inputs):
        super().__init__(workers)
        self.inputs = inputs

    def _start(self):
        contexts = self.inputs

        class PoolReader(Reader):
            def __init__(self, pack, flags):
                super().__init__(pack, "", flags)

            def raw(self, path, scope, required=True):
                self.inputs = next((ctx for ctx in contexts if Path(path).absolute().is_relative_to(ctx.archive)), None)
                if contexts and self.inputs is None:
                    raise InputRefusal("input_outside_archive")
                return super().raw(path, scope, required)

        original = B5.Reader
        B5.Reader = PoolReader
        try:
            super()._start()
        finally:
            B5.Reader = original


def pack_of(pack_id):
    """Loop registrations say alpha/beta/gamma; rosters name the campaign directory."""
    text = str(pack_id or "").lower()
    if text in ("alpha", "beta", "gamma"):
        return text.upper()
    if "contrast" in text or "_vs_" in text:
        return "GAMMA"
    if "qwen3-1p7b" in text:
        return "ALPHA"
    if "qwen3-8b" in text:
        return "BETA"
    return None


def phase_of(cell_id):
    return "decode" if "decode" in cell_id else "prefill"


def check_synthetic(archive):
    """Under JW_B5_SYNTHETIC_ONLY=1 nothing but a marked synthetic fixture is opened."""
    if os.environ.get("JW_B5_SYNTHETIC_ONLY") == "1" and not (Path(archive) / SYNTHETIC_MARKER).is_file():
        raise SyntheticOnlyRefusal("JW_B5_SYNTHETIC_ONLY=1 and the archive carries no synthetic fixture marker")


class Session:
    """One block-6 session archive, read as block 5's analysis reads one window.

    Provides the attributes the block-5 estimator functions read from a window:
    pack, reader, b, neg8, exclusion_cells, members, diagnostic.
    """
    diagnostic = False

    def __init__(self, archive, flags, attempts=None, claim_root=None, bound_root=None, reharvested=None,
                 inputs=None, pool=None, input_pin=None):
        self.archive = Path(archive)
        self.pool, self.inputs = pool, inputs
        self.input_pin = input_pin or {}
        self.reharvested = mapping(reharvested)
        check_synthetic(self.archive)
        if inputs is None and not (self.archive / SYNTHETIC_MARKER).is_file():
            raise InputRefusal("authenticated_inputs_required")
        self.reader = r = Reader("", "", flags, inputs)
        self.acceptance = r.json(self.archive / "derived/b6-acceptance.json", "derived/b6-acceptance.json")
        self.roster = r.json(self.archive / "derived/roster.json", "derived/roster.json")
        self.harvest = r.json(self.archive / "harvest.json", "harvest.json", False)
        # Bind the final session ID (the copied plan's outer ID) before any
        # session flag is raised, so every stop flag is filed under it. The
        # bracket ID is kept only for the harvest comparison below.
        self.bracket_session_id = (self.acceptance.get("session_id") or self.harvest.get("session_id")
                                   or self.archive.name)
        self.session_id = r.session = self.bracket_session_id
        self.pack = pack_of(self.acceptance.get("pack_id")) or pack_of(self.roster.get("pack_id"))
        r.pack = self.pack or ""
        self.plan_refused = not self.bind_plan()
        if not self.acceptance:
            r.flag("acceptance_record_missing", "session", "no readable acceptance record")
        elif self.acceptance.get("schema") != ACCEPTANCE_SCHEMA:
            r.flag("acceptance_schema_unknown", "session", {"schema": self.acceptance.get("schema")})
        if self.pack is None:
            r.flag("acceptance_pack_unknown", "session", {"pack_id": self.acceptance.get("pack_id")})
        roster_pack = pack_of(self.roster.get("pack_id"))
        if roster_pack is not None and self.pack is not None and roster_pack != self.pack:
            r.flag("acceptance_session_mismatch", "session", {"acceptance_pack": self.pack, "roster_pack": roster_pack})
        if self.harvest.get("session_id") not in (None, self.bracket_session_id):
            r.flag("acceptance_session_mismatch", "session", {"harvest_session_id": self.harvest.get("session_id")})
        self.claim_root = Path(claim_root) if claim_root else self.archive / "sources/claim-runs"
        self.bound_root = Path(bound_root) if bound_root else self.archive / "sources/bound-runs"
        self.attempt = self.loop_attempt(attempts)
        self.round = self.attempt.get("round") if self.attempt else None
        self.counting, self.loop_status = self.decide_counting()
        self.members, self.compared_run_ids = {}, set()
        self.units, self.roster_ids = {}, set()
        for m in objects(self.roster.get("members")):
            if not isinstance(m.get("run_id"), str):
                continue
            self.roster_ids.add(m["run_id"])
            if m.get("kind", "science") != "science":
                continue
            for u in objects(m.get("units")):
                if not all(isinstance(u.get(k), str) for k in ("cell_id", "stratum", "unit_id")):
                    r.flag("unit_shape_invalid", "roster", "malformed unit identity")
                    continue
                self.units.setdefault((u["cell_id"], u["stratum"], u["unit_id"]), []).append(m["run_id"])
        self.verdict_members = set(self.roster_ids)
        self.excluded_codes = {}
        for item in objects(self.acceptance.get("excluding")):
            if item.get("scope") == "member" and isinstance(item.get("run_id"), str):
                self.excluded_codes.setdefault(item["run_id"], set()).add(str(item.get("code")))
        self.excluded = set(self.excluded_codes)
        for run_id in sorted(self.excluded - self.roster_ids):
            r.flag("excluded_run_not_in_roster", run_id, "acceptance excludes a run the roster does not name")
        self.window_codes = sorted({str(item.get("code")) for item in objects(self.acceptance.get("excluding"))
                                    if item.get("scope") != "member"})
        self.flag_rows = (r.lines(self.archive / "derived/flags.jsonl", "derived/flags.jsonl")
                          if present(self.archive / "derived/flags.jsonl") else [])
        if present(self.archive / "derived/b6-flags.jsonl"):
            self.flag_rows += r.lines(self.archive / "derived/b6-flags.jsonl", "derived/b6-flags.jsonl")
        self.flag_rows += objects(self.acceptance.get("emitted_flags"))
        self.exclusion_check = self.check_exclusions()
        self.hazards = None
        if inputs:
            from joulewise.b6_analysis_hazards import desk_hazards
            sizing_bytes = (ROOT_DIR / "configs/b6/recompute/hazard_sizing.json").read_bytes()
            if hashlib.sha256(sizing_bytes).hexdigest() != "bf399bec4195b9237f53c747c6fc9cd24066610eba933a0fad767534d970d29b":
                raise InputRefusal("hazard_sizing_digest_mismatch")
            self.hazards = desk_hazards(self, json.loads(sizing_bytes))
            for rid in self.hazards["power_removed"]:
                self.excluded_codes.setdefault(rid, set()).add("registered P* desk exclusion")
            self.excluded = set(self.excluded_codes)
        self.assist = self.runs_with("battery.assist")
        self.waited = self.runs_with("idle.waited")
        self.exclusion_cells = self.kept_cells(validate_record=not bool(self.hazards))
        self.b = self.calibration()
        if self.pool:
            for row in objects(self.roster.get("members")):
                rid = row["run_id"]
                which = "corpus" if B5.role(rid) == "corpus" else ("science" if row.get("kind") == "science" else B5.role(rid))
                root = self.bound_root if which == "corpus" else self.claim_root
                self.pool.prefetch(self.pack, root, rid, self.b["b_op_s"], which)
        self.neg8 = self.screen()

    def check_exclusions(self):
        """C3: sealed compute, B6 catalog, no B5 pack-scoped exceptions."""
        path = ROOT_DIR / "configs/b6/flag_catalog_b6.json"
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        if sha != "b5bce6c64bbc1d079ecf6fed02bf4c214b76a8f7d279d44eea5984e4a389a42b":
            raise InputRefusal("b6_catalog_digest_mismatch")
        spans = self.reader.json(self.archive / "withheld/spans.json", "spans", False)
        spans = mapping(spans.get("spans", spans))
        spans = {rid: {"monotonic_ns": row.get("monotonic_ns", row.get("member"))}
                 for rid, row in spans.items()}
        derived = compute_exclusions(self.flag_rows, self.roster, spans, load_catalog(path), pack_scoped=False)
        members = {m["run_id"]: set(m["codes"]) for m in derived["members_excluded"]}
        reasons = set(derived["reasons"])
        # Never read derived.claim_usable: B6 counting comes from acceptance and loop.
        cells = {c["cell_id"]: c["kept_units"] for c in derived["cells"]}
        same = (members == self.excluded_codes and reasons == set(self.window_codes)
                and cells == {cid: cell["kept_units"] for cid, cell in self.kept_cells().items()})
        if not same:
            self.reader.flag("b6_exclusions_disagree", "session", "catalog re-derivation differs from acceptance")
        if derived["release_blocked"] or derived["flag_counts"]["unmatched_member"]:
            self.reader.flag("b6_exclusions_unclassified", "session", "unclassified or unmatched flag")
        return {"status": "agrees" if same else "disagrees", "catalog_sha256": sha,
                "members_excluded": derived["members_excluded"], "reasons": derived["reasons"]}

    def runs_with(self, code):
        return {get(f, "scope", "run_id") for f in self.flag_rows if f.get("code") == code
                and isinstance(get(f, "scope", "run_id"), str)}

    def bind_plan(self):
        # The collection writers identify acceptance/harvest by the ledger
        # bracket, while the loop records the enclosing plan's session ID.
        # Bind them through the copied, authenticated plan, never a suffix
        # convention or an archive directory name. Legacy toy inputs omit it.
        # Returns False (session keeps the bracket ID) when the plan refuses.
        plan_path = self.archive / "sources/night-custody/night_plan.json"
        if present(plan_path):
            plan = mapping(self.reader.json(plan_path, "night_plan"))
            bracket = get(plan, "hazard_window", "bindings", "bracket_session_id")
            outer = plan.get("plan_id")
            if not isinstance(outer, str) or not outer or bracket != self.session_id:
                self.reader.flag("acceptance_session_mismatch", "session",
                                 {"plan_id": outer, "bracket_session_id": bracket})
                return False
            self.session_id = self.reader.session = outer
        return True

    def loop_attempt(self, attempts):
        if getattr(self, "plan_refused", False):
            return None
        if attempts is None:
            return None
        rows = [a for a in attempts if a.get("session_id") == self.session_id]
        if len(rows) != 1:
            self.reader.flag("loop_attempt_missing", "session", {"rows": len(rows)})
            return None
        return rows[0]

    def decide_counting(self):
        """Section 4, from the acceptance record; the loop's attempt record must agree."""
        recorded = self.acceptance.get("counting")
        counting = recorded is True and self.acceptance.get("verdict") == "ACCEPT" \
            and self.acceptance.get("physics_stop") is not True
        if self.attempt is None:
            return counting, None
        key = (self.pack or "").lower()
        # The loop keeps re-harvest corrections in its state, leaving attempts.jsonl append-only.
        outcomes = mapping(self.reharvested.get(self.session_id, self.attempt.get("outcomes")))
        status = get(outcomes, key, "status", default=get(outcomes, self.pack or "", "status"))
        if (status == "counting") != counting:
            self.reader.flag("counting_disagrees", "session", {"loop_status": status, "acceptance_counting": recorded})
            return False, status
        return counting, status

    def kept_cells(self, validate_record=True):
        cells = {}
        for (cid, stratum, uid), ids in sorted(self.units.items()):
            cell = cells.setdefault(cid, {"kept_units": {}, "dropped_units": []})
            codes = sorted({c for i in ids for c in self.excluded_codes.get(i, ())})
            if codes:
                cell["dropped_units"].append({"unit_id": uid, "stratum": stratum, "codes": codes})
                cell["kept_units"].setdefault(stratum, [])
            else:
                cell["kept_units"].setdefault(stratum, []).append(uid)
        recorded = mapping(self.acceptance.get("cells")) if validate_record else {}
        for cid, cell in cells.items():
            if cid not in recorded:
                continue
            own = {s: len(v) for s, v in cell["kept_units"].items()}
            value = recorded[cid]
            if isinstance(value, dict):
                same = all(value.get(s) == n for s, n in own.items())
            else:
                same = value == sum(own.values())
            if not same:
                self.reader.flag("acceptance_kept_count_mismatch", cid, {"own": own, "recorded": value})
        return cells

    def member(self, run_id, member_role="science", *, compared=False):
        if compared:
            self.compared_run_ids.add(run_id)
        if run_id not in self.members:
            root = self.bound_root if member_role == "corpus" else self.claim_root
            built = self.pool.take(self.pack, root, run_id, self.b["b_op_s"], member_role) if self.pool else None
            if built is None:
                m = B5.Member(root / run_id, run_id, self.reader, self.b["b_op_s"], member_role)
            else:
                state, rows, files = built
                m = B5.Member.__new__(B5.Member)
                m.__dict__.update(state)
                m.reader = self.reader
                for row in rows:
                    self.reader.flag(row["code"], row["scope"], row["detail"])
                self.reader.files.update(files)
            self.members[run_id] = m
            pre = self.b["b_pre_s"]
            if member_role == "science" and not finite(m.bpre):
                self.reader.flag("member_pre_bound_missing", run_id, {"session_s": pre, "member_s": m.bpre})
            elif member_role == "science" and finite(pre) and m.bpre != pre:
                self.reader.flag("member_pre_bound_mismatch", run_id, {"session_s": pre, "member_s": m.bpre})
        return self.members[run_id]

    def select(self, cell_id, stratum, chosen=None, compare=True):
        units = B5.Window.select(self, cell_id, stratum, chosen, compare)
        if chosen is None:
            declared = set(get(self.exclusion_cells, cell_id, "kept_units", stratum, default=[]))
            dropped = sorted(declared - {u for u, _ in units})
            if dropped:
                self.reader.flag("kept_unit_not_validated", cell_id + "/" + stratum, {"unit_ids": dropped})
        return units

    def calibration(self):
        """Section 1.7: b_op = max(pre, post) + max(|post - pre|, s_bracket)."""
        r = self.reader
        binding = r.json(self.archive / "derived/bracket-binding.json", "derived/bracket-binding.json", False)
        inventory = [(p, r.json(p, "calibration/" + p.parent.name)) for p in
                     sorted((self.claim_root / "instrument_validation").glob("*/instrument_evidence.json"))]
        captures = {}
        for slot in ("pre", "post"):
            attempt = get(binding, "endpoints", slot, "attempt_id")
            matches = [(p, c) for p, c in inventory if isinstance(attempt, str)
                       and c.get("attempt_id", c.get("validation_id")) == attempt]
            if not matches:
                matches = [(p, c) for p, c in inventory if p.parent.name.endswith("-cal-" + slot)]
                if matches:
                    r.flag("calibration_capture_name_fallback", "cal-" + slot, "binding absent or names no capture")
            if len(matches) == 1:
                value = matches[0][1].get("b_fiducial_s")
                if finite(value) and value >= 0:
                    captures[slot] = value
                else:
                    r.flag("nonfinite_value", "cal-" + slot, "invalid fiducial bound")
            else:
                r.flag("archive_file_missing", "cal-" + slot, "need exactly one capture")
        recorded_cal = mapping(self.acceptance.get("calibration"))

        def decimal(key):
            value = recorded_cal.get(key)
            try:
                result = float(value) if value is not None else None
            except (TypeError, ValueError):
                r.flag("b_op_record_unparsed", "session", {"field": key})
                return None
            return result if finite(result) else None
        recorded = decimal("operative_bound_s")
        pre, post = captures.get("pre"), captures.get("post")
        source = "captures"
        if pre is None or post is None:
            if self.inputs is not None:
                raise InputRefusal("calibration_capture_missing")
            pre, post = decimal("pre_s"), decimal("post_s")
            source = "acceptance_record"
            r.flag("b_op_from_record", "session", "capture record missing; the acceptance record's captures used")
        bop = drift = None
        if finite(pre) and finite(post):
            if self.inputs is not None and not finite(recorded):
                raise InputRefusal("calibration_acceptance_bound_missing")
            drift = abs(post - pre)
            bop = max(pre, post) + max(drift, S_BRACKET_S)
            # Same unrounded relative bar as block 5's b_op check (1e-6 relative).
            if finite(recorded) and abs(bop - recorded) > 1e-6 * abs(bop):
                r.flag("b_op_mismatch", "session", {"own_s": bop, "recorded_s": recorded})
        return {"b_pre_s": pre, "b_post_s": post, "b_op_s": bop, "b_op_recorded_s": recorded,
                "drift_s": drift, "s_bracket_s": S_BRACKET_S, "source": source}

    def reference(self, run_id, which):
        m = self.member(run_id, which, compared=True)
        clean = (run_id not in self.excluded and m.usable and m.model == REFERENCE_MODEL
                 and finite(m.energies.get("request")))
        return m if clean else None

    def screen(self):
        """Section 1.8 drift screen and allowance, on the survivors."""
        r = self.reader
        corpus_ids = sorted({p.parent.name for p in self.bound_root.glob("neg8-refcorpus-r*/metadata.json")}
                            | {i for i in self.roster_ids if B5.role(i) == "corpus"},
                            key=lambda i: (B5.ordinal(i), i))
        corpus = []
        for run_id in corpus_ids:
            if not (self.bound_root / run_id / "metadata.json").is_file():
                continue
            m = self.reference(run_id, "corpus")
            if m is not None:
                corpus.append(m)
            if len(corpus) == CORPUS_CAP:
                break
        slots = {"start": [], "midpoint": [], "end": []}
        planned = {"start": 0, "midpoint": 0, "end": 0}
        for run_id in sorted(self.roster_ids, key=lambda i: (B5.ordinal(i), i)):
            which = B5.role(run_id)
            if which not in slots:
                continue
            if "spare" in run_id:
                r.flag("neg8_spare_present", run_id, "block 6 runs no spare references (section 3.2 item 4)")
                continue
            planned[which] += 1
            if (self.claim_root / run_id / "metadata.json").is_file():
                m = self.reference(run_id, which)
                if m is not None:
                    slots[which].append(m)
        counts = {k: len(v) for k, v in slots.items()}
        if counts["start"] < planned["start"] or counts["end"] < planned["end"]:
            r.flag("neg8_reference_lost", "session", {"survivors": counts, "planned": planned})
        if counts["midpoint"] < planned["midpoint"] or not planned["midpoint"]:
            r.flag("neg8_midpoint_lost", "session", {"survivors": counts["midpoint"]})
        result = {"source": "survivor_screen_b6", "corpus_n": len(corpus), "corpus_ids": [m.run_id for m in corpus],
                  "survivor_ids": [m.run_id for k in slots for m in slots[k]],
                  "n_start": counts["start"], "n_mid": counts["midpoint"], "n_end": counts["end"],
                  "verdict": None, "reason": None, "families": {},
                  "start_mean_j": None, "midpoint_j": None, "end_mean_j": None, "bound_j": None,
                  "spread_j": None, "allowance_j": None}
        if len(corpus) < CORPUS_MINIMUM:
            result.update(verdict="undefined", reason="corpus_insufficient")
        elif counts["start"] < ENDPOINT_MINIMUM or counts["end"] < ENDPOINT_MINIMUM:
            result.update(verdict="undefined", reason="references_insufficient")
        else:
            passed = True
            for family in ("gross", "idle_subtracted"):
                energy = (lambda m: m.energies["request"]) if family == "gross" else idle_subtracted
                values = [energy(m) for m in corpus] + [energy(m) for k in slots for m in slots[k]]
                if not all(finite(v) for v in values):
                    r.flag("neg8_idle_family_unavailable", "session", "an idle baseline power is missing")
                    if self.inputs:
                        raise InputRefusal("neg8_idle_family_unavailable")
                    result["families"][family] = {"status": "not_computed", "reason": "idle_baseline_unavailable"}
                    continue
                bound = B5.neg8_bound([energy(m) for m in corpus], counts["start"], counts["end"])
                means = {k: statistics.fmean(energy(m) for m in v) if v else None for k, v in slots.items()}
                difference = abs(means["end"] - means["start"])
                spread, allowance = B5.drift_allowance(means["start"], means["midpoint"], means["end"],
                                                       bound["bound_j"])
                result["families"][family] = {**bound, "start_mean_j": means["start"], "midpoint_j": means["midpoint"],
                                              "end_mean_j": means["end"], "endpoint_difference_j": difference,
                                              "spread_j": spread, "allowance_j": allowance,
                                              "passed": difference <= bound["bound_j"]}
                passed = passed and difference <= bound["bound_j"]
            gross = result["families"]["gross"]
            result.update(verdict="passed" if passed else "failed",
                          **{k: gross[k] for k in ("start_mean_j", "midpoint_j", "end_mean_j", "bound_j",
                                                   "spread_j", "allowance_j", "t", "s_j")})
        recorded = mapping(self.acceptance.get("neg8"))
        if recorded.get("verdict") not in (None, "pending") and recorded.get("verdict") != result["verdict"]:
            r.flag("neg8_verdict_disagrees", "session", {"own": result["verdict"], "recorded": recorded.get("verdict")})
        survivors = recorded.get("survivors")
        if isinstance(survivors, dict) and survivors != counts:
            r.flag("neg8_survivor_count_mismatch", "session", {"own": counts, "recorded": survivors})
        if recorded.get("corpus_clean_n") not in (None, len(corpus)):
            r.flag("neg8_corpus_count_mismatch", "session", {"own": len(corpus), "recorded": recorded.get("corpus_clean_n")})
        return result

    def structure_group(self):
        """Section 11.4 (i): the session's W1, W2, W3 or S1 condition, if any."""
        codes = set(self.window_codes) | set(strings(self.acceptance.get("structural_failures")))
        groups = sorted({"S1" if c.startswith("structure.") else "W" for c in codes
                         if c.startswith("structure.") or c in WRONG_DATA_CODES})
        return groups


def idle_subtracted(member):
    """Gross request energy less the run's idle-baseline power over its request (section 1.8).

    Lead decision 3: the idle power is the block-5 recompute's REG 5.8 source (elapsed_ns-weighted
    rich idle telemetry), for consistency between the blocks.
    """
    power = B5.rail_idle_power(member)
    if not finite(power) or "request" not in member.edges:
        return None
    onset, offset = member.edges["request"]
    return member.energies["request"] - power * (offset - onset)


def read_attempts(path, flags):
    if path is None:
        return None
    reader = Reader("", "loop", flags)
    return reader.lines(Path(path), "loop/attempts.jsonl")


def read_reharvested(path, flags):
    """The loop state's re-harvest corrections ({session_id: outcomes}), if a state file is given."""
    if path is None:
        return {}
    return mapping(Reader("", "loop", flags).json(Path(path), "loop/state.json").get("reharvested"))


# ---------------------------------------------------------------- per-session estimators

def dominance_rows(floors):
    ratios, common, failed = {}, {}, []
    for key, floor in floors.items():
        ratio = floor["R"]
        # PLAN 6: branch dominance at R >= 2 (a doubled point floor).
        ratios[key] = {"numerator_j": floor["corner_widened_unguarded_floor_j"],
                       "denominator_j": floor["point_unguarded_floor_j"], "R": ratio,
                       "pass": finite(ratio) and ratio >= 2, "n": floor["n"]}
        if not ratios[key]["pass"]:
            failed.append(key)
        if key.endswith("comparative"):
            cm = floor["R_cm"]
            common[key.rsplit("/", 1)[0]] = {"numerator_j": floor.get("common_mode_numerator_j"),
                                             "denominator_j": floor["point_unguarded_floor_j"], "R_cm": cm,
                                             "pass": finite(cm) and cm >= 2, "n": floor["n"]}
            if not common[key.rsplit("/", 1)[0]]["pass"]:
                failed.append(key.rsplit("/", 1)[0] + "/common_mode")
    return {"ratios": ratios, "common_mode": common, "failed": sorted(failed)}


def unit_codes(session, cid):
    return {(d["stratum"], d["unit_id"]): set(d["codes"]) for d in session.exclusion_cells.get(cid, {}).get("dropped_units", [])}


def subset_estimate(session, cid, selected, *, gamma):
    phase = phase_of(cid)
    if gamma:
        stats = B5.contrast_stats([B5.quad_difference(ms, phase) for _, ms in selected["quad"]])
        row = {k: stats[k] for k in ("n", "dbar_j", "s_d_j", "se_j", "t_star", "metrology_interval_j")}
        row["status"] = "computed" if stats["n"] >= 5 else "below_registered_minimum"
        return row
    return B5.make_reported(session, cid, selected["repeat"], selected["quad"], None)


def labelled_lines(session, cid, selected):
    """Section 9.5 items 1, 2 and 8 for one cell: restored and removed unit sets."""
    gamma = session.pack == "GAMMA"
    lines = {}
    dropped = unit_codes(session, cid)
    restorable = {key for key, codes in dropped.items() if codes and codes <= LOAD_CODES}
    triggered = {key for key, codes in dropped.items() if codes & LOAD_CODES}
    # The line is always printed (so its keys are fixed), restoring nothing when no unit was triggered.
    restored = {s: session.select(cid, s, [u for u, _ in units] + [u for (st, u) in restorable if st == s], False)
                for s, units in selected.items()}
    row = subset_estimate(session, cid, restored, gamma=gamma)
    row["restored_by_stratum"] = {s: len(restored[s]) - len(selected[s]) for s in selected}
    row["codes"] = sorted({c for key in triggered for c in dropped[key] & LOAD_CODES})
    lines["load_sensitivity"] = row
    for name, runs in (("battery_assist", session.assist), ("waited_runs", session.waited)):
        kept = {s: [(u, ms) for u, ms in units if not any(m.run_id in runs for m in ms)] for s, units in selected.items()}
        row = subset_estimate(session, cid, kept, gamma=gamma)
        row["removed_by_stratum"] = {s: len(selected[s]) - len(kept[s]) for s in selected}
        lines[name] = row
    if session.hazards:
        removed = set(session.hazards["processor_alternative_removed"])
        kept = {s: [(u, ms) for u, ms in units if not any(m.run_id in removed for m in ms)] for s, units in selected.items()}
        row = subset_estimate(session, cid, kept, gamma=gamma)
        row.update(label=session.hazards["processor_label"],
                   removed_by_stratum={s: len(selected[s]) - len(kept[s]) for s in selected})
        lines["outside_processor_alternative"] = row
    return lines


def single_step_cell(session, cid, chosen, registered_mean):
    phase = phase_of(cid)
    members = B5.flatten(chosen["repeat"] + chosen["quad"])
    values = {m.run_id: B5.single_step_member(m) for m in members}
    missing = sorted(m.run_id for m in members if not finite(get(values, m.run_id, "energy_j", phase)))
    row = {"label": B5.RECONSTRUCTION_LABEL, "phase": phase, "unavailable_members": missing,
           "n_r": len(chosen["repeat"]), "n_b": len(chosen["quad"]), "mean_j": None, "h_j": None,
           "shift_j": None, "registered_estimator1_mean_j": registered_mean}
    if missing:
        return {**row, "status": "not_computed", "reason": "reconstruction unavailable for a kept member; units unchanged"}
    recon = B5.diagnostic_estimate([values[ms[0].run_id]["energy_j"][phase] for _, ms in chosen["repeat"]],
                                   [statistics.fmean(values[m.run_id]["energy_j"][phase] for m in ms)
                                    for _, ms in chosen["quad"]])
    row.update(recon)
    if finite(recon["mean_j"]) and finite(registered_mean):
        row["shift_j"] = recon["mean_j"] - registered_mean
    return row


def floor_session(session):
    """Estimators 1 to 3 and the section 9.5 lines for one ALPHA or BETA session."""
    out = {"reported_cells": {}, "floors": {}, "floor_cells": {}, "p42": {}, "lines": {}}
    selections = {}
    tag = "qwen3-1p7b" if session.pack == "ALPHA" else "qwen3-8b"
    basis = B5.reference_scale_basis(session)
    scaled = {"label": B5.SCALED_ALLOWANCE_LABEL, "basis": basis, "reported_cells": {}, "floors": {}, "floor_cells": {}}
    for cell in objects(session.roster.get("cells")):
        cid = cell.get("cell_id")
        if not isinstance(cid, str) or not cid.endswith("-" + tag):
            session.reader.flag("kept_unit_identity_mismatch", str(cid), "cell model disagrees with pack")
            continue
        chosen = {s: session.select(cid, s) for s in ("repeat", "quad")}
        selections[cid] = chosen
        if "p42" in cid:
            out["p42"][cid] = {"status": "expected_unresolvable", "members_with_3plus_records":
                               sum(m.counts.get("prefill", 0) >= 3 for s in chosen for m in B5.flatten(chosen[s]))}
            continue
        phase = phase_of(cid)
        model = MODELS[session.pack]
        reported = B5.make_reported(session, cid, chosen["repeat"], chosen["quad"], 5)
        out["reported_cells"][cid] = reported
        forms, cell_floor = B5.make_floors(session, phase, chosen, reported)
        prefix = model + "/" + phase
        for form, result in forms.items():
            out["floors"][prefix + "/" + form] = result
        out["floor_cells"][prefix] = cell_floor
        lines = labelled_lines(session, cid, chosen)
        lines["single_step_reconstruction"] = single_step_cell(session, cid, chosen, reported["mean_j"])
        lines["whole_machine"] = WHOLE_MACHINE_NOT_COMPUTED
        out["lines"][cid] = lines
        members = B5.flatten(chosen["repeat"] + chosen["quad"])
        duration = (0.2 * statistics.fmean(ms[0].edges[phase][1] - ms[0].edges[phase][0]
                                          for _, ms in chosen["repeat"])
                    + 0.8 * statistics.fmean(statistics.fmean(m.edges[phase][1] - m.edges[phase][0] for m in ms)
                                              for _, ms in chosen["quad"])) if all(chosen.values()) else None
        plain_duration = statistics.fmean(m.edges[phase][1] - m.edges[phase][0] for m in members) if members else None
        factor = B5.allowance_factor(reported["mean_j"], duration, basis)
        scaled["reported_cells"][cid] = {**B5.scaled_reported(reported, factor, session.neg8["allowance_j"]),
                                         "E_j": reported["mean_j"], "T_s": duration}
        if plain_duration != duration:
            scaled["reported_cells"][cid]["plain_mean_alternative"] = {
                "label": "plain member mean T alternative (RL-25 8a)", "T_s": plain_duration,
                "factor": B5.allowance_factor(reported["mean_j"], plain_duration, basis)}
        for form in ("absolute", "comparative"):
            scaled["floors"][prefix + "/" + form] = B5.scaled_floor(out["floors"][prefix + "/" + form], factor)
        a, c = (scaled["floors"][prefix + "/" + f]["drift_widened_guarded_floor_j"] for f in ("absolute", "comparative"))
        scaled["floor_cells"][prefix] = {"factor": factor, "floor_abs_j": a, "floor_cmp_j": c,
                                         "floor_gate_j": max(a, c) if finite(a) and finite(c) else None}
    out["dominance"] = dominance_rows(out["floors"])
    out["scaled_allowance"] = scaled
    return out, selections


def gamma_inputs(session):
    """Estimator 4's per-session statistics before the floor gate is known."""
    selections, rows, operands = {}, {}, {}
    for cell in objects(session.roster.get("cells")):
        cid = cell.get("cell_id")
        if not isinstance(cid, str):
            session.reader.flag("unit_shape_invalid", "roster/cells", "cell id must be a string")
            continue
        chosen = {"quad": session.select(cid, "quad")}
        selections[cid] = chosen
        phase = phase_of(cid)
        row, kinds, a, b = B5.contrast_inputs(session, chosen["quad"], phase)
        declared = len(get(session.exclusion_cells, cid, "kept_units", "quad", default=[]))
        missing = len(chosen["quad"]) < declared
        if row["n"] < 5 or missing:
            row["p"] = 1.0
        if len(chosen["quad"]) < 5:
            session.reader.flag("cell_below_minimum", cid, {"n": len(chosen["quad"])})
        rows[cid], operands[cid] = row, {"kinds": kinds, "a": a, "b": b, "phase": phase, "missing": missing,
                                         "ids": [u for u, _ in chosen["quad"]]}
    return selections, rows, operands


def finish_gamma(session, selections, rows, operands, floor_cells, scaled_floor_cells, paired_reported):
    out = {"contrasts": {}, "descriptive": {}, "cross_session": {}, "lines": {}, "decision_vs_floor": {},
           "scaled_allowance": {"label": B5.SCALED_ALLOWANCE_LABEL, "contrasts": {}}}
    basis = B5.reference_scale_basis(session)
    for cid, row in rows.items():
        op = operands[cid]
        phase = op["phase"]
        other_cid = next((c for c in rows if c != cid), None)
        other_p = rows[other_cid]["p"] if other_cid else 1.0
        partner = None
        if other_cid is not None:
            o = operands[other_cid]
            partner = (rows[other_cid], o["ids"], o["kinds"], o["missing"])
        floor_record = B5.contrast_floor(floor_cells, phase)
        contrast = B5.finish_contrast(row, other_p, floor_record["floor_gate_j"], op["ids"], op["kinds"],
                                      5, op["missing"], partner)
        contrast["floor"] = floor_record
        if row["n"] == 5:
            session.reader.flag("loo_kept_n_equals_minimum", cid, {"kept_n": 5, "loo_n": 4})
        out["contrasts"][cid] = contrast
        out["descriptive"][cid] = B5.descriptive_estimate(op["a"], op["b"], contrast, phase)
        out["decision_vs_floor"][cid] = B5.decision_beyond_floor(contrast, floor_record["floor_gate_j"])
        for model, side in ((MODELS["ALPHA"], op["a"]), (MODELS["BETA"], op["b"])):
            reported = paired_reported.get(model + "/" + phase) or {}
            out["cross_session"][model + "/" + phase] = B5.cross_window(side, reported)
        lines = labelled_lines(session, cid, selections[cid])
        lines["whole_machine"] = {"status": "not_computed", "reason": "not given for GAMMA (section 9.5 item 5)"}
        out["lines"][cid] = lines
        scaled_row, scaled_kinds = B5.scaled_gamma_inputs(session, selections[cid]["quad"], phase, basis)
        scaled_row["p"] = row["p"]
        scaled_floor = B5.contrast_floor(scaled_floor_cells, phase)
        scaled = B5.finish_contrast(scaled_row, other_p, scaled_floor["floor_gate_j"], op["ids"], scaled_kinds,
                                    5, op["missing"])
        for key in ("loo", "loo_verdict_influential", "loo_magnitude_influential", "ceiling"):
            scaled.pop(key, None)
        scaled.update(floor=scaled_floor, outcome_equals_primary=scaled["outcome"] == contrast["outcome"])
        out["scaled_allowance"]["contrasts"][cid] = scaled
    return out


# ---------------------------------------------------------------- pairing (section 6.2)

def pair(gamma_round, floor_sessions):
    """Section 6.2 for one floor pack: [(round, session_id)] of its counting sessions."""
    if not isinstance(gamma_round, int):
        return {"session_id": None, "rule": "gamma_round_unknown"}
    same = [s for r, s in floor_sessions if r == gamma_round]
    if same:
        return {"session_id": same[0], "rule": "1_same_round"}
    later = sorted(((r, s) for r, s in floor_sessions if isinstance(r, int) and r > gamma_round), key=lambda x: x[0])
    if later:
        return {"session_id": later[0][1], "rule": "2_next_counting"}
    earlier = sorted(((r, s) for r, s in floor_sessions if isinstance(r, int) and r < gamma_round), key=lambda x: -x[0])
    if earlier:
        return {"session_id": earlier[0][1], "rule": "3_last_earlier_counting"}
    return {"session_id": None, "rule": "3_floor_from_block_5"}


# ---------------------------------------------------------------- block-5 values (optional input)

def block5_floor_view(b5):
    """Floor cells, reported cells and contrasts from a block-5 recompute output, read only if given."""
    if not b5:
        return None
    return {"floor_cells": mapping(b5.get("floor_cells")), "reported_cells": mapping(b5.get("reported_cells")),
            "contrasts": mapping(b5.get("contrasts")), "descriptive": mapping(b5.get("descriptive")),
            "floors": mapping(b5.get("floors")), "dominance": mapping(b5.get("dominance"))}


# ---------------------------------------------------------------- quantity keys

def tag_of(model):
    return MODEL_TAG.get(model, str(model))


def contrast_key(cid):
    return "decode" if "decode" in cid else "prefill-p2048"


def reported_keys(prefix, cell):
    interval = cell.get("interval") or {}
    return {prefix + "/mean_j": cell.get("mean_j"), prefix + "/lower_j": cell.get("lower_j"),
            prefix + "/upper_j": cell.get("upper_j"), prefix + "/h_j": interval.get("h_j"),
            prefix + "/B_j": interval.get("B_j"), prefix + "/per_token_j": get(cell, "per_token", "j_per_token"),
            prefix + "/attribution_floor_j": get(cell, "attribution_floor", "value_j"),
            prefix + "/n_r": cell.get("n_r"), prefix + "/n_b": cell.get("n_b")}


def floor_keys(prefix, floor):
    return {prefix + "/point_j": floor.get("point_unguarded_floor_j"),
            prefix + "/corner_j": floor.get("corner_widened_unguarded_floor_j"),
            prefix + "/operative_j": floor.get("operative_unguarded_floor_j"),
            prefix + "/guarded_j": floor.get("guarded_floor_j"),
            prefix + "/floor_j": floor.get("drift_widened_guarded_floor_j"), prefix + "/n": floor.get("n")}


def contrast_keys(prefix, contrast, descriptive=None):
    keys = {prefix + "/n": contrast.get("n"), prefix + "/dbar_j": contrast.get("dbar_j"),
            prefix + "/s_d_j": contrast.get("s_d_j"),
            prefix + "/metrology_lower_j": (contrast.get("metrology_interval_j") or [None, None])[0],
            prefix + "/metrology_upper_j": (contrast.get("metrology_interval_j") or [None, None])[1],
            prefix + "/D_j": contrast.get("D_j"),
            prefix + "/decision_lower_j": (contrast.get("decision_interval_j") or [None, None])[0],
            prefix + "/decision_upper_j": (contrast.get("decision_interval_j") or [None, None])[1],
            prefix + "/t": contrast.get("t_stat"), prefix + "/p": contrast.get("p"),
            prefix + "/holm_p": contrast.get("holm_p"), prefix + "/floor_gate_j": contrast.get("floor_gate_j"),
            prefix + "/outcome": contrast.get("outcome"), prefix + "/direction": contrast.get("direction")}
    if "ceiling" in contrast:
        keys[prefix + "/ceiling"] = contrast.get("ceiling")
    if descriptive is not None:
        keys.update({prefix + "/energy_ratio": descriptive.get("ratio"),
                     prefix + "/energy_ratio_lower": descriptive["ratio_interval"][0],
                     prefix + "/energy_ratio_upper": descriptive["ratio_interval"][1],
                     prefix + "/per_token_j": descriptive.get("per_token_difference_j")})
    return keys


def session_quantities(result):
    q = {"calibration/b_op_s": get(result, "calibration", "b_op_s"), "neg8/verdict": get(result, "neg8", "verdict"),
         "neg8/bound_j": get(result, "neg8", "bound_j"), "neg8/allowance_j": get(result, "neg8", "allowance_j")}
    for cid, cell in result.get("reported_cells", {}).items():
        model_phase = tag_of(cell["model"]) + "/" + PHASE_LABEL[cell["phase"]]
        q.update(reported_keys("reported/" + model_phase, cell))
    for key, floor in result.get("floors", {}).items():
        model, phase, form = key.split("/")
        q.update(floor_keys("floor/" + tag_of(model) + "/" + PHASE_LABEL[phase] + "/" + form, floor))
    for key, cell in result.get("floor_cells", {}).items():
        model, phase = key.split("/")
        q["floor/" + tag_of(model) + "/" + PHASE_LABEL[phase] + "/gate_j"] = cell.get("floor_gate_j")
    for key, row in get(result, "dominance", "ratios", default={}).items():
        model, phase, form = key.split("/")
        q["dominance/" + tag_of(model) + "/" + PHASE_LABEL[phase] + "/" + form + "/R"] = row["R"]
    for key, row in get(result, "dominance", "common_mode", default={}).items():
        model, phase = key.split("/")
        q["dominance/" + tag_of(model) + "/" + PHASE_LABEL[phase] + "/comparative/R_cm"] = row["R_cm"]
    for cid, contrast in result.get("contrasts", {}).items():
        q.update(contrast_keys("contrast/" + contrast_key(cid), contrast, result["descriptive"].get(cid)))
    if result.get("pairing_dominance"):
        q["dominance/branch"] = result["pairing_dominance"].get("branch")
    for key, row in result.get("cross_session", {}).items():
        model, phase = key.split("/")
        prefix = "cross_session/" + tag_of(model) + "/" + PHASE_LABEL[phase]
        for field in ("G_j", "h_G_j", "F_j", "h_F_j", "delta_j", "agree", "n"):
            q[prefix + "/" + field] = row.get(field)
    for cid, lines in result.get("lines", {}).items():
        if "p42" in cid:
            continue  # diagnostic p42 must not overwrite the registered p2048 Q
        label = (tag_of(MODELS[result["pack"]]) + "/" if result["pack"] in FLOOR_PACKS else "") + contrast_key(cid)
        for name, row in lines.items():
            if not isinstance(row, dict) or row.get("status") == "not_computed" and "mean_j" not in row:
                continue
            for field in ("mean_j", "dbar_j", "lower_j", "upper_j", "h_j", "n_r", "n_b", "n"):
                if name == "single_step_reconstruction" and field in ("lower_j", "upper_j"):
                    continue  # Absent from the pinned comparison contract, including null diagnostic intervals.
                if field in row:
                    q["lines/" + name + "/" + label + "/" + field] = row[field]
    scaled = result.get("scaled_allowance") or {}
    for cid, row in scaled.get("reported_cells", {}).items():
        model_phase = tag_of(row["model"]) + "/" + PHASE_LABEL[row["phase"]]
        for field in ("factor", "lower_j", "upper_j"):
            q["lines/scaled_allowance/" + model_phase + "/" + field] = row.get(field)
    for key, cell in scaled.get("floor_cells", {}).items():
        model, phase = key.split("/")
        q["lines/scaled_allowance/" + tag_of(model) + "/" + PHASE_LABEL[phase] + "/gate_j"] = cell.get("floor_gate_j")
    for cid, row in scaled.get("contrasts", {}).items():
        prefix = "lines/scaled_allowance/" + contrast_key(cid)
        q.update({prefix + "/D_j": row.get("D_j"), prefix + "/factor": row.get("factor"),
                  prefix + "/outcome": row.get("outcome")})
    return q


def compared_runs(session):
    """The runs whose phase energies are compared (lead decision 2's contract): every run of a kept
    unit, the surviving screen references and the clean corpus."""
    kept = {(cid, stratum, uid) for cid, cell in session.exclusion_cells.items()
            for stratum, uids in cell["kept_units"].items() for uid in uids}
    ids = {rid for key, rids in session.units.items() if key in kept for rid in rids}
    return ids | set(session.neg8["survivor_ids"]) | set(session.neg8["corpus_ids"])


def run_energies(session):
    rows = {}
    wanted = compared_runs(session)
    for run_id, m in sorted(session.members.items()):
        if m.energies and run_id in wanted:
            rows[run_id] = {phase: value for phase, value in sorted(m.energies.items())}
    return rows


# Lead decision 5: a same-day single-session GAMMA run compares run energies and floor-free
# statistics only; these keys are decided by the closed block run.
SINGLE_GAMMA_DEFERRED = ("contrast/*/outcome", "contrast/*/ceiling", "contrast/*/floor_gate_j",
                         "dominance/branch", "cross_session/*", "lines/scaled_allowance/*/outcome")


def single_gamma_view(quantities):
    return {k: v for k, v in quantities.items()
            if not any(fnmatch.fnmatchcase(k, p) for p in SINGLE_GAMMA_DEFERRED)}


# ---------------------------------------------------------------- sections 10 and 11

SUMMARY_PATTERNS = ("reported/*/mean_j", "reported/*/per_token_j", "reported/*/attribution_floor_j",
                    "floor/*/operative_j", "floor/*/floor_j", "dominance/*/R", "dominance/*/R_cm",
                    "contrast/*/dbar_j", "contrast/*/energy_ratio", "lines/whole_machine/*/mean_j")


def summarized(key):
    return any(fnmatch.fnmatchcase(key, p) for p in SUMMARY_PATTERNS)


def between_session(values):
    """Section 10: n, mean and sample standard deviation; nothing else."""
    values = [v for v in values if finite(v)]
    n = len(values)
    return {"n": n, "mean": statistics.fmean(values) if n else None,
            "sd": statistics.stdev(values) if n >= 2 else None}


def block5_quantities(b5):
    if not b5:
        return {}
    view = block5_floor_view(b5)
    fake = {"pack": None, "reported_cells": view["reported_cells"], "floors": view["floors"],
            "floor_cells": view["floor_cells"], "dominance": view["dominance"] if "ratios" in view["dominance"] else {},
            "contrasts": view["contrasts"] if all(isinstance(v, dict) and "dbar_j" in v for v in view["contrasts"].values())
            else {}, "descriptive": view["descriptive"]}
    q = {}
    for cid, cell in fake["reported_cells"].items():
        if isinstance(cell, dict) and cell.get("model") in MODEL_TAG and cell.get("phase") in PHASE_LABEL:
            q.update(reported_keys("reported/" + tag_of(cell["model"]) + "/" + PHASE_LABEL[cell["phase"]], cell))
    for key, floor in fake["floors"].items():
        parts = key.split("/")
        if len(parts) == 3 and parts[1] in PHASE_LABEL:
            q.update(floor_keys("floor/" + tag_of(parts[0]) + "/" + PHASE_LABEL[parts[1]] + "/" + parts[2], floor))
    for key, row in get(fake, "dominance", "ratios", default={}).items():
        parts = key.split("/")
        if len(parts) == 3 and parts[1] in PHASE_LABEL:
            q["dominance/" + tag_of(parts[0]) + "/" + PHASE_LABEL[parts[1]] + "/" + parts[2] + "/R"] = row.get("R")
    for key, row in get(fake, "dominance", "common_mode", default={}).items():
        parts = key.split("/")
        if len(parts) == 2 and parts[1] in PHASE_LABEL:
            q["dominance/" + tag_of(parts[0]) + "/" + PHASE_LABEL[parts[1]] + "/comparative/R_cm"] = row.get("R_cm")
    for cid, contrast in fake["contrasts"].items():
        q.update(contrast_keys("contrast/" + contrast_key(cid), contrast, fake["descriptive"].get(cid)))
    # Consume the released B5 program's output only. Never re-run B5 data.
    for pack in FLOOR_PACKS:
        for cid, row in get(b5, "disclosures", "whole_machine", "windows", pack, "cells", default={}).items():
            if "p42" in cid:
                continue
            q["lines/whole_machine/" + tag_of(MODELS[pack]) + "/" + contrast_key(cid) + "/mean_j"] = row.get("mean_j")
    return q


def pack_block5_keys(pack, keys):
    if pack == "GAMMA":
        return {k: v for k, v in keys.items() if k.startswith("contrast/")}
    tag = MODEL_TAG[MODELS[pack]]
    return {k: v for k, v in keys.items() if k.split("/")[1:2] == [tag]}


def block_lines(results, b5_keys):
    """Sections 10, 11.1, 11.2 and 11.4 over the per-session results."""
    registered = production_comparison_keys()["session_quantity_keys"]
    out = {"between_session": {}, "flagged_inclusive": {}, "side_by_side": {}, "replication": {}, "short": {},
           "block6_only": {}}
    for pack in PACKS:
        counting = [r for r in results.values() if r["pack"] == pack and r["counting"]]
        inclusive = counting + [r for r in results.values() if r["pack"] == pack and not r["counting"]
                                and r["inclusive"]["eligible"]]
        counting.sort(key=lambda r: (r["round"] if isinstance(r["round"], int) else 10 ** 6, r["session_id"]))
        b5 = pack_block5_keys(pack, b5_keys)
        # Quantity names are fixed by the contract even when no session can
        # contribute a Q. The empty arithmetic still prints n=0, mean/sd=null.
        keys = sorted({k for k in registered[pack] if summarized(k)} |
                      {k for r in inclusive for k in r["quantities"] if summarized(k)} |
                      {k for k in b5 if summarized(k)})
        summary, flagged, side = {}, {}, {}
        for key in keys:
            sessions = [r["quantities"].get(key) for r in counting]
            base = [b5[key]] if finite(b5.get(key)) else []
            summary[key] = {**between_session(base + sessions), "block5_included": bool(base)}
            summary[key]["noncomputable_sessions"] = [r["session_id"] for r in counting
                                                       if not finite(r["quantities"].get(key))]
            out["block6_only"].setdefault(pack, {})[key] = between_session(sessions)
            if key.startswith("floor/") or "attribution_floor" in key:
                summary[key]["timing_regime_label"] = (
                    "Block 5's floors were formed under its own calibration acceptance (minimum bracket "
                    "allowance 14.531 ms) and Block 6's under its own (10.818 ms). The difference, up to 3.713 ms "
                    "of timing bound and up to 0.175 J of floor by the registration's sizing, comes from the "
                    "registered rule and not from the machine. The summary over Block 6 sessions alone is "
                    "printed beside the summary over all sessions.")
            summary[key]["sd_label"] = "not defined" if summary[key]["n"] == 1 else None
            flagged[key] = {**between_session(base + [r["quantities"].get(key) for r in inclusive]),
                            "block5_included": bool(base)}
            mean6 = between_session(sessions)["mean"]
            side[key] = {"block5": b5.get(key), "block5_label": None if finite(b5.get(key)) else "block 5: not computed",
                         "sessions": {r["session_id"]: r["quantities"].get(key) for r in counting},
                         "delta": mean6 - b5[key] if finite(mean6) and finite(b5.get(key)) else None,
                         "session_deltas": {r["session_id"]: r["quantities"][key] - b5[key]
                                            for r in counting if finite(r["quantities"].get(key)) and finite(b5.get(key))}}
        out["between_session"][pack] = {"label": "between-session summary", "n_counting": len(counting), "values": summary}
        out["flagged_inclusive"][pack] = {"label": "including sessions that did not count",
                                          "added_sessions": [r["session_id"] for r in inclusive if not r["counting"]],
                                          "values": flagged}
        out["side_by_side"][pack] = side
        out["short"][pack] = {"counting": len(counting), "short": len(counting) < TARGET_SESSIONS,
                              "below_commitment": len(counting) < 2}
    gammas = sorted((r for r in results.values() if r["pack"] == "GAMMA"),
                    key=lambda r: (r["round"] if isinstance(r["round"], int) else 10 ** 6, r["session_id"]))
    for c in ("decode", "prefill-p2048"):
        words = [{"session_id": r["session_id"], "outcome": r["quantities"].get("contrast/" + c + "/outcome"),
                  "direction": r["quantities"].get("contrast/" + c + "/direction")} for r in gammas if r["counting"]]
        inclusive = [{"session_id": r["session_id"], "outcome": r["quantities"].get("contrast/" + c + "/outcome"),
                      "direction": r["quantities"].get("contrast/" + c + "/direction")}
                     for r in gammas if not r["counting"] and r["inclusive"]["eligible"]]
        base_word, base_dir = b5_keys.get("contrast/" + c + "/outcome"), b5_keys.get("contrast/" + c + "/direction")
        row = {"sessions": words, "flagged_inclusive_sessions": inclusive, "block5_outcome": base_word,
               "block5_direction": base_dir, "short": len(words) < TARGET_SESSIONS,
               "short_sentence": (f"short: {len(words)} counting block-6 sessions of the {TARGET_SESSIONS} targeted"
                                  if len(words) < TARGET_SESSIONS else None)}
        if base_word is None:
            row.update(word=None, reason="block5_absent")
        elif base_word == "not_estimable":
            row.update(word=None, reason="block5_not_estimable")
        elif any(r.get("binding_defect") for r in gammas if r["counting"]):
            row.update(word=None, reason="binding_defect; tooling refusal, not a replication outcome")
        elif not words:
            row.update(word=None, reason="no_counting_session")
        else:
            same = all(w["outcome"] == base_word and w["direction"] == base_dir for w in words)
            row["word"] = "replicated" if same else "not replicated"
        out["replication"][c] = row
    return out


def block_quantities(lines):
    q = {}
    for pack, block in lines["between_session"].items():
        for key, row in block["values"].items():
            for stat in ("n", "mean", "sd"):
                q["summary/" + pack + "/" + key + "/" + stat] = row[stat]
        for key, row in lines["flagged_inclusive"][pack]["values"].items():
            for stat in ("n", "mean", "sd"):
                q["inclusive/" + pack + "/" + key + "/" + stat] = row[stat]
        for key, row in lines["side_by_side"][pack].items():
            q["side_by_side/" + pack + "/" + key + "/delta"] = row["delta"]
    for c, row in lines["replication"].items():
        q["replication/" + c + "/word"] = row["word"]
    return q


# ---------------------------------------------------------------- driver

PHASE_BOUNDARY = "DC input at the USB-C port; the adapter's AC-to-DC loss is not included."


def add_session_machine(session, result, selections):
    """RL-30 7b: ONLY the pinned add_machine executes the arithmetic.

    Its archive I/O is supplied as verified temporary meter/clock files. The
    actual members and session bounds stay external. No estimator or corner
    calculation is reproduced here.
    """
    pin = session.input_pin
    paths = pin.get("meter_streams", [])
    if not paths:
        if session.inputs is not None:
            raise InputRefusal("meter_streams_not_supplied")
        return
    with tempfile.TemporaryDirectory(prefix="b6-meter-") as directory:
        root = Path(directory)
        meter = root / "meter"
        meter.mkdir()
        for name in paths:
            path = session.archive / name
            data = session.reader.raw(path, "meter_stream")
            if data is None:
                raise InputRefusal("meter_stream_missing")
            (meter / path.name).write_bytes(data)
        if pin.get("clock_journal"):
            path = root / "sources/night-custody/hazards/monitor/clock.jsonl"
            path.parent.mkdir(parents=True)
            path.write_bytes(session.reader.raw(session.archive / pin["clock_journal"], "clock_journal"))
        recorded = session.reader.raw(session.archive / "withheld/meter.json", "withheld/meter.json", False)
        if session.inputs is not None and recorded is None:
            raise InputRefusal("request_comparison_record_missing")
        if recorded is not None:
            (root / "withheld").mkdir()
            (root / "withheld/meter.json").write_bytes(recorded)
        proxy = types.SimpleNamespace(**vars(session))
        proxy.archive = root
        proxy.harvest = {**session.harvest, "plan_id": session.harvest.get("plan_id", session.archive.name)}
        proxy.reader = Reader(session.pack, session.session_id, session.reader.flags)
        proxy.member = session.member
        output = {"disclosures": {}}
        B5.add_machine(output, {(session.pack, cid): s for cid, s in selections.items()},
                       {session.pack: proxy}, meter)
        machine = output["disclosures"]["whole_machine"]
        if session.inputs is not None:
            for member in machine["windows"][session.pack].get("members", {}).values():
                if "recorded_comparison" not in member["phases"]["request"]:
                    raise InputRefusal("request_comparison_member_missing")
        result["whole_machine"] = machine
        for cid, row in machine["windows"][session.pack].get("cells", {}).items():
            assisted = sorted({m.run_id for m in B5.flatten(selections[cid]["repeat"] + selections[cid]["quad"])
                               if m.run_id in session.assist})
            # Preserve the pinned battery-activity count. The registered flag
            # is separately sourced from harvest battery.assist, per R8.
            result["lines"].setdefault(cid, {})["whole_machine"] = {
                **row, "boundary": PHASE_BOUNDARY,
                "implementation": "single implementation; not independently recomputed",
                "request_assisted_members": assisted, "request_assisted_count": len(assisted)}
        result["request_cross_check"] = machine["request_cross_check"]


def compute_session(session):
    result = {"session_id": session.session_id, "pack": session.pack, "round": session.round,
              "t0": session.attempt.get("t0") if session.attempt else None,
              "counting": session.counting, "loop_status": session.loop_status,
              "acceptance_verdict": session.acceptance.get("verdict"), "window_codes": session.window_codes,
              "calibration": session.b, "neg8": session.neg8,
              "exclusions_rederivation": session.exclusion_check,
              "desk_hazards": session.hazards,
              "kept_units": {cid: cell["kept_units"] for cid, cell in session.exclusion_cells.items()},
              "removed_units": {cid: cell["dropped_units"] for cid, cell in session.exclusion_cells.items()}}
    if session.inputs:
        families = ("monitor_cost", "arm_host", "battery_phase", "subject_temperature",
                    "reference_history", "attempt_history", "g10_history", "block5_codes_carried")
        supplied = session.input_pin.get("copied_records", {})
        if set(supplied) != set(families):
            raise InputRefusal("disclosure_coverage_missing")
        if any(not isinstance(names, list) or not names or any(not isinstance(n, str) for n in names)
               for names in supplied.values()):
            raise InputRefusal("disclosure_coverage_invalid")
        result["copied_disclosures"] = {
            "label": "copied from the harvest or acceptance record, bound by digest, not recomputed",
            "families": {family: [{"path": name, "sha256": session.inputs.expected.get(name),
                                    "record": session.reader.raw(session.archive / name, "disclosure").decode("utf-8")}
                                   for name in supplied[family]] for family in families}}
    computable = finite(session.b["b_op_s"]) and finite(session.neg8["allowance_j"])
    groups = session.structure_group()
    if session.pack in FLOOR_PACKS:
        out, selections = floor_session(session)
        result.update(out)
        enough = all(c["status"] == "computed" for c in out["reported_cells"].values()) and bool(out["reported_cells"])
    elif session.pack == "GAMMA":
        selections, rows, operands = gamma_inputs(session)
        result["_gamma"] = (selections, rows, operands)
        enough = bool(rows) and all(len(s["quad"]) >= 5 for s in selections.values())
    else:
        enough = False
    if session.pack in PACKS:
        add_session_machine(session, result, selections)
    result["_selections"] = selections if session.pack in PACKS else {}
    result["inclusive"] = {"eligible": not session.counting and not groups and computable and enough,
                           "structure_groups": groups, "computable": computable and enough}
    return result


def attach_gamma(result, session, floor_results, b5_view, closed):
    """Pair a GAMMA session (section 6.2), then finish its contrasts with the paired floors."""
    selections, rows, operands = result.pop("_gamma")
    floor_cells, scaled_cells, reported, pairing, ratios = {}, {}, {}, {}, {}
    for pack in FLOOR_PACKS:
        candidates = [(r["round"], r["session_id"]) for r in sorted(floor_results.values(),
                      key=lambda r: (r["t0"] if finite(r["t0"]) else float("inf"), r["session_id"]))
                      if r["pack"] == pack and r["counting"]]
        p = pair(result["round"], candidates)
        # Before the close a same-round floor session can still be harvested and change rules 2 and 3.
        p["provisional"] = not closed and p["rule"] != "1_same_round"
        model = MODELS[pack]
        if p["session_id"] is not None:
            source = floor_results[p["session_id"]]
            for phase in ("decode", "prefill"):
                floor_cells[model + "/" + phase] = source["floor_cells"].get(model + "/" + phase, {})
                scaled_cells[model + "/" + phase] = source["scaled_allowance"]["floor_cells"].get(model + "/" + phase, {})
            for cell in source["reported_cells"].values():
                reported[cell["model"] + "/" + cell["phase"]] = cell
            ratios.update(source["dominance"]["ratios"])
            ratios.update({k + "/common_mode": v for k, v in source["dominance"]["common_mode"].items()})
        elif b5_view is not None:
            p["label"] = "floor from block 5"
            session.reader.flag("pairing_floor_from_block5", pack, "no counting block-6 floor session")
            for phase in ("decode", "prefill"):
                floor_cells[model + "/" + phase] = b5_view["floor_cells"].get(model + "/" + phase, {})
                # Lead decision 6: block 5 prints no scaled-allowance floor; its registered floor stands in, labelled.
                scaled_cells[model + "/" + phase] = {**b5_view["floor_cells"].get(model + "/" + phase, {}),
                                                     "label": "registered block-5 floor stands in (lead decision 6)"}
            for cell in b5_view["reported_cells"].values():
                if isinstance(cell, dict) and cell.get("model") == model:
                    reported[cell["model"] + "/" + cell["phase"]] = cell
        else:
            p["label"] = "floor unavailable"
            session.reader.flag("pairing_floor_unavailable", pack, "no counting floor session and no block-5 input")
        if p.get("provisional"):
            session.reader.flag("pairing_provisional", pack, {"rule": p["rule"]})
        pairing[pack] = p
    result["pairing"] = pairing
    result.update(finish_gamma(session, selections, rows, operands, floor_cells, scaled_cells, reported))
    failed = sorted(k for k, row in ratios.items() if not row.get("pass"))
    result["pairing_dominance"] = ({"branch": "B" if failed else "A", "failed": failed, "n_ratios": len(ratios)}
                                   if len(ratios) == 12 else {"branch": None, "reason": "paired ratios incomplete"})


def recompute_block(archives, attempts_path, flags, b5_output=None, closed=False, state_path=None,
                    input_pins=None, pool=None):
    attempts = read_attempts(attempts_path, flags)
    reharvested = read_reharvested(state_path, flags)
    sessions = {}
    for archive in archives:
        pin = session_input_pin(input_pins or {}, archive)
        inputs = AuthenticatedInputs(archive, pin) if pin is not None else None
        s = Session(archive, flags, attempts, reharvested=reharvested, inputs=inputs, pool=pool, input_pin=pin)
        if s.session_id in sessions:
            s.reader.flag("session_id_duplicate", "session", {"archive": str(archive)})
            continue
        sessions[s.session_id] = s
    results = {sid: compute_session(s) for sid, s in sessions.items()}
    floor_results = {sid: r for sid, r in results.items() if r["pack"] in FLOOR_PACKS}
    b5_view = block5_floor_view(b5_output)
    for sid, r in results.items():
        if r["pack"] == "GAMMA":
            attach_gamma(r, sessions[sid], floor_results, b5_view, closed)
    for sid, r in results.items():
        r["quantities"] = session_quantities(r)
        r["binding_defect"] = any(f.get("session") == sid and f["code"] in STOP_FLAG_CODES for f in flags)
    lines = block_lines(results, block5_quantities(b5_output))
    from joulewise.b6_analysis_check import check_block
    checks = check_block(sessions, results, lines, block5_quantities(b5_output))
    # Compare only independently produced rows. Never echo unchecked primary
    # rows into a purported second producer (in particular, R8's phase line).
    expected = checks.pop("comparison_table")
    primary = comparison_table(sessions, results, lines)
    projected = {"schema": TABLE_SCHEMA, "sessions": {}, "block": {"quantities": {}}}
    for sid, body in expected["sessions"].items():
        source = primary["sessions"][sid]
        projected["sessions"][sid] = {
            "quantities": {k: source["quantities"].get(k) for k in body["quantities"]},
            "run_phase_energy_j": {rid: {p: source["run_phase_energy_j"].get(rid, {}).get(p) for p in phases}
                                   for rid, phases in body["run_phase_energy_j"].items()}}
    projected["block"]["quantities"] = {k: primary["block"]["quantities"].get(k)
                                        for k in expected["block"]["quantities"]}
    comparator, public_comparator = compare(projected, expected)
    # RL-113: keys only the first program prints are reported, never compared, counted or refused on.
    second = table_rows(expected)
    first_only = sorted(({"class": "run_phase_energy" if kind == "run_phase_energy" else quantity_class(name),
                          "session": sid, "key": name}
                         for kind, sid, name in table_rows(primary) if (kind, sid, name) not in second),
                        key=lambda row: (row["class"], row["session"], row["key"]))
    checks["first_program_only"] = first_only
    by_class = {}
    for row in first_only:
        by_class[row["class"]] = by_class.get(row["class"], 0) + 1
    classes = public_comparator["classes"]
    for cls in by_class:
        # A class with no compared row gets counts only; compare() never judged it, so it carries no "pass".
        classes.setdefault(cls, {"compared": 0, "passed": 0, "failed": 0, "unmatched": 0})
    for cls, row in classes.items():
        row["first_program_only"] = by_class.get(cls, 0)
    public_comparator["classes"] = dict(sorted(classes.items()))
    checks["comparator"] = public_comparator
    checks["pass"] = checks["pass"] and comparator["pass"]
    for s in sessions.values():
        if not checks["pass"]:
            s.reader.flag("option_c_disagrees", "block", checks["failures"])
    lines["option_c"] = checks
    for r in results.values():
        r.pop("_selections", None)
    return sessions, results, lines


def comparison_table(sessions, results, lines=None):
    table = {"schema": TABLE_SCHEMA, "sessions": {}}
    for sid, r in results.items():
        table["sessions"][sid] = {"quantities": r["quantities"], "run_phase_energy_j": run_energies(sessions[sid])}
    if lines is not None:
        table["block"] = {"quantities": block_quantities(lines)}
    return table


def stops_comparison(flag, sessions):
    if flag["code"] not in STOP_FLAG_CODES:
        return False
    if flag["code"] in B5.TRACE_STOP_FLAG_CODES:
        return any(flag.get("session") == s.session_id and flag["scope"] in s.compared_run_ids
                   for s in sessions.values())
    return True


def sanitize(value):
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {str(k): sanitize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        items = sorted(value) if isinstance(value, set) else value
        return [sanitize(v) for v in items]
    return value


def canonical(value):
    return (json.dumps(sanitize(value), sort_keys=True, indent=1, allow_nan=False) + "\n").encode("utf-8")


NUMBER_TOKEN = re.compile(r"\d+\.\d|\d[eE][+-]?\d")


def require_structure_only(value, path="public"):
    """Refuse any float, decimal-looking token or outcome word in a public output."""
    if isinstance(value, float):
        raise ValueError("float in public output at " + path)
    if isinstance(value, str):
        if value in OUTCOME_WORDS or NUMBER_TOKEN.search(value):
            raise ValueError("restricted token in public output at " + path)
    elif isinstance(value, dict):
        for key, item in value.items():
            require_structure_only(key, path + "/<key>")
            require_structure_only(item, path + "/" + str(key))
    elif isinstance(value, (list, tuple)):
        for i, item in enumerate(value):
            require_structure_only(item, path + "/" + str(i))
    elif not (value is None or isinstance(value, (bool, int))):
        raise ValueError("unexpected type in public output at " + path)


def public_session(r, session_flags):
    cells = {}
    for cid, kept in r["kept_units"].items():
        cells[cid] = {s: len(v) for s, v in sorted(kept.items())}
    status = {cid: cell["status"] for cid, cell in r.get("reported_cells", {}).items()}
    counts, restricted = {}, 0
    for f in session_flags:
        if f["code"] in PUBLIC_FLAG_CODES:
            counts[f["code"]] = counts.get(f["code"], 0) + 1
        else:
            restricted += 1
    pairing = {p: {"session_id": row.get("session_id"), "rule": row.get("rule"),
                   "provisional": bool(row.get("provisional"))} for p, row in r.get("pairing", {}).items()}
    return {"pack": r["pack"], "round": r["round"], "counting": r["counting"], "loop_status": r["loop_status"],
            "inclusive_eligible": r["inclusive"]["eligible"], "structure_groups": r["inclusive"]["structure_groups"],
            "kept_units": cells, "reported_cell_status": status, "pairing": pairing,
            "flag_counts": dict(sorted(counts.items())), "restricted_flag_count": restricted,
            "runs_compared": len(r.get("_runs", ()))}


def write_outputs(restricted_path, public_path, restricted, public):
    data = canonical(restricted)
    public = sanitize(public)
    require_structure_only(public)
    # A hex digest can look like an exponent ("3e5"); it is added after the guard, by construction.
    public["restricted_sha256"] = hashlib.sha256(data).hexdigest()
    public_data = canonical(public)
    Path(restricted_path).write_bytes(data)
    Path(public_path).write_bytes(public_data)
    return public


def finish_recompute(mode, sessions, results, lines, flags, extra=None):
    flags = sorted((sanitize(f) for f in flags), key=lambda f: (f["code"], f.get("session") or "", f["pack"],
                                                                 f["scope"], json.dumps(f["detail"], sort_keys=True)))
    for f in flags:
        f["stops_comparison"] = stops_comparison(f, sessions)
    stopped = any(f["stops_comparison"] for f in flags)
    table = comparison_table(sessions, results, lines)
    restricted = {"schema": SCHEMA, "mode": mode, "program_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  "b5_program_sha256": B5.loaded_sha256,
                  "sessions": results, "block": lines, "comparison_table": table, "flags": flags,
                  "comparison_stopped": stopped, **(extra or {})}
    public = {"schema": PUBLIC_SCHEMA, "mode": mode, "comparison_stopped": stopped, "sessions": {},
              "flag_count": len(flags)}
    for sid, r in results.items():
        r["_runs"] = table["sessions"][sid]["run_phase_energy_j"]
        public["sessions"][sid] = public_session(r, [f for f in flags if f.get("session") == sid])
        del r["_runs"]
    if lines is not None:
        public["counting_by_pack"] = {p: row["counting"] for p, row in lines["short"].items()}
    return restricted, public


# ---------------------------------------------------------------- comparator (S-13)

# S17-R2 supersedes the October precision. One content-pinned table, shared
# by the option-(c) gate and the external comparison CLI; never fitted to data.
PRECISION_SHA256 = "e242cab6bb311a9c23d5c6dc06374ed3094a351e36d6954c3589e2b535cc63b0"
_precision_bytes = (ROOT_DIR / "configs/b6/recompute/precision.json").read_bytes()
if hashlib.sha256(_precision_bytes).hexdigest() != PRECISION_SHA256:
    raise InputRefusal("print_precision_digest_mismatch")
_precision = json.loads(_precision_bytes)
RATIFIED_COMPARISON_DECIMALS = tuple((p, d) for p, d in _precision["decimals"])
RATIFIED_SOURCE = _precision["source"]
RUN_ENERGY_BAR_J = 1e-3  # S-13: each run's phase energy within 1 mJ.


def decimals_for(key, spec):
    base = key
    if key.split("/", 1)[0] in ("summary", "inclusive", "side_by_side"):
        # <kind>/<pack>/<quantity key>/<stat>: the statistic prints as its quantity does.
        base = "/".join(key.split("/")[2:-1])
    for pattern, places in spec:
        if fnmatch.fnmatchcase(base, pattern):
            return places
    return None


def quantity_class(key):
    head = key.split("/", 1)[0]
    if head == "reported":
        field = key.rsplit("/", 1)[-1]
        return {"per_token_j": "per_token", "attribution_floor_j": "attribution_floor"}.get(field, "reported")
    if head == "contrast":
        field = key.rsplit("/", 1)[-1]
        if field in ("outcome", "direction", "ceiling"):
            return "contrast_word"
        if field.startswith("energy_ratio") or field == "per_token_j":
            return "descriptive"
    return head


def flatten(prefix, value, out):
    if isinstance(value, dict):
        for k, v in value.items():
            flatten(prefix + "/" + str(k) if prefix else str(k), v, out)
    else:
        out[prefix] = value
    return out


def table_rows(table):
    """Accept the comparison-table schema, or any {sessions: {id: nested quantities}} object."""
    rows = {}
    for sid, body in mapping(table.get("sessions")).items():
        body = mapping(body)
        energies = mapping(body.get("run_phase_energy_j"))
        quantities = body.get("quantities") if isinstance(body.get("quantities"), dict) else {
            k: v for k, v in body.items() if k != "run_phase_energy_j"}
        for key, value in flatten("", quantities, {}).items():
            rows[("quantity", sid, key)] = value
        for key, value in flatten("", energies, {}).items():
            rows[("run_phase_energy", sid, key)] = value
    for key, value in flatten("", mapping(get(table, "block", "quantities")), {}).items():
        rows[("quantity", "__block__", key)] = value
    return rows


def compare_value(kind, key, own, other, spec):
    row = {"own": own, "driver": other, "difference": None, "bar": None, "pass": False}
    if kind == "run_phase_energy":
        row["bar"] = RUN_ENERGY_BAR_J
        if finite(own) and finite(other):
            row["difference"] = abs(own - other)
            row["pass"] = row["difference"] <= RUN_ENERGY_BAR_J
        return row
    numeric = lambda v: isinstance(v, (int, float)) and not isinstance(v, bool)
    if isinstance(own, float) or isinstance(other, float):
        places = decimals_for(key, spec)
        if places is None:
            row["reason"] = "print_precision_unspecified"
            return row
        row["bar"] = 0.5 * 10.0 ** -places
        if finite(own) and finite(other):
            row["difference"] = abs(own - other)
            row["pass"] = row["difference"] <= row["bar"]
        return row
    if numeric(own) and numeric(other):
        row["difference"] = abs(own - other)
    row["pass"] = own == other and type(own) is type(other)
    return row


def compare(recompute_output, driver_table, spec=RATIFIED_COMPARISON_DECIMALS, spec_source=RATIFIED_SOURCE,
            release=False):
    own_table = recompute_output.get("comparison_table", recompute_output)
    own, other = table_rows(own_table), table_rows(driver_table)
    rows, classes = [], {}

    def tally(cls):
        return classes.setdefault(cls, {"compared": 0, "passed": 0, "failed": 0, "unmatched": 0,
                                        "max_observed_difference": None})
    for key in sorted(set(own) | set(other)):
        kind, sid, name = key
        cls = "run_phase_energy" if kind == "run_phase_energy" else quantity_class(name)
        t = tally(cls)
        if key not in own or key not in other:
            t["unmatched"] += 1
            rows.append({"class": cls, "session": sid, "key": name, "pass": False,
                         "reason": "only_in_recompute" if key in own else "only_in_driver",
                         "own": own.get(key), "driver": other.get(key)})
            continue
        row = compare_value(kind, name, own[key], other[key], spec)
        row.update({"class": cls, "session": sid, "key": name})
        rows.append(row)
        t["compared"] += 1
        t["passed" if row["pass"] else "failed"] += 1
        if finite(row["difference"]):
            t["max_observed_difference"] = max(t["max_observed_difference"] or 0.0, row["difference"])
    stopped = bool(recompute_output.get("comparison_stopped"))
    # Lead decision 4: the release comparison is a closed block run; provisional pairings are same-day only.
    release_inputs = (not release) or (recompute_output.get("mode") == "BLOCK" and recompute_output.get("closed") is True
                                      and spec == RATIFIED_COMPARISON_DECIMALS and spec_source == RATIFIED_SOURCE)
    for t in classes.values():
        t["result"] = "pass" if t["failed"] == 0 and t["unmatched"] == 0 and t["compared"] > 0 else "fail"
    passed = bool(classes) and all(t["result"] == "pass" for t in classes.values()) and not stopped and release_inputs
    restricted = {"schema": COMPARE_SCHEMA, "tolerance": {"run_phase_energy_j": RUN_ENERGY_BAR_J,
                  "printed": "half a unit of the last printed digit", "print_spec": [list(p) for p in spec],
                  "print_spec_source": spec_source,
                  "note": "observed differences are printed beside the bars and never set them"},
                  "recompute_stopped": stopped, "release": release, "release_inputs_valid": release_inputs,
                  "classes": classes, "rows": rows, "pass": passed}
    public = {"schema": COMPARE_PUBLIC_SCHEMA, "pass": passed, "recompute_stopped": stopped,
              "release": release, "release_inputs_valid": release_inputs,
              "print_spec_ratified": spec_source == RATIFIED_SOURCE,
              "classes": {cls: {k: t[k] for k in ("compared", "passed", "failed", "unmatched")} | {"pass": t["result"] == "pass"}
                          for cls, t in sorted(classes.items())}}
    return restricted, public


def load_spec(path):
    if path is None:
        return RATIFIED_COMPARISON_DECIMALS, RATIFIED_SOURCE
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    def placeholder(value):
        if isinstance(value, dict):
            return value.get("placeholder") is True or any(placeholder(v) for v in value.values())
        return isinstance(value, list) and any(placeholder(v) for v in value)
    if placeholder(data):
        raise InputRefusal("placeholder_print_precision")
    return tuple((str(p), int(d)) for p, d in data["decimals"]), str(data.get("source", path))


# ---------------------------------------------------------------- the key contract (lead decision 2)

KEYS_SCHEMA = "joulewise.b6_comparison_keys.v1"


def key_contract(restricted):
    """Session-independent key names from a block run's restricted output; names only, no values."""
    sessions = restricted["sessions"]
    per_pack = {}
    for r in sessions.values():
        per_pack.setdefault(r["pack"], set()).update(r["quantities"])
    gamma = per_pack.get("GAMMA", set())
    return {"schema": KEYS_SCHEMA,
            "ruling": "lead decision 2, 2026-10-27: this script's key pattern is the comparison contract",
            "session_quantity_keys": {p: sorted(k) for p, k in sorted(per_pack.items())},
            "single_session_gamma_keys": sorted(single_gamma_view(dict.fromkeys(gamma))),
            "single_session_gamma_deferred": list(SINGLE_GAMMA_DEFERRED),
            "block_quantity_keys": sorted(restricted["comparison_table"].get("block", {}).get("quantities", {})),
            "run_phase_energy_keys": {
                "form": "<run_id>/<phase>", "phases": ["decode", "prefill", "request"],
                "runs": "every run of a kept unit, the surviving drift-screen references and the clean corpus"},
            "model_tags": sorted(MODEL_TAG.values()), "phases": sorted(PHASE_LABEL.values())}


def production_comparison_keys():
    data = (ROOT_DIR / "configs/b6/recompute/production_comparison_keys.json").read_bytes()
    if hashlib.sha256(data).hexdigest() != "62dbfaef9ebc5cfbbe5a00734f5eb8ad3d82389f54f28473ed63db6135b9174d":
        raise InputRefusal("comparison_key_registry_digest_mismatch")
    return json.loads(data)


def require_production_coverage(results, lines):
    expected = production_comparison_keys()
    for result in results.values():
        if set(result["quantities"]) != set(expected["session_quantity_keys"][result["pack"]]):
            raise InputRefusal("comparison_session_coverage_mismatch")
    if set(block_quantities(lines)) != set(expected["block_quantity_keys"]):
        raise InputRefusal("comparison_block_coverage_mismatch")


# ---------------------------------------------------------------- command line

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    block = sub.add_parser("block", help="every block-6 session, sections 9 to 11")
    block.add_argument("--session", action="append", required=True, help="a session archive root (repeat)")
    block.add_argument("--loop-attempts", required=True, help="the loop's attempts.jsonl")
    block.add_argument("--block5", help="a block-5 independent recompute output (restricted), if released")
    block.add_argument("--closed", action="store_true", help="block 6 has closed: pairings are final")
    single = sub.add_parser("single", help="one newly harvested session, structure-only public output")
    single.add_argument("--session", required=True)
    single.add_argument("--loop-attempts", help="the loop's attempts.jsonl, if it already holds this session")
    for p in (block, single):
        p.add_argument("--loop-state", help="the loop's state.json, for its re-harvest corrections")
        p.add_argument("--restricted-out", required=True)
        p.add_argument("--public-out", required=True)
        p.add_argument("--inputs", help="external custody pins and relocated meter stream names")
        p.add_argument("--inputs-sha256", help="SHA-256 of the externally supplied run-input document")
        p.add_argument("--workers", type=B5.worker_count, default=1, help="bounded member pool; default 1")
    cmp = sub.add_parser("compare", help="S-13 comparison against the analysis driver's restricted outputs")
    cmp.add_argument("--recompute", required=True, help="this script's restricted output")
    cmp.add_argument("--driver", required=True, help="the driver's comparison table (restricted)")
    cmp.add_argument("--print-spec", help="JSON {decimals: [[pattern, places], ...], source: ...}; "
                     "default: the ratified comparison precision")
    cmp.add_argument("--release", action="store_true",
                     help="the release comparison: requires a closed block run (lead decision 4)")
    cmp.add_argument("--restricted-out", required=True)
    cmp.add_argument("--public-out", required=True)
    keys = sub.add_parser("keys", help="write the comparison key contract from a block run's restricted output")
    keys.add_argument("--recompute", required=True)
    keys.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    if args.command == "keys":
        contract = key_contract(json.loads(Path(args.recompute).read_text(encoding="utf-8")))
        Path(args.out).write_text(json.dumps(contract, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        return 0
    pool = None
    try:
        if args.command == "compare":
            spec, source = load_spec(args.print_spec)
            own = json.loads(Path(args.recompute).read_text(encoding="utf-8"))
            driver = json.loads(Path(args.driver).read_text(encoding="utf-8"))
            restricted, public = compare(own, driver, spec, source, args.release)
            public = write_outputs(args.restricted_out, args.public_out, restricted, public)
            print("compare pass=" + json.dumps(public["pass"]) + " restricted_sha256=" + public["restricted_sha256"])
            return 0 if public["pass"] else 1
        flags = []
        pins = {}
        input_record = {"host": "synthetic", "l9_audit": "not_run"}
        if args.inputs:
            data = Path(args.inputs).read_bytes()
            if not args.inputs_sha256 or hashlib.sha256(data).hexdigest() != args.inputs_sha256:
                raise InputRefusal("run_inputs_digest_mismatch")
            document = json.loads(data)
            if document.get("host") != "Air" or document.get("l9_audit") not in ("not_run", "completed"):
                raise InputRefusal("run_host_or_audit_invalid")
            pins = document["sessions"]
            # RL-115: a pinned external input must be supplied, and a supplied one must be pinned,
            # before any session is read. Only the arguments this command has are considered.
            external = document.get("external", {})
            fields = [f for f in ("loop_attempts", "loop_state", "block5") if hasattr(args, f)]
            supplied = {f: bool(getattr(args, f, None)) for f in ("loop_attempts", "loop_state", "block5")}
            if any(f in external and not supplied[f] for f in fields):
                raise InputRefusal("external_input_missing")
            if any(supplied[f] and f not in external for f in fields):
                raise InputRefusal("external_input_unpinned")
            for field in fields:
                path = getattr(args, field, None)
                if path and hashlib.sha256(Path(path).read_bytes()).hexdigest() != external[field]:
                    raise InputRefusal("external_input_digest_mismatch")
            input_record = {"host": "Air", "l9_audit": document["l9_audit"],
                            "run_inputs_sha256": args.inputs_sha256, "external_supplied": supplied}
            for name, sha in {
                "configs/b6/registration/acceptance.json": "ea130c87ece4e8b557a6357f1f75df045b5a0a738db18fe5ee990a7b539ce2a8",
                "configs/b6/registration/identity_pins.json": "513d7d4a98f464c7236b34c53f51cd523a9f45b4d9f05f2282a4a22424b4841d",
            }.items():
                if hashlib.sha256((ROOT_DIR / name).read_bytes()).hexdigest() != sha:
                    raise InputRefusal("registration_digest_mismatch")
        archives = args.session if args.command == "block" else [args.session]
        contexts = []
        for archive in archives:
            pin = session_input_pin(pins, archive)
            if args.inputs and pin is None:
                raise InputRefusal("session_input_pin_missing")
            if pin is not None:
                context = AuthenticatedInputs(archive, pin)
                contexts.append(context)
        if args.workers > 1:
            pool = MemberPool(args.workers, contexts)
        if args.command == "block":
            b5 = json.loads(Path(args.block5).read_text(encoding="utf-8")) if args.block5 else None
            sessions, results, lines = recompute_block(args.session, args.loop_attempts, flags, b5, args.closed,
                                                       args.loop_state, pins, pool)
            if pins:
                require_production_coverage(results, lines)
            input_record["census"] = {sid: s.inputs.verify_census() for sid, s in sessions.items() if s.inputs}
            restricted, public = finish_recompute("BLOCK", sessions, results, lines, flags,
                                                  {"closed": args.closed, "block5_input": bool(b5), "inputs": input_record})
        else:
            attempts = read_attempts(args.loop_attempts, flags)
            s = Session(args.session, flags, attempts, reharvested=read_reharvested(args.loop_state, flags),
                        inputs=contexts[0] if contexts else None, pool=pool,
                        input_pin=session_input_pin(pins, args.session))
            r = compute_session(s)
            if r["pack"] == "GAMMA":
                # Same day as harvest: the paired floors may not exist yet; contrasts carry no floor gate.
                attach_gamma(r, s, {}, None, False)
            r["quantities"] = session_quantities(r)
            if r["pack"] == "GAMMA":
                r["quantities"] = single_gamma_view(r["quantities"])
                r["deferred_to_block_run"] = list(SINGLE_GAMMA_DEFERRED)
            r.pop("_selections", None)
            if s.inputs:
                input_record["census"] = {s.session_id: s.inputs.verify_census()}
            restricted, public = finish_recompute("SINGLE_SESSION", {s.session_id: s}, {s.session_id: r}, None, flags)
            restricted["inputs"] = input_record
        public = write_outputs(args.restricted_out, args.public_out, restricted, public)
    except SyntheticOnlyRefusal as exc:
        print("refused: " + str(exc), file=sys.stderr)
        return 4
    except (InputRefusal, KeyError, ValueError, OSError, TypeError, ArithmeticError) as exc:
        print("refused: " + (str(exc) if isinstance(exc, InputRefusal) else type(exc).__name__), file=sys.stderr)
        return 4
    finally:
        if pool:
            pool.close()
    print("recompute sessions=" + str(len(public["sessions"])) + " flags=" + str(public["flag_count"])
          + " comparison_stopped=" + json.dumps(public["comparison_stopped"])
          + " restricted_sha256=" + public["restricted_sha256"])
    return 3 if public["comparison_stopped"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
