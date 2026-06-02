# 代码生成器模板对齐新 UI — 清理 + 验证 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 删除已死的 vue2 代码生成模板、把单表弹窗模板对齐重构后的参考页，并端到端实跑生成器证明 vue3 产物在新 UI 下渲染正确。

**Architecture:** UI 重构已在共享组件层（`BasicTable`/`BasicForm`/`TableAction`/`BasicModal`）+ 全局 CSS 完成，vue3 模板消费同一套组件故自动继承新 UI。本计划只做两处模板编辑（删 vue2 + 单表弹窗微调）外加端到端生成验证；vue3 列表/data/api 模板不动。

**Tech Stack:** Freemarker 模板（`.vuei`/`.tsi`）、`codegenerate-1.5.5.jar`（混淆，已 javap 出 API）、Java 17 + Maven、MySQL、Vue3 前端（pnpm）。

**Spec:** `docs/superpowers/specs/2026-06-02-codegen-template-cleanup-and-verify-design.md`

---

## File Structure

模板根目录：`jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/resources/jeecg/code-template/`

| 文件/目录 | 责任 | 本计划动作 |
|---|---|---|
| `{one,one2}/.../vue3/modules/${entityName}Modal.vuei` | 单表新增/编辑弹窗模板 | **改动 B**：useForm 配置微对齐 |
| `{one,one2,onetomany,onetomany2}/.../vue/**` | vue2 死模板（13 文件） | **改动 A**：删除 |
| `{one,one2,onetomany,onetomany2}/.../{vue3,uniapp}/**` | vue3（保留对齐）/ uniapp（保留不动） | 不动 |
| `jeecg-system-start/.../resources/jeecg/jeecg_config.properties` | 生成器输出路径/包/搜索字段 | 验证期临时改，结束还原 |
| `jeecg-system-start/.../resources/jeecg/jeecg_database.properties` | 生成器读表的 DB 连接 | 验证期确认指向可用 DB |
| `jeecg-system-start/.../java/org/jeecg/codegenerate/JeecgOneGenTest.java` | 一次性程序化生成入口 | 验证期新建，结束删除 |

---

## Task 1: 单表弹窗模板微对齐（改动 B）

**Files:**
- Modify: `jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/resources/jeecg/code-template/one/java/${bussiPackage}/${entityPackage}/vue3/modules/${entityName}Modal.vuei`
- Modify: `jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/resources/jeecg/code-template/one2/java/${bussiPackage}/vue3/${entityPackage}/modules/${entityName}Modal.vuei`

- [ ] **Step 1: 改 `one` 弹窗模板的 useForm 配置**

把现有块（注意源文件用 4 空格缩进）：

```js
    const [registerForm, {resetFields, setFieldsValue, validate}] = useForm({
        labelWidth: 150,
        schemas: formSchema,
        showActionButtonGroup: false,
    });
```

改为：

```js
    const [registerForm, {resetFields, setFieldsValue, validate}] = useForm({
        labelWidth: 120,
        wrapperCol: null,
        schemas: formSchema,
        showActionButtonGroup: false,
    });
```

- [ ] **Step 2: 改 `one2` 弹窗模板的 useForm 配置**

`one2` 弹窗模板的 useForm 块与 `one` 完全相同（`labelWidth: 150`），做与 Step 1 **一模一样**的替换：`labelWidth: 150` → `labelWidth: 120`，并在其下新增一行 `wrapperCol: null,`。

- [ ] **Step 3: 验证两处都改到**

Run:
```bash
cd /Users/irvinghua/workspace/javaweb-template
grep -rn "labelWidth: 120\|wrapperCol: null" jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/resources/jeecg/code-template/one/ jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/resources/jeecg/code-template/one2/ --include="*Modal.vuei"
grep -rn "labelWidth: 150" jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/resources/jeecg/code-template/one*/ --include="*Modal.vuei"
```
Expected: 第一条命中 2 个文件、各 2 行（labelWidth: 120 + wrapperCol: null）；第二条**无输出**（150 已全部消失）。

