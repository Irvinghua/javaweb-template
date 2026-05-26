<template>
  <div class="mini-view">
    <h2 class="mini-title">{{ t('sys.login.forgetPassword') }}</h2>

    <div class="mini-stepper">
      <div class="mini-step" :class="{ 'mini-step--active': activeKey === 1, 'mini-step--done': activeKey > 1 }">
        <div class="mini-step-dot">1</div>
        <span>{{ t('sys.login.authentication') }}</span>
      </div>
      <div class="mini-step-line" :class="{ 'mini-step-line--done': activeKey > 1 }"></div>
      <div class="mini-step" :class="{ 'mini-step--active': activeKey === 2, 'mini-step--done': activeKey > 2 }">
        <div class="mini-step-dot">2</div>
        <span>{{ t('sys.login.resetLoginPassword') }}</span>
      </div>
      <div class="mini-step-line" :class="{ 'mini-step-line--done': activeKey > 2 }"></div>
      <div class="mini-step" :class="{ 'mini-step--active': activeKey === 3 }">
        <div class="mini-step-dot">3</div>
        <span>{{ t('sys.login.resetSuccess') }}</span>
      </div>
    </div>

    <a-form v-if="activeKey === 1" ref="formRef" :model="formData" class="mini-form">
      <a-form-item>
        <div class="mini-field">
          <a-input class="mini-control fix-auto-fill" type="text" :placeholder="t('sys.login.mobile')" v-model:value="formData.mobile" :bordered="false" />
        </div>
      </a-form-item>
      <a-form-item>
        <div class="mini-field mini-field--with-action">
          <a-input class="mini-control fix-auto-fill" type="text" :placeholder="t('sys.login.smsCode')" v-model:value="formData.smscode" :bordered="false" />
          <button v-if="showInterval" class="mini-code-btn" type="button" @click="getLoginCode">{{ t('component.countdown.normalText') }}</button>
          <span v-else class="mini-code-btn mini-code-btn--disabled">{{ t('component.countdown.sendText', [unref(timeRuning)]) }}</span>
        </div>
      </a-form-item>
    </a-form>

    <a-form v-else-if="activeKey === 2" ref="pwdFormRef" :model="pwdFormData" class="mini-form">
      <a-form-item>
        <div class="mini-field">
          <a-input class="mini-control fix-auto-fill" type="password" :placeholder="t('sys.login.passwordPlaceholder')" v-model:value="pwdFormData.password" :bordered="false" />
        </div>
      </a-form-item>
      <a-form-item>
        <div class="mini-field">
          <a-input class="mini-control fix-auto-fill" type="password" :placeholder="t('sys.login.confirmPassword')" v-model:value="pwdFormData.confirmPassword" :bordered="false" />
        </div>
      </a-form-item>
    </a-form>

    <div v-else class="mini-success">
      <div class="mini-success-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M20 6 9 17l-5-5" />
        </svg>
      </div>
      <h3>恭喜您，重置密码成功！</h3>
    </div>

    <div class="mini-actions">
      <button v-if="activeKey === 1 || activeKey === 2" class="mini-btn-primary" type="button" @click="nextStepClick">{{ t('sys.login.nextStep') }}</button>
      <button v-else class="mini-btn-primary" type="button" @click="toLogin">{{ t('sys.login.goToLogin') }}</button>
      <button class="mini-btn-ghost" type="button" @click="goBack">{{ t('sys.login.backSignIn') }}</button>
    </div>
  </div>
  <CaptchaModal @register="captchaRegisterModal" @ok="getLoginCode" />
</template>

