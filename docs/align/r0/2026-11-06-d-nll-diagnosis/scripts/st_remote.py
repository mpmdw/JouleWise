"""Range-read tensors from remote safetensors on HF without downloading whole shards."""
import json, struct, subprocess, sys, os
import numpy as np
CACHE = "/private/tmp/jwd8diag/hdr"
def _get(url, start, end):
    r = subprocess.run(["curl", "-sfL", "-r", f"{start}-{end}", url], capture_output=True, check=True)
    return r.stdout
def header(repo, rev, fname):
    p = os.path.join(CACHE, f"{repo.replace('/','__')}__{rev[:8]}__{fname}.hdr.json")
    url = f"https://huggingface.co/{repo}/resolve/{rev}/{fname}"
    if os.path.exists(p):
        h, n = json.load(open(p)); return h, n, url
    n = struct.unpack("<Q", _get(url, 0, 7))[0]
    h = json.loads(_get(url, 8, 8 + n - 1))
    json.dump([h, n], open(p, "w")); return h, n, url
def tensor(repo, rev, index_map, key):
    fname = index_map[key]
    h, n, url = header(repo, rev, fname)
    m = h[key]; s, e = m["data_offsets"]
    raw = _get(url, 8 + n + s, 8 + n + e - 1)
    dt = m["dtype"]
    if dt == "BF16":
        a = np.frombuffer(raw, dtype=np.uint16).astype(np.uint32) << 16
        return a.view(np.float32).reshape(m["shape"])
    if dt == "F32": return np.frombuffer(raw, dtype=np.float32).reshape(m["shape"])
    if dt == "F16": return np.frombuffer(raw, dtype=np.float16).astype(np.float32).reshape(m["shape"])
    if dt == "U32": return np.frombuffer(raw, dtype=np.uint32).reshape(m["shape"])
    if dt == "F8_E4M3": return np.frombuffer(raw, dtype=np.uint8).reshape(m["shape"])
    raise ValueError(dt)
def index(repo, rev):
    url = f"https://huggingface.co/{repo}/resolve/{rev}/model.safetensors.index.json"
    return json.loads(subprocess.run(["curl", "-sfL", url], capture_output=True, check=True).stdout)["weight_map"]