- [ ] **Step 4: 提交**

```bash
cd /Users/irvinghua/workspace/javaweb-template
git add jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/resources/jeecg/code-template/one/ jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/resources/jeecg/code-template/one2/
git commit -m "feat(codegen): 单表弹窗模板表单配置对齐参考页(labelWidth 120 + wrapperCol null)"
```

---

## Task 2: 准备验证环境（配置 + 测试表）

> 需要可用的 MySQL（默认 `jeecg-boot` 库）。环境不可用则本计划阻塞，先解决环境。

**Files:**
- Modify (临时): `jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/resources/jeecg/jeecg_config.properties`
- 确认: `jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/resources/jeecg/jeecg_database.properties`

- [ ] **Step 1: 确认 DB 连接配置指向可用库**

打开 `jeecg_database.properties`，确认 `url` / `username` / `password` 指向一个**可连接、且能建表**的 MySQL（默认 `jdbc:mysql://localhost:3306/jeecg-boot`，root/root）。如本机不同，临时改成本机实际值（记下原值，Task 6 还原）。

- [ ] **Step 2: 备份并临时调整 `jeecg_config.properties`**

```bash
cd /Users/irvinghua/workspace/javaweb-template
cp jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/resources/jeecg/jeecg_config.properties /tmp/jeecg_config.properties.bak
```

把 `project_path` 改成一个临时输出目录（避免污染源码树），`bussi_package` 保持 `org.jeecg.modules.demo`：

```properties
project_path=/tmp/codegen-out
bussi_package=org.jeecg.modules.demo
page_search_filed_num=6
```
（`page_search_filed_num=6` 让生成的搜索区含 6 个字段，便于验证"高级筛选自动折叠"。）

- [ ] **Step 3: 建测试表（含 6 查询字段 + 1 枚举 + 1 时间）**

把下面 SQL 在目标库执行（用你的 MySQL 客户端，或 `mysql -uroot -proot jeecg-boot < /tmp/codegen_test.sql`）：

```sql
DROP TABLE IF EXISTS `codegen_demo`;
CREATE TABLE `codegen_demo` (
  `id` varchar(36) NOT NULL COMMENT '主键',
  `name` varchar(100) DEFAULT NULL COMMENT '名称',
  `code` varchar(50) DEFAULT NULL COMMENT '编码',
  `category` varchar(50) DEFAULT NULL COMMENT '分类',
  `owner` varchar(50) DEFAULT NULL COMMENT '负责人',
  `amount` decimal(12,2) DEFAULT NULL COMMENT '金额',
  `status` varchar(2) DEFAULT NULL COMMENT '状态',
  `start_time` datetime DEFAULT NULL COMMENT '开始时间',
  `create_by` varchar(50) DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  `update_by` varchar(50) DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='代码生成测试表';
```

- [ ] **Step 4: 验证表已建**

Run:
```bash
mysql -uroot -proot jeecg-boot -e "DESC codegen_demo;" 2>/dev/null || echo "请用你的 DB 客户端确认 codegen_demo 表存在"
```
Expected: 列出 12 个字段（含 status、start_time）。

（本任务不 commit：配置/表为临时验证资产。）

---

## Task 3: 基线生成（vue2 仍在）+ 前端核对

**Files:**
- Create (临时): `jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/java/org/jeecg/codegenerate/JeecgOneGenTest.java`

- [ ] **Step 1: 写一次性程序化生成入口**

按从 `codegenerate-1.5.5.jar` 反编译出的 `JeecgOneUtil` 规范写（`generateCodeFile(输出根, 模板classpath根, 风格)`）：

