# 设计方案：用对齐版 code-template 重建 jeecg-codegen 生成器

- 日期：2026-06-03
- 范围：`.claude/skills/jeecg-codegen/`（纯本地，不在 git 跟踪内）
- 保留：`SKILL.md`（已做完路径 mac 化 / 名称统一 / 中立化 / 占位符 4 项修改）
- 重建：`scripts/`（codegen.py + FtlRunner.java）、`templates/`

## 背景与动机

`.claude/skills/jeecg-codegen` 是从开源 JeecgBoot 复制来的自带引擎的代码生成器，**自带一整套未对齐本工程 UI 的 FreeMarker 模板**（default/one、tree、tab/inner-table/erp、vue3Native 等）。

本工程已经过裁剪 + UI 重构，并由团队在仓库内维护了一套**对齐过新 UI 的模板**：

```
jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/resources/jeecg/code-template/
  ├── one/         单表
  ├── one2/        单表（另一种包布局，本工程不用）
  ├── onetomany/   一对多·平铺子表（JVxeTable）
  └── onetomany2/  一对多·Tab
```

目标：**删除 skill 自带的 scripts 与 templates，改用仓库对齐版 code-template 完整复刻生成器功能**，使生成产物与团队现有页面风格一致。

## 关键事实（已核验）

1. **渲染兼容**：code-template 与 skill 的 FtlRunner 约定**完全一致**——`.javai/.vuei/.tsi` 后缀、`${var}` 路径占位、`[1-n]` 子表文件用 `#segment#${subTab.entityName}.java` 切分、FreeMarker 语法。故 FtlRunner 可近乎原样复用。
2. **包布局**：本工程真实模块为 `org.jeecg.modules.<模块>/entity`，对应 `one`（非 `one2`）。
3. **一对多可行**：改造后前端 `src/components/jeecg/JVxeTable` 存在；onetomany / onetomany2 的 vue3 模板均为 BasicTable 同框架、已对齐。
4. **无移动端**：本仓库不存在 uniapp 工程 → 砍掉 mobile 产物。
5. **菜单 SQL**：code-template **没有** menu SQL 模板；skill 旧版的 `common/sql/menu_insert.ftl` 与本工程 `sys_permission` 列（`is_route`/`is_leaf`/`rule_flag`/`internal_or_external` 等）**完全匹配**，可移植。
6. **上下文契约（审计 code-template 得出）**：
   - 顶层：`entityName` `entityPackage` `bussiPackage` `tableName` `primaryKeyField` `columns` `subTables` `currentDate`
   - `po`（列）：`fieldName` `fieldType` `filedComment`（注意此拼写）`fieldDbType` `classType`
   - `tableVo`：`ftlDescription` `searchFieldNum`
   - `sub`（子表）：`entityName` `ftlDescription` `foreignKeys` `tableName` `colums`（注意此拼写）`originalColumns` `originalForeignKeys`
   - 结论：旧 skill 的 `normalize_ctx` 是该契约的**超集**，仅需补 `tableVo.searchFieldNum`，并核对字典/classType 处理。

## 已确认的决策

| # | 决策 |
|---|---|
| 渲染引擎 | 保留 Java FreeMarker，复刻 FtlRunner（不改用纯 Python） |
| SKILL.md | 允许同步更新「模板覆盖范围」表与 CLI 参数表，使之与真实能力一致 |
| 菜单 SQL | 保留，移植旧 `menu_insert.ftl` |
| 表类型 | 支持三种：单表 / 一对多平铺 / 一对多Tab |
| 移动端 | 砍掉 |
| 包布局 | 用 `one` |
| templates 来源 | **复制** code-template 进 skill（self-contained），SKILL.md 注明源在仓库需同步 |

## 架构

两层保持，均重建：

### scripts/FtlRunner.java（渲染器，功能等价复刻）

模板无关。职责：读 ctx.json（fastjson2）→ 注入 `Format` 驼峰工具 → 遍历风格目录每个模板 → 路径 `${var}` 展开（包名点转斜杠）→ FreeMarker 渲染 → 含 `[1-n]` 的按 `#segment#文件名` 切分 → `.javai/.vuei/.tsi` 还原后缀落盘。与现有实现逻辑相同，仅作为「重建」一并重写并验证可独立编译（锁定 Java 8 字节码）。

### scripts/codegen.py（编排层，重写）

