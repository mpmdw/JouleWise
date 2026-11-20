"""Fresh R12 external interpreter profile for the original file courier.

The shell and Python payload are pinned, byte-for-byte. Only the executable
input is redirected into the isolated interpreter, preserving argv and stdin.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shlex

PROMPT = "docs/process/NIGHT_COURIER_PROMPT.md"
COURIER = "scripts/b6_courier.sh"


def bootstrap_text():
    return ("from b6_r12_courier_profile import install_runtime\ninstall_runtime()\n"
            "from runtime import bootstrap\nraise SystemExit(bootstrap())\n")


def prepare_profile(root):
    root = Path(root)
    (root / "b6_r12_courier_profile.py").write_bytes(Path(__file__).read_bytes())
    (root / "bootstrap.py").write_text(bootstrap_text())
    # Global aliases also apply after the shell's exec precommand modifier.
    # The original pinned shell file is sourced unchanged, not parsed/rebuilt.
    alias = "/opt/homebrew/bin/python3.13=" + shlex.quote(str(root / "interpreter/python3.13"))
    (root / "courier-source.zsh").write_text(
        "#!/bin/zsh -f\nalias -g " + shlex.quote(alias) + "\n"
        + "alias -g " + shlex.quote("/bin/sh=/bin/zsh -f " + shlex.quote(str(root / "courier-source.zsh")))
        + '\nsource "$1" "${@:2}"\n')
    path = root / "manifest.json"
    value = json.loads(path.read_bytes())
    value["generator_files_sha256"][Path(__file__).name] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    value["courier_profile"] = {"kind": "original pinned file courier with isolated interpreter input",
        "bootstrap_sha256": hashlib.sha256((root / "bootstrap.py").read_bytes()).hexdigest(),
        "shell_input_sha256": hashlib.sha256((root / "courier-source.zsh").read_bytes()).hexdigest(),
        "seam": "b6_r12_runtime.install_sources -> returned ChainSources.rewritten; external executable input only",
        "interpreter_input": "/opt/homebrew/bin/python3.13 -> " + str(root / "interpreter/python3.13"),
        "smoke_shell_input": "/bin/sh -> isolated zsh source wrapper, only the exact pinned smoke writer's launcher template",
        "courier_process_inputs": "subprocess.Popen.__init__: missing/None stdin is declared EOF (night-job shape); same existing SharedClock passive foreground observation as other isolated code children",
        "judgments_and_writers": "original f31; no replacement", "network_or_message_delivery": False}
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    return root


def export_prompt(root):
    from b6_r12_session_fixture import git_blobs
    raw = git_blobs([PROMPT])[PROMPT]
    target = Path(root) / "pin" / PROMPT
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
    path = Path(root) / "manifest.json"
    value = json.loads(path.read_bytes())
    value["pinned_input_sha256"][PROMPT] = hashlib.sha256(raw).hexdigest()
    value["courier_profile"]["courier_sha256"] = value["source_sha256"][COURIER]
    value["courier_profile"]["prompt_sha256"] = hashlib.sha256(raw).hexdigest()
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def install_runtime():
    """Install only in the generator bootstrap, before pinned code imports."""
    import runtime
    original = runtime.install_sources
    if getattr(original, "_r12_courier_profile", False):
        return

    def install(root, clock):
        import inspect
        import subprocess
        sources = original(root, clock)
        rewritten = sources.rewritten
        root = Path(root)
        profile = json.loads((root / "manifest.json").read_bytes())["courier_profile"]

        def command_input(argv):
            words = list(map(str, argv))
            if words and Path(words[0]).name in {"b6_courier.sh", "smoke-courier"}:
                path = Path(words[0])
                plain = path.is_absolute() and path.is_relative_to(root) and path == path.resolve() and path.is_file()
                direct = (plain and path.name == "b6_courier.sh" and path.parent.name == "scripts"
                          and hashlib.sha256(path.read_bytes()).hexdigest() == profile["courier_sha256"])
                smoke = False
                if plain and path.name == "smoke-courier" and path.parent.name == "bin":
                    target = path.parent.parent / "measurement" / COURIER
                    expected = '#!/bin/sh\nexec /bin/sh ' + shlex.quote(str(target)) + ' "$@"\n'
                    smoke = (path.read_bytes() == expected.encode() and target == target.resolve()
                             and target.is_file()
                             and hashlib.sha256(target.read_bytes()).hexdigest() == profile["courier_sha256"])
                if direct or smoke:
                    # Runtime's general source-read audit selects extensions;
                    # the original smoke writer's extensionless launcher also
                    # needs its actual bytes included in final attestation.
                    if smoke:
                        with (root / f"source-reads-{os.getpid()}.jsonl").open("a") as stream:
                            stream.write(json.dumps({"path": str(path)}) + "\n")
                    return ["/bin/zsh", "-f", str(root / "shell.zsh"),
                            str(root / "courier-source.zsh"), *words]
            return rewritten(argv)

        sources.rewritten = command_input
        native_init = subprocess.Popen.__init__
        signature = inspect.signature(native_init)

        def process_input(process, args, *positional, **keywords):
            words = list(map(str, args)) if not isinstance(args, (str, bytes)) else []
            courier = (words and Path(words[0]).name in {"b6_courier.sh", "smoke-courier"}
                       and command_input(words) is not None)
            if not courier:
                return native_init(process, args, *positional, **keywords)
            bound = signature.bind(process, args, *positional, **keywords)
            if bound.arguments.get("stdin") is None:
                bound.arguments["stdin"] = subprocess.DEVNULL
            result = native_init(*bound.args, **bound.kwargs)
            # A shell courier is an isolated foreground program just like
            # the runtime's existing Python/zsh children. Native interpreter
            # startup is not elapsed synthetic scenario time. The pinned
            # wait/retry/heartbeat judgments run on the coherent clock.
            clock.passive = True
            clock.foreground = process
            clock.foregrounds[process.pid] = process
            return result

        subprocess.Popen.__init__ = process_input
        return sources

    install._r12_courier_profile = True
    runtime.install_sources = install
