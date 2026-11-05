#!/usr/bin/env python3
"""Stream-convert an HF ``qwen4_exp`` (Qwen3.8-Flash-Next) checkpoint to the
JouleWise MLX twin format (``joulewise/align/models/qwen4_exp_twin.py``).

Run with the pinned MLX environment (mlx 0.31.2 / mlx-lm 0.31.3), e.g.::

    /path/to/venv-mlx/bin/python scripts/align_convert_qwen4_exp_twin.py \
        --src /path/to/hf_checkpoint --out /path/to/mlx_twin \
        --expert-bits 4 --dense-bits 8 --ngram-format q4

Design (the bf16 checkpoint is ~360 GB; the target Mac has ~82 GB free):

* Source shards are processed ONE AT A TIME (optionally fetched one at a time
  with ``--hf-repo`` and deleted after use with ``--delete-source-shards``);
  tensors are read individually and released after conversion.
* Routed experts arrive per expert (``mlp.experts.{e}.{gate,up,down}_proj``)
  and may straddle shards: each expert is quantized as soon as it is read and
  the layer is stacked once all experts are present.
* The hashed n-gram table (``ple.ple_embedding.ngram_embedding.shard_*``) is
  never put in an MLX weight file: rows are encoded (f32/bf16/q8/q4) straight
  into a memory-mappable on-disk store.
* Mixed precision: experts at ``--expert-bits``; dense Linear/Embedding at
  ``--dense-bits`` (8 or none); router, shared-expert gate, the QSA indexer,
  DeltaNet a/b projections, hyper-connection write gates, norms, convs,
  ``A_log`` and ``dt_bias`` stay float. The QSA indexer is never dropped:
  the converter fails if any attention layer lacks it.
* ``twin_manifest.json`` records sha256 + bytes of every output file, the
  quantization policy and per-category byte totals.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Dict, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
MODEL_FILE = REPO_ROOT / "joulewise" / "align" / "models" / "qwen4_exp_twin.py"
CONVERTER_VERSION = "align_convert_qwen4_exp_twin/v1"
SIDE_FILES = (
    "tokenizer.json", "tokenizer_config.json", "chat_template.jinja",
    "generation_config.json", "special_tokens_map.json", "vocab.json", "merges.txt",
    "preprocessor_config.json",
)
_EXPERT_RE = re.compile(r"^(?P<head>.+)\.mlp\.experts\.(?P<e>\d+)\.(?P<proj>gate_proj|up_proj|down_proj)\.weight$")
_NGRAM_PART_RE = re.compile(r"^(?P<head>.+)\.layers\.(?P<layer>\d+)\.ple\.ple_embedding\.ngram_embedding\.(?:shard_(?P<part>\d+)\.)?weight$")


def _load_twin_module():
    sys.path.insert(0, str(REPO_ROOT))
    from joulewise.align.models import qwen4_exp_twin  # noqa: E402
    return qwen4_exp_twin


def _git_head() -> Optional[str]:
    import subprocess
    try:
        head = subprocess.run(["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
        dirty = subprocess.run(["git", "-C", str(REPO_ROOT), "status", "--porcelain", "--",
                                str(MODEL_FILE), __file__], capture_output=True, text=True).stdout
        return head + ("+dirty" if dirty.strip() else "")
    except Exception:
        return None


def sha256_file(path: Path, chunk: int = 8 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            b = fh.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def _category(path: str) -> str:
    if ".switch_mlp." in path:
        return "routed_experts"
    if ".self_attn.indexer." in path:
        return "qsa_indexer"
    if ".self_attn." in path:
        return "attention"
    if ".linear_attn." in path:
        return "deltanet"
    if ".shared_expert" in path:
        return "shared_expert"
    if path.endswith(".mlp.gate.weight"):
        return "router"
    if "hyper_connection" in path:
        return "hyper_connection"
    if ".ple." in path:
        return "ple_dense"
    if "embed_tokens" in path:
        return "embed_tokens"
    if "lm_head" in path:
        return "lm_head"
    return "other"


class Converter:
    def __init__(self, opts):
        import mlx.core as mx
        import numpy as np

        self.mx, self.np = mx, np
        # mx.quantize on the CPU and GPU streams can round differently, so the
        # quantization device is part of the artifact identity: pin it.
        self.device = opts.device
        mx.set_default_device(mx.cpu if opts.device == "cpu" else mx.gpu)
        self.tw = _load_twin_module()
        self.opts = opts
        self.out = Path(opts.out)
        self.out.mkdir(parents=True, exist_ok=True)
        self.dtype = {"bfloat16": mx.bfloat16, "float16": mx.float16,
                      "float32": mx.float32}[opts.dtype]
        self.expert_bits = None if (opts.no_quantize or opts.expert_bits == "none") else int(opts.expert_bits)
        self.dense_bits = None if (opts.no_quantize or opts.dense_bits == "none") else int(opts.dense_bits)
        self.group_size = opts.group_size
        self.buffer: Dict[str, object] = {}
        self.buffer_bytes = 0
        self.out_files = []
        self.weight_map: Dict[str, str] = {}
        self.quant_overrides: Dict[str, dict] = {}
        self.quantized_paths: Dict[str, int] = {}
        self.emitted_shapes: Dict[str, tuple] = {}
        self.category_bytes: Dict[str, int] = {}
        self.pending_experts: Dict[tuple, Dict[int, tuple]] = {}
        self.dropped = {"mtp": 0, "vision": 0}
        self.ngram_buffer_checks: Dict[str, bool] = {}
        self.sources = []
        self.pins = self._load_pins(opts.pins, opts.pins_repo) if opts.pins else None

    @staticmethod
    def _load_pins(path: str, repo: Optional[str]) -> Dict[str, str]:
        """``{"repos": {repo: {"files": [{path, sha256}]}}}`` or ``{name: sha256}``."""
        data = json.loads(Path(path).read_text())
        if "repos" in data:
            if repo is None:
                raise ValueError("--pins-repo is required for a multi-repo pins file")
            return {f["path"]: f["sha256"] for f in data["repos"][repo]["files"]}
        return {k: v for k, v in data.items() if isinstance(v, str)}

    # ---------------- config -----------------
    def load_config(self, src_dir: Path):
        cfg = json.loads((src_dir / "config.json").read_text())
        text = cfg.get("text_config", cfg)
        self.src_config = cfg
        self.args = self.tw.TextModelArgs.from_dict(text)
        self.ngram_dir = Path(self.opts.ngram_dir) if self.opts.ngram_dir else self.out / "ngram"
        self.ngram_dir.mkdir(parents=True, exist_ok=True)
        self.ngram = {}
        for ple_index, lid in enumerate(self.args.ple_layer_ids):
            layer = lid - 1
            spec = self.tw.NgramHashSpec(self.args, ple_index)
            lay = self.tw.ngram_record_layout(self.opts.ngram_format, spec.head_dim,
                                              self.opts.ngram_group_size)
            fname = f"layer{layer}.{self.opts.ngram_format}.bin"
            path = self.ngram_dir / fname
            mm = self.np.memmap(path, dtype=self.np.uint8, mode="w+",
                                shape=(spec.padded_vocab_size, lay["record_bytes"]))
            parts = self.args.split_ngram_parts
            part_rows = -(-spec.padded_vocab_size // parts)  # torch.chunk sizing
            self.ngram[layer] = {"spec": spec, "layout": lay, "file": fname, "path": path,
                                 "mm": mm, "parts": parts, "part_rows": part_rows,
                                 "written": set(), "whole": False}

    # ---------------- emit -----------------
    def _emit(self, key: str, value):
        mx = self.mx
        mx.eval(value)
        self.buffer[key] = value
        self.emitted_shapes[key] = tuple(value.shape)
        nbytes = value.nbytes
        self.buffer_bytes += nbytes
        cat = _category(key)
        self.category_bytes[cat] = self.category_bytes.get(cat, 0) + nbytes
        if self.buffer_bytes >= self.opts.shard_bytes:
            self.flush()

    def flush(self):
        if not self.buffer:
            return
        name = f"model-{len(self.out_files) + 1:05d}.safetensors"
        self.mx.save_safetensors(str(self.out / name), self.buffer, metadata={"format": "mlx"})
        for k in self.buffer:
            self.weight_map[k] = name
        self.out_files.append(name)
        self.buffer = {}
        self.buffer_bytes = 0

    def _emit_linear(self, path: str, w):
        """Emit ``{path}.weight`` (+ scales/biases when the policy quantizes it)."""
        mx = self.mx
        bits = self.tw.quant_policy(path, w.shape, self.expert_bits, self.dense_bits,
                                    self.group_size)
        if bits is None:
            self._emit(f"{path}.weight", w.astype(self.dtype))
            return
        wq, scales, biases = mx.quantize(w.astype(self.dtype), group_size=self.group_size, bits=bits)
        self._record_quant(path, bits)
        self._emit(f"{path}.weight", wq)
        self._emit(f"{path}.scales", scales)
        self._emit(f"{path}.biases", biases)

    def _record_quant(self, path: str, bits: int):
        self.quantized_paths[path] = bits
        top = self.expert_bits if self.expert_bits is not None else self.dense_bits
        if bits != top:
            self.quant_overrides[path] = {"group_size": self.group_size, "bits": bits}

    # ---------------- per-tensor handling -----------------
    def handle(self, key: str, value):
        tw, mx, np = self.tw, self.mx, self.np
        mk = tw.hf_to_mlx_key(key)
        if mk is None:
            self.dropped["mtp" if "mtp" in key.split(".")[0:2] else "vision"] += 1
            return
        if tw.is_ngram_buffer_key(mk):
            self._check_ngram_buffer(mk, value)
            return
        m = _NGRAM_PART_RE.match(mk)
        if m:
            self._write_ngram(int(m.group("layer")), m.group("part"), value)
            return
        m = _EXPERT_RE.match(mk)
        if m:
            self._add_expert(m.group("head"), m.group("proj"), int(m.group("e")), value)
            return
        if mk.endswith(".mlp.experts.gate_up_proj"):
            head = mk[: -len(".mlp.experts.gate_up_proj")]
            half = value.shape[1] // 2
            self._emit_linear(f"{head}.mlp.switch_mlp.gate_proj", value[:, :half])
            self._emit_linear(f"{head}.mlp.switch_mlp.up_proj", value[:, half:])
            return
        if mk.endswith(".mlp.experts.down_proj"):
            head = mk[: -len(".mlp.experts.down_proj")]
            self._emit_linear(f"{head}.mlp.switch_mlp.down_proj", value)
            return
        if mk.endswith("conv1d.weight"):
            if value.ndim == 3 and value.shape[-1] != 1:
                value = value.moveaxis(2, 1)
            self._emit(mk, value.astype(self.dtype))
            return
        if mk.endswith(".weight") and value.ndim == 2:
            self._emit_linear(mk[: -len(".weight")], value)
            return
        if not mx.issubdtype(value.dtype, mx.floating):
            raise ValueError(f"unexpected non-float tensor {key} {value.dtype}")
        self._emit(mk, value.astype(self.dtype))

    def _add_expert(self, head: str, proj: str, e: int, w):
        mx = self.mx
        path = f"{head}.mlp.switch_mlp.{proj}"
        bits = self.tw.quant_policy(path, (1, *w.shape), self.expert_bits, self.dense_bits,
                                    self.group_size)
        if bits is None:
            piece = (w.astype(self.dtype),)
        else:
            piece = tuple(mx.quantize(w.astype(self.dtype), group_size=self.group_size, bits=bits))
        mx.eval(piece)
        slot = self.pending_experts.setdefault((path, bits), {})
        if e in slot:
            raise ValueError(f"duplicate expert {e} for {path}")
        slot[e] = piece
        n = self.args.num_experts
        if len(slot) == n:
            parts = [mx.stack([slot[i][j] for i in range(n)]) for j in range(len(piece))]
            del self.pending_experts[(path, bits)]
            if bits is None:
                self._emit(f"{path}.weight", parts[0])
            else:
                self._record_quant(path, bits)
                self._emit(f"{path}.weight", parts[0])
                self._emit(f"{path}.scales", parts[1])
                self._emit(f"{path}.biases", parts[2])

    def _check_ngram_buffer(self, mk: str, value):
        np = self.np
        layer = int(re.search(r"\.layers\.(\d+)\.", mk).group(1))
        spec = self.ngram[layer]["spec"]
        got = np.array(value).astype(np.int64).tolist()
        if mk.endswith("layer_multipliers"):
            want = spec.multipliers
        elif mk.endswith("ngram_heads_vocab_sizes"):
            want = spec.head_vocab_sizes
        else:
            want = spec.head_offsets
        if [int(x) for x in got] != [int(x) for x in want]:
            raise ValueError(f"{mk}: checkpoint buffer {got} != recomputed {want}")
        self.ngram_buffer_checks[mk] = True

    def _write_ngram(self, layer: int, part: Optional[str], value):
        mx, np = self.mx, self.np
        st = self.ngram[layer]
        spec, lay = st["spec"], st["layout"]
        if value.shape[-1] != spec.head_dim:
            raise ValueError(f"n-gram dim {value.shape[-1]} != {spec.head_dim}")
        if part is None:
            if value.shape[0] != spec.padded_vocab_size:
                raise ValueError("unsplit n-gram table has the wrong row count")
            start = 0
            st["whole"] = True
        else:
            k = int(part)
            start = k * st["part_rows"]
            expect = max(0, min(st["part_rows"], spec.padded_vocab_size - start))
            if value.shape[0] != expect:
                raise ValueError(f"n-gram part {k} has {value.shape[0]} rows, expected {expect}")
            if k in st["written"]:
                raise ValueError(f"duplicate n-gram part {k}")
            st["written"].add(k)
        step = self.opts.ngram_chunk_rows
        for lo in range(0, value.shape[0], step):
            chunk = np.array(value[lo:lo + step].astype(mx.float32))
            st["mm"][start + lo:start + lo + chunk.shape[0]] = self.tw.encode_ngram_rows(
                chunk, self.opts.ngram_format, self.opts.ngram_group_size)
        st["mm"].flush()

    # ---------------- sources -----------------
    def source_shards(self, src_dir: Path):
        idx = src_dir / "model.safetensors.index.json"
        if idx.exists():
            weight_map = json.loads(idx.read_text())["weight_map"]
            return sorted(set(weight_map.values()))
        return sorted(p.name for p in src_dir.glob("model*.safetensors"))

    def fetch(self, name: str) -> Path:
        src = Path(self.opts.src)
        if self.opts.hf_repo:
            from huggingface_hub import hf_hub_download  # official package
            return Path(hf_hub_download(self.opts.hf_repo, name, revision=self.opts.revision,
                                        local_dir=str(src)))
        return src / name

    def run(self):
        src = Path(self.opts.src)
        src.mkdir(parents=True, exist_ok=True)
        if self.opts.hf_repo:
            from huggingface_hub import hf_hub_download
            for side in ("config.json", "model.safetensors.index.json") + SIDE_FILES:
                try:
                    hf_hub_download(self.opts.hf_repo, side, revision=self.opts.revision,
                                    local_dir=str(src))
                except Exception:  # side files are optional
                    if side == "config.json":
                        raise
        self.load_config(src)
        from safetensors import safe_open

        shards = self.source_shards(src)
        if not shards:
            raise FileNotFoundError(f"no safetensors shards under {src}")
        for name in shards:
            path = self.fetch(name)
            info = {"file": name, "bytes": path.stat().st_size}
            if self.opts.hash_sources or self.pins is not None:
                info["sha256"] = sha256_file(path)
            if self.pins is not None:
                want = self.pins.get(name)
                if want is None:
                    raise ValueError(f"{name}: no pinned sha256")
                if info["sha256"] != want:
                    raise ValueError(f"{name}: sha256 {info['sha256']} != pinned {want}")
                info["pin_verified"] = True
            n = 0
            with safe_open(str(path), framework="mlx") as fh:
                for key in fh.keys():
                    self.handle(key, fh.get_tensor(key))
                    n += 1
            info["tensors"] = n
            self.sources.append(info)
            if self.opts.delete_source_shards:
                path.unlink()
            print(f"[convert] {name}: {n} tensors", flush=True)
        self.flush()
        self.finish(src)

    # ---------------- finish -----------------
    def finish(self, src: Path):
        tw, np = self.tw, self.np
        if self.pending_experts:
            missing = {f"{p}": f"{len(v)}/{self.args.num_experts}" for (p, _), v in self.pending_experts.items()}
            raise ValueError(f"incomplete expert sets: {missing}")
        ngram_meta = {}
        for layer, st in self.ngram.items():
            if not st["whole"] and len(st["written"]) != st["parts"]:
                raise ValueError(f"layer {layer}: n-gram parts {len(st['written'])}/{st['parts']}")
            st["mm"].flush()
            del st["mm"]
            ngram_meta[str(layer)] = {
                "file": st["file"], "rows": st["spec"].padded_vocab_size,
                "dim": st["spec"].head_dim, "format": self.opts.ngram_format,
                "group_size": self.opts.ngram_group_size,
                "record_bytes": st["layout"]["record_bytes"],
                "sha256": sha256_file(st["path"]),
            }
        self._verify_complete()
        cfg = dict(self.src_config)
        cfg["model_file"] = MODEL_FILE.name
        top = self.expert_bits if self.expert_bits is not None else self.dense_bits
        if self.quantized_paths:
            q = {"group_size": self.group_size, "bits": top, "mode": "affine"}
            q.update(self.quant_overrides)
            cfg["quantization"] = q
            cfg["quantization_config"] = q
        try:
            ngram_dir_cfg = str(self.ngram_dir.relative_to(self.out))
        except ValueError:
            ngram_dir_cfg = str(self.ngram_dir.resolve())
        cfg["twin"] = {
            "format_version": tw.TWIN_FORMAT_VERSION,
            "converter": CONVERTER_VERSION,
            "dtype": self.opts.dtype,
            "policy": {"expert_bits": self.expert_bits, "dense_bits": self.dense_bits,
                       "group_size": self.group_size},
            "ngram": {"dir": ngram_dir_cfg, "io": self.opts.ngram_io, "layers": ngram_meta},
        }
        (self.out / "config.json").write_text(json.dumps(cfg, indent=2, sort_keys=True) + "\n")
        (self.out / "model.safetensors.index.json").write_text(json.dumps(
            {"metadata": {"format": "mlx"}, "weight_map": dict(sorted(self.weight_map.items()))},
            indent=2) + "\n")
        shutil.copy2(MODEL_FILE, self.out / MODEL_FILE.name)
        for side in SIDE_FILES:
            if (src / side).exists():
                shutil.copy2(src / side, self.out / side)
        self.write_manifest(ngram_meta)

    def _verify_complete(self):
        """Every parameter of the port is present with the right shape; the
        QSA indexer is present on every attention layer."""
        from mlx.utils import tree_flatten
        cfg_args = self.tw.ModelArgs.from_dict(self.src_config)
        model = self.tw.Model(cfg_args)  # lazy arrays: shapes only, no allocation
        expected = dict(tree_flatten(model.parameters()))
        problems = []
        for key, arr in expected.items():
            path = key.rsplit(".", 1)[0]
            if path in self.quantized_paths and key.endswith(".weight"):
                for suffix in ("weight", "scales", "biases"):
                    if f"{path}.{suffix}" not in self.emitted_shapes:
                        problems.append(f"missing {path}.{suffix}")
                continue
            if key not in self.emitted_shapes:
                problems.append(f"missing {key}")
            elif self.emitted_shapes[key] != tuple(arr.shape):
                problems.append(f"shape {key}: {self.emitted_shapes[key]} != {tuple(arr.shape)}")
        allowed = set(expected)
        for path in self.quantized_paths:
            allowed |= {f"{path}.scales", f"{path}.biases"}
        extra = sorted(set(self.emitted_shapes) - allowed)
        problems += [f"unexpected {k}" for k in extra]
        for i, t in enumerate(self.args.layer_types):
            if t == "indexed_attention":
                base = f"language_model.model.layers.{i}.self_attn.indexer."
                for leaf in ("index_qk_proj.weight", "q_layernorm.weight", "k_layernorm.weight"):
                    if base + leaf not in self.emitted_shapes:
                        problems.append(f"QSA indexer missing: {base + leaf}")
        if problems:
            raise ValueError("conversion incomplete:\n  " + "\n  ".join(problems[:50]))

    def write_manifest(self, ngram_meta):
        files = []
        for p in sorted(self.out.iterdir()):
            if p.is_file() and p.name != "twin_manifest.json":
                files.append({"path": p.name, "bytes": p.stat().st_size, "sha256": sha256_file(p)})
        for layer, meta in ngram_meta.items():
            path = self.ngram_dir / meta["file"]
            files.append({"path": str(path.relative_to(self.out)) if path.is_relative_to(self.out)
                          else str(path), "bytes": path.stat().st_size, "sha256": meta["sha256"]})
        manifest = {
            "converter": CONVERTER_VERSION,
            "format_version": self.tw.TWIN_FORMAT_VERSION,
            "created_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
            "source": {"dir": str(Path(self.opts.src).resolve()), "hf_repo": self.opts.hf_repo,
                       "revision": self.opts.revision, "shards": self.sources},
            "options": {k: v for k, v in vars(self.opts).items() if k not in ("src", "out")},
            "quantize_device": self.device,
            "mlx_version": self.mx.__version__,
            "converter_commit": _git_head(),
            "quantized_modules": {str(b): sum(1 for v in self.quantized_paths.values() if v == b)
                                  for b in sorted(set(self.quantized_paths.values()))},
            "category_bytes": dict(sorted(self.category_bytes.items())),
            "ngram_bytes": sum(f["bytes"] for f in files if f["path"].endswith(".bin")),
            "dropped_tensors": self.dropped,
            "ngram_buffer_checks": self.ngram_buffer_checks,
            "files": files,
        }
        (self.out / "twin_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


def parse_args(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--src", required=True, help="HF checkpoint dir (or staging dir with --hf-repo)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--dtype", default="bfloat16", choices=("bfloat16", "float16", "float32"))
    ap.add_argument("--expert-bits", default="4", choices=("2", "3", "4", "5", "6", "8", "none"))
    ap.add_argument("--dense-bits", default="8", choices=("4", "5", "6", "8", "none"))
    ap.add_argument("--group-size", type=int, default=64, choices=(32, 64, 128))
    ap.add_argument("--no-quantize", action="store_true", help="keep every tensor in --dtype")
    ap.add_argument("--ngram-format", default="q8", choices=("f32", "bf16", "q8", "q4"))
    ap.add_argument("--ngram-group-size", type=int, default=32)
    ap.add_argument("--ngram-io", default="mmap", choices=("mmap", "pread"))
    ap.add_argument("--ngram-dir", default=None, help="store dir (default OUT/ngram)")
    ap.add_argument("--ngram-chunk-rows", type=int, default=1 << 18)
    ap.add_argument("--shard-bytes", type=float, default=5e9)
    ap.add_argument("--delete-source-shards", action="store_true",
                    help="unlink each source shard after it has been converted")
    ap.add_argument("--hf-repo", default=None, help="fetch shards one at a time from this repo")
    ap.add_argument("--revision", default=None)
    ap.add_argument("--hash-sources", action="store_true")
    ap.add_argument("--pins", default=None,
                    help="JSON of pinned source sha256s; every shard must match before use")
    ap.add_argument("--pins-repo", default=None, help="repo key inside a multi-repo pins file")
    ap.add_argument("--device", default="cpu", choices=("cpu", "gpu"),
                    help="stream for casts/quantization (part of artifact identity)")
    return ap.parse_args(argv)


def main(argv=None):
    opts = parse_args(argv)
    Converter(opts).run()
    print(f"[convert] wrote {opts.out}")


if __name__ == "__main__":
    main()
