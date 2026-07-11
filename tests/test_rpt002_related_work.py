"""Offline bibliography and positioning-boundary tests for RPT-002."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "docs" / "report_src"
PROPOSAL = REPO / "docs" / "JouleWise_Hardening_Proposal.md"
DRAFT = REPO / "docs" / "phase_4" / "related_work_draft.md"
CHAPTER = SRC / "chapters" / "03_background_and_related_work.md"

RPT002_IDS = {
    "revisiting-disaggregation-energy-2026": "2601.08833",
    "dualscale-2026": "2602.18755",
    "prima-cpp-2025": "2504.08791",
    "splitzip-2026": "2605.01708",
    "systematic-quantization-2025": "2508.16712",
    "sustainable-edge-ai-2025": "2504.03360",
    "silicon-showdown-2026": "2605.00519",
}
PRIMARY_URLS = {
    "revisiting-disaggregation-energy-2026":
        "https://doi.org/10.1145/3805621.3807662",
    "dualscale-2026": "https://arxiv.org/abs/2602.18755v3",
    "prima-cpp-2025": "https://arxiv.org/abs/2504.08791v3",
    "splitzip-2026": "https://arxiv.org/abs/2605.01708v3",
    "systematic-quantization-2025": "https://arxiv.org/abs/2508.16712",
    "sustainable-edge-ai-2025": "https://arxiv.org/abs/2504.03360",
    "silicon-showdown-2026": "https://arxiv.org/abs/2605.00519v2",
}
ARXIV_ONLY_IDS = {
    "dualscale-2026", "splitzip-2026", "systematic-quantization-2025",
    "sustainable-edge-ai-2025", "silicon-showdown-2026",
}
INHERITED_IDS = {
    "joulesort2007", "splitwise-isca2024", "distserve", "mooncake",
    "mlperf_power", "zeus", "tokenpowerbench", "mlenergy_benchmark",
    "intelligence_per_watt", "bench360", "chung2026joules",
}


def load_script(name: str, filename: str):
    path = REPO / "scripts" / filename
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


build_capstone = load_script("rpt002_build_capstone", "build_capstone.py")


class TestRpt002RelatedWork(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.profile = json.loads((SRC / "report.json").read_text(encoding="utf-8"))
        cls.bibliography = json.loads(
            (SRC / "references.csl.json").read_text(encoding="utf-8")
        )
        cls.source_map = json.loads(
            (SRC / "source_map.json").read_text(encoding="utf-8")
        )
        cls.by_id = {item["id"]: item for item in cls.bibliography}
        cls.sources = {item["id"]: item for item in cls.source_map["sources"]}

    def test_json_profiles_and_build_validator(self) -> None:
        self.assertEqual(self.profile["bibliography"], "references.csl.json")
        self.assertEqual(self.profile["source_map"], "source_map.json")
        self.assertEqual(
            self.source_map["schema"], "joulewise.report_source_map.v1"
        )
        build_capstone.validate_bibliography(self.profile)

    def test_csl_ids_are_unique_and_required_sets_are_present(self) -> None:
        ids = [item.get("id") for item in self.bibliography]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), INHERITED_IDS | set(RPT002_IDS))
        for item in self.bibliography:
            self.assertIsInstance(item.get("id"), str)
            self.assertTrue(item["id"])
            self.assertIsInstance(item.get("type"), str)
            self.assertIsInstance(item.get("title"), str)
            for field in ("URL", "DOI"):
                if field in item:
                    self.assertIsInstance(item[field], str)

    def test_seven_primary_urls_and_statuses_are_pinned(self) -> None:
        self.assertEqual(set(self.sources), set(RPT002_IDS))
        for source_id in RPT002_IDS:
            source = self.sources[source_id]
            expected_url = PRIMARY_URLS[source_id]
            self.assertEqual(source["primary_url"], expected_url)
            self.assertEqual(self.by_id[source_id]["URL"], expected_url)
            self.assertEqual(
                source["verification_status"], "VERIFIED_AGAINST_PRIMARY"
            )
            self.assertEqual(source["retrieval_date"], "2026-07-11")
            self.assertIn(expected_url, source["verified_primary_urls"])
            self.assertTrue(source["claim_role"])
            self.assertTrue(source["scope_boundary"])
            self.assertTrue(source["artifact_status"])
            self.assertTrue(source["verification_result"])
            self.assertTrue(source["evidence_locations"])
            self.assertTrue(source["feeds"])
            self.assertTrue(source["lead_verification_required"])
            self.assertTrue(all(
                check.startswith("COMPLETED:")
                for check in source["lead_verification_required"]
            ))

    def test_status_transition_records_completed_verification(self) -> None:
        transition = self.source_map["status_transition"]
        self.assertEqual(transition["field"], "verification_status")
        self.assertEqual(transition["current"], "VERIFIED_AGAINST_PRIMARY")
        self.assertEqual(transition["verified_value"], "VERIFIED_AGAINST_PRIMARY")
        self.assertEqual(self.source_map["retrieval_date"], "2026-07-11")
        for source in self.sources.values():
            self.assertIn("verification_status", source)
            self.assertNotIn("verified", source)
            self.assertNotIn("verification", source)

    def test_every_proposal_arxiv_id_is_mapped(self) -> None:
        proposal = PROPOSAL.read_text(encoding="utf-8")
        for arxiv_id in RPT002_IDS.values():
            self.assertIn(f"https://arxiv.org/abs/{arxiv_id}", proposal)
        for source in self.sources.values():
            for location in source["evidence_locations"]:
                self.assertEqual(
                    location["path"], "docs/JouleWise_Hardening_Proposal.md"
                )
                self.assertTrue(location["locator"])

    def test_all_report_citations_resolve(self) -> None:
        cited = set()
        for rel in self.profile["chapters"]:
            text = (SRC / rel).read_text(encoding="utf-8")
            cited.update(re.findall(r"@([A-Za-z0-9_.:-]+)", text))
        self.assertEqual(cited, set(self.by_id))

    def test_verified_claims_retain_required_boundaries_and_novelty_wording(self) -> None:
        draft = DRAFT.read_text(encoding="utf-8")
        chapter = CHAPTER.read_text(encoding="utf-8")
        for text in (draft, chapter):
            normalized = " ".join(text.lower().split())
            self.assertNotIn("UNVERIFIED_BY_SESSION", text)
            self.assertIn("VERIFIED_AGAINST_PRIMARY", text)
            self.assertIn(
                "does not claim to originate energy-aware disaggregated inference",
                normalized,
            )
            self.assertIn(
                "per-stage both-end split, boundary-labeled discipline, "
                "re-reducible bundles",
                normalized,
            )
            self.assertIn("single raspberry pi 4", normalized)
            self.assertIn("cpu-only", normalized)
            self.assertIn("ecosystem-as-deployed", normalized)
            self.assertRegex(normalized, r"23x .*crosses unmatched")
        intake = chapter.split("## 2026 positioning intake and novelty boundary", 1)[1]
        for source_id in RPT002_IDS:
            self.assertIn(f"@{source_id}", intake)
        self.assertNotIn("first to measure", chapter.lower())
        self.assertNotIn("no surveyed work", chapter.lower())

    def test_corrected_metadata_types_authors_and_dates(self) -> None:
        revisiting = self.by_id["revisiting-disaggregation-energy-2026"]
        self.assertEqual(revisiting["type"], "paper-conference")
        self.assertEqual(len(revisiting["author"]), 5)
        self.assertEqual(revisiting["page"], "397-406")
        self.assertEqual(revisiting["DOI"], "10.1145/3805621.3807662")
        self.assertEqual(revisiting["issued"]["date-parts"], [[2026, 4, 27]])

        prima = self.by_id["prima-cpp-2025"]
        self.assertEqual(
            prima["title"],
            "Prima.cpp: Fast 30-70B LLM Inference on Heterogeneous and "
            "Low-Resource Home Clusters",
        )
        self.assertEqual(prima["type"], "paper-conference")
        self.assertEqual(prima["version"], "v3")
        self.assertEqual(len(prima["author"]), 11)
        self.assertEqual(prima["issued"]["date-parts"], [[2026, 7, 4]])
        self.assertIn("ICLR 2026", prima["container-title"])

        expected_author_counts = {
            "dualscale-2026": 4,
            "splitzip-2026": 2,
            "systematic-quantization-2025": 2,
            "sustainable-edge-ai-2025": 8,
            "silicon-showdown-2026": 2,
        }
        for source_id in ARXIV_ONLY_IDS:
            record = self.by_id[source_id]
            self.assertEqual(record["type"], "article")
            self.assertEqual(record["genre"], "preprint")
            self.assertEqual(len(record["author"]), expected_author_counts[source_id])

    def test_verified_artifact_and_claim_corrections_are_locked(self) -> None:
        source_text = json.dumps(self.source_map, ensure_ascii=False).lower()
        chapter = " ".join(CHAPTER.read_text(encoding="utf-8").lower().split())
        self.assertIn("no artifact was released", source_text)
        self.assertIn("none released", source_text)
        self.assertIn("stated available", source_text)
        self.assertIn("released under cc by 4.0", source_text)
        self.assertIn("it reports no energy measurement", chapter)
        self.assertIn("gpu-only", chapter)
        self.assertIn("no rigorous-uncertainty claim", chapter)
        self.assertIn("releases no artifact", chapter)


if __name__ == "__main__":
    unittest.main()
