# 微信 HTML 输出

## 快速生成

在技能目录执行：

```bash
python scripts/render_wechat.py article.md --theme auto --preview
```

常用参数：

```text
--theme moyu-green|red-white|graphite-minimal|auto
--output PATH       指定纯正文 HTML 路径
--preview           同时生成带复制按钮的预览页
--preview-output    指定预览页路径
--author NAME       在末尾增加署名
--bio TEXT          增加一句作者简介
--list-themes       列出主题并退出
```

默认输出：

- `article_wechat.html`：只有可粘贴正文，以单个根 `<section>` 开始；不含页面壳、按钮或脚本。
- `article_preview.html`：浏览器预览页。点击“复制到公众号”后，到微信公众号编辑器按 `Ctrl+V`／`⌘V`。

## 正文红线

- 只使用微信相对稳定的语义标签和内联样式。
- 禁止 `<style>`、`<script>`、`<div>`、`<link>`、`class`、`id`。
- 禁止 `position: fixed/absolute/sticky`、`float`、`display:grid`、CSS 变量、媒体查询、动画和外部字体。
- 正文中的文字节点使用 `<span leaf="">` 包裹，降低粘贴后的样式损失。
- 预览页可以有脚本和样式，但预览外壳永远不得作为正文校验或粘贴目标。

## 校验

渲染器默认先校验再写出；也可以单独运行：

```bash
python scripts/validate_gzh_html.py output_wechat.html
```

退出码 `0` 表示无致命问题；`1` 表示必须修复。警告通常是半角中文标点、未包裹文字或外链图片提醒，交付前应人工确认。

## 能力降级

若当前 Agent 不能执行 Python：

1. 交付最终 Markdown。
2. 告知用户进入技能目录后运行上面的渲染命令。
3. 不凭记忆手写大段内联 HTML，不伪造校验成功信息。
