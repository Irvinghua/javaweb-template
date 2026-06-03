# 字典匹配规则

> ⚠️ **重要前提（与旧版不同）**：本工程对齐版 code-template **不会**根据 ctx 上的 `dictField` / `classType` 自动渲染字典控件。生成的 `*.data.ts` 只按 `fieldType` 选 `Input` / `InputNumber` / `DatePicker`。
>
> 因此「字典」是一个**生成后 post-edit** 的步骤：先查 `sys_dict` 确定字段该用哪个字典，**生成基础代码后**再用 Edit 把对应列/表单项改成字典控件。在 ctx 上设 dict 字段没有效果（normalize 会兜底保留这些键，但模板不读）。

## 第一步：查全部字典（先查后建，配合 jeecg-system skill）

```bash
mysql --no-defaults --default-character-set=utf8mb4 -h127.0.0.1 -P3306 -u<user> -p<password> {dbname} -e "
SELECT d.dict_code, d.dict_name,
       GROUP_CONCAT(i.item_text, '=', i.item_value ORDER BY i.sort_order SEPARATOR ', ') AS items
FROM sys_dict d
LEFT JOIN sys_dict_item i ON d.id = i.dict_id AND i.status = 1
WHERE d.del_flag = 0
GROUP BY d.dict_code, d.dict_name
ORDER BY d.dict_code"
```

得到字典清单：`dict_code` / `dict_name` / `items`。字典不存在又确需时，用 `jeecg-system` skill 的 `find_or_create_dict` 创建。

## 第二步：逐字段判断该用哪个字典编码

按优先级：

1. **用户明确指定** —— "状态用字典 order_status" → `order_status`
2. **fieldName == dict_code** —— 字段 `status` 与 `dict_code='status'` 相等
3. **关键词匹配** —— 字段注释含关键词，搜 `dict_name` 包含该词的字典（"状态"→含"状态"的 dict_name；"类型"→含"类型"；"级别/等级"→含"级别"）
4. **不匹配** —— 该字段保持普通输入框，不加字典

把结论记下来（字段 → dict_code 的对应表），第三步用。

## 第三步：生成后 post-edit 把字段改成字典控件

> 在生成的 `<EntityName>.data.ts` 里改（该文件已 `import { render } from '/@/utils/common/renderUtils'`，列渲染开箱即用）。

假设字段 `orderStatus`（注释"订单状态"）匹配到字典 `order_status`：

**① 列表列（`columns` 里该列）** —— 加 `customRender` 把值翻译成字典文本：

```ts
{
  title: '订单状态',
  dataIndex: 'orderStatus',
  customRender: ({ text }) => render.renderDict(text, 'order_status'),
},
```

**② 查询项（`searchFormSchema`）和表单项（`formSchema`）里该字段** —— `component` 改成 `JDictSelectTag`：

```ts
{
  label: '订单状态',
  field: 'orderStatus',
  component: 'JDictSelectTag',
  componentProps: { dictCode: 'order_status' },
},
```

- 多选字典：`component: 'JSelectMultiple'` + `componentProps: { dictCode: 'order_status' }`
- 表字典（关联业务表，如 `sys_user`）：`componentProps: { dictCode: "表名,label字段,value字段" }`，例 `"sys_user,realname,username"`

完成后无需改后端：列表接口返回原始 value，前端 `renderDict` 负责显示文本。

**（可选）后端直接回填 `_dictText`**：在 `Entity.java` 对应字段加 `@Dict(dicCode = "order_status")`，jeecg 的 `DictAspect` 会自动补 `orderStatus_dictText` 字段，此时列 `dataIndex` 可直接改用 `orderStatus_dictText`（就不必写 customRender）。

## 小结

| 步骤 | 动作 | 在哪 |
|---|---|---|
| 1 | 查 `sys_dict` 拿字典清单 | DB（配合 jeecg-system） |
| 2 | 判定字段 → dict_code | 思考 |
| 3 | **生成后** 改 `.data.ts`（列 `renderDict` + 表单 `JDictSelectTag`） | post-edit 产物 |

> 对齐版模板不内建字典 ⇒ 字典永远是生成后的人工增强，属 `post-edit-recipes.md` 范畴。
