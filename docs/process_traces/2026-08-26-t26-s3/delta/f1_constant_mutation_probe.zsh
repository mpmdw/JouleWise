#!/bin/zsh
set -eu

root=$(git rev-parse --show-toplevel)
probe_root=$(mktemp -d "${TMPDIR:-/tmp}/joulewise-f1-mutation.XXXXXX")
trap 'find "$probe_root" -depth -delete' EXIT
repository="$probe_root/repository"
mkdir -p "$repository"
git -C "$root" archive HEAD | tar -x -C "$repository"
cp "$root/joulewise/arm_readiness.py" "$repository/joulewise/arm_readiness.py"
cp "$root/joulewise/arm_readiness_evidence.py" "$repository/joulewise/arm_readiness_evidence.py"
cp "$root/tests/test_arm_readiness_evidence_packauth.py" "$repository/tests/test_arm_readiness_evidence_packauth.py"
git -C "$repository" init -q
git -C "$repository" config user.name 'delta mutation probe'
git -C "$repository" config user.email 'delta-mutation@invalid'
git -C "$repository" add -A
git -C "$repository" commit -qm 'current audited tree'

perl -0pi -e 's/(    capability = _generator_preserve_capability\(raw, kind=kind\)\n)/$1    _constant, _status = _generator_frozen_receipt_constant(raw)\n    if _status != "absent":\n        raise _underivable(kind, "mutation: frozen-receipt constant controls authentication")\n/' \
  "$repository/joulewise/arm_readiness_evidence.py"
git -C "$repository" add joulewise/arm_readiness_evidence.py
git -C "$repository" commit -qm 'mutation: restore constant-dependent refusal'

set +e
(cd "$repository" && /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest \
  tests.test_arm_readiness_evidence_packauth.ProjectedPackAuthenticationTests.test_frozen_receipt_constant_variants_do_not_change_the_authentication_verdict) \
  >"$probe_root/test.log" 2>&1
rc=$?
set -e
tail -4 "$probe_root/test.log"
printf 'MUTATION_TEST_RC=%s\n' "$rc"
test "$rc" -ne 0
