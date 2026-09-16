#!/usr/bin/env python3.11
"""LIVE launchctl smoke for joulewise/night_agent_install.py, throwaway labels only.

Drives the REAL LaunchctlAdapter (real launchctl, real gui/<uid> domain) through one full
install transaction then one uninstall, with labels com.joulewise.smoke.* and a plist dir
under this session's scratchpad; never touches ~/Library/LaunchAgents, ~/night-custody,
~/JouleWise-measurement-*, or the canonical checkout. Exit 0 only when install rc 0, both
labels LOADED (rc 0), uninstall rc 0, both ABSENT by the exact wire signature (rc 113 +
"Could not find service" line), and both plists + .prior sidecars gone. Exit 14 whenever
a smoke label is still loaded at the end. --cleanup recovers a run that died mid-way.
"""
import argparse, hashlib, json, os, platform, plistlib, shutil, subprocess, sys, time
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

SCRATCH = Path(__file__).resolve().parent                 # .../scratchpad/smoke
ROOT = SCRATCH / "live"                                   # the ONLY tree this smoke writes
LAUNCH_DIR, CUSTODY = ROOT / "LaunchAgents", ROOT / "custody"
ENGINE_REPO = Path("/Users/edr/code/JouleWise-wt-iw-txn")  # read-only: engine + template
LABELS = ("com.joulewise.smoke.night", "com.joulewise.smoke.night.deadman")
FORBIDDEN = (Path.home() / "Library/LaunchAgents", Path("/Users/edr/night-custody"),
             Path("/Users/edr/code/JouleWise"))
UID = os.getuid()
ABSENT_LINE = 'Could not find service "{}" in domain for user gui: {}'  # engine D2 signature
REAL_RUN = subprocess.run
LAUNCHCTL = shutil.which("launchctl") or "/bin/launchctl"

class Fail(Exception):
    def __init__(self, code, message):
        super().__init__(message); self.code = code

def say(line=""): print(line, flush=True)

def guard():
    if sys.version_info < (3, 11):
        raise Fail(2, "python 3.11+ required")
    if "scratchpad" not in ROOT.parts or any(ROOT.is_relative_to(f) for f in FORBIDDEN) \
            or any(p.startswith("JouleWise-measurement-") for p in ROOT.parts):
        raise Fail(2, "refusing: smoke root is not under the session scratchpad: {}".format(ROOT))

def logged_run(argv, *args, **kwargs):
    """Replaces subprocess.run while the engine runs: prints every launchctl call raw."""
    try:
        result = REAL_RUN(argv, *args, **kwargs)
    except subprocess.TimeoutExpired:
        say("launchctl argv={} TIMEOUT".format(json.dumps(list(argv))))
        raise
    say("launchctl argv={} rc={}".format(json.dumps(list(argv)), result.returncode))
    say("  stdout={!r}\n  stderr={!r}".format(result.stdout, result.stderr))
    return result

def raw_print(phase, label):
    """Independent evidence query, outside the adapter: raw rc/stdout/stderr, verbatim."""
    r = REAL_RUN([LAUNCHCTL, "print", "gui/{}/{}".format(UID, label)],
                 capture_output=True, text=True, timeout=10)
    say("EVIDENCE {} label={} rc={}".format(phase, label, r.returncode))
    for stream, text in (("stdout", r.stdout), ("stderr", r.stderr)):
        for line in text.splitlines(): say("  {}| {}".format(stream, line))
    return r

def absent(r, label):
    return r.returncode == 113 and ABSENT_LINE.format(label, UID) in r.stderr.splitlines()

def header(engine):
    src = Path(engine.__file__)
    build = REAL_RUN(["sw_vers", "-buildVersion"], capture_output=True, text=True).stdout.strip()
    say("smoke start {} macOS={} build={} kernel={} python={} uid={} launchctl={}".format(
        datetime.now().astimezone().isoformat(), platform.mac_ver()[0], build,
        os.uname().release, sys.version.split()[0], UID, LAUNCHCTL))
    say("engine={} sha256={}".format(src, hashlib.sha256(src.read_bytes()).hexdigest()))
    say("launch_dir={} custody={} labels={}".format(LAUNCH_DIR, CUSTODY, LABELS))

