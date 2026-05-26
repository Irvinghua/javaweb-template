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
    <BasicForm @register="registerForm" class="menuForm redesign-form menu-drawer-form" />
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
<!-- UI Redesign: 菜单弹窗专属换肤                          -->
<!-- 通用部分（字号/控件高度/段控件/.form-tabs-row 下划线 tab） -->
<!-- 由 src/design/ant/form-redesign.less 提供              -->
<!-- 本块只保留菜单特有: 抽屉头图标                          -->
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
</style>
