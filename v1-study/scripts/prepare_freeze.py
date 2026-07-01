"""Gera FROZEN_COMMIT.txt — correr depois do pytest verde e do git commit."""
import datetime
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(ROOT)


def git_head(cwd):
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                           text=True, cwd=cwd, timeout=5)
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:
        return None


def main():
    commit = git_head(REPO) or git_head(ROOT)
    out_path = os.path.join(REPO, "docs", "osf", "FROZEN_COMMIT.txt")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        f"frozen_at: {now}",
        f"git_commit: {commit or 'PENDING — init git repo and commit before tagging'}",
        "tag: prereg-v2.0 (run: git tag -a prereg-v2.0 -m 'Pre-registration freeze v2')",
        "phase5: cd v1-study && python -m pytest tests/ -v",
    ]
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Wrote {out_path}")
    if not commit:
        print("NOTE: initialize git and commit before creating tag prereg-v2.0")


if __name__ == "__main__":
    main()
