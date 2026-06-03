---
name: jeecg-codegen
description: Use when user asks to generate JeecgBoot CRUD code, create a new module, add/modify fields on existing module, or says "代码生成", "生成代码", "创建模块", "新增功能", "建表", "加字段", "加一个字段", "增加字段", "新增字段", "修改字段", "删除字段", "generate code", "new entity", "add field"
disable-model-invocation: true
---

# JeecgBoot 代码生成器（Freemarker 驱动）

把用户的自然语言需求转成 Freemarker 上下文 JSON，交给 `scripts/codegen.py` 调用模板生成全套 CRUD（后端 Java + 前端 Vue3 + 菜单 SQL）。

## 核心原则

> **AI 不再从零写代码。** 基础代码全部由对齐版 code-template（Freemarker）生成，AI 只做三件事：
>
> 1. **拼参数** — 把用户需求映射成 `ctx.json`
> 2. **调脚本** — 跑 `scripts/codegen.py` 让 Freemarker 出基础代码
> 3. **改产物** — 用户提了模板不覆盖的特殊需求时，**用 Edit 改已生成的代码**
>
> ⛔ **禁止**修改 `templates/` 目录下任何模板文件。它们是本工程 `jeecg-boot/.../resources/jeecg/code-template`（团队已对齐新 UI）的副本——要改模板请改那个源，再同步回本 skill，否则会与团队对齐版脱节。
> ⛔ **禁止**绕开脚本直接手写 Entity / Controller / data.ts 等基础文件。

## 主数据复用

涉及字典、角色、用户、部门时遵循"先查后建"，使用 `jeecg-system` skill。详见 `../jeecg-system/SKILL.md`。

## 接口禁止猜测

所有接口路径/参数必须来自用户提供、`jeecg-system` skill 文档、或经查询确认。猜测命中也算违规。

---

## 模板覆盖范围

模板源自本工程 `jeecg-boot/.../resources/jeecg/code-template`（团队已对齐新 UI）。**前端仅 vue3**：

| 表类型 | `--style` | 触发关键词 |
|---|---|---|
| 单表 | `single` | 默认 |
| 一对多 · 平铺子表（JVxeTable） | `onetomany` | 一对多 / 主子表 / 子表录入 |
| 一对多 · Tab（子表独立列表页） | `onetomany-tab` | tab风格 / 标签页子表 |

> 本工程不提供：树表、ERP、内嵌子表（inner-table）、Tab-in-Modal、vue3Native 第二前端风格、uniapp 移动端（仓库未使用，对齐版模板也无）。如有需要需另行补模板。

---

## 交互流程

### Step 0 — 判断操作类型

- 关键词 "加字段 / 删字段 / 改字段 / 给XX加" → **增量修改**（跳到本文末"增量修改"章节）
- 其他 → **全量生成**

### Step 1 — 收集参数（一次性问完）

> ⛔ **铁律：**Step 2 摘要被用户明确确认前，禁止调脚本、禁止落地任何文件、禁止执行任何 SQL。
> "需求很清楚了""都用默认值""先生成再改" 都是合理化跳过确认的借口，全部无效。

向用户一次问全所有缺失项（已知项可填默认值并标注"如无异议保留"）：

