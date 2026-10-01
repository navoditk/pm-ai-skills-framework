"""Every relative link in tracked Markdown must point at a tracked file.

A link to a git-ignored path (raw reports under reports/, say) works in the
author's checkout and is broken for everyone else, so existence on disk is
not enough: the target has to be in `git ls-files`.
"""

import posixpath
import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
FENCE = re.compile(r"^\s*(```|~~~)")


def _tracked():
    files = subprocess.run(
        ["git", "ls-files"], cwd=REPO_ROOT, capture_output=True, text=True, check=True
    ).stdout.splitlines()
    paths = set(files)
    for name in files:
        parent = posixpath.dirname(name)
        while parent:
            paths.add(parent)
            parent = posixpath.dirname(parent)
    return files, paths


def _links(text):
    in_fence = False
    for number, line in enumerate(text.splitlines(), 1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for match in LINK.finditer(re.sub(r"`[^`]*`", "", line)):
            yield number, match.group(1)


def test_relative_markdown_links_point_at_tracked_files():
    files, tracked = _tracked()
    broken = []
    for name in files:
        # site/ links to built pages; scripts/build_curriculum_pages.py checks those.
        if not name.endswith(".md") or name.startswith("site/"):
            continue
        text = (REPO_ROOT / name).read_text(encoding="utf-8")
        for number, href in _links(text):
            if re.match(r"[a-z][a-z0-9+.-]*:", href) or href.startswith("#"):
                continue
            path = href.split("#", 1)[0]
            target = posixpath.normpath(posixpath.join(posixpath.dirname(name), path))
            if target not in tracked:
                broken.append(f"{name}:{number}: {href}")
    assert not broken, "links to untracked or missing files:\n" + "\n".join(broken)
