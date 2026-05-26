<!--
  历史命名沿用 TenantUserDrawer.vue —— 实际已改为居中 Modal。
  约定：表单字段 ≤ 较多但不爆炸时走居中 Modal；>10 个且分组明显才用 Drawer。
  文件名保留是为了不动 TenantUserList.vue 的 import 路径。
-->
<template>
  <BasicModal
    @register="registerModal"
    :title="title"
    :width="640"
    destroyOnClose
    @ok="handleSubmit"
    wrapClassName="tenant-user-modal-redesign"
  >
    <BasicForm @register="registerForm" class="redesign-form tenant-user-form" />
  </BasicModal>
</template>

<script lang="ts">
  import { defineComponent, ref, unref, computed } from 'vue';
  import { BasicModal, useModalInner } from '/@/components/Modal';
  import { BasicForm, useForm } from '/@/components/Form';
  import { getUserDepartList } from '../../user/user.api';
  import { tenantUserSchema } from '../tenant.data';
  import { saveOrUpdateTenantUser } from '../tenant.api';

  export default defineComponent({
    name: 'TenantUserDrawer',
    components: {
      BasicModal,
      BasicForm,
    },
    emits: ['success', 'register'],
    setup(_p, { emit }) {
      const status = ref<string>('');
      const isUpdate = ref(false);
      const title = computed(() => {
        return isUpdate.value ? '编辑人员' : '添加人员';
      });

      //表单
      const [registerForm, { setFieldsValue, resetFields, validate, setProps, clearValidate }] = useForm({
        // UI Redesign: 单列布局 + labelWidth 88 与设计稿 .dlg-form 对齐，
        // 表单整体居中（由 Modal 居中 + 表单 baseColProps 全宽，配合 .redesign-form 自带 padding）
        schemas: tenantUserSchema,
        showActionButtonGroup: false,
        labelWidth: 88,
        baseColProps: { span: 24 },
      });

      const showFooter = ref<boolean>(true);
      // 历史命名 registerDrawer/closeDrawer/setDrawerProps —— 实际是 Modal
      const [registerModal, { closeModal, setModalProps }] = useModalInner(async (data) => {
        isUpdate.value = data.isUpdate;
        await resetFields();
        showFooter.value = data?.showFooter ?? true;
        // BasicModal 用 showOkBtn / showCancelBtn 控制底部按钮显示
        setModalProps({ showOkBtn: showFooter.value, showCancelBtn: showFooter.value });
        if (unref(isUpdate)) {
          const userDepart = await getUserDepartList({ userId: data.record.id });
          let departData: any = '';
          if (userDepart && userDepart.length > 0) {
            departData = userDepart.map((item) => item.value);
          }
          let formData = {
            ...data.record,
            selecteddeparts: departData,
            selectedroles: data.record.selectedroles,
          };
          status.value = data.status;
          await setFieldsValue(formData);
        }
        // 隐藏底部时禁用整个表单（详情态）
        setProps({ disabled: !data?.showFooter });
        if (!data?.showFooter) {
          await clearValidate();
        }
      });

      const confirmLoading = ref<boolean>(false);

      //提交事件
      async function handleSubmit() {
        const data: any = await validate();
        if (!data.username) {
          data.username = data.phone;
        }
        data.password = '123456';
        confirmLoading.value = true;
        await saveOrUpdateTenantUser(data, isUpdate.value);
        confirmLoading.value = false;
        emit('success');
        handleClose();
      }

      /**
       * 取消
       */
      function handleClose() {
        closeModal();
      }

      return {
        isUpdate,
        title,
        registerForm,
        registerModal,
        handleSubmit,
        handleClose,
        status,
        confirmLoading,
      };
    },
  });
</script>
