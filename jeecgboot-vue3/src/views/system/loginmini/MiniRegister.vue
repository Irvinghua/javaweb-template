<template>
  <div class="mini-view">
    <h2 class="mini-title">{{ t('sys.login.signUpFormTitle') }}</h2>

    <a-form ref="formRef" :model="formData" class="mini-form">
      <a-form-item>
        <div class="mini-field">
          <Icon class="mini-icon" icon="ant-design:user-outlined" />
          <a-input class="mini-control fix-auto-fill" type="text" :placeholder="t('sys.login.userName')" v-model:value="formData.username" :bordered="false" />
        </div>
      </a-form-item>
      <a-form-item>
        <div class="mini-field">
          <Icon class="mini-icon" icon="ant-design:mobile-outlined" />
          <a-input class="mini-control fix-auto-fill" type="text" :placeholder="t('sys.login.mobile')" v-model:value="formData.mobile" :bordered="false" />
        </div>
      </a-form-item>
      <a-form-item>
        <div class="mini-field">
          <Icon class="mini-icon" icon="ant-design:mail-outlined" />
          <a-input class="mini-control fix-auto-fill" type="text" :placeholder="t('sys.login.smsCode')" v-model:value="formData.smscode" :bordered="false" />
          <button v-if="showInterval" class="mini-code-btn" type="button" @click="getLoginCode">{{ t('component.countdown.normalText') }}</button>
          <span v-else class="mini-code-btn mini-code-btn--disabled">{{ t('component.countdown.sendText', [unref(timeRuning)]) }}</span>
        </div>
      </a-form-item>
      <a-form-item>
        <div class="mini-field">
          <Icon class="mini-icon" icon="ant-design:lock-outlined" />
          <a-input class="mini-control fix-auto-fill" :type="pwdIndex === 'close' ? 'password' : 'text'" :placeholder="t('sys.login.password')" v-model:value="formData.password" :bordered="false" />
          <button class="mini-eye" type="button" @click="pwdClick(pwdIndex === 'open' ? 'close' : 'open')">
            <img :src="pwdIndex === 'open' ? eyeKImg : eyeGImg" alt="" />
          </button>
        </div>
      </a-form-item>
      <a-form-item>
        <div class="mini-field">
          <Icon class="mini-icon" icon="ant-design:lock-outlined" />
          <a-input class="mini-control fix-auto-fill" :type="confirmPwdIndex === 'close' ? 'password' : 'text'" :placeholder="t('sys.login.confirmPassword')" v-model:value="formData.confirmPassword" :bordered="false" />
          <button class="mini-eye" type="button" @click="confirmPwdClick(confirmPwdIndex === 'open' ? 'close' : 'open')">
            <img :src="confirmPwdIndex === 'open' ? eyeKImg : eyeGImg" alt="" />
          </button>
        </div>
      </a-form-item>
      <a-form-item name="policy">
        <a-checkbox v-model:checked="formData.policy" class="mini-policy">{{ t('sys.login.policy') }}</a-checkbox>
      </a-form-item>
    </a-form>

    <div class="mini-actions">
      <button class="mini-btn-primary" type="button" @click="registerHandleClick">{{ t('sys.login.registerButton') }}</button>
      <button class="mini-btn-ghost" type="button" @click="goBackHandleClick">{{ t('sys.login.backSignIn') }}</button>
    </div>
  </div>
  <CaptchaModal @register="captchaRegisterModal" @ok="getLoginCode" />
</template>

