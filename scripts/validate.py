#!/usr/bin/env python3
"""Validate repository and Skill structure without third-party dependencies."""

from __future__ import annotations

import re
import sys
from pathlib import Path


SKILL_NAME = "write-wechat-articles"
REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / SKILL_NAME
SKILL_MD = SKILL_ROOT / "SKILL.md"
OPENAI_YAML = SKILL_ROOT / "agents" / "openai.yaml"
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+\.md)\)")


class Validator:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)

    def read_utf8(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8")
        except FileNotFoundError:
            self.errors.append(f"Missing file: {path.relative_to(REPO_ROOT)}")
        except UnicodeDecodeError:
            self.errors.append(f"File is not valid UTF-8: {path.relative_to(REPO_ROOT)}")
        return ""


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}
    result: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip()
    return result


def validate() -> list[str]:
    validator = Validator()
    validator.check(SKILL_ROOT.is_dir(), f"Missing Skill directory: skills/{SKILL_NAME}")

    skill_text = validator.read_utf8(SKILL_MD)
    frontmatter = parse_frontmatter(skill_text)
    validator.check(bool(frontmatter), "SKILL.md must start with valid YAML frontmatter")
    validator.check(
        set(frontmatter) == {"name", "description"},
        "SKILL.md frontmatter must contain only name and description",
    )
    validator.check(frontmatter.get("name") == SKILL_NAME, "Skill name does not match folder")
    validator.check(bool(NAME_PATTERN.fullmatch(SKILL_NAME)), "Skill name is invalid")
    validator.check(bool(frontmatter.get("description")), "Skill description is empty")
    validator.check("TODO" not in skill_text and "[TODO" not in skill_text, "SKILL.md contains TODO placeholders")

    for link in LINK_PATTERN.findall(skill_text):
        target = (SKILL_ROOT / link).resolve()
        try:
            target.relative_to(SKILL_ROOT.resolve())
        except ValueError:
            validator.errors.append(f"Reference link escapes Skill directory: {link}")
            continue
        validator.check(target.is_file(), f"Broken Skill reference link: {link}")

    for path in SKILL_ROOT.rglob("*"):
        if path.is_file():
            text = validator.read_utf8(path)
            validator.check("[TODO" not in text, f"Placeholder remains in {path.relative_to(REPO_ROOT)}")

    yaml_text = validator.read_utf8(OPENAI_YAML)
    display = re.search(r'^\s*display_name:\s*"([^"]+)"\s*$', yaml_text, re.MULTILINE)
    short = re.search(r'^\s*short_description:\s*"([^"]+)"\s*$', yaml_text, re.MULTILINE)
    default = re.search(r'^\s*default_prompt:\s*"([^"]+)"\s*$', yaml_text, re.MULTILINE)
    validator.check(bool(display), "agents/openai.yaml is missing display_name")
    validator.check(bool(short), "agents/openai.yaml is missing short_description")
    if short:
        validator.check(25 <= len(short.group(1)) <= 64, "short_description must be 25-64 characters")
    validator.check(bool(default), "agents/openai.yaml is missing default_prompt")
    if default:
        validator.check(f"${SKILL_NAME}" in default.group(1), "default_prompt must mention the Skill explicitly")

    for required in (REPO_ROOT / "README.md", REPO_ROOT / "LICENSE"):
        validator.check(required.is_file(), f"Missing repository file: {required.name}")

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
