# jeecg-codegen 生成器重建 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 删除 skill 自带的 scripts/templates，改用本工程对齐版 `code-template` 重建一套等价的 JeecgBoot CRUD 代码生成器。

**Architecture:** 两层——`FtlRunner.java`（模板无关的 Java FreeMarker 渲染器，功能等价复刻）+ `codegen.py`（编排层，重写：新风格映射、按 code-template 审计字段喂 ctx、分发到本工程目录、保留菜单 SQL）。templates 为 code-template 的 one/onetomany/onetomany2 三套副本 + 移植的菜单 SQL。

**Tech Stack:** Python 3.9+、Java 8+（javac/java）、FreeMarker 2.3.32、fastjson2。

> **环境约定**
> - SKILL 根：`/Users/irvinghua/workspace/javaweb-template/.claude/skills/jeecg-codegen`（下称 `<SKILL>`）
> - 对齐版模板源：`/Users/irvinghua/workspace/javaweb-template/jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/resources/jeecg/code-template`（下称 `<CT>`）
> - `.claude/` 不在 git 跟踪内 → 每个 Task 末尾用**验证检查点**代替 commit；不要对 skill 文件跑 git。
> - 保留不动：`<SKILL>/lib/`、`<SKILL>/references/`（Task 7 才动）、`<SKILL>/SKILL.md`（Task 6 才动）。

---

## File Structure

| 文件 | 职责 |
|---|---|
| `<SKILL>/scripts/FtlRunner.java` | Java FreeMarker 渲染器：读 ctx → 渲染风格目录 → `[1-n]` 切分 → 还原后缀落盘 |
| `<SKILL>/scripts/codegen.py` | 编排：CLI、normalize_ctx、编译/调用 FtlRunner、分发到工程目录 |
| `<SKILL>/scripts/tests/test_codegen.py` | codegen.py 纯函数单测（normalize_ctx + 路径分类） |
| `<SKILL>/templates/one/…` | 单表模板（copy 自 `<CT>/one`，去 uniapp）+ 菜单 SQL stub |
| `<SKILL>/templates/onetomany/…` | 一对多平铺（copy 自 `<CT>/onetomany`）+ 菜单 SQL stub |
| `<SKILL>/templates/onetomany2/…` | 一对多Tab（copy 自 `<CT>/onetomany2`）+ 菜单 SQL stub |
| `<SKILL>/templates/common/sql/menu_insert.ftl` | 菜单 SQL 公共片段（移植，含授权 admin） |
| `<SKILL>/SKILL.md` | 文档：范围表/CLI/示例同步为真实能力 |
| `<SKILL>/references/dict-matching.md` | 字典匹配规则（按 code-template 实际行为核对调整） |

---

## Task 1: 清空旧 scripts/templates（留白）

**Files:**
- Delete: `<SKILL>/scripts/codegen.py`、`<SKILL>/scripts/FtlRunner.java`、`<SKILL>/scripts/.cache/*`、`<SKILL>/templates/`（整目录）

- [ ] **Step 1: 先确认要保留的目录还在**

Run:
```bash
ls /Users/irvinghua/workspace/javaweb-template/.claude/skills/jeecg-codegen
```
Expected: 看到 `lib  references  scripts  templates  SKILL.md`。

- [ ] **Step 2: 删除旧脚本与旧模板**

```bash
SKILL=/Users/irvinghua/workspace/javaweb-template/.claude/skills/jeecg-codegen
rm -f "$SKILL/scripts/codegen.py" "$SKILL/scripts/FtlRunner.java"
rm -rf "$SKILL/scripts/.cache" "$SKILL/templates"
mkdir -p "$SKILL/templates" "$SKILL/scripts/tests"
```

- [ ] **Step 3: 验证留白结果**

Run:
```bash
ls -R /Users/irvinghua/workspace/javaweb-template/.claude/skills/jeecg-codegen/scripts; ls /Users/irvinghua/workspace/javaweb-template/.claude/skills/jeecg-codegen/templates
```
Expected: `scripts/` 下只剩 `tests/`（空）；`templates/` 为空。`lib/`、`references/`、`SKILL.md` 仍在。

---

## Task 2: 复刻 FtlRunner.java（模板无关渲染器）

**Files:**
- Create: `<SKILL>/scripts/FtlRunner.java`

- [ ] **Step 1: 写入 FtlRunner.java（完整内容）**

文件 `/Users/irvinghua/workspace/javaweb-template/.claude/skills/jeecg-codegen/scripts/FtlRunner.java`：

