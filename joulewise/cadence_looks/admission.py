"""Stage-1 admission: the one strict validator of what the pinned span writers serialize (RL-184 section 3.3).

``validate_roster`` runs over every rostered span before any trace, telemetry or meter file opens, in both stages.
A span is admitted only if its receipt, soak reference, leg records, leg summaries and each selected runtime bundle
are a shape one writer revision issues, taken together: closed member sets, JSON kinds, registered values, the
step sequence and its exit paths, the soak history, and agreement between the independently serialized copies.

The grammar mirrors ``scripts/cadence_legs_runner.py`` and ``joulewise/cadence/legs.py`` at the three rostered
Automatic writer revisions (A ``b4b6aeb19``, B ``2d347f721``, C ``6e9d42f1d``) and hp-01 (``dd206025a``,
which shares A's leg and journal shape). Line triples below are A/B/C in the runner
(R) or in legs.py (L). The bundle journals are in ``admission_journals``. A refusal names a file and a member,
never a value. Nothing here reads an energy-bearing file.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
import re

from joulewise.cadence_looks import admission_journals as journals, admission_kits as kits, admission_synthetic
from joulewise.cadence_looks.admission_shape import (
    BOOL, DIGEST, FLOAT, INT, NAT, NUM, POS, REVISION, STR, TEXT, Refusal, arr, const, decode, decode_lines, either,
    enum, is_int, keys, mapping, nullable, obj, refuse, rx)

RECEIPT = "runner_receipt.json"
SOAK_REFERENCE = "soak/soak_reference.json"
RECEIPT_SCHEMA = "joulewise.cadence_span_receipt.v1"                    # R 63/63/70
RECORD_SCHEMA = "joulewise.cadence_leg_record.v1"                       # R 64/64/71
SOAK_SCHEMA = "joulewise.align.r1_soak_reference.v1"
SPEC_V1 = "joulewise.cadence_leg_spec.v1"
SPEC_V11 = "joulewise.cadence_leg_spec.v1.1"                            # L -/86/86
PINS = {"b4b6aeb192da60d895a7529311b06599efff5be4": "A",
        "2d347f721552fe03bdd19f113e7bad7a7c24908e": "B",
        "6e9d42f1dd3d308bc9239143d0d634ab965e50e1": "C"}
HP01_KIT = {"campaign_id": "cl-hp-01", "frozen_commit": "dd206025abb30fd5c07515cd4b34b3e653174810",
            "sha256": "7eaf2660312ce6b3af90e8a1d9da1e05a6c409366a88a7e5e558d3bebb9d2965"}
WORK_RESERVE_S = 370                                                    # R 72/72/79
SOAK_ATTEMPTS = 2                                                       # R C:84, SOAK_RETRIES + 1
SIGNAL_CODES = (129, 130, 143)                                          # R 362-363/365-366/497-498
BUNDLE_FILES = ("config.json", "events.jsonl", "outputs/align_turns.jsonl", "outputs/align_thermal.jsonl",
                "outputs/align_runtime_events.jsonl")
ROOT_SALVAGE = "align_runtime_events.jsonl"         # the reader once searched here; no pinned writer puts it there

# The kits a receipt may name: the repository's kit files (with their seeded legs) and the filler registry's
# digests (admission_kits, generated from those files).
LEG_ID = rx(r"L[0-9]{3,4}")                                             # joulewise/cadence/kit.py:50
STAMP = obj({"epoch_s": FLOAT, "monotonic_ns": INT})                    # R 96-97/96-97/111-112
SPAN_ID = rx(r"[A-Za-z0-9][A-Za-z0-9_.:-]*")                            # R C:88
RELATIVE_PATH = rx(r"(?!/)(?:[^/\x00]+/)*[^/\x00]+")
_ERROR = re.compile(r"([A-Za-z_][A-Za-z0-9_]*): (.*)", re.DOTALL)
_ATTEMPT_STEP = re.compile(r"(L[0-9]{3,4})\.a([1-9][0-9]*)")
_WINDOW = re.compile(r"([01][0-9]|2[0-3]):([0-5][0-9])-([01][0-9]|2[0-3]):([0-5][0-9])")
_DEADLINE_REFUSALS = re.compile(
    r"work deadline reached; cleanup reserve retained"
    r"|.+ not started: its \S+ s cap cannot fit before the work deadline"
    r"|.+ exceeded its \S+ s cap"
    r"|.+: mock leg would overrun the work deadline", re.DOTALL)
_RETURNED_RC = re.compile(r"(.+): rc (-?(?:0|[1-9][0-9]*))", re.DOTALL)


def writer_pin(runner_commit):
    """Return the commit's writer pin, or None for an unknown revision."""
    if runner_commit == HP01_KIT["frozen_commit"]:
        return "A"
    return PINS.get(runner_commit)


# ================================================================================================ span sources
class SpanFiles:
    """The operational files of one span directory, opened by their literal paths."""

    def __init__(self, sdir):
        self.sdir = Path(sdir)

    def exists(self, rel):
        return (self.sdir / rel).is_file()

    def read(self, rel):
        """The file's bytes, or None when it is absent. The open is attempted: whether a file exists is decided by
        the open, never by a separate check that could disagree with it."""
        try:
            with open(self.sdir / rel, "rb") as handle:
                return handle.read()
        except (FileNotFoundError, NotADirectoryError):
            return None
        except OSError:
            refuse(f"{self.sdir.name}/{rel}", "not readable as a file")


def locator(name, where):
    """RL-184 F01: a relative POSIX path of one or more components, none empty, ``.`` or ``..``."""
    if type(name) is not str or "\0" in name or not name or any(p in ("", ".", "..") for p in name.split("/")):
        refuse(where, "invalid runtime bundle path (RL-184 F01)")


# ============================================================================================ exception strings
def error_code(error, where):
    """The rc the writers' handlers store with ``error`` (R 355-356,465/358-359,490/490-491,648): an integer
    SpanRefusal or SystemExit code, else 2."""
    match = _ERROR.fullmatch(error) if type(error) is str else None
    if match is None:
        refuse(where, "not a formatted exception")
    kind, detail = match.groups()
    if kind == "SystemExit":
        return int(detail) if re.fullmatch(r"-?(?:0|[1-9][0-9]*)", detail) else 2
    if kind == "SpanRefusal":
        returned = _RETURNED_RC.fullmatch(detail)
        if returned:
            return int(returned[2])
        if _DEADLINE_REFUSALS.fullmatch(detail):
            return 3
    return 2


