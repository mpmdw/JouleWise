# Exhibit F — how the night gate and the plan writer bind the chain digest (verbatim excerpts at main 5472ff53)

```
70:        "night_chain_digest_mismatch",
105:    "night_chain_digest_mismatch",
125:    "chain_sha256_path",
206:    chain_sha256_path: str
292:        chain_sha256_path = require_text("chain_sha256_path")
357:            chain_sha256_path=chain_sha256_path,
722:    keys = {"purpose", "attempt_id", "claim_eligible", "pack_sha256", "permitted_chain_sha256", "permitted_blocks", "authority"}
725:    for field in ("pack_sha256", "permitted_chain_sha256"):
777:    chain = _pack_bytes(Path(plan.chain_path), "window_chain_sha256", authorization["permitted_chain_sha256"])
778:    sidecar = _pack_bytes(Path(plan.chain_sha256_path), "chain_sha256_path").decode("utf-8")
782:        raise PackNightRefusal("window_chain_sha256: sidecar mismatch")
1048:                "chain_sha256_path": plan.chain_sha256_path,
```
```
scripts/run_night.py:1001:    chain_sha256: str | None,
scripts/run_night.py:1019:            "chain_sha256": chain_sha256,
scripts/run_night.py:1066:        chain_sha256_path="",
scripts/run_night.py:1464:        "window_chain_sha256": refs["window_chain"]["sha256"],
scripts/run_night.py:1796:        chain_sha256 = None
scripts/run_night.py:1800:        chain_sha256 = _sha256_path(chain_path) if chain_path.is_file() else None
scripts/run_night.py:1801:        sidecar_path = Path(plan.chain_sha256_path)
scripts/run_night.py:1806:        if chain_sha256 is None or expected is None or chain_sha256 != expected:
scripts/run_night.py:1811:                _CODES["chain_digest_mismatch"],
scripts/run_night.py:1816:                    "actual": chain_sha256,
```

The plan pins the chain digest at arm time (the sidecar written by the arm procedure), and the gate refuses night_chain_digest_mismatch when the tracked chain's bytes differ from that pin at t0. The pre-registration's digest sentence is a SCIENCE pin, not what the gate reads; the two agree only if the addendum re-pins it.
