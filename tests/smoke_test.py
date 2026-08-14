#!/usr/bin/env python3
"""Render every built-in theme and check both fragment and preview boundaries."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "write-wechat-articles"
RENDER = SKILL / "scripts" / "render_wechat.py"
VALIDATE = SKILL / "scripts" / "validate_gzh_html.py"
SAMPLE = ROOT / "tests" / "sample.md"


def run(*args: str) -> None:
    environment = os.environ.copy()
    environment["PYTHONUTF8"] = "1"
    result = subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        capture_output=True,
        encoding="utf-8",
        env=environment,
    )
    if result.returncode:
        raise RuntimeError(f"Command failed: {' '.join(args)}\n{result.stdout}\n{result.stderr}")


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        temp = Path(directory)
        for theme in ("moyu-green", "red-white", "graphite-minimal"):
            fragment = temp / f"{theme}.html"
            preview = temp / f"{theme}-preview.html"
            run(sys.executable, str(RENDER), str(SAMPLE), "--theme", theme, "--output", str(fragment), "--preview-output", str(preview))
            run(sys.executable, str(VALIDATE), str(fragment))
            fragment_text = fragment.read_text(encoding="utf-8")
            preview_text = preview.read_text(encoding="utf-8")
            assert fragment_text.lstrip().startswith("<section")
            assert "<script" not in fragment_text and "<style" not in fragment_text
            assert 'span leaf=""' in fragment_text
            assert "复制到公众号" in preview_text and "<script" in preview_text
    print("Smoke tests passed: 3 themes, validated fragments, copy previews")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
