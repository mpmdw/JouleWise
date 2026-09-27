"""Inventory every tolerant or direct bundle read in production Python."""

from __future__ import annotations

import ast
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOLERANT = {"raw_metadata", "raw_config", "raw_summary", "raw_artifact_bytes"}
FILES = {"metadata.json", "summary_metrics.json", "power_trace.csv"}
READS = {"read_text", "read_bytes", "open", "read_authentication_input",
         "read_authentication_text", "_read_json_object", "_load_json_object"}

# Key: tracked path, qualified function, operation.  Classes are ruled by T12.
ALLOWLIST: dict[tuple[str, str, str], tuple[str, str]] = {
    ('joulewise/analysis_engine/registry.py', 'validate_attempt_ledger', 'direct:read_authentication_input'): ('strict_validation', 'Checks manifest and attempt-ledger custody; no claim value is derived here.'),
    ('joulewise/analysis_engine/registry.py', 'validate_manifest_target_evidence', 'direct:read_authentication_input'): ('strict_validation', 'Checks manifest and attempt-ledger custody; no claim value is derived here.'),
    ('joulewise/arm_readiness.py', 'authenticate_bundle_launch_lineage', 'direct:read_bytes'): ('strict_validation', 'Authenticates launch lineage source bytes before admission.'),
    ('joulewise/bundle.py', 'RunBundleWriter.write_power_trace', 'direct:open'): ('non_claim', 'Writes the bundle trace; it does not consume a window.'),
    ('joulewise/bundle_read.py', 'BundleReader.is_complete', 'raw_summary'): ('strict_validation', 'Reader-local inventory and AXI validation; numeric accessors call metadata first.'),
    ('joulewise/bundle_read.py', 'BundleReader.is_event_v2', 'raw_metadata'): ('strict_validation', 'Reader-local inventory and AXI validation; numeric accessors call metadata first.'),
    ('joulewise/bundle_read.py', 'BundleReader.is_frozen_legacy_identity', 'raw_metadata'): ('strict_validation', 'Reader-local inventory and AXI validation; numeric accessors call metadata first.'),
    ('joulewise/bundle_read.py', 'BundleReader.rail_manifest', 'raw_metadata'): ('strict_validation', 'Reader-local inventory and AXI validation; numeric accessors call metadata first.'),
    ('joulewise/bundle_read.py', 'axi_v2_validation_problems', 'raw_config'): ('strict_validation', 'Reader-local inventory and AXI validation; numeric accessors call metadata first.'),
    ('joulewise/bundle_read.py', 'axi_v2_validation_problems', 'raw_metadata'): ('strict_validation', 'Reader-local inventory and AXI validation; numeric accessors call metadata first.'),
    ('joulewise/bundle_read.py', 'axi_v2_validation_problems', 'raw_summary'): ('strict_validation', 'Reader-local inventory and AXI validation; numeric accessors call metadata first.'),
    ('joulewise/cli.py', '_strict_emitted_token_ids_problems', 'raw_metadata'): ('strict_validation', 'Strict bundle validator reports input defects; it does not form a claim set.'),
    ('joulewise/cli.py', '_strict_problems', 'raw_config'): ('strict_validation', 'Strict bundle validator reports input defects; it does not form a claim set.'),
    ('joulewise/cli.py', '_strict_problems', 'raw_metadata'): ('strict_validation', 'Strict bundle validator reports input defects; it does not form a claim set.'),
    ('joulewise/cli.py', '_strict_problems', 'raw_summary'): ('strict_validation', 'Strict bundle validator reports input defects; it does not form a claim set.'),
    ('joulewise/cli.py', '_strict_realized_output_problems', 'raw_config'): ('strict_validation', 'Strict bundle validator reports input defects; it does not form a claim set.'),
    ('joulewise/cli.py', '_strict_realized_output_problems', 'raw_metadata'): ('strict_validation', 'Strict bundle validator reports input defects; it does not form a claim set.'),
    ('joulewise/cli.py', '_strict_reducer_version_dispatch', 'raw_metadata'): ('strict_validation', 'Strict bundle validator reports input defects; it does not form a claim set.'),
    ('joulewise/cli.py', '_strict_rich_telemetry_problems', 'raw_metadata'): ('strict_validation', 'Strict bundle validator reports input defects; it does not form a claim set.'),
    ('joulewise/cli.py', '_strict_uncertainty_evidence_problems', 'raw_metadata'): ('strict_validation', 'Strict bundle validator reports input defects; it does not form a claim set.'),
    ('joulewise/cli.py', '_strict_workload_provenance_problems', 'raw_metadata'): ('strict_validation', 'Strict bundle validator reports input defects; it does not form a claim set.'),
    ('joulewise/cli.py', '_verify_nvidia_smi_raw_to_trace', 'raw_metadata'): ('strict_validation', 'Strict bundle validator reports input defects; it does not form a claim set.'),
    ('joulewise/cli.py', '_verify_powermetrics_raw_to_trace', 'raw_metadata'): ('strict_validation', 'Strict bundle validator reports input defects; it does not form a claim set.'),
    ('joulewise/controller.py', '_experiment_cooldown_anchor', 'direct:read_text'): ('non_claim', 'Collection cooldown metadata and gap notes, before claim-set construction.'),
    ('joulewise/controller.py', '_experiment_cooldown_reference_eligibility', 'direct:read_text'): ('non_claim', 'Collection cooldown metadata and gap notes, before claim-set construction.'),
    ('joulewise/controller.py', '_member_gap_note', 'direct:read_text'): ('non_claim', 'Collection cooldown metadata and gap notes, before claim-set construction.'),
    ('joulewise/envelope_gate.py', '_level_window_energy_records', 'raw_summary'): ('historical', 'Legacy affine-smoke envelope diagnostic over strict-valid suite bundles.'),
    ('joulewise/envelope_gate.py', 'analyze_envelope_gate', 'raw_summary'): ('historical', 'Legacy affine-smoke envelope diagnostic over strict-valid suite bundles.'),
    ('joulewise/idle_dependence.py', 'derive_idle_mean_uncertainty', 'raw_artifact_bytes'): ('strict_validation', 'Reducer-owned idle uncertainty derivation follows BundleReader.metadata authentication.'),
    ('joulewise/publication_privacy.py', '_audit_metadata', 'direct:_load_json_object'): ('non_claim', 'Publication privacy audit and redaction, without a claim calculation.'),
    ('joulewise/publication_privacy.py', '_audit_summary', 'direct:_load_json_object'): ('non_claim', 'Publication privacy audit and redaction, without a claim calculation.'),
    ('joulewise/publication_privacy.py', 'verify_public_bundle', 'direct:_load_json_object'): ('non_claim', 'Publication privacy audit and redaction, without a claim calculation.'),
    ('joulewise/reduce.py', '_resolve_reducer_version', 'raw_config'): ('strict_validation', 'Single-bundle rederivation authenticates BundleReader.metadata first.'),
    ('joulewise/reduce.py', '_resolve_reducer_version', 'raw_summary'): ('strict_validation', 'Single-bundle rederivation authenticates BundleReader.metadata first.'),
    ('joulewise/reduce.py', '_verify_instrument_calibration', 'raw_config'): ('strict_validation', 'Single-bundle rederivation authenticates BundleReader.metadata first.'),
    ('joulewise/report.py', '_discover_bundles', 'raw_config'): ('non_claim', 'Read-only run browser, not a claim-set producer.'),
    ('joulewise/report.py', '_discover_bundles', 'raw_metadata'): ('non_claim', 'Read-only run browser, not a claim-set producer.'),
    ('joulewise/report.py', '_discover_bundles', 'raw_summary'): ('non_claim', 'Read-only run browser, not a claim-set producer.'),
    ('joulewise/salvage_dangler.py', '_inspect_preworkload_abort', 'direct:_read_json_object'): ('strict_validation', 'Validates terminal-absence closure and stored bundle identity only.'),
    ('joulewise/salvage_dangler.py', 'inspect_salvage_attempt', 'direct:_read_json_object'): ('strict_validation', 'Validates terminal-absence closure and stored bundle identity only.'),
    ('joulewise/whole_window.py', '_authenticated_bundle_launch_lineage_set', 'direct:_read_json_object'): ('strict_validation', 'Verdict provenance and member identity validation called behind the window gate.'),
    ('joulewise/whole_window.py', '_consumption_provenance_valid', 'direct:_read_json_object'): ('strict_validation', 'Verdict provenance and member identity validation called behind the window gate.'),
    ('joulewise/whole_window.py', '_current_core_rederivation_reasons', 'direct:_read_json_object'): ('strict_validation', 'Verdict provenance and member identity validation called behind the window gate.'),
    ('joulewise/whole_window.py', '_manifest_bundle_paths', 'direct:_read_json_object'): ('strict_validation', 'Verdict provenance and member identity validation called behind the window gate.'),
    ('joulewise/whole_window.py', '_manifest_members', 'direct:_read_json_object'): ('strict_validation', 'Verdict provenance and member identity validation called behind the window gate.'),
    ('joulewise/whole_window.py', '_row_references_current_strict_member', 'direct:_read_json_object'): ('strict_validation', 'Verdict provenance and member identity validation called behind the window gate.'),
    ('joulewise/whole_window.py', '_scientific_config_identity', 'direct:_read_json_object'): ('strict_validation', 'Verdict provenance and member identity validation called behind the window gate.'),
    ('joulewise/whole_window.py', '_validate_row_uncached', 'direct:_read_json_object'): ('strict_validation', 'Verdict provenance and member identity validation called behind the window gate.'),
    ('joulewise/whole_window.py', 'custody_telemetry_identity', 'direct:_read_json_object'): ('strict_validation', 'Verdict provenance and member identity validation called behind the window gate.'),
    ('joulewise/whole_window.py', 'whole_window_refusal_reasons', 'direct:_read_json_object'): ('strict_validation', 'Verdict provenance and member identity validation called behind the window gate.'),
    ('scripts/analyze_phase_share.py', 'analyze_bundle', 'raw_summary'): ('non_claim', 'Desk sensitivity diagnostic; no governed claim output.'),
    ('scripts/corpus_compat_receipt.py', 'evaluate_bundle', 'raw_config'): ('non_claim', 'Compatibility-gate receipt, not an energy claim.'),
    ('scripts/corpus_compat_receipt.py', 'evaluate_bundle', 'raw_metadata'): ('non_claim', 'Compatibility-gate receipt, not an energy claim.'),
    ('scripts/corpus_compat_receipt.py', 'evaluate_bundle', 'raw_summary'): ('non_claim', 'Compatibility-gate receipt, not an energy claim.'),
    ('scripts/issue_dg071_dg075_statistics.py', 'build_payload', 'direct:read_bytes'): ('historical', 'Pinned pre-directive a10 trace, SHA-256 checked by this issuer.'),
    ('scripts/make_figures.py', 'extract_rows', 'raw_config'): ('historical', 'Pinned legacy two-experiment figure corpus; historical rendering only.'),
    ('scripts/make_figures.py', 'extract_rows', 'raw_metadata'): ('historical', 'Pinned legacy two-experiment figure corpus; historical rendering only.'),
    ('scripts/make_figures.py', 'extract_rows', 'raw_summary'): ('historical', 'Pinned legacy two-experiment figure corpus; historical rendering only.'),
    ('scripts/make_figures.py', 'gate_inputs', 'raw_summary'): ('historical', 'Pinned legacy two-experiment figure corpus; historical rendering only.'),
    ('scripts/make_figures.py', 'realized_output_tokens', 'raw_metadata'): ('historical', 'Pinned legacy two-experiment figure corpus; historical rendering only.'),
    ('scripts/package_bundle_pack.py', '_preflight_bundle', 'raw_metadata'): ('non_claim', 'Publication package preflight, without claim math.'),
    ('scripts/run_campaign.py', '_axi_discover_finalized_bundles', 'direct:read_bytes'): ('strict_validation', 'Collection provenance, order, and finalized-bundle discovery before gated final analysis.'),
    ('scripts/run_campaign.py', 'authenticate_campaign_child_launch_lineage', 'direct:read_bytes'): ('strict_validation', 'Collection provenance, order, and finalized-bundle discovery before gated final analysis.'),
    ('scripts/run_campaign.py', 'run_axi_spec_campaign', 'direct:read_bytes'): ('strict_validation', 'Collection provenance, order, and finalized-bundle discovery before gated final analysis.'),
    ('scripts/run_campaign.py', 'suite_order_evidence', 'direct:_load_json_object'): ('strict_validation', 'Collection provenance, order, and finalized-bundle discovery before gated final analysis.'),
}


