<!--
  UI Redesign: 我的组织 (Tenant Setting)
  按 profile.html "Tab 2：我的组织" 设计稿重做：
    .tenant-redesign 外层
    .org-tile-list 列表，每项 .org-tile (rounded card with hover lift)
      .org-tile-head：org-tile-logo (gradient square) + org-tile-title (name + tag + houseNumber + copy) + status + toggle
      .org-tile-body (展开)：.org-card-block 组织名片 + .org-tile-foot 操作按钮
  业务逻辑（drownClick / copyClick / cancelApplyClick / joinOrRefuseClick / footerClick / 各弹窗）保持不变
-->
<template>
  <div :class="[`${prefixCls}`, 'tenant-redesign']">
    <div class="card org-card">
      <div class="org-card-head">
        <h2>我的组织</h2>
        <span class="spacer"></span>
        <span class="invited-trigger" @click="invitedClick">
          <Icon icon="ant-design:mail-outlined" :size="14" />
          我的受邀信息
          <span class="approved-count" v-if="invitedCount > 0">{{ invitedCount }}</span>
        </span>
      </div>

      <div class="org-tile-list" v-if="dataSource.length > 0">
        <div
          v-for="item in dataSource"
          :key="item.tenantUserId"
          class="org-tile"
          :class="{ open: item.show }"
        >
          <div class="org-tile-head" @click="drownClick(item)">
            <div class="org-tile-logo">{{ getInitial(item.name) }}</div>
            <div class="org-tile-title">
              <div class="name">
                <span class="name-text">{{ item.name }}</span>
                <span class="tag tag-blue" v-if="item.userTenantStatus === '3'">待审核</span>
                <span class="tag tag-orange" v-else-if="item.userTenantStatus === '5'">受邀</span>
              </div>
              <div class="id-line" v-if="item.houseNumber">
                <span>组织门牌号：{{ item.houseNumber }}</span>
                <span class="copy" @click.stop="copyClick(item.houseNumber)" title="复制门牌号">
                  <Icon icon="ant-design:copy-outlined" :size="13" />
                </span>
              </div>
            </div>

            <!-- 状态操作区 -->
            <div class="org-tile-actions" @click.stop>
              <template v-if="item.userTenantStatus === '3'">
                <a class="link-action danger" @click="cancelApplyClick(item.tenantUserId)">取消申请</a>
              </template>
              <template v-else-if="item.userTenantStatus === '5'">
                <a class="link-action" @click="joinOrRefuseClick(item.tenantUserId, '1')">加入</a>
                <a class="link-action danger" @click="joinOrRefuseClick(item.tenantUserId, '4')">拒绝</a>
              </template>
            </div>

            <button class="org-tile-toggle" aria-label="展开">
              <Icon icon="ant-design:down-outlined" :size="14" />
            </button>
          </div>

          <div class="org-tile-body">
            <div class="otb-inner">
              <div class="org-card-block">
                <div class="card-key">组织名片</div>
                <div class="rows">
                  <div class="row">
                    <span class="label">姓名</span>
                    <span class="value">{{ userDetail.realname }}</span>
                  </div>
                  <div class="row">
                    <span class="label">部门</span>
                    <span class="value" :class="{ empty: !userDetail.orgCodeTxt }">
                      {{ userDetail.orgCodeTxt || '未填写' }}
                    </span>
                  </div>
                  <div class="row">
                    <span class="label">职位</span>
                    <span class="value" :class="{ empty: !userDetail.postText }">
                      {{ userDetail.postText || '未填写' }}
                    </span>
                  </div>
                </div>
              </div>
              <div class="org-tile-foot">
                <button
                  class="link-btn-2"
                  :disabled="item.userTenantStatus === '3'"
                  @click="footerClick('editTenant', item)"
                >
                  <Icon icon="ant-design:idcard-outlined" :size="14" />
                  <span>查看租户名片</span>
                </button>
                <button
                  class="link-btn-2 danger"
                  :disabled="item.userTenantStatus === '3'"
                  @click="footerClick('exitTenant', item)"
                >
                  <Icon icon="ant-design:export-outlined" :size="14" />
                  <span>退出租户</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <a-empty v-else description="暂无数据" style="padding: 60px 20px;" />
    </div>
  </div>

  <a-modal v-model:open="tenantVisible" width="400px" wrapClassName="edit-tenant-setting">
    <template #title>
      <div style="font-size: 17px; font-weight: 700">查看名片</div>
      <div style="color: #9e9e9e; margin-top: 10px; font-size: 13px"> 名片是您在该组织下的个人信息，只在本组织中展示。 </div>
    </template>
    <div style="margin-top: 24px; font-size: 13px; padding: 0 24px">
      <div class="font-color75">姓名</div>
      <div class="margin-top6 margin-bottom-16">{{ userDetail.realname }}</div>
      <div>部门</div>
      <div class="margin-top6 margin-bottom-16">{{ userDetail.orgCodeTxt ? userDetail.orgCodeTxt : '未填写' }}</div>
      <div>职位</div>
      <div class="margin-top6 margin-bottom-16">{{ userDetail.postText ? userDetail.postText : '未填写' }}</div>
      <div>工作地点</div>
      <div class="margin-top6 margin-bottom-16">{{ userData.workPlace ? userData.workPlace : '未填写' }}</div>
      <div>工号</div>
      <div class="margin-top6 margin-bottom-16">{{ userDetail.workNo ? userDetail.workNo : '未填写' }}</div>
    </div>
  </a-modal>

  <!-- 退出租户 -->
  <a-modal v-model:open="cancelVisible" width="800" destroy-on-close>
    <template #title>
      <div class="cancellation">
        <Icon icon="ant-design:warning-outlined" style="font-size: 20px;color: red"/>
        退出租户 {{myTenantInfo.name}}
      </div>
    </template>
    <a-form :model="formCancelState" ref="cancelTenantRef">
      <a-form-item name="tenantName">
        <a-row :span="24" style="padding: 20px 20px 0;font-size: 13px">
          <a-col :span="24">
            请输入租户名称
          </a-col>
          <a-col :span="24" style="margin-top: 10px">
            <a-input v-model:value="formCancelState.tenantName" @change="tenantNameChange"/>
          </a-col>
        </a-row>
      </a-form-item>
      <a-form-item name="loginPassword">
        <a-row :span="24" style="padding: 0 20px;font-size: 13px">
          <a-col :span="24">
            请输入您的登录密码
          </a-col>
          <a-col :span="24" style="margin-top: 10px">
            <a-input-password v-model:value="formCancelState.loginPassword" />
          </a-col>
        </a-row>
      </a-form-item>
    </a-form>
    <template #footer>
      <a-button type="primary" @click="handleOutClick" :disabled="outBtnDisabled">确定</a-button>
      <a-button @click="handleCancelOutClick">取消</a-button>
    </template>
  </a-modal>

  <a-modal
    title="变更拥有者"
    v-model:open="owenVisible"
    width="800"
    destroy-on-close
    :cancelButtonProps="{display:'none'}"
    @ok="changeOwen">
      <div style="padding: 20px">
        <a-row :span="24">
          <div class="change-owen">
            只有变更拥有着之后,才能退出
          </div>
        </a-row>
        <a-row :span="24" style="margin-top: 10px">
          <UserSelect v-model:value="tenantOwen" izExcludeMy/>
        </a-row>
      </div>
  </a-modal>

  <!-- begin 我的受邀信息 -->
  <a-modal title="我的受邀信息" v-model:open="invitedVisible" :footer="null">
      <a-row :span="24" class="invited-row">
        <a-col :span="16">
          组织
        </a-col>
        <a-col :span="8">
          操作
        </a-col>
      </a-row>
    <a-row :span="24" class="invited-row-list" v-for="item in invitedList">
      <a-col :span="16">
        {{item.name}}
      </a-col>
      <a-col :span="8">
        <span class="common" @click="joinOrRefuseClick(item.tenantUserId,'1')">加入</span>
        <span class="common refuse" @click="joinOrRefuseClick(item.tenantUserId,'4')">拒绝</span>
      </a-col>
    </a-row>
    <div style="height: 20px"></div>
  </a-modal>
  <!-- end 我的受邀信息 -->
