"""The daily radar is a snapshot, while reviewed papers need a durable queue."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import cards


class CardQueueTests(unittest.TestCase):
    def test_reviews_survive_radar_rotation_and_latest_decision_wins(self):
        with tempfile.TemporaryDirectory() as directory:
            audits = Path(directory)
            (audits / "audit-20260901T000000Z.json").write_text(json.dumps({
                "discovery_entries": [{"id": "2609.00001", "published": "2026-09-01", "authors": ["Author"]}],
                "candidates": [
                    {"arxiv_id": "2609.00001", "title": "Old review", "decision": "review"},
                    {"arxiv_id": "2609.00002", "title": "Withdrawn review", "decision": "review"},
                ],
            }), encoding="utf-8")
            (audits / "audit-20260902T000000Z.json").write_text(json.dumps({
                "candidates": [{"arxiv_id": "2609.00002", "title": "Withdrawn review", "decision": "archive"}],
            }), encoding="utf-8")
            radar = {"papers": [{"id": "2609.00003", "title": "Today's review", "decision": "review", "arxivUrl": "https://arxiv.org/abs/2609.00003"}]}
            state = {"catalog": [], "paper_ids": set(), "titles": set()}
            with patch.object(cards, "AUDITS_DIR", audits):
                pending = cards.select_candidates(radar, state, 10, ["review"], None)
                self.assertEqual([p["id"] for p in pending], ["2609.00001", "2609.00003"])
                self.assertEqual(pending[0]["authors"], ["Author"])
                self.assertEqual(pending[0]["published"], "2026-09-01")
                state["paper_ids"].add("2609.00001")
                self.assertEqual([p["id"] for p in cards.select_candidates(radar, state, 10, ["review"], None)], ["2609.00003"])

    def test_missing_historical_metadata_fetched_from_hf(self):
        paper = {"id": "2609.00001", "title": "Old review"}
        response = json.dumps({"publishedAt": "2026-09-01", "authors": [{"name": "A"}, {"name": "B"}]}).encode()
        with patch.object(cards, "http_get", return_value=response):
            completed = cards.complete_metadata(paper)
        self.assertEqual(completed["authors"], ["A", "B"])
        self.assertEqual(completed["published"], "2026-09-01")
        self.assertEqual(paper, {"id": "2609.00001", "title": "Old review"})


if __name__ == "__main__":
    unittest.main()
