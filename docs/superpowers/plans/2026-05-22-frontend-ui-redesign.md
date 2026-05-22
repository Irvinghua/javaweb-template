# 前端 UI 重构 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 `jeecgboot-vue3/` 前端按 `jeecgboot-ui/` 新设计稿整体换皮——登录页、应用外壳、首页、共享组件层（让全部系统页统一换皮），只改 UI 不改业务逻辑。

**Architecture:** 在隔离 git worktree（`../javaweb-template-ui-redesign`，分支 `feat/ui-redesign`，dev 端口 3101）中进行。先改 design token 与全局 CSS 变量层（70% CRUD 页自动吃新主题），再依次重绘外壳 / 登录 / 首页，最后改 `src/components/Table`、`src/components/Form`、`src/components/Modal|Drawer` 共享组件层使系统页统一换皮。业务逻辑（api/store/router/hooks/事件处理/表单字段）零变更。

**Tech Stack:** Vue 3 + Vite 6 + TypeScript + Ant Design Vue 4 + Less + pnpm + Node ^18 || >=20。

**Reference spec:** `docs/superpowers/specs/2026-05-22-frontend-ui-redesign-design.md`

**设计稿（在主仓库 `jeecgboot-ui/`，权威性见 spec）:**
- `login.html` — 登录页 + 全局主色权威来源
- `jeecgboot-redesign-v2.html` — 应用外壳 + 首页权威来源
- `pages/menu.html` — 系统列表页模板权威来源
- `pages/jeecg-page.css` — 页面级组件样式参考
- `pages/user-v2.html` 等 — 次要参考，与 `menu.html` 冲突时以后者为准

---

## 通用约定（每个可视任务都遵守）

**业务逻辑零变更**：只改 `<template>` 结构样式与 `<style>`，不改 `<script>` 里的事件处理、store 调用、接口调用、表单业务字段、props/emit 契约。如某处换皮必须动 `<script>`，先停下告知用户。

**每个可视任务的验证循环**（写进各任务 Step）：
1. `pnpm dev`（worktree，端口 3101）启动无控制台 error。
2. 用 chrome-devtools 打开 `http://localhost:3101` 对应页面截图，与设计稿 HTML 截图并列对比。
3. `npx vue-tsc --noEmit`：错误数不超过 Task 1 记录的 baseline。
4. `npx eslint <本任务改动的文件>`：无新增 error。
5. 任务指定的业务冒烟测试通过。
6. `git commit`（约定式提交信息）。

**禁区例外**：本计划经用户确认，允许改 `src/components/Table/**`、`src/components/Form/**`、`src/components/Modal/**`、`src/components/Drawer/**`，仅限 UI 换皮。其余禁区（api/store/router/utils/hooks/logics/settings 的业务逻辑）不动。

---

## File Structure Plan

```
worktree: ../javaweb-template-ui-redesign  (分支 feat/ui-redesign)
└── jeecgboot-vue3/
    ├── .env                                  # [MODIFY] VITE_PORT 3100 → 3101
    ├── package.json                          # [MODIFY] 加 @fontsource 字体依赖
    ├── src/
    │   ├── theme/
    │   │   ├── tokens.ts                      # [MODIFY] AntD token 改为新配色
    │   │   └── variables.less                # [NEW] 全局 CSS 变量层（--accent/--ink-* 等）
    │   ├── App.vue                            # [MODIFY] modeAction 的 colorTextBase 字面量
    │   ├── design/index.less                  # [MODIFY] @import variables.less
    │   ├── main.ts                            # [MODIFY] import @fontsource 字体
    │   ├── layouts/default/**                 # [MODIFY] 应用外壳换皮
    │   ├── views/sys/login/**                 # [MODIFY] 登录页换皮
    │   ├── views/dashboard/Analysis/**        # [MODIFY] 首页重写
    │   └── components/
    │       ├── Table/src/components/settings/ # [MODIFY] 工具栏 3→2、表格换皮
    │       ├── Table/src/components/TableAction.vue
    │       ├── Form/src/components/FormAction.vue   # [MODIFY] 高级筛选
    │       └── Modal|Drawer/**                # [MODIFY] 弹窗换皮
    └── TODO.md                                # [NEW] 系统页遗留记录
docs/superpowers/plans/2026-05-22-frontend-ui-redesign.md  # 本文件（主仓库 main）
```

---

## Task 1: 创建 worktree、分支、改端口、记录 baseline

