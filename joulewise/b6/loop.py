"""One locked, atomic tick. Each method below is one transition-table row."""
from __future__ import annotations

import fcntl
import json
import math
import os
import time
from dataclasses import asdict, replace
from pathlib import Path

from joulewise.b6 import compose, queue
from joulewise.b6.lanes import (Done, LaneMissing, Prepared, Refused, Running, SessionLine, Waker, collection_live,
                                resolve)
from joulewise.b6.mailer import Mailer
from joulewise.b6.pack_registration import Registration, open_packs
from joulewise.flags.catalog import load_catalog

DEFAULT_LOOP_ROOT = "/Users/edr/night-b6/loop"
STOP_REF_GLOB = "refs/heads/ops/stop*"
COLLECTING = {"SMOKE_RUN", "SESSION_RUN"}
LOOP_WINDOW_FLAGS = frozenset({"registration.after_first_session", "notice.undelivered", "notice.no_unreadable"})


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
        self.lanes = lanes or resolve(self.repo, self.root, run=run, config=self.config, clock=clock)
        self.catalog = catalog or load_catalog(self.repo / self.config["flag_catalog"])
        self.mailer = mailer or Mailer(self.root, self.catalog, clock=clock)
        wake_argv = [arg.replace("{repo_root}", str(self.repo.resolve())).replace("{loop_root}", str(self.root.resolve()))
                     for arg in self.config.get("wake_argv", [])]
        self.waker = waker or Waker(self.root, wake_argv=wake_argv, run=run)
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
            state = self.state["state"]
            try:
                self._registrations()
                if state not in {"HOLD_LOOP", "DONE"}:
                    getattr(self, "_" + state.lower())()
            except Exception as exc:
                session = self.state.get("session") or {}
                prefix = "smoke_" if state == "SMOKE_RUN" else ""
                if state in COLLECTING and not session.get(prefix + "handle") and not session.get(prefix + "launch_confirmed"):
                    self._rollback_launch(state == "SMOKE_RUN")
                cause = f"exception:{type(exc).__name__}:{state}"
                self.state["hold_reason"] = cause
                self.state["last_exception"] = {"type": type(exc).__name__, "message": str(exc)[:200], "state": state}
                self._transition("HOLD_LOOP")
                self._notify_or_defer("loop_hold", cause)
            if self.state["state"] == "HOLD_LOOP" and self.state.get("deferred_event") and not collection_live(self.root):
                # The collection that deferred this hold has ended: tell Ed and wake now.
                deferred = self.state.pop("deferred_event")
                self._io(deferred["kind"], lambda: self._event(deferred["kind"], deferred["cause"]))
            atomic_state(self.root / "state.json", self.state)
            # Overrun holds may deliver program mail while wake jobs still wait.
            io_failed = not self._flush(state=self.state["state"], deferred_overrun=self.state.get("deferred_overrun", False))
            if not collection_live(self.root):
                io_failed = not self._io("waker.bootstrap_deferred", self.waker.bootstrap_deferred) or io_failed
            if io_failed:
                atomic_state(self.root / "state.json", self.state)
        return 0

    def _io(self, operation, action):
        try:
            action()
            return True
        except Exception as exc:
            # Transport text can contain credentials; only the type is recorded.
            self.state["last_io_error"] = {"operation": operation, "type": type(exc).__name__}
            return False

    def _notify_or_defer(self, kind, cause):
        # While a collection may be measuring, keep the notice until its terminal record exists.
        if collection_live(self.root):
            self.state["deferred_event"] = {"kind": kind, "cause": cause}
        else:
            self._io(kind, lambda: self._event(kind, cause))

    def _flush(self, **kwargs):
        return self._io("mailer.flush", lambda: self.mailer.flush(**kwargs))

    def _transition(self, state):
        if self.state["state"] != state:
            if self.state["state"] == "WAIT_PHYSICS":
                self.state["wait"] = None
            if self.state["state"] == "HOLD_LOOP":
                self.state.pop("deferred_overrun", None)
                self.state.pop("deferred_event", None)
            self.state.update(state=state, since=self.clock())

    def _event(self, kind, cause=None, packs=None, *, wake=True, fields=None):
        if self.state["state"] in COLLECTING or (collection_live(self.root) and kind != "overrun"):
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
        # Hold, and defer mail and wake until the terminal path exists.
        self.state["hold_reason"] = "lane_missing:" + result.name
        self._transition("HOLD_LOOP")
        self._notify_or_defer("lane_missing", result.name)
        return True

    def _layout(self):
        s = self.state["session"]
        layout = compose.layout(queue.Selection(tuple(s["packs"]), s["round"]), self.regs, self.repo)
        attempt = s.get("launch_attempt", 0)
        return replace(layout, session_id=s["id"] + (f"-a{attempt}" if attempt else ""))

    def _fresh_id(self, base):
        """A collection id never used before by this loop.

        The driver keys its staging, plan and terminal records by this id, so a
        reused id (a pack held and resumed in the same round, or a new smoke
        after a failed one) would re-desk the old collection instead of running
        a new one. The first use keeps the plain id.
        """
        used = self.state.setdefault("used_ids", [])
        candidate, n = base, 1
        while candidate in used:
            n += 1
            candidate = f"{base}-n{n}"
        used.append(candidate)
        return candidate

    def _prepared(self, smoke=False):
        return Prepared(**self.state["session"]["smoke_prepared" if smoke else "prepared"])

    def _next(self):
        selection = queue.next_session(self.state, self.regs, self.clock(), next_t0=self._next_t0())
        if isinstance(selection, queue.Close):
            self.state["session"] = None
            self._transition("DONE")
            self._event("close", fields={"counts": selection.counts, "short": selection.short})
            return
        if isinstance(selection, queue.Idle):
            self.state["idle_reasons"] = selection.reasons
            self.state["session"] = None
            for p, reason in selection.reasons.items():
                if reason == "pack_not_open":
                    self._event("loop_hold", "pack_not_open:" + p, [p])
            return
        self.state.pop("idle_reasons", None)
        layout = compose.layout(selection, self.regs, self.repo)
        layout = replace(layout, session_id=self._fresh_id(layout.session_id))
        self.state["session"] = {"id": layout.session_id, "packs": list(selection.packs), "round": selection.round,
                                 "registrations": {p: {"data": dict(self.regs[p].data), "commit_time": self.regs[p].commit_time}
                                                   for p in selection.packs}}
        if any(self.regs[p].data.get("interleave") == "quad_round_robin" for p in selection.packs):
            capability = self.lanes.harvest.capabilities()
            if self._missing(capability):
                return
            if not capability.block_id_strata:
                packs = [p for p in selection.packs if self.regs[p].data.get("interleave") == "quad_round_robin"]
                self.state["session"] = None
                for p in packs:
                    self.state["packs"][p].update(status="held", hold_reason="interleave_unconfirmed:H3")
                    self._event("loop_hold", "interleave_unconfirmed:H3", [p])
                return
        if self._prepare_session(layout):
            self._transition("PRECHECK")

    def _prepare_session(self, layout=None):
        layout = layout or self._layout()
        prepared = self.lanes.driver.prepare_session(layout, compose.render(layout), smoke=False, keep={},
                                                     staging_root=self.root / "staging" / layout.session_id)
        if self._missing(prepared):
            return False
        self.state["session"]["prepared"] = asdict(prepared)
        return True

    def _wait_for(self, result, return_state):
        if "clock.rate_hold" in result.predicted_flags:
            # Lead ruling 2026-10-16: there is no redraw entry point. A fixed
            # rate cannot improve by waiting with time synchronization off.
            self.state["wait"] = None
            self.state["hold_reason"] = "clock.rate_hold"
            self._transition("HOLD_LOOP")
            self._event("loop_hold", "clock.rate_hold", fields={"flags": ["clock.rate_hold"]})
            return
        hazard = result.would_refuse[0].hazard
        episode = self.state.get("wait")
        if episode is None or self.state["state"] != "WAIT_PHYSICS":
            episode = {"hazard": hazard, "since": self.clock(), "remedied_hazards": [], "mailed": False,
                       "last_check": self.clock(), "return_state": return_state}
        episode["hazard"] = hazard
        episode["last_check"] = self.clock()
        self.state["wait"] = episode
        self._transition("WAIT_PHYSICS")
        remedied = set(episode.get("remedied_hazards", []))
        if hazard in result.remedies and hazard not in remedied:
            remedied.add(hazard)
            episode["remedied_hazards"] = sorted(remedied)
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

    def _certain_exclusion(self, result):
        if not result.certain_exclusion:
            return False
        packs = set()
        for x in result.certain_exclusion:
            packs.update([x.pack_id] if x.pack_id else self.state["session"]["packs"])
        self._hold_packs("certain_exclusion", [x.code for x in result.certain_exclusion], sorted(packs))
        return True

    def _precheck(self):
        layout = self._layout()
        result = self.lanes.precheck.run(layout, self._prepared().plan_path)
        if self._missing(result):
            return
        if result.would_refuse:
            self._wait_for(result, "PRECHECK")
            return
        if self._certain_exclusion(result):
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
        self._flush(state="PRECHECK")
        self._transition("SMOKE_RUN" if smoke else "ARM_WAIT")

    def _wait_physics(self):
        episode = self.state["wait"]
        if self.clock() - episode["last_check"] < 240:
            return
        result = self.lanes.precheck.run(self._layout(), self._prepared().plan_path)
        if self._missing(result):
            return
        if result.would_refuse:
            self._wait_for(result, episode["return_state"])
        elif self._certain_exclusion(result):
            return
        else:
            self.state["wait"] = None
            self._transition(episode["return_state"])

    def _active(self, prepared):
        path = self.root / "collection.active"
        if not path.exists():
            path.write_text(f"{prepared.terminal_path}\n{prepared.max_s + 3600}\n")

    def _rollback_launch(self, smoke):
        (self.root / "collection.active").unlink(missing_ok=True)
        session = self.state.get("session") or {}
        if not smoke and "started" in session:
            slots = self.state.get("slots", {}).get(str(session["round"]), [])
            for p in session["packs"]:
                if p in slots:
                    slots.remove(p)
                    self.state["packs"][p]["attempts_since_resume"] -= 1

    def _new_smoke(self):
        session = self.state["session"]
        session["smoke_attempt"] = session.get("smoke_attempt", 0) + 1
        for key in ("smoke_prepared", "smoke_handle", "smoke_started", "smoke_done", "smoke_launch_confirmed"):
            session.pop(key, None)

    def _retry_physics(self, hazards, return_state):
        self.state["wait"] = {"hazard": hazards[0] if hazards else "physics_refused", "since": self.clock(),
                              "remedied_hazards": [], "mailed": False, "last_check": self.clock(), "return_state": return_state}
        self._transition("WAIT_PHYSICS")

    def _run_collection(self, smoke):
        session = self.state["session"]
        if not smoke and "started" not in session and any(
                queue.done_reason(self.state, self.regs[p], self.clock(), next_t0=self._next_t0())
                for p in session["packs"]):
            self._drop_unarmed_session()
            return
        prefix = "smoke_" if smoke else ""
        if smoke and "smoke_prepared" not in session:
            layout = self._layout()
            layout = replace(layout, session_id=self._fresh_id(
                layout.session_id + f"-smoke-{session.get('smoke_attempt', 0)}"))
            prepared = self.lanes.driver.prepare_session(layout, compose.render(layout), smoke=True,
                keep=compose.smoke_keep(layout), staging_root=self.root / "staging" / layout.session_id)
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
            if handle is None and not session.get(prefix + "launch_confirmed"):
                self._rollback_launch(smoke)
            self._missing(result)
            return
        if isinstance(result, Refused):
            self._rollback_launch(smoke)
            if smoke:
                self._new_smoke()
            else:
                for key in ("started", "t0", "handle", "launch_confirmed", "prepared"):
                    session.pop(key, None)
                session["launch_attempt"] = session.get("launch_attempt", 0) + 1
                if not self._prepare_session():
                    return
            self._retry_physics(result.hazards, "SMOKE_RUN" if smoke else "ARM_WAIT")
            return
        session["launch_confirmed" if not smoke else "smoke_launch_confirmed"] = True
        if isinstance(result, Running):
            session[prefix + "handle"] = result.handle
            if self.clock() - session[prefix + "started"] > prepared.max_s + 3600 and not Path(prepared.terminal_path).exists():
                # Notify only after leaving the polling state. No process is killed.
                session["overrun"] = True
                self.state["hold_reason"] = "overrun"
                self._transition("HOLD_LOOP")
                # Keep the marker and defer the agent job; program mail can flush.
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
            self._new_smoke()
            self._retry_physics(result.codes or ("smoke_physics",), "SMOKE_RUN")
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

    def _drop_unarmed_session(self):
        session = self.state["session"]
        if session.get("notice_key"):
            self.mailer.close_notice(session["notice_key"])
        self.state.setdefault("unarmed_sessions", []).append({
            "session_id": session["id"], "packs": session["packs"],
            "notice_key": session.get("notice_key"), "status": "never_armed",
            "reason": "pack_closed", "epoch_s": self.clock()})
        self.state["session"] = None
        self._transition("NEXT")

    def _arm_wait(self):
        s = self.state["session"]
        if self.clock() < s["notice_sent"] + 1800:
            return
        if any(queue.done_reason(self.state, self.regs[p], self.clock(), next_t0=self._next_t0())
               for p in s["packs"]):
            self._drop_unarmed_session()
            return
        stop = self._stop()
        if self.state.get("stop_probe_unavailable"):
            s["no_unreadable"] = True
        if stop:
            self._owner_hold()
            return
        no = False
        try:
            no = self.mailer.has_no(s["notice_key"], self.config["owner_login"])
            if self.mailer.entry(s["notice_key"]).get("no_probe_failed"):
                s["no_unreadable"] = True
        except Exception:
            s["no_unreadable"] = True
        if no:
            self._owner_hold()
            return
        result = self.lanes.precheck.run(self._layout(), self._prepared().plan_path)
        if self._missing(result):
            return
        if result.would_refuse:
            self._wait_for(result, "ARM_WAIT")
            return
        if self._certain_exclusion(result):
            return
        self.state["last_certain_exclusion"] = None
        if any(self.state["packs"][p]["last_smoke_fingerprint"] != result.fingerprint for p in s["packs"]):
            s["fingerprint"] = result.fingerprint
            s["needs_smoke"] = True
            self._new_smoke()
            self._transition("SMOKE_RUN")
        else:
            self._transition("SESSION_RUN")

    def _session_run(self):
        self._run_collection(False)

    def _next_t0(self):
        return 60 * math.ceil((self.clock() + self.config.get("launch_lead_s", 420)) / 60)

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
        if s.get("no_unreadable"):
            flags.append("notice.no_unreadable")
        line = replace(line, session_id=s["id"], window_flags=tuple(sorted(set(flags))))
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
        existing = next((a for a in self.state["attempts"] if a["session_id"] == s["id"]), None)
        line = SessionLine(**existing["line"]) if existing else self.lanes.desk.session_desk(self._prepared(), Done(**s["done"]))
        if self._missing(line):
            return
        line = self._append_attempt(line)
        if not line.structure_ok:
            self.state["hold_reason"] = "structure_defect"
            self._transition("HOLD_LOOP")
            self._event("structure_defect", fields={"flags": line.window_flags})
            return
        self._transition("ROTATE")
        if line.harvest_rc not in (0, 6) or line.acceptance_verdict == "HARVEST_RERUN":
            self.state["harvest_fault"] = True
            self.state.setdefault("pending_sessions", {})[s["id"]] = s
            self._event("harvest_fault")
        elif line.harvest_rc == 6:
            self.state.setdefault("pending_sessions", {})[s["id"]] = s
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
                if self.state["state"] in {"HOLD_LOOP", "DONE"}:
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
                line = self.lanes.desk.reharvest(Prepared(**pending["prepared"]), Done(**pending["done"]))
                if self._missing(line):
                    atomic_state(self.root / "state.json", self.state)
                    return 0
                if not line.structure_ok or line.harvest_rc != 0 or line.acceptance_verdict not in ("ACCEPT", "EXCLUDE"):
                    raise ValueError("reharvest is not structurally complete")
                original = next(a for a in self.state["attempts"] if a["session_id"] == session_id)
                flags = set(line.window_flags) | (set(original["line"]["window_flags"]) & LOOP_WINDOW_FLAGS)
                line = replace(line, window_flags=tuple(sorted(flags)))
                regs = {p: Registration(r["data"], commit_time=r["commit_time"]) for p, r in pending["registrations"].items()}
                self.state.setdefault("reharvested", {})[session_id] = {p: queue.outcome(r, line, self.catalog) for p, r in regs.items()}
                del self.state["pending_sessions"][session_id]
                self.regs.update(regs)
                self._precision([p for p in regs if session_id in queue.counting_ids(self.state, p)])
            atomic_state(self.root / "state.json", self.state)
        return 0
