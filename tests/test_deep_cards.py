"""Deep-card pipeline tests: extraction, budgeting, contract, repair and grounding."""
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import cards  # noqa: E402
from content_model import PAPER_DEEP, check_structure, parse_claims, ungrounded_numbers  # noqa: E402

CONFIG = {
    "limit": 2,
    "decisions": ["review"],
    "max_chars": 60000,
    "per_section_chars": 20000,
    "section_source_budget": 20000,
    "sections_per_call": 2,
    "section_tokens": 1000,
    "planning_tokens": 1000,
    "plan_attempts": 2,
    "repair_attempts": 1,
    "max_ungrounded_numbers": 3,
    "review_status": cards.REVIEW_STATUS,
    "target_depth": "deep",
    "enforce": True,
}

MATH_HTML = """<html><head><title>T</title></head><body>
<h2>3 Method</h2><p>We optimise <math alttext="\\mathcal{L}=\\mathbb{E}[r]"><mi>L</mi></math> over trajectories.</p>
<table><tr><th>Bench</th><th>Score</th></tr><tr><td>SWE-bench</td><td>58.04</td></tr></table>
<h2>4 Experiments</h2><p>We report 58.04 on the benchmark with 12 seeds.</p>
</body></html>"""


def compliant_sections(prefix: str = "") -> dict[str, str]:
    """A body that satisfies the paper/deep contract, used as the fake LLM output."""
    filler = "论文的证据只覆盖有限基准与单一模型族，迁移性仍需独立验证；本档案因此把结论标为作者主张，并记录可能推翻它的观察。" * 7
    sections = {}
    for name in PAPER_DEEP:
        if name == "核心主张":
            body = (
                "论文提出三条主张，按证据强度排序如下。\n\n"
                "| # | 主张 | 证据 | 状态 |\n| --- | --- | --- | --- |\n"
                "| C1 | 类别感知专家训练缓解跷跷板效应 | §4.2 表 2 | 作者主张 |\n"
                "| C2 | 标签路由多教师蒸馏提升长尾类别 | §5.1 图 3 | 作者主张 |\n"
                "| C3 | 增益可迁移到未见语言 | 附录 B 表 7 | 存疑 |\n\n"
                "其中 C1 证据最直接，C3 只在一项设置上验证。" + filler
            )
        elif name == "证据与结果":
            body = (
                "| 指标 | 数值 | 设置 | 出处 |\n| --- | --- | --- | --- |\n"
                "| Pro-618 | 58.04 | 主实验 | §4.2 表 2 |\n| SWE-bench Multilingual | 59.00 | 主实验 | §4.2 表 2 |\n\n"
                "消融显示去掉路由后长尾类别下降。" + filler
            )
        elif name == "自测":
            body = "1. 为什么类别跷跷板会出现？\n<details><summary>答案</summary>因为不同类别的优势估计尺度不同。</details>\n" + filler
        else:
            body = f"{prefix}{name} 的完整讨论。" + filler
        sections[name] = body
    return sections


class ExtractionTests(unittest.TestCase):
    def test_parser_keeps_table_rows_and_math_alttext(self):
        parser = cards.PaperParser()
        parser.feed(MATH_HTML)
        parsed = parser.result()
        method = next(section for section in parsed["sections"] if section["title"] == "3 Method")
        self.assertIn("\\mathcal{L}", method["text"])
        self.assertIn("SWE-bench | 58.04", method["text"])
        self.assertEqual(parsed["title"], "T")

    def test_allocate_budget_preserves_paper_order(self):
        sections = [{"title": f"S{index}", "text": "x" * 1000} for index in range(5)]
        allocated = cards.allocate_budget(sections, max_chars=2500, per_section=1000)
        self.assertEqual([section["title"] for section in allocated], ["S0", "S1", "S2"])
        self.assertLessEqual(sum(len(section["text"]) for section in allocated), 2500)