```java
package org.jeecg.codegenerate;

import org.jeecgframework.codegenerate.generate.impl.CodeGenerateOne;
import org.jeecgframework.codegenerate.generate.pojo.TableVo;

/** 一次性：单表代码生成验证入口（验证完删除） */
public class JeecgOneGenTest {
    public static void main(String[] args) throws Exception {
        TableVo tableVo = new TableVo();
        tableVo.setTableName("codegen_demo");
        tableVo.setEntityName("CodegenDemo");
        tableVo.setEntityPackage("codegendemo");
        tableVo.setFtlDescription("代码生成测试");
        tableVo.setPrimaryKeyPolicy("ASSIGN_ID");
        tableVo.setSearchFieldNum(6);
        // 第3参为模板风格目录：one / one2 / onetomany / onetomany2
        new CodeGenerateOne(tableVo).generateCodeFile("/tmp/codegen-out", "/jeecg/code-template", "one");
        System.out.println("=== generate done -> /tmp/codegen-out ===");
    }
}
```

- [ ] **Step 2: 运行生成器（单表风格）**

Run（从 jeecg-system-start 模块跑 main；需依赖在 classpath，用 exec 插件或 IDE）：
```bash
cd /Users/irvinghua/workspace/javaweb-template/jeecg-boot
mvn -q -pl jeecg-module-system/jeecg-system-start -am compile
mvn -q -pl jeecg-module-system/jeecg-system-start exec:java -Dexec.mainClass=org.jeecg.codegenerate.JeecgOneGenTest
```
Expected: 控制台打印 `=== generate done -> /tmp/codegen-out ===`，无异常栈。
> 若 `exec:java` 不可用或缺 display 相关报错：退回 GUI `org.jeecg.codegenerate.JeecgOneGUI`（IDE 里 run main），在界面选 `codegen_demo` + 单表风格 + vue3 生成。

- [ ] **Step 3: 定位生成的 vue3 产物**

Run:
```bash
find /tmp/codegen-out -type f \( -name "*.vue" -o -name "*.data.ts" -o -name "*.api.ts" \) | grep -i vue3
```
Expected: 至少出现 `CodegenDemoList.vue`、`CodegenDemo.data.ts`、`CodegenDemo.api.ts`、`modules/CodegenDemoModal.vue`（同时也会生成 `vue/` 下的 vue2 版本——这正是基线，证明删除前 vue2 仍产出）。

- [ ] **Step 4: 把 vue3 产物放进前端工程**

Run（路径以 Step 3 实际输出为准）：
```bash
mkdir -p /Users/irvinghua/workspace/javaweb-template/jeecgboot-vue3/src/views/codegendemo
# 将 vue3 目录下的 List/data/api/modules 拷过去（示例，按实际 find 结果调整源路径）
cp -r $(find /tmp/codegen-out -type d -name vue3 | head -1)/* /Users/irvinghua/workspace/javaweb-template/jeecgboot-vue3/src/views/codegendemo/
```

- [ ] **Step 5: 临时挂路由访问页面**

在 `jeecgboot-vue3` 起 dev，并通过临时静态路由访问该页（避免改后端菜单）。最简方式：在浏览器地址栏用已有的开发路由直接渲染，或临时在 `src/router/routes/index.ts` 加一条指向 `views/codegendemo/CodegenDemoList.vue` 的路由（记下改动，Task 6 还原）。

Run:
```bash
cd /Users/irvinghua/workspace/javaweb-template/jeecgboot-vue3
pnpm dev
```
Expected: 端口 3100 起服，无编译报错；打开测试页能渲染。

- [ ] **Step 6: 逐项核对新 UI（对照 spec `2026-05-23` 第 4 节）**

人工核对并勾选：
- [ ] 上 card 搜索 + 下 card 表格两段布局，间距 16px
- [ ] 前 2 字段 + 查询/重置/高级筛选 同一行
- [ ] 点高级筛选：行 1 不变 + 行 2 高级字段 + dashed 分隔线；折叠无滞后
- [ ] Select（status 字段）下拉不被剪
- [ ] 表格仅水平线、thead/tbody 无空隙、右侧无滚动条槽空隙
- [ ] 表格右上仅 2 图标（刷新 + 齿轮），密度可切
- [ ] 操作列 ghost 按钮 + ⋯ 更多；"删除"自动红色
- [ ] 新增/编辑弹窗沿用全局 chrome（无错位、无硬塞样式）
- [ ] 工具栏：新增=填充主按钮，导出/导入=ghost（由 btn.less 自动转）

