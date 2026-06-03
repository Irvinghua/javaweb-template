# JeecgBoot UI 重构设计规范（design.md）

> 本文档系统性总结 `jeecgboot-redesign-v2.html`（主壳/首页）、`login.html`（登录认证）、以及 `pages/` 目录下全部子页面所共同遵循的设计语言。
> 目标：让任意一名设计/前端在不看历史文件的情况下，也能产出与现有系统**完全一致**的新页面。
>
> 适用范围：JeecgBoot 企业级低代码平台 · 浅色主题（Light，深色为预留态）。

---

## 0. 设计基调（Design Principles）

| 原则 | 说明 |
|---|---|
| **柔和浅色仪表盘** | 大面积留白 + 极浅灰背景 + 纯白卡片 + 柔和阴影，**不用硬边框分割**。 |
| **单一主色克制使用** | 蓝色仅用于：主操作按钮、激活态、链接、强调数字。其余一律中性灰。 |
| **信息密度适中** | 表格、表单行高舒适；提供"紧凑/默认/宽松"三档密度切换。 |
| **圆角统一** | 卡片大圆角（16–18px），控件中圆角（10px），标签全圆角（999px）。 |
| **状态用色语义化** | 绿=成功/已绑定，橙=警告/建议，红=危险/失败，蓝=信息/进行中。 |
| **动效轻量** | 过渡 0.15–0.22s，缓动 `cubic-bezier(.4,0,.2,1)`；尊重 `prefers-reduced-motion`。 |
| **无 AI 风** | 不用大面积渐变背景、不用 emoji、不用"圆角卡+左色条"套路；图标统一线性 stroke。 |

---

## 1. 设计令牌（Design Tokens）

三个文件的令牌已对齐，**以 `pages/jeecg-page.css` 的 `:root` 为权威基准**。主壳的 `--accent` 等同于子页的 `--brand-500`，命名差异见下表末注。

### 1.1 品牌色 Brand

| Token | 值 | 用途 |
|---|---|---|
| `--brand-500` | `#1A56FF` | 主色：主按钮、激活态、链接、focus 环 |
| `--brand-600` | `#1E4ED8` | 主色加深：链接文字、hover |
| `--brand-50` | `#EEF3FF` | 主色极浅底：激活底、soft 按钮、info 提示底 |

> 登录页（`login.html`）使用略偏紫的 `--brand:#5B6CFF` 作为悬浮卡视觉主色，这是**认证场景的专属强调色**；进入系统后统一回到 `#1A56FF`。新建系统内页一律用 `#1A56FF`。

### 1.2 表面 Surface

| Token | 值 | 用途 |
|---|---|---|
| `--surface` | `#FFFFFF` | 卡片、弹窗、输入框聚焦态 |
| `--surface-2` | `#F7F8FB` | hover 底、表头、次级填充 |
| `--surface-3` | `#F1F3F8` | 输入框默认底、chip 灰底 |
| `--window` | `#FBFBFD` | 页面最底层背景 |

### 1.3 文字 Ink（中性灰阶）

| Token | 值 | 用途 |
|---|---|---|
| `--ink-900` | `#0F172A` | 标题、关键值 |
| `--ink-700` | `#334155` | 正文、表格单元格 |
| `--ink-500` | `#64748B` | 次要文字、label、说明 |
| `--ink-400` | `#94A3B8` | 占位符、禁用、空值 |
| `--ink-300` | `#CBD5E1` | 分隔点、checkbox 边框、滚动条 |
| `--line` | `rgba(15,23,42,.07)` | 所有分隔线 / 描边 |

### 1.4 语义状态色 Status

| 语义 | 前景 | 底色 | Token |
|---|---|---|---|
| 成功 good | `#16A34A` | `#DCFCE7` | `--good` / `--good-bg` |
| 警告 warn | `#F59E0B` | `#FEF3C7` | `--warn` / `--warn-bg` |
| 危险 bad | `#EF4444` | `#FEE2E2` | `--bad` / `--bad-bg` |
| 信息 info | `#2563EB` | `#DBEAFE` | `--info` / `--info-bg` |
| 紫（辅助） | `#7C3AED` | `#EDE9FE` | — |

### 1.5 圆角 / 阴影 / 动效

