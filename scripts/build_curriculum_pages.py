#!/usr/bin/env python3
"""Build the SkillEvaluator Mastery course site and its single-file version.

The lessons come from the agent skill in skills/skillevaluator-mastery/ and
from docs 15 and 16. The skill's module files are written for an agent to
teach from, so the build turns them into learner pages: the line telling the
tutor what to teach becomes a source note, and the section telling it how to
quiz is replaced with the multiple-choice questions in site/quizzes.yaml.
The landing page is site/index.md; any finished HTML page in site/, such as
the Skills Ledger slide deck, is copied to the output unchanged.

Output goes to public/ by default:

    uv run python scripts/build_curriculum_pages.py [--out DIR]

The build fails, rather than writing a degraded page, if the Markdown
renderer is missing, a source file is missing, a relative link points at a
file Git does not track, or the quiz bank is malformed.
"""

from __future__ import annotations

import argparse
import html
import json
import math
import posixpath
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

try:
    import markdown
    from markdown.extensions.toc import slugify as _toc_slugify
except ImportError:  # pragma: no cover - exercised only on a broken install
    sys.exit(
        "The 'markdown' package is required to build the course site.\n"
        "Install the dev dependencies with: uv sync --extra dev"
    )

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO_ROOT / "public"
SITE_DIR = REPO_ROOT / "site"
QUIZ_BANK = SITE_DIR / "quizzes.yaml"
REPO_URL = "https://github.com/navoditk/pm-ai-skills-framework"
SITE_URL = "https://navoditk.github.io/pm-ai-skills-framework/"
STANDALONE_NAME = "skillevaluator-mastery-standalone.html"
COURSE_TITLE = "SkillEvaluator Mastery"
DEFAULT_PASS_MARK = 0.8
MODULE_REFS = "skills/skillevaluator-mastery/references"


class BuildError(Exception):
    """A problem in the sources that would otherwise produce a broken page."""


@dataclass(frozen=True)
class Page:
    id: str
    nav: str
    group: str
    source: str
    kind: str  # landing, doc, module, or quiz
    summary: str = ""

    @property
    def filename(self) -> str:
        return "index.html" if self.id == "index" else f"{self.id}.html"

    @property
    def tracked(self) -> bool:
        """Whether the page counts towards course progress."""
        return self.kind in {"module", "quiz"}


PAGES: tuple[Page, ...] = (
    Page("index", "Overview", "Start", "site/index.md", "landing"),
    Page("tutorial", "Hands-on tutorial", "Start", "docs/16_SKILLEVALUATOR_MASTERY.md", "doc"),
    Page(
        "reference", "Reference", "Start", "docs/15_SKILLS_AND_SKILLEVALUATOR_REFERENCE.md", "doc"
    ),
    Page(
        "module-1",
        "What it is and why",
        "Modules",
        f"{MODULE_REFS}/module-1-overview.md",
        "module",
        "The four tiers, what each one costs, and what SkillEvaluator leaves to you.",
    ),
    Page(
        "module-2",
        "Tier 1: construction and security",
        "Modules",
        f"{MODULE_REFS}/module-2-tier1.md",
        "module",
        "Free, offline checks for schema, quality, and security on every pull request.",
    ),
    Page(
        "module-3",
        "Tier 2: similarity",
        "Modules",
        f"{MODULE_REFS}/module-3-tier2.md",
        "module",
        "Catching near-duplicate skills, and the embedding-provider trap.",
    ),
    Page(
        "module-4",
        "Tier 3: live-agent evaluation",
        "Modules",
        f"{MODULE_REFS}/module-4-tier3.md",
        "module",
        "Measuring Skill Lift with a live agent and judge, and what that costs.",
    ),
    Page(
        "module-5",
        "Tier 4: domain graders",
        "Modules",
        f"{MODULE_REFS}/module-5-tier4.md",
        "module",
        "Writing reusable graders that judge domain correctness.",
    ),
    Page(
        "module-6",
        "Installing and running",
        "Modules",
        f"{MODULE_REFS}/module-6-install.md",
        "module",
        "Install options, pinning an exact commit, and checking the install.",
    ),
    Page(
        "module-7",
        "Skill package layout",
        "Modules",
        f"{MODULE_REFS}/module-7-layout.md",
        "module",
        "The folder layout and frontmatter that Tier 1 checks.",
    ),
    Page(
        "module-8",
        "Reports, CI/CD, and real bugs",
        "Modules",
        f"{MODULE_REFS}/module-8-reports-and-cicd.md",
        "module",
        "Reading reports, wiring CI, and four problems this repository hit.",
    ),
    Page(
        "scenarios", "Troubleshooting scenarios", "Practice", f"{MODULE_REFS}/scenarios.md", "quiz"
    ),
    Page("final-exam", "Final exam", "Practice", f"{MODULE_REFS}/final-exam.md", "quiz"),
)
PAGE_BY_ID = {page.id: page for page in PAGES}
PAGE_BY_SOURCE = {page.source: page for page in PAGES}
PAGE_BY_FILENAME = {page.filename: page for page in PAGES}
TRACKED_IDS = [page.id for page in PAGES if page.tracked]


