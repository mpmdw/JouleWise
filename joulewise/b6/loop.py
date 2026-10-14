"""One locked, atomic tick. Each method below is one transition-table row."""
from __future__ import annotations

import fcntl
import json
import os
import time
from dataclasses import asdict, replace
from pathlib import Path

from joulewise.b6 import compose, queue
from joulewise.b6.lanes import Done, LaneMissing, Prepared, Running, SessionLine, Waker, resolve
from joulewise.b6.mailer import Mailer
from joulewise.b6.registration import Registration, open_packs
from joulewise.flags.catalog import load_catalog

DEFAULT_LOOP_ROOT = "/Users/edr/night-b6/loop"
STOP_REF_GLOB = "refs/heads/ops/stop*"
COLLECTING = {"SMOKE_RUN", "SESSION_RUN"}


def atomic_state(path, state):
    temp = path.with_suffix(".tmp")
    with temp.open("w") as stream:
        json.dump({k: v for k, v in state.items() if k != "attempts"}, stream, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    temp.replace(path)


class Loop:
    def __init__(self, repo_root, loop_root=DEFAULT_LOOP_ROOT, *, config=None, regs=None,
                 lanes=None, mailer=None, waker=None, clock=time.time, run=None, catalog=None):
        self.repo, self.root = Path(repo_root), Path(loop_root)
        self.config = config or json.loads((self.repo / "configs/b6/loop.json").read_text())
        self.regs_source, self.clock, self.run = regs, clock, run
        self.lanes = lanes or resolve()
        self.catalog = catalog or load_catalog(self.repo / self.config["flag_catalog"])
        self.mailer = mailer or Mailer(self.root, self.catalog, clock=clock)
        self.waker = waker or Waker(self.root, wake_argv=self.config.get("wake_argv", []), run=run)
        self.state = None
        self.regs = {}

    def read_state(self):
        path = self.root / "state.json"
        state = json.loads(path.read_text()) if path.exists() else {
            "state": "NEXT", "session": None, "since": self.clock(), "packs": {}, "round": 1, "wait": None,
            "slots": {}, "base_order": self.config["base_order"],
            "science_minutes_max": self.config.get("science_minutes_max", 265)}
        attempts = self.root / "attempts.jsonl"
        state["attempts"] = [json.loads(line) for line in attempts.read_text().splitlines() if line] if attempts.exists() else []
        return state

    def _lock(self):
        self.root.mkdir(parents=True, exist_ok=True)
        stream = (self.root / "loop.lock").open("a")
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            stream.close()
            return None
        return stream

    def _registrations(self):
        if self.regs_source is not None:
            self.regs = dict(self.regs_source)
        elif self.run is not None:
            def rejected(path, reasons):
                self.state.setdefault("pack_not_open", {})[path] = reasons
            self.regs = {r.pack_id: r for r in open_packs(self.repo, run=self.run, rejected=rejected)}
        else:
            self.regs = {}
            self.state["pack_not_open"] = {"runner": ["registration_runner_missing"]}
        session = self.state.get("session")
        if session and self.state["state"] not in {"NEXT", "DONE"}:
            for p, r in session["registrations"].items():
                self.regs[p] = Registration(r["data"], commit_time=r["commit_time"])
        for p in self.regs:
            self.state["packs"].setdefault(p, {"status": "open", "last_smoke_fingerprint": None,
                                              "attempts_since_resume": 0, "hold_reason": None})

    def tick(self):
        lock = self._lock()
        if lock is None:
            return 0
        with lock:
            self.state = self.read_state()
            self._registrations()
            state = self.state["state"]
            if state not in {"HOLD_LOOP", "DONE"}:
                getattr(self, "_" + state.lower())()
            atomic_state(self.root / "state.json", self.state)
            # Never flush in the tick that still has a collection active.
            self.mailer.flush(state=self.state["state"])
        return 0

    def _transition(self, state):
        if self.state["state"] != state:
            self.state.update(state=state, since=self.clock())

    def _event(self, kind, cause=None, packs=None, *, wake=True, fields=None):
        if self.state["state"] in COLLECTING or ((self.root / "collection.active").exists() and kind != "overrun"):
            raise RuntimeError("notification during collection")
        session = self.state.get("session") or {}
        identity = session.get("id") or ",".join(packs or []) or "loop"
        ctx = {"session_id": session.get("id"), "packs": list(packs or session.get("packs", [])), "cause": cause}
        self.mailer.enqueue(kind, identity, cause, {"state": self.state["state"], **ctx, **(fields or {})})
        if wake:
            self.waker.wake(kind, ctx)

    def _missing(self, result):
        if not isinstance(result, LaneMissing):
            return False
        # Missing status cannot establish that a running collection has ended.
        # Hold without waking or mailing until the terminal path exists.
        active = self.root / "collection.active"
        self.state["hold_reason"] = "lane_missing:" + result.name
        self._transition("HOLD_LOOP")
        if not active.exists():
            self._event("lane_missing", result.name)
        return True

    def _layout(self):
        s = self.state["session"]
        return compose.layout(queue.Selection(tuple(s["packs"]), s["round"]), self.regs, self.repo)

    def _prepared(self, smoke=False):
        return Prepared(**self.state["session"]["smoke_prepared" if smoke else "prepared"])

    def _next(self):
        selection = queue.next_session(self.state, self.regs, self.clock())
        if isinstance(selection, queue.Close):
            self.state["session"] = None
            self._transition("DONE")
            self._event("close", fields={"counts": selection.counts, "short": selection.short})
            return
        if isinstance(selection, queue.Idle):
            self.state["idle_reasons"] = selection.reasons
            return
        self.state.pop("idle_reasons", None)
        layout = compose.layout(selection, self.regs, self.repo)
        self.state["session"] = {"id": layout.session_id, "packs": list(selection.packs), "round": selection.round,
                                 "registrations": {p: {"data": dict(self.regs[p].data), "commit_time": self.regs[p].commit_time}
                                                   for p in selection.packs}}
        if any(self.regs[p].data.get("interleave") == "quad_round_robin" for p in selection.packs):
            capability = self.lanes.harvest.capabilities()
            if self._missing(capability):
                return
            if not capability.block_id_strata:
                self.state["hold_reason"] = "interleave_unconfirmed:H3"
                self._transition("HOLD_LOOP")
                self._event("loop_hold", "interleave_unconfirmed:H3")
                return
        prepared = self.lanes.driver.prepare_session(layout, compose.render(layout), smoke=False, keep={},
                                                     staging_root=self.root / "staging" / layout.session_id)
        if self._missing(prepared):
            return
        self.state["session"]["prepared"] = asdict(prepared)
        self._transition("PRECHECK")

    def _wait_for(self, result, return_state):
        hazard = result.would_refuse[0].hazard
        episode = self.state.get("wait")
        if episode is None or episode["hazard"] != hazard:
            episode = {"hazard": hazard, "since": self.clock(), "remedied": False, "mailed": False,
                       "last_check": self.clock(), "return_state": return_state}
        episode["last_check"] = self.clock()
        self.state["wait"] = episode
        self._transition("WAIT_PHYSICS")
        if hazard in result.remedies and not episode["remedied"]:
            episode["remedied"] = True
            remedy = self.lanes.precheck.remedy(hazard)
            self._missing(remedy)
        if self.clock() - episode["since"] >= 7200 and not episode["mailed"]:
            episode["mailed"] = True
            self._event("physics_wait_2h", hazard, wake=False)

    def _hold_packs(self, kind, codes, packs):
        code_set = sorted(set(codes))
        previous = self.state.get("last_" + kind)
        repeated = previous and previous["codes"] == code_set and set(previous["packs"]) != set(packs)
        self.state["last_" + kind] = {"codes": code_set, "packs": list(packs)}
        for p in packs:
            self.state["packs"][p].update(status="held", hold_reason=kind + ":" + ",".join(code_set))
        self._transition("HOLD_LOOP" if repeated else "NEXT")
        self._event(kind, ",".join(code_set), packs)

    def _precheck(self):
        layout = self._layout()
        result = self.lanes.precheck.run(layout, self._prepared().plan_path)
        if self._missing(result):
            return
        if result.would_refuse:
            self._wait_for(result, "PRECHECK")
            return
        if result.certain_exclusion:
            packs = set()
            for x in result.certain_exclusion:
                packs.update([x.pack_id] if x.pack_id else self.state["session"]["packs"])
            self._hold_packs("certain_exclusion", [x.code for x in result.certain_exclusion], sorted(packs))
            return
        self.state["last_certain_exclusion"] = None
        self.state["wait"] = None
        if self._stop():
            self._owner_hold()
            return
        session = self.state["session"]
        session["fingerprint"] = result.fingerprint
        smoke = self.state.get("harvest_fault", False) or any(
            self.state["packs"][p]["last_smoke_fingerprint"] != result.fingerprint for p in session["packs"])
        session["needs_smoke"] = smoke
        session["notice_sent"] = self.clock()
        session["notice_key"] = self.mailer.enqueue("arm_notice", session["id"], None, {
            "state": "ARM_WAIT", "session_id": session["id"], "packs": session["packs"], "round": session["round"],
            "t0_not_before": self.clock() + 1800, "smoke": smoke, "thin_margin": result.thin_margin,
            "predicted_flags": result.predicted_flags, "previous": self.state.get("previous")})
        # Deliver before entering a collection state, so the NO window runs during smoke.
        self.mailer.flush(state="PRECHECK")
        self._transition("SMOKE_RUN" if smoke else "ARM_WAIT")

    def _wait_physics(self):
        episode = self.state["wait"]
        if self.clock() - episode["last_check"] < 300:
            return
        result = self.lanes.precheck.run(self._layout(), self._prepared().plan_path)
        if self._missing(result):
            return
        if result.would_refuse:
            self._wait_for(result, episode["return_state"])
        elif result.certain_exclusion:
            packs = set()
            for x in result.certain_exclusion:
                packs.update([x.pack_id] if x.pack_id else self.state["session"]["packs"])
            self._hold_packs("certain_exclusion", [x.code for x in result.certain_exclusion], sorted(packs))
        else:
            self.state["wait"] = None
            self._transition(episode["return_state"])

    def _active(self, prepared):
        path = self.root / "collection.active"
        if not path.exists():
            path.write_text(f"{prepared.terminal_path}\n{prepared.max_s + 3600}\n")

    def _run_collection(self, smoke):
        session = self.state["session"]
        prefix = "smoke_" if smoke else ""
        if smoke and "smoke_prepared" not in session:
            layout = self._layout()
            layout = replace(layout, session_id=layout.session_id + f"-smoke-{session.get('smoke_attempt', 0)}")
            prepared = self.lanes.driver.prepare_session(layout, compose.render(layout), smoke=True,
                keep=compose.smoke_keep(layout), staging_root=self.root / "staging" / (session["id"] + "-smoke"))
            if self._missing(prepared):
                return
            session["smoke_prepared"] = asdict(prepared)
        prepared = self._prepared(smoke)
        # Publish the start intent before launch; retry uses the same Prepared.
        if prefix + "started" not in session:
            session[prefix + "started"] = self.clock()
            if not smoke:
                self.state = queue.consume(self.state, queue.Selection(tuple(session["packs"]), session["round"]))
                session = self.state["session"]
                session["t0"] = self.clock()
                session["notice_undelivered"] = not self.mailer.entry(session["notice_key"])["delivered"]
                self.mailer.close_notice(session["notice_key"])
            atomic_state(self.root / "state.json", self.state)
        self._active(prepared)
        handle = session.get(prefix + "handle")
        result = self.lanes.driver.status(Running(handle)) if handle else self.lanes.driver.launch(prepared)
        if isinstance(result, LaneMissing):
            # A failed launch stub has started nothing; remove the active marker.
            if handle is None:
                (self.root / "collection.active").unlink(missing_ok=True)
                if not smoke and not session.get("launch_confirmed"):
                    for p in session["packs"]:
                        self.state["slots"][str(session["round"])].remove(p)
                        self.state["packs"][p]["attempts_since_resume"] -= 1
            self._missing(result)
            return
        session["launch_confirmed" if not smoke else "smoke_launch_confirmed"] = True
        if isinstance(result, Running):
            session[prefix + "handle"] = result.handle
            if self.clock() - session[prefix + "started"] > prepared.max_s + 3600 and not Path(prepared.terminal_path).exists():
                # Notify only after leaving the polling state. No process is killed.
                session["overrun"] = True
                self.state["hold_reason"] = "overrun"
                self._transition("HOLD_LOOP")
                # The marker remains: external wake/mail waits for a terminal record.
                self.state["deferred_overrun"] = True
                self._event("overrun", "overrun")
            return
        session[prefix + "done"] = asdict(result)
        (self.root / "collection.active").unlink(missing_ok=True)
        self._transition("SMOKE_DESK" if smoke else "SESSION_DESK")

    def _smoke_run(self):
        self._run_collection(True)

    def _smoke_desk(self):
        s = self.state["session"]
        result = self.lanes.desk.evaluate_smoke(self._prepared(True), Done(**s["smoke_done"]))
        if self._missing(result):
            return
        if result.status == "pass":
            for p in s["packs"]:
                self.state["packs"][p]["last_smoke_fingerprint"] = s["fingerprint"]
            self.state["harvest_fault"] = False
            self.state["last_smoke_hold"] = None
            self._transition("ARM_WAIT")
        elif result.status == "physics":
            # A new smoke gets its own idempotency key after a physics stop.
            s["smoke_attempt"] = s.get("smoke_attempt", 0) + 1
            for key in ("smoke_prepared", "smoke_handle", "smoke_started", "smoke_done"):
                s.pop(key, None)
            self.state["wait"] = {"hazard": result.codes[0] if result.codes else "smoke_physics", "since": self.clock(),
                                  "remedied": False, "mailed": False, "last_check": self.clock(), "return_state": "SMOKE_RUN"}
            self._transition("WAIT_PHYSICS")
        else:
            self._hold_packs("smoke_hold", result.codes, s["packs"])

    def _stop(self):
        if (self.root / "STOP").exists():
            return True
        if self.run is None:
            self.state["stop_probe_unavailable"] = True
            return False
        try:
            result = self.run(["git", "-C", str(self.repo), "ls-remote", "origin", STOP_REF_GLOB])
            self.state["stop_probe_unavailable"] = result.returncode != 0
            return result.returncode == 0 and bool(result.stdout.strip())
        except Exception:
            self.state["stop_probe_unavailable"] = True
            return False

    def _owner_hold(self):
        self.state["hold_reason"] = "owner_no"
        self._transition("HOLD_LOOP")
        self._event("owner_no_ack", "owner_no", wake=False)

    def _arm_wait(self):
        s = self.state["session"]
        if self.clock() < s["notice_sent"] + 1800:
            return
        if self._stop() or self.mailer.has_no(s["notice_key"], self.config["owner_login"]):
            self._owner_hold()
        else:
            self._transition("SESSION_RUN")

    def _session_run(self):
        self._run_collection(False)

    def _append_attempt(self, line):
        s = self.state["session"]
        existing = next((a for a in self.state["attempts"] if a["session_id"] == s["id"]), None)
        if existing is not None:
            line = SessionLine(**existing["line"])
            self._previous(line, existing["outcomes"])
            return line
        flags = list(line.window_flags)
        for p in s["packs"]:
            first = next((a["t0"] for a in self.state["attempts"] if p in a["packs"]), s["t0"])
            if self.regs[p].commit_time >= first:
                flags.append("registration.after_first_session")
        if s["notice_undelivered"]:
            flags.append("notice.undelivered")
        line = replace(line, window_flags=tuple(sorted(set(flags))))
        outcomes = {p: queue.outcome(self.regs[p], line, self.catalog) for p in s["packs"]}
        record = {"session_id": s["id"], "round": s["round"], "packs": s["packs"], "t0": s["t0"],
                  "outcomes": outcomes, "structure_ok": line.structure_ok,
                  "registration_commit_times": {p: self.regs[p].commit_time for p in s["packs"]}, "line": asdict(line)}
        if not any(a["session_id"] == s["id"] for a in self.state["attempts"]):
            with (self.root / "attempts.jsonl").open("a") as stream:
                stream.write(json.dumps(record) + "\n")
                stream.flush()
                os.fsync(stream.fileno())
            self.state["attempts"].append(record)
        self._previous(line, outcomes)
        return line

    def _previous(self, line, outcomes):
        self.state["previous"] = {"verdict": line.verdict, "counting": {p: o["status"] == "counting" for p, o in outcomes.items()},
                                   "flags": list(line.window_flags) + [c for codes in line.pack_flags.values() for c in codes],
                                   "minutes": line.minutes}

    def _precision(self, packs):
        for p in packs:
            r = self.regs[p]
            ids = queue.counting_ids(self.state, p)
            if r.stopping.get("precision") is not None and len(ids) >= r.minimum_sessions:
                result = self.lanes.analysis.precision_reached(p, r, ids)
                if self._missing(result):
                    return False
                self.state["packs"][p]["precision_reached"] = result is True
        return True

    def _session_desk(self):
        s = self.state["session"]
        line = self.lanes.desk.session_desk(self._prepared(), Done(**s["done"]))
        if self._missing(line):
            return
        line = self._append_attempt(line)
        if not line.structure_ok:
            self.state["hold_reason"] = "structure_defect"
            self._transition("HOLD_LOOP")
            self._event("structure_defect", fields={"flags": line.window_flags})
            return
        self._transition("ROTATE")
        if line.harvest_rc in (2, 3):
            self.state["harvest_fault"] = True
            self.state.setdefault("pending_sessions", {})[s["id"]] = s
            self._event("harvest_fault")
        if line.physics_stop:
            self._event("physics_ended_session", line.physics_stop, wake=False)
        self._precision([p for p in s["packs"] if queue.counting_ids(self.state, p)[-1:] == [s["id"]]])

    def _rotate(self):
        self.state, events = queue.rotate(self.state, self.regs)
        self._transition("NEXT")
        for kind, pack in events:
            self._event(kind, packs=[pack])
        self.state["session"] = None

    def control(self, command, *, pack=None, attempts=5, session_id=None):
        lock = self._lock()
        if lock is None:
            return 0
        with lock:
            self.state = self.read_state()
            self._registrations()
            if command == "resume":
                active = self.root / "collection.active"
                recovering = None
                if active.exists():
                    terminal = active.read_text().splitlines()[0]
                    if not Path(terminal).exists():
                        raise ValueError("collection active; wait for its terminal record")
                    active.unlink()
                    recovering = "SMOKE_RUN" if "smoke_handle" in (self.state.get("session") or {}) and "handle" not in self.state["session"] else "SESSION_RUN"
                if pack is not None and pack not in self.state["packs"]:
                    raise ValueError("unknown pack")
                self.state = queue.resume(self.state, pack, attempts)
                if self.state["state"] == "HOLD_LOOP":
                    self.state["wait"] = None
                    if recovering:
                        self._transition(recovering)
                    else:
                        self.state["session"] = None
                        self._transition("NEXT")
                self.state["hold_reason"] = None
            elif command == "hold":
                if pack:
                    self.state["packs"][pack].update(status="held", hold_reason="manual")
                else:
                    self.state["hold_reason"] = "manual"
                    self._transition("HOLD_LOOP")
                if not (self.root / "collection.active").exists():
                    self._event("loop_hold", "manual", [pack] if pack else None, wake=False)
            elif command == "reharvested":
                if (self.root / "collection.active").exists():
                    raise ValueError("collection active; defer reharvest desk work")
                pending = self.state.get("pending_sessions", {}).get(session_id)
                if pending is None:
                    raise ValueError("session is not pending harvest")
                line = self.lanes.desk.session_desk(Prepared(**pending["prepared"]), Done(**pending["done"]))
                if self._missing(line):
                    atomic_state(self.root / "state.json", self.state)
                    return 0
                if not line.structure_ok or line.harvest_rc in (2, 3):
                    raise ValueError("reharvest is not structurally complete")
                regs = {p: Registration(r["data"], commit_time=r["commit_time"]) for p, r in pending["registrations"].items()}
                self.state.setdefault("reharvested", {})[session_id] = {p: queue.outcome(r, line, self.catalog) for p, r in regs.items()}
                del self.state["pending_sessions"][session_id]
                self.regs.update(regs)
                self._precision([p for p in regs if session_id in queue.counting_ids(self.state, p)])
            atomic_state(self.root / "state.json", self.state)
        return 0
