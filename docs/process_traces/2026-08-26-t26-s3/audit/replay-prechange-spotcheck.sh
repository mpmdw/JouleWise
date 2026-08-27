#!/bin/sh
set -eu

source_repo=$(git rev-parse --show-toplevel)
test "$(git -C "$source_repo" rev-parse HEAD)" = 2fd7c920314333535ea2631bec887a19b964f834
audit_tmp=$(mktemp -d /private/tmp/jw-audit-prechange.XXXXXX)
trap 'rm -rf -- "$audit_tmp"' EXIT HUP INT TERM

git clone -q --shared "$source_repo" "$audit_tmp/repository"
cp "$source_repo/tests/test_arm_readiness_evidence_packauth.py" \
  "$audit_tmp/repository/tests/test_arm_readiness_evidence_packauth.py"
cp "$source_repo/tests/test_receipt_histsem.py" \
  "$audit_tmp/repository/tests/test_receipt_histsem.py"
cd "$audit_tmp/repository"

/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest -v \
  tests.test_arm_readiness_evidence_packauth.ProjectedPackAuthenticationTests.test_preserve_authentication_refuses_canonical_committed_freeze_receipt_tamper_with_regenerated_sidecar \
  tests.test_arm_readiness_evidence_packauth.ProjectedPackAuthenticationTests.test_stale_current_frozen_receipt_constant_is_detected_but_not_an_authentication_dependency \
  tests.test_arm_readiness_evidence_packauth.ProjectedPackAuthenticationTests.test_projected_pack_authentication_uses_no_preserve_anchor_when_constant_is_stale \
  tests.test_receipt_histsem.PackAuthenticationRegenerationTests.test_recorded_anchor_replay_refuses_unresolvable_or_off_lineage_commit
