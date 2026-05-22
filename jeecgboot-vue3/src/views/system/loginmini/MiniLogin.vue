<template>
  <!-- ============================================================
       全屏登录页容器
       [ TODO ] 换背景图：把 .ml-page 的 background 改成
                background: url('your-bg.jpg') center/cover no-repeat;
       ============================================================ -->
  <div :class="prefixCls" class="ml-page">
    <!-- 装饰网格点 -->
    <div class="ml-grid-dots" aria-hidden="true"></div>

    <!-- 工具栏 -->
    <div class="ml-toolbar">
      <AppLocalePicker :showText="false" v-if="showLocale" />
      <AppDarkModeToggle />
    </div>

    <!-- 左侧品牌区（移动端隐藏） -->
    <div class="ml-brand-block" v-if="!getIsMobile">
      <div class="ml-brand-header">
        <div class="ml-brand-logo">
          <img :src="logoImg" alt="logo" />
        </div>
        <span class="ml-brand-platform">JeecgBoot 企业级低代码平台</span>
      </div>
      <h1 class="ml-brand-project">欢迎使用<br />企业管理平台</h1>
      <p class="ml-brand-slogan">让管理回归本质，让协作更高效。<br />一站式企业级业务管理平台。</p>
    </div>

    <!-- 右侧悬浮登录卡片 -->
    <div class="ml-card" :class="{ 'ml-card--mobile': getIsMobile }">

      <!-- ============ 账号/手机登录面板 ============ -->
      <template v-if="type === 'login'">
        <div class="ml-card-header">
          <h2 class="ml-form-title">登录</h2>
          <p class="ml-form-sub">请输入您的账号信息以继续</p>
        </div>

        <!-- Tab 切换 -->
        <div class="ml-tabs" role="tablist">
          <button
            class="ml-tab"
            :class="{ 'ml-tab--active': activeIndex === 'accountLogin' }"
            role="tab"
            type="button"
            @click="loginClick('accountLogin')"
          >{{ t('sys.login.signInFormTitle') }}</button>
          <button
            class="ml-tab"
            :class="{ 'ml-tab--active': activeIndex === 'phoneLogin' }"
            role="tab"
            type="button"
            @click="loginClick('phoneLogin')"
          >{{ t('sys.login.mobileSignInFormTitle') }}</button>
        </div>

        <!-- 账号登录表单 -->
        <a-form ref="loginRef" :model="formData" v-if="activeIndex === 'accountLogin'" @keyup.enter.native="loginHandleClick">
          <!-- 账号 -->
          <a-form-item>
            <div class="ml-field" :class="{ 'ml-field--focused': focusedField === 'username' }">
              <svg class="ml-field-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
              <a-input
                class="ml-control fix-auto-fill"
                :placeholder="t('sys.login.userName')"
                v-model:value="formData.username"
                :bordered="false"
                @focus="focusedField = 'username'"
                @blur="focusedField = ''"
              />
            </div>
          </a-form-item>

          <!-- 密码 -->
          <a-form-item>
            <div class="ml-field" :class="{ 'ml-field--focused': focusedField === 'password' }">
              <svg class="ml-field-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <rect x="3" y="11" width="18" height="11" rx="2"/>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
              </svg>
              <a-input
                class="ml-control fix-auto-fill"
                type="password"
                :placeholder="t('sys.login.password')"
                v-model:value="formData.password"
                :bordered="false"
                @focus="focusedField = 'password'"
                @blur="focusedField = ''"
              />
            </div>
          </a-form-item>

          <!-- 验证码 -->
          <a-form-item>
            <div class="ml-field-row">
              <div class="ml-field" :class="{ 'ml-field--focused': focusedField === 'inputCode' }">
                <svg class="ml-field-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                  <path d="M9 12l2 2 4-4"/>
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                </svg>
                <a-input
                  class="ml-control fix-auto-fill"
                  type="text"
                  :placeholder="t('sys.login.inputCode')"
                  v-model:value="formData.inputCode"
                  :bordered="false"
                  :maxlength="4"
                  @focus="focusedField = 'inputCode'"
                  @blur="focusedField = ''"
                />
              </div>
              <img
                v-if="randCodeData.requestCodeSuccess"
                class="ml-captcha-img"
                :src="randCodeData.randCodeImage"
                @click="handleChangeCheckCode"
                title="点击更换"
                alt="验证码"
              />
              <img
                v-else
                class="ml-captcha-img"
                :src="codeImg"
                @click="handleChangeCheckCode"
                title="点击更换"
                alt="验证码"
              />
            </div>
          </a-form-item>

          <!-- 部门选择（多部门时才显示） -->
          <a-form-item v-if="showDepart">
            <div class="ml-field ml-field--select" :class="{ 'ml-field--focused': focusedField === 'dept' }">
              <svg class="ml-field-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                <polyline points="9 22 9 12 15 12 15 22"/>
              </svg>
              <a-select
                allow-clear
                class="ml-select"
                :bordered="false"
                v-model:value="formData.loginOrgCode"
                :placeholder="t('sys.login.loginOrgCode')"
                @focus="focusedField = 'dept'"
                @blur="focusedField = ''"
              >
                <template #suffixIcon>
                  <Icon icon="ant-design:gold-outline" />
                </template>
                <template v-for="depart in departList" :key="depart.orgCode">
                  <a-select-option :value="depart.orgCode">{{ getShortDeptName(depart.label) }}</a-select-option>
                </template>
              </a-select>
            </div>
          </a-form-item>

          <!-- 记住我 + 忘记密码 -->
          <div class="ml-helper-row">
            <a-checkbox v-model:checked="rememberMe" class="ml-remember">
              {{ t('sys.login.rememberMe') }}
            </a-checkbox>
            <a class="ml-forgot" @click="forgetHandelClick">{{ t('sys.login.forgetPassword') }}</a>
          </div>

          <!-- 登录按钮 -->
          <a-form-item>
            <a-button
              :loading="loginLoading"
              class="ml-btn-primary"
              type="primary"
              @click="loginHandleClick"
            >{{ t('sys.login.loginButton') }}</a-button>
          </a-form-item>
        </a-form>

        <!-- 手机登录表单 -->
        <a-form v-else ref="phoneFormRef" :model="phoneFormData" @keyup.enter.native="loginHandleClick">
          <!-- 手机号 -->
          <a-form-item>
            <div class="ml-field" :class="{ 'ml-field--focused': focusedField === 'mobile' }">
              <svg class="ml-field-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <rect x="5" y="2" width="14" height="20" rx="2"/>
                <line x1="12" y1="18" x2="12.01" y2="18"/>
              </svg>
              <a-input
                class="ml-control fix-auto-fill"
                :placeholder="t('sys.login.mobile')"
                v-model:value="phoneFormData.mobile"
                :bordered="false"
                @focus="focusedField = 'mobile'"
                @blur="focusedField = ''"
              />
            </div>
          </a-form-item>

          <!-- 短信验证码 + 发送按钮 -->
          <a-form-item>
            <div class="ml-field-row">
              <div class="ml-field" :class="{ 'ml-field--focused': focusedField === 'smscode' }">
                <svg class="ml-field-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                  <path d="m22 4-10 10.01-3-3"/>
                </svg>
                <a-input
                  class="ml-control fix-auto-fill"
                  :maxlength="6"
                  :placeholder="t('sys.login.smsCode')"
                  v-model:value="phoneFormData.smscode"
                  :bordered="false"
                  @focus="focusedField = 'smscode'"
                  @blur="focusedField = ''"
                />
              </div>
              <button
                v-if="showInterval"
                class="ml-sms-btn"
                type="button"
                @click="getLoginCode"
              >{{ t('component.countdown.normalText') }}</button>
              <span v-else class="ml-sms-countdown">{{ t('component.countdown.sendText', [unref(timeRuning)]) }}</span>
            </div>
          </a-form-item>

          <!-- 部门选择（多部门时才显示） -->
          <a-form-item v-if="showDepart">
            <div class="ml-field ml-field--select">
              <svg class="ml-field-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                <polyline points="9 22 9 12 15 12 15 22"/>
              </svg>
              <a-select
                allow-clear
                class="ml-select"
                :bordered="false"
                v-model:value="phoneFormData.loginOrgCode"
                :placeholder="t('sys.login.loginOrgCode')"
              >
                <template #suffixIcon>
                  <Icon icon="ant-design:gold-outline" />
                </template>
                <template v-for="depart in departList" :key="depart.orgCode">
                  <a-select-option :value="depart.orgCode">{{ getShortDeptName(depart.label) }}</a-select-option>
                </template>
              </a-select>
            </div>
          </a-form-item>

          <!-- 登录按钮 -->
          <a-form-item>
            <a-button
              :loading="loginLoading"
              class="ml-btn-primary"
              type="primary"
              @click="loginHandleClick"
            >{{ t('sys.login.loginButton') }}</a-button>
          </a-form-item>
        </a-form>

        <!-- 其他登录入口 -->
        <div class="ml-alt-row">
          <a class="ml-alt-link" @click="codeHandleClick">{{ t('sys.login.qrSignInFormTitle') }}</a>
          <span class="ml-alt-sep">·</span>
          <a class="ml-alt-link" @click="registerHandleClick">{{ t('sys.login.registerButton') }}</a>
        </div>

        <!-- 第三方登录 -->
        <div class="ml-divider">
          <span>{{ t('sys.login.otherSignIn') }}</span>
        </div>
        <div class="ml-third-row" :class="`${prefixCls}-sign-in-way`">
          <a class="ml-third-btn" title="GitHub" @click="onThirdLogin('github')"><GithubFilled /></a>
          <a class="ml-third-btn" title="企业微信" @click="onThirdLogin('wechat_enterprise')"><icon-font class="item-icon" type="icon-qiyeweixin3" /></a>
          <a class="ml-third-btn" title="钉钉" @click="onThirdLogin('dingtalk')"><DingtalkCircleFilled /></a>
          <a class="ml-third-btn" title="微信" @click="onThirdLogin('wechat_open')"><WechatFilled /></a>
        </div>
      </template>

      <!-- ============ 忘记密码面板 ============ -->
      <div v-show="type === 'forgot'" class="ml-sub-panel">
        <MiniForgotpad ref="forgotRef" @go-back="goBack" @success="handleSuccess" />
      </div>

      <!-- ============ 注册面板 ============ -->
      <div v-show="type === 'register'" class="ml-sub-panel">
        <MiniRegister ref="registerRef" @go-back="goBack" @success="handleSuccess" />
      </div>

      <!-- ============ 二维码登录面板 ============ -->
      <div v-show="type === 'codeLogin'" class="ml-sub-panel">
        <MiniCodelogin ref="codeRef" @go-back="goBack" @success="handleSuccess" />
      </div>
    </div>

    <!-- 版权 -->
    <div class="ml-page-foot">© {{ new Date().getFullYear() }} 企业管理平台 · 保留所有权利</div>

    <!-- 第三方登录弹框 -->
    <ThirdModal ref="thirdModalRef" />

    <!-- 图片验证码弹窗 -->
    <CaptchaModal @register="captchaRegisterModal" @ok="getLoginCode" />
  </div>
