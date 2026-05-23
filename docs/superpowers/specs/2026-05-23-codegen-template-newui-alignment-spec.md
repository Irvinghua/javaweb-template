# CRUD 代码生成模板对齐新 UI Spec

> 本 spec 整理：在把 vibeCRUD 前端按新设计稿换皮（`feat/ui-redesign` 分支）过程中固化下来的「列表页布局规约」+ 踩过的坑，作为后续修改 JeecgBoot 代码生成器模板（旧 UI 风格）的依据。当前**只做盘点，不动代码生成模板**。

## 0. 背景

- 工程是 ToB CRUD 脚手架，70% 业务页是「上方搜索区 + 下方表格」的列表页
- JeecgBoot 的代码生成器会按既定模板批量产出 `XxxList.vue` / `xxx.data.ts` 等文件
- 当前模板对齐的是旧 UI 风格，与 `feat/ui-redesign` 分支的新设计稿（设计稿源：`jeecgboot-ui/pages/user-v2.html` + `jeecgboot-ui/pages/jeecg-page.css`）有结构和样式差距
- 目标：把模板按下面"新 UI 规约"+"踩坑清单"对齐，让以后新生成的列表页直接长得对，不用再手工返工

## 1. 新 UI 列表页结构规约（生成代码必须符合）

### 1.1 DOM/组件树骨架

```
BasicTable (.jeecg-basic-table.jeecg-basic-table-form-container)
  └── BasicForm (.jeecg-basic-form)                   ← 搜索 card
        ├── <FormItem> × N                              （每字段一个 col）
        └── <FormAction>                                （查询/重置/高级筛选 actionCol）
  └── <a-form-item-rest> > <a-form-item>
        └── <a-table> (.ant-table-wrapper)            ← 表格 card
              ├── .ant-table-title                     （TableHeader：toolbar + 选中提示）
              ├── .ant-table-container/.ant-table-content/.ant-table-body
              └── .ant-pagination
```

外层 `.jeecg-basic-table` 同时挂 `.jeecg-basic-table-form-container`（modifier）—— 这两个 class 指向**同一个 div**，不是两层。⚠️ 见踩坑 #1。

### 1.2 关键 layout 规则（已在 `feat/ui-redesign` 分支落地）

| 元素 | 规则 |
|---|---|
| `.jeecg-layout-content` | `padding: 22px 24px 28px`（对齐设计稿 `.page`） |
| `.jeecg-basic-table`（外层容器） | `display: flex; flex-direction: column; gap: 16px`，**无** bg/shadow/radius/padding |
| `.jeecg-basic-form`（搜索 card） | bg `--surface`、`border-radius: 18px`、`box-shadow: --shadow-card`、`padding: 18px 22px` |
| `.ant-table-wrapper`（表格 card） | bg `--surface`、`border-radius: 18px`、`box-shadow: --shadow-card`、`padding: 16px 20px 18px` |
| `.ant-table-title`（toolbar 槽位） | `padding: 0 0 14px; background: transparent` |
| `.ant-pagination` | `margin: 14px 0 0 0` |

### 1.3 搜索区字段规则

| 配置 | 默认值（已在 `useListPage.ts` 改过） |
|---|---|
| `autoAdvancedCol` | **2**（超过 2 字段自动折叠进"高级筛选"） |
| `baseColProps` | `{ xs:24, sm:12, md:12, lg:8, xl:8, xxl:6 }` |
| `labelCol`（不要在页面里乱覆盖！） | `{ xs:24, sm:8, md:6, lg:8, xl:6, xxl:6 }` |
| `actionColOptions` | 沿用 useListPage 默认即可，无需在页面覆盖 |
| 行 1 视觉 | `[f1] [f2] [actionCol]` 永远占据一行 |
| 行 2+ | 高级字段，与行 1 之间一条 dashed 横线分隔 |

### 1.4 表格样式

- 仅水平行线，**无任何竖线**
- thead：bg `--surface-2`、color `--ink-500`、font-weight 600、font-size 13px、padding 12px 14px
- tbody td：font-size 13px、color `--ink-700`、padding 13px 14px、border-bottom 1px `--line`
- 末行：`border-bottom: 0`
- 行 hover：bg `--surface-2`
- 表格密度：通过 `settings/index.vue` 给 wrap 元素挂 `.jeecg-table-density-loose` / `.jeecg-table-density-compact` 切换

