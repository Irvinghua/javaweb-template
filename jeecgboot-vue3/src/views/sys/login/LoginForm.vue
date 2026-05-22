<template>
  <template v-if="getShow">
    <LoginFormTitle />

    <!-- ============================================================
         Tab 切换行（账号 / 手机）
         点击手机 tab 时调用 setLoginState 切到 MobileForm
         ============================================================ -->
    <div class="lf-tabs" role="tablist">
      <button class="lf-tab lf-tab--active" role="tab" type="button">账号登录</button>
      <button class="lf-tab" role="tab" type="button" @click="setLoginState(LoginStateEnum.MOBILE)">手机登录</button>
    </div>

    <!-- 账号登录表单 -->
    <Form :model="formData" :rules="getFormRules" ref="formRef" @keypress.enter="handleLogin">

      <!-- 账号输入框 -->
      <FormItem name="account">
        <div class="lf-field" :class="{ 'lf-field--focused': focusedField === 'account' }">
          <svg class="lf-field-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
          <Input
            v-model:value="formData.account"
            :placeholder="t('sys.login.userName')"
            class="lf-control fix-auto-fill"
            :bordered="false"
            @focus="focusedField = 'account'"
            @blur="focusedField = ''"
          />
        </div>
      </FormItem>

      <!-- 密码输入框 -->
      <FormItem name="password">
        <div class="lf-field" :class="{ 'lf-field--focused': focusedField === 'password' }">
          <svg class="lf-field-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <rect x="3" y="11" width="18" height="11" rx="2"/>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
          </svg>
          <InputPassword
            v-model:value="formData.password"
            :placeholder="t('sys.login.password')"
            class="lf-control lf-control--password fix-auto-fill"
            :bordered="false"
            @focus="focusedField = 'password'"
            @blur="focusedField = ''"
          />
        </div>
      </FormItem>

      <!-- 验证码 -->
      <FormItem name="inputCode">
        <div class="lf-field lf-field--with-suffix" :class="{ 'lf-field--focused': focusedField === 'inputCode' }">
          <svg class="lf-field-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M9 12l2 2 4-4"/>
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
          </svg>
          <Input
            v-model:value="formData.inputCode"
            :placeholder="t('sys.login.inputCode')"
            class="lf-control fix-auto-fill"
            :bordered="false"
            :maxlength="4"
            @focus="focusedField = 'inputCode'"
            @blur="focusedField = ''"
          />
          <img
            v-if="randCodeData.requestCodeSuccess"
            class="lf-captcha-img"
            :src="randCodeData.randCodeImage"
            @click="handleChangeCheckCode"
            title="点击更换"
            alt="验证码"
          />
          <img
            v-else
            class="lf-captcha-img"
            src="../../../assets/images/checkcode.png"
            @click="handleChangeCheckCode"
            title="点击更换"
            alt="验证码"
          />
        </div>
      </FormItem>

      <!-- 记住我 + 忘记密码 -->
      <div class="lf-helper-row">
        <Checkbox v-model:checked="rememberMe" class="lf-remember">
          {{ t('sys.login.rememberMe') }}
        </Checkbox>
        <Button type="link" class="lf-forgot" @click="setLoginState(LoginStateEnum.RESET_PASSWORD)">
          {{ t('sys.login.forgetPassword') }}
        </Button>
      </div>

      <!-- 登录按钮 -->
      <FormItem>
        <button class="lf-btn-primary" type="button" @click="handleLogin" :disabled="loading">
          <span v-if="loading">登录中…</span>
          <span v-else>{{ t('sys.login.loginButton') }}</span>
        </button>
      </FormItem>

      <!-- 其他登录方式入口 -->
      <div class="lf-alt-row">
        <Button type="link" size="small" @click="setLoginState(LoginStateEnum.QR_CODE)">
          {{ t('sys.login.qrSignInFormTitle') }}
        </Button>
        <span class="lf-alt-divider">·</span>
        <Button type="link" size="small" @click="setLoginState(LoginStateEnum.REGISTER)">
          {{ t('sys.login.registerButton') }}
        </Button>
      </div>

      <!-- 第三方登录 -->
      <div class="lf-divider-line">
        <span>{{ t('sys.login.otherSignIn') }}</span>
      </div>
      <div class="lf-third-row">
        <a class="lf-third-btn" @click="onThirdLogin('github')" title="GitHub">
          <GithubFilled />
        </a>
        <a class="lf-third-btn" @click="onThirdLogin('wechat_enterprise')" title="企业微信">
          <icon-font class="item-icon" type="icon-qiyeweixin3" />
        </a>
        <a class="lf-third-btn" @click="onThirdLogin('dingtalk')" title="钉钉">
          <DingtalkCircleFilled />
        </a>
        <a class="lf-third-btn" @click="onThirdLogin('wechat_open')" title="微信">
          <WechatFilled />
        </a>
      </div>
    </Form>

    <!-- 服务协议 -->
    <div class="lf-agreement">
      <span class="lf-agreement-text">登录即代表您同意 <a href="#" class="lf-agreement-link">《服务协议》</a> 和 <a href="#" class="lf-agreement-link">《隐私政策》</a></span>
    </div>

    <!-- 第三方登录弹框 -->
    <ThirdModal ref="thirdModalRef" />
  </template>
