#!/usr/bin/env python3
"""Wrap a validated article fragment in a browser preview with a copy button."""

from __future__ import annotations

import argparse
import html
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "assets" / "preview-template.html"


def build_preview(fragment: str, title: str) -> str:
    template = TEMPLATE.read_text(encoding="utf-8")
    return template.replace("{{TITLE}}", html.escape(title)).replace(
        "<!--WECHAT_CONTENT-->", fragment.strip()
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="生成带一键复制按钮的公众号预览页")
    parser.add_argument("input", type=Path, help="已校验的正文 HTML")
    parser.add_argument("output", nargs="?", type=Path, help="预览页输出路径")
    args = parser.parse_args()

    try:
        fragment = args.input.read_text(encoding="utf-8")
    except OSError as exc:
        parser.error(str(exc))
    output = args.output or args.input.with_name(f"{args.input.stem}_preview.html")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_preview(fragment, args.input.stem), encoding="utf-8")
    print(f"预览页：{output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
