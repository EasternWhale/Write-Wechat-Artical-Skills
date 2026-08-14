#!/usr/bin/env python3
"""Validate the portable Agent Skill and its deterministic renderer."""

from __future__ import annotations

import json
import py_compile
import re
from pathlib import Path


SKILL_NAME = "write-wechat-articles"
REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / SKILL_NAME
SKILL_MD = SKILL_ROOT / "SKILL.md"
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
REQUIRED_THEME_KEYS = {
    "label", "accent", "accent_soft", "paper", "text", "muted", "border", "quote", "code", "code_text"
}


class Validator:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)

    def read(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            self.errors.append(f"Cannot read UTF-8 file {path.relative_to(REPO_ROOT)}: {exc}")
            return ""


def frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        return {}
    values: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip()
    return values


def validate() -> list[str]:
    validator = Validator()
    skill_text = validator.read(SKILL_MD)
    meta = frontmatter(skill_text)
    validator.check(set(meta) == {"name", "description"}, "SKILL.md frontmatter must contain name and description only")
    validator.check(meta.get("name") == SKILL_NAME, "Skill name must match its directory")
    validator.check(bool(NAME_PATTERN.fullmatch(SKILL_NAME)), "Skill name is invalid")
    validator.check(0 < len(meta.get("description", "")) <= 1024, "Description must be 1-1024 characters")
    validator.check(len(skill_text.splitlines()) < 500, "SKILL.md should remain under 500 lines")

    for link in LINK_PATTERN.findall(skill_text):
        if "://" in link or link.startswith("#"):
            continue
        target = (SKILL_ROOT / link).resolve()
        try:
            target.relative_to(SKILL_ROOT.resolve())
        except ValueError:
            validator.errors.append(f"Link escapes Skill directory: {link}")
            continue
        validator.check(target.is_file(), f"Broken Skill link: {link}")

    required = [
        "assets/themes.json",
        "assets/preview-template.html",
        "scripts/render_wechat.py",
        "scripts/validate_gzh_html.py",
        "scripts/wrap_preview.py",
        "references/theme-index.md",
        "references/html-output.md",
        "agents/openai.yaml",
    ]
    for relative in required:
        validator.check((SKILL_ROOT / relative).is_file(), f"Missing Skill resource: {relative}")

    for path in SKILL_ROOT.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".md", ".py", ".json", ".html", ".yaml"}:
            text = validator.read(path)
            validator.check("[TODO" not in text, f"Placeholder remains in {path.relative_to(REPO_ROOT)}")

    try:
        themes = json.loads(validator.read(SKILL_ROOT / "assets" / "themes.json"))
        validator.check(set(themes) == {"moyu-green", "red-white", "graphite-minimal"}, "Theme registry has unexpected theme names")
        for name, values in themes.items():
            validator.check(set(values) == REQUIRED_THEME_KEYS, f"Theme {name} has missing or extra keys")
    except json.JSONDecodeError as exc:
        validator.errors.append(f"Invalid themes.json: {exc}")

    for path in list((SKILL_ROOT / "scripts").glob("*.py")) + list((REPO_ROOT / "scripts").glob("*.py")):
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as exc:
            validator.errors.append(f"Python compile failed for {path.relative_to(REPO_ROOT)}: {exc.msg}")

    yaml = validator.read(SKILL_ROOT / "agents" / "openai.yaml")
    validator.check("display_name:" in yaml and "short_description:" in yaml, "agents/openai.yaml is incomplete")
    validator.check(f"${SKILL_NAME}" in yaml, "OpenAI default prompt must mention the skill")
    for name in ("README.md", "LICENSE"):
        validator.check((REPO_ROOT / name).is_file(), f"Missing repository file: {name}")
    return validator.errors


def main() -> int:
    errors = validate()
    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Validation passed: skills/{SKILL_NAME}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