<script lang="ts" setup name="mini-register">
  import { ref, reactive, unref, toRaw } from 'vue';
  import { getCaptcha, register } from '/@/api/sys/user';
  import { SmsEnum } from '/@/views/sys/login/useLogin';
  import { useMessage } from '/@/hooks/web/useMessage';
  import eyeKImg from '/@/assets/loginmini/icon/icon-eye-k.png';
  import eyeGImg from '/@/assets/loginmini/icon/icon-eye-g.png';
  import { useI18n } from '/@/hooks/web/useI18n';
  import CaptchaModal from '@/components/jeecg/captcha/CaptchaModal.vue';
  import { useModal } from '@/components/Modal';
  import { ExceptionEnum } from '@/enums/exceptionEnum';
  import { Icon } from '/@/components/Icon';

  const { t } = useI18n();
  const { notification, createMessage } = useMessage();
  const emit = defineEmits(['go-back', 'success', 'register']);
  const formRef = ref();
  const formData = reactive<any>({
    username: '',
    mobile: '',
    smscode: '',
    password: '',
    confirmPassword: '',
    policy: false,
  });
  const showInterval = ref<boolean>(true);
  const timeRuning = ref<number>(60);
  const timer = ref<any>(null);
  const pwdIndex = ref<string>('close');
  const confirmPwdIndex = ref<string>('close');
  const [captchaRegisterModal, { openModal: openCaptchaModal }] = useModal();

  function goBackHandleClick() {
    emit('go-back');
    initForm();
  }

  async function getLoginCode() {
    if (!formData.mobile) {
      createMessage.warn(t('sys.login.mobilePlaceholder'));
      return;
    }
    const result = await getCaptcha({ mobile: formData.mobile, smsmode: SmsEnum.REGISTER }).catch((res) => {
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

  function registerHandleClick() {
    if (!formData.username) {
      createMessage.warn(t('sys.login.accountPlaceholder'));
      return;
    }
    if (!formData.mobile) {
      createMessage.warn(t('sys.login.mobilePlaceholder'));
      return;
    }
    if (!formData.smscode) {
      createMessage.warn(t('sys.login.smsPlaceholder'));
      return;
    }
    if (!formData.password) {
      createMessage.warn(t('sys.login.passwordPlaceholder'));
      return;
    }
    if (!formData.confirmPassword) {
      createMessage.warn(t('sys.login.confirmPassword'));
      return;
    }
    if (formData.password !== formData.confirmPassword) {
      createMessage.warn(t('sys.login.diffPwd'));
      return;
    }
    if (!formData.policy) {
      createMessage.warn(t('sys.login.policyPlaceholder'));
      return;
    }
    registerAccount();
  }

  async function registerAccount() {
    try {
      const resultInfo = await register(
        toRaw({
          username: formData.username,
          password: formData.password,
          phone: formData.mobile,
          smscode: formData.smscode,
        })
      );
      if (resultInfo && resultInfo.data.success) {
        notification.success({
          description: resultInfo.data.message || t('sys.api.registerMsg'),
          duration: 3,
        });
        emit('success', { username: formData.username, password: formData.password });
        initForm();
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
    }
  }

  function initForm() {
    Object.assign(formData, { username: '', mobile: '', smscode: '', password: '', confirmPassword: '', policy: false });
    if (!unref(timer)) {
      showInterval.value = true;
      clearInterval(unref(timer));
      timer.value = null;
    }
    formRef.value?.resetFields();
  }

  function pwdClick(value) {
    pwdIndex.value = value;
  }

  function confirmPwdClick(value) {
    confirmPwdIndex.value = value;
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
    margin: 0 0 32px;
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

  .mini-form {
    :deep(.ant-form-item) {
      margin-bottom: 14px;
    }
  }

  .mini-field {
    position: relative;
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

      .mini-icon {
        color: var(--accent);
      }
    }
  }

  .mini-icon {
    position: absolute;
    left: 14px;
    z-index: 1;
    color: var(--ink-400);
    font-size: 18px !important;
  }

  .mini-control {
    flex: 1;
    height: 54px;
    padding: 0 44px 0 42px !important;
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

  .mini-eye {
    position: absolute;
    right: 12px;
    width: 32px;
    height: 32px;
    border: 0;
    background: transparent;
    display: grid;
    place-items: center;
    cursor: pointer;

    img {
      width: 18px;
      height: 18px;
    }
  }

  .mini-policy {
    color: var(--ink-600);
    font-size: 13px;
    line-height: 1.55;
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