```java
import com.alibaba.fastjson2.JSON;
import com.alibaba.fastjson2.JSONReader;
import freemarker.core.TemplateClassResolver;
import freemarker.template.Configuration;
import freemarker.template.Template;
import freemarker.template.TemplateExceptionHandler;

import java.io.IOException;
import java.io.StringWriter;
import java.io.Writer;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.regex.*;
import java.util.stream.Collectors;

public class FtlRunner {

    private static final Pattern VAR_RE = Pattern.compile("\\$\\{([a-zA-Z_][a-zA-Z0-9_]*)\\}");
    private static final Pattern SUB_RE = Pattern.compile("\\[1-n\\]");
    private static final String SEGMENT_PREFIX = "#segment#";

    public static void main(String[] args) throws Exception {
        if (args.length < 4) {
            System.err.println("Usage: FtlRunner <templateRoot> <stylePath> <ctxJson> <outputDir>");
            System.exit(2);
        }
        Path templateRoot = Paths.get(args[0]).toAbsolutePath();
        String stylePath = args[1].replace("\\", "/");
        Path ctxJson = Paths.get(args[2]).toAbsolutePath();
        Path outputDir = Paths.get(args[3]).toAbsolutePath();

        String ctxText = new String(Files.readAllBytes(ctxJson), StandardCharsets.UTF_8);
        Map<String, Object> rootCtx = JSON.parseObject(ctxText, Map.class, JSONReader.Feature.UseBigDecimalForDoubles);
        rootCtx.put("Format", new FormatTool());

        Configuration cfg = new Configuration(Configuration.VERSION_2_3_28);
        cfg.setNumberFormat("0.#####################");
        cfg.setDirectoryForTemplateLoading(templateRoot.toFile());
        cfg.setDefaultEncoding("UTF-8");
        cfg.setTemplateExceptionHandler(TemplateExceptionHandler.RETHROW_HANDLER);
        cfg.setNewBuiltinClassResolver(TemplateClassResolver.SAFER_RESOLVER);

        Path styleRoot = templateRoot.resolve(stylePath);
        if (!Files.isDirectory(styleRoot)) {
            throw new RuntimeException("stylePath not found: " + styleRoot);
        }

        Files.createDirectories(outputDir);
        List<String> generated = new ArrayList<>();

        try (java.util.stream.Stream<Path> walk = Files.walk(styleRoot)) {
            List<Path> files = walk.filter(Files::isRegularFile).collect(Collectors.toList());
            for (Path tpl : files) {
                String relFromRoot = templateRoot.relativize(tpl).toString().replace("\\", "/");
                String relFromStyle = styleRoot.relativize(tpl).toString().replace("\\", "/");
                String outRel = expandPath(relFromStyle, rootCtx);
                Path outFile = outputDir.resolve(outRel);
                renderOne(cfg, relFromRoot, rootCtx, outFile, generated);
            }
        }

        for (String g : generated) System.out.println("WROTE " + g);
        System.out.println("DONE " + generated.size() + " files -> " + outputDir);
    }

    private static void renderOne(Configuration cfg, String tplRel, Map<String, Object> ctx, Path outFile, List<String> generated) throws Exception {
        Template t = cfg.getTemplate(tplRel, "UTF-8");
        StringWriter sw = new StringWriter();
        t.process(ctx, sw);
        String content = sw.toString();

        boolean isSegmented = SUB_RE.matcher(outFile.toString()).find();
        if (isSegmented) {
            splitAndWriteSegments(content, outFile, generated);
        } else {
            Path finalOut = adjustOutputPath(outFile);
            Files.createDirectories(finalOut.getParent());
            Files.write(finalOut, content.getBytes(StandardCharsets.UTF_8));
            generated.add(finalOut.toString());
        }
    }

    private static void splitAndWriteSegments(String content, Path outFile, List<String> generated) throws IOException {
        Path parent = adjustOutputPath(outFile).getParent();
        Files.createDirectories(parent);
        String[] lines = content.split("\\r?\\n", -1);
        Writer cur = null;
        try {
            for (String line : lines) {
                if (line.trim().length() > 0 && line.startsWith(SEGMENT_PREFIX)) {
                    if (cur != null) cur.close();
                    String segName = line.substring(SEGMENT_PREFIX.length()).trim();
                    Path curPath = parent.resolve(segName);
                    Files.createDirectories(curPath.getParent());
                    cur = Files.newBufferedWriter(curPath, StandardCharsets.UTF_8);
                    generated.add(curPath.toString());
                } else if (cur != null) {
                    cur.write(line);
                    cur.write("\r\n");
                }
            }
        } finally {
            if (cur != null) cur.close();
        }
    }

    private static Path adjustOutputPath(Path p) {
        String name = p.getFileName().toString();
        String fixed = name;
        if (name.endsWith(".javai")) fixed = name.substring(0, name.length() - 6) + ".java";
        else if (name.endsWith(".vuei")) fixed = name.substring(0, name.length() - 5) + ".vue";
        else if (name.endsWith(".tsi"))  fixed = name.substring(0, name.length() - 4) + ".ts";
        return p.resolveSibling(fixed);
    }

    private static String expandPath(String path, Map<String, Object> ctx) {
        Matcher m = VAR_RE.matcher(path);
        StringBuffer sb = new StringBuffer();
        while (m.find()) {
            String key = m.group(1);
            Object v = ctx.get(key);
            String s = (v == null) ? "" : v.toString();
            if ("bussiPackage".equals(key) || "entityPackage".equals(key) || "parentPackage".equals(key)) {
                s = s.replace('.', '/');
            }
            m.appendReplacement(sb, Matcher.quoteReplacement(s));
        }
        m.appendTail(sb);
        return sb.toString();
    }

    public static class FormatTool {
        public String humpToUnderline(String para) {
            if (para == null) return null;
            StringBuilder sb = new StringBuilder(para);
            int offset = 0;
            if (!para.contains("_")) {
                for (int i = 0; i < para.length(); i++) {
                    if (Character.isUpperCase(para.charAt(i))) { sb.insert(i + offset, "_"); offset++; }
                }
            }
            String r = sb.toString().toLowerCase();
            return r.startsWith("_") ? r.substring(1) : r;
        }
        public String humpToShortbar(String para) {
            if (para == null) return null;
            StringBuilder sb = new StringBuilder(para);
            int offset = 0;
            if (!para.contains("-")) {
                for (int i = 0; i < para.length(); i++) {
                    if (Character.isUpperCase(para.charAt(i))) { sb.insert(i + offset, "-"); offset++; }
                }
            }
            String r = sb.toString().toLowerCase();
            return r.startsWith("-") ? r.substring(1) : r;
        }
        public String underlineToHump(String para) {
            if (para == null) return null;
            StringBuilder sb = new StringBuilder();
            for (String part : para.split("_")) {
                if (!para.contains("_")) sb.append(part);
                else if (sb.length() == 0) sb.append(part.toLowerCase());
                else if (part.length() > 0) { sb.append(part.substring(0,1).toUpperCase()); sb.append(part.substring(1).toLowerCase()); }
            }
            return sb.toString();
        }
    }
}
```

- [ ] **Step 2: 验证可独立编译为 Java 8 字节码**

Run:
```bash
SKILL=/Users/irvinghua/workspace/javaweb-template/.claude/skills/jeecg-codegen
mkdir -p "$SKILL/scripts/.cache"
javac -encoding UTF-8 --release 8 -cp "$SKILL/lib/freemarker-2.3.32.jar:$SKILL/lib/fastjson2.jar" -d "$SKILL/scripts/.cache" "$SKILL/scripts/FtlRunner.java"
echo "exit=$?"
```
Expected: `exit=0`，`.cache/FtlRunner.class` 生成（若本机 JDK 为 8，将 `--release 8` 换成 `-source 8 -target 8`；codegen.py 会自动探测，这里只是手验）。

- [ ] **Step 3: 检查点**

Run: `ls -la /Users/irvinghua/workspace/javaweb-template/.claude/skills/jeecg-codegen/scripts/.cache/FtlRunner.class`
Expected: 文件存在。FtlRunner 渲染契约就绪。

---

## Task 3: 复制对齐版模板（one/onetomany/onetomany2，去 uniapp）

**Files:**
- Create: `<SKILL>/templates/one/`、`<SKILL>/templates/onetomany/`、`<SKILL>/templates/onetomany2/`

- [ ] **Step 1: 拷贝三套风格目录**

```bash
SKILL=/Users/irvinghua/workspace/javaweb-template/.claude/skills/jeecg-codegen
CT=/Users/irvinghua/workspace/javaweb-template/jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/resources/jeecg/code-template
for s in one onetomany onetomany2; do cp -R "$CT/$s" "$SKILL/templates/$s"; done
```

