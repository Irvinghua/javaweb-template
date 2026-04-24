# vibeCRUD Frontend Template Fork Conventions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 引入一个最小化的 `tokens.ts` design token 单一真源、重构 `App.vue` 消费之，并产出 fork-and-forget 的工程级规约（README.md + docs/ai-redesign-workflow.md + CLAUDE.md），让每次 fork 后基于新项目设计稿的 UI 换皮流程对 AI 和人都有清晰边界。

**Architecture:** 不移动任何文件。新建一个 TypeScript 模块 `jeecgboot-vue3/src/theme/tokens.ts`，把 `src/App.vue:75-89` 内联 token 字面量抽出。三份文档建立 fork-and-forget 规约与 AI 改造流程。不改后端；不改 DefaultLayout；不改 Less 变量系统。

**Tech Stack:** Vue 3 / Vite 6 / TypeScript / Ant Design Vue 4 / pnpm 11 / Node 18+。

**Reference spec:** `docs/superpowers/specs/2026-04-24-frontend-template-fork-conventions-design.md`

---

## File Structure Plan

```
jeecgboot-vue3/
├── src/
│   ├── theme/
│   │   └── tokens.ts              # [NEW] design token 单一真源
│   └── App.vue                    # [MODIFY line 75-89] 消费 tokens.ts
├── docs/
│   └── ai-redesign-workflow.md    # [NEW] AI 改造 workflow 文档
├── README.md                       # [REWRITE] vibeCRUD 模板 readme
└── CLAUDE.md                       # [MODIFY 3 处] 定位句 / Theme 节 / Fork Conventions 节
```

---

## Task 1: 建 `src/theme/tokens.ts`

**Files:**
- Create: `jeecgboot-vue3/src/theme/tokens.ts`

- [ ] **Step 1: 创建目录与文件**

```bash
cd /Users/irvinghua/workspace/javaweb-template/jeecgboot-vue3
mkdir -p src/theme
```

- [ ] **Step 2: 写入 tokens 内容**

创建 `jeecgboot-vue3/src/theme/tokens.ts`，内容如下：

```typescript
/**
 * AntD ConfigProvider theme token 单一真源。
 *
 * 每次 fork 后按新项目设计稿修改本文件即可让 70% 的 CRUD 页面自动吃上新主题。
 * 详见 docs/ai-redesign-workflow.md 与 README.md。
 */
export const tokens = {
  colorPrimary: '#1890ff',
  colorSuccess: '#55D187',
  colorWarning: '#EFBD47',
  colorError: '#ED6F6F',
  colorInfo: '#1890ff',
  colorTextBase: '#333',
  borderRadius: 4,
  fontSize: 14,
  sizeStep: 4,
  sizeUnit: 4,
  wireframe: true,
  fontFamily:
    '-apple-system,BlinkMacSystemFont,Segoe UI,PingFang SC,Hiragino Sans GB,Microsoft YaHei,Helvetica Neue,Helvetica,Arial,sans-serif,Apple Color Emoji,Segoe UI Emoji,Segoe UI Symbol',
};
```

值与 `src/App.vue:75-89` 现有内联字面量**完全一致**。本文件只负责 token 字典，不参与 dark 模式分支与 CSS 变量写入。

- [ ] **Step 3: 类型检查**

运行：
```bash
cd /Users/irvinghua/workspace/javaweb-template/jeecgboot-vue3
npx vue-tsc --noEmit
```
预期：通过（无新增错误）。若工程原本就有 vue-tsc 错误（JeecgBoot 现状可能存在），记录下来但允许通过，只要**不增加**新错误即可。

- [ ] **Step 4: Commit**

```bash
cd /Users/irvinghua/workspace/javaweb-template
git add jeecgboot-vue3/src/theme/tokens.ts
git commit -m "feat(theme): 抽离 AntD ConfigProvider token 为单一真源"
```

---

## Task 2: 重构 `src/App.vue` 消费 `tokens.ts`

**Files:**
- Modify: `jeecgboot-vue3/src/App.vue` (line 9-20 import 区，line 68-96 watch appStore 分支)

- [ ] **Step 1: 读取现有 App.vue 完整内容定位改动行**