### 1.5 工具栏按钮（toolbar）

- 主按钮（新增）：accent 渐变填充、白字、accent 阴影、36px 高、10px 圆角
- 次按钮（导出/导入/回收站）：ghost（白底、`--line` 边、`--ink-700` 字）
- 表格右上角图标按钮**只有 2 个**：`RedoSetting`（刷新）+ 齿轮 `Popover`（密度/列设置/全屏 三合一）

### 1.6 操作列（"操作"）

- 每个按钮：`.row-btn` ghost 风格（28px 高、padding 0 10px、border `--line`、radius 6px、font 12.5px）
- "更多"按钮：`.row-btn.more` 28×28 方形 + `⋯` SVG 图标
- 下拉浮层：`.menu-pop` 风格
- **`label` 含"删除"或"delete"**自动 danger 红色（共享层 `TableAction.vue` 已实现）
- 页面 schema 不需要再手动传 `danger: true`

## 2. 代码生成模板需要同步修改的点

> 待审阅，确定模板路径后逐个修改。常见模板位置：`jeecg-boot/.../jimureport-spring-boot/resources/jeecg/${entityName}/vue3/` 或类似。

### 2.1 `${EntityName}List.vue` 模板

模板生成的页面通常包含：

```vue
<template>
  <BasicTable @register="registerTable" ...>
    <template #toolbar>
      <a-button preIcon="ant-design:plus-outlined" type="primary" @click="handleAdd">新增</a-button>
      <a-button preIcon="ant-design:export-outlined" @click="onExportXls">导出</a-button>
      ...
    </template>
    <template #action="{ record }">
      <TableAction :actions="getTableAction(record)" :dropDownActions="getDropdownAction(record)" />
    </template>
  </BasicTable>
</template>
<script setup>
  const [registerTable, { reload }] = useListPage({
    designScope: 'xxx',
    tableProps: {
      api: queryXxxList,
      columns,
      formConfig: {
        labelWidth: 120,
        schemas: searchFormSchema,
      },
      actionColumn: { width: 120, fixed: false, ... },
    },
    exportConfig: { ... },
    importConfig: { ... },
  });
</script>
```

**需要确认/修改**：

- [ ] `formConfig` 中**不要写** `labelCol: { xxl: 8 }` 这类单 key 覆盖（见踩坑 #11）
- [ ] `formConfig.actionColOptions` 不要在模板写死，让 useListPage 默认值生效
- [ ] `formConfig.autoAdvancedCol` 不要在模板写死（useListPage 默认已是 2）
- [ ] toolbar 模板的按钮顺序：主按钮（新增/批量）在前，次按钮（导出/导入/回收站）后跟
- [ ] action 列模板：用 `getTableAction(record)` 直接返回数组，**label 含"删除"的对象不需要再写 `color: 'error'` 或 `danger: true`**——共享层会自动识别
- [ ] action 列模板里的"更多"下拉用 `dropDownActions` 参数即可，无需额外处理 ⋯ 图标，共享层会渲染

### 2.2 `${entityName}.data.ts` 模板

```ts
export const columns: BasicColumn[] = [...]
export const searchFormSchema: FormSchema[] = [
  {
    field: 'xxx',
    label: 'xxx',
    component: 'JInput',
    // colProps 应该是完整的 6 个屏宽都写，或者干脆不写让 useListPage 默认接管
  },
  ...
]
```

**需要确认/修改**：

- [ ] `searchFormSchema` 每个字段的 `colProps`：
  - **要么完全省略**（让 useListPage 默认 `{xs:24, sm:12, md:12, lg:8, xl:8, xxl:6}` 生效）
  - **要么写完整 6 个屏宽**（不要只写 `{ xxl: 8 }` 这种偏一个 key 的，会和默认 deep merge 出奇怪结果）
- [ ] `columns` 中`action` 列定义保持 `{ width: 120, fixed: false, dataIndex: 'action', slots: { customRender: 'action' } }`，不要写死 `align: 'center'` 以外的样式
- [ ] 如果模板里有 `defaultHidden` 字段，确认它们参与"列设置"的勾选/隐藏正确

### 2.3 Drawer/Modal 模板（增删改弹窗）

新 UI 的 Modal/Drawer 样式由 `src/components/Modal/**` + `src/components/Drawer/**` 全局统一接管，模板不需要写额外样式。

