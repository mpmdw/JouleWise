"""Replay the emitted arm gate and reviewed CLI against invented Git histories."""

import argparse
from collections import Counter
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
# Only the public registration row is copied into the invented evidence histories.
QUAL_REGISTERED_PATH = (
    "docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/"
    "looks/lm-qual-01.manifest.json"
)
MANIFEST = f"docs/process/cadence/looks/{LOOK}.json"
SCHEMA = f"docs/process/cadence/looks/{LOOK}.output.schema.json"
ROOT = "public"
REPORT = f"{ROOT}/{LOOK}/PUBLIC.json"
NAMING = f"docs/process/cadence/looks/{LOOK}.freeze2.json"
DECISIONS = "docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md"
NAMING_SCHEMA = "joulewise.cadence_looks.freeze2_naming.v1"
RULING = "RL-9999"  # Invented ruling applying RL-184 §2.
PROVIDER = "e3f2c7ae8c9be7a7884cf3fefa1fba3c9875f675"
CLI = "scripts/cadence_look_manifest.py"
CODE_PATHS = (
    CLI,
    "joulewise/__init__.py",
    "joulewise/schemas.py",
    "joulewise/axi_decode_config.py",
    "joulewise/idle_admission.py",
    "joulewise/validation.py",
    "joulewise/cadence_looks/__init__.py",
    "joulewise/cadence_looks/manifest.py",
    "joulewise/cadence_looks/interim_release.py",
    "joulewise/cadence_looks/custody_pins.py",
    "joulewise/cadence_looks/schema_check.py",
)
DEPENDENCY = CODE_PATHS[-1]
MISSING_EXECUTION_FIELDS = {
    "missing-execution-host": "execution_host",
    "missing-execution-custody-root": "custody_root",
}
QUAL_REGISTERED_SHA = "82a8da3deadbc43fb61d213b748b57c6c29dab101e3c06ac4e36b9e69a83c3a0"
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
    """Mutate the production pin only for an explicit refusal case."""
    pin = f'provider_commit = "{PROVIDER}"'
    assert text.count(pin) == 1
    return text.replace(pin, f"provider_commit = {revision!r}")


def naming_stanza(record):
    return ("FREEZE-2-NAMING ruling={ruling} look={look_id} coefficients_sha256={coefficients_sha256} "
            "public_sha256={public_sha256} designation={designation}").format(**record)


def deliver_provider(source, auth):
    """Copy only the reviewed code objects and the trees needed to address them by commit:path."""
    directories = {parent for path in CODE_PATHS for parent in Path(path).parents}
    entries = [("commit", PROVIDER, PROVIDER)]
    for directory in sorted(directories):
        spec = PROVIDER + ("^{tree}" if directory == Path(".") else ":" + directory.as_posix())
        entries.append(("tree", spec, oid(source, "rev-parse", spec)))
    for path in CODE_PATHS:
        spec = f"{PROVIDER}:{path}"
        entries.append(("blob", spec, oid(source, "rev-parse", spec)))
    inventory = {}
    for kind, spec, object_id in entries:
        payload = git(source, "cat-file", kind, spec)
        written = subprocess.run(["git", "-C", str(auth), "hash-object", "-w", "-t", kind, "--stdin"],
                                 input=payload, capture_output=True, env=ENV, check=True).stdout
        assert written.decode().strip() == object_id, spec
        if kind == "blob":
            inventory[spec.split(":", 1)[1]] = {"oid": object_id, "sha256": digest(payload)}
    assert oid(auth, "cat-file", "-t", PROVIDER) == "commit"
    return inventory


