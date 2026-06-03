JavaWeb CRUD 脚手架（基于 JeecgBoot 裁剪 + UI 重构）
===============

[![License](https://img.shields.io/badge/license-Apache%20License%202.0-blue.svg)](./LICENSE)

> 本工程基于开源 [JeecgBoot](https://github.com/jeecgboot/JeecgBoot) 3.9.1 **裁剪**而来，并对前端 UI 做了重构。
> 定位：**fork-and-forget 的 ToB CRUD 脚手架** —— 只保留权限/组织/字典等系统底座 + 代码生成能力，让工程更轻、更可控。

- **后端** `jeecg-boot/`：Spring Boot 3 + MyBatis-Plus + Shiro + MySQL
- **前端** `jeecgboot-vue3/`：Vue3 + Vite6 + Ant Design Vue4 + TypeScript（UI 已重构，见 `jeecgboot-vue3/design.md`）
- **代码生成器** `skills/jeecg-codegen/`：本工程自带的 CRUD 代码生成 skill（见下方"代码生成器使用说明"）

---

## 支持功能

**保留并可用**：系统管理（用户 / 角色 / 菜单 / 部门 / 字典 / 分类字典 / 职务 / 公告 / 租户 / 多数据源 / 定时任务）、系统监控、消息中心、**代码生成器（jeecg-codegen）**、通用前端组件、Flowable 工作流底座。

---

## 技术栈

**前端**
- Node 20+ / pnpm 9+
- Vue3 + TypeScript + Vite6 + Ant Design Vue4 + Pinia + vxe-table + ECharts + UnoCSS

**后端**
- JDK 17（兼容 21/24），Maven 多模块
- Spring Boot 3 + MyBatis-Plus 3.5 + Apache Shiro 2 + JWT
- Druid 连接池 + Redis 缓存 + Quartz + Lombok
- 默认提供 MySQL 5.7+ 脚本（`jeecg-boot/db/`）

**数据库支持**：MySQL（默认）、Oracle、SQL Server、PostgreSQL、MariaDB、达梦、人大金仓、TiDB、KingBase8。

---

## 启动项目

> 默认账号密码：`admin / 123456`

1. **数据库**：MySQL 5.7+，导入 `jeecg-boot/db/jeecgboot-mysql-5.7.sql`；后端 `application-dev.yml` 配置数据源（默认库 `jeecg-boot`）。Redis 需启动。
2. **后端**：`mvn -pl jeecg-module-system/jeecg-system-start -am spring-boot:run`（首次可先 `mvn ... -am install -DskipTests`）。默认端口 8080，contextPath `/jeecg-boot`。
3. **前端**：`cd jeecgboot-vue3 && pnpm install && pnpm dev`。默认端口 3100，代理后端 `localhost:8080/jeecg-boot`。

---

## 功能清单

```
├─系统管理
│  ├─用户管理 / 角色管理 / 菜单管理（含按钮权限、数据权限）
│  ├─部门管理 / 我的部门（二级管理员）/ 职务管理
│  ├─字典管理 / 分类字典 / 系统公告
│  ├─多数据源管理 / 第三方配置（钉钉、企业微信）
│  └─多租户管理（租户 / 租户角色 / 我的租户 / 套餐）
├─代码生成器（jeecg-codegen）
│  ├─单表 / 一对多（平铺·JVxeTable）/ 一对多（Tab）
│  └─后端 Java + 前端 Vue3 + 菜单 SQL 一键生成
├─系统监控
│  ├─定时任务 / 数据源 / 在线用户 / 系统日志 / SQL 监控
│  └─性能监控（Redis / Tomcat / JVM / 服务器 / 请求追踪）
├─消息中心
│  └─消息管理 / 模板管理（短信、邮件、微信推送、WebSocket）
└─通用组件
   └─表格 / 高级查询 / 字典组件 / 选人·选部门 / 上传 / 富文本 等
```

---

## 代码生成器使用说明（jeecg-codegen）

本工程**自带**一套代码生成 skill：把自然语言需求 → 上下文 JSON → FreeMarker 渲染**已对齐本工程 UI** 的模板 → 生成全套 CRUD（后端 Java + 前端 Vue3 + 菜单 SQL），支持单表 / 一对多（平铺 / Tab）。

### 位置与依赖

| 项 | 值 |
|---|---|
| 工程内副本（可纳入 git） | `skills/jeecg-codegen/` |
| Claude Code 加载位置 | `.claude/skills/jeecg-codegen/` |
| 运行依赖 | `java`（JDK 8+）+ `python3`（3.9+） |
| 引擎 | `scripts/codegen.py`（编排）+ `scripts/FtlRunner.java`（FreeMarker 渲染）+ `templates/`（对齐模板）+ `references/`（字段/字典/ctx/post-edit 规则） |

> ⚠️ skill 是 git 外的本地深度定制，工程内 `skills/jeecg-codegen/` 为其可追溯副本。详见 `SKILL.md`。

### 三平台使用方式

skill 的核心是**平台无关**的：`SKILL.md`（工作流规则）+ `codegen.py`（生成引擎）。**任何能读文件、跑 python/java 的 AI 编码助手都能用**——差别只在"怎么让它加载 SKILL.md"。

#### ① Claude Code（原生支持 skill）

1. 确保 `.claude/skills/jeecg-codegen/` 存在（本工程已自带；如缺，从 `skills/jeecg-codegen/` 复制过去）。
2. 直接对话，**显式点名 skill**（它设了 `disable-model-invocation`，需手动触发）：
   > 用 jeecg-codegen 创建一个商品管理模块，字段：商品名称(必填)、价格(金额)、状态(开关)、描述(富文本)。
3. Claude 按 `SKILL.md` 流程执行：收集参数 → 展示摘要**等你确认** → 调 `codegen.py` 生成 → post-edit 特殊控件 → 建菜单 → 启动验证。

#### ② Codex（OpenAI Codex CLI）

Codex 无原生 skill 加载器，用「**读 SKILL.md + 跑脚本**」的方式：

1. 在项目根 `AGENTS.md` 加一行指引（或直接写进 prompt）：
   > 需要生成 CRUD 模块时，先读 `skills/jeecg-codegen/SKILL.md` 并严格按其流程执行。
2. 对话：
   > 读 `skills/jeecg-codegen/SKILL.md`，按它给我创建一个商品管理模块，字段：…
3. Codex 读规则后构造 `ctx.json`、运行 `python skills/jeecg-codegen/scripts/codegen.py ...`，再按 `references/` 做 post-edit。

#### ③ OpenCode

同 Codex（无原生 Claude-skill 加载器）：

1. 在 `AGENTS.md` 或 OpenCode 配置中指引读 `skills/jeecg-codegen/SKILL.md`；也可把"读 SKILL.md 生成模块"封装成 OpenCode 的自定义 command/agent。
2. 对话让其读 `SKILL.md` 并执行，过程同上。

### 命令行直跑（不经 AI，给熟手）

skill 本质是个 CLI 工具，可绕过 AI 直接调用引擎：

```bash
python skills/jeecg-codegen/scripts/codegen.py \
  --style single \
  --ctx "$TMPDIR/jeecg-codegen/biz_goods_ctx.json" \
  --backend-root  <repo>/jeecg-boot/jeecg-module-system/jeecg-system-biz \
  --frontend-root <repo>/jeecgboot-vue3 \
  --flyway-dir    <repo>/jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/resources/flyway/sql/mysql
```

- `--style`：`single`（单表）/ `onetomany`（一对多平铺）/ `onetomany-tab`（一对多Tab）
- `--ctx`：上下文 JSON，schema 见 `skills/jeecg-codegen/references/context-schema.md`
- 调试可用 `--out <dir>` 只渲染不分发、`--dry-run` 只打印计划

### 注意事项（避坑，完整版见 SKILL.md）

- **特殊控件需 post-edit**：对齐模板只按 `fieldType` 出基础控件（Input / InputNumber / DatePicker）；字典下拉、图片上传、开关、富文本等**生成后**再改产物 `.data.ts`（见 `references/dict-matching.md`、`post-edit-recipes.md`）。
- **菜单**：名称/层级不明确时**必须先确认**；手工建「目录 + 子页」两级菜单有字段规则（目录 `always_show=0` + `redirect`、子页 `component_name` 等），**改完菜单必须重新登录**才生效。
- **建表**：生成器逆向读已存在表的字段，**不建表**；新表需先写 DDL 建好。

---

## 免责声明

本工程基于 [JeecgBoot](https://github.com/jeecgboot/JeecgBoot) 二次裁剪，遵循 [Apache License 2.0](./LICENSE) 开源协议。凡下载、复制、安装或以任何方式使用本软件的行为，即视为已阅读、理解并同意上述协议。