- [ ] **Step 2: 删除 uniapp 产物（本仓库无移动端）**

```bash
SKILL=/Users/irvinghua/workspace/javaweb-template/.claude/skills/jeecg-codegen
find "$SKILL/templates" -type d -name uniapp -prune -exec rm -rf {} +
find "$SKILL/templates" -type d -name 'uniapp3' -prune -exec rm -rf {} +
```

- [ ] **Step 3: 验证目录与子表切分约定**

Run:
```bash
SKILL=/Users/irvinghua/workspace/javaweb-template/.claude/skills/jeecg-codegen
echo "--- 风格目录 ---"; ls "$SKILL/templates"
echo "--- 残留 uniapp? ---"; find "$SKILL/templates" -iname '*uniapp*' | head
echo "--- [1-n] 切分标记存在? ---"; grep -rl '#segment#' "$SKILL/templates/onetomany" | head
```
Expected: 风格目录为 `one onetomany onetomany2`；无 uniapp 残留；onetomany 下能搜到 `#segment#`（确认与 FtlRunner 约定一致）。

---

## Task 4: 移植菜单 SQL 模板 + 每风格 stub

**Files:**
- Create: `<SKILL>/templates/common/sql/menu_insert.ftl`
- Create: `<SKILL>/templates/one/java/${bussiPackage}/${entityPackage}/vue3/V${currentDate}_1__menu_insert_${entityName}.sql`
- Create: `<SKILL>/templates/onetomany/java/${bussiPackage}/${entityPackage}/vue3/V${currentDate}_1__menu_insert_${entityName}.sql`
- Create: `<SKILL>/templates/onetomany2/java/${bussiPackage}/${entityPackage}/vue3/V${currentDate}_1__menu_insert_${entityName}.sql`

- [ ] **Step 1: 写公共片段 `templates/common/sql/menu_insert.ftl`（完整内容）**

```
-- 注意：该页面对应的前台目录为views/${entityPackagePath}文件夹下
-- 如果你想更改到其他目录，请修改sql中component字段对应的值

<#assign mainId = "${.now?long}01">
<#assign addId = "${.now?long}02">
<#assign editId = "${.now?long}03">
<#assign delId = "${.now?long}04">
<#assign batchDelId = "${.now?long}05">
<#assign exportId = "${.now?long}06">
<#assign importId = "${.now?long}07">

-- 主菜单
INSERT INTO sys_permission(id, parent_id, name, url, component, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_route, is_leaf, keep_alive, hidden, hide_tab, description, status, del_flag, rule_flag, create_by, create_time, update_by, update_time, internal_or_external)
VALUES ('${mainId}', NULL, '${tableVo.ftlDescription}', '/${entityPackagePath}/${entityName?uncap_first}List', '${entityPackagePath}/${entityName}List', NULL, NULL, 0, NULL, '1', 0.00, 0, NULL, 1, 0, 0, 0, 0, NULL, '1', 0, 0, 'admin', '${.now?string["yyyy-MM-dd HH:mm:ss"]}', NULL, NULL, 0);

-- 新增
INSERT INTO sys_permission(id, parent_id, name, url, component, is_route, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_leaf, keep_alive, hidden, hide_tab, description, create_by, create_time, update_by, update_time, del_flag, rule_flag, status, internal_or_external)
VALUES ('${addId}', '${mainId}', '添加${tableVo.ftlDescription}', NULL, NULL, 0, NULL, NULL, 2, '${entityPackage}:${tableName}:add', '1', NULL, 0, NULL, 1, 0, 0, 0, NULL, 'admin', '${.now?string["yyyy-MM-dd HH:mm:ss"]}', NULL, NULL, 0, 0, '1', 0);

-- 编辑
INSERT INTO sys_permission(id, parent_id, name, url, component, is_route, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_leaf, keep_alive, hidden, hide_tab, description, create_by, create_time, update_by, update_time, del_flag, rule_flag, status, internal_or_external)
VALUES ('${editId}', '${mainId}', '编辑${tableVo.ftlDescription}', NULL, NULL, 0, NULL, NULL, 2, '${entityPackage}:${tableName}:edit', '1', NULL, 0, NULL, 1, 0, 0, 0, NULL, 'admin', '${.now?string["yyyy-MM-dd HH:mm:ss"]}', NULL, NULL, 0, 0, '1', 0);

-- 删除
INSERT INTO sys_permission(id, parent_id, name, url, component, is_route, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_leaf, keep_alive, hidden, hide_tab, description, create_by, create_time, update_by, update_time, del_flag, rule_flag, status, internal_or_external)
VALUES ('${delId}', '${mainId}', '删除${tableVo.ftlDescription}', NULL, NULL, 0, NULL, NULL, 2, '${entityPackage}:${tableName}:delete', '1', NULL, 0, NULL, 1, 0, 0, 0, NULL, 'admin', '${.now?string["yyyy-MM-dd HH:mm:ss"]}', NULL, NULL, 0, 0, '1', 0);

-- 批量删除
INSERT INTO sys_permission(id, parent_id, name, url, component, is_route, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_leaf, keep_alive, hidden, hide_tab, description, create_by, create_time, update_by, update_time, del_flag, rule_flag, status, internal_or_external)
VALUES ('${batchDelId}', '${mainId}', '批量删除${tableVo.ftlDescription}', NULL, NULL, 0, NULL, NULL, 2, '${entityPackage}:${tableName}:deleteBatch', '1', NULL, 0, NULL, 1, 0, 0, 0, NULL, 'admin', '${.now?string["yyyy-MM-dd HH:mm:ss"]}', NULL, NULL, 0, 0, '1', 0);

-- 导出excel
INSERT INTO sys_permission(id, parent_id, name, url, component, is_route, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_leaf, keep_alive, hidden, hide_tab, description, create_by, create_time, update_by, update_time, del_flag, rule_flag, status, internal_or_external)
VALUES ('${exportId}', '${mainId}', '导出excel_${tableVo.ftlDescription}', NULL, NULL, 0, NULL, NULL, 2, '${entityPackage}:${tableName}:exportXls', '1', NULL, 0, NULL, 1, 0, 0, 0, NULL, 'admin', '${.now?string["yyyy-MM-dd HH:mm:ss"]}', NULL, NULL, 0, 0, '1', 0);

-- 导入excel
INSERT INTO sys_permission(id, parent_id, name, url, component, is_route, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_leaf, keep_alive, hidden, hide_tab, description, create_by, create_time, update_by, update_time, del_flag, rule_flag, status, internal_or_external)
VALUES ('${importId}', '${mainId}', '导入excel_${tableVo.ftlDescription}', NULL, NULL, 0, NULL, NULL, 2, '${entityPackage}:${tableName}:importExcel', '1', NULL, 0, NULL, 1, 0, 0, 0, NULL, 'admin', '${.now?string["yyyy-MM-dd HH:mm:ss"]}', NULL, NULL, 0, 0, '1', 0);

-- 角色授权（admin 角色）
INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip) VALUES ('${.now?long}08', 'f6817f48af4fb3af11b9e8bf182f618b', '${mainId}', NULL, '${.now?string["yyyy-MM-dd HH:mm:ss"]}', '127.0.0.1');
INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip) VALUES ('${.now?long}09', 'f6817f48af4fb3af11b9e8bf182f618b', '${addId}', NULL, '${.now?string["yyyy-MM-dd HH:mm:ss"]}', '127.0.0.1');
INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip) VALUES ('${.now?long}10', 'f6817f48af4fb3af11b9e8bf182f618b', '${editId}', NULL, '${.now?string["yyyy-MM-dd HH:mm:ss"]}', '127.0.0.1');
INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip) VALUES ('${.now?long}11', 'f6817f48af4fb3af11b9e8bf182f618b', '${delId}', NULL, '${.now?string["yyyy-MM-dd HH:mm:ss"]}', '127.0.0.1');
INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip) VALUES ('${.now?long}12', 'f6817f48af4fb3af11b9e8bf182f618b', '${batchDelId}', NULL, '${.now?string["yyyy-MM-dd HH:mm:ss"]}', '127.0.0.1');
INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip) VALUES ('${.now?long}13', 'f6817f48af4fb3af11b9e8bf182f618b', '${exportId}', NULL, '${.now?string["yyyy-MM-dd HH:mm:ss"]}', '127.0.0.1');
INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip) VALUES ('${.now?long}14', 'f6817f48af4fb3af11b9e8bf182f618b', '${importId}', NULL, '${.now?string["yyyy-MM-dd HH:mm:ss"]}', '127.0.0.1');
```

