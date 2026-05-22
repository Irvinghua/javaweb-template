# vibeCRUD 前端 UI 重构 Design（基于新设计稿）

> 本 spec 定义把 `jeecgboot-vue3/` 前端按 `jeecgboot-ui/` 新设计稿做的一次整体 UI 重构。
> **只改 UI 表现，不改业务逻辑。** 在隔离的 git worktree 中进行，便于"设计稿 / 原前端 / 重构中前端"三方对比 QA。

## 背景

- 仓库为基于 JeecgBoot 3.9.1 裁剪的 ToB CRUD 脚手架（后端 `jeecg-boot/`，前端 `jeecgboot-vue3/`）。
- 上一版 spec/plan（`2026-04-24-frontend-template-fork-conventions`）建立了 fork-and-forget 的"可改区 / 禁区"规约，并规划了 `src/theme/tokens.ts`。**该 plan 尚未执行**——`src/theme/` 目录不存在，`App.vue` 仍是内联 token。本 spec 把 `tokens.ts` 的创建吸收为第一步。
- 本任务是上一版规约所预备的"真实 fork 换皮"。它**显式覆盖**上一版 spec 的两条非目标：本次**要**重绘 layout / login / dashboard，且**要**改 `src/components/**` 共享组件层。

## 目标

按设计稿重构前端 UI，覆盖三层：

1. **登录页** —— `src/views/sys/login/**`
2. **登录后的应用外壳 + 首页** —— `src/layouts/default/**`、`src/views/dashboard/Analysis/**`
3. **每个功能菜单页** —— 通过改造共享组件层（`BasicTable` / `BasicForm` / `Modal` 等），让全部 `src/views/system/**` 系统页一次性统一换皮

## 设计稿资产与权威性规则

| 资产 | 用途 | 权威性 |
|------|------|--------|
| `jeecgboot-ui/login.html` | 登录页视觉 | **登录页 + 全局主色的权威来源** |
| `jeecgboot-ui/jeecgboot-redesign-v2.html` | 应用外壳 + 首页视觉 | 外壳与首页的权威来源 |
| `jeecgboot-ui/pages/menu.html` | 系统列表页模板（筛选区 + 工具栏 + 表格 + 弹窗） | **系统页列表模板的权威来源** |
| `jeecgboot-ui/pages/*.html`（v2 后缀优先） | 各系统页布局参考 | 次要参考；与 `menu.html` 冲突时以 `menu.html` 为准 |
| `jeecgboot-ui/pages/jeecg-page.css` | 页面级 token 与组件样式 | 组件层换皮的样式参考 |
| `jeecgboot-ui/screens/*.png`、`ref/*` | 渲染参考图 | 仅供视觉参考 |

**权威性规则**：设计稿各页面并不完全一致。实现时——

- 登录页与全局**主色**以 `login.html` 为准。
- 系统列表页的筛选区 / 工具栏 / 表格 / 行操作 / 弹窗布局，以 `pages/menu.html` 为准；其它 `pages/*.html`（含 `user-v2.html`）凡与 `menu.html` 不一致的，按 `menu.html` 的模式对齐。
- 设计稿不精细处、弹窗表单字段，**一律以原系统为准**，不得增减业务字段、不得影响业务逻辑。

## 已决策项（澄清结论汇总）

1. **系统页改造深度** = 组件层一次性改造。改 `tokens` + 共享组件（`BasicTable` 工具栏 / 表格、`BasicForm` 搜索区），全部系统页自动换皮，**不逐页改** `system/**`。
2. **登录方式** = 保留原系统全部登录能力（账号 / 手机 / 扫码 / 第三方 OAuth / 注册 / 找回密码），仅整体换皮；设计稿未画的入口按同款风格补齐。**不删除任何登录入口。**
3. **首页内容** = 照设计稿重写（4 指标卡 + 销售额柱状图 + 促销卡 + 最近动态 + 排行榜）。指标无对应后端，**用占位 / demo 数据**，代码中明确标注；接真实接口为后续工作。
4. **Worktree** = 仓库同级新建 `../javaweb-template-ui-redesign`，分支 `feat/ui-redesign`，重构版 dev 端口 **3101**（与原版 3100 并行）。
5. **全局主色** = `#5B6CFF`（取自 `login.html` 的 `--brand-color`）。主壳设计稿原用的 `#2A6BEF` 统一替换为 `#5B6CFF` 及其衍生色阶。
6. **表格工具栏右上** = **2 个按钮**：`刷新`（独立）+ `设置`（齿轮图标，弹出菜单内含密度 / 列设置 / 全屏）。原 JeecgBoot 的三个独立设置图标合并为此结构。