</template>

<script lang="ts" name="tenant-setting" setup>
import { onMounted, ref, unref } from "vue";
import { getTenantListByUserId, cancelApplyTenant, exitUserTenant, changeOwenUserTenant, agreeOrRefuseJoinTenant } from "./UserSetting.api";
import { useUserStore } from "/@/store/modules/user";
import { userExitChangeLoginTenantId } from "/@/utils/common/compUtils";
import {useMessage} from "/@/hooks/web/useMessage";
import { Modal } from 'ant-design-vue';
import UserSelect from '/@/components/Form/src/jeecg/components/userSelect/index.vue';
import {router} from "/@/router";
import { useDesign } from '/@/hooks/web/useDesign';
import { Icon } from '/@/components/Icon';

const { prefixCls } = useDesign('j-user-tenant-setting-container');
//数据源
const dataSource = ref<any>([]);
const userStore = useUserStore();

//数据源
const { createMessage } = useMessage();
//部门字典
const departOptions = ref<any>([]);
//租户编辑是或否隐藏
const tenantVisible = ref<boolean>(false);
//用户数据
const userData = ref<any>([]);
//用户
// UserInfo 类型未声明 workNo / orgCodeTxt / postText，但运行时存在 — 走 any 跳过 TS 报错
const userInfoAny: any = userStore.getUserInfo;
const userDetail = ref({
  realname: userInfoAny.realname,
  workNo: userInfoAny.workNo,
  orgCodeTxt: userInfoAny.orgCodeTxt,
  postText: userInfoAny.postText,
});

