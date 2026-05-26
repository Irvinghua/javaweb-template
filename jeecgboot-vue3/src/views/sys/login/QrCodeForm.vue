<template>
  <template v-if="getShow">
    <LoginFormTitle />

    <div class="qf-body">
      <!-- 二维码展示 -->
      <div class="qf-qrcode-wrap">
        <QrCode :value="qrCodeUrl" class="qf-qrcode" :width="200" />
      </div>

      <p class="qf-scan-tip" :class="{ 'qf-scan-tip--success': state === '2' }">
        <svg v-if="state === '2'" class="qf-icon-ok" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M20 6 9 17l-5-5"/>
        </svg>
        {{ scanContent }}
      </p>

      <button class="qf-btn-back" type="button" @click="handleBackLogin">
        {{ t('sys.login.backSignIn') }}
      </button>
    </div>
  </template>
</template>

<script lang="ts" setup>
  import { computed, onMounted, unref, ref, watch } from 'vue';
  import LoginFormTitle from './LoginFormTitle.vue';
  import { QrCode } from '/@/components/Qrcode/index';
  import { useUserStore } from '/@/store/modules/user';
  import { useI18n } from '/@/hooks/web/useI18n';
  import { useLoginState, LoginStateEnum } from './useLogin';
  import { getLoginQrcode, getQrcodeToken } from '/@/api/sys/user';

  const qrCodeUrl = ref('');
  let timer: IntervalHandle;
  const { t } = useI18n();
  const userStore = useUserStore();
  const { handleBackLogin, getLoginState } = useLoginState();
  const state = ref('0');
  const getShow = computed(() => unref(getLoginState) === LoginStateEnum.QR_CODE);
  const scanContent = computed(() => {
    return unref(state) === '0' ? t('sys.login.scanSign') : t('sys.login.scanSuccess');
  });

  //加载二维码信息
  function loadQrCode() {
    state.value = '0';
    getLoginQrcode().then((res) => {
      qrCodeUrl.value = res.qrcodeId;
      if (res.qrcodeId) {
        openTimer(res.qrcodeId);
      }
    });
  }

  //监控扫码状态
  function watchQrcodeToken(qrcodeId) {
    getQrcodeToken({ qrcodeId: qrcodeId }).then((res) => {
      let token = res.token;
      if (token == '-2') {
        //二维码过期重新获取
        loadQrCode();
        clearInterval(timer);
      }
      //扫码成功
      if (res.success) {
        state.value = '2';
        clearInterval(timer);
        setTimeout(() => {
          userStore.qrCodeLogin(token);
        }, 500);
      }
    });
  }

  /** 开启定时器 */
  function openTimer(qrcodeId) {
    watchQrcodeToken(qrcodeId);
    closeTimer();
    timer = setInterval(() => {
      watchQrcodeToken(qrcodeId);
    }, 1500);
  }

  /** 关闭定时器 */
  function closeTimer() {
    if (timer) clearInterval(timer);
  }

  watch(getShow, (v) => {
    if (v) {
      loadQrCode();
    } else {
      closeTimer();
    }
  });
</script>

<style lang="less" scoped>
  .qf-body {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 20px;
    padding: 8px 0 4px;
  }

  .qf-qrcode-wrap {
    padding: 16px;
    background: #fff;
    border-radius: 12px;
    border: 1px solid var(--line);
    box-shadow: var(--shadow-card);
    display: inline-flex;
  }

  .qf-qrcode {
    display: block;
  }

  .qf-scan-tip {
    font-size: 14px;
    color: var(--ink-500);
    margin: 0;
    display: flex;
    align-items: center;
    gap: 6px;
    transition: color var(--fast);

    &--success {
      color: var(--good);
    }
  }

  .qf-icon-ok {
    width: 16px;
    height: 16px;
    flex-shrink: 0;
  }

  .qf-btn-back {
    width: 100%;
    height: 44px;
    background: rgba(255, 255, 255, 0.7);
    border: 1px solid rgba(15, 23, 42, 0.08);
    border-radius: 10px;
    font-family: inherit;
    font-size: 14px;
    font-weight: 500;
    color: var(--ink-600);
    cursor: pointer;
    transition:
      background-color var(--fast),
      color var(--fast);

    &:hover {
      background: #fff;
      color: var(--ink-900);
    }
  }
</style>