## 改造范围

### 可改区（本任务改）

- `src/theme/**`（新建）—— design token 与全局 CSS 变量层
- `src/App.vue` —— 消费 tokens
- `src/layouts/default/**` —— 应用外壳
- `src/views/sys/login/**` —— 登录页
- `src/views/dashboard/Analysis/**` —— 首页
- `src/components/Table/**`、`src/components/Form/**`、`src/components/Modal/**`、`src/components/Drawer/**` —— 共享组件层（**经用户确认解除禁区限制**，仅做 UI 换皮）
- `src/assets/**` —— logo / 图片 / 背景
- `src/design/**` 或全局样式入口 —— 注册全局 CSS 变量层

### 不改（保持业务逻辑零变更）

- `src/api/**`、`src/store/**`、`src/router/**`、`src/utils/**`、`src/hooks/**`、`src/logics/**`、`src/settings/**` 的**业务逻辑**
- 任何后端代码（`jeecg-boot/**`）
- 各组件 / 页面的事件处理、表单提交、store 交互、接口调用、数据流
- 弹窗 / 抽屉的业务字段集合

> 例外：若换皮**必须**触碰上述目录中的纯样式 / 纯模板片段（如某 hook 里写死的 class 名），先停下告知用户、说明原因、等确认。

## 产物 1：Design Tokens

### 1a. `src/theme/tokens.ts`（新建）

AntD Vue 4 `ConfigProvider.theme.token` 的单一真源：

```typescript
export const tokens = {
  colorPrimary: '#5B6CFF',
  colorInfo: '#5B6CFF',
  colorSuccess: '#15A34A',
  colorWarning: '#D97706',
  colorError: '#DC2626',
  colorTextBase: '#0F172A',
  borderRadius: 8,
  fontSize: 14,
  wireframe: false,
  fontFamily:
    "'Inter','Noto Sans SC',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'PingFang SC','Microsoft YaHei','Helvetica Neue',Helvetica,Arial,sans-serif",
};
```

说明：
- 取值来自设计稿 `:root`（`login.html` 主色 + `jeecgboot-redesign-v2.html` 状态色 / 字体）。
- `wireframe` 由原 `App.vue` 的 `true` 改为 `false`——设计稿按钮为实心填充风格。
- `borderRadius` 取 8（设计稿输入框 / 按钮 8–10px；卡片 16px 由 CSS 变量层单独管理）。

### 1b. `src/App.vue` 重构

删除内联 token 字面量（约 line 75-89），改为 import 消费 `tokens.ts`；运行时仍用 `appStore.getProjectConfig.themeColor` 覆盖 `colorPrimary` / `colorInfo`，保留用户主题切换器能力；`modeAction` / dark 分支 / `getDarkMode` watch **保持不动**。

### 1c. 全局 CSS 变量层（新建，如 `src/theme/variables.less`）

AntD token 覆盖不到的设计稿变量，集中为一份 CSS 自定义属性，注册到全局样式入口，供外壳 / 登录 / 首页 / 工具栏等自定义样式引用：

- 强调色阶：`--accent #5B6CFF`、`--accent-600 #4756E0`、`--accent-50 #EEF0FF`、`--accent-100 #DDE2FF`
- 文字阶：`--ink-900 #0F172A` … `--ink-300 #CBD5E1`
- 表面：`--surface`、`--surface-2 #F5F7FB`、`--surface-3 #EEF1F6`、`--window #FAFBFD`
- 描边：`--line`、`--line-strong`
- 状态色 / 圆角（`--radius-card 16px`、`--radius-pill 999px`）/ 阴影 / 过渡

> 仅设 light 主题值。JeecgBoot 原生 dark 模式代码保留不动，本次不做暗色设计。

## 产物 2：应用外壳 `src/layouts/default/**`

对照 `jeecgboot-redesign-v2.html`，以改 CSS 为主、按需微调结构。目标为默认侧边栏导航模式（mix / top 模式做到不破即可，不专门重绘）。

- **侧边栏 sider**：232px 宽，白底，顶部品牌区（logo + 名称），分组菜单（分组标题大写小字），`nav-item` 圆角 + 浅蓝 active 态 + 左侧 3px indicator；可折叠至 72px，折叠态子菜单为 flyout 浮层 + leaf 项 tooltip。
- **顶栏 topbar**：折叠按钮 + 多页签 tabs（胶囊式，移入顶栏行）+ 右侧操作区（搜索图标 / 主题 / 通知 / 语言 / 分隔线 / 头像 profile）。
- **面包屑**：顶栏下方独立一行。
- **多页签 tabs**：胶囊样式，active 白底主色字，可关闭，右键上下文菜单（刷新 / 关闭 / 关闭其他等——复用现有能力，仅换皮）。
- 菜单数据仍由后端 `sys_permission` 动态下发，只换样式不改取数。
- 设计稿独有的全新功能（Cmd+K 命令面板等）现系统没有则**不新增**；现系统已有的（头部搜索、主题色板、租户切换等）顺带换皮。

