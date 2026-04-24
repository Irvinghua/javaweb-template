# vibeCRUD 前端模板 Fork 规约改造 Design

> 本 spec 定义为 `jeecgboot-vue3/` 前端工程做的一次"最小结构性改造"，让每次 fork 后基于新项目的设计稿做 UI 换皮变得规约清晰、AI 友好。

## 背景

- 仓库为 ToB CRUD 后台管理系统的脚手架模板，来源是裁剪过的 JeecgBoot 3.9.1
- 前端在 `jeecgboot-vue3/`，后端在 `jeecg-boot/`，本 spec 只涉及前端
- 交付模式：**fork-and-forget**。每个项目独立 fork，不回流 template
- 项目场景：70% CRUD 页面（复用 JeecgBoot 系统管理 + 组件库吃全局主题） + 30% 定制（dashboard、报表、业务页，按设计稿 AI 改造）
- 每个项目的设计稿风格差异大。决定**不做** UI 组件层抽象，也**不预置**中性视觉底盘（均属负 ROI）

## 目标

建立三样东西，让每次 fork 后的"换皮"高效且 AI 可执行：

1. **单一 design token 真源** `src/theme/tokens.ts`，集中 AntD `ConfigProvider.theme.token`
2. **AI 改造 workflow 文档** `docs/ai-redesign-workflow.md`，含步骤 / 禁区 / prompt 模板
3. **工程级规约 README** `README.md` 重写，告知 fork 者怎么用、什么不能改

## 非目标（本 spec 不做）

- ❌ 移动任何现有文件（不拆 DefaultLayout、不建 `src/project/` 目录）
- ❌ 预置任何"中性视觉底盘"（不换默认色、不重绘 layout/login/dashboard）
- ❌ 建脚手架工具链（无 `pnpm theme:apply`、无 `pnpm page:gen`）
- ❌ 改 Less 变量生成逻辑（`build/generate/generateModifyVars.ts` 原样保留）
- ❌ 深色模式做为设计目标——tokens.ts / workflow 只按 light 设计；JeecgBoot 原生 dark 代码保留不动（解读 A：留着不触发，零运行时代价）
- ❌ 改后端代码
- ❌ 改任何 `src/views/system/**` 或 `src/components/**`

## 产物清单

| # | 文件 | 性质 | 说明 |
|---|------|------|------|
| 1 | `jeecgboot-vue3/src/theme/tokens.ts` | 新建 | AntD ConfigProvider token 单一真源 |
| 2 | `jeecgboot-vue3/src/App.vue` | 重构 | 消费 `tokens.ts`，去掉内联 token 字面量 |
| 3 | `jeecgboot-vue3/docs/ai-redesign-workflow.md` | 新建 | AI 改造流程 + prompt 模板 |
| 4 | `jeecgboot-vue3/README.md` | 大改 | 定位从 JeecgBoot 官方 readme → vibeCRUD 模板 readme |
| 5 | `jeecgboot-vue3/CLAUDE.md` | 小改 | Theme System 节重写、新增 Template Fork Conventions 节、顶部定位句更新 |

## 产物 1：`src/theme/tokens.ts`

**职责**：集中维护 AntD Vue 4 `ConfigProvider.theme.token` 的所有可调参数。
**不负责**：Less 变量（走 `build/generate/generateModifyVars.ts`）、`--j-global-primary-color` CSS 变量（走 App.vue `modeAction`）。

**完整导出**：

```typescript
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

值全部从 `App.vue` 当前内联字面量（App.vue:75-89）搬迁，**行为不变**。

**设计说明**：

- **扁平而非分组**：AntD 官方 token 就是扁平结构，强分三组会增加维护成本。AI 一次性看完十几个 key 比分组查找更快
- **运行时主色分层**：编译期默认值在 tokens.ts；运行时用户主题切换器仍通过 `appStore.getProjectConfig.themeColor` 覆盖，消费方在 `{...tokens, colorPrimary: themeColor}` 上合并
- **命名保留 `tokens.ts`**：follow AntD 官方 terminology，避免与"运行时主题切换"语义冲突

## 产物 2：`src/App.vue` 重构

**唯一变更**：删除 line 75-89 内联 token 字面量，改为 import 消费 `tokens.ts`。

**伪代码（仅示意变更点）**：

```typescript
import { tokens } from '/@/theme/tokens';

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

**保持不动**：
- `modeAction(data)` 整体逻辑（含 `colorTextBase` 在 dark 下临时设为 `#fff` 的分支）
- `getDarkMode` watch 分支（切 `theme.darkAlgorithm`）
- `changeTheme(themeColor)` 调用
- setTimeout 延迟触发

**验证标准**：
- `pnpm dev` 运行无控制台报错
- 首屏视觉与改造前逐像素一致（重构零行为变化）
- 主题色切换器（设置抽屉里的预置色板）仍能切换主色

## 产物 3：`docs/ai-redesign-workflow.md`

文档用中文，面向 Claude Code / Cursor 等 AI 代理以及审阅者人类。

**章节结构与完整内容**：

```markdown
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

禁区 ≠ 绝对不动；是"未经用户显式确认不要改"。注意本文档针对**UI 改造任务**；fork 初始化（改项目身份、`package.json` name、`.env` 标题等）不在本文档范围，按 README.md 执行。

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
```

## 产物 4：`jeecgboot-vue3/README.md` 重写

**现状**：JeecgBoot 官方中文 readme，含社区链接、Pro 版介绍、贡献流程、徽章群组等。对 fork 使用者无价值。