# ================================================================================================ step results
def _result_leg(pin, mock):
    """The leg runtime's result as the runner keeps it (R 477-483/502-509/661-666): the keys of _RESULT_KEEP
    the result carries. A turn adds its three stamps; the built-in mock returns a smaller projection."""
    def check(value, where):
        if type(value) is not dict:
            refuse(where, "not an object")
        required = ["leg_id", "leg_status", "bundle", "member_status", "g0_outcome", "g0_released", "g0_wait_s",
                    "g0_timeout_s", "quiet_s", "prefill_chars", "prefill_tokens", "decode_cap", "decode_tokens",
                    "decode_cap_reached", "os_level_max", "pm_nominal", "incomplete_reasons", "ac_powermode"]
        if pin != "A":
            required += ["g0_shape", "g0_role", "g0_reference_source", "g0_reference_record_sha256"]
        turn = not mock and value.get("prefill_tokens") is not None
        if not mock:
            required += ["config_sha256", "quiet_spans_ns"]
        if turn:
            required += ["turn_start_ns", "turn_end_ns", "first_token_ns"]
        keys(value, where, required)
        LEG_ID(value["leg_id"], f"{where}.leg_id")
        enum("complete", "incomplete", "g0_unreleased")(value["leg_status"], f"{where}.leg_status")
        locator(value["bundle"], f"{where}.bundle")
        enum("succeeded", "failed", "unsupported")(value["member_status"], f"{where}.member_status")
        nullable(enum("released", "timeout", "deadman", "unobserved"))(value["g0_outcome"], f"{where}.g0_outcome")
        BOOL(value["g0_released"], f"{where}.g0_released")
        nullable(NUM)(value["g0_wait_s"], f"{where}.g0_wait_s")
        nullable(NUM)(value["g0_timeout_s"], f"{where}.g0_timeout_s")
        NAT(value["quiet_s"], f"{where}.quiet_s")
        NAT(value["prefill_chars"], f"{where}.prefill_chars")
        nullable(NAT)(value["prefill_tokens"], f"{where}.prefill_tokens")
        NAT(value["decode_cap"], f"{where}.decode_cap")
        nullable(NAT)(value["decode_tokens"], f"{where}.decode_tokens")
        BOOL(value["decode_cap_reached"], f"{where}.decode_cap_reached")
        nullable(INT)(value["os_level_max"], f"{where}.os_level_max")
        nullable(BOOL)(value["pm_nominal"], f"{where}.pm_nominal")
        arr(STR)(value["incomplete_reasons"], f"{where}.incomplete_reasons")
        if (value["prefill_tokens"] is None) != (value["decode_tokens"] is None) and not mock:
            refuse(where, "prefill_tokens and decode_tokens are recorded together")
        if mock:
            obj({"value": INT})(value["ac_powermode"], f"{where}.ac_powermode")
        else:
            # joulewise/align/apple/workload.py:859-881: the episode-start record, or its failed-probe form
            nullable(either(obj({"value": nullable(INT), "source": STR, "observed_at": const("episode_start")}),
                            obj({"value": const(None), "source": STR, "observed_at": const("episode_start"),
                                 "error": STR, "attempts": POS})))(value["ac_powermode"], f"{where}.ac_powermode")
            DIGEST(value["config_sha256"], f"{where}.config_sha256")
            arr(arr(INT, least=2, most=2))(value["quiet_spans_ns"], f"{where}.quiet_spans_ns")
        if turn:
            INT(value["turn_start_ns"], f"{where}.turn_start_ns")
            INT(value["turn_end_ns"], f"{where}.turn_end_ns")
            nullable(INT)(value["first_token_ns"], f"{where}.first_token_ns")
        if pin != "A":
            enum("own", "span")(value["g0_shape"], f"{where}.g0_shape")
            enum("capture", "consume")(value["g0_role"], f"{where}.g0_role")
            nullable(STR)(value["g0_reference_source"], f"{where}.g0_reference_source")
            nullable(DIGEST)(value["g0_reference_record_sha256"], f"{where}.g0_reference_record_sha256")
    return check


_SUPERVISOR_STAMP = obj({"wall_s": FLOAT, "monotonic_ns": INT, "monotonic_raw_ns": nullable(INT)})
_SUPERVISOR_EXIT = {"pid": POS, "at": _SUPERVISOR_STAMP}
_SUPERVISOR_FINAL_EXIT = obj({**_SUPERVISOR_EXIT, "returncode": const(0), "lived_s": FLOAT, "final": const(True)})
# joulewise/b5/driver.py:948-987,1026-1084, the monitor supervisor's stop summary
_SUPERVISOR = obj(
    {"schema": const("joulewise.b5_monitor_supervision.v1"), "argv": arr(STR), "starts": NAT, "restarts": NAT,
     "start_failures": NAT, "exits": arr(either(
         obj({**_SUPERVISOR_EXIT, "returncode": INT, "lived_s": FLOAT}),
         obj({**_SUPERVISOR_EXIT, "returncode": nullable(INT), "discarded": STR}),
         _SUPERVISOR_FINAL_EXIT)),
     "gaps": arr(obj({"down_from": _SUPERVISOR_STAMP, "up_at": _SUPERVISOR_STAMP})),
     "stop": lambda value, where: _supervisor_stop(value, where),
     "journal": STR, "errors": arr(STR), "crash_loop": BOOL},
    {"final_exit": nullable(_SUPERVISOR_FINAL_EXIT)})
_GROUP = obj({"group_census": arr(STR), "reaped": BOOL})


def _supervisor_stop(value, where):
    """MonitorSupervisor.stop (joulewise/b5/driver.py:1034-1072): a running monitor is signalled and its group
    censused. A process that already exited is only polled, and a cleared process has no returncode."""
    running = type(value) is dict and value.get("was_running") is True
    if running:
        obj({"requested": _SUPERVISOR_STAMP, "was_running": const(True), "proven_stopped": BOOL,
             "returncode": nullable(INT)}, {"escalated_to_kill": const(True), "group_absent": BOOL,
                                            "group_census": arr(STR)})(value, where)
        if ("group_absent" in value) != ("group_census" in value):
            refuse(where, "a group census and its verdict together")
        proven = value.get("group_absent", value["returncode"] is not None)
    else:
        obj({"requested": _SUPERVISOR_STAMP, "was_running": const(False), "proven_stopped": BOOL},
            {"returncode": INT})(value, where)
        proven = True
    if value["proven_stopped"] != proven:
        refuse(f"{where}.proven_stopped", "not what its stop proved")
_RESTORE = either(
    obj({"rc": const(0), "action": enum("no_power_read", "foreign_marker_left")}),
    # joulewise/align/apple/powermode.py:519-535 with the smoke's rc (scripts/run_align_r1_smoke.py:138-152)
    obj({"argv": arr(STR), "exit_code": nullable(INT), "stderr": STR, "observed": nullable(INT), "ok": BOOL,
         "marker": nullable(STR), "marker_removed": BOOL, "rc": enum(0, 2)}))


def _stopped(check, supervised=False):
    """The meter's stop: rc 0 on proof, 2 on failed proof. A supervised meter with a started monitor also reports the
    remaining monitor process's group proof (scripts/run_align_r1_smoke.py:226-269; scripts/run_night.py:536-595).
    The record starts as a proof and ``stop`` changes it together with the group evidence, so a failed proof always
    carries its supervisor and group."""
    def stopped(value, where):
        check(value, where)
        if value["rc"] != (0 if value["proven_stopped"] else 2):
            refuse(f"{where}.rc", "not the code its proof gives")
        if not value["proven_stopped"] and not ("group" in value and "supervisor" in value):
            refuse(where, "a failed proof without the process-group evidence that failed it")
        if supervised and ("group" in value or "supervisor" in value):
            has_process = "supervisor" in value and "returncode" in value["supervisor"]["stop"]
            if "supervisor" not in value or ("group" in value) != has_process:
                refuse(where, "a process-group proof exactly when the supervisor still has a process")
            if has_process:
                group = value["group"]
                if value["proven_stopped"] != (group["reaped"] and not group["group_census"]):
                    refuse(f"{where}.proven_stopped", "not what its process-group evidence proved")
    return stopped


# A returned host check is one the helper did not raise on (scripts/run_align_r1_smoke.py:78-95): a nonzero exit, a
# reading without AC power, or a loaded night agent raises ValueError and leaves an error, never a result.
_NIGHT_AGENT = re.compile(r"(?:^|\s)com\.joulewise\.night\S*")


def _ac_power(value, where):
    obj({"rc": const(0), "stdout": STR})(value, where)
    if "Now drawing from 'AC Power'" not in value["stdout"].splitlines():
        refuse(f"{where}.stdout", "not a reading that shows AC power")


