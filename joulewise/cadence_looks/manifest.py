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
import math
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from datetime import date

from joulewise.cadence_looks import custody_pins, interim_release as release, schema_check

SCHEMA = "joulewise.cadence_look_manifest.v1"
INTERIM_LOOK_ID = "lm-interim-01"
LEDGER_SCHEMA = "joulewise.cadence_span_ledger.v1"
LOOK_LEDGER_SCHEMA = "joulewise.cadence_look_ledger.v1"
LOOK_LEDGER_PATH = "docs/process/cadence/looks/LOOKS.json"
FILLER_KIT_REGISTRY = "docs/process/cadence/looks/filler-kit-registry.json"
FILLER_SERIES = ("f2-inst-", "f2-stab-", "r1-partc-f0-")      # every id of a filler series, registered or not
LOOK_LEDGER_STATUSES = ("draft", "committed", "stage1_committed", "run", "frozen", "superseded", "failed", "interrupted")
_REGISTERED_QUAL_ID = re.compile(r"lm-qual-[0-9]{2}")
# What each status needs recorded, so that "committed" is checkable (Mythos cold seat 8).
# verdicts_sha256: inclusion_34.py's verdict file, committed with the roster's hash before stage 1 runs, so stage 1
# can authenticate both inputs (Mythos round-3 N8).
LOOK_ROW_HASHES = ("roster_sha256", "verdicts_sha256", "stage1_sha256", "output_sha256", "coefficients_sha256")
PUBLIC_RELEASE_STATEMENT = ("No number computed from energy is public before the data release. "
                            "The public outputs are at most sixteen words, counts that hold no energy, and hashes.")
INTERIM_PREFIX_STATISTIC = "the mean of the day means; its 90 % t interval uses the same equal-day weights"
_STAGE1_HASHES = ("roster_sha256", "verdicts_sha256", "stage1_sha256")
LOOK_ROW_REQUIRES = {"stage1_committed": _STAGE1_HASHES, "failed": _STAGE1_HASHES, "interrupted": _STAGE1_HASHES,
                     "run": (*_STAGE1_HASHES, "output_sha256", "coefficients_sha256"),
                     "frozen": (*_STAGE1_HASHES, "output_sha256", "coefficients_sha256")}

TOP_KEYS = {"schema", "look_id", "look_kind", "status", "title", "rulings", "when", "stages", "reads", "energy",
            "fit", "inclusion", "outputs", "decisions", "later_looks", "freeze1", "freeze2", "custody", "review",
            "open_questions", "inputs"}
# RL-194: the one file that pins, by sha256 and size, every file of every roster span (custody_pins)
INPUTS_PATH = "docs/process/cadence/looks/lm-interim-01.inputs.json"
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
                                   STEP3_PATH, STEP3_ADAPTER_PATH, "scripts/cadence_look_run.py",
                                   "joulewise/cadence_looks/interim_release.py", "joulewise/cadence_looks/interim_twin.py",
                                   "scripts/cadence_look_manifest.py",
                                   "joulewise/cadence_looks/schema_check.py",
                                   "joulewise/cadence_looks/time_fields.py",
                                   # RL-184 section 3.3: the one stage-1 admission validator and its grammar
                                   "joulewise/cadence_looks/admission.py", "joulewise/cadence_looks/admission_shape.py",
                                   "joulewise/cadence_looks/admission_journals.py",
                                   "joulewise/cadence_looks/admission_synthetic.py",
                                   "joulewise/cadence_looks/admission_kits.py",
                                   # RL-194: stage 1's and stage 2's first act, the content pins of the roster's files
                                   "joulewise/cadence_looks/custody_pins.py"}}   # RL-166 Q1; Sol N3; RL-173 E.1

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
                      "start_fan_rpm", "start_tv0h_excess_over_soak_reference", "predicted_onset_s",
                      "expected_hot_seconds"}                                                # RL-166b B-1
ONSET_PREDICTORS = {"start_tf08", "start_fan_rpm", "start_tv0h_excess_over_soak_reference",
                    "prefill_seconds_from_counts"}                                           # RL-166 Q4
REQUIRED_FORBIDDEN = {"in_turn_reading", "in_turn_clock", "in_turn_state", "in_turn_duration",
                      "start_tv0h_raw", "condition", "kit_start_band", "kit_g0_shape", "prompt_size_cell_effect"}
REQUIRED_READS_NEVER = {"condition", "kit_start_band", "kit_g0_shape"}  # RL-150 R6; RL-150 R2; RL-161 F12

INCLUSION_RULE_IDS = {1: "ran_to_cap", 2: "g0_released", 3: "sidecar_coverage", 4: "km003c_clean",
                      5: "not_a_contaminated_attempt", 6: "block_power_mode"}
LOOK_JUDGED_RULES = {3, 4}                        # RL-150 R9: "Rules 3 and 4 are judged at a look"

PREFIX_RATIOS = [1.10, 1.30, 1.374]                # RL-150 section 3.2
# The thresholds RL-166 fixed, by decision id. None: the decision carries no threshold.
REQUIRED_DECISIONS = {"interim": {"drift_tripwire": None, "qualified_interim_half": 0.02, "hp01_included_below_9": 9,
                                  "stage1_tripwires": None, "step3_cell_not_run": 2, "extension_rule": None,
                                  "onsets_before_116_s": 0}}                           # RL-166b P-4
# The sentences RL-166b dictates (fit.stated_limits) and the rules it fixes for freeze 2 (freeze2.deferred_rules).
REQUIRED_STATED_LIMITS = {"interim": {"qualified_yes_meaning", "qualified_pass_rate", "pooled_error", "half_t2_limit",
                                      "partial_correction", "not_zero_before_onset", "delta_se_overstates",
                                      "warm_series_outside_joint_range", "ratio_of_tokens", "hidden_holes"}}
REQUIRED_DEFERRED = {"interim": {"kappa_signs", "sd_j_covariance", "leverage_flag", "hot_prefill_flag"}}
STAGE2_HOLD_FLAGS = {"interim": {"onsets_before_116_s.to_research_lead", "meter_clock.to_research_lead",  # RL-166c §2 row 7
                                 "tripwires.any"}}                                                        # RL-166 Q8
WITHDRAWN_FORM_RE = re.compile(r"(?i)H is zero for a turn")                           # RL-166b Amends
DRIFT_FALLBACK = 0.04                              # RL-166 Q11
DRIFT_RULED = 0.08
REQUIRED_NEVER_READ_IDS = {"interim": {"qualification", "ctl01", "fillers", "v4", "type_T", "rejected_attempts", "step3_legs",
                                       "reserve_qualification", "hp01_energy"}}
# The import closure the look's entry points execute that reads or decodes custody, pinned beside the look code
# (Mythos cold seat 3; Sol 9): the DC-in decoder and the meter-parser's own imports, and rule 3's sensor policy.
REQUIRED_DEPENDENCIES = {"interim": {"joulewise/external/km003c_parse.py", "joulewise/aggregate.py",
                                     "joulewise/desk_compress.py", "configs/align/v4/r1_runtime.json",
                                     "joulewise/cadence_looks/manifest.py", FILLER_KIT_REGISTRY}}
# Dictated and ruled texts, pinned verbatim (Sol cold seat 7; Mythos cold seat 11): RL-166b section 2.1, 2.2, 3 and
# 4 (with RL-166c section 5 for the partial correction), RL-166 Q3 and Q4 as amended, RL-166c section 2 row 7. A
# change to any of them is a change of the ruled text and needs a ruling, then a new hash here.
VERBATIM_SHA256 = {
    "fit.heat_term.form":
        "94c4e5517456edae88dd530a1a9b833f90afb9ec09d34f4fb8921d2621db578c",
    "fit.onset.estimable_when":
        "e97ccfef1f293c32528916ae6c34044f81bcbbb0c5ca908dbea09adc2e87482a",
    "fit.onset.response":
        "af7f62c15a3a69b0a55fec9be635454d69f96abe25c92a823893c03578b50399",
    "fit.stated_limits.delta_se_overstates":
        "9e077ec9144e097e7f3e8fa409e9e7c8d7f1f8278941f129ec34b42688f92460",
    "fit.stated_limits.half_t2_limit":
        "e669690b387b4eb839c3bfa057108e1973ebecca27a0f6280c2287d4df82fad3",
    "fit.stated_limits.not_zero_before_onset":
        "45f021de90d6a1bfa545af10e9ceb47a6d195c36a28a427322aba6c2a6a2313d",
    "fit.stated_limits.partial_correction":
        "673db6e35e56d946dfa020280de145ad12f1fd12f891e60d3a909accf542bba6",
    "fit.stated_limits.pooled_error":
        "cb08f40ccf17b470577d649ed5ead00f3f980e8f6de996dd2999b43b5cb60019",
    "fit.stated_limits.qualified_pass_rate":
        "c4c4313581a0f576aaefbd6b45e13dd2ef7500c1cd8b9cf39ec98d8b7f27bd4f",
    "fit.stated_limits.hidden_holes":
        "0f2dca00f1f203c75d2632fd7b23ce466af9248eb800c6f3d91454e82e2ac9a2",
    "fit.stated_limits.qualified_yes_meaning":
        "6195455f392c51de7021c26ca50351e259519689ccde13d236786b05fa53e80d",
    "fit.stated_limits.ratio_of_tokens":
        "938504cefe67ae43bad5ca30fd2b91390bd9f22e01c38f5f6e30e0dbaa28dd07",
    "fit.stated_limits.warm_series_outside_joint_range":
        "5e98adbe2a14a646cf868d90d8202ce53be0a9598df907f83de73a15e5aa08a9",
    "fit.validation.hot_stretch":
        "2a3239c9fb98dcfc25a7cc9701696ec6bbb670b862da60f08653026cdd37f76c",
    "fit.validation.qualified_rule":
        "c897d3dea7075843731bdc85396ea0fd7c002d47824529965b4083fcc4f9dd42",
    "fit.validation.relative_error":
        "5e601f7eaaf79acc21c64e8ce4d37100d2135a62e2df1ea9206ad3aa97233921",
    "freeze2.deferred_rules.hot_prefill_flag":
        "fff067656f4cf113c204ad8beb99a0e5373cbb67fd0f1e9dd2a833480c2a61ec",
    "freeze2.deferred_rules.kappa_signs":
        "8ec186b3e232527cc20bded46202241cde596150252c895292e752358f77cdbd",
    "freeze2.deferred_rules.leverage_flag":
        "affc86ecb35000a844ed9170614c2c49faa869db35e6af112946a36edf960ce7",
    "freeze2.deferred_rules.sd_j_covariance":
        "b62bf853e24e664f0387768874f4cfe13cadf00c719c843630ff32fa7b70f0c2",
    "reads.never_read.ctl01":
        "36eb70f3bae26541337fcd2ab3e2da3c66f15116fc37099faaaf8f74cae7211b",
    "reads.never_read.fillers":
        "760433e9fc357849a474ac6275c445cf763acccc58e58f6e52918c24e002d39f",
    "reads.never_read.hp01_energy":
        "025244fb89f99afe19aebc1d26faebe4c30bbba349c16a6f8893a2e43e80e24d",
    "reads.never_read.qualification":
        "84bc01a5199e982997640a70c1cc8c06810644484e36a5c568de5ebecaff6be8",
    "reads.never_read.rejected_attempts":
        "daddb48eac886291b17172088a86dde756a659c55378da4e6bb773e5b1c25ec9",
    "reads.never_read.reserve_qualification":
        "6e76bddbbae6b730cbd4db23d63754237305d1a801489ab64bf38e6c77a48793",
    "reads.never_read.step3_legs":
        "022f20bcd6d9c4f1d121c595385da32564b209120840305ed1e4acf424d4e4c9",
    "reads.never_read.type_T":
        "d6f7b145f5b355a76181644c1dbd27759c65f2d6960551ad147f58c3ae57f0cd",
    "reads.never_read.v4":
        "e48f0cd818a7f07c4c03a4e9eae140cfa18257c2b39304e7d2ab2d6f5475c81f",
    "stages.stage2.holds.meter_clock.to_research_lead":
        "8a5447e6dde8f07ccccf06ed58557e747237c3080a61efedc122b114eef05250",
    "stages.stage2.holds.onsets_before_116_s.to_research_lead":
        "9f441e66ac77db3b13620cb5a03ff03e8b8dd8549ef51508f826afe9b36a5108",
    "stages.stage2.holds.tripwires.any":
        "5054db332ab4932c7c374bb424179d0cff68a555f8d9dae8107a0c216f29a27b",
}