1. **CLI**：
   ```
   --style   single | onetomany | onetomany-tab     (映射 one / onetomany / onetomany2)
   --ctx     <必填> ctx.json 路径（{tempdir}/jeecg-codegen/<表名>_ctx.json）
   --backend-root / --frontend-root / --flyway-dir   (正常模式至少传一个)
   --out     [调试] 仅渲染到目录不分发
   --dry-run 只打印计划
   ```
   去掉旧的 `--frontend-style`（只剩 vue3）、`--mobile-root`。
2. **风格校验**：`STYLE_MAP = {single: one, onetomany: onetomany, onetomany-tab: onetomany2}`，非法直接拒绝。
3. **normalize_ctx**：移植旧 skill 的列/子表补全（超集），新增 `tableVo.searchFieldNum`；按 code-template 实际用到的 5 个 po 字段为准，多余兜底无害保留；重新核对字典/classType 渲染路径与对齐版一致。
4. **ensure_compiled**：首次 javac 编译 FtlRunner（探测 JDK 版本，产出 Java 8 字节码）。
5. **render**：`java -cp lib/*:cache FtlRunner <templates> <styleDir> <normCtx> <workDir>`。
6. **dispatch**：
   - backend → `{backend-root}/src/main/java/{bussiPackage}/{entityPackage}/...`
   - 前端(vue3) → `{frontend-root}/src/views/{entityPackagePath}/{entityNameLower}/...`
   - sql → `{flyway-dir}/V<date>_1__menu_insert_<entity>.sql`（同名去重；菜单 component 路径按模块子目录改写）
   - 任一目标根未传 → 对应类别产物跳过。
7. **write_files**：支持 `--dry-run`，输出 `[codegen] WROTE <abs>` 事件行；退出码 0=成功。

### templates/（复制 + 菜单 SQL）

```
templates/
  ├── common/sql/menu_insert.ftl                 ← 移植自旧 skill，与本工程 sys_permission 对齐
  ├── one/         …/vue3/…  + …/vue3/V${currentDate}_1__menu_insert_${entityName}.sql (include 上面)
  ├── onetomany/   …（含 [1-n] 子表，#segment# 切分）+ 菜单 SQL stub
  └── onetomany2/  …（含 [1-n]List）+ 菜单 SQL stub
```
- 内容来自 `jeecg/code-template` 的 one / onetomany / onetomany2。
- 丢弃 one2、uniapp。
- 菜单 SQL：保留旧 skill 的 `common/sql/menu_insert.ftl`（自带 role 授权 admin），每风格 vue3 目录下放一个 `.sql` stub `<#include "/common/sql/menu_insert.ftl">`。FtlRunner 的 templateRoot=`templates/`，故 `/common/...` 绝对 include 可解析。

## SKILL.md 同步改动

- 「模板覆盖范围」表：改为 single / onetomany / onetomany-tab，前端仅 vue3。
- CLI 参考表：去掉 `--frontend-style`、`--mobile-root`，`--style` 取值改为新三种。
- 删除 tree / erp / inner-table / vue3Native 全部描述与示例。
- 典型调用示例：`--style single`，去掉 frontend-style。
- 新增一行注记：templates 源自 `jeecg/code-template`，改模板需回源同步。

## 验证策略

1. `--dry-run` 跑 single / onetomany / onetomany-tab 三个样例 ctx → 断言产出文件清单符合预期（后端 6 类 + 前端 4 类 + 1 SQL；一对多额外子表组）。
2. `--out` 渲染到临时目录 → 肉眼比对生成的 `*List.vue` / `*.data.ts` 与仓库已对齐页面（如 `system/tenant/TenantUserList.vue`）风格一致、import 路径有效。
3. 菜单 SQL → 核对列名与 `sys_permission` DDL 一致，可被 Flyway 命名规范接受。
4.（可选）对生成的 Java 跑 `mvn -pl jeecg-module-system/jeecg-system-biz -am compile -DskipTests` 验证可编译。

## 不做（YAGNI）

- 树表（code-template 无）、ERP / 内嵌子表 / Tab-in-Modal（skill 旧专属，code-template 无）
- vue3Native 第二套前端风格
- uniapp / uniapp3 移动端
- one2 包布局

## 风险与缓解

- **模板漂移**：templates 是 code-template 的副本，团队改了源不会自动同步 → SKILL.md 注明 + 后续可加一个 sync 检查（暂不做）。
- **字典/classType 差异**：旧 normalize 的 @Dict/popup_dict/cat_tree 逻辑可能与对齐版不一致 → 实施时以 code-template 实际模板为准逐项核对。
- **onetomany 子表**：依赖 JVxeTable，生成后需实跑确认子表录入正常（验证第 2 步覆盖）。