class PublicHistory:
    def __init__(self, root, source):
        self.publisher = root / "origin"
        self.auth = root / "auth"
        self.tmp = root / "code"
        for directory in (self.publisher, self.tmp):
            directory.mkdir(parents=True)
        self.auth.mkdir(exist_ok=True)
        for repo in (self.publisher, self.auth):
            git(repo, "init", "-q", "--template=")
        git(self.auth, "remote", "add", "origin", str(self.publisher.resolve()))
        self.source = source
        self.qual = dict(look_id=QUAL, status="registered",
                         manifest_path=QUAL_REGISTERED_PATH,
                         sha256=QUAL_REGISTERED_SHA)
        self.report = dict(look_id=LOOK, manifest_sha256=None, commit=None, stage1_sha256="3" * 64,
                           coefficients_sha256=DIGEST, in_energy_fit=0, qualified_interim="no",
                           dev_included_below_45="no", days_below_4="no", cell_below_10="no",
                           start_reading_invalid_over_10pct="no", hp01_below_9="no",
                           drift_tripwire="within", twin_agrees="yes", stage2_error="no")
        self.schema = git(source, "cat-file", "blob", f"{PROVIDER}:{SCHEMA}")
        self.manifest = dict(look_id=LOOK, status="committed",
                             outputs={"schema": {"path": SCHEMA, "sha256": digest(self.schema)}})
        self.stage1 = dict(look_id=LOOK, status="stage1_committed", manifest_path=MANIFEST,
                           sha256=digest(raw(self.manifest)), stage1_sha256="3" * 64,
                           roster_sha256="4" * 64, verdicts_sha256="5" * 64,
                           public_root=ROOT, custody_root="/invented/never-opened",
                           execution_host="fixture")
        self.execution = self.execution_commit()
        self.main = self.publish("yes")
        self.set_heads(self.main)

    def bad_provider(self, case):
        code = self.publisher.parent / case
        code.mkdir()
        git(code, "init", "-q", "--template=")
        for path in CODE_PATHS:
            if path == DEPENDENCY:
                continue
            put(code, path, git(self.source, "cat-file", "blob", f"{PROVIDER}:{path}"))
        if case == "symlink-dependency":
            (code / DEPENDENCY).symlink_to("invented-target.py")
        revision = commit(code, case)
        git(code, "update-ref", "refs/heads/bad-provider", revision)
        git(self.auth, "fetch", "-q", "--no-tags", str(code), "refs/heads/bad-provider")
        return revision

    def ledger(self, rows):
        put(self.publisher, LEDGER, raw({"schema": "joulewise.cadence_look_ledger.v1", "looks": rows}))

    def execution_commit(self, case="yes"):
        rows = [self.stage1] + ([self.qual] if self.qual is not None else [])
        if case == "single":
            rows = [self.stage1]
        if case == "bad-execution-sibling":
            rows = [self.stage1, dict(self.qual, status="run")]
        if case == "duplicate-execution":
            rows = [*rows, self.stage1]
        if case == "stale-execution":
            rows[0] = dict(self.stage1, status="committed")
        if case in MISSING_EXECUTION_FIELDS:
            rows[0] = dict(self.stage1)
            del rows[0][MISSING_EXECUTION_FIELDS[case]]
        self.ledger(rows)
        return commit(self.publisher, f"Synthetic execution {case}")

    def publish(self, case, parent=None):
        report = dict(self.report, commit=self.execution, manifest_sha256=self.stage1["sha256"])
        row = dict(self.stage1, status="run", coefficients_sha256=DIGEST)
        manifest = json.loads(raw(self.manifest))
        if case in ("no", "bare-ruling"):
            report["twin_agrees"] = "no"
        if case == "bare-ruling":
            row["ruling"] = "RL-183"
        named_words = {"named-no": "no", "named-not-evaluable": "not_evaluable", "named-invalid": "maybe"}
        if case in named_words:
            report["twin_agrees"] = named_words[case]
            row["ruling"] = RULING
        if case == "changed-commitment":
            report["coefficients_sha256"] = row["coefficients_sha256"] = OTHER
        for label, field, value in (
            ("not-evaluable", "twin_agrees", "not_evaluable"), ("bad-word", "twin_agrees", "maybe"),
            ("report-look", "look_id", QUAL), ("report-coefficient", "coefficients_sha256", OTHER),
            ("report-stage1", "stage1_sha256", OTHER), ("report-manifest", "manifest_sha256", OTHER),
        ):
            if case == label:
                report[field] = value
        if case == "missing-word":
            del report["twin_agrees"]
        if case == "nonancestor-execution":
            report["commit"] = commit(self.publisher, "Unrelated synthetic execution")
        if case in ("bad-execution-sibling", "duplicate-execution", "stale-execution", "single",
                    *MISSING_EXECUTION_FIELDS):
            report["commit"] = self.execution_commit(case)
            parent = report["commit"]
        if case == "missing-main-host":
            del row["execution_host"]
        if case == "missing-main-custody-root":
            del row["custody_root"]
        for label, field, value in (
            ("frozen", "status", "frozen"), ("registered-interim", "status", "registered"),
            ("execution-binding", "execution_host", "other-invented-host"),
            ("manifest-route", "manifest_path", "invented/restricted/coefficients.json"),
            ("report-route", "public_root", "invented/../other"),
            ("reserved-report-route", "public_root", "invented/restricted"),
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
        siblings = [self.qual] if self.qual is not None else []
        if case == "single":
            siblings = []
        elif case == "duplicate":
            siblings.append(row)
        elif case == "bad-current-sibling":
            siblings = [dict(self.qual, sha256="bad")]
        self.ledger(siblings if case == "qual-only" else [*siblings, row])
        put(self.publisher, MANIFEST, raw(manifest))
        put(self.publisher, SCHEMA, self.schema)
        put(self.publisher, REPORT, report_bytes)
        if case in ("missing-report", "audit-only", "audit-only-note", "worktree-only"):
            (self.publisher / REPORT).unlink()
        return commit(self.publisher, f"Synthetic public decision {case}", parent or self.execution)

    def set_heads(self, main, audit=None):
        git(self.publisher, "update-ref", "refs/heads/main", main)
        git(self.publisher, "update-ref", "refs/heads/audit/2026-11-10-fable", audit or main)

    def fetch(self):
        git(self.auth, "fetch", "-q", "--no-tags", "origin",
            f"+refs/heads/main:{MAIN}", f"+refs/heads/audit/2026-11-10-fable:{AUDIT}")


def observer():
    """Run the gate and its pinned Python entry in one observed interpreter."""
    import subprocess
    import sysconfig
    import tempfile

    rules = json.loads(os.environ["FREEZE_TEST_RULES"])
    scratch = os.path.abspath(rules["tmp"])
    assert tempfile.gettempdir() == scratch
    repo = os.path.abspath(rules["repo"])
    parents = {str(parent) for path in (scratch, repo) for parent in Path(path).parents}
    code_paths = set(rules["code"])
    code_dirs = {str(parent) for path in code_paths for parent in Path(path).parents}
    stdlib = os.path.realpath(sysconfig.get_path("stdlib"))
    stdlib_alias = sysconfig.get_path("stdlib")
    opened = {}
    relative_open = None

    def record(kind, detail):
        print("OBSERVE " + json.dumps([kind, detail]), file=sys.stderr, flush=True)

    def deny(detail):
        record("DENIED", detail)
        raise SystemExit("test blocked a forbidden lookup")

    def in_stdlib(path):
        return (any(path == lib or path.startswith(lib + os.sep) for lib in (stdlib, stdlib_alias))
                and not {"site-packages", "dist-packages"}.intersection(Path(path).parts))

    def staged_code(path):
        if path.startswith(scratch + os.sep):
            stage, _, entry = os.path.relpath(path, scratch).partition(os.sep)
            if stage.startswith("freeze2-code-"):
                return entry
        return None

    def file(path, operation, mode=None):
        if isinstance(path, int):
            if path not in opened:
                return
            path = opened[path]
        if path is None:
            return
        path = os.path.abspath(os.fsdecode(path))
        record("file", [operation, path, mode])
        if path == os.devnull or in_stdlib(path):
            return
        if operation in ("stat", "lstat", "access", "os.readlink", "readlink") and path in parents | {scratch, repo}:
            return
        entry = staged_code(path)
        if entry is not None and (not entry or entry in code_paths | code_dirs):
            if entry == rules.get("alter_staged") and operation == "open" and mode == "r":
                # Inject changed staged bytes just before the gate reads them back.
                rules.pop("alter_staged")
                with open(path, "ab") as handle:
                    handle.write(b"# injected scratch mutation\n")
            return
        cache = sys.pycache_prefix
        if cache and os.path.dirname(cache) == scratch and os.path.basename(cache).startswith("jw-look-pyc-"):
            if path == cache and operation != "open":
                return
            if path.startswith(cache + os.sep) and operation == "open" and mode == "r" and path.endswith(".pyc"):
                source = path.removeprefix(cache).split(".cpython-", 1)[0] + ".py"
                if in_stdlib(source) or staged_code(source) in code_paths:
                    return
        if path.startswith(scratch + os.sep):
            stage, _, entry = os.path.relpath(path, scratch).partition(os.sep)
            if stage.startswith("jw-look-pyc-") and not entry:
                return
        deny([operation, path])

    def audit(event, args):
        if event == "subprocess.Popen":
            executable, argv = args[:2]
            op = argv[3:]
            record("git", op)
            if executable != "git" or argv[:3] != ["git", "-C", repo] or op not in rules["git"]:
                deny(argv)
            env = args[3]
            if env.get("GIT_NO_REPLACE_OBJECTS") != "1" or "GIT_DIR" in env:
                deny("Git process did not isolate object provenance")
        elif event == "open":
            file(relative_open if relative_open is not None else args[0], event, args[1])
        elif event in ("os.listdir", "os.scandir", "os.chdir", "os.readlink", "os.mkdir"):
            file(args[0], event)

    def watch_metadata(name):
        original = getattr(os, name)

        def wrapped(path, *args, **kwargs):
            directory = opened.get(kwargs.get("dir_fd"))
            file(os.path.join(directory, os.fsdecode(path)) if directory else path, name)
            return original(path, *args, **kwargs)

        setattr(os, name, wrapped)

    real_open = os.open
    real_close = os.close

    def open_fd(path, flags, mode=0o777, *, dir_fd=None):
        nonlocal relative_open
        directory = opened.get(dir_fd)
        absolute = os.path.abspath(os.path.join(directory, os.fsdecode(path)) if directory else path)
        relative_open = absolute
        try:
            fd = real_open(path, flags, mode, dir_fd=dir_fd)
        finally:
            relative_open = None
        opened[fd] = absolute
        return fd

    def close_fd(fd):
        opened.pop(fd, None)
        real_close(fd)

    real_run = subprocess.run

    def git_run(argv, *args, **kwargs):
        try:
            result = real_run(argv, *args, **kwargs)
        except subprocess.CalledProcessError as failure:
            record("exit", [argv[3:], failure.returncode])
            raise
        record("exit", [argv[3:], result.returncode])
        return result

    payload = sys.stdin.read()
    args_at = sys.argv.index("-")
    assert sys.argv[1:args_at] == ["-I", "-B", "-S"]
    sys.addaudithook(audit)
    for name in ("stat", "lstat", "access", "readlink"):
        watch_metadata(name)
    os.open = open_fd
    os.close = close_fd
    subprocess.run = git_run
    sys.argv = ["-", *sys.argv[args_at + 1:]]
    exec(compile(payload, "<emitted freeze gate>", "exec"), {"__name__": "__main__"})


def probe_program(root):
    import inspect

    probe = root / "observe.py"
    globals_used = "import json, os, sys\nfrom pathlib import Path\n"
    probe.write_text(globals_used + inspect.getsource(observer) + "\nobserver()\n")
    shell = root / "observe-python"
    shell.write_text(f"#!/bin/sh\nexec {shlex.quote(sys.executable)} -I -B -S "
                     f'{shlex.quote(str(probe))} "$@"\n')
    shell.chmod(0o700)
    return shell


def exercise(root, probe, shell, body, auth, rules, *, label, **values):
    env = dict(ENV, PY=str(probe), AUTH_REPO=str(auth), TMPDIR=rules["tmp"],
               FREEZE_TEST_RULES=json.dumps(rules), FREEZE2_COEF_SHA256=DIGEST, **values)
    del env["GIT_NO_REPLACE_OBJECTS"]
    result = subprocess.run([shell, "-c", body], cwd=root, env=env, text=True,
                            capture_output=True, timeout=90)
    trace = [json.loads(line.removeprefix("OBSERVE ")) for line in result.stderr.splitlines()
             if line.startswith("OBSERVE ")]
    log = {"case": label, "shell": Path(shell).name, "exit": result.returncode, "trace": trace,
           "stdout": result.stdout, "stderr": [line for line in result.stderr.splitlines()
                                             if not line.startswith("OBSERVE ")]}
    with (root / "observed.jsonl").open("a") as handle:
        print(json.dumps(log), file=handle)
    return result, trace


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


def provider_ops(pin):
    ops = [["rev-parse", "--verify", pin + "^{commit}"]]
    for path in CODE_PATHS:
        ops.extend([["ls-tree", "-z", "--full-tree", pin, "--", path],
                    ["cat-file", "blob", pin + ":" + path]])
    return ops


def remote_ops(ref):
    short_name = ref.removeprefix("refs/remotes/")
    branch = short_name.removeprefix("origin/")
    return [
        ["fetch", "--quiet", "--no-tags", "origin", f"+refs/heads/{branch}:{ref}"],
        ["rev-parse", "--verify", "--quiet", "--symbolic-full-name", "--end-of-options", short_name],
        ["remote"],
        ["symbolic-ref", "-q", ref],
        ["remote"],
        ["rev-parse", "--verify", "--quiet", ref + "^{commit}"],
    ]


def public_rules(world, main, *, pin=PROVIDER, execution=None, naming=False):
    execution = execution or world.execution
    history_query = ["log", "--full-history", "--format=%H", main, "--", LEDGER]
    history = git(world.publisher, *history_query).decode().split()
    if execution in history:
        # In the valid fixture history the report's execution row is the first match.
        history = history[:history.index(execution) + 1]
    ops = provider_ops(pin) + remote_ops(MAIN)
    ops.extend(["show", main + ":" + path] for path in (LEDGER, MANIFEST, SCHEMA))
    ops.append(history_query)
    ops.extend(["show", commit + ":" + LEDGER] for commit in history)
    ops.extend((["show", main + ":" + REPORT], ["merge-base", "--is-ancestor", execution, main],
                ["show", execution + ":" + LEDGER]))
    if naming:
        ops.append(["show", main + ":" + NAMING])
    return dict(repo=str(world.auth), tmp=str(world.tmp), git=ops, code=CODE_PATHS)


def assert_outcome(result, trace, expected, *, label, denied_count=0):
    diagnostics = [line for line in result.stderr.splitlines() if not line.startswith("OBSERVE ")]
    denied = [detail for kind, detail in trace if kind == "DENIED"]
    assert len(denied) == denied_count, (label, denied, diagnostics)
    assert result.returncode == (0 if expected else 1), (label, result.returncode, result.stdout, diagnostics)
    assert "Traceback" not in result.stderr, (label, diagnostics)
    if not expected and ["phase", "run"] not in trace:
        assert not receipts(result)
        assert "scripts/" not in result.stdout and "qual_pin_gate" not in result.stdout


def receipts(result):
    rows = [line + "\n" for line in result.stdout.splitlines() if line.startswith("{")]
    records = [json.loads(line) for line in rows]
    assert [raw(record).decode() for record in records] == rows, result.stdout
    return records


def assert_receipt(world, result, trace, rules, main, source="yes", *, index=0):
    public = git(world.publisher, "cat-file", "blob", main + ":" + REPORT)
    expected = dict(look_id=LOOK, main_commit=main, public_sha256=digest(public),
                    coefficients_sha256=DIGEST, decision_source=source)
    assert receipts(result)[index] == expected, result.stdout
    assert f"FREEZE2_CODE {PROVIDER}" in result.stderr
    assert [op for kind, op in trace if kind == "git"] == rules["git"]
    assert [pair for kind, pair in trace if kind == "exit"] == [
        [op, 1 if op[0] == "symbolic-ref" else 0] for op in rules["git"]
    ]
    staged = {"w": Counter(), "r": Counter()}
    for kind, detail in trace:
        if kind == "file":
            op, path, mode = detail
            relative = Path(path).relative_to(rules["tmp"]) if path.startswith(rules["tmp"] + os.sep) else None
            if relative and relative.parts[0].startswith("freeze2-code-") and op == "open" and mode in staged:
                staged[mode][Path(*relative.parts[1:]).as_posix()] += 1
    assert staged["w"] == Counter(CODE_PATHS)
    assert staged["r"] == Counter({path: 2 for path in CODE_PATHS})  # Readback, then Python loads source.
    return expected


def named_history(world, case):
    word = {
        "yes-ignores-record": "yes", "named-not-evaluable": "named-not-evaluable",
        "invalid-word": "named-invalid",
    }.get(case, "named-no")
    publication = world.publish(word, parent=world.main)
    report = git(world.publisher, "cat-file", "blob", publication + ":" + REPORT)
    record = dict(schema=NAMING_SCHEMA, ruling=RULING, look_id=LOOK, coefficients_sha256=DIGEST,
                  public_sha256=digest(report), designation="freeze-2", decisions_path=DECISIONS)
    field_changes = {
        "wrong-ruling": ("ruling", "RL-9998"), "wrong-look": ("look_id", QUAL),
        "wrong-coefficient": ("coefficients_sha256", OTHER), "wrong-public": ("public_sha256", OTHER),
        "wrong-purpose": ("designation", "admit-a-successor"),
        "wrong-route": ("decisions_path", "invented/restricted/coefficients.json"),
    }
    if case in field_changes:
        field, value = field_changes[case]
        record[field] = value
    stanza = naming_stanza(record)
    record["stanza"] = stanza if case != "wrong-stanza" else stanza + " "
    heading = "RL-9998" if case == "wrong-heading" else record["ruling"]
    lines = [f"# {heading}. Synthetic ruling"]
    if case == "near-match":
        lines.append(stanza + " ")
    elif case != "main-only-record":
        lines.append(stanza)
    if case == "duplicate-stanza":
        lines.append(stanza)
    put(world.publisher, DECISIONS, ("\n".join(lines) + "\n").encode())
    decision = commit(world.publisher, "Synthetic naming audit entry " + case, publication)
    audit = commit(world.publisher, "Synthetic audit descendant", decision)
    (world.publisher / DECISIONS).unlink()
    record["decisions_commit"] = decision
    if case == "extra-key":
        record["extra"] = True
    data = raw(record)
    if case in ("noncanonical", "yes-ignores-record"):
        data = json.dumps(record, indent=2).encode()
    put(world.publisher, NAMING, data)
    if case == "audit-only-record":
        main, audit = publication, commit(world.publisher, "Synthetic audit-only record", decision)
    else:
        parent = decision if case == "off-audit" else publication
        main = commit(world.publisher, "Synthetic main naming record " + case, parent)
        if case == "off-audit":
            audit = publication
    (world.publisher / NAMING).unlink()
    world.set_heads(main, audit)
    return main, audit, decision


def naming_rules(world, main, audit, decision, case):
    reads_record = case not in ("yes-ignores-record", "invalid-word")
    rules = public_rules(world, main, naming=reads_record)
    if case in ("named-no", "named-not-evaluable", "main-only-record", "wrong-heading", "near-match",
                "duplicate-stanza", "off-audit"):
        rules["git"].extend(remote_ops(AUDIT))
        rules["git"].append(["merge-base", "--is-ancestor", decision, audit])
        if case != "off-audit":
            rules["git"].append(["show", decision + ":" + DECISIONS])
    return rules


def naming_matrix(root, probe, world, definitions, start, run):
    cases = (
        "named-not-evaluable", "yes-ignores-record", "invalid-word", "wrong-ruling",
        "wrong-look", "wrong-coefficient", "wrong-public", "wrong-purpose", "wrong-stanza",
        "wrong-route", "noncanonical", "extra-key", "audit-only-record", "main-only-record",
        "off-audit", "wrong-heading", "near-match", "duplicate-stanza",
    )
    for case in cases:
        main, audit, decision = named_history(world, case)
        rules = naming_rules(world, main, audit, decision, case)
        accepted = case in ("named-not-evaluable", "yes-ignores-record")
        for shell in SHELLS:
            result, trace = exercise(root, probe, shell, definitions + "\n" + start, world.auth, rules,
                                     label=case)
            assert_outcome(result, trace, accepted, label=(case, shell))
            if accepted:
                source = "yes" if case == "yes-ignores-record" else RULING
                assert_receipt(world, result, trace, rules, main, source)
            else:
                assert "REFUSE freeze 2 public authority" in result.stderr, result.stderr
        print(f"PASS RL-184 {case} (bash, zsh)")

    main, audit, decision = named_history(world, "named-no")
    rules = naming_rules(world, main, audit, decision, "named-no")
    earlier = oid(world.publisher, "rev-parse", decision + "^")
    changed = naming_rules(world, main, earlier, decision, "off-audit")
    for shell in SHELLS:
        world.set_heads(main, audit)
        switch = shlex.join(["git", "-C", str(world.publisher), "update-ref",
                             "refs/heads/audit/2026-11-10-fable", earlier])
        transition = switch + " || exit 1\n" + change_phase(changed)
        result, trace = exercise(root, probe, shell, "\n".join((definitions, start, transition, run)),
                                 world.auth, rules, label="named authority lost at Run")
        assert_outcome(result, trace, False, label=(shell, "named authority lost at Run"))
        assert len(receipts(result)) == 1
        assert "scripts/launch_cadence_span.py launch" not in result.stdout
        assert trace.count(["git", ["show", decision + ":" + DECISIONS]]) == 1

        world.set_heads(main, audit)
        delete = shlex.join(["git", "-C", str(world.publisher), "update-ref", "-d",
                             "refs/heads/audit/2026-11-10-fable"])
        transition = delete + " || exit 1\n" + change_phase(rules)
        result, trace = exercise(root, probe, shell, "\n".join((definitions, start, transition, run)),
                                 world.auth, rules, label="failed audit fetch at Run")
        assert_outcome(result, trace, False, label=(shell, "failed audit fetch at Run"))
        assert trace[-1] == ["phase", "run"] and result.stdout.count("native_checks") == 1
        assert len(receipts(result)) == 1
        assert "scripts/launch_cadence_span.py launch" not in result.stdout
    print("PASS Run refuses stale audit naming proof or failed audit fetch (bash, zsh)")


def registered_sibling_matrix(root, probe, world, definitions, start):
    alternate = f"docs/process/cadence/looks/{QUAL}.json"
    malformed = (
        "/" + QUAL_REGISTERED_PATH,
        "invented/../" + QUAL_REGISTERED_PATH,
        QUAL_REGISTERED_PATH.removesuffix(".json"),
    )
    cases = [
        ("control", alternate, alternate, True),
        ("registered sibling on current ledger only", QUAL_REGISTERED_PATH, None, True),
        ("registered sibling on execution ledger only", None, QUAL_REGISTERED_PATH, True),
        ("registered path on both ledgers", QUAL_REGISTERED_PATH, QUAL_REGISTERED_PATH, True),
    ]
    for path in malformed:
        cases.extend((
            (f"malformed current path {path}", path, QUAL_REGISTERED_PATH, False),
            (f"malformed execution path {path}", QUAL_REGISTERED_PATH, path, False),
        ))

    original_sibling, original_execution = world.qual, world.execution
    body = definitions + "\n" + start
    observations = []
    for case, current_path, execution_path, accepted in cases:
        world.qual = dict(original_sibling, manifest_path=execution_path) if execution_path else None
        world.execution = world.execution_commit()
        world.qual = dict(original_sibling, manifest_path=current_path) if current_path else None
        main = world.publish("yes")
        world.set_heads(main)
        rules = public_rules(world, main)
        for shell in SHELLS:
            result, trace = exercise(root, probe, shell, body, world.auth, rules, label=case)
            passed = (result.returncode == 0) == accepted
            print(f"{'PASS' if passed else 'FAIL'} {case} ({Path(shell).name}, exit {result.returncode})")
            observations.append((case, shell, result, trace, accepted, rules, main))
    world.qual, world.execution = original_sibling, original_execution
    for case, shell, result, trace, accepted, rules, main in observations:
        assert_outcome(result, trace, accepted, label=(case, shell))
        if accepted:
            assert_receipt(world, result, trace, rules, main)
        else:
            assert "REFUSE freeze 2 public authority" in result.stderr


def absent_provider_matrix(root, probe, world, items, projections):
    # Both decision refs fetch, but only the separate provider delivery supplies this object.
    rules = public_rules(world, world.main)
    rules["git"] = provider_ops(PROVIDER)[:1]
    for item, (definitions, start, run) in zip(items, projections, strict=True):
        for shell in SHELLS:
            for phase, entry in (("Start", start), ("Run", run)):
                label = f"{item.name} {phase} without provider object"
                result, trace = exercise(root, probe, shell, definitions + "\n" + entry, world.auth, rules,
                                         label=label)
                assert_outcome(result, trace, False, label=(label, shell))
                assert [op for kind, op in trace if kind == "git"] == rules["git"]
                assert "public verifier or its pinned dependencies unavailable" in result.stderr
    print("PASS all 24 shipped item/phase/shell combinations refuse before public lookups without provider delivery")


def positive_matrix(root, probe, world, items, projections):
    ordinary = world.main
    named, audit, decision = named_history(world, "named-no")
    examples = {}
    for source, main, audit_ref, rules in (
        ("yes", ordinary, ordinary, public_rules(world, ordinary)),
        (RULING, named, audit, naming_rules(world, named, audit, decision, "named-no")),
    ):
        world.set_heads(main, audit_ref)
        for item, (definitions, start, run) in zip(items, projections, strict=True):
            for shell in SHELLS:
                for phase, entry in (("Start", start), ("Run", run)):
                    label = f"{item.name} {phase} {source}"
                    result, trace = exercise(root, probe, shell, definitions + "\n" + entry,
                                             world.auth, rules, label=label)
                    assert_outcome(result, trace, True, label=(label, shell))
                    assert len(receipts(result)) == 1
                    examples[source] = assert_receipt(world, result, trace, rules, main, source)
                    endpoint = ("scripts/cadence_legs_runner.py plan" if phase == "Start" else
                                "scripts/launch_cadence_span.py launch")
                    assert result.stdout.splitlines()[2:] == re.findall(r"\b(\w+_gate)\b", CHAIN)[1:] + [endpoint]
        print(f"PASS 24 item/phase/shell combinations for {source}: {raw(examples[source]).decode().rstrip()}")


def refusal_matrix(root, probe, world, definitions, start):
    before_report = {
        "bad-execution-sibling": "history does not authenticate the execution row",
        "duplicate-execution": "history does not authenticate the execution row",
        "stale-execution": "history does not authenticate the execution row",
        "execution-binding": "history does not authenticate the execution row",
        "missing-main-host": "execution row lacks execution_host",
        "missing-main-custody-root": "execution row lacks custody_root",
        "report-route": "allowed public root is 'public'",
        **dict.fromkeys(MISSING_EXECUTION_FIELDS, "history does not authenticate the execution row"),
    }
    cases = (
        "single", "frozen", "dirty-sources", "no", "not-evaluable", "bad-word", "bare-ruling",
        "missing-word", "missing-report", "audit-only", "audit-only-note", "worktree-only", "qual-only",
        "duplicate", "registered-interim", "bad-current-sibling", "bad-execution-sibling",
        "duplicate-execution", "stale-execution", "manifest-pin", "manifest-look", "report-pin",
        "report-look", "report-manifest", "report-stage1", "report-coefficient", "noncanonical-report",
        "schema-pin", "execution-binding", "nonancestor-execution", "manifest-route", "report-route",
        "schema-route", "missing-main-host", "missing-main-custody-root", *MISSING_EXECUTION_FIELDS,
        "wrong-expected", "malformed-expected", "unset-expected", "unfilled",
        "unbound-pin", "wrong-pin", "noncommit-pin", "missing-dependency", "symlink-dependency",
        "altered-staged-dependency", "failed-main-fetch", "failed-audit-fetch",
    )
    for case in cases:
        accepted = case in ("single", "frozen", "dirty-sources")
        main = world.publish(case)
        audit = world.main if case == "audit-only" else main
        pin = PROVIDER
        data = definitions
        if case == "audit-only-note":
            note = raw({"word": "yes", "coefficients_sha256": DIGEST})
            put(world.publisher, "ordinary-public-note.json", note)
            audit = commit(world.publisher, "Invented ordinary yes note only on audit", main)
            (world.publisher / "ordinary-public-note.json").unlink()
        if case in ("missing-dependency", "symlink-dependency"):
            pin = world.bad_provider(case)
        if case == "wrong-pin":
            pin = "f" * 40
        if case == "noncommit-pin":
            pin = oid(world.auth, "rev-parse", f"{PROVIDER}:{CLI}")
        if pin != PROVIDER or case == "unbound-pin":
            data = with_test_pin(definitions, None if case == "unbound-pin" else pin)
        if case in ("worktree-only", "dirty-sources"):
            for path in (LEDGER, MANIFEST, SCHEMA, REPORT):
                put(world.auth, path, git(world.publisher, "cat-file", "blob", world.main + ":" + path))
        if case == "dirty-sources":
            for path in (*CODE_PATHS, "sitecustomize.py", "joulewise/__pycache__/__init__.cpython-313.pyc"):
                put(world.auth, path, b"raise RuntimeError('ambient source ran')\n")
        try:
            execution = json.loads(git(world.publisher, "cat-file", "blob", main + ":" + REPORT))["commit"]
        except subprocess.CalledProcessError:
            execution = world.execution
        if case == "nonancestor-execution":
            audit = execution  # Supply the object without making it a main ancestor.
        world.set_heads(main, audit)
        if case in ("failed-main-fetch", "failed-audit-fetch"):
            branch = "main" if case == "failed-main-fetch" else "audit/2026-11-10-fable"
            git(world.publisher, "update-ref", "-d", f"refs/heads/{branch}")
        rules = public_rules(world, main, pin=pin, execution=execution, naming=case == "bare-ruling")
        if case in before_report:
            rules["git"].remove(["show", main + ":" + REPORT])
        if case == "altered-staged-dependency":
            rules["alter_staged"] = DEPENDENCY
        value = {"wrong-expected": OTHER, "malformed-expected": "wrong", "unfilled": ""}.get(case, DIGEST)
        issued = ('unset FREEZE2_COEF_SHA256' if case == "unset-expected" else
                  'FREEZE2_COEF_SHA256="$FREEZE_TEST_EXPECTED"')
        for shell in SHELLS:
            result, trace = exercise(root, probe, shell, "\n".join((data, issued, start)),
                                     world.auth, rules, label=case, PYTHONPATH=str(world.auth),
                                     FREEZE_TEST_EXPECTED=value)
            assert_outcome(result, trace, accepted, label=(case, shell))
            if accepted:
                assert_receipt(world, result, trace, rules, main)
                continue
            if case.startswith("failed-"):
                assert not trace and not result.stdout
                continue
            assert result.stdout == "native_checks\n" or (case in ("unfilled", "unset-expected") and
                                                         result.stdout.endswith("WAIT: HOLD_FOR_FIT_FREEZE\n"))
            decisions = [op for kind, op in trace if kind == "git" and op[0] in ("fetch", "show")]
            if case in ("unfilled", "unset-expected", "unbound-pin", "malformed-expected"):
                assert not any(kind == "git" for kind, _ in trace)
            if case in ("wrong-pin", "noncommit-pin", "missing-dependency", "symlink-dependency",
                        "altered-staged-dependency"):
                assert not decisions and "FREEZE2_CODE" not in result.stderr
            if case in ("missing-dependency", "symlink-dependency"):
                assert "requires a regular code blob" in result.stderr
            if case == "altered-staged-dependency":
                assert "staged code differs from the pinned blob" in result.stderr
            if case in before_report:
                assert before_report[case] in result.stderr, result.stderr
                assert not any(op[0] == "show" and op[-1].endswith("/PUBLIC.json") for op in decisions)
            if case == "nonancestor-execution":
                assert "execution commit is not in main's history" in result.stderr
                assert ["show", main + ":" + REPORT] in decisions
                assert ["show", execution + ":" + LEDGER] not in decisions
            if case in ("audit-only", "audit-only-note"):
                assert ["show", main + ":" + REPORT] in decisions
                assert not any(audit + ":" in arg for op in decisions for arg in op)
        print(f"PASS {case} (bash, zsh)")


def change_phase(rules):
    return "\n".join((
        "export FREEZE_TEST_RULES=" + shlex.quote(json.dumps(rules)),
        """echo 'OBSERVE ["phase", "run"]' >&2""",
    ))


def refresh_matrix(root, probe, world, items, projections):
    changes = {
        "updated yes": world.publish("yes", parent=world.main),
        "replaced with no": world.publish("no", parent=world.main),
        "removed report": world.publish("missing-report", parent=world.main),
        "changed commitment": world.publish("changed-commitment", parent=world.main),
        "main fetch failure": None,
    }
    advance = ["git", "-C", str(world.publisher), "update-ref"]
    for item, (definitions, start, run) in zip(items, projections, strict=True):
        rules = public_rules(world, world.main)
        for shell in SHELLS:
            for case, change in changes.items():
                world.set_heads(world.main)
                args = [*advance, "refs/heads/main", change] if change else [*advance, "-d", "refs/heads/main"]
                updated = public_rules(world, change or world.main)
                transition = shlex.join(args) + " || exit 1\n" + change_phase(updated)
                result, trace = exercise(root, probe, shell, "\n".join((definitions, start, transition, run)),
                                         world.auth, rules, label=f"{item.name} {case} at Run")
                accepted = case == "updated yes"
                assert_outcome(result, trace, accepted, label=(item.name, shell, case))
                marker = trace.index(["phase", "run"])
                assert_receipt(world, result, trace[:marker], rules, world.main)
                assert result.stdout.count("scripts/cadence_legs_runner.py plan") == 1
                assert ("scripts/launch_cadence_span.py launch" in result.stdout) == accepted
                assert len(receipts(result)) == (2 if accepted else 1)
                if accepted:
                    assert_receipt(world, result, trace[marker + 1:], updated, change, index=1)
                if change:
                    assert ["git", ["show", change + ":" + REPORT]] in trace[marker:]
                    assert oid(world.auth, "rev-parse", MAIN) == change
                else:
                    assert not trace[marker + 1:] and result.stdout.count("native_checks") == 1
        print(f"PASS {item.name} Start accepts and Run independently refreshes (bash, zsh)")


def observer_checks(root, probe, world, definitions, start):
    world.set_heads(world.main)
    rules = public_rules(world, world.main)
    mutations = (
        'open(repo + "/invented/restricted/coefficients.json", "rb")',
        'os.stat(repo + "/invented/night-custody")',
        f'subprocess.check_output(["git", "-C", repo, "show", '
        f'{world.main + ":invented/restricted/coefficients.json"!r}])',
        'subprocess.run(["/bin/echo", "unexpected command"])',
    )
    for mutation in mutations:
        mutant = definitions.replace("provider_commit =", mutation + "\nprovider_commit =", 1)
        assert mutant != definitions
        result, trace = exercise(root, probe, SHELLS[0], mutant + "\n" + start,
                                 world.auth, rules, label="observer self-test")
        assert_outcome(result, trace, False, label=mutation, denied_count=1)
    print("PASS observer blocks invented forbidden open, stat, blob and subprocess attempts")


def reserved_report_route(root, probe, world, definitions, start):
    main = world.publish("reserved-report-route")
    world.set_heads(main)
    rules = public_rules(world, main)
    rules["git"] = provider_ops(PROVIDER) + remote_ops(MAIN) + [["show", main + ":" + LEDGER]]
    label = "reserved-report-route"
    for shell in SHELLS:
        result, trace = exercise(root, probe, shell, definitions + "\n" + start, world.auth, rules,
                                 label=label)
        assert_outcome(result, trace, False, label=(label, shell))
        assert "REFUSE freeze 2 public authority:" in result.stderr
        assert f"reserved component in report route 'invented/restricted/{LOOK}/PUBLIC.json'" in result.stderr
        assert [op for kind, op in trace if kind == "git"] == rules["git"]
        assert not any(kind == "file" and detail[1].endswith("/PUBLIC.json") for kind, detail in trace)
    print("PASS reserved-report-route provider refusal with zero report reads (bash, zsh)")


def matrix(root, probe, items):
    source = Path(oid(DRAFT, "rev-parse", "--show-toplevel"))
    world = PublicHistory(root / "matrix", source)
    projections = [projection(item) for item in items]
    assert len(set(projections)) == 1
    definitions, start, run = projections[0]
    absent_provider_matrix(root, probe, world, items, projections)
    inventory = deliver_provider(source, world.auth)
    (root / "provider-inventory.json").write_bytes(raw(inventory))
    for path, hashes in inventory.items():
        print(f"PROVIDER {hashes['oid']} {hashes['sha256']} {path}")
    positive_matrix(root, probe, world, items, projections)
    registered_sibling_matrix(root, probe, world, definitions, start)
    refusal_matrix(root, probe, world, definitions, start)
    naming_matrix(root, probe, world, definitions, start, run)
    refresh_matrix(root, probe, world, items, projections)
    observer_checks(root, probe, world, definitions, start)
    reserved_report_route(root, probe, world, definitions, start)


def check_regeneration(scratch, base, items):
    repo = Path(oid(DRAFT, "rev-parse", "--show-toplevel"))
    prefix = DRAFT.relative_to(repo).as_posix()
    source_roots = ("joulewise", "scripts", "configs")
    git(repo, "diff", "--exit-code", f"{base}...HEAD", "--", *source_roots)
    git(repo, "diff", "--exit-code", "HEAD", "--", *source_roots)

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
    matrix(scratch, probe, items)
    print("PASS public freeze arm in bash and zsh (reviewed CLI, ordinary yes and committed RL-184 naming)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
