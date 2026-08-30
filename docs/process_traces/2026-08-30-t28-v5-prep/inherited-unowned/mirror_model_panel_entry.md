# Mirror and admit the D-164 model-panel entries

Run these commands from the measurement checkout. `hf download --local-dir` creates the same `.cache/huggingface/download/*.metadata` records and `.cache/huggingface/trees/<revision>.json` provenance receipt carried by the existing local mirrors.

```sh
/Users/edr/code/JouleWise/.venv/bin/hf download mlx-community/Qwen3-1.7B-4bit --revision 3b1b1768f8f8cf8351c712464f906e86c2b8269e --local-dir /Users/edr/jw_models/mlx-community/Qwen3-1.7B-4bit
/Users/edr/code/JouleWise/.venv/bin/hf download mlx-community/Qwen3-8B-4bit --revision 545dc4251c05440727734bcd94334791f6ab0192 --local-dir /Users/edr/jw_models/mlx-community/Qwen3-8B-4bit
```

The recorded revisions must be present at these exact paths before admission:

```sh
test -f /Users/edr/jw_models/mlx-community/Qwen3-1.7B-4bit/.cache/huggingface/trees/3b1b1768f8f8cf8351c712464f906e86c2b8269e.json
test -f /Users/edr/jw_models/mlx-community/Qwen3-8B-4bit/.cache/huggingface/trees/545dc4251c05440727734bcd94334791f6ab0192.json
```

Then create the desk admission receipts:

```sh
/Users/edr/code/JouleWise/.venv/bin/python scripts/admit_model_panel_entry.py --panel configs/model_panels/qwen3_4bit.json --model-id qwen3-1p7b --out /tmp/qwen3-1p7b-admission.json
/Users/edr/code/JouleWise/.venv/bin/python scripts/admit_model_panel_entry.py --panel configs/model_panels/qwen3_4bit.json --model-id qwen3-8b --out /tmp/qwen3-8b-admission.json
```

These commands do not load a model. D-074 still requires the measurement machine to run the three-repeat generation/determinism check, the G10 peak-memory-cap check, and KV-cache receipts. Only after those gates pass should the panel entries be changed from `pending` to `admitted` in a separately reviewed data edit.