def verbatim_texts(doc):
    """name -> text for every text VERBATIM_SHA256 pins."""
    out = {}
    f = doc.get("fit") or {}
    for x in f.get("stated_limits") or []:
        if isinstance(x, dict):
            out[f"fit.stated_limits.{x.get('id')}"] = x.get("text")
    for x in (doc.get("freeze2") or {}).get("deferred_rules") or []:
        if isinstance(x, dict):
            out[f"freeze2.deferred_rules.{x.get('id')}"] = x.get("rule")
    out["fit.heat_term.form"] = (f.get("heat_term") or {}).get("form")
    for k in ("estimable_when", "response"):
        out[f"fit.onset.{k}"] = (f.get("onset") or {}).get(k)
    for k in ("hot_stretch", "relative_error", "qualified_rule"):
        out[f"fit.validation.{k}"] = (f.get("validation") or {}).get(k)
    for x in ((doc.get("stages") or {}).get("stage2") or {}).get("holds") or []:
        if isinstance(x, dict):
            out[f"stages.stage2.holds.{x.get('flag')}"] = x.get("rule")
    for x in (doc.get("reads") or {}).get("never_read") or []:              # Mythos N10: the sentence, not only the id
        if isinstance(x, dict):
            out[f"reads.never_read.{x.get('id')}"] = x.get("what")
    return out


def _verbatim(doc, kind, problems):
    if kind != "interim":
        return
    got = verbatim_texts(doc)
    for name, sha in VERBATIM_SHA256.items():
        text = got.get(name)
        if not isinstance(text, str) or hashlib.sha256(text.encode("utf-8")).hexdigest() != sha:
            problems.append(f"{name}: differs from the ruled text (pinned verbatim)")
    for sid in ("qualified_pass_rate", "partial_correction"):
        note = next((x.get("note") for x in (doc.get("fit") or {}).get("stated_limits") or []
                     if isinstance(x, dict) and x.get("id") == sid), None)
        for path, sha in EVIDENCE.items():
            if not (isinstance(note, str) and path in note and sha in note):
                problems.append(f"fit.stated_limits.{sid}.note: cites {path} at sha256 {sha[:12]}...")


# The re-run evidence the dictated sentences cite; check_repo hashes the file.
EVIDENCE = {"docs/process/cadence/looks/evidence/2026-11-14-mythos-passrate-rerun-REPORT.md":
            "f1c6bc323d736bb13483a1783266d652f6eea2d347b93ed6e5a307ae614773aa"}
# RL-173 E (Q11): the 8 % cell's two rows at 10,000 repetitions, synthetic (0.0280 and 0.0231, both at or under .035:
# 0.08). The drift decision cites it when the threshold is the ruled 0.08.
Q11_EVIDENCE = {"path": "docs/process/cadence/looks/evidence/2026-11-15-q11-drift-10k-REPORT.md",
                "sha256": "b175a786c5f9ec422e5fab603795d48f0238dea8dac1001e3fc41b2fb292edad"}
