import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_build_curriculum_pages_executes_and_generates_artifacts(tmp_path, monkeypatch):
    public_dir = REPO_ROOT / "public"

    # Execute build_curriculum_pages.py
    cmd = [
        "python3",
        str(REPO_ROOT / "scripts" / "build_curriculum_pages.py"),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert "Curriculum build complete!" in res.stdout

    expected_files = [
        "index.html",
        "tutorial.html",
        "reference.html",
        "module-1.html",
        "module-2.html",
        "module-3.html",
        "module-4.html",
        "module-5.html",
        "module-6.html",
        "module-7.html",
        "module-8.html",
        "scenarios.html",
        "final-exam.html",
        "skillevaluator-mastery-standalone.html",
    ]

    for fname in expected_files:
        fpath = public_dir / fname
        assert fpath.is_file(), f"Missing expected output HTML file: {fname}"
        content = fpath.read_text(encoding="utf-8")
        assert "NVIDIA SkillEvaluator" in content
        assert "<html" in content.lower()