/**
 * 取组织名称首字符作为 logo 内容
 */
function getInitial(name: string): string {
  if (!name) return '?';
  const trimmed = name.trim();
  return trimmed.charAt(0).toUpperCase();
}

/**
 * 初始化租户数据
 */
  async function initDataSource() {
  //获取用户数据
    // 代码逻辑说明: [QQYUN-5608]用户导入后，邀请后,被导入人同意即可,新增被邀信息-----------
    getTenantListByUserId({ userTenantStatus: '1,3,5' }).then((res) => {
      if (res.success) {
        if(res.result && res.result.length>0){
          let result = res.result;
          //存放正常和审核中的数组
          let normal:any = [];
          //存放受邀的信息
          let invited:any = [];
          for (let i = 0; i < result.length; i++) {
            let status = result[i].userTenantStatus;
            //状态为邀请的放入invited数组中
            if(status === '5'){
              invited.push(result[i]);
            }
            normal.push(result[i]);
          }
          dataSource.value = normal;
          invitedList.value = invited;
          invitedCount.value = invited.length;
        }else{
          setInitedValue();
        }
      } else {
        setInitedValue();
      }
    });
  }
  function setInitedValue() {
    dataSource.value = [];
    invitedList.value = [];
    invitedCount.value = 0;
  }

  /**
   * 复制门户
   * @param value
   */
  function copyClick(value) {
    // 创建input元素
    const el = document.createElement('input');
    // 给input元素赋值需要复制的文本
    el.setAttribute('value', value);
    // 将input元素插入页面
    document.body.appendChild(el);
    // 选中input元素的文本
    el.select();
    // 复制内容到剪贴板
    document.execCommand('copy');
    // 删除input元素
    document.body.removeChild(el);
    createMessage.success('复制成功');
  };

  /**
   * 取消申请
   * @param id
   */
  function cancelApplyClick(id) {
    Modal.confirm({
      title: '取消申请',
      content: '是否取消申请',
      okText: '确认',
      cancelText: '取消',
      onOk: () => {
        cancelApplyTenant({ tenantId: id }).then((res) => {
          if (res.success) {
            createMessage.success('取消申请成功');
            initDataSource();
          }else{
            createMessage.warning(res.message);
          }
        }).catch((e)=>{
           createMessage.warning(e.message);
        });
      },
    });
  };

  /**
   * 展开关闭事件
   */
  function drownClick(value) {
    if (!value.show) {
      value.show = true;
    } else {
      value.show = false;
    }
  };

  /**
   * 底部文本点击事件
   */
  function footerClick(type, item) {
    if (item.userTenantStatus === '3') return;
    userData.value = item;
    //编辑组织名片
    if (type === 'editTenant') {
      tenantVisible.value = true;
    }else if(type === 'exitTenant'){
      //退出租户
      formCancelState.value = {loginPassword:'', tenantName:''};
      outBtnDisabled.value = true;
      cancelVisible.value = true;
      myTenantInfo.value = item;
    }
  }

  //退出租户弹窗
  const cancelVisible = ref<boolean>(false);
  //退出租户数据
  const formCancelState = ref<any>({});
  //租户数据
  const myTenantInfo = ref<any>({});
  //注销租户弹窗确定按钮是否可以点击
  const outBtnDisabled = ref<boolean>(true);
  //拥有者
  const tenantOwen = ref<string>('');
  //拥有者弹窗
  const owenVisible = ref<boolean>(false);

  /**
   * 租户名称值改变事件
   */
  function tenantNameChange() {
    let name = unref(myTenantInfo).name;
    let tenantName = unref(formCancelState).tenantName;
    if(name === tenantName){
      outBtnDisabled.value = false;
    }else{
      outBtnDisabled.value = true;
    }
  }

  /**
   * 退出确定点击事件
   */
  async function handleOutClick() {
    if(!unref(formCancelState).loginPassword){
        createMessage.warning("请输入登录密码");
        return;
    }
    console.log("myTenantInfo::::",myTenantInfo);
    await exitUserTenant({ id: unref(myTenantInfo).tenantUserId, loginPassword: unref(formCancelState).loginPassword }).then((res) => {
      if (res.success) {
        createMessage.success(res.message);
        cancelVisible.value = false;
        initDataSource();
        // 代码逻辑说明: 【QQYUN-6822】7、登录拥有多个租户身份的用户，退出租户，只剩下一个租户后显示为空---
        userExitChangeLoginTenantId(unref(myTenantInfo).tenantUserId);
      } else {
        if (res.message === 'assignedOwen') {
          //需要指定变更者
          owenVisible.value = true;
          cancelVisible.value = false;
        // 代码逻辑说明: 【QQYUN-5270】名下租户全部退出后，再次登录，提示租户全部冻结。拥有者提示前往注销------------
        }else if(res.message === 'cancelTenant'){
          cancelVisible.value = false;
          let fullPath = router.currentRoute.value.fullPath;
          Modal.confirm({
            title: '您是该组织的拥有者',
            content: '该组织下没有其他成员，需要您前往注销',
            okText: '前往注销',
            okType: 'danger',
            cancelText: '取消',
            onOk: () => {
              if(fullPath === '/system/usersetting'){
                return;
              }
              router.push('/myapps/settings/organization/organMessage/'+unref(myTenantInfo).tenantUserId)
            }
          })
        } else {
          createMessage.warning(res.message);
        }
      }
    }).catch((res) => {
      createMessage.warning(res.message);
    })
  }

  /**
   * 退出租户取消事件
   */
  function handleCancelOutClick() {
    cancelVisible.value = false;
    outBtnDisabled.value = true;
  }

  /**
   * 变更拥有着
   */
  function changeOwen() {
    if(!unref(tenantOwen)){
      createMessage.warning("请选择变更拥有者");
      return;
    }
    changeOwenUserTenant({ userId:unref(tenantOwen), tenantId:unref(myTenantInfo).tenantUserId }).then((res) =>{
      if(res.success){
        createMessage.success(res.message);
        initDataSource();
        // 代码逻辑说明: 【QQYUN-6822】7、登录拥有多个租户身份的用户，退出租户，只剩下一个租户后显示为空---
        userExitChangeLoginTenantId(unref(myTenantInfo).tenantUserId);
      } else {
        createMessage.warning(res.message);
      }
    })
  }

  //邀请数量
  const invitedCount = ref<number>(0);
  //受邀信息
  const invitedList = ref<any>([]);
  //受邀信息弹窗
  const invitedVisible = ref<boolean>(false);

  /**
   * 受邀信息点击事件
   */
  function invitedClick() {
    invitedVisible.value = true;
  }

  /**
   * 加入组织点击事件
   */
  async function joinOrRefuseClick(tenantId,status) {
    await agreeOrRefuseJoinTenant( { tenantId:Number.parseInt(tenantId), status:status });
    initDataSource();
  }

  onMounted(() => {
    initDataSource();
  });

