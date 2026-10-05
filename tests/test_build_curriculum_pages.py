"""Tests for the course site build in scripts/build_curriculum_pages.py."""

import importlib.util
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
_SPEC = importlib.util.spec_from_file_location(
    "build_curriculum_pages", REPO_ROOT / "scripts" / "build_curriculum_pages.py"
)
build_pages = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = build_pages  # dataclasses look the module up by name
_SPEC.loader.exec_module(build_pages)

# Phrases that belong to the agent skill's instructions, not to a learner page.
AGENT_PHRASES = ("Teach these points", "ask_user", "INVOKES", "+15 XP", "Reveal Solution")


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    out = tmp_path_factory.mktemp("site")
    build_pages.build(out)
    return out


def _ids(text):
    return set(re.findall(r'\bid="([^"]+)"', text))


def test_build_writes_every_page_and_the_single_file(site):
    names = {path.name for path in site.glob("*.html")}
    expected = {page.filename for page in build_pages.PAGES} | {
        build_pages.STANDALONE_NAME,
        "skills-ledger.html",
    }
    assert names == expected


def test_every_page_has_one_h1_and_no_agent_instructions(site):
    for path in site.glob("*.html"):
        text = path.read_text(encoding="utf-8")
        assert text.count("<h1") == 1, path.name
        for phrase in AGENT_PHRASES:
            assert phrase not in text, f"{path.name} contains {phrase!r}"


def test_module_pages_turn_the_tutor_brief_into_a_source_note(site):
    text = (site / "module-4.html").read_text(encoding="utf-8")
    assert '<p class="source-note">Based on <a href="reference.html">the reference</a>' in text
    assert "Check your understanding" in text


def test_no_relative_markdown_links_survive(site):
    for path in site.glob("*.html"):
        for href in re.findall(r'href="([^"]+)"', path.read_text(encoding="utf-8")):
            if href.startswith(("http://", "https://", "#")):
                continue
            assert href.split("#")[0].endswith(".html"), f"{path.name}: {href}"


def test_internal_links_resolve_to_pages_and_anchors(site):
    pages = {path.name: path.read_text(encoding="utf-8") for path in site.glob("*.html")}
    for name, text in pages.items():
        for href in re.findall(r'href="([^"]+)"', text):
            if href.startswith(("http://", "https://")):
                continue
            target, _, fragment = href.partition("#")
            target = target or name
            assert target in pages, f"{name}: {href}"
            if fragment:
                assert fragment in _ids(pages[target]), f"{name}: {href}"


def test_quiz_counts_match_their_sources():
    bank = build_pages.load_quiz_bank()
    refs = REPO_ROOT / build_pages.MODULE_REFS
    scenarios = re.findall(r"^\d+\. \*\*", (refs / "scenarios.md").read_text(), re.MULTILINE)
    exam = re.findall(r"^\d+\. .*", (refs / "final-exam.md").read_text(), re.MULTILINE)
    assert len(bank["scenarios"]["questions"]) == len(scenarios)
    assert len(bank["final-exam"]["questions"]) == len(exam)


def test_quiz_answers_are_marked_in_the_page(site):
    text = (site / "final-exam.html").read_text(encoding="utf-8")
    assert text.count('class="question"') == 15
    assert 'data-pass="0.8"' in text


def test_a_page_missing_from_the_quiz_bank_fails_the_build(tmp_path, monkeypatch):
    bank = tmp_path / "quizzes.yaml"
    bank.write_text(
        "module-1:\n  questions:\n"
        + "    - {q: Q, why: W, choices: [a, b, c, d], answer: 4}\n" * 4,
        encoding="utf-8",
    )
    monkeypatch.setattr(build_pages, "QUIZ_BANK", bank)
    with pytest.raises(build_pages.BuildError, match="no questions for module-2"):
        build_pages.load_quiz_bank()


def test_a_link_to_an_untracked_file_fails_the_build():
    linker = build_pages.Linker(build_pages.tracked_paths(), standalone=False)
    with pytest.raises(build_pages.BuildError, match="does not resolve"):
        linker.resolve("../reports/m4/result.json", "docs/16_SKILLEVALUATOR_MASTERY.md")


def test_links_between_course_sources_become_page_links():
    tracked = build_pages.tracked_paths()
    site = build_pages.Linker(tracked, standalone=False)
    single = build_pages.Linker(tracked, standalone=True)
    source = "docs/16_SKILLEVALUATOR_MASTERY.md"
    href = "15_SKILLS_AND_SKILLEVALUATOR_REFERENCE.md#3-feasibility"
    assert site.resolve(href, source) == "reference.html#3-feasibility"
    assert single.resolve(href, source) == "#reference--3-feasibility"
    assert site.resolve("../framework/", source) == (f"{build_pages.REPO_URL}/tree/main/framework")


def test_an_answer_index_out_of_range_fails_the_build(tmp_path, monkeypatch):
    text = build_pages.QUIZ_BANK.read_text(encoding="utf-8")
    bank = tmp_path / "quizzes.yaml"
    bank.write_text(text.replace("answer: 2", "answer: 4", 1), encoding="utf-8")
    monkeypatch.setattr(build_pages, "QUIZ_BANK", bank)
    with pytest.raises(build_pages.BuildError, match="module-1 question 1 has an answer index"):
        build_pages.load_quiz_bank()


def test_the_single_file_does_not_repeat_its_title(site):
    text = (site / build_pages.STANDALONE_NAME).read_text(encoding="utf-8")
    headings = re.findall(r"<h[12][^>]*>([^<]*)</h[12]>", text)
    assert headings.count(build_pages.COURSE_TITLE) == 1


def test_hand_written_site_pages_are_published_and_mobile_ready(site):
    for source in sorted(build_pages.SITE_DIR.glob("*.html")):
        text = (site / source.name).read_text(encoding="utf-8")
        assert text.startswith("<!DOCTYPE html>"), source.name
        assert 'name="viewport"' in text, source.name
        assert text.count("<h1") == 1, source.name
