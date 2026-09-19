# Exhibit A — the live generator drift set and its head-file pin (verbatim `sed` from `configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py` at main `2f79e633`)

```python
    "0227bca3f826edc7f0a1baf98a394df01d8f48e9609966088870d712f765697d"
)
SUCCESSOR_ACCEPTANCE_DERIVATION_SHA256 = (
    "18d09aa9d4accb16a8dff770de85cd7e7525bdb0b6e68f1de716e20fb8a9b9f3"
)
SUCCESSOR_ACCEPTANCE_ID = "d079_calibration_acceptance_v2_n17_r6"
LEDGER_HEAD_FILE_SHA256 = (
    "6bbe26258165bbd11ca996324a5862c2e6e34faae7999b6c06f5e12f27ac2902"
)
LEDGER_HEAD_SHA256 = (
    "08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7"
)
NEG8_MANIFEST_REL = Path("configs/campaigns/neg8_reference_corpus/order_manifest.json")
NEG8_SETTLED_REL = Path(
    "configs/campaigns/neg8_reference_corpus/derivation/settled_corpus.json"
)
# …
    (
        decode_definition,
        decode_raw,
        prefill_definition,
        prefill_raw,
        p512_definition,
        p512_raw,
    ) = load_and_verify_families()
    p512_prompt_text = P512_PROMPT_TEXT
    for path, expected in (
        (POLICY_REL, POLICY_SHA256),
        (acceptance_pin()["rel"], acceptance_pin()["artifact_sha256"]),
        (LEDGER_HEAD_REL, LEDGER_HEAD_FILE_SHA256),
        (NEG8_SETTLED_REL, NEG8_SETTLED_SHA256),
    ):
        if sha256_file(REPO_ROOT / path) != expected:
            raise ValueError(f"pinned input drifted: {path.as_posix()}")

    write_bytes(output_root, PACK_REL / "generate_configs.py", source_raw)
    write_bytes(output_root, PACK_REL / "README.md", readme_bytes())
    decode_suite_raw = render_json(decode_suite_manifest())
# …
            "issued_acceptance": {
                "acceptance_id": acceptance_pin()["acceptance_id"],
                "path": acceptance_pin()["rel"].as_posix(),
                "artifact_sha256": acceptance_pin()["artifact_sha256"],
                "derivation_sha256": acceptance_pin()["derivation_sha256"],
            },
            "issued_ledger_head": {
                "path": LEDGER_HEAD_REL.as_posix(),
                "file_sha256": LEDGER_HEAD_FILE_SHA256,
                "head_sha256": LEDGER_HEAD_SHA256,
            },
            "successor_effect": "invalidate_and_reissue_readiness_and_pin_projection",
            "arming_prerequisites": [
                {"id": "D117-U2", "status": "required_before_arm"},
                {"id": "D117-POSTCOLLECTION-TRUST-01", "status": "required_before_mint"},
                {
```

Generators declaring `LEDGER_HEAD_FILE_SHA256` at `2f79e633` (`grep -l "^LEDGER_HEAD_FILE_SHA256" configs/campaigns/*/generate_configs.py`):

```
configs/campaigns/d117_floor_qwen25_1p5b_v1/generate_configs.py
configs/campaigns/d117_floor_qwen25_1p5b_v2/generate_configs.py
configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py
configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py
configs/campaigns/d117_floor_qwen3-8b_v5/generate_configs.py
```

Generators referencing the head-file path at all:

```
configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/generate_configs.py
configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v2/generate_configs.py
configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py
configs/campaigns/d117_contrast_v5/generate_configs.py
configs/campaigns/d117_floor_qwen25_1p5b_v1/generate_configs.py
configs/campaigns/d117_floor_qwen25_1p5b_v2/generate_configs.py
configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py
configs/campaigns/d117_floor_qwen25_7b_v1/generate_configs.py
configs/campaigns/d117_floor_qwen25_7b_v2/generate_configs.py
configs/campaigns/d117_floor_qwen25_7b_v3/generate_configs.py
configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py
configs/campaigns/d117_floor_qwen3-8b_v5/generate_configs.py
```
