#!/usr/bin/env python3
"""Render a practical Markdown subset into WeChat-safe inline HTML."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

from validate_gzh_html import validate_fragment
from wrap_preview import build_preview


ROOT = Path(__file__).resolve().parents[1]
THEMES_FILE = ROOT / "assets" / "themes.json"
TOKEN_RE = re.compile(
    r"(`[^`]+`|\*\*.+?\*\*|\+\+.+?\+\+|==.+?==|\[[^\]]+\]\(https?://[^)]+\))"
)
LINK_RE = re.compile(r"^\[([^\]]+)\]\((https?://[^)]+)\)$")
IMAGE_RE = re.compile(r"^!\[([^\]]*)\]\((https?://[^)]+)\)\s*$")
FENCE_RE = re.compile(r"^```([^`]*)$")
UL_RE = re.compile(r"^\s*[-*+]\s+(.+)$")
OL_RE = re.compile(r"^\s*\d+[.)]\s+(.+)$")


def load_themes() -> dict[str, dict[str, str]]:
    return json.loads(THEMES_FILE.read_text(encoding="utf-8"))


def leaf(text: str, style: str = "") -> str:
    attr = f' style="{style}"' if style else ""
    return f'<span leaf=""{attr}>{html.escape(text, quote=False)}</span>'


def inline_markup(text: str, theme: dict[str, str]) -> str:
    pieces: list[str] = []
    position = 0
    for match in TOKEN_RE.finditer(text):
        if match.start() > position:
            pieces.append(leaf(text[position:match.start()]))
        token = match.group(0)
        if token.startswith("**"):
            pieces.append(
                f'<strong style="color:{theme["accent"]};font-weight:700;">'
                f'{leaf(token[2:-2])}</strong>'
            )
        elif token.startswith("++"):
            pieces.append(
                f'<span leaf="" style="border-bottom:2px solid {theme["accent"]};padding-bottom:1px;">'
                f'{html.escape(token[2:-2], quote=False)}</span>'
            )
        elif token.startswith("=="):
            pieces.append(
                f'<span leaf="" style="background:{theme["accent_soft"]};color:{theme["text"]};padding:1px 4px;">'
                f'{html.escape(token[2:-2], quote=False)}</span>'
            )
        elif token.startswith("`"):
            pieces.append(
                f'<span leaf="" style="font-family:Consolas,monospace;background:{theme["accent_soft"]};'
                f'color:{theme["accent"]};padding:2px 5px;border-radius:3px;">'
                f'{html.escape(token[1:-1], quote=False)}</span>'
            )
        else:
            link = LINK_RE.match(token)
            if link:
                label, url = link.groups()
                pieces.append(
                    f'<a href="{html.escape(url, quote=True)}" style="color:{theme["accent"]};text-decoration:underline;">'
                    f'{leaf(label)}</a>'
                )
        position = match.end()
    if position < len(text):
        pieces.append(leaf(text[position:]))
    return "".join(pieces) or leaf("")


def is_block_start(line: str) -> bool:
    stripped = line.strip()
    return bool(
        not stripped
        or stripped.startswith(("#", ">", "```"))
        or UL_RE.match(line)
        or OL_RE.match(line)
        or IMAGE_RE.match(stripped)
        or (stripped.startswith("|") and stripped.endswith("|"))
    )


def table_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_separator(line: str) -> bool:
    cells = table_cells(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def choose_theme(requested: str, source: str, themes: dict[str, dict[str, str]]) -> str:
    if requested != "auto":
        if requested not in themes:
            raise ValueError(f"未知主题：{requested}")
        return requested
    if re.search(r"争议|真相|反对|代价|高估|低估|骗局|为什么.*不", source):
        return "red-white"
    if re.search(r"AI|科技|商业|数据|公司|职场|财经|法律|软件|互联网", source, re.I):
        return "graphite-minimal"
    return "moyu-green"


def render_markdown(source: str, theme_name: str, author: str = "", bio: str = "") -> tuple[str, str]:
    themes = load_themes()
    selected = choose_theme(theme_name, source, themes)
    theme = themes[selected]
    lines = source.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    body: list[str] = []
    title = "公众号文章"
    h2_number = 0
    index = 0

    root_style = (
        f'max-width:100%;box-sizing:border-box;background:{theme["paper"]};color:{theme["text"]};'
        'font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;'
        'font-size:16px;line-height:1.85;padding:24px 20px;letter-spacing:.02em;'
    )
    body.append(f'<section style="{root_style}">')
    body.append(
        f'<section style="border-top:4px solid {theme["accent"]};width:54px;margin:0 0 24px 0;"></section>'
    )

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if not stripped:
            index += 1
            continue

        fence = FENCE_RE.match(stripped)
        if fence:
            language = fence.group(1).strip()
            index += 1
            code_lines: list[str] = []
            while index < len(lines) and not lines[index].strip().startswith("```"):
                code_lines.append(lines[index])
                index += 1
            index += 1 if index < len(lines) else 0
            label = f"{language} · CODE" if language else "CODE"
            label_html = leaf(label, f'color:{theme["code_text"]};opacity:.72;')
            body.append(
                f'<section style="margin:22px 0;border-radius:7px;overflow:hidden;background:{theme["code"]};">'
                f'<p style="margin:0;padding:7px 13px;border-bottom:1px solid {theme["muted"]};font-size:12px;line-height:1.4;">'
                f'{label_html}</p>'
                f'<section style="padding:14px;white-space:pre-wrap;word-break:break-word;font-family:Consolas,monospace;'
                f'font-size:13px;line-height:1.65;color:{theme["code_text"]};">{leaf(chr(10).join(code_lines))}</section></section>'
            )
            continue

        image_match = IMAGE_RE.match(stripped)
        if image_match:
            alt, url = image_match.groups()
            body.append(
                f'<section style="margin:24px 0;text-align:center;">'
                f'<img src="{html.escape(url, quote=True)}" alt="{html.escape(alt, quote=True)}" '
                'style="display:block;width:100%;max-width:100%;height:auto;margin:0 auto;border-radius:6px;">'
                + (f'<p style="margin:8px 0 0;font-size:12px;line-height:1.5;color:{theme["muted"]};">{leaf(alt)}</p>' if alt else "")
                + '</section>'
            )
            index += 1
            continue

        if stripped.startswith("# "):
            title = stripped[2:].strip()
            body.append(
                f'<h1 style="margin:0 0 12px;font-size:30px;line-height:1.32;font-weight:800;letter-spacing:-.02em;'
                f'color:{theme["text"]};">{inline_markup(title, theme)}</h1>'
                f'<p style="margin:0 0 28px;font-size:12px;line-height:1.5;color:{theme["muted"]};letter-spacing:.12em;">'
                f'{leaf(theme["label"].upper())}</p>'
            )
            index += 1
            continue

        if stripped.startswith("## "):
            h2_number += 1
            heading = stripped[3:].strip()
            body.append(
                f'<section style="margin:38px 0 17px;padding:0 0 9px;border-bottom:1px solid {theme["border"]};">'
                f'<p style="margin:0 0 3px;font-size:12px;line-height:1.4;color:{theme["accent"]};font-weight:700;letter-spacing:.14em;">'
                f'{leaf(f"SECTION {h2_number:02d}")}</p>'
                f'<h2 style="margin:0;font-size:23px;line-height:1.45;font-weight:750;color:{theme["text"]};">'
                f'{inline_markup(heading, theme)}</h2></section>'
            )
            index += 1
            continue

        if stripped.startswith("### "):
            heading = stripped[4:].strip()
            body.append(
                f'<h3 style="margin:27px 0 11px;padding-left:10px;border-left:3px solid {theme["accent"]};'
                f'font-size:18px;line-height:1.55;font-weight:700;color:{theme["text"]};">'
                f'{inline_markup(heading, theme)}</h3>'
            )
            index += 1
            continue

        if stripped.startswith(">"):
            quotes: list[str] = []
            while index < len(lines) and lines[index].strip().startswith(">"):
                quotes.append(lines[index].strip()[1:].strip())
                index += 1
            quote_text = " ".join(quotes)
            body.append(
                f'<section style="margin:22px 0;padding:16px 18px;background:{theme["quote"]};'
                f'border-left:4px solid {theme["accent"]};">'
                f'<p style="margin:0;font-size:15px;line-height:1.8;color:{theme["text"]};">'
                f'{inline_markup(quote_text, theme)}</p></section>'
            )
            continue

        list_match = UL_RE.match(line) or OL_RE.match(line)
        if list_match:
            ordered = bool(OL_RE.match(line))
            pattern = OL_RE if ordered else UL_RE
            tag = "ol" if ordered else "ul"
            items: list[str] = []
            while index < len(lines):
                item_match = pattern.match(lines[index])
                if not item_match:
                    break
                items.append(item_match.group(1).strip())
                index += 1
            rendered = "".join(
                f'<li style="margin:7px 0;padding-left:3px;color:{theme["text"]};">{inline_markup(item, theme)}</li>'
                for item in items
            )
            body.append(
                f'<{tag} style="margin:17px 0;padding-left:24px;font-size:16px;line-height:1.8;">{rendered}</{tag}>'
            )
            continue

        if stripped.startswith("|") and stripped.endswith("|") and index + 1 < len(lines) and is_separator(lines[index + 1]):
            headers = table_cells(line)
            index += 2
            rows: list[list[str]] = []
            while index < len(lines) and lines[index].strip().startswith("|") and lines[index].strip().endswith("|"):
                rows.append(table_cells(lines[index]))
                index += 1
            head_html = "".join(
                f'<th style="padding:9px;border:1px solid {theme["border"]};background:{theme["accent_soft"]};text-align:left;">'
                f'{inline_markup(cell, theme)}</th>' for cell in headers
            )
            row_html = "".join(
                '<tr>' + "".join(
                    f'<td style="padding:9px;border:1px solid {theme["border"]};vertical-align:top;">'
                    f'{inline_markup(cell, theme)}</td>' for cell in row
                ) + '</tr>' for row in rows
            )
            body.append(
                f'<section style="margin:20px 0;overflow-x:auto;"><table style="width:100%;border-collapse:collapse;'
                f'font-size:14px;line-height:1.6;"><thead><tr>{head_html}</tr></thead><tbody>{row_html}</tbody></table></section>'
            )
            continue

        paragraph = [stripped]
        index += 1
        while index < len(lines) and not is_block_start(lines[index]):
            paragraph.append(lines[index].strip())
            index += 1
        text = " ".join(part for part in paragraph if part)
        body.append(
            f'<p style="margin:0 0 16px;font-size:16px;line-height:1.85;text-align:justify;color:{theme["text"]};">'
            f'{inline_markup(text, theme)}</p>'
        )

    if author:
        signature = author + (f"｜{bio}" if bio else "")
        body.append(
            f'<section style="margin:34px 0 0;padding-top:16px;border-top:1px solid {theme["border"]};text-align:right;">'
            f'<p style="margin:0;font-size:13px;line-height:1.6;color:{theme["muted"]};">{leaf(signature)}</p></section>'
        )
    body.append('</section>')
    return "\n".join(body), selected


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="把 Markdown 渲染为微信公众号可粘贴 HTML")
    parser.add_argument("input", nargs="?", type=Path)
    parser.add_argument("--theme", default="auto")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--preview", action="store_true")
    parser.add_argument("--preview-output", type=Path)
    parser.add_argument("--author", default="")
    parser.add_argument("--bio", default="")
    parser.add_argument("--list-themes", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    themes = load_themes()
    if args.list_themes:
        for name, theme in themes.items():
            print(f'{name}: {theme["label"]}')
        return 0
    if args.input is None:
        print("ERROR: 请提供 Markdown 文件，或使用 --list-themes", file=sys.stderr)
        return 2
    try:
        source = args.input.read_text(encoding="utf-8")
        fragment, selected = render_markdown(source, args.theme, args.author, args.bio)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    errors, warnings, leaf_count = validate_fragment(fragment)
    for warning in warnings:
        print(f"WARNING: {warning}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    output = args.output or args.input.with_name(f"{args.input.stem}_wechat.html")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(fragment + "\n", encoding="utf-8")
    print(f"主题：{selected}")
    print(f"正文 HTML：{output.resolve()}")
    print(f"校验：PASS（span leaf {leaf_count} 处）")

    if args.preview or args.preview_output:
        preview = args.preview_output or args.input.with_name(f"{args.input.stem}_preview.html")
        preview.parent.mkdir(parents=True, exist_ok=True)
        preview.write_text(build_preview(fragment, args.input.stem), encoding="utf-8")
        print(f"一键复制预览：{preview.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
