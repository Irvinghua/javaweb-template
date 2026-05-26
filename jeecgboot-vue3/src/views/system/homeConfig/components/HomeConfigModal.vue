<template>
  <BasicModal
    v-bind="$attrs"
    @register="registerModal"
    :title="getTitle"
    @ok="handleSubmit"
    :width="560"
    wrapClassName="home-config-redesign"
    destroyOnClose
  >
    <!-- UI Redesign: 自定义弹窗标题，带首页图标，匹配设计稿 .dlg-title -->
    <template #title>
      <span class="home-config-title">
        <Icon icon="ant-design:home-outlined" :size="18" />
        <span class="home-config-title__text">{{ getTitle }}</span>
      </span>
    </template>
    <BasicForm @register="registerForm" class="redesign-form home-config-form" />
  </BasicModal>
</template>

<script lang="ts" setup>
  import { computed, ref, unref } from 'vue';
  import { BasicModal, useModalInner } from '/@/components/Modal';
  import { BasicForm, useForm } from '/@/components/Form/index';
  import { formSchema } from '../home.data';
  import { saveOrUpdate } from '../home.api';
  import { Icon } from '/@/components/Icon';
  // Emits声明
  const emit = defineEmits(['register', 'success']);
  const isUpdate = ref(false);
  //表单配置
  const [registerForm, { resetFields, setFieldsValue, validate }] = useForm({
    // UI Redesign: 单列布局 + labelWidth 88px 与 .dlg-form 设计稿对齐
    baseColProps: { span: 24 },
    labelWidth: 88,
    schemas: formSchema,
    showActionButtonGroup: false,
  });
  // UI Redesign: 标题随新增/编辑切换
  const getTitle = computed(() => (unref(isUpdate) ? '编辑首页配置' : '新增首页配置'));
  //表单赋值
  const [registerModal, { setModalProps, closeModal }] = useModalInner(async (data) => {
    //重置表单
    await resetFields();
    setModalProps({ confirmLoading: false });
    isUpdate.value = !!data?.isUpdate;
    if (unref(isUpdate)) {
      const record = {...data.values}
      //表单赋值
      if (record.relationType == 'USER') {
        record.userCode = record.roleCode;
      }
      //表单赋值
      if (record.relationType == 'DEFAULT') {
        record.roleCode = '';
      }
      await setFieldsValue({
        ...record,
      });
    }
  });

  //表单提交事件
  async function handleSubmit() {
    try {
      let values = await validate();
      setModalProps({ confirmLoading: true });
      //提交表单
      if(values.relationType == 'USER'){
        values.roleCode = values.userCode;
      }
      if(values.relationType == 'DEFAULT'){
        values.roleCode = 'DEF_INDEX_ALL';
      }
      await saveOrUpdate(values, isUpdate.value);
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
<!-- UI Redesign: 首页配置弹窗专属换肤                      -->
<!-- 通用部分（字号 / 控件高度 / .form-tabs-row 顶部 tab /   -->
<!--   .seg 段控件）由 .redesign-form 提供                  -->
<!-- 本块只保留：弹窗标题图标                                -->
<!-- ================================================== -->
<style lang="less">
  .home-config-title {
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
