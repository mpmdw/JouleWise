#!/usr/bin/env bash
# Fresh Ubuntu + NVIDIA driver. No provider API or rental command runs here.
set -euo pipefail
repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd)"
venv_dir="${JOULEWISE_VENV:-$repo_root/.gpukit-venv}"
python_bin="${JOULEWISE_PYTHON:-python3}"
probe_timeout="${JOULEWISE_PROBE_TIMEOUT_S:-}"
gpu_indices="${JOULEWISE_GPU_INDICES:-}"
monitor_index=""
skip_install=false
check_only=false
session_args=()
# Parse wrapper flags anywhere, preserving session arguments as separate argv.
while (($#)); do
  case "$1" in
    --skip-install) skip_install=true; shift ;;
    --check-only) check_only=true; shift ;;
    --probe-timeout-s) probe_timeout="${2:?probe timeout missing}"; shift 2 ;;
    --gpu-index) gpu_indices="${2:?GPU index missing}"; session_args+=("$1" "$2"); shift 2 ;;
    --gpu-indices) gpu_indices="${2:?GPU indices missing}"; session_args+=("$1" "$2"); shift 2 ;;
    --monitor-gpu-index) monitor_index="${2:?monitor GPU index missing}"; session_args+=("$1" "$2"); shift 2 ;;
    *) session_args+=("$1"); shift ;;
  esac
done
: "${probe_timeout:?Set JOULEWISE_PROBE_TIMEOUT_S or --probe-timeout-s}"
: "${gpu_indices:?Set JOULEWISE_GPU_INDICES or --gpu-index/--gpu-indices}"
if $skip_install && [[ -x "$venv_dir/bin/python" ]]; then
  python_bin="$venv_dir/bin/python"
  export PATH="$venv_dir/bin:$PATH"
fi
cd -- "$repo_root"
"$python_bin" -c 'import sys; assert sys.version_info >= (3, 11), "Python >=3.11 required"'
# The same whole-GPU check runs before installation, in either flag order.
"$python_bin" -c '
import json, math, sys
from joulewise.align.gpukit.session import whole_gpu
timeout = float(sys.argv[1])
if not math.isfinite(timeout) or timeout <= 0:
    raise SystemExit("probe timeout must be finite and positive")
indices = [int(i) for group in sys.argv[2:] for i in group.split(",") if i]
print(json.dumps([whole_gpu(gpu_index=i, timeout_s=timeout) for i in dict.fromkeys(indices)]))
' "$probe_timeout" "$gpu_indices" "$monitor_index" >&2
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
# Environment-selected devices also bind the session, unless flags override them.
exec "$python_bin" -m joulewise.align.gpukit.session --gpu-indices "$gpu_indices" "${session_args[@]}"
