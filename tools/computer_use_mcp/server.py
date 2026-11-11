#!/usr/bin/env python3.13
"""Local macOS computer-use MCP server. Python stdlib only; no work at import."""

from __future__ import annotations

import base64
from collections import deque
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid


HERE = Path(__file__).resolve().parent
PROTOCOL_VERSIONS = ("2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05")
INPUT_TOOLS = frozenset({"click", "move", "drag", "scroll", "type_text", "key", "open_app"})
MAX_FRAME_BYTES = 1024 * 1024


class ToolError(Exception):
    """An expected tool failure, returned as MCP content with isError=true."""


class ArmedError(ToolError):
    """A positively observed armed state, distinct from an unreadable guard."""


def schema(properties=None, required=()):
    return {"type": "object", "properties": properties or {},
            "required": list(required), "additionalProperties": False}


NUMBER = {"type": "number"}
POINT = {"x": NUMBER, "y": NUMBER}
TOOL_SCHEMAS = {
    "screenshot": ("Capture the main display; return JPEG and image-to-screen mapping.", schema()),
    "click": ("Click at absolute screen POINTS (convert screenshot pixels using its mapping).",
              schema({**POINT, "button": {"type": "string", "enum": ["left", "right"]},
                      "count": {"type": "integer", "enum": [1, 2]}}, ("x", "y"))),
    "move": ("Move the pointer to absolute screen points.", schema(POINT, ("x", "y"))),
    "drag": ("Drag between hit-tested screen points; distances under 3 points become a click at the start.",
             schema({**POINT, "to_x": NUMBER, "to_y": NUMBER,
                     "duration": {"type": "number", "minimum": 0.1, "maximum": 5}},
                    ("x", "y", "to_x", "to_y"))),
    "scroll": ("Scroll by signed pixel deltas; positive dy scrolls up, positive dx left.",
               schema({"dx": {"type": "integer", "minimum": -5000, "maximum": 5000},
                       "dy": {"type": "integer", "minimum": -5000, "maximum": 5000}}, ("dy",))),
    "type_text": ("Type Unicode text into the focused control (does not use the clipboard).",
                  schema({"text": {"type": "string", "maxLength": 10000}}, ("text",))),
    "key": ("Press a key combo, e.g. shift+tab or cmd+a; app/launcher shortcuts are blocked.",
            schema({"combo": {"type": "string", "minLength": 1, "maxLength": 100}}, ("combo",))),
    "open_app": ("Open an allowlisted bundle id (name argument), including to recover focus.",
                 schema({"name": {"type": "string", "minLength": 1, "maxLength": 200}}, ("name",))),
    "frontmost_app": ("Report the frontmost app (subject to armed-night and app gates).", schema()),
    "wait": ("Wait up to ten seconds (subject to armed-night and app gates).",
             schema({"seconds": {"type": "number", "minimum": 0, "maximum": 10}}, ("seconds",))),
    "permissions_status": ("Preflight Screen Recording and Accessibility; never request a grant.", schema()),
}
TOOLS = [{"name": name, "description": description, "inputSchema": spec}
         for name, (description, spec) in TOOL_SCHEMAS.items()]


