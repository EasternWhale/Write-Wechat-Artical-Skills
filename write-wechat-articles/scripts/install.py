#!/usr/bin/env python3
"""Install write-wechat-articles into a Codex home directory."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path


SKILL_NAME = "write-wechat-articles"
REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE = REPO_ROOT / "skills" / SKILL_NAME


def default_codex_home() -> Path:
    configured = os.environ.get("CODEX_HOME")
    return Path(configured).expanduser() if configured else Path.home() / ".codex"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install the write-wechat-articles Codex Skill."
    )
    parser.add_argument(
        "--target",
        type=Path,
        default=default_codex_home(),
        help="Codex home directory. Defaults to CODEX_HOME or ~/.codex.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Update an existing installation by copying repository files over it.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    target_home = args.target.expanduser().resolve()
    destination = target_home / "skills" / SKILL_NAME

    if not (SOURCE / "SKILL.md").is_file():
        print(f"Source Skill is incomplete: {SOURCE}", file=sys.stderr)
        return 1

    if destination.exists() and not args.force:
        print(f"Installation already exists: {destination}", file=sys.stderr)
        print("Run again with --force only after reviewing the existing Skill.", file=sys.stderr)
        return 2

    destination.parent.mkdir(parents=True, exist_ok=True)

    try:
        if destination.exists():
            shutil.copytree(SOURCE, destination, dirs_exist_ok=True)
            action = "Updated"
        else:
            shutil.copytree(SOURCE, destination)
            action = "Installed"
    except OSError as exc:
        print(f"Installation failed: {exc}", file=sys.stderr)
        return 1

    print(f"{action}: {destination}")
    print("Restart Codex or open a new task to reload the Skill list.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
