"""Validate a look manifest (RL-150 R4, RL-166) and resolve the spans a look may open. Opens no energy.

A look manifest is the file, beside the leg kits and never inside one, that fixes before any
development energy is read what a look reads, how it fits, which inclusion rules it judges and what
it prints (freeze 1, RL-149 section 2.6 as amended by RL-150 R4 and RL-166). Schema
``joulewise.cadence_look_manifest.v1``; the human-readable copy is
``docs/process/cadence/looks/look_manifest.schema.json`` and the spec is
``docs/process/cadence_look_manifest.md``.

Four checks, each a pure function over JSON and repository source:

* ``validate_manifest(doc, final=None)``: the closed structure, the required fields, and the
  ruling-derived invariants (phases a look may read, the leg types, the predictor lists, the two
  stages, inclusion rules 3 and 4 at the look, the required prints and decisions, the thresholds
  RL-166 fixed, freezes, one analyst seat). Placeholders: ``PENDING:CODE`` only as the sha256 of a
  pinned code or schema file not yet written (RL-166 section 2 item 3), ``PENDING:Qn`` only for an
  open question the manifest carries. A committed manifest carries neither.
* ``check_repo(doc, repo, kit_paths)``: the pinned hashes match the repository; no look code path is
  a leg kit's frozen path; no frozen ``.py`` path imports look code (RL-150 R4); the fit code never
  reads the ``condition`` field (RL-150 R6).
* ``validate_look_ledger(doc, repo=None)``: ``docs/process/cadence/looks/LOOKS.json`` (RL-166 Q18).
* ``resolve_roster(doc, ledger, manifest_sha256)``: at the look, before anything is opened, the
  spans the look reads. A span that is not desk-final where the look waits for it, whose energy seal
  is broken or that an earlier energy read named (unsealed), or whose phase the look may not read
  (out of phase) is refused; the ledger must carry this manifest's hash (RL-166 Q18).

Nothing here opens a custody, energy, power, meter or journal file. It reads the manifest, the span
ledger and the look ledger (operational JSON), kit files and repository source only.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import re

SCHEMA = "joulewise.cadence_look_manifest.v1"
LEDGER_SCHEMA = "joulewise.cadence_span_ledger.v1"
LOOK_LEDGER_SCHEMA = "joulewise.cadence_look_ledger.v1"
LOOK_LEDGER_PATH = "docs/process/cadence/looks/LOOKS.json"
LOOK_LEDGER_STATUSES = ("draft", "committed", "stage1_committed", "run", "frozen", "superseded")

TOP_KEYS = {"schema", "look_id", "look_kind", "status", "title", "rulings", "when", "stages", "reads", "energy",
            "fit", "inclusion", "outputs", "decisions", "later_looks", "freeze1", "freeze2", "custody", "review",
            "open_questions"}
LOOK_KINDS = {"interim", "qualification", "controls"}
STATUSES = {"draft", "committed"}

LOOK_ID_RE = re.compile(r"lm-[a-z0-9][a-z0-9-]{2,40}")
BLOCK_ID_RE = re.compile(r"[a-z0-9][a-z0-9-]{2,40}")
SPAN_ID_RE = re.compile(r"[a-z0-9][a-z0-9-]{2,60}")
RULING_RE = re.compile(r"RL-\d+[a-z]?(?: (?:§\d{1,2}(?:\.\d{1,2})?|R\d|Q\d{1,2}|F\d{1,2})(?:[ ,].*)?)?")
SHA_RE = re.compile(r"[0-9a-f]{64}")
PENDING_Q_RE = re.compile(r"PENDING:(Q\d{1,2})\b")
PENDING_CODE = "PENDING:CODE"
QID_RE = re.compile(r"Q\d{1,2}")
SPAN_SELECTORS = ("all_desk_final", "desk_final_if_any")

STEP3_PATH = "joulewise/cadence_looks/step3_energy_ratios.py"
STEP3_SHA256 = "84a1a5530ab06e688b000c84f248b2c4e561e8330f37d3132ec47aa2572eb173"   # RL-166 Q6
STEP3_ADAPTER_PATH = "joulewise/cadence_looks/step3_roster.py"
REQUIRED_CODE_PATHS = {"interim": {"joulewise/cadence_looks/fit_interim.py", "joulewise/cadence_looks/inclusion_34.py",
                                   STEP3_PATH, STEP3_ADAPTER_PATH, "scripts/cadence_look_run.py"}}   # RL-166 Q1

# Which block phases each look may read, by role (RL-149 sections 2.3 and 2.6; RL-157 section 4).
# Phases are BLOCK-QUEUE's (joulewise/cadence/blocks.py PHASES). hp-01 is phase "extension".
ALLOWED_PHASES = {
    ("interim", "fit"): {"pilot", "development"},
    ("interim", "describe"): {"extension"},
    ("qualification", "fit"): set(),             # nothing is refitted on qualification legs (RL-149 2.6 item 2)
    ("qualification", "describe"): {"qualification"},
    ("controls", "describe"): {"extension"},
    ("controls", "fit"): set(),
}
# Blocks a look never reads, by id prefix, whatever phase the ledger gives them.
FORBIDDEN_BLOCK_PREFIX = {
    "interim": ("qual-", "ctl-", "reserve-", "f0-", "f2-", "f3-", "partc-", "w1", "c1", "t1"),
    "qualification": ("dev-", "hp-", "ctl-", "f0-", "f2-", "f3-", "partc-", "w1", "c1", "t1"),
    "controls": ("dev-", "hp-", "qual-", "f0-", "f2-", "f3-", "partc-", "w1", "c1", "t1"),
}
DESCRIBE_ONLY_PREFIX = ("hp-",)                   # never in the fit (RL-149 2.3, 2.5)
LEG_TYPES = {"A", "H", "L", "M", "T", "C"}         # RL-149 section 2.2
LEG_TYPES_NEVER = {"interim": {"T", "L", "M", "C"}}  # RL-166 Q14 (T); L and M are qualification, C is ctl-01

ENERGY_CHANNELS = {"gpu_rail", "dc_in", "cpu_rail", "ane_rail", "package", "smc_system_total"}
REQUIRED_CHANNELS = {"interim": {"gpu_rail", "dc_in"}}   # RL-149 2.4 rule 4, 2.6; RL-166 Q17: these only

# RL-149 section 2.7 as amended by RL-150 R1 and fixed by RL-166 Q1, Q2 and Q4. Counts, the count-derived
# clock, the frozen rates, the start readings and the onset predicted from them. Nothing read inside a turn.
ALLOWED_PREDICTORS = {"prefill_tokens", "decode_tokens", "decode_block_tokens", "context_tokens", "turn_index",
                      "prefill_rate_frozen", "decode_rate_frozen", "load_seconds_from_counts",
                      "prefill_seconds_from_counts", "segment_duration_s", "segment_midpoint_s", "start_tf08",
                      "start_fan_rpm", "start_tv0h_excess_over_soak_reference", "predicted_onset_s"}
ONSET_PREDICTORS = {"start_tf08", "start_fan_rpm", "start_tv0h_excess_over_soak_reference",
                    "prefill_seconds_from_counts"}                                           # RL-166 Q4
REQUIRED_FORBIDDEN = {"in_turn_reading", "in_turn_clock", "in_turn_state", "in_turn_duration",
                      "start_tv0h_raw", "condition", "kit_start_band", "kit_g0_shape", "prompt_size_cell_effect"}
REQUIRED_READS_NEVER = {"condition", "kit_start_band", "kit_g0_shape"}  # RL-150 R6; RL-150 R2; RL-161 F12

INCLUSION_RULE_IDS = {1: "ran_to_cap", 2: "g0_released", 3: "sidecar_coverage", 4: "km003c_clean",
                      5: "not_a_contaminated_attempt", 6: "block_power_mode"}
LOOK_JUDGED_RULES = {3, 4}                        # RL-150 R9: "Rules 3 and 4 are judged at a look"

REQUIRED_PRINTS = {
    "interim": {"inclusion_table", "rates", "onset_fit", "onset_lodo_error", "heat_term_fit",
                "lodo_rel_error_hot_stretch", "lodo_rel_error_leg", "holdout_rms_rel_error", "without_heat_columns",
                "per_leg_relative_residuals", "prefix_length_bias", "high_power_table", "step3_statistic_iii",
                "qualified_interim_half", "marked_span_sensitivity", "realized_prompt_tokens", "disclosure"},
}
PREFIX_RATIOS = [1.10, 1.30, 1.374]                # RL-150 section 3.2 ("the looks print ... 1.10, 1.30 and 1.374")
REQUIRED_CARRIES = {"model_sha256", "qualified"}   # RL-149 section 4
# The thresholds RL-166 fixed, by decision id. None: the decision carries no threshold.
REQUIRED_DECISIONS = {"interim": {"drift_tripwire": 0.08, "qualified_interim_half": 0.02, "hp01_included_below_9": 9,
                                  "stage1_tripwires": None, "step3_cell_not_run": 2, "extension_rule": None}}
DRIFT_FALLBACK = 0.04                              # RL-166 Q11
# RL-166 Q8; ids as the stage-1 output (level D, docs/process/cadence_look_fit_interface.md section 3.3) names them
STAGE1_TRIPWIRES = {"dev_included_below_45": 45, "days_below_3": 3, "cell_below_10": 10,
                    "start_reading_invalid_over_10pct": 0.10, "hp01_below_9": 9}
RETIRED_DECISION_RE = re.compile(r"(?i)rule[_-]?p|s_?w_selection|one_decision")  # RL-151 section 2.1
FREEZE2_COMMIT_BEFORE = {"qualification_energy_opened", "qualification_leg_runs", "phase_boundary_crossed",
                         "release_run_inputs_signed"}

CODE_SUFFIXES = (".py", ".json")
CONDITION_RE = re.compile(r"""(?x)(["']condition["']|\.condition\b|\bcondition\s*=)""")
# A deny-list that refuses the field is not a read of it (RL-150 R6): FORBIDDEN_FIELDS = ("condition", ...).
DENY_LIST_LINE_RE = re.compile(r"^\s*[A-Z0-9_]*(FORBIDDEN|DENY|DENIED|REFUSED)[A-Z0-9_]*\s*=")


class ManifestError(ValueError):
    def __init__(self, problems):
        self.problems = list(problems)
        super().__init__("; ".join(self.problems))


# ---------------------------------------------------------------------------------------------- helpers

def _closed(obj, keys, where, problems, optional=()):
    if not isinstance(obj, dict):
        problems.append(f"{where}: object")
        return False
    keys, optional = set(keys), set(optional)
    for k in sorted(set(obj) - keys - optional):
        problems.append(f"{where}: unknown key {k!r}")
    for k in sorted(keys - set(obj)):
        problems.append(f"{where}: missing key {k!r}")
    return True


def _text(v):
    return isinstance(v, str) and v.strip() != ""


def _texts(v, where, problems, allowed=None):
    if not (isinstance(v, list) and v and all(_text(x) for x in v)):
        problems.append(f"{where}: non-empty list of text")
        return []
    if allowed is not None and set(v) - set(allowed):
        problems.append(f"{where}: unknown values {sorted(set(v) - set(allowed))}")
    return v


def _cites(v):
    return isinstance(v, list) and v and all(isinstance(c, str) and RULING_RE.fullmatch(c) for c in v)


def _need_cite(obj, where, problems):
    if not _cites(obj.get("cite")):
        problems.append(f"{where}.cite: a non-empty list of ruling cites (RL-n ...)")


def _strings(node, path="$"):
    if isinstance(node, dict):
        for k, v in node.items():
            yield from _strings(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _strings(v, f"{path}[{i}]")
    elif isinstance(node, str):
        yield path, node


def _number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _repo_path_ok(p):
    if not isinstance(p, str) or not p or p.startswith(("/", "~")) or "\\" in p:
        return False
    parts = PurePosixPath(p).parts
    return ".." not in parts and p.endswith(CODE_SUFFIXES)


def _code_ref(ref, where, problems, final):
    if not _closed(ref, {"path", "sha256"}, where, problems):
        return
    if not _repo_path_ok(ref.get("path")):
        problems.append(f"{where}.path: repository-relative .py or .json path, no '..'")
    sha = ref.get("sha256")
    if not (isinstance(sha, str) and (SHA_RE.fullmatch(sha) or (not final and sha == PENDING_CODE))):
        problems.append(f"{where}.sha256: 64 lowercase hex" + ("" if final else " or PENDING:CODE"))


def code_refs(doc):
    """Every pinned file reference in the manifest: (where, path, sha256)."""
    out = []
    fit = doc.get("fit") or {}
    for i, ref in enumerate(fit.get("code") or []):
        if isinstance(ref, dict):
            out.append((f"fit.code[{i}]", ref.get("path"), ref.get("sha256")))
    s3 = fit.get("step3") or {}
    for key in ("code", "adapter"):
        if isinstance(s3.get(key), dict):
            out.append((f"fit.step3.{key}", s3[key].get("path"), s3[key].get("sha256")))
    for i, rule in enumerate((doc.get("inclusion") or {}).get("rules") or []):
        if isinstance(rule, dict) and isinstance(rule.get("code"), dict):
            out.append((f"inclusion.rules[{i}].code", rule["code"].get("path"), rule["code"].get("sha256")))
    for where, node in (("outputs.schema", (doc.get("outputs") or {}).get("schema")),
                        ("stages.stage1.schema", ((doc.get("stages") or {}).get("stage1") or {}).get("schema"))):
        if isinstance(node, dict):
            out.append((where, node.get("path"), node.get("sha256")))
    return out


def _pinned_paths(doc):
    """path -> sha256 over every reference; two references to one path must agree."""
    pins = {}
    for _, path, sha in code_refs(doc):
        pins.setdefault(path, set()).add(sha)
    return pins


# ---------------------------------------------------------------------------------------------- manifest

def validate_manifest(doc, *, final=None):
    """Raise ManifestError listing every problem; return the open placeholders as [(json path, id)].

    ``final`` defaults to the manifest's own status: a ``committed`` manifest may carry no placeholder."""
    problems = []
    if not isinstance(doc, dict):
        raise ManifestError(["manifest: object"])
    _closed(doc, TOP_KEYS, "manifest", problems)
    if final is None:
        final = doc.get("status") == "committed"
    if doc.get("schema") != SCHEMA:
        problems.append(f"schema: {SCHEMA}")
    if not (isinstance(doc.get("look_id"), str) and LOOK_ID_RE.fullmatch(doc["look_id"])):
        problems.append("look_id: lm-<lowercase id>")
    kind = doc.get("look_kind")
    if kind not in LOOK_KINDS:
        problems.append(f"look_kind: one of {sorted(LOOK_KINDS)}")
    if doc.get("status") not in STATUSES:
        problems.append(f"status: one of {sorted(STATUSES)}")
    if final and doc.get("status") != "committed":
        problems.append("status: a final check needs status 'committed'")
    if not _text(doc.get("title")):
        problems.append("title: text")
    rulings = doc.get("rulings")
    if not _cites(rulings):
        problems.append("rulings: a non-empty list of ruling cites")
    else:
        for need in ("RL-149 §2.6", "RL-150 R4", "RL-166 §1"):
            if need not in rulings:
                problems.append(f"rulings: must cite {need!r}")

    qids = _open_questions(doc.get("open_questions"), problems)
    _when(doc.get("when"), kind, problems)
    _stages(doc.get("stages"), kind, problems, final)
    _reads(doc.get("reads"), kind, doc.get("when"), problems)
    _energy(doc.get("energy"), kind, problems)
    _fit(doc.get("fit"), kind, problems, final)
    _inclusion(doc.get("inclusion"), problems, final)
    _outputs(doc.get("outputs"), kind, problems, final)
    _decisions(doc.get("decisions"), kind, problems)
    _later_looks(doc.get("later_looks"), problems)
    _freezes(doc.get("freeze1"), doc.get("freeze2"), problems)
    _custody(doc.get("custody"), problems)
    _review(doc.get("review"), problems)
    for path, shas in _pinned_paths(doc).items():
        if len(shas) > 1:
            problems.append(f"{path}: pinned with different sha256 values {sorted(shas)}")

    pending = []
    for path, s in _strings(doc):
        if path.startswith("$.open_questions"):
            continue
        for m in PENDING_Q_RE.finditer(s):
            pending.append((path, m.group(1)))
            if m.group(1) not in qids:
                problems.append(f"{path}: placeholder names {m.group(1)}, which is not an open question")
        if s == PENDING_CODE:
            pending.append((path, "CODE"))
            if not path.endswith(".sha256"):
                problems.append(f"{path}: PENDING:CODE stands only for the sha256 of a file not yet written")
        elif "PENDING" in s and not PENDING_Q_RE.search(s):
            problems.append(f"{path}: a placeholder is written PENDING:Qn or, for a sha256, PENDING:CODE")
    if final and pending:
        problems.append(f"a committed manifest carries {len(pending)} placeholder(s): "
                        + ", ".join(sorted({p for p, _ in pending}))[:300])
    if final and qids:
        problems.append("a committed manifest carries open questions: " + ", ".join(sorted(qids)))
    if problems:
        raise ManifestError(problems)
    return pending


def _open_questions(qs, problems):
    if not isinstance(qs, list):
        problems.append("open_questions: list (empty in a committed manifest)")
        return set()
    ids = set()
    for i, q in enumerate(qs):
        where = f"open_questions[{i}]"
        if _closed(q, {"id", "question", "proposal", "cite"}, where, problems):
            if not (isinstance(q.get("id"), str) and QID_RE.fullmatch(q["id"])) or q["id"] in ids:
                problems.append(f"{where}.id: unique Qn")
            ids.add(q.get("id"))
            if not _text(q.get("question")):
                problems.append(f"{where}.question: text")
            _need_cite(q, where, problems)
    return ids


def _when(w, kind, problems):
    if not _closed(w, {"after_desk_final", "describe_blocks_rule", "before", "cite"}, "when", problems):
        return
    blocks = w.get("after_desk_final")
    if not (isinstance(blocks, list) and blocks and all(isinstance(b, str) and BLOCK_ID_RE.fullmatch(b) for b in blocks)):
        problems.append("when.after_desk_final: non-empty list of block ids")
    if kind == "interim" and isinstance(blocks, list):
        for b in ("dev-01", "dev-02", "dev-03", "dev-04", "dev-05"):
            if b not in blocks:
                problems.append(f"when.after_desk_final: the interim look waits for {b} (RL-155 §3.3, slot 11)")
        for b in blocks:
            if b.startswith(("hp-", "reserve-")):
                problems.append(f"when.after_desk_final: the look does not wait for {b} (RL-166 Q9, Q13)")
    _texts(w.get("before"), "when.before", problems)
    if not _text(w.get("describe_blocks_rule")):
        problems.append("when.describe_blocks_rule: text")
    _need_cite(w, "when", problems)


def _stages(st, kind, problems, final):
    if not _closed(st, {"stage1", "stage2", "tripwires", "tripwire_action", "cite"}, "stages", problems):
        return
    _need_cite(st, "stages", problems)
    s1 = st.get("stage1")
    if _closed(s1, {"opens", "writes", "schema", "committed_before_stage2", "dry_run", "cite"}, "stages.stage1",
               problems):
        opens = _texts(s1.get("opens"), "stages.stage1.opens", problems, allowed=("inclusion", "journal"))
        if "energy" in opens:
            problems.append("stages.stage1.opens: stage 1 opens no energy (RL-166 Q8)")
        _texts(s1.get("writes"), "stages.stage1.writes", problems)
        _code_ref(s1.get("schema"), "stages.stage1.schema", problems, final)
        if s1.get("committed_before_stage2") is not True:
            problems.append("stages.stage1.committed_before_stage2: true (RL-166 Q8)")
        if not _text(s1.get("dry_run")):
            problems.append("stages.stage1.dry_run: text")
        _need_cite(s1, "stages.stage1", problems)
    s2 = st.get("stage2")
    if _closed(s2, {"opens", "roster_source", "time_budget_s", "cite"}, "stages.stage2", problems):
        _texts(s2.get("opens"), "stages.stage2.opens", problems, allowed=("energy", "journal"))
        if not (_text(s2.get("roster_source")) and "sha256" in s2["roster_source"]):
            problems.append("stages.stage2.roster_source: stage 1's committed output, taken by sha256 (RL-166 Q8)")
        if not (_number(s2.get("time_budget_s")) and 0 < s2["time_budget_s"] <= 1200):
            problems.append("stages.stage2.time_budget_s: at most 1200 (RL-166 §2)")
        _need_cite(s2, "stages.stage2", problems)
    tws = st.get("tripwires")
    got = {}
    for i, t in enumerate(tws if isinstance(tws, list) else []):
        if _closed(t, {"id", "threshold", "cite"}, f"stages.tripwires[{i}]", problems):
            got[t.get("id")] = t.get("threshold")
            _need_cite(t, f"stages.tripwires[{i}]", problems)
    if kind == "interim":
        for tid, th in STAGE1_TRIPWIRES.items():
            if got.get(tid) != th:
                problems.append(f"stages.tripwires: {tid} with threshold {th} (RL-166 Q8)")
    if not _text(st.get("tripwire_action")):
        problems.append("stages.tripwire_action: text")


def _reads(r, kind, when, problems):
    if not _closed(r, {"blocks", "leg_types_read", "leg_types_never", "attempts", "day_rule", "never_read",
                       "custody_files", "cite"}, "reads", problems):
        return
    _need_cite(r, "reads", problems)
    if r.get("attempts") != "accepted_only":
        problems.append("reads.attempts: 'accepted_only' (a rejected attempt runtime.rejected<N> is never opened)")
    if not _text(r.get("day_rule")):
        problems.append("reads.day_rule: text")
    read_types = set(_texts(r.get("leg_types_read"), "reads.leg_types_read", problems, allowed=LEG_TYPES))
    never_types = set(_texts(r.get("leg_types_never"), "reads.leg_types_never", problems, allowed=LEG_TYPES))
    if read_types & never_types:
        problems.append(f"reads: leg types both read and never read {sorted(read_types & never_types)}")
    for t in sorted(LEG_TYPES_NEVER.get(kind, set()) - never_types):
        problems.append(f"reads.leg_types_never: a {kind} look never reads type {t}"
                        + (" (RL-166 Q14)" if t == "T" else ""))
    blocks = r.get("blocks")
    if not (isinstance(blocks, list) and blocks):
        problems.append("reads.blocks: non-empty list")
        blocks = []
    seen, fit_blocks = set(), set()
    for i, b in enumerate(blocks):
        where = f"reads.blocks[{i}]"
        if not _closed(b, {"block_id", "phase", "role", "kit_sha256", "spans", "cite"}, where, problems,
                       optional={"serves_phase"}):
            continue
        bid, role, phase = b.get("block_id"), b.get("role"), b.get("phase")
        if not (isinstance(bid, str) and BLOCK_ID_RE.fullmatch(bid)) or bid in seen:
            problems.append(f"{where}.block_id: unique lowercase id")
        seen.add(bid)
        if role not in ("fit", "describe"):
            problems.append(f"{where}.role: 'fit' or 'describe'")
            continue
        if role == "fit" and phase != "reserve":
            fit_blocks.add(bid)
        for reason in block_phase_problems(kind, bid, phase, role, b.get("serves_phase")):
            problems.append(f"{where}: {reason}")
        sha = b.get("kit_sha256")
        if not (sha is None or (isinstance(sha, str) and SHA_RE.fullmatch(sha))):
            problems.append(f"{where}.kit_sha256: 64 hex or null")
        spans = b.get("spans")
        if spans not in SPAN_SELECTORS and not (isinstance(spans, list) and spans and all(
                isinstance(s, str) and SPAN_ID_RE.fullmatch(s) for s in spans)):
            problems.append(f"{where}.spans: one of {SPAN_SELECTORS} or a non-empty list of span ids")
        waited = isinstance(when, dict) and bid in (when.get("after_desk_final") or [])
        if spans == "desk_final_if_any" and waited:
            problems.append(f"{where}.spans: the look waits for {bid}, so its spans are 'all_desk_final'")
        if spans == "all_desk_final" and (phase == "reserve" or bid.startswith(DESCRIBE_ONLY_PREFIX)):
            problems.append(f"{where}.spans: the look does not wait for {bid}: 'desk_final_if_any' (RL-166 Q9, Q13)")
        _need_cite(b, where, problems)
    if isinstance(when, dict) and isinstance(when.get("after_desk_final"), list):
        for bid in when["after_desk_final"]:
            if bid.startswith("dev-") and bid not in fit_blocks:
                problems.append(f"reads.blocks: {bid} is waited for but not read in the fit")
    nr = r.get("never_read")
    if not (isinstance(nr, list) and nr):
        problems.append("reads.never_read: non-empty list")
    else:
        for i, item in enumerate(nr):
            if _closed(item, {"what", "cite"}, f"reads.never_read[{i}]", problems):
                _need_cite(item, f"reads.never_read[{i}]", problems)
        if kind == "interim" and not any("type-T" in str(x.get("what", "")) for x in nr if isinstance(x, dict)):
            problems.append("reads.never_read: names the type-T legs (RL-166 Q14)")
    cf = r.get("custody_files")
    if not isinstance(cf, list):
        problems.append("reads.custody_files: list of {basename, scope, carries, stage}")
    else:
        for j, x in enumerate(cf):
            if not _closed(x, {"basename", "scope", "carries", "stage"}, f"reads.custody_files[{j}]", problems):
                continue
            if x.get("stage") not in ("inclusion", "energy", "journal"):
                problems.append(f"reads.custody_files[{j}].stage: inclusion, energy or journal")
            if x.get("stage") in ("inclusion", "journal") and x.get("carries") == "energy":
                problems.append(f"reads.custody_files[{j}]: stage 1 opens no energy file (RL-166 Q8)")


def block_phase_problems(kind, block_id, phase, role, serves_phase=None):
    """Why a block may not be read by this look in this role (empty when it may)."""
    out = []
    if not isinstance(block_id, str):
        return ["block id missing"]
    if kind in FORBIDDEN_BLOCK_PREFIX and block_id.startswith(FORBIDDEN_BLOCK_PREFIX[kind]) and phase != "reserve":
        out.append(f"out of phase: a {kind} look never reads {block_id}")
    if role == "fit" and block_id.startswith(DESCRIBE_ONLY_PREFIX):
        out.append(f"{block_id} is never in the fit (RL-149 §2.3, §2.5); its role is 'describe'")
    allowed = ALLOWED_PHASES.get((kind, role), set())
    if phase == "reserve":
        if not (role == "fit" and kind == "interim" and serves_phase == "development"):
            out.append("out of phase: a reserve block enters an interim look only as replacement development "
                       "legs (serves_phase 'development'; RL-149 §2.4, RL-166 Q13)")
    elif phase not in allowed:
        out.append(f"out of phase: phase {phase!r} is not read by a {kind} look as {role!r} "
                   f"(allowed {sorted(allowed) or 'none'})")
    return out


def _energy(e, kind, problems):
    if not _closed(e, {"channels", "not_read", "per_leg_energy_in_output", "per_leg_relative_residuals_in_output",
                       "cite"}, "energy", problems):
        return
    _need_cite(e, "energy", problems)
    ids = []
    for i, c in enumerate(e.get("channels") or []):
        where = f"energy.channels[{i}]"
        if _closed(c, {"id", "source", "unit", "read_as", "cite"}, where, problems):
            if c.get("id") not in ENERGY_CHANNELS:
                problems.append(f"{where}.id: one of {sorted(ENERGY_CHANNELS)}")
            ids.append(c.get("id"))
            for k in ("source", "unit", "read_as"):
                if not _text(c.get(k)):
                    problems.append(f"{where}.{k}: text")
            _need_cite(c, where, problems)
    if len(ids) != len(set(ids)):
        problems.append("energy.channels: each channel once")
    need = REQUIRED_CHANNELS.get(kind)
    if need is not None and set(ids) != need:
        problems.append(f"energy.channels: the {kind} look reads exactly {sorted(need)} (RL-166 Q17)")
    nr = e.get("not_read")
    if not isinstance(nr, list):
        problems.append("energy.not_read: list")
    else:
        for i, c in enumerate(nr):
            if _closed(c, {"id", "cite"}, f"energy.not_read[{i}]", problems) and c.get("id") in ids:
                problems.append(f"energy.not_read[{i}]: {c.get('id')} is also read")
    if e.get("per_leg_energy_in_output") is not False:
        problems.append("energy.per_leg_energy_in_output: false (no joule or watt per leg, turn or block; RL-166 Q16)")
    if not isinstance(e.get("per_leg_relative_residuals_in_output"), bool):
        problems.append("energy.per_leg_relative_residuals_in_output: boolean (RL-166 Q16 allows them)")


def _fit(f, kind, problems, final):
    keys = {"code", "runtime", "authors", "heat_term", "rates", "onset", "validation", "prefix_bias", "step3",
            "sensitivity", "reads_from_leg_record", "reads_never", "cite"}
    if not _closed(f, keys, "fit", problems):
        return
    _need_cite(f, "fit", problems)
    code = f.get("code")
    if not (isinstance(code, list) and code):
        problems.append("fit.code: non-empty list of {path, sha256}")
        code = []
    for i, ref in enumerate(code):
        _code_ref(ref, f"fit.code[{i}]", problems, final)
    paths = {ref.get("path") for ref in code if isinstance(ref, dict)}
    for p in sorted(REQUIRED_CODE_PATHS.get(kind, set()) - paths):
        problems.append(f"fit.code: pins {p} (RL-166 Q1)")
    if not (_text(f.get("runtime")) and "numpy" in f["runtime"] and "scipy" in f["runtime"] and "-I" in f["runtime"]):
        problems.append("fit.runtime: stdlib plus numpy, no scipy, run with -I, numpy version printed (RL-166 Q1)")
    if not (isinstance(f.get("authors"), dict) and f["authors"]):
        problems.append("fit.authors: object")
    ht = f.get("heat_term")
    if _closed(ht, {"unit", "segments", "count_clock", "start_readings", "form", "response", "base", "estimation",
                    "predictors", "forbidden_predictors", "sign_of_start_term_assumed", "missing_start_reading",
                    "out_of_state_start", "onset_not_estimable", "outside_calibrated_range", "cite"},
               "fit.heat_term", problems):
        if ht.get("unit") != "segment":
            problems.append("fit.heat_term.unit: 'segment' (RL-166 Q1)")
        preds = ht.get("predictors")
        if not (isinstance(preds, list) and preds and all(isinstance(p, str) for p in preds)):
            problems.append("fit.heat_term.predictors: non-empty list")
            preds = []
        bad = sorted(set(preds) - ALLOWED_PREDICTORS)
        if bad:
            problems.append(f"fit.heat_term.predictors: not allowed by RL-149 §2.7 / RL-150 R1 / RL-166: {bad}")
        forb = ht.get("forbidden_predictors")
        if not isinstance(forb, list):
            problems.append("fit.heat_term.forbidden_predictors: list")
            forb = []
        missing = sorted(REQUIRED_FORBIDDEN - set(forb))
        if missing:
            problems.append(f"fit.heat_term.forbidden_predictors: must list {missing}")
        if set(preds) & set(forb):
            problems.append(f"fit.heat_term: predictors and forbidden overlap {sorted(set(preds) & set(forb))}")
        if ht.get("sign_of_start_term_assumed") is not False:
            problems.append("fit.heat_term.sign_of_start_term_assumed: false (RL-149 §2.7; RL-166 Q1)")
        for k in ("segments", "count_clock", "start_readings", "form", "response", "base", "estimation",
                  "missing_start_reading", "out_of_state_start", "onset_not_estimable", "outside_calibrated_range"):
            if not _text(ht.get(k)):
                problems.append(f"fit.heat_term.{k}: text")
        _need_cite(ht, "fit.heat_term", problems)
    rates = f.get("rates")
    if _closed(rates, {"r_p", "r_d", "stage", "per_cell", "cite"}, "fit.rates", problems):
        if rates.get("stage") != "stage1":
            problems.append("fit.rates.stage: 'stage1' (token stamps, no energy; RL-166 Q5)")
        _need_cite(rates, "fit.rates", problems)
    on = f.get("onset")
    if _closed(on, {"stage", "reads_energy", "response", "predictors", "censoring", "estimable_when", "error",
                    "count_only_cut", "cite"}, "fit.onset", problems):
        if on.get("stage") != "stage1" or on.get("reads_energy") is not False:
            problems.append("fit.onset: fitted in stage 1, reading no energy (RL-166 Q4)")
        if not (_text(on.get("response")) and "start stamp" in on["response"]):
            problems.append("fit.onset.response: seconds from the turn's start stamp (RL-166 Q4)")
        op = on.get("predictors")
        if not (isinstance(op, list) and set(op) == ONSET_PREDICTORS):
            problems.append(f"fit.onset.predictors: exactly {sorted(ONSET_PREDICTORS)} (RL-166 Q4)")
        for k in ("censoring", "estimable_when", "error", "count_only_cut"):
            if not _text(on.get(k)):
                problems.append(f"fit.onset.{k}: text")
        _need_cite(on, "fit.onset", problems)
    v = f.get("validation")
    if _closed(v, {"unit", "method", "hot_stretch", "relative_error", "qualified_rule", "also_printed",
                   "min_calendar_days", "folds_refit", "cite"}, "fit.validation", problems):
        if v.get("unit") != "calendar_day" or v.get("method") != "leave_one_day_out":
            problems.append("fit.validation: unit 'calendar_day', method 'leave_one_day_out' (RL-149 §2.3)")
        if not (type(v.get("min_calendar_days")) is int and v["min_calendar_days"] >= 3):
            problems.append("fit.validation.min_calendar_days: at least 3 (RL-149 §2.3)")
        if set(v.get("folds_refit") or []) != {"base", "heat_term", "onset_model"}:
            problems.append("fit.validation.folds_refit: base, heat_term and onset_model; never rates or medians "
                            "(RL-166 Q3)")
        for k in ("hot_stretch", "relative_error", "qualified_rule", "also_printed"):
            if not _text(v.get(k)):
                problems.append(f"fit.validation.{k}: text")
        _need_cite(v, "fit.validation", problems)
    pb = f.get("prefix_bias")
    if _closed(pb, {"long", "short", "residuals", "statistic", "cite"}, "fit.prefix_bias", problems):
        _need_cite(pb, "fit.prefix_bias", problems)
    s3 = f.get("step3")
    if _closed(s3, {"code", "adapter", "statistic", "method", "kept", "dropped", "tripwire_reads", "leg_failure",
                    "cite"}, "fit.step3", problems):
        _code_ref(s3.get("code"), "fit.step3.code", problems, final)
        _code_ref(s3.get("adapter"), "fit.step3.adapter", problems, final)
        if isinstance(s3.get("code"), dict) and (s3["code"].get("path") != STEP3_PATH
                                                 or s3["code"].get("sha256") != STEP3_SHA256):
            problems.append(f"fit.step3.code: {STEP3_PATH} at sha256 {STEP3_SHA256[:12]}..., byte-identical (RL-166 Q6)")
        if isinstance(s3.get("adapter"), dict) and s3["adapter"].get("path") != STEP3_ADAPTER_PATH:
            problems.append(f"fit.step3.adapter.path: {STEP3_ADAPTER_PATH} (RL-166 Q1)")
        if s3.get("statistic") != "iii":
            problems.append("fit.step3.statistic: 'iii' (RL-151 §1.3 item 2)")
        for k in ("method", "tripwire_reads", "leg_failure"):
            if not _text(s3.get(k)):
                problems.append(f"fit.step3.{k}: text")
        for k in ("kept", "dropped"):
            _texts(s3.get(k), f"fit.step3.{k}", problems)
        _need_cite(s3, "fit.step3", problems)
    if not isinstance(f.get("sensitivity"), list):
        problems.append("fit.sensitivity: list")
    rn = f.get("reads_never")
    if not isinstance(rn, list) or REQUIRED_READS_NEVER - set(rn):
        problems.append(f"fit.reads_never: must list {sorted(REQUIRED_READS_NEVER)} (RL-150 R6, RL-161 F12)")
    if not (isinstance(f.get("reads_from_leg_record"), list) and f["reads_from_leg_record"]):
        problems.append("fit.reads_from_leg_record: non-empty list")


def _inclusion(inc, problems, final):
    if not _closed(inc, {"rules", "interval", "inclusion_reads_no_energy", "no_drop_by_outcome",
                         "verdicts_frozen_before_energy", "cite"}, "inclusion", problems):
        return
    _need_cite(inc, "inclusion", problems)
    if inc.get("inclusion_reads_no_energy") is not True:
        problems.append("inclusion.inclusion_reads_no_energy: true (RL-157 §4)")
    if inc.get("no_drop_by_outcome") is not True:
        problems.append("inclusion.no_drop_by_outcome: true (RL-149 §2.4)")
    if inc.get("verdicts_frozen_before_energy") is not True:
        problems.append("inclusion.verdicts_frozen_before_energy: true (RL-166 Q8)")
    if not (_text(inc.get("interval")) and "G0" in inc["interval"] and "last stamped token" in inc["interval"]):
        problems.append("inclusion.interval: G0's start to the last stamped token (RL-166 Q7)")
    seen = {}
    for i, rule in enumerate(inc.get("rules") or []):
        where = f"inclusion.rules[{i}]"
        if not _closed(rule, {"rule", "id", "text", "judged_at", "reads_energy", "cite"}, where, problems,
                       optional={"code"}):
            continue
        n = rule.get("rule")
        if n not in INCLUSION_RULE_IDS or rule.get("id") != INCLUSION_RULE_IDS.get(n) or n in seen:
            problems.append(f"{where}: rule 1-6 once each, id as RL-149 §2.4 (rule {n}: {INCLUSION_RULE_IDS.get(n)})")
            continue
        seen[n] = rule
        if rule.get("reads_energy") is not False:
            problems.append(f"{where}.reads_energy: false (inclusion reads no energy, RL-157 §4)")
        if n in LOOK_JUDGED_RULES and rule.get("judged_at") != "look":
            problems.append(f"{where}.judged_at: 'look' (RL-150 R9)")
        if n not in LOOK_JUDGED_RULES and rule.get("judged_at") not in ("runner", "look"):
            problems.append(f"{where}.judged_at: 'runner' or 'look'")
        if n in LOOK_JUDGED_RULES:
            if "code" not in rule:
                problems.append(f"{where}.code: the code that judges rule {n} is pinned in the manifest (RL-150 R4)")
            else:
                _code_ref(rule["code"], f"{where}.code", problems, final)
        if not _text(rule.get("text")):
            problems.append(f"{where}.text: the ruling's words")
        _need_cite(rule, where, problems)
    for n in sorted(set(INCLUSION_RULE_IDS) - set(seen)):
        problems.append(f"inclusion.rules: rule {n} ({INCLUSION_RULE_IDS[n]}) is missing")
    r3, r4 = seen.get(3), seen.get(4)
    if r3 is not None and "max(1 s, 5 periods)" not in str(r3.get("text")):
        problems.append("inclusion.rules rule 3: powermetrics gaps at most max(1 s, 5 periods), U1's number (RL-166 Q7)")
    if r4 is not None and "trailer counts zero" in str(r4.get("text")):
        problems.append("inclusion.rules rule 4: the 'trailer counts zero' clause is refused (RL-166 Q7)")


def _outputs(o, kind, problems, final):
    if not _closed(o, {"schema", "prints", "every_print_carries", "forbidden_content", "cite"}, "outputs", problems):
        return
    _need_cite(o, "outputs", problems)
    _code_ref(o.get("schema"), "outputs.schema", problems, final)
    ids = set()
    for i, p in enumerate(o.get("prints") or []):
        where = f"outputs.prints[{i}]"
        if not _closed(p, {"id", "what", "cite"}, where, problems, optional={"channels", "ratios", "caption"}):
            continue
        if p.get("id") in ids:
            problems.append(f"{where}.id: duplicate")
        ids.add(p.get("id"))
        if not _text(p.get("what")):
            problems.append(f"{where}.what: text")
        for ch in p.get("channels") or []:
            if ch not in ENERGY_CHANNELS:
                problems.append(f"{where}.channels: unknown channel {ch!r}")
        if p.get("id") == "prefix_length_bias" and p.get("ratios") != PREFIX_RATIOS:
            problems.append(f"{where}.ratios: {PREFIX_RATIOS} (RL-150 §3.2)")
        _need_cite(p, where, problems)
    for need in sorted(REQUIRED_PRINTS.get(kind, set()) - ids):
        problems.append(f"outputs.prints: the {kind} look prints {need}")
    carries = o.get("every_print_carries")
    if not isinstance(carries, list) or REQUIRED_CARRIES - set(carries):
        problems.append(f"outputs.every_print_carries: must include {sorted(REQUIRED_CARRIES)} (RL-149 §4)")
    if not (isinstance(o.get("forbidden_content"), list) and o["forbidden_content"]):
        problems.append("outputs.forbidden_content: non-empty list")


def _decisions(ds, kind, problems):
    if not isinstance(ds, list):
        problems.append("decisions: list")
        return
    got = {}
    for i, d in enumerate(ds):
        where = f"decisions[{i}]"
        if not _closed(d, {"id", "statistic", "rule", "action", "reads_energy", "cite"}, where, problems,
                       optional={"threshold", "fallback_threshold"}):
            continue
        if RETIRED_DECISION_RE.search(str(d.get("id"))):
            problems.append(f"{where}.id: Rule P and the interim look's one decision are retired (RL-151 §2.1)")
        if d.get("id") in got:
            problems.append(f"{where}.id: duplicate")
        got[d.get("id")] = d
        for k in ("threshold", "fallback_threshold"):
            if k in d and not _number(d[k]):
                problems.append(f"{where}.{k}: a number")
        if not isinstance(d.get("reads_energy"), bool):
            problems.append(f"{where}.reads_energy: boolean")
        for k in ("statistic", "rule", "action"):
            if not _text(d.get(k)):
                problems.append(f"{where}.{k}: text")
        _need_cite(d, where, problems)
    for did, th in REQUIRED_DECISIONS.get(kind, {}).items():
        d = got.get(did)
        if d is None:
            problems.append(f"decisions: the {kind} look carries {did}")
        elif th is not None and d.get("threshold") != th:
            problems.append(f"decisions {did}: threshold {th} (RL-166)")
    drift = got.get("drift_tripwire")
    if kind == "interim" and drift is not None and drift.get("fallback_threshold") != DRIFT_FALLBACK:
        problems.append(f"decisions drift_tripwire: fallback_threshold {DRIFT_FALLBACK} (RL-166 Q11)")


def _later_looks(ll, problems):
    if not isinstance(ll, list):
        problems.append("later_looks: list")
        return
    for i, x in enumerate(ll):
        where = f"later_looks[{i}]"
        if _closed(x, {"look_id", "look_kind", "declared_prints", "scorer", "committed_before", "cite"}, where,
                   problems):
            if not (isinstance(x.get("look_id"), str) and LOOK_ID_RE.fullmatch(x["look_id"])):
                problems.append(f"{where}.look_id: lm-<id>")
            if x.get("look_kind") not in LOOK_KINDS:
                problems.append(f"{where}.look_kind: one of {sorted(LOOK_KINDS)}")
            _texts(x.get("declared_prints"), f"{where}.declared_prints", problems)
            for k in ("scorer", "committed_before"):
                if not _text(x.get(k)):
                    problems.append(f"{where}.{k}: text")
            _need_cite(x, where, problems)


def _freezes(f1, f2, problems):
    if _closed(f1, {"contents", "committed_before", "ledger_pointer", "cite"}, "freeze1", problems):
        if f1.get("committed_before") != "any development energy is read":
            problems.append("freeze1.committed_before: 'any development energy is read' (RL-149 §2.6 item 1)")
        if not (isinstance(f1.get("contents"), list) and f1["contents"]):
            problems.append("freeze1.contents: non-empty list")
        if not (_text(f1.get("ledger_pointer")) and "LOOKS.json" in f1["ledger_pointer"]):
            problems.append("freeze1.ledger_pointer: the look ledger LOOKS.json (RL-166 Q18)")
        _need_cite(f1, "freeze1", problems)
    if _closed(f2, {"artifact", "contents", "commit_before", "used_by", "refit_on_qualification", "cite"}, "freeze2",
               problems):
        if f2.get("refit_on_qualification") is not False:
            problems.append("freeze2.refit_on_qualification: false (RL-149 §2.6 item 2)")
        cb = f2.get("commit_before")
        if not isinstance(cb, list) or FREEZE2_COMMIT_BEFORE - set(cb):
            problems.append(f"freeze2.commit_before: must include {sorted(FREEZE2_COMMIT_BEFORE)}")
        for k in ("contents", "used_by"):
            if not (isinstance(f2.get(k), list) and f2[k]):
                problems.append(f"freeze2.{k}: non-empty list")
        if not _text(f2.get("artifact")):
            problems.append("freeze2.artifact: text (the coefficient file's path)")
        _need_cite(f2, "freeze2", problems)


def _custody(c, problems):
    keys = {"runs_by", "seats", "lead_checks_output_against_schema", "custody_copy", "host", "no_import_by",
            "fit_paths_outside_kit_frozen_paths", "disclosure", "pre_run_check", "cite"}
    if not _closed(c, keys, "custody", problems):
        return
    if c.get("runs_by") != "analyst_seat" or c.get("seats") != 1:
        problems.append("custody: runs_by 'analyst_seat', seats 1 (RL-149 §2.6; RL-166 Q1)")
    if c.get("lead_checks_output_against_schema") is not True:
        problems.append("custody.lead_checks_output_against_schema: true (RL-149 §2.6)")
    if c.get("fit_paths_outside_kit_frozen_paths") is not True:
        problems.append("custody.fit_paths_outside_kit_frozen_paths: true (RL-150 R4)")
    if not (isinstance(c.get("no_import_by"), list) and c["no_import_by"]):
        problems.append("custody.no_import_by: non-empty list (the runner and the leg runtime, RL-150 R4)")
    for k in ("custody_copy", "host", "disclosure", "pre_run_check"):
        if not _text(c.get(k)):
            problems.append(f"custody.{k}: text")
    _need_cite(c, "custody", problems)


def _review(r, problems):
    if not _closed(r, {"cold_seat", "then", "paper_bound", "due", "cite"}, "review", problems):
        return
    if r.get("paper_bound") is not True:
        problems.append("review.paper_bound: true (RL-150 R4)")
    for k in ("cold_seat", "then", "due"):
        if not _text(r.get(k)):
            problems.append(f"review.{k}: text")
    _need_cite(r, "review", problems)


# ---------------------------------------------------------------------------------------------- repository

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _module_names(path):
    p = PurePosixPath(path)
    if p.suffix != ".py":
        return set()
    dotted = ".".join(p.with_suffix("").parts)
    return {dotted, p.stem}


def check_repo(doc, repo, kit_paths=(), *, final=None):
    """Hash the pinned files in ``repo`` and check the import and condition rules. Opens repository source
    and kit JSON only. Placeholders are skipped (``validate_manifest`` reports them).

    A draft may pin a file that is not on its own branch (code another seat writes on its own branch,
    pinned on a draft basis): that is returned as a warning. In a committed manifest (or ``final=True``) it
    is a problem. Returns the warnings."""
    repo = Path(repo)
    if final is None:
        final = doc.get("status") == "committed"
    problems, warnings = [], []
    code_paths = []
    for where, path, sha in code_refs(doc):
        if not (isinstance(path, str) and _repo_path_ok(path)):
            continue
        f = repo / path
        if path.endswith(".py"):
            code_paths.append(path)
        if not isinstance(sha, str) or not SHA_RE.fullmatch(sha):
            continue
        if not f.is_file():
            (problems if final else warnings).append(f"{where}: {path} is not in the repository"
                                                     + ("" if final else " (draft pin; checked where the file is)"))
            continue
        if sha256_file(f) != sha:
            problems.append(f"{where}: {path} sha256 differs from the pin")
    code_paths = sorted(set(code_paths))
    look_modules = {"joulewise.cadence_looks", "cadence_looks"}
    for p in code_paths:
        look_modules |= _module_names(p)
    import_re = re.compile(r"(?m)^\s*(?:from|import)\s+([\w.]+)")
    for kp in kit_paths:
        kit = json.loads(Path(kp).read_text(encoding="utf-8"))
        frozen = set(((kit.get("frozen") or {}).get("paths") or {}))
        for p in code_paths:
            if p in frozen:
                problems.append(f"{p} is a frozen path of kit {Path(kp).name}; look code makes no measurement "
                                "and must stay outside every leg kit (RL-150 R4)")
        if kit.get("looks"):
            problems.append(f"kit {Path(kp).name}: looks must stay [] (RL-150 R4)")
        for fp in sorted(frozen):
            if not fp.endswith(".py") or not (repo / fp).is_file():
                continue
            src = (repo / fp).read_text(encoding="utf-8", errors="replace")
            for mod in import_re.findall(src):
                if any(mod == m or mod.startswith(m + ".") for m in look_modules if "." in m) or \
                        mod.split(".")[-1] in {m for m in look_modules if "." not in m}:
                    problems.append(f"{fp} (frozen in {Path(kp).name}) imports {mod}; the runner and the leg "
                                    "runtime never import look code (RL-150 R4)")
    for p in code_paths:
        if not (repo / p).is_file():
            continue
        src = (repo / p).read_text(encoding="utf-8", errors="replace")
        for n, text in enumerate(src.splitlines(), 1):
            if CONDITION_RE.search(text) and not DENY_LIST_LINE_RE.match(text):
                problems.append(f"{p}:{n} reads a 'condition' field; look code never reads it (RL-150 R6)")
                break
    if problems:
        raise ManifestError(problems)
    return warnings


# ---------------------------------------------------------------------------------------------- look ledger

def validate_look_ledger(doc, repo=None):
    """``LOOKS.json`` (RL-166 Q18): look id, manifest path, sha256 and status per look. With ``repo``, each
    manifest exists, hashes to its pin, carries its look id, and a draft or committed manifest's status
    matches the ledger's. Returns the ledger."""
    problems = []
    if not _closed(doc, {"schema", "looks"}, "look ledger", problems):
        raise ManifestError(problems)
    if doc.get("schema") != LOOK_LEDGER_SCHEMA:
        problems.append(f"look ledger schema: {LOOK_LEDGER_SCHEMA}")
    seen = set()
    for i, row in enumerate(doc.get("looks") or []):
        where = f"looks[{i}]"
        if not _closed(row, {"look_id", "manifest_path", "sha256", "status"}, where, problems):
            continue
        lid = row.get("look_id")
        if not (isinstance(lid, str) and LOOK_ID_RE.fullmatch(lid)) or lid in seen:
            problems.append(f"{where}.look_id: unique lm-<id>")
        seen.add(lid)
        if row.get("status") not in LOOK_LEDGER_STATUSES:
            problems.append(f"{where}.status: one of {LOOK_LEDGER_STATUSES}")
        if not (isinstance(row.get("sha256"), str) and SHA_RE.fullmatch(row["sha256"])):
            problems.append(f"{where}.sha256: 64 hex")
        mp = row.get("manifest_path")
        if not (_repo_path_ok(mp) and str(mp).endswith(".json")):
            problems.append(f"{where}.manifest_path: repository-relative .json path")
            continue
        if repo is None:
            continue
        f = Path(repo) / mp
        if not f.is_file():
            problems.append(f"{where}: {mp} is not in the repository")
            continue
        if sha256_file(f) != row.get("sha256"):
            problems.append(f"{where}: {mp} sha256 differs from the ledger")
        man = json.loads(f.read_text(encoding="utf-8"))
        if man.get("look_id") != lid:
            problems.append(f"{where}: the manifest's look_id is {man.get('look_id')!r}")
        if row.get("status") == "draft" and man.get("status") != "draft":
            problems.append(f"{where}: ledger says draft, the manifest says {man.get('status')!r}")
        if row.get("status") != "draft" and man.get("status") != "committed":
            problems.append(f"{where}: ledger says {row.get('status')}, the manifest is not committed")
    if problems:
        raise ManifestError(problems)
    return doc


# ---------------------------------------------------------------------------------------------- roster

def validate_ledger(ledger):
    problems = []
    if not _closed(ledger, {"schema", "look_manifest", "spans", "energy_reads"}, "ledger", problems):
        raise ManifestError(problems)
    if ledger.get("schema") != LEDGER_SCHEMA:
        problems.append(f"ledger.schema: {LEDGER_SCHEMA}")
    lmf = ledger.get("look_manifest")
    if _closed(lmf, {"look_id", "sha256"}, "ledger.look_manifest", problems):
        if not (isinstance(lmf.get("sha256"), str) and SHA_RE.fullmatch(lmf["sha256"])):
            problems.append("ledger.look_manifest.sha256: 64 hex")
    seen = set()
    for i, s in enumerate(ledger.get("spans") or []):
        where = f"ledger.spans[{i}]"
        if _closed(s, {"span_id", "block_id", "phase", "desk_final", "energy_seal", "t0_local_date"}, where, problems,
                   optional={"serves_phase"}):
            if s.get("span_id") in seen:
                problems.append(f"{where}.span_id: duplicate")
            seen.add(s.get("span_id"))
            if s.get("energy_seal") not in ("sealed", "opened"):
                problems.append(f"{where}.energy_seal: 'sealed' or 'opened'")
            if not isinstance(s.get("desk_final"), bool):
                problems.append(f"{where}.desk_final: boolean")
            if not (isinstance(s.get("t0_local_date"), str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", s["t0_local_date"])):
                problems.append(f"{where}.t0_local_date: YYYY-MM-DD (a leg's day is its span's t0 date, RL-155a §1.2)")
    for i, r in enumerate(ledger.get("energy_reads") or []):
        if _closed(r, {"read_id", "spans", "cite"}, f"ledger.energy_reads[{i}]", problems):
            if not isinstance(r.get("spans"), list):
                problems.append(f"ledger.energy_reads[{i}].spans: list")
    if problems:
        raise ManifestError(problems)
    return ledger


def resolve_roster(doc, ledger, manifest_sha256=None):
    """The spans this look reads, resolved from the span ledger before anything is opened.

    Refuses: a ledger that does not carry this manifest's look id and hash (RL-166 Q18); a span the
    ledger does not know; a span named under a block it does not belong to; a span whose phase the look
    may not read (out of phase); a span of a waited-for block that is not desk-final; a span whose energy
    seal is broken or that an earlier energy read named (unsealed); a fit roster on fewer calendar days
    than the manifest's minimum. For a ``desk_final_if_any`` block (hp-01, reserve-01) a span that is not
    yet desk-final is skipped, as is a reserve span serving another phase. Returns
    [{span_id, block_id, role, t0_local_date}] in ledger order."""
    validate_ledger(ledger)
    problems = []
    lmf = ledger["look_manifest"]
    if lmf["look_id"] != doc.get("look_id"):
        problems.append(f"the span ledger is for {lmf['look_id']!r}, not {doc.get('look_id')!r}")
    if manifest_sha256 is not None and lmf["sha256"] != manifest_sha256:
        problems.append("the span ledger carries another manifest hash than the manifest's file (RL-166 Q18)")
    kind = doc.get("look_kind")
    by_id = {s["span_id"]: s for s in ledger["spans"]}
    opened = {sid: r["read_id"] for r in ledger["energy_reads"] for sid in r["spans"]}
    roster = []
    for b in (doc.get("reads") or {}).get("blocks") or []:
        bid, role, selector = b["block_id"], b["role"], b["spans"]
        if selector in SPAN_SELECTORS:
            chosen = [s for s in ledger["spans"] if s["block_id"] == bid]
            if selector == "desk_final_if_any":
                chosen = [s for s in chosen if s["desk_final"]
                          and (b["phase"] != "reserve" or s.get("serves_phase") == b.get("serves_phase"))]
            elif not chosen:
                problems.append(f"{bid}: no span of this block is in the ledger")
        else:
            chosen = []
            for sid in selector:
                s = by_id.get(sid)
                if s is None:
                    problems.append(f"{sid}: not in the span ledger")
                elif s["block_id"] != bid:
                    problems.append(f"{sid}: belongs to {s['block_id']}, not {bid}")
                else:
                    chosen.append(s)
        for s in chosen:
            sid = s["span_id"]
            reasons = block_phase_problems(kind, bid, s["phase"], role, s.get("serves_phase"))
            if s["phase"] != b["phase"]:
                reasons.append(f"out of phase: the ledger gives phase {s['phase']!r}, the manifest {b['phase']!r}")
            if not s["desk_final"]:
                reasons.append("not desk-final")
            if s["energy_seal"] != "sealed":
                reasons.append("unsealed: its energy seal is broken")
            if sid in opened:
                reasons.append(f"unsealed: energy read {opened[sid]} already named it")
            if reasons:
                problems.extend(f"{sid}: {r}" for r in reasons)
            else:
                roster.append({"span_id": sid, "block_id": bid, "role": role, "t0_local_date": s["t0_local_date"]})
    need_days = ((doc.get("fit") or {}).get("validation") or {}).get("min_calendar_days")
    fit_days = {r["t0_local_date"] for r in roster if r["role"] == "fit"}
    if not problems and isinstance(need_days, int) and len(fit_days) < need_days:
        problems.append(f"the fit roster covers {len(fit_days)} calendar day(s); leave-one-day-out needs "
                        f"{need_days} (RL-149 §2.3)")
    if problems:
        raise ManifestError(problems)
    return roster


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))
