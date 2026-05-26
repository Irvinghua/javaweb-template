<template>
  <template v-if="getShow">
    <LoginFormTitle />

    <!-- Tab 切换行 — 点"账号登录"tab 时切回 LoginForm -->
    <div class="mf-tabs" role="tablist">
      <button class="mf-tab" role="tab" type="button" @click="handleBackLogin">账号登录</button>
      <button class="mf-tab mf-tab--active" role="tab" type="button">手机登录</button>
    </div>

    <Form :model="formData" :rules="getFormRules" ref="formRef">

      <!-- 手机号 -->
      <FormItem name="mobile">
        <div class="mf-field" :class="{ 'mf-field--focused': focusedField === 'mobile' }">
          <svg class="mf-field-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <rect x="5" y="2" width="14" height="20" rx="2"/>
            <line x1="12" y1="18" x2="12.01" y2="18"/>
          </svg>
          <Input
            v-model:value="formData.mobile"
            :placeholder="t('sys.login.mobile')"
            class="mf-control fix-auto-fill"
            :bordered="false"
            @focus="focusedField = 'mobile'"
            @blur="focusedField = ''"
          />
        </div>
      </FormItem>

      <!-- 短信验证码 -->
      <FormItem name="sms">
        <div class="mf-field mf-field--with-suffix" :class="{ 'mf-field--focused': focusedField === 'sms' }">
          <svg class="mf-field-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <path d="m22 4-10 10.01-3-3"/>
          </svg>
          <CountdownInput
            v-model:value="formData.sms"
            :placeholder="t('sys.login.smsCode')"
            :sendCodeApi="sendCodeApi"
            class="mf-control mf-control--countdown fix-auto-fill"
            :bordered="false"
            @focus="focusedField = 'sms'"
            @blur="focusedField = ''"
          />
        </div>
      </FormItem>

      <!-- 登录按钮 -->
      <FormItem>
        <button class="mf-btn-primary" type="button" @click="handleLogin" :disabled="loading">
          <span v-if="loading">登录中…</span>
          <span v-else>{{ t('sys.login.loginButton') }}</span>
        </button>
      </FormItem>
    </Form>

    <!-- 服务协议 -->
    <div class="mf-agreement">
      <span>登录即代表您同意 <a href="#" class="mf-agreement-link">《服务协议》</a> 和 <a href="#" class="mf-agreement-link">《隐私政策》</a></span>
    </div>
  </template>
</template>

<script lang="ts" setup>
  import { reactive, ref, computed, unref, toRaw } from 'vue';
  import { Form, Input } from 'ant-design-vue';
  import { CountdownInput } from '/@/components/CountDown';
  import LoginFormTitle from './LoginFormTitle.vue';
  import { useI18n } from '/@/hooks/web/useI18n';
  import { useMessage } from '/@/hooks/web/useMessage';
  import { useLoginState, useFormRules, useFormValid, LoginStateEnum, SmsEnum } from './useLogin';
  import { useUserStore } from '/@/store/modules/user';
  import { getCaptcha } from '/@/api/sys/user';

  const FormItem = Form.Item;
  const { t } = useI18n();
  const { handleBackLogin, getLoginState } = useLoginState();
  const { getFormRules } = useFormRules();
  const { notification, createErrorModal } = useMessage();
  const userStore = useUserStore();
  const formRef = ref();
  const loading = ref(false);
  const focusedField = ref('');

  const formData = reactive({
    mobile: '',
    sms: '',
  });
  const { validForm } = useFormValid(formRef);
  const getShow = computed(() => unref(getLoginState) === LoginStateEnum.MOBILE);

  /**
   * 登录
   */
  async function handleLogin() {
    const data = await validForm();
    if (!data) return;
    try {
      loading.value = true;
      const userInfo = await userStore.phoneLogin(
        toRaw({
          mobile: data.mobile,
          captcha: data.sms,
          mode: 'none', //不要默认的错误提示
        })
      );
      if (userInfo) {
        notification.success({
          message: t('sys.login.loginSuccessTitle'),
          description: `${t('sys.login.loginSuccessDesc')}: ${userInfo.realname}`,
          duration: 3,
        });
      }
    } catch (error) {
      notification.error({
        message: t('sys.api.errorTip'),
        description: error.message || t('sys.api.networkExceptionMsg'),
        duration: 3,
      });
    } finally {
      loading.value = false;
    }
  }

  //倒计时执行前的函数
  function sendCodeApi() {
    // 代码逻辑说明: 【issues/8567】严重：修改密码存在水平越权问题：登录应该用登录模板不应该用忘记密码的模板---
    return getCaptcha({ mobile: formData.mobile, smsmode: SmsEnum.LOGIN });
  }