| 项 | 默认值 / 提示 |
|---|---|
| **后端模块根** | `<backend_root>`（如 `/Users/irvinghua/workspace/javaweb-template/jeecg-boot/jeecg-module-system/jeecg-system-biz`） |
| **前端项目根** | `<frontend_root>`（如 `/Users/irvinghua/workspace/javaweb-template/jeecgboot-vue3`） |
| **Flyway SQL 目录** | `/Users/irvinghua/workspace/javaweb-template/jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/resources/flyway/sql/mysql` |
| **bussiPackage** | `org.jeecg.modules` |
| **entityPackage** | 由用户给（如 `biz` / `edu`） |
| **entityName / tableName** | 由用户给或推导（如 `BizGoods` / `biz_goods`） |
| **描述（中文）** | 用户业务名（如"商品管理"） |
| **菜单设置** | 菜单名称 / 层级（顶级菜单 还是 挂在某目录下）/ 父菜单。**上下文不明确时禁止擅自决定，必须弹确认项**（见下方"菜单设置"） |
| **表类型 / --style** | `single`（单表）/ `onetomany`（一对多平铺）/ `onetomany-tab`（一对多Tab） |
| **字段清单** | 已有表 → 查 DDL 自动取；新建表 → 由用户描述 |
| **字典字段** | 需要字典的字段：先查 `sys_dict` 定 dict_code，**生成后**再 post-edit 加字典控件（模板不自动出，见下方"字典"） |
| **目标数据库名** | 仅"已有表/字典查询/本地执行 SQL"时需要，必须由用户确认 |

### Step 2 — 展示摘要

把构造好的 `ctx.json` 用**表格**展示给用户：
- 表头：表名、实体名、风格、前端风格、字段数
- 字段表：fieldName / fieldDbName / 注释 / fieldDbType / classType / 字典 / 必填 / 列表显示 / 表单显示 / 查询
- **不要 dump 整个 JSON**，太冗长

明确询问 "是否生成？" — 收到 "确认 / ok / 可以 / 没问题" 等表述后才进入 Step 3。

### Step 3 — 调用脚本

调用前先把构造好的 JSON 写到临时目录（路径规则见下方"临时配置文件规则"），然后用绝对路径调脚本。

**SKILL 路径定位：** 脚本永远在 `<SKILL_ROOT>/scripts/codegen.py`。`<SKILL_ROOT>` 就是包含 `SKILL.md` 的那个目录，比如 `/Users/irvinghua/workspace/javaweb-template/.claude/skills/jeecg-codegen`——你能加载 SKILL.md 就能得出这个路径，**不要再去 Read codegen.py 来确认任何东西**，下面的 CLI 参考就是脚本的完整契约。

#### 完整 CLI 参考

```
python <SKILL_ROOT>/scripts/codegen.py [OPTIONS]
```

| 参数 | 必填 | 默认 | 取值 | 说明 |
|---|:-:|---|---|---|
| `--style` | ✅ | — | `single` `onetomany` `onetomany-tab` | 表类型，见"模板覆盖范围"表 |
| `--ctx` | ✅ | — | 文件路径 | ctx.json 路径，必须在 `{tempdir}/jeecg-codegen/<表名>_ctx.json` |
| `--backend-root` | 🟡 | — | 后端模块根 | 比如 `/Users/irvinghua/workspace/javaweb-template/jeecg-boot/jeecg-module-system/jeecg-system-biz`，脚本会自动拼 `/src/main/java/<bussiPackage>/<entityPackage>/` |
| `--frontend-root` | 🟡 | — | 前端项目根 | 比如 `/Users/irvinghua/workspace/javaweb-template/jeecgboot-vue3`，脚本会自动拼 `/src/views/<entityPackage>/<实体名小写>/` |
| `--flyway-dir` | 🟡 | — | Flyway SQL 目录 | 菜单 SQL 落到这里；同名 SQL 自动去重 |
| `--out` | ❌ | — | 任意目录 | 调试用：渲染产物原样落到此目录，**跳过分发**。设了它就不需要 backend/frontend/flyway-root |
| `--dry-run` | ❌ | `false` | flag | 打印分发计划但不写文件 |

> 🟡 = 在没有 `--out` 的"正常模式"下，至少要传 `--backend-root` 或 `--frontend-root` 或 `--flyway-dir` 之一（任何没传的目录类型对应的产物都被跳过）；正常代码生成场景三个都该传。
>
> ✅ = 任何模式都必填。

#### 退出码 & 输出

- 退出码 `0` = 成功；其他都失败（参数非法、Java 编译失败、Freemarker 渲染异常）
- 标准输出每行一个事件：`[codegen] WROTE <绝对路径>`、`[codegen] WOULD WRITE ...`（dry-run 时）、`[codegen] running FtlRunner …` 等
- 失败时 stderr 含完整 Java 栈或 `[codegen] xxx` 错误信息

