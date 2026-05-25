<template>
  <BasicDrawer
    v-bind="$attrs"
    @register="registerDrawer"
    showFooter
    :width="adaptiveWidth"
    :title="getTitle"
    @ok="handleSubmit"
    wrapClassName="menu-drawer-redesign"
  >
    <!-- UI Redesign: 自定义抽屉标题，带菜单图标，匹配设计稿 .dlg-title -->
    <template #title>
      <span class="menu-drawer-title">
        <Icon icon="ant-design:menu-outlined" :size="18" />
        <span class="menu-drawer-title__text">{{ getTitle }}</span>
      </span>
    </template>
    <BasicForm @register="registerForm" class="menuForm menu-drawer-form" />
  </BasicDrawer>
</template>
<script lang="ts" setup>
  import { ref, computed, unref, useAttrs } from 'vue';
  import { BasicForm, useForm } from '/@/components/Form/index';
  import { formSchema, ComponentTypes } from './menu.data';
  import { BasicDrawer, useDrawerInner } from '/@/components/Drawer';
  import { list, saveOrUpdateMenu } from './menu.api';
  import { useDrawerAdaptiveWidth } from '/@/hooks/jeecg/useAdaptiveWidth';
  import { useI18n } from "/@/hooks/web/useI18n";
  import { Icon } from '/@/components/Icon';
  // 声明Emits
  const emit = defineEmits(['success', 'register']);
  const { adaptiveWidth } = useDrawerAdaptiveWidth();
  const attrs = useAttrs();
  const isUpdate = ref(true);
  const menuType = ref(0);
  const isButton = (type) => type === 2;
  const [registerForm, { setProps, resetFields, setFieldsValue, updateSchema, validate, clearValidate }] = useForm({
    // UI Redesign: 2 列网格布局；
    // - labelWidth 88px 与设计稿 .dlg-form .form-row > label 对齐
    // - rowProps.gutter [26, 0] 与设计稿 .dlg-form.cols-2 gap: 16px 26px 的列间距对齐
    //   （行间距由 .ant-form-item margin-bottom 16px 提供）
    baseColProps: { span: 12 },
    labelWidth: 88,
    rowProps: { gutter: [26, 0] },
    schemas: formSchema,
    showActionButtonGroup: false,
  });

  const [registerDrawer, { setDrawerProps, closeDrawer }] = useDrawerInner(async (data) => {
    await resetFields();
    setDrawerProps({ confirmLoading: false });
    isUpdate.value = !!data?.isUpdate;
    menuType.value = data?.record?.menuType;

    //获取下拉树信息
    const treeData = await list();
    updateSchema([
      {
        field: 'parentId',
        // 代码逻辑说明: 【QQYUN-8379】菜单管理页菜单国际化
        componentProps: { treeData: translateMenu(treeData, 'name') },
      },
      {
        field: 'name',
        label: isButton(unref(menuType)) ? '按钮/权限' : '菜单名称',
      },
      {
        field: 'url',
        required: !isButton(unref(menuType)),
        componentProps: {
          onChange: (e) => onUrlChange(e.target.value),
        },
      },
    ]);

    // 无论新增还是编辑，都可以设置表单值
    if (typeof data.record === 'object') {
      let values = { ...data.record };
      setFieldsValue(values);
      onUrlChange(values.url);
    }
    //按钮类型情况下，编辑时候清除一下地址的校验
    if (menuType.value == 2) {
      clearValidate();
    }
    //禁用表单
    setProps({ disabled: !attrs.showFooter });
  });
  //获取弹窗标题
  const getTitle = computed(() => (!unref(isUpdate) ? '新增菜单' : '编辑菜单'));
  //提交事件
  async function handleSubmit() {
    try {
      const values = await validate();
      // iframe兼容
      if (ComponentTypes.IFrame === values.component) {
        values.component = values.frameSrc;
      }
      setDrawerProps({ confirmLoading: true });
      //提交表单
      await saveOrUpdateMenu(values, unref(isUpdate));
      closeDrawer();
      emit('success');
    } finally {
      setDrawerProps({ confirmLoading: false });
    }
  }

  /** url 变化时，动态设置组件名称placeholder */
  function onUrlChange(url) {
    let placeholder = '';
    let httpUrl = url;
    if (url != null && url != '') {
      if (url.startsWith('/')) {
        url = url.substring(1);
      }
      url = url.replaceAll('/', '-');
      // 特殊标记
      url = url.replaceAll(':', '@');
      placeholder = `${url}`;
    } else {
      placeholder = '请输入组件名称';
    }
    updateSchema([{ field: 'componentName', componentProps: { placeholder } }]);
    // 代码逻辑说明: [QQYUN-4058]菜单添加智能化处理------------
    if (httpUrl != null && httpUrl != '') {
      if (httpUrl.startsWith('http://') || httpUrl.startsWith('https://')) {
        setFieldsValue({ component: httpUrl });
      }
    }
  }

  /**
  * 2024-03-06
  * liaozhiyang
  * 翻译菜单名称
  */
  function translateMenu(data, key) {
    if (data?.length) {
      const { t } = useI18n();
      data.forEach((item) => {
        if (item[key]) {
          if (item[key].includes("t('") && t) {
            item[key] = new Function('t', `return ${item[key]}`)(t);
          }
        }
        if (item.children?.length) {
          translateMenu(item.children, key);
        }
      });
    }
    return data;
  }
</script>

