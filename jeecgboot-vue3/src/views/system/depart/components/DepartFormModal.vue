<template>
  <BasicModal
    :title="title"
    :width="560"
    v-bind="$attrs"
    @ok="handleOk"
    @register="registerModal"
    wrapClassName="depart-form-redesign"
    destroyOnClose
  >
    <!-- UI Redesign: 自定义弹窗标题，带机构图标，匹配设计稿 .dlg-title -->
    <template #title>
      <span class="depart-form-title">
        <Icon icon="ant-design:cluster-outlined" :size="18" />
        <span class="depart-form-title__text">{{ title }}</span>
      </span>
    </template>
    <BasicForm @register="registerForm" class="redesign-form depart-form-modal">
      <template #depPostParentId="{ model, field }">
        <a-tree-select v-model:value="depPostValue" :treeData="treeData" allowClear treeCheckable @select="treeSelect">
          <template #title="{ orgCategory, title }">
            <TreeIcon :orgCategory="orgCategory" :title="title"></TreeIcon>
          </template>
          <template #tagRender="{option}">
            <span style="margin-left: 10px" v-if="orgNameMap[option.id]">{{orgNameMap[option.id]}}</span>
          </template>
        </a-tree-select>
      </template>
    </BasicForm>
  </BasicModal>
</template>

<script lang="ts" setup>
  import { watch, computed, inject, ref, unref, onMounted } from 'vue';

  import { BasicForm, useForm } from '/@/components/Form/index';
  import { BasicModal, useModalInner } from '/@/components/Modal';

  import { saveOrUpdateDepart } from '../depart.api';
  import { useBasicFormSchema, orgCategoryOptions } from '../depart.data';
  import TreeIcon from "@/components/Form/src/jeecg/components/TreeIcon/TreeIcon.vue";
  import { getDepartPathNameByOrgCode } from "@/utils/common/compUtils";
  import { Icon } from '/@/components/Icon';

  const emit = defineEmits(['success', 'register']);
  const props = defineProps({
    rootTreeData: { type: Array, default: () => [] },
  });
  const prefixCls = inject('prefixCls');
  // 当前是否是更新模式
  const isUpdate = ref<boolean>(false);
  // 是否是“添加下级”入口
  const isChildRef = ref<boolean>(false);
  // 当前的弹窗数据
  const model = ref<object>({});
  // UI Redesign: 标题更具体，与设计稿 .dlg-title 「新增部门 / 编辑部门 / 新增下级部门」对齐
  const title = computed(() => {
    if (isUpdate.value) return '编辑部门';
    return isChildRef.value ? '新增下级部门' : '新增部门';
  });
  const treeData = ref<any>([]);
  //上级岗位
  const depPostValue = ref<any>([]);
  //上级岗位名称映射
  const orgNameMap = ref<Record<string, string>>({});

  //注册表单
  const [registerForm, { resetFields, setFieldsValue, validate, updateSchema }] = useForm({
    // UI Redesign: 单列布局 + labelWidth 88 与设计稿 .dlg-form 对齐
    schemas: useBasicFormSchema(treeData).basicFormSchema,
    showActionButtonGroup: false,
    labelWidth: 88,
    baseColProps: { span: 24 },
  });

  // 注册弹窗
  const [registerModal, { setModalProps, closeModal }] = useModalInner(async (data) => {
    await resetFields();
    isUpdate.value = unref(data?.isUpdate);
    // 当前是否为添加子级
    let isChild = unref(data?.isChild);
    isChildRef.value = !!isChild;
    let categoryOptions = isChild ? orgCategoryOptions.child : orgCategoryOptions.root;
    
    if(data.record?.orgCategory && data.record?.orgCategory === '2'){
      categoryOptions = orgCategoryOptions.childDepartPost; 
    }
    if(data.record?.orgCategory && data.record?.orgCategory === '3'){
      categoryOptions = orgCategoryOptions.childPost; 
    }
    if(data.record?.depPostParentId){
      orgNameMap.value[data.record.depPostParentId] = await getDepartPathNameByOrgCode('', '', data.record.depPostParentId);
      depPostValue.value = [data.record.depPostParentId];
    }
    // 隐藏不需要展示的字段
    updateSchema([
      {
        field: 'parentId',
        show: isChild,
        componentProps: {
          // 如果是添加子部门，就禁用该字段
          disabled: isChild,
          treeData: props.rootTreeData,
        },
      },
      {
        field: 'orgCode',
        show: false,
      },
      {
        field: 'orgCategory',
        componentProps: { options: categoryOptions },
      },
    ]);

    let record = unref(data?.record);
    if (typeof record !== 'object') {
      record = {};
    }
    let orgCategory = data.record?.orgCategory;
    let company = orgCategory === '1' || orgCategory === '4';
    delete data.record?.orgCategory;
    // 赋默认值
    record = Object.assign(
      {
        departOrder: 0,
        orgCategory: company?categoryOptions[1].value:categoryOptions[0].value,
      },
      record
    );
    model.value = record;
    await setFieldsValue({ ...record });
  });

  // 提交事件
  async function handleOk() {
    try {
      setModalProps({ confirmLoading: true });
      let values = await validate();
      if(depPostValue.value && depPostValue.value.length > 0){
        values.depPostParentId = depPostValue.value[0];
      }else{
        values.depPostParentId = "";
      }
      //提交表单
      await saveOrUpdateDepart(values, isUpdate.value);
      //关闭弹窗
      closeModal();
      //刷新列表
      emit('success');
    } finally {
      setModalProps({ confirmLoading: false });
    }
  }

  /**
   * 树选中事件
   *
   * @param info
   * @param keys
   */
  async function treeSelect(keys,info) {
    if (info.checkable) {
      //解决闪动问题
      orgNameMap.value[info.id] = "";
      depPostValue.value = [info.value];
      orgNameMap.value[info.id] = await getDepartPathNameByOrgCode(info.orgCode,info.label,info.id);
    } else {
      depPostValue.value = [];
    }
  }
</script>

<style lang="less" scoped>
  :deep(.ant-select-selector .ant-select-selection-item){
    svg {
      display: none !important;
    }
  }
</style>

<!-- UI Redesign: 弹窗标题图标（非 scoped 才能命中 BasicModal title slot） -->
<style lang="less">
  .depart-form-redesign {
    .depart-form-title {
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
  }
</style>