</script>

<style lang="less" scoped>
  /* Tab 行 */
  .mf-tabs {
    display: flex;
    gap: 24px;
    border-bottom: 1px solid var(--line);
    margin-bottom: 24px;
  }

  .mf-tab {
    border: 0;
    background: transparent;
    padding: 10px 0;
    font-family: inherit;
    font-size: 14.5px;
    font-weight: 500;
    color: var(--ink-500);
    cursor: pointer;
    position: relative;
    transition: color var(--fast);
    margin-bottom: -1px;
    outline: none;

    &:hover {
      color: var(--ink-900);
    }

    &--active {
      color: var(--ink-900);
      font-weight: 600;

      &::after {
        content: '';
        position: absolute;
        left: 0;
        right: 0;
        bottom: -1px;
        height: 2px;
        background: var(--accent);
        border-radius: 1px;
      }
    }
  }

  /* 通用输入字段 */
  .mf-field {
    position: relative;
    display: flex;
    align-items: center;
    background: rgba(255, 255, 255, 0.7);
    border: 1px solid rgba(15, 23, 42, 0.08);
    border-radius: 10px;
    transition:
      background-color var(--fast),
      border-color var(--fast),
      box-shadow var(--fast);

    &--focused {
      background: #fff;
      border-color: var(--accent);
      box-shadow: 0 0 0 3px var(--accent-50);

      .mf-field-icon {
        color: var(--accent);
      }
    }

    &--with-suffix {
      overflow: hidden;
    }
  }

  .mf-field-icon {
    position: absolute;
    left: 14px;
    width: 17px;
    height: 17px;
    color: var(--ink-400);
    pointer-events: none;
    transition: color var(--fast);
    flex-shrink: 0;
    z-index: 1;
  }

  .mf-control {
    :deep(.ant-input),
    :deep(input) {
      height: 44px;
      padding: 0 14px 0 42px !important;
      background: transparent !important;
      border: none !important;
      box-shadow: none !important;
      font-size: 14px;
      color: var(--ink-900);

      &::placeholder {
        color: var(--ink-400);
      }
    }

    /* CountdownInput 特殊处理 */
    &--countdown {
      flex: 1;
      :deep(.ant-input-group) {
        display: flex;
      }
      :deep(.ant-input-group-addon) {
        background: transparent;
        border: none;
        border-left: 1px solid rgba(15, 23, 42, 0.08);
        padding: 0;

        button {
          height: 44px;
          border: none !important;
          border-radius: 0 10px 10px 0;
          background: rgba(255, 255, 255, 0.5);
          color: var(--accent);
          font-weight: 600;
          font-size: 13px;
          white-space: nowrap;
          padding: 0 16px;
          cursor: pointer;
          transition: background-color var(--fast);
          box-shadow: none !important;

          &:hover {
            background: #fff;
          }

          &:disabled {
            color: var(--ink-400);
            cursor: not-allowed;
            background: rgba(241, 243, 248, 0.7);
          }
        }
      }
    }

    :deep(.ant-input:focus),
    :deep(.ant-input-affix-wrapper-focused) {
      box-shadow: none !important;
    }
  }

  :deep(.ant-form-item) {
    margin-bottom: 14px;
  }

  /* 主登录按钮 */
  .mf-btn-primary {
    width: 100%;
    height: 48px;
    background: var(--accent);
    color: #fff;
    border: 0;
    border-radius: 10px;
    font-family: inherit;
    font-size: 15px;
    font-weight: 600;
    letter-spacing: 4px;
    cursor: pointer;
    box-shadow: 0 10px 22px rgba(91, 108, 255, 0.32);
    transition:
      background-color var(--fast),
      box-shadow var(--fast),
      transform var(--fast);
    margin-top: 8px;

    &:hover {
      background: var(--accent-600);
      box-shadow: 0 14px 28px rgba(91, 108, 255, 0.4);
    }

    &:active {
      transform: translateY(1px);
    }

    &:disabled {
      opacity: 0.7;
      cursor: not-allowed;
      transform: none;
    }
  }

  /* 服务协议 */
  .mf-agreement {
    margin-top: 18px;
    padding-top: 16px;
    border-top: 1px solid var(--line);
    font-size: 12px;
    color: var(--ink-500);
    line-height: 1.55;
    text-align: center;
  }

  .mf-agreement-link {
    color: var(--accent);
    text-decoration: none;

    &:hover {
      text-decoration: underline;
    }
  }
</style>
