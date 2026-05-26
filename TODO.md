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

### C. 未抽查的页面 — ✅ Task 10 已补抽样

Task 10 端到端验证里补查了：
- `/system/tableWhiteList` ✓（截图 `sample-tablewhitelist.png`）— 操作列 fixed:right 生效；
  表格里看到 `airag_knowledge` / `airag_flow` / `airag_model` 行 — 已由 B 项的
  flyway 迁移 V3.9.3_0 处理，下次启动后端自动清掉。
- `/system/category` ✓（截图 `sample-category.png`）— 编辑/删除/添加下级 三个操作在
  120px 操作列里略挤但仍可读，可后续考虑给该页 actionColumn 覆盖 width 为 160。
- 其余 `/system/tenant`、`/system/homeConfig`、`/system/message` 未单独抽样，但都走
  同一套 BasicTable / useListPage，A 项修复后均默认受益（操作列锁右）。
- `/monitor/*` 已在前期任务覆盖 disk / redis / route / datalog。
- `/mytenant/*` 在前期单独改过。

### D. 暗色主题适配 — 保留为"模板未启用"

整改时走亮色（设计稿基准）。暗色模式 (`html[data-theme='dark']`) 各部件的状态：
- `BasicTable` / `Modal/Drawer` / 工具栏 — 走 antd ConfigProvider tokens，未单独
  改过暗色主题样式；
- 加载页 — `index.html` 里已补 dark 主题 fork（双 radial + linear 反色）；
- App 整体 — 默认亮色，设置抽屉里仍有"暗色主题"切换按钮，但本模板未做暗色稿。

依据 `jeecgboot-vue3/CLAUDE.md`："Dark 模式：JeecgBoot 原生能力保留但不主动使用。
fork 项目如确定不用，可删设置抽屉里的开关。" — 本模板暗色保留为"原生兜底"，
不做逐页回归。fork 项目如要正式支持，需按设计稿出一版暗色 token 再回归。

**优先级**：P3 — 模板范畴外，留给具体 fork 项目处理。

## 不影响合并的"提了知道一下"

- `tenant-setting-redesigned` 的 `.org-tile-toggle` 在 hover 时背景色用了
  `--surface-2`，跟 mockup `--surface-3` 略浅，但视觉差异极小，未改。
- `BaseSetting` 个性签名上传组件 `:deep(.sign-upload)` 的 200×80 尺寸是
  hardcoded —— 可考虑提到 token，但目前只有这一处使用，不做提取。
- 加载页 color hardcoded 用了 `#5B6CFF`/`#7E8DFF` 字面量而不是 CSS
  variable，原因是 `<style>` 在 `index.html` 里，跑在 Vue 挂载前，
  `variables.less` 还没载入。属于不可避免的硬编码。

## Task 10 端到端验证结论

执行了下列检查（命令均在 `jeecgboot-vue3/` 目录跑）：

| 项 | 命令 | 结果 |
| --- | --- | --- |
| Type check | `npx vue-tsc --noEmit` | 30 个 TS 错误，**全是 JeecgBoot 基线问题**（chart/Bar.vue、BasicButton.vue、mock/menu.ts、build/vite/plugin/* 等），UI 重构涉及的文件 0 错误 |
| Prod build | `pnpm build` | exit 0，dist 正常产出（PWA + sw.js + _app.config.js 都齐全），末尾"复制 airag chat 目录失败"是裁剪 AI 模块后 copyChat 脚本找不到目录的副作用，不影响构建 |
| 浏览器抽样 | chrome-devtools | 用户/角色/菜单/部门/职务/字典/通告 / 白名单 / 分类字典 全部正常渲染；操作列默认锁右生效，毛玻璃遮罩生效，新增 Modal 富文本可用 |
| Git 状态 | `git log --oneline` | feat/ui-redesign 分支累计 ~30 个 commit，最后一个是本 Task 10 收口 |

**结论**：UI 重构无破坏性回归，可合并。剩余 30 个 vue-tsc 基线错误属于 JeecgBoot 3.9.1
继承，不在本次重构范围；建议后续单独发一个 `chore: clean baseline ts errors` 系列收尾。
