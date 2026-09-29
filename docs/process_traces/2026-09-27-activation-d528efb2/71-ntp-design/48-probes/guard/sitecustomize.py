import subprocess
_orig = subprocess.Popen.__init__
def _g(self, args, *a, **k):
    text = args if isinstance(args, str) else " ".join(map(str, args))
    if any(w in text for w in ("ioreg", "sudo", "powermetrics", "systemsetup", "sntp", "/usr/bin/log")):
        raise RuntimeError("p1 guard blocked: " + text[:80])
    return _orig(self, args, *a, **k)
subprocess.Popen.__init__ = _g
