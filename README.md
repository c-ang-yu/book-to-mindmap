# book-to-mindmap · 书籍思维导图 Skill

把一本书的 txt 全文改造成**极致详细**的单文件思维导图：不是传统导图的短语概括，而是把书中**逐字原文长段**直接装进末端节点——「它不只是一个思维导图，你不能按照传统思维导图那种简洁的要求来制作它」。

一个 Trae / Trae CN 的 Agent Skill（同样适用于其他支持 SKILL.md 约定的 Agent 环境）。

## 特性

- **树状图 + 列表双形态**一键切换，内容不变
- **末端节点 = 书中逐字原文**（150-500 字起，上不封顶），金色「原文」徽标，点击弹出原文浮层（可滚动、可复制、内嵌名词释义）
- **渊源与影响**单独成节点（渊源段 + 影响段两块原文）
- 金色名词点击看释义（手机端友好，替代悬停）
- 平板 + 电容笔**手写批注**（多色、撤销、自动本地保存），手指只用于平移缩放画布
- 纯离线单文件 HTML，手机浏览器直接打开；可选打包 Android APK
- 附带 3 个 Python 脚本：数据提取 / 合并回写（自动校验节点总数）/ 完整性体检

## 安装

下载本仓库（Code → Download ZIP，或 `git clone`），把整个文件夹放入：

- 项目级：`<你的项目>\.trae\skills\book-to-mindmap\`
- 全局：`~\.trae-cn\skills\book-to-mindmap\`（国际版为 `~\.trae\skills\`）

## 使用

在对话里直接说：

- 「把 XX 书做成思维导图」
- 「把这本教材整理成知识导图」
- 「这个导图节点不够详细，补成书中原文」

书源自备 txt。公版书可从合法渠道获取；版权期内的书请使用你自己拥有的电子文本。

## 快速上手

1. 浏览器打开 `assets/template.html` 预览成品形态（10 个演示节点）
2. 按 `SKILL.md` 的流水线走：通读书 txt → 设计骨架 → 并行摘录原文 → 脚本合并 → 三层验证
3. 详细方法论见 `references/pipeline.md`（含 subagent 提示词模板与踩坑清单）

## 环境适配

- Python：Windows 若不在 PATH，用 `%LOCALAPPDATA%\Programs\Python\Python3xx\python.exe`；macOS/Linux 用 `python3`
- APK 打包为可选项，需要自备任意 Android WebView 壳工程；不打包的话 HTML 本身即可交付
- 作者环境专属条目已在 `references/pipeline.md` 顶部标注

## 许可

MIT（见 LICENSE）。模板与脚本为原创；**摘录内容版权归原书作者**——使用本工具产生的内容仅供个人学习，请勿分发受版权保护的书籍原文。