</template>

<script lang="ts" setup>
  import { reactive, ref, toRaw, unref, computed, onMounted } from 'vue';

  import { Checkbox, Form, Input, Button } from 'ant-design-vue';
  import { GithubFilled, WechatFilled, DingtalkCircleFilled, createFromIconfontCN } from '@ant-design/icons-vue';
  import LoginFormTitle from './LoginFormTitle.vue';
  import ThirdModal from './ThirdModal.vue';
  import { useI18n } from '/@/hooks/web/useI18n';
  import { useMessage } from '/@/hooks/web/useMessage';

  import { useUserStore } from '/@/store/modules/user';
  import { LoginStateEnum, useLoginState, useFormRules, useFormValid } from './useLogin';
  import { useDesign } from '/@/hooks/web/useDesign';
  import { getCodeInfo } from '/@/api/sys/user';
  import { encryptAESCBC } from '/@/utils/cipher';

  const FormItem = Form.Item;
  const InputPassword = Input.Password;
  const IconFont = createFromIconfontCN({
    scriptUrl: '//at.alicdn.com/t/font_2316098_umqusozousr.js',
  });
  const { t } = useI18n();
  const { notification, createErrorModal } = useMessage();
  const { prefixCls } = useDesign('login');
  const userStore = useUserStore();

  const { setLoginState, getLoginState } = useLoginState();
  const { getFormRules } = useFormRules();

  const formRef = ref();
  const thirdModalRef = ref();
  const loading = ref(false);
  const rememberMe = ref(false);
  const focusedField = ref('');

  const formData = reactive({
    account: 'admin',
    password: '123456',
    inputCode: '',
  });
  const randCodeData = reactive({
    randCodeImage: '',
    requestCodeSuccess: false,
    checkKey: null,
  });

  const { validForm } = useFormValid(formRef);

  const getShow = computed(() => unref(getLoginState) === LoginStateEnum.LOGIN);

  async function handleLogin() {
    const data = await validForm();
    if (!data) return;
    try {
      loading.value = true;

      // 密码使用AES加密传输
      const encryptedPassword = encryptAESCBC(data.password);
      const { userInfo } = await userStore.login(
        toRaw({
          password: encryptedPassword,
          username: data.account,
          captcha: data.inputCode,
          checkKey: randCodeData.checkKey,
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
      loading.value = false;
      handleChangeCheckCode();
    }
  }
  function handleChangeCheckCode() {
    formData.inputCode = '';
    // 代码逻辑说明: [QQYUN-10775]验证码可以复用 #7674------------
    randCodeData.checkKey = new Date().getTime() + Math.random().toString(36).slice(-4); // 1629428467008;
    getCodeInfo(randCodeData.checkKey).then((res) => {
      randCodeData.randCodeImage = res;
      randCodeData.requestCodeSuccess = true;
    });
  }

  /**
   * 第三方登录
   * @param type
   */
  function onThirdLogin(type) {
    thirdModalRef.value.onThirdLogin(type);
  }
  //初始化验证码
  onMounted(() => {
    handleChangeCheckCode();
  });
</script>

<style lang="less" scoped>
  /* ============================================================
     账号登录表单样式
     ============================================================ */

  /* Tab 行 */
  .lf-tabs {
    display: flex;
    gap: 24px;
    border-bottom: 1px solid var(--line);
    margin-bottom: 24px;
  }

  .lf-tab {
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

  /* 通用输入框字段 */
  .lf-field {
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

      .lf-field-icon {
        color: var(--accent);
      }
    }

    &--with-suffix {
      gap: 0;
    }
  }

  .lf-field-icon {
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

  /* AntD Input 裸露内核 —— 去掉默认边框/背景，让外层 .lf-field 负责视觉 */
  .lf-control {
    :deep(.ant-input),
    :deep(input) {
      height: 44px;
      padding: 0 14px 0 42px !important;
      background: transparent !important;
      border: none !important;
      box-shadow: none !important;
      font-size: 14px;
      color: var(--ink-900);
      width: 100%;

      &::placeholder {
        color: var(--ink-400);
      }
    }

    /* Password input 特殊处理 */
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

    /* 去掉 AntD focus ring */
    :deep(.ant-input:focus),
    :deep(.ant-input-affix-wrapper-focused) {
      box-shadow: none !important;
    }
  }

  /* 验证码图片 */
  .lf-captcha-img {
    width: 100px;
    height: 40px;
    border-radius: 8px;
    margin-right: 4px;
    flex-shrink: 0;
    cursor: pointer;
    object-fit: cover;
    border: 1px solid rgba(0, 0, 0, 0.04);
    transition: opacity var(--fast);

    &:hover {
      opacity: 0.82;
    }
  }

  /* AntD FormItem 去掉额外 margin，自己控制间距 */
  :deep(.ant-form-item) {
    margin-bottom: 14px;
  }
  :deep(.ant-form-item:last-child) {
    margin-bottom: 0;
  }

  /* 记住我 + 忘记密码 行 */
  .lf-helper-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 13px;
    margin-bottom: 4px;
    margin-top: -4px;
  }

  .lf-remember {
    color: var(--ink-600);
    font-size: 13px;
  }

  .lf-forgot {
    color: var(--accent) !important;
    font-weight: 500;
    font-size: 13px;
    padding: 0;
    height: auto;

    &:hover {
      opacity: 0.8;
    }
  }

  /* 主登录按钮 */
  .lf-btn-primary {
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

  /* 其他登录入口链接行 */
  .lf-alt-row {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 2px;
    margin-top: 4px;
    font-size: 13px;

    .ant-btn-link {
      color: var(--ink-500) !important;
      font-size: 13px;
      padding: 0 4px;
      height: auto;

      &:hover {
        color: var(--accent) !important;
      }
    }
  }

  .lf-alt-divider {
    color: var(--ink-300);
    font-size: 13px;
  }

  /* 分割线 */
  .lf-divider-line {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 14px 0 12px;
    color: var(--ink-400);
    font-size: 12px;

    &::before,
    &::after {
      content: '';
      flex: 1;
      height: 1px;
      background: var(--line);
    }
  }

  /* 第三方登录图标行 */
  .lf-third-row {
    display: flex;
    justify-content: center;
    gap: 20px;
  }

  .lf-third-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.7);
    border: 1px solid var(--line);
    color: var(--ink-500);
    cursor: pointer;
    transition:
      color var(--fast),
      background-color var(--fast);
    font-size: 18px;

    &:hover {
      color: var(--accent);
      background: var(--accent-50);
      border-color: var(--accent-100);
    }
  }

  /* 服务协议 */
  .lf-agreement {
    margin-top: 18px;
    padding-top: 16px;
    border-top: 1px solid var(--line);
    font-size: 12px;
    color: var(--ink-500);
    line-height: 1.55;
    text-align: center;
  }

  .lf-agreement-link {
    color: var(--accent);
    text-decoration: none;

    &:hover {
      text-decoration: underline;
    }
  }
</style>
