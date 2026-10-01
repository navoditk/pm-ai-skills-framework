"""The per-agent skill loaders stay identical and point at the canonical skill.

Claude Code discovers project skills in .claude/skills/, Codex in
.agents/skills/, and GitHub Copilot in both. Each loader is a thin pointer to
skills/<name>/SKILL.md, so it must name the same skill and must not drift.
"""

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
LOADER_DIRS = (".claude/skills", ".agents/skills")


def _frontmatter(path):
    text = path.read_text(encoding="utf-8")
    return yaml.safe_load(text.split("---", 2)[1])


def test_loaders_are_identical_across_agents():
    names = [sorted(p.name for p in (REPO_ROOT / d).iterdir()) for d in LOADER_DIRS]
    assert names[0] == names[1]
    for name in names[0]:
        copies = [(REPO_ROOT / d / name / "SKILL.md").read_text() for d in LOADER_DIRS]
        assert copies[0] == copies[1], name


def test_each_loader_matches_and_points_at_its_canonical_skill():
    for loader in (REPO_ROOT / LOADER_DIRS[0]).glob("*/SKILL.md"):
        name = loader.parent.name
        canonical = REPO_ROOT / "skills" / name / "SKILL.md"
        assert canonical.is_file(), name
        meta, source = _frontmatter(loader), _frontmatter(canonical)
        assert meta["name"] == source["name"] == name
        assert meta["description"] == source["description"], name
        assert f"skills/{name}/SKILL.md" in loader.read_text()


def test_no_copilot_only_loader_folder_remains():
    assert not (REPO_ROOT / ".github" / "skills").exists()
