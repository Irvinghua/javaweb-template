<!--
  历史命名沿用 RoleDrawer.vue —— 实际已改为居中 Modal（设计稿: jeecgboot-ui/pages/role.html .dlg-role-form）。
  规则：表单字段 <= 3 个走居中 Modal；> 10 个再走右侧抽屉。
  文件名保留是为了不动 index.vue / TenantRoleList.vue 的 import 路径。
-->
<template>
  <BasicModal
    v-bind="$attrs"
    @register="registerModal"
    :title="getTitle"
    :width="560"
    @ok="handleSubmit"
    destroyOnClose
    wrapClassName="role-modal-redesign"
  >
    <BasicForm @register="registerForm" class="redesign-form role-form" />
  </BasicModal>
</template>
<script lang="ts" setup>
  import { ref, computed, unref, useAttrs } from 'vue';
  import { BasicForm, useForm } from '/src/components/Form';
  import { BasicModal, useModalInner } from '/src/components/Modal';
  import { formSchema } from '../role.data';
  import { saveOrUpdateRole } from '../role.api';
  // 声明Emits
  const emit = defineEmits(['success', 'register']);
  const attrs = useAttrs();
  const isUpdate = ref(true);
  const [registerForm, { setProps, resetFields, setFieldsValue, validate }] = useForm({
    // UI Redesign: labelWidth 88 + 单列布局 与设计稿 .dlg-form 对齐
    labelWidth: 88,
    baseColProps: { span: 24 },
    schemas: formSchema,
    showActionButtonGroup: false,
  });
  const [registerModal, { setModalProps, closeModal }] = useModalInner(async (data) => {
    resetFields();
    isUpdate.value = !!data?.isUpdate;
    setModalProps({ confirmLoading: false });
    if (unref(isUpdate)) {
      setFieldsValue({
        ...data.record,
      });
    }
    //禁用表单（沿用 showFooter=false → 只读 的旧约定，调用方仍传 :showFooter）
    setProps({ disabled: !attrs.showFooter });
  });
  /**
   * 标题
   */
  const getTitle = computed(() => (!unref(isUpdate) ? '新增角色' : '编辑角色'));
  /**
   * 提交
   */
  async function handleSubmit() {
    try {
      const values = await validate();
      setModalProps({ confirmLoading: true });
      //提交表单
      await saveOrUpdateRole(values, isUpdate.value);
      closeModal();
      emit('success');
    } finally {
      setModalProps({ confirmLoading: false });
    }
  }
</script>