**需要确认**：

- [ ] 模板里的 `<BasicDrawer>` 或 `<BasicModal>` 不要传 `style` / `headerStyle` / `bodyStyle` / `footerStyle` 覆盖样式
- [ ] 表单字段的 schema 沿用通用 colProps 即可（增删改弹窗里通常用 `colProps: { span: 12 }` 表示 2 列布局，不需要 6 屏宽完整覆盖）

## 3. 踩坑清单（修改模板时要绕开/对齐这些）

### 踩坑 1：`getWrapperClass` 双 class 指同一元素

`BasicTable.vue` 的 `getWrapperClass` 计算：
```ts
return [
  'jeecg-basic-table',
  { 'jeecg-basic-table-form-container': useSearchForm }
];
```

这两个 class **挂在同一个外层 `<div>` 上**，不是两个嵌套元素。给 `.jeecg-basic-table-form-container` 加 bg/shadow/padding 等于给整个 BasicTable 外壳加，会和内层"表格 card"重复出现"嵌套卡片"。**正确做法**：把外层做成纯 flex 布局容器（无 bg/shadow），bg/shadow 各自挂到 `.jeecg-basic-form`（搜索 card）和 `.ant-table-wrapper`（表格 card）。

### 踩坑 2：CSS specificity 战争

JeecgBoot 原有规则大量使用 `!important`。覆盖时要么提高特异性，要么靠 CSS 加载顺序兜底。

**典型例子**：`.ant-table-tbody > tr > td` 特异性 (0,2,2)。要中和 `.ant-table-measure-row` 必须用 `.ant-table-tbody > tr.ant-table-measure-row > td` (0,3,2) 才能压过——`.ant-table-measure-row > td` (0,2,1) 在 `!important` 大战里反而输。

### 踩坑 3：AntD `.ant-table-measure-row` 被自定义规则撑高

AntD 在 tbody 里塞了一个隐藏的 `ant-table-measure-row` 用于列宽测量。正常 height:0。但只要给 `.ant-table-tbody > tr > td` 加 padding/font-size，这一行就被撑成 ~26.5px → thead 和首条数据行之间出现"空白间隙"。

**专门中和规则**（保留在 `src/design/ant/table.less`）：
```less
.ant-table-wrapper .ant-table-tbody > tr.ant-table-measure-row,
.ant-table-wrapper .ant-table-tbody > tr.ant-table-measure-row > td {
  height: 0 !important;
  padding: 0 !important;
  line-height: 0 !important;
  font-size: 0 !important;
  border: 0 !important;
}
```

### 踩坑 4：AntD 表格 header/body 宽度不一致

AntD 在 scroll 模式（`scroll: { y: ... }`）下把 `<table>` 拆成两个独立元素 `.ant-table-header` 和 `.ant-table-body`，给 body 留垂直滚动条槽 → body 比 header 窄几像素，右侧出现"漏出一个 margin"的视觉空隙。

**修法**：
- `.ant-table-container/.ant-table-content/.ant-table-body { overflow-y: hidden !important }` 抑制垂直滚动条槽
- 同时 `overflow-x: auto !important` 保留横向滚动（超宽列必须能滚动查看）
- 不要给 `.ant-table-wrapper` 加 `overflow: hidden` 兜底，会把超宽列直接剪掉看不到

### 踩坑 5：AntD Vue 4 对 `size='large'` 不一定加 `.ant-table-large` 类

`size='small'` 会加 `.ant-table-small`，但 `'large'` 在某些 AntD Vue 4 版本里被当成 'middle' 处理，不加 `.ant-table-large` → CSS 没法靠 `.ant-table-large` 切换"宽松"密度。

**修法**：`settings/index.vue` 的 `setSize` 调完 AntD 的 `table.setProps({size})` 后，**手动给 `table.wrapRef` 挂自定义 class** `.jeecg-table-density-loose` / `.jeecg-table-density-compact`。CSS 规则用这两个自定义 class 控制 padding。

### 踩坑 6：`.ant-input-affix-wrapper > input.ant-input` 双层高度不一致

AntD `<a-input>` 在某些场景（带 prefix/suffix/clear-icon）下渲染嵌套结构：
```
<span class="ant-input-affix-wrapper">  ← 38px (外层、有边框、bg)
  <input class="ant-input" />            ← 默认 height:auto，只占文字高 ~20px
</span>
```

