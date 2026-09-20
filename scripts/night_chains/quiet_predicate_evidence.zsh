#!/bin/zsh
# QPE-01 idle-only pilot. The sealed protocol owns every timing parameter.
set -euo pipefail
cd "${0:A:h:h:h}"
export NIGHT_PAYLOAD_KIND=quiet_predicate_evidence
: "${PY:?required}"
: "${EVIDENCE_PLAN_PATH:?required}"
: "${EVIDENCE_MANIFEST_SHA256:?required}"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$PWD"
if [[ "${NIGHT_VERIFY_ONLY:-0}" == 1 ]]; then
    exec "$PY" -B -m joulewise.quiet_predicate_campaign verify
fi
# The executor supervises collector, recorder and sampler process groups and
# journals their identities and bounded cleanup before returning an exit code.
exec "$PY" -B -m joulewise.quiet_predicate_campaign run
