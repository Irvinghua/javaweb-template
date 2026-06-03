# 字段语义 → Freemarker 字段映射

新建表时（用户用自然语言描述字段），按此表把字段转成 ctx.json 中 column 项的 `fieldDbType` / `fieldType`。
已有表场景从 DDL 读类型，不需要这张表。

> ⚠️ **对齐模板只按 `fieldType` 选控件**：`date`→DatePicker、`datetime`→DatePicker(带时间)、`int/decimal/double`→InputNumber、其余→Input。**不读 `classType`**。
> 所以下表 `classType` 列只是**语义标注**——凡是需要"非 Input 控件"（多行文本/富文本/下拉字典/开关/上传/用户·部门选择/省市区/弹窗关联等）的字段，对齐模板都先按普通 Input 生成，**再生成后 post-edit**（见 `dict-matching.md` 与 `post-edit-recipes.md`）。`fieldDbType`/`fieldType` 仍然重要（决定 DB 列类型与控件大类）。

## 类型映射

按字段中文/英文语义匹配最近一行：

| 语义关键词 | DB 类型 | fieldDbType | fieldType | classType | 说明 |
|---|---|---|---|---|---|
| 名称 / 标题 / 编码 / 编号 | varchar(100) | string | java.lang.String | text | 普通输入框 |
| 备注 / 描述 / 说明 / 详情 | text | Text | java.lang.String | textarea | 多行文本 |
| 内容（富文本）| text | Text | java.lang.String | umeditor | 富文本编辑器 |
| 金额 / 价格 / 费用 / 单价 / 总价 | decimal(10,2) | BigDecimal | java.math.BigDecimal | text | 数字输入 |
| 数量 / 个数 / 库存 / 排序 / 序号 | int | int | java.lang.Integer | text | 整数输入 |
| 状态 / 类型 / 级别 / 分类 | varchar(10) | string | java.lang.String | list | 单选下拉 + 字典 |
| 下拉搜索 / 搜索选择 / 关联搜索 | varchar(36) | string | java.lang.String | sel_search | JSearchSelect，支持输入过滤 |
| 多选 / 多分类 | varchar(50) | string | java.lang.String | list_multi | 多选 + 字典 |
| 单选按钮组 / radio | varchar(10) | string | java.lang.String | radio | Radio 按钮组 + 字典 |
| 多选复选框 / checkbox | varchar(50) | string | java.lang.String | checkbox | Checkbox 组 + 字典 |
| 是否 / 启用 / 开关 | varchar(2) | string | java.lang.String | switch | Switch 开关 |
| 密码 / 口令 | varchar(100) | string | java.lang.String | password | Input[password] |
| Markdown | text | Text | java.lang.String | markdown | Markdown 编辑器 |
| 日期 / 生日 | date | Date | java.util.Date | date | 日期选择 |
| 时间 / 时刻 | time | Time | java.util.Date | time | 时间选择 |
| 日期时间 / 创建时间 / 更新时间 | datetime | Datetime | java.util.Date | datetime | 日期时间 |
| 图片 / 头像 / 照片 | varchar(1000) | string | java.lang.String | image | JImageUpload |
| 文件 / 附件 / 文档 | varchar(1000) | string | java.lang.String | file | JUpload |
| 用户 / 操作人 / 负责人 | varchar(32) | string | java.lang.String | sel_user | JSelectUserByDept |
| 部门 / 组织 / 单位 | varchar(32) | string | java.lang.String | sel_depart | JSelectDept |
| 省市区 / 地址 | varchar(50) | string | java.lang.String | pca | 省市区联动 |
| 关联（弹窗选择） | varchar(36) | string | java.lang.String | popup | JPopup 关联记录 |
| 关联（弹窗字典） | varchar(36) | string | java.lang.String | popup_dict | JPopup 字典模式 |

## 字典 / 关联字段

> ⚠️ 对齐模板**不会**根据 ctx 自动展开字典——在 column 上设 `classType`/`dictTable`/`dictText`/`dictField` 没有效果（normalize 会兜底保留，但模板不读）。

字典、关联表、用户/部门选择等都是**生成后 post-edit** 的人工增强：先查 `sys_dict`（或目标业务表）确定编码，再改产物 `.data.ts` 的列与表单项。完整写法见 `references/dict-matching.md`（系统字典 `JDictSelectTag`、表字典 `JSearchSelect`、列 `render.renderDict` 等）。

## 系统字段约定

新建表默认含五个系统字段（`originalColumns` 里直接补齐）：

| fieldName | fieldDbName | fieldDbType | classType | nullable |
|---|---|---|---|---|
| createBy | create_by | string | text | Y |
| createTime | create_time | Datetime | datetime | Y |
| updateBy | update_by | string | text | Y |
| updateTime | update_time | Datetime | datetime | Y |
| sysOrgCode | sys_org_code | string | text | Y |

**已有表场景：** 检查 DDL，只生成实际存在的系统字段。

## 主键策略

| 主键定义 | fieldType | TableId 注解 | 说明 |
|---|---|---|---|
| `varchar(36)` 无自增 | `java.lang.String` | `IdType.ASSIGN_ID` | 默认（雪花 ID）|
| `int AUTO_INCREMENT` | `java.lang.Integer` | `IdType.AUTO` | DB 自增 |
| `bigint AUTO_INCREMENT` | `java.lang.Long` | `IdType.AUTO` | DB 自增 |

主键策略由 ctx.json 的 `primaryKeyField` + 主键所在 column 的 `fieldType` 推导，模板自动选注解。
