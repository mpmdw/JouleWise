"""Battery records and raw probes have explicit publication classifications."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from joulewise.publication_privacy import PrivacyAuditError, audit_private_bundle


class BatteryPrivacyTests(unittest.TestCase):
    def test_battery_record_and_raw_paths_are_classified_extra_key_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            from tests.test_publication_privacy import PublicationPrivacyTests
            fixture = PublicationPrivacyTests("test_canonical_tree_identity_algorithm_is_versioned_and_stable")
            fixture.tmp = Path(tmp)
            bundle = fixture.make_secret_bundle()
            metadata_path = bundle / "metadata.json"
            metadata = json.loads(metadata_path.read_text())
            metadata["battery_float"] = {
                "pre": {"raw_path": "raw/battery_float.pre.ioreg"},
                "post": {"raw_path": "raw/battery_float.post.ioreg"},
            }
            metadata_path.write_text(json.dumps(metadata))
            for phase in ("pre", "post"):
                (bundle / f"raw/battery_float.{phase}.ioreg").write_bytes(b"probe")
            audit_private_bundle(bundle)
            metadata["unclassified_battery_extra"] = "secret"
            metadata_path.write_text(json.dumps(metadata))
            with self.assertRaisesRegex(PrivacyAuditError, "unclassified"):
                audit_private_bundle(bundle)


if __name__ == "__main__":
    unittest.main()