```bash
cd /Users/irvinghua/workspace/javaweb-template/jeecgboot-vue3
```
用 Read 工具读 `src/App.vue` 全文。确认：
- `<script lang="ts" setup>` 起始处无 `from '/@/theme/tokens'` import
- `watch(appStore.getProjectConfig, ...)` 回调里的 `token: {...}` 字面量占据 line 75-89

- [ ] **Step 2: 在 script 区新增 import**

在 `src/App.vue` 的 `<script lang="ts" setup>` import 区（约 line 9-20 之间）追加一行：

```typescript
import { tokens } from '/@/theme/tokens';
```

位置建议紧随 `import { changeTheme } from '/@/logics/theme/index';` 之后（保持相邻 import 分组）。

- [ ] **Step 3: 替换内联 token 字面量**

找到 `src/App.vue` 中的 `watch(appStore.getProjectConfig, ...)` 回调，该回调当前内容（约 line 68-96）：

```typescript
watch(
  appStore.getProjectConfig,
  (newValue) => {
    const primary = newValue.themeColor;
    const result = {
      ...appTheme.value,
      ...{
        token: {
          colorPrimary: primary,
          wireframe: true,
          fontSize: 14,
          colorTextBase: '#333',
          colorSuccess: '#55D187',
          colorInfo: primary,
          borderRadius: 4,
          sizeStep: 4,
          sizeUnit: 4,
          colorWarning: '#EFBD47',
          colorError: '#ED6F6F',
          fontFamily:
            '-apple-system,BlinkMacSystemFont,Segoe UI,PingFang SC,Hiragino Sans GB,Microsoft YaHei,Helvetica Neue,Helvetica,Arial,sans-serif,Apple Color Emoji,Segoe UI Emoji,Segoe UI Symbol',
        },
      },
    };
    appTheme.value = result;
    modeAction(result);
  },
  { immediate: true }
);
```

替换为：

```typescript
watch(
  appStore.getProjectConfig,
  (newValue) => {
    const primary = newValue.themeColor;
    const result = {
      ...appTheme.value,
      token: {
        ...tokens,
        colorPrimary: primary,
        colorInfo: primary,
      },
    };
    appTheme.value = result;
    modeAction(result);
  },
  { immediate: true }
);
```

要点：
- 保留 `primary` 变量与 `modeAction(result)` 调用
- 保留 `{ immediate: true }`
- 去除 `...{ token: {...} }` 这层多余的 spread 包裹，直接写 `token: {...}`
- 运行时用 `primary` 覆盖 `colorPrimary` 和 `colorInfo`（保持原行为）

- [ ] **Step 4: 运行 dev 服务器 + 视觉验证**

```bash
cd /Users/irvinghua/workspace/javaweb-template/jeecgboot-vue3
pnpm dev
```

在浏览器打开 `http://localhost:3100`，人工验证：
1. 登录页视觉与改造前一致（按钮颜色、圆角、字号、字体）
2. 登录后（如果有测试账号），打开任意系统管理页（`/system/user` 等），按钮/表格视觉无变化
3. 设置抽屉（右侧齿轮图标）切换主题色：点击主色预置，整站主色应跟随切换
4. 浏览器 DevTools Console 无新增 error / warning
5. 切 dark 模式（设置抽屉里的深色开关）：主题切到深色后，文字色变白、主色仍生效

若以上任一失败，停下定位差异再继续。

- [ ] **Step 5: 类型检查 + Lint**

```bash
cd /Users/irvinghua/workspace/javaweb-template/jeecgboot-vue3
npx vue-tsc --noEmit
npx eslint src/App.vue
```
预期：无新增错误。

- [ ] **Step 6: Commit**

```bash
cd /Users/irvinghua/workspace/javaweb-template
git add jeecgboot-vue3/src/App.vue
git commit -m "refactor(App): 消费 tokens.ts 替换内联 ConfigProvider token"
```

---

## Task 3: 新建 `docs/ai-redesign-workflow.md`

**Files:**
- Create: `jeecgboot-vue3/docs/ai-redesign-workflow.md`

- [ ] **Step 1: 创建目录**

```bash
cd /Users/irvinghua/workspace/javaweb-template/jeecgboot-vue3
mkdir -p docs
```