如果给 `.ant-input` 写 `height: auto`，内层 input 高度只是文字行高 → DOM 检查时看到内层 ~20px、外层 38px，焦点态/点击区域都会有怪异感。

**修法**：让内层 input `height: 100% + width: 100% + border: 0 + padding: 0 + box-shadow: none + outline: none`，所有可视样式（边框/背景/焦点光晕）都由外层 wrapper 承担。

### 踩坑 7：`useListPage` 的 deep merge 覆盖优先级

`useListPage.ts` 把页面传入的 `tableProps` 用 `lodash.merge` 深合并到 `defaultTableProps`。如果你在 `useTableForm.getFormProps` 里注入默认值（比如 `autoAdvancedCol: 2`），它们会被 `...formConfig` spread 后置覆盖——因为 `formConfig` 已经是 deep-merge 后的成品。

**修法**：要改默认行为，直接改 `useListPage.ts:251-319` 的 `defaultTableProps.formConfig` 源默认值。

### 踩坑 8：`autoAdvancedCol` 与 actionCol 排序冲突

`BasicForm.vue` 模板把 v-for 渲染的字段 col 和 `<FormAction>` actionCol 都放进同一个 `<a-row>`，DOM 顺序固定 `[f1, f2, ..., actionCol]`。点开"高级筛选"展开时所有字段都 `display: block`，actionCol 自然跑到最后 → 第 1 行变成 3 个字段一起挤。

**修法**：CSS flex `order` 强制重排视觉顺序：
```less
.jeecg-basic-form--advanced > .ant-row {
  > .ant-col:last-of-type { order: 1 !important; }       /* actionCol 锁第 1 行末 */
  > .ant-col:nth-of-type(n+3):not(:last-of-type) {
    order: 2 !important;                                  /* 高级字段换第 2 行 */
  }
}
```

并且要在 `BasicForm.vue` 的 `getFormClass` 里根据 `advanceState.isAdvanced` 加 `--advanced` modifier class。

### 踩坑 9：`useAdvanced` 折叠动画滞后

`useAdvanced.ts` 用 `useDebounceFn(updateAdvanced, 30)`，toggle 后 30ms 才更新各字段的 `schema.isAdvanced` → 折叠时字段"先保持显示几百毫秒再消失"的滞后动画。

**修法**：`handleToggleAdvanced` 在切完 `advanceState.isAdvanced` 后**立即同步调用 `updateAdvanced()`**，不等 debounce 触发。

### 踩坑 10：dashed 分隔线与 dropdown 浮层冲突

想用 `::before` + `width: 200vw` + `.ant-row { overflow: hidden }` 实现"分隔线随 row 宽自动裁切"，但 AntD Select/DatePicker 的 popup 浮层在 JeecgBoot 配置下挂在 `.ant-row`（或它的子节点）里 → popup 也被一起剪了，下拉显示不全。

**修法**：
- 不要给 `.ant-row` 加 `overflow: hidden`
- dashed 线 `::before` 用 `width: 100vw + max-width: calc(100vw - 200px)` 兜底足够覆盖 row 宽，溢出部分落在浅色页面背景上肉眼几乎不可见
- 或者更彻底：给 Select 配 `getPopupContainer: () => document.body` 让 popup 永远脱离搜索区挂到 body

### 踩坑 11：`labelCol` 单 key 覆盖陷阱

页面在 `formConfig.labelCol` 写 `{ xxl: 8 }` 这种偏一个 key 的覆盖，**会和 useListPage 的默认 labelCol deep merge**，结果 xxl 屏宽下 label 占 col 1/3 宽，留给 input 的空间极少。租户套餐就栽在这里。

**模板生成时**：要么不要在页面 `formConfig` 里覆盖 `labelCol`（让 useListPage 默认接管），要么写**完整 6 屏宽**避免合并出意外结果。

### 踩坑 12：TableAction "删除"自动 danger

旧约定要求页面 schema 在 `actions` 数组里显式传 `color: 'error'` 或 `danger: true`，但 29 个系统页都没传。**新约定**：共享层 `TableAction.vue` 已加自动识别——label 含"删除"或"delete"（不分大小写）自动注入 `danger: true`。

**模板生成时**：删除动作不需要再写 `danger: true`，写好 `label: '删除'` 就行。