| Token | 值 |
|---|---|
| `--radius-card` | `18px`（卡片）；主壳为 `16px` |
| `--radius-ctrl` | `10px`（按钮、输入框、pager） |
| 标签圆角 | `999px` |
| `--shadow-card` | `0 4px 18px rgba(15,23,42,.05), 0 1px 3px rgba(15,23,42,.04)` |
| 弹窗阴影 | `0 24px 64px -12px rgba(15,23,42,.28), 0 8px 24px rgba(15,23,42,.12)` |
| 弹出层阴影 | `0 12px 32px rgba(15,23,42,.14), 0 2px 8px rgba(15,23,42,.06)` |
| 过渡时长 | 快 `.16s` / 常规 `.2s` |
| 缓动 | `cubic-bezier(.4,0,.2,1)`；弹窗弹入 `cubic-bezier(.16,1,.3,1)` |

---

## 2. 字体排印（Typography）

- **字体族**：`'Inter','Noto Sans SC',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif`
- **基准字号**：`14px`（`body`）

| 层级 | 字号 | 字重 | 颜色 |
|---|---|---|---|
| 页面/弹窗大标题 | 15–17px | 600–700 | `--ink-900` |
| 卡片区块标题 | 14px | 600 | `--ink-900` |
| 正文 / 单元格 | 13–14px | 400–500 | `--ink-700` |
| Label / 说明 | 12–13px | 400–500 | `--ink-500` |
| 微标注 / 占位 | 11–12px | 400 | `--ink-400` |
| KPI 数值 | 22px | 700 | `--ink-900`，`font-variant-numeric: tabular-nums` |

- **数字**：所有金额、ID、统计、分页一律 `font-variant-numeric: tabular-nums` 等宽对齐。
- **区块小标题**：左侧 `3px×13px` 蓝色竖条（`.dlg-section-title` / `.block-title`），竖条后接标题文字，可跟一段浅灰副说明。

---

## 3. 布局结构（Layout）

### 3.1 三层信息架构

1. **主壳 Shell**（`jeecgboot-redesign-v2.html`）：左侧固定导航栏（232px）+ 右侧内容区，`grid-template-columns: 232px 1fr`。
2. **子页 Page**（`pages/*.html`）：在内容区中以 `.page`（`padding:22px 24px 28px; gap:16px`）纵向堆叠卡片。
3. **认证页 Auth**（`login.html`）：独立全屏，左品牌叙事 + 右悬浮卡片，不带主壳。

### 3.2 侧边导航 Sidebar（主壳）

- 宽 232px，纯白底，右侧 `--line` 分隔；可折叠到 72px（仅留图标）。
- **品牌区**：34px 圆角方形 logo（主色底白图标）+ 平台名 + 折叠按钮。
- **导航项** `.nav-item`：高 ≥44px，13px 间距，line icon（20px，stroke 1.7）+ 文字。
  - hover：`--surface-2` 底。
  - **激活态**：`--brand-50` 底 + 主色字/图标 + 左侧 `3px` 圆角主色 indicator。
- **分组**：父级可展开（`grid-template-rows 0fr→1fr` 动画），子项左侧带 1.5px 引导竖线；分组标题为 11px 大写字母 + 1.2px letter-spacing 的灰色 overline。

### 3.3 卡片 Card

```css
.card{ background:#fff; border-radius:18px; box-shadow:var(--shadow-card); }
```
- 卡片之间用 `.page` 的 `gap:16px` 拉开，**不要加边框**。
- 常见内边距：筛选卡 `18–20px`；面板 `16–20px`；信息卡用 `padding:0` + 内部 `.info-head/.info-body` 分区。

### 3.4 子页内子导航（个人信息中心模式）

- 左侧 232px 纵向 pill 子菜单（`.pn-item`，激活=`--brand-50`底+主色字）+ 右侧 tab 内容区。
- 窄屏（≤960px）子菜单转为横向可滚动，pill 宽度 `auto`。

---

## 4. 组件库（Components）

### 4.1 按钮 Button（高 38px，`.btn-sm` 为 32px）

| 类 | 样式 | 场景 |
|---|---|---|
| `.btn-primary` | 主色渐变 `linear-gradient(135deg,#2A66FF,#1A56FF)` + 投影 | 提交、确定、新增 |
| `.btn-ghost` | 白底 + `--line` 边 + 灰字 | 取消、次操作 |
| `.btn-soft` | `--brand-50` 底 + `--brand-600` 字 | 轻量强调（编辑、绑定） |
| `.btn-danger` | 红色渐变 + 投影 | 删除、危险操作 |
| `.icon-action` | 36px 圆形白底描边 | 工具栏图标按钮（刷新等） |

