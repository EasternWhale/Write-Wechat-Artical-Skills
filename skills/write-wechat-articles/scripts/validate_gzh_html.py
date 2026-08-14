#!/usr/bin/env python3
"""Validate a WeChat article fragment before it is copied into the editor."""

from __future__ import annotations

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path


FORBIDDEN = [
    (re.compile(r"<style[\s>]", re.I), "正文不能包含 <style>"),
    (re.compile(r"<script[\s>]", re.I), "正文不能包含 <script>"),
    (re.compile(r"</?div[\s>]", re.I), "请用 <section> 代替 <div>"),
    (re.compile(r"<link[\s>]", re.I), "正文不能包含外部 <link>"),
    (re.compile(r"\sclass\s*=", re.I), "class 粘贴后可能被移除，请使用内联样式"),
    (re.compile(r"\sid\s*=", re.I), "id 粘贴后可能被移除"),
    (re.compile(r"position\s*:\s*(fixed|absolute|sticky)", re.I), "不支持固定或绝对定位"),
    (re.compile(r"float\s*:", re.I), "不支持 float"),
    (re.compile(r"@(?:media|keyframes|import)", re.I), "不支持 CSS at-rule"),
    (re.compile(r"display\s*:\s*grid", re.I), "不支持 display:grid"),
    (re.compile(r"var\s*\(\s*--", re.I), "不支持 CSS 变量"),
    (re.compile(r"url\s*\(\s*['\"]?https?://[^)]*\.(?:woff2?|ttf|otf|eot)", re.I), "不支持外部字体"),
]

CJK = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")
HALF_PUNCT = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff][,;!?]")
CODE_STYLE = re.compile(r"monospace|white-space\s*:\s*pre|courier|consolas", re.I)
SKIP_TAGS = {"head", "title", "style", "script"}


class FragmentChecker(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, bool, bool]] = []
        self.leaf_depth = 0
        self.code_depth = 0
        self.leaf_count = 0
        self.unwrapped: list[str] = []
        self.half_punct: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        is_leaf = tag == "span" and "leaf" in values
        is_code = bool(CODE_STYLE.search(values.get("style", "") or ""))
        self.stack.append((tag, is_leaf, is_code))
        if is_leaf:
            self.leaf_depth += 1
            self.leaf_count += 1
        if is_code:
            self.code_depth += 1

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                removed = self.stack[index:]
                self.stack[index:] = []
                self.leaf_depth -= sum(1 for _, leaf, _ in removed if leaf)
                self.code_depth -= sum(1 for _, _, code in removed if code)
                return

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if not text or any(tag in SKIP_TAGS for tag, _, _ in self.stack):
            return
        if CJK.search(text) and self.leaf_depth == 0:
            self.unwrapped.append(text[:32])
        if self.code_depth == 0 and HALF_PUNCT.search(text):
            self.half_punct.append(text[:32])


def validate_fragment(source: str) -> tuple[list[str], list[str], int]:
    errors: list[str] = []
    warnings: list[str] = []
    stripped = source.strip()

    if not re.match(r"^<section(?:\s|>)", stripped, re.I):
        errors.append("正文必须以单个根 <section> 开始")
    if not re.search(r"</section>\s*$", stripped, re.I):
        errors.append("正文必须以 </section> 结束")

    for pattern, message in FORBIDDEN:
        count = len(pattern.findall(source))
        if count:
            errors.append(f"{message}（{count} 处）")

    checker = FragmentChecker()
    try:
        checker.feed(source)
        checker.close()
    except Exception as exc:
        errors.append(f"HTML 解析失败：{exc}")

    if CJK.search(source) and checker.leaf_count == 0:
        errors.append('中文正文没有使用 <span leaf=""> 包裹')
    elif checker.unwrapped:
        sample = "；".join(checker.unwrapped[:4])
        warnings.append(f"{len(checker.unwrapped)} 处中文文字未被 leaf 包裹，例如：{sample}")
    if checker.half_punct:
        sample = "；".join(checker.half_punct[:4])
        warnings.append(f"疑似中文半角标点 {len(checker.half_punct)} 处，例如：{sample}")

    return errors, warnings, checker.leaf_count


def main() -> int:
    parser = argparse.ArgumentParser(description="校验微信公众号正文 HTML 片段")
    parser.add_argument("file", nargs="?", type=Path)
    parser.add_argument("--stdin", action="store_true")
    args = parser.parse_args()

    if args.stdin or args.file is None:
        source = sys.stdin.read()
        name = "<stdin>"
    else:
        try:
            source = args.file.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"读取失败：{exc}", file=sys.stderr)
            return 1
        name = str(args.file)

    errors, warnings, leaf_count = validate_fragment(source)
    print(f"公众号 HTML 校验：{name}")
    print(f"span leaf：{leaf_count} 处")
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    if not errors:
        print("PASS: 正文片段可进入预览复制流程")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
