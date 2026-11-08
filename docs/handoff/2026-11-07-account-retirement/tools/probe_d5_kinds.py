"""Structure-only D5 probe: why the claim gate's GAMMA floor resolutions refused with artifact_schema_invalid.

For the lead to run, on the dry-run custody, from a clean checkout whose joulewise tree equals the pinned analysis
commit (main at d271fb476 does). It replays step 9's input loading (joulewise.cli._cmd_analyze_claims: the same
block5_claim_gate_inputs and analyze_claims call, the same arguments dry_run.step_9 builds) and captures:

  * the claim-side floor evidence binding (analysis_engine.inputs.bind_floor_artifact_evidence): every global and
    per-cell problem, reduced to a fixed label (the code word before ':' or a phrase from the binder's source);
  * which floor cells were bound;
  * what each GAMMA arm's floor request returned (request / identity codes / empty);
  * each contrast's resolution status and reason codes;

then STOPS (a BaseException raised right after both contrasts' floors are resolved), before any claim artifact is
written. stdout/stderr of the engine are discarded. It prints only labels, cell ids, words and counts, and refuses
output with a decimal.

Usage (from the checkout root):
  python3.13 -I docs/process_traces/2026-11-07-b5-release-trace/probe_d5_binding.py <repo root> <custody root> <window index>
"""
import collections
import contextlib
import io
import json
import logging
import re
import shutil
import sys
import tempfile
from pathlib import Path

# Free-text binder problems (analysis_engine/inputs.py bind_floor_artifact_evidence and helpers at 929fc65c9).
PHRASES = (
    (r"complete bundle sha256 mismatch", "complete_bundle_sha256_mismatch"),
    (r"config sha256 mismatch", "config_sha256_mismatch"),
    (r"stored floor metric does not match strict summary", "stored_metric_mismatch"),
    (r"scientific config identity is unavailable", "scientific_identity_unavailable"),
    (r"stack identity is unavailable", "stack_identity_unavailable"),
    (r"calibration bundle status is not succeeded", "bundle_status_not_succeeded"),
    (r"calibration bundle_id is not a safe basename", "bundle_id_unsafe"),
    (r"does not have one scientific config identity", "cell_identity_not_single"),
    (r"stack identity does not match the floor cell", "cell_stack_identity_mismatch"),
    (r"phase window_class cell must extract", "phase_cell_metric_mismatch"),
    (r"bound to non-phase window_class", "phase_metric_window_class_mismatch"),
    (r"^metadata\.source_provenance", "source_provenance_problem"),
    (r"floor evidence binding was not loaded", "binding_not_loaded"),
)


def label(problem):
    text = str(problem)
    m = re.match(r"strict validation raised ([A-Za-z_]+)", text)
    if m:
        return "strict_validation_raised:" + m.group(1)
    m = re.match(r"([a-z][a-z0-9_]{2,80})(:|$)", text)
    if m:
        return m.group(1)
    for pattern, name in PHRASES:
        if re.search(pattern, text):
            return name
    # Unclassified (strict-validator or other free text): its alphabetic words only, digits stripped.
    words = [w for w in re.findall(r"[A-Za-z_][A-Za-z_.]*", text) if not re.search(r"\d", w)][:6]
    return "unclassified:" + "_".join(w.lower().strip(".") for w in words)


class Stop(BaseException):
    pass


def outputs(record):
    names = set()
    for step in record.get("steps", []):
        for item in step.get("outputs") or []:
            if isinstance(item, dict) and isinstance(item.get("name"), str):
                names.add(item["name"])
    return sorted(names)


def one(names, pattern):
    found = [n for n in names if re.fullmatch(pattern, n)]
    if len(found) != 1:
        raise SystemExit("refused: custody output %s found %d times" % (pattern.split("/")[-1], len(found)))
    return found[0]