def validate(name, arguments):
    spec = TOOL_SCHEMAS[name][1]
    if not isinstance(arguments, dict):
        raise ToolError("arguments must be an object")
    if set(arguments) - set(spec["properties"]):
        raise ToolError("Unknown argument")
    if set(spec["required"]) - set(arguments):
        raise ToolError("Missing required argument")
    for key, value in arguments.items():
        rule = spec["properties"][key]
        kind = rule["type"]
        valid = ((kind == "string" and isinstance(value, str)) or
                 (kind == "integer" and type(value) is int) or
                 (kind == "number" and type(value) in (int, float)))
        if not valid:
            raise ToolError(f"Invalid type for {key}")
        if kind in ("number", "integer"):
            try:
                finite = math.isfinite(value)
            except OverflowError:
                finite = False
            if not finite:
                raise ToolError(f"{key} must be finite")
            if value < rule.get("minimum", -math.inf) or value > rule.get("maximum", math.inf):
                raise ToolError(f"{key} outside allowed range")
        if kind == "string":
            if not rule.get("minLength", 0) <= len(value) <= rule.get("maxLength", math.inf):
                raise ToolError(f"Invalid length for {key}")
            if "\0" in value or any(0xD800 <= ord(char) <= 0xDFFF for char in value):
                raise ToolError(f"Invalid Unicode for {key}")
        if "enum" in rule and value not in rule["enum"]:
            raise ToolError(f"Invalid choice for {key}")
    if name == "key":
        parts = [part.strip().lower() for part in arguments["combo"].split("+")]
        aliases = {"cmd": "cmd", "command": "cmd", "ctrl": "ctrl", "control": "ctrl",
                   "alt": "opt", "option": "opt", "opt": "opt", "shift": "shift", "fn": "fn"}
        try:
            modifiers = {aliases[part] for part in parts[:-1]}
        except KeyError as exc:
            raise ToolError("Unsupported key modifier") from exc
        key = parts[-1]
        if (("cmd" in modifiers and key in ("tab", "space")) or
                ("ctrl" in modifiers and key in ("up", "down")) or
                ({"cmd", "opt"} <= modifiers and key in ("esc", "escape"))):
            raise ToolError("App-switching and launcher key combos are blocked")


def text_result(value, *, error=False):
    return {"content": [{"type": "text", "text": json.dumps(value, ensure_ascii=True)}],
            "isError": error}


def reject_json_constant(value):
    raise ValueError(f"Invalid JSON constant: {value}")


class Executor:
    """The single subprocess boundary; tests replace it in its entirety."""

    def run(self, argv, *, input=None, timeout=15):
        try:
            result = subprocess.run(argv, input=input, capture_output=True, text=True,
                                    timeout=timeout, check=False)
        except FileNotFoundError as exc:
            raise ToolError(f"Required executable missing: {argv[0]}") from exc
        except subprocess.TimeoutExpired as exc:
            raise ToolError(f"Timed out running {Path(argv[0]).name}") from exc
        if result.returncode:
            # Do not echo subprocess stdin, captured screen paths, or typed text.
            raise ToolError(f"{Path(argv[0]).name} failed (exit {result.returncode}): "
                            + result.stderr.strip()[:500])
        return result.stdout


class MacBackend:
    def __init__(self, home, executor=None, swiftc=None):
        self.home = Path(home)
        self.executor = executor or Executor()
        self.swiftc = swiftc
        self.binary = None

    def helper(self, operation, arguments=None):
        if self.binary is None:
            source = HERE / "cu_input.swift"
            digest = hashlib.sha256(source.read_bytes()).hexdigest()[:24]
            cache = self.home / "Library/Caches/joulewise-cu"
            cache.mkdir(mode=0o700, parents=True, exist_ok=True)
            target = cache / f"cu_input-{digest}"
            if not target.is_file():
                compiler = self.swiftc or shutil.which("swiftc")
                if compiler is None:
                    raise ToolError("swiftc is missing; install Apple's Command Line Tools before live use")
                # Unique temporary output allows simultaneous servers to compile safely.
                with tempfile.TemporaryDirectory(prefix="build-", dir=cache) as work:
                    output = Path(work) / "cu_input"
                    self.executor.run([compiler, str(source), "-o", str(output)], timeout=120)
                    output.chmod(0o700)
                    output.replace(target)
            self.binary = target
        raw = self.executor.run([str(self.binary), operation],
                                input=json.dumps(arguments or {}, ensure_ascii=True))
        try:
            result = json.loads(raw)
        except ValueError as exc:
            raise ToolError("Invalid Swift helper response") from exc
        if not isinstance(result, dict):
            raise ToolError("Invalid Swift helper response")
        return result

    def frontmost(self):
        value = self.helper("frontmost_app")
        if (not isinstance(value.get("bundle_id"), str) or not value["bundle_id"] or
                type(value.get("pid")) is not int or value["pid"] <= 0):
            raise ToolError("Cannot determine frontmost app")
        return value

    def screenshot(self, before_capture):
        permissions = self.helper("permissions_status")
        if permissions.get("screen_recording") is not True:
            raise ToolError("Screen Recording permission is missing; grant it in System Settings")
        display = self.helper("display_info")
        with tempfile.TemporaryDirectory(prefix="joulewise-cu-") as work:
            original, jpeg = Path(work) / "screen.png", Path(work) / "screen.jpg"
            # Compilation and preflight may have taken time since the first gate.
            before_capture()
            self.executor.run(["/usr/sbin/screencapture", "-x", "-m", "-t", "png", str(original)])
            original_size = self.image_size(original)
            long_edge = min(1280, max(original_size))
            self.executor.run(["/usr/bin/sips", "-s", "format", "jpeg", "-Z", str(long_edge),
                               str(original), "--out", str(jpeg)])
            size = self.image_size(jpeg)
            mapping = coordinate_mapping(display, original_size, size)
            data = base64.b64encode(jpeg.read_bytes()).decode("ascii")
        return {"content": [{"type": "text", "text": json.dumps(mapping)},
                            {"type": "image", "data": data, "mimeType": "image/jpeg"}],
                "isError": False}

    def image_size(self, path):
        output = self.executor.run(["/usr/bin/sips", "-g", "pixelWidth", "-g", "pixelHeight", str(path)])
        width = re.search(r"pixelWidth:\s*(\d+)", output)
        height = re.search(r"pixelHeight:\s*(\d+)", output)
        if not width or not height:
            raise ToolError("Cannot determine screenshot dimensions")
        return int(width[1]), int(height[1])


