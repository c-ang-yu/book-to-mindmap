# book-to-mindmap 详细流水线

本文档是 SKILL.md 的展开版：并行摘录的组织方式、subagent 提示词模板、完整坑清单与实战案例。

> **环境适配说明**：本文档在 Windows + 自建 Android WebView 壳工程环境实战沉淀。APK 层小节中的 gradle 配置、模拟器 selftest 协议为作者环境专属，其他机器按需改造；其余内容（数据层、浏览器验证层、摘录纪律）为通用方法论。

## 一、阶段 3 全书原文扩写的组织方式

### 1. 任务切分

- 用 extract_T.py 得到 `T_paths.json`（扁平清单，每条含 path/t/n/d/dlen/terminal）。
- 按 era（第一段 path 数字）分组，每个 subagent 领一个时期（约 30-60 个末端节点）。时期过大再按 school 二次切分。
- 每个任务清单只需给 agent：path、n（节点名）、chain（从 era 到该节点的祖先名链，帮 agent 判断书里哪一章）、当前 d（旧短句，提示该节点应讲什么）。

### 2. subagent 提示词模板

```
你是书籍摘录员。为思维导图的下列节点补写 d 字段，内容 = 指定书中的逐字原文。
书源 txt：<绝对路径>（若是"每行一页"的扫描转换版，行号≈页码，用 Grep 找关键词定位章节，Read offset/limit 分块读）

待补节点（JSON 数组，含 path/n/chain/old_d）：...

要求：
1. 只逐字抄录原文，不改写、不缩写、不总结；150-500 字，宁多勿少
2. lineage（渊源影响）节点：渊源段 + "\n\n" + 影响段 两块原文
3. 每段末尾另起一行加：——摘自《书名》
4. 概念在书中确无正面论述时：选语义最相关的相邻段落，并在最终汇报（不是 JSON 里）说明"该节点书中无正面论述，用了 X 段"，绝不编造
5. 输出纯 JSON 对象：{"<path>": "<d 全文>", ...}，d 内换行写字面 \n\n；禁止 markdown 代码围栏，禁止解释性文字
6. 完成后把 JSON 写入指定输出文件，并在汇报里列出：成功 N 个 / 未覆盖节点及原因
```

### 3. 合并与验收

- 汇总各 agent 的 exp_*.json 为一个 updates.json（`{"path": "d", ...}`），跑 merge_d.py。
- merge_d.py 自动复检：JSON 可解析 + 节点总数不变；总数变了立即停。
- probe_node.py 终检：detail/idea/note/lineage 类末端节点 d 覆盖率必须 100%（era/school/person 允许无 d）。
- 对用户点名过的重点概念（如柏拉图分有/第三者、唯名论三大立场）抽样打印 d 开头核对是否真为原文长段。

## 二、完整坑清单（每条都真实踩过）

### 数据层

- `const T=[...]` 数据行是**一整行几百 KB**：Edit 工具对超长单行易出错且难审查，一律走脚本。
- 数据行是双引号 JSON 风格 → 整段可直接 `json.loads` 校验；回写用 `json.dumps(ensure_ascii=False, separators=(',',':'))`。
- 段内换行必须写字面 `\n` 转义（docBody 是 white-space:pre-wrap，渲染为换行）；lineage 两段之间用 `\n\n`。
- 书名号、中文引号「」“”无需转义；只有双引号字符本身和反斜杠需要。
- **BOM 坑**：PowerShell `Set-Content -Encoding UTF8` 会写 BOM，`encoding="utf-8"` 读 JSON 直接炸（Unexpected UTF-8 BOM）。所有读取用 `utf-8-sig`（skill 脚本已内置）；或用 python 自己写 updates.json。
- 末端覆盖判定：`not ch` 即末端。era/school/person 无 d 正常；detail/idea/note/lineage 无 d = 漏做。

### 浏览器验证层

- 自动化测试壳（Vite 代理类环境）会**覆写 document.title**：页面 ?test/?test2 自测通道把结果写进 title，桌面里读不到（页面无错但 title 恒为默认值）。别浪费时间排查页面，改用 browser_evaluate 直接探针。
- 合成 `el.click()` 不触发点击逻辑——tap 由 viewport 的 pointerup 统一处理（12px 拖动容差）。探针必须 `dispatchEvent(new PointerEvent('pointerdown'/..., {bubbles:true,pointerId:9,clientX,clientY,isPrimary:true}))`。
- 深层节点被折叠隐藏时 getBoundingClientRect 全 0：先程序化展开祖先（移除 .kids 的 closed 类）再探。
- docPop 探针断言：`#docPop` display=flex；`#docBody` textContent 长度 ≈ d 长度；`#docClose`.click() 后 display=none。

### APK 层

- 改 HTML 后必须 Copy 到 `mindmap/src/main/assets/www/mindmap.html` 再编译，两份内容不同=白改。
- 编译必须 `$env:GRADLE_USER_HOME='C:\gradle-home-bypass'`：全局 `C:\gradle-home` 被 init.gradle（阿里云镜像）污染，与本项目 settings 的 PREFER_SETTINGS 冲突，报 "repository 'maven' was added by initialization script"。bypass 目录用 junction 复用 caches/wrapper，勿删。
- `python`/`py` 都不在 PATH：用 `%LOCALAPPDATA%\Programs\Python\Python312\python.exe`。
- PowerShell 5.1 不支持 `&&`，链式命令用 `;`。
- 模拟器 WebView 冷启动 70s+，白屏≠加载失败；uiautomator dump 看不到 WebView 内部（NAF），验证靠 evaluateJavascript + logcat(tag MapSelfTest) 或截图。
- selftest 协议：`am start ... --ez selftest true --es selftest_mode run|draw|check`；run=读 ?test2 的 title；check/draw 用于批注持久化验证（勿加载 ?test2，会 clearInk）。
- **每个新版本 APK 换新文件名**（用户 2026-10-11 要求，防止与平板上的旧包混淆）。

## 三、实战案例

- **波菲利问题与三大立场**（869 字）：用户点名"三大立场是什么"。正确做法=抄录书中该节完整原文（波菲利三问 + 极端/温和唯名论与实在论 + 概念论），不是写一句概括。
- **0.4.0.2 社会契约论萌芽**：书中无伊壁鸠鲁社会契约的正面论述。处理=用最相关的相邻原文（其个人主义倾向段 + 卢克莱修《物性论》补社会观段）填充，并在交付说明中如实告知"书里没有正面论述，未杜撰"。用户接受了这种诚实处理。
- **版本混淆事故**：数据与代码全部就位后用户仍"点不开"，根因是用户打开的是上午旧版（无弹层功能）。教训：①交付物加可见版本标记（页头副标题带「原文完整版」）；②APK 换新文件名；③排查先跑数据探针（md5+节点覆盖率）再怀疑代码。