# RL-166 Q8; ids as the stage-1 output (level D, docs/process/cadence_look_fit_interface.md section 3.3) names them
STAGE1_TRIPWIRES = {"dev_included_below_45": 45, "days_below_4": 4, "cell_below_10": 10,     # days: RL-166b B-7
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


def strict_json(raw):
    """Decode pinned writer JSON without ambiguous keys or nonfinite numbers. Bytes are UTF-8 as ``json.dump``
    writes them: ``json.loads`` alone would also guess UTF-16 or UTF-32 and skip a byte-order mark. Every refusal
    is a ManifestError, so no caller mistakes text that is not JSON for an absent file."""
    def unique(pairs):
        result = dict(pairs)
        if len(result) != len(pairs):
            raise ManifestError(["writer JSON has duplicate keys"])
        return result

    def number(token):
        value = float(token)
        if not math.isfinite(value):
            raise ManifestError(["writer JSON has a nonfinite number"])
        return value

    try:
        if isinstance(raw, (bytes, bytearray)):
            raw = bytes(raw).decode("utf-8")
        return json.loads(raw, object_pairs_hook=unique, parse_float=number, parse_constant=number)
    except ManifestError:
        raise
    except (ValueError, RecursionError):
        raise ManifestError(["writer JSON is not JSON as the pinned writers serialize it"]) from None


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


def code_refs(doc, *, look_code_only=False):
    """Every pinned file reference in the manifest: (where, path, sha256). ``look_code_only`` leaves out
    fit.dependencies (shared repository code the look executes: hashed, but not look code)."""
    out = []
    fit = doc.get("fit") or {}
    if not look_code_only:
        for i, ref in enumerate(fit.get("dependencies") or []):
            if isinstance(ref, dict):
                out.append((f"fit.dependencies[{i}]", ref.get("path"), ref.get("sha256")))
        for i, block in enumerate((doc.get("reads") or {}).get("blocks") or []):
            if isinstance(block, dict) and block.get("kit_sha256") is not None and isinstance(block.get("block_id"), str):
                out.append((f"reads.blocks[{i}].kit_sha256",
                            f"docs/process/cadence/kits/cl-{block['block_id']}.json", block["kit_sha256"]))
    for i, ref in enumerate(fit.get("code") or []):
        if isinstance(ref, dict):
            out.append((f"fit.code[{i}]", ref.get("path"), ref.get("sha256")))
    twin = fit.get("twin")
    if isinstance(twin, dict):
        out.append(("fit.twin", twin.get("path"), twin.get("sha256")))
    s3 = fit.get("step3") or {}
    for key in ("code", "adapter"):
        if isinstance(s3.get(key), dict):
            out.append((f"fit.step3.{key}", s3[key].get("path"), s3[key].get("sha256")))
    for i, rule in enumerate((doc.get("inclusion") or {}).get("rules") or []):
        if isinstance(rule, dict) and isinstance(rule.get("code"), dict):
            out.append((f"inclusion.rules[{i}].code", rule["code"].get("path"), rule["code"].get("sha256")))
    for where, node in (("outputs.schema", (doc.get("outputs") or {}).get("schema")),
                        ("stages.stage1.schema", ((doc.get("stages") or {}).get("stage1") or {}).get("schema")),
                        ("freeze2.schema", (doc.get("freeze2") or {}).get("schema")),
                        ("inputs.pins", (doc.get("inputs") or {}).get("pins"))):
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
    _closed(doc, TOP_KEYS, "manifest", problems, optional={"supersedes"})
    route = (("schema", SCHEMA), ("look_kind", "interim"), ("look_id", INTERIM_LOOK_ID))
    if any(doc.get(key) != expected for key, expected in route):
        problems.extend(f"{key}: the v1 validator admits only {expected}" for key, expected in route
                        if doc.get(key) != expected)
        raise ManifestError(problems)
    if "supersedes" in doc and (not isinstance(doc["supersedes"], str)
                               or not LOOK_ID_RE.fullmatch(doc["supersedes"])
                               or doc["supersedes"] == doc.get("look_id")):
        problems.append("supersedes: a different look id")
    if final is None:
        final = doc.get("status") == "committed"
    kind = doc.get("look_kind")
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
        for need in ("RL-149 §2.6", "RL-150 R4", "RL-166 §1", "RL-166b §3", "RL-172a"):
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
    _decisions(doc.get("decisions"), kind, problems, final)
    _later_looks(doc.get("later_looks"), problems)
    _freezes(doc.get("freeze1"), doc.get("freeze2"), problems, kind, final)
    _custody(doc.get("custody"), problems)
    _inputs(doc.get("inputs"), problems)
    _review(doc.get("review"), problems)
    _verbatim(doc, kind, problems)
    if kind == "interim":
        schema_root = Path(LOOK_LEDGER_PATH).parent
        for node, filename in (((doc.get("outputs") or {}).get("schema"), "output"),
                               (((doc.get("stages") or {}).get("stage1") or {}).get("schema"), "stage1"),
                               ((doc.get("freeze2") or {}).get("schema"), "coefficients")):
            if isinstance(node, dict) and node.get("path") != str(schema_root / f"lm-interim-01.{filename}.schema.json"):
                problems.append(f"the interim {filename} schema pin must name its registered path")
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


def filler_reference(block_id=None, kit_sha256=None):
    """Whether a block id or a kit digest names a filler kit (RL-181 section 2.1): an id or a digest of the reviewed
    registry, or an id in one of the filler series. The one predicate for every place the v1 manifest names a block.
    The comparison folds case, as main's dispatcher does, so no spelling of a filler passes as another block."""
    registry_path = Path(__file__).resolve().parents[2] / FILLER_KIT_REGISTRY
    try:
        registry = strict_json(registry_path.read_bytes())
        registered = registry["kit_sha256_by_id"]
        filler_ids = {item.casefold() for item in (*registered, *registry["other_ids"])}
        filler_digests = {digest.casefold() for digest in registered.values()}
    except (AttributeError, KeyError, OSError, TypeError, ValueError):
        raise ManifestError(["reads.blocks: the filler-kit registry is unavailable or invalid"]) from None
    return ((isinstance(block_id, str) and (block_id.casefold() in filler_ids
                                            or block_id.casefold().startswith(FILLER_SERIES)))
            or (isinstance(kit_sha256, str) and kit_sha256.casefold() in filler_digests))


def _when(w, kind, problems):
    if not _closed(w, {"after_desk_final", "describe_blocks_rule", "before", "cite"}, "when", problems):
        return
    blocks = w.get("after_desk_final")
    if not (isinstance(blocks, list) and blocks and all(isinstance(b, str) and BLOCK_ID_RE.fullmatch(b) for b in blocks)):
        problems.append("when.after_desk_final: non-empty list of block ids")
    if isinstance(blocks, list) and any(filler_reference(b) for b in blocks):
        problems.append("when.after_desk_final: a counted block cannot reference a filler kit (RL-181 §2.1)")
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
    if _closed(s2, {"opens", "roster_source", "time_budget_s", "holds", "hold_record", "cite"},
               "stages.stage2", problems, optional={"failure_exit_status"}):
        if kind == "interim" and (type(s2.get("failure_exit_status")) is not int
                                  or s2["failure_exit_status"] != release.FAILURE_STATUS):
            problems.append("stages.stage2.failure_exit_status: the fixed RL-180 exit status")
        flags = set()
        for i, h in enumerate(s2.get("holds") if isinstance(s2.get("holds"), list) else []):
            if _closed(h, {"flag", "rule", "cite"}, f"stages.stage2.holds[{i}]", problems):
                flags.add(h.get("flag"))
                if not _text(h.get("rule")):
                    problems.append(f"stages.stage2.holds[{i}].rule: text")
                _need_cite(h, f"stages.stage2.holds[{i}]", problems)
        for fl in sorted(STAGE2_HOLD_FLAGS.get(kind, set()) - flags):
            problems.append(f"stages.stage2.holds: the lead holds stage 2 on {fl} (RL-166c §2 row 7)")
        if not _text(s2.get("hold_record")):
            problems.append("stages.stage2.hold_record: text")
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
        if filler_reference(bid, sha):
            problems.append(f"{where}: a counted block cannot reference a filler kit (RL-181 §2.1)")
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
        got = set()
        for i, item in enumerate(nr):
            if _closed(item, {"id", "what", "cite"}, f"reads.never_read[{i}]", problems):
                got.add(item.get("id"))
                if not _text(item.get("what")):
                    problems.append(f"reads.never_read[{i}].what: text")
                _need_cite(item, f"reads.never_read[{i}]", problems)
        for nid in sorted(REQUIRED_NEVER_READ_IDS.get(kind, set()) - got):
            problems.append(f"reads.never_read: carries {nid}" + (" (RL-166 Q14: the type-T legs)" if nid == "type_T" else ""))
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
        problems.append("energy.per_leg_relative_residuals_in_output: boolean")
    elif kind == "interim" and e["per_leg_relative_residuals_in_output"]:
        problems.append("energy.per_leg_relative_residuals_in_output: false (RL-175 B.3)")


def _fit(f, kind, problems, final):
    keys = {"code", "dependencies", "runtime", "authors", "heat_term", "rates", "onset", "validation", "prefix_bias",
            "step3", "sensitivity", "reads_from_leg_record", "reads_never", "stated_limits", "cite"}
    if not _closed(f, keys, "fit", problems, optional={"gpu_trace_hole_refusal", "twin"}):
        return
    twin = f.get("twin")
    if final and kind == "interim" and twin is None:
        problems.append("fit.twin: RL-180 requires the independent twin path and sha256")
    if "twin" in f and twin is not None:
        _code_ref(twin, "fit.twin", problems, final)
        if isinstance(twin, dict) and (not str(twin.get("path")).endswith(".py") or
                twin.get("path") in {ref.get("path") for key in ("code", "dependencies")
                                     for ref in (f.get(key) or []) if isinstance(ref, dict)}):
            problems.append("fit.twin.path: a separate Python script")
    # Mythos round-3 N7 / round-4 N5: the GPU-rail hole refusal, off unless the research lead rules it on. The
    # stage-2 CLI reads it (cadence_look_run.gpu_gap_rule); its shape is checked here so the switch can be set.
    sw = f.get("gpu_trace_hole_refusal")
    if "gpu_trace_hole_refusal" in f and not isinstance(sw, dict):      # Mythos r5 N10: as the schema, no null
        problems.append("fit.gpu_trace_hole_refusal: an object {enabled, max_gap_s[, cite]}")
    elif kind == "interim" and not (isinstance(sw, dict) and sw.get("enabled") is True and sw.get("max_gap_s") == 2):
        # RL-173 E.1 item 3: stage 2's refusal stays on as the backstop, at 2 s
        problems.append("fit.gpu_trace_hole_refusal: enabled at max_gap_s 2 (RL-173 E.1 item 3)")
    if isinstance(sw, dict):
        if not _closed(sw, {"enabled", "max_gap_s"}, "fit.gpu_trace_hole_refusal", problems, optional={"cite"}):
            pass
        else:
            if not isinstance(sw.get("enabled"), bool):
                problems.append("fit.gpu_trace_hole_refusal.enabled: true or false")
            g = sw.get("max_gap_s")
            if isinstance(g, bool) or not isinstance(g, (int, float)) or not (0 < g <= 60):
                problems.append("fit.gpu_trace_hole_refusal.max_gap_s: seconds, above 0 and at most 60")
            if sw.get("enabled") is True:
                _need_cite(sw, "fit.gpu_trace_hole_refusal", problems)
    deps = f.get("dependencies")
    if not isinstance(deps, list):
        problems.append("fit.dependencies: list of {path, sha256}")
        deps = []
    for i, ref in enumerate(deps):
        _code_ref(ref, f"fit.dependencies[{i}]", problems, final)
    for pth in sorted(REQUIRED_DEPENDENCIES.get(kind, set()) - {r.get("path") for r in deps if isinstance(r, dict)}):
        problems.append(f"fit.dependencies: pins {pth} (Mythos cold seat 3; Sol 9)")
    _items_with_ids(f.get("stated_limits"), "fit.stated_limits", {"id", "text", "cite"}, {"note"},
                    REQUIRED_STATED_LIMITS.get(kind, set()), "RL-166b", problems)
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
        problems.append("fit.runtime: stdlib plus numpy, no scipy, run with -I, numpy version bound to stage 1 (RL-180)")
    if not (isinstance(f.get("authors"), dict) and f["authors"]):
        problems.append("fit.authors: object")
    ht = f.get("heat_term")
    if _closed(ht, {"unit", "segments", "count_clock", "start_readings", "form", "response", "base", "estimation",
                    "predictors", "forbidden_predictors", "sign_of_start_term_assumed", "missing_start_reading",
                    "out_of_state_start", "onset_not_estimable", "outside_calibrated_range", "cite"},
               "fit.heat_term", problems):
        if WITHDRAWN_FORM_RE.search(str(ht.get("form"))):
            problems.append("fit.heat_term.form: 'H is zero for a turn ...' is withdrawn (RL-166b Amends)")
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
        if kind == "interim" and pb.get("statistic") != INTERIM_PREFIX_STATISTIC:
            problems.append("fit.prefix_bias.statistic: use equal-day weights for both parts (RL-175 B.4)")
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
    if not _closed(o, {"schema", "words", "cite"}, "outputs", problems):
        return
    _need_cite(o, "outputs", problems)
    _code_ref(o.get("schema"), "outputs.schema", problems, final)
    if kind == "interim" and o.get("words") != {k: list(v) for k, v in release.PUBLIC_WORDS.items()}:
        problems.append("outputs.words: the closed RL-180 interim word lists")


def _decisions(ds, kind, problems, final=False):
    if not isinstance(ds, list):
        problems.append("decisions: list")
        return
    got = {}
    for i, d in enumerate(ds):
        where = f"decisions[{i}]"
        if not _closed(d, {"id", "statistic", "rule", "action", "reads_energy", "cite"}, where, problems,
                       optional={"threshold", "fallback_threshold", "ruled_threshold", "pending", "disposed_by",
                                 "evidence"}):
            continue
        if RETIRED_DECISION_RE.search(str(d.get("id"))):
            problems.append(f"{where}.id: Rule P and the interim look's one decision are retired (RL-151 §2.1)")
        if d.get("id") in got:
            problems.append(f"{where}.id: duplicate")
        got[d.get("id")] = d
        for k in ("threshold", "fallback_threshold", "ruled_threshold"):
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
    if kind == "interim" and drift is not None:
        if drift.get("fallback_threshold") != DRIFT_FALLBACK:
            problems.append(f"decisions drift_tripwire: fallback_threshold {DRIFT_FALLBACK} (RL-166 Q11)")
        th = drift.get("threshold")
        if final and "pending" in drift:
            problems.append("decisions drift_tripwire: a committed manifest carries no pending disposition; the "
                            "research lead disposes RL-166 Q11 first (Mythos N10)")
        disposed = drift.get("disposed_by")
        if disposed is not None and not (isinstance(disposed, str) and RULING_RE.fullmatch(disposed)):
            problems.append("decisions drift_tripwire.disposed_by: the disposing ruling, RL-n")
        if disposed is not None and "pending" in drift:
            problems.append("decisions drift_tripwire: pending and disposed_by both present")
        if th == DRIFT_FALLBACK:
            if drift.get("ruled_threshold") != DRIFT_RULED or not (_text(drift.get("pending")) or disposed):
                problems.append("decisions drift_tripwire: the fallback 0.04 carries ruled_threshold 0.08 and either "
                                "the pending disposition or the disposing ruling (RL-166 Q11)")
        elif th == DRIFT_RULED and drift.get("evidence") != Q11_EVIDENCE:
            problems.append(f"decisions drift_tripwire: 0.08 cites RL-173's 10,000-repetition run as evidence "
                            f"{Q11_EVIDENCE} (RL-166 Q11; RL-173 E)")
        elif th != DRIFT_RULED:
            problems.append(f"decisions drift_tripwire: threshold {DRIFT_RULED}, or the fallback {DRIFT_FALLBACK} "
                            "if Q11's condition fails (RL-166 Q11)")


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


def _items_with_ids(items, where, keys, optional, required_ids, ruling, problems):
    if not isinstance(items, list):
        problems.append(f"{where}: list")
        return
    seen = set()
    for i, x in enumerate(items):
        if _closed(x, keys, f"{where}[{i}]", problems, optional=optional):
            if x.get("id") in seen:
                problems.append(f"{where}[{i}].id: duplicate")
            seen.add(x.get("id"))
            for k in keys - {"id", "cite"}:
                if not _text(x.get(k)):
                    problems.append(f"{where}[{i}].{k}: text")
            _need_cite(x, f"{where}[{i}]", problems)
    for rid in sorted(required_ids - seen):
        problems.append(f"{where}: carries {rid} ({ruling})")


def _freezes(f1, f2, problems, kind=None, final=None):
    if _closed(f1, {"contents", "committed_before", "ledger_pointer", "cite"}, "freeze1", problems):
        if f1.get("committed_before") != "any development energy is read":
            problems.append("freeze1.committed_before: 'any development energy is read' (RL-149 §2.6 item 1)")
        if not (isinstance(f1.get("contents"), list) and f1["contents"]):
            problems.append("freeze1.contents: non-empty list")
        if not (_text(f1.get("ledger_pointer")) and "LOOKS.json" in f1["ledger_pointer"]):
            problems.append("freeze1.ledger_pointer: the look ledger LOOKS.json (RL-166 Q18)")
        _need_cite(f1, "freeze1", problems)
    if _closed(f2, {"artifact", "contents", "commit_before", "used_by", "refit_on_qualification", "deferred_rules",
                    "cite"}, "freeze2", problems, optional={"schema"}):
        if kind == "interim" and "schema" not in f2:
            problems.append("freeze2.schema: the coefficient file's pinned schema (RL-173 E: write_coefficients)")
        if "schema" in f2:
            _code_ref(f2.get("schema"), "freeze2.schema", problems, final)
        _items_with_ids(f2.get("deferred_rules"), "freeze2.deferred_rules", {"id", "when", "rule", "cite"}, (),
                        REQUIRED_DEFERRED.get(kind, set()), "RL-166b §4", problems)
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
            "fit_paths_outside_kit_frozen_paths", "disclosure", "pre_run_check", "pin_check", "cite"}
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
    for k in ("custody_copy", "host", "disclosure", "pre_run_check", "pin_check"):
        if not _text(c.get(k)):
            problems.append(f"custody.{k}: text")
    _need_cite(c, "custody", problems)