def _night_agents(value, where):
    obj({"rc": const(0), "stdout": STR})(value, where)
    if _NIGHT_AGENT.search(value["stdout"]):
        refuse(f"{where}.stdout", "a loaded night agent in a list that returned")


def _display(value, where):
    """scripts/run_align_r1_smoke.py:288-290: the step's rc is the display command's exit status, or 2 when none was
    observed. The record's own exit_code is copied after it."""
    obj({"rc": INT, "argv": arr(STR), "epoch_s": FLOAT, "exit_code": nullable(INT), "stderr": STR})(value, where)
    if value["rc"] != (value["exit_code"] if value["exit_code"] is not None else 2):
        refuse(f"{where}.rc", "not the code its exit status gives")


# dd206025a: cadence_legs_runner.py's High Power steps and receipt, and PowerModeGuard's records.
_HP_OBSERVED = {"ac_powermode": nullable(INT), "pmset_error": nullable(STR), "host_marker": STR,
                "host_marker_present": BOOL}
_HP_HELD = {**_HP_OBSERVED, "marker_is_this_spans": BOOL}
_HP_RESTORE_NONE = {"action": const("none"), "reason": const("no mode command was issued by this span")}
_HP_RESTORE = {"action": const("restore_automatic"), "ok": BOOL, "deferred": BOOL, "attempts": enum(1, 2, 3)}
_HP_PROOF = {**_HP_OBSERVED, "proven": BOOL}
_HP_TERMINATION = either(
    obj({"argv": arr(STR, most=6), "pid": POS, "proven": const(False), "authority": const("lead ruling R8-1"),
         "error": STR}),
    obj({"argv": arr(STR, most=6), "pid": POS, "proven": const(False), "authority": const("lead ruling R8-1"),
         "descendants": mapping(STR), "survivors": nullable(mapping(STR)), "returncode": nullable(INT)},
        {key: const(True) for key in ("pipes_held_open", "census_failed", "unreaped")}))
_HP_GUARD = either(
    obj({"point": enum("before_high", "after_high"), "stdout": STR}),
    obj({"point": const("restore_automatic"), "exit_code": INT, "stdout": STR, "stderr": STR}),
    obj({"point": const("after_restore_automatic"), "exit_code": INT, "stdout": STR, "observed": nullable(INT)}),
    obj({"point": enum("restore_raised", "after_restore_automatic"), "error": STR}),
    obj({"point": const("restore_deferred"), "reason": STR}, {"unproven": arr(_HP_TERMINATION, least=1)}),
    obj({"point": const("restore_deferred"), "reason": STR, "lock_error": nullable(STR)}))
_HP_RECEIPT = obj(
    {"block_power_mode": const(2), "host_marker": STR},
    {"before_restore": obj(_HP_HELD), "restore": either(obj(_HP_RESTORE_NONE), obj(_HP_RESTORE)),
     "close_proof": obj(_HP_PROOF), "guard": arr(_HP_GUARD),
     "revoked": arr(obj({"leg_id": LEG_ID, "reason": STR}), least=1)})
_HP_CLOSE = ("power_last_look", "restore", "power_proof", "host_lock_release")
_HP_RESULTS = {
    "host_lock": obj({"rc": const(0), "lock_path": STR}),
    "high_power_marker_absent": obj({"rc": const(0), "host_marker": STR, "present": const(False)}),
    "powermode_guard": obj({"rc": const(0), "sudo_rule": const("listed"), "automatic_proved": const(True)}),
    "high_power": obj({"rc": const(0), "ac_powermode": const(2)}),
    "power_last_look": either(obj({"rc": const(0), "skipped": const("High Power was never set")}),
                              obj({"rc": const(0), **_HP_HELD})),
    "restore": either(obj({"rc": const(0), **_HP_RESTORE_NONE}), obj({"rc": enum(0, 2), **_HP_RESTORE})),
    "power_proof": obj({"rc": enum(0, 2), **_HP_PROOF}),
    "host_lock_release": obj({"rc": const(0), "released": BOOL}),
}
_HP_CHECK = obj({"rc": const(0), **_HP_HELD, "ac_powermode": const(2), "host_marker_present": const(True),
                 "marker_is_this_spans": const(True)})


def _result_check(name, role, *, pin, mock):
    """The production a returned step attaches (GRAMMAR.md, "Span receipt and step grammar")."""
    if role == "leg":
        return _result_leg(pin, mock)
    if role == "hp":
        return _HP_CHECK if name.endswith("-powermode") else _HP_RESULTS[name]
    if role in ("start", "before", "close"):
        return obj({"rc": const(0)})                                   # every feed returns {"rc": 0} (smoke 142-205)
    if role == "wait":
        return obj({"rc": const(0), "waited_s": NUM})
    if role == "soak":
        return obj({"rc": const(0), "path": STR})
    if role == "stop":
        if mock or name != "stop-meter":
            return obj({"rc": const(0), "proven_stopped": const(True)})      # the census feeds' constant (smoke 152)
        return _stopped(obj({"rc": INT, "proven_stopped": BOOL}, {"supervisor": _SUPERVISOR, "group": _GROUP}),
                        supervised=True)
    if mock and name in ("night_agents", "ac_power", "condition13", "display"):
        return obj({"rc": const(0), "mock": const(True)})                              # R C:755-757
    return {
        "deadline": obj({"rc": const(0), "remaining_s": NUM}),
        "frozen": (obj({"rc": const(0), "skipped": STR}) if mock
                   else obj({"rc": const(0), "head": REVISION, "paths": NAT})),
        "night_agents": _night_agents,
        "ac_power": _ac_power,
        "condition13": obj({"rc": const(0), "executed_commit": REVISION}),
        "read_power": (obj({"rc": const(0), "ac_powermode": INT, "mock": const(True)}) if mock
                       else obj({"rc": const(0), "ac_powermode": const(0), "automatic": const(True)})),
        "display": _display,
        "dwell": obj({"rc": const(0), "dwell_s": NUM}),
        "plan": obj({"rc": const(0), "deadline_epoch_s": NUM, "worst_case_s": INT, "expected_s": INT,
                     "legs": arr(LEG_ID, least=1)}),
        "restore": (obj({"rc": const(0), "action": STR, "mock": const(True)}) if mock else _RESTORE),
    }[name]


