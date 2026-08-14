# write-wechat-articles

一个面向主流 AI Agent 的全领域微信公众号写作与排版 Skill：从选题、研究、争议设计、事实核查和中文自然化，一直完成到微信兼容 HTML 与“一键复制到公众号”预览页。

核心目录遵循 [Agent Skills 开放规范](https://agentskills.io/specification)，不绑定某个模型。排版能力内置于仓库。

- 生成并评分公众号选题，输出标题、大纲、全文或系列策划；
- 覆盖文学、影视、音乐、科技、商业、财经、职场、教育、健康、法律、历史、消费、旅行等领域；
- 制造有依据、可辩论的观点冲突，不靠虚构事实、群体攻击或标题诈骗；
- 按风险等级核查数据、引语、时效信息和专业结论；
- 处理宣传腔、模糊归因、机械连接词、三段式等常见 AI 写作痕迹；
- 把最终 Markdown 渲染成内联样式的微信公众号 HTML；
- 自动校验微信排版红线，并生成带“一键复制”按钮的浏览器预览页。

## Agent 兼容性

Skill 本体只要求客户端能读取 `SKILL.md`；HTML 渲染需要 Python 3.9+。安装器支持以下目录：

| 目标 | 用户级目录 | 项目级目录 | 安装参数 |
|---|---|---|---|
| 开放共享目录 | `~/.agents/skills` | `.agents/skills` | `--agent agents` |
| OpenAI Codex | `~/.codex/skills` | `.codex/skills` | `--agent codex` |
| Claude Code | `~/.claude/skills` | `.claude/skills` | `--agent claude` |
| Cursor | `~/.cursor/skills` | `.cursor/skills` | `--agent cursor` |
| GitHub Copilot / VS Code | `~/.copilot/skills` | `.github/skills` | `--agent copilot` |
| Gemini CLI | `~/.gemini/skills` | `.gemini/skills` | `--agent gemini` |
| OpenCode | `~/.config/opencode/skills` | `.opencode/skills` | `--agent opencode` |

`.agents/skills` 是默认值，Gemini CLI、OpenCode 和 GitHub Copilot 等客户端原生识别这个共享别名；若某个产品只扫描自己的目录，改用对应参数即可。各产品仍可能更新发现路径，安装器把路径集中在一个文件中，便于调整。

规范与路径依据：[Agent Skills](https://agentskills.io/specification)、[GitHub Copilot](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)、[VS Code](https://code.visualstudio.com/docs/agent-customization/agent-skills)、[Gemini CLI](https://geminicli.com/docs/cli/using-agent-skills/)、[OpenCode](https://opencode.ai/docs/skills)。

## 安装

### Windows CMD / PowerShell

```bat
git clone https://github.com/EasternWhale/Write-Wechat-Artical-Skills.git
cd Write-Wechat-Artical-Skills
py scripts\install.py --agent codex
```

安装到开放共享目录：

```bat
py scripts\install.py
```

更新已有安装：

```bat
py scripts\install.py --agent codex --force
```

### macOS / Linux

```bash
git clone https://github.com/EasternWhale/Write-Wechat-Artical-Skills.git
cd Write-Wechat-Artical-Skills
python3 scripts/install.py --agent agents
```

### 其他安装方式

安装到当前项目：

```bash
python scripts/install.py --agent copilot --scope project
```

一次复制到所有产品专属目录：

```bash
python scripts/install.py --agent all --force
```

指定任意 `skills` 父目录：

```bash
python scripts/install.py --target /path/to/skills
```

Gemini CLI 也支持直接从 Git 安装：

```bash
gemini skills install https://github.com/EasternWhale/Write-Wechat-Artical-Skills
```

安装后重启目标 Agent 或新建会话，使技能列表重新加载。安装第三方 Skill 前应先审阅 `SKILL.md` 与脚本。

## 在 Agent 中使用

完整文章并生成排版：

```text
使用 write-wechat-articles，给普通职场人写一篇“AI 为什么没有减少加班”的公众号文章，约 2200 字。观点鲜明，联网核查，最后生成可一键复制到公众号的 HTML 预览页。
```

只做选题：

```text
使用 write-wechat-articles。账号定位是“替年轻家庭拆解重要消费决策”，生成 12 个选题并推荐 3 个，先不要写正文。
```

改写旧稿：

```text
使用 write-wechat-articles 改写这篇草稿。保留事实和原意，重做标题与开头，删掉 AI 腔，输出 Markdown 和 red-white 主题 HTML。
```

部分客户端支持 `$write-wechat-articles` 或 `/write-wechat-articles` 显式调用；不支持时，直接在提示词中写技能名即可。

## 独立生成公众号 HTML

Agent 写完 `article.md` 后，可以手动运行：

```bash
python skills/write-wechat-articles/scripts/render_wechat.py article.md --theme auto --preview
```

输出：

- `article_wechat.html`：经过校验的纯正文片段；
- `article_preview.html`：浏览器预览和复制页面。

打开预览页，点击“复制到公众号”，再到微信公众号编辑器粘贴。复制按钮和 JavaScript 位于正文外壳，不会进入被复制的文章。

内置主题：

- `moyu-green`：教程、知识、清单和生活方式；
- `red-white`：观点评论、热点与社会议题；
- `graphite-minimal`：科技、商业、财经、职场和数据内容。

单独校验自己修改过的正文 HTML：

```bash
python skills/write-wechat-articles/scripts/validate_gzh_html.py article_wechat.html
```

## 项目结构

```text
Write-Wechat-Artical-Skills/
├── .github/workflows/validate.yml
├── scripts/
│   ├── install.py
│   └── validate.py
├── tests/
│   ├── sample.md
│   └── smoke_test.py
└── skills/write-wechat-articles/
    ├── SKILL.md
    ├── agents/openai.yaml
    ├── assets/
    │   ├── themes.json
    │   └── preview-template.html
    ├── references/
    └── scripts/
        ├── render_wechat.py
        ├── validate_gzh_html.py
        └── wrap_preview.py
```

`SKILL.md` 保持短而可触发，详细写作、风险、主题和 HTML 规则按需加载。排版结构参考 `gzh-design` 的“主题注册—组件渲染—平台校验—预览复制”分层；文字自然化规则参考 `humanizer-zh` 的反 AI 痕迹检查，并针对公众号重新收敛。

## 本地验证

```bash
python scripts/validate.py
python tests/smoke_test.py
```

验证覆盖 Skill 元数据、引用文件、UTF-8、主题注册表、Python 语法、三套主题渲染、微信正文红线、预览复制页和安装器。GitHub Actions 在推送与拉取请求时运行同一流程。

## 安全边界

- 不虚构亲历、采访、内幕、数据或引语；
- 医疗、法律、金融与新闻内容采用更严格证据标准；
- 不洗稿，不大段复制受版权保护的作品；
- 不把观点冲突变成群体羞辱或无证据名誉指控；
- 不在仓库或文章中写入密钥、账号、私人地址或病历等敏感信息。

## License

[MIT License](LICENSE)