- 图标 15px，与文字 `gap:6px`。禁用态 `opacity:.65` 且去投影。

### 4.2 表单控件 Control（高 38px）

```css
.control{ height:38px; padding:0 12px; background:var(--surface-3);
  border:1px solid var(--line); border-radius:10px; font-size:13px; }
.control:focus{ background:#fff; border-color:rgba(26,86,255,.4);
  box-shadow:0 0 0 3px rgba(26,86,255,.12); }
```
- `select.control` 内置自绘 chevron；`textarea.control` 最小高 76px 可纵向拉伸。
- **登录页输入框**为更大尺寸变体（高 54px、左内嵌图标、focus 环更明显），仅用于认证场景。
- **Checkbox** `.cbx`：16px 圆角方框，选中=主色底+白勾。**Switch**：38×22 圆角滑块，开=主色。
- **表单行** `.form-row`：右对齐 label（96px，必填前缀红 `.req`）+ 控件；底部 `.form-footer` 右对齐按钮，上边 `--line` 分隔。

### 4.3 标签 / 状态 Tag（`.tag` 全圆角 pill，11px/600）

`.tag-green` 已绑定/启用 · `.tag-orange` 建议/警告 · `.tag-red` 停用/失败 · `.tag-blue` 信息/当前 · `.tag-gray` 中性/英文别名。

### 4.4 数据表格 Table `.data-table`

- 表头 `.surface-2` 底、`--ink-500` 字、600 字重、左对齐、首尾单元格 10px 圆角。
- 行 hover `--surface-2`；末行去底边线。`.col-name` 关键列加深加粗；`.num` 等宽数字；`.muted` 弱化。
- **树形表**：`.tree-toggle`（折叠箭头旋转）+ `.indent-1/2` 缩进 + 行内 `.tree-icon`。
- **空态** `.table-empty`：居中线性图标（52px，`--ink-300`）+ 说明文字。
- **行操作** `.link-action`：主色文字链接，hover 浅蓝底；危险项 `.danger` 红色；多个之间用 `.link-sep` 竖分隔。

### 4.5 分页 Pagination

右对齐；`.pager button` 32px 圆角方块，hover 主色描边，`.active` 主色渐变底白字；附 `.page-size` 下拉。

### 4.6 KPI 统计卡 `.kpi`

白卡 + 左侧 46px 圆角图标块（`.blue/.green/.orange/.red/.purple` 对应语义底色）+ 右侧 22px 等宽数值 + 12px 灰 label。栅格 `repeat(auto-fill,minmax(210px,1fr))`。

### 4.7 分段切换 Segmented `.seg`

灰底圆角药丸容器，激活项=白底+主色字+轻投影。用于视图/范围切换。

### 4.8 弹窗层 Dialog Layer（z-index：遮罩/抽屉 1000，Toast 1100）

| 组件 | 类 | 要点 |
|---|---|---|
| 遮罩 | `.dlg-overlay` / `.drawer-overlay` | `rgba(15,23,42,.45)` + 2px 模糊 |
| 居中弹窗 | `.dlg` + `.dlg-sm/md/lg/xl`（420/560/720/980） | 弹入 pop 动画，头/体/脚三段式 |
| 右侧抽屉 | `.drawer` + `.drawer-md/lg/xl` | 右滑入场 |
| 头部 | `.dlg-head` | 56px 高，标题前可带主色图标，右侧 `.dlg-close` |
| 底部 | `.dlg-foot` | 右对齐按钮，`.foot-left` 可放次要信息 |
| 确认框 | `.confirm-icon.danger/warn/info` | 圆形语义图标 + 标题 + 说明 |
| 导入 | `.dropzone` + `.steps` 步骤条 | 虚线拖拽区 hover 变蓝 |
| 轻提示 | `.toast.success/error/warn/info` | 顶部居中，左 3px 语义色条 |
| 行内菜单 | `.menu-pop` | fixed 弹出，危险项红色 |

### 4.9 加载与骨架

