<template>
  <BasicModal
    v-bind="$attrs"
    @register="registerModal"
    :title="title"
    @ok="handleSubmit"
    :width="720"
    destroyOnClose
    wrapClassName="tenant-form-redesign"
  >
    <!-- UI Redesign: 自定义弹窗标题，带建筑图标，匹配设计稿 .dlg-title -->
    <template #title>
      <span class="tenant-form-title">
        <Icon icon="ant-design:bank-outlined" :size="18" />
        <span class="tenant-form-title__text">{{ title }}</span>
      </span>
    </template>
    <BasicForm @register="registerForm" class="redesign-form tenant-form" />
  </BasicModal>
</template>
<script lang="ts" setup>
  import { ref, computed, unref } from 'vue';
  import { BasicModal, useModalInner } from '/@/components/Modal';
  import { BasicForm, useForm } from '/@/components/Form/index';
  import { formSchema } from '../tenant.data';
  import { saveOrUpdateTenant, getTenantById } from '../tenant.api';
  import { Icon } from '/@/components/Icon';
  // Emits声明
  const emit = defineEmits(['register', 'success']);
  const isUpdate = ref(true);
  //表单配置
  const [registerForm, { resetFields, setFieldsValue, validate, updateSchema }] = useForm({
    // UI Redesign:
    // - 2 列网格布局 (baseColProps span 12)，与设计稿 .dlg-form.cols-2 一致
    // - rowProps.gutter [26, 0] 对齐 .cols-2 gap: 16px 26px 的列间距（行间距由 .ant-form-item margin-bottom 提供）
    // - labelWidth: 88 与设计稿 .form-row > label 对齐
    schemas: formSchema,
    showActionButtonGroup: false,
    labelWidth: 88,
    baseColProps: { span: 12 },
    rowProps: { gutter: [26, 0] },
  });
  //表单赋值
  const [registerModal, { setModalProps, closeModal }] = useModalInner(async (data) => {
    //重置表单
    await resetFields();
    setModalProps({ confirmLoading: false });
    isUpdate.value = !!data?.isUpdate;
    if (unref(isUpdate)) {
      // 编辑模式下禁用id字段
      updateSchema({ field: 'id', dynamicDisabled: true });
      //获取详情
      data.record = await getTenantById({ id: data.record.id });
      //表单赋值
      await setFieldsValue({
        ...data.record,
      });
    } else {
      updateSchema({ field: 'id', dynamicDisabled: false });
    }
  });
  //设置标题
  const title = computed(() => (!unref(isUpdate) ? '新增租户' : '编辑租户'));
  //表单提交事件
  async function handleSubmit(v) {
    try {
      let values = await validate();
      setModalProps({ confirmLoading: true });
      //提交表单
      await saveOrUpdateTenant(values, isUpdate.value);
      //关闭弹窗
      closeModal();
      //刷新列表
      emit('success');
    } finally {
      setModalProps({ confirmLoading: false });
    }
  }
</script>

<!-- ================================================== -->
<!-- UI Redesign: 租户弹窗专属换肤                          -->
<!-- 通用部分（字号 / 控件高度 / 段控件）由 .redesign-form 提供 -->
<!-- 本块只保留：弹窗标题图标                                -->
<!-- ================================================== -->
<style lang="less">
  .tenant-form-title {
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
</style>