**Files:**
- Create: git worktree `../javaweb-template-ui-redesign`
- Modify: `jeecgboot-vue3/.env`（worktree 内）

- [ ] **Step 1: 创建 worktree 与分支**

在主仓库根目录运行：
```bash
cd /Users/irvinghua/workspace/javaweb-template
git worktree add ../javaweb-template-ui-redesign -b feat/ui-redesign
```
预期：`Preparing worktree (new branch 'feat/ui-redesign')`，新目录 `../javaweb-template-ui-redesign` 出现。

- [ ] **Step 2: 安装依赖**

```bash
cd /Users/irvinghua/workspace/javaweb-template-ui-redesign/jeecgboot-vue3
pnpm install
```
预期：安装成功（worktree 有独立 `node_modules`）。

- [ ] **Step 3: 改 dev 端口为 3101**

用 Edit 修改 `../javaweb-template-ui-redesign/jeecgboot-vue3/.env`：
找到 `VITE_PORT = 3100`，改为 `VITE_PORT = 3101`。

- [ ] **Step 4: 记录 vue-tsc baseline**

```bash
cd /Users/irvinghua/workspace/javaweb-template-ui-redesign/jeecgboot-vue3
npx vue-tsc --noEmit 2>&1 | tail -5
```
把输出的错误总数记下来（JeecgBoot 现状可能本就有若干类型错误）。**后续任务以"不超过此数"为通过标准。** 把数字写进本任务 commit 信息。

- [ ] **Step 5: 启动 dev 冒烟**

```bash
pnpm dev
```
预期：终端打印 `Start Port: 3101`，浏览器访问 `http://localhost:3101` 出现登录页。确认后停掉。

- [ ] **Step 6: Commit**

```bash
cd /Users/irvinghua/workspace/javaweb-template-ui-redesign
git add jeecgboot-vue3/.env
git commit -m "chore(ui-redesign): worktree dev 端口改 3101（vue-tsc baseline: N 个错误）"
```
（把 N 换成 Step 4 的实际数字。）

> 后续所有任务均在 worktree 目录 `/Users/irvinghua/workspace/javaweb-template-ui-redesign/jeecgboot-vue3` 内操作。

---

## Task 2: Design Tokens + 全局 CSS 变量层 + 字体

**Files:**
- Modify: `src/theme/tokens.ts`
- Modify: `src/App.vue:39`
- Create: `src/theme/variables.less`
- Modify: `src/design/index.less`
- Modify: `package.json`（加字体依赖）
- Modify: `src/main.ts`（import 字体）

- [ ] **Step 1: 改 `src/theme/tokens.ts`**

整体替换 `tokens` 对象为：
```typescript
/**
 * AntD ConfigProvider theme token 单一真源。
 *
 * 每次 fork 后按新项目设计稿修改本文件即可让 70% 的 CRUD 页面自动吃上新主题。
 * 详见 docs/ai-redesign-workflow.md 与 README.md。
 */
export const tokens = {
  colorPrimary: '#5B6CFF',
  colorSuccess: '#15A34A',
  colorWarning: '#D97706',
  colorError: '#DC2626',
  colorInfo: '#5B6CFF',
  colorTextBase: '#0F172A',
  borderRadius: 8,
  fontSize: 14,
  sizeStep: 4,
  sizeUnit: 4,
  wireframe: false,
  fontFamily:
    "'Inter','Noto Sans SC',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'PingFang SC','Microsoft YaHei','Helvetica Neue',Helvetica,Arial,sans-serif",
};
```

- [ ] **Step 2: 改 `src/App.vue` 的 modeAction**

`App.vue` 的 `modeAction` 在 light 模式下用字面量 `'#333'` 覆盖了 `colorTextBase`，会盖掉 token。找到第 39 行：
```javascript
        Object.assign(data.token, { colorTextBase: '#333' });
```
改为：
```javascript
        Object.assign(data.token, { colorTextBase: '#0F172A' });
```
（dark 分支的 `'fff'` 不动——是既有代码，超出本次范围。）

- [ ] **Step 3: 新建 `src/theme/variables.less`**