#### 典型调用（**复制后改 `--style` 与 `--ctx` 即可，三个 root 本工程固定**）

```bash
python /Users/irvinghua/workspace/javaweb-template/.claude/skills/jeecg-codegen/scripts/codegen.py \
  --style single \
  --ctx "$TMPDIR/jeecg-codegen/biz_goods_ctx.json" \
  --backend-root /Users/irvinghua/workspace/javaweb-template/jeecg-boot/jeecg-module-system/jeecg-system-biz \
  --frontend-root /Users/irvinghua/workspace/javaweb-template/jeecgboot-vue3 \
  --flyway-dir /Users/irvinghua/workspace/javaweb-template/jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/resources/flyway/sql/mysql
```

## 临时配置文件规则（强制）

所有传给脚本的 `--ctx <xxx.json>` 必须写到 **`{系统临时目录}/jeecg-codegen/`** 下，由操作系统自动清理；skill 与脚本均不主动删除该目录或文件。

```python
import tempfile, os, json

SKILL_NAME = "jeecg-codegen"
skill_dir = os.path.join(tempfile.gettempdir(), SKILL_NAME)
os.makedirs(skill_dir, exist_ok=True)          # 确保目录存在，不主动检查

config_path = os.path.join(skill_dir, 'biz_goods_ctx.json')   # 示例文件名：<表名>_ctx.json
with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(cfg, f, ensure_ascii=False, indent=2)
```

`tempfile.gettempdir()` 自动适配：Windows `%TEMP%`、Linux `/tmp`、macOS `/var/folders/.../T`（注意 macOS 并非 `/tmp`）。
文件名建议使用 **`<表名>_<步骤>.json`**（如 `biz_goods_ctx.json` / `biz_goods_alter.json`），无需重复技能前缀，因路径已包含技能名称，便于排错。

**❌ 禁止：**

- 写到 `<skill>/tmp/` 或当前工作目录（污染 skill / 用户项目）
- 硬编码 `/tmp`、`C:\Temp` 或任何固定路径（不跨平台）
- 每步完成后主动 `rm` / `Remove-Item`（操作系统会清理，属多余 tool call）
- 主动 `os.path.exists()` 检查（其本身即为一次 tool call）
  （使用 `os.makedirs(…, exist_ok=True)` 满足需求，不算主动检查）

**临时文件可能被操作系统异步清理**，但仍遵循 **乐观调用 + 报错补救**：仅当脚本返回 `FileNotFoundError` 或 `配置文件不存在` 时，使用相同内容、**在相同的 `{系统临时目录}/jeecg-codegen/` 路径下重写**（重写前仍需 `os.makedirs(skill_dir, exist_ok=True)` 确保目录存在），切勿更换路径或回退至 skill 目录。

### Step 4 — 处理特殊需求（模板没覆盖的部分）

用户的需求经常超出模板能力（比如"商品名要带前缀生成""价格变更后自动算总价""列表行加复制按钮"），这时：

1. 先跑脚本生成基础代码
2. 再用 Read 读出对应文件、用 Edit 做精细修改
3. **不要改 templates/，永远改产物**

常见的特殊需求与改动位置参考 `references/post-edit-recipes.md`。

### Step 5 — 后续操作

- **Flyway SQL**：脚本已落到 `<flyway-dir>/V<date>_1__menu_insert_<entity>.sql`，重启后端时 Flyway 自动执行；如果用户要求立即生效，按"本地自动执行 SQL"流程做（见下方）。
- **重启后端**：提示用户 `mvn spring-boot:run -pl jeecg-module-system/jeecg-system-start`
- **前端热更新**：`pnpm dev` 自动热更，无需重启
- **菜单**：见下方"菜单设置"——菜单名称/层级不明确时**必须先弹确认项**；手工建"目录+子页"有字段避坑规则；**改完菜单要重新登录**才生效。

---