- [ ] **Step 2: 在每个风格的 vue3 目录下放一个 SQL stub**

三个文件内容**完全相同**，均只有一行：
```
<#include "/common/sql/menu_insert.ftl">
```
落到（注意目录名里的 `${...}` 是字面量目录，不要展开）：
```bash
SKILL=/Users/irvinghua/workspace/javaweb-template/.claude/skills/jeecg-codegen
for s in one onetomany onetomany2; do
  d="$SKILL/templates/$s/java/\${bussiPackage}/\${entityPackage}/vue3"
  printf '<#include "/common/sql/menu_insert.ftl">\n' > "$d/V\${currentDate}_1__menu_insert_\${entityName}.sql"
done
```

- [ ] **Step 3: 验证 stub 与 include 路径**

Run:
```bash
SKILL=/Users/irvinghua/workspace/javaweb-template/.claude/skills/jeecg-codegen
find "$SKILL/templates" -name 'V*menu_insert*.sql'
cat "$SKILL/templates/common/sql/menu_insert.ftl" | head -1
```
Expected: 三个风格各一个 `.sql` stub；公共片段首行为注释。`/common/...` 相对 templateRoot 可被 FtlRunner 解析（Task 6 集成验证会真正渲染）。

---

## Task 5: 重写 codegen.py + 纯函数单测

**Files:**
- Create: `<SKILL>/scripts/codegen.py`
- Test: `<SKILL>/scripts/tests/test_codegen.py`

- [ ] **Step 1: 写单测（先失败）`scripts/tests/test_codegen.py`**

```python
import sys, os
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import codegen as cg


def test_style_map_keys():
    assert cg.STYLE_MAP == {'single': 'one', 'onetomany': 'onetomany', 'onetomany-tab': 'onetomany2'}


def test_normalize_injects_pk_and_currentdate():
    ctx = {'entityName': 'BizGoods', 'tableName': 'biz_goods', 'entityPackage': 'biz',
           'bussiPackage': 'org.jeecg.modules',
           'originalColumns': [{'fieldName': 'name', 'filedComment': '名称'}]}
    out = cg.normalize_ctx(ctx)
    assert out['currentDate']  # YYYYMMDD 注入
    assert out['entityPackagePath'] == 'biz'
    assert any(c['fieldName'] == 'id' for c in out['originalColumns'])  # 主键自动注入
    name_col = [c for c in out['originalColumns'] if c['fieldName'] == 'name'][0]
    assert name_col['fieldDbName'] == 'name'         # camel->snake 兜底
    assert name_col['classType'] == 'text'           # 默认 classType


def test_normalize_sets_searchfieldnum():
    ctx = {'entityName': 'A', 'tableName': 'a', 'entityPackage': 'b', 'bussiPackage': 'org.jeecg.modules',
           'originalColumns': []}
    out = cg.normalize_ctx(ctx)
    assert out['tableVo']['searchFieldNum'] == 6
    assert out['tableVo']['ftlDescription'] == 'a'    # 缺 description 用 tableName 兜底


def test_normalize_subtable_foreignkeys_camel():
    ctx = {'entityName': 'A', 'tableName': 'a', 'entityPackage': 'b', 'bussiPackage': 'org.jeecg.modules',
           'originalColumns': [],
           'subTables': [{'entityName': 'AItem', 'tableName': 'a_item',
                          'foreignKeys': ['order_id'], 'originalColumns': [{'fieldName': 'qty'}]}]}
    out = cg.normalize_ctx(ctx)
    sub = out['subTables'][0]
    assert sub['foreignKeys'] == ['orderId']          # snake->camel
    assert sub['colums'] == sub['originalColumns']     # jeecg 拼写别名补齐
    assert any(c['fieldName'] == 'id' for c in sub['originalColumns'])


def test_categorize_paths():
    assert cg.categorize(Path('org/jeecg/modules/biz/vue3/BizGoodsList.vue')) == 'frontend'
    assert cg.categorize(Path('org/jeecg/modules/biz/entity/BizGoods.java')) == 'backend'
    assert cg.categorize(Path('V20260603_1__menu_insert_BizGoods.sql')) == 'sql'


def test_strip_and_segment_helpers():
    assert cg.strip_template_prefix(Path('java/org/jeecg/x/entity/A.java')) == Path('org/jeecg/x/entity/A.java')
    before, after = cg.split_at_segment(Path('org/jeecg/biz/vue3/BizList.vue'), 'vue3')
    assert after == Path('BizList.vue')


def test_normalize_dst_name_dunder_to_dot():
    assert cg.normalize_dst_name(Path('BizGoods__data.ts')).name == 'BizGoods.data.ts'
    # .sql 的 __ 是 Flyway 规范，保留
    assert cg.normalize_dst_name(Path('V20260603_1__menu_insert_Biz.sql')).name == 'V20260603_1__menu_insert_Biz.sql'


if __name__ == '__main__':
    import traceback
    fns = [v for k, v in sorted(globals().items()) if k.startswith('test_') and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn(); print(f'PASS {fn.__name__}')
        except Exception:
            failed += 1; print(f'FAIL {fn.__name__}'); traceback.print_exc()
    print(f'\n{len(fns)-failed}/{len(fns)} passed')
    sys.exit(1 if failed else 0)
```

