# S1-REPAIR-ROUTE-01 §5.1 triage recorder (lead, bench; main's tree only; never committed into a test).
# Wraps joulewise.whole_window.custody_telemetry_identity and joulewise.cli.validate_bundle so that
# every call is logged with the running test id; both return the real result unchanged.
# Also blocks any ioreg start (the battery guard), as every S1 run does.
import json, os, subprocess, sys

sys.path.insert(0, os.getcwd())
_LOG = os.environ.get("TRIAGE_LOG")
_CURRENT = {"test": None}


def _log(row):
    if _LOG:
        row["test"] = _CURRENT["test"]
        with open(_LOG, "a") as fh:
            fh.write(json.dumps(row, sort_keys=True) + "\n")


_orig_init = subprocess.Popen.__init__


def _guarded(self, args, *a, **k):
    text = args if isinstance(args, str) else " ".join(map(str, args))
    if "ioreg" in text:
        _log({"kind": "ioreg_blocked"})
        raise RuntimeError("triage guard: battery probe blocked")
    return _orig_init(self, args, *a, **k)


subprocess.Popen.__init__ = _guarded

import unittest  # noqa: E402

_orig_run = unittest.TestCase.run


def _run(self, result=None):
    _CURRENT["test"] = self.id()
    try:
        return _orig_run(self, result)
    finally:
        _CURRENT["test"] = None


unittest.TestCase.run = _run

try:
    import joulewise.whole_window as _ww  # noqa: E402

    _orig_identity = _ww.custody_telemetry_identity

    def custody_telemetry_identity(bundle_path, *args, **kwargs):
        identity = _orig_identity(bundle_path, *args, **kwargs)
        _log({
            "kind": "identity",
            "bundle": str(bundle_path),
            "exempt": bool(identity.production_predicate_exempt),
            "mock_config": bool(identity.mock_config),
            "bound": bool(identity.custody_bound_config),
        })
        return identity

    _ww.custody_telemetry_identity = custody_telemetry_identity
except Exception as exc:  # pragma: no cover - recorded, never hidden
    _log({"kind": "recorder_error", "where": "whole_window", "error": repr(exc)})

try:
    import joulewise.cli as _cli  # noqa: E402

    _orig_validate = _cli.validate_bundle

    def validate_bundle(path, strict=False, *args, **kwargs):
        problems = _orig_validate(path, strict, *args, **kwargs)
        _log({"kind": "strict_validator", "bundle": str(path), "strict": bool(strict),
              "problems": len(problems)})
        return problems

    _cli.validate_bundle = validate_bundle
except Exception as exc:  # pragma: no cover
    _log({"kind": "recorder_error", "where": "cli", "error": repr(exc)})

# Rule 7 (S1-REPAIR-ROUTE-01-A1 §4.4): log every answer of _current_strict_summary per test and bundle.
try:
    _orig_css = _ww._current_strict_summary

    def _current_strict_summary(summary, bundle_path=None, *args, **kwargs):
        answer = _orig_css(summary, bundle_path, *args, **kwargs)
        _log({"kind": "strict_summary", "bundle": str(bundle_path), "answer": bool(answer)})
        return answer

    _ww._current_strict_summary = _current_strict_summary
except Exception as exc:  # pragma: no cover
    _log({"kind": "recorder_error", "where": "strict_summary", "error": repr(exc)})