def _inputs(node, problems):
    """RL-194: the manifest pins one inputs file; that file pins every file of every roster span (custody_pins)."""
    if not _closed(node, {"pins", "rule", "cite"}, "inputs", problems):
        return
    pins = node.get("pins")
    if not (isinstance(pins, dict) and set(pins) == {"path", "sha256"} and pins["path"] == INPUTS_PATH
            and isinstance(pins["sha256"], str) and (SHA_RE.fullmatch(pins["sha256"]) or pins["sha256"] == PENDING_CODE)):
        problems.append(f"inputs.pins: path {INPUTS_PATH} and its sha256")
    if not _text(node.get("rule")):
        problems.append("inputs.rule: text")
    if not (_cites(node.get("cite")) and any(c.startswith("RL-194") for c in node["cite"])):
        problems.append("inputs.cite: ruling cites, RL-194 among them")


def input_pins(repo, doc, *, complete):
    """(pin list, its file's sha256) for a manifest whose pins ``verify_pins`` has checked. ``complete`` refuses the
    unfilled list a draft may carry. Raises ManifestError."""
    raw = (Path(repo) / doc["inputs"]["pins"]["path"]).read_bytes()
    try:
        return custody_pins.load_pin_list(raw, complete=complete), hashlib.sha256(raw).hexdigest()
    except custody_pins.PinRefusal as error:
        raise ManifestError([f"inputs: {error}"]) from None


PUBLIC_RUN_STATE_REF = "refs/remotes/origin/main"


def public_run_state(repo):
    """RUN_STATE.md as it stands on the public main branch: where each roster span's Check item is (RL-194
    condition 2). Read from the remote-tracking ref, never from the working tree."""
    rc, raw, _ = _git(Path(repo).resolve(), "show", f"{PUBLIC_RUN_STATE_REF}:RUN_STATE.md")
    if rc != 0:
        raise ManifestError([f"RUN_STATE.md cannot be read from {PUBLIC_RUN_STATE_REF}: the pins' Check items "
                             "are not available to chain to"])
    return raw.decode("utf-8", "replace")


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
    look_code = {path for _, path, _ in code_refs(doc, look_code_only=True)}
    code_paths = []
    for where, path, sha in code_refs(doc):
        if not (isinstance(path, str) and _repo_path_ok(path)):
            continue
        f = repo / path
        if path.endswith(".py") and path in look_code:
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
    for path, sha in EVIDENCE.items():
        f = repo / path
        if not f.is_file() or sha256_file(f) != sha:
            problems.append(f"{path}: the evidence the dictated sentences cite is missing or differs from sha256 {sha[:12]}")
    q11 = repo / Q11_EVIDENCE["path"]
    if not q11.is_file() or sha256_file(q11) != Q11_EVIDENCE["sha256"]:
        problems.append(f"{Q11_EVIDENCE['path']}: the Q11 evidence is missing or differs from its sha256")
    if problems:
        raise ManifestError(problems)
    return warnings


# ---------------------------------------------------------------------------------------------- look ledger

def _relative_directory(path):
    return (isinstance(path, str) and bool(path) and not Path(path).is_absolute()
            and all(piece not in ("", ".", "..") for piece in path.split("/")) and "\\" not in path)


def require_successor_ruling(doc, ledger):
    if "supersedes" in doc:
        failed = _look_row(ledger, doc["supersedes"])
        if failed.get("status") not in ("failed", "interrupted") or not failed.get("ruling"):
            raise ManifestError(["supersedes: the prior look needs a failed or interrupted row and a research-lead ruling id"])


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
        if not _closed(row, {"look_id", "manifest_path", "sha256", "status"}, where, problems,
                       optional=LOOK_ROW_HASHES + ("stage1_superseded", "execution_host", "public_root",
                                                  "custody_root", "holds_cleared", "error_type", "ruling")):
            continue
        problems += superseded_problems(row.get("stage1_superseded"), where)
        for k in LOOK_ROW_HASHES:
            if k in row and not (row[k] is None or (isinstance(row[k], str) and SHA_RE.fullmatch(row[k]))):
                problems.append(f"{where}.{k}: 64 hex or null")
        st = row.get("status")
        if st in LOOK_LEDGER_STATUSES:
            for k in LOOK_ROW_REQUIRES.get(st, ()):
                if not (isinstance(row.get(k), str) and SHA_RE.fullmatch(row[k])):
                    problems.append(f"{where}: status {st} needs {k} (Mythos cold seat 8)")
        lid = row.get("look_id")
        registered = (st == "registered" and isinstance(lid, str) and _REGISTERED_QUAL_ID.fullmatch(lid)
                      and row.keys() == {"look_id", "manifest_path", "sha256", "status"})
        if "execution_host" in row and not _text(row["execution_host"]):
            problems.append(f"{where}.execution_host: a host id")
        if "public_root" in row and not _relative_directory(row["public_root"]):
            problems.append(f"{where}.public_root: a canonical repository-relative directory")
        if "custody_root" in row and not (
                _text(row["custody_root"]) and Path(row["custody_root"]).is_absolute()):
            problems.append(f"{where}.custody_root: an absolute directory")
        if "holds_cleared" in row:
            cleared = row["holds_cleared"]
            if not isinstance(cleared, dict) or any(
                    flag not in STAGE2_HOLD_FLAGS["interim"] or not isinstance(ruling, str)
                    or not RULING_ID_RE.fullmatch(ruling) for flag, ruling in cleared.items()):
                problems.append(f"{where}.holds_cleared: stage-1 flags and their ruling ids")
        if st == "failed":
            if not isinstance(row.get("error_type"), str) or row["error_type"] not in release.ERROR_TYPES:
                problems.append(f"{where}.error_type: the fixed RL-180 exception vocabulary")
        elif st == "interrupted":
            if row.get("error_type") != "none_recorded":
                problems.append(f"{where}.error_type: an interrupted look records none_recorded (RL-183)")
        elif "error_type" in row:
            problems.append(f"{where}.error_type: only on a failed or interrupted row")
        if st in ("failed", "interrupted") and (row.get("output_sha256") or row.get("coefficients_sha256")):
            problems.append(f"{where}: {st} look has no output or coefficient commitment")
        if "ruling" in row and (not isinstance(row["ruling"], str) or not RULING_ID_RE.fullmatch(row["ruling"])):
            problems.append(f"{where}.ruling: a ruling id")
        if not (isinstance(lid, str) and LOOK_ID_RE.fullmatch(lid)) or lid in seen:
            problems.append(f"{where}.look_id: unique lm-<id>")
        seen.add(lid)
        if st not in LOOK_LEDGER_STATUSES and not registered:
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
        payload = f.read_bytes()
        man = strict_json(payload)
        if man.get("look_id") != lid:
            problems.append(f"{where}: the manifest's look_id is {man.get('look_id')!r}")
        if row.get("status") == "draft" and man.get("status") != "draft":
            problems.append(f"{where}: ledger says draft, the manifest says {man.get('status')!r}")
        if registered:
            from joulewise.cadence_looks import qualification_manifest

            try:
                qualification_manifest.validate_registration(payload)
            except qualification_manifest.ManifestError as error:
                problems.append(f"{where}: {error}")
            if man.get("status") != "registered":
                problems.append(f"{where}: ledger says registered, the qualification manifest does not")
        elif st != "draft" and man.get("status") != "committed":
            problems.append(f"{where}: ledger says {row.get('status')}, the manifest is not committed")
    if problems:
        raise ManifestError(problems)
    return doc


RULED_EXCLUSION_RULES = ("sidecar_coverage", "km003c_clean")
RULING_ID_RE = re.compile(r"RL-\d+[a-z]?")


