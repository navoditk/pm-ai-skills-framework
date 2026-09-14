#!/usr/bin/env python3
"""Build GitHub Pages and standalone HTML artifacts for the NVIDIA SkillEvaluator Mastery Curriculum.

Outputs:
  - public/index.html (GitHub Pages landing page with sidebar navigation & dark mode)
  - public/skillevaluator-mastery-standalone.html (Single-file browseable/downloadable artifact)
  - public/<id>.html (Individual page for each curriculum module)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import markdown
except ImportError:
    markdown = None

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = REPO_ROOT / "public"

CURRICULUM_ITEMS = [
    {
        "id": "intro",
        "title": "Trainer Overview & Quick Start",
        "category": "Overview",
        "source": "skills/skillevaluator-mastery/SKILL.md",
        "description": "Interactive agent skill overview, trigger phrases, loading rules, and routing.",
    },
    {
        "id": "tutorial",
        "title": "Self-Paced Hands-On Tutorial",
        "category": "Overview",
        "source": "docs/16_SKILLEVALUATOR_MASTERY.md",
        "description": "Step-by-step exercise from zero experience to running Tier 1-4 checks locally.",
    },
    {
        "id": "reference",
        "title": "Complete SkillEvaluator Reference",
        "category": "Overview",
        "source": "docs/15_SKILLS_AND_SKILLEVALUATOR_REFERENCE.md",
        "description": "One-stop reference guide covering concepts, tiers, findings, bugs, and costs.",
    },
    {
        "id": "module-1",
        "title": "Module 1: What SkillEvaluator Is, and Why",
        "category": "Core Modules",
        "source": "skills/skillevaluator-mastery/references/module-1-overview.md",
        "description": "Core concepts, the four evaluation tiers, and support guarantees.",
    },
    {
        "id": "module-2",
        "title": "Module 2: Tier 1 — Construction & Security",
        "category": "Core Modules",
        "source": "skills/skillevaluator-mastery/references/module-2-tier1.md",
        "description": "Schema validation, security scanning, and quality scores.",
    },
    {
        "id": "module-3",
        "title": "Module 3: Tier 2 — Semantic Similarity",
        "category": "Core Modules",
        "source": "skills/skillevaluator-mastery/references/module-3-tier2.md",
        "description": "Deduplication, embedding requirements, and governance actions.",
    },
    {
        "id": "module-4",
        "title": "Module 4: Tier 3 — Live Agent Evaluation",
        "category": "Core Modules",
        "source": "skills/skillevaluator-mastery/references/module-4-tier3.md",
        "description": "Harbor execution, Docker environments, and Skill Lift calculations.",
    },
    {
        "id": "module-5",
        "title": "Module 5: Tier 4 — Correctness & Graders",
        "category": "Core Modules",
        "source": "skills/skillevaluator-mastery/references/module-5-tier4.md",
        "description": "Ground-truth verification, PM domain graders, and custom rubrics.",
    },
    {
        "id": "module-6",
        "title": "Module 6: Installation & CLI Usage",
        "category": "Core Modules",
        "source": "skills/skillevaluator-mastery/references/module-6-install.md",
        "description": "Pinned installation, environment variables, and CLI subcommands.",
    },
    {
        "id": "module-7",
        "title": "Module 7: Skill Package Layout",
        "category": "Core Modules",
        "source": "skills/skillevaluator-mastery/references/module-7-layout.md",
        "description": "Directory structure, required files, and skill.yaml metadata schema.",
    },
    {
        "id": "module-8",
        "title": "Module 8: Reports, Metrics & CI/CD",
        "category": "Core Modules",
        "source": "skills/skillevaluator-mastery/references/module-8-reports-and-cicd.md",
        "description": "JSON report structures, metrics normalization, and GitHub Actions.",
    },
    {
        "id": "scenarios",
        "title": "Practical Scenario Challenges",
        "category": "Assessment & Practice",
        "source": "skills/skillevaluator-mastery/references/scenarios.md",
        "description": "8 real-world debugging scenarios and step-by-step solutions.",
    },
    {
        "id": "final-exam",
        "title": "Final Exam & Self-Assessment",
        "category": "Assessment & Practice",
        "source": "skills/skillevaluator-mastery/references/final-exam.md",
        "description": "15 comprehensive Q&A assessment covering all 4 tiers.",
    },
]

CSS_STYLES = """
:root {
  --bg-primary: #0d1117;
  --bg-secondary: #161b22;
  --bg-tertiary: #21262d;
  --text-primary: #e6edf3;
  --text-secondary: #8b949e;
  --accent-color: #2f81f7;
  --accent-hover: #58a6ff;
  --border-color: #30363d;
  --code-bg: #161b22;
  --card-bg: #161b22;
  --sidebar-width: 300px;
  --font-stack: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

@media (prefers-color-scheme: light) {
  :root {
    --bg-primary: #ffffff;
    --bg-secondary: #f6f8fa;
    --bg-tertiary: #eaeef2;
    --text-primary: #1f2328;
    --text-secondary: #656d76;
    --accent-color: #0969da;
    --accent-hover: #1f883d;
    --border-color: #d0d7de;
    --code-bg: #f6f8fa;
    --card-bg: #ffffff;
  }
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: var(--font-stack);
  background-color: var(--bg-primary);
  color: var(--text-primary);
  line-height: 1.6;
  display: flex;
  min-height: 100vh;
}

/* Sidebar Navigation */
.sidebar {
  width: var(--sidebar-width);
  background-color: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  overflow-y: auto;
  padding: 1.5rem 1rem;
  z-index: 100;
}

.sidebar-header {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.sidebar-header h1 {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.sidebar-header .subtitle {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-top: 0.25rem;
}

.nav-category {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--text-secondary);
  margin: 1.25rem 0 0.5rem 0.5rem;
  letter-spacing: 0.05em;
}

.nav-list {
  list-style: none;
}

.nav-item {
  margin-bottom: 0.25rem;
}

.nav-link {
  display: block;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  color: var(--text-primary);
  text-decoration: none;
  font-size: 0.875rem;
  transition: background-color 0.15s ease;
}

.nav-link:hover {
  background-color: var(--bg-tertiary);
  color: var(--accent-hover);
}

.nav-link.active {
  background-color: var(--bg-tertiary);
  color: var(--accent-color);
  font-weight: 600;
  border-left: 3px solid var(--accent-color);
}

/* Main Content Area */
.main-content {
  margin-left: var(--sidebar-width);
  flex: 1;
  padding: 2.5rem 3rem;
  max-width: 1000px;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.badge {
  display: inline-block;
  padding: 0.25rem 0.6rem;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 12px;
  background-color: var(--bg-tertiary);
  color: var(--accent-color);
  border: 1px solid var(--border-color);
}

.download-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 1rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: #ffffff;
  background-color: var(--accent-color);
  border-radius: 6px;
  text-decoration: none;
  transition: opacity 0.2s;
}

.download-btn:hover {
  opacity: 0.9;
}

/* Typography & Content Styling */
.markdown-body h1 {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border-color);
}

.markdown-body h2 {
  font-size: 1.4rem;
  font-weight: 600;
  margin-top: 2rem;
  margin-bottom: 0.75rem;
}

.markdown-body h3 {
  font-size: 1.15rem;
  font-weight: 600;
  margin-top: 1.5rem;
  margin-bottom: 0.5rem;
}

.markdown-body p, .markdown-body ul, .markdown-body ol {
  margin-bottom: 1rem;
}

.markdown-body ul, .markdown-body ol {
  padding-left: 1.5rem;
}

.markdown-body li {
  margin-bottom: 0.25rem;
}

.markdown-body table {
  width: 100%;
  border-collapse: collapse;
  margin: 1.25rem 0;
  font-size: 0.9rem;
}

.markdown-body th, .markdown-body td {
  padding: 0.6rem 0.8rem;
  border: 1px solid var(--border-color);
  text-align: left;
}

.markdown-body th {
  background-color: var(--bg-secondary);
  font-weight: 600;
}

.markdown-body code {
  font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
  font-size: 0.85em;
  background-color: var(--code-bg);
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  border: 1px solid var(--border-color);
}

.markdown-body pre {
  background-color: var(--code-bg);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 1rem;
  overflow-x: auto;
  margin: 1rem 0;
}

.markdown-body pre code {
  background: none;
  border: none;
  padding: 0;
  font-size: 0.85rem;
}

.markdown-body blockquote {
  padding: 0.5rem 1rem;
  color: var(--text-secondary);
  border-left: 4px solid var(--accent-color);
  background-color: var(--bg-secondary);
  margin: 1rem 0;
  border-radius: 0 6px 6px 0;
}

.section-card {
  background-color: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

/* Footer */
footer {
  margin-top: 4rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-color);
  font-size: 0.85rem;
  color: var(--text-secondary);
  text-align: center;
}

/* Responsive */
@media (max-width: 768px) {
  body {
    flex-direction: column;
  }
  .sidebar {
    position: relative;
    width: 100%;
    height: auto;
  }
  .main-content {
    margin-left: 0;
    padding: 1.5rem;
  }
}
"""


def strip_yaml_frontmatter(content: str) -> str:
    """Remove YAML frontmatter from markdown content."""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()
    return content.strip()


def render_markdown_to_html(md_text: str) -> str:
    """Convert Markdown string to HTML."""
    text = strip_yaml_frontmatter(md_text)
    if markdown:
        return markdown.markdown(
            text,
            extensions=["fenced_code", "tables", "toc", "sane_lists"],
        )
    # Simple fallback renderer if markdown library is missing
    html_lines = []
    in_code = False
    for line in text.splitlines():
        if line.startswith("```"):
            if in_code:
                html_lines.append("</code></pre>")
                in_code = False
            else:
                html_lines.append("<pre><code>")
                in_code = True
            continue
        if in_code:
            html_lines.append(line.replace("<", "&lt;").replace(">", "&gt;"))
            continue
        if line.startswith("# "):
            html_lines.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith("## "):
            html_lines.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("### "):
            html_lines.append(f"<h3>{line[4:]}</h3>")
        elif line.strip():
            html_lines.append(f"<p>{line}</p>")
    return "\n".join(html_lines)


def build_sidebar_html(active_id: str, is_standalone: bool = False) -> str:
    """Generate sidebar navigation HTML."""
    html = ['<div class="sidebar">']
    html.append('  <div class="sidebar-header">')
    html.append('    <h1><span>🎓</span> SkillEvaluator</h1>')
    html.append('    <div class="subtitle">PM AI Mastery Curriculum</div>')
    html.append('  </div>')

    categories: dict[str, list[dict[str, Any]]] = {}
    for item in CURRICULUM_ITEMS:
        categories.setdefault(item["category"], []).append(item)

    for cat_name, items in categories.items():
        html.append(f'  <div class="nav-category">{cat_name}</div>')
        html.append('  <ul class="nav-list">')
        for item in items:
            active_class = " active" if item["id"] == active_id else ""
            if is_standalone:
                href = f'#{item["id"]}'
            else:
                href = "index.html" if item["id"] == "intro" else f'{item["id"]}.html'
            html.append('    <li class="nav-item">')
            html.append(
                f'      <a href="{href}" class="nav-link{active_class}">{item["title"]}</a>'
            )
            html.append("    </li>")
        html.append("  </ul>")

    html.append("</div>")
    return "\n".join(html)


def build_page_template(
    title: str, content_html: str, active_id: str, is_standalone: bool = False
) -> str:
    """Wrap content in a full HTML page layout."""
    sidebar = build_sidebar_html(active_id, is_standalone=is_standalone)
    download_link = (
        ""
        if is_standalone
        else '<a href="skillevaluator-mastery-standalone.html" class="download-btn" download>📥 Single-File HTML Artifact</a>'
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — NVIDIA SkillEvaluator Mastery</title>
  <style>
{CSS_STYLES}
  </style>
</head>
<body>
{sidebar}
  <div class="main-content">
    <div class="top-bar">
      <span class="badge">NVIDIA SkillEvaluator Framework</span>
      {download_link}
    </div>
    <div class="markdown-body">
{content_html}
    </div>
    <footer>
      <p>PM AI Skills Framework — NVIDIA SkillEvaluator Mastery Curriculum</p>
      <p>Automatically compiled from target repo documentation &amp; interactive skills catalog.</p>
    </footer>
  </div>
</body>
</html>
"""


def build_site() -> None:
    """Compile all curriculum items to public/ HTML pages."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Building curriculum pages into {OUTPUT_DIR}...")

    # Build individual pages & gather content for standalone single file
    standalone_sections = []

    for item in CURRICULUM_ITEMS:
        src_path = REPO_ROOT / item["source"]
        if not src_path.exists():
            print(f"Warning: source path missing {src_path}")
            continue

        raw_md = src_path.read_text(encoding="utf-8")
        html_content = render_markdown_to_html(raw_md)

        # Write individual page
        page_filename = "index.html" if item["id"] == "intro" else f'{item["id"]}.html'
        page_html = build_page_template(item["title"], html_content, active_id=item["id"])
        (OUTPUT_DIR / page_filename).write_text(page_html, encoding="utf-8")
        print(f"  ✓ Created public/{page_filename}")

        # Collect section for standalone artifact
        standalone_sections.append(
            f'<section id="{item["id"]}" class="section-card">\n'
            f'<div class="badge" style="margin-bottom:0.8rem;">{item["category"]}</div>\n'
            f'{html_content}\n'
            f'</section>'
        )

    # Build single-file standalone artifact
    all_content = "\n<hr style='border:1px solid var(--border-color); margin:3rem 0;'>\n".join(
        standalone_sections
    )
    standalone_html = build_page_template(
        "Complete Curriculum Artifact", all_content, active_id="intro", is_standalone=True
    )
    standalone_filename = "skillevaluator-mastery-standalone.html"
    (OUTPUT_DIR / standalone_filename).write_text(standalone_html, encoding="utf-8")
    print(f"  ✓ Created public/{standalone_filename} (Standalone Artifact)")

    print("Curriculum build complete!")


if __name__ == "__main__":
    build_site()
