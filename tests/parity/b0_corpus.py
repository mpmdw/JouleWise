"""B0 IDLE input partitions, independent of the implementation under test.

Sources: activation 278ebc9e consults 77/78/79 Q3 and witnesses 29a/29b/47b/72b.
Every non-default value occurs alone and with every value of every other axis.
The four-way cleanup cross is exhaustive, not a pairwise approximation.
Projection only removes axes an operation cannot consume; coverage is checked
before projection. Named witnesses are never deduplicated away.
"""
from itertools import combinations, product
import random

SEED = 278_097_879
BASE = "2ea6a7ec"
IDLE = "quiet_predicate_evidence"
AXES = {
    "plan": ("valid", "missing", "truncated", "nonutf8", "bom", "utf16", "utf16be",
             "list", "object", "scalar", "null", "missing_keys", "wrong_types", "wrong_class"),
    "kind": ("idle", "list", "object", "integer", "null", "unknown", "calibration", "missing"),
    "identity": ("valid", "plan_id", "state_id", "head", "binding"),
    "wrapper": ("idle", "calibration", "stripped", "duplicate", "coexport", "unknown",
                "quoted", "literal_removed", "literal_changed", "tampered", "bare_idle", "bare_stripped"),
    "wrapper_file": ("regular", "missing", "directory", "symlink", "dangling", "unreadable"),
    "wrapper_encoding": ("utf8", "nonutf8", "bom", "utf16", "utf16le", "utf16be", "truncated"),
    "sidecar": ("matching", "resealed", "mismatch", "missing", "wrong_name", "malformed", "directory", "symlink", "unreadable", "nonutf8"),
    "source_sidecar": ("matching", "mismatch", "missing", "wrong_name", "malformed", "directory", "symlink", "unreadable", "nonutf8"),
    "source": ("intact", "modified", "moved", "absent", "nonutf8", "directory", "symlink", "unreadable"),
    "clone": ("intact", "dirty", "wrong_head", "moved", "archived", "absent"),
    "manifest": ("intact", "missing", "altered", "malformed", "nonutf8", "directory", "symlink", "unreadable"),
    "receipt_encoding": ("utf8", "absent", "bom", "utf16", "utf16le", "utf16be", "nonutf8", "truncated"),
    "receipt": ("valid", "invalid_schema", "plan_id", "list", "object", "scalar", "null", "wrong_types", "missing_fields"),
    "c5": ("idle", "fail", "absent", "none", "missing_kind", "calibration", "unknown", "conflict"),
    "started": ("present", "absent"),
    "outcome": ("absent", "complete", "partial", "refused", "malformed", "nonutf8", "list", "object"),
    "prepare": ("complete", "missing", "malformed", "list", "object", "scalar", "missing_digests",
                "clone", "venv", "plan", "wrapper", "render", "no_steps", "bad_steps", "bom", "utf16", "nonutf8"),
    "cleanup": ("proven", "unproven"),
    "refusal": ("absent", "present"),
    "template": ("default", "alternate"),
    "read_schedule": ("stable", "wrapper_removed_on_second_read", "wrapper_changed_on_second_read",
                      "receipt_changed_on_second_read", "source_changed_on_second_read"),
}
DEFAULTS = {name: values[0] for name, values in AXES.items()}
WRAPPER_AXES = ("wrapper", "wrapper_file", "wrapper_encoding")
SEAL_AXES = (*WRAPPER_AXES, "sidecar", "source_sidecar", "source", "clone", "manifest", "identity", "read_schedule")
STATE_AXES = ("kind", "identity", "prepare", *SEAL_AXES)
PLAN_AXES = ("plan", "identity")
REPORT_AXES = (*PLAN_AXES, *WRAPPER_AXES, "receipt_encoding", "receipt", "c5", "started", "outcome", "refusal", "read_schedule")
CLEANUP_AXES = (*REPORT_AXES, "cleanup")
OPERATIONS = {
    # Resume has unpublished custody: no driver receipt/outcome is installed.
    "evidence.prepare": (*STATE_AXES, "plan"),
    "evidence.prepare_fresh": ("kind",),
    "evidence.candidate_state": STATE_AXES,
    "evidence.sealed_state": (*STATE_AXES, "plan"),
    "evidence.sealed_state_published": (*STATE_AXES, "plan"),
    "evidence.sealed_candidate": (*PLAN_AXES, *SEAL_AXES),
    "evidence.notice_subject": STATE_AXES,
    "evidence.render_notice": (*STATE_AXES, "plan"),
    "evidence.notice_unused": STATE_AXES,
    "evidence.clone_census": STATE_AXES,
    "evidence.candidate_payload_kind": STATE_AXES,
    "generator.render_only": (*PLAN_AXES, *SEAL_AXES, "template"),
    "gate.C5": (*PLAN_AXES, *SEAL_AXES),
    "gate.C3": (*PLAN_AXES, *WRAPPER_AXES, "sidecar", "source", "c5"),
    "installer.render": (*PLAN_AXES, *SEAL_AXES),
    "installer.receipt_validation": (*PLAN_AXES, *SEAL_AXES, "receipt_encoding", "receipt", "cleanup"),
    "installer.uninstall": (*STATE_AXES, "plan"),
    "installer.veto": STATE_AXES,
    "installer.verify": (*STATE_AXES, "plan"),
    "driver.probe_dispatch": (*PLAN_AXES, *SEAL_AXES),
    "driver.artifact_list": REPORT_AXES,
    "driver.refusal_result": REPORT_AXES,
    "driver.cleanup": CLEANUP_AXES,
    "driver.courier_cleanup": CLEANUP_AXES,
    "driver.courier_argv": REPORT_AXES,
    "driver.durable_record": REPORT_AXES,
    "zero_capture_facts": (*REPORT_AXES, "sidecar", "source"),
    # Added in B0: API-availability observations, not a legacy public oracle.
    "diagnostic.custody_row": (*WRAPPER_AXES, "receipt_encoding", "receipt", "c5", "sidecar", "source"),
}