**改写为"vibeCRUD 前端模板 readme"**，章节如下：

```markdown
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

​```bash
pnpm install
pnpm dev          # 端口 3100；代理 /jeecgboot → localhost:8080/jeecg-boot
​```

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

​```
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
​```

## 常用命令

​```bash
pnpm dev              # 开发服务器
pnpm build            # 生产构建
pnpm clean:cache      # 清 vite 缓存
pnpm reinstall        # 重装依赖
pnpm batch:prettier   # 批量格式化 src
​```

## Lint / 类型检查

- `npx eslint src/path/to/file.vue`
- `npx stylelint "src/**/*.{vue,less,css}"`
- `npx vue-tsc --noEmit`（未配全量 CI，手动跑）

## 更多

- 后端参见 `jeecg-boot/` 及其 `CLAUDE.md`
- 前端编码约定参见 `CLAUDE.md`（与本文互补：本文档面向人类与 AI 代理，CLAUDE.md 记录编码细节）

---

底层基于 [JeecgBoot](https://github.com/jeecgboot/JeecgBoot) 3.9.1 裁剪。
```

## 产物 5：`jeecgboot-vue3/CLAUDE.md` 改动

三处最小改动：

### 改动 1 — 顶部定位句

line 7 `JeecgBoot Vue3 frontend — an enterprise low-code platform ...` 改为：

> vibeCRUD 前端模板（基于 JeecgBoot Vue3 3.9.1 裁剪）—— 为 fork-and-forget 的 ToB CRUD 项目设计。工程级规约见 `README.md`；本文件记录编码细节。

### 改动 2 — Theme System 节重写

替换 "### Theme System" 小节（约 line 87-92）为：

```markdown
### Theme System

- **AntD ConfigProvider tokens**：集中在 `src/theme/tokens.ts`，是每次 fork 后按设计稿换皮的主入口。App.vue 消费此文件注入 `<ConfigProvider :theme.token>`
- **Runtime 主色覆盖**：`src/App.vue` 监听 `appStore.getProjectConfig.themeColor`，运行时覆盖 tokens 里的 `colorPrimary` / `colorInfo`，保留用户主题切换器能力
- **Less 变量生成**：`build/generate/generateModifyVars.ts` 独立维护 Less 侧变量（不与 tokens.ts 联动；两套系统并行）
- **Dark 模式**：JeecgBoot 原生能力保留但不主动使用。fork 项目如确定不用，可删设置抽屉里的开关（位于 `src/layouts/default/setting/**`）
- **CSS 变量 `--j-global-primary-color`**：App.vue 动态写入 `document.documentElement`，供自定义样式引用
- **CSS class prefix**：`jeecg`（定义在 `src/settings/designSetting.ts`）
```

### 改动 3 — 新增"Template Fork Conventions"节

位置：放在 "## Project Overview" 之下、"## Common Commands" 之上。

```markdown
## Template Fork Conventions

本工程是 fork-and-forget 模板。修改代码时请留意"可改区 / 禁区"边界：

**可改区**（按项目设计稿自由改）
- `src/theme/tokens.ts` / `src/layouts/default/**` / `src/views/login/**` / `src/views/dashboard/**` / `src/views/<业务模块>/**`

**禁区**（未经用户确认不要主动改）
- `src/views/system/**` / `src/components/**` / `src/store/**` / `src/router/**` / `src/utils/**` / `src/api/**` / `src/hooks/**` / `src/logics/**` / `src/settings/**` / `build/**` / `vite.config.ts`

完整说明见 `README.md` 与 `docs/ai-redesign-workflow.md`。
```

## 验证计划

改造完成后执行：

1. `cd jeecgboot-vue3 && pnpm install`（确认无依赖变化）
2. `pnpm dev`，浏览器访问 `http://localhost:3100`
   - 登录页视觉与改造前一致（零行为差异）
   - 登录后，用设置抽屉切几次主题色：主色仍然能动态变
   - 打开 3-5 个系统管理页：视觉与改造前一致
3. `npx vue-tsc --noEmit`（无类型错误）
4. `npx eslint src/theme/tokens.ts src/App.vue`（无 lint 错误）

## 风险与应对

| 风险 | 可能性 | 应对 |
|------|--------|------|
| App.vue 重构改漏 `modeAction` 分支，dark 模式下文字色错 | 中 | 验证计划第 2 步要求切 dark 看文字色；用 git diff 对照原 token 字面量逐字段比对 |
| tokens.ts 导出方式与现有 vite alias `/@/` 不兼容 | 低 | `src/` 下其他 `.ts` 文件已大量使用相同 alias，参照它们即可 |
| README 中文编写后与 CLAUDE.md 英文编码约定重复 / rot | 中 | 约定"README = 工程级规约，CLAUDE.md = 编码细节"两者互相引用不互相复制；在 CLAUDE.md 改动 1 的定位句里明示 |
| workflow 文档的 prompt 模板在实际 AI 使用中发现不够用 | 中-高 | 该文档是"活文档"，第一个真实 fork 项目使用后收集反馈迭代，不要求本次 spec 定稿完美 |

## 实施顺序建议（后续 writing-plans 阶段决定最终拆分）

建议顺序：

1. 先做产物 1（tokens.ts）+ 产物 2（App.vue 重构）+ 验证，保证功能零回退
2. 再做产物 3（workflow 文档）、产物 4（README 重写）、产物 5（CLAUDE.md 改动）——纯文档，不影响运行
3. 一次提 PR 或分两个 commit（code / docs）
