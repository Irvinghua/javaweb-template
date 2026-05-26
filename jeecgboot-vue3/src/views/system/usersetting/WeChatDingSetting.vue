<!--
  UI Redesign: 第三方APP 绑定
  按 profile.html "Tab 4：第三方 APP" 设计稿重做：
    .app-card 卡片，内部多行 .app-row
    每行：app-info (app-logo 渐变方块 + app-meta：name + desc) + 绑定按钮
  业务逻辑（initUserDetail / dingDingBind / wechatBind / wechatEnterpriseBind 等）保持不变
-->
<template>
  <div :class="[`${prefixCls}`, 'third-app-redesign']">
    <div class="card app-wrapper">
      <div class="block-title">第三方 APP <span class="sub">绑定后可使用对应应用快速登录</span></div>

      <div class="app-card">
        <!-- 钉钉 -->
        <div class="app-row">
          <div class="app-info">
            <span class="app-logo app-logo--dingtalk">
              <DingtalkCircleFilled />
            </span>
            <div class="app-meta">
              <div class="app-name">
                钉钉
                <span class="sec-tag sec-tag--green" v-if="bindDingData.sysUserId">已绑定</span>
              </div>
              <div class="app-desc">
                {{ bindDingData.realname ? `已绑定 ${bindDingData.realname}` : '未绑定，绑定后可使用钉钉账号一键登录' }}
              </div>
            </div>
          </div>
          <a-button
            :type="bindDingData.sysUserId ? 'default' : 'primary'"
            :ghost="!bindDingData.sysUserId"
            @click="dingDingBind"
          >
            {{ !bindDingData.sysUserId ? '绑定' : '解绑' }}
          </a-button>
        </div>

        <!-- 微信 -->
        <div class="app-row">
          <div class="app-info">
            <span class="app-logo app-logo--wechat">
              <WechatFilled />
            </span>
            <div class="app-meta">
              <div class="app-name">
                微信
                <span class="sec-tag sec-tag--green" v-if="bindWechatData.sysUserId">已绑定</span>
              </div>
              <div class="app-desc">
                {{ bindWechatData.realname ? `已绑定 ${bindWechatData.realname}` : '未绑定，绑定后可使用微信账号一键登录' }}
              </div>
            </div>
          </div>
          <a-button
            :type="bindWechatData.sysUserId ? 'default' : 'primary'"
            :ghost="!bindWechatData.sysUserId"
            @click="wechatBind"
          >
            {{ !bindWechatData.sysUserId ? '绑定' : '解绑' }}
          </a-button>
        </div>
      </div>
    </div>
  </div>