def _step(step, where, role, *, pin, mock):
    """One step row through ``step()`` (R 342-360/345-363/477-495). Returns its state:
    ``initial`` (appended, never entered), ``returned``, ``raised`` (an error and no result) or ``both``
    (a result attached, then an error: a fatal nonzero rc, or an interruption after the store)."""
    name = step["name"]
    if "ended" not in step and "result" not in step and "error" not in step:
        # F03: a soak row's absent rc is read as the null the writer initializes
        keys(step, where, ("name", "started"), ("rc",) if role != "soak" else ("rc",))
        if role != "soak" and "rc" not in step:
            refuse(where, "lacks rc")
        if step.get("rc") is not None:
            refuse(f"{where}.rc", "not null on a row its operation never entered")
        STAMP(step["started"], f"{where}.started")
        return "initial"
    keys(step, where, ("name", "started", "rc", "ended"), ("result", "error"))
    STAMP(step["started"], f"{where}.started")
    STAMP(step["ended"], f"{where}.ended")
    INT(step["rc"], f"{where}.rc")
    has_result, has_error = "result" in step, "error" in step
    if not has_result and not has_error:
        refuse(where, "an ended row with neither a result nor an error")
    if has_result:
        _result_check(name, role, pin=pin, mock=mock)(step["result"], f"{where}.result")
    returned = step["result"].get("rc", 0) if has_result else None
    if not has_error:
        if step["rc"] != returned:
            refuse(f"{where}.rc", "not the rc its result returned")
        if returned != 0 and name != "display":            # every step but display is fatal on a nonzero rc
            refuse(where, "a nonzero rc returned without the refusal it raises")
        return "returned"
    TEXT(step["error"], f"{where}.error")
    if step["rc"] != error_code(step["error"], f"{where}.error"):
        refuse(f"{where}.rc", "not the code its error carries")
    if not has_result:
        if re.fullmatch(re.escape(f"SpanRefusal: {name}: rc ") + r"-?[0-9]+", step["error"]):
            refuse(f"{where}.result", "absent beside the refusal its returned rc raised")
        return "raised"
    raised_for_rc = step["error"] == f"SpanRefusal: {name}: rc {returned}"
    if returned != 0 and name != "display" and not raised_for_rc:
        refuse(f"{where}.error", "not the refusal its returned rc raises")
    if raised_for_rc and returned == 0:
        refuse(f"{where}.error", "a refusal for an rc the result did not return")
    return "both"


# =============================================================================================== leg documents
_OS_LOAD = obj({"seconds": nullable(NAT), "max_busy_cores": nullable(NUM), "max_gap_s": nullable(NUM)})
_ATTEMPT = obj({"attempt": POS, "started_epoch_s": FLOAT, "ended_epoch_s": FLOAT, "wall_s": FLOAT,
                "os_batch_wait_s": NUM, "contaminated": BOOL, "redo_reason": nullable(const("cpu_load")),
                "redone": BOOL, "os_load": _OS_LOAD,
                "leg_status": nullable(enum("complete", "incomplete", "g0_unreleased")), "output_dir": STR})
_SPAN_REFERENCE = {"leg_id": LEG_ID, "attempt": POS, "redone": BOOL, "excluded": BOOL}
_BAND_QUIET_S = {"q0": 0, "q300": 300, "q600": 600}                    # L 61/61/61, BAND_RECIPES


def _attempts(rows, leg_id, where):
    """A leg's attempt rows (R 394-403/413-422/545-555): numbered from 1; a contaminated attempt with quota left
    is renamed and redone, so only the last one keeps ``runtime``."""
    arr(_ATTEMPT)(rows, where)
    for index, row in enumerate(rows):
        at = f"{where}[{index}]"
        last = index + 1 == len(rows)
        if row["attempt"] != index + 1:
            refuse(f"{at}.attempt", "not numbered in order from 1")
        if row["wall_s"] != row["ended_epoch_s"] - row["started_epoch_s"]:
            refuse(f"{at}.wall_s", "not the difference of its two stamps")
        if (row["redo_reason"] is not None) != row["contaminated"]:
            refuse(f"{at}.redo_reason", "not the reason of a contaminated attempt")
        if row["redone"] != (not last) or (row["redone"] and not row["contaminated"]):
            refuse(f"{at}.redone", "only a contaminated attempt before the last is redone")
        expected = f"legs/{leg_id}/runtime" + (f".rejected{index + 1}" if row["redone"] else "")
        if row["output_dir"] != expected:
            refuse(f"{at}.output_dir", "not the directory the runner leaves this attempt in")


def _spec(spec, where, *, pin, leg_id, position, campaign_id, budget_s, kit_leg=None):
    """The planned leg spec with its budget (L 99-162,244-279 / 113-217,330-367)."""
    shaped = pin != "A" and type(spec) is dict and spec.get("schema") == SPEC_V11
    required = {"schema": const(SPEC_V11 if shaped else SPEC_V1), "campaign_id": const(campaign_id),
                "leg_id": const(leg_id), "seed": NAT, "start_band": enum(*_BAND_QUIET_S), "prefill_tokens": INT,
                "prefill_chars": INT, "decode_tokens": INT, "quiet_s": INT, "budget_s": const(budget_s)}
    if shaped:
        required.update(g0_shape=const("span"), g0_role=const("capture" if position == 0 else "consume"))
    obj(required)(spec, where)
    if not 256 <= spec["prefill_tokens"] <= 32768:
        refuse(f"{where}.prefill_tokens", "outside the kit's range")
    if spec["prefill_chars"] != round(spec["prefill_tokens"] * 40000 / 19458):          # L 55-56,110
        refuse(f"{where}.prefill_chars", "not the pinned rounding of its tokens")
    if not 1 <= spec["decode_tokens"] <= 4096:
        refuse(f"{where}.decode_tokens", "outside the kit's range")
    if spec["quiet_s"] != _BAND_QUIET_S[spec["start_band"]]:
        refuse(f"{where}.quiet_s", "not its band's recipe")
    if spec["seed"] >= 2 ** 32:
        refuse(f"{where}.seed", "outside the seed law's range")
    if kit_leg is not None:
        _, seed, band, tokens, decode, shape = kit_leg
        if (spec["seed"], spec["start_band"], spec["prefill_tokens"], spec["decode_tokens"]) != (
                seed, band, tokens, decode) or shaped != (shape == "span"):
            refuse(where, "not the kit's seeded leg")


def _admitted(result, contaminated, block_mode):
    """legs.leg_admitted (L 325-334/415-424): rules 1, 2, 5 and 6 as the runner sees them."""
    mode = result.get("ac_powermode")
    mode = mode.get("value") if isinstance(mode, dict) else mode
    return (not contaminated and result.get("leg_status") == "complete" and result.get("g0_released") is True
            and result.get("decode_cap_reached") is True and is_int(mode) and mode == block_mode)


def _summary(summary, where, *, spec, attempts, result, budget_s, cell, reference, block_mode, revoked):
    """legs.leg_summary (L 337-369/427-462): a projection of the spec, the accepted result and the attempts."""
    rejected = [a for a in attempts if a["contaminated"]]
    last = attempts[-1]
    expected = {"leg_id": spec["leg_id"], "seed": spec["seed"], "start_band": spec["start_band"],
                "band_reached": result["g0_released"] is True, "g0_s": result["g0_wait_s"],
                "g0_outcome": result["g0_outcome"], "wall_s": last["wall_s"], "budget_s": budget_s,
                "attempts": len(attempts), "contaminated_redos": len(rejected),
                "redo_reasons": [a["redo_reason"] for a in rejected], "os_level_max": result["os_level_max"],
                "pm_nominal": result["pm_nominal"], "started_epoch_s": attempts[0]["started_epoch_s"],
                "admitted": not revoked and _admitted(result, last["contaminated"], block_mode)}
    if cell:
        expected.update(prefill_tokens=spec["prefill_tokens"], g0_shape=spec.get("g0_shape", "own"),
                        g0_role=spec.get("g0_role", "capture"), span_reference=reference)
    keys(summary, where, (*expected, "ended_epoch_s"))
    FLOAT(summary["ended_epoch_s"], f"{where}.ended_epoch_s")
    if summary["ended_epoch_s"] < last["ended_epoch_s"]:
        refuse(f"{where}.ended_epoch_s", "before its last attempt ended")
    for key, value in expected.items():
        if not same(summary[key], value):
            refuse(f"{where}.{key}", "not the value its spec, result and attempts give")


def same(left, right):
    """Structural equality that keeps JSON kinds apart (True is not 1, 1 is not 1.0)."""
    if type(left) is not type(right):
        return False
    if type(left) is dict:
        return left.keys() == right.keys() and all(same(left[k], right[k]) for k in left)
    if type(left) is list:
        return len(left) == len(right) and all(same(a, b) for a, b in zip(left, right))
    return left == right


