# Cold-gate guard: any attempt to start ioreg raises and is logged. No return value is supplied.
import os, subprocess
_LOG = "/tmp/cg-s1ctl-d528efb2/ioreg_attempts.log"
_orig_init = subprocess.Popen.__init__
def _guarded(self, args, *a, **k):
    text = args if isinstance(args, str) else " ".join(map(str, args))
    if "ioreg" in text:
        with open(_LOG, "a") as fh:
            fh.write(f"pid={os.getpid()} argv={text}\n")
        raise RuntimeError("cold-gate guard: battery probe blocked")
    return _orig_init(self, args, *a, **k)
subprocess.Popen.__init__ = _guarded