# --------------------------------------------------------------------------
# Source loading and learner-facing transforms
# --------------------------------------------------------------------------


def tracked_paths() -> set[str]:
    """Paths Git tracks, plus every directory that contains one.

    Links are checked against this rather than the filesystem so a link to a
    git-ignored local file (reports/, say) fails here instead of on GitHub.
    """
    try:
        out = subprocess.run(
            ["git", "ls-files"], cwd=REPO_ROOT, capture_output=True, text=True, check=True
        ).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise BuildError(f"cannot list tracked files with git: {exc}") from exc
    paths: set[str] = set()
    for line in out.splitlines():
        paths.add(line)
        parent = posixpath.dirname(line)
        while parent:
            paths.add(parent)
            parent = posixpath.dirname(parent)
    return paths


def strip_frontmatter(text: str) -> str:
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            return text[end + 4 :].lstrip("\n")
    return text


def learner_markdown(page: Page, text: str) -> str:
    """Turn a source file into the Markdown a learner should read."""
    text = strip_frontmatter(text)
    if page.kind == "doc":
        # "# 15. Skills & ..." -> "# Skills & ...": the numbering is the docs folder's.
        text = re.sub(r"\A# \d+\.\s+", "# ", text)
    if page.kind == "module":
        # The tutor brief becomes a source note.
        text = re.sub(
            r"^Teach these points one at a time, grounded in\s+",
            "Based on ",
            text,
            count=1,
            flags=re.MULTILINE,
        )
        # The quiz brief is for the agent; the site asks site/quizzes.yaml instead.
        text = re.split(r"^## Quiz\b", text, maxsplit=1, flags=re.MULTILINE)[0]
    # GitHub task lists: "- [ ] item" renders as a checkbox there, not here.
    text = re.sub(r"^(\s*)- \[ \] ", r"\1- ", text, flags=re.MULTILINE)
    return text.rstrip() + "\n"


def make_slugify(prefix: str):
    def slugify(value: str, separator: str) -> str:
        return prefix + _toc_slugify(value, separator)

    return slugify


def render_markdown(text: str, prefix: str = "") -> str:
    return markdown.markdown(
        text,
        extensions=["fenced_code", "tables", "toc", "sane_lists"],
        extension_configs={"toc": {"slugify": make_slugify(prefix)}},
        output_format="html5",
    )


class Linker:
    """Rewrites links in rendered HTML so they work on the site."""

    def __init__(self, tracked: set[str], standalone: bool):
        self.tracked = tracked
        self.standalone = standalone

    def page_href(self, page: Page, fragment: str = "") -> str:
        if self.standalone:
            return f"#{page.id}--{fragment}" if fragment else f"#{page.id}"
        return page.filename + (f"#{fragment}" if fragment else "")

    def resolve(self, href: str, source: str) -> str:
        if not href or href.startswith(("http://", "https://", "mailto:")):
            return href
        if href.startswith("#"):
            if self.standalone:
                return f"#{PAGE_BY_SOURCE[source].id}--{href[1:]}"
            return href
        path, _, fragment = href.partition("#")
        if source.startswith("site/") and path in PAGE_BY_FILENAME:
            return self.page_href(PAGE_BY_FILENAME[path], fragment)
        if source.startswith("site/") and (
            path == STANDALONE_NAME or (path.endswith(".html") and (SITE_DIR / path).is_file())
        ):
            # A published page that is not built from Markdown. The single file
            # is opened offline, so it links to the live copy.
            return (SITE_URL + path if self.standalone else path) + (
                f"#{fragment}" if fragment else ""
            )
        target = posixpath.normpath(posixpath.join(posixpath.dirname(source), path))
        if target in PAGE_BY_SOURCE:
            return self.page_href(PAGE_BY_SOURCE[target], fragment)
        if target.startswith("..") or target not in self.tracked:
            raise BuildError(f"{source}: link to {href!r} does not resolve to a tracked file")
        kind = "blob" if (REPO_ROOT / target).is_file() else "tree"
        return f"{REPO_URL}/{kind}/main/{target}" + (f"#{fragment}" if fragment else "")

    def code_path(self, text: str) -> str | None:
        """A link target for an inline `path/to/file`, if it names a tracked path."""
        path = html.unescape(text).rstrip("/")
        if "/" not in path or not re.fullmatch(r"[\w.\-/]+", path):
            return None
        if path in PAGE_BY_SOURCE:
            return self.page_href(PAGE_BY_SOURCE[path])
        if path not in self.tracked:
            return None
        kind = "blob" if (REPO_ROOT / path).is_file() else "tree"
        return f"{REPO_URL}/{kind}/main/{path}"

    def apply(self, body: str, source: str) -> str:
        body = re.sub(
            r'href="([^"]*)"',
            lambda m: f'href="{html.escape(self.resolve(html.unescape(m.group(1)), source))}"',
            body,
        )

        def link_code(match: re.Match[str]) -> str:
            page = PAGE_BY_SOURCE.get(html.unescape(match.group(1)))
            if page is not None:
                # A course page is named, not shown as its source path.
                return f'<a href="{self.page_href(page)}">the {page.nav.lower()}</a>'
            href = self.code_path(match.group(1))
            if href is None:
                return match.group(0)
            return f'<a class="code-link" href="{html.escape(href)}">{match.group(0)}</a>'

        # Inline code only: a fenced block's <code> follows <pre> or has a class,
        # and code already inside a link is left alone.
        return re.sub(r"(?<!<pre>)(?<!\">)<code>([^<]+)</code>(?!</a>)", link_code, body)


