"""Validate a look manifest (RL-150 R4) and resolve the spans a look may open. Opens no energy.

A look manifest is the file, beside the leg kits and never inside one, that fixes before any
development energy is read what a look reads, how it fits, which inclusion rules it judges and what
it prints (freeze 1, RL-149 section 2.6 as amended by RL-150 R4). Schema
``joulewise.cadence_look_manifest.v1``; the human-readable copy is
``docs/process/cadence/looks/look_manifest.schema.json`` and the spec is
``docs/process/cadence_look_manifest.md``.

Three checks, each a pure function over JSON and repository source:

* ``validate_manifest(doc, final=False)``: the closed structure, the required fields, and the
  ruling-derived invariants (phases a look may read, the predictor list, inclusion rules 3 and 4 at
  the look, the required prints, freezes, one analyst seat). With ``final=True`` (a committed
  manifest) no ``PENDING:Qn`` placeholder may remain. In a draft every placeholder must name an open
  question the manifest carries.
* ``check_repo(doc, repo, kit_paths)``: the pinned code hashes match the repository; no fit path is a
  leg kit's frozen path; no frozen ``.py`` path imports the look code (RL-150 R4); the fit code never
  reads the ``condition`` field (RL-150 R6).
* ``resolve_roster(doc, ledger)``: at the look, before anything is opened, the spans the look reads.
  A span that is not desk-final, whose energy seal is broken or that an earlier energy read named
  (unsealed), or whose phase the look may not read (out of phase) is refused.

Nothing here opens a custody, energy, power, meter or journal file. It reads the manifest, the span
ledger (operational JSON), kit files and repository source only.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import re

SCHEMA = "joulewise.cadence_look_manifest.v1"
LEDGER_SCHEMA = "joulewise.cadence_span_ledger.v1"

TOP_KEYS = {"schema", "look_id", "look_kind", "status", "title", "rulings", "when", "reads", "energy", "fit",
            "inclusion", "outputs", "decisions", "freeze1", "freeze2", "custody", "review", "open_questions"}
LOOK_KINDS = {"interim", "qualification", "controls"}
STATUSES = {"draft", "committed"}

LOOK_ID_RE = re.compile(r"lm-[a-z0-9][a-z0-9-]{2,40}")
BLOCK_ID_RE = re.compile(r"[a-z0-9][a-z0-9-]{2,40}")
SPAN_ID_RE = re.compile(r"[a-z0-9][a-z0-9-]{2,60}")
RULING_RE = re.compile(r"RL-\d+[a-z]?(?: (?:§\d{1,2}(?:\.\d{1,2})?|R\d|Q\d|F\d{1,2})(?:[ ,].*)?)?")
SHA_RE = re.compile(r"[0-9a-f]{64}")
PENDING_RE = re.compile(r"PENDING:(Q\d{1,2})\b")
QID_RE = re.compile(r"Q\d{1,2}")

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

ENERGY_CHANNELS = {"gpu_rail", "dc_in", "cpu_rail", "ane_rail", "package", "smc_system_total"}
REQUIRED_CHANNELS = {"interim": {"gpu_rail", "dc_in"}}  # RL-149 2.4 rule 4 and 2.6 ("the same for DC-in")

# RL-149 section 2.7 as amended by RL-150 R1 part 1 (and RL-158 Q1: excess over the soak reference).
ALLOWED_PREDICTORS = {"decode_tokens", "prefill_tokens", "turn_index", "prefill_rate_frozen",
                      "decode_rate_frozen", "load_seconds_from_counts", "start_tf08", "start_fan_rpm",
                      "start_tv0h_excess_over_soak_reference"}
REQUIRED_FORBIDDEN = {"in_turn_reading", "in_turn_clock", "in_turn_state", "in_turn_duration",
                      "start_tv0h_raw", "condition", "kit_start_band", "kit_g0_shape"}
REQUIRED_READS_NEVER = {"condition", "kit_start_band", "kit_g0_shape"}  # RL-150 R6; RL-150 R2; RL-161 F12

INCLUSION_RULE_IDS = {1: "ran_to_cap", 2: "g0_released", 3: "sidecar_coverage", 4: "km003c_clean",
                      5: "not_a_contaminated_attempt", 6: "block_power_mode"}
LOOK_JUDGED_RULES = {3, 4}                        # RL-150 R9: "Rules 3 and 4 are judged at a look"

REQUIRED_PRINTS = {
    "interim": {"inclusion_table", "heat_term_fit", "lodo_rel_error_hot_stretch", "lodo_rel_error_leg",
                "prefix_length_bias", "onset_fit", "onset_lodo_error", "high_power_table",
                "step3_statistic_iii", "qualified_interim_half", "marked_span_sensitivity",
                "realized_prompt_tokens", "disclosure"},
}
PREFIX_RATIOS = [1.10, 1.30, 1.374]                # RL-150 section 3.2 ("the looks print ... 1.10, 1.30 and 1.374")
REQUIRED_CARRIES = {"model_sha256", "qualified"}   # RL-149 section 4
REQUIRED_DECISIONS = {"interim": {"drift_tripwire", "qualified_interim_half", "hp01_included_below_9",
                                  "extension_rule"}}
RETIRED_DECISION_RE = re.compile(r"(?i)rule[_-]?p|s_?w_selection|one_decision")  # RL-151 section 2.1
FREEZE2_COMMIT_BEFORE = {"qualification_energy_opened", "qualification_leg_runs", "phase_boundary_crossed",
                         "release_run_inputs_signed"}

CODE_SUFFIXES = (".py", ".json")
CONDITION_RE = re.compile(r"""(?x)(["']condition["']|\.condition\b|\bcondition\s*=)""")


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


def _sha_ok(v, final):
    return isinstance(v, str) and (SHA_RE.fullmatch(v) or (not final and PENDING_RE.fullmatch(v)))


def _code_ref(ref, where, problems, final):
    if not _closed(ref, {"path", "sha256"}, where, problems):
        return
    p = ref.get("path")
    if isinstance(p, str) and PENDING_RE.fullmatch(p) and not final:
        pass
    elif not _repo_path_ok(p):
        problems.append(f"{where}.path: repository-relative .py or .json path, no '..'")
    if not _sha_ok(ref.get("sha256"), final):
        problems.append(f"{where}.sha256: 64 lowercase hex" + ("" if final else " or PENDING:Qn"))


def _repo_path_ok(p):
    if not isinstance(p, str) or not p or p.startswith(("/", "~")) or "\\" in p:
        return False
    parts = PurePosixPath(p).parts
    return ".." not in parts and p.endswith(CODE_SUFFIXES)


def code_refs(doc):
    """Every pinned code reference in the manifest: (where, path, sha256)."""
    out = []
    fit = doc.get("fit") or {}
    for i, ref in enumerate(fit.get("code") or []):
        out.append((f"fit.code[{i}]", ref.get("path"), ref.get("sha256")))
    s3 = fit.get("step3") or {}
    for key in ("code", "adapter"):
        if isinstance(s3.get(key), dict):
            out.append((f"fit.step3.{key}", s3[key].get("path"), s3[key].get("sha256")))
    for i, rule in enumerate((doc.get("inclusion") or {}).get("rules") or []):
        if isinstance(rule, dict) and isinstance(rule.get("code"), dict):
            out.append((f"inclusion.rules[{i}].code", rule["code"].get("path"), rule["code"].get("sha256")))
    sch = (doc.get("outputs") or {}).get("schema")
    if isinstance(sch, dict):
        out.append(("outputs.schema", sch.get("path"), sch.get("sha256")))
    return out


# ---------------------------------------------------------------------------------------------- manifest

def validate_manifest(doc, *, final=None):
    """Raise ManifestError listing every problem; return the list of open placeholders (draft only).

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
        for need in ("RL-149 §2.6", "RL-150 R4"):
            if need not in rulings:
                problems.append(f"rulings: must cite {need!r}")

    qids = _open_questions(doc.get("open_questions"), problems)
    _when(doc.get("when"), kind, problems)
    _reads(doc.get("reads"), kind, doc.get("when"), problems)
    _energy(doc.get("energy"), kind, problems)
    _fit(doc.get("fit"), problems, final)
    _inclusion(doc.get("inclusion"), problems, final)
    _outputs(doc.get("outputs"), kind, problems, final)
    _decisions(doc.get("decisions"), kind, problems)
    _freezes(doc.get("freeze1"), doc.get("freeze2"), problems)
    _custody(doc.get("custody"), problems)
    _review(doc.get("review"), problems)

    pending = []
    for path, s in _strings(doc):
        if path.startswith("$.open_questions"):
            continue
        for m in PENDING_RE.finditer(s):
            pending.append((path, m.group(1)))
            if m.group(1) not in qids:
                problems.append(f"{path}: placeholder names {m.group(1)}, which is not an open question")
        if "PENDING" in s and not PENDING_RE.search(s):
            problems.append(f"{path}: a placeholder is written PENDING:Qn")
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
    before = w.get("before")
    if not (isinstance(before, list) and before and all(_text(b) for b in before)):
        problems.append("when.before: non-empty list")
    if not _text(w.get("describe_blocks_rule")):
        problems.append("when.describe_blocks_rule: text")
    _need_cite(w, "when", problems)


def _reads(r, kind, when, problems):
    if not _closed(r, {"blocks", "attempts", "day_rule", "never_read", "custody_files", "cite"}, "reads", problems):
        return
    _need_cite(r, "reads", problems)
    if r.get("attempts") != "accepted_only":
        problems.append("reads.attempts: 'accepted_only' (a rejected attempt runtime.rejected<N> is never opened)")
    if not _text(r.get("day_rule")):
        problems.append("reads.day_rule: text")
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
        if role == "fit":
            fit_blocks.add(bid)
        for reason in block_phase_problems(kind, bid, phase, role, b.get("serves_phase")):
            problems.append(f"{where}: {reason}")
        sha = b.get("kit_sha256")
        if not (sha is None or _sha_ok(sha, False)):
            problems.append(f"{where}.kit_sha256: 64 hex, PENDING:Qn or null")
        spans = b.get("spans")
        if spans != "all_desk_final" and not (isinstance(spans, list) and spans
                                              and all(isinstance(s, str) and SPAN_ID_RE.fullmatch(s) for s in spans)):
            problems.append(f"{where}.spans: 'all_desk_final' or a non-empty list of span ids")
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
    cf = r.get("custody_files")
    if not (isinstance(cf, list) and all(_closed(x, {"basename", "scope", "carries", "stage"}, f"reads.custody_files[{j}]",
                                                problems) for j, x in enumerate(cf))):
        problems.append("reads.custody_files: list of {basename, scope, carries, stage}")
    else:
        for j, x in enumerate(cf):
            if x.get("stage") not in ("inclusion", "energy", "journal"):
                problems.append(f"reads.custody_files[{j}].stage: inclusion, energy or journal")
            if x.get("stage") == "inclusion" and x.get("carries") == "energy":
                problems.append(f"reads.custody_files[{j}]: the inclusion stage opens no energy file (RL-157 §4)")


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
                       "legs (serves_phase 'development'; RL-149 §2.4, RL-157 §4)")
    elif phase not in allowed:
        out.append(f"out of phase: phase {phase!r} is not read by a {kind} look as {role!r} "
                   f"(allowed {sorted(allowed) or 'none'})")
    return out


def _energy(e, kind, problems):
    if not _closed(e, {"channels", "not_read", "per_leg_energy_in_output", "cite"}, "energy", problems):
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
    for need in sorted(REQUIRED_CHANNELS.get(kind, set()) - set(ids)):
        problems.append(f"energy.channels: the {kind} look reads {need}")
    nr = e.get("not_read")
    if not isinstance(nr, list):
        problems.append("energy.not_read: list")
    else:
        for i, c in enumerate(nr):
            if _closed(c, {"id", "cite"}, f"energy.not_read[{i}]", problems) and c.get("id") in ids:
                problems.append(f"energy.not_read[{i}]: {c.get('id')} is also read")
    if e.get("per_leg_energy_in_output") is not False:
        problems.append("energy.per_leg_energy_in_output: false (the output holds fits, ratios and errors)")


def _fit(f, problems, final):
    keys = {"code", "heat_term", "onset", "validation", "step3", "sensitivity", "reads_from_leg_record",
            "reads_never", "cite"}
    if not _closed(f, keys, "fit", problems):
        return
    _need_cite(f, "fit", problems)
    code = f.get("code")
    if not (isinstance(code, list) and code):
        problems.append("fit.code: non-empty list of {path, sha256}")
    else:
        for i, ref in enumerate(code):
            _code_ref(ref, f"fit.code[{i}]", problems, final)
    ht = f.get("heat_term")
    if _closed(ht, {"response", "model_family", "predictors", "forbidden_predictors", "sign_of_start_term_assumed",
                    "missing_start_reading", "outside_calibrated_range", "cite"}, "fit.heat_term", problems):
        preds = ht.get("predictors")
        if not (isinstance(preds, list) and preds and all(isinstance(p, str) for p in preds)):
            problems.append("fit.heat_term.predictors: non-empty list")
            preds = []
        bad = sorted(set(preds) - ALLOWED_PREDICTORS)
        if bad:
            problems.append(f"fit.heat_term.predictors: not allowed by RL-149 §2.7 / RL-150 R1: {bad}")
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
            problems.append("fit.heat_term.sign_of_start_term_assumed: false (RL-149 §2.7)")
        for k in ("response", "model_family", "missing_start_reading", "outside_calibrated_range"):
            if not _text(ht.get(k)):
                problems.append(f"fit.heat_term.{k}: text")
        _need_cite(ht, "fit.heat_term", problems)
    on = f.get("onset")
    if _closed(on, {"definition", "predictors", "censoring", "error", "cite"}, "fit.onset", problems):
        if not (isinstance(on.get("predictors"), list) and on["predictors"]):
            problems.append("fit.onset.predictors: non-empty list")
        elif set(on["predictors"]) - ALLOWED_PREDICTORS:
            problems.append(f"fit.onset.predictors: not allowed {sorted(set(on['predictors']) - ALLOWED_PREDICTORS)}")
        for k in ("definition", "censoring", "error"):
            if not _text(on.get(k)):
                problems.append(f"fit.onset.{k}: text")
        _need_cite(on, "fit.onset", problems)
    v = f.get("validation")
    if _closed(v, {"unit", "method", "hot_stretch", "relative_error", "min_calendar_days", "cite"}, "fit.validation",
               problems):
        if v.get("unit") != "calendar_day" or v.get("method") != "leave_one_day_out":
            problems.append("fit.validation: unit 'calendar_day', method 'leave_one_day_out' (RL-149 §2.3)")
        if not (type(v.get("min_calendar_days")) is int and v["min_calendar_days"] >= 3):
            problems.append("fit.validation.min_calendar_days: at least 3 (RL-149 §2.3)")
        for k in ("hot_stretch", "relative_error"):
            if not _text(v.get(k)):
                problems.append(f"fit.validation.{k}: text")
        _need_cite(v, "fit.validation", problems)
    s3 = f.get("step3")
    if _closed(s3, {"code", "adapter", "statistic", "cite"}, "fit.step3", problems):
        _code_ref(s3.get("code"), "fit.step3.code", problems, final)
        _code_ref(s3.get("adapter"), "fit.step3.adapter", problems, final)
        if s3.get("statistic") != "iii":
            problems.append("fit.step3.statistic: 'iii' (RL-151 §1.3 item 2)")
        _need_cite(s3, "fit.step3", problems)
    if not (isinstance(f.get("sensitivity"), list)):
        problems.append("fit.sensitivity: list")
    rn = f.get("reads_never")
    if not isinstance(rn, list) or REQUIRED_READS_NEVER - set(rn):
        problems.append(f"fit.reads_never: must list {sorted(REQUIRED_READS_NEVER)} (RL-150 R6, RL-161 F12)")
    if not (isinstance(f.get("reads_from_leg_record"), list) and f["reads_from_leg_record"]):
        problems.append("fit.reads_from_leg_record: non-empty list")


def _inclusion(inc, problems, final):
    if not _closed(inc, {"rules", "inclusion_reads_no_energy", "no_drop_by_outcome", "verdicts_frozen_before_energy",
                         "cite"}, "inclusion", problems):
        return
    _need_cite(inc, "inclusion", problems)
    if inc.get("inclusion_reads_no_energy") is not True:
        problems.append("inclusion.inclusion_reads_no_energy: true (RL-157 §4)")
    if inc.get("no_drop_by_outcome") is not True:
        problems.append("inclusion.no_drop_by_outcome: true (RL-149 §2.4)")
    if not isinstance(inc.get("verdicts_frozen_before_energy"), bool):
        problems.append("inclusion.verdicts_frozen_before_energy: boolean")
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
        want = "look" if n in LOOK_JUDGED_RULES else ("runner", "look")
        if (n in LOOK_JUDGED_RULES and rule.get("judged_at") != "look") or \
                (n not in LOOK_JUDGED_RULES and rule.get("judged_at") not in want):
            problems.append(f"{where}.judged_at: {want!r} (RL-150 R9)")
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
    ids = set()
    for i, d in enumerate(ds):
        where = f"decisions[{i}]"
        if not _closed(d, {"id", "statistic", "rule", "action", "reads_energy", "cite"}, where, problems,
                       optional={"threshold"}):
            continue
        if RETIRED_DECISION_RE.search(str(d.get("id"))):
            problems.append(f"{where}.id: Rule P and the interim look's one decision are retired (RL-151 §2.1)")
        if d.get("id") in ids:
            problems.append(f"{where}.id: duplicate")
        ids.add(d.get("id"))
        th = d.get("threshold")
        if th is not None and not (isinstance(th, (int, float)) and not isinstance(th, bool)) and \
                not (isinstance(th, str) and PENDING_RE.fullmatch(th)):
            problems.append(f"{where}.threshold: a number or PENDING:Qn")
        if not isinstance(d.get("reads_energy"), bool):
            problems.append(f"{where}.reads_energy: boolean")
        for k in ("statistic", "rule", "action"):
            if not _text(d.get(k)):
                problems.append(f"{where}.{k}: text")
        _need_cite(d, where, problems)
    for need in sorted(REQUIRED_DECISIONS.get(kind, set()) - ids):
        problems.append(f"decisions: the {kind} look carries {need}")


def _freezes(f1, f2, problems):
    if _closed(f1, {"contents", "committed_before", "ledger_pointer", "cite"}, "freeze1", problems):
        if f1.get("committed_before") != "any development energy is read":
            problems.append("freeze1.committed_before: 'any development energy is read' (RL-149 §2.6 item 1)")
        if not (isinstance(f1.get("contents"), list) and f1["contents"]):
            problems.append("freeze1.contents: non-empty list")
        if not _text(f1.get("ledger_pointer")):
            problems.append("freeze1.ledger_pointer: text (the block ledger points at the manifest by hash)")
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
        problems.append("custody: runs_by 'analyst_seat', seats 1 (RL-149 §2.6)")
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

def _sha256_file(path):
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


def check_repo(doc, repo, kit_paths=()):
    """Hash the pinned code in ``repo`` and check the import and condition rules. Opens repository source
    and kit JSON only. Placeholders are skipped (``validate_manifest`` reports them)."""
    repo = Path(repo)
    problems = []
    fit_paths = []
    for where, path, sha in code_refs(doc):
        if not (isinstance(path, str) and _repo_path_ok(path)) or not isinstance(sha, str) or not SHA_RE.fullmatch(sha):
            continue
        f = repo / path
        if not f.is_file():
            problems.append(f"{where}: {path} is not in the repository")
            continue
        if _sha256_file(f) != sha:
            problems.append(f"{where}: {path} sha256 differs from the pin")
        if path.endswith(".py"):
            fit_paths.append(path)
    look_modules = {"joulewise.cadence_looks", "cadence_looks"}
    for p in fit_paths:
        look_modules |= _module_names(p)
    import_re = re.compile(r"(?m)^\s*(?:from|import)\s+([\w.]+)")
    for kp in kit_paths:
        kit = json.loads(Path(kp).read_text(encoding="utf-8"))
        frozen = set(((kit.get("frozen") or {}).get("paths") or {}))
        for p in fit_paths:
            if p in frozen:
                problems.append(f"{p} is a frozen path of kit {Path(kp).name}; fit code makes no measurement "
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
    for p in fit_paths:
        src = (repo / p).read_text(encoding="utf-8", errors="replace")
        hit = CONDITION_RE.search(src)
        if hit:
            line = src.count("\n", 0, hit.start()) + 1
            problems.append(f"{p}:{line} reads a 'condition' field; the fit code never reads it (RL-150 R6)")
    if problems:
        raise ManifestError(problems)


# ---------------------------------------------------------------------------------------------- roster

def validate_ledger(ledger):
    problems = []
    if not _closed(ledger, {"schema", "spans", "energy_reads"}, "ledger", problems):
        raise ManifestError(problems)
    if ledger.get("schema") != LEDGER_SCHEMA:
        problems.append(f"ledger.schema: {LEDGER_SCHEMA}")
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


def resolve_roster(doc, ledger):
    """The spans this look reads, resolved from the span ledger before anything is opened.

    Refuses: a span the ledger does not know; a span named under a block it does not belong to; a span
    whose phase the look may not read (out of phase); a span that is not desk-final; a span whose energy
    seal is broken or that an earlier energy read named (unsealed); a fit roster on fewer calendar days
    than the manifest's minimum. Returns [{span_id, block_id, role, t0_local_date}] in ledger order."""
    validate_ledger(ledger)
    kind = doc.get("look_kind")
    by_id = {s["span_id"]: s for s in ledger["spans"]}
    opened = {sid: r["read_id"] for r in ledger["energy_reads"] for sid in r["spans"]}
    problems, roster = [], []
    for b in (doc.get("reads") or {}).get("blocks") or []:
        bid, role = b["block_id"], b["role"]
        if b["spans"] == "all_desk_final":
            chosen = [s for s in ledger["spans"] if s["block_id"] == bid]
            if not chosen:
                problems.append(f"{bid}: no span of this block is in the ledger")
        else:
            chosen = []
            for sid in b["spans"]:
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