### 踩坑 13：旧 `mobile-popover` 第三个图标

旧 `TableHeader.vue` 模板里有一个 mobile-only 的 `<a-popover>` 包裹的汉堡 `ant-design:menu` 按钮。CSS 上是 `@media(max-width:lg) display:flex`，但桌面端依然会出现第 3 个图标。已从共享层删除。**模板里也不要再生成它**。

### 踩坑 14：Settings 弹窗合并

旧模板生成的 `TableSetting` 平排渲染 4 个独立图标（Redo/Size/Column/FullScreen）。新版统一为 **2 个图标**：
- `RedoSetting`（刷新）独立
- 齿轮 `Popover`（密度切换 + 列设置 + 全屏 三合一）

逻辑层（密度切换/列勾选/全屏开关）复用原 hook，仅渲染结构改了。模板生成的页面**不需要传 `tableSetting.size/setting/fullScreen` 等开关**，sharedlayer 默认行为已足够。

## 4. 验证清单

修改完代码生成模板后，用 JeecgBoot 代码生成器跑一个典型实体（含 5+ 个查询字段、1 个枚举字段、1 个时间字段），生成完成后逐项核：

- [ ] 页面打开后是「上 card 搜索 + 下 card 表格」的两段布局，间距 16px
- [ ] 搜索区：前 2 字段 + 查询/重置/高级筛选 同一行
- [ ] 点击高级筛选：行 1 不变，行 2 出现高级字段，行 1 与行 2 之间一条 dashed 横线
- [ ] 折叠高级筛选：动画无滞后
- [ ] Select 类字段下拉弹窗显示完整，不被剪
- [ ] Input 焦点态：软主色边框 + 浅光晕，没有双层高度不一致
- [ ] 表格：只有水平行线、无竖线、thead 和 tbody 紧贴无空隙、右侧无滚动条槽空隙
- [ ] 表格密度切换：宽松/默认/紧凑都有可见区别
- [ ] 表格超宽：底部出现横向滚动条，可拖动看完整列
- [ ] 表格右上：只有 2 个图标（刷新 + 齿轮）
- [ ] 操作列：ghost 按钮 + ⋯ 方形更多键 + 设计稿 menu-pop 风格下拉
- [ ] 操作列「删除」自动红色，不需在 schema 里写 `danger: true`
- [ ] 新增/编辑 Drawer/Modal 沿用全局 chrome 样式，不被模板硬塞 style 覆盖

## 5. 关键文件路径速查

新 UI 落地的所有修改（按文件分类）：

| 文件 | 作用 |
|---|---|
| `src/design/ant/table.less` | 表格 layout/density/边框/滚动条所有规则 |
| `src/design/ant/index.less` | 搜索区 layout/高级筛选 dashed 线/input focus |
| `src/components/Table/src/components/TableAction.vue` | 行操作 row-btn + ⋯ + auto-danger |
| `src/components/Table/src/components/TableHeader.vue` | 表格右上图标（删 mobile-popover） |
| `src/components/Table/src/components/settings/index.vue` | 刷新+齿轮 + 自定义 density class |
| `src/components/Table/src/hooks/useTableForm.ts` | BasicTable 搜索表单默认值 |
| `src/components/Form/src/BasicForm.vue` | `--advanced` modifier class |
| `src/components/Form/src/hooks/useAdvanced.ts` | 折叠同步、actionSpan 计算 |
| `src/hooks/system/useListPage.ts` | **所有系统页搜索区默认值的源头**（autoAdvancedCol/baseColProps/labelCol） |
| `src/theme/tokens.ts` + `src/theme/variables.less` | 全局 design tokens |

## 6. 待后续决策

- 代码生成模板的实际路径需要先 grep 定位（JeecgBoot 模板在 backend 还是 frontend？是否在 jeecg-boot/jimureport-spring-boot/... 下？）
- 模板修改完应该 run 一次端到端代码生成（任意业务实体）作为冒烟测试
- 是否需要把"新 UI 规约" + "踩坑清单"作为 README 或 ai-redesign-workflow.md 的附录长期维护

---

本 spec 由 `feat/ui-redesign` 分支多次返工调试经验沉淀而来，对应 commit 链：从 `c111b5b8`（合并单行）到 `cc54f19f`（dashed/折叠/labelCol 三连修）共约 30 个 commit。
