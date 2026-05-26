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

### A. 多列窄表格 操作列空间不足（**UI 微调**）— ✅ 已处理

**现象**：列数较多的表格在默认列宽下，最右"操作"列被挤压。
- 用户管理 10 列：操作列只剩 `编辑 ⋯`（"删除/详情/冻结"等折叠到 `⋯`，但展开按钮也很挤）
- 菜单管理 7 列：操作列 + "排序" 列头都被截断（显示 `排…` / `编辑 ⋯`）

**根因 + 处理**：

1. **真正的源头**在 `src/hooks/system/useListPage.ts` 默认 `actionColumn.fixed: false`
   ——每个调 useListPage 的页面都拿到这个默认值。已改成 `fixed: 'right'` + `align: 'center'`。
2. 加固在 `src/components/Table/src/hooks/useColumns.ts handleActionColumn`，
   即使外部不传 `actionColumn.fixed`，默认也会注入 `fixed: 'right'`。
3. 菜单管理 columns（`menu.data.ts`）的"图标 50 / 排序 50 / 组件 150 / 路径 150"
   过窄，已调整为"图标 70 / 排序 80 / 组件 180 / 路径 180"。

效果：操作列锁定在右侧、阴影提示，菜单/用户/角色/字典/职务等系统页统一受益。

### B. 残留种子数据（**DB 数据清理**）— ✅ 已处理

裁剪了 AI / Online / JimuReport 模块代码后，数据库 seed 里还有引用：

- `/system/role` 列表里 "AI应用角色 / aiadmin"
- `/system/dict` 列表里 "AI应用类型 / 知识库文档类型 / 模型类型 / 模型提供者"
- `/system/notice` 列表里 "【重磅】JimuReport积木报表v2.0版本发布"、
  "JeecgBootv3.8.2 Online专项升级来袭，引领AI低代码平台新时代～" 等

**处理**：新增 flyway 迁移
`jeecg-boot/.../flyway/sql/mysql/V3.9.3_0__remove_ai_jimureport_seeds.sql`，
内容包括：

- 删除 AI 字典定义（dict_code='ai_app_type'/'know_doc_type'/'model_type'/'model_provider'）
  及其 dict_item；
- 删除 AI 应用角色（role_code='aiadmin'）+ 角色关联 + 用户关联；
- 删除 AI / OpenAPI 残留菜单权限（url/component 匹配 super/airag / dashboard/ai /
  super/aiapp / views/openapi）+ 角色关联；
- 删除 JimuReport / 积木报表 / Online 关键字的 sys_announcement 行 + 对应 send 记录；
- 清理 sys_table_white_list 中残留的 ai_/airag_/jimu_ 表行。

迁移会在下次启动 jeecg-boot 时自动执行（位于 `src/main/resources/flyway/sql/mysql/`），
覆盖既有数据库的清理 + 新 fork DB 初始化后的清理（fresh dump 里 V3.9.0~V3.9.3 全跑一遍）。

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