- [ ] **Step 2: 写入文档完整内容**

创建 `jeecgboot-vue3/docs/ai-redesign-workflow.md`，内容如下（一字不差复制进文件）：

````markdown
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
````

- [ ] **Step 3: Commit**

```bash
cd /Users/irvinghua/workspace/javaweb-template
git add jeecgboot-vue3/docs/ai-redesign-workflow.md
git commit -m "docs(frontend): 新增 AI 改造 workflow 文档"
```

---

## Task 4: 重写 `jeecgboot-vue3/README.md`

**Files:**
- Modify: `jeecgboot-vue3/README.md`（大改：从 JeecgBoot 官方 readme 换成 vibeCRUD 模板 readme）

- [ ] **Step 1: 读取现有 README 确认待移除内容**

```bash
cd /Users/irvinghua/workspace/javaweb-template/jeecgboot-vue3
```

用 Read 工具查看 `README.md`。预期是 JeecgBoot 官方中文 readme，含徽章、社区链接、Pro 版介绍、贡献流程、二维码等。**整体替换**。

- [ ] **Step 2: 整体替换 README 内容**

用 Write 工具把 `jeecgboot-vue3/README.md` 替换为以下内容：

````markdown
# vibeCRUD 前端模板（基于 JeecgBoot Vue3 裁剪）

本工程是 ToB 后台管理系统的前端脚手架模板，为**每个新项目 fork 一次独立开发**而设计（fork-and-forget）。
后端在同仓库的 `jeecg-boot/` 目录。

## 工程定位

- 70% 业务是 CRUD 后台管理，复用 JeecgBoot 的系统管理、权限、字典等内核
- 30% 业务为 dashboard / 报表 / 定制业务页，按每个项目的设计稿 AI 改造
- 每个项目 fork 后独立演化，**不回流 template**

## 技术栈

Vue 3 + Vite 6 + TypeScript + Ant Design Vue 4 + Pinia + Vue Router 4。
包管理 pnpm，Node ^18 || >=20。

## 启动

```bash
pnpm install
pnpm dev          # 端口 3100；代理 /jeecgboot → localhost:8080/jeecg-boot
```

详细环境变量见 `.env.development`。

## Fork 后的改造流程

fork 本模板后 + 拿到新项目设计稿，按以下步骤：

1. **改项目身份**
   - `package.json` 的 `name` / `version` / `author` / `repository`
   - `.env` 的 `VITE_GLOB_APP_TITLE` / `VITE_GLOB_APP_SHORT_NAME`
   - `public/favicon.ico`、`src/assets/images/logo.png`
2. **改主题 token**：修改 `src/theme/tokens.ts`（ROI 最高，让 70% 的 CRUD 页自动吃上新风格）
3. **改应用外壳**：按设计稿重写 `src/layouts/default/**`
4. **改登录 / 主页**：`src/views/login/**`、`src/views/dashboard/**`
5. **如项目不需要深色模式**：删除设置抽屉里的 dark 切换组件（位于 `src/layouts/default/setting/**`）
6. **开发业务页**：新模块建议放 `src/views/<moduleName>/**`

完整流程与给 AI 的 prompt 模板见 **[`docs/ai-redesign-workflow.md`](./docs/ai-redesign-workflow.md)**。

## 禁区（不主动改）

除非有明确理由，fork 后**不要**改以下目录：

- `src/views/system/**` — JeecgBoot 系统管理页
- `src/components/**` — 基础组件库
- `src/store/**` / `src/router/**` / `src/utils/**` / `src/api/**` / `src/hooks/**` / `src/logics/**` / `src/settings/**`
- `build/**` / `vite.config.ts`

改这些会把本模板的内核改坏，也让未来想借鉴其他 fork 的修复变困难。

## 目录结构（节选）

```
src/
├── theme/tokens.ts         # [可改区] design token 单一真源
├── layouts/default/        # [可改区] 应用外壳
├── views/
│   ├── login/              # [可改区] 登录页
│   ├── dashboard/          # [可改区] 主页 / 概览
│   ├── system/             # [禁区] JeecgBoot 系统管理页
│   └── <your-module>/      # [可改区] 业务页
├── components/             # [禁区] 基础组件库
├── store/                  # [禁区] 状态管理
├── router/                 # [禁区] 路由配置
├── api/                    # [禁区] HTTP 客户端与业务 API
└── assets/                 # [可改区] 静态资源
```

