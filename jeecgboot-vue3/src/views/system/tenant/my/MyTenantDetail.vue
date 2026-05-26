<!--
  我的租户 - 当前租户信息（profile 风格）
  UI Redesign: 按设计稿 my-tenant.html 重做布局，两张 card：
    组织信息（LOGO / 组织名称 / 门牌号 / 组织编号）
    其他信息（所在地 / 所在行业 / 工作地点）
  业务逻辑（initTenant / updateTenantInfo / modal 表单字段）完全不动。
-->
<template>
  <div class="my-tenant-page">
    <!-- ===== 组织信息 ===== -->
    <div class="info-card">
      <div class="info-head">
        <h2>组织信息</h2>
        <div class="sub">当前租户的基础组织资料</div>
      </div>
      <div class="info-body">
        <div class="info-row">
          <span class="info-label">组织 LOGO</span>
          <span class="info-value">
            <JImageUpload v-model:value="formState.companyLogo" @change="handleCompanyLogoChange" />
          </span>
        </div>
        <div class="info-row">
          <span class="info-label">组织名称</span>
          <span class="info-value">{{ formState.name || '--' }}</span>
          <a class="link-action" @click="goUpdate('name')">修改</a>
        </div>
        <div class="info-row">
          <span class="info-label">组织门牌号</span>
          <span class="info-value">
            <span class="id-pill" v-if="formState.houseNumber">{{ formState.houseNumber }}</span>
            <span class="info-value empty" v-else>未设置</span>
          </span>
        </div>
        <div class="info-row">
          <span class="info-label">组织编号(ID)</span>
          <span class="info-value">
            <span class="id-pill" v-if="formState.id">{{ formState.id }}</span>
            <span class="info-value empty" v-else>--</span>
          </span>
        </div>
      </div>
    </div>

    <!-- ===== 其他信息 ===== -->
    <div class="info-card">
      <div class="info-head">
        <h2>其他信息</h2>
        <div class="sub">补充组织的所在地与行业信息</div>
      </div>
      <div class="info-body">
        <div class="info-row">
          <span class="info-label">所在地</span>
          <span class="info-value" :class="{ empty: !formState.companyAddress_dictText }">
            {{ formState.companyAddress_dictText || '未设置' }}
          </span>
          <a class="link-action" @click="goUpdate('companyAddress')">修改</a>
        </div>
        <div class="info-row">
          <span class="info-label">所在行业</span>
          <span class="info-value" :class="{ empty: !formState.trade_dictText }">
            {{ formState.trade_dictText || '未设置' }}
          </span>
          <a class="link-action" @click="goUpdate('trade')">修改</a>
        </div>
        <div class="info-row">
          <span class="info-label">工作地点</span>
          <span class="info-value" :class="{ empty: !formState.workPlace }">
            {{ formState.workPlace || '未设置' }}
          </span>
          <a class="link-action" @click="goUpdate('workPlace')">修改</a>
        </div>
      </div>
    </div>
  </div>

  <!-- 组织名称修改弹窗 -->
  <a-modal v-model:open="modalVisible.name" title="修改组织名称" :width="500" destroy-on-close @ok="doUpdate('name')">
    <a-form ref="manageNameRef" :model="updateInfo" :rules="getManageNameRules">
      <a-form-item name="name" class="form-item-padding">
        <div class="form-group">
          <span class="form-label">
            组织名称
            <span class="txt-middle red">*</span>
          </span>
          <a-input v-model:value="updateInfo.name" />
        </div>
      </a-form-item>
    </a-form>
  </a-modal>

  <!-- 组织所在地弹窗 -->
  <a-modal v-model:open="modalVisible.companyAddress" title="所在地" :width="500" destroy-on-close @ok="doUpdate('companyAddress')">
    <a-form :model="updateInfo">
      <a-form-item name="companyAddress" class="form-item-padding">
        <div style="margin-top: 20px">
          <j-area-select v-model:value="updateInfo.companyAddress" />
        </div>
      </a-form-item>
    </a-form>
  </a-modal>

  <!-- 组织所在行业弹窗 -->
  <a-modal v-model:open="modalVisible.trade" title="设置所在行业" :width="500" destroy-on-close @ok="doUpdate('trade')">
    <a-form :model="updateInfo">
      <a-form-item name="trade" class="form-item-padding">
        <div style="margin-top: 20px">
          <j-dict-select-tag v-model:value="updateInfo.trade" dictCode="trade" />
        </div>
      </a-form-item>
    </a-form>
  </a-modal>

  <!-- 工作地点弹窗 -->
  <a-modal v-model:open="modalVisible.workPlace" title="设置工作地点" :width="500" destroy-on-close @ok="doUpdate('workPlace')">
    <a-form ref="workPlaceRef" :model="updateInfo">
      <a-form-item name="workPlace" class="form-item-padding">
        <div style="margin-top: 20px">
          <a-textarea placeholder="请填写工作地点" v-model:value="updateInfo.workPlace" />
        </div>
      </a-form-item>
    </a-form>
  </a-modal>