</template>

<script lang="ts" setup name="login-mini">
  import { getCaptcha, getCodeInfo } from '/@/api/sys/user';
  import { computed, onMounted, reactive, ref, toRaw, unref, watch } from 'vue';
  import codeImg from '/@/assets/images/checkcode.png';
  import { Rule } from '/@/components/Form';
  import { useUserStore } from '/@/store/modules/user';
  import { useMessage } from '/@/hooks/web/useMessage';
  import { useI18n } from '/@/hooks/web/useI18n';
  import { SmsEnum } from '/@/views/sys/login/useLogin';
  import ThirdModal from '/@/views/sys/login/ThirdModal.vue';
  import MiniForgotpad from './MiniForgotpad.vue';
  import MiniRegister from './MiniRegister.vue';
  import MiniCodelogin from './MiniCodelogin.vue';
  import logoImg from '/@/assets/loginmini/icon/jeecg_logo.png';
  import adTextImg from '/@/assets/loginmini/icon/jeecg_ad_text.png';
  import { AppLocalePicker, AppDarkModeToggle } from '/@/components/Application';
  import { useLocaleStore } from '/@/store/modules/locale';
  import { createLocalStorage } from '/@/utils/cache';
  import { useDesign } from "/@/hooks/web/useDesign";
  import { useAppInject } from "/@/hooks/web/useAppInject";
  import { GithubFilled, WechatFilled, DingtalkCircleFilled, createFromIconfontCN } from '@ant-design/icons-vue';
  import CaptchaModal from '@/components/jeecg/captcha/CaptchaModal.vue';
  import { useModal } from "@/components/Modal";
  import { ExceptionEnum } from "@/enums/exceptionEnum";
  import { encryptAESCBC } from '/@/utils/cipher';
  import { defHttp } from "@/utils/http/axios";
  import { Icon } from '/@/components/Icon';

  const IconFont = createFromIconfontCN({
    scriptUrl: '//at.alicdn.com/t/font_2316098_umqusozousr.js',
  });
  const { prefixCls } = useDesign('mini-login');
  const { notification, createMessage } = useMessage();
  const userStore = useUserStore();
  const { t } = useI18n();
  const $ls = createLocalStorage();
  const localeStore = useLocaleStore();
  const showLocale = localeStore.getShowPicker;
  const randCodeData = reactive<any>({
    randCodeImage: '',
    requestCodeSuccess: false,
    checkKey: null,
  });
  // 记住用户名
  const rememberMe = ref<boolean>(false);
  const REMEMBER_USERNAME_KEY = 'LOGIN_REMEMBER_USERNAME';
  //手机号登录还是账号登录
  const activeIndex = ref<string>('accountLogin');
  const type = ref<string>('login');
  // focus 状态
  const focusedField = ref<string>('');
  //账号登录表单字段
  const formData = reactive<any>({
    inputCode: '',
    username: 'admin',
    password: '123456',
    loginOrgCode: '',
  });
  //手机登录表单字段
  const phoneFormData = reactive<any>({
    mobile: '',
    smscode: '',
    loginOrgCode: '',
  });
  const loginRef = ref();
  //第三方登录弹窗
  const thirdModalRef = ref();
  //扫码登录
  const codeRef = ref();
  //是否显示获取验证码
  const showInterval = ref<boolean>(true);
  //60s
  const timeRuning = ref<number>(60);
  //定时器
  const timer = ref<any>(null);
  //忘记密码
  const forgotRef = ref();
  //注册
  const registerRef = ref();
  const loginLoading = ref<boolean>(false);
  const { getIsMobile } = useAppInject();
  const [captchaRegisterModal, { openModal: openCaptchaModal }] = useModal();
  defineProps({
    sessionTimeout: {
      type: Boolean,
    },
  });
 //**********************查询部门逻辑begin**********************************************
  //用户部门
  const departList = ref([]);
  //部门显示
  const showDepart = computed(()=>{
    return departList.value.length > 1
  })
  //获取部门缩写
  const getShortDeptName = computed(()=>{
    return (deptName) => {
      if (!deptName) return '';
      if (deptName.length > 18) {
        return '...' + deptName.substring(deptName.length-18, deptName.length) ;
      }
      return deptName;
    };
  })
  //监听验证码和输入框的修改
  watch(
      () => [formData.inputCode, phoneFormData.smscode],
      () => {
        if ((formData.inputCode && formData.inputCode.length == 4)
            || (phoneFormData.smscode && phoneFormData.smscode.length == 6)) {
            checkAccount()
        }
      },
  );
  /**
   * 监听账号变化，清除部门信息
   */
  watch(
      () => [formData.username,phoneFormData.mobile,activeIndex.value],
      () => {
        formData.loginOrgCode = null;
        phoneFormData.loginOrgCode = null;
        departList.value = [];
        if ((formData.inputCode && formData.inputCode.length == 4)
            || (phoneFormData.smscode && phoneFormData.smscode.length == 6)) {
          checkAccount()
        }
      }
  );

  //初始化数据
  let deptTimer;
  function checkAccount() {
    deptTimer && clearTimeout(deptTimer);
    deptTimer = setTimeout(async () => {
      let loginType = activeIndex.value === 'accountLogin' ? 'account' : 'phone';
      // 验证条件提取
      const isValidAccount = loginType === 'account' && formData.username && formData.password;
      const isValidPhone = loginType == 'phone' && phoneFormData.mobile && phoneFormData.smscode;
      let finalFormData = loginType == 'phone' ? {...phoneFormData} : {...formData};
      if (!isValidAccount && !isValidPhone) {
        return;
      }
      //查询部门信息前，优先进行账户校验
      if (departList.value && departList.value.length == 0) {
        let params = {...finalFormData, loginType: activeIndex.value === 'accountLogin' ? 'account' : 'phone'};
        if (loginType == 'account') {
          params['password'] = encryptAESCBC(formData.password);
          params['checkKey'] = randCodeData.checkKey;
        }
        const res = await defHttp.post({
          url: '/sys/loginGetUserDeparts',
          params: {...params}
        }, {isTransformResponse: false});
        if (res.success && res.result) {
          let {departs,currentOrgCode} = res.result;
          // 判断当前部门是否在所属的部门列表中
          if (departs && departs.length > 0) {
            // 代码逻辑说明: JHHB-790 用户部门变更，会出现这个情况（因为之前设置的这里只切换部门，过滤了公司和岗位信息）
            const hasCurrentDepart = departs.some(item => item.orgCode == currentOrgCode);
            formData.loginOrgCode = hasCurrentDepart?currentOrgCode:null;
            phoneFormData.loginOrgCode = hasCurrentDepart?currentOrgCode:null;
            departList.value = departs.map((item) => {
              return {
                label: item.departName,
                value: item.orgCode,
                orgCode: item.orgCode,
                departName: item.departName,
              };
            });
          }
        } else {
          //createMessage.warn(res.message);
        }
      }
    },500)
  }
 //**********************查询部门逻辑end*************************************************
  /**
   * 获取验证码
   */
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
   * 切换登录方式
   */
  function loginClick(type) {
    activeIndex.value = type;
  }

  /**
   * 账号或者手机登录
   */
  async function loginHandleClick() {
    if (unref(activeIndex) === 'accountLogin') {
      accountLogin();
    } else {
      //手机号登录
      phoneLogin();
    }
  }

  async function accountLogin() {
    if (!formData.username) {
      createMessage.warn(t('sys.login.accountPlaceholder'));
      return;
    }
    if (!formData.password) {
      createMessage.warn(t('sys.login.passwordPlaceholder'));
      return;
    }
    try {
      loginLoading.value = true;

      // 密码使用AES加密传输
      const encryptedPassword = encryptAESCBC(formData.password);
      const { userInfo } = await userStore.login(
        toRaw({
          password: encryptedPassword,
          username: formData.username,
          loginOrgCode: formData.loginOrgCode,
          captcha: formData.inputCode,
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
        // 登录成功后处理记住用户名
        if (rememberMe.value && formData.username) {
          $ls.set(REMEMBER_USERNAME_KEY, formData.username)
        } else {
          $ls.remove(REMEMBER_USERNAME_KEY)
        }
      }
    } catch (error) {
      notification.error({
        message: t('sys.api.errorTip'),
        description: error.message || t('sys.login.networkExceptionMsg'),
        duration: 3,
      });
      handleChangeCheckCode();
    } finally {
      loginLoading.value = false;
    }
  }

  /**
   * 手机号登录
   */
  async function phoneLogin() {
    if (!phoneFormData.mobile) {
      createMessage.warn(t('sys.login.mobilePlaceholder'));
      return;
    }
    if (!phoneFormData.smscode) {
      createMessage.warn(t('sys.login.smsPlaceholder'));
      return;
    }
    try {
      loginLoading.value = true;
      const { userInfo }: any = await userStore.phoneLogin({
        mobile: phoneFormData.mobile,
        captcha: phoneFormData.smscode,
        loginOrgCode: phoneFormData.loginOrgCode,
        mode: 'none', //不要默认的错误提示
      });
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
        description: error.message || t('sys.login.networkExceptionMsg'),
        duration: 3,
      });
    } finally {
      loginLoading.value = false;
    }
  }

  /**
   * 获取手机验证码
   */
  async function getLoginCode() {
    if (!phoneFormData.mobile) {
      createMessage.warn(t('sys.login.mobilePlaceholder'));
      return;
    }
    // 代码逻辑说明: 【issues/8567】严重：修改密码存在水平越权问题：登录应该用登录模板不应该用忘记密码的模板---
    const result = await getCaptcha({ mobile: phoneFormData.mobile, smsmode: SmsEnum.LOGIN }).catch((res) =>{
      if(res.code === ExceptionEnum.PHONE_SMS_FAIL_CODE){
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

  /**
   * 第三方登录
   * @param type
   */
  function onThirdLogin(type) {
    thirdModalRef.value.onThirdLogin(type);
  }

  /**
   * 忘记密码
   */
  function forgetHandelClick() {
    type.value = 'forgot';
    setTimeout(() => {
      forgotRef.value.initForm();
    }, 300);
  }

  /**
   * 返回登录页面
   */
  function goBack() {
    activeIndex.value = 'accountLogin';
    type.value = 'login';
  }

  /**
   * 忘记密码/注册账号回调事件
   * @param value
   */
  function handleSuccess(value) {
    Object.assign(formData, value);
    Object.assign(phoneFormData, { mobile: "", smscode: "" });
    type.value = 'login';
    activeIndex.value = 'accountLogin';
    handleChangeCheckCode();
  }

  /**
   * 注册
   */
  function registerHandleClick() {
    type.value = 'register';
    setTimeout(() => {
      registerRef.value.initForm();
    }, 300);
  }

  /**
   * 注册
   */
  function codeHandleClick() {
    type.value = 'codeLogin';
    setTimeout(() => {
      codeRef.value.initFrom();
    }, 300);
  }

  onMounted(() => {
    //加载验证码
    handleChangeCheckCode();
    // 恢复已记住的用户名
    const saved = $ls.get(REMEMBER_USERNAME_KEY);
    if (saved) {
      formData.username = saved;
      rememberMe.value = true;
    }
  });
</script>

<style lang="less" scoped>
  /* ============================================================
     登录页全局样式
     [ TODO ] 换背景图：把 .ml-page 的 background 改成
              background: url('your-bg.jpg') center/cover no-repeat;
     ============================================================ */
  .ml-page {
    position: relative;
    min-height: 100vh;
    width: 100%;
    overflow: hidden;
    /* 占位渐变（紫蓝色系） */
    background:
      radial-gradient(ellipse 80% 60% at 80% 50%, rgba(255, 255, 255, 0.55), transparent 60%),
      radial-gradient(ellipse 60% 50% at 10% 80%, rgba(179, 201, 255, 0.55), transparent 65%),
      radial-gradient(ellipse 50% 50% at 30% 20%, rgba(220, 210, 255, 0.7), transparent 60%),
      linear-gradient(135deg, #e9ecff 0%, #dde5ff 35%, #f1ecff 70%, #f6f0ff 100%);

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

  .ml-grid-dots {
    position: absolute;
    inset: 0;
    background-image: radial-gradient(rgba(15, 23, 42, 0.05) 1px, transparent 1.5px);
    background-size: 28px 28px;
    pointer-events: none;
    opacity: 0.6;
  }

  /* 工具栏 */
  .ml-toolbar {
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
  .ml-brand-block {
    position: absolute;
    left: 8%;
    top: 50%;
    transform: translateY(-50%);
    max-width: 560px;
    z-index: 2;
  }

  .ml-brand-header {
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

  .ml-brand-logo {
    width: 28px;
    height: 28px;
    border-radius: 7px;
    background: var(--accent);
    display: grid;
    place-items: center;
    flex-shrink: 0;
    overflow: hidden;

    img {
      width: 20px;
      height: 20px;
      object-fit: contain;
    }
  }

  .ml-brand-platform {
    font-weight: 700;
    font-size: 14px;
    color: var(--ink-900);
    letter-spacing: 0.1px;
    white-space: nowrap;
  }

  .ml-brand-project {
    font-size: 60px;
    line-height: 1.15;
    font-weight: 800;
    color: var(--ink-900);
    letter-spacing: -1.5px;
    margin: 0 0 24px;
  }

  .ml-brand-slogan {
    font-size: 22px;
    line-height: 1.55;
    color: var(--ink-600);
    margin: 0;
    font-weight: 400;
    max-width: 480px;
  }

  /* ============================================================
     右侧登录卡片
     ============================================================ */
  .ml-card {
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

    &--mobile {
      position: static;
      transform: none;
      right: auto;
      margin: 24px auto 60px;
      width: calc(100% - 32px);
    }
  }

  /* 卡片头部 */
  .ml-card-header {
    margin-bottom: 24px;
  }

  .ml-form-title {
    font-size: 24px;
    font-weight: 700;
    color: var(--ink-900);
    margin: 0 0 6px;
    letter-spacing: -0.3px;
    line-height: 1.3;
  }

  .ml-form-sub {
    color: var(--ink-500);
    font-size: 13.5px;
    margin: 0;
    line-height: 1.5;
  }

  /* Tab 行 */
  .ml-tabs {
    display: flex;
    gap: 24px;
    border-bottom: 1px solid var(--line);
    margin-bottom: 20px;
  }

  .ml-tab {
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

  /* AntD FormItem 间距重置 */
  :deep(.ant-form-item) {
    margin-bottom: 14px;
  }

  /* 输入字段 + 右侧附件（验证码图片 / 短信按钮）的横向容器 */
  .ml-field-row {
    display: flex;
    align-items: center;
    gap: 10px;

    .ml-field {
      flex: 1;
      min-width: 0;
    }
  }

  /* 通用输入字段容器 */
  .ml-field {
    position: relative;
    display: flex;
    align-items: center;
    min-height: 46px;
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

      .ml-field-icon {
        color: var(--accent);
      }
    }

    &--select {
      overflow: visible;
    }

    /* AntD a-input 渲染出的 <input class="ant-input">，是 .ml-field 的直接子节点 */
    :deep(.ant-input) {
      height: 46px;
      padding: 0 14px 0 42px;
      background: transparent;
      border: none;
      box-shadow: none !important;
      font-size: 14px;
      color: var(--ink-900);
      width: 100%;

      &::placeholder {
        color: var(--ink-400);
      }

      &:focus {
        box-shadow: none !important;
      }
    }
  }

  .ml-field-icon {
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

  /* 验证码图片（输入框外的独立方块，与设计稿一致） */
  .ml-captcha-img {
    width: 108px;
    height: 46px;
    border-radius: 10px;
    border: 1px solid rgba(15, 23, 42, 0.08);
    flex-shrink: 0;
    cursor: pointer;
    object-fit: fill;
    transition: opacity var(--fast);

    &:hover {
      opacity: 0.82;
    }
  }

  /* 部门选择 */
  .ml-select {
    flex: 1;
    padding-left: 42px;

    :deep(.ant-select-selector) {
      background: transparent !important;
      border: none !important;
      box-shadow: none !important;
      height: 46px !important;
      padding: 0 !important;

      .ant-select-selection-item,
      .ant-select-selection-placeholder {
        line-height: 46px;
        font-size: 14px;
        color: var(--ink-400);
      }
    }
  }

  /* 记住我 + 忘记密码 */
  .ml-helper-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
    font-size: 13px;
  }

  .ml-remember {
    color: var(--ink-600);
    font-size: 13px;
  }

  .ml-forgot {
    color: var(--accent);
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    transition: opacity var(--fast);

    &:hover {
      opacity: 0.8;
    }
  }

  /* 主登录按钮 */
  .ml-btn-primary {
    width: 100%;
    height: 48px !important;
    background: var(--accent) !important;
    border-color: var(--accent) !important;
    border-radius: 10px !important;
    font-size: 15px !important;
    font-weight: 600;
    letter-spacing: 4px;
    box-shadow: 0 10px 22px rgba(91, 108, 255, 0.32) !important;
    transition:
      background-color var(--fast),
      box-shadow var(--fast),
      transform var(--fast) !important;
    margin-top: 4px;

    &:hover,
    &:focus {
      background: var(--accent-600) !important;
      border-color: var(--accent-600) !important;
      box-shadow: 0 14px 28px rgba(91, 108, 255, 0.4) !important;
    }

    &:active {
      transform: translateY(1px);
    }
  }

  /* 短信按钮（输入框外的独立方块，与设计稿一致） */
  .ml-sms-btn {
    height: 46px;
    padding: 0 16px;
    border: 1px solid rgba(15, 23, 42, 0.08);
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.7);
    color: var(--accent);
    font-family: inherit;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    white-space: nowrap;
    flex-shrink: 0;
    transition: background-color var(--fast);

    &:hover {
      background: #fff;
    }
  }

  .ml-sms-countdown {
    height: 46px;
    padding: 0 16px;
    border: 1px solid rgba(15, 23, 42, 0.08);
    border-radius: 10px;
    background: rgba(241, 243, 248, 0.7);
    color: var(--ink-400);
    font-size: 12px;
    display: flex;
    align-items: center;
    flex-shrink: 0;
    white-space: nowrap;
  }

  /* 其他登录入口 */
  .ml-alt-row {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
    margin-top: 4px;
    font-size: 13px;
  }

  .ml-alt-link {
    color: var(--ink-500);
    font-size: 13px;
    cursor: pointer;
    padding: 0 4px;
    transition: color var(--fast);

    &:hover {
      color: var(--accent);
    }
  }

  .ml-alt-sep {
    color: var(--ink-300);
  }

  /* 分割线 */
  .ml-divider {
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

  /* 第三方登录 */
  .ml-third-row {
    display: flex;
    justify-content: center;
    gap: 20px;
  }

  .ml-third-btn {
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
    font-size: 18px;
    transition:
      color var(--fast),
      background-color var(--fast);

    &:hover {
      color: var(--accent);
      background: var(--accent-50);
      border-color: var(--accent-100);
    }
  }

  /* 子面板（忘记密码、注册、扫码） */
  .ml-sub-panel {
    /* 子组件自带样式，这里仅提供容器 */
  }

  /* 底部版权 */
  .ml-page-foot {
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
    .ml-brand-block {
      position: static;
      transform: none;
      padding: 60px 28px 12px;
      max-width: 100%;
    }
    .ml-brand-project {
      font-size: 36px;
    }
    .ml-brand-slogan {
      font-size: 16px;
    }
    .ml-card {
      position: static;
      transform: none;
      right: auto;
      margin: 24px auto 60px;
      width: calc(100% - 32px);
    }
    .ml-page::before,
    .ml-page::after {
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

<style lang="less">
/* 非 scoped：AntD 全局覆盖，仅在登录页生效 */
@prefix-cls: ~'@{namespace}-mini-login';

@dark-bg: #293146;

html[data-theme='dark'] {
  .@{prefix-cls} {
    background-color: @dark-bg !important;
    background-image: none;

    .ml-card {
      background: rgba(41, 49, 70, 0.92) !important;
      border-color: rgba(255, 255, 255, 0.1) !important;
    }

    .ml-form-title,
    .ml-brand-project,
    .ml-brand-platform {
      color: #e2e8f0 !important;
    }

    .ml-form-sub,
    .ml-brand-slogan {
      color: #94a3b8 !important;
    }

    .ml-field {
      background: rgba(51, 65, 85, 0.8) !important;
      border-color: rgba(255, 255, 255, 0.08) !important;
    }

    .ml-field input,
    .ml-field .ant-input {
      color: #e2e8f0 !important;
      -webkit-text-fill-color: #e2e8f0 !important;
      background: transparent !important;
    }

    .ml-tab {
      color: #94a3b8 !important;
    }
    .ml-tab--active {
      color: #e2e8f0 !important;
    }

    .@{prefix-cls}-sign-in-way {
      .anticon {
        font-size: 22px !important;
        color: #888 !important;
        cursor: pointer !important;

        &:hover {
          color: @primary-color !important;
        }
      }
    }
  }

  input.fix-auto-fill,
  .fix-auto-fill input {
    -webkit-text-fill-color: #c9d1d9 !important;
    box-shadow: inherit !important;
  }
}
</style>
