import subprocess
import config


def test_manifest_git_commit():
    """Manifest helper returns str or None without crashing."""
    from run import _git_commit
    h = _git_commit()
    assert h is None or isinstance(h, str)


def test_dry_run_full_panel():
    r = subprocess.run(
        ["python", "run.py", "--full"],
        cwd=config.ROOT, capture_output=True, text=True, timeout=30)
    assert r.returncode == 0
    assert "21" in r.stdout or "Qwen3 235B" in r.stdout
