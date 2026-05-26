# UI Redesign 遗留事项

Task 9（系统页抽样验证）输出。基于 worktree `feat/ui-redesign` 抽查
`/system/**` 子页面，记录新 UI 在系统页上的表现 + 残留问题。

## 抽样范围

| 路径 | 类型 | 截图 | 结论 |
| --- | --- | --- | --- |
| `/system/user` | 表格 + 搜索 + 分页 | `sample-user.png` | OK |
| `/system/role` | 表格 + 搜索 + 分页 | `sample-role.png` | OK |
| `/system/menu` | 树表格 | `sample-menu.png` | OK，操作列偏窄 |
| `/system/depart` | 树 + 右侧 Tabs Form | `sample-depart.png` | OK |
| `/system/position` | 表格 | `sample-position.png` | OK |
| `/system/dict` | 表格 + 多页分页 + 跳转 | `sample-dict.png` | OK |
| `/system/notice` | 表格 + 状态 Tag | `sample-notice.png` | OK |
| `/system/notice` → 新建 | Modal + Form + 富文本 | `sample-notice-drawer.png` | OK（含毛玻璃） |

新 UI 总体生效：表格头/工具栏/已选提示条 14px 间距、分页 32×32 + 110px 下拉、
卡片圆角 + 阴影、Tag 配色、Modal/Drawer 毛玻璃遮罩、富文本编辑器 — 全部
hold 住，未发现破坏性回归。

## 待处理

### A. 多列窄表格 操作列空间不足（**UI 微调**）

**现象**：列数较多的表格在默认列宽下，最右"操作"列被挤压。
- 用户管理 10 列：操作列只剩 `编辑 ⋯`（"删除/详情/冻结"等折叠到 `⋯`，但展开按钮也很挤）
- 菜单管理 7 列：操作列 + "排序" 列头都被截断（显示 `排…` / `编辑 ⋯`）

**根因**：antd `Table` 默认每列均分剩余宽度，未对操作列设置固定宽度或 `fixed: 'right'`。
旧版同样存在，不是本次重构引入。但既然要做收口，建议：

1. 抽样表格 columns 配置补 `width: 120`（操作列）、`fixed: 'right'`；
2. 关键列（如菜单名称、用户姓名）补 `minWidth: 140`；
3. 整体走表格水平滚动条而不是挤压（已在 Task 6 阶段把 `.ant-table-body` 改成 `overflow-x: auto`，配套即可）。

**优先级**：P2 — 影响体验，不影响功能。

### B. 残留种子数据（**DB 数据清理，不属本 UI 任务**）

裁剪了 AI / Online / JimuReport 模块代码后，数据库 seed 里还有引用：

- `/system/role` 列表里 "AI应用角色 / aiadmin"
- `/system/dict` 列表里 "AI应用类型 / 知识库文档类型 / 模型类型 / 模型提供者"
- `/system/notice` 列表里 "【重磅】JimuReport积木报表v2.0版本发布"、
  "JeecgBootv3.8.2 Online专项升级来袭，引领AI低代码平台新时代～" 等

**根因**：种子 SQL（`db/*.sql` 或对应 mybatis-plus 初始化数据）里还有这些行。

**处理**：跟模板裁剪一并交给后端 / 数据库初始化脚本，前端只是"显示出来了"。
新仓库 fork 后第一次 init DB 前清掉对应行即可。

**优先级**：P3 — 仅是历史数据展示，不影响新 fork 项目的真实使用。

### C. 未抽查的页面（**Task 10 端到端再过一遍即可**）

抽样代表性已够，下列页面留到端到端最终验证里扫一眼（应该都没问题）：

- `/system/tableWhiteList`（白名单管理）
- `/system/tenant`（多租户管理）— 注意：tenant 弹窗已经在前期任务里改过设计稿对齐
- `/system/category`（分类字典）
- `/system/homeConfig`（首页配置）
- `/system/message`（消息中心 — 模板 / 收件箱）
- `/monitor/*`（系统监控）— 已覆盖 disk / redis / route / datalog
- `/mytenant/*`（我的租户子页 — 租户用户、租户默认套餐等已逐个改过）

### D. 暗色主题适配（**Task 10 时再过**）

整改时主要走亮色（设计稿基准），暗色模式（`html[data-theme='dark']`）的：
- `BasicTable` 表格底色 / 行 hover
- `Modal/Drawer` 表面色
- 加载页（已在最新 commit 里补了 dark fork）
- 工具栏 / 搜索区文本对比度

均未逐个回归。Task 10 启动后再切到 dark mode 抽样几个页面校对。

**优先级**：P2 — fork 项目默认亮色，但模板要兼顾。

## 不影响合并的"提了知道一下"

- `tenant-setting-redesigned` 的 `.org-tile-toggle` 在 hover 时背景色用了
  `--surface-2`，跟 mockup `--surface-3` 略浅，但视觉差异极小，未改。
- `BaseSetting` 个性签名上传组件 `:deep(.sign-upload)` 的 200×80 尺寸是
  hardcoded —— 可考虑提到 token，但目前只有这一处使用，不做提取。
- 加载页 color hardcoded 用了 `#5B6CFF`/`#7E8DFF` 字面量而不是 CSS
  variable，原因是 `<style>` 在 `index.html` 里，跑在 Vue 挂载前，
  `variables.less` 还没载入。属于不可避免的硬编码。