- [ ] **Step 2: 运行确认失败（codegen 还不存在）**

Run: `python3 /Users/irvinghua/workspace/javaweb-template/.claude/skills/jeecg-codegen/scripts/tests/test_codegen.py`
Expected: FAIL —— `ModuleNotFoundError: No module named 'codegen'` 或 import 报错。

- [ ] **Step 3: 写 `scripts/codegen.py`（完整内容）**

```python
#!/usr/bin/env python3
"""jeecg-codegen — 用对齐版 code-template 渲染 JeecgBoot CRUD 代码（Java FreeMarker 驱动）。

读 ctx.json → normalize → FtlRunner 渲染 → 按文件类型分发到本工程目录。
模板来自 jeecg/code-template（已对齐新 UI），本脚本不修改模板内容。
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
LIB_DIR = SKILL_DIR / 'lib'
TEMPLATES_DIR = SKILL_DIR / 'templates'
SCRIPTS_DIR = SKILL_DIR / 'scripts'
CACHE_DIR = SCRIPTS_DIR / '.cache'
JAR_NAMES = ['freemarker-2.3.32.jar', 'fastjson2.jar']

# 用户友好风格名 → code-template 目录名
STYLE_MAP = {
    'single':        'one',
    'onetomany':     'onetomany',
    'onetomany-tab': 'onetomany2',
}
VALID_STYLES = set(STYLE_MAP)

# 后端自动维护字段：前端表单/子表默认不显示（与 jeecg 一致）
SYSTEM_FIELD_NAMES = {'createBy', 'createTime', 'updateBy', 'updateTime', 'sysOrgCode'}

# code-template 实际用到的列字段为 fieldName/fieldType/filedComment/fieldDbType/classType；
# 其余为兜底，保证模板里偶发引用不抛 InvalidReferenceException。
COLUMN_DEFAULTS = {
    'fieldDbName': '',
    'filedComment': '',          # jeecg 模板拼写为 'filed'
    'fieldDbType': 'string',
    'fieldType': 'java.lang.String',
    'classType': 'text',
    'nullable': 'Y',
    'isShowList': 'Y',
    'isShow': 'Y',
    'isQuery': 'N',
    'dictField': '',
    'dictText': '',
    'dictTable': '',
}


def _camel_to_snake(s):
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s).lower()


def _snake_to_camel(s):
    if '_' not in s:
        return s
    parts = s.split('_')
    return parts[0] + ''.join(p[:1].upper() + p[1:] for p in parts[1:])


def _enrich_column(col, primary_key=None):
    out = dict(col)
    fn = out.get('fieldName', '')
    out.setdefault('fieldDbName', _camel_to_snake(fn))
    if 'isShow' not in col and (fn in SYSTEM_FIELD_NAMES or (primary_key and fn == primary_key)):
        out['isShow'] = 'N'
    for k, v in COLUMN_DEFAULTS.items():
        out.setdefault(k, v)
    if not out.get('filedComment'):
        out['filedComment'] = fn
    return out


def _enrich_tablevo(tv, ctx):
    out = dict(tv) if tv else {}
    out.setdefault('entityName', ctx.get('entityName', ''))
    out.setdefault('tableName', ctx.get('tableName', ''))
    out.setdefault('ftlDescription', ctx.get('description', ctx.get('tableName', '')))
    out.setdefault('searchFieldNum', 6)   # 高级查询折叠前显示字段数，jeecg 默认 6
    return out


def normalize_ctx(ctx):
    """补齐 code-template 模板需要、AI 不一定显式传入的派生字段。"""
    if 'entityPackage' in ctx and 'entityPackagePath' not in ctx:
        ctx['entityPackagePath'] = str(ctx['entityPackage']).replace('.', '/')
    if 'currentDate' not in ctx:
        ctx['currentDate'] = time.strftime('%Y%m%d')

    pk = ctx.get('primaryKeyField') or 'id'
    cols = ctx.get('originalColumns') or []
    if not any(c.get('fieldName') == pk for c in cols):
        cols = [{'fieldName': pk, 'filedComment': '主键', 'fieldDbName': pk,
                 'fieldDbType': 'string', 'fieldType': 'java.lang.String', 'classType': 'text',
                 'nullable': 'Y', 'isShowList': 'N', 'isShow': 'N', 'isQuery': 'N'}] + cols
    cols = [_enrich_column(c, pk) for c in cols]
    ctx['originalColumns'] = cols

    if 'columns' not in ctx:
        ctx['columns'] = [c for c in cols if c.get('fieldName') != pk]
    else:
        fe = [_enrich_column(c, pk) for c in ctx['columns']]
        ctx['columns'] = [c for c in fe if c.get('fieldName') != pk]

    ctx['tableVo'] = _enrich_tablevo(ctx.get('tableVo') or {}, ctx)
    ctx.setdefault('primaryKeyField', pk)

    subs = ctx.get('subTables') or []
    for sub in subs:
        sub_pk = sub.get('primaryKeyField') or 'id'
        sub_cols = sub.get('originalColumns') or []
        if not any(c.get('fieldName') == sub_pk for c in sub_cols):
            sub_cols = [{'fieldName': sub_pk, 'filedComment': '主键', 'fieldDbName': sub_pk,
                         'fieldDbType': 'string', 'fieldType': 'java.lang.String', 'classType': 'text',
                         'nullable': 'Y', 'isShowList': 'N', 'isShow': 'N', 'isQuery': 'N'}] + sub_cols
        sub_cols = [_enrich_column(c, sub_pk) for c in sub_cols]
        sub['originalColumns'] = sub_cols
        sub['colums'] = sub_cols       # jeecg 模板拼写别名（少一个 n）
        sub['columns'] = sub_cols
        sub.setdefault('originalForeignKeys', [])
        sub['foreignKeys'] = [_snake_to_camel(k) for k in (sub.get('foreignKeys') or [])]
        sub.setdefault('foreignRelationType', '0')
        sub.setdefault('ftlDescription', sub.get('tableName', ''))
        sub.setdefault('primaryKeyField', 'id')
    ctx['subTables'] = subs
    return ctx


def build_classpath():
    sep = ';' if os.name == 'nt' else ':'
    paths = [str(LIB_DIR / n) for n in JAR_NAMES]
    paths.append(str(CACHE_DIR))
    return sep.join(paths)


def _javac_release_flags():
    try:
        out = subprocess.run(['javac', '-version'], capture_output=True, text=True, check=True)
        ver = (out.stdout + out.stderr).strip()
    except Exception:
        return ['-source', '8', '-target', '8']
    m = re.search(r'javac\s+(\d+)(?:\.(\d+))?', ver)
    if not m:
        return ['-source', '8', '-target', '8']
    return ['-source', '8', '-target', '8'] if int(m.group(1)) == 1 else ['--release', '8']


def ensure_compiled():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    src = SCRIPTS_DIR / 'FtlRunner.java'
    cls = CACHE_DIR / 'FtlRunner.class'
    if cls.exists() and cls.stat().st_mtime >= src.stat().st_mtime:
        return
    sep = ';' if os.name == 'nt' else ':'
    jar_cp = sep.join(str(LIB_DIR / n) for n in JAR_NAMES)
    cmd = ['javac', '-encoding', 'UTF-8', *_javac_release_flags(), '-cp', jar_cp, '-d', str(CACHE_DIR), str(src)]
    print('[codegen] compiling FtlRunner …', ' '.join(cmd))
    subprocess.run(cmd, check=True)


def run_freemarker(style_dir, ctx_path, work_dir):
    cmd = ['java', '-cp', build_classpath(), 'FtlRunner', str(TEMPLATES_DIR), style_dir, str(ctx_path), str(work_dir)]
    print('[codegen] running FtlRunner …')
    return subprocess.run(cmd, check=False).returncode


def collect_outputs(work_dir):
    return [p for p in work_dir.rglob('*') if p.is_file()]


def categorize(rel):
    """backend / frontend(vue3) / sql。"""
    if rel.name.endswith('.sql'):
        return 'sql'
    if 'vue3' in rel.parts:
        return 'frontend'
    return 'backend'


def strip_template_prefix(rel):
    parts = list(rel.parts)
    if parts and parts[0] == 'java':
        parts = parts[1:]
    return Path(*parts)


def split_at_segment(rel, segment):
    parts = list(rel.parts)
    if segment in parts:
        idx = parts.index(segment)
        return Path(*parts[:idx]), Path(*parts[idx + 1:]) if parts[idx + 1:] else Path()
    return rel, Path()


def normalize_dst_name(p):
    if p.suffix == '.sql':
        return p
    return p.with_name(p.name.replace('__', '.')) if '__' in p.name else p


def entity_module_dir(ctx):
    name = str(ctx.get('entityName', ''))
    return name[:1].lower() + name[1:] if name else ''


def dispatch(work_dir, args, ctx):
    results = []
    sql_seen = set()
    entity_path = str(ctx.get('entityPackage', '')).replace('.', '/')
    module_dir = entity_module_dir(ctx)

    for src in collect_outputs(work_dir):
        rel = strip_template_prefix(src.relative_to(work_dir))
        cat = categorize(rel)
        if cat == 'sql':
            if not args.flyway_dir or src.name in sql_seen:
                continue
            sql_seen.add(src.name)
            dst = Path(args.flyway_dir) / src.name
        elif cat == 'frontend':
            if not args.frontend_root:
                continue
            _, after = split_at_segment(rel, 'vue3')
            dst = Path(args.frontend_root) / 'src/views' / entity_path / module_dir / after
        else:  # backend
            if not args.backend_root:
                continue
            dst = Path(args.backend_root) / 'src/main/java' / rel
        results.append((src, normalize_dst_name(dst)))
    return results


def write_files(plan, dry_run, sql_rewrite=None):
    for src, dst in plan:
        print(f"[codegen] {'WOULD WRITE' if dry_run else 'WROTE'} {dst}")
        if dry_run:
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.suffix == '.sql' and sql_rewrite:
            old, new = sql_rewrite
            dst.write_text(src.read_text(encoding='utf-8').replace(old, new), encoding='utf-8')
        else:
            shutil.copyfile(src, dst)


def parse_args():
    p = argparse.ArgumentParser(description='JeecgBoot codegen via Freemarker (code-template aligned).')
    p.add_argument('--style', required=True, choices=sorted(VALID_STYLES))
    p.add_argument('--ctx', required=True)
    p.add_argument('--backend-root')
    p.add_argument('--frontend-root')
    p.add_argument('--flyway-dir')
    p.add_argument('--out', help='[调试] 仅渲染到目录不分发')
    p.add_argument('--dry-run', action='store_true')
    return p.parse_args()


def main():
    args = parse_args()
    ctx_path = Path(args.ctx).resolve()
    if not ctx_path.is_file():
        sys.exit(f'ctx file not found: {ctx_path}')
    with ctx_path.open(encoding='utf-8') as f:
        ctx = normalize_ctx(json.load(f))
    norm_path = ctx_path.with_suffix('.normalized.json')
    with norm_path.open('w', encoding='utf-8') as f:
        json.dump(ctx, f, ensure_ascii=False, indent=2)

    ensure_compiled()
    style_dir = STYLE_MAP[args.style]

    if args.out:
        work_dir = Path(args.out).resolve()
        work_dir.mkdir(parents=True, exist_ok=True)
        rc = run_freemarker(style_dir, norm_path, work_dir)
        sys.exit(rc) if rc else print(f'[codegen] rendered to {work_dir}, skip dispatch (--out)')
        return

    with tempfile.TemporaryDirectory(prefix='jeecg-codegen-') as tmp:
        work_dir = Path(tmp)
        rc = run_freemarker(style_dir, norm_path, work_dir)
        if rc != 0:
            sys.exit(rc)
        plan = dispatch(work_dir, args, ctx)
        entity_path = str(ctx.get('entityPackage', '')).replace('.', '/')
        module_dir = entity_module_dir(ctx)
        entity_name = ctx.get('entityName', '')
        sql_rewrite = (f"'{entity_path}/{entity_name}", f"'{entity_path}/{module_dir}/{entity_name}") \
            if module_dir and entity_path and entity_name else None
        write_files(plan, args.dry_run, sql_rewrite)
        print(f'[codegen] {len(plan)} files dispatched.')


if __name__ == '__main__':
    main()
```