def superseded_problems(entries, where):
    """RL-173 E.1 item 4 (and Mythos round-5 N3): a stage-1 commitment is replaced only by a named ruling. The row's
    optional ``stage1_superseded`` lists each replaced commitment: its three hashes, the ruling that allows the
    replacement, and the legs that ruling excluded by name (empty for a corrected hash, where stage 1 is not run
    again)."""
    if entries is None:
        return []
    out = []
    if not isinstance(entries, list) or not entries:
        return [f"{where}.stage1_superseded: a non-empty list"]
    for i, e in enumerate(entries):
        w = f"{where}.stage1_superseded[{i}]"
        if not isinstance(e, dict) or set(e) != {"stage1_sha256", "roster_sha256", "verdicts_sha256", "ruling",
                                                 "ruled_exclusions"}:
            out.append(f"{w}: stage1_sha256, roster_sha256, verdicts_sha256, ruling, ruled_exclusions")
            continue
        for k in ("stage1_sha256", "roster_sha256", "verdicts_sha256"):
            if not (isinstance(e[k], str) and SHA_RE.fullmatch(e[k])):
                out.append(f"{w}.{k}: 64 hex")
        if not (isinstance(e["ruling"], str) and RULING_ID_RE.fullmatch(e["ruling"])):
            out.append(f"{w}.ruling: the research lead's RL-n")
        rx = e["ruled_exclusions"]
        if not isinstance(rx, list) or any(not isinstance(x, dict) or set(x) != {"leg_key", "rule"}
                                           or not isinstance(x["leg_key"], str)
                                           or x["rule"] not in RULED_EXCLUSION_RULES for x in rx):
            out.append(f"{w}.ruled_exclusions: [{{leg_key, rule}}], rule one of {RULED_EXCLUSION_RULES}")
    return out


def _triple(e):
    return (e.get("stage1_sha256"), e.get("roster_sha256"), e.get("verdicts_sha256"))


def _look_row(looks_doc, look_id):
    row = next((r for r in (looks_doc or {}).get("looks") or [] if r.get("look_id") == look_id), None)
    if row is None:
        raise ManifestError([f"LOOKS.json has no row for {look_id}"])
    return row


COMMITTED_STATUSES = ("committed", "stage1_committed", "run", "frozen")
STAGE1_COMMITTED_STATUSES = ("stage1_committed", "run", "frozen")


def _git(repo, *args):
    """git in ``repo`` and nowhere else: every GIT_* variable of the caller's environment (GIT_DIR, GIT_WORK_TREE,
    GIT_INDEX_FILE, GIT_OBJECT_DIRECTORY, GIT_CEILING_DIRECTORIES, ...) is dropped, so none can point the gate at
    another repository (Mythos round-3 N5)."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env["GIT_NO_REPLACE_OBJECTS"] = "1"
    env["GIT_OPTIONAL_LOCKS"] = "0"
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, timeout=60, env=env)
    return r.returncode, r.stdout, r.stderr.decode("utf-8", "replace").strip()


def shared_ref(repo, ledger_ref=None):
    """The shared ref the committed ledger must be on, as (full ref name, commit) (Sol round-3 NEW-2; Mythos N3).
    One resolver for every tool. Only a remote-tracking branch is accepted (refs/remotes/<remote>/<branch>): never
    HEAD, a local branch, a tag, a commit id or a revision expression, each of which can name the commit under test
    itself and so waive the check. Default: the branch's upstream, else origin/main. From a detached HEAD on a
    campaign branch that is not yet on main, name that branch's remote-tracking ref (e.g. ``--ledger-ref
    origin/<campaign-branch>``, the PR's base branch)."""
    if ledger_ref is None:
        rc, up, _ = _git(repo, "rev-parse", "--verify", "--quiet", "--symbolic-full-name", "@{upstream}")
        full = up.decode().strip() if rc == 0 else ""
        full = full or "refs/remotes/origin/main"
        shown = full
    else:
        shown = str(ledger_ref)
        rc, out, _ = _git(repo, "rev-parse", "--verify", "--quiet", "--symbolic-full-name", "--end-of-options",
                          shown)
        full = out.decode().strip() if rc == 0 else ""
        # a symbolic ref (origin/HEAD) or a bare remote name resolves to some branch; name the branch itself
        rc, remotes, _ = _git(repo, "remote")
        names = [shown, f"refs/remotes/{shown}"]
        if shown in remotes.decode().split() or shown.split("/")[-1] == "HEAD" or any(
                _git(repo, "symbolic-ref", "-q", n)[0] == 0 for n in names if n.startswith("refs/")):
            full = ""
    if not full.startswith("refs/remotes/") or full.endswith("/HEAD"):
        raise ManifestError([f"ledger ref {shown!r}: the shared ref is a remote-tracking branch "
                             "(refs/remotes/<remote>/<branch>), never HEAD, a local branch, a tag, a commit or a "
                             "revision expression"])
    rc, remotes, _ = _git(repo, "remote")
    if not any(full.startswith(f"refs/remotes/{r}/") for r in remotes.decode().split()):
        # Mythos round-4 N6: a ref under refs/remotes/ that no configured remote serves is a local name
        raise ManifestError([f"ledger ref {shown!r} ({full}) belongs to no configured remote"])
    rc, sha, _ = _git(repo, "rev-parse", "--verify", "--quiet", f"{full}^{{commit}}")
    if rc != 0:
        raise ManifestError([f"ledger ref {shown!r} ({full}) does not resolve to a commit"])
    return full, sha.decode().strip()


def ledger_gate(repo, ledger_ref=None):
    """What satisfied the committed-ledger gate, for a stage's output: {commit, ref, ref_commit}."""
    head, ref, _ = committed_ledger(repo, ledger_ref=ledger_ref)
    return {"commit": head, "ref": ref, "ref_commit": shared_ref(repo, ledger_ref)[1]}


def committed_ledger(repo, *, ledger_ref=None):
    """LOOKS.json as committed, never a file a caller names (Sol cold seat N1; Mythos N1). Refuses unless:
    ``repo`` is the top of a git worktree; LOOKS.json is committed at HEAD and the working-tree file is
    identical to it and clean; HEAD is an ancestor of ``ledger_ref`` (default: the branch's upstream, else
    origin/main), so the commitment is on the shared history; and the committed ledger validates (one row per
    look, each status carrying the hashes it requires). Returns (head sha, ref, ledger)."""
    repo = Path(repo).resolve()
    rc, top, err = _git(repo, "rev-parse", "--show-toplevel")
    if rc != 0 or Path(top.decode().strip()).resolve() != repo:
        raise ManifestError([f"{repo} is not the top of a git worktree: the ledger must be committed ({err[:120]})"])
    rc, shallow, _ = _git(repo, "rev-parse", "--is-shallow-repository")
    if rc != 0 or shallow.strip() != b"false":
        raise ManifestError(["the committed-ledger gate requires complete, non-shallow Git history"])
    rc, head, _ = _git(repo, "rev-parse", "HEAD")
    head = head.decode().strip()
    rc, raw, _ = _git(repo, "show", f"{head}:{LOOK_LEDGER_PATH}")
    if rc != 0:
        raise ManifestError([f"{LOOK_LEDGER_PATH} is not committed at HEAD {head[:12]}"])
    working = repo / LOOK_LEDGER_PATH
    if not working.is_file() or working.read_bytes() != raw:
        raise ManifestError([f"the working-tree {LOOK_LEDGER_PATH} differs from the one committed at HEAD {head[:12]}"])
    rc, status, _ = _git(repo, "status", "--porcelain", "--", LOOK_LEDGER_PATH)
    if rc != 0 or status.strip():
        raise ManifestError([f"{LOOK_LEDGER_PATH} is not clean"])
    ref, _ = shared_ref(repo, ledger_ref)
    rc, _, err = _git(repo, "merge-base", "--is-ancestor", head, ref)
    if rc != 0:
        raise ManifestError([f"HEAD {head[:12]} is not on {ref}: the ledger's commitment is not on the shared history"
                             + (f" ({err[:120]})" if err else "")])
    try:
        ledger = json.loads(raw)
    except ValueError:
        raise ManifestError([f"the committed {LOOK_LEDGER_PATH} is not JSON"]) from None
    validate_look_ledger(ledger)
    return head, ref, ledger


_FREEZE2_DECISIONS_PATH = "docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md"
_FREEZE2_AUDIT_REF = "origin/audit/2026-11-10-fable"


def _freeze2_naming(repo, row, raw):
    record = strict_json(raw)
    common = {"schema": "joulewise.cadence_looks.freeze2_naming.v1", "look_id": row["look_id"],
              "ruling": row.get("ruling"), "coefficients_sha256": row["coefficients_sha256"],
              "public_sha256": row["output_sha256"], "designation": "freeze-2",
              "decisions_path": _FREEZE2_DECISIONS_PATH}
    if (type(record) is not dict or record.keys() != common.keys() | {"decisions_commit", "stanza"}
            or any(record[key] != value for key, value in common.items())
            or not common["ruling"] or release.dump(record) != raw):
        raise ManifestError(["freeze 2: naming record differs from the public commitments"])
    stanza = (f'FREEZE-2-NAMING ruling={common["ruling"]} look={common["look_id"]} '
              f'coefficients_sha256={common["coefficients_sha256"]} public_sha256={common["public_sha256"]} '
              'designation=freeze-2')
    commit = record["decisions_commit"]
    if record["stanza"] != stanza or not isinstance(commit, str) or not re.fullmatch(r"[a-f0-9]{40}", commit):
        raise ManifestError(["freeze 2: naming stanza or audit commit is invalid"])
    _, audit = shared_ref(repo, _FREEZE2_AUDIT_REF)
    if _git(repo, "merge-base", "--is-ancestor", commit, audit)[0]:
        raise ManifestError(["freeze 2: naming commit is outside the research lead's audit branch"])
    rc, log, _ = _git(repo, "show", f"{commit}:{_FREEZE2_DECISIONS_PATH}")
    if rc:
        raise ManifestError(["freeze 2: research lead's decisions log is absent"])
    lines = log.split(b"\n")
    stanza_bytes = stanza.encode("utf-8")
    if lines.count(stanza_bytes) != 1:
        raise ManifestError(["freeze 2: naming stanza must occur once as a whole line"])
    heading = next((line for line in reversed(lines[:lines.index(stanza_bytes)]) if line.startswith(b"# RL-")), b"")
    ruling = re.match(rb"# (RL-[0-9]+[a-z]?)(?:[. \t]|$)", heading)
    if ruling is None or ruling[1].decode("ascii") != common["ruling"]:
        raise ManifestError(["freeze 2: the stanza is outside its named ruling"])
    return common["ruling"]