def coordinate_mapping(display, original_size, size):
    """CGDisplayBounds is in points; screencapture/sips report actual pixels."""
    try:
        width, height = display["width"], display["height"]
        x, y = display["x"], display["y"]
        values = (width, height, x, y, *original_size, *size)
        if any(type(v) not in (int, float) or not math.isfinite(v) for v in values):
            raise ValueError
        if min(width, height, *original_size, *size) <= 0 or max(size) > 1280:
            raise ValueError
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        raise ToolError("Invalid display or resized image dimensions") from exc
    sx, sy = size[0] / width, size[1] / height
    return {"display": "main", "image_width": size[0], "image_height": size[1],
            "screen_bounds_points": {"x": x, "y": y, "width": width, "height": height},
            "capture_pixels_per_point": {"x": original_size[0] / width, "y": original_size[1] / height},
            "resize_scale": size[0] / original_size[0],
            "scale_factor": sx, "scale_x": sx, "scale_y": sy,
            "mapping": "screen_x = x + image_x / scale_x; screen_y = y + image_y / scale_y"}


class ComputerUse:
    def __init__(self, *, home=None, env=None, backend=None, clock=time.time,
                 monotonic=time.monotonic, sleeper=time.sleep, allowlist_path=None):
        self.home = Path.home() if home is None else Path(home)
        self.env = os.environ if env is None else env
        self.backend = backend or MacBackend(self.home)
        self.clock, self.monotonic, self.sleeper = clock, monotonic, sleeper
        self.allowlist_path = Path(allowlist_path) if allowlist_path else HERE / "allowlist.json"
        self.log_path = self.home / "Library/Logs/joulewise-cu/actions.jsonl"
        self.input_times = deque()

    def log(self, call_id, phase, name, arguments, frontmost, result):
        if name == "type_text" and self.env.get("JW_CU_REDACT") == "1":
            # Redact malformed type_text requests too, not just the valid text field.
            arguments = {"text": "[REDACTED]"}
        entry = {"timestamp": datetime.fromtimestamp(self.clock(), timezone.utc).isoformat(),
                 "call_id": call_id, "phase": phase, "tool": name, "arguments": arguments,
                 "frontmost_app": frontmost, "result": result}
        self.log_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        # O_APPEND and a single write per record; no truncation or rotation by this server.
        flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(self.log_path, flags, 0o600)
        try:
            record = (json.dumps(entry, ensure_ascii=True, allow_nan=False) + "\n").encode("utf-8")
            if os.write(fd, record) != len(record):
                raise OSError("short action-log write")
            os.fsync(fd)
        finally:
            os.close(fd)

    def check_armed(self):
        # Never use the caller-relative `list`: SSH/Background can see a different
        # domain from the user's night LaunchAgents. Check system jobs as well.
        for domain in (f"gui/{os.getuid()}", "system"):
            try:
                output = self.backend.executor.run(["/bin/launchctl", "print", domain])
            except Exception as exc:
                raise ToolError(f"Cannot verify armed-night state: unreadable launchctl domain {domain}") from exc
            if (not re.match(r"\s*" + re.escape(domain) + r"\s*=\s*\{\s*\n", output) or
                    not re.search(r"^\}[^\S\n]*$", output.rstrip(), re.M)):
                raise ToolError(f"Cannot verify armed-night state: malformed launchctl domain {domain}")
            # Only a closing line at the block's own indentation ends services.
            # A stray deeper/unindented brace stays a row and fails validation.
            sections = re.findall(r"^([ \t]*)services = \{[^\S\n]*\n(.*?)^\1\}[^\S\n]*$",
                                  output, re.M | re.S)
            if len(sections) != 1:
                raise ToolError(f"Cannot verify armed-night state: malformed launchctl services in {domain}")
            for line in sections[0][1].splitlines():
                fields = line.split()
                if (len(fields) != 3 or (fields[0] != "-" and not fields[0].isdigit()) or
                        (fields[1] != "-" and not re.fullmatch(r"-?\d+|\([a-z]+\)", fields[1])) or
                        not re.fullmatch(r"[A-Za-z0-9._-]+", fields[2])):
                    raise ToolError(f"Cannot verify armed-night state: malformed launchctl row in {domain}")
                if fields[2].lower().startswith("com.joulewise.night"):
                    raise ArmedError(f"Armed-night refusal: loaded launchd label {fields[2]} in {domain}")
        config = self.config()
        if not config.get("respect_remote_armed", True):
            return
        for configured in config.get("armed_marker_paths", ["~/Library/Logs/jw-hostlink/armed_until"]):
            marker = self.home / configured[2:] if configured.startswith("~/") else Path(configured)
            try:
                raw = marker.read_text(encoding="utf-8").strip()
            except FileNotFoundError:
                continue
            except (OSError, UnicodeError) as exc:
                raise ToolError("Cannot verify armed-night state: unreadable armed_until marker") from exc
            try:
                epoch = float(raw)
                if not math.isfinite(epoch):
                    raise ValueError
            except ValueError as exc:
                raise ToolError("Cannot verify armed-night state: invalid armed_until epoch") from exc
            if epoch > self.clock():
                raise ArmedError(f"Armed-night refusal: armed_until epoch {epoch} is in the future")

    def config(self):
        try:
            config = json.loads(self.allowlist_path.read_text(encoding="utf-8"))
            apps = config["apps"]
            if (not isinstance(apps, list) or not apps or
                    any(not isinstance(a, str) or not re.fullmatch(r"[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+", a)
                        for a in apps)):
                raise ValueError
            if type(config.get("respect_remote_armed", True)) is not bool:
                raise ValueError
            paths = config.get("armed_marker_paths", ["~/Library/Logs/jw-hostlink/armed_until"])
            if (not isinstance(paths, list) or not paths or
                    any(not isinstance(p, str) or "\0" in p or
                        not (p.startswith("~/") or Path(p).is_absolute()) for p in paths)):
                raise ValueError
            return config
        except (OSError, ValueError, KeyError, TypeError) as exc:
            raise ToolError("Cannot read valid app allowlist") from exc

    def allowed_apps(self):
        return self.config()["apps"]

    def check_app(self, name, arguments):
        apps = self.allowed_apps()
        if name == "open_app":
            if arguments["name"] not in apps:
                raise ToolError("App refusal: requested app is not allowlisted")
            return None
        frontmost = self.backend.frontmost()
        if frontmost["bundle_id"] not in apps:
            raise ToolError(f"App refusal: frontmost app {frontmost['bundle_id']!r} is not allowlisted")
        return frontmost

    def check_click_target(self, arguments, frontmost):
        target = self.backend.helper("window_at_point", {k: arguments[k] for k in ("x", "y")})
        if (target.get("bundle_id") != frontmost["bundle_id"] or
                type(target.get("pid")) is not int or target["pid"] != frontmost["pid"] or
                type(target.get("layer")) is not int or target["layer"] != 0 or
                target["bundle_id"] == "com.apple.dock"):
            raise ToolError("Click refusal: target must be a normal window of the allowed frontmost app; Dock/status items refused")

    def rate_limit(self):
        now = self.monotonic()
        while self.input_times and now - self.input_times[0] >= 1:
            self.input_times.popleft()
        if len(self.input_times) >= 5:
            raise ToolError("Rate limit: at most 5 input actions per second; wait and retry")
        self.input_times.append(now)

    def call(self, name, arguments):
        call_id, frontmost = uuid.uuid4().hex, None
        input_reserved, before_logged = False, False
        try:
            # Normalize validated short drags before all log phases and gates.
            # Validation is pure; even invalid requests get intent before probes.
            try:
                if name not in TOOL_SCHEMAS:
                    raise ToolError("Unknown tool")
                validate(name, arguments)
                if name == "drag" and math.hypot(arguments["to_x"] - arguments["x"],
                                                 arguments["to_y"] - arguments["y"]) < 3:
                    name, arguments = "click", {"x": arguments["x"], "y": arguments["y"]}
            finally:
                try:
                    self.log(call_id, "before", name, arguments, frontmost, "pending")
                    before_logged = True
                except Exception as exc:
                    raise ToolError(f"Action log unavailable; nothing executed ({type(exc).__name__})") from exc
            if self.env.get("JW_CU_DRY_RUN") not in (None, "", "0"):
                result = text_result({"dry_run": True, "executed": False,
                                      "note": "No probes or actions ran; safety/permissions were not evaluated"})
            else:
                if name != "permissions_status":
                    self.check_armed()
                    # Screenshot is intentionally exempt from the foreground allowlist.
                    if name == "screenshot":
                        try:
                            frontmost = self.backend.frontmost()
                        except ToolError:
                            # A screenshot can diagnose a missing foreground app.
                            frontmost = None
                    else:
                        frontmost = self.check_app(name, arguments)
                if name in INPUT_TOOLS:
                    # Probes/first compilation can take time. Recheck immediately before input.
                    self.check_armed()
                    frontmost = self.check_app(name, arguments)
                    self.rate_limit()
                    input_reserved = True
                # Record the resolved foreground immediately before the actual operation.
                self.log(call_id, "execute", name, arguments, frontmost, "pending")
                try:
                    result = self.execute(name, arguments, frontmost)
                finally:
                    if input_reserved:
                        # Keep the slot charged through completion, including errors.
                        self.input_times[-1] = self.monotonic()
            # Serialization/shape errors must be caught before the stdio writer.
            json.dumps(result, ensure_ascii=True, allow_nan=False)
            # Never log image bytes.
            summary = {"isError": result.get("isError", False),
                       "content": [item for item in result["content"] if item["type"] == "text"]}
        except Exception as exc:
            result = text_result({"error": f"{type(exc).__name__}: {exc}"}, error=True)
            summary = {"isError": True, "content": result["content"]}
        try:
            self.log(call_id, "after", name, arguments, frontmost, summary)
        except Exception:
            if not before_logged:
                return result  # Logging is unavailable; no probes/actions ran.
            # Execution may already have happened: the caller must not silently retry.
            return text_result({"error": "Result log failed; operation may have executed. Inspect state before retrying."}, error=True)
        return result

    def execute(self, name, arguments, frontmost):
        if name == "screenshot":
            return self.backend.screenshot(before_capture=self.check_armed)
        if name == "permissions_status":
            try:
                self.check_armed()
            except ArmedError as exc:
                return text_result({"armed": True, "reason": str(exc),
                                    "screen_recording": "unknown (armed; not compiled)",
                                    "accessibility": "unknown (armed; not compiled)"})
            return text_result({**self.backend.helper("permissions_status"), "armed": False})
        if name == "frontmost_app":
            return text_result(frontmost)
        if name == "wait":
            self.sleeper(arguments["seconds"])
            return text_result({"waited_seconds": arguments["seconds"]})
        permissions = self.backend.helper("permissions_status")
        if permissions.get("accessibility") is not True:
            raise ToolError("Accessibility permission is missing; grant it in System Settings")
        # open_app can be the first helper use; preflight may have compiled it.
        self.check_armed()
        if name == "open_app":
            self.check_app(name, arguments)
            self.backend.executor.run(["/usr/bin/open", "-b", arguments["name"]])
            return text_result({"opened": arguments["name"]})
        if name in ("click", "drag"):
            self.check_click_target(arguments, frontmost)
            if name == "drag":
                self.check_click_target({"x": arguments["to_x"], "y": arguments["to_y"]}, frontmost)
            self.check_armed()
            arguments = {**arguments, "expected_pid": frontmost["pid"],
                         "expected_bundle_id": frontmost["bundle_id"]}
        return text_result(self.backend.helper(name, arguments))


