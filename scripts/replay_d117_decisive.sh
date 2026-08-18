#!/bin/sh
# One-command replay of the D-117 v2 decisive production proof (cold-gate
# ruling 2026-08-11, condition C2): download-by-descriptor -> sha verify ->
# governed hydrate -> census byte-compare -> run the single decisive test
# with the no-skip flag. Takes hours (3h35m on an M3 Max). Run from a clean
# checkout of the head under test.
set -eu

REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)
if [ "$#" -lt 1 ]; then
  echo "usage: $0 <work-dir-outside-the-repository>" >&2
  echo "(the governed hydrator refuses destinations inside the repo, so no in-repo default exists)" >&2
  exit 2
fi
WORK=$1
DESCRIPTOR="$REPO_ROOT/tests/fixtures/d117_v2_production/transport_descriptor.json"
CENSUS="$REPO_ROOT/tests/fixtures/d117_v2_production/custody_store/manifest.json"

mkdir -p "$WORK"
ASSET=$(python3 -c "import json;print(json.load(open('$DESCRIPTOR'))['asset_name'])")
TAG=$(python3 -c "import json;print(json.load(open('$DESCRIPTOR'))['release_tag'])")
SHA=$(python3 -c "import json;print(json.load(open('$DESCRIPTOR'))['archive_sha256'])")
REPO_SLUG=$(git -C "$REPO_ROOT" remote get-url origin | sed -E 's#.*[:/]([^/]+/[^/.]+)(\.git)?$#\1#')

echo "== 1/5 anonymous download: $ASSET from release $TAG"
curl --fail --location --retry 3 \
  "https://github.com/$REPO_SLUG/releases/download/$TAG/$ASSET" \
  --output "$WORK/$ASSET"

echo "== 2/5 digest gate"
OBSERVED=$(shasum -a 256 "$WORK/$ASSET" | cut -d' ' -f1)
[ "$OBSERVED" = "$SHA" ] || { echo "SHA MISMATCH: $OBSERVED != $SHA"; exit 1; }

echo "== 3/5 governed hydration"
python3 "$REPO_ROOT/scripts/hydrate_d117_fixture.py" \
  --archive "$WORK/$ASSET" --descriptor "$DESCRIPTOR" \
  --census "$CENSUS" --destination "$WORK/store"

echo "== 4/5 census byte-compare"
cmp "$CENSUS" "$WORK/store/manifest.json"

echo "== 5/5 decisive test (hours; output buffered until completion)"
cd "$REPO_ROOT"
JOULEWISE_D117_CUSTODY_STORE="$WORK/store" \
JOULEWISE_REQUIRE_D117_FULL_FIXTURE=1 \
"${PYTHON:-python3}" -m unittest -v \
  tests.test_mint_floor_artifact_generalized.V2PinsetAndMintTests.test_coordinated_report_and_pin_change_refuses_against_floor_evidence
echo "DECISIVE REPLAY: OK"
