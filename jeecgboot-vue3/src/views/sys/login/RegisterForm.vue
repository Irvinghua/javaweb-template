<template>
  <template v-if="getShow">
    <LoginFormTitle />

    <Form :model="formData" :rules="getFormRules" ref="formRef">

      <!-- 账号 -->
      <FormItem name="account">
        <div class="rf-field" :class="{ 'rf-field--focused': focusedField === 'account' }">
          <svg class="rf-field-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
          <Input
            class="rf-control fix-auto-fill"
            v-model:value="formData.account"
            :placeholder="t('sys.login.userName')"
            :bordered="false"
            @focus="focusedField = 'account'"
            @blur="focusedField = ''"
          />
        </div>
      </FormItem>

      <!-- 手机号 -->
      <FormItem name="mobile">
        <div class="rf-field" :class="{ 'rf-field--focused': focusedField === 'mobile' }">
          <svg class="rf-field-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <rect x="5" y="2" width="14" height="20" rx="2"/>
            <line x1="12" y1="18" x2="12.01" y2="18"/>
          </svg>
          <Input
            v-model:value="formData.mobile"
            :placeholder="t('sys.login.mobile')"
            class="rf-control fix-auto-fill"
            :bordered="false"
            @focus="focusedField = 'mobile'"
            @blur="focusedField = ''"
          />
        </div>
      </FormItem>

      <!-- 短信验证码 -->
      <FormItem name="sms">
        <div class="rf-field rf-field--with-suffix" :class="{ 'rf-field--focused': focusedField === 'sms' }">
          <svg class="rf-field-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <path d="m22 4-10 10.01-3-3"/>
          </svg>
          <CountdownInput
            v-model:value="formData.sms"
            :placeholder="t('sys.login.smsCode')"
            :sendCodeApi="sendCodeApi"
            class="rf-control rf-control--countdown fix-auto-fill"
            :bordered="false"
            @focus="focusedField = 'sms'"
            @blur="focusedField = ''"
          />
        </div>
      </FormItem>

      <!-- 密码（强度计） -->
      <FormItem name="password">
        <div class="rf-field" :class="{ 'rf-field--focused': focusedField === 'password' }">
          <svg class="rf-field-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <rect x="3" y="11" width="18" height="11" rx="2"/>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
          </svg>
          <StrengthMeter
            v-model:value="formData.password"
            :placeholder="t('sys.login.password')"
            class="rf-control rf-control--strength"
            :bordered="false"
            @focus="focusedField = 'password'"
            @blur="focusedField = ''"
          />
        </div>
      </FormItem>

      <!-- 确认密码 -->
      <FormItem name="confirmPassword">
        <div class="rf-field" :class="{ 'rf-field--focused': focusedField === 'confirmPassword' }">
          <svg class="rf-field-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <rect x="3" y="11" width="18" height="11" rx="2"/>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
          </svg>
          <InputPassword
            v-model:value="formData.confirmPassword"
            :placeholder="t('sys.login.confirmPassword')"
            class="rf-control rf-control--password fix-auto-fill"
            :bordered="false"
            @focus="focusedField = 'confirmPassword'"
            @blur="focusedField = ''"
          />
        </div>
      </FormItem>

      <!-- 服务协议勾选 -->
      <FormItem name="policy">
        <Checkbox v-model:checked="formData.policy" class="rf-policy-check">
          {{ t('sys.login.policy') }}
        </Checkbox>
      </FormItem>

      <!-- 注册按钮 -->
      <FormItem>
        <button class="rf-btn-primary" type="button" @click="handleRegister" :disabled="loading">
          <span v-if="loading">注册中…</span>
          <span v-else>{{ t('sys.login.registerButton') }}</span>
        </button>
      </FormItem>

      <!-- 返回登录 -->
      <FormItem>
        <button class="rf-btn-back" type="button" @click="handleBackLogin">
          {{ t('sys.login.backSignIn') }}
        </button>
      </FormItem>
    </Form>
  </template>
</template>

<script lang="ts" setup>
  import { reactive, ref, unref, computed, toRaw } from 'vue';
  import LoginFormTitle from './LoginFormTitle.vue';
  import { Form, Input, Checkbox } from 'ant-design-vue';
  import { StrengthMeter } from '/@/components/StrengthMeter';
  import { CountdownInput } from '/@/components/CountDown';
  import { useI18n } from '/@/hooks/web/useI18n';
  import { useMessage } from '/@/hooks/web/useMessage';
  import { useLoginState, useFormRules, useFormValid, LoginStateEnum, SmsEnum } from './useLogin';
  import { register, getCaptcha } from '/@/api/sys/user';

  const FormItem = Form.Item;
  const InputPassword = Input.Password;
  const { t } = useI18n();
  const { handleBackLogin, getLoginState } = useLoginState();
  const { notification, createErrorModal } = useMessage();
  const formRef = ref();
  const loading = ref(false);
  const focusedField = ref('');

  const formData = reactive({
    account: '',
    password: '',
    confirmPassword: '',
    mobile: '',
    sms: '',
    policy: false,
  });
  const { getFormRules } = useFormRules(formData);
  const { validForm } = useFormValid(formRef);
  const getShow = computed(() => unref(getLoginState) === LoginStateEnum.REGISTER);

  /**
   * 注册
   */
  async function handleRegister() {
    const data = await validForm();
    if (!data) return;
    try {
      loading.value = true;
      const resultInfo = await register(
        toRaw({
          username: data.account,
          password: data.password,
          phone: data.mobile,
          smscode: data.sms,
        })
      );
      if (resultInfo && resultInfo.data.success) {
        notification.success({
          description: resultInfo.data.message || t('sys.api.registerMsg'),
          duration: 3,
        });
        handleBackLogin();
      } else {
        notification.warning({
          message: t('sys.api.errorTip'),
          description: resultInfo.data.message || t('sys.api.networkExceptionMsg'),
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

  //发送验证码的函数
  function sendCodeApi() {
    return getCaptcha({ mobile: formData.mobile, smsmode: SmsEnum.REGISTER });
  }
</script>

<style lang="less" scoped>
  /* 通用输入字段 */
  .rf-field {
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

      .rf-field-icon {
        color: var(--accent);
      }
    }

    &--with-suffix {
      overflow: hidden;
    }
  }

  .rf-field-icon {
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

  .rf-control {
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

    &--password {
      :deep(.ant-input-affix-wrapper) {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 14px 0 42px !important;
        height: 44px;

        input {
          padding: 0 !important;
          height: 100%;
        }
      }
    }

    &--strength {
      :deep(.ant-input-affix-wrapper) {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 14px 0 42px !important;
        height: 44px;
      }
    }

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

  .rf-policy-check {
    font-size: 13px;
    color: var(--ink-600);
  }

  /* 注册按钮 */
  .rf-btn-primary {
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

  /* 返回登录按钮 */
  .rf-btn-back {
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
