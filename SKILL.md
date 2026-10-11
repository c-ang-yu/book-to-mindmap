---
name: book-to-mindmap
description: 把一本书的 txt 全文改造成极致详细的单文件思维导图——树状图加列表双形态、末端节点替换为书中逐字原文长段、点击弹原文浮层、可打包 APK。当用户要求把书做成思维导图、把教材整理成知识导图、或抱怨导图节点不够详细时使用。不用于与书籍无关的通用网页开发。
---

# 书 → 思维导图改造

把一本书变成「不是传统导图」的极致详细知识导图：末端节点就是书本身。

## 铁律（用户明确要求，违反即返工）

1. **极致详细**：末端节点（detail/lineage/note/idea）的 d 必须是对应书中**逐字原文长文段**（150-500 字，上不封顶），禁止按传统思维导图习惯压缩成短语。
2. **渊源与影响单独成节点**：lineage 节点的 d = 渊源段 + 空行 + 影响段两块原文。
3. **原文纪律**：只逐字抄录，不改写不缩写。书中确无正面论述的概念，选最相关相邻段落填充，并在交付说明中如实告知，绝不杜撰。
4. 每段 d 末尾加署名行：`——摘自《书名》`。
5. 核心名词用金色标记：`<b class=term>名词<span class=tip>一句话释义</span></b>`（无引号属性，释义随浮窗展示）。
6. 版权期内书籍只处理用户自己提供的文本；公版书可自行从合法渠道取文。

## 流水线

Python 可能不在 PATH：Windows 用 `%LOCALAPPDATA%\Programs\Python\Python3xx\python.exe`（下称 `$PY`），macOS/Linux 用 `python3`。

### 1. 通读定位

书源为 txt（扫描版转出的「每行一页」txt 也适用）。用 Read 分块通读（limit 25-30），边读边记骨架与关键原文的行号位置。

### 2. 骨架与数据 schema

复制本仓库 `assets/template.html` 作为底版（已内置全部 CSS/JS/原文弹层/双形态/批注壳与 10 个演示节点，浏览器打开即可预览成品形态），只替换其中 `const T` 数据行。节点 schema（**单行、双引号 JSON 风格、段内换行=字面 `\n\n` 转义**）：

| t | 含义 | 层级 |
|---|------|------|
| era | 时期（可带 ec 时代色） | 1 |
| school | 学派/思潮 | 2 |
| person | 人物 | 3 |
| idea | 学说/概念 | 4+ |
| detail / lineage / note | 末端原文节点 | 最深 |

末端节点 d=原文长段；非末端节点 d 只作悬停提示，留短句即可。

### 3. 全书原文扩写（核心，用脚本，禁止手改数据行）

数据行是一整行几百 KB，**禁止用 Edit 工具手改，必须走 skill 自带脚本**：

```
$PY scripts/extract_T.py <html> <outdir>    # 提取 T.json（全树）+ T_paths.json（扁平含 path）
# 把 T_paths.json 按时期切成任务清单，并行派 subagent 分书摘录（提示词模板见 references/pipeline.md）
$PY scripts/merge_d.py <html> updates.json  # 把 {"path": "新d全文", ...} 合并回写并自动校验
$PY scripts/probe_node.py <html> [关键词]    # 体检：节点数 / 末端 d 覆盖率 / 按名查节点
```

每轮合并后必须跑 probe：末端节点中 detail/idea/note/lineage 类型的 d 覆盖率必须 100%。

### 4. 验证（三个坑）

- **桌面浏览器**：自动化测试壳会覆写 document.title，页面内置 ?test 自测通道在桌面读不到 → 改用 browser_evaluate 功能探针（合成 `PointerEvent` 的 pointerdown/up 事件；普通 `el.click()` 不触发 pointerup 点击逻辑，会误判失败）。检查项：节点折叠（closed 类+cnt 数字）、term 释义浮窗（tshow 类）、形态切换（列表 eras=时期数）、docPop 原文弹层（display=flex 且 body 字数=d 长度、可关闭）。
- **数据**：merge 脚本已自动 json.loads 复检节点总数，总数变化即数据被破坏。
- **APK**（可选）：把成品 HTML 放进 Android WebView 壳工程的 assets 加载即可；验证用 `evaluateJavascript` 或 Chrome 远程调试（WebView 冷启动可达 70s+，白屏≠失败）。

### 5. 交付

- 桌面 HTML 副本（与工作副本字节一致，md5 校验）。
- APK（可选）：任意 Android WebView 壳工程加载 HTML 即可。**每个新版本 APK 必须换新文件名（带版本特征），禁止覆盖旧名**——用户要求，防止装错旧包。

完整方法论（并行摘录提示词模板、完整坑清单、实战案例）见 `references/pipeline.md`。