- [ ] **Step 4: 运行单测确认通过**

Run: `python3 /Users/irvinghua/workspace/javaweb-template/.claude/skills/jeecg-codegen/scripts/tests/test_codegen.py`
Expected: `7/7 passed`，退出码 0。

- [ ] **Step 5: 检查点**

Run: `python3 -c "import sys; sys.path.insert(0,'/Users/irvinghua/workspace/javaweb-template/.claude/skills/jeecg-codegen/scripts'); import codegen; print('import ok', sorted(codegen.STYLE_MAP))"`
Expected: `import ok ['onetomany', 'onetomany-tab', 'single']`。

---

## Task 6: 集成验证（三风格渲染 + 菜单 SQL）

**Files:**
- 临时：`$TMPDIR/jeecg-codegen/*.json`、`$TMPDIR/cg-out-*/`（验证用，不入 skill）

- [ ] **Step 1: 造单表样例 ctx**

```bash
mkdir -p "$TMPDIR/jeecg-codegen"
cat > "$TMPDIR/jeecg-codegen/biz_goods_ctx.json" <<'JSON'
{
  "bussiPackage": "org.jeecg.modules",
  "entityPackage": "biz",
  "entityName": "BizGoods",
  "tableName": "biz_goods",
  "description": "商品管理",
  "primaryKeyField": "id",
  "originalColumns": [
    {"fieldName": "name", "filedComment": "商品名称", "fieldDbType": "string", "fieldType": "java.lang.String", "classType": "text", "isQuery": "Y"},
    {"fieldName": "price", "filedComment": "价格", "fieldDbType": "double", "fieldType": "java.lang.Double", "classType": "text"}
  ]
}
JSON
```