## 产物 3：登录页 `src/views/sys/login/**`

对照 `login.html` 整页重写视觉，保留全部登录逻辑。

- **布局**：全屏背景（渐变占位 + 装饰，预留替换真实背景图）；左侧品牌区（logo + 平台名 + 大标题 + slogan）；右侧悬浮玻璃卡片。
- **卡片**：账号 / 手机两个 tab + 输入框（带前置图标、focus 态）+ 验证码 / 短信验证码 + 记住我 + 登录按钮 + 服务协议勾选。
- **保留全部登录方式**：扫码登录、第三方 / OAuth、注册、找回密码——设计稿未画的，按同款卡片风格补齐为附加 tab / 链接 / 弹窗。
- **不动逻辑**：`useLogin.ts`、各 Form 的 `onSubmit` / 校验 / store 交互、`LoginState` 状态机全部保留；只替换 `Login.vue` 及各子表单组件（`LoginForm` / `MobileForm` / `QrCodeForm` / `RegisterForm` / `ForgetPasswordForm` / `OAuth2Login` / `LoginFormTitle`）的 template + style。
- 表单字段集合以原系统为准（设计稿如有出入以原系统为准）。

## 产物 4：首页 `src/views/dashboard/Analysis/**`

照 `jeecgboot-redesign-v2.html` 首页区重写。

- **就地重写** `src/views/dashboard/Analysis/index.vue` 及其子组件——保留该文件路径与组件名，使后端菜单引用的组件串 `dashboard/Analysis` 仍能解析（不改后端菜单）。
- **内容**：4 张指标卡（图标 + 标签 + 数值 + 涨跌幅）、销售额柱状图（用已装好的 echarts）、促销卡、最近动态 feed、门店销售排行榜表格。
- **数据**：设计稿指标无对应后端接口，使用**占位 / demo 静态数据**，在代码注释中明确标注 `// TODO: 占位数据，待接真实接口`。本次不接后端、不新增 API。
- `dashboard/workbench` 等其它首页组件吃全局主题即可，不专门重绘。

## 产物 5：共享组件层（系统页统一换皮）

改共享组件，使全部 `src/views/system/**` 列表页自动获得设计稿风格。以 `pages/menu.html` + `jeecg-page.css` 为样式基准。

### 5a. 表格 `src/components/Table/**`

- **工具栏右上**：由原三个独立设置图标，改为 **2 个按钮**——`刷新`（独立）+ `设置`（齿轮图标，点击弹出 Popover / Dropdown，内含密度切换、列设置、全屏）。需调整 table setting 区组件的组合结构（把 Size / Column / FullScreen 收进一个弹层），属受控的结构改动。
- **工具栏左侧**：页面操作按钮（新增 / 导入 / 导出等）由各页 slot 传入，靠 AntD 按钮 token 自动换皮 + 工具栏容器样式。
- **表格本体**：表头加深加粗 + `--surface-2` 底；行 hover；单元格内距；分页器换皮；空态插画样式；密度（紧凑 / 默认 / 宽松）。
- **选择提示条**："已选择 N 项" 条按设计稿 `.alert-info` / `.selection-bar` 换皮。
- **行操作** `TableAction`：保持"编辑 | 更多"链接式（`menu.html` 即此式）+ 更多下拉，仅换皮。

### 5b. 搜索区 `src/components/Form/**`

- 列表页搜索表单：默认显示常用字段，超出部分由"**高级筛选**"展开 / 收起控制——复用 `BasicForm` 已有的 `showAdvancedButton` 折叠能力，重做按钮文案（→"高级筛选"）与样式。
- 查询 / 重置按钮、字段标签、输入控件按设计稿换皮。

### 5c. 弹窗 / 抽屉 `src/components/Modal/**`、`src/components/Drawer/**`

- 弹窗 / 抽屉的头部、主体、底部按钮区按设计稿 `.dlg-head` / `.dlg-body` / `.dlg-foot` 换皮。
- **表单字段集合不动**——以原系统为准。

> `JVxeTable` 使用内置皮肤，token / 全局样式覆盖不全，列为已知差距，本轮做到不崩、视觉基本协调即可；如需深改另记遗留。

