from pathlib import Path
import importlib.util
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def _load_package_chat():
    path = ROOT / "scripts" / "package_chat.py"
    spec = importlib.util.spec_from_file_location("package_chat_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def test_chat_bootstrap_has_explicit_precedence_and_core_independence():
    text = (ROOT / "SYSTEM-MODELLER-CHAT.md").read_text(encoding="utf-8")
    assert "instructions/chat-runtime.md" in text
    assert "instructions/source-analysis.md" in text
    assert "metamodel/" in text and "schemas/" in text
    assert "examples/" in text
    assert "Kärnflödet ska fungera" in text

def test_chat_package_excludes_development_material(tmp_path):
    mod = _load_package_chat()
    out = tmp_path / "chat.zip"
    mod.build(out, "0.1.0-test")
    with zipfile.ZipFile(out) as zf:
        names = set(zf.namelist())
    assert not any("/tests/" in n for n in names)
    assert "docs/github-actions.md" not in names
    assert "docs/release-readiness.md" not in names
    assert "docs/test-environment-isolation.md" not in names
    assert "scripts/ci_build.py" not in names
    assert "scripts/release_check.py" not in names
    assert "scripts/package_custom_gpt.py" not in names
    assert "scripts/package_chat.py" not in names

def test_chat_package_retains_runtime_material(tmp_path):
    mod = _load_package_chat()
    out = tmp_path / "chat.zip"
    mod.build(out, "0.1.0-test")
    with zipfile.ZipFile(out) as zf:
        names = set(zf.namelist())
    required = {
        "SYSTEM-MODELLER-CHAT.md",
        "instructions/chat-runtime.md",
        "instructions/source-analysis.md",
        "docs/modeling-principles.md",
        "docs/architecture-description.md",
        "scripts/analyze.py",
        "scripts/validate.py",
        "scripts/report.py",
        "scripts/view.py",
        "scripts/package_project.py",
    }
    assert required.issubset(names)
    assert any(n.startswith("metamodel/") for n in names)
    assert any(n.startswith("schemas/") for n in names)
    assert any(n.startswith("templates/system-project/") for n in names)
