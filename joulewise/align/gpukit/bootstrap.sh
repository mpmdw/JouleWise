#!/usr/bin/env bash
# Fresh Ubuntu with NVIDIA driver, Python >=3.11 and venv already available.
# No provider API or rental command runs here. Invoke only after Ed's approval.
set -euo pipefail
repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd)"
venv_dir="${JOULEWISE_VENV:-$repo_root/.gpukit-venv}"
python_bin="${JOULEWISE_PYTHON:-python3}"
if [[ "${1:-}" == "--skip-install" && -x "$venv_dir/bin/python" ]]; then
  python_bin="$venv_dir/bin/python"
  export PATH="$venv_dir/bin:$PATH"
fi
cd -- "$repo_root"
"$python_bin" -c 'import sys; assert sys.version_info >= (3, 11), "Python >=3.11 required"'
if [[ "${1:-}" == "--check-only" ]]; then
  shift
  exec "$python_bin" -c 'import json; from joulewise.align.gpukit.session import whole_gpu; print(json.dumps(whole_gpu(gpu_index=0, timeout_s=30)))'
fi
if [[ "${1:-}" == "--skip-install" ]]; then
  shift
else
  # Verify isolation before spending time installing serving dependencies.
  cd -- "$repo_root"
  "$python_bin" -c 'from joulewise.align.gpukit.session import whole_gpu; whole_gpu(gpu_index=0, timeout_s=30)'
  "$python_bin" -m venv "$venv_dir"
  python_bin="$venv_dir/bin/python"
  "$python_bin" -m pip install 'vllm==0.10.2'
  "$python_bin" -m pip install --no-deps "$repo_root"
  export PATH="$venv_dir/bin:$PATH"
fi
cd -- "$repo_root"
exec "$python_bin" -m joulewise.align.gpukit.session "$@"