# ==================================================================================================== receipt
def _receipt(receipt, where):
    """The span receipt and everything it alone determines. Returns the facts the leg files are checked with."""
    if type(receipt) is not dict:
        refuse(where, "not an object")
    kit = receipt.get("kit")
    obj({"campaign_id": STR, "sha256": DIGEST, "frozen_commit": REVISION})(kit, f"{where}.kit")
    hp01 = kit == HP01_KIT
    pin = writer_pin(kit["frozen_commit"])
    # The writer pin does not admit another kit that claims the hp-01 revision.
    if pin is None or (kit["frozen_commit"] == HP01_KIT["frozen_commit"] and not hp01):
        refuse(f"{where}.kit.frozen_commit", "not a rostered writer revision")
    registered = kits.KITS.get(kit["sha256"])
    if registered is None and (hp01 or kit["sha256"] not in kits.FILLERS):
        refuse(f"{where}.kit.sha256", "not a registered kit")
    if registered is not None and (kit["campaign_id"] != registered["campaign_id"]
                                   or kit["frozen_commit"] != registered["frozen_commit"]):
        refuse(f"{where}.kit", "not the registered kit's campaign and frozen revision")
    if registered is None and kit["campaign_id"] != kits.FILLERS[kit["sha256"]]:
        refuse(f"{where}.kit.campaign_id", "not the registered kit's campaign")
    required = ["schema", "runner_kind", "mock", "started", "ended", "deadline", "work_reserve_s", "kit", "roster",
                "batch_windows", "steps", "legs", "feeds", "rc", "span_result", "meter", "legs_finished",
                "legs_planned", "load_redos_used"]
    optional = ["error", "soak_reference", "meter_health_error", "desk_bundle_error"]
    if hp01:
        required.append("high_power")
        optional.append("late_signals")
    if pin == "C":
        required.append("soak_attempts")                                # R C:453, always initialized
        optional += ["span_id", "t0_authority"]
    keys(receipt, where, required, optional)
    hp = receipt["high_power"] if hp01 else {}
    if hp01:
        _HP_RECEIPT(hp, f"{where}.high_power")
        if "late_signals" in receipt:
            arr(TEXT, least=1)(receipt["late_signals"], f"{where}.late_signals")
    const(RECEIPT_SCHEMA)(receipt["schema"], f"{where}.schema")
    (const("cadence-legs-v1") if pin == "A" else enum("cadence-legs-v1", "cadence-legs-v1.1"))(
        receipt["runner_kind"], f"{where}.runner_kind")
    if registered is not None and pin != "A" and receipt["runner_kind"] != registered["runner_kind"]:
        refuse(f"{where}.runner_kind", "not the verified kit's runner kind")
    BOOL(receipt["mock"], f"{where}.mock")
    mock = receipt["mock"]
    FLOAT(receipt["deadline"], f"{where}.deadline")
    const(WORK_RESERVE_S)(receipt["work_reserve_s"], f"{where}.work_reserve_s")
    INT(receipt["rc"], f"{where}.rc")
    for key in ("error", "soak_reference", "meter_health_error", "desk_bundle_error"):
        if key in receipt:
            TEXT(receipt[key], f"{where}.{key}")
    # ---- start authority and span id (R C:426-455, 717-720)
    authority = "t0_authority" in receipt
    if authority:
        obj({"authorized_t0_date": STR, "t0_not_before": POS, "t0_before": POS},
            {"t0_not_before_ns": POS})(receipt["t0_authority"], f"{where}.t0_authority")
        granted = receipt["t0_authority"]
        try:
            canonical = date.fromisoformat(granted["authorized_t0_date"]).isoformat() == granted["authorized_t0_date"]
        except ValueError:
            canonical = False
        if not canonical or granted["t0_not_before"] >= granted["t0_before"] or (
                granted.get("t0_not_before_ns", 1) >= granted["t0_before"] * 10 ** 9):
            refuse(f"{where}.t0_authority", "not an authority the launcher validates")
    if "span_id" in receipt:
        SPAN_ID(receipt["span_id"], f"{where}.span_id")
    obj({"epoch_s": FLOAT, "monotonic_ns": INT, **({"epoch_ns": INT, "continuous_ns": INT} if authority else {})})(
        receipt["started"], f"{where}.started")
    obj({"epoch_s": FLOAT, "monotonic_ns": INT, **({"epoch_ns": INT} if "span_id" in receipt else {})})(
        receipt["ended"], f"{where}.ended")
    # ---- roster and windows
    arr(LEG_ID, least=1)(receipt["roster"], f"{where}.roster")
    roster = receipt["roster"]
    if len(set(roster)) != len(roster):
        refuse(f"{where}.roster", "a leg selected twice")
    planned = {}
    if registered is not None:                          # L 195-217: selected kit legs, in the kit's seeded order
        order = [leg[0] for leg in registered["legs"]]
        if any(leg_id not in order for leg_id in roster) or [order.index(i) for i in roster] != sorted(
                order.index(i) for i in roster):
            refuse(f"{where}.roster", "not the kit's legs in its seeded order")
        planned = {leg[0]: leg for leg in registered["legs"]}
    arr(STR)(receipt["batch_windows"], f"{where}.batch_windows")
    for index, window in enumerate(receipt["batch_windows"]):
        match = _WINDOW.fullmatch(window)
        if not match or (match[1], match[2]) >= (match[3], match[4]):
            refuse(f"{where}.batch_windows[{index}]", "not a same-day HH:MM-HH:MM window")
    for key in ("legs_finished", "legs_planned", "load_redos_used"):
        NAT(receipt[key], f"{where}.{key}")
    if receipt["legs_planned"] != len(roster):                          # the plan's legs are the roster's
        refuse(f"{where}.legs_planned", "not the length of the plan")

    facts = {"pin": pin, "mock": mock, "roster": roster, "campaign_id": kit["campaign_id"], "planned": planned,
             "cell": pin != "A" and receipt["runner_kind"] == "cadence-legs-v1.1",
             "block_mode": 2 if hp01 else 0, "revoked": [row["leg_id"] for row in hp.get("revoked", ())]}
    span_error = "error" in receipt
    work_rc = error_code(receipt["error"], f"{where}.error") if span_error else 0
    if hp01 and "late_signals" in receipt:
        late_codes = [error_code(message, f"{where}.late_signals[{i}]")
                      for i, message in enumerate(receipt["late_signals"])]
        work_rc = work_rc or late_codes[0]

    # ---- the steps: the work prefix, then the whole close (R 365-466,485-503 / 368-491,511-529 / 500-649,669-687)
    steps = receipt["steps"]
    if type(steps) is not list:
        refuse(f"{where}.steps", "not an array")
    for index, step in enumerate(steps):
        if type(step) is not dict or type(step.get("name")) is not str:
            refuse(f"{where}.steps[{index}]", "not a step row")
    feeds = ("agents", "meter", "volumes")
    before = feeds if mock else ("volumes",)            # the feeds with a per-part check (smoke: the volume feed)
    power_close = _HP_CLOSE if hp01 else ("restore",)
    close = [*power_close, *("stop-" + feed for feed in reversed(feeds)), *(() if mock else ("close-volumes",))]
    names = [step["name"] for step in steps]
    if close[0] not in names:
        refuse(f"{where}.steps", "the close never ran")
    cut = names.index(close[0])
    if names[cut:] != close:
        refuse(f"{where}.steps", "not the close sequence")
    work, closing = steps[:cut], steps[cut:]

    attempts = receipt.get("soak_attempts")
    if pin == "C":
        arr(obj({"attempt": POS, "started_epoch_s": FLOAT, "refused": nullable(TEXT),
                 "output_dir": enum("soak", "soak.rejected1")}), most=SOAK_ATTEMPTS)(
            attempts, f"{where}.soak_attempts")
        for index, row in enumerate(attempts):
            if row["attempt"] != index + 1:
                refuse(f"{where}.soak_attempts[{index}].attempt", "not numbered in order from 1")

    legs = receipt["legs"]
    if type(legs) is not list:
        refuse(f"{where}.legs", "not an array")
    for index, row in enumerate(legs):
        if type(row) is not dict:
            refuse(f"{where}.legs[{index}]", "not an object")

    position = 0
    states = []                                         # (name, role, state, step) of the work prefix

    def take(name, role, optional=False):
        nonlocal position
        if position >= len(work):
            return None
        step = work[position]
        if step["name"] != name:
            if optional:
                return False
            refuse(f"{where}.steps[{position}].name", "not the step the writer runs here")
        state = _step(step, f"{where}.steps[{position}]", role, pin=pin, mock=mock)
        states.append((name, role, state, step))
        position += 1
        return state

    def proceeds(state):
        """Work goes on to the next step only after a step that returned."""
        return state == "returned"

    complete = False
    soak_steps, leg_steps = [], {leg_id: [] for leg_id in roster}

    def part(label, role, step_name):
        """One soak or leg attempt: its optional blackout wait, the per-part checks, then the work step."""
        waited = take(f"{label}-blackout-wait", "wait", optional=True)
        if waited not in (False, "returned"):
            return waited
        for feed in before:
            state = take(f"before-{label}-{feed}", "before")
            if not proceeds(state):
                return state
        if hp01 and role == "leg":
            state = take(f"{step_name}-powermode", "hp")
            if not proceeds(state):
                return state
        return take(step_name, role)

    def run():
        nonlocal complete
        work_steps = ("deadline", "frozen", "night_agents", "ac_power", "condition13",
                      *(("host_lock", "high_power_marker_absent") if hp01 else ()), *("start-" + f for f in feeds),
                      "read_power", *(("powermode_guard",) if hp01 else ()), "display", "dwell", "plan")
        for name in work_steps:
            role = "hp" if hp01 and name in _HP_RESULTS else name.split("-")[0]
            if not proceeds(take(name, role)):
                return
        if not same(states[-1][3]["result"]["legs"], roster):
            refuse(f"{where}.steps[{position - 1}].result.legs", "not the roster")
        number = 1
        while True:
            label = "soak" if number == 1 else f"soak.a{number}"
            state = part(label, "soak", label)
            if states and states[-1][1] == "soak":
                soak_steps.append(states[-1])
            if state == "returned":
                break
            retried = (pin == "C" and state == "raised" and number < SOAK_ATTEMPTS and position < len(work)
                       and states[-1][3]["error"].startswith("SoakRefusal: "))
            if not retried:
                return
            number += 1
        if hp01 and not proceeds(take("high_power", "hp")):
            return
        for leg_id in roster:
            number = 1
            while True:
                state = part(leg_id, "leg", f"{leg_id}.a{number}")
                if states and states[-1][1] == "leg" and states[-1][0] == f"{leg_id}.a{number}":
                    leg_steps[leg_id].append(states[-1])
                if not proceeds(state):
                    return
                redo = position < len(work) and work[position]["name"] in (
                    f"{leg_id}-blackout-wait", f"before-{leg_id}-{before[0]}")
                if not redo:
                    break
                number += 1
        complete = True

    run()
    if position != len(work):
        refuse(f"{where}.steps[{position}]", "a step after the work stopped")
    last_state = states[-1][2] if states else None
    if not span_error and not complete:
        refuse(f"{where}.steps", "the work stopped without the span's error")
    if last_state in ("raised", "both", "initial") and not span_error and not complete:
        refuse(f"{where}.error", "absent after a step that raised")
    if last_state in ("raised", "both") and span_error and complete is False:
        # the handler stores the exception that left the step (R 465/490/648); a refused soak that could not be
        # retried is raised again with its budget appended (R C:599-600)
        failed = states[-1][3]["error"]
        if receipt["error"] != failed and not (states[-1][1] == "soak" and failed.startswith("SoakRefusal: ")
                                               and receipt["error"].startswith(failed + "; no retry: ")):
            if error_code(receipt["error"], f"{where}.error") != states[-1][3]["rc"]:
                refuse(f"{where}.error", "not the exception that stopped the work")

    # ---- the soak history (R C:575-605; RL-184 F02 to F05)
    names_soak = [entry[0] for entry in soak_steps]
    if pin == "C":
        expected = ["soak", "soak.a2"][:len(attempts)]
        if names_soak != expected and not (attempts and names_soak == expected[:-1]):
            refuse(f"{where}.soak_attempts", "not one row per soak step, the last row at most one ahead")
        for index, row in enumerate(attempts):
            at = f"{where}.soak_attempts[{index}]"
            entry = soak_steps[index] if index < len(soak_steps) else None
            if row["refused"] is not None:
                if (entry is None or entry[2] != "raised" or entry[3]["rc"] != 2
                        or entry[3]["error"] != f"SoakRefusal: {row['refused']}"):
                    refuse(f"{at}.refused", "not the refusal its soak step raised")
            else:
                if entry is not None and entry[2] == "raised" and entry[3]["error"].startswith("SoakRefusal: "):
                    refuse(f"{at}.refused", "null on a soak the step refused")
                if index + 1 < len(attempts):
                    refuse(f"{at}.refused", "a retry without a recorded refusal")
            if row["output_dir"] == "soak.rejected1" and (index != 0 or row["refused"] is None):
                refuse(f"{at}.output_dir", "only a refused first soak is set aside")
            if index + 1 < len(attempts) and index == 0 and row["output_dir"] not in ("soak", "soak.rejected1"):
                refuse(f"{at}.output_dir", "not a soak directory")
        if not attempts and names_soak:
            refuse(f"{where}.soak_attempts", "empty beside a soak step (RL-184 F02)")
    soaked = bool(soak_steps) and soak_steps[-1][2] == "returned"
    if "soak_reference" in receipt:
        if not soaked or not same(receipt["soak_reference"], soak_steps[-1][3]["result"]["path"]):
            refuse(f"{where}.soak_reference", "not the path its soak step returned")
    elif soaked and (not span_error or any(leg_steps.values()) or len(legs) > 0):
        refuse(f"{where}.soak_reference", "absent after an accepted soak the work went on from")
    facts["soak_reference"] = "soak_reference" in receipt

    # ---- the reached legs (R 365-416/368-441/500-573)
    reached = [leg_id for leg_id in roster if leg_steps[leg_id]]
    started_parts = {name.split("-")[1] for name, _, _, _ in states if name.startswith("before-L")
                     or (name.endswith("-blackout-wait") and name.startswith("L"))}
    reached = [leg_id for leg_id in roster if leg_steps[leg_id] or leg_id in started_parts]
    if [row.get("leg_id") for row in legs][:len(reached)] != reached or len(legs) not in (
            len(reached), len(reached) + 1) or [row.get("leg_id") for row in legs] != roster[:len(legs)]:
        refuse(f"{where}.legs", "not the legs the work reached, in roster order")
    if len(legs) == len(reached) + 1 and not (span_error and soaked):
        refuse(f"{where}.legs", "a leg row the work never reached")
    finished, redos = 0, 0
    facts["legs"] = []
    for index, row in enumerate(legs):
        at = f"{where}.legs[{index}]"
        leg_id = row["leg_id"]
        shape = planned[leg_id][5] if leg_id in planned else None
        consumer = facts["cell"] and index > 0 and (shape == "span" if shape is not None else "span_reference" in row)
        if shape is not None and ("span_reference" in row) != consumer:
            refuse(f"{at}.span_reference", "present exactly on a span-shaped leg after the first")
        keys(row, at, ("leg_id", "attempts", "budget_s"), ("summary", "span_reference"))
        POS(row["budget_s"], f"{at}.budget_s")
        _attempts(row["attempts"], leg_id, f"{at}.attempts")
        returned = [entry for entry in leg_steps[leg_id] if entry[2] == "returned"]
        if len(row["attempts"]) not in (len(returned), len(returned) - 1) or (
                len(row["attempts"]) < len(returned) and not (span_error and index + 1 == len(legs))):
            refuse(f"{at}.attempts", "not one row per returned attempt step")
        for number, attempt in enumerate(row["attempts"]):
            if not same(attempt["leg_status"], returned[number][3]["result"]["leg_status"]):
                refuse(f"{at}.attempts[{number}].leg_status", "not its attempt step's status")
        redos += sum(attempt["redone"] for attempt in row["attempts"])
        if "span_reference" in row:
            if not consumer:
                refuse(f"{at}.span_reference", "on a leg that consumes no span reference")
            obj({**_SPAN_REFERENCE, "dir": STR})(row["span_reference"], f"{at}.span_reference")
            first = legs[0]
            source = row["span_reference"]
            if (source["leg_id"] != roster[0] or source["dir"] != f"legs/{roster[0]}/runtime"
                    or source["attempt"] != len(first["attempts"]) or source["redone"] != (source["attempt"] > 1)
                    or "summary" not in first or type(first["summary"]) is not dict
                    or source["excluded"] != (not first["summary"].get("admitted"))):
                refuse(f"{at}.span_reference", "not the span's first leg as it stood")
        done = "summary" in row
        if done:
            if not row["attempts"] or len(row["attempts"]) != len(returned) or index != finished:
                refuse(f"{at}.summary", "on a leg whose last attempt never returned")
            finished += 1
        elif index + 1 != len(legs) or not span_error:
            refuse(f"{at}.summary", "absent on a leg the work went past")
        facts["legs"].append({"leg_id": leg_id, "row": row, "done": done, "position": index,
                              "result": returned[-1][3]["result"] if returned else None})
    if receipt["legs_finished"] != finished:
        refuse(f"{where}.legs_finished", "not the number of legs with a summary")
    if receipt["load_redos_used"] != redos:
        refuse(f"{where}.load_redos_used", "not the number of redone attempts")
    if not span_error and (finished != len(roster)):
        refuse(f"{where}.legs", "an unfinished leg without the span's error")

    # ---- the close (R 485-538/511-564/669-725)
    closed = {}
    failed_close = False
    for offset, step in enumerate(closing):
        index = cut + offset
        name = step["name"]
        role = "hp" if hp01 and name in power_close else name.split("-")[0]
        state = _step(step, f"{where}.steps[{index}]", role, pin=pin, mock=mock)
        if state == "initial":
            refuse(f"{where}.steps[{index}]", "a close step that never ran")
        closed[name] = (state, step)
        failed_close = failed_close or state != "returned"
    if hp01:
        _high_power_close(hp, closed, states, facts, where)
    restore = closed["restore"][1]
    if closed["restore"][0] == "returned" and not mock and "ok" in restore["result"] and (
            (restore["result"]["rc"] == 0) != restore["result"]["ok"]):
        refuse(f"{where}.steps[{names.index('restore')}].result.rc", "not zero exactly when the restore verified")
    if closed["restore"][0] == "both" and "ok" in restore["result"] and restore["result"]["ok"]:
        refuse(f"{where}.steps[{names.index('restore')}].result.ok", "true on a restore that returned a failure")
    fault = any(closed["stop-" + feed][0] != "returned" for feed in feeds)

    obj({feed: lambda value, at: None for feed in feeds})(receipt["feeds"], f"{where}.feeds")
    hashing_failed = False
    for feed in feeds:
        at = f"{where}.feeds.{feed}"
        entry = receipt["feeds"][feed]
        obj({"files": arr(obj({"path": RELATIVE_PATH, "sha256": DIGEST}))}, {"stop": lambda v, w: None, "error": STR})(
            entry, at)
        state, step = closed["stop-" + feed]
        if ("stop" in entry) != (state == "returned"):
            refuse(f"{at}.stop", "present exactly when its stop step returned")
        if "stop" in entry and not same(entry["stop"], step["result"]):
            refuse(f"{at}.stop", "not what its stop step returned")
        if state == "returned" and step["result"]["rc"] == 0 and not step["result"]["proven_stopped"]:
            refuse(f"{at}.stop.proven_stopped", "false on a stop that returned zero")
        hashing_failed = hashing_failed or "error" in entry

    # ---- the meter projection (L 372-410/465-503) and the result snapshot (L 413-418/506-511)
    meter = receipt["meter"]
    stopped = bool(receipt["feeds"]["meter"].get("stop", {}).get("proven_stopped"))
    if "meter_health_error" in receipt:
        obj({"present": const(False), "proven_stopped": const(False)})(meter, f"{where}.meter")
    else:
        obj({"present": BOOL, "proven_stopped": const(stopped), "bad_polls": nullable(NAT), "usb_errors": nullable(NAT),
             "polls": nullable(NAT), "elapsed_s": nullable(FLOAT)})(meter, f"{where}.meter")
        populated = [meter[key] is not None for key in ("bad_polls", "usb_errors", "polls", "elapsed_s")]
        if any(populated) != all(populated) or meter["present"] != all(populated):
            refuse(f"{where}.meter", "its four counters are present together, with present")
    chain = work_rc or (2 if failed_close or hashing_failed else 0)
    done = chain == 0 and finished == len(roster)
    obj({"chain_exit_code": const(chain), "chain_outcome": const("COMPLETE" if done else "INCOMPLETE"),
         "fault": const(fault), "outcome": const("MEASURED_OK" if done and not fault else "REFUSED"),
         "verdict": const(f"{finished}/{len(roster)} legs run"),
         **({"restore_proven": const(hp.get("close_proof", {}).get("proven", False))} if hp01 else {})})(
        receipt["span_result"], f"{where}.span_result")
    if receipt["rc"] != (chain or (2 if "desk_bundle_error" in receipt else 0)):
        refuse(f"{where}.rc", "not the code its error, close and desk give")
    return facts


