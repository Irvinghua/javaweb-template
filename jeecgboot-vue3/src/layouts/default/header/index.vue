<template>
  <Header :class="getHeaderClass">
    <!-- Mobile: sidebar trigger (tabs row is not shown on mobile) -->
    <LayoutTrigger
      v-if="getIsMobile"
      :theme="getHeaderTheme"
      :sider="false"
    />

    <!-- Tabs strip (flex-grows, contains collapse toggle as leftmost element) -->
    <MultipleTabs v-if="!getIsMobile" class="header-tabs-slot" />

    <!-- action  -->
    <div :class="`${prefixCls}-action`">
      <AppSearch :class="`${prefixCls}-action__item `" v-if="getShowSearch" />

      <ErrorAction v-if="getUseErrorHandle" :class="`${prefixCls}-action__item error-action`" />

      <Notify v-if="getShowNotice" :class="`${prefixCls}-action__item notify-item`" />

      <FullScreen v-if="getShowFullScreen" :class="`${prefixCls}-action__item fullscreen-item`" />

      <LockScreen v-if="getUseLockPage" />

      <AppLocalePicker v-if="getShowLocalePicker" :reload="true" :showText="false" :class="`${prefixCls}-action__item`" />

      <div class="top-divider"></div>

      <UserDropDown :theme="getHeaderTheme" />
    </div>
  </Header>
  <LoginSelect ref="loginSelectRef" @success="loginSelectOk"></LoginSelect>
</template>
<script lang="ts">
  import { defineComponent, unref, computed, ref, onMounted, toRaw } from 'vue';
  import { useGlobSetting } from '/@/hooks/setting';
  import { propTypes } from '/@/utils/propTypes';

  import { Layout } from 'ant-design-vue';
  import LayoutTrigger from '../trigger/index.vue';
  import MultipleTabs from '../tabs/index.vue';

  import { AppSearch } from '/@/components/Application';

  import { useHeaderSetting } from '/@/hooks/setting/useHeaderSetting';
  import { useMenuSetting } from '/@/hooks/setting/useMenuSetting';
  import { useRootSetting } from '/@/hooks/setting/useRootSetting';

  import { MenuModeEnum, MenuSplitTyeEnum } from '/@/enums/menuEnum';
  import { SettingButtonPositionEnum } from '/@/enums/appEnum';
  import { AppLocalePicker } from '/@/components/Application';

  import { UserDropDown, FullScreen, Notify, ErrorAction, LockScreen } from './components';
  import { useAppInject } from '/@/hooks/web/useAppInject';
  import { useDesign } from '/@/hooks/web/useDesign';

  import { createAsyncComponent } from '/@/utils/factory/createAsyncComponent';
  import { useLocale } from '/@/locales/useLocale';

  import LoginSelect from '/@/views/sys/login/LoginSelect.vue';
  import { useUserStore } from '/@/store/modules/user';
  import { useI18n } from '/@/hooks/web/useI18n';
  const { t } = useI18n();

  export default defineComponent({
    name: 'LayoutHeader',
    components: {
      Header: Layout.Header,
      LayoutTrigger,
      MultipleTabs,
      UserDropDown,
      AppLocalePicker,
      FullScreen,
      Notify,
      AppSearch,
      ErrorAction,
      LockScreen,
      LoginSelect,
      SettingDrawer: createAsyncComponent(() => import('/@/layouts/default/setting/index.vue'), {
        loading: true,
      }),
    },
    props: {
      fixed: propTypes.bool,
    },
    setup(props) {
      const { prefixCls } = useDesign('layout-header');
      const userStore = useUserStore();
      const { getShowTopMenu, getShowHeaderTrigger, getSplit, getIsMixMode, getMenuWidth, getIsMixSidebar } = useMenuSetting();
      const { getUseErrorHandle, getShowSettingButton, getSettingButtonPosition } = useRootSetting();
      const { title } = useGlobSetting();

      const {
        getHeaderTheme,
        getShowFullScreen,
        getShowNotice,
        getShowContent,
        getShowBread,
        getShowHeaderLogo,
        getShowHeader,
        getShowSearch,
        getUseLockPage,
        getShowBreadTitle,
      } = useHeaderSetting();

      const { getShowLocalePicker } = useLocale();

      const { getIsMobile } = useAppInject();

      const getHeaderClass = computed(() => {
        const theme = unref(getHeaderTheme);
        return [
          prefixCls,
          {
            [`${prefixCls}--fixed`]: props.fixed,
            [`${prefixCls}--mobile`]: unref(getIsMobile),
            [`${prefixCls}--${theme}`]: theme,
          },
        ];
      });

      const getShowSetting = computed(() => {
        if (!unref(getShowSettingButton)) {
          return false;
        }
        const settingButtonPosition = unref(getSettingButtonPosition);

        if (settingButtonPosition === SettingButtonPositionEnum.AUTO) {
          return unref(getShowHeader);
        }
        return settingButtonPosition === SettingButtonPositionEnum.HEADER;
      });

      const getLogoWidth = computed(() => {
        if (!unref(getIsMixMode) || unref(getIsMobile)) {
          return {};
        }
        const width = unref(getMenuWidth) < 180 ? 180 : unref(getMenuWidth);
        return { width: `${width}px` };
      });

      const getSplitType = computed(() => {
        return unref(getSplit) ? MenuSplitTyeEnum.TOP : MenuSplitTyeEnum.NONE;
      });

      const getMenuMode = computed(() => {
        return unref(getSplit) ? MenuModeEnum.HORIZONTAL : null;
      });

      /**
       * 首页多租户部门弹窗逻辑
       */
      const loginSelectRef = ref();

      function showLoginSelect() {
        //判断是否是登陆进来
        const loginInfo = toRaw(userStore.getLoginInfo) || {};
        if (!!loginInfo.isLogin) {
          loginSelectRef.value.show(loginInfo);
        }
      }

      function loginSelectOk() {
        console.log('成功。。。。。');
      }

      onMounted(() => {
        showLoginSelect();
      });

      return {
        prefixCls,
        getHeaderClass,
        getHeaderTheme,
        getShowHeaderTrigger,
        getIsMobile,
        getShowLocalePicker,
        getShowFullScreen,
        getShowNotice,
        getUseErrorHandle,
        getShowSetting,
        getShowSearch,
        getUseLockPage,
        loginSelectOk,
        loginSelectRef,
        t,
      };
    },
  });
</script>
<style lang="less">
  @import './index.less';
  @prefix-cls: ~'@{namespace}-layout-header';

  .ant-layout .@{prefix-cls} {
    display: flex;
    padding: 0 16px 0 8px;
    height: @header-height;
    align-items: center;
    gap: 8px;

    .headerIntroductionClass {
      margin-right: 4px;
      margin-bottom: 2px;
      border-bottom: 0;
      border-left: 0;
      font-size: 13px;
      color: var(--ink-500);
    }

    &--light {
      .headerIntroductionClass {
        color: var(--ink-500);
      }
    }

    &--dark {
      .headerIntroductionClass {
        color: rgba(255, 255, 255, 0.8);
      }
      .anticon, .truncate {
        color: rgba(255, 255, 255, 1);
      }
    }
  }
</style>