def build(engine):
    """Throwaway plan + Prepared, the fixture way (validate_install is bypassed on purpose)."""
    now = time.time()
    t0 = (int(now) // 60 + 1) * 60 + 3 * 3600            # now + 3 h, minute-aligned
    deadman = t0 + 3600
    plan = {"plan_id": "smoke-{}".format(int(now)), "receipt_class": "REHEARSAL_STUB",
            "t0_epoch_s": t0, "window_max_s": 600, "authored_epoch_s": now,
            "repo_head": "0" * 40, "measurement_root": str(ROOT / "measurement"),
            "measurement_head": "0" * 40, "chain_path": str(ROOT / "chain.sh"),
            "chain_sha256_path": str(ROOT / "chain.sh.sha256"), "custody_root": str(CUSTODY),
            "registration_path": None}
    CUSTODY.mkdir(parents=True)
    plan_path = (CUSTODY / "night_plan.json").resolve()   # admit(): must equal custody/night_plan.json
    plan_path.write_text(json.dumps(plan, indent=1))

    def cal(epoch):
        d = datetime.fromtimestamp(epoch)
        return {"Month": d.month, "Day": d.day, "Hour": d.hour, "Minute": d.minute}
    schedule = {"t0_epoch_s": t0, "install_close_epoch_s": t0 - 85 * 60,  # t0 - PLAN_LEAD - MARGIN
                "deadman_epoch_s": deadman, "night_calendar": cal(t0),
                "deadman_calendar": {k: v for k, v in cal(deadman).items() if k in ("Hour", "Minute")}}
    template = (ENGINE_REPO / "configs/launchd/com.joulewise.night.plist.template").read_text()
    prepared = engine.Prepared(SimpleNamespace(**plan), plan_path, ROOT, "/usr/bin/true", template,
                               "/usr/bin/true", "/usr/bin:/bin", schedule,
                               lambda day: [(now - 60, schedule["install_close_epoch_s"])])
    for label, payload in prepared.render(LABELS):        # harmlessness gate, before any launchctl
        p = plistlib.loads(payload)
        if (p["Label"] != label or p["ProgramArguments"][0] != "/usr/bin/true" or p.get("RunAtLoad")
                or "KeepAlive" in p or not p.get("StartCalendarInterval")):
            raise Fail(2, "rendered plist is not harmless: " + label)
        say("render {}: ProgramArguments={} StartCalendarInterval={}".format(
            label, p["ProgramArguments"], p["StartCalendarInterval"]))
    say("schedule: t0={} ({}) install_close={} deadman={}".format(
        t0, datetime.fromtimestamp(t0).astimezone().isoformat(), schedule["install_close_epoch_s"], deadman))
    target = engine.Target.for_mode(LAUNCH_DIR, labels=LABELS)
    return engine.LaunchctlAdapter(target, LAUNCHCTL), prepared

def transact(engine, adapter, prepared):
    # ADJUST ONLY HERE if the seat's rewrite changes the Transaction/Shield constructor.
    shield = engine.Shield()
    machine = engine.Transaction(adapter, lambda: prepared, clock=time.time, shield=shield)
    trace, enter = [], machine._enter
    machine._enter = lambda state: (enter(state), trace.append(state.name))
    try: rc = machine.run()
    finally: shield.release()   # run() quiesced INT/TERM/HUP; give the smoke its Ctrl-C back
    trace.append(machine.state.name + "(final)")
    say("engine state trace: " + " -> ".join(trace))
    say("engine install rc={} adapter_calls={}".format(rc, len(adapter.outcomes)))
    return rc

def unload(engine, adapter):
    shield = engine.Shield()
    try: rc = engine.uninstall(adapter, shield=shield)
    finally: shield.release()
    say("engine uninstall rc={} adapter_calls_total={}".format(rc, len(adapter.outcomes)))
    return rc

def run_mode(engine):
    if ROOT.exists():
        raise Fail(2, "{} exists (previous run?): run --cleanup first".format(ROOT))
    ROOT.mkdir(parents=True)
    header(engine)
    for label in LABELS:
        if not absent(raw_print("baseline", label), label):
            raise Fail(14, "smoke label not ABSENT at baseline; run --cleanup")
    adapter, prepared = build(engine)
    subprocess.run = logged_run
    try:
        if (rc := transact(engine, adapter, prepared)) != 0:
            raise Fail(10, "install transaction rc={}".format(rc))
        for label in LABELS:
            if raw_print("loaded", label).returncode != 0:
                raise Fail(11, "{} not LOADED (rc 0) after install".format(label))
            if not adapter.target.path(label).is_file() or adapter.target.sidecar(label).exists():
                raise Fail(11, "plist missing or .prior present after install: " + label)
        if (rc := unload(engine, adapter)) != 0:
            raise Fail(12, "uninstall rc={}".format(rc))
        for label in LABELS:
            if not absent(raw_print("absent", label), label):
                raise Fail(13, "{} not ABSENT by wire signature after uninstall".format(label))
            for path in (adapter.target.path(label), adapter.target.sidecar(label)):
                if path.exists():
                    raise Fail(13, "file remains after uninstall: {}".format(path))
    finally:
        subprocess.run = REAL_RUN

def cleanup():
    for label in LABELS:
        r = REAL_RUN([LAUNCHCTL, "bootout", "gui/{}/{}".format(UID, label)],
                     capture_output=True, text=True, timeout=10)
        say("cleanup bootout {} rc={} stderr={!r}".format(label, r.returncode, r.stderr))
    for label in LABELS:
        if not absent(raw_print("cleanup", label), label):
            raise Fail(14, "{} still not ABSENT after bootout; files kept".format(label))
    if ROOT.exists():
        shutil.rmtree(ROOT)
        say("cleanup removed {}".format(ROOT))

def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--cleanup", action="store_true", help="boot out both smoke labels, delete the throwaway tree")
    args = parser.parse_args()
    code, message = 0, "PASS"
    try:
        guard()
        sys.path.insert(0, str(ENGINE_REPO))
        from joulewise import night_agent_install as engine
        cleanup() if args.cleanup else run_mode(engine)
    except Fail as exc:
        code, message = exc.code, str(exc)
    except Exception as exc:
        code, message = 1, "{}: {}".format(type(exc).__name__, exc)
    finally:
        try:
            still = [label for label in LABELS if raw_print("final", label).returncode == 0]
        except Exception as exc:
            still, message = list(LABELS), "final liveness query failed ({}); ".format(exc) + message
        if still:
            code, message = 14, "THROWAWAY LABEL(S) STILL LOADED: {}; run --cleanup; {}".format(" ".join(still), message)
        say("SMOKE VERDICT exit={}: {}".format(code, message))
    return code


if __name__ == "__main__":
    sys.exit(main())
