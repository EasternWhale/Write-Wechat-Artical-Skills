# write-wechat-articles

面向 Codex 的全领域微信公众号写作 Skill。它把选题、研究、争议设计、事实核查、中文自然化和公众号 Markdown 交付串成一套可复用流程。

适用于文学、影视、音乐、科技、商业、财经、职场、教育、健康、法律、历史、消费、旅行等领域。文章可以有立场，但不能靠虚构事实、群体攻击或标题诈骗制造争议。

## 能做什么

- 生成并评分公众号选题；
- 输出标题、大纲、完整文章或系列策划；
- 自动选择观点、科普、教程、测评、复盘、数据、人物、清单等结构；
- 对医疗、法律、金融、新闻等领域提高证据标准；
- 处理模糊归因、宣传腔、机械连接词、三段式和其他常见 AI 写作痕迹；
- 生成适合手机阅读、方便继续排版的 Markdown；
- 与可选的 `gzh-design` Skill 衔接，继续制作公众号 HTML。

## 安装

需要 Python 3.9 或更高版本。

```bash
git clone https://github.com/<your-account>/write-wechat-articles.git
cd write-wechat-articles
python scripts/install.py
```

安装器会把 Skill 复制到：

- 设置了 `CODEX_HOME`：`$CODEX_HOME/skills/write-wechat-articles`
- 未设置 `CODEX_HOME`：`~/.codex/skills/write-wechat-articles`

如果目标目录已经存在，安装器会停止，不会覆盖。确认需要更新后使用：

```bash
python scripts/install.py --force
```

安装后重新打开 Codex，或新建一个任务，使技能列表重新加载。

也可以手动把 [`skills/write-wechat-articles`](skills/write-wechat-articles) 整个目录复制到个人 Codex Skills 目录。

## 使用

在 Codex 中显式调用：

```text
使用 $write-wechat-articles，给普通职场人写一篇关于“AI 为什么没有减少加班”的公众号文章，2000 字，观点鲜明，允许联网核查。
```

只做选题：

```text
使用 $write-wechat-articles。账号定位是“替年轻家庭拆解重要消费决策”，请生成 12 个选题并推荐 3 个，先不要写正文。
```

改写旧稿：

```text
使用 $write-wechat-articles 改写这篇公众号草稿。保留事实和原意，重做标题与开头，删掉 AI 腔，只交付标题、摘要和正文。
```

需要公众号 HTML 时：

```text
先使用 $write-wechat-articles 完成文章，再使用 gzh-design 自动排版成可粘贴到微信公众号编辑器的 HTML。
```

`gzh-design` 是可选协作 Skill，不包含在本仓库中。没有它时，本 Skill 仍可正常交付 Markdown。

## 工作方式

Skill 采用渐进加载：

- `SKILL.md`：核心工作流和交付规则；
- `article-blueprints.md`：文章类型与结构路由；
- `evidence-and-risk.md`：领域证据标准、风险和透明规则；
- `natural-chinese.md`：中文去 AI 腔与自然化编辑；
- `wechat-markdown-handoff.md`：公众号 Markdown 和排版交接。

详细规则只在任务需要时加载，避免每次调用都占用过多上下文。

## 项目结构

```text
write-wechat-articles/
├── .github/workflows/validate.yml
├── scripts/
│   ├── install.py
│   └── validate.py
├── skills/write-wechat-articles/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/
├── .gitignore
├── LICENSE
└── README.md
```

## 本地校验

```bash
python scripts/validate.py
```

校验内容包括：Skill 命名、frontmatter、UI 元数据、引用文件、相对链接、遗留占位符和 UTF-8 编码。GitHub Actions 会在推送和拉取请求时执行同一检查。

可以在临时目录试装，不影响已安装的 Skill：

```bash
python scripts/install.py --target ./tmp-codex-home
```

## 参与修改

修改后至少完成：

1. 运行 `python scripts/validate.py`；
2. 用一个普通观点题和一个高风险专业题试跑；
3. 确认“只要正文”等输出裁剪指令仍然有效；
4. 确认没有把本机绝对路径、账号信息或私有材料提交到仓库。

## 许可证

[MIT License](LICENSE)
