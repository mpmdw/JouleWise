#!/usr/bin/env bash
# Fresh Ubuntu + NVIDIA driver. No provider API or rental command runs here.
set -euo pipefail
repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd)"
venv_dir="${JOULEWISE_VENV:-$repo_root/.gpukit-venv}"
python_bin="${JOULEWISE_PYTHON:-python3}"
probe_timeout="${JOULEWISE_PROBE_TIMEOUT_S:-}"
gpu_indices=""
monitor_index=""
gpu_selected=false
skip_install=false
check_only=false
# Bash 3.2 treats empty arrays as unset under set -u; use guarded expansions below.
session_args=()
argument_error() { echo "$*" >&2; exit 3; }
# Wrapper flags may occur anywhere; device flags reach the session unchanged.
while (($#)); do
  case "$1" in
    --skip-install) skip_install=true; shift ;;
    --check-only) check_only=true; shift ;;
    --probe-timeout-s)
      (($# >= 2)) || argument_error "probe timeout missing"
      probe_timeout="$2"; shift 2 ;;
    --gpu-index|--gpu-indices)
      (($# >= 2)) || argument_error "GPU selection missing"
      gpu_indices="$2"; gpu_selected=true
      session_args+=("$1" "$2"); shift 2 ;;
    --monitor-gpu-index)
      (($# >= 2)) || argument_error "monitor GPU index missing"
      monitor_index="$2"; session_args+=("$1" "$2"); shift 2 ;;
    *) session_args+=("$1"); shift ;;
  esac
done
[[ -n "$probe_timeout" ]] || argument_error "Set JOULEWISE_PROBE_TIMEOUT_S or --probe-timeout-s"
if ! $gpu_selected && [[ -n "${JOULEWISE_GPU_INDICES:-}" ]]; then
  gpu_indices="$JOULEWISE_GPU_INDICES"
  session_args=(--gpu-indices "$gpu_indices" ${session_args[@]+"${session_args[@]}"})
fi
if $skip_install && [[ -x "$venv_dir/bin/python" ]]; then
  python_bin="$venv_dir/bin/python"
  export PATH="$venv_dir/bin:$PATH"
fi
cd -- "$repo_root"
"$python_bin" -c 'import sys; assert sys.version_info >= (3, 11), "Python >=3.11 required"'
layout=""
if ! $check_only; then
  # Stdlib-only validation runs before inventory, venv creation or installation.
  layout=$("$python_bin" -m joulewise.align.gpukit.session --validate-only ${session_args[@]+"${session_args[@]}"})
else
  [[ -n "$gpu_indices" ]] || argument_error "Select GPUs for --check-only"
fi
"$python_bin" -c '
import json, math, sys
from joulewise.align.gpukit.session import IsolationError, whole_gpu
try:
    timeout = float(sys.argv[1])
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("probe timeout must be finite and positive")
    if sys.argv[2]:
        layout = json.loads(sys.argv[2])
        indices = layout["measured_gpu_indices"]
        if layout["monitor_gpu_index"] is not None:
            indices = [*indices, layout["monitor_gpu_index"]]
    else:
        indices = [int(i) for group in sys.argv[3:] for i in group.split(",") if i]
    if not indices or any(i < 0 for i in indices):
        raise ValueError("GPU indices must be nonnegative")
except (ValueError, KeyError, TypeError) as exc:
    print(str(exc), file=sys.stderr)
    raise SystemExit(3)
try:
    print(json.dumps([whole_gpu(gpu_index=i, timeout_s=timeout) for i in dict.fromkeys(indices)]))
except IsolationError as exc:
    print(str(exc), file=sys.stderr)
    raise SystemExit(2)
' "$probe_timeout" "$layout" "$gpu_indices" "$monitor_index" >&2
if $check_only; then
  exit 0
fi
if ! $skip_install; then
  "$python_bin" -m venv "$venv_dir"
  python_bin="$venv_dir/bin/python"
  "$python_bin" -m pip install 'vllm==0.10.2'
  "$python_bin" -m pip install --no-deps "$repo_root"
  export PATH="$venv_dir/bin:$PATH"
fi
exec "$python_bin" -m joulewise.align.gpukit.session ${session_args[@]+"${session_args[@]}"}