def polish(body: str, page: Page) -> str:
    """Small HTML adjustments that Markdown alone cannot express."""
    body = re.sub(r"<table>", '<div class="table-wrap"><table>', body)
    body = body.replace("</table>", "</table></div>")
    if page.kind == "module":
        body = body.replace("<p>Based on ", '<p class="source-note">Based on ', 1)
    return body


def shift_headings(body: str) -> str:
    """Demote every heading one level, for pages nested in the single file."""
    return re.sub(
        r"<(/?)h([1-6])\b",
        lambda m: f"<{m.group(1)}h{min(int(m.group(2)) + 1, 6)}",
        body,
    )


# --------------------------------------------------------------------------
# Quizzes
# --------------------------------------------------------------------------


def inline(text: str) -> str:
    """Escape quiz text, keeping `code` spans."""
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", html.escape(str(text)))


def load_quiz_bank() -> dict[str, Any]:
    bank = yaml.safe_load(QUIZ_BANK.read_text(encoding="utf-8"))
    if not isinstance(bank, dict):
        raise BuildError(f"{QUIZ_BANK.name}: expected a mapping of page id to quiz")
    for page in PAGES:
        if page.tracked and page.id not in bank:
            raise BuildError(f"{QUIZ_BANK.name}: no questions for {page.id}")
    for page_id, quiz in bank.items():
        if page_id not in PAGE_BY_ID or not PAGE_BY_ID[page_id].tracked:
            raise BuildError(f"{QUIZ_BANK.name}: {page_id!r} is not a module or practice page")
        questions = quiz.get("questions") or []
        if len(questions) < 4:
            raise BuildError(f"{QUIZ_BANK.name}: {page_id} needs at least four questions")
        for number, question in enumerate(questions, 1):
            where = f"{QUIZ_BANK.name}: {page_id} question {number}"
            choices = question.get("choices") or []
            if not question.get("q") or not question.get("why"):
                raise BuildError(f"{where} needs both q and why")
            if len(choices) != 4 or len({str(c) for c in choices}) != 4:
                raise BuildError(f"{where} needs four distinct choices")
            answer = question.get("answer")
            if not isinstance(answer, int) or not 0 <= answer < 4:
                raise BuildError(f"{where} has an answer index outside 0-3")
        pass_mark = quiz.get("pass_mark", DEFAULT_PASS_MARK)
        if not 0 < pass_mark <= 1:
            raise BuildError(f"{QUIZ_BANK.name}: {page_id} pass_mark must be in (0, 1]")
    return bank


def render_quiz(page: Page, quiz: dict[str, Any], heading_level: int) -> str:
    questions = quiz["questions"]
    pass_mark = quiz.get("pass_mark", DEFAULT_PASS_MARK)
    needed = math.ceil(pass_mark * len(questions) - 1e-9)
    h = f"h{heading_level}"
    parts = [f'<section class="quiz" data-quiz="{page.id}" data-pass="{pass_mark}">']
    if page.kind == "module":
        parts.append(f'<{h} id="{page.id}--check">Check your understanding</{h}>')
        intro = f"{len(questions)} questions on this module. Get {needed} right to complete it."
    else:
        intro = html.escape(" ".join(quiz.get("intro", "").split()))
    parts.append(f'<p class="quiz-intro">{intro}</p>')
    parts.append('<ol class="questions">')
    for number, question in enumerate(questions, 1):
        name = f"{page.id}-q{number}"
        parts.append(f'<li class="question" data-answer="{question["answer"]}">')
        parts.append(f'<fieldset><legend>{inline(question["q"])}</legend><div class="choices">')
        for index, choice in enumerate(question["choices"]):
            parts.append(
                f'<label class="choice"><input type="radio" name="{name}" value="{index}">'
                f"<span>{inline(choice)}</span></label>"
            )
        parts.append("</div></fieldset>")
        parts.append(f'<p class="why" hidden>{inline(question["why"])}</p>')
        parts.append("</li>")
    parts.append("</ol>")
    parts.append(
        '<div class="quiz-bar">'
        '<button type="button" class="btn primary" data-check>Check answers</button>'
        '<button type="button" class="btn" data-retry hidden>Try again</button>'
        '<output class="quiz-result" aria-live="polite"></output>'
        "</div>"
    )
    parts.append("<noscript><p>The questions need JavaScript to mark answers.</p></noscript>")
    parts.append("</section>")
    return "\n".join(parts)


