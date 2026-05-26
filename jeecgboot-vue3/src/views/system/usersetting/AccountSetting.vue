<!--
  UI Redesign: 账号安全 (Account Setting)
  按 profile.html "Tab 3：账号安全" 设计稿重做：
    .sec-card 卡片，内部多行 .sec-row
    每行：sec-icon (40×40 圆角图标) + sec-meta (label + desc) + sec-value + tag + link-action
  业务逻辑（updatePhone / bindPhone / updateEmail / updatePassWord）保持不变
-->
<template>
  <div :class="[`${prefixCls}`, 'account-security-redesign']">
    <div class="card sec-wrapper">
      <div class="block-title">账户安全 <span class="sub">绑定常用联系方式以确保账户安全</span></div>

      <div class="sec-card">
        <!-- 手机 -->
        <div class="sec-row">
          <div class="sec-row__main">
            <span class="sec-icon sec-icon--phone">
              <Icon icon="ant-design:mobile-outlined" :size="20" />
            </span>
            <div class="sec-meta">
              <div class="sec-label">手机</div>
              <div class="sec-desc">用于登录、找回密码及接收安全通知</div>
            </div>
          </div>
          <span class="sec-value" :class="{ empty: !userDetail.phoneText }">
            {{ userDetail.phoneText || '未绑定' }}
          </span>
          <span class="sec-tag" :class="userDetail.phone ? 'sec-tag--green' : 'sec-tag--gray'">
            {{ userDetail.phone ? '已绑定' : '未绑定' }}
          </span>
          <a class="link-action" @click="updatePhone" v-if="userDetail.phone">修改</a>
          <a class="link-action" @click="bindPhone" v-else>绑定</a>
        </div>

        <!-- 邮箱 -->
        <div class="sec-row">
          <div class="sec-row__main">
            <span class="sec-icon sec-icon--mail">
              <Icon icon="ant-design:mail-outlined" :size="20" />
            </span>
            <div class="sec-meta">
              <div class="sec-label">邮箱</div>
              <div class="sec-desc">用于接收账户通知与重要邮件</div>
            </div>
          </div>
          <span class="sec-value" :class="{ empty: !userDetail.email }">
            {{ userDetail.email || '未填写' }}
          </span>
          <span class="sec-tag" :class="userDetail.email ? 'sec-tag--green' : 'sec-tag--gray'">
            {{ userDetail.email ? '已绑定' : '未绑定' }}
          </span>
          <a class="link-action" @click="updateEmail">{{ userDetail.email ? '修改' : '绑定' }}</a>
        </div>

        <!-- 密码 -->
        <div class="sec-row">
          <div class="sec-row__main">
            <span class="sec-icon sec-icon--lock">
              <Icon icon="ant-design:lock-outlined" :size="20" />
            </span>
            <div class="sec-meta">
              <div class="sec-label">登录密码</div>
              <div class="sec-desc">建议定期更换密码以保障账户安全</div>
            </div>
          </div>
          <span class="sec-value">••••••••</span>
          <span class="sec-tag sec-tag--orange">建议更新</span>
          <a class="link-action" @click="updatePassWord">修改</a>
        </div>
      </div>
    </div>
  </div>

  <UserReplacePhoneModal @register="registerModal" @success="initUserDetail" />
  <UserReplaceEmailModal @register="registerEmailModal" @success="initUserDetail" />
  <UserPasswordModal @register="registerPassModal" @success="initUserDetail" />
  <UserPasswordNotBindPhone @register="registerPassNotBindPhoneModal" @success="initUserDetail" />
  <UserCancellationModal @register="registerCancelModal" />
