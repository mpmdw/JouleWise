# Runtime closure prototype for B-3 (and _cache forgery), applied in-process only; no repo edit.
import sys, tempfile
sys.path.insert(0,"."); sys.path.insert(0,"tests"); sys.path.insert(0,"/tmp/cg_sweep")
from pathlib import Path
import reader_probe_lib as L
from joulewise import bundle_read
from joulewise.bundle_read import BundleReader
A=L.build(Path(tempfile.mkdtemp(prefix="ss_A_")), charging=False)
B=L.build(Path(tempfile.mkdtemp(prefix="ss_B_")), charging=True)
def show(k,fn):
    try: v=fn(); print(f"{k:52s} RETURNED sentinel={L.holds(v)} n={len(v) if hasattr(v,'__len__') else '-'}")
    except Exception as e: print(f"{k:52s} raised {type(e).__name__}")
def repoint():
    r=BundleReader(A); r.metadata(); r._path=Path(B); return r.trace_rows()
def forge():
    r=BundleReader(B); r._cache.update(metadata=r.raw_metadata()); return r.trace_rows()
show("baseline pass bundle A trace_rows", lambda: BundleReader(A).trace_rows())
show("baseline charging B trace_rows", lambda: BundleReader(B).trace_rows())
show("B-3 repoint, current code", repoint)
show("cache forge, current code", forge)
orig=BundleReader.metadata
def metadata(self):
    # proposed: the verdict is bound to the path it was computed for, and the
    # slot is honoured only if the gate itself wrote it (token object).
    if self._cache.get("_gate_token") is not _TOKEN or self._cache.get("_gated_path") != self._path:
        self._cache.clear()
        out=orig(self)
        self._cache["_gated_path"]=self._path; self._cache["_gate_token"]=_TOKEN
        return out
    return self._cache["metadata"]
_TOKEN=object()
BundleReader.metadata=metadata
show("PROTO pass bundle A trace_rows", lambda: BundleReader(A).trace_rows())
show("PROTO charging B trace_rows", lambda: BundleReader(B).trace_rows())
show("PROTO B-3 repoint", repoint)
show("PROTO cache forge", forge)