def freeze2_authority(repo, *, expected_coefficients_sha256=None):
    """Authenticate the public freeze against one main commit and return its public evidence."""
    _, main = shared_ref(repo, "origin/main")

    def main_bytes(path):
        rc, raw, _ = _git(repo, "show", f"{main}:{path}")
        if rc:
            raise ManifestError(["freeze 2: a required public artifact is missing on origin/main"])
        return raw

    ledger = validate_look_ledger(json.loads(main_bytes(LOOK_LEDGER_PATH)))
    row = _look_row(ledger, "lm-interim-01")
    if row["status"] not in ("run", "frozen") or not _relative_directory(row.get("public_root")):
        raise ManifestError(["freeze 2: the public report is not committed on origin/main"])
    directory = "docs/process/cadence/looks"
    if row["manifest_path"] != f"{directory}/{row['look_id']}.json":
        raise ManifestError(["freeze 2: unexpected public manifest path"])
    manifest_raw = main_bytes(row["manifest_path"])
    if hashlib.sha256(manifest_raw).hexdigest() != row["sha256"]:
        raise ManifestError(["freeze 2: the mainline manifest differs from its ledger pin"])
    doc = json.loads(manifest_raw)
    if doc.get("status") != "committed" or doc.get("look_id") != row["look_id"]:
        raise ManifestError(["freeze 2: the mainline manifest must be committed for this look"])
    pin = doc["outputs"]["schema"]
    if pin["path"] != f"{directory}/{row['look_id']}.output.schema.json":
        raise ManifestError(["freeze 2: unexpected public schema path"])
    schema_raw = main_bytes(pin["path"])
    if hashlib.sha256(schema_raw).hexdigest() != pin["sha256"]:
        raise ManifestError(["freeze 2: the mainline public schema differs from its pin"])
    path = f'{row["public_root"]}/{row["look_id"]}/PUBLIC.json'
    raw = main_bytes(path)
    if hashlib.sha256(raw).hexdigest() != row["output_sha256"]:
        raise ManifestError(["freeze 2: the mainline public report differs from its ledger pin"])
    public = release.read_public(raw, json.loads(schema_raw), look_id=row["look_id"])
    for key, expected in (("manifest_sha256", row["sha256"]), ("stage1_sha256", row["stage1_sha256"]),
                          ("coefficients_sha256", row["coefficients_sha256"])):
        if public[key] != expected:
            raise ManifestError(["freeze 2: the public report differs from its ledger commitments"])
    if expected_coefficients_sha256 is not None and public["coefficients_sha256"] != expected_coefficients_sha256:
        raise ManifestError(["freeze 2: the issued coefficient commitment differs from the published one"])
    execution_commit = public["commit"]
    if _git(repo, "merge-base", "--is-ancestor", execution_commit, main)[0]:
        raise ManifestError(["freeze 2: the execution commit is not in main's history"])
    rc, ledger_raw, _ = _git(repo, "show", f"{execution_commit}:{LOOK_LEDGER_PATH}")
    if rc:
        raise ManifestError(["freeze 2: the execution commit does not carry the look ledger"])
    executed = _look_row(validate_look_ledger(json.loads(ledger_raw)), row["look_id"])
    bindings = ("sha256", "stage1_sha256", "public_root", "custody_root", "execution_host")
    if executed["status"] != "stage1_committed" or any(executed.get(key) != row.get(key) for key in bindings):
        raise ManifestError(["freeze 2: the execution commit does not authenticate the published look"])
    source = "yes"
    if public["twin_agrees"] != "yes":
        if not row.get("ruling"):
            raise ManifestError(["freeze 2: the mainline report does not record twin agreement or a naming ruling"])
        source = _freeze2_naming(repo, row, main_bytes(f"{directory}/{row['look_id']}.freeze2.json"))
    evidence = {"look_id": row["look_id"], "main_commit": main, "public_sha256": row["output_sha256"],
                "coefficients_sha256": row["coefficients_sha256"], "decision_source": source}
    return row, evidence


def freeze2_commitment(repo):
    """Read the public mainline decision before any scoring code opens coefficients."""
    return freeze2_authority(repo)[0]