创建文件，内容如下（值取自设计稿 `:root`；`--accent` 系列用 `login.html` 主色）：
```less
/**
 * 全局 CSS 变量层 —— AntD ConfigProvider token 覆盖不到的设计稿变量。
 * 供应用外壳 / 登录页 / 首页 / 表格工具栏等自定义样式引用。
 * 仅维护 light 主题值；JeecgBoot 原生 dark 模式不在本层处理。
 */
:root {
  /* 强调色（主色 = 登录页设计稿 #5B6CFF） */
  --accent: #5b6cff;
  --accent-600: #4756e0;
  --accent-700: #3a48c0;
  --accent-50: #eef0ff;
  --accent-100: #dde2ff;

  /* 表面 */
  --surface: #ffffff;
  --surface-2: #f5f7fb;
  --surface-3: #eef1f6;
  --window: #fafbfd;

  /* 文字阶 */
  --ink-900: #0f172a;
  --ink-700: #334155;
  --ink-600: #475569;
  --ink-500: #64748b;
  --ink-400: #7b8597;
  --ink-300: #cbd5e1;

  /* 描边 */
  --line: rgba(15, 23, 42, 0.07);
  --line-strong: rgba(15, 23, 42, 0.12);

  /* 状态色 */
  --good: #15a34a;
  --good-bg: #dcfce7;
  --warn: #d97706;
  --warn-bg: #fef3c7;
  --bad: #dc2626;
  --bad-bg: #fee2e2;

  /* 圆角 / 阴影 / 过渡 */
  --radius-card: 16px;
  --radius-pill: 999px;
  --shadow-card: 0 2px 10px rgba(15, 23, 42, 0.04), 0 1px 2px rgba(15, 23, 42, 0.04);
  --shadow-pop: 0 12px 32px rgba(15, 23, 42, 0.14), 0 2px 8px rgba(15, 23, 42, 0.06);
  --fast: 0.16s ease;
  --norm: 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}
```

- [ ] **Step 4: 把 variables.less 接入全局样式**

用 Read 查看 `src/design/index.less`，在其 `@import` 区追加一行（路径按该文件现有 import 风格）：
```less
@import './../theme/variables.less';
```
（若 `index.less` 用 `(reference)` 等修饰，普通 `@import` 即可——本文件只含 `:root` 声明。确认 import 后该文件仍能编译。）

- [ ] **Step 5: 自托管字体**

```bash
cd /Users/irvinghua/workspace/javaweb-template-ui-redesign/jeecgboot-vue3
pnpm add @fontsource/inter @fontsource/noto-sans-sc
```
然后用 Read 查看 `src/main.ts` 顶部 import 区，追加：
```typescript
import '@fontsource/inter/400.css';
import '@fontsource/inter/500.css';
import '@fontsource/inter/600.css';
import '@fontsource/inter/700.css';
import '@fontsource/noto-sans-sc/400.css';
import '@fontsource/noto-sans-sc/500.css';
import '@fontsource/noto-sans-sc/700.css';
```
（放在现有样式 import 附近即可。）

- [ ] **Step 6: 启动 dev 验证**

```bash
pnpm dev
```
用 chrome-devtools 打开 `http://localhost:3101`：
- 登录页按钮、链接等主色应变为紫蓝 `#5B6CFF`。
- 控制台无 error。
- 字体生效（Inter / Noto Sans SC）。

- [ ] **Step 7: 类型检查 + Lint**

```bash
npx vue-tsc --noEmit 2>&1 | tail -5
npx eslint src/App.vue src/theme/tokens.ts
```
预期：vue-tsc 错误数 ≤ baseline；eslint 无 error。

- [ ] **Step 8: Commit**

```bash
git add src/theme/tokens.ts src/theme/variables.less src/App.vue src/design/index.less src/main.ts package.json pnpm-lock.yaml
git commit -m "feat(ui-redesign): 应用新设计稿 design token 与全局 CSS 变量层"
```

---

## Task 3: 应用外壳 `src/layouts/default/**`

按 `jeecgboot-redesign-v2.html` 重绘侧边栏 / 顶栏 / 多页签 / 面包屑。以改 `<style>` 为主，结构按需微调。目标默认侧边栏导航模式。

**Files（先 Read 全部，再改）:**
- Modify: `src/layouts/default/index.vue` — 外壳根
- Modify: `src/layouts/default/sider/index.vue`、`LayoutSider.vue` — 侧边栏
- Modify: `src/layouts/default/menu/index.vue` — 菜单
- Modify: `src/layouts/default/header/index.vue`、`MultipleHeader.vue` — 顶栏
- Modify: `src/layouts/default/header/components/Breadcrumb.vue` — 面包屑
- Modify: `src/layouts/default/tabs/index.vue`、`tabs/components/TabContent.vue` — 多页签
- 参考但不改业务：`sider/useLayoutSider.ts`、`tabs/useMultipleTabs.ts`、`menu/useLayoutMenu.ts`