def _high_power_close(hp, closed, states, facts, where):
    """Check the typed copies of the mode observations and close proof in the receipt and steps."""
    at = f"{where}.high_power"
    for name, key in (("power_last_look", "before_restore"), ("restore", "restore"), ("power_proof", "close_proof")):
        result = closed[name][1].get("result")
        if result is not None:
            copied = None if "skipped" in result else {k: v for k, v in result.items() if k != "rc"}
            if not same(hp.get(key), copied):
                refuse(f"{at}.{key}", "not what its close step returned")
    observations = [row[3].get("result", {}) for row in states if row[1] == "hp"]
    observations += [hp.get("before_restore", {}), hp.get("close_proof", {})]
    if any("host_marker" in item and item["host_marker"] != hp["host_marker"] for item in observations):
        refuse(f"{at}.host_marker", "not the marker named in the mode observations")
    if "close_proof" in hp:
        proof = hp["close_proof"]
        proven = proof["ac_powermode"] == 0 and not proof["host_marker_present"]
        if proof["proven"] != proven or closed["power_proof"][1].get("result", {}).get("rc", 2) != (0 if proven else 2):
            refuse(f"{at}.close_proof", "not what the Automatic read-back and marker proved")
    if facts["revoked"] != [entry["leg_id"] for entry in facts["legs"]
                            if entry["done"] and entry["leg_id"] in facts["revoked"]]:
        refuse(f"{at}.revoked", "not a list of finished legs in order")