## 字段语义推导

新建表时，AI 需要把用户描述的字段（如"价格"、"备注"）映射到合适的 `classType` / `fieldDbType` / `fieldType`。映射表见 `references/field-mapping.md`。

已有表场景下，从 DDL 直接读类型，不依赖语义推导。

## 已有表反向生成

用户给了表名 → 必须先查数据库取 DDL 再构造 ctx：

```bash
# 询问用户目标数据库名后，一条命令拿全部信息
mysql --no-defaults --default-character-set=utf8mb4 -h127.0.0.1 -P3306 -u<user> -p<password> {dbname} \
  -e "SHOW CREATE TABLE 表名\G" \
  -e "SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT, COLUMN_COMMENT, COLUMN_KEY, EXTRA FROM information_schema.COLUMNS WHERE TABLE_SCHEMA='{dbname}' AND TABLE_NAME='表名' ORDER BY ORDINAL_POSITION"
```

> ⛔ 执行任何 SQL 前必须先询问用户目标数据库名，**不要从 application-dev.yml 自动取**——用户本机可能多库并存。

## 字典（生成后 post-edit，模板不自动出）

> ⚠️ 对齐版模板**不会**根据 ctx 自动渲染字典控件——生成的 `.data.ts` 只按 `fieldType` 选 Input/InputNumber/DatePicker。字典是**生成基础代码之后**的人工增强步骤。

流程：先查 `sys_dict` 判定每个字段该用哪个 `dict_code`（优先级：用户明确指定 > 字段名等于 dict_code > 注释关键词命中 dict_name > 不匹配），**生成代码后**再用 Edit 把对应列改成 `customRender: ({text}) => render.renderDict(text,'<code>')`、把查询/表单项 `component` 改成 `JDictSelectTag` + `componentProps.dictCode`。

完整写法（含表字典、多选、`@Dict` 后端回填）见 `references/dict-matching.md`。

## 菜单设置（务必先确认 + 避坑指南）

### 0. 确认规则（强制）

如果**没有非常明确的上下文**说明本模块的：①菜单名称、②菜单层级（顶级菜单 / 挂在某目录下）、③层级具体设置（父菜单是谁）——**禁止擅自决定**，必须向用户弹确认项（用 `AskUserQuestion` 或等价方式），至少给两个选项：

- **(A) 你的建议方案（标注"推荐"）**：基于模块描述给一个具体方案，例如「顶级菜单，名称『商品管理』」或「在『XX』目录下新建子菜单『商品管理』」。
- **(B) 用户自行输入**：让用户给菜单名称 / 层级 / 父菜单。

确认后才建菜单。**不要默认顶级、也不要默认挂某处**。

### 1. 两种形态

- **顶级页面菜单（脚本默认）**：生成的 `menu_insert.ftl` SQL 建的就是顶级菜单（`menu_type=0` + 页面 component），登录后直接在一级区可见，开箱即用。
- **挂到某目录下（一级目录 ▸ 二级页面）**：脚本**不生成**，需手工插 `sys_permission`，按下方字段规则——**这里最容易踩坑**。

### 2. 手工建「一级目录 ▸ 二级页面」的正确字段（血泪避坑）

**一级目录行：**
- `parent_id = ''`（**空字符串，不是 NULL**；本工程顶级菜单都用空串）
- `url = '/路由前缀'`（如 `/wms`）
- `component = 'layouts/RouteView'`（目录固定用它；本工程里 `layouts/RouteView`、`layouts/default/index` **不对应真实文件**，由路由层特殊处理，照抄即可）
- `menu_type=0`、`is_route=1`、`is_leaf=0`、`perms_type='0'`、`status=1`、`del_flag=0`
- ⚠️ **`always_show=0`**：单个子菜单时若设 `1`，会命中 jeecg 路由提升边界 → **子菜单不渲染、点目录右侧报"查看组件引用是否正确"**（本次踩坑根因，定位很久）。务必 `0`。
- `redirect = 子页面的 url`：让点目录直接落到子页，避免空 RouteView 报错。