> 若任一项不符：说明 vue3 模板确有残留差异，停下，回到 brainstorming 修订 spec/模板。否则继续。

（本任务不 commit：产物与临时入口都是验证资产。）

---

## Task 4: 删除 vue2 死模板（改动 A）

**Files:**
- Delete: 13 个 `*/vue/**` 模板文件（见下）

- [ ] **Step 1: 删除 vue2 模板文件**

Run:
```bash
cd /Users/irvinghua/workspace/javaweb-template/jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/resources/jeecg/code-template
git rm -r \
  'one/java/${bussiPackage}/${entityPackage}/vue' \
  'one2/java/${bussiPackage}/vue' \
  'onetomany/java/${bussiPackage}/${entityPackage}/vue' \
  'onetomany2/java/${bussiPackage}/${entityPackage}/vue'
```
> 注：`one2` 的 vue2 在 `vue/${entityPackage}/...` 层级，整个 `one2/.../vue` 目录删掉即可。uniapp（`one/.../uniapp`）与全部 `vue3/` 不在删除范围。

- [ ] **Step 2: 验证只删了 vue2、vue3/uniapp 完好**

Run:
```bash
cd /Users/irvinghua/workspace/javaweb-template/jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/resources/jeecg/code-template
echo "剩余 vue2（应为空）:"; find . -path '*/vue/*' -type f
echo "vue3（应仍在，4套）:"; find . -path '*/vue3/*' -name "*List.vuei" | sort
echo "uniapp（应仍在）:"; find . -path '*uniapp*' -type f
```
Expected: 第一行无输出；vue3 列出 4 套 List；uniapp 仍列出文件。

- [ ] **Step 3: 提交**

```bash
cd /Users/irvinghua/workspace/javaweb-template
git add -A jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/resources/jeecg/code-template
git commit -m "chore(codegen): 删除 vue2 死模板(vue3-only 前端用不到，含 labelCol 单key 旧包袱)"
```

---

## Task 5: 删后再跑 + 确认无报错 + 产物不变

- [ ] **Step 1: 清掉上次输出，重跑生成器**

Run:
```bash
rm -rf /tmp/codegen-out
cd /Users/irvinghua/workspace/javaweb-template/jeecg-boot
mvn -q -pl jeecg-module-system/jeecg-system-start exec:java -Dexec.mainClass=org.jeecg.codegenerate.JeecgOneGenTest
```
Expected: 仍打印 `=== generate done ===`，**无 "template not found / FileNotFoundException / 模板缺失" 之类异常**。
> 若报模板缺失异常 → 说明引擎硬依赖 `vue/`。回滚：`git revert` Task 4 的 commit（或 `git checkout` 恢复 vue/ 目录），并在 spec 风险表记录"vue2 不可删"，本计划改为保留 vue2、仅做改动 B。

- [ ] **Step 2: 确认 vue3 产物与基线一致**

Run:
```bash
find /tmp/codegen-out -type f | grep -i vue3 | sort
echo "vue2 产物（删模板后应为空）:"; find /tmp/codegen-out -type d -name vue | head
```
Expected: vue3 文件齐全（List/data/api/Modal）；删模板后不再生成 `vue/` 目录。vue3 内容与 Task 3 Step 3 一致。

- [ ] **Step 3: （可选）抽跑一对多风格确认不报错**

把 `JeecgOneGenTest` 第 3 参 `"one"` 临时改为 `"onetomany"` 重跑一次（一对多需要主子表，若无现成子表可跳过此步，仅记为未覆盖）。Expected: 单表风格已足够证明删除安全；一对多如跑则同样无"模板缺失"异常。