</template>
<script lang="ts" name="tenant-my-tenant-list" setup>
  import { onMounted, reactive, ref } from 'vue';
  import { useMessage } from '/@/hooks/web/useMessage';
  import { tenantSaasMessage } from '@/utils/common/compUtils';
  import { getTenantById, saveOrUpdateTenant } from '@/views/system/tenant/tenant.api';
  import { getTenantId } from '@/utils/auth';
  import { getDataByCode, getRealCode, provinceOptions } from '@/components/Form/src/utils/areaDataUtil';
  import { initDictOptions } from '@/utils/dict';
  import { JImageUpload } from '@/components/Form';
  import { defHttp } from '/@/utils/http/axios';
  import JAreaSelect from '/@/components/Form/src/jeecg/components/JAreaSelect.vue';
  import JDictSelectTag from '/@/components/Form/src/jeecg/components/JDictSelectTag.vue';

  const { createMessage } = useMessage();
  const formState = reactive({
    id: '',
    name: '',
    houseNumber: '',
    companyAddress_dictText: '',
    trade_dictText: '',
    workPlace: '',
    createBy: '',
    companyLogo: '',
  });
  let tradeOptions: any[] = [];
  //组织名称ref
  const manageNameRef = ref();
  // modal显示
  const modalVisible = reactive<any>({
    name: false,
    trade: false,
    companyAddress: false,
    workPlace: false,
  });

  // 组织名称检验规则
  const getManageNameRules = {
    name: [{ required: true, message: '组织名称不能为空', trigger: 'blur' }],
  };

  //修改对象
  const updateInfo = reactive<any>({
    name: '',
    trade: '',
    companyAddress: '',
    workPlace: '',
  });

  /**
   * 初始化租户信息
   */
  async function initTenant() {
    let result = await getTenantById({ id: getTenantId() });
    if (result) {
      if (result.companyAddress) {
        formState.companyAddress_dictText = getPcaText(result.companyAddress);
      } else {
        formState.companyAddress_dictText = '';
      }
      if (result.trade) {
        formState.trade_dictText = await getTradeText(result.trade);
      } else {
        formState.trade_dictText = '';
      }
      Object.assign(formState, result);
    }
  }

  /**
   * 获取省市区文本
   * @param code
   */
  function getPcaText(code) {
    let arr = getRealCode(code, 3);
    let provinces: any = provinceOptions.filter((item) => item.value == arr[0]);
    let cities: any[] = getDataByCode(arr[0]);
    let areas: any[] = getDataByCode(arr[1]);
    let str = '';
    if (provinces && provinces.length > 0) {
      str = provinces[0].label;
      if (cities && cities.length > 0) {
        let temp1 = cities.filter((item) => item.value == arr[1]);
        str = str + '/' + temp1[0].label;
        if (areas && areas.length > 0) {
          let temp2 = areas.filter((item) => item.value == arr[2]);
          str = str + '/' + temp2[0].label;
        }
      }
    }
    return str;
  }

  /**
   * 获取行业文本
   *
   * @param trade
   */
  async function getTradeText(trade) {
    if (tradeOptions.length == 0) {
      let options: any = await initDictOptions('trade');
      tradeOptions = options;
    }
    let arr = tradeOptions.filter((item) => item.value == trade);
    if (arr.length > 0) {
      return arr[0].label;
    }
    return '';
  }

  /**
   * 公司logo上传成功事件
   */
  function handleCompanyLogoChange(val) {
    if (val) {
      saveOrUpdateTenant({ id: formState.id, companyLogo: val }, true);
    }
  }

  /**
   * 更新打开弹窗
   */
  function goUpdate(key) {
    modalVisible[key] = true;
    updateInfo[key] = formState[key];
  }

  /**
   * 编辑租户信息
   */
  async function updateTenantInfo(params) {
    return defHttp.put({ url: '/sys/tenant/editOwnTenant', params });
  }

  /**
   * 更新数据
   */
  async function doUpdate(key) {
    if (key == 'name') {
      await manageNameRef.value.validateFields();
    }
    //所在地为空报错
    if (key == 'companyAddress') {
      if (updateInfo[key] instanceof Array) {
        updateInfo[key] = '';
      }
    }
    let params = {
      id: formState.id,
      [key]: updateInfo[key],
    };
    await updateTenantInfo(params);
    initTenant();
    modalVisible[key] = false;
  }

  onMounted(() => {
    //提示信息
    tenantSaasMessage('我的租户');
    initTenant();
  });