<!-- ================================================== -->
<!-- UI Redesign: 菜单表单专属换肤                       -->
<!-- 设计稿参考: jeecgboot-ui/pages/menu.html              -->
<!--   - 顶部 menuType 渲染为 .detail-tabs（下划线 tab）   -->
<!--   - 表单 2 列网格                                      -->
<!--   - 布尔字段渲染为 .seg 胶囊段控件                     -->
<!-- ================================================== -->
<style lang="less">
  // 抽屉头：自定义标题
  .menu-drawer-title {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 15px;
    font-weight: 600;
    color: var(--ink-900);

    .app-iconify,
    svg {
      color: var(--accent);
      flex-shrink: 0;
    }
  }

  // BasicTitle 包裹下，避免外层 BasicTitle 额外样式干扰
  .menu-drawer-redesign {
    .jeecg-basic-title .menu-drawer-title {
      gap: 8px;
    }
  }

  // ----------------------------------------------------
  // 菜单类型：顶部 tabs（设计稿 .detail-tabs）
  // ----------------------------------------------------
  .menu-drawer-form {
    .menu-type-row {
      margin-bottom: 18px;
      padding-bottom: 0;
      border-bottom: 1px solid var(--line);

      // 隐藏标签列“菜单类型”
      .ant-form-item-label {
        display: none;
      }

      .ant-form-item-control-input-content {
        // 让 RadioGroup 占满
        > div {
          width: 100%;
        }
      }

      // 把 RadioButtonGroup 渲染成下划线 tab
      .ant-radio-group {
        display: inline-flex;
        gap: 4px;
        background: transparent;
        border: 0;
        padding: 0;
        margin-bottom: -1px;
      }

      .ant-radio-button-wrapper {
        height: auto;
        line-height: 1.4;
        padding: 10px 14px;
        font-size: 13px;
        color: var(--ink-500);
        font-weight: 500;
        background: transparent !important;
        border: 0 !important;
        border-bottom: 2px solid transparent !important;
        border-radius: 0 !important;
        box-shadow: none !important;

        &::before {
          display: none !important;
        }

        &:hover {
          color: var(--ink-900);
        }

        &-checked {
          color: var(--accent) !important;
          font-weight: 600 !important;
          border-bottom-color: var(--accent) !important;
          background: transparent !important;
        }
      }
    }

    // ----------------------------------------------------
    // 表单整体：字号 / 控件高度 / 标签垂直居中 全部对齐设计稿
    // 设计稿基线: .control { height: 38px; font-size: 13px; border-radius: 10px; padding: 0 12px }
    //            .form-row > label { font-size: 13px; color: var(--ink-700); font-weight: 500 }
    // ----------------------------------------------------
    .ant-form-item {
      margin-bottom: 16px;
      // 标签与输入框垂直居中（默认 align-items: stretch → 标签视觉偏顶部）
      .ant-form-item-row {
        align-items: center;
      }
    }

    // 标签：去掉固定 height、改用 line-height 让 inline-flex 自适应居中
    .ant-form-item-label {
      padding-bottom: 0;
      line-height: 38px;
      > label {
        font-size: 13px;
        color: var(--ink-700);
        font-weight: 500;
        height: 38px;
        line-height: 1.4;
      }
    }

    // 必填星号：靠左、红色
    .ant-form-item-label > label.ant-form-item-required:not(.ant-form-item-required-mark-optional)::before {
      color: var(--bad);
      margin-right: 2px;
    }

    // 控件：高度 38px / 字号 13px / 圆角 10px（与设计稿 .control 完全对齐）
    .ant-input,
    .ant-input-number-input,
    .ant-input-affix-wrapper > input.ant-input {
      font-size: 13px;
    }
    .ant-input,
    .ant-input-affix-wrapper,
    .ant-input-number,
    .ant-select-single .ant-select-selector,
    .ant-tree-select .ant-select-selector {
      height: 38px;
      min-height: 38px;
      border-radius: var(--radius-ctrl, 10px);
      font-size: 13px;
    }
    .ant-select-single .ant-select-selector .ant-select-selection-item,
    .ant-select-single .ant-select-selector .ant-select-selection-placeholder {
      line-height: 36px;
      font-size: 13px;
    }
    .ant-input-number {
      width: 100%;
    }
    .ant-input-number .ant-input-number-input {
      height: 36px;
    }
    // affix-wrapper 内层 input 撑满，撕掉自带 padding/border（沿用全局 search 区方案）
    .ant-input-affix-wrapper > input.ant-input {
      height: 100%;
      padding: 0;
      border: 0;
    }
    .ant-input-affix-wrapper {
      padding: 0 12px;
    }

    // ----------------------------------------------------
    // 普通 RadioButtonGroup（非 menuType）→ 胶囊段控件 .seg
    // 通过 :not(.menu-type-row) 排除顶部 tabs
    // ----------------------------------------------------
    .ant-form-item:not(.menu-type-row) {
      .ant-radio-group {
        display: inline-flex;
        background: var(--surface-3);
        border-radius: 999px;
        padding: 3px;
        gap: 2px;
        border: 0;
        height: 34px;
        align-items: center;
      }

      .ant-radio-button-wrapper {
        height: 26px;
        line-height: 26px;
        padding: 0 16px;
        border: 0 !important;
        background: transparent !important;
        font-size: 12px;
        font-weight: 600;
        color: var(--ink-500);
        border-radius: 999px !important;
        box-shadow: none !important;
        transition: color var(--fast), background-color var(--fast);

        &::before {
          display: none !important;
        }

        &:hover {
          color: var(--ink-900);
        }

        &-checked {
          background: var(--surface) !important;
          color: var(--accent) !important;
          box-shadow: 0 1px 4px rgba(15, 23, 42, 0.1) !important;
        }
      }
    }
  }
</style>