class Protocol:
    """MCP stdio is one UTF-8 JSON-RPC message per line (no HTTP/LSP headers)."""

    def __init__(self, computer):
        self.computer = computer
        self.initialized = False
        self.ready = False

    @staticmethod
    def error(request_id, code, message):
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}

    def handle(self, message):
        if not isinstance(message, dict) or message.get("jsonrpc") != "2.0":
            return self.error(None, -32600, "Invalid Request")
        request_id = message.get("id")
        if "id" in message and (type(request_id) not in (str, int)):
            return self.error(None, -32600, "Invalid request id")
        method = message.get("method")
        if not isinstance(method, str):
            # JSON-RPC responses (e.g. to server requests) need no reply.
            if "result" in message or "error" in message:
                return None
            return self.error(request_id, -32600, "Invalid Request")
        if "id" not in message:
            if method == "notifications/initialized" and self.initialized:
                self.ready = True
            # Cancellation/unknown notifications never elicit a response. Operations
            # are synchronous and bounded; cancellation cannot undo an input event.
            return None
        params = message.get("params", {})
        if not isinstance(params, dict):
            return self.error(request_id, -32602, "params must be an object")
        if method == "initialize":
            if self.initialized:
                return self.error(request_id, -32600, "Already initialized")
            if (not isinstance(params.get("protocolVersion"), str) or
                    not isinstance(params.get("capabilities"), dict) or
                    not isinstance(params.get("clientInfo"), dict) or
                    not all(isinstance(params["clientInfo"].get(k), str) for k in ("name", "version"))):
                return self.error(request_id, -32602, "Invalid initialize params")
            requested = params["protocolVersion"]
            version = requested if requested in PROTOCOL_VERSIONS else PROTOCOL_VERSIONS[0]
            self.initialized = True
            result = {"protocolVersion": version, "capabilities": {"tools": {"listChanged": False}},
                      "serverInfo": {"name": "joulewise-computer-use", "version": "1.0.0"},
                      "instructions": "Use permissions_status first. All other tools refuse armed nights. "
                                      "Coordinates are absolute screen points; apply screenshot mapping."}
        elif method == "ping":
            result = {}
        elif not self.ready:
            return self.error(request_id, -32000, "Initialize and send notifications/initialized first")
        elif method == "tools/list":
            result = {"tools": TOOLS}
        elif method == "tools/call":
            if not isinstance(params.get("name"), str):
                return self.error(request_id, -32602, "Tool name must be a string")
            result = self.computer.call(params["name"], params.get("arguments", {}))
        else:
            return self.error(request_id, -32601, "Method not found")
        return {"jsonrpc": "2.0", "id": request_id, "result": result}


def serve(input_stream, output_stream, computer=None):
    protocol = Protocol(computer or ComputerUse())
    while True:
        line = input_stream.readline(MAX_FRAME_BYTES + 1)
        if not line:
            return
        if len(line) > MAX_FRAME_BYTES:
            while line and not line.endswith(b"\n"):
                line = input_stream.readline(MAX_FRAME_BYTES + 1)
            response = protocol.error(None, -32700, "Message exceeds 1 MiB")
        else:
            try:
                message = json.loads(line, parse_constant=reject_json_constant)
                response = protocol.handle(message)
            except (ValueError, UnicodeError, RecursionError):
                response = protocol.error(None, -32700, "Parse error")
        if response is not None:
            output_stream.write(json.dumps(response, ensure_ascii=True, allow_nan=False).encode("utf-8") + b"\n")
            output_stream.flush()


if __name__ == "__main__":
    serve(sys.stdin.buffer, sys.stdout.buffer)