**保留不动的逻辑：** 菜单数据由后端动态下发（`useLayoutMenu`）、tabs 状态机（`useMultipleTabs`、`multipleTab` store）、侧边栏折叠状态、右键 tab 菜单的动作函数（`useTabDropdown`）、所有路由跳转。

- [ ] **Step 1: 读设计稿与现有代码**

Read `jeecgboot-ui/jeecgboot-redesign-v2.html`（CSS 段 line 86-385 是 sidebar，387-571 是 topbar/tabs；body 段 line 1044-1217 是结构）。Read 上述全部 layout 文件，弄清现有结构与 class。

- [ ] **Step 2: 侧边栏换皮**

对照设计稿 `.sidebar` / `.nav` / `.nav-item` / `.nav-group` / `.nav-sub`：
- 宽 232px、白底、右侧 1px `--line` 边线。
- 顶部品牌区：logo 方块（`--accent` 底）+ 名称。
- 菜单项：圆角 10px、字号 14.5px；hover `--surface-2`；active 态 `--accent-50` 底 + `--accent` 字 + 左侧 3px indicator。
- 分组标题：大写、11px、`--ink-400`、letter-spacing。
- 折叠态 72px：仅图标居中；子菜单 flyout 浮层；leaf 项 hover tooltip。
- 改 `<style>` 实现；菜单的展开/折叠/路由逻辑不动。

- [ ] **Step 3: 顶栏 + 多页签换皮**

对照设计稿 `.topbar` / `.tabs` / `.top-actions`：
- 顶栏一行：折叠按钮 + 多页签（胶囊容器，移入顶栏行）+ 右侧操作区（搜索 / 主题 / 通知 / 语言 / 分隔线 / 头像）。
- 多页签：胶囊式，圆角 7px，active 白底 + `--accent` 字 + 阴影；可关闭；右键菜单换皮（动作不动）。
- 顶栏滚动时加底部阴影（`.topbar.scrolled`）。
- 右侧图标按钮统一 `.icon-btn` 样式（36px、圆角 9px、hover `--surface-2`）。

- [ ] **Step 4: 面包屑换皮**

对照设计稿 `.crumbs`：顶栏下方独立一行，12px、`--ink-500`，分隔符小箭头，当前项 `--ink-900`。

- [ ] **Step 5: 验证（通用验证循环）**

`pnpm dev` → chrome-devtools 截图对比设计稿外壳 → `vue-tsc` ≤ baseline → `eslint` 改动文件无 error。
业务冒烟：登录进系统，点侧边栏菜单能正常跳转、打开多个 tab、关闭 tab、折叠/展开侧边栏、面包屑正确。

- [ ] **Step 6: Commit**

```bash
git add src/layouts/default
git commit -m "feat(ui-redesign): 重绘应用外壳（侧边栏/顶栏/多页签/面包屑）"
```

---

## Task 4: 登录页 `src/views/sys/login/**`

按 `login.html` 整页重写视觉，**保留全部登录方式与逻辑**。

**Files（先 Read 全部）:**
- Modify: `src/views/sys/login/Login.vue` — 容器（背景 + 左品牌区 + 右卡片）
- Modify: `src/views/sys/login/LoginForm.vue` — 账号登录表单
- Modify: `src/views/sys/login/MobileForm.vue` — 手机登录表单
- Modify: `src/views/sys/login/LoginFormTitle.vue`、`QrCodeForm.vue`、`RegisterForm.vue`、`ForgetPasswordForm.vue`、`OAuth2Login.vue` — 其余方式，按同款卡片风格补齐
- 参考不改：`useLogin.ts`（状态机 `useLoginState` / `LoginStateEnum`）、`LoginSelect.vue`

**保留不动的逻辑：** `useLogin.ts` 全部、各 Form 的 `handleLogin`/`onSubmit`/表单校验规则/store 调用（`userStore.login`）、`LoginState` 切换、验证码与短信倒计时逻辑、`handleBackLogin`。只换 `<template>` + `<style>`。表单字段集合以原系统为准。

- [ ] **Step 1: 读设计稿与现有代码**

Read `jeecgboot-ui/login.html` 全文（CSS line 25-445，结构 line 456-550，交互 line 552-609）。Read 上述全部登录文件。