# ================================================================================================ soak reference
_DETRENDED = obj({"mean_c": NUM, "detrended_sd_c": NUM, "slope_c_per_min": NUM, "settled": BOOL, "window_s": NAT,
                  "window_reads": NAT})


def _soak_reference(doc, where, mock):
    """scripts/align_r1_rehearsal.py write_soak_reference (964-974/964-974/1074-1084); the mock's is R C:823-838."""
    if mock:
        obj({"schema": const(SOAK_SCHEMA), "mock": const(True)})(doc, where)
        return
    obj({"schema": const(SOAK_SCHEMA), "source_segment": STR, "source_output": STR, "attempt": NAT, "window_s": NAT,
         "sensors_c": mapping(NUM), "detrended": mapping(_DETRENDED), "sensor_roles": nullable(journals._POLICY)})(
        doc, where)
    if doc["sensors_c"].keys() != doc["detrended"].keys() or not doc["sensors_c"] or any(
            not same(doc["sensors_c"][name], doc["detrended"][name]["mean_c"]) for name in doc["sensors_c"]):
        refuse(f"{where}.sensors_c", "not the detrended means")


# ======================================================================================================= spans
def validate_span(files, where="span"):
    """Admit one span or raise Refusal. ``files`` has ``read(rel)`` (bytes or None) and ``exists(rel)``.
    Returns ``{"synthetic": bool, "docs": {rel: decoded}}`` for the reader."""
    raw = files.read(RECEIPT)
    if raw is None:
        refuse(f"{where}/{RECEIPT}", "absent")
    receipt = decode(raw, f"{where}/{RECEIPT}")
    docs = {RECEIPT: receipt}
    if type(receipt) is dict and "synthetic" in receipt:
        admission_synthetic.validate_span(files, receipt, docs, where)
        return {"synthetic": True, "docs": docs}
    facts = _receipt(receipt, f"{where}/{RECEIPT}")
    pin, mock, roster = facts["pin"], facts["mock"], facts["roster"]

    raw = files.read(SOAK_REFERENCE)
    if raw is None:
        if facts["soak_reference"]:
            refuse(f"{where}/{SOAK_REFERENCE}", "absent beside a receipt that names it")
    else:
        docs[SOAK_REFERENCE] = decode(raw, f"{where}/{SOAK_REFERENCE}")
        _soak_reference(docs[SOAK_REFERENCE], f"{where}/{SOAK_REFERENCE}", mock)

    by_leg = {entry["leg_id"]: entry for entry in facts["legs"]}
    for leg_id in roster:
        entry = by_leg.get(leg_id)
        record_rel, summary_rel = f"legs/{leg_id}/leg_record.json", f"legs/{leg_id}/leg_summary.json"
        raw_record, raw_summary = files.read(record_rel), files.read(summary_rel)
        if entry is None or not entry["done"]:
            # a record for a leg that never returned is not one the writer leaves (R 410-416/435-441/567-573)
            for rel, raw in ((record_rel, raw_record), (summary_rel, raw_summary)):
                if raw is not None:
                    refuse(f"{where}/{rel}", "present for a leg the receipt never finished")
            continue
        for rel, raw in ((record_rel, raw_record), (summary_rel, raw_summary)):
            if raw is None:
                refuse(f"{where}/{rel}", "absent for a leg the receipt counts as finished")
        record = docs[record_rel] = decode(raw_record, f"{where}/{record_rel}")
        summary = docs[summary_rel] = decode(raw_summary, f"{where}/{summary_rel}")
        row, at = entry["row"], f"{where}/{record_rel}"
        keys(record, at, ("schema", "spec", "attempts", "result"))
        const(RECORD_SCHEMA)(record["schema"], f"{at}.schema")
        _spec(record["spec"], f"{at}.spec", pin=pin, leg_id=leg_id, position=entry["position"],
              campaign_id=facts["campaign_id"], budget_s=row["budget_s"], kit_leg=facts["planned"].get(leg_id))
        _attempts(record["attempts"], leg_id, f"{at}.attempts")
        if not same(record["attempts"], row["attempts"]):
            refuse(f"{at}.attempts", "not the attempts the receipt records for this leg")
        _result_leg(pin, mock)(record["result"], f"{at}.result")
        if not same(record["result"], entry["result"]):
            refuse(f"{at}.result", "not the result its attempt step returned")
        result, spec = record["result"], record["spec"]
        if result["leg_id"] != leg_id:
            refuse(f"{at}.result.leg_id", "not this leg")
        if pin != "A" and not mock and (result["g0_shape"] != spec.get("g0_shape", "own")
                                         or result["g0_role"] != spec.get("g0_role", "capture")):
            refuse(f"{at}.result.g0_role", "not the shape and role its spec plans")
        if ("span_reference" in row) != (spec.get("g0_role") == "consume"):
            refuse(f"{where}/{RECEIPT}.legs[{entry['position']}].span_reference",
                   "present exactly on a leg whose spec consumes the span reference")
        reference = None
        if "span_reference" in row:
            reference = {key: row["span_reference"][key] for key in _SPAN_REFERENCE}
        _summary(row["summary"], f"{where}/{RECEIPT}.legs[{entry['position']}].summary", spec=spec,
                 attempts=row["attempts"], result=result, budget_s=row["budget_s"], cell=facts["cell"],
                 reference=reference, block_mode=facts["block_mode"], revoked=leg_id in facts["revoked"])
        if not same(summary, row["summary"]):
            refuse(f"{where}/{summary_rel}", "not the summary the receipt records for this leg")
        _bundle(files, docs, f"legs/{leg_id}/runtime/{result['bundle']}", where,
                {"pin": {"A": "b4b6aeb19", "B": "2d347f721", "C": "6e9d42f1d"}[pin], "leg_id": leg_id,
                 "result": result, "spec": spec})
    return {"synthetic": False, "docs": docs}


def _bundle(files, docs, bundle, where, context):
    """The accepted attempt's runtime bundle: every journal the look reads, or none of them."""
    if files.exists(f"{bundle}/{ROOT_SALVAGE}"):
        refuse(f"{where}/{bundle}/{ROOT_SALVAGE}", "salvage events outside outputs/, where no pinned writer puts them")
    present = {}
    for name in BUNDLE_FILES:
        raw = files.read(f"{bundle}/{name}")
        if raw is not None:
            at = f"{where}/{bundle}/{name}"
            present[name] = decode_lines(raw, at) if name.endswith(".jsonl") else decode(raw, at)
            docs[f"{bundle}/{name}"] = present[name]
    if present:
        journals.validate_bundle(present, f"{where}/{bundle}", context)


def validate_roster(spans):
    """Admit every rostered span, in order, before anything else of the look is read. ``spans`` is
    [(span_id, files)]. A roster is all synthetic or all written by the pinned runners."""
    admitted = {}
    for span_id, files in spans:
        admitted[span_id] = validate_span(files, span_id)
    kinds = {entry["synthetic"] for entry in admitted.values()}
    if len(kinds) > 1:
        raise Refusal("roster: generated and written spans are never mixed")
    return admitted