def execution_host():
    """Return the RL-184 host token without publishing the hardware UUID."""
    try:
        probe = subprocess.run(["/usr/sbin/ioreg", "-rd1", "-c", "IOPlatformExpertDevice"],
                               capture_output=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        raise ManifestError(["host-id: could not read IOPlatformUUID"]) from None
    properties = re.findall(rb'(?m)^[ \t|]*"IOPlatformUUID"[ \t]*=[ \t]*([^\r\n]*)', probe.stdout)
    uuid_pattern = rb'"([0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12})"[ \t]*'
    uuid = re.fullmatch(uuid_pattern, properties[0]) if len(properties) == 1 else None
    if uuid is None:
        raise ManifestError(["host-id: expected exactly one UUID-shaped IOPlatformUUID"])
    material = ("joulewise.execution_host.v1:" + uuid[1].decode("ascii").upper()).encode("utf-8")
    return "hw1:" + hashlib.sha256(material).hexdigest()


def _ledger_history_rows(repo, look_id, head):
    """Every preserved row of this look on HEAD or any remote-tracking history, newest first."""
    rc, out, err = _git(repo, "log", "--full-history", "--format=%H", head, "--remotes", "--", LOOK_LEDGER_PATH)
    if rc != 0:
        raise ManifestError([f"the history of {LOOK_LEDGER_PATH} cannot be read ({err[:120]})"])
    rows_out = []
    for commit in out.decode().split():
        rc, raw, _ = _git(repo, "show", f"{commit}:{LOOK_LEDGER_PATH}")
        try:
            rows = json.loads(raw).get("looks") if rc == 0 else None
        except ValueError:
            rows = None
        if isinstance(rows, list):
            rows_out.extend(row for row in rows if isinstance(row, dict) and row.get("look_id") == look_id)
    return rows_out


def look_spent(repo, look_id, head):
    return any(row.get("status") in release.SPENT_STATUSES or row.get("output_sha256")
               for row in _ledger_history_rows(repo, look_id, head))


def stage1_history(repo, look_id, head):
    """The distinct stage-1/roster/verdict commitments on HEAD and every remote-tracking history."""
    seen = []
    for row in _ledger_history_rows(repo, look_id, head):
        if row.get("stage1_sha256") and _triple(row) not in seen:
            seen.append(_triple(row))
    return seen


def require_stage1_committed(repo, look_id, stage1_sha256, *, stage1_doc, ledger_ref=None, for_execution=False):
    """Refuse unless the committed LOOKS.json (``committed_ledger``) names, for this look: the manifest as committed
    at HEAD, at status stage1_committed or later; this stage-1 file's sha256; and as roster_sha256 the roster hash
    the stage-1 file recorded (``code_sha256["input:roster_sha256"]``; Mythos N7). Stage 2, step3_roster.py and
    assemble call it before they open anything. Returns the ledger row."""
    head, ref, ledger = committed_ledger(repo, ledger_ref=ledger_ref)
    row = _look_row(ledger, look_id)
    problems = []
    if for_execution:
        if look_spent(repo, look_id, head):
            raise ManifestError(["this manifest id is already spent"])
        rc, raw, _ = _git(repo, "show", f"{ref}:{LOOK_LEDGER_PATH}")
        if rc or _look_row(json.loads(raw), look_id) != row:
            raise ManifestError(["the shared ledger no longer carries this stage-2 row"])
    history = stage1_history(repo, look_id, head)
    # Mythos round-4 N3: stage 1 is fixed once, before energy; RL-173 E.1 item 4: a replaced commitment is listed in
    # the row's stage1_superseded with the research lead's ruling, and nothing else replaces one
    superseded = {_triple(e): e for e in row.get("stage1_superseded") or []}
    current = _triple(row)
    for h in history:
        if h != current and h not in superseded:
            problems.append(f"LOOKS.json's history names a stage-1 commitment for {look_id} that the row neither "
                            f"holds nor lists as superseded by a ruling: stage1 {h[0]}, roster {h[1]}, verdicts {h[2]} "
                            "(RL-166 Q8; RL-173 E.1 item 4)")
    if current in superseded:
        problems.append(f"LOOKS.json {look_id}: the current stage-1 commitment is listed as superseded")
    want = sorted({(x["leg_key"], x["rule"]) for e in row.get("stage1_superseded") or []
                   for x in e.get("ruled_exclusions") or []})
    got = sorted((leg["leg_key"], leg["ruled_exclusion"]["rule"]) for leg in (stage1_doc or {}).get("legs") or []
                 if isinstance(leg, dict) and leg.get("ruled_exclusion"))
    if got != want:
        problems.append(f"the stage-1 file's ruled exclusions {got} are not the ones the row's superseded entries "
                        f"names {want}")
    if row.get("status") not in STAGE1_COMMITTED_STATUSES:
        problems.append(f"LOOKS.json {look_id} is {row.get('status')!r}: stage 1 is not committed")
    if row.get("stage1_sha256") != stage1_sha256:          # Mythos r5 N3: full hashes, so a typo shows
        problems.append(f"LOOKS.json {look_id} names stage-1 sha256 {row.get('stage1_sha256')}, not {stage1_sha256}")
    rc, man, _ = _git(repo, "show", f"{head}:{row.get('manifest_path')}")
    if rc != 0:
        problems.append(f"the manifest {row.get('manifest_path')} is not committed at HEAD")
    else:
        if hashlib.sha256(man).hexdigest() != row.get("sha256"):
            problems.append("the committed manifest's sha256 is not the one LOOKS.json names")
        if (Path(repo) / row["manifest_path"]).read_bytes() != man:
            problems.append("the working-tree manifest differs from the committed one")
    recorded = ((stage1_doc or {}).get("code_sha256") or {})
    for field, key, what in (("roster_sha256", "input:roster_sha256", "roster"),
                             ("verdicts_sha256", "input:rules_3_4_sha256", "rules-3-4 verdict file")):
        if recorded.get(key) is None or row.get(field) != recorded.get(key):
            problems.append(f"LOOKS.json {look_id} {field} {row.get(field)} is not the {what} the stage-1 "
                            f"file records ({recorded.get(key)})")
    if problems:
        raise ManifestError(problems)
    return (head, row) if for_execution else row


def require_inputs_committed(repo, look_id, manifest_sha256, *, roster_sha256, verdicts_sha256, ledger_ref=None,
                             ruled_exclusions=None):
    """Stage 1's gate on its two inputs (Mythos round-3 N8): the committed LOOKS.json row for this look names this
    manifest at status committed or later, and the roster (``validate --roster-out``) and the rules-3-4 verdict file
    (``inclusion_34.py``) stage 1 was given, by sha256. The lead commits both hashes in the row before stage 1
    runs. Returns the row."""
    head, _, ledger = committed_ledger(repo, ledger_ref=ledger_ref)
    row = _look_row(ledger, look_id)
    problems = []
    history = stage1_history(repo, look_id, head)
    given_rx = sorted((k, v[0]) for k, v in (ruled_exclusions or {}).items())
    entries = row.get("stage1_superseded") or []
    if history:
        prior_rows = _ledger_history_rows(repo, look_id, head)
        if any(r.get("status") in release.SPENT_STATUSES or r.get("output_sha256") for r in prior_rows):
            problems.append("stage 1 cannot run once more after this manifest id is spent")
        if any(r.get("stage1_sha256") and r.get("sha256") != manifest_sha256 for r in prior_rows):
            problems.append("a stage 1 run once more takes the replaced commitment's manifest unchanged")
        # Mythos round-4 N3: stage 1 runs once. RL-173 E.1 item 4: once more only when the research lead has excluded
        # a leg by name after a stage-2 refusal: every earlier commitment is listed as superseded by a ruling, the
        # last entry names exactly the exclusions this run applies (with every earlier entry's), and the roster and
        # the verdict file are the replaced commitment's: no other change.
        listed = {_triple(e) for e in entries}
        unlisted = [h for h in history if h not in listed]
        if unlisted:
            problems.append(f"LOOKS.json's history already commits a stage 1 for {look_id} ({unlisted[0][0]}) that no "
                            "ruling supersedes: stage 1 is never run again without one (RL-166 Q8; RL-173 E.1 item 4)")
        elif not entries[-1]["ruled_exclusions"]:
            problems.append("the row's last superseded entry excludes no leg: stage 1 runs again only for a ruled "
                            "exclusion (a corrected hash needs no new stage 1)")
        else:
            last = entries[-1]
            want = sorted((x["leg_key"], x["rule"]) for x in last["ruled_exclusions"])
            earlier = {(x["leg_key"], x["rule"]) for e in entries[:-1] for x in e["ruled_exclusions"]}
            if given_rx != want or not earlier <= set(want):
                problems.append(f"the ruled exclusions given {given_rx} are not the ones the row's last superseded entry "
                                f"names {want}, with every earlier one")
            if (roster_sha256, verdicts_sha256) != (last["roster_sha256"], last["verdicts_sha256"]):
                problems.append("a stage 1 run once more takes the replaced commitment's roster and verdict file")
            for x in last["ruled_exclusions"]:
                if (ruled_exclusions or {}).get(x["leg_key"], (None, None))[1] != last["ruling"]:
                    problems.append(f"the ruled exclusion of {x['leg_key']} does not name {last['ruling']}")
        if row.get("stage1_sha256") is not None:
            problems.append(f"LOOKS.json {look_id} still names a stage-1 hash: a rerun starts from a row without one")
    elif given_rx:
        problems.append("ruled exclusions apply only to a stage 1 run once more after a committed one")
    if row.get("sha256") != manifest_sha256:
        problems.append("LOOKS.json does not name this manifest's sha256")
    if row.get("status") not in COMMITTED_STATUSES:
        problems.append(f"LOOKS.json lists this look as {row.get('status')!r}, not committed")
    for field, given, what in (("roster_sha256", roster_sha256, "roster"),
                               ("verdicts_sha256", verdicts_sha256, "rules-3-4 verdict file")):
        if row.get(field) is None:
            problems.append(f"LOOKS.json {look_id} has no {field}: commit the {what}'s sha256 before stage 1")
        elif row.get(field) != given:
            problems.append(f"the {what} given ({given}) is not the one LOOKS.json {look_id} names ({row[field]})")
    if problems:
        raise ManifestError(problems)
    return row


def runtime_bundle(sdir, leg_id, record):
    """Bind the literal RL-184 F01 locator. Resolution is used only to check containment."""
    for where, value in (("leg record", record), *((f"leg record.{key}", record.get(key)) for key in ("spec", "result")
                                                   if isinstance(record, dict) and record.get(key) is not None)):
        if not isinstance(value, dict):
            raise ManifestError([f"{where}: not an object as the pinned writers serialize it"])
    name = (record.get("result") or {}).get("bundle")
    if name is None:
        return None
    if not isinstance(name, str) or "\0" in name or any(part in ("", ".", "..") for part in name.split("/")):
        raise ManifestError(["invalid runtime bundle path (RL-184 F01)"])
    if (record.get("spec") or {}).get("leg_type") == "T":
        return None
    sdir = Path(sdir)
    parent = Path("legs") / leg_id / "runtime"
    path = sdir / parent / name
    try:
        root = sdir.resolve() / parent
        resolved = path.resolve()
    except (OSError, RuntimeError):
        raise ManifestError(["runtime bundle path could not be resolved (RL-184 F01)"]) from None
    if root not in resolved.parents:
        raise ManifestError(["bundle escapes the leg runtime directory (RL-184 F01)"])
    return path


def check_runtime_bundles(sdir):
    """Check all rostered locators using only the receipt and leg records."""
    receipt = strict_json((sdir / "runner_receipt.json").read_bytes())
    if not isinstance(receipt, dict) or not isinstance(receipt.get("roster"), list):
        raise ManifestError(["invalid receipt roster (RL-184 F01)"])
    bundles = []
    for leg_id in receipt["roster"]:
        if (not isinstance(leg_id, str) or not leg_id or "\0" in leg_id
                or Path(leg_id).name != leg_id or leg_id in (".", "..")):
            raise ManifestError(["invalid receipt leg ID (RL-184 F01)"])
        record = sdir / "legs" / leg_id / "leg_record.json"
        if record.is_file():
            bundle = runtime_bundle(sdir, leg_id, strict_json(record.read_bytes()))
            if bundle is not None:
                bundles.append(bundle)
    return receipt, bundles


def operational_paths(sdir):
    """Span-relative paths of the operational sources the look reads: the receipt, the soak reference, each roster
    leg's record and summary, and each accepted bundle's journals and config. Present or not; no energy-bearing
    telemetry, trace or meter file is among them."""
    sdir = Path(sdir)
    receipt = strict_json((sdir / "runner_receipt.json").read_bytes())
    paths = {"runner_receipt.json", "soak/soak_reference.json"}
    for lid in receipt["roster"]:
        base = f"legs/{lid}"
        paths.update((f"{base}/leg_record.json", f"{base}/leg_summary.json"))
        recpath = sdir / base / "leg_record.json"
        if recpath.is_file():
            rec = strict_json(recpath.read_bytes())
            bundle = runtime_bundle(sdir, lid, rec)
            if bundle is not None:
                b = bundle.relative_to(sdir).as_posix()
                paths.update(f"{b}/{n}" for n in ("events.jsonl", "outputs/align_turns.jsonl",
                                                  "outputs/align_thermal.jsonl", "config.json",
                                                  "outputs/align_runtime_events.jsonl", "align_runtime_events.jsonl"))
    return sorted(paths)


# The span paths admission reads and the look reuses (``operational_paths``), as a pattern over a path with no span on
# disk: staging expands exactly these members before admission and every other member only after it (deny by default).
_OPERATIONAL = re.compile(
    r"runner_receipt\.json|soak/soak_reference\.json"
    r"|legs/[^/]+/leg_(?:record|summary)\.json"
    r"|legs/[^/]+/runtime/(?:[^/]+/)*(?:events\.jsonl|config\.json|align_runtime_events\.jsonl"
    r"|align_(?:turns|thermal|runtime_events)\.jsonl)")


def is_operational_path(rel):
    """Whether a span-relative POSIX path is one of the operational sources, never an energy-bearing file."""
    return _OPERATIONAL.fullmatch(rel) is not None


def nonenergy_files(sdir):
    """Operational sources reused by the look, with paths relative to a span and byte hashes.
    Optional files are included when present; adding or removing one changes the map. No energy-bearing
    telemetry, trace or meter file is opened here; those retain their dedicated time projections.
    """
    sdir = Path(sdir)
    return {rel: sha256_file(sdir / rel) for rel in operational_paths(sdir) if (sdir / rel).is_file()}


def native_pm_files(sdir):
    """Blind digests of the rich/plist timing and native-state projection reused by step 3.
    Each byte stream is scanned by pattern; no rich JSON line or plist frame is decoded.
    A partial final plist frame remains outside the row pairing, as in the existing native-state reader.
    """
    sdir = Path(sdir)
    receipt = strict_json((sdir / "runner_receipt.json").read_bytes())
    out = {}
    ts = re.compile(rb'"timestamp_s":\s*(-?[0-9][0-9.eE+-]*)')
    el = re.compile(rb'"elapsed_ns":\s*([0-9]+)')
    pel = re.compile(rb"<key>elapsed_ns</key>\s*<integer>([0-9]+)</integer>")
    tp = re.compile(rb"<key>thermal_pressure</key>\s*<string>([^<]*)</string>")
    for lid in receipt["roster"]:
        p = sdir / "legs" / lid / "leg_record.json"
        if not p.is_file():
            continue
        rec = strict_json(p.read_bytes())
        b = runtime_bundle(sdir, lid, rec)
        if b is None:
            continue
        rel = b.relative_to(sdir).as_posix()
        # Missing pairs are represented by absence and differ from any previously recorded projection.
        if not (b / "rich_telemetry.jsonl").is_file() or not (b / "raw/powermetrics.plist").is_file():
            continue
        rows = []
        with (b / "rich_telemetry.jsonl").open("rb") as f:
            for line in f:
                if not line.strip():
                    continue
                t, e = ts.search(line), el.search(line)
                # Missing fields remain part of the blind projection. The existing turn reader decides
                # whether that leg has a usable turn; an already excluded A must not become a look refusal.
                rows.append([t.group(1).decode("ascii") if t else None,
                             e.group(1).decode("ascii") if e else None])
        frames = [fr for fr in (b / "raw/powermetrics.plist").read_bytes().split(b"\0") if fr.strip()]
        states = []
        for fr in frames[:len(rows)]:
            e, state = pel.search(fr), tp.search(fr)
            states.append([e.group(1).decode("ascii") if e else None, state.group(1).hex() if state else None])
        data = json.dumps([rows, states, len(frames)], sort_keys=True, separators=(",", ":"), allow_nan=False)
        out[rel] = hashlib.sha256(data.encode()).hexdigest()
    return out


def nonenergy_problems(stage1, sdir_of, span_ids, *, include_native_pm=True):
    spans = {sp["span_id"]: sp for sp in stage1["roster"]["spans"]}
    out = []
    for sid in sorted(set(span_ids)):
        files = ((spans.get(sid) or {}).get("custody") or {}).get("files_sha256")
        if files is None:
            if stage1.get("synthetic") is not True:
                out.append(f"{sid}: the stage-1 file carries no custody record")
            continue
        try:
            got = nonenergy_files(sdir_of(sid))
        except (OSError, ValueError, TypeError, KeyError):
            out.append(f"custody: {sid}: operational source unreadable; no values decoded")
            continue
        for rel in sorted(set(files) | set(got)):
            if files.get(rel) != got.get(rel):
                out.append(f"custody: {sid}/{rel} is not the file stage 1 read")
        if not include_native_pm:
            continue
        try:
            got_pm = native_pm_files(sdir_of(sid))
        except (OSError, ValueError, TypeError, KeyError):
            out.append(f"custody: {sid}: native PM time/state projection unreadable")
            continue
        want_pm = (spans[sid].get("custody") or {}).get("native_pm_sha256")
        if want_pm != got_pm:
            out.append(f"custody: {sid}: native PM time/state projection is not the one stage 1 read")
    return out


def loaded_repo_files(repo):
    """{repository path: sha256} of every repository source file loaded in this process (sys.modules)."""
    repo = Path(repo).resolve()
    out = {}
    for mod in list(sys.modules.values()):
        f = getattr(mod, "__file__", None)
        if not f:
            continue
        try:
            rel = Path(f).resolve().relative_to(repo).as_posix()
        except ValueError:
            continue
        if rel.endswith(".py"):
            out[rel] = sha256_file(repo / rel)
    return out


# The exact repository files each stage's process loads (their import closures, measured on the e2e run); each
# stage records exactly its set, at the pins (Sol round-2 N2, round-3 NEW-3). The stage-2 set also takes every
# fit.dependencies file but the stage-1-only sensor policy.
_SHARED_CODE = ("joulewise/__init__.py", "joulewise/cadence_looks/__init__.py", "joulewise/cadence_looks/manifest.py",
                "joulewise/cadence_looks/custody_pins.py",
                "joulewise/cadence_looks/schema_check.py", "joulewise/cadence_looks/interim_release.py",
                "joulewise/axi_decode_config.py",
                "joulewise/idle_admission.py", "joulewise/schemas.py", "joulewise/validation.py")
# RL-173 E.1: stage 1 reads time fields of the energy files through time_fields.py, which runs the pinned meter
# decoder's unwrap and clock fit on the counters; its import closure joins stage 1's set
_DECODER_CODE = ("joulewise/aggregate.py", "joulewise/authentication_io.py",
                 "joulewise/bundle_read.py", "joulewise/desk_compress.py", "joulewise/desk_restore.py",
                 "joulewise/external/__init__.py",
                 "joulewise/external/km003c_parse.py", "joulewise/provenance.py", "joulewise/suite.py")
# RL-184 section 3.3: the stage-1 admission validator and its grammar run before any trace opens, in both stages
_ADMISSION_CODE = ("joulewise/cadence_looks/admission.py", "joulewise/cadence_looks/admission_shape.py",
                   "joulewise/cadence_looks/admission_journals.py", "joulewise/cadence_looks/admission_synthetic.py",
                   "joulewise/cadence_looks/admission_kits.py")
STAGE1_CODE = _SHARED_CODE + ("joulewise/cadence_looks/fit_interim.py", "joulewise/cadence_looks/inclusion_34.py",
                              "joulewise/cadence_looks/time_fields.py", "scripts/cadence_look_run.py"
                              ) + _ADMISSION_CODE + _DECODER_CODE
def coefficients_schema(repo):
    """The coefficient file's schema (freeze 2; RL-173 E) as it stands in ``repo`` (verify_pins has checked its pin)."""
    return json.loads((Path(repo) / "docs/process/cadence/looks/lm-interim-01.coefficients.schema.json")
                      .read_text(encoding="utf-8"))


def look_schemas(repo):
    """(stage-1 schema, output schema) as they stand in ``repo`` (verify_pins has checked their pins)."""
    looks = Path(repo) / "docs/process/cadence/looks"
    return (json.loads((looks / "lm-interim-01.stage1.schema.json").read_text(encoding="utf-8")),
            json.loads((looks / "lm-interim-01.output.schema.json").read_text(encoding="utf-8")))


def provenance_problems(name, rec, manifest_sha, pins, *, exact=None):
    """Sol N2: the hashes a stage recorded are the pins, exactly: each recorded repository file is pinned with
    that hash; ``exact`` (when given) is the set the stage must have recorded, no more and no less; and the
    stage names the manifest. Keys starting 'input:' record inputs, not code."""
    problems = []
    if rec.get("manifest_sha256") != manifest_sha:
        problems.append(f"{name} was made under manifest {str(rec.get('manifest_sha256'))[:12]}, not this one "
                        f"({manifest_sha[:12]})")
    code = {k: v for k, v in (rec.get("code_sha256") or {}).items() if not k.startswith("input:")}
    for path, sha in sorted(code.items()):
        if pins.get(path) != sha:
            problems.append(f"{name} ran {path} at {str(sha)[:12]}, which is not the manifest's pin")
    if exact is not None:
        for path in sorted(exact - set(code)):
            problems.append(f"{name} does not record {path}'s hash")
        for path in sorted(set(code) - exact):
            problems.append(f"{name} records {path}, which the pinned stage does not run")
    return problems


def stage1_problems(repo, doc, stage1, manifest_sha, *, allow_draft):
    """Everything about a stage-1 file that can be checked without energy (Sol round-4 NEW-3): it passes the pinned
    stage-1 schema; it was made under this manifest; it records exactly stage 1's code at the pins and its roster's
    hash; and it was made under --allow-draft only if this run is one. ``assemble``, step3_roster.py and stage 2
    call it before anything else. Returns problems."""
    s1_schema, _ = look_schemas(repo)
    problems = [f"stage 1 does not pass its schema: {e}" for e in schema_check.errors(stage1, s1_schema)[:20]]
    pins = {path: sha for _, path, sha in code_refs(doc)}
    problems += provenance_problems("stage 1", stage1, manifest_sha, pins, exact=set(STAGE1_CODE))
    if "input:roster_sha256" not in (stage1.get("code_sha256") or {}):
        problems.append("stage 1 does not record its roster's hash (input:roster_sha256)")
    if not allow_draft and stage1.get("allow_draft") is True:
        problems.append("the stage-1 file was made under --allow-draft")
    problems += gate_problems((("stage 1", stage1),))       # Sol round-5 NEW-3: before either reader opens energy
    return problems


def gate_problems(named):
    """Mythos round-4 N6: a record carries a ledger gate exactly when it was not made under --allow-draft."""
    out = []
    for name, rec in named:
        gate, draft = rec.get("ledger_gate"), rec.get("allow_draft") is True
        if draft and gate is not None:
            out.append(f"{name} was made under --allow-draft but records a ledger gate")
        if not draft and not isinstance(gate, dict):
            out.append(f"{name} was not made under --allow-draft but records no ledger gate")
    return out


def cached_bytecode(repo):
    """Loaded repository modules that may have run from cached bytecode: a .pyc loaded as the module, or a cache file
    present where Python would read one (Mythos round-4 N4). The entry points run with a fresh, empty
    pycache prefix, so the list is empty unless something planted a file there."""
    repo = Path(repo).resolve()
    out = []
    for mod in list(sys.modules.values()):
        f = getattr(mod, "__file__", None)
        if not f:
            continue
        try:
            rel = Path(f).resolve().relative_to(repo).as_posix()
        except ValueError:
            continue
        cached = getattr(mod, "__cached__", None)
        if f.endswith((".pyc", ".pyo")) or (cached and os.path.exists(cached)):
            out.append(rel)
    return sorted(out)


def unpinned_loaded_modules(doc, repo):
    """Repository files loaded in this process that the manifest does not pin, or whose bytes differ from the pin
    (Mythos N6). Each entry point calls it before it writes, and refuses on a non-empty list."""
    pins = {path: sha for _, path, sha in code_refs(doc)}
    return sorted(f"{p} ({'not pinned' if p not in pins else 'differs from the pin'})"
                  for p, sha in loaded_repo_files(repo).items() if pins.get(p) != sha)


def verify_pins(manifest_path, repo, *, allow_draft=False, running=(), ledger_ref=None):
    """The run path's pin check (Mythos cold seat 3; Sol 9). Before any custody file is opened, refuse unless:
    the manifest validates (as committed unless ``allow_draft``); the committed LOOKS.json (``committed_ledger``)
    names its sha256 at status committed or later (unless ``allow_draft``); every file in fit.code, fit.dependencies, the step 3 pins, the inclusion code
    and the two schemas exists and hashes to its pin; and every path in ``running`` (the caller's own files) is
    one of them. Opens the manifest, LOOKS.json and repository files only. Returns the manifest."""
    repo = Path(repo).resolve()
    manifest_path = Path(manifest_path)
    raw = manifest_path.read_bytes()
    doc = json.loads(raw)
    problems = []
    try:
        validate_manifest(doc, final=not allow_draft)
    except ManifestError as error:
        problems += error.problems
    if not allow_draft:
        try:
            _, _, ledger = committed_ledger(repo, ledger_ref=ledger_ref)
            row = _look_row(ledger, doc.get("look_id"))
            require_successor_ruling(doc, ledger)
            if row.get("sha256") != hashlib.sha256(raw).hexdigest():
                problems.append("LOOKS.json does not name this manifest's sha256")
            if row.get("status") in ("failed", "interrupted"):
                problems.append(f"this manifest id is already spent ({row['status']})")
            elif row.get("status") not in COMMITTED_STATUSES:                # Mythos N5
                problems.append(f"LOOKS.json lists this look as {row.get('status')!r}, not committed")
        except (OSError, ValueError, ManifestError) as error:
            problems += [f"LOOKS.json: {p}" for p in getattr(error, "problems", [type(error).__name__])]
    pinned = {}
    for where, path, sha in code_refs(doc):
        if not (isinstance(path, str) and _repo_path_ok(path)):
            continue
        pinned[path] = sha
        f = repo / path
        if where == "fit.twin" and f.resolve() != f:
            problems.append(f"{where}: {path} is not at its canonical repository path")
            continue
        if not (isinstance(sha, str) and SHA_RE.fullmatch(sha)):
            problems.append(f"{where}: {path} has no pin")
        elif not f.is_file():
            problems.append(f"{where}: {path} is not in the repository")
        elif sha256_file(f) != sha:
            problems.append(f"{where}: {path} sha256 differs from the pin")
    if isinstance(doc.get("inputs"), dict) and (repo / INPUTS_PATH).is_file() and not problems:
        try:                                    # RL-194: a committed look's pin list is filled and chains internally
            input_pins(repo, doc, complete=not allow_draft)
        except ManifestError as error:
            problems += error.problems
    for r in running:
        try:
            rel = Path(r).resolve().relative_to(repo).as_posix() if Path(r).is_absolute() else Path(r).as_posix()
        except ValueError:
            problems.append(f"{r} runs from outside the repository {repo}")
            continue
        if rel not in pinned:
            problems.append(f"{rel} runs but is not pinned in the manifest")
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
            day = s.get("t0_local_date")
            try:
                if date.fromisoformat(day).isoformat() != day:
                    raise ValueError
            except (TypeError, ValueError):
                problems.append(f"{where}.t0_local_date: a valid YYYY-MM-DD date (RL-155a §1.2)")
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
