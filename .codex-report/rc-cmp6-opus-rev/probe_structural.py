"""RC-CMP-OPUS-REV-3: attacks on the RC-CMP-5 structural rules at 7fede8c7 (synthetic fixtures only).

Run from the repo root:
TMPDIR=/tmp/rcrevtmp PYTHONPATH=.:tests JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 \
  python3.13 .codex-report/rc-cmp-opus-rev-3/probe_structural.py
"""
import ast
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parents[2]), str(Path(__file__).resolve().parents[2] / "tests")]
from tests.independent_recompute import test_review_fixes as t  # noqa: E402
from tests.independent_recompute import test_structural_rules as s  # noqa: E402

cmp, FILL, DISCLOSURE, VERDICTS = t.cmp, t.FILL, t.DISCLOSURE, t.VERDICTS
CODED = t.BARS["recompute_coded_7e322b76"]
DECODE, PREFILL = s.DECODE, s.PREFILL


def show(name, case, raw_fill=None):
    if raw_fill is None:
        code, err, out = case.exit_code(CODED)
    else:
        code, err, out = exit_with_raw_fill(case, raw_fill)
    cover = out.get("coverage", {})
    print(f"{name}: exit={code} stderr={err.strip()!r} fails={case.fails(out) if 'counts' in out else None} "
          f"unmapped={cover.get('unmapped')} unbound={[(u['path'], u['reason']) for u in cover.get('unbound', [])]} "
          f"uncovered_numeric={cover.get('uncovered_numeric')}")
    return out


def exit_with_raw_fill(case, raw):
    """The CLI on the case's custody, with the fill file replaced by raw bytes (digest re-listed)."""
    root = case.custody()
    (root / cmp.RESTRICTED / FILL).write_bytes(raw)
    record = json.loads((root / cmp.RECORD).read_text())
    for output in record["steps"][0]["outputs"]:
        if output["name"] == FILL:
            output["sha256"] = hashlib.sha256(raw).hexdigest()
    (root / cmp.RECORD).write_text(json.dumps(record))
    ours = case.root / "ours-raw.json"
    ours.write_text(json.dumps(case.ours))
    out = case.root / "restricted-raw.json"
    out.unlink(missing_ok=True)
    import contextlib, io
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as err:
        code = cmp.main(["--l9-custody", str(root), "--recompute", str(ours), "--bars", str(CODED),
                         "--restricted-out", str(out)])
    return code, err.getvalue(), json.loads(out.read_text())