<script lang="ts" name="mini-forgotpad" setup>
  import { reactive, ref, toRaw, unref } from 'vue';
  import { useI18n } from '/@/hooks/web/useI18n';
  import { SmsEnum, useLoginState } from '/@/views/sys/login/useLogin';
  import { useMessage } from '/@/hooks/web/useMessage';
  import { getCaptcha, passwordChange, phoneVerify } from '/@/api/sys/user';
  import CaptchaModal from '@/components/jeecg/captcha/CaptchaModal.vue';
  import { useModal } from '@/components/Modal';
  import { ExceptionEnum } from '@/enums/exceptionEnum';

  const [captchaRegisterModal, { openModal: openCaptchaModal }] = useModal();
  const activeKey = ref<number>(1);
  const { t } = useI18n();
  const { handleBackLogin } = useLoginState();
  const { notification, createMessage, createErrorModal } = useMessage();
  const showInterval = ref<boolean>(true);
  const timeRuning = ref<number>(60);
  const timer = ref<any>(null);
  const formRef = ref();
  const pwdFormRef = ref();
  const accountInfo = reactive<any>({});
  const formData = reactive({
    mobile: '',
    smscode: '',
  });
  const pwdFormData = reactive<any>({
    password: '',
    confirmPassword: '',
  });
  const emit = defineEmits(['go-back', 'success', 'register']);

  async function handleNext() {
    if (!formData.mobile) {
      createMessage.warn(t('sys.login.mobilePlaceholder'));
      return;
    }
    if (!formData.smscode) {
      createMessage.warn(t('sys.login.smsPlaceholder'));
      return;
    }
    const resultInfo = await phoneVerify(
      toRaw({
        phone: formData.mobile,
        smscode: formData.smscode,
      })
    );
    if (resultInfo.success) {
      Object.assign(accountInfo, {
        username: resultInfo.result.username,
        phone: formData.mobile,
        smscode: formData.smscode,
      });
      activeKey.value = 2;
      setTimeout(() => {
        pwdFormRef.value.resetFields();
      }, 300);
    } else {
      notification.error({
        message: '错误提示',
        description: resultInfo.message || t('sys.api.networkExceptionMsg'),
        duration: 3,
      });
    }
  }

  async function finishedPwd() {
    if (!pwdFormData.password) {
      createMessage.warn(t('sys.login.passwordPlaceholder'));
      return;
    }
    if (!pwdFormData.confirmPassword) {
      createMessage.warn(t('sys.login.confirmPassword'));
      return;
    }
    if (pwdFormData.password !== pwdFormData.confirmPassword) {
      createMessage.warn(t('sys.login.diffPwd'));
      return;
    }
    const resultInfo = await passwordChange(
      toRaw({
        username: accountInfo.username,
        password: pwdFormData.password,
        smscode: accountInfo.smscode,
        phone: accountInfo.phone,
      })
    );
    if (resultInfo.success) {
      accountInfo.password = pwdFormData.password;
      activeKey.value = 3;
    } else {
      createErrorModal({
        title: t('sys.api.errorTip'),
        content: resultInfo.message || t('sys.api.networkExceptionMsg'),
      });
    }
  }

  function nextStepClick() {
    if (unref(activeKey) == 1) {
      handleNext();
    } else if (unref(activeKey) == 2) {
      finishedPwd();
    }
  }

  function toLogin() {
    emit('success', { username: accountInfo.username, password: accountInfo.password });
    initForm();
  }

  function goBack() {
    emit('go-back');
    handleBackLogin();
    initForm();
  }

  async function getLoginCode() {
    if (!formData.mobile) {
      createMessage.warn(t('sys.login.mobilePlaceholder'));
      return;
    }
    const result = await getCaptcha({ mobile: formData.mobile, smsmode: SmsEnum.FORGET_PASSWORD }).catch((res) => {
      if (res.code === ExceptionEnum.PHONE_SMS_FAIL_CODE) {
        openCaptchaModal(true, {});
      }
    });
    if (result) {
      const TIME_COUNT = 60;
      if (!unref(timer)) {
        timeRuning.value = TIME_COUNT;
        showInterval.value = false;
        timer.value = setInterval(() => {
          if (unref(timeRuning) > 0 && unref(timeRuning) <= TIME_COUNT) {
            timeRuning.value = timeRuning.value - 1;
          } else {
            showInterval.value = true;
            clearInterval(unref(timer));
            timer.value = null;
          }
        }, 1000);
      }
    }
  }

  function initForm() {
    activeKey.value = 1;
    Object.assign(formData, { mobile: '', smscode: '' });
    Object.assign(pwdFormData, { password: '', confirmPassword: '' });
    Object.assign(accountInfo, {});
    if (unref(timer)) {
      clearInterval(unref(timer));
      timer.value = null;
      showInterval.value = true;
    }
    setTimeout(() => {
      formRef.value?.resetFields();
    }, 300);
  }

  defineExpose({
    initForm,
  });