class DeepCardTests(unittest.TestCase):
    def setUp(self):
        self.paper = {"id": "2609.00001", "title": "Fake Paper", "authors": ["A"], "published": "2026-09-01", "arxivUrl": "https://arxiv.org/abs/2609.00001"}
        self.full = {"url": "https://arxiv.org/html/2609.00001", "title": "Fake Paper", "chars": 5000, "sections": [{"title": "Abstract", "text": "We report 58.04 and 59.00."}], "excerpt": "## Abstract\nWe report 58.04 and 59.00 across 12 seeds. Method uses a router."}
        self.evidence = {"problem": "类别跷跷板", "claims": [{"id": "C1", "claim": "x", "evidence": "§4.2", "status": "作者主张"}]}
        self.state = {"ids": {"existing-a", "existing-b", "existing-c"}, "catalog": [], "catalog_ids": set(), "max_order": 45, "records": []}

    def test_deep_card_satisfies_contract(self):
        card, _ = cards.build_deep_card(
            "key", self.paper, self.full, self.state, CONFIG,
            plan=lambda *a, **k: self.evidence,
            draft=lambda api, paper, evidence, names, full, config, extra="": compliant_sections(),
        )
        self.assertEqual(card["violations"], [])
        self.assertGreaterEqual(len(parse_claims(card["body"])), 3)
        self.assertEqual(check_structure("paper", "deep", card["body"], related_count=3), [])
        self.assertGreater(len(card["body"]), 4500)

    def test_repair_pass_fixes_a_thin_draft(self):
        calls = {"n": 0}

        def flaky_draft(api, paper, evidence, names, full, config, extra=""):
            calls["n"] += 1
            if extra:
                return compliant_sections()
            return {name: "太短。" for name in names}

        card, _ = cards.build_deep_card(
            "key", self.paper, self.full, self.state, CONFIG,
            plan=lambda *a, **k: self.evidence,
            draft=flaky_draft,
        )
        self.assertGreater(calls["n"], 4)  # grouped drafts plus one repair pass
        self.assertEqual(card["violations"], [])
        self.assertEqual(check_structure("paper", "deep", card["body"], related_count=3), [])

    def test_ungrounded_numbers_are_detected(self):
        self.assertEqual(ungrounded_numbers("结果是 58.04 分。", self.full["excerpt"]), [])
        found = ungrounded_numbers("在 §4.2 中提升到 91.37，参数量 7B。", self.full["excerpt"])
        self.assertEqual(found, ["91.37"])

    def test_structural_references_are_not_treated_as_data(self):
        body = "见 §4.2 表 2、图 3、Table 7、附录 C 与 C1 主张。"
        self.assertEqual(ungrounded_numbers(body, self.full["excerpt"]), [])

    def test_normalize_card_requires_real_relations(self):
        card = {"summary": "s", "body": compliant_sections()["机制与方法"], "meta": {"related": ["missing-note"]}, "note_id": "new-note"}
        with self.assertRaises(cards.CardError):
            cards.normalize_card(card, self.paper, self.state, CONFIG)
        card["meta"]["related"] = ["existing-a", "existing-b"]
        normalized = cards.normalize_card(card, self.paper, self.state, CONFIG)
        self.assertEqual(normalized["related"], ["existing-a", "existing-b"])

    def test_final_violations_catch_invented_link_and_missing_relations(self):
        card = {"body": compliant_sections()["机制与方法"] + "\n见 [x](https://evil.example/paper)"}
        normalized = {"related": ["only-one"]}
        problems = cards.final_violations("paper", "deep", card, normalized, self.full, CONFIG)
        self.assertTrue(any("URL not present" in item for item in problems))
        self.assertTrue(any("related" in item for item in problems))

    def test_render_note_round_trips_through_frontmatter(self):
        import tempfile

        body = "\n\n".join(f"## {name}\n\n{compliant_sections()[name]}" for name in PAPER_DEEP)
        text = cards.render_note(
            note_id="fake-paper", title="Fake [Paper] #1\n第二行", summary="s", stage="FRONTIER", track="前沿专题",
            order=46, minutes=30, review_status=cards.REVIEW_STATUS, evidence_grade="C",
            objectives=["a"], tags=["t"], source_id="src", related=["existing-a", "existing-b"], prerequisites=[],
            paper=self.paper, full=self.full, body=body, claim_count=3, today="2026-09-25",
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "46-fake-paper.md"
            path.write_text(text, encoding="utf-8")
            data = cards.parse_frontmatter(path)
            # The body must still be split from the frontmatter on the closing marker.
            self.assertIn("## 核心主张", path.read_text(encoding="utf-8").split("\n---\n", 1)[-1])
        self.assertEqual(data["kind"], "paper")
        self.assertEqual(data["depth"], "deep")
        self.assertEqual(data["claim_count"], 3)
        self.assertEqual(data["related"], ["existing-a", "existing-b"])
        # Brackets, hashes and newlines would corrupt the flat frontmatter parser.
        self.assertEqual(data["title"], "Fake （Paper） ＃1 第二行")

    def test_sanitize_scalar_protects_list_and_block_syntax(self):
        self.assertEqual(cards.sanitize_scalar("[a, b]"), "（a, b）")
        self.assertEqual(cards.sanitize_scalar("标题 #1\n\n第二行"), "标题 ＃1 第二行")


class TransportTests(unittest.TestCase):
    """The model is a hostile container for LaTeX Markdown; these lock the workarounds."""

    class FakeResponse:
        def __init__(self, payload):
            self._payload = json.dumps(payload).encode()

        def read(self):
            return self._payload

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    def envelope(self, content, finish_reason="stop"):
        return {"choices": [{"message": {"content": content}, "finish_reason": finish_reason}]}

    def test_latex_backslash_in_json_is_repaired(self):
        # Single backslashes (\rho, \mathcal, \theta, \underline) are not legal JSON escapes.
        content = '{"method": "使用 \\rho、\\mathcal{L}、\\theta 与 \\underline{x}"}'
        with patch.object(cards.urllib.request, "urlopen", return_value=self.FakeResponse(self.envelope(content))):
            result = cards.chat_json("k", "s", "u", max_tokens=100, label="t")
        self.assertIn("\\rho", result["method"])
        self.assertIn("\\mathcal{L}", result["method"])
        self.assertIn("\\theta", result["method"])
        self.assertIn("\\underline{x}", result["method"])

    def test_genuine_json_escapes_still_work(self):
        content = '{"a": "行一\\n行二", "b": "引号\\"结束"}'
        with patch.object(cards.urllib.request, "urlopen", return_value=self.FakeResponse(self.envelope(content))):
            result = cards.chat_json("k", "s", "u", max_tokens=100, label="t")
        self.assertEqual(result["a"], "行一\n行二")
        self.assertEqual(result["b"], '引号"结束')

    def test_chat_text_reports_finish_reason(self):
        with patch.object(cards.urllib.request, "urlopen", return_value=self.FakeResponse(self.envelope("<<<SECTION a>>>\nx\n<<<END>>>", "length"))):
            text, finish = cards.chat_text("k", "s", "u", max_tokens=100, label="t")
        self.assertEqual(finish, "length")
        self.assertIn("<<<END>>>", text)

    def test_sentinel_drafting_retries_when_a_block_is_missing(self):
        calls = {"n": 0}

        def fake_text(api, system, user, *, max_tokens, temperature=0.2, label="call"):
            calls["n"] += 1
            if calls["n"] == 1:
                return "<<<SECTION 问题与语境>>>\n只有一节。\n<<<END>>>", "length"
            return "\n".join(f"<<<SECTION {name}>>>\n{compliant_sections()[name]}\n<<<END>>>" for name in PAPER_DEEP[:2]), "stop"

        paper = {"id": "2609.00001", "title": "T", "authors": [], "published": "", "arxivUrl": ""}
        full = {"url": "u", "title": "T", "chars": 10, "sections": [{"title": "Abstract", "text": "x"}], "excerpt": "## Abstract\nx"}
        with patch.object(cards, "chat_text", fake_text):
            drafted = cards.draft_sections("k", paper, {}, tuple(PAPER_DEEP[:2]), full, CONFIG)
        self.assertEqual(calls["n"], 2)
        self.assertEqual(set(drafted), set(PAPER_DEEP[:2]))

    def test_sentinel_drafting_gives_up_loudly(self):
        def broken_text(*args, **kwargs):
            return "完全没有块的输出", "stop"

        paper = {"id": "1", "title": "T", "authors": [], "published": "", "arxivUrl": ""}
        full = {"url": "u", "title": "T", "chars": 10, "sections": [{"title": "Abstract", "text": "x"}], "excerpt": "x"}
        with patch.object(cards, "chat_text", broken_text):
            with self.assertRaises(cards.CardError):
                cards.draft_sections("k", paper, {}, tuple(PAPER_DEEP[:2]), full, CONFIG)

    def test_best_slug_avoids_generic_ids_from_chinese_titles(self):
        # A Chinese-only title slugs to the fallback "card"; prefer the English title.
        self.assertEqual(
            cards.best_slug(["探索引导的提示脚手架", "Not All Prompts Are Equal: Exploration-Guided Prompt Scaffolding"], set()),
            "not-all-prompts-are-equal-exploration",
        )
        # A stray short acronym ("moe") is too weak to identify a note.
        self.assertEqual(
            cards.best_slug(["MoE 强化学习", "Expert-Space Exploration in MoE Reinforcement Learning"], set()),
            "expert-space-exploration-in-moe",
        )
        # Good slugs are kept, and collisions still get a suffix.
        self.assertEqual(cards.best_slug(["Reward Shaping for Agents"], set()), "reward-shaping-for-agents")
        self.assertEqual(cards.best_slug(["Reward Shaping for Agents"], {"reward-shaping-for-agents"}), "reward-shaping-for-agents-2")


if __name__ == "__main__":
    unittest.main()
