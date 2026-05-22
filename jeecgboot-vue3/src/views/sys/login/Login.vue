<template>
  <!-- 全屏页面容器 -->
  <!-- [ TODO ] 后期换背景图：把 .login-page 的 background 改成 url('your-bg.jpg') center/cover no-repeat -->
  <div class="login-page">
    <!-- 装饰网格点 -->
    <div class="login-grid-dots" aria-hidden="true"></div>

    <!-- 左侧品牌区 -->
    <div class="login-brand-block" v-if="!sessionTimeout">
      <div class="login-brand-header">
        <div class="login-brand-logo">
          <AppLogo :alwaysShowTitle="false" />
        </div>
        <span class="login-brand-platform">{{ title }}</span>
      </div>
      <h1 class="login-brand-project">欢迎使用<br />企业管理平台</h1>
      <p class="login-brand-slogan">让管理回归本质，让协作更高效。<br />一站式企业级业务管理平台。</p>
    </div>

    <!-- 工具栏（locale / dark-toggle） -->
    <div class="login-toolbar" v-if="!sessionTimeout">
      <AppLocalePicker :showText="false" v-if="showLocale" />
      <AppDarkModeToggle />
    </div>

    <!-- 右侧悬浮登录卡片 -->
    <div class="login-card" :class="{ 'login-card--centered': sessionTimeout }">
      <LoginForm />
      <ForgetPasswordForm />
      <RegisterForm />
      <MobileForm />
      <QrCodeForm />
    </div>

    <!-- 底部版权 -->
    <div class="login-page-foot" aria-hidden="true">© {{ currentYear }} 企业管理平台 · 保留所有权利</div>
  </div>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import { AppLogo } from '/@/components/Application';
  import { AppLocalePicker, AppDarkModeToggle } from '/@/components/Application';
  import LoginForm from './LoginForm.vue';
  import ForgetPasswordForm from './ForgetPasswordForm.vue';
  import RegisterForm from './RegisterForm.vue';
  import MobileForm from './MobileForm.vue';
  import QrCodeForm from './QrCodeForm.vue';
  import { useGlobSetting } from '/@/hooks/setting';
  import { useI18n } from '/@/hooks/web/useI18n';
  import { useDesign } from '/@/hooks/web/useDesign';
  import { useLocaleStore } from '/@/store/modules/locale';
  import { useLoginState, LoginStateEnum } from './useLogin';

  defineProps({
    sessionTimeout: {
      type: Boolean,
    },
  });

  const globSetting = useGlobSetting();
  const { prefixCls } = useDesign('login');
  const { t } = useI18n();
  const localeStore = useLocaleStore();
  const showLocale = localeStore.getShowPicker;
  const title = computed(() => globSetting?.title ?? '');
  const currentYear = new Date().getFullYear();
  const { handleBackLogin } = useLoginState();
  handleBackLogin();
</script>