- [ ] **Step 2: 重写 `Login.vue` 容器**

按 `login.html`：
- 全屏 `.page` 背景（渐变占位 + `::before/::after` 装饰 + `.grid-dots`），代码注释标明"后期可替换真实背景图"。
- 左侧 `.brand-block`：品牌徽标行（logo + 平台名 pill）+ 大标题（项目名）+ slogan。文案接现有 i18n / `globSetting.title`。
- 右侧 `.login-card`：悬浮玻璃卡片，承载各登录表单子组件。
- 保留 `LoginForm`/`ForgetPasswordForm`/`RegisterForm`/`MobileForm`/`QrCodeForm` 五个子组件挂载与 `useLoginState` 切换；保留 locale picker、dark toggle、`AppLogo`。
- 删除/替换旧 Less（`login-bg.svg` 等），dark 分支可保留或一并换皮。

- [ ] **Step 3: 重写账号 / 手机登录表单视觉**

按 `login.html` 的 `.tabs` + `.pane` + `.field` + `.btn-primary`：
- 账号/手机两个 tab（`LoginFormTitle` 或卡片内 tab 承载切换，复用现有 `LoginState`）。
- 输入框带前置图标、focus 态（`--accent` 边框 + 浅色光晕）。
- 账号表单：账号 / 密码 / 验证码（带验证码图片）/ 记住我 / 登录按钮 / 服务协议勾选——字段以原 `LoginForm.vue` 为准。
- 手机表单：手机号 / 短信验证码（带倒计时按钮）——字段以原 `MobileForm.vue` 为准。
- 仅替换模板与样式，校验和提交逻辑不动。

- [ ] **Step 4: 补齐其余登录方式风格**

`QrCodeForm` / `RegisterForm` / `ForgetPasswordForm` / `OAuth2Login`：设计稿未画，按同款玻璃卡片 + 输入框风格换皮，保持各自原有字段与逻辑。扫码/第三方入口以链接或附加 tab 形式保留在卡片内。

- [ ] **Step 5: 验证（通用验证循环）**

`pnpm dev` → chrome-devtools 截图 `http://localhost:3101`（登录页）对比 `login.html` → `vue-tsc` ≤ baseline → `eslint` 改动文件。
业务冒烟：账号登录成功进入系统；切到手机 tab，短信倒计时按钮工作；切到忘记密码/注册/扫码，界面正常无报错。

- [ ] **Step 6: Commit**

```bash
git add src/views/sys/login
git commit -m "feat(ui-redesign): 重绘登录页（保留全部登录方式）"
```

---

## Task 5: 首页 `src/views/dashboard/Analysis/**`

按 `jeecgboot-redesign-v2.html` 首页区重写。**就地重写** `Analysis/index.vue`，保留文件路径与组件名，使后端菜单组件串 `dashboard/Analysis` 仍解析。

**Files:**
- Modify: `src/views/dashboard/Analysis/index.vue` — 改为渲染新首页
- Create: `src/views/dashboard/Analysis/components/RedesignHome.vue`（或同级新 SFC）— 新首页主体
- 参考不改：`dashboard/Analysis/homePage/*`、`components/*`（旧首页组件，保留文件不删，避免破坏其它引用）

**数据：** 设计稿指标无对应后端接口，用占位静态数据，每处加注释 `// TODO: 占位数据，待接真实接口`。本任务不接后端、不新增 API。

- [ ] **Step 1: 读设计稿**

Read `jeecgboot-ui/jeecgboot-redesign-v2.html` 首页区：CSS line 773-957（stats / card / chart / promo / feed / table），结构 line 1221-1366。

- [ ] **Step 2: 新建 `RedesignHome.vue`**

按设计稿首页实现一个 SFC，含：
- 4 张指标卡 `.stat-card`（图标 chip + 标签 + 数值 + 涨跌 `delta`）。
- 销售额卡片 `.card`：标题切换器 + 时间范围 + 月度柱状图——用已装的 `echarts`（`package.json` 有 `echarts ^5.6.0`）渲染柱状图，替代设计稿的纯 CSS 柱。
- 促销卡 `.promo`（渐变背景 + 标签 + 标题 + 描述 + 按钮）。
- 最近动态 `.feed`（头像 + badge + 文案 + 时间）。
- 门店销售排行榜 `table`（排名 pill + 门店 + 负责人 + 金额 + 状态 tag）。
- 全部数据为占位常量，加 `// TODO` 注释。
- 样式用 Task 2 的全局 CSS 变量层（`--surface` / `--ink-*` / `--accent` / `--radius-card` 等）。

