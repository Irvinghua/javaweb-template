<template>
  <div class="mini-view">
    <div class="mini-title-wrap">
      <h2 class="mini-title">{{ t('sys.login.qrSignInFormTitle') }}</h2>
    </div>

    <div class="mini-qr-wrap">
      <div class="mini-qr-box">
        <QrCode :value="qrCodeUrl" class="mini-qr" :width="200" />
      </div>
      <p class="mini-qr-tip" :class="{ 'mini-qr-tip--success': state === '2' }">
        {{ state === '2' ? t('sys.login.scanSuccess') : t('sys.login.scanSign') }}
      </p>
    </div>

    <button class="mini-btn-ghost" type="button" @click="goBackHandleClick">{{ t('sys.login.backSignIn') }}</button>

    <div class="mini-divider">
      <span>{{ t('sys.login.otherSignIn') }}</span>
    </div>
    <div class="mini-third-row" :class="`${prefixCls}-sign-in-way`">
      <a class="mini-third-btn" href="javascript:;" title="github" @click="onThirdLogin('github')"><GithubFilled /></a>
      <a class="mini-third-btn" href="javascript:;" title="企业微信" @click="onThirdLogin('wechat_enterprise')"><icon-font class="item-icon" type="icon-qiyeweixin3" /></a>
      <a class="mini-third-btn" href="javascript:;" title="钉钉" @click="onThirdLogin('dingtalk')"><DingtalkCircleFilled /></a>
      <a class="mini-third-btn" href="javascript:;" title="微信" @click="onThirdLogin('wechat_open')"><WechatFilled /></a>
    </div>
  </div>
  <ThirdModal ref="thirdModalRef"></ThirdModal>
</template>

<script lang="ts" setup name="mini-code-login">
  import { ref, onUnmounted } from 'vue';
  import { getLoginQrcode, getQrcodeToken } from '/@/api/sys/user';
  import { useUserStore } from '/@/store/modules/user';
  import { QrCode } from '/@/components/Qrcode/index';
  import ThirdModal from '/@/views/sys/login/ThirdModal.vue';
  import { useI18n } from '/@/hooks/web/useI18n';
  import { useDesign } from '/@/hooks/web/useDesign';
  import { GithubFilled, WechatFilled, DingtalkCircleFilled, createFromIconfontCN } from '@ant-design/icons-vue';

  const IconFont = createFromIconfontCN({
    scriptUrl: '//at.alicdn.com/t/font_2316098_umqusozousr.js',
  });
  const { prefixCls } = useDesign('minilogin');
  const { t } = useI18n();
  const qrCodeUrl = ref<string>('');
  let timer: IntervalHandle;
  const state = ref('0');
  const thirdModalRef = ref();
  const userStore = useUserStore();
  const emit = defineEmits(['go-back', 'success', 'register']);

  function loadQrCode() {
    state.value = '0';
    getLoginQrcode().then((res) => {
      qrCodeUrl.value = res.qrcodeId;
      if (res.qrcodeId) {
        openTimer(res.qrcodeId);
      }
    });
  }

  function watchQrcodeToken(qrcodeId) {
    getQrcodeToken({ qrcodeId: qrcodeId }).then((res) => {
      let token = res.token;
      if (token == '-2') {
        loadQrCode();
        clearInterval(timer);
      }
      if (res.success) {
        state.value = '2';
        clearInterval(timer);
        setTimeout(() => {
          userStore.qrCodeLogin(token);
        }, 500);
      }
    });
  }

  function openTimer(qrcodeId) {
    watchQrcodeToken(qrcodeId);
    closeTimer();
    timer = setInterval(() => {
      watchQrcodeToken(qrcodeId);
    }, 1500);
  }

  function closeTimer() {
    if (timer) clearInterval(timer);
  }

  function onThirdLogin(type) {
    thirdModalRef.value.onThirdLogin(type);
  }

  function initFrom() {
    loadQrCode();
  }

  function goBackHandleClick() {
    emit('go-back');
    closeTimer();
  }

  onUnmounted(() => {
    closeTimer();
  });

  defineExpose({
    initFrom,
  });
</script>

<style lang="less" scoped>
  .mini-view {
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .mini-title-wrap {
    text-align: center;
  }

  .mini-title {
    display: inline-block;
    position: relative;
    font-size: 26px;
    font-weight: 800;
    color: var(--ink-900);
    margin: 0;
    letter-spacing: -0.4px;

    &::after {
      content: '';
      display: block;
      width: 38px;
      height: 3px;
      margin: 8px auto 0;
      border-radius: 2px;
      background: var(--accent);
    }
  }

  .mini-qr-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 18px;
    margin: 28px 0 12px;
  }

  .mini-qr-box {
    width: 220px;
    height: 220px;
    padding: 14px;
    background: #fff;
    border: 1px solid var(--line);
    border-radius: 16px;
    box-shadow: 0 8px 22px rgba(40, 40, 90, 0.08);
    display: grid;
    place-items: center;
  }

  .mini-qr-tip {
    margin: 0;
    color: var(--ink-600);
    font-size: 14px;
    text-align: center;

    &--success {
      color: var(--good);
      font-weight: 600;
    }
  }

  .mini-btn-ghost {
    width: 100%;
    height: 54px;
    margin-top: 20px;
    border: 1px solid rgba(15, 23, 42, 0.08);
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.4);
    color: var(--ink-700);
    font-family: inherit;
    font-size: 15px;
    font-weight: 600;
    letter-spacing: 2px;
    cursor: pointer;
  }

  .mini-divider {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 24px 0 14px;
    color: var(--ink-400);
    font-size: 13px;

    &::before,
    &::after {
      content: '';
      flex: 1;
      height: 1px;
      background: var(--line);
    }
  }

  .mini-third-row {
    display: flex;
    justify-content: center;
    gap: 18px;
  }

  .mini-third-btn {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: var(--surface-2);
    border: 1px solid var(--line);
    color: var(--ink-600);
    display: grid;
    place-items: center;
    font-size: 20px;
    text-decoration: none;
    transition:
      transform var(--fast),
      color var(--fast),
      background-color var(--fast);

    &:hover {
      transform: translateY(-2px);
      color: var(--accent);
      background: #fff;
    }
  }
</style>
