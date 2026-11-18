"""Exercise only the emitted freeze gate with invented, offline Git histories."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys

DRAFT = Path(__file__).resolve().parents[1]
MAIN = "refs/remotes/origin/main"
AUDIT = "refs/remotes/origin/audit/2026-11-10-fable"
LEDGER = "docs/process/cadence/looks/LOOKS.json"
LOOK = "lm-interim-01"
QUAL = "lm-qual-01"
MANIFEST = f"docs/process/cadence/looks/{LOOK}.json"
SCHEMA = f"docs/process/cadence/looks/{LOOK}.output.schema.json"
ROOT = "invented/public"
REPORT = f"{ROOT}/{LOOK}/PUBLIC.json"
CLI = "scripts/cadence_look_manifest.py"
DEPENDENCY = "fixture_dependency.py"
CODE_PATHS = (CLI, DEPENDENCY)
SHELLS = ("/bin/bash", "/bin/zsh")
FETCH = (
    'git -C "$AUTH_REPO" fetch -q --no-tags origin \\\n'
    f'  +refs/heads/main:{MAIN} \\\n'
    f'  +refs/heads/audit/2026-11-10-fable:{AUDIT} || exit 1'
)
CHAIN = r"""all_gates() {
  freeze2_gate && qual_pin_gate && host_event_gate && v4_gate \
    && admission_gate && queue_gate && close_gate && pred_gate && day_gate && window_gate \
    && arm_bound_gate && batch_gate
}"""
ENV = {
    "PATH": "/usr/bin:/bin", "LC_ALL": "C", "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1", "GIT_ALLOW_PROTOCOL": "file", "GIT_NO_REPLACE_OBJECTS": "1",
    "GIT_AUTHOR_NAME": "Fixture", "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
    "GIT_COMMITTER_NAME": "Fixture", "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
    "GIT_AUTHOR_DATE": "2001-02-03T04:05:06Z", "GIT_COMMITTER_DATE": "2001-02-03T04:05:06Z",
    "GIT_TERMINAL_PROMPT": "0", "HOME": "/nonexistent",
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def raw(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


DIGEST = digest(b"opaque synthetic public commitment")
OTHER = "d" * 64


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                          env=ENV, check=True).stdout


def oid(repo, *args):
    return git(repo, *args).decode().strip()


def put(root, path, data):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)


def commit(repo, message, parent=None):
    git(repo, "add", "-A")
    parents = ["-p", parent] if parent else []
    return oid(repo, "commit-tree", oid(repo, "write-tree"), *parents, "-m", message,
               "-m", "Co-Authored-By: Sol 6.2 <noreply@openai.com>")


def function(text, name):
    return re.search(rf"^{name}\(\) \{{\n.*?^\}}$", text, re.M | re.S)[0]


def item_blocks(text):
    return re.findall(r"```sh\n(.*?)```", text, re.S)


def with_test_pin(text, revision):
    """Compile synthetic pins into a copied test program only."""
    assert text.count("provider_commit = None") == text.count("provider_paths = ()") == 1
    return text.replace("provider_commit = None", f"provider_commit = {revision!r}").replace(
        "provider_paths = ()", f"provider_paths = {CODE_PATHS!r}")


def decision_source(word, ruling_id, look, coefficient, proof=None):
    if word == "yes":
        return "yes"
    if word in ("no", "not_evaluable") and ruling_id is not None:
        if proof == (ruling_id, look, coefficient, "name-as-freeze2"):
            return "MOCK_VERIFIED"
    return None


def require(condition, detail):
    if not condition:
        raise ValueError(detail)


def authorize(repo, look, expected):
    """Model the requested interface in synthetic Git only. The owner supplies production validation."""
    require(look == LOOK and re.fullmatch("[0-9a-f]{64}", expected), "issued identity")

    def git(*args):
        return subprocess.check_output(["git", "-C", repo, *args], stderr=subprocess.DEVNULL)

    def blob(revision, path):
        return git("cat-file", "blob", revision + ":" + path)

    def row_at(revision, statuses):
        ledger = json.loads(blob(revision, LEDGER))
        require(ledger["schema"] == "joulewise.cadence_look_ledger.v1", "ledger schema")
        rows = {row["look_id"]: row for row in ledger["looks"]}
        require(len(rows) == len(ledger["looks"]) and set(rows) <= {LOOK, QUAL}, "ledger rows")
        if QUAL in rows:
            sibling = rows[QUAL]
            require(sibling["status"] == "registered" and sibling["manifest_path"] ==
                    f"docs/process/cadence/looks/{QUAL}.json" and
                    re.fullmatch("[0-9a-f]{64}", sibling["sha256"]), "registered sibling")
        row = rows[LOOK]
        require(row["status"] in statuses, "interim status")
        return row

    main = git("rev-parse", "--verify", MAIN + "^{commit}").decode().strip()
    row = row_at(main, ("run", "frozen"))
    require((row["manifest_path"], row["public_root"]) == (MANIFEST, ROOT), "public route")
    manifest = blob(main, MANIFEST)
    require(digest(manifest) == row["sha256"], "manifest pin")
    doc = json.loads(manifest)
    require((doc["look_id"], doc["status"]) == (LOOK, "committed"), "manifest identity")
    pin = doc["outputs"]["schema"]
    require(pin["path"] == SCHEMA, "output schema route")
    schema = blob(main, SCHEMA)
    require(digest(schema) == pin["sha256"], "output schema pin")
    report = blob(main, REPORT)
    require(digest(report) == row["output_sha256"], "report pin")
    public = json.loads(report)
    require(report == raw(public) and set(public) == set(json.loads(schema)["required"]),
            "closed, canonical fixture report")
    require(public["look_id"] == look, "report look")
    for key, row_key in (("manifest_sha256", "sha256"), ("stage1_sha256", "stage1_sha256"),
                         ("coefficients_sha256", "coefficients_sha256")):
        require(re.fullmatch("[0-9a-f]{64}", public[key]) and public[key] == row[row_key], key)
    require(public["coefficients_sha256"] == expected, "issued coefficient digest")
    execution = public["commit"]
    require(re.fullmatch("[0-9a-f]{40}", execution), "execution commit")
    git("merge-base", "--is-ancestor", execution, main)
    earlier = row_at(execution, ("stage1_committed",))
    for key in ("sha256", "stage1_sha256", "public_root", "custody_root", "execution_host"):
        require(earlier[key] == row[key], "execution binding")
    word = public["twin_agrees"]
    source = decision_source(word, row.get("ruling"), look, expected)
    require(source is not None, "no effective public decision")
    print("FREEZE2", look, main, row["output_sha256"], expected, source)


def provider_main():
    try:
        _, verb, r, repo, l, look, h, expected = sys.argv
        require((verb, r, l, h) == ("authorize-freeze2", "--repo", "--look-id",
                                     "--expected-coefficients-sha256"), "command")
        authorize(repo, look, expected)
    except (ValueError, KeyError, OSError, TypeError, subprocess.CalledProcessError) as error:
        sys.exit(f"HOLD_FOR_FIT_FREEZE: {error}")


def provider_source(answer):
    import inspect

    lines = ["import json, re, subprocess, sys", "from fixture_dependency import digest"]
    for name in ("MAIN", "LEDGER", "LOOK", "QUAL", "MANIFEST", "SCHEMA", "ROOT", "REPORT"):
        lines.append(f"{name} = {globals()[name]!r}")
    for fn in (raw, decision_source, require, authorize, provider_main):
        lines.append(inspect.getsource(fn))
    source = "\n".join(lines)
    if answer is not None:
        # Model an already authenticated response without an on-disk decision or record format.
        call = '    source = decision_source(word, row.get("ruling"), look, expected)'
        assert source.count(call) == 1
        source = source.replace(call, "    key = object()\n"
                                f'    proof = (key, look, {answer}, "name-as-freeze2")\n'
                                "    source = decision_source(word, key, look, expected, proof)")
    return (source + "\nprovider_main()\n").encode()


class PublicHistory:
    def __init__(self, root, *, auth=None):
        self.publisher = root / "origin"
        self.auth = auth if auth is not None else root / "auth"
        self.tmp = root / "code"
        for directory in (self.publisher, self.tmp):
            directory.mkdir(parents=True)
        self.auth.mkdir(exist_ok=True)
        for repo in (self.publisher, self.auth):
            git(repo, "init", "-q", "--template=")
        git(self.auth, "remote", "add", "origin", str(self.publisher.resolve()))
        self.code = self.provider()
        self.qual = dict(look_id=QUAL, status="registered",
                         manifest_path=f"docs/process/cadence/looks/{QUAL}.json",
                         sha256="2" * 64)
        self.report = dict(look_id=LOOK, manifest_sha256=None, commit=None, stage1_sha256="3" * 64,
                           coefficients_sha256=DIGEST, in_energy_fit=0, qualified_interim="no",
                           dev_included_below_45="no", days_below_4="no", cell_below_10="no",
                           start_reading_invalid_over_10pct="no", hp01_below_9="no",
                           drift_tripwire="within", twin_agrees="yes", stage2_error="no")
        self.schema = raw({"required": list(self.report)})
        self.manifest = dict(look_id=LOOK, status="committed",
                             outputs={"schema": {"path": SCHEMA, "sha256": digest(self.schema)}})
        self.stage1 = dict(look_id=LOOK, status="stage1_committed", manifest_path=MANIFEST,
                           sha256=digest(raw(self.manifest)), stage1_sha256="3" * 64,
                           public_root=ROOT, custody_root="/invented/never-opened",
                           execution_host="fixture")
        self.execution = self.execution_commit()
        self.main = self.publish("yes")
        self.set_heads(self.main)

    def provider(self, answer=None, *, missing=False, symlink=False):
        put(self.publisher, CLI, provider_source(answer))
        dep = self.publisher / DEPENDENCY
        dep.unlink(missing_ok=True)
        if symlink:
            dep.symlink_to("invented-target.py")
        elif not missing:
            dep.write_text("import hashlib\ndef digest(data):\n    return hashlib.sha256(data).hexdigest()\n")
        return commit(self.publisher, f"Synthetic provider {answer} {missing} {symlink}")

    def ledger(self, rows):
        put(self.publisher, LEDGER, raw({"schema": "joulewise.cadence_look_ledger.v1", "looks": rows}))

    def execution_commit(self, case="yes"):
        rows = [self.stage1, self.qual]
        if case == "single":
            rows = [self.stage1]
        if case == "bad-execution-sibling":
            rows = [self.stage1, dict(self.qual, status="run")]
        if case == "duplicate-execution":
            rows = [*rows, self.stage1]
        self.ledger(rows)
        return commit(self.publisher, f"Synthetic execution {case}", self.code)

    def publish(self, case, parent=None):
        report = dict(self.report, commit=self.execution, manifest_sha256=self.stage1["sha256"])
        row = dict(self.stage1, status="run", coefficients_sha256=DIGEST)
        manifest = json.loads(raw(self.manifest))
        if case in ("no", "bare-ruling"):
            report["twin_agrees"] = "no"
        if case == "bare-ruling":
            row["ruling"] = "RL-183"
        if case == "changed-commitment":
            report["coefficients_sha256"] = row["coefficients_sha256"] = OTHER
        for label, field, value in (
            ("not-evaluable", "twin_agrees", "not_evaluable"), ("bad-word", "twin_agrees", "maybe"),
            ("report-look", "look_id", QUAL), ("report-coefficient", "coefficients_sha256", OTHER),
            ("report-stage1", "stage1_sha256", OTHER), ("report-manifest", "manifest_sha256", OTHER),
            ("nonancestor-execution", "commit", self.code),
        ):
            if case == label:
                report[field] = value
        if case == "missing-word":
            del report["twin_agrees"]
        if case == "nonancestor-execution":
            report["commit"] = commit(self.publisher, "Unrelated synthetic execution")
        if case in ("bad-execution-sibling", "duplicate-execution", "single"):
            report["commit"] = self.execution_commit(case)
            parent = report["commit"]
        for label, field, value in (
            ("frozen", "status", "frozen"), ("registered-interim", "status", "registered"),
            ("execution-binding", "execution_host", "other-invented-host"),
            ("manifest-route", "manifest_path", "invented/restricted/coefficients.json"),
            ("report-route", "public_root", "invented/restricted"),
        ):
            if case == label:
                row[field] = value
        if case == "schema-pin":
            manifest["outputs"]["schema"]["sha256"] = OTHER
        if case == "schema-route":
            manifest["outputs"]["schema"]["path"] = "invented/restricted/coefficients.json"
        if case == "manifest-look":
            manifest["look_id"] = QUAL
        if case in ("schema-pin", "schema-route", "manifest-look"):
            row["sha256"] = report["manifest_sha256"] = digest(raw(manifest))
        report_bytes = raw(report) if case != "noncanonical-report" else json.dumps(report).encode()
        row["output_sha256"] = OTHER if case == "report-pin" else digest(report_bytes)
        if case == "manifest-pin":
            row["sha256"] = OTHER
        siblings = {
            "single": [], "duplicate": [self.qual, row], "bad-current-sibling": [dict(self.qual, sha256="bad")],
        }.get(case, [self.qual])
        self.ledger(siblings if case == "qual-only" else [*siblings, row])
        put(self.publisher, MANIFEST, raw(manifest))
        put(self.publisher, SCHEMA, self.schema)
        put(self.publisher, REPORT, report_bytes)
        if case in ("missing-report", "audit-only", "worktree-only"):
            (self.publisher / REPORT).unlink()
        return commit(self.publisher, f"Synthetic public decision {case}", parent or self.execution)

    def set_heads(self, main, audit=None):
        git(self.publisher, "update-ref", "refs/heads/main", main)
        git(self.publisher, "update-ref", "refs/heads/audit/2026-11-10-fable", audit or main)

    def fetch(self):
        git(self.auth, "fetch", "-q", "origin",
            f"+refs/heads/main:{MAIN}", f"+refs/heads/audit/2026-11-10-fable:{AUDIT}")


def observer():
    """Run the gate and its pinned Python entry in one observed interpreter."""
    import sysconfig

    rules = json.loads(os.environ["FREEZE_TEST_RULES"])
    code_root = rules["tmp"]
    stdlib = sysconfig.get_path("stdlib")

    def record(kind, detail):
        print("OBSERVE " + json.dumps([kind, detail]), file=sys.stderr, flush=True)

    def deny(detail):
        record("DENIED", detail)
        raise SystemExit("test blocked a forbidden lookup")

    def file(path, operation):
        if isinstance(path, int) or path is None:
            return
        path = os.path.abspath(os.fsdecode(path))
        record("file", [operation, path])
        if path == os.devnull:
            return
        if path == stdlib or path.startswith(stdlib + os.sep):
            return
        if path == code_root or path.startswith(code_root + os.sep):
            relative = os.path.relpath(path, code_root)
            if not re.search(r"coefficients|night-custody|restricted", relative):
                return
        deny(path)

    def audit(event, args):
        if event == "subprocess.Popen":
            executable, argv = args[:2]
            op = argv[3:]
            record("git", op)
            if executable != "git" or argv[:3] != ["git", "-C", rules["repo"]] or op not in rules["git"]:
                deny(argv)
        elif event in ("open", "os.listdir", "os.scandir", "os.chdir", "os.readlink"):
            file(args[0], event)

    def watch_metadata(name):
        original = getattr(os, name)

        def wrapped(path, *args, **kwargs):
            file(path, name)
            return original(path, *args, **kwargs)

        setattr(os, name, wrapped)

    payload = sys.stdin.read()
    args_at = sys.argv.index("-")
    flags = ["-I", "-B", "-S"] if "provider_commit =" in payload else ["-I", "-B"]
    assert sys.argv[1:args_at] == flags
    sys.addaudithook(audit)
    for name in ("stat", "lstat", "access", "readlink"):
        watch_metadata(name)
    sys.argv = ["-", *sys.argv[args_at + 1:]]
    exec(compile(payload, "<emitted freeze gate>", "exec"), {"__name__": "__main__"})


def probe_program(root):
    import inspect

    probe = root / "observe.py"
    globals_used = "import json, os, re, sys\n"
    probe.write_text(globals_used + inspect.getsource(observer) + "\nobserver()\n")
    shell = root / "observe-python"
    shell.write_text(f"#!/bin/sh\nexec {shlex.quote(sys.executable)} -I -B -S "
                     f'{shlex.quote(str(probe))} "$@"\n')
    shell.chmod(0o700)
    return shell


def exercise(root, probe, shell, body, auth, rules, **values):
    env = dict(ENV, PY=str(probe), AUTH_REPO=str(auth), TMPDIR=rules["tmp"],
               FREEZE_TEST_RULES=json.dumps(rules), FREEZE2_COEF_SHA256=DIGEST, **values)
    del env["GIT_NO_REPLACE_OBJECTS"]
    result = subprocess.run([shell, "-c", body], cwd=root, env=env, text=True,
                            capture_output=True, timeout=30)
    trace = [json.loads(line.removeprefix("OBSERVE ")) for line in result.stderr.splitlines()
             if line.startswith("OBSERVE ")]
    return result, trace


def red_boundary(root, probe, items):
    repo = root / "ordinary-note"
    repo.mkdir()
    git(repo, "init", "-q", "--template=")
    path = "ordinary-public-note.txt"
    put(repo, path, b"invented public main note\n")
    main = commit(repo, "Synthetic main without a decision")
    put(repo, path, b"ordinary invented note on audit only\n")
    audit = commit(repo, "Synthetic audit-only note", main)
    git(repo, "update-ref", MAIN, main)
    git(repo, "update-ref", AUDIT, audit)
    note_hash = digest((repo / path).read_bytes())
    temp = root / "red-code"
    temp.mkdir()
    rules = dict(repo=str(repo), tmp=str(temp), git=[
        ["rev-parse", "--verify", "origin/main^{commit}"],
        ["rev-parse", "--verify", "origin/audit/2026-11-10-fable^{commit}"],
        ["merge-base", "--is-ancestor", audit, audit],
        ["merge-base", "--is-ancestor", audit, main],
        ["cat-file", "blob", audit + ":" + path],
    ])
    failures = []
    bounds = set()
    for item in items:
        start = item_blocks(item.read_text())[0]
        bounds.add((function(start, "filled"), function(start, "freeze2_gate")))
    assert len(bounds) == 1
    filled, gate = bounds.pop()
    is_old = "FREEZE2_COEF_PATH" in gate
    # Preserve the original audit-only ordinary-blob vector even when the old fills disappear.
    payload = "\n".join((filled, gate, f"FREEZE2_COEF_SHA256={note_hash}", "freeze2_gate"))
    for shell in SHELLS:
        result, trace = exercise(root, probe, shell, payload, repo, rules,
                                 FREEZE2_COMMIT=audit, FREEZE2_COEF_PATH=path)
        (root / f"red-{Path(shell).name}.log").write_text(result.stdout + result.stderr)
        denied = sum(kind == "DENIED" for kind, _ in trace)
        assert denied == 0, result.stderr
        assert "Traceback" not in result.stderr and result.returncode in (0, 1), result.stderr
        if is_old:
            assert ["git", ["cat-file", "blob", audit + ":" + path]] in trace, result.stderr
        diagnostics = [line for line in result.stderr.splitlines() if not line.startswith("OBSERVE ")]
        detail = " / ".join([*result.stdout.splitlines(), *diagnostics])
        summary = (f"{Path(shell).name} ordinary audit-only note: exit {result.returncode}; "
                   f"main {main}; audit {audit}; forbidden lookups {denied}; {detail}")
        print(summary, flush=True)
        if result.returncode == 0:
            failures.append(Path(shell).name)
    return failures


def projection(item):
    start, run, *_ = item_blocks(item.read_text())
    assert function(start, "all_gates") == CHAIN
    phases = []
    for block, endpoint in ((start, "scripts/cadence_legs_runner.py plan"),
                            (run, "scripts/launch_cadence_span.py launch")):
        lines = [FETCH, "native_checks || exit 1", "all_gates || exit 1", endpoint]
        assert all(block.count(line) == 1 for line in lines)
        positions = [block.index(line) for line in lines]
        assert positions == sorted(positions)
        phases.append("\n".join(lines[:3]) + f"\nprintf '%s\\n' {shlex.quote(endpoint)}")
    names = re.findall(r"\b(\w+_gate)\b", CHAIN)[1:]
    stubs = [f"{name}() {{ echo {name}; }}" for name in names]
    preamble = "\n".join((function(start, "filled"), function(start, "freeze2_gate"), CHAIN,
                          "native_checks() { echo native_checks; }", *stubs))
    return preamble, *phases


def public_rules(world, main, pin, *, execution=None):
    execution = execution or world.execution
    ops = [["rev-parse", "--verify", MAIN + "^{commit}"],
           ["rev-parse", "--verify", pin + "^{commit}"],
           ["merge-base", "--is-ancestor", execution, main],
           ["cat-file", "blob", execution + ":" + LEDGER]]
    for path in CODE_PATHS:
        ops.extend([["ls-tree", "-z", "--full-tree", pin, "--", path],
                    ["cat-file", "blob", pin + ":" + path]])
    ops.extend(["cat-file", "blob", main + ":" + path] for path in (LEDGER, MANIFEST, SCHEMA, REPORT))
    return dict(repo=str(world.auth), tmp=str(world.tmp), git=ops)


def assert_outcome(result, trace, expected, *, label, denied_count=0):
    assert sum(kind == "DENIED" for kind, _ in trace) == denied_count, (label, result.stderr)
    assert (result.returncode == 0) == expected, (label, result.returncode, result.stdout, result.stderr)


def assert_receipt(result, trace, rules, main, pin, source="yes"):
    look, tip, report, expected, via = next(line.split()[1:] for line in result.stdout.splitlines()
                                           if line.startswith("FREEZE2 "))
    assert (look, tip, expected, via) == (LOOK, main, DIGEST, source), result.stdout
    assert re.fullmatch("[0-9a-f]{64}", report)
    assert f"FREEZE2_CODE {pin}" in result.stderr
    git_ops = [op for kind, op in trace if kind == "git"]
    assert git_ops.count(["rev-parse", "--verify", MAIN + "^{commit}"]) == 1
    assert {tuple(op) for op in git_ops} == {tuple(op) for op in rules["git"]}, git_ops


def matrix(root, probe, items):
    world = PublicHistory(root / "matrix")
    projections = [projection(item) for item in items]
    assert len(set(projections)) == 1
    definitions, start, run = projections[0]
    cases = (
        "yes", "single", "frozen", "dirty-sources", "no", "not-evaluable", "bad-word", "bare-ruling",
        "missing-word", "missing-report", "audit-only", "worktree-only", "qual-only", "duplicate",
        "registered-interim", "bad-current-sibling", "bad-execution-sibling", "duplicate-execution",
        "manifest-pin", "manifest-look", "report-pin", "report-look", "report-manifest", "report-stage1",
        "report-coefficient", "noncanonical-report", "schema-pin", "execution-binding",
        "nonancestor-execution", "manifest-route", "report-route", "schema-route", "wrong-expected",
        "malformed-expected", "unfilled", "provider-held", "missing-pin", "missing-dependency",
        "symlink-dependency", "verified-response", "wrong-hash-response",
    )
    for case in cases:
        yes = case in ("yes", "single", "frozen", "dirty-sources", "verified-response")
        evidence_case = "no" if case in ("verified-response", "wrong-hash-response") else case
        main = world.publish(evidence_case)
        audit = world.main if case == "audit-only" else main
        pin = world.code
        if case in ("missing-dependency", "symlink-dependency", "verified-response", "wrong-hash-response"):
            answer = {"verified-response": "expected", "wrong-hash-response": repr(OTHER)}.get(case)
            pin = world.provider(answer, missing=case == "missing-dependency",
                                 symlink=case == "symlink-dependency")
            audit = pin
        if case == "missing-pin":
            pin = "f" * 40
        if case in ("worktree-only", "dirty-sources"):
            for path in (LEDGER, MANIFEST, SCHEMA, REPORT):
                put(world.auth, path, git(world.publisher, "cat-file", "blob", world.main + ":" + path))
        if case == "dirty-sources":
            for path in (*CODE_PATHS, "sitecustomize.py"):
                put(world.auth, path, b"raise RuntimeError('ambient source ran')\n")
        try:
            execution = json.loads(git(world.publisher, "cat-file", "blob", main + ":" + REPORT))["commit"]
        except subprocess.CalledProcessError:
            execution = world.execution
        if case == "nonancestor-execution":
            audit = execution  # Supply the object without making it a main ancestor.
        world.set_heads(main, audit)
        rules = public_rules(world, main, pin, execution=execution)
        value = {"wrong-expected": OTHER, "malformed-expected": "wrong", "unfilled": ""}.get(case, DIGEST)
        data = definitions if case == "provider-held" else with_test_pin(definitions, pin)
        for shell in SHELLS:
            body = data + '\nFREEZE2_COEF_SHA256="$FREEZE_TEST_EXPECTED"\n' + start
            result, trace = exercise(root, probe, shell, body, world.auth, rules,
                                     PYTHONPATH=str(world.auth), FREEZE_TEST_EXPECTED=value)
            assert_outcome(result, trace, yes, label=(case, shell))
            assert "Traceback" not in result.stderr, (case, shell, result.stderr)
            assert result.stdout.startswith("native_checks\n")
            if yes:
                source = "MOCK_VERIFIED" if case == "verified-response" else "yes"
                assert_receipt(result, trace, rules, main, pin, source)
                assert result.stdout.splitlines()[2:] == re.findall(r"\b(\w+_gate)\b", CHAIN)[1:] + [
                    "scripts/cadence_legs_runner.py plan"]
            else:
                assert not any(line.endswith("_gate") or line.startswith("scripts/")
                               for line in result.stdout.splitlines()), result.stdout
                if case == "unfilled":
                    assert not trace, (case, trace)
                if case in ("malformed-expected", "provider-held"):
                    assert not any(kind == "git" or where[1].startswith(rules["tmp"])
                                   for kind, where in trace), (case, trace)
                if case in ("missing-dependency", "symlink-dependency"):
                    assert "requires a regular code blob" in result.stderr
        print(f"PASS {case} (bash, zsh)")

    key, other = object(), object()
    proof = (key, LOOK, DIGEST, "name-as-freeze2")
    assert decision_source("no", key, LOOK, DIGEST, proof) == "MOCK_VERIFIED"
    for invalid in (None, (other, *proof[1:]), (key, QUAL, *proof[2:]),
                    (key, LOOK, OTHER, proof[3]), (*proof[:3], "admit-new-look")):
        assert decision_source("no", key, LOOK, DIGEST, invalid) is None
    print("PASS in-memory naming response and wrong ID, look, digest and purpose")

    unchanged = world.publish("yes", parent=world.main)
    newer = world.publish("no", parent=world.main)
    removed = world.publish("missing-report", parent=world.main)
    different = world.publish("changed-commitment", parent=world.main)
    advance = ["git", "-C", str(world.publisher), "update-ref"]
    for item, (definitions, start, run) in zip(items, projections):
        data = with_test_pin(definitions, world.code)
        rules = public_rules(world, world.main, world.code)
        for shell in SHELLS:
            for change in (unchanged, newer, removed, different, None):
                world.set_heads(world.main)
                args = [*advance, "refs/heads/main", change] if change else [
                    *advance, "-d", "refs/heads/main"]
                updated = public_rules(world, change or world.main, world.code)
                transition = "\n".join((
                    shlex.join(args) + " || exit 1",
                    "export FREEZE_TEST_RULES=" + shlex.quote(json.dumps(updated)),
                    """echo 'OBSERVE ["phase", "run"]' >&2""",
                ))
                result, trace = exercise(root, probe, shell, "\n".join((data, start, transition, run)),
                                         world.auth, rules)
                assert_outcome(result, trace, change == unchanged, label=(item.name, shell, change))
                marker = trace.index(["phase", "run"])
                assert_receipt(result, trace[:marker], rules, world.main, world.code)
                assert result.stdout.count("scripts/cadence_legs_runner.py plan") == 1
                assert ("scripts/launch_cadence_span.py launch" in result.stdout) == (change == unchanged)
                if change == unchanged:
                    receipts = [line.split()[2] for line in result.stdout.splitlines() if line.startswith("FREEZE2 ")]
                    assert receipts == [world.main, unchanged]
                    assert trace[marker + 1:].count(["git", ["rev-parse", "--verify", MAIN + "^{commit}"]]) == 1
                if change:
                    assert ["git", ["cat-file", "blob", change + ":" + REPORT]] in trace[marker:]
                    assert oid(world.auth, "rev-parse", MAIN) == change
                else:
                    assert not trace[marker + 1:] and result.stdout.count("native_checks") == 1
                if change == different:
                    assert "issued coefficient digest" in result.stderr
        print(f"PASS {item.name} Start accepts; Run refreshes before accepting or refusing (bash, zsh)")

    world.set_heads(world.main)
    rules = public_rules(world, world.main, world.code)
    for forbidden in (
        'open(repo + "/invented/restricted/coefficients.json", "rb")',
        'os.stat(repo + "/invented/night-custody")',
        f'subprocess.check_output(["git", "-C", repo, "cat-file", "blob", '
        f'{world.main + ":invented/restricted/coefficients.json"!r}])',
    ):
        mutant = data.replace("provider_commit =", forbidden + "\nprovider_commit =", 1)
        assert mutant != data
        result, trace = exercise(root, probe, SHELLS[0], mutant + "\n" + start, world.auth, rules)
        assert_outcome(result, trace, False, label=forbidden, denied_count=1)
    print("PASS open, stat and Git blob observer mutations blocked; zero forbidden lookups on ordinary paths")
    print("HELD — Fable representation (committed exception)")


def check_regeneration(scratch, base, items):
    repo = Path(oid(DRAFT, "rev-parse", "--show-toplevel"))
    prefix = DRAFT.relative_to(repo).as_posix()

    def base_blob(name):
        return git(repo, "cat-file", "blob", f"{base}:{prefix}/{name}")

    metadata = json.loads(base_blob("items.json"))
    dates = ",".join(f"{span}={day}" for span, day in metadata["dates"].items())
    first, second = scratch / "first", scratch / "second"
    for output in (first, second):
        subprocess.run([sys.executable, "-B", str(DRAFT / "build_items.py"), "--dates", dates,
                        "--queue-expiry", metadata["queue_expiry"], "--output-dir", str(output)],
                       cwd=DRAFT, check=True)
        generated = json.loads((output / "items.json").read_bytes())
        assert {key: generated[key] for key in ("dates", "queue_expiry", "source", "pin")} == {
            key: metadata[key] for key in ("dates", "queue_expiry", "source", "pin")}
    pin = "6e9d42f1dd3d308bc9239143d0d634ab965e50e1"
    assert metadata["pin"] == pin
    closures = set()
    for directory in ("kits", "queues"):
        names = {row[f"{directory[:-1]}_file"] for row in metadata["items"]}
        assert len(names) == 3
        for candidate in (first, second):
            assert {p.relative_to(candidate).as_posix() for p in (candidate / directory).iterdir()} == names
        for name in sorted(names):
            expected = base_blob(name)
            assert (DRAFT / name).read_bytes() == (first / name).read_bytes() == (second / name).read_bytes() == expected, name
            if directory == "kits":
                frozen = json.loads(expected)["frozen"]
                assert frozen["commit"] == pin and len(frozen["paths"]) == 38
                members = []
                for path, sha256 in sorted(frozen["paths"].items()):
                    blob = oid(repo, "rev-parse", f"{pin}:{path}")
                    pinned = git(repo, "cat-file", "blob", f"{pin}:{path}")
                    git(repo, "diff", "--exit-code", base, "--", path)
                    assert digest(pinned) == sha256
                    assert hashlib.sha1(f"blob {len(pinned)}\0".encode() + pinned).hexdigest() == blob
                    members.append((path, sha256, blob))
                closures.add(tuple(members))
                print(f"PASS {name} exact base bytes and 38 source digests/blob OIDs")
            else:
                print(f"PASS {name} exact base bytes")

    assert len(closures) == 1
    common = (DRAFT / "gates.sh").read_text().split("# BEGIN TESTABLE GATES\n")[1].split("# END TESTABLE GATES")[0]
    old_common = base_blob("gates.sh").decode().split("# BEGIN TESTABLE GATES\n")[1].split("# END TESTABLE GATES")[0]

    def neutral_gate(text):
        freeze = re.search(r"^# RL-165 §8\.1;.*\n(?:FREEZE2_[A-Z0-9_]+=.*\n)+", text, re.M)
        assert freeze
        return text.replace(freeze[0], "<freeze fills>\n").replace(function(text, "freeze2_gate"), "<freeze gate>")

    assert neutral_gate(common) == neutral_gate(old_common)
    for item in items:
        generated = (first / item.name).read_text()
        assert (second / item.name).read_bytes() == (first / item.name).read_bytes() == item.read_bytes()
        baseline = base_blob(item.name).decode()
        assert item_blocks(generated)[0].split("# BEGIN TESTABLE GATES\n")[1].split("# END TESTABLE GATES")[0] == common
        assert_preserved(baseline.replace(old_common, common), generated)
        projection(item)
        print(f"PASS {item.name} repeatable render, unchanged non-freeze shell/text and common gate")

    kit_queue_paths = [f"{prefix}/{directory}" for directory in ("kits", "queues")]
    git(repo, "diff", "--exit-code", base, "--", *kit_queue_paths)


def assert_preserved(baseline, generated):
    def normalized(text):
        text, count = re.subn(r"(?<=HOLD_FOR_FIT_FREEZE until )[^.]+", "<freeze prerequisite>", text, count=1)
        assert count == 1
        text, count = re.subn(r"(?<=\*\*Freeze and pin\.\*\* ).*?(?=`qual_pin_gate`:)",
                              "<freeze instructions> ", text, count=1)
        assert count == 1
        text, count = re.subn(r"Verify the current kit/queue hashes again and [^.]+\.",
                              "<Run refresh>.", text, count=1)
        assert count == 1
        text, count = re.subn(r"^# Fresh refs [^\n]+\n", "<Start refresh>\n", text, flags=re.M)
        assert count == 1
        old_fetch = 'git -C "$AUTH_REPO" fetch -q origin audit/2026-11-10-fable main || exit 1'
        text, count = re.subn(f"{re.escape(old_fetch)}|{re.escape(FETCH)}", "<fetch>", text)
        assert count == 2
        text, count = re.subn(r"(?<=queue expiry stamps, )freeze-2 [^,]+", "<receipt>", text, count=1)
        assert count == 1
        return text

    assert normalized(generated) == normalized(baseline), "generation changed text outside the authorized freeze edits"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scratch", required=True, type=Path)
    parser.add_argument("--compare-regen", action="store_true")
    parser.add_argument("--base")
    args = parser.parse_args()
    if args.compare_regen != bool(args.base):
        parser.error("--compare-regen requires --base")
    scratch = args.scratch.resolve()
    scratch.mkdir(parents=True)
    items = sorted(DRAFT.glob("ITEM-qual*.md"))
    assert len(items) == 6
    if args.compare_regen:
        check_regeneration(scratch, args.base, items)
        print("PASS regeneration (six items, three kits, three queues and three 38-path closures)")
        return 0
    probe = probe_program(scratch)
    failures = red_boundary(scratch, probe, items)
    if failures:
        print("FAIL: an audit-only ordinary text blob with no public decision on main must refuse "
              f"({', '.join(failures)})")
        return 1
    matrix(scratch, probe, items)
    print("PASS public freeze arm in bash and zsh (synthetic interface only); committed exception HELD")
    return 0


if __name__ == "__main__":
    sys.exit(main())