- [ ] **Step 3: 改 `Analysis/index.vue`**

整体替换为渲染新首页：
```vue
<template>
  <RedesignHome />
</template>
<script lang="ts" setup>
  import RedesignHome from './components/RedesignHome.vue';
</script>
```
（旧的 `indexStyle` 切换与 `IndexChart/IndexDef/IndexBdc/IndexTask` 不再渲染；旧文件保留在仓库中，不删除。）

- [ ] **Step 4: 验证（通用验证循环）**

`pnpm dev` → 登录后进入首页，chrome-devtools 截图对比设计稿首页 → `vue-tsc` ≤ baseline → `eslint` 改动文件。
业务冒烟：首页加载无报错；echarts 柱状图正常渲染；切换主题色后首页主色跟随。

- [ ] **Step 5: Commit**

```bash
git add src/views/dashboard/Analysis
git commit -m "feat(ui-redesign): 按设计稿重写首页（占位数据）"
```

---

## Task 6: 共享组件层 — 表格 `src/components/Table/**`

按 `pages/menu.html` + `pages/jeecg-page.css` 给 `BasicTable` 换皮，使全部系统列表页统一生效。

**Files（先 Read 全部）:**
- Modify: `src/components/Table/src/components/settings/index.vue` — 工具栏 3 图标 → 2 按钮
- Read 参考: `settings/RedoSetting.vue`、`SizeSetting.vue`、`ColumnSetting.vue`、`FullScreenSetting.vue`
- Modify: `src/components/Table/src/components/TableHeader.vue`、`TableTitle.vue` — 工具栏容器
- Modify: `src/components/Table/src/components/TableAction.vue` — 行操作
- Modify: `src/components/Table/src/components/TableFooter.vue` 及表格主体样式
- Modify: `src/design/ant/table.less`、`src/design/ant/pagination.less` — 表头/行/分页样式

**保留不动的逻辑：** 刷新、密度切换、列设置、全屏各自的功能函数与 emit；`TableAction` 的动作回调；表格取数、分页、选择 hooks（`useTableContext` 等）。只动渲染结构与样式。

- [ ] **Step 1: 读设计稿与现有代码**

Read `jeecgboot-ui/pages/menu.html`（工具栏 line 32-52、表格 line 59-166、`.toolbar-right` 即目标）与 `jeecgboot-ui/pages/jeecg-page.css`（搜 `.toolbar`、`.icon-action`、`.data-table`、`.pagination`、`.row-actions`）。Read 上述全部组件。

- [ ] **Step 2: 工具栏 3 图标 → 「刷新 + 设置」2 按钮**

改 `settings/index.vue`：当前并排渲染 `RedoSetting` / `SizeSetting` / `ColumnSetting` / `FullScreenSetting` 四个。改为：
- `RedoSetting` 保留为独立「刷新」图标按钮。
- 新增一个齿轮「设置」按钮，点击弹出 AntD `Dropdown` / `Popover`，其浮层内**组合**密度切换（来自 `SizeSetting` 的选项）、列设置（来自 `ColumnSetting` 的列勾选内容）、全屏开关（来自 `FullScreenSetting`）。
- 复用三个子组件已有的功能函数（密度切换/列变更 emit/全屏），只把它们的「触发器」从独立图标改为统一浮层内的条目。
- 图标按钮样式对齐设计稿 `.icon-action`（方形、圆角、hover/active 态）。
- `getSetting` 的开关（redo/size/setting/fullScreen）逻辑保留——某项关闭时浮层内对应条目不渲染。

- [ ] **Step 3: 表格本体换皮**

按设计稿 `.data-table`：
- 表头：`--surface-2` 底、`--ink-700` 字、加粗。
- 行 hover `--surface-2`；单元格内距与字号对齐设计稿。
- 「已选择 N 项」提示条按设计稿 `.alert-info` 换皮。
- 分页器按设计稿 `.pagination` 换皮。
- 改 `src/design/ant/table.less` / `pagination.less` 等全局表格样式实现。

- [ ] **Step 4: 行操作 `TableAction` 换皮**