**二级页面行：**
- `parent_id = 一级目录的 id`
- `url = 唯一路由路径`（如 `/wms/bizGoodsList`；**不必**嵌在父 url 下）
- `component = '前端目录/模块名小写/实体List'`（如 `biz/bizGoods/BizGoodsList`，相对 `src/views`、**不带 `.vue`**；路由层按 glob 匹配文件，非 index 页也能匹配）
- ⚠️ `component_name = 生成页面 .vue 里 name="xxx" 的值`（如 `biz-bizGoods`；缺了 keep-alive 路由名对不上）
- `menu_type=1`、`is_route=1`、`is_leaf=1`、`icon='ant-design:...'`

**授权**：给 admin 角色（`role_id='f6817f48af4fb3af11b9e8bf182f618b'`）插 `sys_role_permission`，目录 + 页面各一条。

**id**：用唯一字符串（19 位数字，避开现有 id 段）；插入前 `SELECT` 校验不冲突。

### 3. ⚠️ 改完菜单必须重新登录

菜单和路由是**登录时一次性构建**的。直接改 `sys_permission` 后，提示用户**退出再重新登录**（仅 F5 刷新可能看到旧构建，造成"改了没效果"的假象）。

### 4. 本地执行 SQL（仅 127.0.0.1 / localhost，用户确认目标库后）

```bash
# 顶级菜单：先查重再执行脚本生成的 Flyway SQL
mysql ... -e "SELECT id FROM sys_permission WHERE name='<描述>' AND (parent_id IS NULL OR parent_id='')"
mysql ... < <flyway_sql_file_path>
```

> 若改用"挂目录"形态，**不要**再让 Flyway 执行那份顶级菜单 SQL（会重复插一条顶级菜单）——删掉生成的 `V*menu_insert*.sql`，改用上面手工的目录+子页 SQL 直连执行。执行失败只提示、不中断。

---

## 增量修改（加 / 删 / 改字段）

> 所有"模板已生成的代码 + 用户后续小调整"都走 Edit，不重新跑脚本。

### Step A — 定位文件

```bash
# Entity
find <backend_root>/src/main/java -name "<EntityName>.java"
# 前端 data.ts
find <frontend_root>/src/views -name "<EntityName>.data.ts"
```

需要读：`Entity.java` / `*.data.ts` / `*List.vue` / `modules/*Modal.vue`（一对多还含各子表 `*.java` 与子表 `*List.vue`）。

### Step B — 推导新字段属性

参考 `references/field-mapping.md`。

### Step C — 展示摘要 → 等用户确认 → 执行 Edit

加字段：在所有相关文件追加；删字段：精确删除；改字段：定位修改。
ALTER TABLE 写到新的 Flyway SQL（版本号递增）。

> 不要因为"加一个字段"就重新跑全量代码生成，会覆盖用户对生成结果的手工修改。

---

## 文件夹与脚本

| 路径 | 说明 |
|---|---|
| `templates/` | 对齐版 code-template 副本（**只读**，源在 `jeecg/code-template`）|
| `lib/` | freemarker.jar + fastjson2.jar |
| `scripts/codegen.py` | 主入口（Python3）|
| `scripts/FtlRunner.java` | Java 渲染器（首次运行自动 javac）|
| `scripts/.cache/` | 编译产物 + 临时 ctx |
| `references/field-mapping.md` | 字段语义 → Freemarker 字段映射 |
| `references/context-schema.md` | ctx.json 完整 schema |
| `references/post-edit-recipes.md` | 模板没覆盖的特殊需求改动位置 |
| `references/dict-matching.md` | 字典匹配规则与 ctx 映射 |

依赖：`java`（JDK 8+）+ `python3`（3.9+，类型注解用了 PEP 585 语法）。脚本会自动探测 javac 版本：JDK 8 用 `-source 8 -target 8`，JDK 9+ 用 `--release 8`，最终编译产物始终为 Java 8 字节码（major=52）。
