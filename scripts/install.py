#!/usr/bin/env python3
"""Install the skill for common Agent Skills clients without third-party packages."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path


SKILL_NAME = "write-wechat-articles"
REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE = REPO_ROOT / "skills" / SKILL_NAME


def user_root(agent: str) -> Path:
    home = Path.home()
    if agent == "codex":
        codex_home = Path(os.environ.get("CODEX_HOME", home / ".codex")).expanduser()
        return codex_home / "skills"
    return {
        "agents": home / ".agents" / "skills",
        "claude": home / ".claude" / "skills",
        "cursor": home / ".cursor" / "skills",
        "copilot": home / ".copilot" / "skills",
        "gemini": home / ".gemini" / "skills",
        "opencode": home / ".config" / "opencode" / "skills",
    }[agent]


def project_root(agent: str, project: Path) -> Path:
    return {
        "agents": project / ".agents" / "skills",
        "codex": project / ".codex" / "skills",
        "claude": project / ".claude" / "skills",
        "cursor": project / ".cursor" / "skills",
        "copilot": project / ".github" / "skills",
        "gemini": project / ".gemini" / "skills",
        "opencode": project / ".opencode" / "skills",
    }[agent]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="安装全领域公众号写作与排版 Skill")
    parser.add_argument(
        "--agent",
        choices=("agents", "codex", "claude", "cursor", "copilot", "gemini", "opencode", "all"),
        default="agents",
        help="目标 Agent；默认 agents 使用开放的 ~/.agents/skills 共享目录。",
    )
    parser.add_argument("--scope", choices=("user", "project"), default="user")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="项目级安装的项目根目录，默认当前目录。",
    )
    parser.add_argument(
        "--target",
        type=Path,
        help="高级用法：直接指定 skills 父目录，忽略 --agent 与 --scope。",
    )
    parser.add_argument("--force", action="store_true", help="覆盖更新已有安装。")
    return parser.parse_args()


def destinations(args: argparse.Namespace) -> list[Path]:
    if args.target:
        return [args.target.expanduser().resolve() / SKILL_NAME]
    agents = ["agents", "codex", "claude", "cursor", "copilot", "gemini", "opencode"] if args.agent == "all" else [args.agent]
    roots = [
        user_root(agent) if args.scope == "user" else project_root(agent, args.project_root.expanduser().resolve())
        for agent in agents
    ]
    unique: list[Path] = []
    for root in roots:
        destination = root.resolve() / SKILL_NAME
        if destination not in unique:
            unique.append(destination)
    return unique


def install(destination: Path, force: bool) -> str:
    if destination.exists() and not force:
        raise FileExistsError(f"已存在：{destination}（确认后使用 --force 更新）")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        shutil.copytree(SOURCE, destination, dirs_exist_ok=True)
        return "已更新"
    shutil.copytree(SOURCE, destination)
    return "已安装"


def main() -> int:
    args = parse_args()
    if not (SOURCE / "SKILL.md").is_file():
        print(f"Skill 源目录不完整：{SOURCE}", file=sys.stderr)
        return 1
    try:
        for destination in destinations(args):
            action = install(destination, args.force)
            print(f"{action}：{destination}")
    except (OSError, FileExistsError) as exc:
        print(f"安装失败：{exc}", file=sys.stderr)
        return 2
    print("请重新启动目标 Agent，或新建会话以重新加载技能列表。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