按 `menu.html` 的 `.row-actions`：「编辑 | 更多」链接式 + 分隔符 + 更多下拉。JeecgBoot `TableAction` 本就是此形态，仅换皮（链接颜色 `--accent`、危险项 `--bad`、下拉浮层样式）。动作回调不动。

- [ ] **Step 5: 验证（通用验证循环）**

`pnpm dev` → 打开 `http://localhost:3101/#/system/user`（或任一系统列表页），chrome-devtools 截图对比 `menu.html` → `vue-tsc` ≤ baseline → `eslint` 改动文件。
业务冒烟：刷新按钮刷新表格；设置浮层内密度切换生效、列勾选生效、全屏生效；行内「编辑」「更多」下拉动作正常；分页正常；多选「已选择 N 项」正常。

- [ ] **Step 6: Commit**

```bash
git add src/components/Table src/design/ant
git commit -m "feat(ui-redesign): BasicTable 换皮（工具栏 3→2、表格/行操作/分页）"
```

---

## Task 7: 共享组件层 — 搜索区「高级筛选」`src/components/Form/**`

**Files（先 Read）:**
- Modify: `src/components/Form/src/components/FormAction.vue` — 查询/重置/展开按钮
- Read 参考: `src/components/Form/src/BasicForm.vue`、`src/components/Form/src/hooks/useAdvanced.ts`（若存在）
- Modify: 相关 Form 全局样式（如 `src/components/Form` 内 less 或 `src/design`）

**保留不动的逻辑：** `BasicForm` 的 `showAdvancedButton` 折叠机制、字段配置、查询/重置 emit、`useAdvanced` 计算。只换文案与样式。

- [ ] **Step 1: 读设计稿与现有代码**

Read `jeecgboot-ui/pages/user-v2.html`（`.filter-card` / `.filter-toggle` / `.filter-fields-advanced`，line 22-77、257-324）与 `pages/menu.html`（`.filter-card`，line 12-29）。Read `FormAction.vue` 与 `BasicForm` 折叠相关代码。

- [ ] **Step 2: 改 `FormAction.vue`**

- 展开/收起按钮文案改为「高级筛选」+ 箭头图标，样式对齐设计稿 `.filter-toggle`（`--accent` 字、ghost）。
- 查询按钮 primary、重置按钮 ghost，对齐设计稿 `.btn-primary` / `.btn-ghost`。
- 默认折叠：保留 `BasicForm` 现有「字段超过 N 行自动折叠」机制，不改其判定逻辑。

- [ ] **Step 3: 搜索区容器换皮**

筛选区卡片对齐设计稿 `.filter-card`：白底、圆角、`--shadow-card`；字段标签与输入控件样式跟随全局 token。

- [ ] **Step 4: 验证（通用验证循环）**

`pnpm dev` → 系统列表页（如 `/system/user`、`/system/depart`）→ chrome-devtools 截图对比设计稿筛选区 → `vue-tsc` ≤ baseline → `eslint` 改动文件。
业务冒烟：点「高级筛选」展开/收起更多字段；查询、重置正常工作。

- [ ] **Step 5: Commit**

```bash
git add src/components/Form
git commit -m "feat(ui-redesign): 搜索区换皮（展开按钮改高级筛选）"
```

---

## Task 8: 共享组件层 — 弹窗 / 抽屉 `src/components/Modal|Drawer/**`

**Files（先 Read 目录）:**
- Modify: `src/components/Modal/**` 内样式相关文件
- Modify: `src/components/Drawer/**` 内样式相关文件
- 必要时 Modify: `src/design` 内弹窗相关全局样式

**保留不动的逻辑：** Modal/Drawer 的开关控制、`useModal`/`useDrawer` hooks、确定/取消 emit、内部表单业务字段。只换头/体/底样式。

- [ ] **Step 1: 读设计稿与现有代码**

Read `jeecgboot-ui/pages/menu.html` 弹窗段（line 182-357：`.drawer` / `.dlg` / `.dlg-head` / `.dlg-body` / `.dlg-foot` / `.confirm-body`）与 `pages/jeecg-page.css` 对应 class。Read Modal/Drawer 组件目录。

- [ ] **Step 2: 弹窗 / 抽屉换皮**

- 头部 `.dlg-head`：标题（可带图标）+ 关闭按钮，底部 1px 边线。
- 主体 `.dlg-body`：内距、表单两列栅格样式跟随全局 token。
- 底部 `.dlg-foot`：右对齐「取消」(ghost) +「确定」(primary)。
- 确认类弹窗 `.confirm-body`：图标 + 标题 + 说明。
- **不改任何弹窗内的业务表单字段**——字段集合以原系统为准。