（本任务不 commit：仅验证。）

---

## Task 6: 清理工作区 + 文档收尾

**Files:**
- Delete (临时): `JeecgOneGenTest.java`、`jeecgboot-vue3/src/views/codegendemo/`
- Restore: `jeecg_config.properties`、`jeecg_database.properties`（若改过）、临时路由
- Modify: `docs/superpowers/specs/2026-06-02-codegen-template-cleanup-and-verify-design.md`（追加 JVxeTable 遗留记录）

- [ ] **Step 1: 删除临时入口与生成产物，还原配置**

```bash
cd /Users/irvinghua/workspace/javaweb-template
rm -f jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/java/org/jeecg/codegenerate/JeecgOneGenTest.java
rm -rf jeecgboot-vue3/src/views/codegendemo
cp /tmp/jeecg_config.properties.bak jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/resources/jeecg/jeecg_config.properties
# 若 Task 2 改过 jeecg_database.properties / Task 3 加过临时路由：用 git checkout 还原
git checkout -- jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/resources/jeecg/jeecg_database.properties 2>/dev/null || true
git checkout -- jeecgboot-vue3/src/router 2>/dev/null || true
rm -rf /tmp/codegen-out
```
（测试表 `codegen_demo` 可选 `DROP TABLE codegen_demo;` 清掉。）

- [ ] **Step 2: 确认工作区干净（无验证残留）**

Run:
```bash
cd /Users/irvinghua/workspace/javaweb-template
git status --porcelain
git diff --stat HEAD -- jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/resources/jeecg/jeecg_config.properties
```
Expected: 无 `JeecgOneGenTest.java`、无 `views/codegendemo`、`jeecg_config.properties` 无 diff。

- [ ] **Step 3: 在 spec 追加 JVxeTable 已知遗留记录**

在 `docs/superpowers/specs/2026-06-02-codegen-template-cleanup-and-verify-design.md` 末尾追加：

```markdown
## 8. 验证结论与已知遗留

- 端到端验证：用 `codegen_demo` 测试表按单表风格生成，vue3 产物在新 UI 下逐项核对通过（见 plan Task 3 Step 6 清单）。删除 vue2 模板后重跑，生成器不报"模板缺失"，vue3 产物不变。
- **已知遗留（不修）**：`onetomany`/`onetomany2` 弹窗内的子表用 `JVxeTable`，其内置皮肤 token/全局样式覆盖不全，与新 UI 存在视觉差距。沿用重构主 spec（`2026-05-23`）的处置：做到不崩、视觉基本协调即可，深改另立任务。
```

- [ ] **Step 4: 提交文档**

```bash
cd /Users/irvinghua/workspace/javaweb-template
git add docs/superpowers/specs/2026-06-02-codegen-template-cleanup-and-verify-design.md
git commit -m "docs(codegen): 记录端到端验证结论 + JVxeTable 子表已知遗留"
```

---

## Self-Review 结论

- **Spec 覆盖**：改动 A（Task 4）、改动 B（Task 1）、端到端验证（Task 2/3/5）、删前删后对比（Task 3 基线 vs Task 5）、生成进 jeecgboot-vue3 后 `git checkout` 清理（Task 3 Step 4 + Task 6）、JVxeTable 遗留记录（Task 6 Step 3）——全部有对应任务。
- **占位符**：无 TBD/TODO；测试代码、SQL、命令、模板编辑内容均为实体。
- **类型一致**：`JeecgOneGenTest` 用的 `TableVo` setter（setTableName/setEntityName/setEntityPackage/setFtlDescription/setPrimaryKeyPolicy/setSearchFieldNum）与 `CodeGenerateOne(TableVo).generateCodeFile(String,String,String)` 均来自 jar 实测签名，前后一致。
- **风险回滚**：Task 5 Step 1 写明"删 vue2 致引擎报错"的回滚路径。
```