def named_cases():
    """Keep historical case names even where several reports reused a witness.

    Third-row witnesses 29a's duplicate source row, 29b S1 and 47b C4 belong to brief 10 and are
    intentionally excluded; the corresponding IDLE zero-capture seed remains.
    """
    rows = []

    def add(name, **changes):
        rows.append({"id": name, "changes": changes, "named": True})

    for report in ("29b.B1", "47b.C1", "72b.C1"):
        for label, changes in (
            ("ambiguous", {"wrapper": "duplicate"}),
            ("nonutf8", {"wrapper_encoding": "nonutf8"}),
            ("unknown", {"wrapper": "unknown"}),
            ("cal", {"wrapper_file": "missing", "identity": "plan_id", "receipt_encoding": "absent"}),
        ):
            add(report + "." + label, **changes)
    for report in ("29b.B2", "47b.C2", "72b.C2"):
        for label, changes in (
            ("intact", {}), ("clone_archived", {"source": "absent"}),
            ("chain_removed", {"wrapper_file": "missing"}),
            ("chain_tampered", {"wrapper": "tampered"}),
        ):
            add(report + "." + label, **changes)
    for report in ("29a.F1", "47b.C1.identity", "72b.C1.identity"):
        add(report + ".missing_no_C5", wrapper_file="missing", receipt_encoding="absent")
        add(report + ".wrapper_vs_C5", wrapper="calibration")
    for report in ("29a.F2", "47b.C3", "72b.C3"):
        add(report + ".list_plan", plan="list")
    for report in ("29b.N1", "47b.C5", "72b.C5"):
        add(report + ".wrong_class", plan="wrong_class", template="alternate")
        add(report + ".malformed", plan="list", template="alternate")
    add("47b.C1.cleanup_nonutf8", wrapper_encoding="nonutf8")
    add("47b.C1.nonobject_receipt", receipt="list")
    for encoding in ("bom", "utf16"):
        add("72b.F1." + encoding, wrapper_encoding="nonutf8", receipt_encoding=encoding)
    for label, changes in (
        ("missing", {"wrapper_file": "missing"}), ("nonutf8", {"wrapper_encoding": "nonutf8"}),
        ("ambiguous", {"wrapper": "duplicate"}), ("stripped", {"wrapper": "stripped"}),
        ("source_drift", {"source": "modified"}),
    ):
        add("72b.F2." + label, **changes)
    for kind in ("list", "object"):
        add("72b.F3." + kind, kind=kind)
    for wrapper in ("idle", "stripped"):
        add("72b.F4.bare_" + wrapper, wrapper="bare_" + wrapper, receipt_encoding="absent",
            sidecar="missing", source_sidecar="missing", source="absent")
    add("78.notice_subject.missing_wrapper", wrapper_file="missing")
    add("29a.source_wrapper_disagree", identity="binding")
    add("29a.zero_capture.missing_wrapper", wrapper_file="missing", started="absent")
    add("47b.C6.reporting_no_identity", wrapper="stripped", receipt_encoding="absent")
    add("29b.S2.c5_none", c5="none")
    add("29b.N4.changed_wrapper_between_reads", read_schedule="wrapper_changed_on_second_read")
    add("29a.missing_wrapper_probe", wrapper_file="missing")
    return rows


def corpus():
    cases = [{"id": "idle.valid", "changes": {}, "named": True}]
    cases.extend(named_cases())
    mutations = [(axis, value) for axis, values in AXES.items() for value in values[1:]]
    cases.extend({"id": f"single.{a}={v}", "changes": {a: v}} for a, v in mutations)
    for (a, av), (b, bv) in combinations(mutations, 2):
        if a != b:
            cases.append({"id": f"pair.{a}={av}+{b}={bv}", "changes": {a: av, b: bv}})
    # Readable/missing/directory/permission denied/invalid encoding are the
    # readability partition. Encoding also has its independent pairwise axis.
    readability = ({}, {"wrapper_file": "missing"}, {"wrapper_file": "directory"},
                   {"wrapper_file": "unreadable"}, {"wrapper_encoding": "nonutf8"})
    for read, enc, c5, outcome in product(range(len(readability)), AXES["receipt_encoding"], AXES["c5"], AXES["outcome"]):
        changes = dict(readability[read], receipt_encoding=enc, c5=c5, outcome=outcome)
        cases.append({"id": f"cross.r{read}.{enc}.{c5}.{outcome}", "changes": changes,
                      "operations": ["driver.cleanup", "driver.courier_cleanup"]})
    rng = random.Random(SEED)
    for index in range(64):
        axes = rng.sample(list(AXES), rng.randint(3, 7))
        cases.append({"id": f"multi.{index:03d}", "changes": {a: rng.choice(AXES[a][1:]) for a in axes}})
    return cases


def jobs(cases=None):
    """Deterministic per-operation projection; every retained witness runs all surfaces."""
    seen = {op: set() for op in OPERATIONS}
    for case in corpus() if cases is None else cases:
        for op in case.get("operations", OPERATIONS):
            changes = {a: v for a, v in case["changes"].items()
                       if a in OPERATIONS[op] and v != DEFAULTS[a]}
            key = tuple(sorted(changes.items()))
            if key in seen[op] and not case.get("named") and not case["id"].startswith("cross."):
                continue
            seen[op].add(key)
            yield {"id": case["id"], "operation": op, "changes": changes}