</template>
<script lang="ts" setup name="we-chat-ding-setting">
  import { onMounted, ref, reactive, unref } from 'vue';
  import { CollapseContainer } from '/@/components/Container';
  import { bindThirdAppAccount, deleteThirdAccount, getThirdAccountByUserId } from './UserSetting.api';
  import { useUserStore } from '/@/store/modules/user';
  import { useModal } from '/@/components/Modal';
  import { DingtalkCircleFilled, createFromIconfontCN, WechatFilled } from '@ant-design/icons-vue';
  import { useGlobSetting } from '/@/hooks/setting';
  import { useMessage } from '/@/hooks/web/useMessage';
  import { Modal } from 'ant-design-vue';
  import { useDesign } from '/@/hooks/web/useDesign';

  const { prefixCls } = useDesign('j-user-tenant-setting-container');

  const IconFont = createFromIconfontCN({
    scriptUrl: '//at.alicdn.com/t/font_2316098_umqusozousr.js',
  });
  const userStore = useUserStore();

  //绑定微信的数据
  const bindWechatData = ref<any>({});
  //绑定钉钉的数据
  const bindDingData = ref<any>({});
  //绑定企业微信的数据
  const bindEnterpriseData = ref<any>({});

  const glob = useGlobSetting();
  //第三方类型
  const thirdType = ref('');
  //第三方用户UUID
  const thirdUserUuid = ref('');
  //第三方详情
  const thirdDetail = ref<any>({});
  const { createMessage } = useMessage();
  //windows对象，用于关闭窗口事件
  const windowsIndex = ref<any>('');
  //窗口监听事件
  const receiveMessage = ref<any>('');

  /**
   * 初始化钉钉和企业微信数据
   */
  async function initUserDetail() {
    let values = await getThirdAccountByUserId({ thirdType: 'wechat_open,dingtalk,wechat_enterprise' });
    bindWechatData.value = "";
    bindDingData.value = "";
    bindEnterpriseData.value = "";
    if (values && values.result) {
      let result = values.result;
      for (let i = 0; i < result.length; i++) {
        setThirdDetail(result[i]);
      }
    }
  }

  /**
   * 企业微信绑定解绑事件
   */
  function wechatEnterpriseBind() {
    console.log('企业微信绑定解绑事件');
    let data = unref(bindEnterpriseData);
    if (!data.sysUserId) {
      onThirdLogin('wechat_enterprise');
    }else{
      deleteAccount({ sysUserId: data.sysUserId, id: data.id }, '企业微信');
    }
  }

  /**
   * 钉钉绑定解绑事件
   */
  function dingDingBind() {
    let data = unref(bindDingData);
    if (!data.sysUserId) {
      onThirdLogin('dingtalk');
    } else {
      deleteAccount({ sysUserId: data.sysUserId, id: data.id }, '钉钉');
    }
    console.log('钉钉绑定解绑事件');
  }

  /**
   * 微信绑定
   */
  function wechatBind() {
    let data = unref(bindWechatData);
    if (!data.sysUserId) {
      onThirdLogin('wechat_open');
    }else{
      deleteAccount({ sysUserId: data.sysUserId, id: data.id }, '微信');
    }
  }

  /**
   * 第三方登录
   * @param source
   */
  function onThirdLogin(source) {
    let url = `${glob.uploadUrl}/sys/thirdLogin/render/${source}`;
    //窗口为不空关闭
    console.log("unref(windowsIndex) ::",unref(windowsIndex))
    if(unref(windowsIndex)){
      //确保只有一个窗口
      windowsIndex.value.close();
      //确保只有一个监听
      window.removeEventListener('message', unref(receiveMessage),false);
    }

    windowsIndex.value = window.open(
      url,
      `login ${source}`,
      'height=500, width=500, top=0, left=0, toolbar=no, menubar=no, scrollbars=no, resizable=no,location=n o, status=no'
    );
    thirdType.value = source;
    receiveMessage.value = async function (event) {
      let token = event.data;
      if (typeof token === 'string') {
        //如果是字符串类型 说明是token信息
        if (token === '登录失败') {
          cmsFailed();
        } else if (token.includes('绑定手机号')) {
          let strings = token.split(',');
          thirdUserUuid.value = strings[1];
          await bindThirdAccount();
        }else{
          if(token){
            createMessage.warning('该敲敲云账号已被其它第三方账号绑定,请解绑或绑定其它敲敲云账号');
          }
        }
      } else {
        cmsFailed();
      }
      window.removeEventListener('message', unref(receiveMessage),false);
      windowsIndex.value = "";
    };
    window.addEventListener('message', unref(receiveMessage), false);
  }

  /**
   * 绑定当前用户
   */
  async function bindThirdAccount() {
    if (!unref(thirdUserUuid)) {
      cmsFailed();
      return;
    }
    let params = { thirdUserUuid: unref(thirdUserUuid), thirdType: unref(thirdType) };
    await bindThirdAppAccount(params)
      .then((res) => {
        if (res.success) {
          if (res.result) {
            setThirdDetail(res.result);
          }
        } else {
          createMessage.warning(res.message);
        }
      })
      .catch((res) => {
        createMessage.warning(res.message);
      });
  }

  /**
   * 失败提示信息
   */
  function cmsFailed() {
    createMessage.warning('第三方账号绑定异常');
    return;
  }

  /**
   * 设置第三方数据
   * @param value
   */
  function setThirdDetail(value) {
    let type = value.thirdType;
    if (type == 'wechat_open') {
      bindWechatData.value = value;
    } else if (type == 'dingtalk') {
      bindDingData.value = value;
    } else if (type == 'wechat_enterprise') {
      bindEnterpriseData.value = value;
    }
  }

  /**
   * 删除第三方信息表
   * @param params
   */
  async function deleteAccount(params, text) {
    Modal.confirm({
      title: '解绑' + text,
      content: '确定要解绑吗',
      okText: '确认',
      cancelText: '取消',
      onOk: async () => {
        await deleteThirdAccount(params).then((res) =>{
          if(res.success){
            initUserDetail();
            createMessage.success(res.message)
          }else{
            createMessage.warning(res.message)
          }
        });
      },
    });
  }

  onMounted(() => {
    initUserDetail();
  });
</script>
<style lang="less" scoped>
  // ----------------------------------------------------
  // UI Redesign: profile.html .app-card
  // ----------------------------------------------------
  .third-app-redesign {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .card {
    background: var(--surface, #fff);
    border-radius: var(--radius-card, 18px);
    box-shadow: var(--shadow-card, 0 2px 12px rgba(15, 23, 42, 0.05));
  }

  .app-wrapper {
    padding: 22px 28px 4px;
  }

  .block-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    font-weight: 600;
    color: var(--ink-900);
    margin-bottom: 4px;

    &::before {
      content: '';
      width: 3px;
      height: 14px;
      border-radius: 2px;
      background: var(--accent, #5b6cff);
    }

    .sub {
      font-size: 12px;
      color: var(--ink-400);
      font-weight: 400;
      margin-left: 4px;
    }
  }

  .app-card {
    padding: 0;
  }

  .app-row {
    display: grid;
    grid-template-columns: 1fr auto;
    align-items: center;
    gap: 20px;
    padding: 22px 0;
    border-bottom: 1px solid var(--line, rgba(15, 23, 42, 0.07));

    &:last-child {
      border-bottom: 0;
    }
  }

  .app-info {
    display: flex;
    align-items: center;
    gap: 14px;
    min-width: 0;
  }

  .app-logo {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    display: grid;
    place-items: center;
    flex-shrink: 0;
    color: #fff;
    font-size: 22px;

    :deep(.anticon) {
      font-size: 22px;
      color: #fff;
    }

    &--dingtalk {
      background: linear-gradient(135deg, #2dbcff, #0089d6);
    }

    &--wechat {
      background: linear-gradient(135deg, #2bc964, #07c160);
    }
  }

  .app-meta {
    display: flex;
    flex-direction: column;
    gap: 3px;
    min-width: 0;
  }

  .app-name {
    color: var(--ink-900);
    font-size: 14px;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 8px;
  }

  .app-desc {
    color: var(--ink-500);
    font-size: 12.5px;
  }

  .sec-tag {
    display: inline-flex;
    align-items: center;
    height: 22px;
    padding: 0 10px;
    border-radius: 11px;
    font-size: 12px;
    font-weight: 500;
    line-height: 1;
    white-space: nowrap;

    &--green {
      background: #e8f7ee;
      color: #15a052;
    }
  }
</style>