- [ ] **Step 2: 单表 `--out` 渲染（不分发），检查产物**

```bash
SKILL=/Users/irvinghua/workspace/javaweb-template/.claude/skills/jeecg-codegen
rm -rf "$TMPDIR/cg-out-one"
python3 "$SKILL/scripts/codegen.py" --style single \
  --ctx "$TMPDIR/jeecg-codegen/biz_goods_ctx.json" --out "$TMPDIR/cg-out-one"
echo "=== 产物清单 ==="; find "$TMPDIR/cg-out-one" -type f | sort
```
Expected: 渲染成功（退出 0）。产物含后端 `BizGoods.java`/`BizGoodsMapper.java`/`BizGoodsMapper.xml`/`IBizGoodsService.java`/`BizGoodsServiceImpl.java`/`BizGoodsController.java`，前端 `BizGoodsList.vue`/`BizGoods.data.ts`/`BizGoods.api.ts`/`modules/BizGoodsModal.vue`，以及一个 `V<date>_1__menu_insert_BizGoods.sql`。

- [ ] **Step 3: 核对前端风格与菜单 SQL 列名**

Run:
```bash
echo "=== List.vue 关键 import ==="; grep -nE "useListPage|/@/components/Table|BasicTable" "$TMPDIR/cg-out-one"/**/BizGoodsList.vue
echo "=== 菜单 SQL 列 ==="; grep -oE "is_route|is_leaf|rule_flag|internal_or_external" "$TMPDIR/cg-out-one"/**/V*BizGoods.sql | sort -u
```
Expected：List.vue 用 `useListPage` + `/@/components/Table`（与仓库对齐页面一致）；SQL 含 `is_route/is_leaf/rule_flag/internal_or_external`（与 `sys_permission` DDL 一致）。

- [ ] **Step 4: 造一对多样例 ctx 并渲染 onetomany + onetomany-tab**

```bash
cat > "$TMPDIR/jeecg-codegen/biz_order_ctx.json" <<'JSON'
{
  "bussiPackage": "org.jeecg.modules", "entityPackage": "biz",
  "entityName": "BizOrder", "tableName": "biz_order", "description": "订单管理",
  "primaryKeyField": "id",
  "originalColumns": [{"fieldName": "orderNo", "filedComment": "订单号", "classType": "text", "isQuery": "Y"}],
  "subTables": [{
    "entityName": "BizOrderItem", "tableName": "biz_order_item", "ftlDescription": "订单明细",
    "foreignKeys": ["order_id"], "originalForeignKeys": ["order_id"],
    "originalColumns": [{"fieldName": "qty", "filedComment": "数量", "classType": "text"}]
  }]
}
JSON
SKILL=/Users/irvinghua/workspace/javaweb-template/.claude/skills/jeecg-codegen
for st in onetomany onetomany-tab; do
  rm -rf "$TMPDIR/cg-out-$st"
  python3 "$SKILL/scripts/codegen.py" --style $st --ctx "$TMPDIR/jeecg-codegen/biz_order_ctx.json" --out "$TMPDIR/cg-out-$st"
  echo "=== $st 子表产物 ==="; find "$TMPDIR/cg-out-$st" -type f -name '*BizOrderItem*' | sort
done
```
Expected：两种风格都渲染成功；`#segment#` 切分出子表 `BizOrderItem.java`/`BizOrderItemMapper.java`/`...Mapper.xml`/`IBizOrderItemService.java`/`BizOrderItemServiceImpl.java`，且 onetomany-tab 额外有子表 `BizOrderItemList.vue`。

- [ ] **Step 5: dry-run 验证分发路径（不写工程）**

```bash
SKILL=/Users/irvinghua/workspace/javaweb-template/.claude/skills/jeecg-codegen
REPO=/Users/irvinghua/workspace/javaweb-template
python3 "$SKILL/scripts/codegen.py" --style single --ctx "$TMPDIR/jeecg-codegen/biz_goods_ctx.json" --dry-run \
  --backend-root "$REPO/jeecg-boot/jeecg-module-system/jeecg-system-biz" \
  --frontend-root "$REPO/jeecgboot-vue3" \
  --flyway-dir "$REPO/jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/resources/flyway/sql/mysql"
```
Expected：打印 `WOULD WRITE` 行，后端落到 `.../jeecg-system-biz/src/main/java/org/jeecg/modules/biz/...`，前端落到 `.../jeecgboot-vue3/src/views/biz/bizGoods/...`，SQL 落到 flyway 目录。**无任何文件实际写入。**

- [ ] **Step 6: 检查点（清理临时产物）**

Run: `rm -rf "$TMPDIR/cg-out-"* && echo cleaned`
Expected: `cleaned`。三风格渲染 + 分发路径均验证通过。

---

## Task 7: 同步更新 SKILL.md（范围/CLI/示例）

**Files:**
- Modify: `<SKILL>/SKILL.md`

