<template>
  <div class="lft-header">
    <h2 class="lft-title">{{ titleText }}</h2>
    <p class="lft-sub">{{ subText }}</p>
  </div>
</template>

<script lang="ts" setup>
  import { computed, unref } from 'vue';
  import { useI18n } from '/@/hooks/web/useI18n';
  import { LoginStateEnum, useLoginState } from './useLogin';

  const { t } = useI18n();
  const { getLoginState } = useLoginState();

  const titleText = computed(() => {
    const map: Record<LoginStateEnum, string> = {
      [LoginStateEnum.LOGIN]: '登录',
      [LoginStateEnum.MOBILE]: '手机登录',
      [LoginStateEnum.REGISTER]: '注册账号',
      [LoginStateEnum.RESET_PASSWORD]: '找回密码',
      [LoginStateEnum.QR_CODE]: '扫码登录',
    };
    return map[unref(getLoginState)] ?? '登录';
  });

  const subText = computed(() => {
    const map: Record<LoginStateEnum, string> = {
      [LoginStateEnum.LOGIN]: '请输入您的账号信息以继续',
      [LoginStateEnum.MOBILE]: '请输入手机号与短信验证码',
      [LoginStateEnum.REGISTER]: '填写以下信息完成注册',
      [LoginStateEnum.RESET_PASSWORD]: '通过手机号验证身份后重置密码',
      [LoginStateEnum.QR_CODE]: '使用 APP 扫描二维码登录',
    };
    return map[unref(getLoginState)] ?? '';
  });
</script>

<style lang="less" scoped>
  .lft-header {
    margin-bottom: 24px;
  }
  .lft-title {
    font-size: 24px;
    font-weight: 700;
    color: var(--ink-900);
    margin: 0 0 6px;
    letter-spacing: -0.3px;
    line-height: 1.3;
  }
  .lft-sub {
    color: var(--ink-500);
    font-size: 13.5px;
    margin: 0;
    line-height: 1.5;
  }
</style>
