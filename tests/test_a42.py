from pathlib import Path
import importlib.util
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def _mode(info: zipfile.ZipInfo) -> int:
    return (info.external_attr >> 16) & 0o777

def test_repository_package_preserves_executable_script_modes(tmp_path):
    # package.py writes to ROOT/distributions, so run it and inspect the produced ZIP.
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "package.py")],
        cwd=ROOT, capture_output=True, text=True
    )
    assert result.returncode == 0, result.stdout + result.stderr
    out = Path(result.stdout.strip().splitlines()[-1])
    assert out.is_file()

    with zipfile.ZipFile(out) as zf:
        script_infos = [
            i for i in zf.infolist()
            if i.filename.startswith("system-modeller/scripts/")
            and Path(i.filename).suffix in {".py", ".sh"}
        ]
        assert script_infos
        assert all(_mode(i) == 0o755 for i in script_infos), [
            (i.filename, oct(_mode(i))) for i in script_infos
        ]

def test_chat_package_runtime_scripts_are_executable(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts"))
    import package_chat
    out = tmp_path / "chat.zip"
    package_chat.build(out, "0.1.0-test")
    with zipfile.ZipFile(out) as zf:
        script_infos = [
            i for i in zf.infolist()
            if i.filename.startswith("system-modeller/scripts/")
            and Path(i.filename).suffix in {".py", ".sh"}
        ]
        assert script_infos
        assert all(_mode(i) == 0o755 for i in script_infos)
