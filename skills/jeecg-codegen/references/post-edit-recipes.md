# 模板没覆盖的特殊需求 — 改产物清单

跑完 `codegen.py` 之后，如果用户提了模板表达不出的需求，按这里指引找改动位置。**不要改 templates/，永远改产物**。

## 常见需求 → 改动位置

| 用户需求 | 改哪 | 改什么 |
|---|---|---|
| **字段加字典 / 下拉**（状态、类型、关联表）| 模板不自动出字典。`*.data.ts` 列加 `customRender: ({text})=>render.renderDict(text,'<code>')`；查询/表单项 `component` 改 `'JDictSelectTag'` + `componentProps.dictCode`（表字典用 `'JSearchSelect'` + `componentProps.dict="表名,label,value"`）。详见 `dict-matching.md` | data.ts |
| **字段联动**（A 变化触发 B 重算） | `*.data.ts` formSchema 中字段对象加 `dynamicRules` 或 `componentProps` 加事件 | data.ts |
| **价格 × 数量 = 总价** 自动算 | `*Modal.vue` / `*Form.vue` 的 `setup()` 里加 watch | Modal.vue |
| **列表行加自定义按钮**（如"复制""审批"） | `*List.vue` 的 `getTableAction` 返回数组里追加；**同时**按按钮数量调整 `actionColumn.width`（见下方"操作列宽度参考"） | List.vue |
| **列表行级状态着色**（如启用绿色禁用红色）| `*.data.ts` columns 项加 `customRender` 返回带 class 的 span | data.ts |
| **新增前自动填某字段**（如生成单号）| `*Modal.vue` `handleAdd` 里赋值给 formData | Modal.vue |
| **保存前校验跨字段约束** | `*Modal.vue` 的 `handleOk` 里加自定义校验 | Modal.vue |
| **导出 Excel 自定义字段** | `Entity.java` `@Excel` 注解的 `replace` / `format` 参数；Controller 不用改 | Entity.java |
| **列表查询加非字段条件**（如近 30 天）| `Controller.java` 的 `queryPageList` 里追加 QueryWrapper 条件 | Controller.java |
| **下拉/多选字段查询语义改 LIKE** | `Controller.java` 加 `customeRuleMap.put("xxx", QueryRuleEnum.LIKE_WITH_OR)` | Controller.java |
| **新增的子业务方法**（删除时联动清理）| `IService.java` + `ServiceImpl.java` 增加方法 | Service |
| **自定义查询接口** | `Controller.java` 加 `@GetMapping("/customQuery")` + 调 service | Controller.java |
| **字段权限 / 按钮权限** | 用 jeecg-system skill 在 `sys_permission` 配，不改代码 | 无 |
| **大字段折叠 / 单元格弹窗** | `*.data.ts` columns 加 `customRender` 用 `<a-popover>` | data.ts |
| **修改菜单图标 / 标题颜色** | 改生成的 Flyway SQL 中 `sys_permission.icon`；或先 INSERT 后 UPDATE | SQL |

## 操作列宽度参考

`getTableAction()` 里的按钮显示为行内链接，`getDropDownAction()` 折叠进"更多"下拉。
每增加一个行内按钮，操作列需相应加宽：

| `getTableAction` 按钮数 | 有"更多"下拉 | 推荐 `actionColumn.width` |
|---|---|---|
| 1（仅编辑） | 是 | 120 |
| 2（编辑 + 复制） | 是 | 180 |
| 3 | 是 | 240 |
| 1 | 否（dropDownActions 为空） | 80 |

改动位置：`*List.vue` 的 `useListPage` 配置块中 `actionColumn.width`。

## 默认值需求（"创建时预填某值"）

- **后端默认值**：对齐版模板不读 `defaultVal`；在生成的 `Entity.java` 字段或建表 DDL 上手工加默认值
- **前端表单默认值**：改产物 `*Modal.vue` 的 `defaultData()` 函数

## 列表布局调整

某些字段需要独占整行（如富文本、备注）时，改产物 `*.data.ts` 的 `formSchema` 里该字段加 `colProps: { span: 24 }`。

## 增量改字段（不是新需求）

走 SKILL.md 的"增量修改"流程，不要重新跑全量生成。

## 改完之后

- 跑 IDE 的格式化 / lint
- 用 `git diff` 让用户看一下差异
- 提示用户重启后端 + 刷新前端