- **跳动方块 Loader**（系统选定方案，见 `pages/loading-final.html`）：5 根主色渐变竖条，`@keyframes` 中间高两侧低波浪跳动，纯 CSS 无 GIF。
- `.spinner` 旋转环（按钮内白色 / `.dark` 主色）；`.skeleton` shimmer 骨架屏。

---

## 5. 图标（Icons）

- 统一 **线性描边（line / stroke）** 风格，`stroke-width` 1.7–2，`stroke-linecap/linejoin: round`。
- 常用尺寸：导航 20px、按钮 15px、表格/行内 14–16px、KPI/图标块 21px。
- 颜色随上下文：默认 `--ink-400/500`，激活/强调用主色。
- **禁止** 使用 emoji 或彩色填充插画作为功能图标。第三方品牌（钉钉/微信/飞书/GitHub）可用其品牌色填充 logo。

---

## 6. 认证页专属规范（login.html）

- **整体**：浅蓝紫渐变背景 + 网格点 + 模糊光斑；左侧品牌叙事（pill 徽标 + 72px 超大标题 + slogan），右侧玻璃拟态悬浮卡（`backdrop-filter: blur(18px)`，圆角 22px）。
- **悬浮卡固定 `min-height:700px`**：登录 / 忘记密码 / 注册 / 二维码登录四视图切换时高度恒定，不跳动；视图淡入（`viewIn` 动画）。
- **登录表单**：Tabs（账号登录 / 手机登录）+ 大输入框（左图标）+ 账号登录含**图形验证码行**（输入框 + 右侧彩色验证码图块，点击刷新）+ 记住我/忘记密码行 + 大号主按钮（letter-spacing 加宽）+ "二维码登录 · 注册"链接 + "其他登录方式"社交图标。
- **子视图**：均带返回按钮回到登录；忘记密码为三步走（验证身份 → 重置密码 → 重置成功）带步骤指示器；二维码视图含扫码框 + 中心 logo。
- 该页主色用 `#5B6CFF`（认证专属），其余规范（圆角、按钮、输入、tag）与系统一致。

---

## 7. 响应式与无障碍

- 断点：`960px`（子菜单转横向 / 双列转单列）、`900px`（split 转单列）、`560px`（弹窗双列转单列、抽屉满宽）。
- `prefers-reduced-motion: reduce` 时关闭全部动画与过渡。
- focus 可见态：主色 focus 环 `box-shadow:0 0 0 3px rgba(26,86,255,.12)`；`.dlg-close` 有 `:focus-visible` outline。
- 命中目标：导航项 ≥44px；登录页按钮/输入 54px。
- 对比度：`--ink-400` 已提到满足 AA 的灰度用于说明文字。

---

## 8. 文件清单（现状）

| 文件 | 角色 |
|---|---|
| `jeecgboot-redesign-v2.html` | 主壳 + 首页（导航、顶栏、KPI、图表的权威样式来源） |
| `pages/jeecg-page.css` | **子页共享样式表（设计令牌与组件权威基准）** |
| `pages/jeecg-page.js` | 子页共享交互（弹窗、Toast、筛选折叠、表格设置等） |
| `pages/*.html` | 各系统管理子页（用户、菜单、部门、字典、数据源、日志、个人信息中心等） |
| `pages/profile.html` | 个人信息中心（左子菜单 + 4 tab） |
| `pages/loading-final.html` | 加载页落地版（跳动方块 Loader） |
| `login.html` | 登录认证页（四视图切换） |

---

## 9. 新建页面快速检查清单（Checklist）

- [ ] 引入 `pages/jeecg-page.css`，复用其 token 与组件类，**不要新造颜色**。
- [ ] 用 `.page` 包裹，卡片间靠 `gap` 拉开，不加硬边框。
- [ ] 主色只用于主按钮 / 激活 / 链接 / 强调数字；其余中性灰。
- [ ] 数字加 `tabular-nums`；状态用语义 tag；图标用线性 stroke。
- [ ] 交互态齐全：hover / focus 环 / 禁用 / 空态 / 加载（spinner 或骨架）。
- [ ] 过渡 0.15–0.22s + 标准缓动；做 `prefers-reduced-motion` 兜底。
- [ ] 响应式断点处理；命中目标足够大；focus 可见。
- [ ] 无 emoji、无大渐变背景、无"圆角卡+左色条"套路。