</template>
<script lang="ts" setup>
  import { onMounted, ref, reactive } from 'vue';
  import { CollapseContainer } from '/@/components/Container';
  import { getUserData } from './UserSetting.api';
  import { useUserStore } from '/@/store/modules/user';
  import UserReplacePhoneModal from './commponents/UserPhoneModal.vue';
  import UserReplaceEmailModal from './commponents/UserEmailModal.vue';
  import UserPasswordModal from './commponents/UserPasswordModal.vue';
  import UserPasswordNotBindPhone from './commponents/UserPasswordNotBindPhone.vue';
  import UserCancellationModal from './commponents/UserCancellationModal.vue';
  import { useModal } from '/@/components/Modal';
  import { WechatFilled } from '@ant-design/icons-vue';
  import { useDesign } from '/@/hooks/web/useDesign';
  import { Icon } from '/@/components/Icon';

  const { prefixCls } = useDesign('j-user-account-setting-container');

  const userDetail = ref<any>([]);
  const userStore = useUserStore();
  const [registerModal, { openModal }] = useModal();
  const [registerEmailModal, { openModal: openEmailModal }] = useModal();
  const [registerPassModal, { openModal: openPassModal }] = useModal();
  const [registerPassNotBindPhoneModal, { openModal: openPassNotBindPhoneModal }] = useModal();
  const [registerCancelModal, { openModal: openCancelModal }] = useModal();

  const wechatData = reactive<any>({
    bindWechat: false,
    name: '昵称',
  });

  /**
   * 初始化用户数据
   */
  function initUserDetail() {
    //获取用户数据
    getUserData().then((res) => {
      if (res.success) {
        userDetail.value = res.result;
        if(res.result.phone){
          userDetail.value.phoneText = res.result.phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2');
        }
      }
    });
  }

  /**
   * 修改手机号
   */
  function updatePhone() {
    openModal(true, {
      record: { phone: userDetail.value.phone, username: userDetail.value.username, id: userDetail.value.id, phoneText: userDetail.value.phoneText },
    });
  }

  /**
   * 绑定手机号
   */
  function bindPhone() {
    openModal(true, {
      record: { username: userDetail.value.username, id: userDetail.value.id },
    });
  }

  /**
   * 修改邮箱
   */
  function updateEmail() {
    openEmailModal(true, {
      record: { email: userDetail.value.email, id: userDetail.value.id },
    });
  }

  /**
   * 密码修改
   */
  function updatePassWord() {
    //存在手机号手机号修改密码
    if(userDetail.value.phone){
      openPassModal(true, {
        record: { username: userDetail.value.username },
      });
    } else {
      //没有手机号走直接修改密码弹窗
      openPassNotBindPhoneModal(true, {
        record: { username: userDetail.value.username },
      });
    }
  }

  /**
   * 手机号解绑
   */
  function unbindPhone() {
    console.log('手机号解绑');
  }

  /**
   * 邮箱解绑
   */
  function unbindEmail() {
    console.log('邮箱解绑');
  }

  /**
   * 邮箱验证
   */
  function checkEmail() {
    console.log('邮箱验证');
  }

  /**
   * 微信绑定解绑事件
   */
  function wechatBind() {
    console.log('微信绑定解绑事件');
  }

  /**
   * 注销事件
   */
  function cancellation() {}

  onMounted(() => {
    initUserDetail();
  });
</script>
<style lang="less" scoped>
  // ----------------------------------------------------
  // UI Redesign: profile.html .sec-card
  // ----------------------------------------------------
  .account-security-redesign {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .card {
    background: var(--surface, #fff);
    border-radius: var(--radius-card, 18px);
    box-shadow: var(--shadow-card, 0 2px 12px rgba(15, 23, 42, 0.05));
  }

  .sec-wrapper {
    padding: 22px 28px 4px;
  }

  .block-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    font-weight: 600;
    color: var(--ink-900);
    margin-bottom: 4px;

    &::before {
      content: '';
      width: 3px;
      height: 14px;
      border-radius: 2px;
      background: var(--accent, #5b6cff);
    }

    .sub {
      font-size: 12px;
      color: var(--ink-400);
      font-weight: 400;
      margin-left: 4px;
    }
  }

  .sec-card {
    padding: 0;
  }

  .sec-row {
    display: grid;
    grid-template-columns: 1fr auto auto auto;
    align-items: center;
    gap: 20px;
    padding: 22px 0;
    border-bottom: 1px solid var(--line, rgba(15, 23, 42, 0.07));

    &:last-child {
      border-bottom: 0;
    }
  }

  .sec-row__main {
    display: flex;
    align-items: center;
    gap: 14px;
    min-width: 0;
  }

  .sec-icon {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    display: grid;
    place-items: center;
    flex-shrink: 0;

    &--phone {
      background: var(--accent-50, rgba(91, 108, 255, 0.08));
      color: var(--accent-600, #4f5edb);
    }

    &--mail {
      background: #fff1e5;
      color: #ea580c;
    }

    &--lock {
      background: #fef3c7;
      color: #d97706;
    }
  }

  .sec-meta {
    display: flex;
    flex-direction: column;
    gap: 3px;
    min-width: 0;
  }

  .sec-label {
    color: var(--ink-900);
    font-size: 14px;
    font-weight: 600;
  }

  .sec-desc {
    color: var(--ink-500);
    font-size: 12.5px;
  }

  .sec-value {
    color: var(--ink-900);
    font-size: 14px;
    font-weight: 500;
    font-variant-numeric: tabular-nums;

    &.empty {
      color: var(--ink-400);
      font-weight: 400;
    }
  }

  .sec-tag {
    display: inline-flex;
    align-items: center;
    height: 22px;
    padding: 0 10px;
    border-radius: 11px;
    font-size: 12px;
    font-weight: 500;
    line-height: 1;
    white-space: nowrap;

    &--green {
      background: #e8f7ee;
      color: #15a052;
    }

    &--gray {
      background: var(--surface-2, #f7f8fb);
      color: var(--ink-500);
    }

    &--orange {
      background: #fff4e5;
      color: #e58a00;
    }
  }

  .link-action {
    color: var(--accent-600, #4f5edb);
    font-size: 13px;
    cursor: pointer;
    transition: color 0.15s;

    &:hover {
      color: var(--accent, #5b6cff);
      text-decoration: underline;
    }
  }

  // Responsive: collapse value/tag under meta on narrow screens
  @media (max-width: 700px) {
    .sec-row {
      grid-template-columns: 1fr auto;
      gap: 10px 12px;
    }

    .sec-value,
    .sec-tag {
      grid-column: 1 / -1;
      justify-self: start;
    }
  }
</style>
