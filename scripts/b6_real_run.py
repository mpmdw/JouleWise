#!/usr/bin/env python3
"""Block 6 real-run launcher (pin request O-6; RL-134 items 4, 5, 6, 11, 13; runbook build B-2).

    b6_real_run.py --checkout W --expect-commit SHA --stem NAME --limit-s N --out-dir DIR -- <argv for
                   scripts/independent_recompute_b6.py>

Before launch it refuses (exit 9, one line) unless the run checkout is at SHA, clean, and its 24 closure files
hash to the table below; DIR does not exist and its parent is mode 700; JW_B5_SYNTHETIC_ONLY is unset; every
--session path is absolute; --restricted-out and --public-out lie inside DIR.

It runs `[PY, "-B", W/scripts/independent_recompute_b6.py, ...]` with cwd W, a new session (process group),
stdin /dev/null and a fixed environment (TMPDIR = DIR/analysis-tmp, mode 700), at normal priority, under
`/usr/bin/time -l` as `b6_r12_verify.run_option_c` does: time wraps this script's --exec-child mode, which runs
the program, keeps its exit code and peak RSS in DIR/process.json, and writes the program's stdout and stderr to
DIR/stdout and DIR/stderr (0600). time's own report goes to DIR/time.

A sampler appends one line to DIR/samples.jsonl every 60 s: elapsed, the program's CPU seconds and RSS, its nice
and priority, the custody session id it has open (the `<id>` of `<root>/<id>/archive`, never a file name), and the
names of the three busiest other processes. It signals nothing.

At N seconds the launcher sends SIGTERM to its own child's process group, waits 5 s, then SIGKILL; it prints
`stopped_profile_required` and exits 124. It never signals any other process.

What it prints, and nothing else (RL-134 item 4): exit 0, `complete` and the program's one stdout line; exit 3,
`hold: comparison_stopped`; exit 4, `refused: <code> class=<A-E>` when stderr's last line has the refusal form;
exit 1, `refused: traceback`, the frame lines and the exception type without its message; exit 2,
`refused: usage`; a signal, `killed: signal N`. The record goes to DIR/record.json and one line is appended to the
attempts ledger DIR/../attempts.jsonl, for a refused launch too. DIR/analysis-tmp is removed after the exit.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import threading
import time

SCHEMA = "joulewise.b6_real_run.v1"
LEDGER_SCHEMA = "joulewise.b6_real_run.attempt.v1"
PROGRAM = "scripts/independent_recompute_b6.py"
REFUSE_LAUNCH = 9
STOPPED = 124
SAMPLE_S = 60.0
KILL_GRACE_S = 5.0
CHILD_ENV = {"PATH": "/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin", "PYTHONNOUSERSITE": "1",
             "PYTHONDONTWRITEBYTECODE": "1"}
TIME = "/usr/bin/time"

# The 24 closure files of the S-14 pin (pin request section 2a rows 1-18 and 2b rows 19-24), at the pin candidate
# analysis/2026-11-13-b6-s14-merge @ b5ab6a71d798e168209fd66a0832f66f97a0b096: rows 1, 3 and 5 as RL-133 section 3
# item 7 and RL-129 changed them (runbook section 1). If the cut commit differs, this table is regenerated at the
# cut (`git show <cut>:<path> | shasum -a 256`) before the gate run.
PIN_TABLE = {
    "scripts/independent_recompute_b6.py": "90e22603593926e5654a8e72f095b6e600b5b85009a5a76d2e7f68431fb85759",
    "scripts/independent_recompute_b5.py": "d49103e884ccae47242b8efb91ea1f5764e4505a4ad5e54558cc42a399a2e4e0",
    "joulewise/b6_analysis_check.py": "634c991c527106d32a93197dc00af113636ce30789b1080431cfa1750d056b30",
    "joulewise/b6_analysis_hazards.py": "9a907a3671dbe210df4d417428c9108f0fdee1c16531bd0bef2fd39b0f27bb2b",
    "joulewise/b6_analysis_inputs.py": "283dfc78341742768dc210b9fd46da19cc0b1f883f316db8106e3db79f89219e",
    "joulewise/twins/__init__.py": "e717dc7f4b7c3b6006f06763873a70c79d95d9ad7cb3183c21eb5251daffaeb0",
    "joulewise/twins/engine_twin.py": "5cd6977d79b2951a6e4351a9e8f95b4f91bc38af50eeb4c5bf2d5115ffedbff8",
    "joulewise/twins/harvest_twin.py": "df39036b24eab0d015c198686e3ed03ae0add341e487636d34ed622fa0695af0",
    "joulewise/flags/__init__.py": "2ea17e7b30b4101d2149be0a216c82e223b903121f50bda8f0d5665b33378ba2",
    "joulewise/flags/catalog.py": "006840601a37009d685db458186492963b15fa7cb9be05a3ae066b9e9ae82ef0",
    "joulewise/flags/exclusions.py": "ebe1678c0fdd60b1ddd20d432cf07412bd321a8629589f4ce4c6b334378f0ad6",
    "joulewise/flags/schema.py": "cd7ce3c00dec53068db4e5c6a41115e264399dbbcc741b96dc8133b67fa1fad8",
    "joulewise/desk_compress.py": "ac770c9407dad936cc742957b6f5673a1b69523156aa2be9baf7de8eb2b56777",
    "joulewise/__init__.py": "df98d6ea46fd21ec24bb8fc4c208e4e01f5167e6c7f2af36490781779d5710cc",
    "joulewise/schemas.py": "f47fbf68c2c4a931854995d1258425b476c4bc8a686dfccf011d9caef092cc3b",
    "joulewise/axi_decode_config.py": "fab53ea66a636458bb8c36f0c5f5f3f014478db8351e246746c9b6bc7c62dd93",
    "joulewise/idle_admission.py": "9dc6b5d45c1dc138a13195b64cd1ca23eac0427c864063f26e274775b5a5a79e",
    "joulewise/validation.py": "82bb03f3aed626446298d186e845b7fe75b3371ca6cbabd7160946bd8e7bfcfd",
    "configs/b6/recompute/precision.json": "e242cab6bb311a9c23d5c6dc06374ed3094a351e36d6954c3589e2b535cc63b0",
    "configs/b6/recompute/production_comparison_keys.json":
        "62dbfaef9ebc5cfbbe5a00734f5eb8ad3d82389f54f28473ed63db6135b9174d",
    "configs/b6/recompute/hazard_sizing.json": "bf399bec4195b9237f53c747c6fc9cd24066610eba933a0fad767534d970d29b",
    "configs/b6/flag_catalog_b6.json": "b5bce6c64bbc1d079ecf6fed02bf4c214b76a8f7d279d44eea5984e4a389a42b",
    "configs/b6/registration/acceptance.json": "ea130c87ece4e8b557a6357f1f75df045b5a0a738db18fe5ee990a7b539ce2a8",
    "configs/b6/registration/identity_pins.json": "513d7d4a98f464c7236b34c53f51cd523a9f45b4d9f05f2282a4a22424b4841d",
}

# RL-134 item 11: refusal code to class. A: invocation or document; B: pin closure; C: custody; D: the process;
# E: a state the pinned program does not handle (and any code not listed here).
CLASS_A = frozenset("""usage run_inputs_digest_mismatch run_host_or_audit_invalid external_input_missing
external_input_unpinned session_input_unsupplied session_input_pin_missing session_input_pin_ambiguous
authenticated_inputs_required clock_journal_required disclosure_coverage_missing disclosure_coverage_invalid
meter_streams_not_supplied input_path_invalid compression_input_path_invalid compression_relocation_ambiguous
compression_record_missing input_digest_missing input_digest_invalid input_digest_conflict""".split())
CLASS_B = frozenset("""b5_script_digest_mismatch hazard_sizing_digest_mismatch b6_catalog_digest_mismatch
print_precision_digest_mismatch comparison_key_registry_digest_mismatch registration_digest_mismatch
placeholder_print_precision""".split())
CLASS_C = frozenset("""input_digest_mismatch input_symlink input_outside_archive input_decompression_failed
external_input_digest_mismatch disclosure_record_missing meter_stream_missing request_comparison_record_missing
zstd_unavailable""".split())
CLASS_E = frozenset("""calibration_capture_missing calibration_acceptance_bound_missing neg8_idle_family_unavailable
request_comparison_member_missing comparison_session_coverage_mismatch comparison_block_coverage_mismatch
KeyError ValueError ArithmeticError OSError""".split())
# The JW_B5_SYNTHETIC_ONLY refusal is printed as a sentence; it is class A ("unset it").
SYNTHETIC_REFUSAL = "JW_B5_SYNTHETIC_ONLY=1 and the archive carries no synthetic fixture marker"
# `refused: TypeError` is class C when it comes from the clock-journal read (RL-133's unnamed signature), else E.
# The launcher cannot tell the two apart from the refusal line, so it prints both and the sampler names the session.
AMBIGUOUS = {"TypeError": "C/E"}

REFUSAL_LINE = re.compile(r"^refused: [A-Za-z0-9_ =.]+$")
STDOUT_LINE = re.compile(r"^recompute sessions=\d+ flags=\d+ comparison_stopped=(true|false) "
                         r"restricted_sha256=[0-9a-f]{64}$")
FRAME_LINE = re.compile(r'^\s*File "([^"\n]+)", line (\d+), in ([A-Za-z0-9_<>.]+)\s*$')
TYPE_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_.]*$")


class LaunchRefusal(Exception):
    pass


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def closure_hashes(checkout):
    out = {}
    for name in PIN_TABLE:
        path = Path(checkout) / name
        out[name] = sha256_file(path) if path.is_file() else None
    return out


def git(checkout, *args):
    result = subprocess.run(["git", "-C", str(checkout), *args], capture_output=True, text=True, check=False,
                            stdin=subprocess.DEVNULL)
    if result.returncode != 0:
        raise LaunchRefusal("checkout_not_a_repository")
    return result.stdout


def option_values(argv, name):
    values = []
    for i, item in enumerate(argv):
        if item == name and i + 1 < len(argv):
            values.append(argv[i + 1])
        elif item.startswith(name + "="):
            values.append(item.split("=", 1)[1])
    return values


def inside(path, directory):
    path, directory = os.path.abspath(path), os.path.abspath(directory)
    return os.path.commonpath([path, directory]) == directory and path != directory


def preflight(args, program_argv):
    """Every pre-launch condition of build B-2. Returns the closure hashes taken before launch."""
    checkout = Path(args.checkout)
    if os.environ.get("JW_B5_SYNTHETIC_ONLY") is not None:
        raise LaunchRefusal("synthetic_only_set")
    if not program_argv:
        raise LaunchRefusal("program_argv_missing")
    if git(checkout, "rev-parse", "HEAD").strip() != args.expect_commit:
        raise LaunchRefusal("checkout_commit_mismatch")
    if git(checkout, "status", "--porcelain").strip():
        raise LaunchRefusal("checkout_dirty")
    before = closure_hashes(checkout)
    if before != PIN_TABLE:
        raise LaunchRefusal("closure_hash_mismatch")
    out_dir = Path(os.path.abspath(args.out_dir))
    if os.path.lexists(out_dir):
        raise LaunchRefusal("out_dir_exists")
    parent = out_dir.parent
    if not parent.is_dir() or (parent.stat().st_mode & 0o777) != 0o700:
        raise LaunchRefusal("out_dir_parent_not_0700")
    if any(not os.path.isabs(s) for s in option_values(program_argv, "--session")):
        raise LaunchRefusal("session_path_not_absolute")
    for name in ("--restricted-out", "--public-out"):
        values = option_values(program_argv, name)
        if not values or any(not inside(v, out_dir) for v in values):
            raise LaunchRefusal("output_outside_out_dir")
    return before


def classify(code):
    if code == "usage" or code == SYNTHETIC_REFUSAL:
        return "A"
    if code in AMBIGUOUS:
        return AMBIGUOUS[code]
    for cls, codes in (("A", CLASS_A), ("B", CLASS_B), ("C", CLASS_C), ("E", CLASS_E)):
        if code in codes:
            return cls
    return "E"


def last_line(path):
    try:
        lines = [line for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines() if line.strip()]
    except OSError:
        return None
    return lines[-1] if lines else None


def traceback_summary(path):
    """Frame lines and the exception type; never the message (RL-134 item 4)."""
    try:
        lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        lines = []
    frames, last = [], -1
    for i, line in enumerate(lines):
        m = FRAME_LINE.match(line)
        if m:
            frames.append({"file": m.group(1), "line": int(m.group(2)), "function": m.group(3)})
            last = i
    # The exception line is the first unindented line after the last frame; the lines of a multi-line message
    # that follow it are never looked at.
    final = next((line for line in lines[last + 1:] if line.strip() and not line.startswith((" ", "\t"))
                  and not line.startswith("Traceback (")), "")
    kind = final.split(":", 1)[0].strip()
    if not TYPE_NAME.match(kind):
        kind = "unparsed"
    return frames, kind


def traceback_class(frames, kind):
    """RL-134 item 11: class C for the hazard-code AttributeError signature, D for a dead pool worker, else E."""
    last = frames[-1] if frames else None
    if kind == "AttributeError" and last and last["file"].endswith("b6_analysis_hazards.py") and last["line"] == 58:
        return "C"
    if kind == "RuntimeError":
        return "D"
    return "E"


def outcome(exit_code, out_dir):
    """The printed lines and the record's status, class and code, from the program's exit and its two files."""
    stdout, stderr = out_dir / "stdout", out_dir / "stderr"
    if exit_code == STOPPED:
        return ["stopped_profile_required"], {"status": "stopped_profile_required", "class": "D", "code": None}
    if exit_code is None:
        return ["refused: wrapper_record_missing class=D"], {"status": "refused", "class": "D",
                                                             "code": "wrapper_record_missing"}
    if exit_code < 0:
        return ["killed: signal " + str(-exit_code)], {"status": "killed", "class": "D", "code": "signal_" + str(-exit_code)}
    if exit_code == 0:
        line = last_line(stdout) or ""
        shown = line if STDOUT_LINE.match(line) else "stdout line not in the expected form"
        return ["complete", shown], {"status": "complete", "class": None, "code": None}
    if exit_code == 3:
        return ["hold: comparison_stopped"], {"status": "hold", "class": None, "code": "comparison_stopped"}
    if exit_code == 4:
        line = last_line(stderr) or ""
        if REFUSAL_LINE.match(line):
            code = line[len("refused: "):]
            cls = classify(code)
            return ["refused: " + code + " class=" + cls], {"status": "refused", "class": cls, "code": code}
        return ["refused: unparsed class=E"], {"status": "refused", "class": "E", "code": "unparsed"}
    if exit_code == 1:
        frames, kind = traceback_summary(stderr)
        cls = traceback_class(frames, kind)
        lines = ["refused: traceback class=" + cls]
        lines += ['  File "' + f["file"] + '", line ' + str(f["line"]) + ", in " + f["function"] for f in frames]
        lines.append(kind)
        return lines, {"status": "refused", "class": cls, "code": "traceback:" + kind, "frames": frames}
    if exit_code == 2:
        return ["refused: usage class=A"], {"status": "refused", "class": "A", "code": "usage"}
    return ["refused: exit " + str(exit_code) + " class=E"], {"status": "refused", "class": "E",
                                                              "code": "exit_" + str(exit_code)}


# ---------------------------------------------------------------- sampler

def process_table():
    result = subprocess.run(["ps", "-A", "-o", "pid=,pgid=,time=,rss=,nice=,pri=,%cpu=,comm="], capture_output=True,
                            text=True, check=False, stdin=subprocess.DEVNULL)
    rows = []
    for line in result.stdout.splitlines():
        parts = line.split(None, 7)
        if len(parts) < 8:
            continue
        try:
            rows.append({"pid": int(parts[0]), "pgid": int(parts[1]), "cpu_s": cpu_seconds(parts[2]),
                         "rss_kib": int(parts[3]), "nice": int(parts[4]), "pri": int(parts[5]),
                         "pcpu": float(parts[6]), "name": os.path.basename(parts[7].strip())})
        except ValueError:
            continue
    return rows


def cpu_seconds(text):
    days, _, rest = text.rpartition("-")
    total = 0.0
    for part in rest.split(":"):
        total = total * 60 + float(part)
    return total + (int(days) * 86400 if days else 0)


def session_roots(program_argv):
    """{archive path prefix: session id} for the `<root>/<id>/archive` spelling of every --session."""
    roots = {}
    for value in option_values(program_argv, "--session"):
        path = Path(value)
        roots[str(path).rstrip("/") + "/"] = path.parent.name if path.name == "archive" else path.name
    return roots


def open_sessions(pids, roots):
    if not pids or not roots:
        return []
    result = subprocess.run(["lsof", "-n", "-P", "-Fn", "-p", ",".join(str(p) for p in pids)], capture_output=True,
                            text=True, check=False, stdin=subprocess.DEVNULL)
    found = set()
    for line in result.stdout.splitlines():
        if line.startswith("n"):
            name = line[1:]
            for prefix, sid in roots.items():
                if name.startswith(prefix) or name == prefix.rstrip("/"):
                    found.add(sid)
    return sorted(found)


def sample(group, started, roots):
    rows = process_table()
    ours = [r for r in rows if r["pgid"] == group]
    program = max(ours, key=lambda r: r["rss_kib"], default=None)
    others = sorted((r for r in rows if r["pgid"] != group and r["pid"] != os.getpid()),
                    key=lambda r: -r["pcpu"])[:3]
    return {"elapsed_s": round(time.monotonic() - started, 1),
            "group_processes": len(ours),
            "cpu_s": sum(r["cpu_s"] for r in ours),
            "rss_kib": program["rss_kib"] if program else None,
            "nice": program["nice"] if program else None, "pri": program["pri"] if program else None,
            "open_sessions": open_sessions([r["pid"] for r in ours], roots),
            "busiest_other": [r["name"] for r in others]}


class Sampler(threading.Thread):
    def __init__(self, path, group, started, roots):
        super().__init__(daemon=True)
        self.path, self.group, self.started, self.roots = path, group, started, roots
        self.done = threading.Event()

    def run(self):
        while not self.done.wait(SAMPLE_S):
            try:
                row = sample(self.group, self.started, self.roots)
            except Exception as exc:  # the sampler never stops the run
                row = {"elapsed_s": round(time.monotonic() - self.started, 1), "sampler_error": type(exc).__name__}
            append_line(self.path, row)


# ---------------------------------------------------------------- files

def write_private(path, data):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)
    os.chmod(path, 0o600)


def append_line(path, row):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    with os.fdopen(fd, "a", encoding="utf-8") as stream:
        stream.write(json.dumps(row, sort_keys=True) + "\n")


def argv_sha256(argv):
    return hashlib.sha256(json.dumps(argv).encode("utf-8")).hexdigest()


def signal_group(group, sig):
    """The one place a signal is sent: only ever the launcher's own child's process group."""
    os.killpg(group, sig)


def ledger_row(record):
    return {"schema": LEDGER_SCHEMA, "stem": record["stem"], "time_ns": record.get("start_time_ns"),
            "argv_sha256": record.get("argv_sha256"), "exit_code": record.get("exit_code"),
            "status": record.get("status"), "class": record.get("class"), "code": record.get("code"),
            "wall_s": record.get("wall_s"), "outputs_sha256": record.get("outputs_sha256", {}),
            "record": record.get("record_path")}


def record_refusal(args, program_argv, reason):
    out_dir = Path(os.path.abspath(args.out_dir))
    now = time.time_ns()
    record = {"schema": SCHEMA, "stem": args.stem, "status": "launch_refused", "code": reason, "class": None,
              "start_time_ns": now, "argv_sha256": argv_sha256(program_argv), "exit_code": REFUSE_LAUNCH,
              "wall_s": 0.0, "outputs_sha256": {}, "record_path": None}
    if out_dir.parent.is_dir():
        append_line(out_dir.parent / "attempts.jsonl", ledger_row(record))
    print("launch refused: " + reason)
    return REFUSE_LAUNCH


# ---------------------------------------------------------------- launch

def launch(args, program_argv, before):
    checkout = Path(args.checkout).resolve()
    out_dir = Path(os.path.abspath(args.out_dir))
    os.mkdir(out_dir, 0o700)
    os.chmod(out_dir, 0o700)
    tmp = out_dir / "analysis-tmp"
    os.mkdir(tmp, 0o700)
    os.chmod(tmp, 0o700)
    child_argv = [sys.executable, "-B", str(checkout / PROGRAM), *program_argv]
    write_private(out_dir / "child-argv.json", (json.dumps({"schema": SCHEMA, "checkout": str(checkout),
                                                            "argv": child_argv}, indent=1) + "\n").encode())
    timed = [TIME, "-l", sys.executable, "-I", "-B", str(Path(__file__).resolve()), "--exec-child", str(out_dir)]
    env = {**CHILD_ENV, "TMPDIR": str(tmp)}
    start_ns, started = time.time_ns(), time.monotonic()
    fd = os.open(out_dir / "time", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as time_out:
        child = subprocess.Popen(timed, cwd=str(checkout), env=env, stdin=subprocess.DEVNULL,
                                 stdout=subprocess.DEVNULL, stderr=time_out, start_new_session=True)
        group = child.pid  # start_new_session: the child leads its own process group
        sampler = Sampler(out_dir / "samples.jsonl", group, started, session_roots(program_argv))
        sampler.start()
        stopped = False
        try:
            child.wait(timeout=args.limit_s)
        except subprocess.TimeoutExpired:
            stopped = True
            if child.poll() is None:
                signal_group(group, signal.SIGTERM)
                try:
                    child.wait(timeout=KILL_GRACE_S)
                except subprocess.TimeoutExpired:
                    if child.poll() is None:
                        signal_group(group, signal.SIGKILL)
                    child.wait()
        sampler.done.set()
        sampler.join(timeout=10)
    end_ns, wall = time.time_ns(), time.monotonic() - started
    wrapper_exit = child.returncode
    try:
        process = json.loads((out_dir / "process.json").read_text())
    except (OSError, ValueError):
        process = {}
    if stopped:
        exit_code = STOPPED
    elif "exit_code" in process:
        exit_code = process["exit_code"]
    elif wrapper_exit is not None and wrapper_exit < 0:
        exit_code = wrapper_exit
    else:
        exit_code = None
    shutil.rmtree(tmp, ignore_errors=True)
    lines, result = outcome(exit_code, out_dir)
    outputs = {}
    for label, path in (("stdout", out_dir / "stdout"), ("stderr", out_dir / "stderr")):
        if path.is_file():
            outputs[label] = sha256_file(path)
    for label, option in (("restricted", "--restricted-out"), ("public", "--public-out")):
        values = option_values(program_argv, option)
        if values and Path(values[-1]).is_file():
            os.chmod(values[-1], 0o600)
            outputs[label] = sha256_file(values[-1])
    after = closure_hashes(checkout)
    record = {"schema": SCHEMA, "stem": args.stem, "commit": args.expect_commit, "checkout": str(checkout),
              "closure_before": before, "closure_after": after, "closure_unchanged": before == after == PIN_TABLE,
              "argv": child_argv, "argv_sha256": argv_sha256(child_argv), "timed_argv": timed,
              "start_time_ns": start_ns, "end_time_ns": end_ns, "wall_s": round(wall, 3), "limit_s": args.limit_s,
              "exit_code": exit_code, "time_wrapper_exit": wrapper_exit,
              "peak_rss": process.get("peak_rss"), "peak_rss_units": process.get("peak_rss_units"),
              "python": sys.version.split()[0], "outputs_sha256": outputs,
              "record_path": str(out_dir / "record.json"), **{k: v for k, v in result.items() if k != "frames"},
              "frames": result.get("frames", [])}
    write_private(out_dir / "record.json", (json.dumps(record, indent=1, sort_keys=True) + "\n").encode())
    append_line(out_dir.parent / "attempts.jsonl", ledger_row(record))
    for line in lines:
        print(line)
    if exit_code is None:
        return 1
    return exit_code if exit_code >= 0 else 128 - exit_code


def exec_child(out_dir):
    """Run under /usr/bin/time -l: the program's exit code and peak RSS survive a failing time wrapper."""
    import resource
    out_dir = Path(out_dir)
    document = json.loads((out_dir / "child-argv.json").read_text())
    argv, checkout = document["argv"], Path(document["checkout"])
    if not (len(argv) > 2 and argv[:2] == [sys.executable, "-B"] and Path(argv[2]) == checkout / PROGRAM):
        raise SystemExit("only the declared pinned program may be launched")
    os.umask(0o077)  # the program's outputs and temporary files are created 0600 / 0700
    out = os.open(out_dir / "stdout", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    err = os.open(out_dir / "stderr", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        result = subprocess.run(argv, cwd=str(checkout), stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                                check=False)
    finally:
        os.close(out)
        os.close(err)
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    receipt = {"exit_code": result.returncode, "peak_rss": usage.ru_maxrss,
               "peak_rss_units": "bytes" if sys.platform == "darwin" else "KiB",
               "user_s": usage.ru_utime, "system_s": usage.ru_stime}
    write_private(out_dir / "process.json", (json.dumps(receipt, indent=1, sort_keys=True) + "\n").encode())
    return 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) == 2 and argv[0] == "--exec-child":
        return exec_child(argv[1])
    if "--" in argv:
        split = argv.index("--")
        own, program_argv = argv[:split], argv[split + 1:]
    else:
        own, program_argv = argv, []
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--checkout", required=True, help="the clean detached run checkout at the S-14 commit")
    parser.add_argument("--expect-commit", required=True, help="the S-14 commit, 40 hex")
    parser.add_argument("--stem", required=True, help="the attempt's name in the ledger (gate, dry, ...)")
    parser.add_argument("--limit-s", required=True, type=float, help="stop at this many seconds (exit 124)")
    parser.add_argument("--out-dir", required=True, help="new directory, inside a mode-700 parent")
    args = parser.parse_args(own)
    try:
        before = preflight(args, program_argv)
    except LaunchRefusal as exc:
        return record_refusal(args, program_argv, str(exc))
    return launch(args, program_argv, before)


if __name__ == "__main__":
    raise SystemExit(main())