- [ ] **Step 3: 验证（通用验证循环）**

`pnpm dev` → 系统页打开新增/编辑弹窗、删除确认弹窗 → chrome-devtools 截图对比设计稿 → `vue-tsc` ≤ baseline → `eslint` 改动文件。
业务冒烟：打开/关闭弹窗正常；弹窗内表单字段齐全、提交/取消正常。

- [ ] **Step 4: Commit**

```bash
git add src/components/Modal src/components/Drawer src/design
git commit -m "feat(ui-redesign): 弹窗/抽屉换皮"
```

---

## Task 9: 系统页抽样验证 + 遗留记录

**Files:**
- Create: `TODO.md`（worktree `jeecgboot-vue3/` 根，或仓库根——与现有约定一致）

- [ ] **Step 1: 抽查系统页**

`pnpm dev`，逐一打开并用 chrome-devtools 截图检查（每页确认换皮生效、布局无失控、CRUD+分页业务正常）：
- `/system/user`（用户管理）
- `/system/role`（角色管理）
- `/system/menu`（菜单管理 — 对比 `menu.html`）
- `/system/depart`（部门管理）
- `/system/position`（职务管理）
- `/system/dict`（数据字典）
- 监控类页面任选 1-2 个（如在线用户、定时任务）
- demo 页任选 1 个（确认组件层改动未波及 demo）

- [ ] **Step 2: 记录遗留**

新建 `TODO.md`，列出抽查中发现的视觉出格 / `JVxeTable` 皮肤未跟 / 其它非阻断问题。明显出格项记此处，**本轮不逐页修**。

- [ ] **Step 3: Commit**

```bash
git add TODO.md
git commit -m "docs(ui-redesign): 系统页抽查遗留记录"
```

---

## Task 10: 端到端最终验证

**Files:**（不改文件，只验证）

- [ ] **Step 1: 类型检查**

```bash
cd /Users/irvinghua/workspace/javaweb-template-ui-redesign/jeecgboot-vue3
npx vue-tsc --noEmit 2>&1 | tail -5
```
预期：错误数 ≤ Task 1 baseline。

- [ ] **Step 2: Lint**

```bash
npx eslint src/theme src/App.vue src/layouts/default src/views/sys/login src/views/dashboard/Analysis src/components/Table src/components/Form src/components/Modal src/components/Drawer
```
预期：无新增 error。

- [ ] **Step 3: 生产构建冒烟**

```bash
pnpm build
```
预期：构建成功，产物在 `dist/`。

- [ ] **Step 4: 三方对比回归**

`pnpm dev`（3101），与原版（主仓库 `main`，3100）、设计稿 HTML 三方并列核对：
- [ ] 登录页（各登录方式）匹配 `login.html`
- [ ] 应用外壳（侧边栏/顶栏/多页签/面包屑）匹配 `jeecgboot-redesign-v2.html`
- [ ] 首页匹配设计稿首页
- [ ] 系统页（user/role/menu 等）匹配 `menu.html` 模板
- [ ] 主题色切换、dark 切换无崩溃
- [ ] 控制台无新 error

- [ ] **Step 5: git 状态检查**

```bash
cd /Users/irvinghua/workspace/javaweb-template-ui-redesign
git log --oneline -12
git status
```
预期：commit 链含 `chore(ui-redesign)` + 多个 `feat(ui-redesign)` + `docs(ui-redesign)`；`git status` 干净。

---

## 回退预案

- 各任务独立 commit，单个产物出问题可 `git revert <sha>`。
- 整体放弃：删 worktree 分支即可，主仓库 `main` 不受影响：
  ```bash
  cd /Users/irvinghua/workspace/javaweb-template
  git worktree remove ../javaweb-template-ui-redesign
  git branch -D feat/ui-redesign
  ```

## 超出范围声明（不在本 plan）

- 改后端代码、改业务逻辑/数据流/接口/表单业务字段
- 新增设计稿独有的全新功能（Cmd+K 命令面板等）
- 暗色模式专门设计（JeecgBoot 原生 dark 代码保留不动）
- 逐页重写 `src/views/system/**`
- 给首页接真实后端接口
- 深改 `JVxeTable` 内置皮肤
- 把 `feat/ui-redesign` 合并回 `main`（由用户在 QA 通过后决定）