# --------------------------------------------------------------------------
# Page assembly
# --------------------------------------------------------------------------


def module_list(linker: Linker) -> str:
    items = []
    for number, page in enumerate((p for p in PAGES if p.kind == "module"), 1):
        items.append(
            f'<li><a href="{linker.page_href(page)}" data-page="{page.id}">'
            f'<span class="step">Module {number}</span>'
            f"<strong>{html.escape(page.nav)}</strong>"
            f"<span>{html.escape(page.summary)}</span></a></li>"
        )
    return '<ol class="module-list">\n' + "\n".join(items) + "\n</ol>"


def page_body(page: Page, bank: dict[str, Any], linker: Linker, standalone: bool) -> str:
    prefix = f"{page.id}--" if standalone else ""
    source_text = (REPO_ROOT / page.source).read_text(encoding="utf-8")
    if page.kind == "quiz":
        markdown_text = f"# {page.nav}\n"
    else:
        markdown_text = learner_markdown(page, source_text)
    body = render_markdown(markdown_text, prefix)
    body = linker.apply(body, page.source)
    body = polish(body, page)
    if page.kind == "landing":
        body = body.replace("<!-- modules -->", module_list(linker))
    if standalone:
        body = shift_headings(body)
        if page.kind == "landing":
            # The single file's own h1 is the course title; don't repeat it.
            body = re.sub(r"\A\s*<h2[^>]*>[^<]*</h2>\s*", "", body, count=1)
    if page.tracked:
        body += "\n" + render_quiz(page, bank[page.id], 3 if standalone else 2)
    if page.kind == "module":
        body += (
            '\n<div class="complete-bar"><button type="button" class="btn" '
            f'data-mark="{page.id}" aria-pressed="false">Mark module as complete</button></div>'
        )
    return body


def nav_html(linker: Linker, active: str | None) -> str:
    parts = ['<nav id="site-nav" class="site-nav" aria-label="Course">']
    parts.append(
        '<div class="progress" aria-live="polite"><span data-progress-text>'
        f"0 of {len(TRACKED_IDS)} complete</span>"
        '<span class="bar"><span data-progress-bar></span></span></div>'
    )
    group = None
    for page in PAGES:
        if page.group != group:
            if group is not None:
                parts.append("</ul>")
            group = page.group
            parts.append(f'<p class="nav-group">{html.escape(group)}</p><ul>')
        current = ' aria-current="page"' if page.id == active else ""
        parts.append(
            f'<li><a href="{linker.page_href(page)}" data-page="{page.id}"{current}>'
            f"{html.escape(page.nav)}</a></li>"
        )
    parts.append("</ul>")
    parts.append('<div class="nav-foot">')
    if not linker.standalone:
        parts.append(f'<a href="{STANDALONE_NAME}">Download as one file</a>')
    parts.append(f'<a href="{REPO_URL}">Source on GitHub</a>')
    parts.append('<button type="button" class="link-button" data-reset>Reset progress</button>')
    parts.append("</div></nav>")
    return "\n".join(parts)


def pager(page: Page, linker: Linker) -> str:
    index = PAGES.index(page)
    links = []
    if index > 0:
        prev = PAGES[index - 1]
        links.append(
            f'<a class="prev" href="{linker.page_href(prev)}"><span>Previous</span>'
            f"{html.escape(prev.nav)}</a>"
        )
    if index < len(PAGES) - 1:
        nxt = PAGES[index + 1]
        links.append(
            f'<a class="next" href="{linker.page_href(nxt)}"><span>Next</span>'
            f"{html.escape(nxt.nav)}</a>"
        )
    return '<nav class="pager" aria-label="Previous and next">' + "".join(links) + "</nav>"