</script>
<style lang="less" scoped>
  // ----------------------------------------------------
  // UI Redesign: 设计稿 my-tenant.html .info-card / .info-head / .info-body
  // ----------------------------------------------------
  .my-tenant-page {
    display: flex;
    flex-direction: column;
    gap: 16px;
    padding: 22px 24px;
  }

  .info-card {
    background: var(--surface, #fff);
    border: 1px solid var(--line, rgba(15, 23, 42, 0.07));
    border-radius: var(--radius-card, 18px);
    padding: 0;
    overflow: hidden;
  }

  .info-head {
    padding: 18px 24px;
    border-bottom: 1px solid var(--line, rgba(15, 23, 42, 0.07));

    h2 {
      margin: 0;
      font-size: 15px;
      font-weight: 600;
      color: var(--ink-900);
    }
    .sub {
      font-size: 12px;
      color: var(--ink-400);
      margin-top: 3px;
    }
  }

  .info-body {
    padding: 6px 24px 16px;
  }

  .info-row {
    display: flex;
    align-items: center;
    gap: 18px;
    padding: 16px 0;
    border-bottom: 1px solid var(--line, rgba(15, 23, 42, 0.07));

    &:last-child {
      border-bottom: 0;
    }

    .info-label {
      width: 120px;
      flex-shrink: 0;
      color: var(--ink-500);
      font-size: 13px;
    }

    .info-value {
      flex: 1;
      color: var(--ink-900);
      font-size: 14px;
      font-weight: 500;
      min-width: 0;

      &.empty {
        color: var(--ink-400);
        font-weight: 400;
      }
    }
  }

  .id-pill {
    display: inline-flex;
    align-items: center;
    font-variant-numeric: tabular-nums;
    background: var(--surface-3, #F1F3F8);
    color: var(--ink-700);
    border-radius: 8px;
    padding: 4px 10px;
    font-size: 13px;
    font-weight: 600;
  }

  .link-action {
    color: var(--accent);
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    text-decoration: none;
    padding: 2px 6px;
    border-radius: 4px;

    &:hover {
      background: var(--accent-50, rgba(91, 108, 255, 0.08));
    }
  }

  // 弹窗内 form 元素
  .form-item-padding {
    padding: 0 24px 22px;
  }
  .form-group {
    display: block;
    font-size: 13px;
    width: 100%;

    .form-label {
      color: var(--ink-900);
      font-weight: 600;
      line-height: 29px;
    }
    .txt-middle {
      vertical-align: middle !important;
    }
    .red {
      color: var(--bad);
    }
  }

  // LOGO 上传缩略图：保留原 80×80 大小
  :deep(.ant-upload.ant-upload-select),
  :deep(.ant-upload-list-item-container) {
    width: 80px !important;
    height: 80px !important;
    border: unset !important;
  }
</style>