</script>

<style lang="less" scoped>
  .mini-view {
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .mini-title {
    display: inline-block;
    position: relative;
    font-size: 26px;
    font-weight: 800;
    color: var(--ink-900);
    margin: 0 0 8px;
    letter-spacing: -0.4px;

    &::after {
      content: '';
      display: block;
      width: 38px;
      height: 3px;
      margin-top: 8px;
      border-radius: 2px;
      background: var(--accent);
    }
  }

  .mini-stepper {
    display: grid;
    grid-template-columns: auto 1fr auto 1fr auto;
    align-items: center;
    margin: 32px 0 36px;
  }

  .mini-step {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    min-width: 80px;
    color: var(--ink-500);
    font-size: 13.5px;
    font-weight: 500;
    text-align: center;
    white-space: nowrap;

    &--active,
    &--done {
      color: var(--ink-900);
      font-weight: 600;
    }
  }

  .mini-step-dot {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: var(--ink-200);
    color: #fff;
    display: grid;
    place-items: center;
    font-size: 15px;
    font-weight: 700;

    .mini-step--active & {
      background: var(--accent);
      box-shadow: 0 0 0 6px var(--accent-50);
    }

    .mini-step--done & {
      background: var(--accent);
    }
  }

  .mini-step-line {
    height: 2px;
    margin: 0 4px 28px;
    border-radius: 1px;
    background: var(--ink-200);

    &--done {
      background: var(--accent);
    }
  }

  .mini-form {
    :deep(.ant-form-item) {
      margin-bottom: 16px;
    }
  }

  .mini-field {
    display: flex;
    align-items: center;
    min-height: 54px;
    background: rgba(255, 255, 255, 0.65);
    border: 1px solid rgba(15, 23, 42, 0.08);
    border-radius: 12px;
    overflow: hidden;

    &:focus-within {
      background: #fff;
      border-color: var(--accent);
      box-shadow: 0 0 0 3px var(--accent-50);
    }
  }

  .mini-control {
    flex: 1;
    height: 54px;
    padding: 0 16px !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    font-size: 15px;
    color: var(--ink-900);
  }

  .mini-code-btn {
    height: 42px;
    padding: 0 16px;
    margin-right: 6px;
    border: 0;
    border-left: 1px solid var(--line);
    background: transparent;
    color: var(--accent);
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    white-space: nowrap;

    &--disabled {
      color: var(--ink-400);
      cursor: not-allowed;
      display: inline-flex;
      align-items: center;
    }
  }

  .mini-success {
    text-align: center;
    padding: 12px 4px 24px;

    h3 {
      font-size: 22px;
      font-weight: 700;
      color: var(--ink-900);
      margin: 0;
    }
  }

  .mini-success-icon {
    width: 78px;
    height: 78px;
    margin: 0 auto 22px;
    border-radius: 50%;
    background: linear-gradient(135deg, #5bcb99 0%, #2daf7e 100%);
    color: #fff;
    display: grid;
    place-items: center;
    box-shadow: 0 14px 28px rgba(45, 175, 126, 0.32);

    svg {
      width: 40px;
      height: 40px;
    }
  }

  .mini-actions {
    margin-top: auto;
  }

  .mini-btn-primary,
  .mini-btn-ghost {
    width: 100%;
    height: 54px;
    border-radius: 12px;
    font-family: inherit;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
  }

  .mini-btn-primary {
    border: 0;
    background: var(--accent);
    color: #fff;
    letter-spacing: 4px;
    box-shadow: 0 12px 24px rgba(91, 108, 255, 0.32);
  }

  .mini-btn-ghost {
    margin-top: 12px;
    border: 1px solid rgba(15, 23, 42, 0.08);
    background: rgba(255, 255, 255, 0.4);
    color: var(--ink-700);
    letter-spacing: 2px;
  }
</style>