def _name(call: ast.Call) -> str:
    if isinstance(call.func, ast.Attribute):
        return call.func.attr
    if isinstance(call.func, ast.Name):
        return call.func.id
    return ""


def _qualified_functions(tree: ast.AST):
    def visit(node: ast.AST, prefix: str):
        for child in getattr(node, "body", []):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                qualname = f"{prefix}.{child.name}" if prefix else child.name
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    yield qualname, child
                yield from visit(child, qualname)
    yield from visit(tree, "")


def _function_nodes(root: ast.AST):
    stack = [root]
    while stack:
        node = stack.pop()
        yield node
        stack.extend(
            child for child in ast.iter_child_nodes(node)
            if not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef,
                                      ast.Lambda, ast.ClassDef))
        )


def sweep_source(path: str, source: str) -> list[tuple[str, str, str, int]]:
    tree = ast.parse(source, filename=path)
    found: list[tuple[str, str, str, int]] = []
    for qualname, function in _qualified_functions(tree):
        # Nested functions are inventoried separately, never inherited by a
        # parent function's gate.  The same applies to class methods.
        nodes = list(_function_nodes(function))
        calls = [node for node in nodes if isinstance(node, ast.Call)]
        gated = any(
            _name(call) == "authenticate_window_members"
            or _name(call) == "metadata" and isinstance(call.func, ast.Attribute)
            for call in calls
        )
        if gated:
            continue
        for call in calls:
            name = _name(call)
            if name in TOLERANT:
                found.append((path, qualname, name, call.lineno))
            elif name in READS and any(
                isinstance(child, ast.Constant) and child.value in FILES
                for child in ast.walk(call)
            ) or (path == "scripts/issue_dg071_dg075_statistics.py"
                  and qualname == "build_payload" and name == "read_bytes"
                  and isinstance(call.func, ast.Attribute)
                  and isinstance(call.func.value, ast.Name)
                  and call.func.value.id == "actual_path"
                  and "p2015-df-ph-decode-abs-r03/power_trace.csv" in source):
                found.append((path, qualname, "direct:" + name, call.lineno))
    return found