</script>

<style lang="less" scoped>
  // ----------------------------------------------------
  // UI Redesign: profile.html .org-card / .org-tile
  // ----------------------------------------------------
  .tenant-redesign {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .card {
    background: var(--surface, #fff);
    border-radius: var(--radius-card, 18px);
    box-shadow: var(--shadow-card, 0 2px 12px rgba(15, 23, 42, 0.05));
    overflow: hidden;
  }

  .org-card-head {
    display: flex;
    align-items: center;
    padding: 18px 24px;
    border-bottom: 1px solid var(--line, rgba(15, 23, 42, 0.07));

    h2 {
      margin: 0;
      font-size: 15px;
      font-weight: 600;
      color: var(--ink-900);
    }

    .spacer {
      flex: 1;
    }

    .invited-trigger {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 13px;
      color: var(--accent-600, #4f5edb);
      cursor: pointer;
      transition: opacity 0.15s;

      &:hover {
        opacity: 0.8;
      }
    }

    .approved-count {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 18px;
      height: 18px;
      padding: 0 5px;
      border-radius: 9px;
      background: #fde4e4;
      color: #d33;
      font-size: 11px;
      font-weight: 600;
      margin-left: 2px;
    }
  }

  // ---------- Tile ----------
  .org-tile {
    margin: 16px 20px;
    border: 1px solid var(--line, rgba(15, 23, 42, 0.07));
    border-radius: 14px;
    background: var(--surface, #fff);
    overflow: hidden;
    transition: box-shadow 0.2s;

    &:hover {
      box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06);
    }
  }

  .org-tile-head {
    padding: 18px 22px;
    display: flex;
    align-items: center;
    gap: 14px;
    cursor: pointer;
  }

  .org-tile-logo {
    width: 44px;
    height: 44px;
    border-radius: 11px;
    background: linear-gradient(135deg, #5995ff, var(--accent, #5b6cff));
    color: #fff;
    display: grid;
    place-items: center;
    font-weight: 700;
    font-size: 16px;
    flex-shrink: 0;
  }

  .org-tile-title {
    flex: 1;
    min-width: 0;

    .name {
      font-size: 16px;
      font-weight: 700;
      color: var(--ink-900);
      display: flex;
      align-items: center;
      gap: 8px;

      .name-text {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }

    .id-line {
      margin-top: 6px;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-size: 13px;
      color: var(--ink-500);

      .copy {
        cursor: pointer;
        color: var(--ink-400);
        display: inline-flex;
        padding: 2px 4px;
        border-radius: 5px;
        transition: background-color 0.15s, color 0.15s;

        &:hover {
          background: var(--surface-3, #eef0f5);
          color: var(--accent-600);
        }
      }
    }
  }

  .tag {
    display: inline-flex;
    align-items: center;
    height: 20px;
    padding: 0 7px;
    border-radius: 10px;
    font-size: 10.5px;
    font-weight: 500;
    line-height: 1;

    &.tag-blue {
      background: rgba(91, 108, 255, 0.1);
      color: var(--accent-600);
    }

    &.tag-orange {
      background: #fff4e5;
      color: #e58a00;
    }
  }

  .org-tile-actions {
    display: inline-flex;
    align-items: center;
    gap: 16px;
  }

  .link-action {
    color: var(--accent-600, #4f5edb);
    font-size: 13px;
    cursor: pointer;

    &.danger {
      color: #e5484d;
    }

    &:hover {
      text-decoration: underline;
    }
  }

  .org-tile-toggle {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    border: 1px solid var(--line);
    background: var(--surface);
    color: var(--ink-500);
    cursor: pointer;
    display: grid;
    place-items: center;
    transition: background-color 0.15s, transform 0.25s ease;
    padding: 0;
    flex-shrink: 0;

    &:hover {
      background: var(--surface-2, #f7f8fb);
      color: var(--ink-900);
    }
  }

  .org-tile.open .org-tile-toggle {
    transform: rotate(180deg);
  }

  // ---------- Body (expand/collapse) ----------
  .org-tile-body {
    display: grid;
    grid-template-rows: 0fr;
    transition: grid-template-rows 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .org-tile.open .org-tile-body {
    grid-template-rows: 1fr;
  }

  .org-tile-body > .otb-inner {
    overflow: hidden;
  }

  .otb-inner {
    padding: 0 22px 18px;
  }

  // ---------- Card block (组织名片) ----------
  .org-card-block {
    border-top: 1px solid var(--line);
    padding: 16px 0 18px;
    display: grid;
    grid-template-columns: 96px 1fr;
    gap: 0;

    .card-key {
      color: var(--ink-500);
      font-size: 13px;
      padding-top: 5px;
    }

    .rows {
      display: flex;
      flex-direction: column;
    }

    .row {
      display: grid;
      grid-template-columns: 70px 1fr;
      gap: 14px;
      align-items: center;
      padding: 5px 0;

      .label {
        color: var(--ink-500);
        font-size: 13px;
      }

      .value {
        color: var(--ink-900);
        font-size: 14px;
        font-weight: 600;

        &.empty {
          color: var(--ink-400);
          font-weight: 400;
        }
      }
    }
  }

  // ---------- Tile foot (操作按钮) ----------
  .org-tile-foot {
    border-top: 1px solid var(--line);
    padding: 14px 0 2px;
    display: flex;
    gap: 24px;

    .link-btn-2 {
      background: transparent;
      border: 0;
      color: var(--accent-600, #4f5edb);
      font-size: 13px;
      font-weight: 500;
      cursor: pointer;
      font-family: inherit;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 0;
      transition: opacity 0.15s;

      &:hover:not(:disabled) {
        opacity: 0.8;
      }

      &:disabled {
        color: var(--ink-400);
        cursor: not-allowed;
      }

      &.danger:not(:disabled) {
        color: #e5484d;
      }
    }
  }
</style>

<style lang="less">
// 退出/受邀弹窗保留旧样式（这些 Modal 内的 class 全局可见，scoped 不生效）
.cancellation {
  font-size: 16px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 8px;
}

.change-owen {
  font-size: 14px;
  font-weight: 700;
}

.approved-count {
  background: #ffd2d2;
  border-radius: 19px;
  color: red;
  display: inline-block;
  font-weight: 500;
  height: 19px;
  line-height: 18px;
  min-width: 19px;
  padding: 0 6px;
  text-align: center;
}

.invited-row {
  padding: 10px 34px;
}
.invited-row-list {
  padding: 0px 34px;

  .common {
    color: var(--accent-600, #4f5edb);
    cursor: pointer;
  }

  .refuse {
    color: red;
    margin-left: 20px;
  }
}

.margin-top6 {
  margin-top: 6px;
}

.margin-bottom-16 {
  margin-bottom: 16px;
}

.font-color75 {
  color: var(--ink-500);
}
</style>
