<template>
  <BasicModal
    v-bind="$attrs"
    @register="registerModal"
    :title="getTitle"
    @ok="handleSubmit"
    :width="560"
    destroyOnClose
  >
    <BasicForm @register="registerForm" class="redesign-form position-form" />
  </BasicModal>
</template>
<script lang="ts" setup>
  import { ref, computed, unref } from 'vue';
  import { BasicModal, useModalInner } from '/@/components/Modal';
  import { BasicForm, useForm } from '/@/components/Form/index';
  import { formSchema } from './position.data';
  import { saveOrUpdatePosition, getPositionById } from './position.api';
  // 声明Emits
  const emit = defineEmits(['success', 'register']);
  const isUpdate = ref(true);
  //表单配置
  const [registerForm, { resetFields, setFieldsValue, validate }] = useForm({
    // UI Redesign: 单列布局 + labelWidth 88 与设计稿 .dlg-form 对齐
    schemas: formSchema,
    showActionButtonGroup: false,
    labelWidth: 88,
    baseColProps: { span: 24 },
  });
  //表单赋值
  const [registerModal, { setModalProps, closeModal }] = useModalInner(async (data) => {
    //重置表单
    await resetFields();
    setModalProps({ confirmLoading: false });
    isUpdate.value = !!data?.isUpdate;
    if (unref(isUpdate)) {
      //获取详情
      data.record = await getPositionById({ id: data.record.id });
      //表单赋值
      await setFieldsValue({
        ...data.record,
      });
    }
  });
  //设置标题
  const getTitle = computed(() => (!unref(isUpdate) ? '新增职务级别' : '编辑职务级别'));
  //表单提交事件
  async function handleSubmit() {
    try {
      const values = await validate();
      setModalProps({ confirmLoading: true });
      //提交表单
      await saveOrUpdatePosition(values, isUpdate.value);
      //关闭弹窗
      closeModal();
      //刷新列表
      emit('success');
    } finally {
      setModalProps({ confirmLoading: false });
    }
  }
</script>
