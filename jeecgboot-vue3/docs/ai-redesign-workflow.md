# AI-Assisted Redesign Workflow

> 本工程是 vibeCRUD 脚手架的 fork。本文档指导"如何在 fork 后根据新项目的设计稿快速完成 UI 改造"。
> 面向读者：Claude Code / Cursor 等 AI 编码代理，以及审阅改造结果的人类开发者。

## 0. 上下文

- 本工程是 fork-and-forget 模板，每个项目独立演化，不回流 template
- 70% 业务为 CRUD，复用 JeecgBoot 原生 `src/views/system/**` 及组件库，**不改**这些页面，让它们吃全局主题
- 视觉改造聚焦**整体风格 + 关键页**：design token、DefaultLayout、Login、Dashboard

## 1. 可改区 vs 禁区

### 可改区（fork 后按设计稿自由改）

- `src/theme/tokens.ts` — 全局 design token
- `src/layouts/default/**` — 应用外壳（header / sider / tabs / footer）
- `src/views/login/**` — 登录页
- `src/views/dashboard/**` — 主页 / 概览仪表盘
- `src/views/<本项目业务模块>/**` — 新增的业务页
- `src/assets/**` — logo / 图片 / 全局背景

### 禁区（未经用户显式确认不要改）

- `src/views/system/**` — JeecgBoot 系统管理页（user/role/menu/dict/tenant/dept/...）
- `src/components/**` — 基础组件库（JVxeTable、Form、Table 等）
- `src/store/**` / `src/router/**` / `src/utils/**` / `src/api/**` — 状态/路由/工具/接口
- `src/hooks/**` / `src/logics/**` / `src/settings/**` — 应用逻辑层
- `build/**` / `vite.config.ts` — 构建配置

禁区 ≠ 绝对不动；是"未经用户显式确认不要改"。注意本文档针对 **UI 改造任务**；fork 初始化（改项目身份、`package.json` name、`.env` 标题等）不在本文档范围，按 README.md 执行。

## 2. 改造步骤

### Step 1：读取设计稿，产出 token 清单

从设计稿提取这些字段（对齐 `src/theme/tokens.ts`）：

- 主色 `colorPrimary`
- 成功/警告/错误色 `colorSuccess` / `colorWarning` / `colorError`
- 辅色 `colorInfo`（通常 = 主色）
- 文字主色 `colorTextBase`
- 基础字号 `fontSize`
- 圆角 `borderRadius`
- 字体栈 `fontFamily`

如设计稿给了间距基准（8px/12px/16px 等），映射到 `sizeStep` / `sizeUnit`。

### Step 2：改 `src/theme/tokens.ts`

把 Step 1 清单写进 `tokens` 对象。**只改这一个文件**，跑 `pnpm dev`。验证点：系统管理列表、表单、按钮、弹窗视觉都应该自动跟随主题变化。

> 这是 ROI 最高的一步——让 70% 的 CRUD 页自动吃上新风格。务必先做完这步、跑通 dev 再进行下一步。

### Step 3：改 `src/layouts/default/**`

对照设计稿的应用外壳（顶栏高度、侧边栏宽度、logo 位置、菜单样式、tabs 样式）调整。优先改 CSS、避免改结构。如结构差异大（比如设计稿没有 tabs），可直接删组件。

### Step 4：改 `src/views/login/**`

登录页通常视觉要求最高。建议整页直接重写（保留 form 的 onSubmit 逻辑与 store 交互，替换模板 + style）。

### Step 5：改 `src/views/dashboard/**`

主页 / 概览。通常含统计卡片 + 图表，按设计稿直接生成 Vue SFC。echarts 已装好可直接用。

### Step 6：抽样验证系统页

随机打开 3-5 个 `src/views/system/**` 页面，确认全局主题生效、无视觉失控。如某页样式明显出格，记入项目遗留，**不在此轮修**。

## 3. AI Prompt 模板

把下面这段作为对 AI 代理的起始 prompt，附设计稿截图/Figma 链接：

```text
这是一个 vibeCRUD 前端模板的 fork 项目。工程规约见 README.md 和 docs/ai-redesign-workflow.md。
当前任务：根据提供的设计稿完成 UI 改造。

请严格按以下流程：
1. 读 docs/ai-redesign-workflow.md 第 1 节，掌握"可改区 vs 禁区"
2. 从设计稿提取 token 清单（第 2 节 Step 1），列给我确认
3. 我确认后，改 src/theme/tokens.ts（Step 2），跑 pnpm dev 验证系统页主题已变
4. 依次改 DefaultLayout / Login / Dashboard（Step 3-5），每一个完成跑一次 dev 截图给我
5. Step 6 抽样验证，记录遗留问题到 TODO.md

约束：
- 禁区文件禁止主动改。如发现禁区文件需要改，先停下告诉我原因、等我确认
- 每完成一步做一个 commit（约定式消息，feat: apply design tokens / feat: redesign login 等）
- 发现 ESLint / vue-tsc 报错立即停下修掉，不带错进下一步

开始前先回答：你读懂上述约束了吗？设计稿在哪里？
```

## 4. 产出 checklist（人类审阅用）

- [ ] `tokens.ts` 已更新
- [ ] `pnpm dev` 无控制台报错
- [ ] 登录页视觉匹配设计稿
- [ ] 主页 / dashboard 视觉匹配设计稿
- [ ] DefaultLayout（顶栏 / 侧栏 / tabs）视觉匹配设计稿
- [ ] 抽查 5 个系统管理页无视觉崩溃
- [ ] 无 ESLint 新错误、`vue-tsc --noEmit` 通过
- [ ] CLAUDE.md / README.md 无需在此轮更新（它们是模板层文档，不在单项目 fork 迭代中改）

## 5. 常见坑

- **JVxeTable 用内置皮肤**，token 覆盖不到完整。如必要改 `src/components/JVxeTable/**`（进入禁区，要告知用户）
- **vxe-table** 通过 `vxe-table-plugin-antd` 适配，主色会跟；但圆角 / 间距不完全跟，视情况单独处理
- **如项目不需要深色模式**：本模板保留了 JeecgBoot 原生 dark 开关（设置抽屉里）。不用的话可直接删 `src/layouts/default/setting/**` 里深色开关组件（但不要只改 tokens，开关还在会误导用户）
- **Less 变量侧**：`build/generate/generateModifyVars.ts` 与 `tokens.ts` **两套独立**，Less 不会跟随 tokens 自动变。如发现某处样式因 Less 变量未更新而不对，再手动改 Less 或统一到 CSS token 方案
- **图标**：换 logo 走 `src/assets/images/logo.png` + `public/favicon.ico`。菜单图标是 Iconify CDN 加 SVG sprites 两套方案，见 CLAUDE.md "Icon System" 节
