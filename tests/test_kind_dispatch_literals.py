"""Source guard for idle literals in shared night-kind dispatch code."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
FILES = (
    'joulewise/evidence_night.py',
    'scripts/gen_evidence_night.py',
    'joulewise/night_gate.py',
    'joulewise/night_agent_install.py',
    'scripts/run_night.py',
    'joulewise/zero_capture_facts.py',
)
TOKENS = re.compile(r"quiet_predicate_evidence|QPE01|qpe01|evidence_manifest\.json|EVIDENCE_")
# Each allowed line is pinned exactly; new literals need a reviewed reason.
ALLOW = {
    ('joulewise/evidence_night.py', 28): ('KIND = kind_row("quiet_predicate_evidence").kind', 'Explicit idle default for a legacy caller without a candidate plan.'),
    ('joulewise/evidence_night.py', 271): ('    if sha!=night_gate.QPE01_PILOT_REGISTRATION_SHA256: raise ValueError(check)', 'Ruled idle registration constant or historical digest entry; no new digest is admitted.'),
    ('joulewise/evidence_night.py', 278): ("    if not (json.loads((Path(p.custody_root)/'evidence_manifest.json').read_text())==manifest_for(p)): raise ValueError(check)", 'Idle manifest verifier in the sealed clone; other rows refuse before this handler.'),
    ('joulewise/evidence_night.py', 282): ("    if not (night_gate.chain_literal(text,'EVIDENCE_CHAIN_SOURCE_SHA256')==source): raise ValueError(check)", 'Idle wrapper export verified by the approved evidence handler.'),
    ('joulewise/evidence_night.py', 286): ("    if not (night_gate.chain_literal(text,'EVIDENCE_PLAN_PATH')==str(Path(p.custody_root)/'night_plan.json')): raise ValueError(check)", 'Idle wrapper export verified by the approved evidence handler.'),
    ('joulewise/evidence_night.py', 314): ('            or night_gate.chain_literal(raw.decode("utf-8"), "EVIDENCE_CHAIN_SOURCE_SHA256")', 'Idle wrapper export verified by the approved evidence handler.'),
    ('joulewise/evidence_night.py', 1096): ("    `probe_payload_kind` of the plan's chain says `quiet_predicate_evidence`", 'Idle executor compatibility reference.'),
    ('joulewise/night_gate.py', 8): ('``binds_chain``, the zsh chain source named by ``EVIDENCE_CHAIN_PATH``. It', 'Historical idle protocol explanation or recorder compatibility comment.'),
    ('joulewise/night_gate.py', 60): ('# binds EVIDENCE_CHAIN_PATH, never a Python module): the cured Python is', 'Historical idle protocol explanation or recorder compatibility comment.'),
    ('joulewise/night_gate.py', 63): ('# 2026-09-23 (cold gate QPE01-DAEMON-CONTAMINATION-01, rulings 10 and 31;', 'Historical idle protocol explanation or recorder compatibility comment.'),
    ('joulewise/night_gate.py', 69): ('QPE01_PILOT_REGISTRATION_PATH = kind_row("quiet_predicate_evidence").protocol_path', 'Ruled idle registration constant or historical digest entry; no new digest is admitted.'),
    ('joulewise/night_gate.py', 70): ('QPE01_PILOT_REGISTRATION_SHA256 = "69321c693b3370b949b0a4a1b8548e35dd081a36165ba8f6799a387c2d813616"', 'Ruled idle registration constant or historical digest entry; no new digest is admitted.'),
    ('joulewise/night_gate.py', 75): ('QPE01_PILOT_REGISTRATION_V2_SHA256 = "2c5392401a7956dfbb30f316a084541e0f53f214a4ce98c7d56d595ddb2779f1"', 'Ruled idle registration constant or historical digest entry; no new digest is admitted.'),
    ('joulewise/night_gate.py', 81): ('QPE01_PILOT_REGISTRATION_V1_SHA256 = "f59804a9a28b2145f7bb8e91a8f0fe11b21ae6728cee70d8e943fe52a46da6f6"', 'Ruled idle registration constant or historical digest entry; no new digest is admitted.'),
    ('joulewise/night_gate.py', 82): ('EVIDENCE_CHAIN_PATH = kind_row("quiet_predicate_evidence").chain_source_path', 'Published idle chain path constant retained for compatibility.'),
    ('joulewise/night_gate.py', 95): ('    QPE01_PILOT_REGISTRATION_V1_SHA256: {"label": "QPE-01 idle-variance pilot protocol v1",', 'Ruled idle registration constant or historical digest entry; no new digest is admitted.'),
    ('joulewise/night_gate.py', 97): ('        "superseded_by": QPE01_PILOT_REGISTRATION_V2_SHA256,', 'Ruled idle registration constant or historical digest entry; no new digest is admitted.'),
    ('joulewise/night_gate.py', 100): ('    QPE01_PILOT_REGISTRATION_V2_SHA256: {"label": "QPE-01 idle-variance pilot protocol v2 (A269 gate 2026-09-22)",', 'Ruled idle registration constant or historical digest entry; no new digest is admitted.'),
    ('joulewise/night_gate.py', 103): ('        "superseded_by": QPE01_PILOT_REGISTRATION_SHA256,', 'Ruled idle registration constant or historical digest entry; no new digest is admitted.'),
    ('joulewise/night_gate.py', 108): ('    QPE01_PILOT_REGISTRATION_SHA256: {', 'Ruled idle registration constant or historical digest entry; no new digest is admitted.'),
    ('joulewise/night_gate.py', 109): ('        "label": "QPE-01 idle-variance pilot protocol v3 (QPE01-DAEMON-CONTAMINATION-01 gate 2026-09-23)",', 'Historical idle registration or predicate record.'),
    ('joulewise/night_gate.py', 112): ('                  "QPE01-DAEMON-CONTAMINATION-01 ruling 10 (2026-09-23) Q1(c)/Q2/Q3(a), "', 'Historical idle registration or predicate record.'),
    ('joulewise/night_gate.py', 183): ('# Cold gate 10 QPE01-DAEMON-CONTAMINATION-01 (2026-09-23) Q2(i).  The night of', 'Historical idle protocol explanation or recorder compatibility comment.'),
    ('joulewise/night_gate.py', 336): ('    # QPE01-DAEMON-CONTAMINATION-01, 2026-09-23, Q2(i)).  It is not one argv,', 'Historical idle protocol explanation or recorder compatibility comment.'),
    ('joulewise/night_gate.py', 1060): ('                      and Path(item["path"]).parent == Path(t0_author._EVIDENCE_DIRECTORY)]', 'Idle recorder or wrapper environment compatibility literal.'),
    ('joulewise/night_gate.py', 1062): ('    expected_paths = {str(pack_custody / t0_author._EVIDENCE_DIRECTORY / t0_author._receipt_name(row)) for row in t0_author._EXPECTED_ROWS}', 'Idle recorder or wrapper environment compatibility literal.'),
    ('joulewise/night_gate.py', 1400): ('                if (chain_literal(chain_text, "EVIDENCE_CHAIN_SOURCE_SHA256") != measured or', 'Idle wrapper export verified by the approved evidence handler.'),
    ('joulewise/night_gate.py', 1572): ('        # QPE01-DAEMON-CONTAMINATION-01, 2026-09-23, Q2(i)), on BOTH branches', 'Historical idle protocol explanation or recorder compatibility comment.'),
    ('joulewise/night_agent_install.py', 909): ('    if night_gate.chain_literal(chain.read_text(), "EVIDENCE_PLAN_PATH") != str(published_plan_path):', 'Idle wrapper export verified by the approved evidence handler.'),
    ('joulewise/night_agent_install.py', 1187): ('            if night_gate.chain_literal(chain_text, "EVIDENCE_PLAN_PATH") != str(Path(plan.custody_root) / "night_plan.json"):', 'Idle wrapper export verified by the approved evidence handler.'),
    ('scripts/run_night.py', 70): ('# equal (`sample_quiet_predicate_evidence.REPLAY_ENV`), which is the property', 'Historical idle protocol explanation or recorder compatibility comment.'),
    ('scripts/run_night.py', 73): ('REPLAY_RECORDER_ENV = "EVIDENCE_POWER_RECORDER_REPLAY"', 'Idle recorder or wrapper environment compatibility literal.'),
    ('scripts/run_night.py', 590): ('    # Q7; brief D6).  The bench driver sets EVIDENCE_POWER_RECORDER_REPLAY in', 'Historical idle protocol explanation or recorder compatibility comment.'),
    ('scripts/run_night.py', 622): ('    environment.pop("EVIDENCE_PROCESS_JOURNAL", None)', 'Idle recorder or wrapper environment compatibility literal.'),
    ('scripts/run_night.py', 1010): ('        return kind_row("quiet_predicate_evidence")', 'Explicit idle default for a legacy caller without a candidate plan.'),
    ('scripts/run_night.py', 1015): ('    row = _custody_row(plan) if plan is not None else kind_row("quiet_predicate_evidence")', 'Explicit idle default for a legacy caller without a candidate plan.'),
    ('scripts/run_night.py', 2341): ('                    if os.environ.get("EVIDENCE_PROCESS_JOURNAL"):', 'Idle recorder or wrapper environment compatibility literal.'),
}


class KindDispatchLiteralTests(unittest.TestCase):
    def test_only_reviewed_idle_literals_remain_in_shared_dispatch(self):
        found = set()
        for name in FILES:
            for number, line in enumerate((ROOT / name).read_text().splitlines(), 1):
                if not TOKENS.search(line):
                    continue
                key = (name, number)
                self.assertIn(key, ALLOW, f"unreviewed idle literal: {name}:{number}: {line}")
                expected, reason = ALLOW[key]
                self.assertEqual(line, expected)
                self.assertTrue(reason and "\n" not in reason)
                found.add(key)
        self.assertEqual(found, set(ALLOW), "stale idle literal allowlist entry")