class Probes(t.Case):
    def runTest(self):
        base = copy.deepcopy((self.files, self.ours))

        def reset():
            self.files, self.ours = copy.deepcopy(base)

        show("Q0 baseline", self)

        # Q1: S1 classes a leaf numeric by JSON type only. A number written as a string
        # reaches uncovered: catch-alls and is not listed under uncovered-by-name rules.
        self.files[FILL]["campaigns"] = {"gamma": {"gross_energy_j": 123.4}}
        show("Q1a control: number under fill:campaigns catch-all", self)
        self.files[FILL]["campaigns"] = {"gamma": {"gross_energy_j": "123.4"}}
        show("Q1b same number as a string", self)
        reset()
        self.files[DISCLOSURE]["window_lines"] = {"alpha": [{"line": "battery_discharged", "value_j": 41.7}]}
        show("Q1c control: number under uncovered-by-name (battery_discharged/value_j)", self)
        self.files[DISCLOSURE]["window_lines"] = {"alpha": [{"line": "battery_discharged", "value_j": "41.7"}]}
        show("Q1d same number as a string (listed?)", self)
        self.files[DISCLOSURE]["window_lines"] = {"alpha": [{"line": "host_cpu", "value_s": 1.5,
                                                             "value_text_s": "0.93"}]}
        out = show("Q1e new string field under window_lines/.* (STRUCTURE catch-all)", self)
        reset()

        # Q2: booleans, nested lists, empty containers.
        self.files[FILL]["campaigns"] = {"gamma": {"gross_energy_j": True}}
        show("Q2a boolean under fill:campaigns catch-all", self)
        self.files[FILL]["campaigns"] = {"gamma": {"gross_energy_j": [[123.4]]}}
        show("Q2b nested list of a number under fill:campaigns", self)
        self.files[FILL]["campaigns"] = {"gamma": {"gross_energy_j": [[]]}}
        show("Q2c nested empty list", self)
        reset()
        self.files[FILL]["gamma"]["contrasts"] = []
        show("Q2d fill prints no contrast at all (completeness)", self)
        reset()
        self.files[FILL]["gamma"]["contrasts"][0] = {}
        show("Q2e fill contrast replaced by an empty object", self)
        reset()

        # Q3: S2 says keys come from structural position; binding() takes identity fields from the
        # nearest enclosing object, so a nested object can carry its own contrast_id and re-route.
        s.v3_floor(self)  # DECODE's active floor is 120.0; PREFILL's stays 103.5
        decode = next(r for r in self.files[FILL]["gamma"]["contrasts"] if r["contrast_id"] == DECODE)
        prefill = next(r for r in self.files[FILL]["gamma"]["contrasts"] if r["contrast_id"] == PREFILL)
        decode["floor"], prefill["floor"] = {"active_floor_j": 120.0}, {"active_floor_j": 103.5}
        show("Q3a control: each fill contrast prints its own active floor", self)
        decode["floor"], prefill["floor"] = {"active_floor_j": 103.5}, {"active_floor_j": 120.0}
        show("Q3b control: floors swapped between contrasts", self)
        decode["floor"] = {"contrast_id": PREFILL, "active_floor_j": 103.5}
        prefill["floor"] = {"contrast_id": DECODE, "active_floor_j": 120.0}
        out = show("Q3c floors swapped, each floor object naming the other contrast", self)
        print("    leaves:", {k: v for k, v in out["coverage"]["leaves"].items() if "floor" in k})
        reset()

        # Q4: duplicate keys inside one JSON object: the loader keeps the last one silently.
        fill = copy.deepcopy(self.files[FILL])
        text = json.dumps(fill)
        dup = text.replace('"estimate": -1.25', '"estimate": 999.0, "estimate": -1.25', 1)
        assert dup != text
        show("Q4 fill object with estimate printed twice (999.0 then the agreeing value)", self, dup.encode())
        reset()

        # Q5: breadth of uncovered-by-name rules (numbers pass, listed only in the restricted file).
        self.files[FILL]["gamma"]["contrasts"][0]["floor_attempt"] = {"attempt": 87.25}
        show("Q5a any field named 'attempt' anywhere (IDENTITY_NUMBER)", self)
        reset()
        self.files[FILL]["gamma"]["contrasts"][0]["equivalence"] = {"margin_j": 87.25, "anything": {"x": 1.5}}
        show("Q5b any number under a fill contrast's equivalence/metric/conditions", self)
        reset()
        self.files[FILL]["gamma"]["contrasts"][0]["j_per_token"] = None
        self.files[FILL]["gamma"]["contrasts"][0]["claim_evaluation"] = {"outcome": None}
        show("Q5c control: a null outside the named j_per_token rule", self)
        reset()

        # Q6 (over-refusal): L9's v3 artifact admits a refused arm gate with floor_gate_j null
        # (analysis_engine/artifact.py: "refused gate requires null"); the fill copies it.
        verdict_floor, fill_floor = s.v3_floor(self)
        for floor in (verdict_floor, fill_floor):
            floor["arm_gates"][1].update(status="refused", floor_gate_j=None)
        self.ours["floor_cells"]["Qwen3-8B-4bit/decode"]["floor_gate_j"] = None
        show("Q6 refused arm gate B printed as null on both sides", self)
        reset()


def ast_gaps():
    """S3's AST test, run over the shipped script plus three appended one-sided shapes."""
    shapes = {
        "control_one_sided_for": "def compare_for(c, l9):\n    for k in l9:\n        c.numeric('count', k, l9[k], None)\n",
        "while_loop": "def compare_while(c, l9):\n    it = iter(l9)\n    while True:\n        k = next(it, None)\n"
                      "        if k is None:\n            break\n        c.numeric('count', k, l9[k], None)\n",
        "helper_add": "def helper_add(c, l9):\n    for k in l9:\n        c.add({'family': 'count', 'key': k, 'verdict': 'AGREE'})\n",
        "helper_calls_family": "def helper_loop(c, l9):\n    for k in l9:\n        compare_one(c, k)\n",
    }
    base = s.SCRIPT.read_text()
    for name, extra in shapes.items():
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "script.py"
            path.write_text(base + "\n\n" + extra)
            s.SCRIPT_SAVED, s.SCRIPT = s.SCRIPT, path
            try:
                suite = unittest.TestLoader().loadTestsFromTestCase(s.StructureTests)
                result = unittest.TextTestRunner(stream=open("/dev/null", "w")).run(suite)
                print(f"AST {name}: StructureTests failures={len(result.failures)} errors={len(result.errors)} "
                      f"(0 means the shape is not caught)")
            finally:
                s.SCRIPT = s.SCRIPT_SAVED


if __name__ == "__main__":
    unittest.TextTestRunner(stream=sys.stderr, verbosity=0).run(Probes())
    ast_gaps()