> 逐项替换。改前用 Read 读出当前段落确认上下文，再 Edit。

- [ ] **Step 1: 改「模板覆盖范围」表**

把现有表（含 default/one、tree、tab/inner-table/erp、vue3Native 等行）整体替换为：

```markdown
| 表类型 | --style | 前端 | 触发关键词 |
|---|---|---|---|
| 单表 | `single` | vue3 | 默认 |
| 一对多 · 平铺子表（JVxeTable） | `onetomany` | vue3 | 一对多 / 主子表 / 子表录入 |
| 一对多 · Tab | `onetomany-tab` | vue3 | tab风格 / 标签页子表 |

> 模板源自本工程 `jeecg-boot/.../resources/jeecg/code-template`（已对齐新 UI）。仅 vue3；无树表 / ERP / 内嵌 / vue3Native / 移动端（本仓库未使用）。
```
并删除原先关于「不支持组合 / CgformEnum / vue2」那段说明（已不适用）。

- [ ] **Step 2: 改 CLI 参考表**

去掉 `--frontend-style`、`--mobile-root` 两行；`--style` 取值改为 `single` `onetomany` `onetomany-tab`；其余参数（`--ctx`/`--backend-root`/`--frontend-root`/`--flyway-dir`/`--out`/`--dry-run`）保留。

- [ ] **Step 3: 改典型调用示例**

替换为：
```bash
python /Users/irvinghua/workspace/javaweb-template/.claude/skills/jeecg-codegen/scripts/codegen.py \
  --style single \
  --ctx "$TMPDIR/jeecg-codegen/biz_goods_ctx.json" \
  --backend-root /Users/irvinghua/workspace/javaweb-template/jeecg-boot/jeecg-module-system/jeecg-system-biz \
  --frontend-root /Users/irvinghua/workspace/javaweb-template/jeecgboot-vue3 \
  --flyway-dir /Users/irvinghua/workspace/javaweb-template/jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/resources/flyway/sql/mysql
```

- [ ] **Step 4: 全文搜残留并清理**

Run:
```bash
grep -nE "frontend-style|mobile-root|vue3Native|default/one|inner-table|erp/onetomany|tree|CgformEnum" /Users/irvinghua/workspace/javaweb-template/.claude/skills/jeecg-codegen/SKILL.md
```
Expected: 无输出（全部清理干净）。若有命中，逐条改掉。

- [ ] **Step 5: 检查点**

Run: `grep -nE "single|onetomany|onetomany-tab" /Users/irvinghua/workspace/javaweb-template/.claude/skills/jeecg-codegen/SKILL.md | head`
Expected: 看到新风格名。文档与脚本一致。

---

## Task 8: 核对并调整 references/dict-matching.md

**Files:**
- Modify (按需): `<SKILL>/references/dict-matching.md`

> 旧 references 的字典逻辑假设 `classType='list' + dictField` 会被模板展开成 `@Dict`/`JDictSelectTag`。需核对对齐版 code-template 是否真这么处理（审计显示 po 仅用 5 字段、classType 出现 3 次，可能不一致）。

- [ ] **Step 1: 查 code-template 的字典渲染方式**

Run:
```bash
CT=/Users/irvinghua/workspace/javaweb-template/jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/resources/jeecg/code-template
grep -rnE "@Dict|dictField|dictCode|JDictSelectTag|classType" "$CT/one" | head -30
```
Expected: 看清对齐版到底用哪个字段、什么写法生成字典控件。

- [ ] **Step 2: 按实际行为修订 dict-matching.md**

若对齐版用法与 references 描述不同（字段名 / classType 取值 / 控件），改 `references/dict-matching.md` 使其与对齐版模板一致；若需要 normalize 额外补字典字段，回到 `codegen.py` 的 `COLUMN_DEFAULTS`/`_enrich_column` 补齐并加一条单测。
若一致则本 Task 仅确认、不改。

- [ ] **Step 3: 检查点（回归单测仍绿）**

Run: `python3 /Users/irvinghua/workspace/javaweb-template/.claude/skills/jeecg-codegen/scripts/tests/test_codegen.py`
Expected: 全部 PASS（若 Step 2 动了 codegen.py）。

---

## Task 9: 端到端真实生成（可选，需你点头）

> 真正往工程写文件 + 编译验证。**默认不自动跑**，确认后执行。

- [ ] **Step 1: 真实生成单表到工程**

```bash
SKILL=/Users/irvinghua/workspace/javaweb-template/.claude/skills/jeecg-codegen
REPO=/Users/irvinghua/workspace/javaweb-template
python3 "$SKILL/scripts/codegen.py" --style single --ctx "$TMPDIR/jeecg-codegen/biz_goods_ctx.json" \
  --backend-root "$REPO/jeecg-boot/jeecg-module-system/jeecg-system-biz" \
  --frontend-root "$REPO/jeecgboot-vue3" \
  --flyway-dir "$REPO/jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/resources/flyway/sql/mysql"
```

- [ ] **Step 2: 编译后端验证**

Run:
```bash
cd /Users/irvinghua/workspace/javaweb-template/jeecg-boot
mvn -pl jeecg-module-system/jeecg-system-biz -am compile -DskipTests -q && echo BUILD_OK
```
Expected: `BUILD_OK`（需先有 `biz_goods` 表或仅验证编译——生成的 Entity 不依赖表存在即可编译）。

- [ ] **Step 3: 前端类型检查（可选）**

Run: `cd /Users/irvinghua/workspace/javaweb-template/jeecgboot-vue3 && pnpm dev`（人工看生成页是否加载）。

- [ ] **Step 4: 决定去留**

如为验证生成，记得回收：`git status` 看新增文件，按需 `rm` 或保留。Flyway SQL 若不想入库则删掉对应 `V*.sql`。

---

## Self-Review（写计划后自检）

- **Spec 覆盖**：渲染引擎(Task2) / templates 复制(Task3) / 菜单 SQL(Task4) / 编排+ctx(Task5) / 三风格&分发验证(Task6) / SKILL.md(Task7) / 字典核对(Task8) / 端到端(Task9) —— spec 各节均有对应 Task。✅
- **占位符**：无 TBD/TODO；FtlRunner.java、menu_insert.ftl、codegen.py、测试均为完整内容。✅
- **类型一致**：`STYLE_MAP` 键 `single/onetomany/onetomany-tab` 在 codegen.py、测试、SKILL.md 三处一致；`categorize` 返回 `sql/frontend/backend` 与 `dispatch` 分支一致；`normalize_dst_name`/`split_at_segment`/`strip_template_prefix` 在 codegen 定义、测试引用，签名一致。✅