def document(title: str, description: str, nav: str, main: str, home: str) -> str:
    config = json.dumps({"tracked": TRACKED_IDS})
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description)}">
<style>{CSS}</style>
</head>
<body>
<script>document.documentElement.classList.add("js")</script>
<a class="skip" href="#content">Skip to content</a>
<header class="topbar">
<div class="topbar-inner">
<button type="button" class="menu-button" aria-controls="site-nav" aria-expanded="false">Menu</button>
<a class="brand" href="{home}">{COURSE_TITLE}</a>
<span class="tag">NVIDIA SkillEvaluator</span>
</div>
</header>
<div class="layout">
{nav}
<main id="content" class="content" tabindex="-1">
{main}
<footer class="site-footer">
<p>Part of the <a href="{REPO_URL}">PM AI Skills Framework</a>. Lessons are generated from
the <a href="{REPO_URL}/tree/main/skills/skillevaluator-mastery">skillevaluator-mastery</a> skill
and docs 15 and 16. Progress is stored in this browser only.</p>
</footer>
</main>
</div>
<script id="course-config" type="application/json">{config}</script>
<script>{JS}</script>
</body>
</html>
"""


def build(out_dir: Path) -> list[Path]:
    bank = load_quiz_bank()
    tracked = tracked_paths()
    for page in PAGES:
        if not (REPO_ROOT / page.source).is_file():
            raise BuildError(f"missing source for {page.id}: {page.source}")

    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    site_linker = Linker(tracked, standalone=False)
    for page in PAGES:
        body = page_body(page, bank, site_linker, standalone=False)
        title = COURSE_TITLE if page.id == "index" else f"{page.nav} | {COURSE_TITLE}"
        description = page.summary or (
            "A short course on NVIDIA SkillEvaluator, with lessons, quizzes, "
            "troubleshooting scenarios, and a final exam."
        )
        main = f'<article class="page page-{page.kind}">\n{body}\n</article>\n{pager(page, site_linker)}'
        path = out_dir / page.filename
        path.write_text(
            document(title, description, nav_html(site_linker, page.id), main, "index.html"),
            encoding="utf-8",
        )
        written.append(path)

    one_linker = Linker(tracked, standalone=True)
    sections = [f'<h1 class="standalone-title">{COURSE_TITLE}</h1>']
    for page in PAGES:
        body = page_body(page, bank, one_linker, standalone=True)
        sections.append(
            f'<section class="page page-{page.kind}" id="{page.id}">\n{body}\n</section>'
        )
    path = out_dir / STANDALONE_NAME
    path.write_text(
        document(
            f"{COURSE_TITLE} (single file)",
            "The whole SkillEvaluator Mastery course as one standalone file.",
            nav_html(one_linker, None),
            "\n".join(sections),
            "#index",
        ),
        encoding="utf-8",
    )
    written.append(path)

    # Standalone pages kept in site/ (the Skills Ledger deck) are published as is.
    for extra in sorted(SITE_DIR.glob("*.html")):
        written.append(Path(shutil.copy(extra, out_dir / extra.name)))
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="output directory")
    args = parser.parse_args(argv)
    try:
        written = build(args.out)
    except BuildError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    for path in written:
        print(f"wrote {path}")
    print(f"Built {len(written)} pages into {args.out}")
    return 0


# --------------------------------------------------------------------------
# Styles and behaviour
# --------------------------------------------------------------------------

CSS = """
:root{color-scheme:light dark;--ink:#16202c;--muted:#56657a;--accent:#1560a8;--accent-ink:#fff;
--card:#fff;--line:#dbe3ec;--soft:#eef4fa;--page:#f6f8fb;--code-bg:#eef2f7;--ok:#1f7a45;
--ok-bg:#e7f6ed;--bad:#b03427;--bad-bg:#fbeaea;--gutter:clamp(1rem,4vw,2.5rem);--top:3.5rem;
--measure:72ch}
@media (prefers-color-scheme:dark){:root{--ink:#e6ecf2;--muted:#a7b4c3;--accent:#7cb9f4;
--accent-ink:#0b1622;--card:#17212c;--line:#314154;--soft:#1f2e3e;--page:#0f1720;--code-bg:#223244;
--ok:#4cc38a;--ok-bg:#14301f;--bad:#f07167;--bad-bg:#3a1a17}}
*{box-sizing:border-box}
html{font-size:clamp(16px,.85rem + .22vw,19px);scroll-padding-top:calc(var(--top) + 1rem);
-webkit-text-size-adjust:100%}
body{margin:0;font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;line-height:1.6;
color:var(--ink);background:var(--page)}
a{color:var(--accent);text-underline-offset:.15em}
a:focus-visible,button:focus-visible,input:focus-visible{outline:3px solid var(--accent);
outline-offset:2px;border-radius:.25rem}
.skip{position:absolute;left:-999px;top:0;background:var(--card);padding:.5rem 1rem;z-index:20}
.skip:focus{left:1rem}
.topbar{position:sticky;top:0;z-index:10;height:var(--top);background:var(--card);
border-bottom:1px solid var(--line)}
.topbar-inner{max-width:1480px;height:100%;margin:0 auto;padding:0 var(--gutter);display:flex;
align-items:center;gap:.75rem}
.brand{font-weight:700;font-size:1.05rem;color:var(--ink);text-decoration:none;white-space:nowrap}
.tag{margin-left:auto;font-size:.75rem;font-weight:600;letter-spacing:.04em;text-transform:uppercase;
color:var(--muted);white-space:nowrap}
.menu-button{display:none;min-height:40px;padding:0 .9rem;border:1px solid var(--line);
border-radius:.4rem;background:var(--card);color:var(--ink);font:inherit;font-weight:600;cursor:pointer}
.layout{max-width:1480px;margin:0 auto;padding:0 var(--gutter);display:grid;
grid-template-columns:16rem minmax(0,1fr);gap:clamp(1.5rem,4vw,4rem)}
.site-nav{position:sticky;top:var(--top);align-self:start;max-height:calc(100vh - var(--top));
overflow-y:auto;padding:1.5rem 0 2rem;font-size:.92rem}
.site-nav ul{list-style:none;margin:0 0 .5rem;padding:0}
.site-nav li a{display:flex;align-items:center;gap:.4rem;padding:.35rem .6rem;border-radius:.35rem;
color:var(--ink);text-decoration:none;line-height:1.35}
.site-nav li a:hover{background:var(--soft)}
.site-nav li a[aria-current=page]{background:var(--soft);color:var(--accent);font-weight:650}
.site-nav li a.done::after{content:"\\2713";margin-left:auto;color:var(--ok);font-weight:700}
.nav-group{margin:1.1rem 0 .3rem .6rem;font-size:.72rem;font-weight:700;letter-spacing:.08em;
text-transform:uppercase;color:var(--muted)}
.progress{display:grid;gap:.35rem;padding:0 .6rem;color:var(--muted);font-size:.85rem}
.bar{display:block;height:.4rem;border-radius:1rem;background:var(--line);overflow:hidden}
.bar span{display:block;height:100%;width:0;background:var(--ok);transition:width .3s}
.nav-foot{display:grid;gap:.4rem;margin-top:1.5rem;padding:1rem .6rem 0;border-top:1px solid var(--line);
font-size:.85rem}
.link-button{justify-self:start;padding:0;border:0;background:none;color:var(--muted);font:inherit;
text-decoration:underline;cursor:pointer}
.content{min-width:0;padding:2rem 0 3rem;outline:none}
.page{max-width:52rem}
.page h1,.standalone-title{font-size:clamp(1.8rem,1.3rem + 2vw,2.6rem);line-height:1.15;
letter-spacing:-.015em;margin:0 0 1rem}
.page h2{font-size:clamp(1.3rem,1.1rem + .7vw,1.65rem);line-height:1.25;margin:2.25rem 0 .6rem}
.page h3{font-size:1.12rem;margin:1.75rem 0 .4rem}
.page h4{font-size:1rem;margin:1.25rem 0 .3rem}
p,li{max-width:var(--measure)}
ul,ol{padding-left:1.3rem}
li{margin:.2rem 0}
hr{border:0;border-top:1px solid var(--line);margin:2rem 0}
code{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:.88em;
background:var(--code-bg);padding:.1em .3em;border-radius:.25rem;overflow-wrap:anywhere}
pre{background:var(--code-bg);border:1px solid var(--line);border-radius:.5rem;padding:.9rem 1rem;
overflow-x:auto;line-height:1.45;font-size:.88rem}
pre code{background:none;padding:0;font-size:inherit;overflow-wrap:normal}
.code-link{text-decoration:none}
.code-link code{color:var(--accent)}
.table-wrap{overflow-x:auto;margin:1rem 0;border:1px solid var(--line);border-radius:.5rem;
background:var(--card)}
table{border-collapse:collapse;width:100%;font-size:.92rem}
th,td{padding:.55rem .75rem;text-align:left;vertical-align:top;border-bottom:1px solid var(--line)}
tr:last-child td{border-bottom:0}
thead th{background:var(--soft);font-weight:650}
blockquote{margin:1rem 0;padding:.6rem 1rem;border-left:4px solid var(--accent);background:var(--soft);
border-radius:0 .4rem .4rem 0}
.source-note{color:var(--muted);font-size:.92rem;border-left:3px solid var(--line);padding-left:.75rem}
.module-list{list-style:none;padding:0;display:grid;gap:.75rem;
grid-template-columns:repeat(auto-fill,minmax(min(100%,15rem),1fr))}
.module-list li{margin:0;max-width:none}
.module-list a{display:flex;flex-direction:column;gap:.2rem;height:100%;padding:.9rem 1rem;
background:var(--card);border:1px solid var(--line);border-radius:.6rem;color:var(--ink);
text-decoration:none}
.module-list a:hover{border-color:var(--accent)}
.module-list .step{font:700 .78rem ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--accent)}
.module-list a span:last-child{color:var(--muted);font-size:.9rem}
.module-list a.done .step::after{content:"  \\2713 complete";color:var(--ok)}
.btn{display:inline-flex;align-items:center;min-height:44px;padding:.5rem 1.1rem;border-radius:.45rem;
border:1px solid var(--line);background:var(--card);color:var(--ink);font:inherit;font-weight:650;
cursor:pointer}
.btn.primary{background:var(--accent);border-color:var(--accent);color:var(--accent-ink)}
.btn[aria-pressed=true]{background:var(--ok-bg);border-color:var(--ok);color:var(--ok)}
.quiz{margin-top:2.5rem;padding-top:.5rem;border-top:1px solid var(--line)}
.page-quiz .quiz{margin-top:0;padding-top:0;border-top:0}
.quiz-intro{color:var(--muted)}
.questions{padding:0;list-style:none;counter-reset:q;display:grid;
grid-template-columns:minmax(0,1fr);gap:1rem}
.question{counter-increment:q;margin:0;max-width:none;background:var(--card);border:1px solid var(--line);
border-radius:.6rem;padding:1rem clamp(.9rem,2.5vw,1.25rem)}
.question fieldset{border:0;margin:0;padding:0;min-width:0}
.question legend{padding:0;font-weight:650;margin-bottom:.6rem;max-width:var(--measure)}
.question legend::before{content:counter(q) ". ";color:var(--muted)}
.choices{display:grid;gap:.4rem}
.choice{display:flex;align-items:flex-start;gap:.6rem;min-height:44px;padding:.55rem .7rem;
border:1px solid var(--line);border-radius:.45rem;cursor:pointer}
.choice:hover{background:var(--soft)}
.choice span{min-width:0;overflow-wrap:anywhere}
.choice input{margin:.3rem 0 0;flex:none;width:1.05rem;height:1.05rem;accent-color:var(--accent)}
.choice.correct{border-color:var(--ok);background:var(--ok-bg)}
.choice.chosen-wrong{border-color:var(--bad);background:var(--bad-bg)}
.question.right{border-color:var(--ok)}
.question.wrong{border-color:var(--bad)}
.why{margin:.6rem 0 0;font-size:.93rem;color:var(--muted)}
.question.wrong .why::before{content:"Not quite. ";font-weight:650;color:var(--bad)}
.question.right .why::before{content:"Correct. ";font-weight:650;color:var(--ok)}
.quiz-bar{display:flex;flex-wrap:wrap;align-items:center;gap:.75rem;margin-top:1rem}
.quiz-result{font-weight:650}
.quiz-result.pass{color:var(--ok)}
.quiz-result.fail{color:var(--bad)}
.complete-bar{margin-top:2rem;display:flex;justify-content:flex-end}
.pager{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,14rem),1fr));gap:.75rem;
max-width:52rem;margin-top:2.5rem}
.pager a{display:flex;flex-direction:column;padding:.75rem 1rem;border:1px solid var(--line);
border-radius:.5rem;background:var(--card);text-decoration:none;font-weight:650}
.pager a span{font-size:.78rem;font-weight:600;text-transform:uppercase;letter-spacing:.06em;
color:var(--muted)}
.pager .next{text-align:right;grid-column:-2}
.site-footer{max-width:52rem;margin-top:3rem;padding-top:1rem;border-top:1px solid var(--line);
color:var(--muted);font-size:.85rem}
section.page{padding-bottom:2.5rem;margin-bottom:2.5rem;border-bottom:1px solid var(--line)}
section.page > h2:first-child{margin-top:0;padding-top:1rem}
@media (max-width:960px){
.menu-button{display:inline-flex;align-items:center}
.layout{display:block}
.js .site-nav{display:none;position:fixed;top:var(--top);left:0;right:0;bottom:0;z-index:9;max-height:none;align-self:auto;
background:var(--page);padding:1rem var(--gutter) 2rem;border-top:1px solid var(--line)}
.js .site-nav.open{display:block}
.site-nav{position:static;max-height:none;padding:1rem 0;border-bottom:1px solid var(--line)}
.site-nav li a{min-height:44px}
.tag{display:none}
.content{padding-top:1.25rem}
}
@media print{.topbar,.site-nav,.pager,.quiz-bar,.complete-bar{display:none}.layout{display:block}}
"""

JS = r"""
(function () {
  var cfg = JSON.parse(document.getElementById("course-config").textContent);
  var KEY = "skilleval-course-v2";
  function load() {
    try {
      var s = JSON.parse(localStorage.getItem(KEY) || "{}");
      return { done: s.done || [], best: s.best || {} };
    } catch (e) { return { done: [], best: {} }; }
  }
  var state = load();
  function save() { try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {} }
  function isDone(id) { return state.done.indexOf(id) !== -1; }
  function setDone(id, on) {
    var i = state.done.indexOf(id);
    if (on && i === -1) state.done.push(id);
    if (!on && i !== -1) state.done.splice(i, 1);
    save(); render();
  }
  function render() {
    var n = cfg.tracked.filter(isDone).length;
    document.querySelectorAll("[data-progress-text]").forEach(function (el) {
      el.textContent = n + " of " + cfg.tracked.length + " complete";
    });
    document.querySelectorAll("[data-progress-bar]").forEach(function (el) {
      el.style.width = (100 * n / cfg.tracked.length) + "%";
    });
    document.querySelectorAll("a[data-page]").forEach(function (a) {
      a.classList.toggle("done", isDone(a.getAttribute("data-page")));
    });
    document.querySelectorAll("[data-mark]").forEach(function (b) {
      var on = isDone(b.getAttribute("data-mark"));
      b.setAttribute("aria-pressed", on ? "true" : "false");
      b.textContent = on ? "Completed" : "Mark module as complete";
    });
  }
  function shuffle(quiz) {
    quiz.querySelectorAll(".choices").forEach(function (box) {
      var items = Array.prototype.slice.call(box.children);
      for (var i = items.length - 1; i > 0; i--) {
        var j = Math.floor(Math.random() * (i + 1));
        var t = items[i]; items[i] = items[j]; items[j] = t;
      }
      items.forEach(function (el) { box.appendChild(el); });
    });
  }
  function check(quiz) {
    var qs = quiz.querySelectorAll(".question");
    var out = quiz.querySelector(".quiz-result");
    var open = 0;
    qs.forEach(function (q) { if (!q.querySelector("input:checked")) open++; });
    out.className = "quiz-result";
    if (open) {
      out.textContent = "Answer every question first (" + open + " left).";
      return;
    }
    var right = 0;
    qs.forEach(function (q) {
      var answer = q.getAttribute("data-answer");
      var picked = q.querySelector("input:checked");
      var ok = picked.value === answer;
      if (ok) right++;
      q.classList.add(ok ? "right" : "wrong");
      q.querySelectorAll("input").forEach(function (input) {
        input.disabled = true;
        var label = input.closest(".choice");
        if (input.value === answer) label.classList.add("correct");
        else if (input === picked) label.classList.add("chosen-wrong");
      });
      q.querySelector(".why").hidden = false;
    });
    var id = quiz.getAttribute("data-quiz");
    var mark = parseFloat(quiz.getAttribute("data-pass"));
    var passed = right / qs.length >= mark - 1e-9;
    state.best[id] = Math.max(state.best[id] || 0, right);
    out.textContent = right + " of " + qs.length + " correct. " +
      (passed ? "Passed." : "You need " + Math.ceil(mark * qs.length - 1e-9) + " to pass.");
    out.classList.add(passed ? "pass" : "fail");
    quiz.querySelector("[data-check]").hidden = true;
    quiz.querySelector("[data-retry]").hidden = false;
    if (passed) setDone(id, true); else save();
  }
  function retry(quiz) {
    quiz.querySelectorAll(".question").forEach(function (q) {
      q.classList.remove("right", "wrong");
      q.querySelector(".why").hidden = true;
      q.querySelectorAll(".choice").forEach(function (c) { c.classList.remove("correct", "chosen-wrong"); });
      q.querySelectorAll("input").forEach(function (i) { i.disabled = false; i.checked = false; });
    });
    shuffle(quiz);
    var out = quiz.querySelector(".quiz-result");
    out.textContent = ""; out.className = "quiz-result";
    quiz.querySelector("[data-check]").hidden = false;
    quiz.querySelector("[data-retry]").hidden = true;
    quiz.querySelector(".question input").focus();
  }
  var nav = document.getElementById("site-nav");
  var menu = document.querySelector(".menu-button");
  function setMenu(open) {
    nav.classList.toggle("open", open);
    menu.setAttribute("aria-expanded", open ? "true" : "false");
    menu.textContent = open ? "Close" : "Menu";
  }
  var resetTimer;
  document.addEventListener("click", function (e) {
    var t = e.target;
    if (t.closest(".menu-button")) { setMenu(!nav.classList.contains("open")); return; }
    if (t.closest("#site-nav a")) setMenu(false);
    var b;
    if ((b = t.closest("[data-check]"))) check(b.closest(".quiz"));
    else if ((b = t.closest("[data-retry]"))) retry(b.closest(".quiz"));
    else if ((b = t.closest("[data-mark]"))) {
      var id = b.getAttribute("data-mark"); setDone(id, !isDone(id));
    } else if ((b = t.closest("[data-reset]"))) {
      if (b.getAttribute("data-armed")) {
        clearTimeout(resetTimer);
        state = { done: [], best: {} }; save(); render();
        b.removeAttribute("data-armed"); b.textContent = "Progress reset";
        resetTimer = setTimeout(function () { b.textContent = "Reset progress"; }, 2500);
      } else {
        b.setAttribute("data-armed", "1"); b.textContent = "Click again to reset";
        resetTimer = setTimeout(function () {
          b.removeAttribute("data-armed"); b.textContent = "Reset progress";
        }, 4000);
      }
    }
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && nav.classList.contains("open")) { setMenu(false); menu.focus(); }
  });
  document.querySelectorAll(".quiz").forEach(shuffle);
  render();
})();
"""


if __name__ == "__main__":
    sys.exit(main())
