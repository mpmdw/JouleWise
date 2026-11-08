#!/bin/zsh
# sequential per-model headers then kv; deadline guards
W=/Users/edr/code/JouleWise-wt-af419-kv
PY=/Users/edr/code/JouleWise/.venv/bin/python
export PYTHONDONTWRITEBYTECODE=1
REC=$W/configs/bytes/records
mkdir -p $REC
HF=/Users/edr/.cache/huggingface/hub
JW=/Users/edr/jw_models/mlx-community
DEADLINE=$(date -j -f "%Y-%m-%d %H:%M:%S" "2026-10-20 16:58:00" +%s)
SKIPBIG=$(date -j -f "%Y-%m-%d %H:%M:%S" "2026-10-20 16:50:00" +%s)
# name|dir|revision|big
rows=(
"Qwen3-1.7B-4bit|$JW/Qwen3-1.7B-4bit|3b1b1768f8f8cf8351c712464f906e86c2b8269e|0"
"Qwen3-4B-4bit|$JW/Qwen3-4B-4bit|4dcb3d101c2a062e5c1d4bb173588c54ea6c4d25|0"
"Qwen3-8B-4bit|$JW/Qwen3-8B-4bit|545dc4251c05440727734bcd94334791f6ab0192|0"
"Qwen3-14B-4bit|$HF/models--mlx-community--Qwen3-14B-4bit/snapshots/a4d9b2df59d2c150bef02fcbe0d91046b7ca33a4|a4d9b2df59d2c150bef02fcbe0d91046b7ca33a4|0"
"Qwen3-30B-A3B-4bit|$HF/models--mlx-community--Qwen3-30B-A3B-4bit/snapshots/d388dead1515f5e085ef7a0431dd8fadf0886c57|d388dead1515f5e085ef7a0431dd8fadf0886c57|0"
"Qwen3-32B-4bit|$HF/models--mlx-community--Qwen3-32B-4bit/snapshots/bcaaf7f538adf166c1080a2befdb4f6019f66639|bcaaf7f538adf166c1080a2befdb4f6019f66639|0"
"Llama-3.3-70B-Instruct-4bit|$HF/models--mlx-community--Llama-3.3-70B-Instruct-4bit/snapshots/de2dfaf56839b7d0e834157d2401dee02726874d|de2dfaf56839b7d0e834157d2401dee02726874d|1"
"Qwen3-Next-80B-A3B-Instruct-4bit|$HF/models--mlx-community--Qwen3-Next-80B-A3B-Instruct-4bit/snapshots/d8a069bfa8ae87d3d468412e1034acae19b5892b|d8a069bfa8ae87d3d468412e1034acae19b5892b|1"
"Qwen3.5-122B-A10B-4bit|$JW/Qwen3.5-122B-A10B-4bit|e9c67b08899964be5fdd069bb1b4bc8907fe68f5|1"
)
for row in $rows; do
  IFS='|' read name dir rev big <<< "$row"
  now=$(date +%s)
  if [ $now -ge $DEADLINE ]; then echo "SKIP $name: past 16:58 ($(date))"; continue; fi
  if [ "$big" = 1 ] && [ $now -ge $SKIPBIG ]; then echo "SKIP $name: big model after 16:50 ($(date))"; continue; fi
  echo "=== $name start $(date)"
  s=$(date +%s)
  $PY $W/scripts/bytes_manifest.py headers --model-dir $dir --revision $rev --out $REC/$name.headers.json || { echo "HEADERS FAIL $name"; continue; }
  now=$(date +%s); left=$((DEADLINE-now))
  TMPDIR=/tmp/af419-kv-tmp perl -e 'alarm shift; exec @ARGV' $left $PY $W/scripts/bytes_manifest.py kv --model-dir $dir --revision $rev --out $REC/$name.kv.json
  rc=$?
  e=$(date +%s)
  echo "=== $name rc=$rc wall_s=$((e-s)) end $(date)"
  echo "$name $((e-s))" >> $REC/.walltimes.txt
done
echo DONE $(date)