def sweep_tracked() -> list[tuple[str, str, str, int]]:
    paths = subprocess.check_output(["git", "ls-files", "-z", "joulewise", "scripts"],
                                    cwd=ROOT).decode().split("\0")
    return [row for relative in paths if relative.endswith(".py")
            for row in sweep_source(relative, (ROOT / relative).read_text())]


class ConsumerSweepTests(unittest.TestCase):
    def test_new_tolerant_and_direct_reads_are_reported(self) -> None:
        source = '''
def claim(reader, root):
    one = reader.raw_summary()
    two = (root / "power_trace.csv").read_bytes()
    return one, two
'''
        self.assertEqual(
            {(function, operation) for _, function, operation, _ in
             sweep_source("joulewise/new_claim.py", source)},
            {("claim", "raw_summary"), ("claim", "direct:read_bytes")},
        )

    def test_cli_raw_metadata_self_test(self) -> None:
        source = subprocess.check_output(
            ["git", "show", "b859317c:joulewise/cli.py"], cwd=ROOT, text=True
        )
        self.assertTrue(any(path == "joulewise/cli.py" and line == 423 and op == "raw_metadata"
                            for path, _, op, line in sweep_source("joulewise/cli.py", source)))

    def test_all_ungated_reads_have_named_reason(self) -> None:
        rows = sweep_tracked()
        actual = {(path, qualname, op) for path, qualname, op, _ in rows}
        self.assertEqual(actual, set(ALLOWLIST), sorted(actual - set(ALLOWLIST)))
        self.assertTrue(all(category in {"non_claim", "historical", "strict_validation"}
                            and reason for category, reason in ALLOWLIST.values()))
        self.assertEqual(ALLOWLIST[("scripts/issue_dg071_dg075_statistics.py",
                                    "build_payload", "direct:read_bytes")][0], "historical")


if __name__ == "__main__":
    unittest.main()
