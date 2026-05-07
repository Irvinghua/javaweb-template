<template>
  <BasicModal v-bind="$attrs" @register="registerModal" :title="title" @ok="handleSubmit" width="40%">
    <BasicForm @register="registerForm">
      <template #pwd="{ model, field }">
        <a-row :gutter="8">
          <a-col :span="24">
            <a-input-password v-model:value="model[field]" placeholder="请输入密码" />
          </a-col>
        </a-row>
      </template>
    </BasicForm>
  </BasicModal>
</template>
<script lang="ts" setup>
  import { ref, computed, unref } from 'vue';
  import { BasicModal, useModalInner } from '/@/components/Modal';
  import { BasicForm, useForm } from '/@/components/Form/index';
  import { formSchema } from './datasource.data';
  import { saveOrUpdateDataSource, getDataSourceById } from './datasource.api';
  import { useMessage } from '/@/hooks/web/useMessage';

  const { createMessage } = useMessage();
  // Emits声明
  const emit = defineEmits(['register', 'success']);
  const isUpdate = ref(true);
  //表单配置
  const [registerForm, { getFieldsValue, resetFields, validateFields, setFieldsValue, validate }] = useForm({
    // labelWidth: 150,
    schemas: formSchema,
    showActionButtonGroup: false,
  });
  //表单赋值
  const [registerModal, { setModalProps, closeModal }] = useModalInner(async (data) => {
    //重置表单
    await resetFields();
    setModalProps({ confirmLoading: false });
    isUpdate.value = !!data?.isUpdate;
    if (unref(isUpdate)) {
      //获取详情
      data.record = await getDataSourceById({ id: data.record.id });
      //表单赋值
      await setFieldsValue({
        ...data.record,
      });
    }
  });
  //设置标题
  const title = computed(() => (!unref(isUpdate) ? '新增数据源' : '编辑数据源'));

  //表单提交事件
  async function handleSubmit(v) {
    try {
      let values = await validate();
      setModalProps({ confirmLoading: true });
      //提交表单
      await saveOrUpdateDataSource(values, isUpdate.value);
      //关闭弹窗
      closeModal();
      //刷新列表
      emit('success');
    } finally {
      setModalProps({ confirmLoading: false });
    }
  }
</script>
