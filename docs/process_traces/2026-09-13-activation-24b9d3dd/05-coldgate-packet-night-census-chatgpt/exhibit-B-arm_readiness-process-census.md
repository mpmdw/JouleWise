# Exhibit B — joulewise/arm_readiness_evidence_t0.py at 27957b60 (arm-time process census)

```python
def _derive_process_census(context: _Context) -> _DerivedRow:
    kind = "PROCESS_CENSUS"
    probes = (
        _fresh_probe(context, kind, "keep-awake", ("/usr/bin/pgrep", "-x", "caffeinate")),
        _fresh_probe(context, kind, "agent", ("/usr/bin/pgrep", "-lf", "codex|claude|t3")),
        _fresh_probe(context, kind, "browser", ("/usr/bin/pgrep", "-lf", "Safari|Google Chrome|Chromium|Firefox|browser automation")),
        _fresh_probe(context, kind, "monitor", ("/usr/bin/pgrep", "-lf", "powermetrics|window-chain|run_campaign|tail -f|watch")),
    )
    for label, probe in zip(("keep-awake", "agent", "browser", "monitor"), probes, strict=True):
        _expect_absent(probe, kind=kind, label=label)
    return _DerivedRow(
        "t0.no_stray_keepawake",
        kind,
        {"absent_process_classes": ["agent", "browser", "keep_awake", "monitor"], "fresh_process_census": True},
        "PROBE",
        probes=probes,
    )


def _reverify_offline_inputs(context: _Context, *, kind: str) -> tuple[list[dict[str, str]], dict[str, _Any]]:
    primary: list[dict[str, str]] = []
    external = context.tree.get("external_inputs")
    if not isinstance(external, _Mapping):
        raise _underivable(kind, "pack external-input registry is missing")
    pins: list[_Mapping[str, _Any]] = []
    for item in external.get("artifacts", []):
        if isinstance(item, _Mapping):
            pins.append(item)
    for item in external.get("manifests", []):
        if isinstance(item, _Mapping):
            manifest = item.get("manifest")
            if isinstance(manifest, _Mapping):
                pins.append(manifest)
            pins.extend(member for member in item.get("members", []) if isinstance(member, _Mapping))
    for pin in pins:
        path = pin.get("path")
        digest = pin.get("sha256")
        if not isinstance(path, str) or not isinstance(digest, str):
            raise _underivable(kind, "external-input pin is malformed")
        artifact, _raw = _committed_artifact(context.repository, path, kind=kind)
        if artifact["sha256"] != digest:
            raise _underivable(kind, f"external-input pin differs from committed bytes: {path}")
        primary.append(artifact)
    try:
        tree, projection, _producer = _identity._load_pack_projection(context.pack_root)
        frozen, _raw = _identity._load_frozen_receipt(context.pack_root, projection)
        current_units, current_sha, checks = _identity._derive_projection_units(context.pack_root, projection)
    except _identity.IdentityPinProjectionError as exc:
        raise _underivable(kind, f"live U11 input re-derivation refused: {exc.reason_code}") from exc
    if (
        not _identity._frozen_pack_matches_receipt(projection, frozen)
        or not _identity._frozen_pack_identity_matches_receipt(context.pack_root, tree, frozen)
        or current_sha != frozen["pack"]["projection_input_sha256"]
        or [unit["model_runtime_config"] for unit in current_units]
        != [unit["model_runtime_config"] for unit in frozen["identity_units"]]
    ):
```