<style lang="less" scoped>
  /* ============================================================
     登录页容器与布局
     [ TODO ] 换背景图时只需改 .login-page 的 background 属性
     ============================================================ */
  .login-page {
    position: relative;
    min-height: 100vh;
    width: 100%;
    overflow: hidden;
    /* 占位渐变背景（紫蓝色系）—— 后期换成 url(your-bg.jpg) center/cover no-repeat */
    background:
      radial-gradient(ellipse 80% 60% at 80% 50%, rgba(255, 255, 255, 0.55), transparent 60%),
      radial-gradient(ellipse 60% 50% at 10% 80%, rgba(179, 201, 255, 0.55), transparent 65%),
      radial-gradient(ellipse 50% 50% at 30% 20%, rgba(220, 210, 255, 0.7), transparent 60%),
      linear-gradient(135deg, #e9ecff 0%, #dde5ff 35%, #f1ecff 70%, #f6f0ff 100%);

    /* 装饰球 —— 后期换成真实背景图后可删 */
    &::before,
    &::after {
      content: '';
      position: absolute;
      border-radius: 50%;
      pointer-events: none;
      filter: blur(80px);
    }
    &::before {
      width: 520px;
      height: 520px;
      left: 18%;
      bottom: -120px;
      background: radial-gradient(circle, rgba(160, 180, 255, 0.6), transparent 70%);
    }
    &::after {
      width: 420px;
      height: 420px;
      left: 38%;
      top: -100px;
      background: radial-gradient(circle, rgba(210, 180, 255, 0.45), transparent 70%);
    }
  }

  /* 网格点装饰 */
  .login-grid-dots {
    position: absolute;
    inset: 0;
    background-image: radial-gradient(rgba(15, 23, 42, 0.05) 1px, transparent 1.5px);
    background-size: 28px 28px;
    pointer-events: none;
    opacity: 0.6;
  }

  /* 工具栏（locale + dark toggle） */
  .login-toolbar {
    position: absolute;
    top: 16px;
    right: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
    z-index: 10;
  }

  /* ============================================================
     左侧品牌区
     ============================================================ */
  .login-brand-block {
    position: absolute;
    left: 8%;
    top: 50%;
    transform: translateY(-50%);
    max-width: 560px;
    z-index: 2;
  }

  .login-brand-header {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    padding: 6px 14px 6px 8px;
    background: rgba(255, 255, 255, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border-radius: 999px;
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.05);
    margin-bottom: 36px;
  }

  .login-brand-logo {
    width: 28px;
    height: 28px;
    border-radius: 7px;
    background: var(--accent);
    color: #fff;
    display: grid;
    place-items: center;
    flex-shrink: 0;
    overflow: hidden;

    :deep(img),
    :deep(svg) {
      width: 17px;
      height: 17px;
      object-fit: contain;
    }
    /* Hide the title from AppLogo inside the pill */
    :deep(.jeesite-app-logo__title) {
      display: none;
    }
  }

  .login-brand-platform {
    font-weight: 700;
    font-size: 14px;
    color: var(--ink-900);
    letter-spacing: 0.1px;
    white-space: nowrap;
    max-width: 280px;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .login-brand-project {
    font-size: 60px;
    line-height: 1.15;
    font-weight: 800;
    color: var(--ink-900);
    letter-spacing: -1.5px;
    margin: 0 0 24px;
  }

  .login-brand-slogan {
    font-size: 22px;
    line-height: 1.55;
    color: var(--ink-600);
    margin: 0;
    font-weight: 400;
    max-width: 480px;
  }

  /* ============================================================
     右侧悬浮登录卡片
     ============================================================ */
  .login-card {
    position: absolute;
    right: 8%;
    top: 50%;
    transform: translateY(-50%);
    width: 100%;
    max-width: 420px;
    background: rgba(255, 255, 255, 0.78);
    backdrop-filter: blur(18px) saturate(150%);
    -webkit-backdrop-filter: blur(18px) saturate(150%);
    border: 1px solid rgba(255, 255, 255, 0.9);
    border-radius: 20px;
    box-shadow:
      0 24px 60px -12px rgba(40, 40, 90, 0.18),
      0 8px 24px rgba(40, 40, 90, 0.08);
    padding: 40px 40px 36px;
    z-index: 2;

    &--centered {
      position: static;
      transform: none;
      right: auto;
      margin: 80px auto;
    }
  }

  /* 版权底部 */
  .login-page-foot {
    position: absolute;
    left: 0;
    right: 0;
    bottom: 18px;
    text-align: center;
    font-size: 12px;
    color: rgba(15, 23, 42, 0.4);
    z-index: 2;
    pointer-events: none;
  }

  /* ============================================================
     响应式
     ============================================================ */
  @media (max-width: 980px) {
    .login-brand-block {
      position: static;
      transform: none;
      padding: 60px 28px 12px;
      max-width: 100%;
    }
    .login-brand-project {
      font-size: 36px;
    }
    .login-brand-slogan {
      font-size: 16px;
    }
    .login-card {
      position: static;
      transform: none;
      right: auto;
      margin: 24px auto 60px;
      width: calc(100% - 32px);
    }
    .login-page::before,
    .login-page::after {
      display: none;
    }
  }

  @media (prefers-reduced-motion: reduce) {
    * {
      transition: none !important;
      animation: none !important;
    }
  }
</style>