## 常用命令

```bash
pnpm dev              # 开发服务器
pnpm build            # 生产构建
pnpm clean:cache      # 清 vite 缓存
pnpm reinstall        # 重装依赖
pnpm batch:prettier   # 批量格式化 src
```

## Lint / 类型检查

- `npx eslint src/path/to/file.vue`
- `npx stylelint "src/**/*.{vue,less,css}"`
- `npx vue-tsc --noEmit`（未配全量 CI，手动跑）

## 更多

- 后端参见 `jeecg-boot/` 及其 `CLAUDE.md`
- 前端编码约定参见 `CLAUDE.md`（与本文互补：本文档面向人类与 AI 代理，CLAUDE.md 记录编码细节）

---

底层基于 [JeecgBoot](https://github.com/jeecgboot/JeecgBoot) 3.9.1 裁剪。
````

- [ ] **Step 3: Commit**

```bash
cd /Users/irvinghua/workspace/javaweb-template
git add jeecgboot-vue3/README.md
git commit -m "docs(frontend): README 重写为 vibeCRUD 模板 readme"
```

---

## Task 5: 更新 `jeecgboot-vue3/CLAUDE.md`

**Files:**
- Modify: `jeecgboot-vue3/CLAUDE.md`（3 处改动）

- [ ] **Step 1: 改动 1 — 顶部定位句**

在 `jeecgboot-vue3/CLAUDE.md` 第 7 行：
```
JeecgBoot Vue3 frontend — an enterprise low-code platform built with Vue 3 + Vite 6 + Ant Design Vue 4 + TypeScript. Uses pnpm as package manager. Node 18 or 20+ required (`engines: "^18 || >=20"`).
```

用 Edit 工具替换为：
```
vibeCRUD 前端模板（基于 JeecgBoot Vue3 3.9.1 裁剪）—— 为 fork-and-forget 的 ToB CRUD 项目设计。工程级规约见 `README.md`；本文件记录编码细节。技术栈：Vue 3 + Vite 6 + Ant Design Vue 4 + TypeScript。包管理 pnpm，Node ^18 || >=20。
```

- [ ] **Step 2: 改动 2 — 重写 "### Theme System" 节**

在 `jeecgboot-vue3/CLAUDE.md` 约 line 87-92 的内容：
```markdown
### Theme System

- Less variables generated by `build/generate/generateModifyVars.ts`
- Dark mode via Ant Design Vue `theme.darkAlgorithm`
- CSS variable `--j-global-primary-color` set dynamically from theme color
- CSS class prefix: `jeecg` (defined in `src/settings/designSetting.ts`)
```

用 Edit 工具替换为：
```markdown
### Theme System

- **AntD ConfigProvider tokens**：集中在 `src/theme/tokens.ts`，是每次 fork 后按设计稿换皮的主入口。App.vue 消费此文件注入 `<ConfigProvider :theme.token>`
- **Runtime 主色覆盖**：`src/App.vue` 监听 `appStore.getProjectConfig.themeColor`，运行时覆盖 tokens 里的 `colorPrimary` / `colorInfo`，保留用户主题切换器能力
- **Less 变量生成**：`build/generate/generateModifyVars.ts` 独立维护 Less 侧变量（不与 tokens.ts 联动；两套系统并行）
- **Dark 模式**：JeecgBoot 原生能力保留但不主动使用。fork 项目如确定不用，可删设置抽屉里的开关（位于 `src/layouts/default/setting/**`）
- **CSS 变量 `--j-global-primary-color`**：App.vue 动态写入 `document.documentElement`，供自定义样式引用
- **CSS class prefix**：`jeecg`（定义在 `src/settings/designSetting.ts`）
```

- [ ] **Step 3: 改动 3 — 新增 "## Template Fork Conventions" 节**

位置：`jeecgboot-vue3/CLAUDE.md` 当前 "## Common Commands"（line 9）之前插入新节。

用 Edit 工具找到：
```markdown
## Common Commands
```

替换为：
```markdown
## Template Fork Conventions

本工程是 fork-and-forget 模板。修改代码时请留意"可改区 / 禁区"边界：

**可改区**（按项目设计稿自由改）
- `src/theme/tokens.ts` / `src/layouts/default/**` / `src/views/login/**` / `src/views/dashboard/**` / `src/views/<业务模块>/**`

**禁区**（未经用户确认不要主动改）
- `src/views/system/**` / `src/components/**` / `src/store/**` / `src/router/**` / `src/utils/**` / `src/api/**` / `src/hooks/**` / `src/logics/**` / `src/settings/**` / `build/**` / `vite.config.ts`

完整说明见 `README.md` 与 `docs/ai-redesign-workflow.md`。

## Common Commands
```

- [ ] **Step 4: 验证 CLAUDE.md 结构**

```bash
cd /Users/irvinghua/workspace/javaweb-template/jeecgboot-vue3
head -30 CLAUDE.md
```

预期：
- line 1: `# CLAUDE.md`
- 顶部一段为"vibeCRUD 前端模板..."的中英混合定位句
- "## Template Fork Conventions" 节在 "## Common Commands" 之前

- [ ] **Step 5: Commit**

```bash
cd /Users/irvinghua/workspace/javaweb-template
git add jeecgboot-vue3/CLAUDE.md
git commit -m "docs(frontend): CLAUDE.md 更新定位句与 Theme System 节、新增 Fork Conventions"
```

---

## Task 6: 端到端最终验证

**Files:**（本任务不改文件，只验证）

- [ ] **Step 1: 重新安装依赖（保险起见）**

```bash
cd /Users/irvinghua/workspace/javaweb-template/jeecgboot-vue3
pnpm install
```
预期：`pnpm-lock.yaml` 无变化。

- [ ] **Step 2: 类型检查**

```bash
npx vue-tsc --noEmit
```
预期：无新增错误（对比 Task 1 Step 3 的 baseline）。

- [ ] **Step 3: Lint**

```bash
npx eslint src/theme/tokens.ts src/App.vue
```
预期：0 error。

- [ ] **Step 4: 生产构建冒烟**

```bash
pnpm build
```
预期：构建成功，产物在 `dist/`。如时间有限可跳过（dev 跑通基本够）。

- [ ] **Step 5: 手动视觉回归**

```bash
pnpm dev
```

访问 `http://localhost:3100`，核验清单：

- [ ] 登录页视觉与改造前一致
- [ ] 登录后 `/dashboard` 视觉与改造前一致
- [ ] 打开 `/system/user` / `/system/role` / `/system/menu` 至少 3 个系统页视觉无变化
- [ ] 设置抽屉切主色：主色跟随切换
- [ ] 设置抽屉切 dark 模式：文字变白、主色仍生效
- [ ] Console 无新 error / warning

- [ ] **Step 6: 最终 git 状态检查**

```bash
cd /Users/irvinghua/workspace/javaweb-template
git log --oneline -10
git status
```

预期：
- 最近 5 个 commit 应包含：`feat(theme)`、`refactor(App)`、`docs(frontend)` ×3
- `git status` 干净（无未追踪或未提交文件）

---

## 回退预案

如果 Task 2（App.vue 重构）出现无法快速修复的视觉回归：

```bash
cd /Users/irvinghua/workspace/javaweb-template
git revert <refactor-commit-sha>
```

tokens.ts 文件可以保留（独立文件、不被消费就是 dead code，删除或留下都无害）。文档类改动（Task 3/4/5）纯增量，出问题也不影响运行。

## 超出范围声明

本 plan 只处理 spec 中列明的 5 个文件。以下事项**不在本 plan 范围**：
- 撕掉 JeecgBoot 原生 dark 模式代码（`ThemeEnum.DARK`、`theme.darkAlgorithm` 分支、dark 开关组件）
- 重写 DefaultLayout
- 重写 login / dashboard 视觉
- 任何后端改动
- 整理 Flyway SQL 遗留的 `jimu_*` / `open_api_*` 建表语句

这些如需做，另开 spec / plan。