## 产物 6：系统页抽样验证

组件层改完后，抽查 5–8 个 `src/views/system/**` 页面（如 user / role / dict / depart / position / tenant + monitor 下若干），确认：换皮生效、布局无失控、业务功能（查询 / 新增 / 编辑 / 删除 / 分页）无回退。明显出格的记入 `TODO.md` 遗留，不在本轮逐页修。

## 翻译策略与技术约束

- **优先 AntD token**：能靠 `ConfigProvider` token 覆盖的（主色 / 圆角 / 字体 / 状态色）走 token。
- **token 覆盖不到的**：走 scoped Less / CSS + 全局 CSS 变量层；避免与 AntD 内部样式对抗。
- **自定义 SFC**（外壳 / 登录 / 首页）：直接消费全局 CSS 变量层。
- 考虑过"纯 token""平行 CSS 覆盖层重度对抗 AntD""整体 fork 组件"三种，均偏负 ROI；采用上述**混合策略**。
- **字体**：设计稿用 Inter + Noto Sans SC。Google Fonts CDN 在目标 ToB 内网环境可能加载慢 / 不可达——**自托管这两款字体**（放 `src/assets/fonts/` 并在全局样式 `@font-face` 引入），`fontFamily` 末尾保留系统字体回退。

## Worktree 与三方对比

- 在 `../javaweb-template-ui-redesign` 创建 worktree，分支 `feat/ui-redesign`（基于 `main`）。
- worktree 内重构版前端 dev 端口改为 **3101**（改该 worktree 的 `.env.development` / vite 端口配置，仅限 worktree）。
- 对比方式：原版（主仓库 `main`，3100）+ 重构版（worktree，3101）+ 设计稿（`jeecgboot-ui/*.html` 本地直接打开）三方并列。
- 每个产物完成后截图与设计稿比对。

## 风险与应对

| 风险 | 可能性 | 应对 |
|------|--------|------|
| 改组件层（Table/Form）影响到 `demo`、`sys` 等非 system 页 | 中 | 产物 6 抽查范围纳入 demo 及若干非 system 页 |
| 工具栏"3→2"需重组 table setting 结构，可能碰交互逻辑 | 中 | 只重组渲染结构与触发方式，密度/列设置/全屏各自原有功能函数不动；改完单独验证三项功能 |
| `JVxeTable` 内置皮肤覆盖不全 | 中-高 | 列为已知遗留，本轮不深改 |
| Google Fonts 不可达导致字体回退不一致 | 中 | 自托管字体（见技术约束） |
| 登录页保留全部方式但设计稿只画 2 tab，补齐风格需自行设计 | 中 | 扫码/注册/找回密码等按账号卡片同款风格补齐，提交时截图给用户确认 |
| App.vue 重构改漏 `modeAction` dark 分支 | 低-中 | 用 git diff 逐字段比对；验证时切 dark 看文字色 |
| 首页占位数据被误当真实数据 | 低 | 代码注释明确标注 `TODO: 占位数据` |

## 验证计划

每个产物完成后：

1. `pnpm dev`（worktree，3101）运行无控制台 error。
2. 与设计稿截图比对视觉。
3. `npx vue-tsc --noEmit` 无新增类型错误；`npx eslint <改动文件>` 无新增 lint 错误。
4. 关键业务路径手测：登录（各方式）、首页加载、系统页 CRUD 与分页、主题色切换、dark 切换。

全部完成后：`pnpm build` 生产构建冒烟。

## 实施顺序

1. 创建 worktree + 分支 + 端口 3101
2. 产物 1：Design Tokens（tokens.ts + App.vue + 全局 CSS 变量层 + 自托管字体）
3. 产物 2：应用外壳
4. 产物 3：登录页
5. 产物 4：首页
6. 产物 5：共享组件层
7. 产物 6：系统页抽查 + 遗留记录

每步一次 commit（约定式提交信息）；发现 lint / vue-tsc 报错立即修，不带错进下一步。

## 非目标

- ❌ 改后端代码
- ❌ 改业务逻辑、数据流、接口调用、表单业务字段
- ❌ 新增设计稿独有的全新功能（Cmd+K 命令面板等）
- ❌ 暗色模式专门设计（JeecgBoot 原生 dark 代码保留不动）
- ❌ 逐页重写 `src/views/system/**`
- ❌ 给首页接真实后端接口
- ❌ 深改 `JVxeTable` 内置皮肤
- ❌ 重写 README / CLAUDE.md / 上一版 workflow 文档（模板层文档，不在本次单项目换皮范围）