def main(repo, custody, window_index):
    repo, custody = Path(repo).resolve(), Path(custody).resolve()
    sys.path.insert(0, str(repo))
    import os
    os.chdir(repo)
    logging.disable(logging.CRITICAL)
    from joulewise import cli
    from joulewise import analysis_engine as engine
    from joulewise.analysis_engine import inputs as inputs_mod
    from scripts import produce_b5_disclosures as pbd

    record = json.loads((custody / "dry-run/B5-BLIND-DRY-RUN-RECORD.json").read_bytes())
    restricted = custody / "dry-run/restricted"
    names = outputs(record)
    floor_path = restricted / one(names, r"mint/[0-9a-f]{64}-aggregate-floor\.json")
    manifest_path = restricted / one(names, r"finalized/[^/]+\.finalized\.json")
    extraction = {p: json.loads((restricted / one(names, r"mint/[0-9a-f]{64}-extraction-%s\.json" % p)).read_bytes())
                  for p in ("alpha", "beta")}
    floor = json.loads(floor_path.read_bytes())

    pins = pbd.SealPins.load()
    table = pbd.sealed_pack_table(seal_pins=pins)
    index = pbd.load_window_index(Path(window_index), seal_pins=pins, pack_table=table)
    records = tuple(pbd.open_attempt_record(e, seal_pins=pins, pack_table=table) for e in index.entries)
    windows = pbd.select_analysed_attempts(index, records, seal_pins=pins)
    evidence_roots = {k: Path(v) for k, v in pbd._evidence_roots(floor, extraction, windows).items()}
    runs_root = Path(windows["gamma"].claim_runs_root)

    captured = {"binding": None, "requests": [], "resolutions": {}}
    original_bind = inputs_mod.bind_floor_artifact_evidence
    original_request = engine._floor_request_or_refusal
    original_resolve = engine._resolve_contrast_floor

    def bind(*args, **kwargs):
        captured["binding"] = original_bind(*args, **kwargs)
        raise Stop()

    def request(artifact, binding, contrast, condition_id, evidence, **kwargs):
        result = original_request(artifact, binding, contrast, condition_id, evidence, **kwargs)
        kind = ("empty" if result == () else "codes:" + ",".join(map(label, result)) if isinstance(result, tuple)
                else "request")
        captured["requests"].append((str(contrast.get("contrast_id")), str(condition_id), kind,
                                     "evidence_rows_%d" % len(evidence)))
        return result

    def resolve(inputs, contrast, *args, **kwargs):
        result = original_resolve(inputs, contrast, *args, **kwargs)
        cid = str(contrast.get("contrast_id"))
        if cid not in captured["resolutions"]:
            captured["resolutions"][cid] = [
                "%s:%s" % (r.status, ",".join(map(label, r.reason_codes)) or "-") for r in result]
        if len(captured["resolutions"]) >= len(inputs.manifest.get("contrasts", [])):
            raise Stop()
        return result

    inputs_mod.bind_floor_artifact_evidence = bind
    engine._floor_request_or_refusal = request
    engine._resolve_contrast_floor = resolve
    scratch = Path(tempfile.mkdtemp(prefix="d5probe-"))
    stopped, failure = False, None
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            built = inputs_mod.block5_claim_gate_inputs(Path(window_index), manifest_path, runs_root, evidence_roots)
            engine.analyze_claims(
                manifest_path, runs_root, floor_path, strict_validator=cli.validate_bundle,
                evidence_roots=evidence_roots, output_path=scratch / "never-written.json",
                **{k: built[k] for k in ("kept_units", "archive_contexts", "gamma_archive")},
                legacy_l1_mechanics=False, legacy_allowlist=cli._STRICT_LEGACY_BUNDLE_IDENTITIES,
                neg8_harvest_archive=built["gamma_archive"].window.archive_root)
    except Stop:
        stopped = True
    except Exception as exc:  # structure only: the exception class, never its message
        failure = type(exc).__name__
    finally:
        written = any(scratch.iterdir())
        shutil.rmtree(scratch, ignore_errors=True)

    binding = captured["binding"]
    out = {"stopped_before_claims": stopped, "exception_class": failure, "scratch_written": written,
           "resolutions": captured["resolutions"], "requests": captured["requests"]}
    if binding is not None:
        kinds = ("order_manifest path invalid", "provenance is missing", "cannot be read beneath",
                 "sha256 mismatch beneath", "is not valid UTF-8 JSON evidence", "order_manifest id mismatch",
                 "producer plan mismatch", "does not contain an executed member order",
                 "does not bind every calibration bundle exactly once",
                 "disagrees with frozen calibration member order", "does not preserve a contiguous A/B/B/A block")
        detail = collections.Counter()
        for p in binding.global_problems:
            if not p.startswith("component_evidence_root_disagreement"):
                continue
            comp = "absolute" if ".provenance.absolute" in p else "comparative" if ".provenance.comparative" in p else "?"
            lab = "order_manifest" if "order_manifest" in p else "campaign_log" if "campaign_log" in p else "?"
            kind = next((k for k in kinds if k in p), "other")
            errno = re.search(r"\[Errno (\d+)\]", p)
            detail["%s|%s|%s%s" % (comp, lab, kind, "|errno_" + errno.group(1) if errno else "")] += 1
        out["component_root_detail"] = dict(detail)
        out["global_problems"] = dict(collections.Counter(map(label, binding.global_problems)))
        out["cells"] = {
            cell_id: {"bound": cell_id in binding.bound_cell_ids,
                      "problems": dict(collections.Counter(label(p) for p in problems
                                                           if p not in binding.global_problems))}
            for cell_id, problems in sorted(binding.problems_by_cell.items())}
        out["floor_cells_in_artifact"] = len([c for c in floor.get("cells", []) if isinstance(c, dict)])
    text = json.dumps(out, sort_keys=True, indent=1)
    if re.search(r"\d\.\d|\de[-+]?\d", text):
        raise SystemExit("refused: output would carry a decimal")
    print(text)


if __name__ == "__main__":
    main(*sys.argv[1:])
